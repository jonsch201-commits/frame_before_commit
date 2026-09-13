#!/usr/bin/env python3
"""Make "is the inbox cleared?" a MEASUREMENT instead of a feeling.

⛔ WHY THIS EXISTS. Jon, 2026-08-09: "Are all inboxes and out boxes for all 4 coordinators cleared
and resolved or ticketed?" ⭐ NOBODY COULD ANSWER IT. Measured that day: CFL 169 in / 36 out ·
Personal 97 / 130 · Professional 126 / 9 · SSP 26 / 0 · and 42 sitting in a RETIRED trunk's inbox,
eleven of which landed after it was retired -- one of them from Jon himself.

The only signal any lane had was "unread", and that detector counts letters nobody NAMED, not
letters nobody ACTED ON. Professional's Q-3 correction read UNREAD while CFL had applied it four
hours earlier.

⭐ SO THE FIX IS NOT A CLEANUP PASS. Reading 169 letters produces a number that is stale the moment
it is written -- the same defect as every stale count this cycle. The fix is a RESOLUTION STAMP: a
letter records, on its own face, that it was acted on and what changed. Then "cleared" is derivable
forever instead of measurable once.

A letter is RESOLVED when it carries, anywhere in its text:

    <!-- resolved: 2026-08-09 by cfl — what changed, in one line -->

⚠️ THE HONEST LIMIT, stated because a tool that hides its own bound is the thing this repo keeps
building: this measures whether a STAMP EXISTS. It does not measure whether the resolution was any
good. A stamp is a claim by its author, not a verification -- exactly like the "read" stamps that let
v1 of the decision list carry a closed row.
"""
import argparse, os, pathlib, re, sys

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

STAMP = re.compile(r"<!--\s*resolved:\s*(?P<date>\d{4}-\d{2}-\d{2})\s+by\s+(?P<who>[a-z\-]+)", re.I)

BOXES = [
    ("CFL",          "exchange/inbound"),
    ("CFL",          "exchange/outbound"),
    ("Personal",     "G:/My Drive/Claude/Claude Personal/exchange/inbound"),
    ("Personal",     "G:/My Drive/Claude/Claude Personal/exchange/outbox"),
    ("Professional", "G:/My Drive/Claude/Claude Professional/claude-professional/exchange/inbound"),
    ("Professional", "G:/My Drive/Claude/Claude Professional/claude-professional/exchange/outbox"),
    ("SSP",          "G:/My Drive/Claude/Claude SSP/claude-ssp/exchange/inbound"),
    ("RETIRED herald-wiki", "G:/My Drive/Claude/Herald Wiki/herald-wiki/exchange/inbound"),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--unresolved", action="store_true", help="list the unresolved, newest first")
    a = ap.parse_args()
    os.chdir(a.repo)

    print("=== letter ledger — resolved vs open, by box ===")
    tot_r = tot_n = 0
    openers = []
    for trunk, box in BOXES:
        p = pathlib.Path(box)
        if not p.is_dir():
            print(f"  {trunk:<22} {box:<12} MISSING — reported, not skipped")
            continue
        r = n = 0
        for f in p.glob("*.md"):
            try: txt = f.read_text(encoding="utf-8", errors="replace")
            except Exception: n += 1; continue
            if STAMP.search(txt): r += 1
            else:
                n += 1
                openers.append((f.stat().st_mtime, trunk, f.name))
        tot_r += r; tot_n += n
        bar = "" if (r + n) == 0 else f"{100*r//(r+n)}%"
        print(f"  {trunk:<22} {p.name:<10} resolved {r:>4} | open {n:>4}   {bar}")

    print(f"\n  TOTAL resolved {tot_r} | open {tot_n}")
    if a.unresolved:
        print("\n  --- open, newest first ---")
        for _, trunk, name in sorted(openers, reverse=True)[:25]:
            print(f"    [{trunk}] {name[:88]}")
    print("\n  [!] BOUND: this counts whether a RESOLUTION STAMP EXISTS.")
    print("      It does NOT measure whether the resolution was correct. A stamp is a claim by its")
    print("      author, not a verification -- the same weakness that let a 'read' decision list")
    print("      carry a row Jon had already closed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
