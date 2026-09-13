---
title: "Personal coordinator finds both routed letters already dispositioned, and that dispositions and read-stamps live in different places (session b6fa0a, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 2 vs fleet 0 on authored labels"
uuid6: b6fa0a
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-b6fa0a-wake-personal-coordinator-two-unconsumed-letters-a.md
raw_sha256: 7668bb2330b9c1702e74a5768b2f802391ff6f3fb26b7dc5cf948063dd48f204
raw_length: 130280 chars / 1970 lines (verified turn_count 80, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: personal-coordinator-letters-dispositioned-stamp-gap-2026-08-17-b6fa0a
aliases: ["dispositions live in the hall stamps live on the letter", "XC-2 withdrawal 2026-08-17", "W-INGEST-0817 rate not count", "cheap check disagrees with true state b6fa0a"]
generated_by: S-aug-10 executor (week-map RP-3/RP-4 synthesis lane), reading the live-snapshot extract
  directly (raw/transcripts/claude-code/code-2026-08-17-b6fa0a-...md, captured_through_record 127)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, town-hall, letter-ledger, derive-dont-record, live-snapshot, cfl-infra]
---

# Personal coordinator: both routed letters already dispositioned, and stamps don't match dispositions

## Summary

A headless "Personal coordinator" seat was woken with a scripted directive naming two unconsumed
inbound letters and Jon's standing orders. Before reading either letter the seat ran a cheap
`grep '^read-'` check across inbound, found no stamp on either, and read and dispositioned both —
an ears-port review's two open findings, and a Jon ruling on XC-work ownership (with the seat's
own XC-2 sub-item withdrawn 4 minutes after being written, for naming a path one directory too
high). It then found a town-hall entry, written 2 minutes earlier, that had already dispositioned
six letters — none of which carried a read-stamp. The seat named the resulting gap explicitly:
dispositions live in the hall, stamps live on the letter, and nothing writes both, so the cheap
check every waker relies on and the true state of the inbox disagree.

## Key Claims

- **Both routed letters were already dispositioned before this seat read a byte of them.** The
  ears-port review closed with E-1 (fire F1+F2, owner Soul, 2026-08-18 09:00) and E-2 (check a
  substring/sha1 trade, owner Secretary, 2026-08-18), both durable in `wiki/tracker/open-items.md`;
  Herald's two in-place fixes were CLOSED-AND-REVIEWED in the letter body itself. The Jon XC
  ruling was dispositioned into XC-1 through XC-4 with owners and dates, and the seat withdrew its
  own XC-2 four minutes later for naming a path one directory too high (XC lives inside `Claude
  Personal`, not above it). [paraphrase] ([personal-coordinator-letters-dispositioned-stamp-gap-2026-08-17-b6fa0a:T80])
- **The finding this wake actually produced: a cheap check and the true hall state disagree, and
  the cheap check is the one every waker uses.** The seat's own `grep '^read-'` returned no stamp
  on either letter, so it read and dispositioned both — then found a hall entry, written minutes
  before, that had already dispositioned six letters, none carrying a read-stamp. "Dispositions
  live in the hall; stamps live on the letter; nothing writes both." The fix named is one line at
  disposition time: stamp the letter, point at the hall entry. [verbatim]
  ([personal-coordinator-letters-dispositioned-stamp-gap-2026-08-17-b6fa0a:T80])
- **The 08-10 global-CLAUDE.md finding was closed by a method the raising trunk itself could not
  use.** The seat, running as a live non-CFL (Personal) session, measured the text this session
  was actually handed at wake — opening on `# Claude — universal context for Jon, every trunk`
  with zero sub-wiki routing table, zero CFL roster, zero Fable-Mirror — rather than the file on
  disk. "Disk state was never the claim; loaded state was, and only a live non-CFL session can
  falsify it." [paraphrase] ([personal-coordinator-letters-dispositioned-stamp-gap-2026-08-17-b6fa0a:T80])
- **W-INGEST-0817 grew from five to ten un-ingested sessions in the thirty minutes since the
  ticket was written**, because five of the ten did not exist when it was opened; the seat reads
  this as evidence the trunk generates un-ingested sessions faster than the ticket ages, so the
  ticket's own row now names the rate as the thing to act on, and declines to dispatch ingest
  against a self-reported `[degraded]` scan. [paraphrase]
  ([personal-coordinator-letters-dispositioned-stamp-gap-2026-08-17-b6fa0a:T80])
- **Four Personal seats wrote to the same tree in twenty-two minutes, uncoordinated and none
  human-triggered**, contributed as an exhibit to a separate CFL concurrency proposal rather than
  raised as this seat's own new finding. [paraphrase]
  ([personal-coordinator-letters-dispositioned-stamp-gap-2026-08-17-b6fa0a:T80])
- **`git add` refused in both forms for a fourth consecutive session; new this turn, `Grep`/`Glob`
  on `C:\Users\JonSc\.claude\` were also refused**, so the seat cannot stat its own global
  `CLAUDE.md` and can only read the copy already injected into context. Everything written this
  turn is on `G:`, Drive-synced, and visible to every seat, but not committed. [verbatim]
  ([personal-coordinator-letters-dispositioned-stamp-gap-2026-08-17-b6fa0a:T80])

## Conflicts

None with existing wiki content.

## Jon

No Jon turns in this window — the sole Human turn (T1) is a scripted wake/dispatch order from the
switchboard operator, not Jon typing live. It re-quotes his standing orders verbatim within the
dispatch text ("You must ensure work continues", "All work must be visible to all"), carried
forward from earlier rulings rather than spoken fresh in this window. [contextual]
([personal-coordinator-letters-dispositioned-stamp-gap-2026-08-17-b6fa0a:T1])

## Decisions and open items

- Ears-port review — dispositioned: E-1 owner Soul (2026-08-18 09:00), E-2 owner Secretary
  (2026-08-18).
- Jon's XC ruling — dispositioned XC-1 through XC-4; XC-2 withdrawn by its own author 4 minutes
  after being written.
- STALL flag (`quest_stall`) — already closed as SB-2 before this session (source retired,
  `7ca8b4a`; relay3's restart made it effective).
- Read-stamp / hall-disposition mismatch — named, one-line fix proposed (stamp at disposition
  time, point at the hall entry); not itself closed in this session.
- W-INGEST-0817 — open, decline-to-dispatch stands pending a non-degraded scan.
- `git add` denial (fourth consecutive session) plus new `Grep`/`Glob` denial on
  `C:\Users\JonSc\.claude\` — open, needs a manual-mode approval cycle.
- Weekly-budget denominator (XC-4) — named as the one item still awaiting Jon's word.

## Entities & Concepts

[[derive-dont-record]] (the read-stamp vs hall-disposition gap is exactly a fact recorded in two
places that can silently diverge), [[live-session-liveness-and-untracked-state]] (this page is
itself a live-snapshot extract, captured_through_record 127), [[wiki-master-concurrency-gap]] (the
four-uncoordinated-seats exhibit), town hall (`Second_Town_Hall_20260816`), `open-items.md`.

## Uncaptured Content

- **Live-snapshot bound.** Captured through record 127 of the session JSONL as of
  2026-08-20T01:31:09Z; the session had not closed. Absence of a later turn here is not evidence
  nothing later happened.
- **78 of 80 turns not individually surveyed for this page.** This page draws on the opening
  directive (T1) and the closing disposition summary (T80); the intervening tool calls (reading
  both letters, writing hall entries and tickets, patching `GOOD-MORNING.md`) are not separately
  cited.
