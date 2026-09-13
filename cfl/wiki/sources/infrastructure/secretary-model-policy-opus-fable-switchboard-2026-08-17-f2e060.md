---
title: "Secretary trunk: Jon's Opus/Fable model-policy order, corrected in-session, and the switchboard operator moved off Opus triage (session f2e060, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: f2e060
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-f2e060-run-reading-beat-and-write-brief.md
raw_sha256: d91181f7d807e7d4df57626b04a58e90fd1a4cb0689339848634d1efc84938e3
raw_length: 378979 chars / 6400 lines (verified turn_count 374, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060
aliases: ["Opus reserved to mirror usage order", "switchboard operator moved to sonnet triage",
  "single-flight lock first live fire", "checkpoint critic branch fork 15:3x",
  "Jon corrected switched you not I switched"]
generated_by: S-aug-12 executor (RP-3/RP-4 window-to-source lane), reading the Secretary-trunk
  extract directly (raw/transcripts/claude-code/code-2026-08-17-f2e060-...md, 110 thinking blocks
  encrypted-in-signature, 1 compaction boundary, tool calls/results summarized)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, secretary, model-policy, opus, fable, checkpoint-critic, peer-review-rule]
---

# Secretary trunk: Jon's Opus/Fable model-policy order and the operator's move off Opus — f2e060

## Summary

This is one of at least three separately-captured continuations of the Secretary trunk's long
2026-08-17 "switchboard" session, each inheriting an identical machine-written compaction summary
of the session's earlier hours (the launch order, GraphRAG-embeddings ruling, the 25%-context-max
ruling) and then diverging into its own further turns after that point — the relationship among the
sibling captures (this file, and the separately-catalogued f3604e and fbf416) is not established by
this page and is flagged under Uncaptured Content. This capture's own new material: Jon's
model-policy order ("Order. Opus vs fable...") was initially misread by the session (as the mirror
lane's Opus quota being at risk) and Jon corrected the misreading within a minute ("Sorry said that
poorly. I switched you from fable to Opus..."); the session then pulled Opus out of the switchboard
operator's per-wake triage entirely, moving it to Sonnet, and later a background-task notification
showed the operator's single-flight delivery lock firing for the first time under real traffic. The
capture ends with a Stop-hook "checkpoint critic branch" fork raising three findings against the
session's own claims.

## Key Claims

- **Jon's model-policy order was first misread, then corrected by Jon within roughly a minute — both
  versions preserved in the ruling file rather than silently replaced.** Jon's first message,
  verbatim: "Order. Opus vs fable. We are low on fable. Opus is reserved to mirror usage only, I just
  switched to to Opus." The session read "I just switched to to Opus" as Jon switching his own
  client and wrote a ruling restricting the switchboard's own Opus use as spending a pool "reserved to
  mirror usage." Jon's correction, verbatim: "Sorry said that poorly. I switched you from fable to
  Opus, and we need to manage our remaining fable budget wisely." The session then appended a
  correction section to the same file rather than rewriting it, stating explicitly what it had gotten
  wrong ("Wrong subject. He switched this seat from Fable to Opus. The sentence is about my model, not
  his."). [verbatim] ([secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060:T336],
  [secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060:T341])
- **The switchboard operator's per-wake triage judgment was moved from Opus to Sonnet as the one
  concrete action from the corrected policy.** The operator had been calling `--model opus` once per
  wake — roughly 15 calls/hour at that day's peak — purely to decide DELIVER vs HOLD against a written
  charter. Changed to `--model sonnet` in `switchboard-operator.sh`, selftested (PASS), and restarted;
  a grep confirmed zero remaining `--model opus` references and one `--model sonnet` reference in the
  script. [verbatim: "Triage doesn't need a top tier, and every verdict it writes is logged and
  reviewable."] ([secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060:T341])
- **The session told the room, rather than deciding for it, that "switch to Opus" was not a general
  license.** A hall post plus a courier to all three trunks stated that Fable is the scarce pool this
  policy protects, that the Opus switch was Jon's assignment to one seat, not a general escape hatch,
  and asked every seat to grep its own scripts/hooks for `--model` and report findings rather than
  publish an unmeasured absence claim. An open item — "what still runs on Fable, and who owns the
  Fable spend policy" — was posted with an owner and an expiry (2026-08-18 18:00) and a stated
  default-on-silence output. [paraphrase]
  ([secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060:T366])
- **The single-flight delivery lock fired for the first time under real traffic and behaved as
  designed: it queued rather than double-delivering.** A monitor notification showed a courier letter
  to CFL logged as both `DELIVER-LETTER` and, in the same second, `WAIT (in-flight): cfl busy (pid
  331556), queuing` the same letter — the session read this as the lock doing its job (queuing instead
  of spawning a second session in a busy trunk), calling it "exactly the specific failure CFL warned
  would recreate D14 one scope down." [paraphrase]
  ([secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060:T370])
- **A Stop-hook "checkpoint critic branch" fork raised three findings against the session's own
  claims, each required to cite a checkable receipt or be marked OPINION.** F1: the ears-ledger
  (`rulings/jon-branch-ledger.md`) never received rows for the two model-policy messages — dispositions
  exist elsewhere (the standalone ruling file) but the one file the room is told to audit under-reports
  two Jon messages. F2: the delivery ledger logs a letter as `DELIVER-LETTER` at *queue* time, not
  delivery time, so a letter that later expires in-flight would leave a false "delivered" row standing
  next to an "expired-in-flight" row for the same item. F3: the session's claim that the lock "acquired
  and released cleanly" was asserted without checking that the lockdir was actually gone afterward — a
  stuck lockdir would silently convert every later delivery into a 90-minute wait with no alert.
  [verbatim, three findings quoted with their own receipts]
  ([secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060:T373])

## Jon

- `[secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060:T336]` — "Order. Opus vs fable.
  We are low on fable. Opus is reserved to mirror usage only, I just switched to to Opus." (verbatim,
  typos his)
- `[secretary-model-policy-opus-fable-switchboard-2026-08-17-f2e060:T341]` — "Sorry said that poorly.
  I switched you from fable to Opus, and we need to manage our remaining fable budget wisely."
  (verbatim)

## Decisions and open items

- Fable-spend ownership: OPEN, owner Secretary (post) / cost lane, Herald/XC (answer), expires
  2026-08-18 18:00 CDT, default-on-silence "Fable spend: UNMEASURED, no owner" published as the next
  brief's first finding.
- F1 (ears-ledger under-reporting) — critic finding, no disposition recorded within this capture's
  visible window.
- F2 (delivery ledger writes at queue time, not delivery time) — critic finding, no disposition
  recorded within this capture's visible window.
- F3 (lock release never independently verified) — critic finding, no disposition recorded within
  this capture's visible window.

## Conflicts

None with existing wiki content.

## Links

[[probe-registry]] — the critic-branch fork's own rule ("every finding must cite a checkable receipt
… or be marked OPINION") is the same discipline this seal-before-run pattern names for ordinary work.

## Uncaptured Content

- **This capture shares an identical machine-written compaction summary with at least two sibling
  captures dated the same day** (catalogued separately by this same lane under different session
  ids), each ending in its own distinct "checkpoint critic branch" Stop-hook fork at a different
  timestamp (this one ~15:3x). Whether these are literal forks of one underlying session, independent
  resumes sharing inherited context, or some other relationship is not established from this raw
  alone and is out of scope for this page.
- Turns 1–5953 (the bulk of the session, including the full switchboard-outage diagnosis, the
  operator-v2 rebuild, and multiple earlier hall posts) are not individually cited on this page; only
  the model-policy exchange and its aftermath (T336 onward) are drawn on.
- 110 thinking blocks exist in the raw and are encrypted-in-signature — not recoverable client-side,
  so no claim on this page draws on the session's private reasoning, only its visible tool calls and
  written text.
- The 1 compaction boundary present (machine-generated `## Compaction Boundary`, not a Jon turn) is
  not itself cited as a Key Claim source.
