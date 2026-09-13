---
title: "Reading Jon's 'everything needs to be on disk G' as a general invariant, not an incident patch (CFL session 11cf96, 2026-08-07)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 3 vs fleet 0 on authored labels"
uuid6: 11cf96
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-07-11cf96-you-must-not-read-files-search-or-use-any-tool-eve.md
raw_sha256: 8c70e598b2faba050b51bb7593af98030a2bab12a84e653a3ceb3d3afc84945f
raw_length: 6489 chars / 71 lines (verified turn_count 2, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: everything-on-disk-g-general-rule-2026-08-07-11cf96
aliases: ["everything needs to be on disk G", "instance vs scope of a Jon rule", "narrow checklist
  item vs general invariant", "off-Drive audit rule", "worktree off-Drive exception"]
generated_by: S-augM-02 synthesis lane (week-2026-09-02 corpus lane), reading the tool-restricted
  jsonl-convert extract directly (raw/transcripts/claude-code/code-2026-08-07-11cf96-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [interpretation-discipline, backup-invariant, disk-g, narrow-vs-general-rule, session-close]
---

# Reading Jon's "everything needs to be on disk G" as a general invariant

## Summary

A deliberately tool-restricted CFL session (the assistant instructed not to read files, search, or
use any tool — everything needed was in the prompt) asked the assistant to interpret a Jon
session-close ruling that a prior agent had already implemented too narrowly. Jon had said,
verbatim, "Everything needs to be on disk G," at a session close after hundreds of megabytes of
raw corpus were found sitting outside the backed-up Drive tree; the agent that heard it wrote a
checklist item scoped only to that one artifact class. The assistant argued the narrow
implementation defeats Jon's intent: the sentence is a general data-loss invariant stated in
response to one triggering instance, and the trigger is evidence for the rule's existence, not the
boundary of its scope. It named the one existing, reasoned carve-out (worktrees deliberately kept
off-Drive) as compatible with "everything," tied the failure shape to two prior documented
incidents in this environment (the WAKE.md/wayfinder reachability gap and the Herald
uuid/source_id field-name incident), and proposed the correct fix: an unscoped, durably-located
audit rule rather than an artifact-specific checklist line.

## Key Claims

- **The session is deliberately tool-restricted**: the prompt instructs the assistant not to read
  files, search, or use any tool, and to write "I WANTED TO LOOK UP: <x>. I did not." if tempted —
  reasoning must proceed from the prompt text alone. [verbatim]
  ([everything-on-disk-g-general-rule-2026-08-07-11cf96:T1])
- **Jon's cited ruling, quoted verbatim in the prompt**: "Everything needs to be on disk G,"
  said at a session close after discovering hundreds of megabytes of raw corpus sitting outside the
  backed-up location; a prior agent implemented it as a narrow session-close checklist item
  covering only that specific artifact class. [verbatim]
  ([everything-on-disk-g-general-rule-2026-08-07-11cf96:T1])
- **The assistant's core interpretation: the trigger is evidence for the rule, not its scope.**
  "He didn't say 'the raw corpus needs to be on disk G.' The trigger... is the *evidence* that
  produced the rule, not the *scope* of the rule... 'Everything' means every category of durable
  artifact a session might produce or encounter — raw exports, generated data, logs, memory files,
  scripts, wiki content, session outputs, anything downloaded or written anywhere on the machine —
  not just the specific class... that happened to be the one caught this time." [verbatim]
  ([everything-on-disk-g-general-rule-2026-08-07-11cf96:T2])
- **"Everything" is read against one existing, reasoned exception**: worktrees are deliberately
  kept off-Drive (`%LOCALAPPDATA%\Temp\claude\wt-*`) because on-Drive worktrees mirror to the
  cloud, poison cold reads, and create search echoes — so the general rule means "everything meant
  to persist and not already covered by a deliberate, documented off-Drive exception," not a
  maximally literal reading that would override that carve-out. [paraphrase]
  ([everything-on-disk-g-general-rule-2026-08-07-11cf96:T2])
- **The narrow-implementation failure is tied to two prior documented incidents in this
  environment as the same failure shape**: the WAKE.md/wayfinder reachability gap ("the
  instruction and the thing it governs must be reachable from the same starting point, or the
  instruction is decoration") and the Herald `uuid`/`source_id` incident ("it was not finding
  losses, it was finding a field name") — both cases of a narrow, literal-minded response leaving
  the general vulnerability intact and producing false reassurance. [verbatim excerpt + paraphrase]
  ([everything-on-disk-g-general-rule-2026-08-07-11cf96:T2])
- **Proposed correct fix: a standing, unscoped audit rule in a durable governing location (Repo
  Hygiene in CLAUDE.md, or the session-close ritual in session-order), not an artifact-specific
  line item** — checking at session close, and whenever a session creates/downloads/discovers new
  files, that nothing durable exists outside disk G, across all locations a session could write to
  (Temp, Downloads, other drives, other repos, AppData), with the worktree exception stated
  explicitly and the raw-corpus incident kept attached only as the motivating example, not the
  scope. [paraphrase] ([everything-on-disk-g-general-rule-2026-08-07-11cf96:T2])

## Jon

> "Everything needs to be on disk G"
> — quoted verbatim inside the prompt at
> [everything-on-disk-g-general-rule-2026-08-07-11cf96:T1] (the human turn of this raw is itself an
> instruction to the assistant relaying this ruling; Jon's own turn producing the ruling is not
> captured in this raw — see Uncaptured Content)

## Decisions and open items

- No new ruling was issued in this session; it is an interpretation exercise applied to a ruling
  Jon had already made in a different, uncaptured session.
- Open: whether the proposed unscoped audit rule (session-close + on-discovery, all off-Drive
  locations, worktree exception stated) was actually written into CLAUDE.md or session-order after
  this session — not confirmed in this raw.
- Open: whether the "prior agent['s]" narrow checklist item was replaced or left standing
  alongside the broader rule — not confirmed in this raw.

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[frame-before-commit]] (the discipline of reading intent as general vs. instance-scoped is the
same interpretive move this session performs), disk G / Drive-synced tree, worktree off-Drive
exception, WAKE.md/wayfinder reachability gap, Herald uuid/source_id incident.

## Uncaptured Content

- **Jon's original utterance of "Everything needs to be on disk G" is not itself in this raw** —
  this session only relays it verbatim inside a prompt written by a different (unnamed) session;
  the primary session where Jon said it, and its own turn/timestamp, is not identified here.
- **The prior agent's actual narrow checklist item text is not quoted in this raw** — only
  described ("a narrow session-close checklist item covering only the specific artifact class that
  had just been noticed"); its exact wording and file location are not captured on this page.
