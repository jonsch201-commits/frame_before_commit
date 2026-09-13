---
title: Stylomantic
trunk: fl
branch: [stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; branch from title/slug keyword (stylomantic); sub: branch `stylomantic` has no registered sub-branches"
type: concept
first_seen: stylomantic-motivations-2026-03-29-4b9fcc
source_count: 10
last_updated: 2026-05-11
---

## What This Is

A personalized decoding layer for black-box LLMs. Intervenes at the output probability distribution (logprob layer), token by token, without touching model weights or requiring internal access. The adjustment is a learned per-token reweighting of the top-N logprob distribution — functionally a non-flat, style-aware modifier on the token selection process.

Jon's project: validate on personal style ("sounds like Jon") as proof of mechanism. The framework is target-agnostic; the Jon implementation is the test case. Also called "stylometric decoding layer" in some sessions.

## What the Wiki Says

### Core Architecture

- **Intervention point:** Post-logit, pre-sampling. The model's output distribution is intercepted and reweighted before a token is selected. This is "outside-in" — no access to hidden states, activations, or weights.
- **Parameter count:** ~100 parameters generalizing across token positions. This compression is the interpretability path — inspectable objects rather than a high-dimensional uninterpretable vector.
- **Local inference only:** Designed for Ollama (local) with top-20 visible logprob window via llama-server. The top-20 constraint means ~49,980 tokens are invisible at any given step; the "other" bucket represents 20-40% of probability mass in high-entropy contexts. Known hard ceiling on what's learnable.
- **Model:** v4 fit as conditional logit (McFadden 1974) with Bühlmann-Straub credibility hierarchies. Known fitted parameters: beta_j=1.530, beta_p_top200_x_oob=-0.546.
- **Adjustment factor formula:** `z_i_adjusted = a_i * (z_i / T)`, then softmax. Normalization constraint: `sum(p_i_baseline * a_i) = 1.0` enforced during training (not post-hoc) to prevent the model from learning a redundant flat temperature scalar. ([stylomantic-planning-2026-03-29-280197])

### Research Ancestry

Closest conceptual relatives:
- **PPLM** (Dathathri et al., 2019) — classifier on hidden states, gradient-based nudging. Requires internals access; Stylomantic does not.
- **CTRL** (Keskar et al., 2019) — conditioning via control tokens at input. Changes what model thinks about before generation; Stylomantic changes output distribution after.
- **GeDi** (2021) — class-conditional LMs as discriminators to reweight generation.
- **CFG** (Classifier-Free Guidance, Ho & Salimans, 2022) — most direct conceptual ancestor; critical differences documented below.

Why these techniques fell out of favor: fine-tuning + RLHF outcompeted them for common use cases; API opacity made activation-access approaches irrelevant; the logprob API became a debugging tool, not a research surface. ([stylomantic-ai-evolution-2026-04-06-037ce1])

### CFG vs. Stylomantic — Four Distinctions

1. **Direction derivation:** CFG derives its direction vector analytically from two forward passes on a model trained with conditioning dropout. Stylomantic must learn the direction empirically from behavioral data because the underlying model was not trained with Jon-conditioning dropout.
2. **Intervention timing:** CFG operates on an iterative denoising process that self-corrects across steps. Stylomantic is a single-shot intervention — no correction mechanism. Silent failure mode rather than visually detectable failure.
3. **Interpretability:** CFG's direction vector is high-dimensional and uninterpretable. Stylomantic's ~100 parameters generalize across token positions — compression enables interpretability.
4. **Target:** CFG bakes the conditioning target into model weights. Stylomantic separates what-to-steer-toward from how-to-steer. Target is a pluggable parameter.

([stylomantic-ai-evolution-2026-04-06-037ce1])

### Pluggable Target Framework Claim

The positive class in training is "sounds like Jon" but could equally be "sounds like a model prompted to write beautifully" or "sounds like the strongest steelman of this argument." Same pipeline, different target definition. The Jon implementation is proof of mechanism; the framework — separating what we steer toward from how we steer — is the actual artifact. ([stylomantic-ai-evolution-2026-04-06-037ce1])

### Research Position: Outside-In as Field Inversion

The field's dominant bet is upstream — crack internal geometry via mechanistic interpretability, interpretability of outputs follows. Stylomantic inverts this: observe outputs statistically, build interpretability from outside in, intervene at the boundary. Less theoretically general but more practically accessible: API logit access is common; activation access almost never. Jon's actuarial epistemology (modeling from observed outcomes without opening the black box) maps directly onto this inversion. If logprob-concept correlation is real and stable, it also enables a cleaner alternative to RLHF for concept injection: use empirically validated correlations as training signal (more auditable, less rater-dependent). The [[ai-mechanics]] concept page covers the token-level inference mechanics that Stylomantic operates on. ([stylomantic-planning-2026-03-29-280197])

### POC Design (v0.1)

- **Data source:** Jon's Discord chat history (200MB+, years of conversational data)
- **Runtime:** Gemma 2 9B via Ollama on RTX 2060 (CUDA 12.6); Gemma 2 2B fits in 2-3GB VRAM as fallback
- **Evaluation:** 150-trial blinded forced-choice. Two stages: (1) "Is this AI?" Y/N gate; (2) three-class "Me / Friend A / Friend B" among non-AI messages. Success threshold: 70% accuracy at 80% power, Cohen's d ~0.5.
- **Label strategy versioning:** v0.1 = binary (Jon=1 / other=0). v0.2 = tone-derived labels (from prior tone extraction work). v0.3 = continuous LLM-scored labels. Each step documented with compute implications (~18 extra hours per phase upgrade).
- **Temporal data split:** Train on older messages, validate on middle, holdout on most recent. Mandatory for time-series — prevents future-context leakage.

([stylomantic-planning-2026-03-29-280197])

### Three-Phase Automated Pipeline (Phase A/B/C)

Phase A: explore features (what logit patterns correlate with "sounds like Jon"). Phase B: iterative significance testing with pre-specified inclusion rules (Bonferroni/Benjamini-Hochberg corrections); binary decision rules prevent p-hacking while allowing exploratory insight. Phase C: lock model, evaluate holdout. Fully automatable. PCA for exploratory feature naming ("Jon-ness dimensions"); LDA for actual classification (finds projections maximizing class separation, more appropriate than PCA for "Jon vs. other"). ([stylomantic-planning-2026-03-29-280197])

### Contract Enforcement via Logprob Filters

A logprob-layer filter is structurally different from prompt-based constraints (e.g., CLAUDE.md rules): immune to prompt injection but exploitable via the top-20 truncation window. Explored as a complement to prompt-based rules. Conceptually distinct from the personalization application — a second potential use case for the Stylomantic architecture. ([stylomantic-planning-2026-03-29-280197])

### POC v0.1 Validation Findings (from stylomantic-poc-2026-03-27-29e97a)

The 870K POC session completed the full design-build-validate loop. Four structural problems were identified:

1. **OOB dominance (73.5%):** The fitted model assigned 73.5% of its weight to the "other" bucket (position 21+ in the logprob ranking). The visible top-20 window captured insufficient signal — the adjustment was effectively adjusting noise. This is more severe than the theoretical "hard ceiling" framing implied: the ceiling is functionally lower because OOB dominates within the observable window.

2. **Label leakage:** Training labels were derived from message-level features that leaked into the training examples. The model classified artifacts of label construction, not genuine style signal. This is a data pipeline design flaw, not a model architecture flaw.

3. **Channel softmax cancellation:** Softmax normalization in the adjustment layer canceled out the learned per-token adjustment at inference time. Net style influence near zero despite non-trivial fitted parameters. Requires redesign of the normalization approach.

4. **Bühlmann-Straub credibility collapse:** The hierarchical credibility model collapsed to the global mean for most channels due to insufficient within-channel sample sizes. B-S requires sufficient observations before departing from the global prior; channel granularity was too fine for the available data.

Fitted v4 parameters: beta_j = 1.530, beta_p_top200_x_oob = -0.546 (conditional logit, McFadden 1974). These are real fitted values, but the model's style differentiation was near zero due to the above structural problems.

The pipeline architecture was validated end-to-end despite all negative findings — the failure points are diagnosable and addressable in v0.2. ([stylomantic-poc-2026-03-27-29e97a])

### Known Implementation Gap (v0.1)

Position-0 problem: the model was fit on position-0 logprob distributions only (first token of each message given context). The adjustment was then applied at all positions under an implicit position-invariance assumption for which there is no empirical basis. Distributions at positions 1, 2, 3... were never observed during training. This is a data collection design problem, not a conceptual problem — a correctly specified version would collect logprob distributions at every position across full message generations. ([stylomantic-limitations-2026-04-08-dce1af])

### Model Hierarchies

Three structural hierarchies can interact in the model design:
- Credibility hierarchy (Bühlmann-Straub): channel-level vs. global parameter pooling
- Token position hierarchy: position within a message
- Logprob rank hierarchy: rank 1–20 within top-N window + Other bucket

Six interaction options exist (documented in e1c10c), ordered from most to least defensible. Documentation ambiguity on which option was intended was the root cause of Claude Code implementation collisions. ([stylomantic-doc-gaps-2026-04-10-e1c10c])

### Jon's Motivations

Three framings assessed in 4b9fcc session:
- **Applying actuarial skills at new scale** — described as "most defensible, genuinely real." Pre-registration, BH correction, temporal splits, confound identification, power analysis before collection.
- **Learning to use AI** — where "some of the obsession lives." Project as runway for Claude Code, Ollama, logprob APIs, evaluation design.
- **Improving AI for everyone** — where Claude pushed back hardest. Requires v0.1 results; publication arc depends on empirical findings.

### Publication Plans

LessWrong as planned venue (first), Alignment Forum (organic promotion). Planned post framing: honest about implementation gap rather than overpromising. ([stylomantic-limitations-2026-04-08-dce1af])

### Networking

Anthropic mechanistic interpretability researchers (Olah, Nanda, circuits/monosemanticity authors) are 3 degrees of separation from Jon via LinkedIn, with potential path to 2 via career intermediary. ([stylomantic-ai-evolution-2026-04-06-037ce1])

## Conflicts

None.

## Related

[[frame-before-commit]], [PERSONAL: jon]
