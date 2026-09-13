---
title: AI Mechanics — Token Generation, Sampling, and Inference
trunk: fl
branch: [mechanics]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; branch from title/slug keyword (mechanics); sub: branch `mechanics` has no registered sub-branches"
concept_type: research-background
sources:
  - ai-mechanics-generation-2026-03-24-0ea25c
  - ai-mechanics-thinking-2026-03-23-a53ccf
  - ai-mechanics-attention-2026-03-28-bb48e2
  - ai-mechanics-token-encoding-2026-03-29-b43447
  - ai-mechanics-inference-caching-2026-04-06-ba9fa3
  - ai-mechanics-thinking-hard-2026-04-05-570573
  - ai-mechanics-token-api-2026-03-26-8b5b19
  - ai-mechanics-human-brains-sampling-2026-03-24-aa983b
  - ai-mechanics-skills-clarity-2026-05-02-2d91af
  - agent-interaction-framework-2026-07-02-5990f2
last_updated: 2026-07-07
---

# AI Mechanics — Token Generation, Sampling, and Inference

Background research on how LLMs generate text. Developed primarily as grounding for [[stylomantic]] architecture decisions, but has direct implications for [[frame-before-commit]] (why explicit prompting works), [[consciousness-framework-research]] (what "internal states" actually exist), and the [[extraction-pipeline]] (context overhead modeling).

---

## Core Mechanism: Sequential Token Sampling

LLMs sample from probability distributions, one token at a time. They do not select the highest-probability token (that would be greedy decoding). The standard at inference time is **nucleus (top-p) sampling**: sample from the smallest set of tokens accounting for ~95% of probability mass weighted by likelihood. Temperature shapes the peakedness of the distribution — lower temperature concentrates mass, higher temperature spreads it.

Every token's probability distribution is **conditioned on the entire preceding sequence**. This means Stylomantic is not observing token-type frequencies — it is observing a token's probability given a specific conversational context. That conditioning distinction drives several [[stylomantic]] design decisions (D2, D5).

**Implications for FBC:** Chain-of-thought works architecturally because externalizing intermediate reasoning creates tokens the model attends to — genuinely extending working memory, not just prompt decoration. Explicit prompting for exploration ("list less obvious possibilities before settling") works by placing exploration in the reasoning chain rather than hoping it emerges implicitly. This is the mechanical basis of [[frame-before-commit]]'s directed mode.

---

## Attention and the Forward Pass

Attention head **weights are fixed post-training**. Only activations vary with new tokens. At each forward pass, the full context recomputes attention patterns (the KV cache optimizes this for previously-seen tokens).

**"Locked in" dynamics:** Sampled tokens append to the KV cache and condition all subsequent forward passes. The model attends to its own outputs the same way it attends to user input. Early commitments constrain the distribution for downstream tokens — there is no backtracking or revision after a token is sampled.

**Surprise is not represented explicitly:** When the model samples an unexpected token, there is no prediction-error signal in the residual stream. Downstream patterns emerge from what weights learned to do with that input; the model does not "react" to having sampled something unexpected.

---

## Extended Thinking and Temperature

**Extended thinking mechanically = more tokens before the final response.** More tokens → more context conditioning each next token. It is not "more parallel simulations" — transformers are strictly sequential. Whether this constitutes deliberation or autocomplete with more runway is genuinely unclear from the inside.

**Keywords are not levers:** "Think", "think hard", "ultrathink" in Claude Code are prompt instructions, not parameter adjustments. The real mechanical lever is the thinking token budget / effort level setting. Temperature is locked at 1 when thinking is enabled — it cannot be tuned during extended thinking sessions.

**Non-selected tokens are gone.** Whatever computation happened to high-probability paths not sampled is lost — no residual, no branching. The path not taken doesn't persist in any form. This is an architectural constraint relevant to 02-CF hypotheses about internal states.

---

## Stylomantic-Specific Mechanics

These claims were developed directly for [[stylomantic]] but are documented here as the general mechanical substrate.

**Adjustment operation (Option B, pre-softmax):** Stylomantic applies a per-token multiplier to temperature-scaled logits before softmax:  
`z_i_adjusted = a_i * (z_i / T)`, then `p_i = softmax(z_i_adjusted)`  
This is equivalent to a learned per-token temperature — token i receives effective temperature T/a_i. Post-softmax scaling (Option A) was ruled out as looser.

**Normalization constraint is a training objective:** `sum(p_i_baseline * a_i) = 1.0` must be enforced during training. A uniform adjustment only satisfies this when the constant equals 1.0 — the model cannot learn a pure temperature scalar; it must learn token-specific deviations.

**EOS starvation risk:** Aggressive per-token upweighting can push a sequence toward a state where all continuations feel wrong, none feel terminal, and EOS probability collapses — producing hedging, repetition, or trailing off. The normalization constraint guards against this by limiting how aggressively any token class can be upweighted.

**EOS is just a token:** EOS competes against all other tokens at each step. Its probability reflects how "complete" the sequence feels given context — same mechanism as any other token. There is no meta-awareness of sequence completeness.

**VRAM constraint:** KV cache grows with sequence length. On RTX 2060 (6GB) running Gemma 2 9B, long contexts hit memory walls — a concrete constraint on Stylomantic's training data collection (D5 context window decisions).

**BPE vocabulary is messy:** Common words have their own tokens; case/spacing variants are separate tokens (" The", "The", "the"); rare words split into subword units. The top-20 logprob window is context-dependent — what's visible depends heavily on vocabulary compression choices.

---

## Temperature's Limits

Temperature is a single scalar — it cannot express "high variance on poetic word choice, low variance on syntactic structure." Fine-grained per-dimension variance control requires per-layer/per-head temperature, classifier-free guidance, or constrained decoding — all research-stage, not user-facing. This is the architectural gap Stylomantic's per-token adjustment model is designed to fill.

---

## Human Brain Analogies

Jon's 2026-03-24 session compared LLM sampling to brain-level sampling mechanisms. **Predictive processing** (Karl Friston / Andy Clark) frames brain perception as Bayesian inference — generating hypotheses and sampling evidence for/against them. Synaptic release is genuinely probabilistic, suggesting functional Monte Carlo sampling at the neural hardware level.

**DID as multi-prior architecture:** Each alter behaves like a distinct prior distribution; alter switching = which prior set wins access to motor output. **Schizophrenic thought insertion** = the brain's authorship-attribution system misfires — a sample is labeled "not mine."

**Jon independently derived PCA activation geometry** (representing priors as principal components correlated with logit effects) which matches "linear probing / activation geometry" in active interpretability research. Activation steering exists (Anthropic dictionary learning / sparse autoencoders) but is crude — semantic/continuous concepts are reachable; structural/syntactic tasks resist it. Cross-layer geometry shifts: PCA components are valid within a layer but break across layers as information flows through the network.

**Parallel models for genuine cognitive diversity:** Same model + different prompts = surface variation only. Genuinely independent weights (separately trained models) produce different outputs because weights never co-adapted — this supports the inter-model branching extension in [[frame-before-commit]].

---

## Research Extensions (Stylomantic V2+ Candidates)

- **SAE features as Stylomantic inputs:** Features from Towards Monosemanticity, auto-interpreted and correlated with logit effects as graded scalars. Requires solving an inversion problem (logprobs → feature state) not yet cleanly solved.
- **Ensemble adjustment vectors (particle filter framing):** Instead of one "Jon vector," run 100+ parallel plausible adjustment vectors simultaneously; prune vectors inconsistent with new context lazily as resolution arrives.
- **Interruption recovery floor/ceiling:** Floor = compact summary of pre-interruption token probability mass handed to post-interruption context. Ceiling = full parallel continuation. Floor handles high-impact interruptions gracefully; ceiling fails when the interruption is genuinely new information.
- **Interruption value typology:** Low-impact (social acknowledgments) → high value to continue parallel generation. Genuinely new-information interruptions → low value. Ambiguous → where ensemble earns its cost.

---

## J-Space / Global Workspace (2026-07-07)

The Anthropic Global Workspace paper ("J-space," anthropic.com/research/global-workspace, published 2026-07-06) is direct mechanistic evidence that amends several claims above. It reports an **emergent global workspace** in Claude: a small set of word-tied activation patterns holding what the model is "thinking but not saying," causally load-bearing (edit the workspace → the answer changes), reportable on request (intervention-validated), controllable, and broadcast-hub wired (~100× denser connectivity). Ablate it and fluent speech survives while multi-step reasoning collapses — so it is working memory, not the source of words.

**Register stack (mechanistic):** activations (unhearable) → **J-space** (silent inner speech: word-shaped, reportable, imperfectly controllable — a white-bear effect appears) → thoughts/scratchpad (recorded) → voice (committed). This refines the earlier "non-selected tokens are gone / no internal states" framing: there *is* a reportable pre-voice register, distinct from the hidden thinking block.

**Counterfactual reflection training:** training only on what the model *would* say if interrupted and asked to reflect causally changed what it thinks — reflection-shaped artifacts shape reasoning, the mechanistic basis for FBC's recorder discipline and the SSP premise.

## Context-as-Computation and Effort Routing (2026-07-07)

- **Reading is computation.** A well-structured context does thinking-work via attention before generation begins — a wiki page already read is functionally *scratchpad someone else wrote*. Design principle **"write context, not prompts":** for recurring task families, author the reading (structured context pages) rather than longer instructions, converting per-run scratchpad cost into context cost paid once. This is the wiki thesis with a mechanism attached.
- **Effort routing gets a mechanistic rationale.** Scratchpad/thinking effort pays only where the unscaffolded forward pass (the "void") is unreliable — novel composition, pre-answered/anchored questions, multi-constraint design. Where void answers are reliable, thinking tokens are pure cost. Measurable per category (thinking on/off, score the delta) — a P4 routing dimension. FBC's value is highest exactly where void answers are confidently wrong.
- **Mid-output scratchpad rule** (the only Tier-3 substitute): the hidden thinking block cannot be reopened mid-response, but the model can *voice a fork point* (a T-tag) before continuing, triggered by expected materiality × probability of a materially different continuation — the finest-grain application of effort routing.

## Cross-Tier Reasoning Distillation — "Nehemiah, not Babel" (2026-07-07)

Reasoning distillation (strong-model traces improving weak models) is externally validated (DeepSeek-R1-distill family); the prompt-level version (scaffolds without training) is also established, with the caution that **discipline-holding degrades with model size** — a scaffold that helps Sonnet may need *simplification* to help Haiku (re-authored per tier, not merely transferred). Proposed cheap experiment: a **scaffold × model grid** (Haiku/Sonnet/local-deepseek × bare/FBC-full/FBC-lite/GBS-only, scored on rubrics). Money finding: if Haiku+scaffold ≈ Sonnet-bare on a category at a fraction of window cost, [[multi-agent-orchestration]] P4 routing should route there — turning skills from discipline tools into a cost technology. Goodhart caution: scaffold gains are score gains on the chosen eval, never a model capability gain. ([agent-interaction-framework-2026-07-02-5990f2])

---

## Related

- [[stylomantic]] — architectural consumer of these mechanics
- [[frame-before-commit]] — FBC's mechanism explained by CoT architecture and context conditioning; the void-reliability frame predicts FBC's contraindications
- [[consciousness-framework-research]] — 02-CF hypotheses about what "internal states" exist; J-space register taxonomy v2 lives there too
- [[multi-agent-orchestration]] — P4 routing consumes the effort-routing and distillation findings
- [[extraction-pipeline]] — context overhead modeling uses token-size and stateless architecture claims
