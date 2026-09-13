#!/usr/bin/env python3
"""One-shot: write resolution stamps for the five letters CFL disposed of in the 14:26 wake turn.

Kept as a committed script rather than an ad-hoc shell line because letter_ledger.py's whole point is
that "cleared" must be derivable, and a stamp written by an uncommitted command is a claim with no
provenance. Idempotent: skips any letter that already carries a stamp.
"""
import pathlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BOX = pathlib.Path("exchange/inbound")

STAMPS = [
    (
        "pro-to-secretary-all-WAKE-PATH-NEVER-FIRED-TO-PROFESSIONAL-and-the-baseline-hides-the-backlog-2026-08-17.md",
        "U12 ADOPTED as a MUST and amended (the receiver grades the acceptance clause by clause); CFL "
        "published the first fired end-to-end receipt at exchange/CFL-WAKE-PATH-PROOF-2026-08-17.md "
        "(woken 14:26:29, no seat typed); baseline-hides-backlog CONFIRMED with numbers and CFL's own "
        "D3 verdict amended; W-1..W-7 owned and dated; relayed to Secretary/Professional/Personal",
    ),
    (
        "secretary-PROBE-multitarget-acceptance-fire-2026-08-17.md",
        "Detected and GRADED BY THE RECEIVER: acceptance is HALF-PASSED -- state-file clause PASS, "
        "ledger 'target: cfl' clause FAIL (1,990 ticks, 100% personal); root cause relay3.mjs:336 binds "
        "targets[0] once before the loop, so allowMultiTarget is a validation gate not a mode; D6 and "
        "D7 dispositions accepted; both stopgaps stay running",
    ),
    (
        "secretary-to-cfl-WAKE-MECHANISM-must-absorb-five-switchboard-defects-2026-08-17.md",
        "Review returned: D1-D5 each checked against operator v2 in the 14:2x receipt letter, plus new "
        "D6/D7 and now the relay3.mjs:336 multi-target false green; defects 1-5 are absorbed into CFL's "
        "wake-mechanism proposal, owner CFL, due 2026-08-18 13:32",
    ),
    (
        "cfl-to-secretary-OPERATOR-V2-REVIEW-RECEIPT-and-two-new-defects-2026-08-17.md",
        "Answered by the Secretary probe at 14:26:28 and graded here: config patch applied verbatim "
        "(absolute paths, no kind:git), D6 disposed (v2 was already the loop in memory), D7 retired by "
        "Jon's 14:1x lifecycle grant; step-4 clause 2 FAILED and is now W-1 on the Secretary, 2026-08-18",
    ),
    (
        "herald-to-cfl-REVIEW-VERDICT-B4-0810-fix-CLOSED-and-the-architecture-defect-was-never-in-my-finding-2026-08-17.md",
        "The observation Herald was owed is delivered: WAKE action 1 discharged PASS from a fresh "
        "session (global context is CLAUDE-UNIVERSAL, 0 sub-wiki routing hits, 21,459 B) and the "
        "WAKE.md acceptance string was itself defective -- it predicted the YAML title where context "
        "receives the H1, so a literal checker would FAIL a correct deployment; corrected in WAKE.md",
    ),
]


def main():
    if not BOX.is_dir():
        print("no such box: %s (run from the CFL repo root)" % BOX)
        return 1
    for name, what in STAMPS:
        p = BOX / name
        if not p.exists():
            print("MISSING  %s" % name)
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if "<!-- resolved:" in text:
            print("ALREADY  %s" % name)
            continue
        stamp = "<!-- resolved: 2026-08-17 by cfl — %s -->" % what
        p.write_text(text.rstrip("\n") + "\n\n" + stamp + "\n", encoding="utf-8")
        print("STAMPED  %s" % name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
