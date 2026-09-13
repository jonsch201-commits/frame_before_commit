---
title: Meta-PM Layer Architecture — Layer Taxonomy, Four Trunks, and PM System Design (2026-06-27)
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 6 vs skills 2 on authored labels"
source_file: raw/transcripts/claude-code/fl/code-2026-06-27-a13169-plan-wiki-update-process-for-new-content-zip.md
source_file_status: repaired 2026-07-19 — stale slug; re-resolved by uuid6 (slugs drift when session titles change, uuid6 does not)
date_ingested: 2026-06-29
type: session
tags: meta-pm, layer-taxonomy, life-domains, project-manager, herald, skills, GBS, trunks
---

## Summary

A long two-phase session (June 27–28, 2026) that began as a wiki-update planning request and evolved, in its second half, into the canonical design of the meta-PM layer architecture for the Claude Foundational Layer. Jon confirmed a five-layer taxonomy (Roots → Trunks → Branches → Fruit → Seeds), named four life-domain trunks, resolved the Herald/PM relationship, defined a three-stage meta-PM build plan with six Jon-gated decision points, and initiated twelve downstream sessions (DS-1–DS-12). Two skills shipped during the session: GBS (ground-before-stating) v1 and PM skill expansion to all-trunk scope.

## Key Claims

- **The session has two distinct phases.** Phase 1 (turns 1–~223, June 27 18:12 UTC) covers wiki-update planning, the 7-phase update protocol design, and wiki-master execution. Phase 2 (turns ~223–278, June 28 19:23–June 29 04:12 UTC) covers the meta-PM architecture design. Two compaction events occurred during the session. ([a13169:T223])

- **Layer taxonomy (canonical, Jon-confirmed): Roots → Trunks → Branches → Fruit → Seeds.** Roll-up (Conversation → source page → concept page → project state) is a pipeline that runs alongside the hierarchy, not a sixth layer. ([a13169:T229])

- **Jon corrected "conversations" framing explicitly.** Conversations are fruit hanging from branches, not a layer. Jon's words: "CONVERSATIONS — fruit, not a layer. ← Your correction, and it's right. Conversations hang from branches." ([a13169:T229])

- **Seeds = conversations that spin off new trees.** Jon: "A conversation can produce a seed: a new project, new branch, or even a new trunk that starts its own tree." ([a13169:T229])

- **Four trunks confirmed (canonical):** T1 Personal/Family, T2 Professional, T3 Home, T4 Intellectual/Build. Trunks correspond to Claude project domains and sub-wikis. ([a13169:T243])

- **"How to Learn Claude" is the origin of CFL.** Jon: "how to learn claude is the origin of the CFL and we don't use it anymore." Session encodes: "The 'how to learn Claude' project seeded the CFL." ([a13169:T229])

- **The four personal roles (Soul/Guide/XC/Herald) are NOT trunks.** Roles are invocation patterns; trunks are life management domains. Roles and trunks are orthogonal systems. ([a13169:T229])

- **Meta-PM three-stage build plan:** Stage 1: Layer taxonomy documented (Jon can name everything from memory). Stage 2: Wiki reflects the structure (index + concept pages match taxonomy). Stage 3: project-manager skill operational (answers "what should I work on next?"). ([a13169:T258])

- **Six Jon Gates (JG-1–JG-6) govern the build plan.** JG-1: Jon fills TRUNKS.md vision statements (primary blocker). JG-3: Category recommendation confirmed (boughs for T4 Infrastructure/Research/Skills+Protocol; flat for T1–T3). JG-6: First PM operation = `route-triage`. JG-2, JG-4, JG-5 map to DS-4, DS-5, DS-6 respectively. ([a13169:T262])

- **Herald/PM relationship resolved.** Herald = T1 operational (Lift archetype, session-open protocol, Soul/Guide/XC routing). PM = all-trunk strategic (cross-trunk coordination, route-triage). Herald's session open IS PM's T1 operational mode; PM does not re-run T1 status when Herald is active. Co-load pattern: `/project-manager` + `/herald` together when T1 and T4 interact. ([a13169:T254])

- **T-A triage item resolved.** T-A ("Branches outside Claude's scope") was resolved: PM formally owns PM responsibility for every branch across all trunks, including ones Jon executes. Herald implements within T1. For T2 and T3, PM handles directly. ([a13169:T265])

- **GBS (ground-before-stating) skill v1 created** at commit `4e551c9`. Four files: SKILL.md (process-first architecture, 5 always-on rules, 3 labeling systems, loose/standard/strict modes), references/philosophies-and-grounding.md (P1/P2/P3), references/worked-examples.md (E1–E6), references/sources.md. ([a13169:T274])

- **PM skill expanded all-trunk** at commit `5a564c0` (DS-8, background subagent). SKILL.md rewrite: 9 total operations, two modes (meta-PM + operational), trunk scope map, Herald coordination. New files: references/standards.md, references/coordination.md. Herald SKILL.md update (DS-8b) pending. ([a13169:T271])

- **DS-1 through DS-12 downstream sessions defined.** DS-8 is the only one completed in this session. ([a13169:T262])

## Entities & Concepts

[[meta-pm-framework]], [[life-domains]], [[personal-role-architecture]], [[herald-of-home-and-life]], [[skills-system]], [[wiki-ingest-methodology]]

## Conflicts

None known. This session establishes canonical definitions that supersede prior informal references to "trunks" and "branches."

## Uncaptured Content

a) Phase 1 wiki-master operational work (7-phase update planning, GBS design, wiki-master execution) is captured through commit outputs and the skip-registry, not through Key Claims here. That content is operational and lives in the wiki structure it created.

b) DS-2 through DS-12 details are brief topic labels. Each downstream session will produce its own source page when executed. DS-8 already has implicit coverage in the PM skill commit (5a564c0).

c) The session contains two compaction events that reset context. The compaction summaries at lines ~7390 and ~7978 are the canonical record of Phase 1 work as understood by the agent at Phase 2 start.

d) Herald SKILL.md DS-8b update (changing "FL project manager exists separately" to reflect the new coordination protocol) was proposed but not yet executed as of session end. This is a known open item.
