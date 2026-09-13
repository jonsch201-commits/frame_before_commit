---
title: Stylomantic Decoding Layers in AI Evolution — CFG Comparison and Framework Claims
trunk: fl
branch: [stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-STYLO; sub: branch `stylomantic` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-04-06-037ce1-stylomantic-decoding-layers-in-ai-evolution.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, stylomantic, cfg, technical-grounding, framework-claims
---

## Summary

Major session (91.8K chars, 2026-04-06). Jon and Claude traced the AI research ancestry of the Stylomantic approach (PPLM, CTRL, GeDi, CFG), established precise distinctions between CFG and Stylomantic, developed the pluggable-target framework claim, and explored extensions including autoregressive path dependence, conversational structure as a modeling surface, and the philosophical question of AI selective judgment application. Closes with session organization protocol discussion.

## Key Claims

- Closest ancestors to Stylomantic: PPLM (Dathathri et al., 2019) — train a classifier on hidden states, use gradients to nudge generation; CTRL (Keskar et al., 2019) — conditioning via prepended control tokens; GeDi (2021) — class-conditional LMs as discriminators; Classifier-Free Guidance (Ho & Salimans, 2022) — diffusion-domain inference-time arithmetic. ([stylomantic-ai-evolution-2026-04-06-037ce1:T2])
- Why logprob-layer techniques fell out of favor: scaling/fine-tuning outcompeted inference-time steering on the tasks people cared most about; RLHF absorbed the alignment use case; API opacity made activation-access approaches moot; the logprob API became an afterthought (debugging tool, not research surface). ([stylomantic-ai-evolution-2026-04-06-037ce1:T2])
- Jon's niche — "logprob-layer adjustment with no internals access, trained on personal behavioral data" — has essentially no direct current literature. The technique has ancestors; the specific formulation has no contemporaries. ([stylomantic-ai-evolution-2026-04-06-037ce1:T2])
- CFG vs. Stylomantic — four key distinctions: (1) CFG derives its direction vector analytically from two forward passes on a model trained with conditioning dropout; Jon must learn it empirically because Ollama was not trained with Jon-conditioning dropout. (2) CFG operates on iterative denoising that self-corrects; Stylomantic is a single-shot intervention with no correction mechanism. (3) CFG's direction vector is high-dimensional and uninterpretable; Stylomantic learns ~100 parameters that generalize across token positions — compression is the interpretability path. (4) CFG bakes the target into model weights; Stylomantic separates what-to-steer-toward from how-to-steer — the target is pluggable. ([stylomantic-ai-evolution-2026-04-06-037ce1:T6])
- Pluggable target is the core framework claim: the positive class is "sounds like Jon" but could equally be "sounds like a model prompted to write beautifully" or "sounds like the strongest steelman." Same pipeline, different target definition. Jon implementation is proof of mechanism; framework is the actual artifact. ([stylomantic-ai-evolution-2026-04-06-037ce1:T24])
- CFG's scale parameter has no formal bounds — works because iterative denoising self-corrects; Stylomantic's single-shot intervention on a probability surface has a silent failure mode (subtly wrong output rather than visually ugly output). ([stylomantic-ai-evolution-2026-04-06-037ce1:T72])
- Autoregressive path dependence: sampling equally from two distributions is statistically equal to sampling from their combination, but naive per-step mixing breaks down because early token selections change conditional distributions for all subsequent tokens ("sandwiches" vs. "sentences" example). Distribution mixing is not a simple linear operation at inference time. ([stylomantic-ai-evolution-2026-04-06-037ce1:T44])
- AI selective judgment application: an AI with access to a judgment-layer derived from another AI's corrected outputs could apply it selectively; because generation is autoregressive, even brief application has persistent downstream effects — cannot be fully undone mid-sentence. Flagged as relevant to oversight quality paper thread, not Stylomantic development. ([stylomantic-ai-evolution-2026-04-06-037ce1:T32])
- Networking: Anthropic mechanistic interpretability researchers (Olah, Nanda, circuits/monosemanticity authors) are 3 degrees of separation via LinkedIn. Possible path to 2 via career intermediary. ([stylomantic-ai-evolution-2026-04-06-037ce1:T30])
- Session organization proposal: NOTES.md for volatile ideas and session logs; CLAUDE.md stable context; state brief as Claude Chat handoff document. Jon's editorial control over what crosses the bridge (Claude Chat → Claude Code). ([stylomantic-ai-evolution-2026-04-06-037ce1:T48])

## Entities & Concepts

[[stylomantic]], [[frame-before-commit]]

## Conflicts

None.