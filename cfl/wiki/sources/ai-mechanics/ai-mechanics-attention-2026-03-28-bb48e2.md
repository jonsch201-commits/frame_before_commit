---
title: Attention Heads and Token Updates — Context Sensitivity and the Logprob Collection Problem
trunk: fl
branch: [mechanics]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-MECH; sub: branch `mechanics` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-28-bb48e2-attention-heads-and-token-updates.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, ai-mechanics, stylomantic, attention
source_kind: session
date: 2026-03-28
uuid6: bb48e2
retrieval_key: attention-heads-token-updates-context-sensitivity-bb48e2
aliases: [attention heads and token updates, context-sensitivity constraint for Stylomantic logprobs, locked-in dynamics KV cache, message length confound EOS suppression]
generated_by: frontmatter repaired 2026-09-03 by lane UC-0-dryrun (fable) under wiki/references/source-page-repair-contract-v1.md; fields added only, body untouched except per-claim fidelity tags; original ingest author field was absent; re-anchored 2026-09-03 by lane UC-0b-reanchor (fable) under contract v1 §5 after GATE REJECTED (1 claim uncaptured, 4 verified unchanged)
uncaptured_assessed: not-assessed (field added by UC-0 repair 2026-09-03; page carried no Uncaptured Content section and a repair may not add substantive sections)
raw_sha256: 94a1bb8855c05d3ccab504ca135d404624c455a9837fa7a39ccca2b4e85cf068
raw_length: 17034 chars / 268 lines / 17122 bytes
fixity_measured: 2026-09-03 UC-0-dryrun, sha256 of raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-28-bb48e2-attention-heads-and-token-updates.md under N:/claude-corpus/cfl
---

## Summary

Session (16.5K chars, 2026-03-28) on attention mechanics and context sensitivity. FL-relevant because it establishes the context-sensitivity constraint for Stylomantic's training data collection: logprobs from Ollama reflect the specific context in which a message was generated, not a token's inherent style frequency. This justifies design decisions around context window management (D5) and channel as covariate (D2).

## Key Claims

- **Attention weights are fixed; activations vary**: Attention head weights are fixed post-training. Only activations change with new tokens — the full context recomputes attention patterns at each forward pass (KV cache optimizes this). [paraphrase] ([ai-mechanics-attention-2026-03-28-bb48e2:T2])
- **Context-sensitivity constraint for Stylomantic**: A message responding to a question has materially different top-20 distributions than one initiating a topic. Stylomantic is not observing a token's inherent style frequency — it's observing its probability given a specific context. This is why controlling for context in training data collection matters. [paraphrase] ([ai-mechanics-attention-2026-03-28-bb48e2:T10])
- **"Locked in" dynamics**: Sampled tokens append to the KV cache and condition all subsequent forward passes. The model attends to its own outputs the same way it attends to user input. Early commitments constrain the distribution for all downstream tokens. [paraphrase] ([ai-mechanics-attention-2026-03-28-bb48e2:T4])
- **Surprise not represented explicitly**: When the model samples an unexpected token (e.g., "No" when it expected "Yes"), there is no explicit prediction-error signal in the residual stream. Downstream patterns emerge from what weights learned to do with that input. [paraphrase] ([ai-mechanics-attention-2026-03-28-bb48e2:T4])
- **Message length confound (mechanistic basis)**: The message length confound documented in Stylomantic's design doc has an architectural cause: EOS token probability is suppressed when long continuations are expected; style adjustments that suppress EOS alter message length modeling. [uncaptured]

## Entities & Concepts

[[stylomantic]]

## Conflicts

None.
