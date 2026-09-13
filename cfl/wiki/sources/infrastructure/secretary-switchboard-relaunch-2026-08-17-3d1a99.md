---
probe_sealed: "What order did Jon give the Secretary right after it was compacted and its model
  set to Fable on 2026-08-17, and what did the checkpoint critic branch find wrong with the
  session's own claim to him that the stack was verified end to end? expected_class: TRUSTED"
title: "Secretary wakes post-compact, launches the switchboard on Jon's word, critic branch finds three defects (CFL session 3d1a99, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 9 vs fleet 5 on authored labels"
uuid6: 3d1a99
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-3d1a99-run-reading-beat-and-write-brief.md
raw_sha256: ae58f0bf058d74e9175e3814897f8ac9858ea207e905b61aba8ad51313b33004
raw_length: 314655 chars / 5874 lines (verified turn_count 351, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: secretary-switchboard-relaunch-2026-08-17-3d1a99
aliases: ["switchboard on, secretary is lead", "run reading beat and write brief",
  "precompact-handoff hook", "critic branch F1 F2 F3 2026-08-17", "25 percent standing max"]
generated_by: S-aug-05 executor (week-2026-09 corpus lane), reading the live raw directly
  (raw/transcripts/claude-code/code-2026-08-17-3d1a99-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, secretary-trunk, townhall, precompact-hooks, critic-branch, ears-discipline]
---

# Secretary wakes post-compact, launches the switchboard, critic branch finds three defects

## Summary

A CFL Secretary-trunk session (`9a25daa7-9330-4e89-868d-ead1e367b3b2`) resumes from a mid-session
compaction — the compaction summary (turn 1) recaps a long prior stretch of "SECRETARY CODE SEAT —
TOWN HALL RELAUNCH PREP" work (a 54-fragment Jon work order, hook fixes, an Anthropic-export
absence report, a launcher-frontmatter bug fix) that this page treats as `[reconstructed]` since
it is the machine's own summary, not raw dialogue. After the resume, Jon (via slash commands
setting model to Fable and effort to medium) gives a direct verbatim order to launch the
switchboard and be a better secretary than before. The session builds and exercises a
`precompact-handoff.ps1` hook in both directions, writes a ruling file capturing Jon's order with
a branch-by-branch disposition ledger, and — near its own 25%-context ceiling — forks a
"checkpoint critic branch" that returns three adversarial findings against the session's own
claims to Jon.

## Key Claims

- **Jon's direct order to launch the switchboard, quoted verbatim, no emphasis added inside the
  quote itself.** [verbatim] ([secretary-switchboard-relaunch-2026-08-17-3d1a99:T12])
- **The precompact-handoff hook was built and exercised both directions: a real failure, then a
  real pass, then a real negative control.** First fire hit `exit=4` on an illegal trailing
  backslash in a `-notlike` pattern (`'\scratchpad\'`); after the regex fix, `exit=0` writing a
  9,885-byte `HANDOFF-CURRENT.md` in 7 sections; a negative control that aged `NEXT-ACTIONS.md` to
  45 minutes behind Jon's last message correctly printed a STALE warning, and separately flagged
  `BRIEF-CURRENT.md` as 710 minutes stale. [paraphrase]
  ([secretary-switchboard-relaunch-2026-08-17-3d1a99:T2])
- **A self-conceded retrieval-gap pattern, stated to Jon in-session.** The session told Jon its own
  PreCompact chain already mirrored 116 MB of transcripts and wrote a recovery pointer, but it had
  asked Jon to seal it manually instead — "That information was in my own `scripts/` directory and
  its own log file. Not hidden. Not missing. Just never retrieved. Third instance today of the same
  class." [verbatim, contextual attribution] ([secretary-switchboard-relaunch-2026-08-17-3d1a99:T2])
- **Jon's switchboard-launch order was captured to a ruling file with a per-branch disposition
  ledger** (ACTIONED / ANSWERED / PARKED-with-default per clause), following the session's own
  "ears discipline" — every Jon branch gets a row, not a paraphrase. The relay
  (`node relay.mjs run --no-llm`) was started as a background task (b1fe0nbk6) at 11:42 CDT, owned
  by the Secretary rather than routed to a separate Opus sub-seat, on the session's own reasoning
  that a zero-token relay process costs the Secretary nothing to hold directly. [paraphrase]
  ([secretary-switchboard-relaunch-2026-08-17-3d1a99:T43])
- **A standing self-imposed context ceiling was set without a fresh ruling request.** "25% is now
  this seat's standing max — I'll seal and compact on my own initiative when I approach it, no
  ruling needed next time." [verbatim] ([secretary-switchboard-relaunch-2026-08-17-3d1a99:T346])
- **A forked checkpoint-critic branch returned three findings against the session's own claims to
  Jon, per Herald's four-hook-moments design and the session's own "ears" rule** (a Jon message
  branch with no ledger row is a defect the ledger exists to prevent): (F1) the claim "full stack
  is now running and verified end to end" was unproven — the operator's log showed zero
  `DELIVER ->` lines and zero Opus judgment invocations, so the sub-secretary was "wired, not
  proven"; (F2) a PreCompact hook (`index-check.ps1`) failed at session start and was never
  ticketed, even as the session told Jon "all five PreCompact hooks have fired live today"; (F3)
  today's Jon branches were absent from `rulings/jon-branch-ledger.md` (last written 2026-08-16
  22:51 against roughly 12 Jon messages the next day), including one message ("Manual mode on.
  Change the setting now.") with no verbatim primary in any ruling file. [verbatim, self-critique
  turn] ([secretary-switchboard-relaunch-2026-08-17-3d1a99:T351])

## Jon

- ([secretary-switchboard-relaunch-2026-08-17-3d1a99:T12]) "Wake. Launch and own the switchboard.
  You are my secretary and you are lead. You learned many lessons as an Opus before compact, keep
  my time protected and support the others and help them use best practices. Ensure all attend
  townhall and that all have the ability to meaningfully support each other. Launch and own my
  switchboard. Be a better secretary as a Fable than you were as an Opus, and consider protecting
  your context by having an Opus secretary of your own run the switchboard. Go! We are live! Turn
  the switchboard on!"

Earlier in the same session (per the compaction summary, `[reconstructed]`, not independently
verified against raw dialogue on this page), Jon is recorded as having said, among other things:
"Item 4 you are making clear you should have fixed with support with other trunks. By raising it
to me, you've been assigned the primary owner." and "Soul is just ensuring the resident is ready.
This is all fucking pre work for the town hall." — both flagged `[reconstructed]` since this page
draws them from the model's own compaction summary rather than reading the pre-compaction raw
turns directly.

## Decisions and open items

- **DECIDED (this window):** switchboard turned on, relay started as a background task owned by
  the Secretary directly, no separate Opus sub-seat spun up for it (deferred, "revisit if wake
  volume grows").
- **DECIDED (this window):** the session's own context ceiling — seal and compact at 25%, no
  further ruling needed.
- **OPEN, per the critic branch's own F1:** the switchboard operator's DELIVER path (Opus
  judgment → `claude -p`) was, as of this window, wired but never exercised by a real wake — the
  claim "verified end to end" made to Jon at ~13:31 outran what the log actually showed.
- **OPEN, per F2:** `index-check.ps1`'s PreCompact failure, visible in this session's own first
  local-command-stdout block, was never ticketed or disposed.
- **OPEN, per F3:** `rulings/jon-branch-ledger.md` was stale relative to same-day Jon messages,
  and at least one Jon message ("Manual mode on. Change the setting now.") had no verbatim primary
  recorded in any ruling file as of this window.

## Conflicts

None with existing wiki content.

## Uncaptured Content

- The pre-compaction portion of this session (everything before turn 1's compaction summary) is
  represented on this page only through the machine's own `[reconstructed]` summary, never through
  independently-read raw dialogue — the underlying JSONL is named in the summary
  (`C:\Users\JonSc\.claude\projects\...\9a25daa7-...jsonl`) but was not opened for this page.
  Anything the summary omitted or compressed is not represented here at all.
- Turns between T14 (switchboard launch begins) and T346 (the 25%-ceiling note) — roughly 330
  turns of tool calls and townhall-preparation work — were not individually surveyed for this page;
  this page draws only on the session's open (T1-T14), one mid-session ruling write (T43), and its
  close (T346-T351).

## Links

- [[probe-registry]] — the negative-control discipline this session's own `precompact-handoff.ps1`
  test run instantiates (age the intent file, confirm the hook actually flags STALE).
- [[derive-dont-record]] — the self-conceded pattern at T2 ("Not hidden. Not missing. Just never
  retrieved. Third instance today of the same class.") is the same failure mode this wiki concept
  names.
