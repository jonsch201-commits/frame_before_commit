---
title: Human Brain Sampling Mechanisms — Predictive Processing, Stochastic Neurons, and Temperature Architecture
trunk: fl
branch: [mechanics]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-MECH; sub: branch `mechanics` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-24-aa983b-how-human-brains-sample-observations.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-20
type: session
tags: how-to-use-claude, ai-mechanics, cognitive-science, predictive-processing, stylomantic, temperature, activation-steering
source_kind: session
date: 2026-03-24
uuid6: aa983b
retrieval_key: human-brain-sampling-predictive-processing-temperature-aa983b
aliases: [how human brains sample observations, predictive processing Friston Clark, DID as multi-prior architecture, temperature is one scalar, PCA activation geometry linear probing, activation steering Golden Gate Claude]
generated_by: frontmatter repaired 2026-09-03 by lane UC-0-dryrun (fable) under wiki/references/source-page-repair-contract-v1.md; fields added only, body untouched except per-claim fidelity tags; original ingest author field was absent
uncaptured_assessed: not-assessed (field added by UC-0 repair 2026-09-03; page carried no Uncaptured Content section and a repair may not add substantive sections)
raw_sha256: 9262bbf248482040a2d52284bfe56924f6f0105b9937e12229c36661de268eb3
raw_length: 17269 chars / 264 lines / 17379 bytes
fixity_measured: 2026-09-03 UC-0-dryrun, sha256 of raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-24-aa983b-how-human-brains-sample-observations.md under N:/claude-corpus/cfl
---

## Summary

Session (17K chars, 2026-03-24) on whether human brains do something analogous to AI sampling at the hardware level. Covers predictive processing (Karl Friston/Andy Clark), stochastic synaptic release as functional sampling, dissociative identity disorder as a multi-prior architecture, and why temperature is too coarse a control for fine-grained variance adjustment. Jon independently derived the activation-space PCA approach (linear probing / activation geometry) that matches current interpretability research. Relevant to Stylomantic (per-layer variance, architecture of priors) and 02-CF (consciousness as integration quality).

## Key Claims

- **Predictive processing as brain-level sampling**: The brain generates hypotheses and samples evidence for/against them (Karl Friston, Andy Clark). Perception is Bayesian inference, not camera-recording. Neural synaptic release is genuinely probabilistic — may implement functional Monte Carlo sampling. [paraphrase] ([ai-mechanics-human-brains-sampling-2026-03-24-aa983b:T2])
- **DID as multi-prior architecture**: Each alter behaves like a distinct prior distribution — different beliefs, emotional weightings, sensorimotor habits. Alter switching = which prior set is upstream of the decision layer. The host identity is whichever prior currently wins access to motor output/working memory. [paraphrase] ([ai-mechanics-human-brains-sampling-2026-03-24-aa983b:T4])
- **Schizophrenic thought insertion as authorship-tagging failure**: The brain's attribution system misfires — a sample gets generated but labeled "not mine." Parallel: the meta-layer tracking provenance fails, not the sampling itself. [paraphrase] ([ai-mechanics-human-brains-sampling-2026-03-24-aa983b:T6])
- **Temperature is one scalar — it cannot do both**: Temperature uniformly stretches/compresses the entire output distribution. Cannot say "high variance on poetic word choice, low variance on syntactic structure" with temperature alone. Jon's intuition about fine-grained per-dimension variance control requires per-layer/per-head temperature, classifier-free guidance, or constrained decoding — all research-stage, not user-facing. [paraphrase] ([ai-mechanics-human-brains-sampling-2026-03-24-aa983b:T6])
- **Jon independently derived PCA activation geometry**: Representing priors as principal components and correlating them matches "linear probing / activation geometry" in active interpretability research. Harmful/harmless prompts are separated by roughly linear boundaries; PCA is well-suited. Personality trait PCA on activation vectors is documented. [paraphrase] ([ai-mechanics-human-brains-sampling-2026-03-24-aa983b:T12])
- **Activation steering exists and is crude**: Anthropic's dictionary learning / sparse autoencoders can identify features (Golden Gate Claude demo). Semantic/continuous concepts (formal/casual, poetic register) are reachable; structural/syntactic tasks resist it. The map between human-language concepts and model-internal features is incomplete. [paraphrase] ([ai-mechanics-human-brains-sampling-2026-03-24-aa983b:T10])
- **Cross-layer geometry shift**: PCA applied independently to each layer finds different dominant axes. Component alignment is valid within a layer but breaks across layers as information flows through the network. [paraphrase] ([ai-mechanics-human-brains-sampling-2026-03-24-aa983b:T12])

## Entities & Concepts

[[stylomantic]], [[consciousness-framework-research]]

## Conflicts

None.