---
title: How AI Response Generation Works — Sampling, Temperature, Context Conditioning
trunk: fl
branch: [mechanics]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-MECH; sub: branch `mechanics` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-24-0ea25c-how-ai-response-generation-works.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, ai-mechanics, stylomantic, token-sampling
source_kind: session
date: 2026-03-24
uuid6: 0ea25c
retrieval_key: how-ai-response-generation-works-sampling-temperature-0ea25c
aliases: [how AI response generation works, sampling not maximizing, temperature as GLM intercept, nucleus top-p sampling standard, chain-of-thought is architectural]
generated_by: frontmatter repaired 2026-09-03 by lane UC-0-dryrun (fable) under wiki/references/source-page-repair-contract-v1.md; fields added only, body untouched except per-claim fidelity tags; original ingest author field was absent; re-anchored 2026-09-03 by lane UC-0b-reanchor (fable) under contract v1 §5 after GATE REJECTED (2 claims uncaptured, 1 moved T12->T16, 3 verified unchanged)
uncaptured_assessed: not-assessed (field added by UC-0 repair 2026-09-03; page carried no Uncaptured Content section and a repair may not add substantive sections)
raw_sha256: 2d4a0e3d1eee94a485856da928da9abb9e3e2672874fa0ef9a6b5ac68084aac1
raw_length: 39592 chars / 520 lines / 39805 bytes
fixity_measured: 2026-09-03 UC-0-dryrun, sha256 of raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-24-0ea25c-how-ai-response-generation-works.md under N:/claude-corpus/cfl
---

## Summary

Foundation session (39K chars, 2026-03-24) covering token sampling mechanics, temperature/top-p parameters, and context conditioning. FL-relevant because it establishes the mechanism by which Stylomantic's adjustment layer operates: temperature sets a global distribution intercept, per-token adjustments refine individual tokens relative to that baseline — analogous to a GLM intercept + covariate structure.

## Key Claims

- **Sampling, not maximizing**: LLMs sample from probability distributions at each step; they do not select the highest-probability token (that would be greedy decoding). Temperature and top-p shape the distribution's peakedness/spread. [paraphrase] ([ai-mechanics-generation-2026-03-24-0ea25c:T2])
- **Context conditioning**: Each token's probability distribution is conditioned on the entire preceding sequence, not just recent tokens. Stylomantic is intercepting conditioned distributions, not token-independent frequencies. [paraphrase] ([ai-mechanics-generation-2026-03-24-0ea25c:T2])
- **Chain-of-thought is architectural**: CoT works because externalizing intermediate reasoning creates tokens the model attends to — genuinely extending working memory. Not just a prompting trick. [uncaptured]
- **Thought tokens are not transparent**: CoT outputs are maximum-likelihood representations of what reasoning *looks like*, not windows into actual internal computation. The map is not the territory. [paraphrase] ([ai-mechanics-generation-2026-03-24-0ea25c:T14])
- **Temperature intercept framing**: Temperature sets a global "confidence intercept" on the output distribution. Stylomantic's per-token adjustments then refine tokens relative to that baseline — the two operate in a clear structural relationship. [uncaptured]
- **Nucleus sampling as standard**: Top-p (nucleus) sampling is the actual inference standard — sample from tokens accounting for ~95% of probability mass weighted by likelihood. Not top-k, not greedy. [paraphrase] ([ai-mechanics-generation-2026-03-24-0ea25c:T16])

## Entities & Concepts

[[stylomantic]]

## Conflicts

None.
