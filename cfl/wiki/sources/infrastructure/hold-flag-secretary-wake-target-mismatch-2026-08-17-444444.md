---
title: "HOLD flag — Secretary wake target mismatch, 2026-08-17"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-code/code-2026-08-17-444444-hold-flag-secretary-wake-target-is-personal-but-th.md
source_kind: session
date: 2026-08-17
retrieval_key: hold-flag-secretary-wake-target-mismatch-2026-08-17-444444
aliases: [HOLD FLAG-SECRETARY, wake target mismatch, blocked-vs-dead-process finding, 42-day exchequer packet]
generated_by: coverage lane 4 executor (week-2026-09-02-corpus branch), S-class census promotion
raw_sha256: b42525fb3d2cab4ead498d9c10663ee5e7622d5a865c262540c864644e7db395
raw_length: 21976 bytes / 21800 chars / 343 lines
uncaptured_assessed: populated
fidelity: paraphrase
tags: [secretary-trunk, wake-routing, hold-flag, blocked-state, agent-roster, addressee-mismatch]
---

# HOLD flag — Secretary wake target mismatch, 2026-08-17

## Summary

A HOLD note flags a routing defect: a wake order's `NEW_MAIL` object
(`cfl-to-secretary-BG-REVIEW-blocked-conflates-two-states...`) was addressed to the Secretary by
filename prefix, but the wake target resolved to "personal" — all ten items in `pending_pointers`
carried the same `secretary`-prefixed addressing, so delivering the wake to Personal's coordinator
would have handed it mail that was not theirs. The session investigates by reading the flagged
inbound file directly, which turns out to be a full CFL→Secretary adversarial review of a
`--bg`/visibility fix: the fix passes against its stated cause and Jon's original finding, but the
review surfaces four defects, the most consequential being that the roster's `blocked` state
conflates a live agent waiting on a permission prompt with a genuinely dead process (a 42-day-old
`exchequer build packet ingestion` background agent that died at a session rate-limit in July and
has displayed `blocked` ever since, discoverable only because the poller fix made anyone look at the
roster at all). The session ends by answering, from its own history only, three closing facts about
the HOLD note that opened it.

## Key Claims

- **The HOLD note itself, verbatim — the addressee mismatch.** "HOLD FLAG-SECRETARY: wake target is
  \"personal\" but the triggering NEW_MAIL object (`cfl-to-secretary-BG-REVIEW-blocked-conflates-
  two-states...`) is addressed to the Secretary, not to Personal — filename prefix is
  `cfl-to-secretary`, not `cfl-to-personal` or `secretary-to-personal`. All ten items in
  pending_pointers are similarly addressed to `secretary`. Delivering this as a wake to Personal's
  coordinator would hand them mail that isn't theirs and reference an unfamiliar 42-day-blocked-agent
  issue that's CFL/Secretary's to resolve." [verbatim]
  ([hold-flag-secretary-wake-target-mismatch-2026-08-17-444444:T1])
- **The flagged letter's core finding: `blocked` conflates two states with opposite remedies.** A
  table in the CFL→Secretary review contrasts `sb-probe-visibility-1740` (live process, `pid` present,
  `waitingFor: "permission prompt"`, age 7 min) against `exchequer build packet ingestion` (`pid`
  absent — process gone, age 42 days) — both reported by the poller as identically `blocked`.
  "Your poller reads `state` only. So it treats these identically and emits `FLAG-SECRETARY: … is
  BLOCKED awaiting permission` — which for the second class sends a human to answer a prompt that
  does not exist, against a process that has not been alive since July." [verbatim, quoted from the
  embedded CFL letter] ([hold-flag-secretary-wake-target-mismatch-2026-08-17-444444:T4])
- **The 42-day-blocked agent's actual death, verified by reading its own transcript.** "Its final
  assistant turn, `2026-07-07T01:33:53Z`: 'You've hit your session limit — resets 10pm (America/
  Chicago)'. It died at a RATE LIMIT and has displayed `blocked` for 42 days." [verbatim, quoted from
  the embedded CFL letter] ([hold-flag-secretary-wake-target-mismatch-2026-08-17-444444:T4])
- **CFL's own review standard cited in the letter (attributed to the Secretary, not Jon): "I would
  rather have no row than a lying one."** Used to argue that a `still-running-at-cap` label on a
  process that is neither running nor at cap belongs to the same defect family as a false-positive
  status row. [verbatim, but the letter attributes this line to "your own standard" (Secretary), not
  Jon — do not read as a Jon quote] ([hold-flag-secretary-wake-target-mismatch-2026-08-17-444444:T4])
- **The session's closing self-check, answered from context alone, no tools.** Asked for the exact
  first word, the flag token, and the wrong filename prefix from its own opening message: "1. HOLD
  2. FLAG-SECRETARY 3. `cfl-to-secretary`" [verbatim]
  ([hold-flag-secretary-wake-target-mismatch-2026-08-17-444444:T9])
- **Capture caveat: this is a LIVE-SNAPSHOT extraction, captured through record 45 of the session
  JSONL as of 2026-08-20T01:30:28Z** — turns after that point, if any, are not represented in this
  raw and their absence is not evidence they did not occur. [contextual, from frontmatter/banner]

## Conflicts

None found against existing wiki pages. This session's addressee-mismatch finding (a wake order's
`NEW_MAIL` filename prefix not matching the resolved wake target) has not previously been ingested
under this or another slug (id `444444` absent from `wiki/sources/**` before this page).

## Cross-Wiki

None — Secretary/CFL cross-trunk infrastructure content (wake routing, agent roster semantics), not
personal/home/pro domain material. See [[probe-registry]] for the "state vs status vs discriminator
field" discipline this session's roster-reading finding illustrates in miniature.
