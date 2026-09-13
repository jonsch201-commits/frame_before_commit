---
title: "Secretary relaunches the switchboard on Jon's Fable order; critic branch flags an unproven lock claim, a deferred post-compact ruling, and a self-passing selftest (session be3e53, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 6 vs fleet 0 on authored labels"
uuid6: be3e53
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-be3e53-run-reading-beat-and-write-brief.md
raw_sha256: c70d90230fb0573503cc042ef4d4b25e334ddfdb8215409602496c9976f6d30f
raw_length: 350640 chars / 6011 lines (verified turn_count 338, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: secretary-relaunch-switchboard-critic-findings-2026-08-17-be3e53
aliases: ["25 percent context max MCP diet ruling", "lock UNPROVEN-LIVE finding", "selftest false-pass no per-run marker", "PreCompact index-check failed ignored"]
generated_by: S-aug-10 executor (week-map RP-3/RP-4 synthesis lane), reading the full-visible extract
  (raw/transcripts/claude-code/code-2026-08-17-be3e53-...md), including its one compaction-boundary
  machine summary
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [secretary, switchboard, critic-branch, compaction, mcp-diet, cfl-infra]
---

# Secretary relaunches the switchboard on Jon's Fable order; critic branch flags an unproven lock

## Summary

This raw opens on a compaction-boundary machine summary (not a Jon turn) recounting a session in
which Jon relaunched the Secretary as a Fable seat with standing orders to own the switchboard,
protect his time, and support the other trunks, and later ruled a hard context cap: "I've decided.
You need to compact, 25% is what I'm gonna call your max. And you need way less MCP than you
currently have loaded." The visible window resumes with the seat sealing its own state ahead of
`/compact` and naming the first post-compact item (an MCP diet with a before/after `/context`
measurement). A `/compact` command follows, and later in the session a forked critic branch — same
discipline as the sibling sessions in this batch — returns three findings: an unverified claim
about a delivery lock, a deferred Jon-ruled item with no ticket, and a selftest whose positive
controls can pass forever once they have passed once.

## Key Claims

- **Jon's relaunch order, carried into this window only through the compaction machine's own
  summary of the discarded portion:** "Wake. Launch and own the switchboard. You are my secretary
  and you are lead. You learned many lessons as an Opus before compact, keep my time protected and
  support the others and help them use best practices... Launch and own my switchboard. Be a
  better secretary as a Fable than you were as an Opus... Go! We are live! Turn the switchboard
  on!" [reconstructed — carried via the compaction summary, not this window's own capture]
  ([secretary-relaunch-switchboard-critic-findings-2026-08-17-be3e53:T1])
- **Jon's later context-budget ruling, same path:** "I've decided. You need to compact, 25% is
  what I'm gonna call your max. And you need way less MCP than you currently have loaded. Cheaper
  models can hold that." [reconstructed — carried via the compaction summary]
  ([secretary-relaunch-switchboard-critic-findings-2026-08-17-be3e53:T1])
- **The seat sealed its own state before compacting, naming a concrete post-compact test.** "First
  post-compact item is the MCP diet: Gmail (28 tools) + Calendar (9) + Drive (11) +
  chrome-devtools (30) ~40k tokens for connectors this seat never uses... The post-compact seat
  disables them and proves it with a before/after `/context` measurement." [verbatim]
  ([secretary-relaunch-switchboard-critic-findings-2026-08-17-be3e53:T2])
- **Critic finding: a "clean lock" claim to Jon was unsupported by any artifact read.** The session
  told Jon a delivery was "the first delivery under the single-flight lock, and it acquired and
  released cleanly," but no check confirmed the lock directory was created, that `meta.json` held
  a real pid, or that a last-meta file existed after release — the lock's only observed fire was a
  test short-circuit that exits before any lock code runs. Under the session's own exercise-before-
  reliance rule, the critic grades the lock UNPROVEN-LIVE. [verbatim]
  ([secretary-relaunch-switchboard-critic-findings-2026-08-17-be3e53:T338])
- **Critic finding: the Jon-ruled first post-compact item (the MCP diet) was never executed or
  rescheduled.** Six hours of session contain no `/context` measurement, no MCP disable, and no
  line moving the item to a dated slot; a Jon ruling dispositioned as ACTIONED pre-compact ended up
  "neither done nor owned-with-date" — named by the critic as the exact silence-rots shape the
  standards forbid. [paraphrase]
  ([secretary-relaunch-switchboard-critic-findings-2026-08-17-be3e53:T338])
- **Critic finding: a selftest's positive controls grep an append-only log with no per-run
  marker, so a regression that stops logging a line would still pass forever.** The one control
  that does not read the shared log (a meta-parse check) was the only control observed to fail
  when its subject actually broke. [paraphrase]
  ([secretary-relaunch-switchboard-critic-findings-2026-08-17-be3e53:T338])

## Conflicts

None with existing wiki content.

## Jon

Jon's own words reach this window only through the compaction-boundary machine summary at T1,
which is the harness's own reconstruction of turns discarded from live context, not this window's
direct capture — see the two [reconstructed] citations above (T1). No turn in the raw's directly-
captured portion (T2 onward) carries a fresh Jon utterance; T3 is a `/compact` local-command
caveat, not prose from Jon.

## Decisions and open items

- MCP diet (Gmail, Calendar, Drive, chrome-devtools) — Jon-ruled, sealed as "first post-compact
  item" pre-compact, but per the critic branch's finding, never executed or ticketed with a date
  in this window's visible extract.
- Delivery lock's "acquired and released cleanly" claim — graded UNPROVEN-LIVE by the critic; not
  itself re-verified against the live record within this window.
- Selftest false-pass path — named, remedy proposed (per-run nonce) but marked OPINION by the
  critic, not applied in this window.
- 25% context-max ruling — the seat states it will self-seal and compact at 25% going forward,
  "no ruling needed next time."

## Entities & Concepts

[[derive-dont-record]] (a Jon ruling sealed as ACTIONED that never actually executes is the same
failure as a record that stops tracking reality), [[verify-controls-before-declaring-loss]] (the
lock claim and the selftest finding are both instances of asserting past the evidence),
[[subagent-final-reports-get-swallowed]] (the critic-branch discipline itself — a forked snapshot
whose findings must be independently re-verified, not trusted as-is), switchboard relay, MCP diet.

## Uncaptured Content

- **This raw opens mid-conversation on a compaction boundary; the portion the boundary summarizes
  is not independently captured here** — only the machine's own summary of it is, which is why
  the two Jon quotes above are marked [reconstructed] rather than [verbatim].
- **335 of 338 turns not individually surveyed for this page.** This page draws on the compaction
  summary (T1), the immediately following seal message (T2), and the final critic-branch findings
  turn (T338); the intervening ~335 turns (the switchboard relaunch mechanics, the actual
  `/compact`, and whatever followed it before the critic fork) are not separately cited.
