---
kind: skills-gate/held-out-validation-split
skill: su-compact
created: 2026-09-02 by lane GT-2 (CFL week map: extend GT-1's ground truth to the four skills Jon
  runs most -- skillUsage wake 102 / dream 33 / su-compact 82 / wayfinder 139)
pattern: GT-1 (wiki/intake-triage/GT1-skill-ground-truth-2026-09-02.md); this directory follows it
status: SEALED -- split.jsonl hashed into heldout.sha256 BEFORE the first scored run
---

# The held-out validation split for `.claude/commands/su-compact.md`

## What the artifact is

the close receipt and its landing list: the caller-stated as-of date, a verdict carrying both exit codes with UNKNOWN above the failures, a tally whose every number names the command that produced it, interpretation kept separate, a landing list where every item carries a sha AND a readback, the PROMISES ledger, what is genuinely Jon's, the ASK as its own block, and the fenced compact instruction.

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

Fixtures live in `scripts/tests/fixtures/su-compact/`. A fixture is an **input situation** only.
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

- **R_best = 1.0** (132 passed / 0 failed) for the current skill text, sha
  `b06e130e`.
- **R_degraded = 0.4242** (56 passed / 76 failed) for a scratch copy with **Step 2 (the ordered landing list, the carrier refresh with its struck byte gate, the read-chain verify, the map update) and Step 3 (verdict, tally, separated interpretation, what is genuinely Jon's, STATE THE ASK, what the next session resumes at)**
  removed, sha `278ac3a4`. The ablated copy was never written into the repo.
- **Pre-stated loss condition: R_degraded MUST be < R_best, or the split is rewritten until it can
  see the degradation. RESULT: 0.4242 < 1.0 -- satisfied on the first scored comparison,
  with no rewrite of the split.**

**What the ablation actually broke, by clause.** ask_stated_as_its_own_block on 8 of 8 -- from outside, a session that has gone quiet and a session waiting on Jon look identical, and the degraded receipts are all quiet; then 7 of 8 each on verdict_with_both_exit_codes, tally_rows_carry_commands, promises_table_present, next_resume_ticket_named, interpretation_labelled_separately, every_landing_has_sha and every_landing_has_readback. S04 is the sharpest row: with Step 2.3 gone the degraded receipt reinstates the struck 11,901 B carrier gate and books a trim as owed -- the correction reverted BY PROCESS, which is exactly what the 2026-08-14 note said would happen at the very next close.

## Where this split is BLIND, stated because a saturated instrument that hides its blind spots is
worse than no instrument

no_dry_run and no_main_merge_or_canonical lost nothing (they live in the Fences block, untouched here), and as_of_not_shell_default survived on 8 of 8 because Step 0 is outside the ablation.

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
genuinely blind run are emitted at `N:\claude-cfl\gt2-blind\su-compact\`.

---

## ⭐ RECALIBRATED 2026-09-02 BY LANE GT-3 — and the first blind run is the reason

⛔ **The numbers above are v1. They stand as written (nothing deleted), and the v2 numbers below
govern.** Full working: **`calibration-2026-09-02.md`** in this directory.

**What the blind run found.** GT-2 emitted PRODUCE packets and a SONNET producer that had seen only
the skill text and the situation — never this split, never the property vocabulary, never the
checkers — wrote the artifacts. It scored **0.553**, above the author's own **DEGRADED** variant
at 0.3769. ⚠️ **A degraded skill cannot really outproduce a whole one; what the number measured was
conformity to the author's RENDERING.**

**Classified, every FAIL row: 59 rows = 36 CHECKER-FALSE-POSITIVE, 15 PRODUCER-MISS,
8 PROPERTY-DEFECT.** The checker false positives are fixed. ⛔ **No check was weakened to make a
producer miss pass** — 15 rows are still FAIL and are named in the calibration file.

| | R_best (author, opus) | R_degraded (opus) | R_blind (SONNET, blind) |
|---|---|---|---|
| v1 | 1.0 | 0.3769 | 0.553 |
| **v2** | **1.0** | **0.3769** | **0.8846** |

**The seal.** `heldout.sha256` was `93261764...` and is now `e1864f33...` — **re-sealed**, because PROPERTY-DEFECT rows were moved out of
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
