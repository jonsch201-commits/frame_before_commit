---
title: "Virtual SIM / cloud-telephony capability planning for CC — write-gate design mapped onto call risk, then parked — claude.ai chat 466bf9, 2026-08-02"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 466bf9
source_kind: session
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-02-466bf9-virtual-sim-calling-capabilities-in-claude.md
raw_sha256: 02b13a1a2a11be49e9bc2317a1c7851b5bbf41db6eaed755c33099755f3b8f09
raw_length: 8816 chars / 91 lines (verified turn_count 6, turn_index.py, header_style md)
date: 2026-08-02
retrieval_key: telephony-capability-planning-write-gate-466bf9-2026-08-02
aliases: ["virtual SIM calling capabilities in Claude", "Twilio for Claude cloud telephony", "call-gate allowlist commitment ceiling", "Ollama quarantine tier for calls"]
generated_by: S-augM-07 executor (week-2026-09-02-corpus lane), reading the raw claude-ai export directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [write-gate, capability-planning, telephony, cfl-infra, held-item]
---

# Telephony capability planning for CC — write-gate design mapped onto call risk, then parked — 466bf9, 2026-08-02

## Summary

Jon asked whether Claude Code could place phone calls for him via a virtual SIM or similar, in a
secure environment, and what responsible-use design that would need. The session found that
"Twilio for Claude" (a Connector + CC plugin, launched May 2026) makes CC an initiator/dispatcher
of calls while a separate realtime voice model actually conducts the live conversation, then
mapped CFL's existing write-gate architecture (explicit per-action gate, allowlists, disclosure,
mandatory transcript capture, spending caps, commitment ceilings) onto the specific risks of a
phone call as a durable third-party commitment. After a follow-up on an Ollama local-quarantine
tier and caller-ID options, Jon decided against building it now, and the session recorded the
decision to park rather than discard the design.

## Key Claims

- **CC is framed as coordinator/dispatcher, not the live voice, with an explicit architectural
  split.** Verbatim: "Claude Code can *initiate and manage* calls, but it can't *be* the voice on
  a live call — the real-time loop (streaming audio, sub-second latency) needs a dedicated
  realtime voice model ... the honest framing: CC is the coordinator/dispatcher; a separate voice
  runtime executes the call; CC retrieves the transcript afterward. That maps cleanly onto your
  existing coordinator-PM pattern." [verbatim]
  ([telephony-capability-planning-write-gate-466bf9-2026-08-02:T2])
- **A phone call is explicitly framed as a higher-stakes write-gate case than prior gated
  actions**, because it is "a durable, irreversible commitment made to a third party in your
  name" — the response maps CFL's existing gate vocabulary onto it: a per-call gate (never
  standing authorization), a business-only number allowlist, a mandatory AI-disclosure script, a
  mandatory transcript-to-wiki requirement, spending/call caps enforced outside the agent, and a
  dollar-bounded commitment ceiling with cooling-off for anything the agent can't reverse by a
  follow-up call. [paraphrase] ([telephony-capability-planning-write-gate-466bf9-2026-08-02:T2])
- **A conflict-of-interest is explicitly self-flagged inline**: "`[COI]` note: I'd be the one
  gaining a new action channel here, so discount my enthusiasm accordingly." [verbatim]
  ([telephony-capability-planning-write-gate-466bf9-2026-08-02:T2])
- **An Ollama local-quarantine tier is scoped precisely, distinguishing what it controls from what
  it cannot.** Verbatim: "What it buys you: nothing reaches *Anthropic* without approval ... What
  it doesn't buy: 'sending nothing anywhere.' A phone call necessarily transits the telephony
  provider ... the honest tiering: Anthropic-exposure is fully controllable; telephony-carrier
  exposure is structural; realtime-model exposure depends on the local-voice-loop experiment."
  [verbatim] ([telephony-capability-planning-write-gate-466bf9-2026-08-02:T4])
- **The session closes on Jon's own decision to defer, and records the disposition explicitly as
  parked, not lost.** Verbatim (Jon): "Not worth it at this time, may be when tooling is easier
  and less apparently risky." The response: "No packet written, per write-gate ... this stays
  transcript-only" unless Jon wants a one-line HELD entry so it surfaces in future sequencing.
  [verbatim] ([telephony-capability-planning-write-gate-466bf9-2026-08-02:T5],
  [telephony-capability-planning-write-gate-466bf9-2026-08-02:T6])

## Conflicts

None with existing wiki content.

## Entities & Concepts

Write-gate architecture (call-gate/allowlist/commitment-ceiling extension), Twilio-for-Claude MCP
integration, [[record-architecture-v1]] (HELD disposition class), feast-ledger capture-without-
distillation failure mode (named inline as the risk of letting this vanish untracked).

## Uncaptured Content

- **No intake-triage packet was written for this design**, per the session's own stated write-gate
  discipline ("No packet written, per write-gate") — the full call-gate/allowlist/quarantine
  design exists only in this transcript, not as a durable wiki object, unless a future session
  acts on the offered one-line HELD entry.
- **The exact wording of "your existing phone number" is Jon's own device**, not disclosed on this
  page beyond the fact that it exists — no phone number, carrier account, or other identifying
  detail is repeated here.
