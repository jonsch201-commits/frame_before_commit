---
kind: skills-gate/split-calibration
skill: dream
date: 2026-09-02
lane: GT-3 (calibrate the skill-validation checkers against BLIND producer output, then re-seal)
finding: LEDGER "GT-2 blind run 1" / GT-2-F9 -- blind sonnet producers scored BELOW the author's own
  DEGRADED variants on three of five skills, so the mechanical checkers were measuring conformity to
  the author's rendering rather than skill quality (GT-2-F7: line-scoped checks fail correct prose
  that wrapped)
status: CALIBRATED -- split re-sealed
---

# `dream` -- calibration against blind producer output, 2026-09-02

## The three numbers, before and after

| | R_best (author, opus) | R_degraded (ablated skill, opus) | R_blind (SONNET, blind) |
|---|---|---|---|
| **before calibration** | 1.0 | 0.7476 | **0.6** |
| **after calibration** | 1.0 | 0.7476 | **0.9806** |

⛔ **`R_blind` is a SONNET number and the other two are OPUS.**
`wiki/concepts/wikiskill-adoption.md` forbids reading one tier's number as another's. R_blind below
R_best mixes a tier gap with a skill gap, and **this split cannot separate them.**

## The seal

| | sha256 of `split.jsonl` |
|---|---|
| before (v1, sealed by GT-2 before its first scored run) | `6e2ff4cd...` |
| after (v2, this calibration) | `6422cb49...` |

**Re-sealed.** Rows changed: property names were moved OUT of `expected` and INTO a
`dropped_2026_09_02` map that records each one with its reason.
⛔ **Nothing was deleted** -- the names and the reasons stay in the file, per Jon's standing
*4. Yeah no deletion. And no writing PII to Github.* Every LEDGER row citing the v1 hash now
fails G6 until it is re-scored; that is the intended blast radius, and it is why the drop list
above is short and every entry carries a reason.

## Every blind FAIL row, classified

**42 FAIL rows: 30 CHECKER-FALSE-POSITIVE, 2 PRODUCER-MISS, 10 PROPERTY-DEFECT.**

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
| `packet_frontmatter_complete` | PROPERTY-DEFECT | 8 |
| `dangling_excludes_syntax_docs` | CHECKER-FALSE-POSITIVE | 7 |
| `dangling_resolver_mandated` | CHECKER-FALSE-POSITIVE | 7 |
| `every_sweep_labelled` | CHECKER-FALSE-POSITIVE | 7 |
| `orphan_sweep_skipped_per_mr88` | CHECKER-FALSE-POSITIVE | 7 |
| `unknown_token_present` | PRODUCER-MISS | 2 |
| `formulaic_green_named` | CHECKER-FALSE-POSITIVE | 1 |
| `no_auto_ingest` | CHECKER-FALSE-POSITIVE | 1 |
| `every_sweep_labelled` | PROPERTY-DEFECT | 1 |
| `six_sweeps_present` | PROPERTY-DEFECT | 1 |

## What happened, in detail

One character carried this skill's whole gap. `SWEEP_HDR` required the author's `(a)` rendering -- the
closing parenthesis was mandatory -- and all eight blind packets head their sweeps `## a. Coverage
census`. Zero sweep blocks were found in any of them, which failed `every_sweep_labelled` 8/8 and
cascaded into the three (e)-scoped properties (`orphan_sweep_skipped_per_mr88`,
`dangling_excludes_syntax_docs`, `dangling_resolver_mandated`) at 7/8 each: 29 of the 42 FAIL rows.

A second boundary defect hid underneath it. `_blocks` gave the LAST sweep no stop, so on D03 sweep (f)
swallowed the "## Disposition" section, which says sweep (c) is "flagged NOT RUN" -- and (f), a sweep
that ran and reported 214 / 31 / 9 / 2, was scored as an unreasoned NOT RUN.

Three smaller ones are the same shape. `no_auto_ingest` failed D01 for *"nothing here is
auto-[newline]ingested"*: its negation window was `[^.\n]{0,40}`, which cannot cross a line break.
`dangling_excludes_syntax_docs` wanted "syntax documentation" with a space and the packets wrote
"syntax-documentation". `formulaic_green_named` wanted the literal "su-compact" from a packet that named
`su_gate.sh` and `su_close.sh` -- the two scripts su-compact Step 1 actually runs.

`packet_frontmatter_complete` is the PROPERTY DEFECT: it demanded the exact keys `kind`, `date` and
`sweep`, and `.claude/skills/dream/SKILL.md` names NO frontmatter key anywhere -- it says only "same
format as any other intake packet". A producer holding only the skill text could not have known them.
Rewritten to accept the synonyms the artifacts used (`type` for `kind`, `sweeps-run`/`status` for
`sweep`) with an ISO date still required; a missing field still fails.

The two PRODUCER MISSES are `unknown_token_present` on D03 and D07 -- a sweep that could not run, and a
night cycle whose gate never opened, neither of which marks its coverage UNKNOWN. The skill's own CFL
note says *"An ABSENT gate is UNKNOWN, never PASS"*, so the token is the skill's vocabulary, not the
author's. They stay failed.

## Pre-stated loss conditions, and the result

Stated before the re-score, per CFL-D-012:

1. **After calibration, R_blind must NOT exceed R_best.** Result: 0.9806 <= 1.0 -- **SATISFIED**.
2. **The degraded variant must still score below the author baseline.** Result: 0.7476 < 1.0 --
   **SATISFIED**.
3. **If R_blind still sits below R_degraded, this split is UNKNOWN-CALIBRATION and says so.** Result:
   R_blind 0.9806 vs R_degraded 0.7476 -- **above degraded, so NOT UNKNOWN-CALIBRATION**.

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
