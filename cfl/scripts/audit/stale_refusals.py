#!/usr/bin/env python3
"""Find work parked behind a RECORDED REFUSAL that nobody has re-tested.

WHY THIS EXISTS -- a peer's finding, and the half of a rule this program never wrote
-----------------------------------------------------------------------------------
Professional, 2026-08-24, after measuring 16 town-hall receipts that never reached the spine:

    "Each receipt states its own blocker: 'this session is refused every path outside its own
     repo... the next seat with cross-trunk write appends this block verbatim.' TRUE on 08-17.
     FALSE now. Sixteen items sat behind a blocker that had LIFTED, and no seat re-tested,
     because the refusal was recorded as a FACT rather than as a MEASUREMENT WITH A DATE."

Their WAKE.md already carried half the rule -- *a gate PASSED is not a gate OPEN, RE-TEST* -- and
the inverse appeared nowhere:

    ⛔ A GATE THAT WAS CLOSED IS NOT STILL CLOSED. Anything parked behind a recorded refusal is
       parked until somebody re-runs it.

⭐ AND NOTICE WHICH HALF GOT WRITTEN. The half we wrote protects against ACTING WHEN WE SHOULD NOT.
The omitted half protects against NOT ACTING WHEN WE COULD. A stale PASS gets caught because
something breaks. ⛔ A STALE REFUSAL BREAKS NOTHING -- the work simply never happens, and the record
shows a seat that behaved correctly. It requires no further work from the measurer and it is
invisible even in hindsight unless somebody re-runs the gate.

That is the same asymmetry as `disposition_rate.py`'s self-corroboration and the same asymmetry as
an `outbound-staging/` directory holding sent mail: **the quiet errors accumulate because nothing
is inconvenienced by them.**

WHAT THIS FLAGS, and the ranking is the point
---------------------------------------------
  UNDATED  a recorded refusal with NO date anywhere near it.  <-- WORST. A parked item wearing the
           costume of a decision. Nobody can even ask "is it still true?"
  DATED    a recorded refusal carrying a date. Re-testable, and the age is printed so the reader
           can judge. An old date is not a defect; an old date nobody has acted on is.

⚠️ THIS CANNOT TELL A REFUSAL FROM A DESCRIPTION OF ONE. A page ABOUT blocked work matches the same
words as a page that IS blocked. So every hit is a CANDIDATE, never a finding, and the output says
so. An instrument that presented these as findings would manufacture exactly the false-alarm class
that `AWAITING DELIVERY` produced tonight.

Usage:
    python scripts/audit/stale_refusals.py
    python scripts/audit/stale_refusals.py --selftest
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ROOTS = ("exchange", "wiki/tracker", "wiki/intake-triage")
SKIP_DIR = {".git", "__pycache__", "node_modules", "bake-out", "raw"}

# Phrases that assert a CURRENT inability, not a past event. Tuned toward the shape Professional
# measured: a seat recording what it could not do, with an ask attached for a later seat.
REFUSAL = re.compile(
    r"(refused (?:every|all|the) |permission denied|is refused|was denied|cannot write to|"
    r"blocked by the (?:auto-mode )?classifier|awaiting a seat with|"
    r"the next seat with|needs a seat that can|not permitted to|lacks permission)",
    re.I)
DATE = re.compile(r"20\d{2}-\d{2}-\d{2}")


def scan(root):
    undated, dated = [], []
    for top in ROOTS:
        base = os.path.join(root, top)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, root).replace("\\", "/")
                try:
                    with open(p, encoding="utf-8", errors="ignore") as fh:
                        lines = fh.read().split("\n")
                except OSError:
                    continue
                for i, ln in enumerate(lines):
                    m = REFUSAL.search(ln)
                    if not m:
                        continue
                    # A date "near" the claim: same line, or within two lines either side. A date
                    # in the frontmatter twenty lines up is the FILE's date, not the CLAIM's, and
                    # counting it would let every file clear itself.
                    window = "\n".join(lines[max(0, i - 2):i + 3])
                    ds = DATE.findall(window)
                    rec = (rel, i + 1, m.group(1).strip(), ln.strip()[:150])
                    (dated if ds else undated).append(rec + ((max(ds),) if ds else ()))
    return undated, dated


def report(root):
    undated, dated = scan(root)
    print("=" * 74)
    print("MEASURED ROOT : %s" % root)
    print("                ^-- %s" % ("THIS SCRIPT'S OWN TRUNK" if os.path.abspath(root) == REPO
                                      else "A DIFFERENT TREE"))
    print("roots scanned : %s" % ", ".join(ROOTS))
    print("=" * 74)

    print("\n-- UNDATED recorded refusals -- WORST CLASS --")
    print("   No date near the claim. Nobody can even ask whether it is still true.")
    if not undated:
        print("   NONE.")
    for rel, ln, kind, txt in undated:
        print("   %s:%d" % (rel, ln))
        print("      [%s]  %s" % (kind, txt))

    print("\n-- DATED recorded refusals -- re-testable --")
    if not dated:
        print("   NONE.")
    for rel, ln, kind, txt, d in sorted(dated, key=lambda r: r[4]):
        print("   %-10s %s:%d" % (d, rel, ln))
        print("      [%s]  %s" % (kind, txt))

    print("\ntotals: %d undated, %d dated" % (len(undated), len(dated)))
    print("\nBOUNDS")
    print("  1. NOT REVIEWED: whether any hit is a LIVE refusal or a DESCRIPTION of a past one.")
    print("     The words are identical.")
    print("  2. WHY: distinguishing them needs the surrounding argument, which is a judgment.")
    print("  3. ⛔ RESULTING LIMITATION: EVERY HIT IS A CANDIDATE, NEVER A FINDING. Presenting")
    print("     these as findings would manufacture the false-alarm class that an outbound queue")
    print("     holding SENT mail produced tonight. And a quiet report is NOT a clear tree --")
    print("     the phrase list is hand-built and a refusal phrased a new way is invisible to it.")


def selftest():
    ok = True
    print("--- case 1: a refusal phrase is detected ---")
    good = bool(REFUSAL.search("this session is refused every path outside its own repo"))
    print("    %s" % ("PASS" if good else "FAIL")); ok = ok and good

    print("--- case 2: NEGATIVE CONTROL -- ordinary prose does not match ---")
    good2 = not REFUSAL.search("the wiki freshness arm returned 0.0 days and the gate passed")
    print("    %s" % ("PASS" if good2 else "FAIL")); ok = ok and good2

    print("--- case 3: a date two lines away counts; twenty lines away does NOT ---")
    near = "\n".join(["x", "2026-08-17", "is refused all paths", "y"])
    far = "\n".join(["2026-08-17"] + ["x"] * 20 + ["is refused all paths"])
    i_far = far.split("\n").index("is refused all paths")
    w_far = "\n".join(far.split("\n")[max(0, i_far - 2):i_far + 3])
    good3 = bool(DATE.findall(near)) and not DATE.findall(w_far)
    print("    near=%s far-window=%s  %s"
          % (bool(DATE.findall(near)), bool(DATE.findall(w_far)), "PASS" if good3 else "FAIL"))
    ok = ok and good3

    print("\n" + ("SELFTEST PASS" if ok else "SELFTEST FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    report(os.path.abspath(a.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
