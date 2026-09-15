#!/usr/bin/env python3
"""selftest_db2_levers.py -- both controls (positive fixture must PASS/expected-verdict, negative
fixture must FAIL/WARN) per DB-2 lever check in scripts/audit/db2_levers.py. Run:

    python scripts/audit/db2_levers.py --selftest
    (or directly: python scripts/tests/selftest_db2_levers.py)

P29 rule this repo already carries: a check that cannot fail is this week's dominant defect; a
check that cannot pass is its twin. Every function below is asserted BOTH directions.
"""
from __future__ import annotations

import os
import sys
import datetime as dt

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "scripts", "audit"))
import db2_levers as L  # noqa: E402


def run():
    fails = []
    n = [0]

    def check(label, cond):
        n[0] += 1
        if not cond:
            fails.append(label)

    # ---- Row 2: seal-before-run --------------------------------------------
    # positive control: field-bearing registry, run AFTER seal -> PASS
    good_reg = (
        "| id | class | query | seal_ts | run_ts |\n"
        "|---|---|---|---|---|\n"
        "| P1 | x | q | 2026-08-22 | 2026-08-23 |\n"
    )
    v = L.check_row2_seal_before_run(good_reg)
    check("row2 positive: run-after-seal must PASS", v.status == L.PASS)
    # negative control: run precedes seal -> WARN
    bad_reg = (
        "| id | class | query | seal_ts | run_ts |\n"
        "|---|---|---|---|---|\n"
        "| P1 | x | q | 2026-08-23 | 2026-08-22 |\n"
    )
    v = L.check_row2_seal_before_run(bad_reg)
    check("row2 negative: run-before-seal must WARN", v.status == L.WARN)
    # UNKNOWN-by-design control: real (fieldless) registry text never renders PASS
    v = L.check_row2_seal_before_run("| id | class | query |\n|---|---|---|\n| P1 | x | q |\n")
    check("row2 no-field registry must be UNKNOWN, never PASS", v.status == L.UNKNOWN)

    # ---- Row 9: consolidation at close --------------------------------------
    import tempfile, io
    tmp = tempfile.mkdtemp()
    def touch(name):
        with io.open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
            fh.write("x")
    touch("CONS-2026-08-20-01-compact-aaa-20260820T0000000000.md")
    touch("close-bbb-20260821T0000000000.md")
    v = L.check_row9_consolidation_at_close(tmp)
    check("row9 positive: close after CONS must PASS", v.status == L.PASS)

    tmp2 = tempfile.mkdtemp()
    def touch2(name):
        with io.open(os.path.join(tmp2, name), "w", encoding="utf-8") as fh:
            fh.write("x")
    touch2("close-ccc-20260825T0000000000.md")
    v = L.check_row9_consolidation_at_close(tmp2)
    check("row9 negative: close with no preceding CONS must WARN", v.status == L.WARN)

    # ---- Row 10: template-eval demoted --------------------------------------
    v = L.check_row10_template_eval_demoted("no retirement text here", [("t1", "kind: x\n")])
    check("row10 positive: no version field -> DEMOTE, residue not-buildable",
          v.status == L.DEMOTE and "NOT-BUILDABLE-YET" in v.evidence)
    v = L.check_row10_template_eval_demoted("x", [("t1", "template-version: 2\n")])
    check("row10 negative: version field present -> residue live, not DEMOTE",
          v.status != L.DEMOTE)

    # ---- Row 11: tier-0 index row --------------------------------------------
    idx = "some header\n| close-abc-20260822T0000000000.md | ... |\n"
    v = L.check_row11_index_row_present("close-abc-20260822T0000000000.md", idx)
    check("row11 positive: instance present in index -> PASS", v.status == L.PASS)
    v = L.check_row11_index_row_present("close-ZZZ-missing.md", idx)
    check("row11 negative: instance absent from index -> WARN (verify must FAIL)",
          v.status == L.WARN)

    # ---- Row 12: read-receipt demoted -----------------------------------------
    v = L.check_row12_read_receipt_demoted("nothing about retirement here")
    check("row12 negative: no retirement note -> DEMOTE (outstanding)", v.status == L.DEMOTE)
    v = L.check_row12_read_receipt_demoted("...\nRETIRED (DB-2 row 12) ...\n")
    check("row12 positive: retirement note present -> PASS", v.status == L.PASS)

    # ---- Row 15: WORK-CLAIMS immutability -------------------------------------
    old = [
        "| 2026-08-23T10:00:00 | seatA | TAKE | item-1 |\r\n",
        "| 2026-08-23T11:00:00 | seatB | DONE | item-2 |\r\n",
    ]
    # negative control: whole-file LF<->CRLF conversion, zero rows semantically altered -> PASS
    new_normalized_only = [ln.replace("\r\n", "\n") for ln in old]
    v = L.check_row15_work_claims_immutable(old, new_normalized_only)
    check("row15 negative control (1f51a31 class): EOL-only change must PASS, not WARN",
          v.status == L.PASS)
    # positive control: an existing row's content actually changed -> WARN
    altered = [
        "| 2026-08-23T10:00:00 | seatA | TAKE | item-1-EDITED |\r\n",
        "| 2026-08-23T11:00:00 | seatB | DONE | item-2 |\r\n",
    ]
    v = L.check_row15_work_claims_immutable(old, altered)
    check("row15 positive: real row content change must WARN", v.status == L.WARN)

    # ---- Row 17: no positional reference --------------------------------------
    v = L.check_row17_no_positional_reference(["| a | b | c | see the row above |\n"])
    check("row17 positive: positional phrase present -> WARN", v.status == L.WARN)
    v = L.check_row17_no_positional_reference(["| a | b | c | see id6=abc123 |\n"])
    check("row17 negative: named-antecedent row -> PASS", v.status == L.PASS)

    # ---- Row 20: m14 token on TAKE ---------------------------------------------
    v = L.check_row20_m14_token_on_take(["| t | seat | TAKE | item | m14: yes |\n"])
    check("row20 positive: token present -> PASS", v.status == L.PASS)
    v = L.check_row20_m14_token_on_take(["| t | seat | TAKE | item | |\n"])
    check("row20 negative: token absent on TAKE -> WARN", v.status == L.WARN)

    # ---- Row 18b: canonical age -------------------------------------------------
    v = L.check_row18b_canonical_age(dt.date(2026, 8, 22), dt.date(2026, 8, 23),
                                      fresh_fetch_confirmed=True)
    check("row18b positive: 1 day drift within threshold -> PASS", v.status == L.PASS)
    v = L.check_row18b_canonical_age(dt.date(2026, 8, 22), dt.date(2026, 8, 30),
                                      fresh_fetch_confirmed=True)
    check("row18b negative: 8 day drift beyond threshold -> WARN", v.status == L.WARN)
    v = L.check_row18b_canonical_age(dt.date(2026, 8, 22), dt.date(2026, 8, 30),
                                      fresh_fetch_confirmed=False)
    check("row18b unfresh-operand control: unconfirmed fetch -> UNKNOWN, never PASS",
          v.status == L.UNKNOWN)

    # ---- Row 21: reachability chain (live, wraps existing script) --------------
    v = L.check_row21_reachability_chain()
    check("row21 live run returns a real verdict (PASS or WARN, precondition met)",
          v.status in (L.PASS, L.WARN))

    # ---- Row 22: midturn wrapper scan (live, wraps existing script) ------------
    v = L.check_row22_midturn_wrapper_scan()
    check("row22 live run returns a real verdict or a legible UNKNOWN",
          v.status in (L.PASS, L.WARN, L.UNKNOWN))

    # ---- Tally --------------------------------------------------------------
    hb, tr, dm = L.tally()
    check("tally: 8 heartbeat-warn", hb == 8)
    check("tally: 1 tool-refuses", tr == 1)
    check("tally: 2 demote", dm == 2)
    check("tally: 11 total rows", hb + tr + dm == 11)

    return n[0], fails


if __name__ == "__main__":
    count, fails = run()
    print(f"{count} assertions, {len(fails)} failed")
    for f in fails:
        print(f"  FAIL: {f}")
    sys.exit(0 if not fails else 1)
