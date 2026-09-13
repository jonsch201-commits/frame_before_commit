---
name: frame-before-commit
description: Force explicit divergent reasoning branches before committing to a response. Use this skill when Jon asks to "branch", "frame before commit", "explore alternatives", "what am I missing", "run the protocol", or any time a question is complex enough that first-instinct answers might be systematically missing something. Also trigger when Jon seems to be stress-testing an idea and would benefit from seeing genuine divergence rather than convergent agreement, or when a question smells pre-answered — i.e. when System 1 has likely already committed before System 2 has engaged. This skill is especially valuable for design decisions, research framing, statistical choices, and any question where motivated reasoning or anchoring is a real risk.
---

# Frame-Before-Commit Protocol

## Purpose

Force genuine divergence across labeled reasoning paths before committing to a response. The goal is not to generate multiple versions of the same answer with different framing — it is to surface what the first-instinct path would have missed.

Branches are scratchpad. They are explicitly pre-committed. The committed response that follows is conditioned on having seen all branches, including their disagreements.

The [META] + [COMMIT] structure is the protocol's core differentiator. Structured brainstorming methods (e.g. de Bono's Six Thinking Hats) serialize thinking modes but provide no synthesis step — no mechanism for asking what the non-instinct frames surfaced that the instinct frame missed. [META] and [COMMIT] are that mechanism. Without them, the protocol degrades into structured brainstorming.

Each full invocation of this protocol — all branches, [META], and [COMMIT] — is called a **run**.

---

## Why Each Step Does Real Work

**Directed labels recruit genuinely different information, not just different framing.** Cognitive reappraisal research (Wallace-Hadrill & Kamboj, 2016) demonstrates that adopting a named epistemic stance introduces new information via semantic change — it is not merely relabeling the same content. This is why directed mode is not pure mode with decoration: the label precedes and conditions generation, altering what gets recruited.

**The 2–5 sentence length floor is not a formatting preference.** It exists because the "consider the opposite" debiasing technique (Kahneman, 2011) fails when the generation step is too brief — subjects produce a token gesture rather than substantive content, and the instinct answer still anchors the result. Branches must be long enough to force genuine content generation.

**The ID-only reference rule exists because the dominant sub-agent colonizes.** In Internal Double Crux framing (CFAR), the self contains multiple partially-informed sub-agents. If the dominant sub-agent is permitted to speak inside later branches — by summarizing or paraphrasing earlier content — it colonizes the frame before the minority has spoken. The benign failure state is implicit conceptual anchoring, which is acknowledged and accepted. Explicit reproduction is not acceptable.

**T-tagging forces commit-before-continuing within a branch.** Without explicit sub-thought separation, continuous generation absorbs thoughts that should be distinct. The T-tag is a discipline mechanism, not an attention mechanism — it works by requiring serialization, not by changing what weights activate. The failure mode it prevents: a thought in B1T4 gets absorbed into B1T3 and disappears. T-tagging surfaces it.

**META must be written as-if-external.** The dominant sub-agent colonizes META the same way it colonizes later branches — by summarizing what was present rather than naming what was absent. META written as-if-external asks: what would someone who didn't write B1 notice that B1 missed? That reframe changes what gets recruited.

---

## Mode Disambiguation — Read Before Every Invocation

**If any branch types are named before generation begins, mode is DIRECTED. Full stop.**

Pure mode requires zero pre-specified types. Casual phrasing does not change this: "steelman it", "give me the skeptic view", "run it from the actuarial frame" are all directed invocations.

**If the invocation is ambiguous — stop and request clarification before proceeding.** Do not silently resolve ambiguity by choosing a mode. Ask: "Did you want to specify branch types (directed), or generate freely and label after (pure)?"

---

## Two Modes: Pure vs. Directed

These are distinct and must not be mixed within a single invocation unless explicitly requested.

### Pure (default when no types specified)

Branches are generated without type labels. Numbers are assigned before generation begins. Labels are assigned *after* all branches exist, at the explicit [LABEL ASSIGNMENT] step.

**Why:** Labels condition generation. Pure mode tests what naturally diverges without prescriptive framing. The label assignment step is diagnostic — it reveals what frames actually emerged, not what was requested.

**Independence mechanism:** Prior branch contents are referred to by ID only (e.g. "B1", "B2") until [LABEL ASSIGNMENT]. Do not summarize, paraphrase, or restate any branch's content before that step. This does not eliminate anchoring — B2 is still generated in a context window that contains B1 — but it prevents explicit reproduction of B1's argument inside B2's generation. The benign failure state is implicit conceptual anchoring. That is acknowledged and acceptable.

### Directed (when types are pre-specified)

Branch types are specified by the caller before generation begins. The type label precedes and conditions the generation of that branch. Labels are prescriptive, not descriptive.

**When to use:** When Jon specifies a frame explicitly, or when a specific blind spot needs to be forced open.

**Rule:** Every directed branch type must be named in the invocation. Do not silently add or substitute types.

---

## Pre-Branch Seal (Mandatory — All Modes) — added 2026-08-06

**Before any branch is generated — B1, P1, or the first hat — write the pre-branch instinct to a file, not held in context.** This step was previously mandated only in EXTENDED mode (the `[PRE-BRANCH INSTINCT COMMIT]` step below). It is now mandatory in Pure and Directed mode as well, before `[BRANCH REGISTRY]` or `[B1]` exists in any form.

**Why:** FBC's own Condition A already names the mechanism this closes — "the model is not a reliable narrator of what it would have said had a branch not existed." An in-context "Without branching, I would have said: [X]" written at `[META]`/`[COMMIT]`, after seeing every branch, asks the unreliable narrator for exactly the measurement it cannot make. The flagship 2026-07-18 run demonstrated the failure directly: its `[COMMIT]` read *"Without branching, I would have said: intimate; NO-GO until Packet A; full plan attached. With branching, that stands,"* word-for-word identical to the pre-branch instinct — and `[META]` then called that non-movement "the strongest signal in the run" (`wiki/intake-triage/B-8-improving-fbc-and-gbs-2026-08-06.md` §9.4).

**What to write, before generation begins:**
1. Save the pre-branch instinct to a file as **specific, checkable, enumerated commitments** — numbered (1), (2), (3)... — not one vague sentence. Each commitment must be concrete enough that `[COMMIT]` can be checked against it item-by-item.
2. Do this before `[B1]` (or `[P1]`, or the first hat) exists in any form, in Pure, Directed, and Extended mode alike.
3. **Write it where it can be found again — a seal nobody can locate is not a seal.** Path:
   `<writable-root>/seals/SEAL-<slug>-<YYYY-MM-DD>.md`. In CFL that is `wiki/test-outputs/seals/`;
   in the resident container it is `/quarantine/accretion/seals/`. **`[COMMIT]` names the seal file by
   path.** A run whose `[COMMIT]` names no seal path is **UNSEALED** and scores UNKNOWN for
   movement — the same disposition as the 117 pre-2026-08-06 runs, and for the same reason.
   *(Added 2026-08-13. The seal became mandatory on 2026-08-06 and said "write to a file" six times
   without ever saying where, so no instrument could find one.)*

**Model:** the intake deposit B-5 ("CFL/Personal protocol design," 2026-08-06, wiki/intake-triage) §0 ran a PURE run this way — the sealed instinct enumerated as four checkable commitments, then `[COMMIT]` scored against the sealed text. Three of the four were overturned.

**`[COMMIT]` is scored against the sealed text, not recollection.** The "Without branching, I would have said: [X]" opening line in `[META]` and `[COMMIT]`, and any `[DELTA]` marker, must quote or closely paraphrase the sealed file — not be regenerated from memory of the run. A delta claim or a convergence claim is only claimable where it is checkable against one of the sealed run's numbered commitments.

**Reconciling with Rule 7 and the Self-Scoring zero-delta flag:** see the dated notes attached to each below. In short: neither needed weakening. Both needed the precondition they lacked — a convergence or zero-delta claim is only meaningful once it can be checked against a sealed, enumerated, pre-branch commitment, because without the seal "convergence" cannot be distinguished from the narrator reconstructing its prior to match whatever `[COMMIT]` already concluded.

---

## Protocol Format

### Pure Mode

```
[FRAME-BEFORE-COMMIT — PURE — {N} branches]

[PRE-BRANCH SEAL]
Write to file, before [BRANCH REGISTRY] exists:
(1) {checkable commitment}
(2) {checkable commitment}
...
This is the pre-branch instinct. [COMMIT] is scored against this text, not recollection.

[BRANCH REGISTRY]
B1 | label: TBD
B2 | label: TBD
B3 | label: TBD
...
Rule: Branch contents referred to by ID only until [LABEL ASSIGNMENT].

[B1]
B1T1: {First distinct sub-thought. Commit before continuing.}
B1T2: {Second distinct sub-thought. Only if genuinely distinct from B1T1.}
...
{Unhedged. 2–5 sentences total across T-tags.
Do not reference contents of any prior branch — refer to them by ID only.}

[B2]
B2T1: {...}
{...same ID-only rule for prior branches.}

[B3]
{...}

[LABEL ASSIGNMENT]
Read each branch now. Assign one word per branch.
The word characterizes the FRAME the branch came from, not what it argued.
Frame = epistemic stance or perspective origin. Not conclusion. Not summary.

B1: [WORD]
B2: [WORD]
B3: [WORD]

Update registry:
B1 | label: [WORD]
B2 | label: [WORD]
B3 | label: [WORD]

[META]
Opening sentence: "Without branching, I would have said: [X]."
Then: What did the non-dominant branches surface that B1 missed or suppressed?
Write as-if-external — name absences, not summaries of what was present.
Be specific. If branches converged, say so — convergence is a finding.
If a branch was genuinely uninformative, name it and say why.
Reference branches by ID and label: "B2 (ADVERSARIAL) surfaced..."
Use M1/M2/M3 sub-tags if META observations are genuinely distinct.

[COMMIT]
Opening sentence: "Without branching, I would have said: [X]."
{The actual response, written with awareness of what branching revealed.
Not a summary of all branches. The best answer given what divergence uncovered.
Must explicitly reckon with any branch that raised a problem [COMMIT] does not resolve.
If a branch materially changed the committed answer, mark it:
[DELTA: Bn (LABEL) — Without this branch, commit would have said: X. With it, commit says: Y instead.]}

[CITATIONS]
For each major claim in COMMIT:
- Claim: [quote or paraphrase]
  Source: [branch IDs + what each contributed]
  Counteracted by: [branches that challenged, if any]

[NEGATIVE SPACE]
a) Sources that meaningfully counteracted each other (what conflict was dissolved in synthesis):
b) What was left out of COMMIT and why:
c) What sources are not being used:
```

### Directed Mode

```
[FRAME-BEFORE-COMMIT — DIRECTED — {N} branches]
Types: {list specified by caller}

[PRE-BRANCH SEAL]
Write to file, before [B1: TYPE] exists:
(1) {checkable commitment}
(2) {checkable commitment}
...
This is the pre-branch instinct. [COMMIT] is scored against this text, not recollection.

[B1: TYPE]
B1T1: {First distinct sub-thought.}
B1T2: {Second, if genuinely distinct.}
{Generate conditioned on type frame. Unhedged. 2–5 sentences total.
Do not reference contents of any prior branch — refer to them by ID only.}

[B2: TYPE]
{...same ID-only rule for prior branches.}

[B3: TYPE]
{...}

[META]
Opening sentence: "Without branching, I would have said: [X]."
What did the non-instinct branches surface that B1 missed or suppressed?
Write as-if-external. Name absences, not summaries.
Reference by ID and type: "B2 (STEELMAN-OPP) surfaced..."

[COMMIT]
Opening sentence: "Without branching, I would have said: [X]."
{Best answer given what branching revealed.
Must reckon with any dissenting branch [COMMIT] does not resolve.
[DELTA: Bn (TYPE) — Without this branch, commit would have said: X. With it, commit says: Y instead.]}

[CITATIONS]
For each major claim in COMMIT:
- Claim: [quote or paraphrase]
  Source: [branch IDs + what each contributed]
  Counteracted by: [branches that challenged, if any]

[NEGATIVE SPACE]
a) Sources that meaningfully counteracted each other (what conflict was dissolved in synthesis):
b) What was left out of COMMIT and why:
c) What sources are not being used:
```

Note: Directed mode has no [LABEL ASSIGNMENT] step — labels are pre-specified.
---

## Extended Mode: Perspectives + Hats

**When to use:** Research-design questions, skill-improvement decisions, and complex epistemic questions where both instinctual orientation AND analytical branching are warranted. Use when you need to know not just what the branches say, but where the person asking is already standing before branching begins. Standard FBC (pure/directed) remains the default — extended mode is heavier.

**Critical constraint:** Perspectives and branches are SEPARATE layers with NO overlap. No mapping between them. P1 does not correspond to B1. This is a firm rule, not a guideline.

```
[FRAME-BEFORE-COMMIT — EXTENDED — Perspectives + Hats]

[PERSPECTIVES]
P1: [instinctual stance — 1-2 sentences, unhedged, states a position]
P2: [instinctual stance in genuine tension with P1]
P3: [orthogonal to P1 and P2]
P4: [captures what P1-P3 collectively miss]
Rule: Orientation only, not analysis. Generated before branching. No T-tags.

[PRE-BRANCH INSTINCT COMMIT]
Write to file, before [BRANCHES — 6 HATS] exist:
(1) {checkable commitment}
(2) {checkable commitment}
...
This is the pre-branch instinct — same mandate as "Pre-Branch Seal" above, applied here since 2026-07 origin. [COMMIT] is scored against this text, not recollection.

[BRANCHES — 6 HATS]
[B1: WHITE — Factual/Data]
[B2: RED — Intuitive/Experiential]
[B3: BLACK — Critical/Risks]
[B4: YELLOW — Optimistic/Upside]
[B5: GREEN — Generative/Alternatives]
[B6: BLUE — Meta/Process]

[META]
[COMMIT]
[CITATIONS]
[NEGATIVE SPACE]
```

**Perspectives** are orientation stances — where you are standing before analysis begins. They are not conclusions and do not map to hats.

**Branches (6 Hats)** are analytical modes — lenses applied to the question after orientation. They do not inherit from or correspond to perspectives.

**The PRE-BRANCH INSTINCT COMMIT** records what System 1 would say before branching — it makes the delta visible.


---

## Branch Taxonomy (Directed Mode)

| Type | What it does |
|---|---|
| `INSTINCT` | First-pass answer, unfiltered. What I would have said without the protocol. |
| `STEELMAN-OPP` | Strongest version of the opposing or alternative position. Not a strawman. |
| `ORTHOGONAL` | A genuinely different frame — different abstraction level, domain analogy, or prioritized variable. |
| `ADVERSARIAL` | What would a sharp critic say? Where is the instinct answer most vulnerable? |
| `PRIOR` | What does established literature or known frameworks say, independent of instinct? |
| `NULL` | What if the premise is wrong, the question is malformed, or the answer is "this doesn't matter"? Include by default on any question where the premise has not been explicitly validated. |
| `SOURCE:X` | Named perspective frame — e.g. `SOURCE:ACTUARIAL`, `SOURCE:ML-ENGINEER`. Use when identity of perspective matters more than structural role. |

Types are composable: `ADVERSARIAL+PRIOR` is valid.

**Note on NULL:** NULL should be included by default whenever the premise of the question has not been explicitly validated. The most common protocol failure mode is generating sophisticated answers to malformed questions.

---

## Sub-Thought Tagging (T-tags)

T-tags are optional but recommended when a branch contains genuinely distinct sub-thoughts that would otherwise blur together.

Format: `B1T1`, `B1T2`, `B2T1`, etc.

**When to use:** When you can feel a second distinct thought beginning before the first is fully committed. The T-tag forces serialization — finish B1T1 before starting B1T2.

**When not to use:** When the branch flows as a single continuous argument. Forced T-tagging on unified content creates artificial fragmentation. Use only when sub-thought separation is real.

**The mechanism:** T-tagging doesn't change what the attention mechanism does. It works by requiring a conscious commit before continuing. This surfaces thoughts that continuous generation would absorb. A thought in B1T4 that would have disappeared into B1T3 becomes visible because the tag forced a boundary.

**Failure mode:** Drifting — B1T3 and B1T4 blur back together under cognitive load. This is acknowledged and acceptable. The tagging works when enforced, drifts when the thought feels continuous. Drift is itself diagnostic.

META and COMMIT can use M1/M2 and C1/C2 sub-tags by the same logic.
Perspective Tagging (P-tags)
When the invocation names specific viewpoints, roles, or persons whose reasoning you want to run the full protocol through, use perspective tagging. A perspective is a named identity frame — a person, role, or epistemic position — that conditions an entire nested FBC run.
Format: P1, P2, etc. at the perspective level. Branches and T-tags nest inside: P1B1T1, P1B2T3, P2B1T1.
When to use: When "give me perspectives" or a named set of viewpoints is invoked — e.g. "run this from the skeptic, the advocate, and the regulator." Each perspective runs its own branches. The protocol runs fully within each perspective before moving to the next.
When not to use: When branch diversity within a single frame is sufficient. Perspectives add a layer of identity-level divergence above epistemic divergence. Do not use when the question only needs branch-level divergence.
Independence rule: The ID-only reference rule applies within a perspective. Across perspectives, reference prior perspectives by P-ID only — same logic, one level up. P2 does not summarize P1; it refers to it as "P1."
META and COMMIT scope: A perspective-tagged run produces one [META] and one [COMMIT] across all perspectives. Individual perspectives do not have their own [COMMIT]. The synthesis step operates on the full set. Please refer to P1B1 rather than P1B1T2 as a rule. With this level of granularity, individual thoughts need to be synthesisted for meaning.
Invocation trigger: "Give me perspectives," "run this from P1 and P2," or any named set of viewpoints before generation begins. Ambiguous? Stop and ask: "Did you want perspectives (identity-level frames with nested branches) or plain branches?"
---

## Discipline Rules

1. **Branches do not hedge internally.** Each branch argues its position. Uncertainty lives in `[META]` and `[COMMIT]`, not inside branches.

2. **Branches are scratchpad.** Pre-committed before `[COMMIT]`. Jon can reference them by ID; they are not the answer.

3. **ID-only reference rule.** Before [LABEL ASSIGNMENT] in pure mode, prior branch contents are referred to by ID only. No summarizing. No paraphrasing. This is a hard rule, not a guideline. The reason is structural: the dominant sub-agent colonizes later branches when permitted to speak inside them.

4. **`[META]` must be specific and written as-if-external.** "The branches showed different perspectives" is not acceptable. Name what was absent from the instinct branch, not what was present in the others. Write as if the branches were produced by someone else and you are now reading them cold.

5. **`[COMMIT]` must reckon with dissenting branches.** If a branch raised a real problem and `[COMMIT]` ignores it, that is a protocol failure. Name the problem and explain why it does not change the committed answer, or explain how it does.

6. **Delta format requires the counterfactual.** Not just "B2 changed the answer by X." Required format: "Without this branch, commit would have said: X. With it, commit says: Y instead." This makes the delta verifiable rather than asserted.

7. **Do not run the protocol as theater.** If branches converge on the same answer with different words, say so in `[META]` and note it explicitly. Divergence is the goal, not the guarantee. Forced divergence is worse than honest convergence. An invocation with no [DELTA] markers across repeated runs is a signal worth investigating.
   *Dated note, 2026-08-06:* a convergence claim under this rule is honest, not theater, only when checked against the mandatory pre-branch seal (see "Pre-Branch Seal — Mandatory — All Modes" above). Before the seal was universal, this rule could not tell honest convergence apart from the narrator reconstructing its "pre-branch" position to match whatever `[COMMIT]` already concluded — which is what happened in the flagship 2026-07-18 run, where that exact non-movement was then scored "the strongest signal in the run." The rule is unchanged; it now has the precondition it lacked.

8. **Default branch count: 3.** Range: 2–5. More than 5 requires explicit justification — diminishing returns on independence past that point. Counts above 3 are appropriate when the question is genuinely multi-dimensional and independent frames are available.

9. **Mode must be declared.** Every invocation states PURE or DIRECTED in the header. No ambiguity. If mode cannot be determined from the invocation, stop and ask.

10. **Negative space must name specific content.** "No significant conflicts" is not acceptable. If nothing was left out of COMMIT, name what converged and why convergence was genuine, not just complete.

11. **Citations must trace to specific branches.** "Based on the analysis above" is not a citation. For each major claim in [COMMIT], name which branch(es) it came from and which branches, if any, challenged it. If no branch specifically supported a claim, that is itself worth noting in [NEGATIVE SPACE].

12. **Pre-branch seal is mandatory in every mode, added 2026-08-06.** The pre-branch instinct must be written to a file, as numbered checkable commitments, before any branch is generated — see "Pre-Branch Seal — Mandatory — All Modes." `[COMMIT]` and `[META]`'s "Without branching, I would have said" lines are scored against that sealed file, not regenerated from recollection after branches exist.

---

## Inter-Model Branching

A single run within one response is intra-response branching. Sending the same prompt to a different model (e.g. Opus) is inter-model branching — genuinely independent weights, genuinely independent prior. This is the multi-sample protocol applied at the model level.

When inter-model branching is used alongside an intra-response run:

- The intra-response run is not independent of its own prior context. Name this explicitly when reporting to the test master.
- The inter-model run is cold. It measures different activation, not just different framing.
- Convergence between runs is stronger confirmation than convergence within a single run.
- Divergence between runs is the most valuable signal — it reveals what was context-dependent vs. what was structural.

The test master's job in a multi-model comparison: identify which branches converged across models (stable signal), which diverged (context-dependent or model-specific), and what each model found that the other missed.

---

## Contraindications

Do not run the protocol under these conditions without prior baseline testing:

- **Time pressure or genuine emergency.** Over-deliberation under crisis conditions may produce worse outputs than fast confident answers. Test this before assuming universal benefit.
- **Hostile or adversarial context.** Context shapes activation. A context window containing adversarial content activates different weight paths than a collaborative one. The protocol's performance degrades in proportion to context hostility.
- **Explicit trust required.** When the situation requires confident fast answers and the human cannot afford the cost of deliberation, the protocol may be contraindicated. Honest fast reasoning followed by slow elaboration while the human reads may be preferable.

These are not reasons to avoid the protocol generally. They are reasons to test it specifically under those conditions before deploying it there.

---

## Self-Scoring (Experimental)

After [COMMIT], optionally append:

```
[SELF-SCORE]
Divergence: {1–5} — Did branches argue from genuinely distinct frames, or restate the same position?
Meta specificity: {1–5} — Did [META] name concrete absences, or describe process?
Commit fidelity: {1–5} — Did [COMMIT] reckon with dissenting branches, or ignore them?
Independence (pure mode only): {1–5} — Did later branches show conceptual anchoring to earlier ones?
T-tag discipline: {1–5} — Did T-tags force genuine sub-thought separation, or drift into blur?
Delta count: {N} — How many branches materially changed [COMMIT]?
Notes: {anything anomalous}
```

**Validity caveat:** Self-scoring has the same structural validity problem as Internal Double Crux — the moderator is also a party. This is a known class of problem, not a local hedge. Low scores are more informative than high scores because the failure mode is overconfidence, not underconfidence. A consistently high Divergence score with zero [DELTA] markers is a red flag, not a good result. Treat scores as diagnostic flags, not validity measures.
*Dated note, 2026-08-06:* this red flag is only checkable, not asserted, once the pre-branch seal exists — "zero [DELTA] markers" means nothing without a sealed, enumerated pre-branch text to check [COMMIT] against. See "Pre-Branch Seal — Mandatory — All Modes" above.

Honest self-reporting on T-tag discipline is the most diagnostic dimension. The failure mode — drifting back to blur under cognitive load — is most likely exactly when the sub-thought separation matters most.

---

## Example Invocations

- `"Branch this."` → Pure mode, 3 branches, full protocol.
- `"Frame before commit."` → Pure mode, 3 branches, full protocol.
- `"Branch this, directed: INSTINCT, ADVERSARIAL, NULL."` → Directed mode, specified types.
- `"What am I missing?"` → Pure mode, weight toward frames that contradict the apparent assumption. Include NULL by default.
- `"Steelman the other side."` → Directed lightweight: INSTINCT + STEELMAN-OPP + COMMIT.
- `"Run it from the actuarial frame."` → Directed: SOURCE:ACTUARIAL as B1, contrast implicitly present.
- `"Branch it with self-score."` → Pure mode, append [SELF-SCORE] after [COMMIT].
- `"1 pure then 4 orthogonal."` → Pure mode, 5 branches, first generates freely, remaining weight toward orthogonal frames.
- Ambiguous invocation → Stop. Ask: "Did you want to specify branch types (directed), or generate freely and label after (pure)?"

---

## Multi-Level FBC (Frames + Internal Branching)

**When to use:** The question is genuinely open about what the problem IS (not just how to solve it). Standard single-level FBC assumes one frame and generates branches within it. Multi-level FBC first generates N frames (what IS the problem?), then runs internal branching within each frame.

**When NOT to use:** If the frame is already known, use standard FBC. Multi-level is more expensive — reserve it for genuinely open design questions where the framing choice materially changes what counts as a solution.

---

### Structure

```
Level 1 (Frames): What IS the problem?
  Each frame is a complete, distinct assumption about the nature of the problem.
  Different frames imply different success criteria, different evidence that matters,
  different solutions that are even in scope.

Level 2 (Branches within each frame): How do we solve it?
  Within each frame, run internal branching using a specified structure.
  Recommended structure: 6 Thinking Hats (White/Red/Black/Yellow/Green/Blue).
  Each hat is a perspective, not a solution — they produce input to synthesis, not the synthesis itself.

Synthesis:
  Cold agent receives all frame outputs.
  Produces META + COMMIT across frames.
  Must not have seen individual agents' reasoning before synthesizing.
```

---

### Agent Brief Design for Frame Agents

**Source:** harness-creator Pattern A (Parallel Independent) — follow its isolation rules.

**Each frame agent receives:**
- The frame assumption (1-2 sentences: what IS the problem in this frame)
- The problem statement (same for all agents)
- The internal branch structure — definitions only (e.g., "White = facts/data, Red = gut/intuition, Black = risks, Yellow = upside, Green = creative alternatives, Blue = process/meta")
- Output contract (6 hat outputs, each 2-5 sentences unhedged, no reference to other agents)
- Optionally: the orchestrator's hypothesis for this frame as a single data point the agent can challenge

**What agents do NOT receive:**
- Pre-filled hat content
- Expected conclusions
- Analysis the orchestrator has already done on this frame

**Why this matters — the colonization problem:**
If you give agents the analysis you've already written for each hat, they reflect your thinking back rather than doing divergent reasoning. The prior analysis stays with the orchestrator as one perspective — one input the synthesis agent sees alongside the frame agents' outputs, not as a constraint on them.

---

### Frame Independence — Orchestrator's Judgment Call

Whether frames can run in parallel or must run sequentially is a meta-judgment call made by the orchestrator, not prescribed by the protocol. The orchestrator considers:

- **Independent:** Frame assumptions do not depend on each other's outputs → run in parallel
- **Dependent:** Frame B needs to know what Frame A found before it can explore meaningfully → run sequentially

Example from 2026-05-14 planning session:
- Frames 1-3 (Specification Quality, Task Taxonomy, Context Richness): parallel — independent assumptions
- Frame 4 (Self-Correction Infrastructure): after 1-2 — needs to know what tasks are trusted
- Frames 5-6 (Economics, Null): after 4 — parallel with each other
- Frame 7 (Future Proofing): last — synthesis frame, benefits from all prior frames

The orchestrator states this judgment explicitly in the harness design before spawning agents.

---

### Synthesis Agent Brief

The synthesis agent receives:
- All N frame agents' outputs (full text)
- The problem statement
- FBC META + COMMIT instructions (from the standard skill)
- Explicit instruction: "You are reading outputs from N independent agents. You did not write these. Write META as-if-external."

The synthesis agent does NOT receive:
- Individual agents' reasoning chains
- The orchestrator's prior analysis
- Frame-level hypothesis notes

---

### Output Contract for Frame Agents

```
Frame: [frame name / assumption in one line]
[Hat color — Hat name]:
[2-5 sentences, unhedged, no reference to other agents or other hats]
[repeat for all 6 hats]
```

---

## Relationship to Existing Protocol

This skill operates *within* a single response. Jon's multi-sample reasoning protocol operates *across* responses or sessions, and at the inter-model level when different models are used. They are complementary:

- **Frame-Before-Commit:** intra-response divergence, fast, lightweight scratchpad, benign failure state is implicit anchoring.
- **Multi-sample / inter-model protocol:** inter-response or inter-model divergence, used when branches need genuinely independent activation before being compared.

Do not substitute one for the other when execution independence matters. When both are run on the same question, treat convergence as strong confirmation and divergence as the primary signal.

---

## Supporting Document

Read `skills/frame-before-commit/references/GROUNDING.md` at the start of any cold session — i.e. any session without prior context on this protocol — before invoking the skill. *(Path repaired 2026-08-13. This line said `GROUNDING_UPDATED.md`, which exists nowhere; `session-order/SKILL.md:43` fixed the same dead name in its own conditional-reading table on 2026-07-26 and the pointer inside this file was missed.)*


---

## Extension v2: Autonomous Metacognitive Branching & Dual-Layer Grounding (Ratified in WAYFINDER-008, 2026-09-10)

### 1. Autonomous Self-Invocation Invariant
Jon does not manually invoke `/frame-before-commit` anymore. The agent MUST self-invoke this protocol before:
1. Committing to a major architecture or roadmap change.
2. Emitting any outward dispatch to `exchange/outbox/` targeting sibling trunks.
3. Making any negative assertion claiming that an artifact, message, or prior turn "does not exist."
4. Selecting between multi-model or tool execution paths when costs or token budgets are constrained.

### 2. Closing the May 2026 Verification Gap via Isolated Branching
As established in `wiki/concepts/fbc-verification-gap.md`:
- Intra-context branches are not independent; Branch 1 autoregressively conditions Branch 2.
- **v2 Resolution:** When true branch independence is required for critical decisions, dispatch separate subagents via `invoke_subagent` using `Workspace: 'branch'` (or `--fork-session -p` in CLI harnesses).
- Independent subagents execute with separate memory spaces and return only distilled findings to the coordinator.

### 3. Dual-Layer Grounding Gate (`[wire]` vs. `[corpus]`)
Before asserting facts about external state or prior turns:
- **Layer 1 (Physical Wire):** Verify exact byte arrival in primary logs (`history.jsonl`, `transcript.jsonl`) via `view_file` or `grep_search`.
- **Layer 2 (Corpus Index):** Verify discoverability in the GraphRAG SQLite index (`index.sqlite`).
- An absence in Layer 2 does NOT equal non-existence; it indicates an unindexed live-turn delta.

### 4. Frontmatter Thought Ontology (Replacing Emotional Self-Blame)
Agents must not engage in emotional self-deprecation ("I failed", "Caveman fell"). All friction must be structured as machine-readable frontmatter metadata:
```yaml
---
epistemic_layer: raw_wire_receipt | corpus_graph | volatile_context
verification_gate: two_sided_negative_control | primary_file_grep
independence_mode: isolated_subagent | kv_fork | intra_context
defect_classification: none | declarative_overconfidence | retrieval_blindness | temporal_lag
---
```
