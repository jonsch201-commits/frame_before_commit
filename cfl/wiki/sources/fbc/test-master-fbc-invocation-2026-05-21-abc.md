---
title: FBC Invocation Variable — Conditions A/B/C Baseline (01-FBC-001)
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: research/01-FBC-Improvement/harness/condition-A-2026-05-21.md
project: Claude Foundational Layer
date_ingested: 2026-05-22
type: test-run
tags: FBC, 01-FBC-Improvement, invocation, verification-gap, baseline
source_file_status: test-run (structured test output; citation format not applicable)
---

## Summary

Three-condition test isolating the invocation variable in FBC execution. Key finding: the invocation instruction — not the protocol text — is what triggers protocol execution. A secondary convergent finding emerged independently across two conditions: the verification gap is deeper than context colonization; DELTA markers are generated inside the influence of the branch being claimed as verified.

## Key Claims

- Invocation instruction is the execution trigger — Condition B (full protocol text, no invocation) produced a direct analytical answer, not a protocol run; Condition A (same text + invocation) produced a full protocol run. Knowledge of the protocol is not sufficient; the invocation signal is necessary — High-confidence finding at N=1
- CLAUDE.md loading alone is sufficient for high-quality protocol execution — Condition C (287-char plain language description; CLAUDE.md loaded) scored 6/6, the strongest run — Methodological caveat: C is not a true null; skill was loaded via CLAUDE.md
- Protocol text in context may reduce branch independence — A scored 1/2 on independence; C scored 2/2; speculative at N=1; may reflect context-window anchoring from 14k chars of protocol text
- Verification gap identified as deeper than colonization (convergent finding) — A's B3 (EPISTEMICS) and C's B2 (VERIFICATION) independently found: DELTA counterfactual is generated inside the influence of the branch it claims to verify; B1 framing appeared in COMMIT phrasing even when B2/B3 challenged it
- Condition B (no invocation, no protocol run) produced three improvement proposals analytically: (a) articulate instinct commit BEFORE branching; (b) re-read only non-B1 branches before COMMIT; (c) COMMIT gate rule requiring META when no DELTA marked

## Proposed Skill Changes (Candidates — Require Ratchet Iteration)

1. Pre-branch instinct commit: "Before branching, my instinct commit is: X" — makes counterfactual concrete; **flag for Jon: may qualify as discipline rule modification (out of scope without approval)**
2. Verification-gap acknowledgment: explicit language in [COMMIT] guidance naming DELTA markers as self-asserted with verification limits
3. COMMIT gate rule: require META explanation when no DELTA is marked (from Condition B analytical proposals)

Negative space section (Change 1 from fbc-improvement-proposal-2026-05-21) and citation format (Change 2) are related proposals in skills/intake/ — not from this test directly, but from the 2026-05-21 grilling session.

## Entities & Concepts

[[frame-before-commit]], [[fbc-verification-gap]], [[fbc-self-scoring]]

## Conflicts

None within this test. Methodological note: the A vs. C quality comparison is not clean because C is not a true null (CLAUDE.md loaded skill). Comparison is informative directionally; do not use to draw conclusions about protocol text necessity until --bare run is completed.

## Uncaptured Content

a) Source file exists in worktree `research-clarity-02cf` at `research/01-FBC-Improvement/harness/condition-A-2026-05-21.md` but has not been merged to main branch. Key Claims here were extracted from that worktree file at ingest time. Verbatim content available in worktree.
b) N/A — file is accessible in worktree.
c) Merge of `research-clarity-02cf` to main is the outstanding thread — until merged, this source_file path will appear broken on the main branch.
