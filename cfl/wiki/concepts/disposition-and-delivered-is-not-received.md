---
title: "Delivered Is Not Received — the Parent Defect Class"
aliases: ["delivered is not received", "a count is not a consequence", "count vs consequence", "the parent defect class", "written down is not acted on", "existence is not receipt"]
kind: concept
trunk: fl
branch: [cfl]
sub_branch: [governance]
branch_reason: "R-CONCEPTS; promoted 2026-08-23 from 16 days of frozen tracker material per Jon's 'forcing a wiki update' directive"
type: concept
first_seen: exchange/COMPACT-HANDOFF-2026-08-23-1520.md
source_count: 4
last_updated: 2026-08-23
maintained_by: wiki-master (proposal, this promotion pass — unratified)
---

# Delivered Is Not Received — the parent defect class

**The shape:** an artifact is produced — a file written, a template filled with placeholders, a
row added to a registry, a letter sent — and something downstream **counts the artifact's
existence as the outcome it was meant to produce.** The count is true. The conclusion it licenses
is false. Named 2026-08-23 from a Hank Green transcript on a cancer vaccine trial: eight of sixteen
patients "did not mount an immune response at all... their body just kind of didn't notice it
existed." **Measuring doses administered would have called that trial a success.**

Today's parent defect class is this: **2026-08-23 alone produced at least four independent
instances of it**, each found by a different lane, none aware of the others until this promotion
pass collected them.

## The four instances, named

1. **[[unsaid-ledger]] / promise 5.** `write_barrier_memory.py`'s `verify_instance()` existed and
   was correct — and was called only from `--selftest`, never from a real write. PR-1's promise
   ("every barrier writes its record") was graded VERIFIED by counting how many barrier *files*
   existed, not whether they were filled. True count: 27 files. True outcome: 11 filled, 16 empty
   skeletons, including all three `close` records. **The file existing was mistaken for the record
   being written.**

2. **[[probe-registry]]'s own PROBE-REGRESSIONS check.** A flat `grep FAIL` over an append-only
   registry counted every historical failure forever, including the literal string
   `RECOVERED (was FAIL)` — reporting 9 failures when the true count, read by highest run per
   probe id, was 4. **A row's existence in an append-only log was mistaken for its currency.**

3. **[[disposition-rate]]'s own first published number.** "3.1% disposition rate on agent returns"
   was literally true and installed a false belief: the denominator counted every subagent return,
   including lint checks and mechanical parses whose value was fully consumed inside the session
   that spawned them. **A return being logged was mistaken for a finding being ignored.** Corrected
   by its own author within the hour, against the very defect class the tool was built to detect —
   in the tool itself.

4. **[[de-pii-deriver]]'s term-presence test.** `depii_probe_reach.py` found 0 of 22 needle terms
   lost across the derived branch and read as fully reassuring. `scripts/` retains 3.0% of its
   bytes in that branch. **The words about the tool surviving (because the wiki discusses tools
   constantly) was mistaken for the tool surviving.**

## Why the pattern recurs: the count is always cheaper to build than the check

In every instance above, the cheap instrument (file exists / string matches / needle present) was
built and shipped; the expensive instrument (read the content / classify at write time / measure
bytes retained per directory) was not — until a corrective pass built it and found the gap. The
recurring, generalizable lesson from `disposition_rate.py`'s own docstring: **"THE LEDGER HAS NO
NOTION OF WHICH RETURNS CARRIED SOMETHING WORTH DISPOSITIONING. Fixing it means classifying at
write time, not at read time."** Classifying at write time is more expensive than counting at read
time, every single time — which is exactly why the count gets built first and mistaken for enough.

## The retrospective-scoring instance: PR-1's promises moved from 12 kept to 3/8/1

The clearest large-scale case of this class is PR-1's own promise retrospective
(`wiki/index.md:42`, `wiki/tracker/wayfinder-pr2-2026-08-23.md:206-279`), and it moved **twice, both
downward, both times because a later lane went and built the thing that measures the promise**:

| stage | score | what changed it |
|---|---|---|
| initial grading | 5 VERIFIED / 6 PARTIAL / 1 NOT DONE | graded largely by file/feature presence |
| after the unsaid-ledger seal | **4/7/1** | promise 5 downgraded — the validator that reads real records found 16/27 unfilled skeletons |
| after the supersession probe rebuild | **3/8/1** | promise 7 downgraded — P16 regressed on full-corpus rebuild; the PII amendment lost to its own superseded wording by 2.5% |

`wiki/tracker/wayfinder-pr2-2026-08-23.md:207-212` states the honest remainder plainly: "The
glossary was never written. The template eval loop is designed and has never run. The unsaid
ledger has never once produced an artifact — including at the two boundaries since it was
written. Consolidation and index-rebuild are ritual text, not enforced mechanism."

## What this class implies for review discipline

Per standing fence #5 (report the tally and the story separately): every number in this file is
labeled with the run that produced it and the date. Where a figure superseded an earlier one, both
are kept, in order, so the movement itself is legible — the downgrades are the valuable part, not
an embarrassment to smooth over.

## See also

- [[disposition-rate]] — the instrument that named this class and fell into it itself.
- [[unsaid-ledger]] — instance 1.
- [[probe-registry]] — instance 2, and the mechanism meant to catch future instances by default.
- [[de-pii-deriver]] — instance 4.
- [[supersession-and-old-rules-outranking-amendments]] — the mechanism behind the promise-7 downgrade.
- [[memory-core]] — the system whose promise-5 downgrade is instance 1's origin.
