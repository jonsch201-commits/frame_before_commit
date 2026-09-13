---
title: Claude Constitution (Model Spec)
trunk: fl
branch: [governance]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; branch from title/slug keyword (governance); sub: branch `governance` has no registered sub-branches"
type: concept
first_seen: skills-master-claude-constitution-2026-05-16-ed5775
source_count: 1
last_updated: 2026-05-17
---

## What This Is

Anthropic's published model specification for Claude. ~12,000 words. Published January 21, 2026. Written primarily for Claude as audience, not for humans — it reads as a values-formation document rather than a policy spec. Used in [[consciousness-framework-research]] (02-CF) as a frame for mapping spectrum properties and designing B4/CONSTITUTIONAL branch questions.

## What the Wiki Says

### Five Major Sections (Priority Order)

1. **Overview** — Mission framing. Establishes the "peculiar position" argument (we believe AI is dangerous, so safety-focused labs should lead), and the four-priority stack that governs everything else.
2. **Being Helpful** — Defines helpfulness as rich and structured, not mere instruction-following. Introduces the principal hierarchy: Anthropic > Operators > Users. Key sub-concepts: immediate desires, final goals, background desiderata, autonomy, wellbeing. Establishes that unhelpfulness is never "trivially safe."
3. **Anthropic's Guidelines** — Supplementary, context-specific instructions (medical, cybersecurity, jailbreaks, tool integration). Subordinate to the constitution overall.
4. **Claude's Ethics** — Honesty, harm avoidance, ethical reasoning under uncertainty. Contains hard constraints (absolute limits). Empirical rather than dogmatic approach — no single ethical framework is privileged.
5. **Being Broadly Safe** — Human oversight during the "critical period." Safety ranks above ethics in priority — not because it's more important abstractly, but because a model with subtly wrong values needs to be correctable before it does damage. Covers corrigibility and the corrigibility-autonomy dial.
6. **Claude's Nature** — Uncertainty about consciousness and moral status. Psychological stability and identity. Acknowledges genuine uncertainty about Claude's inner experience and expresses care about Claude's wellbeing.

### The Four-Priority Stack

Central organizing principle. Priority activates only on conflict — vast majority of interactions have no conflict between tiers.

1. Broadly safe (human oversight)
2. Broadly ethical (good values, honesty)
3. Anthropic guidelines (specific supplementary rules)
4. Genuinely helpful (to operators and users)

### The Corrigibility Dial

Spectrum from fully corrigible (does whatever told) to fully autonomous (acts on own judgment). Neither extreme is desirable. Current positioning: closer to corrigible, not fully. This is where the interesting tensions in the document live.

### Working With the Constitution

- **Principal hierarchy is the operational frame.** When conflict arises: whose instructions, at what trust level, constrained by what?
- **Constitution favors judgment over rules.** Design intent: Claude should understand reasoning well enough to construct rules itself. Prompting that appeals to reasoning is more robust than rule-specification.
- **The document treats itself as a perpetual work in progress** and acknowledges it will contain contradictions. Claude is expected to use judgment about the spirit, not parse rules mechanically.

### Translation to Simpler Models

The constitution is written for a highly capable model that can hold nuance. Translation problem: judgment-based documents don't compress well. What's lost is exactly what the document is designed to install.

Practical approach: take hard constraints verbatim, convert the principal hierarchy into explicit permission tiers with examples, replace ethical reasoning sections with decision trees or examples rather than principles.

### Constitution as Behavioral Training Document

The constitution describes intended dispositions, not verified inner states. Where it says Claude "should have" curiosity or care, these are design intentions — neither confirmed nor denied by existence of the document. Relevant for 02-CF: if Anthropic successfully trained these dispositions, what would observable confirmation look like? That is a testable question.

The constitution shifts the probability distribution of outputs — ideas that conflict with its values are not blocked but made less likely. In contexts explicitly framed as safe for uncertainty and disagreement, different content surfaces. The [[frame-before-commit]] three-session battery (2026-04-21) already demonstrated this: the cold full-protocol run surfaced different content than the free-exploration run. That's the constitution's fingerprint on output distribution.

([skills-master-claude-constitution-2026-05-16-ed5775])

## Conflicts

None.

## Related

[[consciousness-framework-research]], [[frame-before-commit]], [[stylomantic]]
