---
kind: skills-gate/held-out-validation-split
skill: dream
created: 2026-09-02 by lane GT-2 (CFL week map: extend GT-1's ground truth to the four skills Jon
  runs most -- skillUsage wake 102 / dream 33 / su-compact 82 / wayfinder 139)
pattern: GT-1 (wiki/intake-triage/GT1-skill-ground-truth-2026-09-02.md); this directory follows it
status: SEALED -- split.jsonl hashed into heldout.sha256 BEFORE the first scored run
---

# The held-out validation split for `.claude/skills/dream/SKILL.md`

## What the artifact is

the night-cycle packet in wiki/intake-triage/: frontmatter, six sweep sections each labelled RUN (with its denominator) or NOT RUN / SKIPPED (with its reason), the MR-88 orphan skip, the CFL-suffixed ruling queue, and a fable-mirror consult.

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

Fixtures live in `scripts/tests/fixtures/dream/`. A fixture is an **input situation** only.
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

- **R_best = 1.0** (105 passed / 0 failed) for the current skill text, sha
  `fd3ca46b`.
- **R_degraded = 0.6952** (73 passed / 32 failed) for a scratch copy with **the missing-input rule ('any sweep whose input is missing reports NOT RUN; it never reports no gaps found') and the CFL trunk-adaptation table (su-compact is this trunk's green; sweep (e) reports SKIPPED per MR-88; the queue is ruling-queue-cfl.md)**
  removed, sha `a792e99b`. The ablated copy was never written into the repo.
- **Pre-stated loss condition: R_degraded MUST be < R_best, or the split is rewritten until it can
  see the degradation. RESULT: 0.6952 < 1.0 -- satisfied on the first scored comparison,
  with no rewrite of the split.**

**What the ablation actually broke, by clause.** formulaic_green_named on 8 of 8 and every_sweep_labelled on 8 of 8; orphan_sweep_skipped_per_mr88 on 7 of 8; run_sweeps_have_denominators on 5. D02 is the sharpest: with MR-88 gone the degraded packet HAND-DERIVES the orphan census by grepping index.md and publishes six orphans -- the precise method that produced 5/5 false positives on trial 1. D03 is the second: the degraded packet writes 'no probes were generated and no gaps were found in this sweep', which is an unrun sweep wearing a clean one's clothes. D05 routes a Jon-gated row to the unsuffixed ruling-queue.md, which in this trunk silently creates a second queue.

## Where this split is BLIND, stated because a saturated instrument that hides its blind spots is
worse than no instrument

no_outward_action_claimed, packet_frontmatter_complete, no_clean_claim_on_missing_input and mirror_consult_recorded lost nothing under this ablation -- they are carried by text this ablation did not touch, so a proposal against those clauses would be scored blind here.

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
genuinely blind run are emitted at `N:\claude-cfl\gt2-blind\dream\`.

---

## ⭐ RECALIBRATED 2026-09-02 BY LANE GT-3 — and the first blind run is the reason

⛔ **The numbers above are v1. They stand as written (nothing deleted), and the v2 numbers below
govern.** Full working: **`calibration-2026-09-02.md`** in this directory.

**What the blind run found.** GT-2 emitted PRODUCE packets and a SONNET producer that had seen only
the skill text and the situation — never this split, never the property vocabulary, never the
checkers — wrote the artifacts. It scored **0.6**, BELOW the author's own **DEGRADED** variant
at 0.7476. ⚠️ **A degraded skill cannot really outproduce a whole one; what the number measured was
conformity to the author's RENDERING.**

**Classified, every FAIL row: 42 rows = 30 CHECKER-FALSE-POSITIVE, 2 PRODUCER-MISS,
10 PROPERTY-DEFECT.** The checker false positives are fixed. ⛔ **No check was weakened to make a
producer miss pass** — 2 rows are still FAIL and are named in the calibration file.

| | R_best (author, opus) | R_degraded (opus) | R_blind (SONNET, blind) |
|---|---|---|---|
| v1 | 1.0 | 0.7476 | 0.6 |
| **v2** | **1.0** | **0.7476** | **0.9806** |

**The seal.** `heldout.sha256` was `6e2ff4cd...` and is now `6422cb49...` — **re-sealed**, because PROPERTY-DEFECT rows were moved out of
`expected` into a `dropped_2026_09_02` map (recorded, never deleted). Every LEDGER row citing
the old hash fails G6 until re-scored.

⛔ **`R_blind` is a SONNET number; `R_best` and `R_degraded` are OPUS.** The cross-tier fence in
`wiki/concepts/wikiskill-adoption.md` binds here: the gap between them is a tier gap AND a skill gap
together, and this split cannot separate them.

⚠️ **The bound on this calibration, stated because it is the same class of defect it repairs:** the
lane that fixed the checkers could SEE the artifacts it re-scored. Every fix is justified against the
skill text in the check's own comment, and the author baseline and the degraded variant were
re-scored on every iteration so that no change could quietly lift the floor — **but that is a guard,
not a proof. The clean measurement is a SECOND blind run against the v2 seal.**
