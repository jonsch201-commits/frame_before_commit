#!/usr/bin/env python3
"""Close-triggered, incremental, hash-verifying capture of the live Claude Code session store.

WHY THIS EXISTS
---------------
`cleanupPeriodDays` does not reliably work. It was set to 3650 on 2026-07-25 and three open
upstream bugs -- GH #62272, #18881, #45903 -- ignore it. CFL treated that setting as the fix
from July onward. Claude Personal measured the cost on their side: 29 sessions permanently
gone (2026-05-01 -> 06-16), including 615 of Jon's prompts.

CFL is NOT in Personal's position, and this script's own docstring should say so plainly so
nobody re-panics: an accumulate archive (`scripts/archive-claude-accumulate.ps1`) already runs
daily at 12:30 via the `ClaudeAccumulateArchive` scheduled task, plus once at SessionStart, to
two destinations. Measured 2026-08-06: 1021 of 1056 CFL live-store files already had a
byte-identical copy under some control.

The gap this script closes is the remaining 35 -- and what they have in common is the whole
point. Every one of them was younger than the last scheduled archive run. A daily schedule
means the newest and most valuable work is always the least protected. This capture is
CLOSE-TRIGGERED, so it can never lag by more than one turn.

It is deliberately a SECOND, INDEPENDENT layer rather than a replacement. Per Claude Personal,
2026-08-06: "when both exist, the two counts disagree or they corroborate, and either is
information."

NON-DESTRUCTIVE GUARANTEE (Jon's standing constraint, his words: NO DESTRUCTIVE ACTS)
-------------------------------------------------------------------------------------
This tool ONLY EVER READS the live store and ONLY EVER WRITES inside the repo's gitignored
`raw/` tree. It never deletes, moves, renames, or modifies anything under
`~/.claude/projects/`. This is structurally enforced, not merely promised:

  * every source access goes through `_read_source()`, which opens mode "rb" and nothing else;
  * `_assert_write_target()` refuses any destination path that does not resolve under
    CAPTURE_ROOT, and is called before every single write;
  * there is no os.remove / os.rename / shutil.move call anywhere in this file whose argument
    can be a source path -- the only mutating calls take paths already passed through
    `_assert_write_target()`.

The capture is ACCUMULATE, not mirror: a file deleted at the source stays here forever.

THE NULL-COMPARE TRAP (Claude Personal's near-miss, inherited deliberately)
--------------------------------------------------------------------------
Their first version "printed MATCH on two files that had not copied -- two nulls compare
equal." A comparison that passes on two empty files is not a verification. Defeated here by
four independent conditions, ALL of which must hold before a copy is called VERIFIED:

  1. `_digest()` RAISES on any read error. It never returns None/""/a sentinel, so two failed
     reads cannot compare equal -- the failure propagates instead of being silently ==.
  2. The digest must be a well-formed 64-char lowercase hex string (`_assert_digest`).
  3. `dst_size == src_size` is checked independently of the hashes. This is the condition that
     actually kills the two-nulls case: a 12 MB source against a 0-byte destination fails on
     size no matter what the digests say.
  4. A destination of 0 bytes for a non-empty source is rejected explicitly with its own
     reason code, so the failure is legible rather than generic.

`--self-test` proves the failure path FIRES, with three negative controls including the exact
two-empty-files case. A capture reporting zero failures on its first run should make you
suspicious, not satisfied; the self-test is what earns the zero.

USAGE
-----
  python scripts/audit/session_store_capture.py              # capture (hook entry point)
  python scripts/audit/session_store_capture.py --measure    # report coverage, copy nothing
  python scripts/audit/session_store_capture.py --self-test  # prove the failure path fires
  python scripts/audit/session_store_capture.py --verbose    # per-file lines
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time

# --------------------------------------------------------------------------- paths

# scripts/audit/session_store_capture.py -> up three levels is the repo root. Getting this
# wrong is not cosmetic: the first run of this script resolved REPO_ROOT one level short and
# wrote 1056 files into `scripts/raw/`. It was still gitignored (the `raw/` pattern matches at
# any depth) so nothing leaked, but the capture was in the wrong place and the sanity check
# that caught it was reading the banner, not any assertion. Hence the assertion below.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAPTURE_ROOT = os.path.join(REPO_ROOT, "raw", "live-store-capture")

if not os.path.isdir(os.path.join(REPO_ROOT, ".git")):
    raise SystemExit(
        f"refusing to run: REPO_ROOT={REPO_ROOT} is not a git repo root. "
        "The capture would land somewhere unintended."
    )
STATE_PATH = os.path.join(CAPTURE_ROOT, "_state", "manifest.json")
LOG_PATH = os.path.join(CAPTURE_ROOT, "_state", "capture.log")

STORE_ROOT = os.path.join(os.path.expanduser("~"), ".claude", "projects")

# The CFL project dirs. Claude Code derives these from the launch working directory, so one
# project has several -- the repo folder, the parent Drive folder (a stale store; see the
# cfl-memory-store-split-by-cwd memory), and one per worktree. A capture scoped to just the
# repo folder would silently miss the rest, which is the same directory-blindness that hides
# subagents one level down.
CFL_PROJECT_PREFIXES = (
    "G--My-Drive-Claude-Claude-Foundational-Layer",
    # ADDED 2026-09-12 after a ten-day silent gap. CFL moved to N:\claude-cfl\clone on 2026-09-02
    # and this tuple did not move with it, so the CURRENT store -- ~/.claude/projects/
    # N--claude-cfl-clone/, including its 86-file memory/ -- was captured ZERO times while the
    # capture printed "files seen 2271 | skipped-unchanged 2271" every run. A printed success over
    # a store it was not looking at.
    #
    # The comment three lines above this one already names the class ("a capture scoped to just the
    # repo folder would silently miss the rest"). The code then committed that exact defect against
    # a different axis -- not worktrees, but DRIVE LETTER. Found 2026-09-12 only because Jon asked
    # whether files CFL writes to C: are meaningfully in the graph; they were not, and the memory
    # corrected that same morning existed on N: only as a stale 2,399 B copy against a 3,296 B live
    # file. A stale indexed copy is worse than an absent one.
    "N--claude-cfl",
)

# ⭐ SUPERSEDED 2026-09-12 10:5x, forty minutes after the tuple above was "fixed" by hand.
# Adding a prefix to a literal tuple is the SAME DEFECT one revision fresher: correct today, wrong the
# next time this tree moves -- which is exactly what happened to the line the tuple above replaced.
# The key is now DERIVED from the tree's own path by scripts/audit/project_dirs.py (design ported from
# Claude Professional, credit in that file's header). The tuple is KEPT as the legacy floor, never as
# the source of truth: if the import fails for any reason the capture still sees what it saw before,
# because a capture that silently narrows is the failure this whole section is about.
def _cfl_project_prefixes():
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import project_dirs
        derived = [os.path.basename(d) for d in project_dirs.existing_dirs(REPO_ROOT)]
        merged = list(dict.fromkeys(derived + list(CFL_PROJECT_PREFIXES)))
        if derived:
            return tuple(merged)
        # UNKNOWN, not empty: an import that resolves nothing must not narrow the capture.
        print("WARN project_dirs resolved 0 dirs for %s -- falling back to the literal prefixes"
              % REPO_ROOT)
        return CFL_PROJECT_PREFIXES
    except Exception as exc:
        print("WARN project_dirs unavailable (%s: %s) -- falling back to the literal prefixes"
              % (type(exc).__name__, exc))
        return CFL_PROJECT_PREFIXES

# Computed ONCE at import so the capture and its receipt agree on one population.
CAPTURE_PREFIXES = _cfl_project_prefixes()


_HEX64 = re.compile(r"^[0-9a-f]{64}$")
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


class VerifyError(Exception):
    """Raised when a copy cannot be proven identical. Never swallowed into a boolean."""


# --------------------------------------------------------------- read-only source access


def _read_source(path, chunk=1 << 20):
    """The ONLY way this module touches the live store. Opens "rb". Yields chunks.

    Structural half of the non-destructive guarantee: there is no other open() against a
    source path in this file, and this one cannot write.
    """
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                return
            yield block


def _digest(path):
    """SHA-256 of a file. RAISES on any read failure -- never returns a falsy sentinel.

    This is condition 1 of the null-compare defeat. If this returned None on error, two
    unreadable files would compare equal and print MATCH. It raises instead.
    """
    h = hashlib.sha256()
    for block in _read_source(path):
        h.update(block)
    return h.hexdigest()


def _assert_digest(value, label):
    """Condition 2: a digest must look like a digest. Guards against ""/None slipping through."""
    if not isinstance(value, str) or not _HEX64.match(value):
        raise VerifyError(f"{label} is not a well-formed sha256: {value!r}")
    return value


def _assert_write_target(path):
    """Structural half of the non-destructive guarantee: refuse to write outside raw/capture."""
    resolved = os.path.realpath(path)
    root = os.path.realpath(CAPTURE_ROOT)
    if not (resolved == root or resolved.startswith(root + os.sep)):
        raise VerifyError(f"REFUSED write outside the capture root: {resolved}")
    return path


def verify_copy(src, dst, src_digest, src_size):
    """Prove dst is byte-identical to src as it was read. Raises VerifyError otherwise.

    All four null-compare conditions live here. Note that `src_digest` is computed from the
    SOURCE BEFORE the copy and passed in -- the destination is never compared against another
    freshly-computed source hash, so a source that became unreadable cannot make both sides
    agree by both failing.
    """
    _assert_digest(src_digest, "source digest")

    if not os.path.isfile(dst):
        raise VerifyError("destination does not exist after copy")

    dst_size = os.path.getsize(dst)

    # Condition 4 -- the loud, specific form of the two-nulls case.
    if src_size > 0 and dst_size == 0:
        raise VerifyError(
            f"destination is EMPTY ({dst_size} B) but source is {src_size} B "
            "-- this is the two-nulls-compare-equal case"
        )

    # Condition 3 -- independent of hashing entirely. This is the one that cannot be fooled.
    if dst_size != src_size:
        raise VerifyError(f"size mismatch: source {src_size} B, destination {dst_size} B")

    dst_digest = _assert_digest(_digest(dst), "destination digest")

    # Belt and braces: an empty-file digest on a non-empty file is incoherent.
    if dst_digest == EMPTY_SHA256 and src_size > 0:
        raise VerifyError("destination hashed as empty while source is non-empty")

    if dst_digest != src_digest:
        raise VerifyError(f"hash mismatch: source {src_digest[:12]}, destination {dst_digest[:12]}")

    return dst_digest


# --------------------------------------------------------------------------- classify


def classify(relpath):
    """Session transcript vs subagent transcript.

    Subagent transcripts live one level down (`<session-id>/subagents/agent-*.jsonl`). A flat
    copy silently misses them, and on CFL they are the great majority of the record -- so they
    are counted SEPARATELY, and a regression in either count is visible on its own.
    """
    parts = relpath.replace("\\", "/").split("/")
    if "subagents" in parts:
        return "subagent"
    if "memory" in parts:
        return "memory"
    if len(parts) == 2 and parts[1].endswith(".jsonl"):
        return "session"
    return "other"


def iter_store():
    """Yield (project_dir, relpath, abspath) for every file in every CFL project dir."""
    if not os.path.isdir(STORE_ROOT):
        return
    for project in sorted(os.listdir(STORE_ROOT)):
        if not project.startswith(CAPTURE_PREFIXES):
            continue
        root = os.path.join(STORE_ROOT, project)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            for fn in sorted(filenames):
                ap = os.path.join(dirpath, fn)
                rp = os.path.relpath(ap, STORE_ROOT)
                yield project, rp, ap


# --------------------------------------------------------------------------- state


def load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("files"), dict):
            return data
    except (OSError, ValueError):
        pass
    return {"files": {}, "runs": 0}


def save_state(state):
    _assert_write_target(STATE_PATH)
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(_assert_write_target(tmp), "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=1, sort_keys=True)
    os.replace(tmp, STATE_PATH)


def log_line(text):
    try:
        _assert_write_target(LOG_PATH)
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")
    except OSError:
        pass


# --------------------------------------------------------------------------- capture


def capture(verbose=False, measure_only=False, reconcile=None, reconcile_every=20):
    started = time.time()
    state = load_state()
    files = state["files"]

    # Checking that each destination file really exists costs ~1000 stat calls against a
    # Google-Drive-mounted path, which measured 5-7 s -- too much to pay at every turn end.
    # But trusting the manifest forever is the "derive, don't record" failure: the manifest is
    # a CLAIM about the world, and a claim nothing ever rechecks will drift. So the full
    # destination reconcile runs periodically (and on demand), and the cheap path runs the rest
    # of the time. Which mode ran is reported, so a fast run is never mistaken for a full one.
    if reconcile is None:
        reconcile = (state.get("runs", 0) % reconcile_every) == 0
    state["last_mode"] = "reconcile" if reconcile else "fast"

    counts = {k: 0 for k in ("seen", "copied", "verified", "failed", "skipped", "busy")}
    by_kind = {}
    failures = []

    for _project, relpath, abspath in iter_store():
        kind = classify(relpath)
        slot = by_kind.setdefault(kind, {"seen": 0, "copied": 0, "verified": 0, "failed": 0})
        counts["seen"] += 1
        slot["seen"] += 1

        try:
            st = os.stat(abspath)
        except OSError as exc:
            counts["failed"] += 1
            slot["failed"] += 1
            failures.append((relpath, f"stat failed: {exc}"))
            continue

        key = relpath.replace("\\", "/")
        prior = files.get(key)
        dst = os.path.join(CAPTURE_ROOT, relpath)

        # Incremental: skip on size+mtime match, but only if the destination is actually
        # there. A manifest entry is a claim about the world, not the world -- if the file
        # is gone, the claim is stale and we re-copy.
        if (
            prior
            and prior.get("size") == st.st_size
            and abs(prior.get("mtime", -1) - st.st_mtime) < 1e-6
            and (
                not reconcile
                or (os.path.isfile(dst) and os.path.getsize(dst) == st.st_size)
            )
        ):
            counts["skipped"] += 1
            continue

        if measure_only:
            continue

        try:
            src_digest = _digest(abspath)
            src_size = st.st_size

            _assert_write_target(dst)
            os.makedirs(os.path.dirname(dst), exist_ok=True)

            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dst), suffix=".part")
            os.close(fd)
            _assert_write_target(tmp)
            try:
                with open(tmp, "wb") as out:
                    for block in _read_source(abspath):
                        out.write(block)

                # The source is a live transcript and may have grown mid-copy. That is BUSY,
                # not a failure -- but it is counted separately so it can never be used to
                # quietly absorb a real failure.
                post = os.stat(abspath)
                if post.st_size != src_size or abs(post.st_mtime - st.st_mtime) > 1e-6:
                    counts["busy"] += 1
                    os.unlink(_assert_write_target(tmp))
                    if verbose:
                        print(f"  BUSY     {relpath}")
                    continue

                verify_copy(abspath, tmp, src_digest, src_size)

                # Truncation guard: if a stored capture is LONGER than what we are about to
                # write, the source shrank. Transcripts are append-only, so that is anomalous
                # -- preserve the longer copy rather than overwrite it.
                if os.path.isfile(dst) and os.path.getsize(dst) > src_size:
                    sup = os.path.join(
                        CAPTURE_ROOT, "_superseded", f"{int(time.time())}-{os.path.basename(dst)}"
                    )
                    _assert_write_target(sup)
                    os.makedirs(os.path.dirname(sup), exist_ok=True)
                    shutil.copy2(dst, sup)

                os.replace(tmp, _assert_write_target(dst))
            finally:
                if os.path.exists(tmp):
                    os.unlink(_assert_write_target(tmp))

            counts["copied"] += 1
            counts["verified"] += 1
            slot["copied"] += 1
            slot["verified"] += 1
            files[key] = {
                "size": src_size,
                "mtime": st.st_mtime,
                "sha256": src_digest,
                "kind": kind,
            }
            if verbose:
                print(f"  VERIFIED {relpath}  ({src_size} B)")

        except (VerifyError, OSError) as exc:
            counts["failed"] += 1
            slot["failed"] += 1
            failures.append((relpath, str(exc)))
            if verbose:
                print(f"  FAILED   {relpath}: {exc}")

    if not measure_only:
        state["runs"] = state.get("runs", 0) + 1
        state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save_state(state)

    elapsed = time.time() - started
    counts["mode"] = "reconcile" if reconcile else "fast"
    return counts, by_kind, failures, elapsed


def report(counts, by_kind, failures, elapsed, measure_only=False):
    head = "MEASURE (no copies made)" if measure_only else "CAPTURE"
    print(f"=== live-store {head} [{counts.get('mode', '?')} mode] ===")
    print(f"capture root : {CAPTURE_ROOT}")
    print(f"source       : {STORE_ROOT}  (READ-ONLY -- never modified)")
    print(
        "files seen {seen} | copied {copied} | verified {verified} | "
        "failed {failed} | skipped-unchanged {skipped} | busy {busy}".format(**counts)
    )
    print()
    print(f"{'kind':<10} {'seen':>6} {'copied':>7} {'verified':>9} {'failed':>7}")
    for kind in ("session", "subagent", "memory", "other"):
        s = by_kind.get(kind)
        if s:
            print(
                f"{kind:<10} {s['seen']:>6} {s['copied']:>7} {s['verified']:>9} {s['failed']:>7}"
            )
    if failures:
        print(f"\n!! {len(failures)} FAILURES")
        for rp, why in failures[:20]:
            print(f"   {rp}: {why}")
    print(f"\nelapsed {elapsed:.2f}s")

    log_line(
        "{ts}  seen={seen} copied={copied} verified={verified} failed={failed} "
        "skipped={skipped} busy={busy} sessions={ses} subagents={sub} {el:.2f}s".format(
            ts=time.strftime("%Y-%m-%d %H:%M:%S"),
            ses=by_kind.get("session", {}).get("seen", 0),
            sub=by_kind.get("subagent", {}).get("seen", 0),
            el=elapsed,
            **counts,
        )
    )


# --------------------------------------------------------------------------- self-test


def self_test():
    """Prove the failure path FIRES. Three negative controls; a green run means nothing without them."""
    results = []

    def check(name, fn):
        try:
            fn()
            results.append((name, True, ""))
        except AssertionError as exc:
            results.append((name, False, str(exc)))
        except Exception as exc:  # noqa: BLE001
            results.append((name, False, f"unexpected {type(exc).__name__}: {exc}"))

    tmpd = tempfile.mkdtemp(prefix="capture-selftest-")
    global CAPTURE_ROOT
    saved_root = CAPTURE_ROOT
    CAPTURE_ROOT = tmpd
    try:
        payload = b"line one\nline two\n" * 500
        src = os.path.join(tmpd, "src.jsonl")
        with open(src, "wb") as fh:
            fh.write(payload)
        src_sha = _digest(src)
        src_size = os.path.getsize(src)

        # POSITIVE 1 -- a true copy verifies.
        def t_good():
            dst = os.path.join(tmpd, "good.jsonl")
            shutil.copy2(src, dst)
            got = verify_copy(src, dst, src_sha, src_size)
            assert got == src_sha, "true copy did not verify"

        check("positive: identical copy verifies", t_good)

        # NEGATIVE 1 -- THE BUG. Empty destination against non-empty source.
        def t_empty():
            dst = os.path.join(tmpd, "empty.jsonl")
            open(dst, "wb").close()
            try:
                verify_copy(src, dst, src_sha, src_size)
            except VerifyError as exc:
                assert "EMPTY" in str(exc), f"wrong reason: {exc}"
                return
            raise AssertionError("EMPTY destination was accepted -- the null-compare bug is live")

        check("negative: empty destination REJECTED (the two-nulls case)", t_empty)

        # NEGATIVE 2 -- two empty files must not verify each other.
        def t_two_nulls():
            a = os.path.join(tmpd, "null_a")
            b = os.path.join(tmpd, "null_b")
            open(a, "wb").close()
            open(b, "wb").close()
            # Verified against a NON-empty source's digest/size: must fail on size.
            try:
                verify_copy(a, b, src_sha, src_size)
            except VerifyError as exc:
                assert "size mismatch" in str(exc) or "EMPTY" in str(exc), f"wrong reason: {exc}"
                return
            raise AssertionError("two nulls compared equal -- exactly Personal's bug")

        check("negative: two empty files do NOT verify as a real copy", t_two_nulls)

        # NEGATIVE 3 -- same size, corrupted bytes. Only the hash can catch this.
        def t_corrupt():
            dst = os.path.join(tmpd, "corrupt.jsonl")
            bad = bytearray(payload)
            bad[len(bad) // 2] ^= 0xFF
            with open(dst, "wb") as fh:
                fh.write(bytes(bad))
            try:
                verify_copy(src, dst, src_sha, src_size)
            except VerifyError as exc:
                assert "hash mismatch" in str(exc), f"wrong reason: {exc}"
                return
            raise AssertionError("same-size corruption was accepted")

        check("negative: same-size corrupted copy REJECTED", t_corrupt)

        # NEGATIVE 4 -- unreadable source must RAISE, not return a falsy sentinel.
        def t_unreadable():
            missing = os.path.join(tmpd, "does-not-exist")
            try:
                _digest(missing)
            except OSError:
                return
            raise AssertionError("_digest returned instead of raising on an unreadable file")

        check("negative: unreadable source raises (no falsy sentinel)", t_unreadable)

        # NEGATIVE 5 -- a malformed digest must be rejected.
        def t_baddigest():
            dst = os.path.join(tmpd, "good2.jsonl")
            shutil.copy2(src, dst)
            for junk in (None, "", "MATCH", "x" * 64):
                try:
                    verify_copy(src, dst, junk, src_size)
                except VerifyError:
                    continue
                raise AssertionError(f"malformed digest accepted: {junk!r}")

        check("negative: malformed digest rejected", t_baddigest)

        # NEGATIVE 6 -- the write fence refuses paths outside the capture root.
        def t_fence():
            outside = os.path.join(STORE_ROOT, "should-never-be-written.txt")
            try:
                _assert_write_target(outside)
            except VerifyError as exc:
                assert "REFUSED" in str(exc)
                return
            raise AssertionError("write fence allowed a path inside the live store")

        check("negative: write fence refuses the live store", t_fence)

        # POSITIVE 2 -- a genuinely empty source is legitimately capturable.
        def t_empty_src():
            a = os.path.join(tmpd, "zero_src")
            b = os.path.join(tmpd, "zero_dst")
            open(a, "wb").close()
            open(b, "wb").close()
            got = verify_copy(a, b, EMPTY_SHA256, 0)
            assert got == EMPTY_SHA256, "legitimately empty file failed to verify"

        check("positive: genuinely empty source still verifies", t_empty_src)

        # POSITIVE 3 -- subagent classification is one level down.
        def t_classify():
            assert classify("proj/abc-123.jsonl") == "session", "session misclassified"
            assert (
                classify("proj/abc-123/subagents/agent-a1.jsonl") == "subagent"
            ), "subagent misclassified -- a flat copy would miss these"
            assert classify("proj/memory/MEMORY.md") == "memory", "memory misclassified"

        check("positive: subagents classified one level down", t_classify)

    finally:
        CAPTURE_ROOT = saved_root
        shutil.rmtree(tmpd, ignore_errors=True)

    print("=== session_store_capture self-test ===")
    for name, ok, why in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {why}" if why else ""))
    passed = sum(1 for _n, ok, _w in results if ok)
    print(f"\nRESULT: {passed}/{len(results)} PASS")
    return 0 if passed == len(results) else 1


# --------------------------------------------------------------------------- main


def main(argv):
    if "--self-test" in argv:
        return self_test()
    verbose = "--verbose" in argv
    measure_only = "--measure" in argv
    reconcile = True if "--reconcile" in argv else None
    counts, by_kind, failures, elapsed = capture(
        verbose=verbose, measure_only=measure_only, reconcile=reconcile
    )
    report(counts, by_kind, failures, elapsed, measure_only=measure_only)
    # Hooks must not block the session on a capture problem; the log and stdout carry it.
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
