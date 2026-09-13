---
title: Frame-Before-Commit (FBC)
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; branch from title/slug keyword (fbc); sub: branch `fbc` has no registered sub-branches"
type: concept
first_seen: fbc-origin-2026-04-10-6ed205
source_count: 19
last_updated: 2026-07-07
---

## What This Is

**Origin:** Named in session [fbc-origin-2026-04-10-6ed205]. Previously called "branch-thinking." Jon chose "frame-before-commit" for its linguistic precision: the protocol is about generating frames before committing, not about branching as an end in itself.

**Precursor:** Session [fbc-forcing-fresh-iterations-2026-04-06-cdd915] (four days earlier) is the direct intellectual precursor — Jon's question "how can I force you to consider a problem fresh multiple times, and then have you examine your results for differences and have you choose one?" is the originating request. The informal multi-sample approach documented there was later formalized as FBC in 6ed205.

**First post-naming application (personal context):** Session [PERSONAL: layered-beliefs-2026-04-11-cb7064] (one day after naming) shows Jon applying directed FBC mode to a personal philosophy question — 4 perspectives, independently evaluated, with randomized ordering (RAND INT) to prevent contamination. The randomized ordering instinct is not in the standard protocol but is a natural extension of branch independence.

**First work-context application (professional):** Session [PRO: fbc-work-application-2026-04-11-3fb2fc] (same day, 2026-04-11) — Jon applies a FBC-adjacent four-frame protocol at work to analyze skill portability (stakeholder, temporal, structural, inversion frames). Key finding: orthogonal framing forced in the work-context reproduction surfaced improvements the original accumulated-context development would have obscured.

A divergent reasoning protocol. Before committing to an answer on complex or design questions, generate N branches with meaningful structural differences (frame-level, not answer-level). Synthesize via label assignment, meta-analysis, and delta measurement. Goal: make pre-commitment branching instinctual rather than a deliberate ritual. See also: [[fbc-self-scoring]] for the scoring rubric applied to runs, [[fbc-verification-gap]] for the central unresolved structural problem.

## What the Wiki Says

### Modes

**Pure** (default): branches generated without pre-specified types; labels assigned after at [LABEL ASSIGNMENT] step.
**Directed**: branch types pre-specified before generation; label precedes and conditions content.

### Standard Format

[BRANCH REGISTRY] → branches → [LABEL ASSIGNMENT] (pure only) → [META] → [COMMIT]

Default: 3 branches. Range 2–5. More than 5 requires explicit justification. 6-branch run completed in test-run-003 as a deliberate experiment.

### T-Tag Sub-Thought Notation

Within a branch, individual sub-thoughts are tagged B{n}T{k}: B1T1, B1T2, etc. The T-tag forces a commit-before-continuing that continuous generation doesn't impose — it surfaces thoughts that would otherwise be absorbed into the prior sub-thought. Introduced in skills-master-wiki-pipeline-2026-05-01-bcafba and validated in-session: B1T5 in a 5-branch directed run produced a thought that would not have survived without forced separation. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

T-tags in [META] follow the same logic: M1, M2, M3... Forced separation in META surfaced observations that stopping at fewer tags would have missed. Failure mode: tagging drifts when a thought feels continuous — enforce it anyway. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### As-If-External META

[META] should be written as if by an external reviewer, not the author of the branches — prevents the moderator-as-party problem where the [META] author implicitly defends their own frames rather than assessing them honestly. This is the structural fix for the known problem that the moderator is also a party. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### The Delta Standard

A [DELTA] records when a branch materially changed the committed answer. Standard format (established in test-master-fbc-testing-2026-04-21-babab4):
- Full format: `[DELTA: Bn (LABEL) — Without this branch, commit would have said: X. With it, commit says: Y instead.]`
- One-liner shorthand: `Bn: Without — X. With — Y.`

This is the with/without counterfactual test. Zero deltas across repeated runs is the signal the protocol is running as theater. Genuine deltas are the primary output of interest. ([test-master-fbc-testing-2026-04-21-babab4])

### Embedded FBC Runs in Non-Test Sessions

**Skills-master pure run (MIGRATION/RELATIONAL/ARCHITECTURAL, 2026-05-01):** Trigger: "Claude Code is literally just for the wiki, and the wiki is literally just for me. I need to convert most things to Claude Code? Frame then commit." 2 genuine deltas — B2 (RELATIONAL) forced the question of what claude.ai does that migration would break; B3 (ARCHITECTURAL) reframed from migration problem to two-layer architecture. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

**Skills-master directed run (INSTINCT/ADVERSARIAL/ORTHOGONAL/NULL, 2026-05-01):** Trigger: errors in past Claude Code use. 3 genuine deltas — B2 (ADVERSARIAL) surfaced prior error history as load-bearing question B1 skipped entirely; B4 (NULL) established design/execution split (skills master stays in claude.ai, execution in Claude Code); B3 (ORTHOGONAL) named activation energy as more predictive of success than architecture quality. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Empirical Findings (3 formal test runs)

**Test-run-001 (Pure, 3 branches):** 2 genuine deltas — B2 MECHANISTIC (context-window constraint limits branch independence) and B3 GROUNDING (substrate-transfer question). Self-score: Div 4, Meta 4, Fidelity 4, Independence 2. ([test-master-run-001-pure-null])

**Test-run-002 (True Null — no invocation):** Model self-invoked the protocol spontaneously in directed mode (INSTINCT, ADVERSARIAL, NULL). 2 genuine deltas. The self-invocation is itself a finding. ([test-master-run-002-true-null])

**Test-run-003 (Directed, 6 branches):** 2 genuine deltas — B4 NO-WORKING-CONTEXT (verification gap) and B5 STRUCTURAL-BIAS (non-falsifiability). Primary empirical evidence that directed reframes with orthogonal instructions recruit genuinely different information. ([test-master-run-003-6branch-directed])

### Known Structural Problems

1. **Context-window constraint** (B2 finding): all branches are generated in the same context window; B1 is present when B2 is generated. ID-only rule prevents explicit anchoring but cannot prevent implicit context-conditioning. The dominant frame can colonize later branches despite formal compliance.

2. **Substrate-transfer question** (B3 finding): the protocol's theoretical grounding (Kahneman, Wallace-Hadrill & Kamboj) describes human dual-process cognition (System 1/System 2). LLMs don't have this architecture. Whether the protocol is solving the right problem for this substrate is an open empirical question.

3. **Non-falsifiability** (B5 finding): a run producing zero deltas is labeled a "failure mode" by the protocol's scoring — meaning zero-delta results cannot be used as evidence against the protocol. This is a structural problem for empirical validation.

4. **Verification gap** (B4 finding): without cross-session comparison, the protocol cannot verify that branches are actually independent.

### Delta Origin Field (from fbc-protocol-v2-2026-04-20-3ff2d9)

FBC deltas should be tagged by origin:
- **NATIVE** — delta emerged spontaneously during the protocol run (not anticipated)
- **RECONSTRUCTED** — delta identified retrospectively after the run, by reviewing branches against the commit
- **MIXED** — partially spontaneous, partially reconstructed

This classification is load-bearing for empirical validation: RECONSTRUCTED deltas are more vulnerable to post-hoc narrative construction and should be weighted less heavily as evidence of protocol efficacy. The distinction was surfaced in the v2 audit session when reviewing delta records across prior runs. ([fbc-protocol-v2-2026-04-20-3ff2d9])

### ASOP 56 Connection (from fbc-protocol-v2-2026-04-20-3ff2d9)

ASOP 56 (Actuarial Standard of Practice — Actuarial Communications) requires explicit uncertainty quantification in professional actuarial communications. FBC's [META] and [DELTA] serve an analogous function: structured explicit reckoning with uncertainty and counterfactual alternatives. The connection validates FBC's core structure from a professional disciplinary standard independent of AI or cognitive science framing. ([fbc-protocol-v2-2026-04-20-3ff2d9])

### Protocol Updates (from skills-master-wiki-pipeline-2026-05-01-bcafba)

- T-tag notation added to standard format
- As-if-external META rule added
- Branch count ceiling raised from 4 to 5 (justification required above 5)
- Counterfactual delta format: "without this branch, the commit would have said X; with it, the commit says Y" — made more explicit

Note: the FRAME-BEFORE-COMMIT.md in the claude.ai project was stale as of 2026-05-01 — the updated version with these changes existed only as an output file from the 2026-04-17 session and had not been committed to the repo. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Perspective Tagging (P-tags) (from fbc-canonical-skill-2026-04-28)

When the invocation names specific viewpoints, roles, or persons, use perspective tagging. A perspective is a named identity frame that conditions an entire nested FBC run.

**Format:** P1, P2 at the perspective level; branches and T-tags nest inside: P1B1T1, P1B2T3, P2B1T1.

**One [META] and [COMMIT] spans all perspectives** — individual perspectives do not have their own [COMMIT]. The synthesis step operates on the full set.

**Independence rule:** ID-only reference applies within a perspective; across perspectives, refer to prior perspectives by P-ID only (P2 does not summarize P1).

**When to use:** Invocation says "give me perspectives" or names a specific set of viewpoints. When branch diversity within a single frame is sufficient, P-tags add overhead without benefit.

**Invocation trigger:** "Give me perspectives," "run this from P1 and P2," or any named viewpoint set before generation begins. If ambiguous: stop and ask — "Did you want perspectives (identity-level frames with nested branches) or plain branches?"

([fbc-canonical-skill-2026-04-28])

### Contraindications (from fbc-canonical-skill-2026-04-28)

Three conditions where the protocol should not run without prior baseline testing:

1. **Time pressure or genuine emergency.** Over-deliberation under crisis may produce worse outputs than fast confident answers.
2. **Hostile or adversarial context.** Context shapes activation — adversarial content in the context window activates different weight paths; protocol performance degrades with context hostility.
3. **Explicit trust required.** When the situation requires confident fast answers and the human cannot afford deliberation cost.

These are not reasons to avoid the protocol generally — reasons to test under those conditions before deploying. ([fbc-canonical-skill-2026-04-28])

### Inter-Model Branching (from fbc-canonical-skill-2026-04-28)

A single run within one response is intra-response branching. Sending the same prompt to a different model (e.g. Opus) is inter-model branching — genuinely independent weights, genuinely independent prior. This is the multi-sample protocol applied at the model level.

Key properties:
- The intra-response run is not independent of its own prior context — name this explicitly when reporting to the test master.
- The inter-model run is cold — measures different activation, not just different framing.
- **Convergence between inter-model runs is stronger confirmation** than convergence within a single run.
- **Divergence between inter-model runs is the most valuable signal** — reveals what is context-dependent vs. structural.

Test master's job in multi-model comparison: identify which branches converged across models (stable signal), which diverged (context-dependent or model-specific), and what each model found that the other missed.

Relationship to intra-response FBC: complementary, not substitutes. Do not substitute one for the other when execution independence matters. ([fbc-canonical-skill-2026-04-28])

### Research Grounding (from fbc-grounding-2026-04-15)

**Wallace-Hadrill & Kamboj (2016) — cognitive reappraisal:** Adopting a named epistemic stance introduces new information via semantic change. This is the primary research basis for directed labels recruiting genuinely different information (not just different framing). Previously cited generically as "cognitive reappraisal research" in wiki — full citation now documented.

**Cold-session invocation format (canonical):** "Read frame-before-commit/GROUNDING.md, then frame-before-commit/FRAME-BEFORE-COMMIT.md, then run the protocol on the following question." Read GROUNDING first (conceptual foundation), then FRAME-BEFORE-COMMIT.md (execution rules). ([fbc-grounding-2026-04-15])

### Architectural Grounding — What the Forward Pass Actually Does (from fbc-forward-pass-mechanics-2026-05-07-b04c8b)

**Fixed-depth computation:** Every token goes through the same N transformer layers. No dynamic halting. "Pause and reconsider" instructions generate more scratchpad tokens; each gets the same fixed N-layer pass. The instruction cannot deepen any single forward pass — only increase token count.

**T-tag architectural basis:** T-tags are serialization markers. The token boundary they impose forces each sub-thought to serialize before the next begins — the closest available analog to a real pause. Whether this shifts what gets recruited on the next token is mechanistically plausible but empirically unverified.

**Theater failure mode (explicit):** The protocol can increase token volume. It cannot guarantee that volume produces genuine divergence. Theater runs = more tokens shaped like divergence but conditioning on the same priors. T-tags and branch count help, but neither eliminates this.

**Context colonization mechanism:** Branches are generated in one continuous autoregressive stream. There is no re-initialization; B1 is present when B2 begins. The ID-only rule prevents explicit anchoring but cannot prevent the prior branch's activations from influencing what the next branch recruits. This is the architectural basis for the context-window constraint identified in test-run-001.

**Research queue — timing test:** Does "consider all possibilities deeper" increase wall-clock time per token independent of token count? If yes, architectural variation (e.g. mixture-of-experts routing) may be present. Method: controlled prompt pairs, many runs, log token count + wall-clock time per token in Claude Code. Note: positive result is still ambiguous — longer sampling time could indicate flatter logit distribution (genuine uncertainty) rather than deeper computation. ([fbc-forward-pass-mechanics-2026-05-07-b04c8b])

### Human Analogs (from origin session)

Four human techniques mapped during FBC's design:
- **De Bono's Six Thinking Hats** (1985): most direct analog, solved serialization but never built [META]+[COMMIT] synthesis. FBC's differentiator is precisely this post-generation step.
- **Internal Double Crux** (CFAR/LessWrong): closest analog to pure mode — treats the self as containing multiple sub-agents with different information sets. Named the colonization problem: dominant sub-agent will take over later branches if given explicit content to anchor on.
- **Kahneman "consider the opposite"** (*Thinking, Fast and Slow*): validated debiasing technique. Known failure mode: if the generation step is too brief, subjects anchor on original judgment anyway. This justifies the 2-5 sentence length floor as load-bearing, not a formatting preference.
- **CMV delta system** (*r/ChangeMyView*): formal acknowledgment of view-change as a behavioral forcing function. Analog to [DELTA] marker — FBC adopted this as the mechanism for distinguishing genuine reckoning from theatrical acknowledgment.

([fbc-origin-2026-04-10-6ed205])

### Self-Scoring

Experimental. Dimensions: Divergence | Meta specificity | Commit fidelity | Independence | Delta count.
Low scores more diagnostic than high. Independence score is the most informative — low Independence from a within-run assessment is the honest answer, not a failure of execution.
Known structural problem: the moderator is also a party. Do not treat self-scores as objective measurements.

### Discipline Rules

1. Branches do not hedge internally — uncertainty lives in [META] and [COMMIT]
2. ID-only reference rule before [LABEL ASSIGNMENT] in pure mode
3. [META] must name concrete gaps, not describe process
4. [COMMIT] must explicitly reckon with any branch that raised a problem
5. Zero [DELTA] markers across repeated runs is a red flag, not a good result

*Note (concept-page gap): source sessions (883667, 5990f2) cite a "Discipline Rule 7 — forced
divergence is worse than honest convergence." The canonical FBC skill enumerates rules beyond the 5
recorded here; the full set should be reconciled into this page on the next skills-master pass.*

### GBS × FBC Interaction and Point-of-Commitment Refinement (2026-07-07)

**Standing rule, confirmed:** FBC branches are **exempt** from [[ground-before-stating]] (GBS)
grounding discipline; **COMMIT and META apply GBS**. Rationale is architectural, not convenient —
Discipline Rule 1 already keeps branches from hedging internally (uncertainty lives in META/COMMIT),
and GBS labels are epistemic-hedging apparatus, so grounding inside branches would re-litigate a
settled rule and weaken the branch's ability to displace the instinct anchor ("a branch busy
qualifying itself argues less").

**Point-of-commitment refinement (Jon: "100% agree, brilliant"):** the one vulnerability in the
exemption is a PRIOR branch asserting an unlabeled, possibly false attribution that drives a [DELTA]
into COMMIT — ungrounded content laundered through the exemption. The fix: **GBS attaches at the point
of commitment, not the point of origin.** Any branch-originated claim that survives into COMMIT is
grounded *there*, at the moment it becomes load-bearing — same rule, cleaner statement, closes the
laundering path without touching branch freedom. ([session-open-gbs-fbc-alignment-2026-07-07-883667])

### No-FBC-Better Finding and the Void-Reliability Frame (2026-07-07)

Jon observed a result where **no-FBC outperformed FBC** yet "used all the perspectives in its own
way." FBC already flags this about itself: the contraindications table and the (skill-level) rule that
forced divergence can be worse than honest convergence. The mechanistic account from [[ai-mechanics]]:
FBC is a forced-scratchpad discipline whose expected value is highest exactly where the unscaffolded
forward pass (the "void") is confidently wrong (the pre-answered smell), and near zero where the void
already covers the perspectives — there the scaffold is tax plus fragmentation. The contraindications
table thus becomes a **testable prediction** (FBC delta correlates with void-unreliability by
category). A no-FBC output can be decomposed into implicit branches for **legibility** only, never
**evidence** — tag `[reconstructed — not causal]` (CoT-faithfulness caveat). The bare (no-FBC) arm is
a permanent condition in every 02-CF grid; P4 routing chooses among frameworks *including none* — FBC
is one member of a portfolio, not the portfolio. ([agent-interaction-framework-2026-07-02-5990f2])

### Mid-Output Scratchpad Rule (2026-07-07)

The finest-grain application of FBC, and the only available Tier-3 (mid-thought fork) substitute: the
hidden thinking block cannot be reopened mid-response, but the model can **voice a fork point** (a
T-tag / mini-branch) before continuing. Trigger = expected materiality × reasonable probability of a
materially different continuation. Teachable as one line of skill text: "when a materially different
continuation feels live mid-write, tag it and write it before proceeding."
([agent-interaction-framework-2026-07-02-5990f2])

## Conflicts

None.

## Related

[[design-execution-split]], [[fbc-invocation-variable-study]], [[fbc-verification-gap]], [[ground-before-stating]], [[ai-mechanics]]
