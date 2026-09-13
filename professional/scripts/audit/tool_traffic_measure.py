#!/usr/bin/env python3
"""Measure tool traffic in a rendered session transcript — THE REVIEWER'S INSTRUMENT, with its own
known defects declared, because it did not have them declared and that was the finding.

⛔ WHY THIS FILE EXISTS AT ALL. On 2026-09-07 this seat graded a peer trunk's chunk policy all
afternoon using these two regexes, and they lived ONLY in throwaway shell heredocs. They were the
yardstick for every number in the review and they had never been committed, never diffed against
anything, and never reviewed. The peer handed over its own removed-span offsets and invited a check;
the byte-set diff found that **the reviewer's rule was the one that over-dropped**.

  A REVIEWER'S INSTRUMENT IS ALSO AN IMPLEMENTATION, AND NOBODY REVIEWS IT.

⚠️ **And the cost was not hypothetical.** The reviewer suggested a wider section terminator as a
candidate cause; the author implemented it and it over-dropped by 21.8 points before being reverted.
The diff below shows why it was suggested: **the reviewer's own regex effectively has that bug.**
The author implemented the reviewer's defect on the reviewer's recommendation. That cost sits on the
reviewer's side of the ledger, and a review that never diffs its own instrument cannot see it.

⛔ TWO KNOWN DEFECTS, DECLARED SO EVERY NUMBER THIS FILE PRODUCES CARRIES THEM. They are NOT fixed to
agree with the implementation being graded — making a yardstick agree with the thing it measures is
the same act as tuning a proxy, which is the defect this whole exchange was about.

  D1  OVER-DROPS: `## Tool Result` sections terminate on the next `## `, but these transcripts use
      `### ` subheadings, so a section span can run past its payload into the prose that follows.
      `[measured on a86404]` 2,298 B in exactly two regions — a `### CFL — predecessor …` block and
      a `### STALE banner` documentation section. Both prose. Both wrongly counted as tool traffic.

  D2  UNDER-DROPS: the payload fence must begin within 200 chars of its `[tool_use]` marker.
      `[measured on a86404]` one real payload of 4,379 B sits outside that window and is missed.

  NET on a86404: this file reports **60.18%**; the graded implementation's own offsets give
  **60.91%**, and 60.91% is the better number. ⭐ **The superseded figure is MARKED, not averaged.**

Usage:
  python scripts/audit/tool_traffic_measure.py <transcript.md> [more.md ...]
  python scripts/audit/tool_traffic_measure.py --diff-spans <transcript.md> <spandump.tsv>
  python scripts/audit/tool_traffic_measure.py --selftest
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FENCE = re.compile(r"```[\s\S]*?```")
TOOL_RESULT = re.compile(r"## Tool Result[\s\S]*?(?=\n## |\Z)")   # carries D1
TOOL_USE = re.compile(r"\[tool_use[^\]]*\]")
FENCE_WINDOW = 200                                                # carries D2


def spans(text):
    """Removed spans under the two exact patterns. Returns [(start, end, kind)]."""
    out = [(m.start(), m.end(), "tool_result_section") for m in TOOL_RESULT.finditer(text)]
    for m in TOOL_USE.finditer(text):
        fm = FENCE.search(text, m.end())
        end = fm.end() if (fm and fm.start() - m.end() < FENCE_WINDOW) else m.end()
        out.append((m.start(), end, "tool_use_block"))
    return sorted(out)


def coverage(sp, n):
    """Byte SET, not a sum — spans overlap, and summing them over-counts. That non-additivity is
    exactly how one drop rate read 'closed' on one file and '+15.8' on another."""
    s = set()
    for a, b, _ in sp:
        s.update(range(a, min(b, n)))
    return s


def measure(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        t = fh.read()
    n = len(t)
    sp = spans(t)
    cov = coverage(sp, n)
    tr = len(coverage([x for x in sp if x[2] == "tool_result_section"], n))
    tu = len(coverage([x for x in sp if x[2] == "tool_use_block"], n))
    return dict(path=path, bytes=n, spans=len(sp), removed=len(cov),
                pct=100.0 * len(cov) / n if n else 0.0,
                tr_pct=100.0 * tr / n if n else 0.0,
                tu_pct=100.0 * tu / n if n else 0.0)


def diff_spans(path, dump):
    """Diff this instrument's spans against a graded implementation's own offsets.

    ⭐ This is the operation that found D1 and D2, and it is the operation a review owes itself:
    the instrument gets the same treatment as the thing it grades.
    """
    with open(path, encoding="utf-8", errors="replace") as fh:
        t = fh.read()
    n = len(t)
    theirs = []
    with open(dump, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            theirs.append((int(parts[0]), int(parts[1]), parts[-1].strip()))
    A, B = coverage(theirs, n), coverage(spans(t), n)
    print(f"file {os.path.basename(path)}  {n:,} B")
    print(f"  graded impl : {len(theirs):>5} spans  {len(A):>9,} B  {100.0*len(A)/n:6.2f}%")
    print(f"  this rule   : {len(spans(t)):>5} spans  {len(B):>9,} B  {100.0*len(B)/n:6.2f}%")
    print(f"  theirs\\mine : {len(A-B):>9,} B  ({100.0*len(A-B)/n:.2f}%)   <- D2 territory")
    print(f"  mine\\theirs : {len(B-A):>9,} B  ({100.0*len(B-A)/n:.2f}%)   <- D1 territory, PROSE")
    return 0


def selftest():
    ok = True

    def check(name, got, want):
        nonlocal ok
        good = got == want
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: got {got!r} want {want!r}")

    # D1 is REPRODUCED as a fixture, not fixed: a '### ' subheading does NOT stop the section, so
    # the prose after it is wrongly counted. Keeping this RED-by-design arm is the point -- a known
    # defect with a passing fixture is a lie.
    t = "## Tool Result\n\npayload\n\n### Subheading\n\nprose that is not tool traffic\n\n## Assistant\n\nx\n"
    cov = coverage(spans(t), len(t))
    check("D1 reproduced: '###' does not terminate the section",
          "prose that is not tool traffic" in "".join(c for i, c in enumerate(t) if i in cov), True)
    check("D1 bounded: '## Assistant' DOES terminate it",
          "\n## Assistant" in "".join(c for i, c in enumerate(t) if i not in cov), True)

    # D2 reproduced: a fence beyond the window is missed.
    far = "[tool_use: Bash]\n" + ("." * 400) + "\n```\npayload\n```\n"
    cov2 = coverage(spans(far), len(far))
    check("D2 reproduced: fence past the window is missed", "payload" in
          "".join(c for i, c in enumerate(far) if i not in cov2), True)
    near = "[tool_use: Bash]\n```\npayload\n```\n"
    cov3 = coverage(spans(near), len(near))
    check("D2 control: fence inside the window is caught", "payload" in
          "".join(c for i, c in enumerate(near) if i in cov3), True)

    # Coverage is a SET, never a sum.
    check("overlapping spans counted once", len(coverage([(0, 10, "a"), (5, 15, "b")], 20)), 15)

    print("selftest:", "ALL PASS" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--diff-spans", nargs=2, metavar=("TRANSCRIPT", "SPANDUMP"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.diff_spans:
        return diff_spans(*args.diff_spans)
    if not args.paths:
        ap.print_help()
        return 2

    print("⚠️ carries D1 (over-drops prose after a '###' subheading) and D2 (misses a fence past "
          "200 chars). See the module docstring; these are NOT fixed.")
    print(f"{'file':<46}{'bytes':>12}{'TR%':>8}{'TU%':>8}{'tool total%':>13}")
    for p in args.paths:
        try:
            m = measure(p)
        except OSError as exc:
            print(f"{os.path.basename(p)[:44]:<46}  UNKNOWN: {exc}")
            continue
        print(f"{os.path.basename(p)[:44]:<46}{m['bytes']:>12,}{m['tr_pct']:>7.1f}%"
              f"{m['tu_pct']:>7.1f}%{m['pct']:>12.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
