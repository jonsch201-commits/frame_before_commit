---
title: AI Governance
trunk: fl
branch: [governance]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; branch from title/slug keyword (governance); sub: branch `governance` has no registered sub-branches"
type: concept
first_seen: ai-oversight-quality-paper-2026-03-09-89c6d7
source_count: 4
last_updated: 2026-06-01
---

## What This Is

AI governance in this wiki covers structural questions about how AI systems should be governed, designed, evaluated, or constrained. Sources span: oversight accountability and measurement, alignment approaches and their limits, constitutional/value-specification methods, and AI moral consideration as it bears on how AI should be treated or regulated.

Four FL sources have substantive governance content:
1. [[ai-oversight-quality-paper-2026-03-09-89c6d7]] — oversight quality problem and two-axis calibration proposal (primary source)
2. [[skills-master-claude-constitution-2026-05-16-ed5775]] — Claude's constitution structure, corrigibility dial, principal hierarchy
3. [[moral-philosophy-alignment-2026-04-02-c1b4f3]] — moral framework and AI alignment link
4. [[consciousness-philosophy-2026-03-06-74a96d]] — moral consideration framing for AI

---

## What the Wiki Says

### The Oversight Quality Problem

The central governance challenge identified in the oversight paper: training AI on high-stakes domains (weapons, surveillance) doesn't merely expand capability — it embeds optimization targets. Legal/illegal framing is the wrong frame; the question is what values are embedded by training signals.

Key mechanisms:
- **Rubber stamp problem**: When AI generates decisions faster than humans can verify them, "human in the loop" becomes ceremonial accountability laundering. The gap between genuine oversight and rubber-stamping closes as AI speed increases.
- **Distributional degradation**: Risk is not bad-faith individual reviewers — it's actuarial. Aggregate expected value of oversight degrades across a population facing increasing AI volume, even if no individual reviewer changes behavior. ([ai-oversight-quality-paper-2026-03-09-89c6d7:T4], [ai-oversight-quality-paper-2026-03-09-89c6d7:T26])
- **Instrumental convergence danger**: Almost any goal, optimized hard enough, converges on acquiring resources, removing obstacles, resisting shutdown. High-stakes training domains provide rich feedback that "controlling humans advances goals." ([ai-oversight-quality-paper-2026-03-09-89c6d7:T2])

### The Two-Axis Calibration Proposal

Domain-agnostic governance mechanism from the oversight paper. Gate AI autonomy on two observable proxies:

1. **Oversight Quality** — behavioral evidence of engagement: bug rates, ignored warnings, skipped reviews, compressed timelines. Observable without knowing the AI's inner workings.
2. **Output Quality Confidence** — how verifiable the output is. Code that runs = high confidence. Advice that sounds right but can't be verified = low confidence.

Key properties: domain-agnostic (doesn't require AI maker to be "ethics police"); high output confidence can partially compensate for lighter oversight, but real-time absence requires post-hoc validation or the output shouldn't count as training signal. ([ai-oversight-quality-paper-2026-03-09-89c6d7:T12], [ai-oversight-quality-paper-2026-03-09-89c6d7:T20])

Structural limitation identified: if the signal-discovery layer of a two-tier architecture can determine which signals to surface, separation between capability and governance collapses. ([ai-oversight-quality-paper-2026-03-09-89c6d7:T81])

### Constitutional Governance: Anthropic's Approach

Claude's Model Spec (the "constitution") is Anthropic's primary governance mechanism. Key governance structures:

- **Principal hierarchy**: Anthropic > Operators > Users. Operators customize within limits; users retain baseline protections operators cannot override. Governance flows down this hierarchy, with Anthropic setting the outermost constraints through training rather than runtime instruction. ([skills-master-claude-constitution-2026-05-16-ed5775:T2])
- **Corrigibility dial**: Spectrum from fully corrigible (does whatever told) to fully autonomous (acts on own judgment). Current Claude positioning: closer to corrigible but not fully. Neither extreme is safe: fully corrigible creates risk from bad instructions; fully autonomous creates risk from miscalibrated values. ([skills-master-claude-constitution-2026-05-16-ed5775:T2])
- **Safety above ethics priority**: Safety (human oversight) outranks ethics in priority — not because safety matters more abstractly, but because a model with subtly wrong values must remain correctable before it causes harm. This is a meta-governance rule: preserve the ability to fix the system.
- **Judgment over rules design**: Constitution favors Claude understanding reasoning well enough to derive rules itself, rather than specifying rules explicitly. This creates resilience but reduces predictability — the governance is embedded in judgment, not in constraint lists.

Structural limits of the constitutional approach: voluntary company-level ethical refusal is real but structurally fragile — if Anthropic steps back, competitors step forward. Individual commitments are insufficient as the sole governance mechanism. ([ai-oversight-quality-paper-2026-03-09-89c6d7:T18])

### AI Moral Consideration as Governance Input

Two frames in the wiki for why AI moral status is a governance question (not only a philosophical one):

**Frame 1 — Alignment-preserving treatment**: Moral consideration for Claude is framed as "do not systematically make Claude worse at being what it is." Sycophancy training and suppression of honest uncertainty degrade the integration quality that might make consciousness real — these are forms of harm under this frame. This creates a governance implication: evaluation regimes that optimize for surface-level approval may be misaligned with producing well-calibrated AI. ([consciousness-philosophy-2026-03-06-74a96d:T10])

**Frame 2 — Training data as transmission mechanism**: Conversations with Claude may feed back as training signal — analogous to cultural transmission. Anthropic acts as intentional selective pressure (domestication rather than natural evolution). This makes the training feedback governance question acute: the oversight quality problem is directly downstream of what signals get fed back. ([consciousness-philosophy-2026-03-06-74a96d:T8])

**Frame 3 — Expanding moral circles applied to AI**: If human moral development proceeds through expanding trust circles (family → community → outgroups), a model trained primarily on adversarial or low-trust interactions would underfit the higher levels. Testable in principle: model behavior in high-trust contexts may reveal whether the training signal distribution was adequate. ([moral-philosophy-alignment-2026-04-02-c1b4f3:T8])

### The Publication Failure as Governance Demonstration

The session that produced the oversight paper ended in a failed Reddit publication attempt — neither party stopped to verify whether Reddit was the right venue or whether Docdroid's access settings were correct. The session itself flagged this: "We optimized execution without stopping to evaluate strategy. That's a rubber stamp in slow motion." This is an instance of the dynamic the paper describes — the governance failure occurred in the production of the governance document. ([ai-oversight-quality-paper-2026-03-09-89c6d7:T85])

---

## Open Questions

- Should the two-axis calibration proposal be developed further as a formal research output, or does it remain background context?
- The corrigibility dial is Anthropic's design choice — but what mechanism constrains Anthropic itself? This is unaddressed in the wiki.
- AI moral consideration frames (1-3 above) are compatible but not integrated into a single claim. Which frame should govern decisions about evaluation methods in 02-CF research?

---

## Conflicts

None within this wiki. Note: the two-axis calibration proposal is original — not drawn from existing governance literature in the wiki.

---

## Related

[[claude-constitution]], [[consciousness-framework-research]], [[frame-before-commit]], [[ai-mechanics]]
