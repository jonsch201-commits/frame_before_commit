---
format: cfl-page/v1
kind: pattern
slug: caution-errors-have-no-instrument
title: "Caution Errors Have No Instrument"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "blind duplicate accusation false final state two complementary implementations professional had not read the code called it a defect checking the artifact is not checking the claim"
aliases: [over-blaming-passes-every-check, accusation-later-self-corrected, checking-existence-not-intent]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "two CFL-clone instances (Professional's mis-read of a deliberate design as a defect; Soul's own self-corrected duplicate-build accusation) — both self-corrected by the accusing party, not caught by any running mechanism. The CFL memory index documents this as a named 9-instance class (feedback_caution-errors-have-no-instrument.md); that file's own primaries are outside this clone's bounded read-set."
probe_sealed: "Professional called CFL's provenance-tier design (deliberate head-only chunking, documented in build_index.py's docstring, SEC-113) a defect. What had Professional actually checked before making that claim? => Only that the files existed — 'I checked whether the FILES EXISTED... THE CLAIM WAS NOT ABOUT FILES. IT WAS ABOUT INTENT... Checking the artifact is not checking the claim.' TRUSTED"
---

## Struggle

An accusation of a defect, a duplicate, or a failure reads as diligence — nobody's instinct is to
challenge a claim that sounds careful — so it passes every review a program has, even when the
claim itself is wrong, and the correction (when it comes) comes only from the accusing party
re-checking their own work, never from a standing detector built to catch over-blaming the way
detectors exist to catch overclaiming.

- `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md:28` [verbatim] (cropped) —
  instance 6: "CFL's `provenance` tier design... existed / Professional had not read the code and
  called it a defect... 'It is a documented design and the design is deliberate... I checked
  whether the FILES EXISTED... THE CLAIM WAS NOT ABOUT FILES. IT WAS ABOUT INTENT... Checking the
  artifact is not checking the claim.' CAUGHT BY: person (Professional re-opened the function
  itself, prompted by no automated check)."
- `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md:44` [verbatim] (cropped) —
  instance 14: "Soul's own two self-corrections in the same letter... found CFL's tool had in fact
  consumed Personal's earlier findings... via a docstring citation -- so the *duplicate build* is
  real (V1) but the *blind duplicate* accusation was false; final state: two complementary
  implementations, neither superseding, to be merged. CAUGHT BY: person..., self-corrected by
  person (Soul re-reading the file three times in the same letter) -- not by any instrument."

## Generalization

Every adversarial mechanism in this program (the skills gate's re-run discipline, the peer-review
rule, negative controls) is aimed at catching a claim that OVERSTATES success or understates a
problem — none is aimed at a claim that OVERSTATES a failure or a duplication that turns out not to
be one, because a strict-sounding accusation looks exactly like the vigilance those mechanisms exist
to reward. Both instances here were only caught because the accusing party independently re-opened
their own claim (reading the actual code's intent; re-reading a letter three times) — an act of
self-scrutiny that no gate required or verified happened.

## Counter-evidence

none found, searched: `wiki/skills-gate/LEDGER.md` for a REJECTED proposal where the rejection
itself was later found to be an over-caution error rather than a correct finding; all three
rejections of PROP-004 (v1, v2, v3) were confirmed by first-hand runs the gate performed itself
(see [[proposal-and-script-describe-different-programs]]), which is a different — and in this
program's own terms, correctly-instrumented — class from the two instances above, where the
accusation preceded any first-hand check.

## Motivates

none yet — no `skills/` page or gate in the bounded read-set requires the accusing party (or a
peer) to check accusation-of-defect/duplication claims with the same rigor the gate applies to
success claims; both corrections found here were voluntary, not procedural.

## Probe

Sealed question above. Falsified if `build_index.py`'s docstring is found NOT to document the
provenance-tier chunking as deliberate (i.e., Professional's original defect claim was actually
correct), or if the Soul/CFL PII-scrubber "final state" is later revised away from "two
complementary implementations, neither superseding" back toward one accusation standing.
