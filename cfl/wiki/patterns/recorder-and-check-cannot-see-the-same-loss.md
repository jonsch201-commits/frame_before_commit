---
format: cfl-page/v1
kind: pattern
slug: recorder-and-check-cannot-see-the-same-loss
title: "Recorder And Check Cannot See The Same Loss"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "check population drawn from the recorder it grades boundary receipt log unrecorded silent dead hook"
aliases: [population-excludes-the-defect, check-blind-to-its-own-source, recorder-died-check-cannot-see-it]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one fully-worked instance this cycle (Professional's C29 check against precompact-receipts.log), generalized in the finding's own closing sentence; RP-29's idempotency gate is a second, adjacent instance (a gate keyed on ledger state the agent's own compliant action destroys)."
probe_sealed: "Did CFL's own C29-equivalent (a compact-boundary coverage check) or RP-29's dedupe gate ever fail to detect a boundary/return whose OWN recorder never wrote? => Professional's C29 measured exactly this on 2026-09-02: 2 real compact boundaries (session e8f94111) where the PreCompact hook died on a Drive fault produced zero receipt lines and were therefore absent from C29's own 22-boundary graded population -- not failed, invisible. TRUSTED"
---

## Struggle

A check that grades coverage or correctness by ranging over the artifact its own subject
produces cannot see the one failure mode it exists to catch: the subject failing to produce
anything at all. The check is correct on its stated predicate and silently wrong on the claim a
reader takes from it.

- `N:\claude-gists-private\FINDING-2026-09-02-professional-C29-CANNOT-SEE-THE-BOUNDARY-WHOSE-RECORDER-DIED.md:14`
  [verbatim] — "A BOUNDARY THAT PRODUCED NO RECEIPT PRODUCES NO LINE, SO IT IS NOT IN THE
  POPULATION, SO IT CANNOT FAIL THE CHECK." Measured the same session: `session e8f94111
  COMPACTED TWICE on 2026-09-02`, `PreCompact hook FAILED both times ("Invalid request code",
  the Drive fault)`, `grep -c '2026-09-02' exchange/precompact-receipts.log -> 0`.
- `N:\claude-gists-private\FINDING-2026-09-02-professional-C29-CANNOT-SEE-THE-BOUNDARY-WHOSE-RECORDER-DIED.md:124`
  [verbatim] (cropped) — "The structural finding. A check whose input is produced by the thing
  it grades cannot see a failure of that thing -- true whatever the reason the recorder missed,
  and untouched by the recorder being healthy today."

## Generalization

Any coverage/correctness check whose population is enumerated from a log, ledger, or receipt
file that the subject process itself writes shares this blind spot by construction: the subject
dying is indistinguishable, to the check, from the subject never having anything to report. The
check's own output can be loud and precise (it printed its population, named the one boundary it
did catch) and still be structurally unable to see the worse case sitting beside the one it
caught -- because the worse case is exactly the one that produced no row to grade. The fix the
same finding proposes (derive the population from an independent source the failure cannot
suppress -- here, `type: system` / `subtype: compact_boundary` events in the session JSONL,
reconciled against receipts, with `UNRECORDED` as a real fail state) generalizes: a coverage
check's population must come from a source outside the thing being covered, or the check's
"clean" result is unfalsifiable by the exact failure it was built for. `wiki/tracker/wayfinder-pr3-record-pipeline-2026-08-31.md`
row RP-29 (fixed in `wiki/intake-triage/H4-rp29-2026-09-02.md`) is the same shape one layer over:
`route_agent_return.py`'s PENDING-gate loop-prevention was keyed on the ledger row's own mutable
`PENDING` state, and the act of routing (editing that row to `ROUTED`) destroyed the gate's own
key -- the gate could not see its own prior action because that action erased the evidence the
gate needed to recognize it had already fired. Related: [[the-disproof-was-in-the-rows-own-column]]
(a check that had the disproof of a wrong verdict sitting in its own uninspected data, rather than
an absent population).

## Counter-evidence

none found, searched: `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md` and
`N:\claude-gists-private\RECEIPT-2026-09-02-secretary-HOOK-RACE-CHECK.md` for a coverage/dedupe
check in the bounded set whose population is drawn from an independent source rather than the
recorder it grades; every instance found derives its population from the subject's own output
(Professional's `boundary-census.py` fix, proposed in the C29 finding, is the one counter-design
on record, but it is PROPOSED, not yet applied, per the finding's own §3).

## Motivates

[SKILL: oath-pairing-check] — its own documented population is "a PreCompact receipt ... paired
iff a barrier record exists," which is the receipt-log-as-population shape this pattern names; a
boundary whose PreCompact hook died writes no receipt and is therefore invisible to
`oath-pairing-check` in exactly the way C29 measured, unless its population is later widened to
an independent boundary source (e.g. the same `type: system`/`compact_boundary` JSONL signal
Professional's proposed fix names).

## Probe

Sealed question above. Falsified if a re-read of `N:\claude-gists-private\FINDING-2026-09-02-professional-C29-CANNOT-SEE-THE-BOUNDARY-WHOSE-RECORDER-DIED.md`
shows the two named boundaries (08-18 `13ffb2bd`, 08-29 `95030d0d`, 09-02 `e8f94111`) were in
fact present in C29's 22-boundary graded population, or if `route_agent_return.py`'s pre-fix
PENDING gate is shown to have keyed on a source other than the ledger row it mutates.
