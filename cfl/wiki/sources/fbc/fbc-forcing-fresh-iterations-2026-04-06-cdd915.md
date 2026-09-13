---
title: Forcing Fresh Problem-Solving Iterations — FBC Precursor, Perspective Generation, PII Gate
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-04-06-cdd915-forcing-fresh-problem-solving-iterations-and-compa.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, fbc-precursor, stylomantic, research-ideas, design
---

## Summary

Session from 2026-04-06 — four days before FBC was formally named in 6ed205. Jon asked how to force Claude to consider a problem fresh multiple times, compare results, and choose among them — the informal multi-sample approach that was documented in CLAUDE.md from this session and later formalized as Frame-Before-Commit. Session also contains two named research and design ideas: Perspective Generation via Labeled Distribution Sampling and a Local PII Gate for selective external transmission.

## Key Claims

- **FBC precursor**: Jon's question — "how can I force you to consider a problem fresh multiple times, and then have you examine your results for differences and have you choose one?" — is the originating request that the FBC protocol answers. This session documented the informal approach; 6ed205 named and formalized it. ([fbc-forcing-fresh-iterations-2026-04-06-cdd915:T1])
- **KV cache branching unavailability**: Anthropic does not expose user-controlled KV cache branching. Implementing it would require separate inference runs per branch, which is computationally expensive. The architectural limitation is real, not a policy choice. This is why FBC must be prompt-level rather than inference-level. ([fbc-forcing-fresh-iterations-2026-04-06-cdd915:T4])
- **Perspective Generation via Labeled Distribution Sampling** [RESEARCH]: "At key decision points, rather than sampling one completion, characterize the *shape* of the output distribution — particularly the tail — along qualitative dimensions. Use those dimension labels to intentionally sample across perspective-space, then feed all sampled chains plus their labels into a fresh synthesis context." Extends the multi-sample idea toward explicit distribution characterization. Ideas log entry written in-session. ([fbc-forcing-fresh-iterations-2026-04-06-cdd915:T16])
- **Local PII Gate** [DESIGN]: Two-stage local classifier before any external transmission. First stage detects PII class; second stage decides transmission eligibility. Motivated by Stylomantic's requirement to transmit personal signals externally — the gate ensures only safe signals leave the local context. ([fbc-forcing-fresh-iterations-2026-04-06-cdd915:T22])

## Entities & Concepts

[[frame-before-commit]], [[stylomantic]]

## Conflicts

None.