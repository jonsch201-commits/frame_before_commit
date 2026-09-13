---
title: CFL Early Setup — Wiki Infrastructure and Skill Initialization
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 4 vs skills 3 on authored labels"
source_file: raw/transcripts/claude-code/_routing/incoming/code-2026-05-01-000a36-claude-code-session-000a36.md
project: Claude Foundational Layer
date_ingested: 2026-05-11
type: session
tags: wiki-master, skills-system, initialization, infrastructure, claude-code
source_file_status: OK
---

## Summary

Earliest captured Claude Code FL session (.jsonl format). Jon initialized a fresh Claude Code instance by providing claude.ai project context (skills, grounding docs) and directing wiki infrastructure creation. Key outputs: wiki-master skill initialized with 7 canonical operations, SESSION-ORDER-SKILL chain established, sync-universal.sh scaffolded for syncing skill files from repo to ~/.claude. This session is the architectural origin of the Claude Code FL setup.

## Key Claims

- **Wiki-master initialized with 7 operations:** init, add, ingest, add-and-ingest, query, lint, intake-review — these became the canonical operation set; intake-review was later formalized in f9cdf4 but appears here as an early defined operation ([UNCERTAIN-cfl-early-setup-2026-05-01-000a36:T38])
- **SESSION-ORDER-SKILL chain:** Instructions field → README → SESSION-ORDER-SKILL.md → conditional/reference files; adding one line to SESSION-ORDER-SKILL.md makes any repo skill effectively guaranteed-available for every session — the critical-vs-reference tier architecture ([UNCERTAIN-cfl-early-setup-2026-05-01-000a36:T38])
- **sync-universal.sh:** Script scaffolded for syncing skill files from the repo to ~/.claude where Claude Code reads them; rsync not available in Git Bash on Windows — required workaround ([UNCERTAIN-cfl-early-setup-2026-05-01-000a36:T38])
- **Cold-start problem identified:** A fresh Claude Code instance has no project context from claude.ai; the workaround is Jon providing skills and grounding docs directly in session; SESSION-ORDER-SKILL is the structural fix for this cold-start gap ([UNCERTAIN-cfl-early-setup-2026-05-01-000a36:T2])
- **CLAUDE.md stacking:** User-level (~/) CLAUDE.md applies globally; repo-level (project) CLAUDE.md applies to that project; both read at session start — skill files become ambient without being in the system prompt itself (synthesized from session context — not stated explicitly in raw turns)
- **Wiki infrastructure created:** SCHEMA.md, wiki/index.md, wiki/log.md, wiki/overview.md, and subdirectories (sources/, concepts/, entities/, analyses/, tracker/) established this session ([UNCERTAIN-cfl-early-setup-2026-05-01-000a36:T27])

## Entities & Concepts

## Conflicts

None.

## Uncaptured Content

a) Full session (41 turns) contains extensive wiki structure creation detail, tracker file seeding, and session-order skill update — not captured in Key Claims as mechanical rather than architectural.
b) Stylomantic origin story was flagged as needed (OI-004) but not obtained in this session — dissolved as "hold for Jon's input."
c) 6 open items carried forward (OI-004 through OI-009) including giant session ingest strategy and role context folder design — threads not followed in this session; tracked in tracker/open-items.md.
