#!/usr/bin/env python3
"""C34 -- can a CROSSGRADE artifact be caught FROM THE ARTIFACT ALONE?

Built 2026-09-07 to answer CFL's priority 1 on the N2 C2 cross-grade task: *"a seat that reads the
other grader's table first, or that produces a table with no population line, must be catchable from
the artifact alone."*

⛔ WHAT THIS CHECK CAN AND CANNOT DO, stated first because the request asks for something impossible
and the honest answer is more useful than a check that pretends.

  CATCHABLE from the artifact:  a missing population line · a missing row count · a count that
    disagrees with the table · a table with no CLASS column · rows with no re-run command · a
    verdict-only sample · an UNKNOWN rate of zero (nobody grading 10-20 rows of a live tree hits
    zero unreachable honestly) · a missing pre-registered expectation · a missing falsifier.

  ⛔ NOT CATCHABLE from the artifact: WHETHER THE GRADER PEEKED. Reading the other table leaves no
    trace in this file. A peeking grader who then writes an independent-looking table is
    indistinguishable from an honest one HERE. What IS detectable is AGREEMENT that is too good --
    and that is a comparison between the two artifacts, not a property of one, so it belongs in a
    PAIR check (--pair) and it is evidence, never proof.

  ⭐ So the acceptance test must not claim to detect peeking. It detects SHAPE. The defence against
    peeking is ordering (publish before you can read) plus the pre-registered expectation, which is
    cheap to write honestly and expensive to fake after seeing an answer.

Usage:
  python scripts/audit/crossgrade_artifact_check.py <CROSSGRADE-file.md>
  python scripts/audit/crossgrade_artifact_check.py --pair <fileA.md> <fileB.md>
  python scripts/audit/crossgrade_artifact_check.py --selftest

Exit: 0 accept · 1 reject (reasons printed) · 3 UNKNOWN (could not read).
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROW = re.compile(r"^\s*\|(?!\s*[-: ]+\|)(?!\s*CLASS\b).+\|\s*$", re.M | re.I)
POP = re.compile(r"population\s*[:=]", re.I)
CNT = re.compile(r"row[_ ]?count\s*[:=]\s*(\d+)", re.I)
EXPECT = re.compile(r"\bexpect(ed|ation)?\s*[:=]", re.I)
FALSIF = re.compile(r"\bfalsif\w*\s*[:=]", re.I)
GRADES = re.compile(r"\b(HELD|DRIFTED|FALSE|UNKNOWN|REFUSED-WITH-REASON)\b")
CMDISH = re.compile(r"(python |git |grep |ls |wc |stat |bash |sqlite3|sed )")


def rows(text):
    """Table rows that carry a grade token. A row with no grade is not a graded row."""
    return [r for r in ROW.findall(text) if GRADES.search(r)]


def check(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            t = fh.read()
    except OSError as exc:
        return 3, [f"UNKNOWN: cannot read {path}: {exc}"], {}

    rs = rows(t)
    grades = GRADES.findall(t)
    fails = []

    if not POP.search(t):
        fails.append("no POPULATION line -- a thin grade is indistinguishable from a lenient one")
    m = CNT.search(t)
    if not m:
        fails.append("no ROW COUNT line")
    elif rs and abs(int(m.group(1)) - len(rs)) > 0:
        fails.append(f"ROW COUNT says {m.group(1)}, table has {len(rs)} graded row(s)")
    if not EXPECT.search(t):
        fails.append("no pre-registered EXPECTATION -- the only cheap defence against a fitted table")
    if not FALSIF.search(t):
        fails.append("no FALSIFIER named")
    if not re.search(r"\bCLASS\b", t, re.I):
        fails.append("no CLASS column -- classes behave differently and a blended rate hides that")
    if not rs:
        fails.append("no graded rows found")
    else:
        nocmd = [r for r in rs if not CMDISH.search(r)]
        if len(nocmd) > len(rs) // 4:
            fails.append(f"{len(nocmd)} of {len(rs)} rows carry no re-run command -- read, not ran")
        if "UNKNOWN" not in grades:
            fails.append("ZERO UNKNOWN grades -- on a live tree that is a claim about the grader, "
                         "not the predecessor; an unreachable check must grade UNKNOWN")
    # A verdict-only sample cannot speak to any other class.
    lowered = t.lower()
    classes = {c for c in ("verdict", "count", "path", "hash", "ruling", "capability")
               if re.search(r"\|\s*\**" + c, lowered)}
    if classes and classes <= {"verdict"}:
        fails.append("VERDICT-ONLY sample -- verdicts are claims about a live tree and drift by "
                     "construction; a rate over them is not a grade of the predecessor")

    info = {"graded_rows": len(rs), "classes": sorted(classes) or ["NONE-DETECTED"],
            "grade_tally": {g: grades.count(g) for g in sorted(set(grades))}}
    return (1 if fails else 0), fails, info


def pair(a, b):
    """Agreement between two independent grades. Evidence about peeking, never proof."""
    ra, rb = None, None
    for p in (a, b):
        code, f, info = check(p)
        print(f"-- {os.path.basename(p)}: {'ACCEPT' if code == 0 else 'REJECT'}  "
              f"rows={info.get('graded_rows')}  tally={info.get('grade_tally')}")
        for x in f:
            print(f"     {x}")
    ta = open(a, encoding="utf-8", errors="replace").read()
    tb = open(b, encoding="utf-8", errors="replace").read()
    ga, gb = GRADES.findall(ta), GRADES.findall(tb)
    print(f"\n-- pair: gradesA={len(ga)} gradesB={len(gb)}")
    print("⛔ OVERLAP OF THE CLAIM SET IS THE THING TO MEASURE AND THIS CHECK CANNOT MEASURE IT")
    print("   from grade tokens alone -- it needs the two claim texts aligned by a shared id.")
    print("   ⭐ WITHOUT A SHARED CLAIM ID, TWO GRADERS DRAWING THEIR OWN SAMPLES FROM ONE")
    print("   TRANSCRIPT ARE NOT A CROSS-GRADE. Give every claim an id in the FIRST grade and")
    print("   hand the id list (claims only, never results) to the second grader.")
    return 0


def selftest():
    ok = True

    def c(name, got, want):
        nonlocal ok
        good = got == want
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: got {got!r} want {want!r}")

    import tempfile
    good = """row_count: 2
population: all claims in predecessor X's WAKE.md, n=2
expectation: I expect counts to drift and paths to hold
falsifier: a path row that drifts

| CLASS | claim | you re-ran | result | grade |
|---|---|---|---|---|
| **path** | a | `sed -n 1p f` | x | HELD |
| **count** | b | `wc -l f` | y | UNKNOWN |
"""
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "good.md")
        open(p, "w", encoding="utf-8").write(good)
        c("well-formed artifact accepted", check(p)[0], 0)

        # RED: no population line
        p2 = os.path.join(td, "nopop.md")
        open(p2, "w", encoding="utf-8").write(good.replace("population:", "note:"))
        c("missing population REJECTED", check(p2)[0], 1)

        # RED: count disagrees with the table -- "a file that exists and says nothing"
        p3 = os.path.join(td, "badcount.md")
        open(p3, "w", encoding="utf-8").write(good.replace("row_count: 2", "row_count: 12"))
        c("row count disagreeing with the table REJECTED", check(p3)[0], 1)

        # RED: zero UNKNOWN on a live tree
        p4 = os.path.join(td, "nounknown.md")
        open(p4, "w", encoding="utf-8").write(good.replace("UNKNOWN |", "HELD |"))
        c("zero-UNKNOWN grade REJECTED", check(p4)[0], 1)

        # RED: verdict-only sample
        p5 = os.path.join(td, "verdictonly.md")
        open(p5, "w", encoding="utf-8").write(
            good.replace("**path**", "**verdict**").replace("**count**", "**verdict**"))
        c("verdict-only sample REJECTED", check(p5)[0], 1)

        # RED: rows with no command -- read, not ran
        p6 = os.path.join(td, "nocmd.md")
        open(p6, "w", encoding="utf-8").write(
            good.replace("`sed -n 1p f`", "looks right").replace("`wc -l f`", "seems fine"))
        c("rows with no re-run command REJECTED", check(p6)[0], 1)

        # RED: no expectation
        p7 = os.path.join(td, "noexp.md")
        open(p7, "w", encoding="utf-8").write(good.replace("expectation:", "aside:"))
        c("missing pre-registered expectation REJECTED", check(p7)[0], 1)

        # The honest negative: a PEEKING grader is not detectable here.
        c("peeking is NOT claimed to be detectable", check(p)[0], 0)

        c("unreadable path -> UNKNOWN not accept", check(os.path.join(td, "nope.md"))[0], 3)

    print("selftest:", "ALL PASS" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?")
    ap.add_argument("--pair", nargs=2)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.pair:
        return pair(*a.pair)
    if not a.path:
        ap.print_help()
        return 2
    code, fails, info = check(a.path)
    print(f"{os.path.basename(a.path)}: {'ACCEPT' if code == 0 else ('UNKNOWN' if code == 3 else 'REJECT')}")
    print(f"  graded rows: {info.get('graded_rows')}  classes: {info.get('classes')}  "
          f"tally: {info.get('grade_tally')}")
    for f in fails:
        print(f"  ⛔ {f}")
    return code


if __name__ == "__main__":
    sys.exit(main())
