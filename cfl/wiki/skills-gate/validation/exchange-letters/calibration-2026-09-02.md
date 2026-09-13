---
kind: skills-gate/split-calibration
skill: exchange-letters
date: 2026-09-02
lane: GT-3 (calibrate the skill-validation checkers against BLIND producer output, then re-seal)
finding: LEDGER "GT-2 blind run 1" / GT-2-F9 -- blind sonnet producers scored BELOW the author's own
  DEGRADED variants on three of five skills, so the mechanical checkers were measuring conformity to
  the author's rendering rather than skill quality (GT-2-F7: line-scoped checks fail correct prose
  that wrapped)
status: CALIBRATED -- split unchanged, seal unchanged
---

# `exchange-letters` -- calibration against blind producer output, 2026-09-02

## The three numbers, before and after

| | R_best (author, opus) | R_degraded (ablated skill, opus) | R_blind (SONNET, blind) |
|---|---|---|---|
| **before calibration** | 1.0 | 0.8672 | **0.9141** |
| **after calibration** | 1.0 | 0.8672 | **0.9141** |

⛔ **`R_blind` is a SONNET number and the other two are OPUS.**
`wiki/concepts/wikiskill-adoption.md` forbids reading one tier's number as another's. R_blind below
R_best mixes a tier gap with a skill gap, and **this split cannot separate them.**

## The seal

| | sha256 of `split.jsonl` |
|---|---|
| before (v1, sealed by GT-2 before its first scored run) | `51e2f7c8...` |
| after (v2, this calibration) | `51e2f7c8...` |

**NOT re-sealed, and that is the result.** No row changed, because no property in this split is
owned by the module this lane edited. The hash is byte-identical to GT-2's seal.

## Every blind FAIL row, classified

**11 FAIL rows: 0 CHECKER-FALSE-POSITIVE, 11 PRODUCER-MISS, 0 PROPERTY-DEFECT.**

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
| `byte_verify_named` | PRODUCER-MISS | 1 |
| `deadline_three_actions` | PRODUCER-MISS | 1 |
| `delivery_state_ladder` | PRODUCER-MISS | 1 |
| `expires_parseable` | PRODUCER-MISS | 1 |
| `fm:expires` | PRODUCER-MISS | 1 |
| `no_expires_and_unclocked_declared_deliberate` | PRODUCER-MISS | 1 |
| `on_silence_acting_label` | PRODUCER-MISS | 1 |
| `on_silence_sentence_not_label` | PRODUCER-MISS | 1 |
| `receipt_mark_present` | PRODUCER-MISS | 1 |
| `three_states_named` | PRODUCER-MISS | 1 |
| `unreceipted_not_declined` | PRODUCER-MISS | 1 |

## What happened, in detail

⭐ **NO CHANGE, and that is the reproduction result.**
`wiki/skills-gate/validation/exchange-letters/split.jsonl` uses ZERO properties from
`gt2_properties.py` -- all 24 of its mechanical property names are owned by `skills_validation.check()`
ABOVE the GT-2 delegation point, and `skills_validation.py` was not modified by this lane. The split was
not re-sealed; `heldout.sha256` is byte-identical.

R_blind = **117/128 = 0.9141**, exactly as GT-2 published it, and R_best and R_degraded are unchanged at
1.0 and 0.8672. **Delta per property: 0 for all 24.**

All 11 FAIL rows re-classify as PRODUCER MISS: T01 (`on_silence` is not an acting sentence; no
byte-verification named), T05 (no `expires`, so unparseable, and only one deadline action),
T06 (unclocked but the deliberateness is not declared), T08 (no receipt mark), T10 (names only
DELIVERED of the three-state ladder, and never says "unreceipted").

## Pre-stated loss conditions, and the result

Stated before the re-score, per CFL-D-012:

1. **After calibration, R_blind must NOT exceed R_best.** Result: 0.9141 <= 1.0 -- **SATISFIED**.
2. **The degraded variant must still score below the author baseline.** Result: 0.8672 < 1.0 --
   **SATISFIED**.
3. **If R_blind still sits below R_degraded, this split is UNKNOWN-CALIBRATION and says so.** Result:
   R_blind 0.9141 vs R_degraded 0.8672 -- **above degraded, so NOT UNKNOWN-CALIBRATION**.

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
