---
title: "Secretary launches the switchboard on Jon's order, gets caught hand-coding for four hours ('Why the fuck are you doing this work rather than assigning it. Asshat.'), lands CLAUDE-STANDARDS §13, and a critic-branch fork finds a stale Jon-words ledger at close (2026-08-17, 1717b6)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 4 vs fleet 0 on authored labels"
uuid6: 1717b6
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-1717b6-run-reading-beat-and-write-brief.md
raw_sha256: 3289c99acb2de8c8dad162673f89eab3504dceb8e9b963b3286bac6e3d2bc6bc
raw_length: 562758 chars / 8635 lines (verified turn_count 542, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6
aliases: ["CLAUDE-STANDARDS 13 coordinator implements", "asshat ruling 2026-08-17",
  "Opus reserved to mirror usage order", "GraphRAG v0 spec assigned to CFL",
  "critic branch stale Jon-words ledger finding", "coordinator that implements has stopped coordinating"]
generated_by: S-aug-03 executor (RP-3/RP-4 window-to-page lane), reading the raw transcript directly
  (N:/claude-corpus/cfl/raw/transcripts/claude-code/code-2026-08-17-1717b6-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
probe_sealed: "What did Jon's correction to the Secretary catch, what standing rule did the session write from it (name the CLAUDE-STANDARDS section), and what did the session's own closing self-critique find still unresolved? [expected class TRUSTED]"
tags: [switchboard, secretary, jon-ruling, claude-standards, model-policy, graphrag, cfl-infra]
---

# Secretary launches the switchboard, gets caught hand-coding, lands §13, closes on a stale-ledger self-critique

## Summary

The Secretary-trunk session opened (after a prior compaction) on Jon's relaunch order to own the
switchboard, then spent hours diagnosing why the switchboard was not reaching the other trunks,
patching the relay and operator directly, running a model-policy change (Fable low, Opus reserved
to mirror usage), and fielding a GraphRAG-with-vector-embeddings design question. Partway through,
Jon corrected the session hard for hand-coding instead of delegating — "Secretary. Why the fuck are
you doing this work rather than assigning it. Asshat." — which the session accepted without
qualification, wrote up as a new binding rule (CLAUDE-STANDARDS §13: a coordinator that implements
has stopped coordinating), and used to reassign its own outstanding work (GraphRAG v0 spec to CFL,
a CLAUDE.md byte-budget shrink to Professional, cost-census integration to CFL, switchboard
maintenance to CFL-builds/Secretary-reviews) rather than continuing to build any of it itself. The
session closed with a hook-fired "critic branch" fork reviewing its own most recent work, which
found the session's own Jon-words ledger had gone stale exactly at the point that mattered — two of
Jon's branches ("Protect my time," "Continue coordinatior") had no disposition anywhere, a
courier the session claimed to have sent was never written, and a "Family B closed" claim rested on
zero fired terminal rows.

## Key Claims

- **The session opened on Jon's relaunch order** (quoted inside a compaction-boundary summary, not
  independently re-verified against a live turn on this page): to launch and own the switchboard as
  lead secretary, protect Jon's time, ensure all trunks reach town hall, and consider running a
  cheaper sub-secretary to protect its own context. [reconstructed, from the session's own
  compaction summary] ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T1])
- **Jon flagged the switchboard as not working as intended** ("Soul never read anything except at
  my word. I bet if I asked the others, they would say the same thing"), which the session took as
  a claim to investigate rather than dispute, checking the operator log, ledger, and wake-order
  directory before diagnosing anything. [verbatim] ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T6])
- **Jon ordered manual permission mode** ("Manual mode. Make it so I don't have to keep fucking
  switching my god"), and the session responded by adding operator-lifecycle permissions to the
  project's settings rather than asking Jon to keep re-approving. [verbatim]
  ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T48])
- **Jon's model-policy order — Fable is low, Opus reserved to mirror usage, seat switched to
  Opus** — was written up as a standing ruling with an explicit branch ledger (three sub-claims,
  each ACTIONED/ANSWERED separately) and immediate compliance: the switchboard operator's wake
  judgment was moved off Opus onto Sonnet, described as "the single largest automated Opus consumer
  on the machine — one Opus turn per wake, and today produced ~15 wakes/hour at peak."
  [verbatim/paraphrase] ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T336])
- **Jon's correction landed as a direct quote and became CLAUDE-STANDARDS §13, not just an
  apology.** Verbatim: "Secretary. Why the fuck are you doing this work rather than assigning it.
  Asshat." The session's own accounting of what it had hand-built that session: five operator
  revisions, a `relay3.mjs` patch, a `usage-census.py`, a PowerShell launcher rewrite, and a
  hall-append helper — "every one was specifiable in a paragraph and buildable by a cheaper seat."
  §13's test for future coordinator turns: "could a cheaper seat do this from a paragraph? If yes,
  write the paragraph." [verbatim] ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T530])
- **The session also caught its own follow-up error inside the same exchange**: when corrected, it
  first justified the hand-coding by citing the Fable meter, while actually running on Opus (per
  Jon's own switch minutes earlier — "I also told you I switched you to Opus"). Corrected reasoning:
  the delegation argument does not rest on which meter a seat bills, but on what the seat is for.
  [verbatim/paraphrase] ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T533])
- **Work was reassigned by written spec rather than continued in-session**: GraphRAG v0
  (vector-embedded, hybrid with the existing but stale code/wiki-structure graph) to CFL, due a
  fired typo-query demo by 2026-08-19 18:00 and a durable index by 2026-08-21; a CLAUDE.md
  byte-budget shrink (≤5KB resident core per file, no deletion, moved content lands in the wiki with
  a pointer back) to Professional plus each trunk applying it to its own file; cost-census
  integration to CFL; switchboard maintenance implementation to CFL with Secretary as reviewer only.
  [paraphrase] ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T533])
- **Jon's GraphRAG requirement, stated twice and verbatim, is the acceptance test the later v0 build
  was measured against**: "I know graph rag alone will fail if we don't also implement vector
  embeding. Think about all my typos and imprecise language and the stylomantic differences between
  trunks," and separately, on purpose: "When can we move shit out of the huge Claude md Files and
  into the wiki, read when needed based on vector embedded graph rag?" — quoted inside the session's
  own assignment courier to CFL. [verbatim, quoted secondhand inside this session's own courier text]
  ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T530])
- **The closing critic-branch fork (a hook-fired self-review per Jon's 2026-08-13 plan) found three
  problems the main session had not caught in itself**: the session's own Jon-words ledger
  (`rulings/jon-branch-ledger.md`) had zero rows for any Jon message after the "Manual mode" entry,
  leaving two branches — "Protect my time" and "Continue coordinatior" — with no disposition
  anywhere; a ruling file claimed a courier had been sent to close specific review-index rows and
  no such courier was ever written; and a "Family B closed" claim rested on 30 delivery-ledger claim
  rows with zero terminal rows ever fired, plus a launcher file (`Switchboard.cmd`) that the fix
  never actually opened, leaving open the possibility the unguarded old relay door was still live.
  [verbatim/paraphrase] ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T541])

## Jon

- ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T6]) "Switchboard is not working as
  intended. Soul never read anything except at my word. I bet if I asked the others, they would say
  the same thing." [verbatim]
- ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T48]) "Manual mode. Make it so I
  don't have to keep fucking switching my god." [verbatim]
- ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T336]) "Order. Opus vs fable. We
  are low on fable. Opus is reserved to mirror usage only, I just switched to to Opus." [verbatim]
- ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T341]) "Sorry said that poorly. I
  switched you from fable to Opus, and we need to manage our remaining fable budget wisely."
  [verbatim]
- ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T418]) "usage limit hit - now reset.
  Continue coordinatior. Protect my time. We have roughly twice as mutch non-fable budget remaining
  as we have fable budget reamining." [verbatim, typos his — includes a longer relayed-recap block
  not reproduced here]
- ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T479]) "Defaults are fine. How long
  till we have durrible vector embeding with graph rag." [verbatim, typos his]
- ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T530]) "Secretary. Why the fuck are
  you doing this work rather than assigning it. Asshat." [verbatim]
- ([secretary-switchboard-launch-asshat-ruling-2026-08-17-1717b6:T533]) "I also told you I switched
  you to Opus." [verbatim]

## Conflicts

None with existing wiki content.

## Decisions and open items

- CLAUDE-STANDARDS §13 landed: a coordinator specs, assigns, and grades; it does not implement,
  with a named test ("could a cheaper seat do this from a paragraph?") and named narrow exceptions.
- Model policy: switchboard operator wake-judgment moved from Opus to Sonnet; Opus reserved to
  mirror usage per Jon's order.
- GraphRAG v0 assigned to CFL (design + typo-query demo by 08-19 18:00, durable index by 08-21);
  CLAUDE.md byte-budget shrink assigned to Professional + each trunk for its own file (rule+lint by
  08-18 18:00, shrink by 08-20); cost-census fold-in to CFL by 08-19; switchboard maintenance
  (D14 durable claim mark, W-6 backlog-on-first-arm, D13 log-truncation cause, read-fence asymmetry)
  to CFL, due 08-19, reviewed by Secretary.
- LEFT OPEN at close, per the critic branch's own findings: two Jon message branches ("Protect my
  time," "Continue coordinatior") with no disposition in the Jon-words ledger; a claimed courier to
  close review-index rows 2/4/5 that was never actually sent; whether `Switchboard.cmd` (the
  double-click door) still starts the retired v0 relay, since the session's fix only touched
  `Switchboard.ps1`.

## Links

[[graphrag-retrieval]] — this session is the origin point of the GraphRAG v0 assignment and its
acceptance test (retrieve correctly on Jon's own typos and imprecise phrasing, where exact-match
search fails), later built out as described in that page.
[[coordinator-dispatches-never-adopts]] — the same discipline this session's own §13 ruling encodes
from the opposite direction: a coordinator's job is to dispatch and grade, not to do the work itself.
[[max-plan-fl-budget]] — the Fable/Opus scarcity backdrop (weekly meter percentages, reset date)
this session's model-policy ruling and cost-census assignment both operate against.

## Entities & Concepts

CLAUDE-STANDARDS §13, switchboard operator/relay, model policy (Fable/Opus), GraphRAG v0 spec,
critic-branch checkpoint fork, `rulings/jon-branch-ledger.md`.

## Uncaptured Content

- This is a partial-window extraction of a 542-turn, 8,635-line session: only ten of the turns
  (T1, T6, T48, T336, T341, T418, T479, T530, T533, T541) are individually cited here. The large
  majority of the session — extensive tool-call diagnosis of the switchboard relay/operator,
  multiple operator version restarts (v2.2 through v2.6+), the full GraphRAG inventory subagent's
  findings, and dozens of Monitor task-notification turns recording individual wake deliveries — is
  not walked turn-by-turn on this page.
- T1's content (the compaction-boundary summary of Jon's launch order and the session's early
  activity) is Claude Code's own machine-generated summary of discarded context, not a live
  human-role turn — tagged `[reconstructed]` above rather than `[verbatim]` for that reason, per
  this raw's own extraction note that compaction-boundary turns are not attributed to Jon.
- 145 thinking blocks and 1 compaction boundary exist in the raw; thinking is encrypted-in-signature
  and not recoverable, so no claim here draws on the session's private reasoning.
- The critic-branch fork's findings (T541) are themselves a snapshot at its fork point and are not
  independently re-verified against the live record on this page — they are reported as the fork's
  own claims, not adjudicated here.
