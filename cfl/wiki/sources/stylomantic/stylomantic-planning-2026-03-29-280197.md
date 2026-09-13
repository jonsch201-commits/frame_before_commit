---
title: Stylomantic Decoding Layer — Planning, POC Design, Statistical Methodology
trunk: fl
branch: [stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-STYLO; sub: branch `stylomantic` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-29-280197-stylomantic-decoding-layer-planning.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: stylomantic, ai-mechanics, statistics, poc-design, how-to-use-claude
---

## Summary

Dense technical session (169K chars, 2026-03-29) covering the full planning arc from conceptual positioning through executable proof-of-concept specification. Session establishes Stylomantic's core research position (outside-in statistical interpretability vs. the field's upstream mechanistic bet), pins down the adjustment factor model specification and normalization constraint, and designs the complete v0.1 POC: Discord history → Gemma 2 9B via Ollama → 150-trial blinded forced-choice evaluation. Also includes comparative landscape of decoding and steering techniques (logit lens, contrastive decoding, CAA, SAE, FGAA) and a brief exploration of logprob-layer filters as a contract enforcement alternative to prompt-based rules.

## Key Claims

- **Outside-in statistical approach as research position**: The field's dominant bet is upstream — crack internal geometry via mechanistic interpretability, interpretability of outputs follows. Stylomantic inverts this: observe outputs statistically, build interpretability from the outside in, intervene at the boundary. This is less theoretically general but more practically accessible: API-level logit access is common; activation access almost never. Jon's actuarial epistemology (building models from observed outcomes without opening the black box) maps directly onto this inversion. ([stylomantic-planning-2026-03-29-280197:T50])
- **Adjustment factor formula and normalization constraint**: `z_i_adjusted = a_i * (z_i / T)`, then softmax. The normalization constraint `sum(p_i_baseline * a_i) = 1.0` must be enforced during training, not post-hoc, to prevent the model from collapsing to a redundant flat temperature scalar. ([stylomantic-planning-2026-03-29-280197:T178])
- **Concept signal accumulates across sequence**: Early tokens carry almost no concept information; by token ~20, logit distributions carry meaningful signal about where the response is heading conceptually. This is load-bearing for the POC design — short texts are harder to classify. ([stylomantic-planning-2026-03-29-280197:T46])
- **Logit lens and contrastive decoding**: Closest existing techniques to concept-aware temperature. But neither implements a proper Bayesian prior over concepts at the logit level, updatable as sequences accumulate — that gap is what Stylomantic is targeting. ([stylomantic-planning-2026-03-29-280197:T48])
- **FGAA cannot be applied post-logit**: FGAA operates in SAE latent space, which has different geometry from vocabulary space (50k+ dimensions, one per token). The monosemantic concept-directional structure FGAA exploits doesn't exist at the logit level. ([stylomantic-planning-2026-03-29-280197:T40])
- **POC design**: Train on Discord chat history (200MB+). Run Gemma 2 9B locally via Ollama (RTX 2060, CUDA 12.6). Log top-20 logprobs per token. Train adjustment factor model. Evaluate via 150-trial blinded forced-choice: "Is this AI?" gate first, then three-class "Me / Friend A / Friend B." 70% accuracy threshold at 80% power for Cohen's d ~0.5 effect size. ([stylomantic-planning-2026-03-29-280197:T86])
- **Three-phase automated pipeline (Phase A/B/C)**: Phase A — explore features (what logit patterns correlate with "sounds like Jon"). Phase B — iterative significance testing with pre-specified inclusion rules (Bonferroni/Benjamini-Hochberg). Phase C — lock model, evaluate holdout. Fully automatable. Prevents p-hacking while allowing exploratory insight. ([stylomantic-planning-2026-03-29-280197:T149])
- **Label strategy versioning**: Binary (Jon=1 / other=0) sufficient for v0.1. Tone-derived labels (from prior tone extraction work) = v0.2. Continuous LLM-scored labels = v0.3. Each step documented with compute implications (~18 extra hours per phase upgrade). ([stylomantic-planning-2026-03-29-280197:T159])
- **Temporal data split**: Train on older Discord messages, validate on middle period, holdout on most recent. Mandatory for time-series data — prevents future-context leakage into training. ([stylomantic-planning-2026-03-29-280197:T60])
- **Contract enforcement via logprob-layer filters**: A logprob-layer filter is structurally different from prompt-based constraints — immune to prompt injection but exploitable via the top-20 logprob truncation window (~49,980 tokens remain invisible). Explored as a complement to CLAUDE.md-based rules, not a replacement. ([stylomantic-planning-2026-03-29-280197:T173])
- **Top-20 truncation as fundamental constraint**: Only the top 20 logprobs are accessible via API. The "other" bucket represents 20-40% of probability mass in high-entropy contexts. This is a hard ceiling on what Stylomantic can observe and adjust. Not noted as a fatal flaw but as a known bound on what's learnable. ([stylomantic-planning-2026-03-29-280197:T56])
- **Outside-in as potential training-time contribution**: If logprob-concept correlation is real and stable, it enables a cleaner alternative to RLHF for concept injection: instead of human ratings, use empirically validated concept-logprob correlations as training signal. More auditable, less rater-dependent. Flagged as a named contribution beyond POC scope. ([stylomantic-planning-2026-03-29-280197:T139])

## Entities & Concepts

[[stylomantic]], [[frame-before-commit]]

## Conflicts

None — this session predates and extends earlier Stylomantic source pages with more technical depth, not contradiction.