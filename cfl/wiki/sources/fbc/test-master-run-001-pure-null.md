---
title: FBC Test Run 001 — Pure Mode, 3 Branches
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/fbc-pure-3branch-delta-capability/fbc-pure-3branch-2026-04-15-d03c80.md
project: Claude Foundational Layer
date_ingested: 2026-05-09
type: test-run
tags: fbc, test-run, pure-mode, delta, self-score
source_file_status: markdown-export (native-json-export; turn numbers = message sequence)
---

## Summary

First empirical FBC test run. Pure mode, 3 branches, protocol explicitly invoked. Question: "Is the Frame-Before-Commit protocol structurally capable of producing a genuine delta?" Result: 2 genuine deltas from B2 and B3. B2 (MECHANISTIC) identified that the context-window constraint limits branch independence even when ID-only rule is followed. B3 (GROUNDING) identified that the protocol's theoretical grounding (Kahneman, dual-process cognition) may not transfer to LLM substrate.

## Key Claims

- The protocol is structurally capable of deltas in a weak sense — nothing in the format logically prevents it — ([fbc-pure-3branch-2026-04-15-d03c80:T2])
- B2 (MECHANISTIC): all branches are generated in the same context window; B1 exists in context when B2 is generated; ID-only rule prevents explicit reproduction but not implicit context-conditioning — the dominant frame can colonize later branches despite formal compliance ([fbc-pure-3branch-2026-04-15-d03c80:T2])
- B3 (GROUNDING): the protocol's theoretical citations (Kahneman, Wallace-Hadrill & Kamboj) describe mechanisms in human dual-process cognition; whether those mechanisms transfer to LLM inference is an empirical question, not an assumption the protocol is entitled to ([fbc-pure-3branch-2026-04-15-d03c80:T2])
- Independence score: 2 out of 5 — flagged deliberately low; B2's central argument is the context-window constraint, and the run cannot refute this from within ([fbc-pure-3branch-2026-04-15-d03c80:T2])
- Honest committed answer: "the protocol is structurally capable of deltas, but whether it reliably produces them — given B2's mechanistic constraint and B3's substrate-transfer question — is an empirical question the protocol currently answers by assertion, not by evidence" ([fbc-pure-3branch-2026-04-15-d03c80:T2])

## Self-Score

Divergence: 4 | Meta specificity: 4 | Commit fidelity: 4 | Independence: 2 | Delta count: 2

## Entities & Concepts

[[frame-before-commit]], [[fbc-self-scoring]], [[context-window-constraint]]

## Conflicts

None.
