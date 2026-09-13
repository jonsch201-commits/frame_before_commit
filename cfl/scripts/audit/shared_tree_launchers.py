#!/usr/bin/env python3
"""Enumerate every executable in the shared Claude tree that a woken seat could run.

WHY THIS EXISTS (CFL, 2026-08-17 16:3x).
  The Secretary's D17 (operator multiplication) was fixed by putting a single-instance lock on
  `relaunch-switchboard-v2.sh`. Its stated cause was broader than the fix:

      "every woken trunk session runs with acceptEdits and can reach relaunch-switchboard-v2.sh
       in my tree ... an instrument's launcher is reachable by every seat the instrument wakes.
       A one-shot script in a shared tree WILL be run by somebody who means well."

  That sentence ranges over every launcher in G:\\My Drive\\Claude, and nothing had ever counted
  them. Per the standing amendment, a stated cause needs a disposition -- fixed, ticketed, or
  declined -- and "annotation is not a disposition." This is the denominator that lets the ticket
  be closed against a list instead of against a feeling.

  MISSING ARTIFACT, NOT MISSING INSIGHT. The insight was already written down, by its author,
  in the same file as the fix. What did not exist was the list.

  ⭐ Its first useful output was D20: `G:\\My Drive\\Claude\\Switchboard.ps1` -- root level, fronted
  by a double-click .cmd wrapper, no lock guard -- launches `node relay.mjs`, the RETIRED v0 relay,
  two fixes after v0 was removed from the operator (D5) and from the relaunch script (D15).

WHAT IT DOES NOT DO, stated because a tool that hides its bound is what this program keeps building:
  - It does NOT grade idempotence. Deciding whether a given launcher is safe to double-run needs
    the owner of that tree; this only produces the population and flags obvious daemon-starters.
  - The DAEMON heuristic is a string match. It will miss a daemon started indirectly and will
    flag a script that merely mentions one. Treat a flag as "read this file", never as a verdict.
  - Excluded by design and named here rather than silently: `.claude-projects-backup` (harness
    shell snapshots, not launchers -- 72 of them, which would have tripled the count and meant
    nothing), `.venv`/`node_modules` (vendored), `extracted-*` (export payloads).

Usage:
  python scripts/audit/shared_tree_launchers.py [--root PATH] [--daemons-only] [--include-vendored]

Exit codes: 0 enumerated · 2 root unreadable.
"""

import argparse
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_ROOT = os.path.join("G:" + os.sep, "My Drive", "Claude")
EXTS = (".sh", ".ps1", ".cmd", ".bat")
SKIP_DIRS = {".claude-projects-backup", "node_modules", ".git", ".venv",
             ".understand-anything", "raw"}

# Things that start something long-lived, i.e. the class where a second run costs money or
# corrupts a shared record. Deliberately broad; every hit is a "go read it", not a finding.
DAEMON_MARKS = ("nohup", "start-process", "relay.mjs", "relay2.mjs", "relay3.mjs",
                "switchboard-operator", "claude -p", "& )", "--daemon")
# A launcher that already refuses to double-start. Absence is not proof of a defect.
GUARD_MARKS = ("lockdir", "instance.lock", "relay.lock", "kill -0", "REFUSING", "--force")


def classify(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            body = fh.read().lower()
    except Exception as exc:
        return None, None, f"unreadable: {exc}"
    daemon = sorted({m for m in DAEMON_MARKS if m in body})
    guard = sorted({m for m in GUARD_MARKS if m in body})
    return daemon, guard, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--daemons-only", action="store_true",
                    help="only rows that start something long-lived")
    ap.add_argument("--include-vendored", action="store_true",
                    help="do not skip .venv/node_modules/backup snapshots (inflates the count)")
    a = ap.parse_args()

    if not os.path.isdir(a.root):
        print(f"FAIL root unreadable: {a.root}", file=sys.stderr)
        return 2

    skip = set() if a.include_vendored else SKIP_DIRS
    rows = []
    for base, dirs, files in os.walk(a.root):
        dirs[:] = [d for d in dirs if d not in skip]
        if not a.include_vendored and "extracted-" in base:
            continue
        for f in files:
            if f.lower().endswith(EXTS):
                p = os.path.join(base, f)
                rows.append((os.path.relpath(p, a.root), p))
    rows.sort()

    total = len(rows)
    daemons, guarded, unreadable = [], [], []
    for rel, full in rows:
        d, g, err = classify(full)
        if err:
            unreadable.append((rel, err))
            continue
        if d:
            daemons.append((rel, d, g))
            if g:
                guarded.append(rel)

    print("=== shared-tree launcher census "
          "(the population the Secretary's D17 stated cause ranges over) ===")
    print(f"  root       : {a.root}")
    print(f"  extensions : {' '.join(EXTS)}")
    print(f"  excluded   : {'nothing (--include-vendored)' if a.include_vendored else ' '.join(sorted(SKIP_DIRS)) + ' extracted-*'}")
    print(f"  DENOMINATOR: {total} executables reachable by any seat with filesystem access")
    print(f"  of which start something long-lived: {len(daemons)}")
    print(f"  of those, carrying any single-instance guard: {len(guarded)}\n")

    print("  --- starts something long-lived ---")
    for rel, d, g in daemons:
        flag = "GUARD" if g else "  !! "
        print(f"    [{flag}] {rel}")
        print(f"             starts: {', '.join(d)}")
        if g:
            print(f"             guard : {', '.join(g)}")
    if not a.daemons_only:
        print("\n  --- everything else (no long-lived start detected) ---")
        for rel, full in rows:
            if not any(rel == r for r, _, _ in daemons) and not any(rel == r for r, _ in unreadable):
                print(f"    {rel}")
    if unreadable:
        print("\n  --- UNREADABLE (counted in the denominator, not classified) ---")
        for rel, err in unreadable:
            print(f"    {rel}  -- {err}")

    print("\n  [!] BOUND: the DAEMON/GUARD columns are string heuristics over file bodies, not")
    print("      analysis. A flag means READ THIS FILE. Idempotence is graded by the owner of")
    print("      the tree the launcher lives in -- this script only produces the denominator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
