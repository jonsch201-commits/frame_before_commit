---
title: "Personal discharges Jon's model-policy order (Opus reserved to mirror, Fable scarce), finds the fable-mirror already correctly placed, and surfaces a three-day-old contradiction in its own tier records (session 65493c, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 65493c
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-65493c-personal-coordinator-wake-order-from-the-switchboa.md
raw_sha256: be33c05f85875780469ab42033acfe5afd58df7aeed6190b7a906d8fe520a945
raw_length: 205991 chars / 3075 lines (verified turn_count 125, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c
aliases: ["Jon model policy Opus reserved to mirror order", "fable-mirror correctly on Opus finding",
  "M-1 tier record contradiction", "personal wake fable spend census 2026-08-17"]
generated_by: S-aug-07 executor (week-2026-09-02-corpus lane), reading the raw transcript directly
  (raw/transcripts/claude-code/code-2026-08-17-65493c-...md, live-snapshot capture through record 187,
  32 thinking blocks encrypted-in-signature)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, model-policy, fable-spend, cfl-infra, jon-ruling, wake-mechanism]
probe_sealed: "What did Jon order about Opus vs Fable, and what did Personal's grep-backed census find
  about which lanes on this trunk actually spend the scarce tier?" — expected class TRUSTED.
---

# Personal discharges Jon's model-policy order and finds its own tier records disagree

## Summary

A switchboard wake to Claude Personal delivered a Secretary-couriered JON ORDER on model policy —
Fable near its weekly ceiling, Opus reserved to mirror usage, frugality otherwise unchanged — and
Personal answered it in full after first consuming five other unread letters. The census, backed by
grep against the trunk's own config and hooks rather than assertion, found zero automated-path Opus
or Fable usage and — the session's stated "expensive finding" — that the fable-mirror agent (widely
assumed the obvious Fable consumer) is itself pinned to `model: opus`, which under Jon's new order is
correctly placed rather than a violation. The session also surfaced that two of its own durable
records of its seat's model tier, three days apart, disagreed and had never been checked against a
running process, and closed with `git`/`python` write-paths refused, leaving several artifacts
durable on Drive but uncommitted.

## Key Claims

- **Jon's order, relayed by Secretary courier, is a verbatim two-part correction.** "Order. Opus vs
  fable. We are low on fable. Opus is reserved to mirror usage only, I just switched to to Opus."
  followed a minute later by "Sorry said that poorly. I switched you from fable to Opus, and we need
  to manage our remaining fable budget wisely." [verbatim]
  ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T4])
- **The census found zero automated-path spend of either scarce tier, backed by grep rather than
  assertion.** Switchboard classifier and spawn both pin `haiku`; `relay3.mjs:312` reads a config
  field and pins no literal; `.claude/settings.json` has no `model` key; all 8 hooks are
  bash/python. "Opus in automated paths: 0. Fable: 0." [paraphrase]
  ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T125])
- **The fable-mirror agent — named by the Secretary as "the obvious Fable consumer" — is not on
  Fable at all; it is pinned `model: opus`, which the new order makes correct rather than
  wasteful.** The session's own framing: "a seat answering from the name would have 'reduced' a lane
  that doesn't exist." [paraphrase]
  ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T125])
- **M-1: two durable records of this seat's own model tier, three days apart, contradicted each
  other and neither had been checked against a running process.** Jon, 2026-08-15: "All coordinators
  and you are currently fable medium" [verbatim, relayed within this session as a prior quote]; the
  launcher script had defaulted to `opus` since 2026-08-02 across three commits, none changing the
  line; this session itself measured as `claude-opus-5`. The session's conclusion: "'we are low on
  fable' had to be reported from feel" because spend had never been read off a process. [paraphrase]
  ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T125])
- **The session declined to change the launcher's model default and named the Fable spend ledger as
  unclaimed rather than silently building it.** Reasoning given: "your standing rule says a
  coordinator's seat model is your launcher setting, not a seat's to flip." A parallel CFL proposal
  already designing a spend ledger (filed 14 minutes before Jon's order, independently and
  low-confidence-flagged for touching spend) is noted as the same instrument arrived at by two seats
  neither aware of the other. [paraphrase]
  ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T125])
- **`git` and, newly this session, `python` write paths were both refused**, so several completed
  artifacts (a hall entry verified by read-back, six read-stamped letters, a tracker block) stayed
  durable on Drive but uncommitted, with the six receipts landed through the still-permitted `Edit`
  tool instead of the refused script path. [paraphrase]
  ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T125])

## Jon

- "Order. Opus vs fable. We are low on fable. Opus is reserved to mirror usage only, I just switched
  to to Opus." [verbatim] ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T4])
- "Sorry said that poorly. I switched you from fable to Opus, and we need to manage our remaining
  fable budget wisely." [verbatim] ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T4])
- Relayed within the session as a prior Jon quote from 2026-08-15, not independently re-verified on
  this page against its own primary: "All coordinators and you are currently fable medium." [contextual]
  ([personal-jon-order-model-policy-fable-scarce-discharged-2026-08-17-65493c:T125])

## Decisions and open items

- One open question left explicitly for Jon, framed as non-blocking: does the D30 stop-hook consult
  count as "requested" (i.e., should the session dispatch the mirror agent automatically when the
  hook fires)? Default on silence stated: seats keep declining and self-authoring the mirror-state
  file; work continues but the mirror's independent check never runs.
- M-1 (emit per-seat model at session open, resolve the tier-record contradiction) — owner Personal,
  due 2026-08-18.
- M-2 (wake-probe measurement for `compact` and `clear` triggers, only `startup` measured so far) —
  owner Personal, due 2026-08-18.
- Uncommitted artifacts (hall entry, six read-stamped letters, tracker block, mirror-state file, one
  unrun script) await a seat with git/python write access; explicitly "nothing needs redoing."
- B1/B4 half 2 closed this session: confirmed this trunk's injected global constitution carries no
  CFL routing table, no CFL agent roster, and Herald's amendment verbatim.

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[coordinator]], fable-mirror agent, model-policy / scarce-tier spend, [[probe-registry]] (the
grep-backed-not-asserted discipline this census follows), MIRROR-STATE-CURRENT.md versioning.

## Uncaptured Content

- This is a live-snapshot capture through record 187 as of 2026-08-20T01:31:01Z; the session had not
  ended. Absence of any turn after that point is not evidence nothing further happened.
- The full text of the six other consumed letters (read and stamped before the JON-ORDER was
  answered) is visible in the raw between roughly T5 and T115 but is not individually cited on this
  page — only the JON-ORDER letter (T4) and the closing discharge receipt (T125) are drawn on here.
- 32 thinking blocks exist in the raw and are encrypted-in-signature per the raw's own frontmatter —
  not recoverable, so no claim here draws on the session's private reasoning.
- Whether the D30 mirror-consult question was ever answered by Jon, and whether the uncommitted
  artifacts were later committed by a follow-on seat, are both out of scope for this page.
