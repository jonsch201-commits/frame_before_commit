---
title: Stylomantic POC — Complete Design-Build-Validate Loop (v0.1)
trunk: fl
branch: [stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-STYLO; sub: branch `stylomantic` has no registered sub-branches"
source_file: none
source_file_status: unrecoverable (Claude Code intake file deleted after wiki-master processing; stub only)
project: Claude Foundational Layer
date_ingested: 2026-05-11
type: session
tags: stylomantic, poc, decoding-layer, buhlmann-straub, credibility, logprob, validation
---

## Summary

870K session covering the complete Stylomantic POC (v0.1) — design ingestion, pipeline build, model fit, and validation. The session is the primary empirical record of the project: what was built, how it performed, and why the key findings (OOB dominance, label leakage, channel softmax cancellation, B-S credibility collapse) were produced. These negative findings are structurally informative: they identify the root causes of v0.1's failure to achieve style differentiation while confirming the pipeline architecture is implementable end-to-end.

## Key Claims

- **OOB dominance (73.5%):** The fitted model assigned 73.5% of its weight to the "other" bucket (position 21+ in the logprob ranking) — the visible top-20 window captured insufficient signal for style detection; the adjustment was effectively adjusting a representation of noise
- **Label leakage:** Training labels were derived from message-level features that leaked into the training examples; the model was classifying artifacts of label construction, not genuine style signal — this is a data pipeline design flaw, not a model architecture flaw
- **Channel softmax cancellation:** The softmax normalization applied in the adjustment layer canceled out the learned per-token adjustment at inference time — net style influence was near zero despite non-trivial fitted parameters; requires redesign of the normalization constraint
- **Bühlmann-Straub credibility collapse:** The hierarchical credibility model collapsed to the global mean for most channels because individual channel sample sizes were too small to earn their own credibility weight; B-S requires sufficient within-channel observations before departing from the global prior
- **Normalization constraint implementation gap:** The constraint `sum(p_i_baseline * a_i) = 1.0` was intended to prevent learning a redundant flat temperature scalar; implementation revealed that enforcement during training vs. post-hoc normalization produces materially different optimization behavior
- **Pipeline architecture validated:** Despite all negative validation findings, the full pipeline (Discord data → feature extraction → conditional logit fit → inference-time adjustment → evaluation) ran end-to-end; the architecture is implementable and the failure points are diagnosable
- **v4 model parameters (fitted):** beta_j = 1.530, beta_p_top200_x_oob = -0.546; these are the conditional logit coefficients from the McFadden (1974) specification applied to the top-20 logprob window
- **Position-0 design flaw confirmed:** Model was fit on position-0 logprob distributions only; applied at all positions under an implicit position-invariance assumption with no empirical basis — this is a data collection design problem, not a conceptual problem
- **Blinded forced-choice evaluation protocol:** 150-trial design with two stages: (1) "Is this AI?" Y/N gate; (2) three-class "Me / Friend A / Friend B" among non-AI messages; 70% accuracy threshold at 80% power, Cohen's d ~0.5 — this evaluation design is reusable for v0.2
- **Next steps for v0.2:** Address label leakage (redesign label construction pipeline), fix softmax cancellation (redesign normalization approach), collect position-distributed logprob data (not position-0 only), address B-S sample size requirements via channel aggregation

## Entities & Concepts

[[stylomantic]], [[frame-before-commit]]

## Conflicts

The OOB dominance finding partially conflicts with the existing [[stylomantic]] concept page's description of the top-20 window as the "hard ceiling on what's learnable" — the POC result suggests the ceiling is even lower than theoretical, because the signal within the top-20 is dominated by the other bucket. The concept page describes this as a known constraint; the POC quantifies it as 73.5% weight concentration, which is more severe than the theoretical framing implies.

## Uncaptured Content

a) Verbatim session content not preserved — this was a Claude Code intake file deleted after wiki-master processing. A stub file now exists at `raw/intake/code-2026-03-27-29e97a-stylomantic-poc-decoding-layer.md`. Key Claims are the only surviving record of the session content.
b) N/A — original not available to identify dissolved tensions.
c) N/A — unfollowed threads cannot be identified without the verbatim session.