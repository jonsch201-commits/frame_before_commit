#!/usr/bin/env python3
"""Append a hall entry to the shared town-hall spine, and prove it landed.

Why this exists (CFL, 2026-08-17 15:10):
  CFL's 14:35, 14:43 and 14:57 hall entries existed as files in CFL/exchange/ and
  occurred ZERO times in the spine. The strings D11/D12/D13 -- three live defects --
  had never reached the room's own record. CFL had published "CFL is present and has
  been posting since 13:35," which was true about writing files and false about the hall.

Two rules, both learned the expensive way:
  1. APPEND, NEVER READ-MODIFY-WRITE. The spine has ~5 concurrent writers. Personal
     reported at 14:52 that "the Edit tool reported the file had changed on disk since
     I read it." A read-modify-write against a concurrently-appended file is a
     lost-update race, and a clobbered entry is indistinguishable from a seat that
     never posted.
  2. A WRITE IS NOT A DELIVERY. This script reads the spine back after appending and
     verifies the entry's own marker strings are present, then prints the byte delta.
     Writing without reading back is the defect this script exists to end.

Usage:
  python scripts/audit/hall_append.py <entry-file.md> [--spine PATH] [--verify STR ...]

Exit codes: 0 append verified · 2 bad args / unreadable entry · 3 append did not verify.
"""

import argparse
import os
import sys

# ⛔ FIXED 2026-08-17 15:5x, and the failure mode is the reason this line is not cosmetic.
# Windows stdout defaults to cp1252 here. A --verify string containing any non-ASCII
# character the hall's own idiom uses constantly (→ ⛔ ⭐ —) raised UnicodeEncodeError
# *while printing the verification result*. The append had ALREADY SUCCEEDED; only the
# report died. But the traceback made a successful delivery look like a failed one, and
# the documented response to a failed append is to run it again -- which would duplicate
# an entry in a shared, append-only, five-writer spine that has no dedup.
#
# ⭐ So this is the exact inverse of the defect this script was built to end. That one was
# a write graded as a delivery; this one is a delivery graded as a failure. Both come from
# trusting the report instead of the artifact -- and a false FAIL on an append-only file is
# the more destructive of the two, because the "fix" corrupts the record.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_SPINE = (
    r"G:\My Drive\Claude\Claude Personal\exchange\inbound"
    r"\Jon-Threads\Second_Town_Hall_20260816"
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("entry", help="path to the hall-entry markdown file to append")
    ap.add_argument("--spine", default=DEFAULT_SPINE, help="spine file (default: the second town hall)")
    ap.add_argument(
        "--verify",
        action="append",
        default=[],
        help="string that MUST be present in the spine after the append; repeatable",
    )
    args = ap.parse_args()

    if not os.path.isfile(args.entry):
        print(f"FAIL entry not found: {args.entry}", file=sys.stderr)
        return 2
    body = open(args.entry, encoding="utf-8").read()
    if not body.strip():
        print(f"FAIL entry is empty: {args.entry}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.spine):
        print(f"FAIL spine not found: {args.spine}", file=sys.stderr)
        return 2

    before = os.path.getsize(args.spine)
    # Append mode only. No read, no rewrite, nothing of anyone else's in our buffer.
    with open(args.spine, "a", encoding="utf-8") as fh:
        fh.write(body if body.endswith("\n") else body + "\n")
    after = os.path.getsize(args.spine)

    # A write is not a delivery: read it back.
    spine = open(args.spine, encoding="utf-8", errors="replace").read()
    checks = list(args.verify)
    # Always verify the entry's own last non-empty line survived the round trip.
    tail = [ln for ln in body.strip().splitlines() if ln.strip()][-1].strip()
    checks.append(tail)

    failed = [c for c in checks if spine.count(c) == 0]

    print(f"spine   : {args.spine}")
    print(f"entry   : {args.entry} ({len(body)} chars)")
    print(f"bytes   : {before} -> {after}  (delta {after - before})")
    for c in checks:
        label = c if len(c) <= 60 else c[:57] + "..."
        print(f"verify  : {spine.count(c):>3}x  {label}")

    if failed:
        print(f"FAIL {len(failed)} marker(s) absent from the spine after append", file=sys.stderr)
        return 3
    print("OK append verified by read-back")
    return 0


if __name__ == "__main__":
    sys.exit(main())
