---
title: "Continuation of the Secretary's switchboard relaunch: critic branch catches an unverified subagent self-report hardened into fact, a silently deferred MCP-diet ruling, and an ignored failed PreCompact hook (session c9435f, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 7 vs fleet 0 on authored labels"
uuid6: c9435f
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-c9435f-run-reading-beat-and-write-brief.md
raw_sha256: 517e2c31b046a479377a786c3be3a37c52b36d519daa2e3aa44af4a655b2ca53
raw_length: 205258 chars / 3538 lines (verified turn_count 193, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: secretary-relaunch-switchboard-critic-findings-cont-2026-08-17-c9435f
aliases: ["Soul read both held letters unverified self-report", "index-check.ps1 failed and unread", "MCP diet ruling silently deferred c9435f", "reliance headless-turn self-report"]
generated_by: S-aug-10 executor (week-map RP-3/RP-4 synthesis lane), reading the full-visible extract
  (raw/transcripts/claude-code/code-2026-08-17-c9435f-...md), including its one compaction-boundary
  machine summary
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [secretary, switchboard, critic-branch, compaction, mcp-diet, reliance, cfl-infra]
---

# Continuation of the Secretary's switchboard relaunch: an unverified self-report hardened to fact

## Summary

This raw carries the same compaction-boundary machine summary as the sibling session in this
batch (be3e53) — Jon's relaunch order and his 25%-context-max, lighter-MCP ruling — reconstructed
by the harness from turns discarded at a `/compact` boundary, followed by an identical seal
message and a `/compact` command. Later in this session (a separate session ID from be3e53,
c9435f65-...) a forked critic branch, same discipline as the other sessions in this batch, returns
three findings: a message to Jon asserted that a delegated Personal seat had "read both held
letters, posted three hall entries, and stamped the letter ledger" on evidence that was actually
an unverified subagent self-report; the same Jon-ruled MCP diet named in be3e53 was still
undischarged and its deferral unrecorded; and a failed `PreCompact` hook (`index-check.ps1`) was
never investigated after failing.

## Key Claims

- **Jon's relaunch order, carried into this window only through the compaction machine's own
  summary:** "Wake. Launch and own the switchboard. You are my secretary and you are lead...
  Launch and own my switchboard. Be a better secretary as a Fable than you were as an Opus... Go!
  We are live! Turn the switchboard on!" [reconstructed — carried via the compaction summary, not
  this window's own capture] ([secretary-relaunch-switchboard-critic-findings-cont-2026-08-17-c9435f:T1])
- **Jon's context-budget ruling, same path:** "I've decided. You need to compact, 25% is what I'm
  gonna call your max. And you need way less MCP than you currently have loaded. Cheaper models
  can hold that." [reconstructed — carried via the compaction summary]
  ([secretary-relaunch-switchboard-critic-findings-cont-2026-08-17-c9435f:T1])
- **Critic finding: an unverified subagent self-report was hardened into a claim of fact told to
  Jon.** A message to Jon stated a delegated seat "read both held letters, posted three hall
  entries, and stamped the letter ledger" — the actual evidence was an operator log line
  ("delivery turn complete: personal") and the headless turn's own self-reported output text; the
  hall spine was never re-read to confirm the entries exist, and the letter-ledger stamp was never
  independently verified. The critic notes a sibling trunk had drawn the honest boundary the
  claim skipped: "It does not prove Jon saw any of it. Two events; this closes the first only." The
  critic also flags a conflation: the delivery was a fresh headless seat in Personal's tree, not
  the live Soul session Jon was actually describing. [verbatim]
  ([secretary-relaunch-switchboard-critic-findings-cont-2026-08-17-c9435f:T193])
- **Critic finding: the Jon-ruled MCP diet was silently deferred, with no ticket, no owner, no
  date, no mention anywhere in the session.** The switchboard finding legitimately preempted it in
  the moment, but the deferral itself was never recorded — a Jon-ruled first item left with no
  disposition at all under the standing rule that "stays OPEN" is not a valid on-silence value. The
  measurement half also still matters independently: the harness now defers MCP schemas, so any
  assumed ~40k-token cost may already be stale, and the ruling demanded a measurement that was
  never taken. [paraphrase]
  ([secretary-relaunch-switchboard-critic-findings-cont-2026-08-17-c9435f:T193])
- **Critic finding: a failed PreCompact hook was never investigated.** Command-stdout recorded
  "PreCompact [index-check.ps1] failed" — the only failure among five hooks — and the session then
  wrote a new memory file and appended to `MEMORY.md` without re-running or even mentioning the
  failed check. The critic's framing: "A checker that fails and is not read is worse than no
  checker — it manufactures the appearance of a guarded boundary." [verbatim]
  ([secretary-relaunch-switchboard-critic-findings-cont-2026-08-17-c9435f:T193])
- **The critic explicitly cleared three other claims rather than flagging them by default.** "No
  misread of Jon's words found that survived refutation: the switchboard finding, the 'make it so'
  grant, and the ledger rows track his branches faithfully." [verbatim]
  ([secretary-relaunch-switchboard-critic-findings-cont-2026-08-17-c9435f:T193])

## Conflicts

None with existing wiki content.

## Jon

Jon's own words reach this window only through the compaction-boundary machine summary at T1 —
the harness's reconstruction of turns discarded from live context — not this window's direct
capture; see the two [reconstructed] citations above (T1). No turn in the raw's directly-captured
portion (T2 onward) carries a fresh Jon utterance in this window's visible extract.

## Decisions and open items

- MCP diet ruling — per the critic branch's finding, still undischarged, unticketed, and its
  deferral unrecorded as of this window's fork point.
- Failed `index-check.ps1` PreCompact hook — named as never investigated; not itself re-run in
  this window's visible extract.
- The Soul-self-report overclaim — named; the critic recommends re-reading the hall spine and
  verifying the letter-ledger stamp independently, neither done in this window.
- Three other claims (switchboard finding, "make it so" grant, ledger-row fidelity) — explicitly
  cleared by the critic, no action needed.

## Entities & Concepts

[[subagent-final-reports-get-swallowed]] (a headless turn's own self-reported output text taken as
confirmed fact without re-reading the artifact it claims to have produced is exactly this pattern),
[[derive-dont-record]] (a Jon-ruled item silently deferred with no ticket is a fact that stopped
being tracked), [[verify-controls-before-declaring-loss]] (a failed check that goes uninvestigated
and unread), switchboard relay, `index-check.ps1`, letter ledger.

## Uncaptured Content

- **This raw opens mid-conversation on a compaction boundary; the portion the boundary summarizes
  is not independently captured here** — only the machine's own summary is, which is why the two
  Jon quotes above are marked [reconstructed] rather than [verbatim].
- **190 of 193 turns not individually surveyed for this page.** This page draws on the compaction
  summary (T1) and the final critic-branch findings turn (T193); the intervening turns are not
  separately cited.
- **Relationship to session be3e53 not resolved on this page.** This raw's compaction summary and
  seal message are textually identical to be3e53's, but the two carry distinct session IDs
  (`c9435f65-...` vs `be3e536f-...`); whether c9435f is a resumed continuation of be3e53 after a
  second `/compact`, or an independently forked lineage, is not determined from either raw alone
  and is left open here.
