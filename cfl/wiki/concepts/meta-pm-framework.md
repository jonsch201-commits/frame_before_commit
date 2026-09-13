---
title: Meta-PM Framework — Layer Taxonomy, Roll-Up Pipeline, and Build Plan
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (wiki); sub: wiki 4 vs skills 3 on authored labels"
type: concept
first_seen: meta-pm-layer-architecture-2026-06-27-a13169
source_count: 1
last_updated: 2026-06-29
---

## What This Is

The meta-PM framework is the architectural backbone of how Claude functions as a project manager across Jon's full life context. It defines a five-layer taxonomy of knowledge and work, a roll-up pipeline from conversation to concept, a three-stage system build plan, and twelve downstream sessions (DS-1–DS-12) required to make the system operational. Established in the June 27–28, 2026 design session.

## What the Wiki Says

### Layer Taxonomy (Canonical)

```
ROOTS       — permanent, non-managed (identity, values, core relationships)
  TRUNKS    — major life domains (T1–T4)
    BRANCHES  — projects and areas within each trunk
      FRUIT   — conversations (hang from branches, not a separate layer)
        SEEDS — conversations that spin off new trees (new branches or trunks)
```

Conversations are fruit hanging from branches. They are not a hierarchical layer. A branch holds many conversations. A conversation can produce a seed: a new project, branch, or even a new trunk. ([meta-pm-layer-architecture-2026-06-27-a13169:T229])

Roll-up is a pipeline alongside the hierarchy, not a sixth layer:
```
Conversation → source page → concept page → project state
```
Roll-up runs at the wiki level; it is how decisions and knowledge compound. ([meta-pm-layer-architecture-2026-06-27-a13169:T229])

### Meta-PM Three-Stage Build Plan

| Stage | Condition | Test |
|-------|-----------|------|
| Stage 1 | Layer taxonomy + domain maps documented | Jon can name everything from memory |
| Stage 2 | Wiki reflects the structure | index + concept pages match taxonomy |
| Stage 3 | project-manager skill operational | answers "what should I work on next?" |

Stage 1 complete as of the June 27–28 session (TRUNKS.md created, concept pages written). Stage 2 in progress (wiki updates required). Stage 3 pending PM skill maturation. ([meta-pm-layer-architecture-2026-06-27-a13169:T258])

### Jon Gates (JG-1 through JG-6)

Jon-gated decision points that must be resolved before the corresponding downstream work:

| Gate | Content | Status |
|------|---------|--------|
| JG-1 | Jon fills TRUNKS.md vision statements — what "winning" looks like in each trunk | **OPEN — primary blocker** |
| JG-2 | Soul/Self domain map (addressed by DS-4) | Open |
| JG-3 | Category recommendation: boughs for T4 (Infrastructure/Research/Skills+Protocol); flat for T1–T3 | Pre-answered by Claude, confirmed by Jon |
| JG-4 | Folder structure audit (addressed by DS-5) | Open |
| JG-5 | Thinking blocks protocol (addressed by DS-6) | Open |
| JG-6 | First PM operation to ship = `route-triage` | Pre-answered |

([meta-pm-layer-architecture-2026-06-27-a13169:T262])

### Downstream Sessions (DS-1 through DS-12)

| DS | Topic | Status |
|----|-------|--------|
| DS-1 | Jon fills TRUNKS.md vision statements (JG-1) | Open |
| DS-2 | wiki-master ingest of this session | Complete — this concept page |
| DS-3 | Wiki organization philosophy documented + tracker/projects.md revival | Open |
| DS-4 | Soul/Self domain map (JG-2) | Open |
| DS-5 | Folder structure audit (JG-4) | Open |
| DS-6 | Thinking blocks protocol (JG-5) | Open |
| DS-7 | CFL genealogy concept page | Open |
| DS-8 | PM skill expansion — all 4 trunks + Herald coordination + standards + coordination refs | **Complete** — commit `5a564c0` |
| DS-9 | session-order v2 — branch routing gate at cold open | Open |
| DS-10 | GBS field test — first ASOP session with GBS loaded | Open |
| DS-11 | test-master session — design tests for layer structure + PM skill | Open |
| DS-12 | First review + Draft 2 of meta-PM plan | Open |

DS-8b: Herald SKILL.md one-line update (change "FL project manager exists separately" to reflect new coordination protocol) — proposed, not yet executed.

### GBS Skill (ground-before-stating)

GBS v1 created at commit `4e551c9` during the meta-PM design session. Four files: SKILL.md (process-first architecture, 5 always-on rules, 3 labeling systems, loose/standard/strict modes), references/philosophies-and-grounding.md, references/worked-examples.md, references/sources.md. ([meta-pm-layer-architecture-2026-06-27-a13169:T274])

## Conflicts

None. This is the first formal concept page for this framework.

## Related

[[life-domains]], [[personal-role-architecture]], [[herald-of-home-and-life]], [[skills-system]], [[wiki-ingest-methodology]]
