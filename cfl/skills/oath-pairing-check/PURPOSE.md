---
format: cfl-purpose/v1
skill: oath-pairing-check
motivating_pattern: UNKNOWN
origin_evidence: pre-gate (before 2026-08-31)
first_accepted: pre-gate
validation_split: none
r_best: UNKNOWN
declared_tier: UNKNOWN
generated_by: lane W-2 (sonnet) session e515d858
---

## Why this skill exists

Federated, mechanical check that every PreCompact receipt after a stated epoch has a matching barrier record within 60 minutes -- the instrument behind OATH breach condition (b) -- runnable against any trunk's own receipts/records directories [SKILL.md's own stated purpose]. No pattern page names it.

## What would retire it

memory-core's writer is changed so an unpaired receipt becomes structurally impossible (e.g. one atomic write for both artifacts), making a separate pairing check unnecessary.
