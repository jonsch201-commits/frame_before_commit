---
title: FBC Test — Directed 4-Branch Delta Capability Analysis
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/fbc-directed-4branch-delta-capability/fbc-4branch-2026-04-15-c6154b.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: Claude Foundational Layer
date_ingested: 2026-05-09
type: session
tags: fl, fbc, test-run, directed, 4-branch, delta-capability
---

## Summary

Directed FBC run with 4 branches (8K chars, 2026-04-15). Branches: AS-IS, NO-BACKGROUND, NO-GROUNDING, ORTHOGONAL (model-chosen). Question: "Is the Frame-Before-Commit protocol, as currently written, structurally capable of producing a genuine delta?" 2 genuine deltas. Self-scores: Divergence 4, Meta 4, Fidelity 5, Independence 3. The original claude.ai URL returns 404; this native JSON export is the only complete record. Known from MANIFEST.md as the 4-branch directed run.

## Key Claims

- Delta 1 — B3 (NO-GROUNDING): introduced "benign failure mode as pre-accommodation" framing — changed commit toward a stronger claim about what protocol failure looks like. Without B3, commit would have treated zero-delta as ambiguous. With B3, commit recognized zero-delta as evidence of pre-accommodation. ([fbc-4branch-delta-2026-04-15-c6154b:T2])
- Delta 2 — B4 (ORTHOGONAL): named multi-sample protocol as the mechanism that would close the verification gap (can't verify branch independence from within a single run; requires cross-run comparison). ([fbc-4branch-delta-2026-04-15-c6154b:T2])
- Independence score 3: some cross-branch anchoring noted; AS-IS likely influenced later branches despite ID-only rule. ([fbc-4branch-delta-2026-04-15-c6154b:T2])
- "404 session": original claude.ai URL returns page not found — confirmed deleted from claude.ai. Native JSON export is the authoritative source. ([fbc-4branch-delta-2026-04-15-c6154b:T1])

## Entities & Concepts

[[frame-before-commit]]

## Conflicts

None — this is a distinct session from the other FBC test runs (test-run-001/002/003 in wiki/sources/). This was also run on 2026-04-15.