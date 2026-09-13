---
title: Stylomantic Decoding Layer — Documentation Gaps and Hierarchy Interactions
trunk: fl
branch: [stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-STYLO; sub: branch `stylomantic` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-04-10-e1c10c-stylomantic-decoding-layer-documentation-gaps.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, stylomantic, documentation, hierarchical-models
---

## Summary

Short session (5.2K chars, 2026-04-10). Jon ran into collisions and incorrect conclusions from Claude Code — traced to a documentation ambiguity about how hierarchies should interact in the model. Session catalogs six distinct ways the three structural hierarchies could interact, ordered by defensibility.

## Key Claims

- Three structural hierarchies in the Stylomantic model: (1) credibility hierarchy (Bühlmann-Straub) — channel-level vs. global parameter pooling; (2) token position hierarchy — position within a message; (3) logprob rank hierarchy — rank 1–20 within the top-20 window plus the "Other" bucket. ([stylomantic-doc-gaps-2026-04-10-e1c10c:T2])
- Six interaction options ordered by defensibility: (1) Channel credibility weights modulate a shared global adjustment vector — the actuarially clean version, Bühlmann-Straub as intended; (2) Channel membership as a standard covariate in per-token adjustment model — simpler, no hierarchical pooling; (3) Channel credibility × token rank interaction; (4) Position within message × channel; (5) Logprob value (not just rank) × channel; (6) Temporal credibility — within-channel drift interacts with pooling. Options 3–6 require progressively more data to identify. ([stylomantic-doc-gaps-2026-04-10-e1c10c:T2])
- Root cause of Claude Code collisions: design doc said "channel covariate: required" without specifying which of options 1, 2, or 3. Claude Code either guessed or received in-session instruction that didn't make it into CLAUDE.md. Documentation ambiguity is upstream of implementation error. ([stylomantic-doc-gaps-2026-04-10-e1c10c:T2])

## Entities & Concepts

[[stylomantic]]

## Conflicts

None.