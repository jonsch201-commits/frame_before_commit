---
format: cfl-purpose/v1
skill: transcript-parser
motivating_pattern: UNKNOWN
origin_evidence: pre-gate (before 2026-08-31)
first_accepted: pre-gate
validation_split: none
r_best: UNKNOWN
declared_tier: UNKNOWN
generated_by: lane W-2 (sonnet) session e515d858
---

## Why this skill exists

Wraps `convert-export.py` (ratified 2026-07-21 as the one extractor) to turn a claude.ai export zip into the incremental mirror corpus that fable-mirror reads, diffing on (uuid, updated_at) so only new/changed conversations re-parse [SKILL.md's own stated purpose]. No pattern page names it.

## What would retire it

claude.ai ships a live/API-driven export, removing the manual download-a-zip step this incremental pipeline is built around.
