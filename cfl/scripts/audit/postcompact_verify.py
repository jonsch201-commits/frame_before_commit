#!/usr/bin/env python3
"""postcompact_verify.py -- CFL's summary READER for the PostCompact hook.

Jon, 2026-08-31 (verbatim, to Secretary and again to CFL): "please ensure this all
trunk standard update is indeed the default and not just the hoped outcome."

Professional's acceptance test (2026-08-31, via Secretary's correction letter):
"does anything READ the summary text, and CAN IT FAIL WHEN THE SUMMARY IS EMPTY."
This script exists to pass that test the honest way: it reads the compact summary
from the hook's stdin and grades it AGAINST DISK GROUND TRUTH -- the thing CFL's
design uniquely has (the record pipeline re-mints the verbatim window at wake, so
this reader checks the summary's pointers against artifacts, not against memory).

Checks (each states what it CANNOT detect):
  C1 live-map     every LIVE wayfinder map is REACHABLE after the barrier -- named in
                  the summary OR in exchange/WAKE.md. Named in neither = finding.
                  Re-aimed 2026-09-04 (CB-9); it previously demanded the summary
                  recite all 13 basenames, which correct behaviour could never satisfy.
                  (cannot-detect: a summary that names the map but garbles its state)
  C2 branch       summary names the current git branch.
                  (cannot-detect: a wrong SHA beside a right branch name)
  C3 spine        summary names the WAKE spine target's basename, when WAKE names one.
                  (cannot-detect: a stale spine in WAKE itself -- that is WAKE's defect)
  C4 quotes       up to 5 longest double-quoted spans (>=25 chars) in the summary each
                  literal-grep to >=1 hit in exchange/ or the newest window mds.
                  (cannot-detect: a faithful quote whose primary lives in another trunk
                  -- graded UNRESOLVED, never FAIL; the 2026-08-31 away-order case)
  C0 empty        an empty/absent summary is UNKNOWN, never clean (denominator floor;
                  the PASS-on-0-of-0 class, twice measured fleet-wide on 2026-08-31).

Verdicts: UNKNOWN (no summary) | FINDINGS(n) | CHECKED-FOUND-NONE.
Artifact: exchange/su-close/postcompact/<utc>-<session>.md -- always written.
Exit: always 0 (a hook failure must never block the wake; findings travel as the
artifact + stderr text, the Secretary convention, blemish stated in their letter).
EXIT 0 DOES NOT MEAN CLEAN -- READ THE ARTIFACT. UNKNOWN and FINDINGS both exit 0;
a consumer wiring `if exit == 0` believes an empty summary was a clean one. This
sentence is the Secretary-returned shared-ancestor fix (2026-08-31): two trunks
inherited exit-0-on-UNKNOWN from one ancestor, so the guard must live in the header
the next consumer-writer reads.
Selftest: selftest_postcompact_verify.py -- proves UNKNOWN, FINDINGS and
CHECKED-FOUND-NONE are all reachable (a check that cannot fail certifies nothing).
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def live_map_basenames(root: Path):
    names = []
    tracker = root / "wiki" / "tracker"
    if not tracker.is_dir():
        return names
    for f in tracker.glob("wayfinder-*.md"):
        try:
            head = f.read_text(encoding="utf-8", errors="ignore")[:2000]
        except OSError:
            continue
        # FRONTMATTER ONLY. Found 2026-09-01 21:3x by CFL at wake: the SUPERSEDED map
        # wayfinder-cfl.md quotes `status: "LIVE"` in its body prose (line 28), and a
        # regex over the first 2000 chars graded it LIVE -> a false finding on every
        # compact. The status field is read between the leading --- fences and nowhere else.
        fm = head
        if head.startswith("---"):
            end = head.find("\n---", 3)
            fm = head[:end] if end > 0 else head
        if "wayfinder:map" in fm and re.search(r'^status:\s*"?LIVE\b', fm, re.MULTILINE):
            names.append(f.name)
    return sorted(names)


def current_branch(root: Path):
    try:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def wake_spine_basename(root: Path):
    wake = root / "exchange" / "WAKE.md"
    if not wake.is_file():
        return ""
    txt = wake.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"SPINE\s+IS\s+`([^`]+)`", txt, re.IGNORECASE)
    return Path(m.group(1)).name if m else ""


def quoted_spans(summary: str, n=5, min_len=25):
    spans = [s for s in re.findall(r'"([^"\n]{%d,400})"' % min_len, summary)]
    spans.sort(key=len, reverse=True)
    return spans[:n]


def grep_quote(root: Path, span: str):
    """Literal search in exchange/ and the newest 10 window mds. True if >=1 hit."""
    targets = [root / "exchange"]
    win_dir = root / "raw" / "transcripts" / "claude-code" / "fl"
    wins = []
    if win_dir.is_dir():
        wins = sorted(win_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
    needle = span.strip()
    for base in targets:
        try:
            r = subprocess.run(["grep", "-rlF", "--include=*.md", needle, str(base)],
                               capture_output=True, text=True, timeout=120)
            if r.stdout.strip():
                return True
        except Exception:
            pass
    for w in wins:
        try:
            if needle in w.read_text(encoding="utf-8", errors="ignore"):
                return True
        except OSError:
            continue
    return False


def write_with_fallback(out_file, text):
    """Drive FS can throw transient OSError 22 on create (measured 2026-09-01: the 19:32
    boundary compact crashed here at line 214; minutes later the same post-reboot mount
    served Errno 22 to every reader of this very script and of .git/packed-refs, healing
    after ~6 min). Retry once, then fall back to LOCALAPPDATA so the verdict is never
    lost to a flaky mount. Returns the path actually written."""
    import os, time
    for attempt in (1, 2):
        try:
            out_file.write_text(text, encoding="utf-8", newline="\n")
            return out_file
        except OSError:
            if attempt == 1:
                time.sleep(1.0)
    from pathlib import Path
    alt = Path(os.environ.get("LOCALAPPDATA", ".")) / "claude" / "postcompact-fallback"
    alt.mkdir(parents=True, exist_ok=True)
    alt_file = alt / out_file.name
    alt_file.write_text(text + "\nWRITTEN-TO-FALLBACK: Drive write failed twice (OSError); "
                        "copy back to exchange/su-close/postcompact/ when the mount recovers.\n",
                        encoding="utf-8", newline="\n")
    return alt_file


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}
    summary = (payload.get("compact_summary") or payload.get("summary") or "").strip()
    session = (payload.get("session_id") or "unknown")[:8]
    trigger = payload.get("trigger") or "unknown"
    # microseconds in the name: two verdicts in one second must be two files, never an
    # overwrite (measured on this script's own first selftest -- 3 fixtures, 2 artifacts)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    out_dir = ROOT / "exchange" / "su-close" / "postcompact"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{ts}-{session}.md"

    # Compact counter (Secretary claude.ai ticket 2026-09-01): "times compacted" is not
    # obtainable in principle from inside a session -- the compact replaces the context that
    # would count. So the hook, which survives the boundary, increments a per-session integer
    # persisted OUTSIDE the transcript. Acceptance: a session reads N from disk without
    # reading its own transcript, and N survives the next compact. Append-only TSV (no
    # deletion; the current count is the max row for the session, so history is kept).
    counts_f = out_dir / "COMPACT-COUNTS.tsv"
    full_session = payload.get("session_id") or "unknown"
    prev = 0
    if counts_f.exists():
        for line in counts_f.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0] == full_session:
                try:
                    prev = max(prev, int(parts[1]))
                except ValueError:
                    pass
    count = prev + 1
    with counts_f.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"{full_session}\t{count}\t{ts}\t{trigger}\n")

    lines = [f"# PostCompact summary verification -- {ts} (trigger={trigger}, session={session}, times_compacted={count})",
             "", "Written by `scripts/audit/postcompact_verify.py` reading the summary from the",
             "hook's stdin and grading it against DISK ground truth. See script header for the",
             "cannot-detect bound of every check.", ""]

    if not summary:
        lines += ["## VERDICT: UNKNOWN -- no compact_summary received on stdin.",
                  "C1-C4 are UNVERIFIED this compact, not confirmed working. Not a pass.",
                  "(denominator floor -- the PASS-on-0-of-0 class)"]
        out_file = write_with_fallback(out_file, "\n".join(lines) + "\n")
        print(f"POSTCOMPACT-VERIFY: UNKNOWN (empty summary) -> {out_file}", file=sys.stderr)
        return 0

    findings = []
    checked = []

    # ------------------------------------------------------------------
    # C1 RE-AIMED 2026-09-04 (ticket CB-9). It used to ask: does the SUMMARY
    # name every LIVE wayfinder map? [m 2026-09-04] there are 13 LIVE maps and a
    # compact summary will essentially never list 13 filenames, so C1 emitted a
    # finding per unnamed map EVERY BARRIER, FOREVER. On 2026-09-04 that was 12
    # findings in one run, all identical in kind, and nothing consumed them.
    #
    # A check that correct behaviour cannot close has a signal worth nothing --
    # the EARS-COUNT / unlazy-G2 class this trunk already owns a receipt for.
    #
    # THE REAL QUESTION IS REACHABILITY, NOT RECITATION: after a compact, can the
    # seat GET to the live maps? The summary is one carrier; exchange/WAKE.md is
    # the other, and it is the durable one -- [m 2026-09-04] WAKE.md lines 14 and
    # 124 already name all 13. So a map named in EITHER is reachable, and only a
    # map named in NEITHER is a real finding.
    #
    # The summary-only misses are still REPORTED, as notes rather than findings,
    # because thinning the summary is a real (smaller) cost and hiding it would
    # trade one blind spot for another.
    # ------------------------------------------------------------------
    maps = live_map_basenames(ROOT)
    wake_text = ""
    # TEST-ONLY override so C1's negative direction is exercisable. Without it the
    # only way to prove this check can still FIRE is to mutate the real WAKE.md,
    # and a control you cannot run is not a control.
    wake_path = Path(os.environ["PCV_WAKE_PATH"]) if os.environ.get("PCV_WAKE_PATH")         else ROOT / "exchange" / "WAKE.md"
    try:
        wake_text = wake_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        # A carrier we could not read is UNKNOWN and UNKNOWN dominates: fall back
        # to the strict summary-only test rather than silently crediting WAKE.md.
        checked.append(f"C1 live-map: WAKE.md UNREADABLE ({e.__class__.__name__}) -- "
                       "falling back to summary-only; absence of a carrier is not a pass")

    summary_only_misses = []
    for m in maps:
        in_summary = m in summary
        in_wake = bool(wake_text) and m in wake_text
        if in_summary:
            checked.append(f"C1 live-map: `{m}` named in summary")
        elif in_wake:
            summary_only_misses.append(m)
        else:
            findings.append(
                f"C1 live-map: LIVE map `{m}` is reachable from NEITHER the summary "
                f"NOR exchange/WAKE.md -- role state for it is lost at this barrier")
    if summary_only_misses:
        checked.append(
            f"C1 live-map: {len(summary_only_misses)} LIVE map(s) absent from the summary but "
            f"named in exchange/WAKE.md, so reachable: "
            + ", ".join(f"`{m}`" for m in summary_only_misses[:6])
            + (" ..." if len(summary_only_misses) > 6 else ""))
    if not maps:
        checked.append("C1 live-map: no LIVE maps derivable (UNKNOWN, not pass)")

    br = current_branch(ROOT)
    if br:
        if br in summary:
            checked.append(f"C2 branch: `{br}` named")
        else:
            findings.append(f"C2 branch: current branch `{br}` NOT named in the summary")
    else:
        checked.append("C2 branch: git unreadable (UNKNOWN, not pass)")

    spine = wake_spine_basename(ROOT)
    if spine:
        if spine in summary:
            checked.append(f"C3 spine: `{spine}` named")
        else:
            findings.append(f"C3 spine: WAKE spine `{spine}` NOT named in the summary")
    else:
        checked.append("C3 spine: WAKE names no spine (nothing to check)")

    spans = quoted_spans(summary)
    unresolved = 0
    for s in spans:
        if grep_quote(ROOT, s):
            checked.append(f"C4 quote resolves: \"{s[:60]}...\"" if len(s) > 60 else f"C4 quote resolves: \"{s}\"")
        else:
            unresolved += 1
            checked.append(f"C4 quote UNRESOLVED in CFL tree (may be another trunk's primary): \"{s[:60]}\"")
    if not spans:
        checked.append("C4 quotes: no >=25-char quoted spans in summary (nothing to check)")

    verdict = f"FINDINGS ({len(findings)})" if findings else "CHECKED-FOUND-NONE"
    lines += [f"## VERDICT: {verdict}", ""]
    if findings:
        lines += ["### Findings (each = a load-bearing pointer the summary dropped)", ""]
        lines += [f"- {f}" for f in findings] + [""]
    lines += ["### Checks run", ""] + [f"- {c}" for c in checked]
    lines += ["", f"summary_chars: {len(summary)} | quoted_spans_sampled: {len(spans)} "
              f"| unresolved_quotes: {unresolved}"]
    out_file = write_with_fallback(out_file, "\n".join(lines) + "\n")
    print(f"POSTCOMPACT-VERIFY: {verdict} -> {out_file}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
