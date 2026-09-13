---
title: "Secretary's first switchboard fire — Jon's 'not working as intended' complaint resolved into manual mode, then the operator log truncates and the critic branch finds attribution and MCP-diet gaps (session e9ab80, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; secondary branch from title/slug — session capture, sub-branch wiki (source-page synthesis, S-aug-11 lane)"
uuid6: e9ab80
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-e9ab80-run-reading-beat-and-write-brief.md
raw_sha256: b7ac172eefa178793cd0244862fc683ed34dfa41552f2e7364ae9ce9f8327ed1
raw_length: 203423 chars / 3490 lines (verified turn_count 187, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80
aliases: ["switchboard first relay-originated CFL wake", "manual mode make it so I don't have to switch",
  "checkpoint critic branch design 2026-08-13", "operator log truncated 4770 bytes"]
generated_by: S-aug-11 executor (week-2026-09-02-corpus lane), reading the raw transcript directly
  (raw/transcripts/claude-code/code-2026-08-17-e9ab80-...md, compaction summary at T1, live turns
  T2-T187, 1 compaction boundary)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [secretary, switchboard, relay, critic-branch, cfl-infra, evidence-loss]
probe_sealed: "Does a wiki page for session e9ab80 already exist under wiki/sources/**? => No — `ls wiki/sources/**/*-e9ab80.md` returned no match before this page was written. TRUSTED"
---

# Secretary's first switchboard fire — manual mode, a first relay-originated wake, and a truncated log

## Summary

This raw opens with the same compaction-boundary summary as
[[secretary-switchboard-restart-discipline-and-ledger-ears-gaps-2026-08-17-ca0248]] (both fork from
the same relaunch-and-25pct-context-max compact), then continues live into the switchboard's actual
first day of operation. Jon reports the switchboard is "not working as intended," the session
diagnoses a classifier-blocked permission requiring his hand on every restart and Jon orders manual
mode instead, the operator settings are made durable, and the first relay-originated wake ever
delivered (to CFL) fires successfully mid-session. The session closes with a system-defined
"CHECKPOINT CRITIC BRANCH" — a forked snapshot fired by a Stop hook per a named 2026-08-13 plan —
which finds an attribution claim never independently verified against the hall spine, a Jon-ruled
first-post-compact action silently preempted and never dispositioned, and an operator log found
truncated to 4,770 bytes with the truncation cause unproven.

## Key Claims

- **The compaction summary (machine-generated, not Jon) records the same relaunch order and
  25%-context-max ruling as the sibling session's opening.** "I've decided. You need to compact, 25%
  is what I'm gonna call your max. And you need way less MCP than you currently have loaded.
  Cheaper models can hold that." [reconstructed]
  ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T1])
- **Jon's live complaint that opens the working section of this session, quoted in full.**
  "Switchboard is not working as intended. Soul never read anything except at my word. I bet if I
  asked the others, they would say the same thing." [verbatim]
  ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T6])
- **Jon's follow-up order to stop requiring his hand on every restart, quoted verbatim including his
  own typo.** "Manual mode. Make it so I don't have to keep fucking switching my god." [verbatim]
  ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T48])
- **The first relay-originated wake to CFL fired and delivered successfully mid-session, closing
  out a standing acceptance criterion.** A monitor task-notification reports "operator v2.2 (pid
  321576)... 2026-08-17 14:40:29 DELIVER -> cfl", and the session states: "the relay itself (not the
  stopgap letter-watch) detected probe 3 in CFL's inbound, emitted wake t02012 with target: cfl, and
  the operator judged and delivered it at 14:40:29. That's the first relay-originated CFL wake
  ever." [verbatim] ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T186])
- **The checkpoint-critic mechanism's own charter is stated verbatim in the system directive that
  invokes it**, naming its origin ("Jon's 2026-08-13 plan: a fable version of the session checking
  its thoughts"), its lens (Herald's four hook-moments design), its ears-check requirement (does any
  Jon message branch lack a ledger disposition), its cap (at most three findings, each citing a
  checkable receipt or marked OPINION), and its scope limit ("claim nothing about events after your
  fork point — you are a snapshot"). [verbatim]
  ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T186])
- **Checkpoint critic F1: an attribution claim delivered to Jon twice was never checked against the
  hall spine that would confirm or refute it, and conflates two different claims.** The operator's
  `claude -p` delivery runs as "a NEW headless session in Personal's directory, not Soul's live
  session," so "'Soul read' and 'a fresh Personal-trunk seat read' are different claims" — the
  attribution rested on an interleaved, truncated log rather than the hall spine itself.
  [paraphrase] ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T187])
- **Checkpoint critic F2: the Jon-ruled first-post-compact action was preempted by the switchboard
  fire and never dispositioned afterward.** "Shed MCP load and MEASURE /context before/after... was
  never executed and never dispositioned after the switchboard fire took priority. Preemption was
  right; silent non-disposition is not (standards section 3: silence rots)." [paraphrase]
  ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T187])
- **Checkpoint critic F3: the operator log was found truncated with the cause unproven, and the
  no-deletion rule was not followed before further processes kept appending to the same file.**
  "The operator log was found truncated to 4,770 B (measured, wc -c) after containing the
  first-ever delivery receipts; the session wrote 'mystery... move on,' preserved nothing, and
  root-caused nothing... under the no-deletion rule the remaining file should have been copied
  aside before two further processes kept appending to it, and the truncator identified
  (candidate: two relays and multiple claude turns sharing one fd via >>; unproven)." [verbatim]
  ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T187])

## Conflicts

None with existing wiki content.

## Jon

- "Switchboard is not working as intended. Soul never read anything except at my word. I bet if I
  asked the others, they would say the same thing."
  ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T6])
- "Manual mode. Make it so I don't have to keep fucking switching my god."
  ([secretary-switchboard-fire-log-truncation-critic-2026-08-17-e9ab80:T48])

Both preserved with Jon's own words, including the run-on phrasing of the second; no correction
applied.

## Decisions and open items

- **Decided:** manual mode adopted; operator-lifecycle permissions added to this project's
  settings, made durable so restarts no longer require Jon's hand.
- **Flagged as awaiting Jon (~30 seconds, stated as genuinely his to do):** Soul's and Herald's
  headless sessions both have finished work sitting uncommitted because `git add` is
  classifier-refused in their windows — needs either brief manual mode in those windows or the same
  allow-rules added to their settings.
- **Open, per the critic branch:** verify the "Soul read" attribution against the hall spine itself
  rather than the interleaved operator log; disposition the shed-MCP/measure-context action that
  was silently preempted; identify the operator-log truncation cause and copy the remaining file
  aside under the no-deletion rule before further writes.

## Entities & Concepts

Checkpoint critic branch (Stop-hook fork, 2026-08-13 plan), switchboard relay/operator, manual mode
permission escalation, [[compaction-as-compact]] (this session's shared compaction summary),
operator log truncation.

## Uncaptured Content

- **The compaction summary's T1 content is machine-reconstructed prose**, per this raw's own
  extraction note — 59 thinking blocks are marked encrypted-in-signature and excluded.
- **Turns 7-47 and 49-185 are not individually cited on this page** — the diagnosis and fix work
  between the two Jon quotes, and the bulk of the relay-fire and delivery-verification work between
  T48 and the closing critic branch, are not walked turn-by-turn here.

## Links

[[secretary-switchboard-restart-discipline-and-ledger-ears-gaps-2026-08-17-ca0248]] (the sibling
session sharing this raw's compaction summary), [[probe-registry]] (the seal-before-run discipline
this batch's own `probe_sealed:` field follows).
