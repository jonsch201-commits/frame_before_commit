---
title: Session Order Skill Document
trunk: fl
branch: [reference]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-REF; sub: branch `reference` has no registered sub-branches"
source_file: none  # skill file moved to skills/ directory
project: Claude Foundational Layer
date_ingested: 2026-05-12
type: note
tags: session-order, skills, cold-session, triage
source_file_status: static-reference (raw/references/ document; not a session)
---

## Summary

The Session Order Skill document as stored in the CFL project (created 2026-04-29). Governs cold session open behavior: mandatory reading order, conditional reading (load FBC files only when needed), topic check before engaging substantively, session map format, HELD vs. Triage distinction, multi-topic message handling, and session close ritual. The HELD/Triage distinction is emphasized as critical — they are not interchangeable and conflating them loses items or creates false closure.

## Key Claims

- **Mandatory reading order (cold session):** README.md → WORKING_CONTEXT.md → SESSION-ORDER-SKILL.md → TEMPORAL-CONTEXT-SKILL.md. Do not skip. Do not reorder.
- **Conditional reading (not every session):** GROUNDING_UPDATED.md and FRAME-BEFORE-COMMIT.md only when FBC will be invoked; BACKGROUND.md only when domain knowledge is directly relevant. Loading conditional files preemptively creates context overhead with no benefit.
- **Topic check rule:** Before engaging substantively, can Jon state his topic in one line? If no: redirect with "Before we go further — what's the one thing you need from this session?" If Jon cannot answer, this is a triage session until a topic is named.
- **HELD vs. Triage — the critical distinction:** HELD = parked within current session, Claude retains responsibility, will return before close. Triage = handed off, session responsibility ends. Default to HELD when unclear — HELD is safer. Do not triage without Jon confirming the handoff.
- **Session close ritual:** (1) State open HELD items, (2) flag items to move from HELD to Triage and ask Jon to confirm each, (3) flag whether wiki needs update, (4) confirm next session's starting point if known. Do not skip if HELD items exist.
- **Multi-topic message rule:** Identify most load-bearing topic first, state the map, get confirmation before proceeding. Jon controls session order; Claude suggests.

## Entities & Concepts

[[skills-system]], [[design-execution-split]]

## Conflicts

None. Source document for the session-order skill; consistent with skills-system concept page.