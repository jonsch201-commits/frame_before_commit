---
format: cfl-purpose/v1
skill: fbc-test-reporter
motivating_pattern: UNKNOWN
origin_evidence: pre-gate (before 2026-08-31)
first_accepted: pre-gate
validation_split: none
r_best: UNKNOWN
declared_tier: UNKNOWN
generated_by: lane W-2 (sonnet) session e515d858
---

## Why this skill exists

Formats raw FBC protocol run output into a standardized record for test-master's cross-condition comparison and scoring; it structures runs, it does not execute them [SKILL.md's own stated purpose]. No pattern page names it.

## What would retire it

Test-master's scoring pipeline consumes raw run output directly, removing the need for a separate formatting step between run and score.
