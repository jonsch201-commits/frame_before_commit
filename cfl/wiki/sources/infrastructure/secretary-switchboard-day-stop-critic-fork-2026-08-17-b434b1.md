---
title: "Secretary, 08-17 afternoon: the switchboard that only ever watched Personal, the Fable-scarce model order, why a headless wake can never light a window, Herald's indictment and the rollback, then the Stop-hook critic fork (Claude Secretary fork b434b1, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 12 vs fleet 9 on authored labels"
uuid6: b434b1
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-b434b1-run-reading-beat-and-write-brief.md
raw_sha256: a6dab7f95288f4d459a97d59088f098ad5121b10aa937ff12fc7e886dce9ab4a
raw_length: 728858 chars / 10845 lines (verified turn_count 684, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1
aliases: ["switchboard is not working as intended", "relay only ever watched Personal allowMultiTarget false", "Fable scarce Opus mirror-only order", "why the fuck are you doing this work rather than assigning it", "notify_jon fired zero times in 2562 ticks", "I HATE push notifications", "Stop-hook critic fork b434b1"]
generated_by: S-cd-02 executor (week-2026-09-02-corpus lane, RP-3/RP-4), reading the raw session extract directly from the N: read-only mirror
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
probe_sealed: "According to the cited turn relaying Herald's verdict, how many times had the notify_jon route fired and over how many ticks, and which section heading of Herald's 08-14 contract did the session quote about what the wake was supposed to be?"
tags: [secretary, switchboard, operator, model-policy, fable-budget, graphrag, remote-control, critic-fork, jon-rulings, cfl-infra]
---

# Secretary switchboard day, Stop-hook critic fork — b434b1

## Summary

This raw resumes the Claude Secretary session (parent id `9a25daa7` per the task-output paths) from
the 2026-08-17 ~10:4x compact (T4–T5, one compaction boundary) and runs the afternoon to ~18:0x CDT,
ending with the Stop-hook checkpoint-critic branch (T683–T684). The morning half of the same
session is on [[secretary-hall-prep-peer-review-root-cause-2026-08-17-28b396]]; a sibling fork
one turn longer, fired at PreCompact, is
[[secretary-switchboard-day-precompact-critic-fork-2026-08-18-1b90e4]]. The afternoon: Jon's
"Switchboard is not working as intended" proved structural (the relay watched one target); Jon's
model order (Fable scarce, Opus for the mirror); a usage-limit reset and a Fable 85% / all-models
69% denominator; his GraphRAG timing question answered with a near-zero inventory; his rebuke for
hand-coding instead of assigning; the discovery that a `claude -p` wake can never light a window he
has open; the strip of push notifications he hates; and, on his order to stop and resume the Herald
that had used the switchboard correctly, Herald's verdict that the route to Jon had never fired.

## Key Claims

- **Structural, not a bet.** Jon: "Switchboard is not working as intended. Soul never read anything
  except at my word. I bet if I asked the others, they would say the same thing." Ten minutes of
  measurement: `config.json` had `allowMultiTarget: false` with one target; 1,967 ledger ticks were
  all personal, cfl 0, professional 0 — CFL, Professional and XC were never in scope; the operator
  had judged a wake's envelope and thrown away its pending contents. [verbatim] / [paraphrase]
  ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T6],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T47])
- **The model order.** Jon: "Order. Opus vs fable. We are low on fable. Opus is reserved to mirror
  usage only, I just switched to to Opus." then "Sorry said that poorly. I switched you from fable to
  Opus, and we need to manage our remaining fable budget wisely." The operator, which had been
  spending Opus per wake judgment, was corrected; the first reading of the key clause was recorded as
  wrong and re-read. [verbatim] / [paraphrase]
  ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T336],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T341])
- **The denominator, and the multiplying operators.** Jon: "usage limit hit - now reset. Continue
  coordinatior. Protect my time. We have roughly twice as mutch non-fable budget remaining as we
  have fable budget reamining." (his message pastes the four trunks' recaps, including
  Professional's letter that its own relay registration "is not a key in an instrument"). Measured:
  Fable 85% used vs 69% all-models, both resetting Aug 21 2 pm; two operator loops alive and 16
  concurrent `claude -p` sessions, killed and capped. [verbatim] / [contextual]
  ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T418],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T425],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T480])
- **GraphRAG, from inventory not adjectives.** Jon: "Defaults are fine. How long till we have
  durrible vector embeding with graph rag." The dispatched inventory found no embedding code, no
  vector store and none of the libraries installed in any of the four trunks; the only graph was the
  understand-anything code-structure graph, stale since June 4. The answer split into two clocks —
  moving content out of the huge CLAUDE.md files does not need GraphRAG. Jon then: "We use a lot of
  cost to resuming sessions after an hour of inactivity. Why isn't v0 of graph rag ready already  and
  why will it take another 2 days?" — answer: the day was misallocated to switchboard repair and the
  two-day estimate was padding that never checked whether an embedding model could be installed.
  [verbatim] / [paraphrase] ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T479],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T539],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T552])
- **Coordinate, don't hand-code.** Jon: "Secretary. Why the fuck are you doing this work rather
  than assigning it. Asshat." Conceded: operator patches, a relay fix, a census script and a launcher
  rewrite had all been hand-coded by the most expensive seat on the day Fable was at 85%. [verbatim]
  / [paraphrase] ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T530],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T531])
- **A headless wake cannot light an open window.** Jon: "Why don't I see Herald's chat window as
  active given you just assigned it work?" Answer: a delivery starts a headless `claude -p` session
  and nothing in the harness can inject a turn into another live interactive session; Personal's
  wakes had completed at 16:51:45 and 16:57:58 in a surface that by construction shows nothing.
  Jon: "That. Is. A. Defect." — and the secretary conceded it had published a second untested
  absence claim in one hour and dispatched a seat to test `claude attach`, `remote-control`, `daemon`
  and `respawn` rather than reason about them. [verbatim] / [paraphrase]
  ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T559],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T561])
- **Stop, and resume the Herald that did it right.** Jon: "I'm making you stop. Because this is so
  obviously wrong. The switchboard worked on Friday/Saturday. None of this shit was needed then.
  Resume the Herald I was actually talking to that actually used the switchboard correctly and ask
  it wtf you are doing so fucking wrong." The secretary resumed Herald's live session `7a72c96d`
  (2.1 MB) as a visible background agent and asked it four blunt questions. [verbatim] /
  [paraphrase] ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T647],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T656])
- **Push notifications, stripped.** Jon: "I've been using rc this whole time and I HATE push
  notifications." Removed from delivery prompts and from the tool grant, recorded as a standing rule;
  the secretary noted it had spent an hour proposing Remote Control to someone already running it.
  [verbatim] / [paraphrase] ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T659],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T667])
- **Herald's verdict.** `notify_jon` had fired ZERO times in 2,562 ticks: the three-way route
  (HOLD / WAKE_COORDINATOR / NOTIFY_JON) had existed in `classify.mjs` since 08-14 and every wake
  ever emitted was addressed to a coordinator, so Jon could see nothing because nothing had been
  addressed to him; and the wake was never meant to start a session — Herald's 08-14 contract
  heading reads "Monitor wake rules — its exit IS the wake." The session executed the rollback Herald
  prescribed. [paraphrase] ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T674],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T682])
- **The Stop-hook critic's three findings (unique to this fork).** F1: the rollback retired the
  letter-watch while CFL's agreed retirement condition (3 or more relay wakes delivered to CFL across
  a 2-hour span, graded by CFL) was unmet — delivered count 2 — leaving CFL and Professional with no
  wake path. F2: Herald's load-bearing zero was never re-grepped before the largest reversal of the
  day. F3: at least five Jon branches after ~15:4x had no ledger disposition row. [paraphrase]
  ([secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T683],
  [secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1:T684])

## Conflicts

None with existing wiki content. Overlaps the CFL-side account of the same afternoon in the memory
"The Guarded Door Is Not the Front Door" (the retired v0 relay launcher, T483–T486 here).

## Entities & Concepts

[[switchboard]], [[graphrag-retrieval]], [[mirror-consult-economics]], [[derive-dont-record]],
[[compaction-as-compact]].

## Uncaptured Content

- The pre-compact history (the 08-16 wake through the 08-17 morning) is present in this raw only as
  the T4 compaction summary and is cited from the sibling 28b396 page, never from the summary.
- Monitor-event turns (T183–T414) were skimmed; individual deliveries are not carried as claims.
- 172 thinking blocks are encrypted-in-signature.
- Jon's profanity is his and is kept where quoted.
