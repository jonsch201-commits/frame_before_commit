# Frame-Before-Commit: Grounding Document

## What Problem This Solves

Human reasoning has a structural failure mode: System 1 — the fast, automatic process — pre-answers questions before deliberate reasoning engages. By the time you are consciously reasoning, you are typically defending a conclusion already reached, not forming one. Standard thinking produces one answer, usually the instinct answer, with post-hoc justification dressed as analysis.

The Frame-Before-Commit protocol addresses this by requiring serialized frame generation before any committed answer is produced. You cannot commit until you have generated content from multiple distinct epistemic stances. The frames are scratchpad — explicitly pre-committed — and the committed response is written only after inspecting what the non-instinct frames surfaced.

This is not brainstorming. Brainstorming generates options without a synthesis obligation. This protocol requires a [META] step that names what the non-instinct frames found that the instinct frame missed, and a [COMMIT] step that must explicitly reckon with any branch that raised a problem. The [META] + [COMMIT] structure is the differentiator. Methods like de Bono's Six Thinking Hats serialize thinking modes but provide no synthesis step. This protocol does.

---

## Why the Mechanics Work

**Directed labels recruit genuinely different information.** When you name a frame before generating content — ADVERSARIAL, NULL, SOURCE:ACTUARIAL — you are not merely relabeling the same output. Research on cognitive reappraisal (Wallace-Hadrill & Kamboj, 2016) shows that adopting a named epistemic stance introduces new information via semantic change. The label alters what gets recruited during generation, not just how it is presented.

**Branch length is a substantive constraint, not a formatting preference.** Short generation steps produce token gestures that fail to displace the instinct anchor. The 2–5 sentence floor exists because the "consider the opposite" debiasing technique (Kahneman, 2011) fails when the generation is too brief — the instinct answer survives regardless of the nominal frame.

**The ID-only reference rule is structural, not procedural.** In any system containing multiple partially-informed reasoning threads, the dominant thread will colonize later threads if permitted to speak inside them. Summarizing or paraphrasing an earlier branch inside a later one is not suppression — it is reproduction. The rule exists to prevent explicit colonization. Implicit anchoring remains possible and is acknowledged as the benign failure state.

---

## The Two Modes

Pure mode generates branches without pre-specified types. Labels are assigned after generation, at the explicit [LABEL ASSIGNMENT] step. This reveals what frames naturally emerged. Pure mode is the default when no types are named.

Directed mode pre-specifies branch types before generation begins. The label precedes and conditions the content. Any naming of branch types before generation begins triggers directed mode, regardless of phrasing. When the invocation is ambiguous, stop and ask before proceeding.

---

## Key Terms

A **run** is one full invocation of the protocol: all branches, [META], and [COMMIT]. Runs are the unit of comparison across sessions.

A **[DELTA]** marker in [COMMIT] records when a branch materially changed the committed answer. Zero deltas across repeated runs on the same question is the primary signal that the protocol is running as theater.

**Self-scoring** applies after [COMMIT] and covers divergence, meta specificity, commit fidelity, and independence. Scores are self-reported and have the same structural validity problem as any self-assessed introspection: the moderator is also a party. Low scores are more diagnostic than high scores. A high Divergence score paired with zero [DELTA] markers is a red flag.

---

## How to Use This Document

Read this document once at the start of any session where the Frame-Before-Commit protocol will be used and no prior context exists. Then read `skills/frame-before-commit/SKILL.md` for the full protocol format and discipline rules. This document establishes the conceptual grounding; `SKILL.md` governs execution.

Cold-session invocation: *"Read `skills/frame-before-commit/references/GROUNDING.md`, then `skills/frame-before-commit/SKILL.md`, then run the protocol on the following question."*

> **Paths repaired 2026-07-26.** Both pointers above named `FRAME-BEFORE-COMMIT.md`, and the invocation line named `frame-before-commit/GROUNDING.md`. Neither path existed: the protocol file was renamed to `SKILL.md` when skills moved to `skills/<name>/`, and this document now lives under `references/`. Anyone following the old invocation literally found nothing and had to guess.
