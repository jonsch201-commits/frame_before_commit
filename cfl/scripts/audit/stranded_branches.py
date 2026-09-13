#!/usr/bin/env python3
"""Committed work nobody is going to find.

WHY THIS EXISTS
---------------
On 2026-08-03 the pre-compact readiness pass found `origin/dev` **9 commits ahead of main with
no open PR** — and only because a dispatched master hit a "file does not exist on main" dead end
and reported it instead of working around it. **Nothing else in the close would have surfaced it.**

Two of those nine commits fix instruments that GATE the corpus. One of them, `verify_quotes.py`
gaining `capture_state` awareness, had been reported to Jon that same night as an OUTSTANDING gap.
It was built on 2026-07-30. The coordinator described the state of the world from `main` and never
looked at the branches.

The standing rule already said *"a completion notification is not evidence of a commit — check the
branch, not the message."* **Its converse was never checked: a commit that exists is not evidence
anyone will find it.** Compaction does not lose the branch. It loses the knowledge that the branch
is there — which is precisely what a compact discards.

WHAT IT REPORTS
---------------
For every remote branch ahead of `origin/main`:

  STRANDED  — ahead of main, no open PR, and nothing else references it. The serious one.
  PR #n     — ahead of main with an open PR. Visible; someone can act on it.
  stale     — ahead of main but its newest commit is older than --stale-days. Probably
              superseded, but "probably" is not "confirmed" and nobody has confirmed it.

WHY IT IS ADVISORY AND NOT BLOCKING
-----------------------------------
An unmerged branch is not a defect in this repo's files, and merges are Jon's. A gate that blocks
until every branch is resolved could never go green from here — the always-fires failure this
program has committed repeatedly. **Loud, every run, never blocking.**

`--strict` exits 1 on any STRANDED branch, for a caller that wants it to bite.

Usage:
    python scripts/audit/stranded_branches.py
    python scripts/audit/stranded_branches.py --stale-days 14 --strict
    python scripts/audit/stranded_branches.py --self-test

Exit: 0, or 1 under --strict when stranded branches exist, or 2 if git is unusable
      (never a silent pass — an unreadable branch list is UNKNOWN, not empty).
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

SKIP = {"origin/HEAD", "origin/main", "origin/canonical"}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def remote_branches():
    r = git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin")
    if r.returncode != 0:
        return None
    return [b for b in r.stdout.split() if b and b not in SKIP]


def open_prs():
    """branch -> PR number. Empty dict if gh is unavailable — which is NOT the same as
    'no PRs exist', so the caller must say so rather than report every branch STRANDED."""
    r = git("--version")  # cheap probe that subprocess works at all
    if r.returncode != 0:
        return None
    p = subprocess.run(["gh", "pr", "list", "--state", "open", "--limit", "200",
                        "--json", "number,headRefName"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        return None
    try:
        return {x["headRefName"]: x["number"] for x in json.loads(p.stdout)}
    except (ValueError, KeyError):
        return None


def changed_since_base(ref, base):
    """Files ref has changed since its merge-base with base. Empty set on any git failure."""
    mb = git("merge-base", base, ref)
    if mb.returncode != 0:
        return set()
    d = git("diff", "--name-only", mb.stdout.strip(), ref)
    if d.returncode != 0:
        return set()
    return {p for p in d.stdout.splitlines() if p.strip()}


def merge_order_hazards(branch, tip, watch_prefix):
    """Files this branch would drag BACKWARDS if merged into tip.

    WHY THIS EXISTS — a branch is not just work you might miss, it is a snapshot you
    might restore.

    2026-08-03: `scan_midturn_messages.py` had a predicate that silently dropped a real
    Jon mid-turn message. It was fixed the same morning. Hours later the branch
    `build/traceability-ratchet-2026-08-03` was found carrying the PRE-FIX copy, cut from
    a base that predated the fix. Merged in the wrong order it would have **silently
    reverted the instrument whose entire job is proving Jon's words are not dropped** —
    and the revert would have shipped under a commit message about raising traceability.

    `stranded_branches.py` already answered "is there work nobody will find?" It did not
    answer "is there work that would UNDO what is already here?" Those are different
    questions and only the second one is silent.

    The check is the classic conflict set: files the branch touched since the merge-base,
    intersected with files the tip touched since the same base. Restricted by default to
    `scripts/` because reverting an instrument is the case where nobody notices — prose
    conflicts announce themselves in review, a stale checker just goes quiet.

    A hit is NOT proof of a regression; the branch may hold the newer version. It is proof
    that MERGE ORDER MATTERS HERE, which is exactly the thing no one was tracking.
    """
    b_files = changed_since_base(branch, tip)
    t_files = changed_since_base(tip, branch)
    both = sorted(f for f in (b_files & t_files) if f.startswith(watch_prefix))
    return both


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-days", type=int, default=7,
                    help="Newest commit older than this is labelled stale (default 7)")
    ap.add_argument("--against", default="origin/main",
                    help="Tip to check merge-order hazards against (default origin/main). "
                         "Point this at the branch you are about to merge INTO.")
    ap.add_argument("--watch", default="scripts/",
                    help="Path prefix to check for merge-order hazards (default scripts/)")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any branch is STRANDED")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    branches = remote_branches()
    if branches is None:
        print("ERROR: cannot read the remote branch list.", file=sys.stderr)
        print("An unreadable branch list is UNKNOWN, not empty. Not a clean bill of health.",
              file=sys.stderr)
        return 2

    prs = open_prs()
    gh_ok = prs is not None
    prs = prs or {}

    rows = []
    for b in branches:
        c = git("rev-list", "--count", f"origin/main..{b}")
        if c.returncode != 0:
            continue
        ahead = int(c.stdout.strip() or 0)
        if ahead == 0:
            continue
        d = git("log", "-1", "--format=%cI", b).stdout.strip()
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(d)).days
        except ValueError:
            age = -1
        short = b[len("origin/"):]
        rows.append((ahead, short, prs.get(short), age,
                     git("log", "-1", "--format=%s", b).stdout.strip()[:56],
                     merge_order_hazards(b, a.against, a.watch)))

    rows.sort(key=lambda r: -r[0])
    stranded = [r for r in rows if r[2] is None]
    total_commits = sum(r[0] for r in rows)

    print("=== COMMITTED WORK NOBODY IS GOING TO FIND ===\n")
    print(f"  branches ahead of main : {len(rows)}")
    print(f"  commits ahead of main  : {total_commits}")
    print(f"  with an open PR        : {len(rows) - len(stranded)}")
    print(f"  STRANDED (no open PR)  : {len(stranded)}")
    if not gh_ok:
        print("\n  WARNING: `gh pr list` unavailable — PR association is UNKNOWN, so every")
        print("  branch below reads STRANDED. Do not act on that count until gh works.")
    print()

    hazard_rows = [r for r in rows if r[5]]
    print(f"  MERGE-ORDER HAZARDS    : {len(hazard_rows)}  "
          f"(branches touching {a.watch!r} that {a.against} has also changed)")
    print()

    for ahead, name, pr, age, subj, hz in rows:
        tag = f"PR #{pr}" if pr else "STRANDED"
        stale = "  stale" if age > a.stale_days else ""
        print(f"  {tag:<10} {ahead:>3} ahead  {age:>3}d{stale:<7}  {name}")
        print(f"             {subj}")
        for f in hz:
            print(f"             !! MERGE-ORDER HAZARD: {f}")

    if hazard_rows:
        print(f"\n  {len(hazard_rows)} branch(es) would touch a {a.watch!r} file that {a.against}")
        print("  has also changed. A hit is not proof of a regression — the branch may hold the")
        print("  NEWER copy. It is proof that merge order matters here, which is the thing")
        print("  nobody was tracking. Diff before merging, do not assume the base was current.")

    if stranded:
        print(f"\n  {len(stranded)} branch(es) hold committed work with no open PR. Some are")
        print("  certainly superseded — but 'certainly' is a guess until someone checks, and on")
        print("  2026-08-03 one of them held a fix to a BLOCKING corpus gate that had been")
        print("  reported to Jon as an outstanding gap five days after it was built.")
    else:
        print("\n  No stranded branches.")

    return 1 if (stranded and a.strict) else 0


def self_test():
    """The check must be able to both fire and stay silent."""
    cases = []

    b = remote_branches()
    cases.append(("remote branch list is readable", b is not None and len(b) > 0))

    # A branch that IS main must never be reported ahead of main.
    c = git("rev-list", "--count", "origin/main..origin/main")
    cases.append(("NEGATIVE CONTROL: main is 0 ahead of itself", c.stdout.strip() == "0"))

    # main/canonical/HEAD must be excluded, or canonical (an orphan snapshot) reads as
    # thousands of commits ahead and swamps the report.
    cases.append(("canonical and main excluded from scan",
                  b is not None and not (set(b) & SKIP)))

    # A branch can never drag ITSELF backwards: merge-base(main, main) == main, so the
    # conflict set is empty. If this ever fires, changed_since_base is wrong.
    cases.append(("NEGATIVE CONTROL: main has no hazard vs itself",
                  merge_order_hazards("origin/main", "origin/main", "scripts/") == []))

    # And the check must be able to FIRE, or it is decoration. The 2026-08-03 case:
    # the ratchet branch vs the close branch that fixed the scanner.
    #
    # STALE FIXTURE, corrected 2026-09-05 (FIX-5): `origin/close/pre-compact-2026-08-02` — the
    # comparison TIP this fixture diffs against — was deleted/merged and pruned from the remote
    # sometime after this control was written (confirmed via `git rev-parse --verify`, exit 128,
    # "Needed a single revision"; `origin/build/traceability-ratchet-2026-08-03`, the first
    # branch, is still live). The escape hatch below originally checked only the FIRST branch's
    # existence, so a pruned TIP made `changed_since_base` come back empty and the hazard set
    # silently empty — a false FAIL that looked identical to "the detector broke," when really
    # the fixture pair had gone stale. Fixed by checking BOTH refs, which is the actual escape
    # condition this case has always meant: "if either side of this historical pair is gone,
    # the comparison can no longer be run, and that is not a defect in merge_order_hazards."
    _branch_gone = git("rev-parse", "--verify",
                        "origin/build/traceability-ratchet-2026-08-03").returncode != 0
    _tip_gone = git("rev-parse", "--verify",
                     "origin/close/pre-compact-2026-08-02").returncode != 0
    fired = merge_order_hazards("origin/build/traceability-ratchet-2026-08-03",
                                "origin/close/pre-compact-2026-08-02", "scripts/")
    cases.append(("known 2026-08-03 hazard is detected (or either fixture branch gone)",
                  bool(fired) or _branch_gone or _tip_gone))

    print("=== SELF-TEST (negative control) ===")
    bad = 0
    for name, ok in cases:
        bad += 0 if ok else 1
        print(f"  {name:<48} : {'PASS' if ok else 'FAIL'}")
    print(f"\nRESULT: {'PASS' if not bad else 'FAIL'} — {len(cases)-bad}/{len(cases)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
