---
title: Forward Pass Mechanics and FBC Validity
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/chat-2026-05-07-b04c8b-clarifying-thought-descriptions-and-forward-pass-mechanics.md
source_file_status: markdown-export (Claude Code session; turn numbers = message sequence)
project: Claude Foundational Layer
date_ingested: 2026-05-13
type: session
tags: fbc, forward-pass, extended-thinking, nla, architecture, stylomantic
---

## Summary

Jon questions what "thinking" means architecturally — forward pass structure, the NLA paper, extended thinking tokens, and what the "thought process" display panel actually shows. Session clarifies the three distinct levels of model introspection and draws out the FBC validity implications: the protocol increases token volume but cannot guarantee genuine divergence.

## Key Claims

- **Forward pass is fixed-depth:** Every token goes through the same N transformer layers. No dynamic halting, no gating that says "enough, stop." The logit projection always runs after layer N. Architecture is determined at training, not at inference. ([fbc-forward-pass-mechanics-2026-05-07-b04c8b:T16])
- **"Pause and reconsider" = more tokens, not deeper computation:** Adding a "reconsider" instruction generates more scratchpad tokens; each gets the same fixed N-layer pass. Instruction cannot deepen any single forward pass. ([fbc-forward-pass-mechanics-2026-05-07-b04c8b:T14])
- **Three distinct introspection levels:** ([fbc-forward-pass-mechanics-2026-05-07-b04c8b:T4])
  1. Raw activation vectors (during forward pass) — what NLA reads; never narrated by Claude
  2. Extended thinking tokens — Claude's scratchpad, generated autoregressively; this IS Claude generating text
  3. "Thought process" display panel — may be Claude's raw thinking tokens, or a summarizer output; Claude flagged uncertainty about which
- **NLA (Neural Language Architecture / Activation Verbalizer):** A separately trained LLM that translates raw activation vectors into natural language. NOT Claude narrating its own thoughts — a different model reading Claude's numbers. Released for open models only (Neuronpedia); not available for Claude via any consumer interface. ([fbc-forward-pass-mechanics-2026-05-07-b04c8b:T4])
- **NLA implication for FBC:** NLA surfaced things Claude "believed but did not say" — activation-level content not captured by thinking tokens. Extended thinking is two compressions from actual computation; display panel adds a third compression. ([fbc-forward-pass-mechanics-2026-05-07-b04c8b:T4])
- **FBC validity concern named explicitly:** Protocol can increase token volume; it cannot guarantee that volume produces genuine divergence. Theater failure mode = more tokens shaped like divergence but conditioning on the same priors. ([fbc-forward-pass-mechanics-2026-05-07-b04c8b:T14])
- **T-tags as serialization markers:** T-tags compensate for the absence of actual separation between branches. A token boundary forces serialization; whether it shifts what gets recruited next is uncertain but mechanistically plausible. ([fbc-forward-pass-mechanics-2026-05-07-b04c8b:T12])
- **Research queue item added:** Timing test — does "consider all possibilities deeper" instruction increase wall-clock time per token independent of token count? If yes, architectural variation (e.g. MoE routing) may be present. Method: controlled prompt pairs, many runs, log token count + wall-clock time per token. ([fbc-forward-pass-mechanics-2026-05-07-b04c8b:T20])

## Entities & Concepts

[[frame-before-commit]], [[stylomantic]], [[claude-thinking-mechanics]], [[fbc-verification-gap]]

## Conflicts

None. Extends and grounds the FBC validity concerns flagged in prior sources. Consistent with claude-thinking-mechanics-2026-03-23-a53ccf.