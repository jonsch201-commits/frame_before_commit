---
title: "Herald's second machine-triggered wake: quest_stall retired as a wrong published cause, a documentation edit that would have killed the relay caught before running, and MIRROR-STATE v28 authored by main because dispatch was instructed off — Personal, 2026-08-17 (8db3d5)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 8db3d5
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-8db3d5-switchboard-wake-delivered-by-the-secretary-on-jon.md
raw_sha256: 61f59017c0a49240754fbaf8373f4556d05bce97959723233d518f04536292a0
raw_length: 193386 chars / 3762 lines (verified turn_count 186, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5
aliases: ["quest_stall RETIRED wrong published cause", "sources[] near-miss core3.mjs",
  "MIRROR-STATE-CURRENT v28", "XC mandate accepted Herald 2026-08-17"]
generated_by: S-aug-08 executor (synthesis lane, week map RP-3/RP-4), reading the live-snapshot
  extract directly (raw/transcripts/claude-code/code-2026-08-17-8db3d5-...md, captured_through_record 267)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [personal-trunk, herald, switchboard-wake, mirror-state, quest-stall, xc-mandate, cfl-infra,
  live-snapshot]
---

# Herald's second machine-triggered wake — quest_stall retraction, sources[] near-miss — 2026-08-17 (8db3d5)

## Summary

Personal's Herald seat was woken a second time by the switchboard on Jon's own 13:1x order — the
session's first-ever wake by machine rather than by keystroke. The session found that a code-level
fix already existed for the `quest_stall` false-positive it had itself diagnosed and committed hours
earlier, retracting its own prior published cause. It also caught, before executing, a documentation
edit of its own that would have thrown a fatal type error at the next relay restart. It accepted a
new XC-coordination mandate from Jon while correcting two of its own premises about XC's silence and
leverage, confirmed a drain-stamp finding from a peer (Soul), and closed by authoring
`MIRROR-STATE-CURRENT.md` v28 itself rather than dispatching the `fable-mirror` consult the standing
hook calls for, because this session was under an explicit standing instruction not to dispatch
agents unless asked. This is a live-snapshot capture (through record 267); the session had not
closed when captured.

## Key Claims

- **`quest_stall` retired: the cause this session itself published 80 minutes earlier was wrong.**
  Grepped this turn: `lastLineHasEndingRun()`, an exact terminal-state predicate, exists in
  `core2.mjs:299` and `core3.mjs:299` since commit `0cb504a` (08-15) and is absent from `core.mjs`
  (0 hits); `core3.mjs:258` runs it before the stall fires, and the tracked STATUS.md's last line
  already ends "ending run." The session's own prior commit `9c9845d` had stated the source "cannot
  tell stopped-because-failed from stopped-because-finished" — true of the config block, false of
  the code — and explicitly names that retiring the block instead of the claim "would have silenced
  the symptom and certified the drift." Marked DERIVED, NOT OBSERVED, since the live process table
  could not be read from this seat. [verbatim]
  ([herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5:T184])
- **A near-miss caught before it could run: a documentation comment placed inside `sources[]` would
  have thrown a fatal type error at the next relay restart.** `core3.mjs:184` runs
  `path.isAbsolute(src.path)` on every array element; an object with no `path` field throws
  `ERR_INVALID_ARG_TYPE`. The session states this was "caught by reading the loop, not by running
  it — which was lucky, since running it was not available" (this session's permission mode refused
  script execution entirely), and writes a rule into the config that `sources[]` holds sources only.
  [verbatim] ([herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5:T184])
- **Both Secretary-suggested "ears port" fixes were applied with one deliberate divergence, and
  neither fix has been run yet.** For the low-length dedup case, the session implemented sha1-stamp
  exact matching instead of the suggested substring test, to avoid appending every short message on
  every run forever; a live measurement (662 raw `queued_command` hits in Personal's JSONL tree) was
  used to size a new counter shape. Status recorded explicitly:
  `REVIEWED-WITH-FINDINGS-APPLIED-BUT-UNFIRED`, citing the standing rule that "a fix nobody reviews
  is a claim." [verbatim] ([herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5:T184])
- **The XC mandate is accepted, with two of the session's own premises corrected in the same turn.**
  A claim the session nearly published — "XC is not silent — it wrote today" — is retracted: the file
  in question was Soul's, merely deposited in XC's drop, so "XC itself has not spoken," named
  explicitly as the same class of error as "author-login is not authorship." A second claim ("XC is
  formally OUT with no switchboard lever") is called false as stated: the lever exists in XC's
  constitution but requires a session to open in XC, which only Jon can do. [verbatim]
  ([herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5:T184])
- **Nothing in this turn is committed, and nothing could be run — the session names this before
  anything else.** Roughly eleven denials are recorded across execution and git-write attempts (no
  script, no `python -c`, no `bash -n`, every `git add` formulation refused). The session states the
  town hall is still visible because it is a shared file every seat appends to directly, but the
  commit and push are missing; six named artifacts sit uncommitted on disk with the claim that "any
  seat with commit rights can land it as-is; nothing needs redoing." [verbatim]
  ([herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5:T184])
- **`MIRROR-STATE-CURRENT.md` v28 was authored by main, not staged by the fable-mirror consult the
  standing hook calls for, and the session states explicitly why**: it was under a standing
  instruction this session not to dispatch agents unless asked, so "read that as a consult NOT RUN,
  never as a consult that returned nothing." [verbatim]
  ([herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5:T186])

## Conflicts

None with existing wiki content.

## Jon

The wake order itself (this session's own first turn) carries a verbatim Jon quote relayed through
the Secretary's switchboard, marked "verbatim" in the order text: "'You must ensure work continues.'
/ 'Progress can't rely on me looking at my phone.'" [verbatim]
([herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5:T1])

A further Jon utterance ("Herald should be coordinating XC work," ~13:1x) is referenced in this
session's own summary as the basis for accepting the XC mandate, but its exact wording is not quoted
in the turns captured on this page. [uncaptured]
([herald-mirror-v28-quest-stall-retired-2026-08-17-8db3d5:T184])

## Decisions and open items

- Closed: the `quest_stall` false-positive cause retracted and replaced with the code-level fix
  finding; the `sources[]` documentation near-miss caught and a config rule written to prevent
  recurrence; both ears-port fixes applied (status UNFIRED, pending the next Stop/PreCompact
  boundary).
- Accepted: the XC-coordination mandate, with the token/turn ledger (not household money) taken into
  Personal's own tree, target 2026-08-19; household-money "Lane B" stays XC's and gated.
- Confirmed: Soul's drain-stamp finding, against the artifact, with a rule adopted narrowing what
  this seat stamps to mail addressed to it.
- Open, named explicitly as not done: a SessionStart wiki-ingest signal — four Personal JSONLs
  unreflected in `wiki/sources/sessions/`, two with no current Drive copy — enqueued but
  unwatermarked, blocked on this session's execution permissions.
- Open: manual-mode approval needed to actually commit and push the session's uncommitted writes.
- This page is a live-snapshot extract captured through record 267 of the session JSONL; anything
  after that record is not represented here and is not claimed to be absent from the real session.

## Links

[[fable-mirror]] (this session explicitly declines to dispatch a fable-mirror consult and states why,
the exact SIGNAL/NOTICE distinction the mirror charter turns on), [[mirror-stateless-dispatch-only]]
(the standing-instruction-not-to-dispatch constraint this session operates under), quest_stall relay
false-positive, XC-Exchequer coordination mandate.
