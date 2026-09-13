---
format: cfl-purpose/v1
skill: memory-core
motivating_pattern: UNKNOWN
origin_evidence: pre-gate (before 2026-08-31)
first_accepted: pre-gate
validation_split: none
r_best: UNKNOWN
declared_tier: UNKNOWN
generated_by: lane W-2 (sonnet) session e515d858
---

## Why this skill exists

Barrier-write discipline writing durable, addressable records at the four points session state would otherwise be lost: compact, close, branch-dispatch, and fold-in [SKILL.md's own stated purpose]. No pattern page names it.

## What would retire it

The harness itself persists session state across these four boundaries natively, without a skill-level write discipline mediating it.
