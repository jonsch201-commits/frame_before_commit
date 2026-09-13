---
format: cfl-page/v1
kind: pattern
slug: a-limitation-rendered-as-a-completed-measurement
title: "A Limitation Rendered As A Completed Measurement"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "missing input labelled a safety determination partial degrade read as trunk-wide number split not held out from producer upper-bound artifact"
aliases: [missing-input-as-safety-verdict, partial-coverage-as-full-coverage, ceiling-reported-as-a-floor]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "three independent instances this cycle, each caught by the instrument's own author before publication or by a peer within the same day: hook_harness.py v1's SKIPPED-DESTRUCTIVE overload, the pre-v5 partial-degrade coverage gap, and GT-1's R_best=1.0 self-authored-split ceiling."
probe_sealed: "In hook_harness.py v1, did a missing --fixtures directory (an input the harness could not find) produce the SAME class label as a hook the harness deliberately declined to run for safety? => Yes: a missing fixture set row['class'] = 'SKIPPED-DESTRUCTIVE' with note 'no fixture ...; not executed' -- a missing input was labelled with a safety determination, and v2 split them into SKIPPED-NO-FIXTURE (no safety claim) vs SKIPPED-DESTRUCTIVE (an actual destructive-scan hit). TRUSTED"
---

## Struggle

An instrument reports a number or a class label that reads as a completed, general measurement,
when what actually happened is that the instrument could not measure at all (a missing input) or
measured only a partial slice (some rows degraded, not all) or measured against a target it
authored itself (a split written by the same reader who then scored against it). The label or
number does not say so, and a reader downstream has no way to tell "measured and clean" from
"could not be measured" or "measured against a ceiling with no headroom."

- `wiki/intake-triage/H1b-harness-v2-2026-09-02.md:15-19` [verbatim] (cropped) -- "`--fixtures`
  defaulted to the repo-relative `scripts/tests/hook_fixtures`, which does not exist for another
  trunk's copy of the script. A missing fixture set `row["class"] = "SKIPPED-DESTRUCTIVE"` with
  note `"no fixture ...; not executed"` -- a **missing input** was labelled with a **safety
  determination**." Fixed in v2 by splitting the class into `SKIPPED-NO-FIXTURE` (no safety
  claim) versus `SKIPPED-DESTRUCTIVE` (an actual destructive-scan hit), per the report's own
  §"Fixes landed."
- `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md:230` [verbatim] (cropped) -- "Harness v5
  (H-1d) adds UNDEGRADABLE-ABSOLUTE-PATH and degraded_n/executed_n so a partial degrade can no
  longer read as a trunk-wide number" -- naming, in the same sentence that fixes it, that a
  prior partial `--degrade` run (fewer scripts actually truncated and re-graded than the full
  hook population) had been reportable as if it covered the whole trunk.
- `wiki/intake-triage/GT1-skill-ground-truth-2026-09-02.md:182-183,196` [verbatim] (cropped) --
  "the split was not held out from ME. I wrote the properties and then wrote the letters. That
  is why `R_best = 1.0`... `R_best = 1.0` is an upper-bound artifact, sound only for the relative
  ablation comparison" -- a saturated score (no headroom, 1.0) is the direct, honest
  consequence of the producer and the grader being the same reader, stated as a limitation in the
  same report that produced the number, not discovered later by a peer.

## Generalization

Three distinct mechanisms produce the same reader-facing shape: a number or class label that
looks like "the thing was measured and came back clean/complete" when the truth is "the
measurement could not run" (missing fixture), "only part of the population was measured"
(partial degrade), or "the measurement's ceiling is an artifact of who built it" (self-authored
split). In every instance here the limitation was eventually stated explicitly and fixed or
flagged in the SAME report or the very next lane -- which is the difference between this pattern
and a silent defect: the discipline that catches it is stating, in the artifact itself, exactly
what was and was not measured, and refusing to let a favorable-looking label or number stand
without that scope statement attached. [[a-check-that-cannot-fail]] names the
adjacent failure (a control that cannot discriminate at all); this pattern is the softer, more
common case: a control that CAN discriminate, but whose result is being read past its actual
scope.

## Counter-evidence

none found, searched: `wiki/intake-triage/H1c-harness-v4-2026-09-02.md` and
`wiki/intake-triage/H3-py-closed-2026-09-02.md` for an instrument in the bounded set whose class
labels or headline numbers were shown, in a later run, to have understated rather than overstated
coverage (the inverse: a scope actually wider than claimed); none found -- every corrected
instance in the bounded set moved from an overstated-completeness reading toward a narrower,
more honest one, never the reverse.

## Motivates

none yet -- `scripts/audit/hook_harness.py` v2/v5 implement the fixes (`SKIPPED-NO-FIXTURE`
split; `degraded_n`/`executed_n` counters) as instrument features, but no `skills/` entry states
"a class label or headline number must carry, alongside it, what fraction of the intended
population it actually covers" as a general authoring rule for new instruments.

## Probe

Sealed question above, plus: does `scripts/audit/skills_gate_check.py`'s G6 check (GT-1) block a
future exchange-letters proposal whose R_after cites the same producer-authored split without
flagging the ceiling? Falsified if `hook_harness.py`'s v1 `SKIPPED-DESTRUCTIVE` class is found to
have already distinguished missing-fixture from destructive-scan hits before v2, or if GT-1's
split is shown to have been produced by a reader who never saw the properties before scoring.
