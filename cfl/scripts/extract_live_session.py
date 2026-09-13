#!/usr/bin/env python3
"""
extract_live_session.py — snapshot a Claude Code session that is STILL RUNNING.

THE HOLE THIS CLOSES
--------------------
`extract_claude_code_sessions.py` extracts sessions that have ENDED. A live session is
therefore not in the corpus, by construction — and Jon's most consequential statements are
made in live Claude Code MAIN sessions. Measured 2026-07-27 by `scripts/audit/cc_corpus_gap.py`:
7 of 29 main-session JSONLs on disk had no markdown at all, two of them being live at that
moment, one 11 MB / 4,786 records. Retention then used to delete many before extraction ever
ran; `cleanupPeriodDays` was raised to 3650 on 2026-07-25, which stops the deletions but does
nothing about the window in which a session exists only as a JSONL nobody has read.

The rule this repo settled on is "**still open is not a reason not to write**" — snapshot,
and be honest about how far the snapshot goes. That honesty is `captured_through_record`.

WHY THE WATERMARK IS THE WHOLE POINT
------------------------------------
A partial capture with no stated boundary is worse than no capture: it looks complete, so a
later reader treats the absence of a turn as evidence the turn never happened. Absence of
evidence silently becomes evidence of absence — which is exactly the failure that let two
sentences be quoted as Jon-verbatim with no Jon turn behind them. `captured_through_record: N`
makes the boundary a fact in the file: everything up to record N is captured, everything after
is simply not yet read. It also makes re-extraction RESUMABLE rather than guesswork, and it
gives `cc_corpus_gap.py` an exact staleness signal instead of an inferred one.

NEVER DISTURBS THE LIVE FILE
----------------------------
The JSONL is being appended to by another process while this runs. So it is opened read-only,
in binary, once; never locked, never truncated, never moved, never written back. The bytes are
copied into a scratch snapshot OUTSIDE the repo and OUTSIDE ~/.claude, and every subsequent
step operates on that copy. A torn final line (a record half-flushed at the instant of the
read) is DISCARDED rather than repaired — see read_complete_records().

ONE FORMAT, NOT TWO
-------------------
Output is produced by `skills/chat-exporter/scripts/convert-claude-code.py`, the same single
canonical converter `extract_claude_code_sessions.py` delegates to, invoked the same way with
the same flags. This script adds frontmatter to that output; it does not render markdown of
its own. A second renderer would be a second convention, and the corpus has been through that
already. The added fields are additive — `source_id`, `title`, turn structure, `raw_sha256`
and every existing field are exactly what the normal extractor would have produced.

REFUSES TO SHRINK
-----------------
Re-running on a grown session EXTENDS the capture. Re-running against a shorter JSONL than the
one already captured (an archive copy, a rolled-back file, a session id typo landing on a stub)
would replace a long extract with a short one and destroy the difference silently. That is
refused with exit 3, before anything is written. The check is explicit and runs on both the
stated watermark and the turn count, because the file being protected may predate watermarks.

Usage:
    python scripts/extract_live_session.py --session 0fb7cad8
    python scripts/extract_live_session.py --session <full-uuid> --dry-run
    python scripts/extract_live_session.py --all-live            # mtime within --live-window
    python scripts/extract_live_session.py --all-live --live-window 240

Exit codes: 0 ok / 1 error / 3 refused (would shrink an existing capture)
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
# Reuse the extractor's own discovery/attribution/output-layout rather than restating it.
# project_for_dir, existing_mds, OUT_DIR, CONVERTER and the subagent-tree exclusions are all
# decisions with reasons already written down; a second copy here would drift from them.
import extract_claude_code_sessions as X  # noqa: E402

LIVE_WINDOW_MIN_DEFAULT = 120


# ---------------------------------------------------------------------------
# Reading a file that is being written to
# ---------------------------------------------------------------------------

def read_complete_records(jsonl_path):
    """Read the live JSONL READ-ONLY and return (complete_line_bytes, n_records, n_bytes).

    Opened 'rb' and read once. No lock, no truncate, no write-back, no move — the file
    belongs to a running process and this function must be invisible to it.

    A TORN TRAILING LINE is expected, not exceptional: the writer appends a record and the
    read can land mid-flush, leaving a final fragment that is not valid JSON. That fragment
    is DISCARDED, and the watermark is set to the last COMPLETE record. Keeping it would
    corrupt the snapshot; "repairing" it would invent content. Dropping it costs at most one
    record, which the next run picks up — that is precisely what the watermark makes safe.

    A line in the MIDDLE that does not parse is a different thing (real corruption, not a
    torn write); it is counted as not-a-record, matching convert-claude-code.load_events(),
    and reported so it is never silent.
    """
    with open(jsonl_path, "rb") as f:
        blob = f.read()

    lines = blob.split(b"\n")
    trailing_partial = False
    if lines and lines[-1] == b"":
        lines.pop()          # file ended on a newline: every line is complete
    elif lines:
        candidate = lines[-1]
        try:
            json.loads(candidate.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            lines.pop()      # torn write in progress — drop it
            trailing_partial = True

    kept, n_records, bad_middle = [], 0, 0
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        try:
            json.loads(s.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            bad_middle += 1
            continue
        kept.append(ln)
        n_records += 1

    body = b"\n".join(kept) + (b"\n" if kept else b"")
    return body, n_records, len(body), trailing_partial, bad_middle


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Existing-capture inspection (the anti-shrink guard)
# ---------------------------------------------------------------------------

FM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")


def read_frontmatter(md_path):
    out = {}
    try:
        with open(md_path, "r", encoding="utf-8", errors="replace") as f:
            if f.readline().strip() != "---":
                return out
            for line in f:
                if line.strip() == "---":
                    break
                m = FM_RE.match(line.rstrip("\n"))
                if m:
                    out[m.group(1)] = m.group(2).strip()
    except OSError:
        pass
    return out


def existing_capture(uuid6):
    """(path, watermark_or_None, turn_count_or_None) for the current extract, or (None,..).

    Uses the extractor's own existing_mds(), which is recursive (domain subfolders) and
    excludes the subagents/ subtree — both for reasons documented there.

    `.sidecar.md` COMPANIONS ARE EXCLUDED, and that exclusion is load-bearing rather than
    cosmetic. existing_mds() globs `*<uuid6>*.md`, which matches the sidecar too, and it
    returns the LARGEST match. The self-test caught the consequence: on a short session the
    sidecar outweighs the primary, so `existing_capture` read the SIDECAR — a file with no
    turn headers — and reported `turns=0`. The anti-shrink turn guard then compared every
    future snapshot against zero and could never fire. A guard that silently degrades to
    always-pass is worse than no guard, because it is still printed as if it ran.
    """
    paths = [p for p in X.existing_mds(uuid6)
             if not p.name.endswith(".sidecar.md") and "payloads" not in p.parts]
    if not paths:
        return None, None, None
    p = max(paths, key=lambda q: q.stat().st_size)
    fm = read_frontmatter(p)
    wm = fm.get("captured_through_record")
    wm = int(wm) if wm and wm.isdigit() else None
    turns = None
    try:
        sys.path.insert(0, str(SCRIPTS_DIR / "audit"))
        from turn_index import index as ti
        turns = ti(str(p))["turn_count"]
    except Exception:
        pass
    return p, wm, turns


# ---------------------------------------------------------------------------
# Frontmatter stamping
# ---------------------------------------------------------------------------

LIVE_BANNER = (
    "> **LIVE SNAPSHOT — this session had not ended when this file was written.** It is "
    "captured through record `{n}` of the session JSONL as of `{ts}`; anything said after "
    "that record is simply not yet read. **Absence of a turn below is NOT evidence the turn "
    "never happened** — check `captured_through_record` before concluding anything from "
    "silence. Re-running `scripts/extract_live_session.py` extends the capture and advances "
    "the watermark."
)


def stamp_frontmatter(text, fields, banner=None):
    """Insert `fields` into the leading `---` block and optionally a banner before `## Summary`.

    Additive and idempotent: any key already present is REPLACED in place rather than
    duplicated, so re-running never accumulates stale watermarks. Turn headers are untouched,
    so turn_index.py numbering and every T/P citation anchor are unaffected.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("converter output has no frontmatter block")
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")

    for key, val in fields.items():
        new = f"{key}: {val}"
        for i in range(1, end):
            if lines[i].startswith(f"{key}:"):
                lines[i] = new
                break
        else:
            lines.insert(end, new)
            end += 1
    out = "\n".join(lines)

    if banner:
        marker = "## Summary"
        idx = out.find(marker)
        if idx != -1 and banner.split("**")[1] not in out[:idx]:
            out = out[:idx] + banner + "\n\n" + out[idx:]
    return out


# ---------------------------------------------------------------------------
# Snapshot one session
# ---------------------------------------------------------------------------

def snapshot(jsonl_path, project, dry_run=False, force_shrink=False):
    """Returns exit-code-ish int: 0 ok, 3 refused, 1 error."""
    uuid = jsonl_path.stem
    uuid6 = uuid[:6]

    pre_hash = sha256_file(jsonl_path)
    body, n_records, n_bytes, torn, bad_middle = read_complete_records(jsonl_path)
    captured_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    prev_path, prev_wm, prev_turns = existing_capture(uuid6)

    print(f"  session {uuid6}  records={n_records}  bytes={n_bytes:,}  project={project}")
    if torn:
        print(f"    note: trailing partial record discarded (torn write) — watermark is the "
              f"last COMPLETE record")
    if bad_middle:
        print(f"    WARNING: {bad_middle} unparseable line(s) mid-file, not counted as records")
    if prev_path:
        print(f"    existing: {prev_path.name}  watermark={prev_wm}  turns={prev_turns}")

    # ---- ANTI-SHRINK GUARD, before any write ----
    if prev_wm is not None and n_records < prev_wm and not force_shrink:
        print(f"    REFUSED: existing capture reaches record {prev_wm}, this source has only "
              f"{n_records}. Writing would DESTROY {prev_wm - n_records} record(s) of capture.")
        return 3

    if dry_run:
        print(f"    [dry-run] would capture through record {n_records} at {captured_at}")
        return 0

    scratch = Path(tempfile.mkdtemp(prefix="livesnap-"))
    try:
        snap = scratch / f"{uuid}.jsonl"     # stem must be the uuid: the converter derives from it
        snap.write_bytes(body)

        out_scratch = scratch / "out"
        title = X.quick_meta(snap)[1]
        cmd = [sys.executable, str(X.CONVERTER), str(snap), "--run",
               "--out", str(out_scratch), "--project", project, "--force"]
        if title:
            cmd += ["--slug", title]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    ERROR: converter failed: {(r.stderr or r.stdout).strip()[:300]}")
            return 1

        produced = sorted(p for p in out_scratch.rglob("*.md")
                          if not p.name.endswith(".sidecar.md"))
        if len(produced) != 1:
            print(f"    ERROR: expected 1 markdown, converter produced {len(produced)}")
            return 1
        md = produced[0]

        # Turn-count guard: protects a pre-watermark extract, which has no watermark to check.
        try:
            sys.path.insert(0, str(SCRIPTS_DIR / "audit"))
            from turn_index import index as ti
            new_turns = ti(str(md))["turn_count"]
        except Exception:
            new_turns = None
        if (prev_turns is not None and new_turns is not None
                and new_turns < prev_turns and not force_shrink):
            print(f"    REFUSED: existing capture holds {prev_turns} turns, this snapshot "
                  f"yields {new_turns}. Refusing to replace a longer extract with a shorter one.")
            return 3

        stamp = {
            "capture_state": "LIVE-SNAPSHOT",
            "captured_through_record": n_records,
            "captured_at": captured_at,
            "session_id": uuid,
            "captured_bytes": n_bytes,
            "source_jsonl_sha256_at_capture": pre_hash,
        }
        md.write_text(
            stamp_frontmatter(md.read_text(encoding="utf-8"), stamp,
                              banner=LIVE_BANNER.format(n=n_records, ts=captured_at)),
            encoding="utf-8")

        for side in out_scratch.rglob("*.sidecar.md"):
            side.write_text(
                stamp_frontmatter(side.read_text(encoding="utf-8"),
                                  {"capture_state": "LIVE-SNAPSHOT",
                                   "captured_through_record": n_records,
                                   "captured_at": captured_at,
                                   "session_id": uuid}),
                encoding="utf-8")

        # Destination: refresh in place at the existing file's directory (never relocate —
        # existing wiki source_file: citations must not break), else the normal new-session
        # domain-subfolder route.
        if prev_path:
            dest_dir = prev_path.parent
        else:
            dest_dir = X.OUT_DIR
            if project in ("fl", "pro", "research"):
                dest_dir = dest_dir / project
        dest_dir.mkdir(parents=True, exist_ok=True)

        moved = []
        for src in sorted(out_scratch.rglob("*")):
            if src.is_dir():
                continue
            rel = src.relative_to(out_scratch)
            # payloads/ keeps its subdirectory; md + sidecar land flat in dest_dir
            dst = dest_dir / rel if rel.parent != Path(".") else dest_dir / rel.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            moved.append(dst)

        # Remove a superseded extract only AFTER the new one is safely written, and only if
        # the slug changed (same path was already overwritten in place).
        new_md = dest_dir / md.name
        if prev_path and prev_path.resolve() != new_md.resolve():
            old_side = prev_path.with_name(prev_path.name[:-3] + ".sidecar.md")
            prev_path.unlink()
            if old_side.exists():
                old_side.unlink()
            print(f"    superseded: {prev_path.name}")

        post_hash = sha256_file(jsonl_path)
        print(f"    WROTE {new_md}")
        print(f"    captured_through_record={n_records}  turns={new_turns}")
        print(f"    source sha256 pre ={pre_hash}")
        print(f"    source sha256 post={post_hash}  "
              f"{'IDENTICAL' if pre_hash == post_hash else 'CHANGED (session still writing)'}")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ---------------------------------------------------------------------------

def resolve_sessions(args):
    """Return [(jsonl_path, project)] for the requested sessions."""
    found = []
    for proj_dir, jsonl_path in X.iter_session_jsonls():
        project = X.project_for_dir(proj_dir.name)
        if args.session:
            if jsonl_path.stem == args.session or jsonl_path.stem.startswith(args.session):
                found.append((jsonl_path, project))
        elif args.all_live:
            age_min = (time.time() - jsonl_path.stat().st_mtime) / 60.0
            if age_min <= args.live_window:
                found.append((jsonl_path, project))
    return found


def _fixture_records(n, start=0):
    """n synthetic CC records: alternating user/assistant, fabricated text only.

    Synthesized, never sampled from the corpus: `raw/` is Jon's full personal history and
    no fixture in a tracked file may carry a byte of it.
    """
    out = []
    for i in range(start, start + n):
        ts = f"2026-07-27T00:{i // 60:02d}:{i % 60:02d}.000Z"
        if i % 2 == 0:
            out.append({"type": "user", "timestamp": ts, "uuid": f"u{i}",
                        "message": {"role": "user", "content": f"fixture prompt {i}"}})
        else:
            out.append({"type": "assistant", "timestamp": ts, "uuid": f"a{i}",
                        "message": {"role": "assistant", "model": "fixture-model",
                                    "content": [{"type": "text", "text": f"fixture reply {i}"}]}})
    return out


def _write_jsonl(path, records):
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")


def self_test():
    """Extension, anti-shrink, and torn-write handling — on synthetic fixtures only.

    Writes exclusively into a temp directory (X.OUT_DIR is redirected for the duration),
    so it can never touch the real corpus, ~/.claude, or the repo.
    """
    tmp = Path(tempfile.mkdtemp(prefix="livesnap-selftest-"))
    real_out = X.OUT_DIR
    try:
        X.OUT_DIR = tmp / "corpus"
        X.OUT_DIR.mkdir(parents=True)
        src = tmp / "aaaaaaaa-1111-2222-3333-444444444444.jsonl"

        # --- 1. first capture ---
        _write_jsonl(src, _fixture_records(6))
        assert snapshot(src, "fl") == 0, "first snapshot failed"
        md = next(p for p in X.OUT_DIR.rglob("*.md") if not p.name.endswith(".sidecar.md"))
        fm = read_frontmatter(md)
        assert fm["capture_state"] == "LIVE-SNAPSHOT", fm
        assert fm["captured_through_record"] == "6", fm
        t1 = int(fm["captured_through_record"])
        size1 = md.stat().st_size

        # --- 2. session grows -> capture must EXTEND, never replace-with-shorter ---
        _write_jsonl(src, _fixture_records(10))
        assert snapshot(src, "fl") == 0, "grown snapshot failed"
        md = next(p for p in X.OUT_DIR.rglob("*.md") if not p.name.endswith(".sidecar.md"))
        fm = read_frontmatter(md)
        assert int(fm["captured_through_record"]) == 10, fm
        assert int(fm["captured_through_record"]) > t1
        # Regression guard for the sidecar-shadowing defect: the prior capture that the
        # anti-shrink guard inspects must be the PRIMARY transcript, never its sidecar
        # (which has no turn headers and would report turns=0, disabling the guard).
        prev_p, prev_wm, prev_turns = existing_capture("aaaaaa")
        assert not prev_p.name.endswith(".sidecar.md"), prev_p
        assert prev_turns == 10, f"guard read the wrong file: turns={prev_turns}"
        assert prev_wm == 10, prev_wm
        # And the sidecar must still exist — it is a companion, not a superseded file.
        assert prev_p.with_name(prev_p.name[:-3] + ".sidecar.md").exists()
        assert md.stat().st_size > size1, "grown capture is not larger"
        # stamping is idempotent: exactly one of each key, one banner
        head = md.read_text(encoding="utf-8").split("\n---", 2)[0]
        for k in ("capture_state", "captured_through_record", "captured_at", "session_id"):
            assert sum(1 for l in head.split("\n") if l.startswith(k + ":")) == 1, k
        assert md.read_text(encoding="utf-8").count("LIVE SNAPSHOT — this session") == 1
        size2 = md.stat().st_size
        before = md.read_bytes()

        # --- 3. shorter source -> MUST refuse, and MUST NOT write ---
        _write_jsonl(src, _fixture_records(4))
        rc = snapshot(src, "fl")
        assert rc == 3, f"expected refusal (3), got {rc}"
        assert md.read_bytes() == before, "REFUSED path still modified the existing capture"
        assert md.stat().st_size == size2

        # --- 4. torn trailing write -> counted through the last COMPLETE record ---
        _write_jsonl(src, _fixture_records(12))
        with open(src, "a", encoding="utf-8") as f:
            f.write('{"type": "user", "timestamp": "2026-07-27T01:00:00.000Z", "mess')
        _body, n, _b, torn, bad = read_complete_records(src)
        assert n == 12, f"torn write miscounted: {n}"
        assert torn is True
        assert bad == 0

        # --- 5. read is non-destructive ---
        h_pre = sha256_file(src)
        read_complete_records(src)
        assert sha256_file(src) == h_pre, "reading altered the source"

        print("self-test OK — extend(6->10), refuse-shrink(10 vs 4, exit 3, file untouched), "
              "torn-write watermark(12), idempotent stamping, non-destructive read")
    finally:
        X.OUT_DIR = real_out
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    if "--self-test" in sys.argv:
        self_test()
        return 0
    g = ap.add_mutually_exclusive_group(required=True)
    ap.add_argument("--self-test", action="store_true",
                    help="synthetic-fixture check of the extend / refuse-shrink guarantees")
    g.add_argument("--session", help="session uuid (or unique leading prefix)")
    g.add_argument("--all-live", action="store_true",
                   help="every session whose JSONL was modified within --live-window")
    ap.add_argument("--live-window", type=float, default=LIVE_WINDOW_MIN_DEFAULT,
                    metavar="MIN", help=f"minutes (default {LIVE_WINDOW_MIN_DEFAULT})")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force-shrink", action="store_true",
                    help="override the anti-shrink guard. Destroys capture; requires intent.")
    args = ap.parse_args()

    if not X.CONVERTER.exists():
        sys.exit(f"ERROR: converter not found at {X.CONVERTER}")

    targets = resolve_sessions(args)
    if not targets:
        print("No matching session found.")
        return 1

    print(f"Converter: {X.CONVERTER}")
    print(f"Corpus:    {X.OUT_DIR}")
    print(f"Snapshotting {len(targets)} session(s)\n")

    worst = 0
    for jsonl_path, project in targets:
        rc = snapshot(jsonl_path, project, dry_run=args.dry_run,
                      force_shrink=args.force_shrink)
        worst = max(worst, rc)
        print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
