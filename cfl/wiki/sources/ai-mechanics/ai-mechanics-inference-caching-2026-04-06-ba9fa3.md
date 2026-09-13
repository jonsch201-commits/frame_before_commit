---
title: Inference Mechanics and Token Caching — EOS Starvation Risk and KV Cache Constraints
trunk: fl
branch: [mechanics]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-MECH; sub: branch `mechanics` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-04-06-ba9fa3-understanding-claude-checkpoints-and-token-caching.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, ai-mechanics, stylomantic, kv-cache
---

## Summary

Short session (6.2K chars, 2026-04-06) on inference mechanics and KV cache. FL-relevant because it identifies a specific design risk for Stylomantic's adjustment layer: aggressive per-token upweighting can create sequences where EOS probability collapses and the model cannot cleanly terminate. The normalization constraint mitigates this. Also constrains D5 context window decisions given RTX 2060 VRAM limits.

## Key Claims

- **Strictly sequential inference**: Standard Ollama runs strictly sequential one-token-at-a-time sampling. No tree exploration, no beam search. Each forward pass only recomputes attention for the new token against cached KV pairs. ([ai-mechanics-inference-caching-2026-04-06-ba9fa3:T2])
- **EOS starvation risk for Stylomantic**: Aggressive per-token upweighting can push a sequence toward a corner where all continuations are slightly wrong, none feel terminal, and EOS probability collapses — producing hedging, repetition, trailing off. The normalization constraint (`sum(p_i * a_i) = 1.0`) prevents this by limiting how aggressively any token class can be upweighted. ([ai-mechanics-inference-caching-2026-04-06-ba9fa3:T4])
- **EOS is just a token**: EOS competes against all other tokens at each step. Its probability reflects how "complete" the sequence feels given everything before it — same mechanism as any other token. There is no meta-awareness or coverage threshold. ([ai-mechanics-inference-caching-2026-04-06-ba9fa3:T4])
- **VRAM constraint on context**: KV cache grows with sequence length. On RTX 2060 (6GB) running Gemma 2 9B, long contexts hit memory walls — this is a concrete constraint on D5 context window decisions in Stylomantic's training data collection. ([ai-mechanics-inference-caching-2026-04-06-ba9fa3:T2])
- **"Painted into a corner" failure mode**: Model can enter a state where all continuations are slightly wrong, choosing the least-bad option at each step. No clean exit. This is the failure mode the normalization constraint guards against. ([ai-mechanics-inference-caching-2026-04-06-ba9fa3:T4])

## Entities & Concepts

[[stylomantic]]

## Conflicts

None.