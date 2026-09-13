---
title: What Does Thinking Hard Mean — Extended Thinking, Parallel Models, Stylomantic Extensions
trunk: fl
branch: [mechanics, stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-MECH; secondary branch from title/slug (stylomantic) — load-bearing-for; sub: branch `mechanics` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-04-05-570573-what-does-thinking-hard-mean-to-you.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, stylomantic, ai-mechanics, research-extensions
---

## Summary

Dense session (43.3K chars, 2026-04-05). Jon probed the mechanics of "thinking hard" for LLMs, then developed several Stylomantic research extensions: parallel models for genuine cognitive diversity, SAE features as adjustment model inputs, ensemble adjustment vectors under interruption uncertainty (a particle filter framing), and a floor/ceiling framework for interruption recovery. Session ended with six memory entries documenting these ideas for future sessions.

## Key Claims

- Extended thinking mechanically = more tokens generated before final response. More tokens → more context conditioning each next token. Not "more parallel simulations" — transformers are sequential, not ensemble samplers. Whether this constitutes deliberation or just autocomplete with more runway is genuinely unclear from the inside. ([ai-mechanics-thinking-hard-2026-04-05-570573:T2])
- Non-selected tokens at each step are gone — no residual. Whatever computation happened to high-probability paths that weren't selected is lost. "The path not taken" doesn't persist in any form. This is a real architectural constraint. ([ai-mechanics-thinking-hard-2026-04-05-570573:T4])
- Human metacognition as undertrained prior: Claude is trained on transformed human thought outputs (introspective reports, essays, therapy transcripts), not process traces. Humans are famously bad introspectors, so training data captures the *reported* thought, not the *actual* process — and the gap between those is exactly what's missing. ([ai-mechanics-thinking-hard-2026-04-05-570573:T4])
- Parallel models (separate weights trained independently) produce genuinely different outputs because weights never co-adapted. Same model + different prompts = surface variation only. Jon's intuition that real cognitive diversity requires separate models is probably correct. ([ai-mechanics-thinking-hard-2026-04-05-570573:T12])
- SAE features (Towards Monosemanticity) as Stylomantic input: features are identified, auto-interpreted, and correlated with logit effects as a graded scalar (not binary). In principle, observable logit patterns could infer which features are likely active — running the direction in reverse. Requires solving an inversion problem (logprobs → feature state) that nobody has cleanly solved. Flagged as future research direction, not v0.1 material. ([ai-mechanics-thinking-hard-2026-04-05-570573:T16])
- Ensemble adjustment vectors (particle filter framing): instead of one learned "Jon vector," run 100+ parallel plausible adjustment vectors simultaneously under interruption uncertainty. Proceed without stalling; prune vectors that become inconsistent with new context when full resolution arrives. Cheap to advance, lazy pruning. ([ai-mechanics-thinking-hard-2026-04-05-570573:T28])
- Interruption recovery floor/ceiling: Floor = compact summary of pre-interruption token probability mass (top-N likely continuations + their probabilities) handed to the post-interruption context as explicit input. Model decides what to carry forward. Ceiling = full parallel continuation with adjusted weights until new context fully ingested. Ceiling fails when interruption is high-impact; floor handles this gracefully. ([ai-mechanics-thinking-hard-2026-04-05-570573:T29])
- Interruption value typology: low-impact interruptions (social acknowledgments like "uh huh") → high value to continue parallel generation. Genuinely new-information interruptions → low value, parallel threads actively mislead. Ambiguous interruptions → where ensemble earns its cost. This typology is itself a contribution — naming the cases where the problem matters makes it tractable for an engineer. ([ai-mechanics-thinking-hard-2026-04-05-570573:T34])

## Entities & Concepts

[[stylomantic]], [[frame-before-commit]]

## Conflicts

None.