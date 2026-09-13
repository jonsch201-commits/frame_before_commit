#!/usr/bin/env python3
"""Partition the extractor's pending list into QUIESCENT and LIVE, by observed mtime movement.

Used only by `su_close.sh`. It exists as a file rather than an inline heredoc so that the join
key is testable: `--self-test` proves the key built here matches the key `snap_mtimes` writes.
A join that silently matches nothing is this repo's signature failure — `cc_corpus_gap.py` read
`source_id:` while 26 extracts declared `uuid:` and reported all of them LOST. It was not finding
losses. It was finding a field name.

Argv: <pending-output-file> <live-keys-file>
Prints: "<quiescent_sessions> <live_sessions> <quiescent_subagents> <live_subagents>"

WHY THE PARTITION EXISTS
------------------------
A stale extract on a QUIESCENT session is neglect — a real loss class that must reach zero.
A stale extract on a LIVE session is physics — the file grew while we were reading it, and no
amount of diligence drives that to zero. Merged into one row, the row can never go green, which
builds an alarm whose steady state is "firing". Partitioned, each half is actionable.
"""
import re
import sys

SUB = re.compile(r"^  \[(?:EXTRACT|REFRESH)\] sub ([0-9a-f]{6})/([0-9a-f]{6})")
TOP = re.compile(r"^  \[(?:EXTRACT|REFRESH)\] ([0-9a-f]{6})")


def partition(pending_lines, live):
    """Return (quiescent_sessions, live_sessions, quiescent_subagents, live_subagents)."""
    q_s = l_s = q_b = l_b = 0
    for line in pending_lines:
        m = SUB.match(line)
        if m:
            key = m.group(1) + "/" + m.group(2)
            if key in live:
                l_b += 1
            else:
                q_b += 1
            continue
        m = TOP.match(line)
        if m:
            if m.group(1) in live:
                l_s += 1
            else:
                q_s += 1
    return q_s, l_s, q_b, l_b


def self_test():
    """Prove the partition can put an item in EITHER bucket, and that the key shape matches."""
    lines = [
        "  [EXTRACT] aaaaaa  (no markdown)  project=fl\n",
        "  [REFRESH] bbbbbb  (jsonl newer)  project=fl\n",
        "  [EXTRACT] sub aaaaaa/cccccc  (no markdown)  project=fl\n",
        "  [REFRESH] sub dddddd/eeeeee  (jsonl newer)  project=fl\n",
        "Sessions  — New: 0  Refreshed: 0  Skipped: 0  EMPTY: 0  Failed: 0\n",
    ]
    cases = []
    # Nothing live -> everything is neglect.
    cases.append(("no live keys -> all quiescent", (2, 0, 2, 0), partition(lines, set())))
    # Everything live -> nothing blocks. This is the row that must not be able to fire forever.
    cases.append(("all live -> all physics", (0, 2, 0, 2),
                  partition(lines, {"aaaaaa", "bbbbbb", "aaaaaa/cccccc", "dddddd/eeeeee"})))
    # The interesting one: a live SESSION whose SUBAGENT is quiescent, and vice versa.
    cases.append(("mixed split", (1, 1, 1, 1), partition(lines, {"aaaaaa", "dddddd/eeeeee"})))
    # NEGATIVE CONTROL on the join key. A subagent key built the wrong way (agent id alone, or
    # the full uuid instead of 6 chars) matches nothing and every item reads quiescent — the
    # failure would be silent and would look like a finding.
    cases.append(("wrong-shaped key matches nothing", (2, 0, 2, 0),
                  partition(lines, {"cccccc", "eeeeee", "aaaaaaaaaa/cccccccccc"})))
    bad = 0
    print("=== _su_close_partition SELF-TEST ===")
    for name, want, got in cases:
        ok = want == got
        bad += 0 if ok else 1
        print("  %-42s %s%s" % (name, "PASS" if ok else "FAIL",
                                "" if ok else "  want %s got %s" % (want, got)))
    print("\nRESULT: %s — %d/%d" % ("PASS" if not bad else "FAIL", len(cases) - bad, len(cases)))
    return 1 if bad else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    if len(sys.argv) < 3:
        print("usage: _su_close_partition.py <pending-file> <live-keys-file>", file=sys.stderr)
        return 2
    try:
        lines = open(sys.argv[1], encoding="utf-8", errors="ignore").readlines()
    except OSError as e:
        print("cannot read pending file: %s" % e, file=sys.stderr)
        return 2
    live = set()
    try:
        live = {l.strip() for l in open(sys.argv[2], encoding="utf-8") if l.strip()}
    except OSError:
        pass  # no observations is not an error; it means nothing moved, so nothing is live
    print("%d %d %d %d" % partition(lines, live))
    return 0


if __name__ == "__main__":
    sys.exit(main())
