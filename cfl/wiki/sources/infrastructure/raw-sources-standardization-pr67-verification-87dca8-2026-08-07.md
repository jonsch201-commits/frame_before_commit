---
title: "Raw-sources standardization — PR #67 independently verified against diffs, worktree-untracked-files gotcha found, elder self-audit on Packet A/B — CFL session 87dca8, 2026-08-07"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 87dca8
source_kind: session
source_file: raw/transcripts/claude-code/fl/code-2026-08-07-87dca8-raw-sources-standardization.md
raw_sha256: 1596f8d8932a7574d5e917e10fa66307d502ac39afd65748759290dd20428217
raw_length: 138429 chars / 1707 lines (verified turn_count 86, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: raw-sources-standardization-pr67-verification-87dca8-2026-08-07
aliases: ["raw-sources-standardization", "PR 67 phase-1 bugfix batch verified", "worktree does not inherit untracked files", "packet A B work order elder consult"]
generated_by: S-augM-07 executor (week-2026-09-02-corpus lane), reading the raw session extract directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [pr-review, coordinator-discipline, worktree-mechanics, cfl-infra, elder-consult-protocol]
---

# Raw-sources standardization — PR #67 verified, worktree gotcha, elder self-audit — 87dca8, 2026-08-07

## Summary

A long CFL coordinator session, resuming post-compaction with the instruction "Proceed from
plan," independently verified all 8 items of a dispatched Phase-1 bugfix batch (PR #67) against
actual diffs rather than trusting the executor's self-report — catching a real structural gap (an
isolated git worktree not inheriting untracked repo files, stalling a dispatched agent) and a
residual gap (a duplicate file's deletion, being on an untracked path, would never actually reach
`main` via the PR). The session then reviewed and merged three further draft PRs (#64–66),
rebased #67 past a real conflict, and drafted a coordination-protocol message to a sibling
Claude.ai-side meta-PM/Herald layer. It closes with two elder-consult self-audits (memory-only,
no file reads) naming interpretive choices made along the way and a note that the Packet A/B work
order cited in CLAUDE.md was never independently verified this session, only read secondhand.

## Key Claims

- **Git worktrees do not inherit untracked repository state — a previously undocumented
  structural limitation, discovered mid-dispatch.** Verbatim from the compaction summary this
  session opened with: "isolated `git worktree` checkouts only replicate tracked/committed repo
  state — untracked files present in the main working tree ... are NOT present in a freshly-
  created worktree. A subagent dispatched into such a worktree will stall on any task requiring
  those files." Fixed by manually copying the specific untracked files into the target worktree
  and resuming the agent via `SendMessage`. [verbatim]
  ([raw-sources-standardization-pr67-verification-87dca8-2026-08-07:T1])
- **A subagent's own recount corrected the original brief's numbers, and the coordinator
  independently reconciled the discrepancy rather than trusting either count blindly.** The
  agent's claimed "12 pre-skill instances" (vs. the brief's 11) reconciled correctly once the
  coordinator's own first grep — which used a strict `type:` field match and got 8 — was
  broadened to the actual filename-prefix convention SKILL.md uses, catching annotated type
  values like `type: triage-stub-erratum` that a strict match misses. [paraphrase]
  ([raw-sources-standardization-pr67-verification-87dca8-2026-08-07:T1])
- **A deletion that will never ship was caught by diff-level verification.** A dispatched agent
  deleted an untracked duplicate file (`wiki/triage-packet-2026-07-10-herald-updates.md`,
  confirmed byte-identical to its tracked canonical copy) inside its isolated worktree — but
  because the file was never git-tracked, "this deletion is on an untracked file and will never
  appear in the PR diff / never reach `main` on merge," flagged as a residual manual action still
  owed in the real working tree. [verbatim]
  ([raw-sources-standardization-pr67-verification-87dca8-2026-08-07:T1])
- **A `SendMessage` parameter-name error was caught and fixed in-session**: the tool call failed
  with `InputValidationError: required parameter 'message' is missing` because `content` was used
  instead of `message`; retried correctly. [paraphrase]
  ([raw-sources-standardization-pr67-verification-87dca8-2026-08-07:T1])
- **A truncated task-notification was correctly NOT trusted as a genuine completion**, verified
  instead via `gh pr list` and direct `git status --short --branch` in the worktree — which
  confirmed the notification's apparent completion was in fact a genuine stall (missing untracked
  files), not merely a reporting artifact, distinguishing two different root causes behind the
  same suspicious-completion symptom. [paraphrase]
  ([raw-sources-standardization-pr67-verification-87dca8-2026-08-07:T1])
- **A follow-on elder-consult self-audit states the Packet A/B work order was never opened this
  session, only read secondhand** through a later file's description of it, and explicitly
  declines to assert closure: "That's a status snapshot, not a closure statement — I have no
  in-session evidence either one actually closed." [verbatim]
  ([raw-sources-standardization-pr67-verification-87dca8-2026-08-07:T83])
- **The same elder-consult turn names four moments of interpreting Jon's words**, three
  surfaced back to Jon at the time (asking rather than silently picking a reading) and one
  ("you continue upon my command there") resolved silently on an assumed reading without
  flagging the alternative. [paraphrase]
  ([raw-sources-standardization-pr67-verification-87dca8-2026-08-07:T83])

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[windows-maxpath-worktree]] (the worktree-mechanics gotcha family this session's finding
belongs to), [[mirror-stateless-dispatch-only]], elder/ancestor consult protocol, PR review
discipline (diff-verification over self-report trust), [[record-architecture-v1]].

## Uncaptured Content

- **Turns 9–66 (the bulk of PR review, rebase, and coordination-draft mechanics) are not
  individually cited on this page** — only the compaction-summary content (T1), the immediate
  status reply (T2, not separately quoted), and the two elder-consult turns (T82–T83) are drawn
  on for Key Claims; the intermediate diff-review and rebase work is visible in the raw but not
  walked turn-by-turn here.
- **20 thinking blocks exist in the raw and are encrypted-in-signature**, not recoverable — no
  claim on this page draws on the session's private reasoning, only visible tool calls and text.
