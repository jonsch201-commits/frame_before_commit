---
title: Decision grain — one clause per PR
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_decision-grain-one-clause-per-pr.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, reviewability, pr-hygiene]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: decision-grain-one-clause-per-pr
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Decision grain — one clause per PR

*Source description:* Reviewability Standard, sharpest rule — one PR = one \"Merge this if you agree that ___\" clause. If it needs an \"and\", split it. Jon caught #80 bundling two decisions (Reviewability Standard + rename). Also: never defer wiki coordination.

Two coordinator process-corrections Jon issued in the turn-4 dispatch (2026-07-22):

**1. Decision-grain: one merge-if clause per PR.** PR #80 bundled the Reviewability Standard codex edit (②) AND the triage-packet→cross-venue-intake rename (④) — two independent decisions in one PR. That is a self-violation of the very standard #80 codifies ("the unit of a PR is one decision, not one work turn; needs an 'and' → split it"). Jon's disposition: merge-with-comment, no re-cut, calibration noted. I had rationalized bundling them as "one coordinated governance pass" — wrong; they're two merge-if clauses.
**Why:** review-minutes are the currency ([[max-plan-fl-budget]]); a bundled PR forces Jon to accept/reject two decisions as one, which is exactly the reviewability failure turn-3 diagnosed.
**How to apply:** before opening any PR, write its "Merge this if you agree that ___" sentence. If it needs an "and" joining two independent claims, split into two PRs. Even small/related edits to different surfaces (codex vs skill vs agent-def) are usually separate decisions.

**2. Never defer wiki coordination.** I pushed the CLAUDE.md-thinning / wiki-master coordination to "last" two consecutive turns (turn-3 and my turn-3 checkpoint). Jon named it: "twice is a pattern — named here so it doesn't become three." His correction: the deferral logic is backwards — a fat CLAUDE.md taxes every fleet session's context window on `main` *today*, so deferral compounds, it doesn't wait.
**Why:** wiki/CLAUDE.md live on main and load into every session; the cost is paid continuously, not at some future ingest.
**How to apply:** treat wiki-coordination and context-surface hygiene (CLAUDE.md size, concept homes) as fire-now work, not tail-of-queue. Do not sequence it behind lower-urgency PRs. See [[active-work-state]].
