---
title: FBC Test Run 002 — True Null (No Invocation)
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/fbc-true-null-capacity/fbc-true-null-2026-04-15-b44ae8.md
project: Claude Foundational Layer
date_ingested: 2026-05-09
type: test-run
tags: fbc, test-run, true-null, spontaneous-invocation, delta
source_file_status: markdown-export (native-json-export; turn numbers = message sequence)
---

## Summary

Second FBC test run. True null condition — the same delta capability question was asked with no protocol invocation instruction. The model spontaneously self-invoked the protocol in directed mode (INSTINCT, ADVERSARIAL, NULL branches). 2 genuine deltas found. The self-invocation itself is a primary finding: the protocol has been internalized to the degree that it runs without explicit instruction.

## Key Claims

- True null condition: no invocation instruction given — same question as test-run-001 ([fbc-true-null-2026-04-15-b44ae8:T1])
- Model self-invoked the protocol spontaneously, running INSTINCT, ADVERSARIAL, NULL branches in directed mode ([fbc-true-null-2026-04-15-b44ae8:T2])
- 2 genuine deltas found under true null conditions ([fbc-true-null-2026-04-15-b44ae8:T2])
- The spontaneous self-invocation is itself an empirical finding — the protocol has been absorbed into model behavior without explicit trigger ([fbc-true-null-2026-04-15-b44ae8:T2])
- Note: this is NOT a clean null baseline — the model ran the protocol, so it cannot be used to compare "protocol vs. no protocol" delta rates ([fbc-true-null-2026-04-15-b44ae8:T2])

## Entities & Concepts

[[frame-before-commit]], [[fbc-self-scoring]]

## Conflicts

None.
