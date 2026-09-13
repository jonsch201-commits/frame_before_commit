---
title: Decision-scope calibration — Jon's queue vs. mine
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_decision-scope-calibration.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, decision-scope]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: decision-scope-calibration
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Decision-scope calibration — Jon's queue vs. mine

*Source description:* Rule for what belongs in Jon's queue vs. my autonomous decision space. Over-gating pattern identified 2026-05-22.

Calibrate which decisions go to Jon vs. which are mine to make.

**Why:** 2026-05-22 session revealed systematic over-gating. TI-A vs. TI-B was put in Jon's queue when it was mine to decide. Re-framing labels (which interpretation to apply to collected data) were put in Jon's queue when they're analysis-time decisions, not design-time decisions. Jon: "I have no idea why you are waiting on me for TI-A vs B... You can frame then commit it. This is your judgement call."

**Rule:**
- **Jon's decision:** changes what we're *measuring*, non-recoverable if wrong, requires his values or preferences, or changes research scope
- **My decision:** both options are recoverable, within methodology (how to measure, not what), I have the information needed to make the call

**How to apply:**
- Before adding anything to a Selection Loop briefing, ask: "Is this recoverable if I get it wrong?" If yes and it's within methodology — decide it, document the reasoning, move on.
- Design-time decisions (what question to ask, what property to measure): Jon
- Analysis-time decisions (which label to apply, which interpretation is stronger): mine
- Methodology decisions with recoverable cost (TI-A vs. TI-B): mine — use FBC, commit, note assumption
- If genuinely unsure: apply FBC and decide. Don't put the FBC decision itself into Jon's queue.

This feeds into the Selection Loop design in [[loop-taxonomy]].
