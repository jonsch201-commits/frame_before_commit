---
title: A subagent stays open only with real work
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-AGENTMEM; sub: fleet 5 vs wiki 0 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_subagent-stays-open-only-with-work.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, subagent-lifecycle, fable-mirror]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: subagent-stays-open-only-with-work
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# A subagent stays open only with real work

*Source description:* A subagent Jon wants to talk to must be given long real work — \"hold and wait for Jon\" closes it in seconds, and tool-restricted agents like fable-mirror have no Bash and cannot sleep.

2026-08-05: Jon asked me to resume the fable-mirror so he could talk to it. I sent it a
brief with "Hold, and wait for Jon. Nothing here asks you for output." It acknowledged and
**completed in 13 seconds.** Jon returned to a closed agent. His words: *"It finished because
you didn't give it any way to stay open. No single additional instruction to run a command that
would allow it to wait for me for at least 5 minutes? It autoclosed before i got back here."*

**Why:** an agent's lifetime is its tool calls. There is no idle state. And the obvious
workaround does not exist for this agent — **`fable-mirror`'s tools are Read, Grep, Glob, Write.
No Bash, so no `sleep`.** A tool-restricted agent cannot wait on a timer at all; the *only*
thing that keeps it available is having genuine work in front of it.

**How to apply:**
- When Jon wants to converse with a subagent, dispatch it with **long, real, multi-step work**
  sized to the conversation — not a hold instruction. Verification tasks are ideal: many
  independent reads, each one useful whether or not he interrupts.
- Put a **standing priority at the top**: if Jon messages, drop the task mid-step and answer
  immediately; do not finish the current step or summarize progress first.
- Tell it to **report findings as it reaches them**, not batched at the end — so an interruption
  doesn't discard what it already knows.
- Note the tension I got wrong: hold-only was chosen to prevent the recorded runaway
  ([[mirror-stateless-dispatch-only]]). It traded Jon's access for safety, and that trade was
  wrong. Scoping the *work* (verify, don't ratify; write nothing unless Jon says so) controls
  runaway without closing the agent.
- Closing is **not** loss — `SendMessage` to the agentId resumes from transcript with context
  intact, and Jon considers that genuine continuity ("literal kv-hash exact context"), unlike a
  fresh `Agent` call. See [[coordinator-dispatches-never-adopts]].

Related: [[mirror-stateless-dispatch-only]], [[coordinator-dispatches-never-adopts]],
[[checkpoint-model]].
