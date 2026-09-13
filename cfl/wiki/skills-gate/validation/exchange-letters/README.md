---
kind: skills-gate/held-out-validation-split
skill: exchange-letters
created: 2026-09-02 by lane GT-1 (CFL week map: ground truth for skill improvement)
authority: Jon, 2026-09-01/02 — "ground truth - how well defined is it currently in a
  wikiskills context ... i require you ticket and improve in this context" and
  "ticket and prototype what is missing" (typos his)
status: SEALED — split.jsonl hashed in heldout.sha256 BEFORE the first run
---

# The held-out validation split for `skills/exchange-letters`

## Why this exists

`wiki/skills-gate/GATE-SPEC.md` says the gate accepts **only strict improvement**, and its
own honest footer says what it is not: *"A benchmark suite. The paper gates on held-out
task splits; CFL's validation probes are E4-style sealed cold-reader panels and runnable
selftests."* Every ACCEPTED row so far reads `Strict improvement: yes` — as prose. There
was no number, and with no number "strict" is an adjective, not a test.

This directory is the number for one skill.

## The rule that makes it held-out, and it is the whole point

⛔ **`split.jsonl` is NEVER handed to an editing lane.** A lane proposing a change to
`skills/exchange-letters/SKILL.md` gets the SKILL, the motivating record, and the ledger.
It does not get this file, these fixtures, or the property vocabulary. A split an editor
can read is a split the editor optimises against, and the resulting R measures memorisation
of the checker, not the skill.

Consequences, stated so nobody has to infer them:

- The gate runner (`scripts/audit/skills_validation.py`) may be read by anyone; the checks
  are mechanical and public. **The task set and the sealed properties are not.**
- If a split row is ever quoted into a proposal, that row is **burned**: it stays in the
  file (no deletion) and a replacement row is appended, and `heldout.sha256` changes — which
  makes G6 in `scripts/audit/skills_gate_check.py` fail every row citing the old hash until
  each is re-scored. That is the intended blast radius.
- `heldout.sha256` is the seal. It is committed BEFORE any run, exactly as
  `wiki/tracker/PROBE-REGISTRY.md` requires ("expectations are SEALED BEFORE any run",
  CFL-D-012).

## What is in here

| file | what it is |
|---|---|
| `split.jsonl` | one row per task: `{id, fixture_path, expected[], grader_instruction}` |
| `heldout.sha256` | sha256 of `split.jsonl` — the seal G6 checks ledger rows against |
| `baseline.json` | the first measured run: R_best, R_degraded, hashes, tier, timestamp |
| `README.md` | this file |

Fixtures live in `scripts/tests/fixtures/letters/`. A fixture is an **input situation** only
— a finding to send, a reply owed, a receipt due, a silence to report, an expiry, a
cross-trunk correction, a standing notice, a size-budgeted verdict, a competing-constraint
quote letter, an unverifiable-arrival receipt. **No fixture contains its expected answer.**

## How a property is scored

`expected` entries are property strings. Those without a prefix are **mechanical** — pure
functions of the produced letter's bytes, checked by `skills_validation.py`, reusing
`lint_silence_clause.py` and `on_silence_report.py` rather than reimplementing rules 8 and 9.
Entries prefixed `cold:` are **cold-reader** properties: a fresh grader with nothing but the
letter answers `grader_instruction`. The runner emits those as **UNKNOWN** and excludes them
from the denominator. ⛔ **UNKNOWN never rounds to PASS.** `--merge-cold` folds a cold lane's
verdicts back in and the combined R is reported separately.

R = passed / (passed + failed), over properties, not tasks — task-level pass/fail throws away
the resolution that shows WHICH clause of the skill is carrying the letter.

## The bound this split does not clear, stated because a saturated instrument is a lie

The 2026-09-02 baseline scored **R_best = 1.0 (128/128 mechanical)**. The producing agent was
an **opus-tier** reader with the whole SKILL.md in context. So on this run the split has
**no headroom**: it can measure DEGRADATION (it did: 0.8672 with rules 6 and 8 removed) and it
cannot measure IMPROVEMENT above the current text at this tier. G6 therefore cannot be
satisfied by an exchange-letters proposal until either (a) the split gains rows the current
skill fails, or (b) R_before is re-measured at the tier the change actually targets — which is
the cross-tier fence `wiki/concepts/wikiskill-adoption.md` already carries: **never score a
fable-authored skill with a haiku reader as if that were the consumer.** Ticketed in the GT-1
report; it is a property of this instrument, not a footnote.

---

## ⭐ RECALIBRATED 2026-09-02 BY LANE GT-3 — and the first blind run is the reason

⛔ **The numbers above are v1. They stand as written (nothing deleted), and the v2 numbers below
govern.** Full working: **`calibration-2026-09-02.md`** in this directory.

**What the blind run found.** GT-2 emitted PRODUCE packets and a SONNET producer that had seen only
the skill text and the situation — never this split, never the property vocabulary, never the
checkers — wrote the artifacts. It scored **0.9141**, above the author's own **DEGRADED** variant
at 0.8672. ⚠️ **A degraded skill cannot really outproduce a whole one; what the number measured was
conformity to the author's RENDERING.**

**Classified, every FAIL row: 11 rows = 0 CHECKER-FALSE-POSITIVE, 11 PRODUCER-MISS,
0 PROPERTY-DEFECT.** The checker false positives are fixed. ⛔ **No check was weakened to make a
producer miss pass** — 11 rows are still FAIL and are named in the calibration file.

| | R_best (author, opus) | R_degraded (opus) | R_blind (SONNET, blind) |
|---|---|---|---|
| v1 | 1.0 | 0.8672 | 0.9141 |
| **v2** | **1.0** | **0.8672** | **0.9141** |

**The seal.** `heldout.sha256` is UNCHANGED at `51e2f7c8...` — no row in this split uses a property owned by the module GT-3
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
