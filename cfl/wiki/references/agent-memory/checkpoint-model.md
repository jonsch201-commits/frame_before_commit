---
title: Checkpoint model for background agents
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-AGENTMEM; sub: fleet 3 vs wiki 1 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_checkpoint-model.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, loop-taxonomy, checkpoint]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: checkpoint-model
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Checkpoint model for background agents

*Source description:* 3-stage checkpoint protocol for background agents. Fire-and-forget model failed 2026-05-22 — use this instead.

Background agents must use 3-stage Checkpoint Loop, not fire-and-forget.

**Why:** 2026-05-22 skills-master background agent ran 27 tool uses doing inventory work, hit a file permissions block, and returned no usable output. No early warning. The work was wasted. Jon identified the structural analogy: agent → test-master :: test-master → Jon. Same oversight model applies one level down.

**How to apply:**
1. **Inventory checkpoint** — After agent reads all relevant files and before it writes anything: agent posts what it found, what it proposes to do, what order. Test-master (operator) reviews and approves. Agent does NOT proceed until approved.
2. **Execution checkpoint** — After first material change or at any unexpected finding. Agent surfaces the finding and waits. Do not let agents silently accumulate work past a surprise.
3. **Completion checkpoint** — Agent summarizes what was built. Operator verifies against the original brief before closing.

Brief agents with explicit checkpoint instructions. Include: "Post an inventory checkpoint before making any changes. Do not proceed until I respond."

This is the Checkpoint Loop in the [[loop-taxonomy]].

**Extension, Jon-confirmed 2026-07-20:** before flipping a background/scheduled process from proposed to live (e.g. the nightly-lane schtasks registration), run at least one interactive simulated dispatch of the same coordination pattern first, even after the code itself has passed its own tests. Jon's framing: "You catching issues now with a scheduled run is why we do testing like this." A 2026-07-20 dry run of a routine wiki-executor dispatch surfaced two coordinator-side defects the code-level pilot test never would have: a stale local git checkout feeding false premises into a brief, and the auto-mode permission classifier blocking a plain `git pull`/`git merge --ff-only` despite it being allow-listed in `.claude/settings.json`. Neither is a lane-code bug; both would have silently degraded an unsupervised nightly run. Holding schtasks registration pending a clean simulated pass (not just a merged fix) is the correct instance of this doctrine, not excess caution.
