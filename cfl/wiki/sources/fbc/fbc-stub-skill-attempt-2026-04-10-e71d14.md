---
title: FBC Skill Invocation Attempt — "Directed Mode" Session (Stub)
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-04-10-e71d14-global-suffering-across-diverse-perspectives.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-20
type: session
tags: how-to-use-claude, fbc, stub, skill-invocation
---

## Summary

Stub session (1.5K chars, 2026-04-10). Jon asked Claude to apply "the skill we just created" in directed mode to generate diverse global suffering perspectives. Claude paused — the referenced skill was not present in the context window and it could not identify which skill was meant. Session ended without execution. Preserves as evidence of an early directed-mode skill invocation attempt and the context-loss problem when skills aren't in context.

## Key Claims

- **Skill context-loss**: When a skill is referenced by implication ("the skill we just created") rather than loaded explicitly, the model cannot reconstruct it. Skills must be present in context window to be applied. ([fbc-stub-skill-attempt-2026-04-10-e71d14:T1])
- **Directed mode requires explicit skill definition**: Calling "directed mode" without the skill file loaded produces a halt, not improvisation — which is the correct behavior. ([fbc-stub-skill-attempt-2026-04-10-e71d14:T2])

## Entities & Concepts

[[frame-before-commit]]

## Conflicts

None.