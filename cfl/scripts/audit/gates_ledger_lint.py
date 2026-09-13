#!/usr/bin/env python3
"""gates_ledger_lint.py — catch a gate whose CHECK does not belong to it.

WHY, and the credit is soul's (Claude Personal, 733efbef, 2026-09-04 21:0x), who found the instance
in a peer review of PR #255 that CFL asked for and did not perform itself:

  GATES.md:51  G7  CHECK: node scripts/gates/pr3_checks.mjs g6
  GATES.md:56  G8  CHECK: node scripts/gates/pr3_checks.mjs g6      <-- invokes g6, not g8

Both were marked [x]. G8's EXPECT is "G8 OK census-figure-matches-live-run"; `g6` prints
"G6 OK pr-255-open ...". ⛔ The gate could not pass its own stated oracle and read GREEN anyway.

⭐ AND G8 IS THE WORST GATE FOR THIS TO HAPPEN TO: its entire purpose is "the coverage figures in
the description are RE-MEASURED, NOT COPIED." The gate that exists to catch a copied value was
disabled by a copied line, and the thing it guarded had silently gone stale (published 493/876
against a live 498/888).

⚠️ THE EVIDENCE LINES PROVE THIS WAS TWO EVENTS, NOT ONE, and that is the finding worth keeping:
G7's recorded evidence is output-bytes=31 and G8's is 37 -- exactly the byte counts of g7's and
g8's own outputs (`g6` emits 90). So the gates WERE run correctly once, and the CHECK lines were
rewritten to g6 afterwards. ⛔ THE EVIDENCE AND THE CHECK LINE HAVE SEPARATE PROVENANCE -- this
week's named dominant defect, sitting inside the ledger that exists to prevent it.

WHAT THIS CHECKS -- statically, running nothing, because a linter that must execute 23 gates to
find a typo is a linter nobody runs:

  L1  ID MISMATCH. If EXPECT names a gate id (e.g. "G8 OK ..."), the CHECK's subcommand must be
      that gate's own (g8). This is the exact defect above and it needs no execution to see.
  L2  SHARED CHECK. Two gates invoking the identical CHECK command, unless one declares itself the
      other's control (the ledger is full of legitimate negative controls, so this must be
      declarable or the lint is noise -- an unsuppressable warning gets suppressed by ignoring it).
  L3  EXPECT-LESS RUNNABLE. A CHECK with no EXPECT: exit status alone is a weak oracle.

⛔ Exit 1 if any L1 fires (that is a false green). L2/L3 are reported and do not fail the run --
they are prompts to sharpen, not defects, and conflating the two is how a lint loses its teeth.

  gates_ledger_lint.py [--file GATES.md] [--self-test]
"""
import argparse
import io
import os
import re
import sys
from collections import defaultdict

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GATE_RE = re.compile(r"^-\s*\[[ xX]\]\s*\**(G\d+)\b", re.MULTILINE)
CHECK_RE = re.compile(r"^\s*(?:CHECK|CONTROL):\s*(.+?)\s*$")
EXPECT_RE = re.compile(r"^\s*EXPECT:\s*(.+?)\s*$")
# "node scripts/gates/pr3_checks.mjs g8"  ->  g8
SUBCMD_RE = re.compile(r"\bpr3_checks\.mjs\s+(g\d+)\b")
# an EXPECT that names a gate: "G8 OK ..."
EXPECT_ID_RE = re.compile(r"\bG(\d+)\b")
CONTROL_HINT = re.compile(r"control|negative|positive", re.IGNORECASE)


def parse(text):
    """-> [ {id, line, checks:[(cmd,line)], expects:[str], body:str} ]"""
    lines = text.splitlines()
    starts = [(m.group(1), text[:m.start()].count("\n")) for m in GATE_RE.finditer(text)]
    gates = []
    for n, (gid, ln) in enumerate(starts):
        end = starts[n + 1][1] if n + 1 < len(starts) else len(lines)
        body_lines = lines[ln:end]
        checks, expects = [], []
        for off, bl in enumerate(body_lines):
            m = CHECK_RE.match(bl)
            if m:
                checks.append((m.group(1), ln + off + 1))
            m = EXPECT_RE.match(bl)
            if m:
                expects.append(m.group(1))
        gates.append({"id": gid, "line": ln + 1, "checks": checks,
                      "expects": expects, "body": "\n".join(body_lines)})
    return gates


def lint(gates):
    l1, l2, l3 = [], [], []
    for g in gates:
        gnum = g["id"][1:]
        # L1 -- the EXPECT names a gate; the CHECK must invoke that gate's own subcommand
        for exp in g["expects"]:
            m = EXPECT_ID_RE.search(exp)
            if not m:
                continue
            want = "g" + m.group(1)
            for cmd, cline in g["checks"]:
                sm = SUBCMD_RE.search(cmd)
                if sm and sm.group(1) != want:
                    l1.append((g["id"], cline, sm.group(1), want, exp[:60]))
        # L3 -- a runnable CHECK with no EXPECT
        runnable = [c for c, _ in g["checks"] if not c.lower().startswith("manual")]
        if runnable and not g["expects"]:
            l3.append((g["id"], g["line"]))
    # L2 -- identical CHECK command in two gates, neither declaring itself a control
    by_cmd = defaultdict(list)
    for g in gates:
        for cmd, cline in g["checks"]:
            if cmd.lower().startswith("manual"):
                continue
            by_cmd[cmd].append((g["id"], cline, bool(CONTROL_HINT.search(g["body"]))))
    for cmd, hits in by_cmd.items():
        if len(hits) > 1 and not any(h[2] for h in hits):
            l2.append((cmd, [h[0] for h in hits]))
    return l1, l2, l3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=os.path.join(ROOT, "GATES.md"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    try:
        text = io.open(a.file, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print("UNKNOWN -- cannot read %s (%s). Unreadable is never clean." % (a.file, e))
        return 1
    gates = parse(text)
    l1, l2, l3 = lint(gates)
    print("=== GATES LEDGER LINT === a gate whose CHECK is not its own can read green forever")
    print("  %d gates parsed from %s\n" % (len(gates), a.file))
    for gid, ln, got, want, exp in l1:
        # NB: this print crashed with a %-arity bug on its FIRST REAL FIRING (2026-09-04), because
        # the live ledger was clean when the script was written and the L1 branch had therefore
        # never executed. The selftest exercised lint(), not main()'s reporting. ⛔ A REPORTING PATH
        # THAT ONLY RUNS WHEN SOMETHING IS WRONG IS UNTESTED EXACTLY WHEN IT MATTERS -- which is
        # the same lesson as G23's "a detector that has only ever returned clean is a written
        # warning", one level further in.
        print("  L1 FALSE-GREEN  %s:%d invokes `%s` but its EXPECT names %s -- should invoke `%s`"
              % (gid, ln, got, exp, want))
    for cmd, ids in l2:
        print("  L2 SHARED-CHECK %s share `%s` and none declares itself a control"
              % ("/".join(ids), cmd[:70]))
    for gid, ln in l3:
        print("  L3 NO-EXPECT    %s:%d has a runnable CHECK and no EXPECT (exit status alone)" % (gid, ln))
    print("\n  L1 %d (false greens, FATAL) · L2 %d · L3 %d" % (len(l1), len(l2), len(l3)))
    if not l1:
        print("  No gate invokes a check belonging to another gate. This is a REPORT, not a proof "
              "that each gate measures what its title claims.")
    return 1 if l1 else 0


def self_test():
    print("=== SELF-TEST -- gates_ledger_lint ===")
    np = nf = 0

    def ok(name, got, want):
        nonlocal np, nf
        if got == want:
            np += 1; print("  PASS  %s" % name)
        else:
            nf += 1; print("  FAIL  %s\n        want: %r\n        got : %r" % (name, want, got))

    # THE REAL DEFECT, verbatim in shape from GATES.md before the 2026-09-04 fix
    bad = ("- [x] G8: coverage figures are re-measured, not copied\n"
           "  CHECK: node scripts/gates/pr3_checks.mjs g6\n"
           "  EXPECT: G8 OK census-figure-matches-live-run\n")
    l1, _l2, _l3 = lint(parse(bad))
    ok("1 THE DEFECT: g6 under G8 -> L1", len(l1), 1)
    ok("2 names both the got and the want", (l1[0][2], l1[0][3]), ("g6", "g8"))

    good = bad.replace("mjs g6", "mjs g8")
    ok("3 NEGATIVE CONTROL: correct subcommand is clean", len(lint(parse(good))[0]), 0)

    # a shared CHECK where one gate SAYS it is a control must not be reported
    ctl = ("- [x] G2: every finding carries a disposition\n"
           "  CHECK: node x.mjs a\n  EXPECT: OK\n"
           "- [x] G3: NEGATIVE CONTROL for G2 -- fails on a fixture\n"
           "  CHECK: node x.mjs a\n  EXPECT: OK\n")
    ok("4 declared control is not an L2", len(lint(parse(ctl))[1]), 0)

    dup = ctl.replace("NEGATIVE CONTROL for G2 -- fails on a fixture", "another gate entirely")
    ok("5 POSITIVE CONTROL for 4: undeclared duplicate IS an L2", len(lint(parse(dup))[1]), 1)

    ok("6 runnable check with no EXPECT -> L3",
       len(lint(parse("- [x] G9: x\n  CHECK: node y.mjs\n"))[2]), 1)
    ok("7 manual gate with no EXPECT is not an L3",
       len(lint(parse("- [x] G9: x\n  CHECK: manual -- a human reads it\n"))[2]), 0)
    # an EXPECT naming no gate id cannot produce a false-green claim either way
    ok("8 EXPECT with no gate id -> no L1",
       len(lint(parse("- [x] G5: x\n  CHECK: node z.mjs g6\n  EXPECT: 0 risky\n"))[0]), 0)
    print("  %d passed, %d failed" % (np, nf))
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
