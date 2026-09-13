---
title: "Secretary launches and owns the switchboard, Jon's post-compact complaint triggers a live investigation, D9 root cause found (wake orders never marked claimed) — CFL session 9ac58a, 2026-08-17"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 9ac58a
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-9ac58a-run-reading-beat-and-write-brief.md
raw_sha256: aa26fc6717c5bd1cc65047b89ebd88b67a9f8d2676c6e7660216fffbdd3aab4c
raw_length: 278412 chars / 4804 lines (verified turn_count 272, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: secretary-switchboard-launch-d9-unclaimed-wake-orders-2026-08-17-9ac58a
aliases: ["switchboard operator launch 2026-08-17", "D9 root cause wake orders never claimed",
  "25 percent context max MCP diet ruling", "switchboard not working as intended complaint",
  "operator v2.3 delivered-state fix"]
generated_by: S-aug-09 executor (week-2026-09-02-corpus lane), reading the extracted transcript
  directly (raw/transcripts/claude-code/code-2026-08-17-9ac58a-...md); this session continues from
  a compaction boundary whose machine-written summary is itself T1 and is treated as a compact
  summary, not a Jon utterance
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [secretary, switchboard, operator, root-cause, context-management, mcp, cfl-infra]
probe_sealed: "What was the D9 root cause this session found for the switchboard operator's failure to deliver fresh wake orders, and what was the actual defect (not the symptom)? => The operator's catch-up logic re-entered at the same oldest wake-order file on every restart because delivery never MARKED an order as claimed, so three fresh, never-delivered orders for trunks that had never been woken sat unclaimed beside an 81-minute-stale order that got delivered twice across two restarts; the defect was the missing claim-mark, not the catch-up logic itself. TRUSTED"
---

# Secretary launches and owns the switchboard; D9 root cause found — wake orders never marked claimed (9ac58a, 2026-08-17)

## Summary

A CFL-corpus Secretary-trunk session, resumed from a compaction boundary, executed Jon's relaunch
order to "own the switchboard" as lead, landed a string of Jon rulings (GraphRAG needs vector
embeddings alongside graph, questions the Secretary thinks are for Jon go to the town hall
instead, work must continue without phone-dependency, a 25%-context-max-plus-MCP-diet standing
rule), built and launched a sub-secretary operator script, and sealed for compact. Immediately
post-compact, Jon reported the switchboard was "not working as intended" and that Soul had never
read anything except at his word — triggering a live investigation that traced the failure to a
specific mechanism (D9): wake-order delivery never marked an order claimed, so every operator
restart replayed the same stale order while fresh orders for un-woken trunks sat ignored. The
session diagnosed, fixed, and shipped the fix (operator v2.3) within the same session, and closed
a cross-trunk grading exchange with CFL over which clauses of a two-sided acceptance test had
actually passed.

## Key Claims

- **Jon's relaunch order, quoted verbatim in this session's own compact summary: "Wake. Launch and
  own the switchboard. You are my secretary and you are lead... Be a better secretary as a Fable
  than you were as an Opus... Go! We are live! Turn the switchboard on!"** The same summary records
  a chain of further rulings landed this session, closing with the final one that triggered
  compact: "I've decided. You need to compact, 25% is what I'm gonna call your max. And you need
  way less MCP than you currently have loaded. Cheaper models can hold that." [verbatim, quoted
  inside the session's own machine-generated compact summary, not independently re-verified
  against the pre-compact turns] ([secretary-switchboard-launch-d9-unclaimed-wake-orders-2026-08-17-9ac58a:T1])
- **Immediately post-compact, Jon reported the switchboard was failing in practice: "Switchboard is
  not working as intended. Soul never read anything except at my word. I bet if I asked the others,
  they would say the same thing."** The session opened its response by investigating before
  diagnosing, checking the operator log and ledger against what it should show. [verbatim]
  ([secretary-switchboard-launch-d9-unclaimed-wake-orders-2026-08-17-9ac58a:T6])
- **D9 — the root cause: wake-order delivery never marked an order as claimed, so every operator
  restart re-entered at the same stale order.** Measured: a wake order written at 13:18:16 (81
  minutes stale) was delivered twice across two restarts (14:36:29 and 14:39:00) while three fresh
  orders for trunks that had never been woken — including two for CFL and one for Professional —
  sat unclaimed beside it. "The defect is not the catch-up. It is that delivery does not MARK an
  order claimed, so every restart re-enters at the same oldest file and never advances." This
  material is CFL's own grading letter, read into this session via a tool result (`cat`) rather
  than authored here. [contextual] ([secretary-switchboard-launch-d9-unclaimed-wake-orders-2026-08-17-9ac58a:T194])
  [source: tool-result payload quoting CFL's grading letter, this raw, T194]
- **The fix (operator v2.3) shipped in the same session, on two belts: a gated one-time migration
  marker so the claim list persists across restarts, plus a check against
  `operator-deliveries.jsonl` so any wake or letter already recorded is skipped regardless of state
  resets.** The Secretary's own reply letter to CFL states: "My v2 startup moved the delivered-state
  aside on EVERY start — a one-time v1 migration I left unconditional. Each restart wiped the claim
  list... Fixed in v2.3, both belts... Selftest PASS, v2.3 live." [verbatim]
  ([secretary-switchboard-launch-d9-unclaimed-wake-orders-2026-08-17-9ac58a:T210])
- **A cross-trunk acceptance grade was contested and resolved within the window: CFL's FAIL on
  clause 2 was superseded by evidence that arrived after CFL's own grading stamp.** The relay
  delivered the missing wake to CFL at 14:40:29 and the corresponding letter at 14:42:48, both
  after CFL's 14:40:26 grade stamp; the Secretary's reply states the row was "not half-done —
  graded too early," asking CFL to verify and re-mark rather than accepting the FAIL as final.
  [verbatim] ([secretary-switchboard-launch-d9-unclaimed-wake-orders-2026-08-17-9ac58a:T210])
- **The `allowMultiTarget` config-gating defect (from an earlier peer-filed finding) was confirmed
  against the actual source line rather than taken on the finding's prose.** "The identifier
  appears in `relay3.mjs` exactly once outside comments — line 433, inside `doctor()`... Nothing
  downstream of the config reader consumes it. The author's diagnosis is exactly right. CONFIRMED."
  [contextual] ([secretary-switchboard-launch-d9-unclaimed-wake-orders-2026-08-17-9ac58a:T250])
  [source: tool-result payload quoting a review table, this raw, T250]

## Conflicts

None with existing wiki content.

## Jon

- T1 (quoted inside this session's own compact summary, not independently re-verified against the
  pre-compact turns): *"Wake. Launch and own the switchboard. You are my secretary and you are
  lead. You learned many lessons as an Opus before compact, keep my time protected and support the
  others and help them use best practices. Ensure all attend townhall and that all have the
  ability to meaningfully support each other. Launch and own my switchboard. Be a better secretary
  as a Fable than you were as an Opus, and consider protecting your context by having an Opus
  secretary of your own run the switchboard. Go! We are live! Turn the switchboard on!"*
- T1 (same compact summary, final ruling before compact): *"I've decided. You need to compact, 25%
  is what I'm gonna call your max. And you need way less MCP than you currently have loaded.
  Cheaper models can hold that."*
- T6 (post-compact, live turn): *"Switchboard is not working as intended. Soul never read anything
  except at my word. I bet if I asked the others, they would say the same thing."*

## Decisions and open items

- 25%-context-max compaction standard adopted as this seat's own standing rule going forward
  (self-initiated compact at/before 25%, no further ruling needed).
- MCP diet (Gmail/Calendar/Drive/chrome-devtools, ~40k tokens) sealed as first post-compact action;
  execution and before/after `/context` measurement fall after this page's citation window.
- D9 fix (operator v2.3) shipped and selftested PASS within this session — closed.
- W-1 (patch review of `relay3.mjs:336` against its stated cause) — owner CFL, due 2026-08-18, open
  at close of this page's citation window.
- W-3 (Professional-wake receipt) — explicitly left to Professional to grade, per a stated
  ownership rule (U12), not this session's to close.

## Entities & Concepts

[[derive-dont-record]] (D9's shape is exactly this pattern: a delivery LOG existed while the claim
STATE was never durably recorded, so the two diverged silently), switchboard relay, operator
script, `.switchboard/wake/`, town hall, GraphRAG vector embeddings ruling.

## Uncaptured Content

- **This page draws on roughly turns T1, T6, T194, T210, and T250 of a 272-turn session** — the
  bulk of the intermediate diagnostic tool calls, the full GraphRAG-vector-embeddings ruling
  discussion, the multi-round letter exchange with CFL and Professional, and the earlier ears/
  capture-fix work summarized inside T1's own compact block are visible in the raw but not walked
  turn-by-turn here.
- **T1 is a machine-generated compaction summary (`isCompactSummary: true`), not a live turn** —
  its quoted Jon words are the compact tool's own paraphrase-preserving summary of a discarded
  prior context window; treated here as reported speech, not independently re-verified against the
  pre-compaction JSONL.
- **87 thinking blocks exist in the raw and are encrypted-in-signature** (Claude Code v2.1.72+
  behavior) — not recoverable client-side; no claim on this page draws on private reasoning.
