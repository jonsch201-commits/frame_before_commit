---
title: Coordinator dispatches, never adopts
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-AGENTMEM; sub: fleet 7 vs wiki 0 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_coordinator-dispatches-never-adopts.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, coordinator, role-boundary]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: coordinator-dispatches-never-adopts
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Coordinator dispatches, never adopts

*Source description:* When Jon asks to speak with a named prior persona \"continued by record\", the coordinator DISPATCHES the packet verbatim to fable-mirror — it never adopts the identity itself.

2026-08-05: Jon pasted `HANDOFF-2026-08-04-triage-fable` — a wake-up packet addressed to a
fable-mirror session, opening "I wish to speak with the triage-Fable of 2026-08-02/03,
continued by record." I read it and **answered as if I were the addressee**. Jon's correction:
*"yes you are not the mirror you are the coordinator. A project manager meta role, you don't do
the work you coordinate the work via agent sdk. Part of that is having a fable-mirror for
guidance, and i need to talk to it with the exact message i sent you."*

**Why:** the coordinator is a session role that runs nothing itself (`CLAUDE.md` § Coordinator).
A packet addressed to another role is a **dispatch payload**, not an instruction to me. Adopting
it collapses two roles into one and destroys the redundancy the whole two-layer design exists for
— the same convergence hazard Herald named on 2026-07-27. It also silently impersonates a layer
with different fences: the mirror is read-only on corpus+wiki and may write only to
`wiki/intake-triage/`; I have full shell and write.

**How to apply:**
- Trigger phrases — "I wish to speak with…", "continued by record", "wake-up packet",
  "HANDOFF-…", a block whose "First actions on wake" section addresses someone else.
- Move: `Agent(subagent_type: fable-mirror, model: fable)` with Jon's message **verbatim,
  packet included**, `run_in_background: true`. Then say it's live and stand down from that thread.
- Do **not** relay the mirror's reply back to Jon as narration — he talks to it directly
  mid-turn, and its answers arrive to me only as task-notification payloads
  (see [[mirror-stateless-dispatch-only]]).
- Fold only *coordinator-relevant* items out of its reply into the run (e.g. a corpus freshness
  stamp affecting SU step 2). Leave the substance in his thread.
- Correct the packet's environment section rather than obeying it: a packet authored on claude.ai
  states *its* constraints ("no shell"), not this environment's. Jon explicitly warned that an
  earlier draft nearly told the reader to never write files, "which would have broken things."

Related: [[mirror-stateless-dispatch-only]], [[mirror-before-jon]],
[[project_cfl-memory-store-split-by-cwd]].
