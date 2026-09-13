---
format: cfl-page/v1
kind: pattern
slug: a-check-that-cannot-fail
title: "A Check That Cannot Fail"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "negative control cannot fail string literal print PASS test skipped absent fixture selftest 6 of 6"
aliases: [negative-control-tests-literals, selftest-that-always-passes, print-literal-not-a-count]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "two distinct instances within the same script's rejection lineage (v2's negative control, v3's selftest count); both caught by the gate running the check adversarially, neither self-reported by the proposer."
probe_sealed: "In PROP-004 v3, does `EXTRACT_TYPED_EDGES_V3_SELFTEST: PASS (6/6 checks verified)` mean six assertions executed and passed? => No — '6/6' is a literal in the print statement (source line 113 per the receipt), not a count; test 6 is guarded by `if sample_file.exists()`, and when that fixture is absent (as it is on N:), only five assertions run and the same '6/6' line prints anyway. TRUSTED"
---

## Struggle

A negative control or a selftest is built to prove a check CAN fail — but its implementation
routes around the real code path (testing two string literals instead of calling the actual
vetting function) or its pass line is a hardcoded string rather than a computed tally, so the
check reports PASS regardless of what the underlying system actually does.

- `wiki/skills-gate/LEDGER.md:151-153` [verbatim] (cropped) — PROP-004 v2 probe finding: "Probe 2
  (`--test-negative`): PASS, exit 0 -- **and cannot fail**: `run_negative_control` tests a Python
  `in` on two string literals and never calls the extractor's vetting path. A check that cannot
  fail (CARRIER's `pid 50516` class)."
- `wiki/skills-gate/LEDGER.md:173` [paraphrase] (fragment verbatim) — PROP-004 v3 row: "Test
  6 is `if exists`; 5 asserts ran. Copy with fixture path pointed at a nonexistent file: identical
  PASS." (Confirmed against the actual code: `exchange/outbox/RECEIPT-PROP-004-v3-RATIFICATION.md:32`
  [verbatim] — "Test 6 is wrapped in `if sample_file.exists():` (line 104). The fixture it names is
  absent from the only tree the letter cites, so on Antigravity's run and on CFL's, five assertions
  executed and the sixth was skipped, and the program printed '6/6' because '6/6' is a literal in
  the print statement (line 113), not a count.")

## Generalization

A check's PASS output is only informative if the code path it exercises can, under some input,
actually produce FAIL — and if the printed tally is computed from what ran rather than typed as a
constant. Both failures here have the same effect: the check's designer (and every reader of its
output) treats the green line as evidence the invariant holds, when the green line would print
identically whether the invariant holds or not. This is the same class CARRIER already names (`pid
50516`) — recurring across at least two independent scripts (the memory-index carrier's own case
and, now, PROP-004's extractor) means it is a shape, not a one-off bug. Same family as
[[proposal-and-script-describe-different-programs]]: a script whose print statements describe it
accurately and whose behavior does not.

## Counter-evidence

none found, searched: `wiki/skills-gate/LEDGER.md` PROP-001-PROP-003 for an accepted proposal whose
negative control or selftest was later found to route around the real code path; PROP-002's and
PROP-003's probes are both run against real artifacts (an actual sent letter; CFL's actual 18
past-due letters), not string-literal fixtures, so the class described here does not appear in the
accepted rows.

## Motivates

none yet — no `skills/` page states "a negative control must call the real vetting function, not a
literal comparison" as a checkable rule; the gate currently catches this by re-implementing the
adversarial run itself each time rather than by a reusable linter.

## Probe

Sealed question above. Falsified if a future run of `extract_typed_edges.py --selftest` (in
whatever tree currently holds it) prints a count that varies with the number of assertions that
actually executed, or if `run_negative_control` (or its successor) is found to call the real
vetting/normalization path rather than comparing string literals.
