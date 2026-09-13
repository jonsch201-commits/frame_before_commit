---
title: PM + Herald skill state
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-AGENTMEM; sub: fleet 4 vs skills 3 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_pm-herald-skill-state.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, project-manager, herald]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: pm-herald-skill-state
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# PM + Herald skill state

*Source description:* Current state of project-manager and herald skills as of 2026-06-28. PM is v1 (all-trunk). Herald unchanged; DS-8b pending to update Herald/PM coordination language.

# PM and Herald Skill State (as of 2026-06-28)

## What exists

**skills/project-manager/SKILL.md** — v1, committed 5a564c0. Expanded to all four trunks. Two modes (Operational / Meta-PM, inferred from question type). 9 operations: status, open-item, close-item, session-brief (existing 4) + open, what-next, route-triage, branch-state, update-tracker (5 new). Reads 8 sources including references/TRUNKS.md as the master map.

**skills/project-manager/references/standards.md** — New file. Defines: Well-Managed Branch, Completed Project (DONE vs. CLOSED distinction), Well-Structured Session, Skill-Update Project Loop, Herald Standard for T1, projects.md schema.

**skills/project-manager/references/coordination.md** — New file. Protocol-style. Covers all 6 role relationships including PM↔Herald, PM↔wiki-master, PM↔skills-master, PM↔test-master, PM↔triage-master, PM↔session-order.

**skills/herald/SKILL.md** — Unchanged from earlier version. Still says "An FL project manager exists separately for FL project work." This is outdated — DS-8b pending.

## The gap remaining (DS-8b)

Herald's Role Identity section doesn't reflect the PM relationship defined in DS-8. Needs:
1. Update "Herald IS NOT" line — reflect the coordination relationship
2. Add paragraph: "Herald implements PM standards within Trunk 1. Herald's session open IS PM's T1 operational mode. Cross-trunk items route Herald → PM via T-item."
3. Standing Decisions row: DS-8 relationship, 2026-06-28

Intake proposal described in session a13169e1. Write to skills/intake/ when ready to execute DS-8b.

## Skill co-invocation pattern (confirmed 2026-06-28)

When T1 (Personal/Family) and T4 (Intellectual/Build) meaningfully interact in a session, Jon loads both `/project-manager` and `/herald`. PM holds cross-trunk picture; Herald handles T1 operational depth. PM does not re-run T1 ops when Herald is active. This pattern is not yet explicitly named in either SKILL.md — add to DS-8b scope.

## Threshold decisions pending

PM standards.md has 8-week idle-to-CLOSED and 30-day CLOSED retention rules. Jon asked to remove date-based thresholds. Replacement: PM flags staleness when context activates it, not on a timer. Needs small skills-master update to standards.md and SKILL.md.

## How to apply

When launching DS-8b skills-master session: brief it with the three Herald changes above + co-invocation pattern + threshold removal. All in one session. Herald reads skills/herald/SKILL.md first; it is well-developed and changes must preserve existing content.
