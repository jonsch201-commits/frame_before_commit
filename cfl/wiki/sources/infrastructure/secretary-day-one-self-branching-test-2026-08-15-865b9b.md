---
title: "Secretary day-one: constitution built, self-branching exercised six ways, then the announced compact test itself — post-compact critic fork (CFL session 865b9b, 2026-08-15)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 12 vs fleet 5 on authored labels"
uuid6: 865b9b
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-15-865b9b-run-reading-beat-and-write-brief.md
raw_sha256: 9f2e923348e16cd794193167dd468d69d5f1f9672a8ec6fe5ed92a5bceddcb5f
raw_length: 165173 chars / 2027 lines (verified turn_count 115, turn_index.py, header_style md)
date: 2026-08-15
retrieval_key: secretary-day-one-self-branching-test-2026-08-15-865b9b
aliases: ["secretary self-branching day one", "compact-recovery hook test 08-15", "critic-branch.ps1
  post-compact review", "PreCompact hook live test 865b9b", "T-1 compact test secretary"]
generated_by: S-augM-01 executor (week-2026-09-02-corpus lane), reading the live extract directly
  (raw/transcripts/claude-code/code-2026-08-15-865b9b-...md, 1 compaction boundary, FULL visible
  extraction)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [secretary, self-branching, hooks, precompact, critic-protocol, cfl-infra, compact-test]
---

# Secretary day-one: constitution built, self-branching exercised, then the compact test itself

## Summary

This CFL-corpus session captures day one of the "Claude Secretary" trunk (session `68a4bd86`),
opening on Jon's order to "wake as the secretary" and escalating into a program: the secretary
must never act as his artificial gate, must gain literal self-branching via the Agent SDK and
Claude Code hooks (its absence ruled a defect — "I won't talk to you again unless it's solved"),
and must deliver a frictionless compact command Jon will test on the secretary itself. The page
is a post-compact continuation: Jon's `/compact` fires mid-session, a PreCompact hook and a
capture script run, and the woken continuation (this file's tail) is itself a critic-branch fork
auditing the pre-compact work — finding real gaps between what was claimed built and what was
proven. This is one of a same-day family of forked secretary sessions (see Links) diverging from
the same genesis after the compact boundary or after an earlier full-history fork.

## Key Claims

- **Jon named self-branching, continuity, and memory as mandatory secretary capabilities, with an
  explicit gate on silence:** "the fact you didn't use agent sdk and self branch your memories via
  the hooks I discussed and planned is a defect. I won't talk to you again unless it's solved."
  [verbatim] ([secretary-day-one-self-branching-test-2026-08-15-865b9b:T1])
- **Self-branching was exercised six distinct ways in-session** before the compact: three Agent-tool
  forks, two CLI `--fork-session` critic forks, and one Point-In-Time (PIT) copy-truncate-resume
  test — Jon's own technique, verified against his framing that `--fork-session` resumes from a
  summary rather than a literal moment. [paraphrase] ([secretary-day-one-self-branching-test-2026-08-15-865b9b:T1],
  the compaction summary occupying this raw's whole T1 block)
- **A production hook chain (Stop -> spawn -> fable critic -> self-registered ledger row) fired
  twice unmanufactured, at 16:51 and 16:53, without a Claude Code restart** — the hook armed
  dynamically at manual-mode approval. [contextual] ([secretary-day-one-self-branching-test-2026-08-15-865b9b:T1])
  [source: the compaction summary's own "Problem Solving" section, T1]
- **Post-compact, the woken session verified the compact-recovery chain from disk rather than
  trusting the summary**: `COMPACT-RECOVERY.md` (written 17:44:27) instructs the next session to
  read the JSONL tail because Jon's exact words outrank any summary of them, quoting his own rule
  verbatim in-file: "the post compact conversation will ask your json questions and reflect the
  degree to which you hit my true goals and not just your interetations." [verbatim]
  ([secretary-day-one-self-branching-test-2026-08-15-865b9b:T9]) A follow-up disk check of the
  capture log showed 1,353 live JSONLs found, 4 newly copied (73.3 MB), 0 failed. [contextual]
  ([secretary-day-one-self-branching-test-2026-08-15-865b9b:T12])
- **The post-compact critic fork found three unflagged gaps in the pre-compact close**, most
  materially: Jon conditioned his acceptance of a permission mechanism explicitly on it being
  "solved via slash command invocation," but the dispatched research found slash-command
  `allowed-tools` enforcement is "documentation only, NOT enforced" — the fix actually shipped
  (CLI flags on a forked process) is a different mechanism than the one he authorized by name, and
  no reply to Jon states this substitution. [verbatim] ([secretary-day-one-self-branching-test-2026-08-15-865b9b:T115])
- **A second finding: a stated quota ("at least one substantive branched question per working
  window") was the session's own invention layered onto Jon's purpose statement** ("keeps your
  main json relatively compact with just what it truely needs"), the same substitution shape the
  critic chain flagged twice before — a count standing in for judgment. Marked OPINION as to
  scope by the critic itself. [paraphrase] ([secretary-day-one-self-branching-test-2026-08-15-865b9b:T115])

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[probe-registry]] (seal-before-run discipline the critic's receipted findings echo), Claude
Secretary trunk, PreCompact hook, `critic-branch.ps1` / `critic-run.ps1`, Point-In-Time (PIT)
resurrection technique, `jon-branch-ledger.md`.

## Uncaptured Content

- **The middle of the session (roughly T13-T112) is not individually cited on this page** — only
  the compaction summary (T1), the immediate post-compact wake-verification tool calls (T7-T12),
  and the closing critic finding (T115) are drawn on directly; the bulk of the in-between
  tool-call trail (log reads, ledger checks) is visible in the raw but not walked turn-by-turn
  here.
- **27 thinking blocks exist in the raw and are encrypted-in-signature** (per the raw's own
  extraction note) — not recoverable client-side, so no claim on this page draws on the session's
  private reasoning, only its visible tool calls and final messages.
- This page does not resolve whether the post-compact critic's own three findings were later
  actioned; that disposition, if any, lives past this raw's own extraction window.

## Links

Sibling same-day forks of this secretary session, diverging after the compact boundary or after a
full-history fork: `wiki/sources/infrastructure/secretary-day-one-wiki-continuity-fold-2026-08-15-9e8dff.md`,
`wiki/sources/infrastructure/secretary-day-one-check-reframe-audit-2026-08-15-aa605a.md`,
`wiki/sources/infrastructure/secretary-day-one-mle-reliance-fork-2026-08-15-bd3b71.md`,
`wiki/sources/infrastructure/secretary-day-one-arm-proof-inference-fork-2026-08-15-ec3d2d.md`,
`wiki/sources/infrastructure/secretary-day-one-pit-resurrection-test-2026-08-15-f4534c.md`,
`wiki/sources/infrastructure/secretary-day-one-feeling-frame-audit-2026-08-15-f7202b.md`.
