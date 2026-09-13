---
title: "Silent-success PreCompact hooks make the Secretary's continuity apparatus untrusted — reading-beat session, 2026-08-17/18 (3bafc5)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 3bafc5
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-18-3bafc5-run-reading-beat-and-write-brief.md
raw_sha256: 5cc1741319cf7bc8f7daf049dd46b1cdbd65b886581745812326259bba47e28f
raw_length: 59720 chars / 755 lines (verified turn_count 31, turn_index.py, header_style md)
date: 2026-08-18
retrieval_key: silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5
aliases: ["343 vs 34 ears ledger", "silent-success PreCompact hooks", "continuity apparatus untrusted", "run reading beat and write brief 2026-08-18 3bafc5", "su-compact interpretation missed"]
generated_by: "S-aug-02 executor, reading the raw extract directly (raw/transcripts/claude-code/code-2026-08-18-3bafc5-run-reading-beat-and-write-brief.md)"
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [secretary, continuity, hooks, silent-success, critic-branch, cfl-infra]
probe_sealed: "During this session's /compact at ~22:07 CDT, how many of five PreCompact hooks reported success, and how much did they actually write? => Four reported 'completed successfully' but the measured artifacts (HANDOFF-CURRENT.md, precompact-handoff.log, COMPACT-RECOVERY.md, newest critic file) all still carried a prior 19:08:04 timestamp — nothing was written by the 22:07 run. TRUSTED"
---

# Silent-success PreCompact hooks make the Secretary's continuity apparatus untrusted — 2026-08-17/18 (3bafc5)

## Summary

This session opens with a compaction-boundary summary of an earlier portion (Herald's switchboard
rollback verdict, not reproduced here), then Jon runs `/compact` and, distrusting the result,
challenges the Secretary directly on whether its own continuity apparatus can be trusted. The
Secretary measures rather than reassures: it finds the just-run `/compact` fired five PreCompact
hooks, four of which reported "completed successfully," while every artifact those hooks were
supposed to write (`HANDOFF-CURRENT.md`, `precompact-handoff.log`, `COMPACT-RECOVERY.md`, the newest
critic file) still carried an earlier 19:08:04 timestamp — meaning the 22:07 run wrote nothing
despite reporting success. It also measures a 343-vs-34 gap between Jon's captured arrival stamps
and disposed ears-ledger rows, 26 undispositioned critic-hook findings, and 12 memory files against
88 total Secretary session JSONLs. The Secretary writes a finding, assigns three owners (CFL,
Professional, Herald) with dated acceptance tests, couriers it to three trunk inboxes, and saves a
memory. A subsequent "checkpoint critic branch" fork (an automated Stop-hook process, not Jon) then
adversarially reviews that very deliverable and finds three real gaps: the failure's timestamp was
never independently pinned, the session dispositioned zero of Jon's own message branches while
assigning that exact backfill to someone else, and the word "su-compact" in Jon's message was never
interpreted or searched for, only answered around.

## Key Claims

- **Silent-success PreCompact hooks: four of five reported success and wrote nothing.**
  `HANDOFF-CURRENT.md`'s own header line reads "written by the PreCompact hook at 2026-08-17
  19:08:04," matching its mtime; `precompact-handoff.log`'s last line is the same 19:08:04 entry
  with no 22:07 line at all, success or failure; `COMPACT-RECOVERY.md` and the newest
  `thought/critic/` file are both 19:08. The one hook that reported "failed" (`index-check.ps1`) is
  the only one that was telling the truth, and firing it by hand still exits 0 despite finding four
  problems — so even its own pass/fail signal is unreliable without a fire-and-diff. [verbatim]
  ([silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5:T22],
  [silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5:T27])
- **343 Jon arrival stamps vs 34 ears-ledger disposition rows — roughly 90% of his captured words
  have no recorded disposition**, and the newest arrival (22:07:23) postdates the last ledger write
  (14:24:42) by 7.7 hours. [contextual] ([silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5:T21])
  [source: `index-check.ps1` fired by hand, this raw, T21]
- **Three dated assignments issued, not built by the Secretary itself.** CFL owns root-cause +
  making every hook "write-proving" (a heartbeat carrying the same stamp it claims), due 2026-08-18
  12:00 CDT, acceptance: a deliberately-broken hook must fail visibly at next session open.
  Professional owns backfilling the ears ledger across all 88 JSONLs verbatim, due 2026-08-18 18:00
  CDT, with a positive-control synthetic Jon turn that must come back UNPARSED. Herald owns a
  cross-instance continuity audit — what a later Secretary instance lost that an earlier one knew —
  due 2026-08-19 12:00 CDT. [paraphrase] ([silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5:T22])
- **The finding shipped without peer review and said so.** The letter (couriered to Personal, CFL,
  and Professional inbounds) explicitly states it ships unreviewed because the finding is about the
  very mechanism the review round-trip would use, names Professional as the assigned reviewer of
  its own root-cause diagnosis, and states the letter is cited as UNREVIEWED until that lands.
  [paraphrase] ([silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5:T22])
- **A critic-branch fork (an automated Stop-hook process, snapshotting the session — not a Jon
  turn) found three real defects in the deliverable it reviewed**, none dropped after the critic's
  own refutation attempt: (1) the claimed 22:07:39 compact-failure time was never independently
  pinned to a receipt — the session's own narrative inferred it, and the rollback courier's mtime
  that could have confirmed it was never read; (2) the session dispositioned zero branches of Jon's
  own 22:07 message even while assigning that exact backfill task to Professional; (3) the term
  "su-compact" in Jon's message was never interpreted or searched for in the trunks before being
  treated as a non-existent thing, violating the standing rule to state an interpretation of
  fragmented phrasing before asking. [verbatim] ([silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5:T31])

## Conflicts

None with existing wiki content.

## Jon

Jon's live turn in this window, verbatim, typos his ([silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5:T6]):

> "oh my god you don't have su-compact and i don't trust that compact does for you that it should and you are not the first json of the secretary i am not confident your memories/logs are complete and accurate."

## Decisions and open items

- **Open (owner CFL, due 2026-08-18 12:00 CDT):** establish the root cause of the silent-success
  PreCompact hooks and make every Secretary hook write-proving.
- **Open (owner Professional, due 2026-08-18 18:00 CDT):** backfill the 343-vs-34 ears-ledger gap
  across all 88 Secretary session JSONLs, verbatim, with a planted positive control.
- **Open (owner Herald, due 2026-08-19 12:00 CDT):** cross-instance continuity audit — name at
  least three losses across the 88 sessions, or an explicit "searched X, found none."
- **Open, raised by the critic branch, not yet assigned an owner on this page:** independently pin
  the 22:07 compact-failure timestamp against the session JSONL's own compaction-boundary event and
  the rollback courier's file mtime, neither of which had been read as of this session's close.
- **Open, raised by the critic branch:** the term "su-compact" in Jon's message was never
  interpreted or searched for — a live gap in this session, disposition unknown from this raw alone.
- Until the write-proof lands, the Secretary states it will stop citing `HANDOFF-CURRENT.md`,
  `NEXT-ACTIONS.md`, or the ears ledger as evidence of anything, labelling them UNTRUSTED and
  deriving state instead from primaries (git log, file mtimes, the switchboard ledger, the JSONLs
  themselves).

## Links

[[probe-registry]] — the same seal-before-run, receipt-over-reassurance discipline this session's
own measurement pass follows before it will trust its compact apparatus again.

## Entities & Concepts

Secretary trunk, PreCompact hooks, ears ledger (`rulings/jon-branch-ledger.md`), checkpoint critic
branch (Stop-hook fork), `HANDOFF-CURRENT.md`, `index-check.ps1`.

## Uncaptured Content

- **This raw opens on a `## Compaction Boundary` block** — the machine's own auto-generated summary
  of an earlier portion of the session (largely Herald's switchboard rollback verdict). That block
  is not reproduced as a Key Claim here and is not Jon's words; anything drawn from it would be
  [reconstructed] at best, and this page draws nothing load-bearing from it.
  ([silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5:T1])
- **8 thinking blocks exist in the raw and are encrypted-in-signature** (per the raw's own
  extraction note) — not recoverable client-side; no claim on this page draws on the session's
  private reasoning, only its visible tool calls and final messages.
- **The critic branch's three findings (T31) are, on this page, reported as findings raised — this
  page does not independently verify whether the compact-failure timestamp was ever subsequently
  pinned, or whether "su-compact" was ever interpreted, in a LATER session not covered by this raw.**
