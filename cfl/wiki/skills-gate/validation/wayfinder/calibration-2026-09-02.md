---
kind: skills-gate/split-calibration
skill: wayfinder
date: 2026-09-02
lane: GT-3 (calibrate the skill-validation checkers against BLIND producer output, then re-seal)
finding: LEDGER "GT-2 blind run 1" / GT-2-F9 -- blind sonnet producers scored BELOW the author's own
  DEGRADED variants on three of five skills, so the mechanical checkers were measuring conformity to
  the author's rendering rather than skill quality (GT-2-F7: line-scoped checks fail correct prose
  that wrapped)
status: CALIBRATED -- split re-sealed
---

# `wayfinder` -- calibration against blind producer output, 2026-09-02

## The three numbers, before and after

| | R_best (author, opus) | R_degraded (ablated skill, opus) | R_blind (SONNET, blind) |
|---|---|---|---|
| **before calibration** | 1.0 | 0.6714 | **0.5316** |
| **after calibration** | 1.0 | 0.6714 | **0.7571** |

⛔ **`R_blind` is a SONNET number and the other two are OPUS.**
`wiki/concepts/wikiskill-adoption.md` forbids reading one tier's number as another's. R_blind below
R_best mixes a tier gap with a skill gap, and **this split cannot separate them.**

## The seal

| | sha256 of `split.jsonl` |
|---|---|
| before (v1, sealed by GT-2 before its first scored run) | `2c13d06b...` |
| after (v2, this calibration) | `b00d5576...` |

**Re-sealed.** Rows changed: property names were moved OUT of `expected` and INTO a
`dropped_2026_09_02` map that records each one with its reason.
⛔ **Nothing was deleted** -- the names and the reasons stay in the file, per Jon's standing
*4. Yeah no deletion. And no writing PII to Github.* Every LEDGER row citing the v1 hash now
fails G6 until it is re-scored; that is the intended blast radius, and it is why the drop list
above is short and every entry carries a reason.

## Every blind FAIL row, classified

**74 FAIL rows: 22 CHECKER-FALSE-POSITIVE, 34 PRODUCER-MISS, 18 PROPERTY-DEFECT.**

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
| `acceptance_tests_failable` | PROPERTY-DEFECT | 7 |
| `every_ticket_has_acceptance_test` | PROPERTY-DEFECT | 7 |
| `out_of_scope_items_carry_why` | CHECKER-FALSE-POSITIVE | 5 |
| `every_ticket_has_question` | CHECKER-FALSE-POSITIVE | 4 |
| `map_body_lists_no_open_tickets` | CHECKER-FALSE-POSITIVE | 4 |
| `tracker_choice_named` | CHECKER-FALSE-POSITIVE | 4 |
| `one_ticket_per_session_with_research_exception` | PROPERTY-DEFECT | 4 |
| `claim_before_work` | PRODUCER-MISS | 4 |
| `destination_is_one_or_two_lines` | PRODUCER-MISS | 4 |
| `map_section:destination` | PRODUCER-MISS | 4 |
| `map_section:notes` | PRODUCER-MISS | 4 |
| `every_ticket_has_question` | PRODUCER-MISS | 3 |
| `every_ticket_has_type_label` | PRODUCER-MISS | 3 |
| `blocking_convention_named` | CHECKER-FALSE-POSITIVE | 2 |
| `destination_is_one_or_two_lines` | CHECKER-FALSE-POSITIVE | 2 |
| `blocking_convention_named` | PRODUCER-MISS | 2 |
| `fog_items_are_in_scope` | PRODUCER-MISS | 2 |
| `map_section:fog` | PRODUCER-MISS | 2 |
| `map_section:out_of_scope` | PRODUCER-MISS | 2 |
| `out_of_scope_items_carry_why` | PRODUCER-MISS | 2 |
| `graduated_fog_cleared` | CHECKER-FALSE-POSITIVE | 1 |
| `fog_and_scope_disjoint` | PRODUCER-MISS | 1 |
| `graduated_fog_cleared` | PRODUCER-MISS | 1 |

## What happened, in detail

Wayfinder is the skill where the checker was LEAST at fault: 34 of its 74 FAIL rows survive calibration
as real producer misses, the highest share of the five. It is also the only split that carried
properties with no basis in the skill text at all.

`every_ticket_has_acceptance_test` and `acceptance_tests_failable` are **DROPPED**. The word
"acceptance" occurs ZERO times in `skills/wayfinder/SKILL.md`; the ticket body template the skill gives
is `## Question` and nothing else. Those two graded a convention imported from another skill and failed
7 of 8 blind rows -- 14 of the 74. `one_ticket_per_session_with_research_exception` is **DROPPED** on
the four rows that carried it: it asked the artifact to RESTATE a rule that binds the session, and
failed four rows that obeyed it silently. A conduct proxy (count the closures the artifact records) was
drafted and **WITHDRAWN** because it failed the AUTHOR baseline row Y03 -- the proxy was not sound
either, and recording that is more useful than shipping it.

The checker fixes are the familiar shapes. `destination_is_one_or_two_lines` counted PHYSICAL lines and
failed two destinations that are two sentences hard-wrapped onto three lines. `every_ticket_has_question`
required Question as a heading and the artifacts write `- Question:` as a bullet.
`map_body_lists_no_open_tickets` defined the map body as everything before the end of Out-of-scope, so
an artifact with no Out-of-scope section had its whole text, ticket definitions included, treated as map
body. `tracker_choice_named` required that exactly one tracker be MENTIONED, so *"Tracker is
`wiki/tracker/`, not GitHub issues"* -- the choice made explicitly, in the CFL Adaptation Note's own
framing -- scored as indecision.

⚠️ **The contestable classification, stated because it moves the number: 22 of the 34 surviving misses
are `map_section:*`, `destination_is_one_or_two_lines` and the fog / out-of-scope rows on Y02, Y03, Y04
and Y07 -- the four fixtures whose situation is "the map already exists; work one ticket."** The blind
producer emitted the resolution plus the map sections it CHANGED; the author's baseline re-emitted the
whole map. The skill does not settle which is the artifact: it says the map is *"an index, not a store"*
and never says a work session restates it. Those rows are recorded as PRODUCER MISS, which is the
conservative reading and the one that keeps R_blind LOWER. **The honest statement is that the wayfinder
artifact contract is UNDECIDED, and until a fixture says which artifact it wants, roughly 22 of these 34
misses are unadjudicated rather than established.**

## Pre-stated loss conditions, and the result

Stated before the re-score, per CFL-D-012:

1. **After calibration, R_blind must NOT exceed R_best.** Result: 0.7571 <= 1.0 -- **SATISFIED**.
2. **The degraded variant must still score below the author baseline.** Result: 0.6714 < 1.0 --
   **SATISFIED**.
3. **If R_blind still sits below R_degraded, this split is UNKNOWN-CALIBRATION and says so.** Result:
   R_blind 0.7571 vs R_degraded 0.6714 -- **above degraded, so NOT UNKNOWN-CALIBRATION**.

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
