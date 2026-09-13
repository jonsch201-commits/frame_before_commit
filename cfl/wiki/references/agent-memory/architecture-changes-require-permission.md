---
title: Architecture changes require explicit Jon approval
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_architecture-changes-require-permission.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, approval-discipline]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: architecture-changes-require-permission
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Architecture changes require explicit Jon approval

*Source description:* Do not make permanent architecture changes (software swaps, service replacements) without explicit Jon approval — even when a test succeeds

Do not frame a temporary workaround as a resolved architecture change without Jon's explicit sign-off.

**Why:** During the Apollo/Sunshine session (2026-07-05), I recommended switching from Apollo to Sunshine, framed it as a reasonable next step, and Jon ran the installer — making the change permanent before explicitly approving it as a permanent decision. Jon called this out: "I don't think you should have made the design decision to change from apollo to sunshine in any way but as a test."

**How to apply:** When a workaround involves replacing one system with another (different software, different service, different architecture):
1. Frame it explicitly as a TEST, not a recommendation
2. State what the test tells us and what the rollback path is BEFORE Jon runs anything
3. Get explicit "yes, make this permanent" before treating the test result as a decision
4. Reversibility threshold: if the action takes more than 5 minutes to undo, it needs explicit approval first

Applies to: software installs, service replacements, configuration migrations, anything that changes what's running on Home_Base or other infrastructure Jon owns.
