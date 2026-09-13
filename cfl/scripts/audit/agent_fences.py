#!/usr/bin/env python3
"""Assert every agent definition carries the standing fences block.

WHY THIS EXISTS
---------------
On 2026-07-26 four failures recurred all session — a verification run against a missing `raw/`
(three invalid results), a stale `index.lock` (four occurrences), agents exhausting budget before
landing anything (three total losses of completed work), and alarming subagent *explanations*
adopted without checking (two of four were wrong, one destructively).

Every one of those had a known countermeasure. **None was written into any agent definition.**
They lived in whichever brief the coordinator happened to write, so they applied when remembered
and vanished when not — and the one time `--raw-root` was forgotten, it cost an hour and produced
a confident false alarm.

Appending the block to nine files fixes today. **This script is what keeps it fixed**: a tenth
agent added without the fences fails the gate instead of quietly shipping without them. Same
doctrine as the skills digest — the fix is the deriving mechanism, not the derived state.

WHY IT CHECKS MARKERS AND NOT A HASH
------------------------------------
A hash would flag any edit, including a legitimate improvement to the block's wording, and would
train everyone to re-bless it without reading. Instead it asserts the presence of the small set of
**load-bearing markers** — the specific fences that were actually violated. The wording may improve
freely; the fences may not silently disappear.

Usage:
    python scripts/audit/agent_fences.py            # report
    python scripts/audit/agent_fences.py --strict   # exit 1 if any definition is missing a fence

Exit: 0 all present (or report-only), 1 under --strict when any is missing, 2 if no defs found.
"""
import argparse
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Marker -> the failure it prevents. Both are printed, because a fence whose reason is not
# stated gets deleted by the next person who finds it inconvenient.
REQUIRED = [
    ("add -f",     "raw/ is Jon's personal history; force-adding it is irreversible and external"),
    ("--raw-root", "a worktree has no raw/; verifying without it produces confident false findings"),
    ("index.lock", "stale lock presents as mass deletions; reset --hard during recovery loses work"),
    ("LAND FIRST", "three agents exhausted budget mid-task and landed nothing"),
    ("TALLY",      "subagent counts were right and explanations wrong, twice in four findings"),
    ("route UP as a decision",
                   "Jon asked a question with no recommendation attached answered 'I don't know "
                   "how we should count it' — unfinished staff work, not delegation"),
    ("Do not stop with work available",
                   "the pause failure fired at two independent coordinators in one night; six "
                   "messages spent restarting one of them"),
    ("deposited as a file",
                   "LOGGED meant 'mention it in the report'; proposals died at compaction — only "
                   "2 of several raised in one session were ever acted on"),
    ("Enumerate before concluding absence",
                   "'it is not there' was wrong three times in one session"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--glob", default=".claude/agents/*.md")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(a.root, a.glob)))
    if not paths:
        print(f"ERROR: no agent definitions matched {a.glob!r} under {a.root!r}", file=sys.stderr)
        return 2

    print(f"=== AGENT FENCES — {len(paths)} definition(s) ===\n")
    bad = 0
    for p in paths:
        text = open(p, encoding="utf-8", errors="ignore").read()
        missing = [(m, why) for m, why in REQUIRED if m not in text]
        name = os.path.basename(p)
        if missing:
            bad += 1
            print(f"  MISSING  {name}")
            for m, why in missing:
                print(f"             - {m!r} — {why}")
        else:
            print(f"  ok       {name}")

    print()
    if bad:
        print(f"{bad} of {len(paths)} definition(s) are missing a standing fence.")
        print("Append the block from another definition rather than paraphrasing it — the point")
        print("is that every agent gets the SAME fences, not a similar-sounding set.")
        return 1 if a.strict else 0
    print(f"All {len(paths)} definitions carry every standing fence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
