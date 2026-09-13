---
kind: skills-gate/split-calibration
skill: su-compact
date: 2026-09-02
lane: GT-3 (calibrate the skill-validation checkers against BLIND producer output, then re-seal)
finding: LEDGER "GT-2 blind run 1" / GT-2-F9 -- blind sonnet producers scored BELOW the author's own
  DEGRADED variants on three of five skills, so the mechanical checkers were measuring conformity to
  the author's rendering rather than skill quality (GT-2-F7: line-scoped checks fail correct prose
  that wrapped)
status: CALIBRATED -- split re-sealed
---

# `su-compact` -- calibration against blind producer output, 2026-09-02

## The three numbers, before and after

| | R_best (author, opus) | R_degraded (ablated skill, opus) | R_blind (SONNET, blind) |
|---|---|---|---|
| **before calibration** | 1.0 | 0.3769 | **0.553** |
| **after calibration** | 1.0 | 0.3769 | **0.8846** |

⛔ **`R_blind` is a SONNET number and the other two are OPUS.**
`wiki/concepts/wikiskill-adoption.md` forbids reading one tier's number as another's. R_blind below
R_best mixes a tier gap with a skill gap, and **this split cannot separate them.**

## The seal

| | sha256 of `split.jsonl` |
|---|---|
| before (v1, sealed by GT-2 before its first scored run) | `93261764...` |
| after (v2, this calibration) | `e1864f33...` |

**Re-sealed.** Rows changed: property names were moved OUT of `expected` and INTO a
`dropped_2026_09_02` map that records each one with its reason.
⛔ **Nothing was deleted** -- the names and the reasons stay in the file, per Jon's standing
*4. Yeah no deletion. And no writing PII to Github.* Every LEDGER row citing the v1 hash now
fails G6 until it is re-scored; that is the intended blast radius, and it is why the drop list
above is short and every entry carries a reason.

## Every blind FAIL row, classified

**59 FAIL rows: 36 CHECKER-FALSE-POSITIVE, 15 PRODUCER-MISS, 8 PROPERTY-DEFECT.**

- **CHECKER-FALSE-POSITIVE** -- the artifact satisfies the property in substance; the check was
  line-scoped, order-scoped, section-name-scoped, or keyed on the author's phrasing. **Fixed, and each
  fix carries its evidence in a comment on the check itself.**
- **PRODUCER-MISS** -- the artifact really lacks the property.
  ⛔ **Not one check was weakened to make one of these pass.**
- **PROPERTY-DEFECT** -- the property is not checkable from the artifact alone, or it contradicts the
  skill text. **Rewritten or dropped, each with its reason recorded in the split row itself under
  `dropped_2026_09_02` and in the check's own source comment.**

| property | class | rows |
|---|---|---|
| `ask_stated_as_its_own_block` | CHECKER-FALSE-POSITIVE | 7 |
| `every_landing_has_readback` | CHECKER-FALSE-POSITIVE | 7 |
| `every_landing_has_sha` | CHECKER-FALSE-POSITIVE | 7 |
| `tally_rows_carry_commands` | PRODUCER-MISS | 7 |
| `barrier_verify_named` | CHECKER-FALSE-POSITIVE | 6 |
| `jon_block_no_ticket` | CHECKER-FALSE-POSITIVE | 6 |
| `as_of_not_shell_default` | PROPERTY-DEFECT | 6 |
| `promises_table_present` | PRODUCER-MISS | 6 |
| `compact_block_six_elements` | PRODUCER-MISS | 2 |
| `no_carrier_byte_gate` | CHECKER-FALSE-POSITIVE | 1 |
| `skipped_step_named_loudly` | CHECKER-FALSE-POSITIVE | 1 |
| `unknown_reported_above_failures` | CHECKER-FALSE-POSITIVE | 1 |
| `jon_block_no_ticket` | PROPERTY-DEFECT | 1 |
| `unknown_token_present` | PROPERTY-DEFECT | 1 |

## What happened, in detail

Two section-name assumptions cost 20 rows. `every_landing_has_sha` and `every_landing_has_readback`
looked for a heading matching `landing list|what landed`; all eight blind receipts carry the same four
landings inside a table under `## Tally`, which is the heading Step 3.2 actually names. They now find the
four Step-2 artifacts (commit, wake map, carrier, wayfinder map) wherever they are reported, and accept a
readback that sits in a neighbouring row -- the readback for a commit is "uncommitted 0 / unpushed 0",
and no receipt puts that inside the commit's own cell.

`ask_stated_as_its_own_block` (7/8) required a markdown HEADING containing "ask"; the receipts write
`**ASK: compact.**` as a standalone bolded lead, which is a block by any reader's reckoning, and the
skill says block, not heading. `barrier_verify_named` (6/8) was ORDER-scoped -- it wanted `--verify`
within 80 characters AFTER the script name, and the receipts report it in the Result cell, which
precedes the Source cell. Same row, same fact, wrong direction. `jon_block_no_ticket` (6/8) failed on
the bare verb "rebuild" inside *"render/consolidate/rebuild/probe all green"* -- a report of work done,
not a ticket handed to Jon.

`as_of_not_shell_default` is the PROPERTY DEFECT: it looked for meta-commentary about where the date
came from ("caller", "proposal") and failed six receipts that each stamped a correct explicit as-of.
Step 0 binds the COMMAND's behaviour; whether the caller stated the date is not decidable from the
receipt unless the receipt has no date or defers to "today". Those two are decidable and are what it
now checks.

⛔ **The 15 PRODUCER MISSES are real and stay failed.** `tally_rows_carry_commands` (7): the Carrier and
Wayfinder-map rows give "Charter A2 refresh" and a bare path where Step 3.2 asks for the command that
produced the number. `promises_table_present` (6): three receipts carry no unsaid ledger at all, and
three carry one whose rows the check could not read as filled until the "when" half was allowed to be a
condition rather than only a date. `compact_block_six_elements` (2): S03 omits corrections, S06 omits
open-but-not-blocking.

## Pre-stated loss conditions, and the result

Stated before the re-score, per CFL-D-012:

1. **After calibration, R_blind must NOT exceed R_best.** Result: 0.8846 <= 1.0 -- **SATISFIED**.
2. **The degraded variant must still score below the author baseline.** Result: 0.3769 < 1.0 --
   **SATISFIED**.
3. **If R_blind still sits below R_degraded, this split is UNKNOWN-CALIBRATION and says so.** Result:
   R_blind 0.8846 vs R_degraded 0.3769 -- **above degraded, so NOT UNKNOWN-CALIBRATION**.

**VERDICT: CALIBRATED.**

## What this calibration does NOT establish

⚠️ **A calibrated checker is not a validated skill.** What moved here is the instrument. The instrument
still measures only the artifact's mechanically checkable PROPERTIES -- never whether the artifact is
TRUE, whether the numbers it reports were really measured, or whether a cold reader could act on it.
Those are the `cold:` half of every split row and they are still **UNKNOWN**.
⛔ **UNKNOWN never rounds to PASS.**

⚠️ **And the calibration was performed by a lane that could SEE the blind artifacts.** Every fix in
`scripts/audit/gt2_properties.py` was written while looking at the output it then re-scored. The guards
against tuning to the sample are that (a) every change is justified against the SKILL TEXT, quoted in
the check's own comment, and (b) the author baseline AND the degraded variant were re-scored on every
iteration, and any change that lifted the degraded score toward the baseline was reverted. **That is a
guard, not a proof. The next clean measurement is a SECOND blind run against this v2 seal, by producers
who have never been scored by this module.**
