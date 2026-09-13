---
title: "Branching speech-contingent continuations as forked KV cache, the eyes/brain/mouth/thoughts subagent mapping, and 'thinking blocks evaporate' corrected under ground-before-stating, 2026-08-01"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-01-9a904e-branching-language-model-responses-to-live-context.md
source_kind: session
date: 2026-08-01
retrieval_key: branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e
aliases: [forked KV cache speculative contingency decoding, feast ledger insight capture, eyes brain mouth thoughts subagent mapping, thinking blocks evaporate correction, ground before stating thinking block test design]
generated_by: coverage lane 7 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion
raw_sha256: f97e4f98106c73465ccee6bb82cdda7c43258dc5ae15cf128c70f0f2b86c875d
raw_length: 12068 bytes / 121 lines
uncaptured_assessed: populated
fidelity: paraphrase
tags: [claude-ai, frame-before-commit, ground-before-stating, kv-cache, subagent-architecture, thinking-blocks, feast-ledger, self-correction]
---

# Branching speech-contingent continuations and the "thinking blocks evaporate" correction, 2026-08-01

## Summary

Jon asks a late-night, fragmented three-part question sequence. First: could an LLM branch its
words on live contextual events (an angry face) at high fidelity, and how would that be
approximated in simulation — answered as a forked-KV-cache speculative-decoding architecture, with
the branching-factor-times-horizon constraint named as the binding limit. Second: a "feast ledger"
question connecting to a running self-critical pattern, which the assistant maps onto an
eyes/brain/mouth/thoughts subagent decomposition where "thoughts" get a precise referent — a
speculatively decoded continuation that was held but never committed — and observes nobody currently
watches the pruned branches for insight. Third, invoking ground-before-stating explicitly, Jon
challenges the assistant's own prior claim that thinking blocks evaporate; the assistant retracts
and retags the claim, distinguishing the narrow true version (not visible in-context across turns)
from the overstated one, and flags that Jon has asked this exact question before — a repeat-ask that
should have been a triage packet the first time, not re-litigated from memory each time.

## Key Claims

- **Jon's original branching question, verbatim, typos and ellipses his** — "If..... A large
  language model could branch its words based on live events and prune or preserve various Next
  words, in a live speach context at high fidelity, could it meaningfully preserve what if branches
  based on possible things that might occur in context? Such as an angry face. It might be wise to
  prepare for the next second. What.... How might that be approximated, assuming simulated
  environment"
  ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T1]).
- **The FBC trigger fires explicitly on the word "branch," and the assistant enumerates three
  candidate readings before committing to one** — speculative contingency decoding, model-predictive
  control, and value-function pruning — answering under the first as its inferred primary intent.
  "'Branch' is an FBC trigger, so: frames first." [verbatim]
  ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T2]).
- **The core mechanism proposed: a forked KV cache where all branches share the spoken prefix, each
  fork appends a discretized event token, and idle inference time between spoken words is used to
  speculatively decode top-k contingencies — cache hit on event arrival emits near-zero-latency,
  cache miss falls back to the reactive baseline at no extra cost.** "All branches share the prefix
  (everything said so far); each fork appends an event token — a discretized observation like
  `[LISTENER:angry]` — and then speculatively decodes a continuation during idle compute between
  spoken words... When the event arrives: cache hit → emit the prepared continuation with near-zero
  latency (verify-and-commit, same trick as speculative decoding); miss → discard and decode fresh,
  which costs only the reactive baseline. So preparation is strictly non-harmful except for
  compute." [verbatim]
  ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T2]).
- **The binding constraint is named as branching-factor × horizon, requiring a listener-simulator
  predictor of which few events are likely next, with a pre-registered success criterion (KL
  divergence between branch distributions) proposed for whether preserved branches actually buy
  adaptivity rather than just latency.** [paraphrase, condensed from the full architecture and
  "measure" steps]
  ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T2]).
- **The "feast ledger" question is read as pointing at a real instrumentation gap: the wiki's own
  stated purpose covers benefits and costs, but every existing instrument (lint, gap audits,
  verify_quotes) detects only faults, and no instrument detects an insight — so an in-conversation
  insight that was never reified functionally does not exist per the "Words Reify" rule.**
  "'I did not see it. I do not know what was in the logs' — the insights happened in-conversation or
  in thinking blocks and were never reified as durable objects, so per Words Reify, they
  functionally don't exist." [verbatim]
  ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T4]).
- **The eyes/brain/mouth/thoughts subagent mapping is worked out onto the branching architecture,
  and gives "thought" a precise referent: a speculatively decoded continuation that was held but
  never committed** — with the observation that pruned branches are discarded thoughts nobody
  currently watches, and that this is the same coordinator root defect already named elsewhere
  (state written to surfaces the next consumer doesn't read). "Thoughts = the preserved un-uttered
  branches themselves. This is the part I find genuinely interesting: in that architecture, a
  'thought' has a precise referent — a speculatively decoded continuation that was held but never
  committed. Pruned branches are discarded thoughts; the feast ledger question becomes 'which pruned
  branches contained insight, and who was watching them?' Nobody, currently. Thinking blocks
  evaporate." [verbatim]
  ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T4]).
- **Jon invokes ground-before-stating explicitly and challenges the "thinking blocks evaporate"
  claim, citing his own recent testing and asking for an audit-log design distinguishing "absent"
  from "wrong field parsed," plus the same question for Claude Code's JSONL captures.** "Ground
  before stating. Do thinking blocks evaporate based on recent testing in Claude.ai? logs should
  show my pasted summary and should either show same or more in thinking blocks, and should have
  audit logs to ensure we are not simply missing the right thing from the json." [verbatim, typos
  his] ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T5]).
- **The correction is accepted without apology and the claim is retagged and narrowed, not simply
  withdrawn** — the assistant distinguishes the overstated "evaporate" claim from a weaker, still-true
  version scoped to in-context visibility, and notes this is in tension with the Fable Mirror
  corpus's own `[THINKING-SUMMARY:date]` labels. "'Thinking blocks evaporate' → retagged [training,
  UNGROUNDED for current claude.ai], and in tension with [MEM]: the Fable Mirror corpus already
  ingests export transcripts plus extended thinking material with `[THINKING-SUMMARY:date]`
  labels... The evaporation claim survives only in the narrow form: not visible to me in-context
  across turns [grounded for this interface], which is a different and weaker claim." [verbatim]
  ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T6]).
- **The repeat-ask itself is flagged as a capture failure on the system's side, not something to
  re-answer from memory each time, and is proposed — not yet written — as a named triage-packet
  item.** "Repeat-ask flag: you noted this isn't the first time. That's a capture failure on the
  system's side — this belongs in a triage packet as a named item, not re-litigated from memory each
  time. Proposing, not writing: hold for a daytime 'write it.'" [verbatim]
  ([branching-forked-kv-cache-feast-ledger-thinking-blocks-evaporate-2026-08-01-9a904e:T6]).

## Conflicts

None found against existing wiki pages. id `9a904e` absent from `wiki/sources/**` before this page.
The corrected, narrower "thinking blocks evaporate" claim (not visible in-context across turns,
rather than absent from the export entirely) should be checked against any later wiki page asserting
the stronger, uncorrected version — this page is the origin point of the correction.

## Cross-Wiki

None — this is CFL infrastructure/architecture-speculation content (KV-cache branching design,
subagent decomposition, thinking-block provenance), not personal/home/pro domain material, though
the session itself closes on a household-planning aside ("Up late planning household orginization
and projects. But now sleep.") that is not developed as content. See [[wiki-query]] if present for
the provenance-ladder discipline (`[TRANSCRIPT]` > `[THINKING-SUMMARY]` > `[MIRROR-INFERENCE]`) this
session's correction directly exercises.
