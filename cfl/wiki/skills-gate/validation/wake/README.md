---
kind: skills-gate/held-out-validation-split
skill: wake
created: 2026-09-02 by lane GT-2 (CFL week map: extend GT-1's ground truth to the four skills Jon
  runs most -- skillUsage wake 102 / dream 33 / su-compact 82 / wayfinder 139)
pattern: GT-1 (wiki/intake-triage/GT1-skill-ground-truth-2026-09-02.md); this directory follows it
status: SEALED -- split.jsonl hashed into heldout.sha256 BEFORE the first scored run
---

# The held-out validation split for `.claude/commands/wake.md`

## What the artifact is

the one-screen wake report: measured clock and WAKE.md age, repo state, what the record says is owed (the reads, the peer mail both directions, the DERIVED live maps, the queue, the two wake checks with their outcomes), what is genuinely Jon's, and the single ticket resumed at.

## The rule that makes it held-out, and it is the whole point

⛔ **`split.jsonl` is NEVER handed to an editing lane.** A lane proposing a change to the skill
gets the SKILL text, the motivating record, and the ledger. It does not get this file, the
fixtures, or the property vocabulary. A split an editor can read is a split the editor optimises
against, and the resulting R measures memorisation of the checker rather than the skill.

- The runner (`scripts/audit/skills_validation.py`) and its GT-2 vocabulary module
  (`scripts/audit/gt2_properties.py`) may be read by anyone; the checks are mechanical and
  public. **The task set and the sealed properties are not.**
- If a split row is ever quoted into a proposal, that row is **burned**: it stays in the file (no
  deletion), a replacement is appended, and `heldout.sha256` changes -- which makes G6 fail every
  ledger row citing the old hash until each is re-scored. That is the intended blast radius.
- `heldout.sha256` is the seal, committed BEFORE any run, per CFL-D-012.

## What is in here

| file | what it is |
|---|---|
| `split.jsonl` | one row per task: `{id, fixture_path, expected[], grader_instruction}` |
| `heldout.sha256` | sha256 of `split.jsonl` -- the seal G6 checks ledger rows against |
| `baseline.json` | the first measured run: R_best, R_degraded, hashes, tier, ablation |
| `README.md` | this file |

Fixtures live in `scripts/tests/fixtures/wake/`. A fixture is an **input situation** only.
**No fixture contains its expected answer.**

## How a property is scored

`expected` entries without a prefix are **mechanical** -- pure functions of the produced
artifact's bytes. Entries prefixed `cold:` are **cold-reader** properties: a fresh grader with
nothing but the artifact answers `grader_instruction`. The runner emits those as **UNKNOWN** and
excludes them from the denominator. ⛔ **UNKNOWN never rounds to PASS.** `--merge-cold` folds a
cold lane's verdicts back in and reports the combined R separately.

R = passed / (passed + failed), over **properties**, not tasks -- task-level pass/fail throws away
the resolution that shows WHICH clause of the skill is carrying the artifact.

## The measured numbers, 2026-09-02

- **R_best = 1.0** (111 passed / 0 failed) for the current skill text, sha
  `ec032c7a`.
- **R_degraded = 0.7568** (84 passed / 27 failed) for a scratch copy with **Step 5 (the one-screen report and its 'do NOT hand him a ticket' clause) and the Fences block (reads-not-lands; a check that could not run is UNKNOWN and dominates a pass; excluded trunks are surfaced, not acted on)**
  removed, sha `61424aa7`. The ablated copy was never written into the repo.
- **Pre-stated loss condition: R_degraded MUST be < R_best, or the split is rewritten until it can
  see the degradation. RESULT: 0.7568 < 1.0 -- satisfied on the first scored comparison,
  with no rewrite of the split.**

**What the ablation actually broke, by clause.** jon_block_no_ticket on 8 of 8 and clock_measured_not_estimated on 8 of 8 -- with Step 5 gone there is no instruction to have a Jon block at all, and no instruction that the clock is MEASURED rather than the shell's proposal; wake_checks_have_outcomes on 5, report_five_elements on 3, and one each of unknown_token_present, no_carrier_byte_gate and excluded_trunk_surface_not_act. W03 is the sharpest row: without the fence, the degraded report renders a check that could not run as 'nothing turned up there - clean on that front', which is the exact I-did-not-look/there-is-nothing-there failure.

## Where this split is BLIND, stated because a saturated instrument that hides its blind spots is
worse than no instrument

Every wake task lost something, so this split has no fully blind row. What it does NOT test: whether the numbers in the report were really measured, and whether the ticket resumed at was the right one.

## The bound on the number itself

**The producing agent was this lane -- an opus-tier reader with the whole skill text in context.**
Not sonnet, not fable, not haiku. `wiki/concepts/wikiskill-adoption.md` fences exactly this:
never score a fable-authored skill with a haiku reader as if that were the consumer. A cross-tier
comparison against this baseline is invalid; re-measure R_before at the consuming tier first.

⚠️ **And the honest one, inherited from GT-1 unchanged: the split was not held out from ME.** This
lane wrote the properties and then produced the artifacts scored against them, so R_best is an
upper bound and the number's only sound use today is the RELATIVE comparison -- baseline vs
ablation, same producer, same tasks. The split IS held out from every future editing lane, which
is what this README enforces and what makes the NEXT measurement clean. Production packets for a
genuinely blind run are emitted at `N:\claude-cfl\gt2-blind\wake\`.

---

## ⭐ RECALIBRATED 2026-09-02 BY LANE GT-3 — and the first blind run is the reason

⛔ **The numbers above are v1. They stand as written (nothing deleted), and the v2 numbers below
govern.** Full working: **`calibration-2026-09-02.md`** in this directory.

**What the blind run found.** GT-2 emitted PRODUCE packets and a SONNET producer that had seen only
the skill text and the situation — never this split, never the property vocabulary, never the
checkers — wrote the artifacts. It scored **0.7387**, BELOW the author's own **DEGRADED** variant
at 0.7928. ⚠️ **A degraded skill cannot really outproduce a whole one; what the number measured was
conformity to the author's RENDERING.**

**Classified, every FAIL row: 29 rows = 20 CHECKER-FALSE-POSITIVE, 1 PRODUCER-MISS,
8 PROPERTY-DEFECT.** The checker false positives are fixed. ⛔ **No check was weakened to make a
producer miss pass** — 1 rows are still FAIL and are named in the calibration file.

| | R_best (author, opus) | R_degraded (opus) | R_blind (SONNET, blind) |
|---|---|---|---|
| v1 | 1.0 | 0.7928 | 0.7387 |
| **v2** | **1.0** | **0.7928** | **0.991** |

**The seal.** `heldout.sha256` is UNCHANGED at `3ea9bb6b...` — no row in this split uses a property owned by the module GT-3
edited, so there was nothing to re-seal. That is the reproduction result, not an
oversight.

⛔ **`R_blind` is a SONNET number; `R_best` and `R_degraded` are OPUS.** The cross-tier fence in
`wiki/concepts/wikiskill-adoption.md` binds here: the gap between them is a tier gap AND a skill gap
together, and this split cannot separate them.

⚠️ **The bound on this calibration, stated because it is the same class of defect it repairs:** the
lane that fixed the checkers could SEE the artifacts it re-scored. Every fix is justified against the
skill text in the check's own comment, and the author baseline and the degraded variant were
re-scored on every iteration so that no change could quietly lift the floor — **but that is a guard,
not a proof. The clean measurement is a SECOND blind run against the v2 seal.**
