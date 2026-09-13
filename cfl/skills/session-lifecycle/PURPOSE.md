---
format: cfl-purpose/v1
skill: session-lifecycle
motivating_pattern: UNKNOWN
origin_evidence: pre-gate (before 2026-08-31)
first_accepted: pre-gate
validation_split: none
r_best: UNKNOWN
declared_tier: UNKNOWN
generated_by: lane W-2 (sonnet) session e515d858
---

## Why this skill exists

Handles session re-open, mid-session status checks, and project status on demand -- deliberately load-on-demand rather than ambient, to keep session-order lean at every cold open [SKILL.md's own stated purpose]. No pattern page names it.

## What would retire it

Status queries are answerable directly from wiki/tracker/ without a dedicated protocol layer mediating the read.
