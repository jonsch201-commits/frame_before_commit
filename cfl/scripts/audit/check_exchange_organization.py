#!/usr/bin/env python3
"""check_exchange_organization.py -- did exchange/ get LESS organized since the baseline?

WHY THIS EXISTS
----------------
Jon, 2026-08-15 18:09: "The single biggest issue I've felt is the wiki being unorganized. And
the exchange is MONDO unorganized last time I checked... ensure testing occurs by design."

Measured the same night, flat (unfiled) files sitting directly in exchange/ root:

    2026-08-01 :  72
    2026-08-08 : 158
    2026-08-12 : 169
    2026-08-14 : 200
    2026-08-15 : 235 (236-237 by the time this script was written -- see BASELINE file)

MONOTONIC. It has never once decreased, and nothing in scripts/ was reporting it. This is that
report -- a companion to scripts/audit/organize_exchange.py (the filing mechanism) and
scripts/audit/check_struck_gates.py (the pattern this file copies: report-only, positive
control, fail-closed on UNKNOWN, delta not level).

WHY IT IS A DELTA AND NOT A LEVEL
----------------------------------
This repo already retired one alarm -- RATIO_FLOOR -- for firing at a steady state that carried
no information ("an instrument that can never return clean is a mute button"). If this checker
demanded a flat count of ZERO it would fire on every run forever (the 594 files this repo
already measured tonight aren't getting bulk-moved tonight -- see
exchange/CFL-EXCHANGE-ORGANIZATION-SCHEME-2026-08-15.md for why) and Jon would rightly learn to
ignore it. So: a BASELINE file records the flat-file count (and the unfiled-deposit count under
inbound/outbound) at a point in time, and this script reports the DELTA against that baseline.
A regression is "the count went UP since the baseline was recorded," not "the count is nonzero."

WHAT COUNTS
-----------
Three numbers, each the count of FLAT files (not recursing into already-organized
subdirectories) directly inside:
  - exchange/           (root deposits)
  - exchange/inbound/   (cross-trunk inbound deposits)
  - exchange/outbound/  (cross-trunk outbound deposits)
These are exactly the three directories scripts/audit/organize_exchange.py scans -- the same
measurement instrument as the filing mechanism, so the two can never silently drift apart on
what "flat" means.

WHAT THIS DOES NOT DO
----------------------
It does not file anything (that is organize_exchange.py's job). It does not block anything --
there is no gate here, only a report, per this repo's standing rule (wiki/references/
struck-gates.md: "No blocking hook, and no gate on the gates").

Exit: 0 clean/no-regression (or baseline recorded) | 1 REGRESSION (flat count rose) |
      2 could not run (UNKNOWN dominates; missing baseline, unreadable dirs).
"""
import argparse
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BASELINE = os.path.join(HERE, "exchange_organization_baseline.txt")

SCAN_DIRS = ["exchange", "exchange/inbound", "exchange/outbound"]


def count_flat(repo_root, rel_dir):
    d = Path(repo_root) / rel_dir
    if not d.is_dir():
        return None
    return sum(1 for p in d.iterdir() if p.is_file())


def measure(repo_root):
    counts = {}
    for rel in SCAN_DIRS:
        n = count_flat(repo_root, rel)
        if n is None:
            return None
        counts[rel] = n
    counts["TOTAL"] = sum(counts.values())
    return counts


def load_baseline():
    try:
        raw = open(BASELINE, encoding="utf-8").read()
    except OSError:
        return None
    counts = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        try:
            counts[k] = int(v)
        except ValueError:
            continue
    if "TOTAL" not in counts:
        return None
    return counts


def write_baseline(counts, note=""):
    lines = [
        "# exchange_organization_baseline.txt -- flat (unfiled) file counts at record time.",
        "# Written by scripts/audit/check_exchange_organization.py --update-baseline.",
        "# A bare run compares CURRENT counts against these and reports the DELTA -- rising",
        "# above this baseline is a regression; falling below it is real filing progress and",
        "# should be re-recorded here (ratchet DOWN, never silently ratchet up).",
    ]
    if note:
        lines.append(f"# {note}")
    for rel in SCAN_DIRS:
        lines.append(f"{rel} = {counts[rel]}")
    lines.append(f"TOTAL = {counts['TOTAL']}")
    with open(BASELINE, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def positive_control():
    """Synthesize a regression in memory (no disk touched) and prove the comparator calls it
    one. A zero-delta result from a comparator never proven to fire is not evidence of health --
    it's indistinguishable from a comparator that cannot fire (cf. check_struck_gates.py)."""
    baseline = {"exchange": 235, "exchange/inbound": 258, "exchange/outbound": 100, "TOTAL": 593}
    synthetic_current = {"exchange": 235, "exchange/inbound": 258, "exchange/outbound": 101, "TOTAL": 594}
    delta = synthetic_current["TOTAL"] - baseline["TOTAL"]
    return delta > 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update-baseline", action="store_true",
                     help="Record CURRENT counts as the new baseline. Do this deliberately -- "
                          "ratcheting the baseline UP hides a regression instead of reporting it. "
                          "Only ratchet down (after real filing progress), or to record the very "
                          "first baseline.")
    ap.add_argument("--note", type=str, default="", help="Optional note stored in the baseline file.")
    args = ap.parse_args()

    fires = positive_control()
    print("=== check_exchange_organization ===")
    print(f"  positive ctrl : {'PASS -- comparator calls a synthetic +1 a regression' if fires else 'FAIL'}")
    if not fires:
        print("    A comparator that cannot detect a synthetic regression cannot be trusted on a", file=sys.stderr)
        print("    real one. Treat as UNKNOWN.", file=sys.stderr)
        return 2

    current = measure(REPO)
    if current is None:
        print("UNKNOWN: one or more of exchange/, exchange/inbound/, exchange/outbound/ is missing", file=sys.stderr)
        print("  or unreadable. A missing directory is not an empty one. Never a pass.", file=sys.stderr)
        return 2

    print(f"  current counts:")
    for rel in SCAN_DIRS:
        print(f"    {rel:22s} : {current[rel]}")
    print(f"    {'TOTAL':22s} : {current['TOTAL']}")

    if args.update_baseline:
        write_baseline(current, note=args.note)
        print(f"  baseline written -> {BASELINE}")
        return 0

    baseline = load_baseline()
    if baseline is None:
        print(file=sys.stderr)
        print("UNKNOWN: no baseline on disk. Run with --update-baseline once to record one.", file=sys.stderr)
        print("  No baseline is not a clean pass -- it means this check has never compared anything.", file=sys.stderr)
        return 2

    print()
    print(f"  baseline (recorded earlier):")
    for rel in SCAN_DIRS:
        b = baseline.get(rel, "?")
        print(f"    {rel:22s} : {b}")
    print(f"    {'TOTAL':22s} : {baseline['TOTAL']}")

    delta = current["TOTAL"] - baseline["TOTAL"]
    print()
    print(f"  DELTA (current - baseline) : {delta:+d}")

    if delta > 0:
        print()
        print(f"  REGRESSION: exchange/ flat-file total rose by {delta} since the baseline was recorded.")
        print(f"  This does not mean nothing was filed -- it means unfiled deposits are accumulating")
        print(f"  faster than anything is filing them. Run organize_exchange.py --report to see where.")
        return 1

    if delta < 0:
        print()
        print(f"  IMPROVEMENT: flat-file total fell by {-delta}. Consider --update-baseline to lock in")
        print(f"  the new floor (never ratchet the baseline UP -- only down, deliberately).")
    else:
        print()
        print("  UNCHANGED since baseline. Not a regression, but not progress either.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
