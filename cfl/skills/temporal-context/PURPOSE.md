---
format: cfl-purpose/v1
skill: temporal-context
motivating_pattern: UNKNOWN
origin_evidence: pre-gate (before 2026-08-31)
first_accepted: pre-gate
validation_split: none
r_best: UNKNOWN
declared_tier: UNKNOWN
generated_by: lane W-2 (sonnet) session e515d858
---

## Why this skill exists

Fires on every response to stamp measured wall-clock time and inform interpretation of Jon's state and decision staleness; corrected 2026-08-05 after a Personal-trunk finding showed both projects extrapolating a stale `date` call and mislabeling it `[measured]` [SKILL.md's own stated purpose and revision history]. No pattern page names it.

## What would retire it

The harness stamps measured wall-clock time on every turn natively, removing the need for a skill-level reminder to call `date` again.
