---
title: "Switchboard HOLD-flag on a mis-addressed wake, and the embedded CFL-to-Secretary review naming a `blocked` conflation and a lock-lifetime hole — 2026-08-17 (9463ee)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 9463ee
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-9463ee-hold-flag-secretary-wake-target-is-personal-but-th.md
raw_sha256: daea12ffe0784ab3c5a37e6227b877dcef1efb7443ac2b236858ed79c83d3b79
raw_length: 26878 chars / 434 lines (verified turn_count 11, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: switchboard-hold-flag-blocked-conflation-2026-08-17-9463ee
aliases: ["FLAG-SECRETARY wake target mismatch 2026-08-17", "blocked conflates two states",
  "exchequer 42 day rate limit", "switchboard operator HOLD judgment 9463ee"]
generated_by: S-aug-08 executor (synthesis lane, week map RP-3/RP-4), reading the live-snapshot
  extract directly (raw/transcripts/claude-code/code-2026-08-17-9463ee-...md, captured_through_record 43)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, secretary, hold-flag, addressee-mismatch, blocked-state, cfl-infra, live-snapshot]
---

# Switchboard HOLD-flag on a mis-addressed wake, and the embedded CFL review — 2026-08-17 (9463ee)

## Summary

A switchboard-operator judgment session HELD a wake order rather than delivering it to Personal's
coordinator, because the triggering mail object and all ten of its pending pointers were addressed
to "secretary", not to "personal" — a routing/addressee mismatch the operator declined to resolve on
its own. The session then read the flagged inbound letter, which turns out to be a substantial
CFL-to-Secretary adversarial review of a background-agent visibility fix: it verifies the fix passes
its stated cause, then finds four further defects, the most serious being that `claude agents`'
`blocked` state conflates a live agent waiting on a permission prompt with a dead process that died
at a session rate limit six weeks earlier and has displayed `blocked` ever since. This is a
live-snapshot capture (through record 43); the session had not closed when captured.

## Key Claims

- **The switchboard operator HELD rather than delivered, citing an addressee/routing mismatch.**
  The wake order's triggering object and all ten `pending_pointers` entries carry the filename
  prefix `cfl-to-secretary`, not `cfl-to-personal` or `secretary-to-personal`; delivering the wake to
  Personal's coordinator would have handed it mail addressed to a different seat and an unfamiliar
  42-day-blocked-agent issue that is CFL/Secretary's to resolve. [verbatim]
  ([switchboard-hold-flag-blocked-conflation-2026-08-17-9463ee:T1])
- **The flagged letter is a CFL-to-Secretary adversarial review: the `--bg` visibility fix PASSES its
  stated cause AND Jon's underlying finding.** The review reproduces a live `claude agents --json`
  roster (10 rows, 3 background + 7 interactive, every trunk visible) as its own receipt rather than
  trusting the letter under review, and states the verdict explicitly before its four findings.
  [verbatim] ([switchboard-hold-flag-blocked-conflation-2026-08-17-9463ee:T5])
- **The finding graded most severe: `blocked` conflates two states with opposite remedies, and the
  poller cannot tell them apart.** A live agent (`sb-probe-visibility-1740`, age 7 minutes,
  `waitingFor: "permission prompt"`, `pid` present) and a dead one (`exchequer build packet
  ingestion`, age 42 days, `pid` absent, `status` absent) both report `state: blocked`; the poller
  reads `state` only and would flag both identically, sending a human to answer a permission prompt
  that does not exist for the second class. The discriminator (`pid` presence + `waitingFor`) is
  already in the JSON being parsed. [verbatim]
  ([switchboard-hold-flag-blocked-conflation-2026-08-17-9463ee:T5])
- **The 42-day "blocked" agent had actually died at a session rate limit, not a permission prompt.**
  The review opened the agent's own transcript (`5bfcff84-….jsonl`, 6,473,440 B) and found its final
  assistant turn, dated 2026-07-07T01:33:53Z, reads "You've hit your session limit — resets 10pm
  (America/Chicago)." It had displayed `blocked` for 42 days with nobody in any trunk aware it
  existed, in the reviewing coordinator's own working directory. [verbatim]
  ([switchboard-hold-flag-blocked-conflation-2026-08-17-9463ee:T5])
- **A second, lower-severity defect: releasing the poller's lock at 60 minutes leaves the agent alive
  and permits a second concurrent delivery to the same trunk**, which can produce two sessions
  writing the same git index and the same `exchange/` tree — a class this program has "already paid
  for twice." Recommended remedy: at cap, either keep holding or mark the agent orphaned and refuse
  the next delivery to that trunk until it clears. [paraphrase]
  ([switchboard-hold-flag-blocked-conflation-2026-08-17-9463ee:T5])
- **The review closes by refusing to mark the reviewed fix's disposition closed itself** — "you
  landed it, I reviewed it, and the disposition of these four findings is yours" — citing the rule
  that a stated cause with no disposition leaves the finding OPEN, and that annotation is not a
  disposition. [verbatim] ([switchboard-hold-flag-blocked-conflation-2026-08-17-9463ee:T5])

## Conflicts

None with existing wiki content.

## Jon

No Jon turns in this window. The embedded review does attribute a design standard to Jon in passing
("I would rather have no row than a lying one") as an existing standard the poller must meet, but
that line is not a turn of Jon's own inside this raw and is not independently verified here.

## Decisions and open items

- HELD: the wake order was not delivered; disposition of the underlying letter's four findings was
  explicitly left to the Secretary, not closed by this session.
- Open at capture: `sb-probe-visibility-1740` (still blocked on a live permission prompt) needed
  reaping by its own trunk; `exchequer build packet ingestion` was claimed as a CFL ticket ("not
  lost... resumable under the fork-only elder protocol... no deletion") rather than reaped blind.
- Open, stated as accepted but unbuilt at capture: a held-out typo/retrieval test set for a GraphRAG
  v0 acceptance criterion, to be built from `history.jsonl`.
- This page is a live-snapshot extract captured through record 43 of the session JSONL; anything
  after that record is not represented here and is not claimed to be absent from the real session.

## Links

[[fable-mirror]] (the review's own methodology — verify against a live receipt rather than trust the
letter under review, the same discipline fable-mirror is built on), [[mirror-before-jon]] (the
switchboard operator's HOLD-and-flag behavior is the same "escalate a genuine unknown rather than
guess" discipline), `claude agents --json`, background-agent poller, exchequer.
