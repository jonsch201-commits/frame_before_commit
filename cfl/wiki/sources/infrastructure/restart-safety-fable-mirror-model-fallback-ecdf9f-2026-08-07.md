---
title: "Restart safety validation — fable-mirror dispatch confirmed, silent model fallback to Opus found — CFL session ecdf9f, 2026-08-07"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: ecdf9f
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-07-ecdf9f-restart-safety-validation.md
raw_sha256: 4bedcdc2665c6afdd7da4ba67d9747f6296953963ae41b7daf7bdd7fdf54feed
raw_length: 64392 chars / 906 lines (verified turn_count 26, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: restart-safety-fable-mirror-model-fallback-ecdf9f-2026-08-07
aliases: ["restart-safety-validation", "fable-mirror silent model fallback opus", "test 5 PASS on disk", "agents slash command gone"]
generated_by: S-augM-07 executor (week-2026-09-02-corpus lane), reading the raw session extract directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [fable-mirror, restart-procedure, model-resolution, cfl-infra, elder-consult-protocol]
---

# Restart safety validation — fable-mirror confirmed dispatchable, silent Opus fallback found — ecdf9f, 2026-08-07

## Summary

A CFL coordinator session, mid-restart-safety discussion, established that "knowing about"
fable-mirror (its `.claude/agents/fable-mirror.md` file existing in the working dir) is not the
same as being able to dispatch it — only a session launched with the right repo attached can
reach it — and that the `/agents` listing command Jon and the assistant both expected no longer
exists. After Jon relaunched into a fresh session and dispatched fable-mirror there, this session
confirmed the dispatch succeeded by reading the subagent's own JSONL directly off disk, and found
a real defect in the process: the mirror ran on `claude-opus-5` in all 35 logged assistant turns
despite its frontmatter declaring `model: fable`, with no warning or error surfaced. The session
closes with an elder-consult self-audit naming eight prior moments where Jon's words had to be
interpreted, several never corrected.

## Key Claims

- **"Knows about it" is explicitly distinguished from "can run it," named as a recurring failure
  shape.** Verbatim: "This is the distinction that matters. A session can discuss fable-mirror
  fluently just by reading `.claude\agents\fable-mirror.md` — 9,641 bytes of prose sitting in its
  working dir. That is knowledge, not capability. Same failure shape this project keeps hitting:
  an instrument describing a thing it cannot reach." [verbatim]
  ([restart-safety-fable-mirror-model-fallback-ecdf9f-2026-08-07:T6])
- **`/agents` was confirmed gone mid-session, correcting the assistant's own prior instruction.**
  Verbatim: "Correction: `/agents` is gone. My instruction was stale. Ignore it — no listing
  command exists now." [verbatim]
  ([restart-safety-fable-mirror-model-fallback-ecdf9f-2026-08-07:T12])
- **Test 5 (fable-mirror dispatchability) was graded PASS from disk evidence, not from the
  subagent's self-report.** The session located
  `agent-ad903c636a59124b7.jsonl`/`.meta.json` under the fresh session's `subagents/` directory,
  confirmed `agentType: fable-mirror` in the meta file, 58 lines, `isSidechain: true`, and tool
  usage of Glob×5/Grep×13/Read×4 with zero Write/Bash/Edit — matching the agent definition's
  declared tool fences. [verbatim] ([restart-safety-fable-mirror-model-fallback-ecdf9f-2026-08-07:T18])
- **Real defect found: the mirror ran on the wrong model silently.** Verbatim: "Frontmatter says
  `model: fable`. All 35 assistant turns logged `claude-opus-5`. [measured] ... It inherited the
  parent's model and said nothing. No warning, no error. Silent fallback — the exact shape this
  project keeps getting burned by: instrument reports success, does a different thing." The
  session flags CFL's own copy of `fable-mirror.md` has the identical `model: fable` line and
  states the likely (untested) fix is the full model ID `claude-fable-5` rather than the alias.
  [verbatim] ([restart-safety-fable-mirror-model-fallback-ecdf9f-2026-08-07:T18])
- **The session explicitly distinguishes a measurement from an inference about a different
  system**, self-flagging: "For CFL I matched a frontmatter string and asserted a runtime
  behaviour. Different harness, possibly different resolution. That clause is inference wearing a
  measurement's clothes." [verbatim]
  ([restart-safety-fable-mirror-model-fallback-ecdf9f-2026-08-07:T26])
- **An elder-consult closing turn lists eight interpreted-and-not-always-corrected readings of
  Jon's words** across the session — including a "personal will never be public" vs. "final sweep
  before we make it public" tension the assistant flags as unresolved and never surfaced to Jon at
  the time, and a falsified compaction-size threshold (n=1 observation written into CLAUDE.md as
  a rule). [paraphrase] ([restart-safety-fable-mirror-model-fallback-ecdf9f-2026-08-07:T26])
- **A relayed one-line message closes the session**: "WAKE-PROBE FIRED. source=fork," reported as
  bearing on whether SessionStart fires on compact/clear, alongside a hook flag naming five
  session JSONLs with unreflected content and a self-declared `degraded: drive-budget-exceeded`
  state — explicitly not acted on, since the turn asked for a consult, not work. [verbatim]
  ([restart-safety-fable-mirror-model-fallback-ecdf9f-2026-08-07:T26])

## Conflicts

None with existing wiki content.

## Entities & Concepts

fable-mirror, [[mirror-stateless-dispatch-only]], model-resolution (alias vs. full ID),
elder/ancestor consult protocol, [[windows-maxpath-worktree]] (same session-class of
worktree/dispatch mechanics).

## Uncaptured Content

- **This raw is compacted mid-session** (one compaction boundary present); the pre-compaction
  portion of the session is represented only via the machine-generated compact summary, not raw
  turns, and this page draws only on post-compaction turns T1–T26.
- **The elder-consult self-audit at T26 is explicitly self-flagged as biased toward documented
  errors**: "The moments where I interpreted Jon and his words did not survive are precisely the
  ones I can no longer see. So this list is biased toward my documented errors and away from my
  undocumented ones. Treat it as a floor, not a census." [verbatim]
