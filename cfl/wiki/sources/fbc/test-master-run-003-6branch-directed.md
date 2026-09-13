---
title: FBC Test Run 003 — Directed Mode, 6 Branches
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/fbc-directed-6branch-delta-detection/fbc-6branch-2026-04-15-a11a71.md
project: Claude Foundational Layer
date_ingested: 2026-05-09
type: test-run
tags: fbc, test-run, directed-mode, b4-b5-finding, delta
source_file_status: markdown-export (native-json-export; turn numbers = message sequence)
---

## Summary

Third FBC test run. Directed mode, 6 branches (B1 AS-IS, B2 NO-BACKGROUND, B3 NO-GROUNDING, B4 NO-WORKING-CONTEXT, B5 STRUCTURAL-BIAS, B6 orthogonal frame of model's choice). 2 genuine deltas from B4 and B5. This is the primary empirical evidence that directed reframes with orthogonal instructions recruit genuinely different information.

## Key Claims

- B4 (NO-WORKING-CONTEXT): removing working context revealed a verification gap in the protocol — the protocol cannot verify that branches are actually independent without cross-session comparison ([fbc-6branch-2026-04-15-a11a71:T2])
- B5 (STRUCTURAL-BIAS): found that the protocol has a non-falsifiability problem — a run that produces zero deltas is labeled a "failure mode" by the protocol's own scoring, making it impossible to use zero-delta results as evidence against the protocol ([fbc-6branch-2026-04-15-a11a71:T2])
- B4 and B5 produced distinct problems from genuinely distinct frames — primary empirical evidence that directed reframes recruit different information ([fbc-6branch-2026-04-15-a11a71:T2])
- 2 genuine deltas found ([fbc-6branch-2026-04-15-a11a71:T2])
- Implication: the multi-sample protocol (cross-session comparison) is the mechanism that would close the verification gap B4 identified ([from MANIFEST.md, c6154b session notes])

## Entities & Concepts

[[frame-before-commit]], [[fbc-self-scoring]], [[fbc-verification-gap]]

## Conflicts

None.
