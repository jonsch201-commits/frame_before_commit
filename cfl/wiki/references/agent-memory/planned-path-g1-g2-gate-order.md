---
title: Planned path — G1 gates G2
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_planned-path-g1-g2-gate-order.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, gate-order, roadmap]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: planned-path-g1-g2-gate-order
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Planned path — G1 gates G2

*Source description:* The CFL roadmap's planned path (44a95b, 2026-07-17, corpus-grounded via fable-mirror): G1 wiki-stabilization GATES G2 skills-hardening — wiki-first, skills-first explicitly REJECTED. Plus the 'coordinator-might-miss' items invisible in the stale trackers.

The planned path for skill + wiki improvements, corpus-grounded (fable-mirror on Opus, 2026-07-24, from roadmap `chat-2026-07-17-44a95b`). Use this to ground next-steps — the current trackers are too stale to show it.

**Gate order is load-bearing: G1 (wiki-stabilization) → G2 (skills-hardening). Wiki-first.** Skills-first was *considered and explicitly rejected*: "skills cite the wiki; hardening behavior against unstable ground truth just reifies the instability." **Proposing skills-hardening ahead of wiki-stabilization reverses a decided-in-session ordering** — don't.

**G1 wiki checklist (priority order):** (a) dedup / single-canonical-copy-per-page enforcement; (b) **tracker refresh, esp. `skills.md`** — a stale skills.md silently breaks the session-open staleness check; (c) **words-reify concept page** (the single most-repeated unmet wiki item — named as BOTH an L0-anchor gap AND a G1 blocker; still absent); (d) goals-file resolution (verbatim excerpting of the oversight-paper commitments — paraphrase forbidden); (e) personal-index count drift; (f) session-open connector-syntax bug.

**G2 skills frame:** skills = "self-modifying weights," each revision evaluated on 5 axes (trigger reliability · executor-tier adherence · safe degradation unobserved · provenance-tagged claims · **eval coverage = goal-cardinality ≤ eval-cardinality**). **temporal-context + session-order have ZERO test runs despite gating every session = the top eval-coverage gap** (trackers hide it — they show these skills "operating"). Also pending: GBS-for-Sonnet + minimal-pair evals; decision-record enforcement. Invariant that stays human even post-docker: *agent proposes diff → eval → decision record → Jon commits.* **CORRECTION (2026-07-24, verified in-tree):** Pocock `/teach` (T-87) is **DONE, not pending** — `skills/teach-me/SKILL.md` is a hard fork of mattpocock `productivity/teach`, adopted 2026-05-22, production. The corpus triage list still carries T-87 as open = corpus staleness; **wiki wins.** Lesson: verify the mirror's `UNVERIFIABLE`-flagged items against the wiki before propagating them as "remaining" — I mis-listed this as pending off the mirror's under-verified first read.

**Coordinator-might-miss (invisible in stale trackers):** words-reify absence · temporal/session-order zero-eval gap · skills.md refreshed-but-stale · the wiki-first ordering itself · **moral-hierarchy is captured (`intake-triage/triage-capture-2026-07-15-...`) but NOT promoted — Jon asked to be REMINDED to discuss it at the Week-4/planning session** · goals-file verbatim constraint.

**Destination caveat:** "review-and-decide, not more files" IS corpus-grounded (7f2815, 2026-07-10). But the mirror could NOT find an **08-01 date attached to a skills/wiki destination** anywhere in the corpus — flagged UNVERIFIABLE-FROM-CORPUS. If the 08-01 bar for these two surfaces is real it lives in the coordination layer, not the records — route to claude.ai to confirm; do not let the mirror be its source. See [[deploy-phase-operating-protocol]], [[active-work-state]].
