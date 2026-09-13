---
title: FBC Verification Gap
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; branch from title/slug keyword (fbc); sub: branch `fbc` has no registered sub-branches"
type: concept
first_seen: test-master-run-003-6branch-directed
source_count: 4
last_updated: 2026-09-11
---

## What This Is

A structural limitation of [[frame-before-commit]] identified empirically: the protocol cannot verify, from within a single run, that branches are genuinely independent. The ID-only rule (no explicit reference to prior branches) prevents explicit anchoring but cannot prevent implicit context-conditioning — B1 is present in the context window when B2 is generated.

## What the Wiki Says

### The Problem

All branches in a standard FBC run are generated in one continuous autoregressive stream. B1 exists in the context window before B2 begins. The ID-only rule prevents B2 from *explicitly* referencing or summarizing B1, but it cannot prevent B1's framing, vocabulary, and activation patterns from conditioning what B2 recruits.

This means: even a formally compliant run (ID-only enforced, no explicit cross-referencing) may produce branches that are less independent than they appear. The dominant frame from B1 can colonize B2 and B3 despite protocol compliance. ([test-master-run-001-pure-null], [test-master-run-003-6branch-directed])

### Empirical Origin

B4 (NO-WORKING-CONTEXT) in test-run-003 surfaced this as a genuine delta: removing working context produced a branch that identified the verification gap as a structural problem. The finding: "the protocol cannot verify that branches are actually independent without cross-session comparison." This was a NATIVE delta — not reconstructed after the run. ([test-master-run-003-6branch-directed])

B4 (ORTHOGONAL) in the 4-branch directed test independently converged on the same finding: "named multi-sample protocol as the mechanism that would close the verification gap (can't verify branch independence from within a single run; requires cross-run comparison)." ([fbc-4branch-delta-2026-04-15-c6154b])

Two independent branches from different runs converging on the same structural diagnosis is stronger confirmation than either alone.

### Architectural Basis (from fbc-forward-pass-mechanics-2026-05-07-b04c8b)

The forward pass provides the architectural grounding: there is no re-initialization between branches. Each token conditions on all prior tokens in the stream. B1 is not "cleared" before B2 begins — it is part of the accumulated context. T-tags and the ID-only rule create serialization boundaries, but these are token-level constraints on a continuous generation, not true independence.

The [[fbc-self-scoring]] Independence dimension captures this: a low Independence score (e.g., 2/5) flagged from within a run is the honest acknowledgment that this constraint was operating.

### The Mechanism That Would Close It

Multi-sample protocol — cross-session comparison. Send the same prompt to a different model instance (inter-model branching) or in a cold session. Convergence across cold independent runs is stronger confirmation than convergence within a single run. Divergence between runs is the most valuable signal — reveals what is context-dependent vs. structural.

This is also the architectural basis for inter-model branching as a protocol extension. ([fbc-canonical-skill-2026-04-28])

### Convergent Finding from 01-FBC-001 (2026-05-21)

The verification gap was independently surfaced in two separate conditions of 01-FBC-001 without the branches being aware of each other's framing:

- **Condition A, B3 (EPISTEMICS):** flagged that DELTA counterfactual is generated inside the influence of the branch it claims to verify
- **Condition C, B2 (VERIFICATION):** independently found the same structural problem — B1 framing appeared in COMMIT phrasing even when B2/B3 directly challenged it

This is stronger confirmation than the earlier runs: convergent across conditions, different scorers, same finding. The gap is not about colonization (surface vocabulary borrowing) but about the DELTA verification mechanism itself. A DELTA is asserted by the model generating COMMIT — which has read all branches, including B1. There is no clean counterfactual available within a single run. ([test-master-fbc-invocation-2026-05-21-abc])

### Current Status

Unresolved. The protocol acknowledges the gap but does not close it. Cross-session comparison is the proposed mechanism; it has not been implemented as a formal test protocol. OI-002 (FBC test suite with Test Master support) is the active item that would begin to address this empirically. Proposed skill changes (verification-gap acknowledgment language in [COMMIT] guidance) are in skills/intake/ as candidates pending ratchet iteration.

## Amendment 2026-09-11 — Extension v2 claims a resolution; CFL records it as PARTIAL, not closed

`skills/frame-before-commit/SKILL.md` §2 of "Extension v2" (ratified by Antigravity in
WAYFINDER-008, 2026-09-10) is titled *"Closing the May 2026 Verification Gap via Isolated
Branching"*. It is recorded here because a skill asserting a closure that its concept page does not
record is annotation, not disposition.

**What v2 proposes:** when true branch independence is required, dispatch separate subagents with
separate memory spaces (`--fork-session -p` in CLI harnesses) and return only distilled findings to
the coordinator, rather than generating branches inside one context window.

**CFL's grade: PARTIAL.** The mechanism does remove autoregressive conditioning, which is the exact
structural cause named above. Two limits keep the row open:

1. ⚠️ **The return path is the new gap.** In this harness a subagent's final report is routinely
   swallowed — the notification delivers `Done.` and the real content is the largest assistant text
   block in the subagent JSONL. An independence mechanism whose distilled findings never reach the
   coordinator is worse than intra-context branching, because it looks like it ran. v2 does not name
   the retrieval step.
2. ⚠️ **Nothing has measured it.** The convergent finding above came from scored runs across
   conditions. No equivalent run exists for isolated-subagent branching, so the claim that the gap is
   closed rests on the mechanism's description, not on a DELTA anyone observed. OI-002 is still the
   item that would settle it.

**Status therefore moves from Unresolved to PARTIAL — mechanism proposed and ratified elsewhere,
unmeasured here.** Do not cite this page as evidence the gap is closed.


## Conflicts

None. All sources independently identify the same structural mechanism.

## Related

[[frame-before-commit]], [[fbc-self-scoring]]
