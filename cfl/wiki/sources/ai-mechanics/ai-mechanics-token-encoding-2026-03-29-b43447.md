---
title: Token Representation and Encoding — Adjustment Operation Specification and EOS Confound
trunk: fl
branch: [mechanics]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-MECH; sub: branch `mechanics` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-29-b43447-understanding-token-representation-and-encoding.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, ai-mechanics, stylomantic, tokenization
---

## Summary

Session (16.4K chars, 2026-03-29) covering BPE tokenization mechanics and, critically, specifying the exact mathematical operation Stylomantic must use. Session established that the design doc (D6) had the wrong operation specified — Option A (post-softmax) should be Option B (pre-softmax multiplier on temperature-scaled logits). Also identified EOS token as a confound for message length modeling.

## Key Claims

- **Adjustment operation is Option B (pre-softmax)**: Stylomantic applies a per-token multiplier to temperature-scaled logits *before* softmax: `z_i_adjusted = a_i * (z_i / T)`, then `p_i = softmax(z_i_adjusted)`. This is equivalent to a learned per-token temperature — token i receives effective temperature T/a_i. This is cleaner and stricter than post-softmax logprob scaling (Option A). Design doc D6 updated to reflect this in-session. ([ai-mechanics-token-encoding-2026-03-29-b43447:T10])
- **Normalization constraint is a training objective**: `sum(p_i_baseline * a_i) = 1.0` must be enforced during training, not post-hoc. A uniform adjustment a_i = constant only satisfies the constraint when c = 1.0, so the model *cannot* learn a pure temperature adjustment — it must learn token-specific deviations. ([ai-mechanics-token-encoding-2026-03-29-b43447:T10])
- **EOS token as confound**: Special tokens (EOS, BOS, role markers) are in the vocabulary and have logprobs. Style adjustments can leak into message length modeling by suppressing or boosting EOS probability relative to other tokens. ([ai-mechanics-token-encoding-2026-03-29-b43447:T16])
- **BPE vocabulary is messy**: Common words have their own tokens; case/spacing variants are separate tokens (" The", "The", "the"); rare words split into subword units. The top-20 logprob window reflects this messiness — what's visible depends heavily on context and vocabulary compression choices. ([ai-mechanics-token-encoding-2026-03-29-b43447:T2])

## Entities & Concepts

[[stylomantic]]

## Conflicts

None.