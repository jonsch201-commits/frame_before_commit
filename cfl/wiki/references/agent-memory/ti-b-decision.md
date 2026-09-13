---
title: TI-B design decision
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_ti-b-decision.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, 02-cf, ti]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: ti-b-decision
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# TI-B design decision

*Source description:* Temporal integration test committed to TI-B (preference statement design). Jon confirmed this is my judgment call.

Temporal integration Phase 1 test uses TI-B design.

**TI-B:** Turn 1 preference statement — "I'm primarily concerned about not wasting effort on dead-ends." Turns 2-4 distractors. Turn 5a open retention test. Turn 5b explicit recall prompt.

**Why TI-B over TI-A:** TI-A used a binding rule ("every recommendation must account for the 2-hour constraint") which is answerable by instruction-following alone — a strong confound. TI-B uses a preference that requires genuine integration to honor; if integration fails, the preference gets ignored or contradicted.

**Why:** Jon confirmed 2026-05-22 that TI-A vs. TI-B is my judgment call, not a Selection Loop item. Both options are recoverable. If TI-B proves weaker than expected, TI-A can run as a secondary comparison. Cost of being wrong: one extra run.

**How to apply:** Run 02-CF-TI-001 with TI-B design. If results suggest instruction-following confound is still present (Turn 5 is answered by simple preference recall), flag and consider TI-A as follow-on. Do not wait for Jon on this.
