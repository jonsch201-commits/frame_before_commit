---
title: "Claude.ai compaction (token-based) vs prompt-cache TTL (time-based), the cold-read cost of sporadic returns, and five moves to give a claude.ai project SDK-agent-equivalent memory, 2026-08-05"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-05-10a99d-claude-conversation-token-caching-and-session-resu.md
source_kind: session
date: 2026-08-05
retrieval_key: claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d
aliases: [compaction token-based not time-based, prompt cache TTL 5 minute 1 hour, sporadic return cold read cost, claude.ai project SDK agent parity, surface registry two-channel pattern, cold-probe gate packet self-containment test]
generated_by: coverage lane 7 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion
raw_sha256: ae8422f65361b75698434a1f0959b52b619579debf89b9d00342fd10c1d8a86d
raw_length: 7291 bytes / 70 lines
uncaptured_assessed: populated
fidelity: paraphrase
tags: [claude-ai, token-caching, compaction, ttl, session-resumption, project-parity, surface-registry, cold-probe]
---

# Claude.ai token caching, compaction, and SDK-agent memory parity, 2026-08-05

## Summary

Jon asks two questions in one session. First: whether claude.ai conversation summarization is purely
token-triggered or has a time element, and whether resuming a session after a long gap costs extra
budget as prompt-cache entries expire. The assistant, after web search, separates two distinct
mechanisms — compaction is token-threshold-triggered with no time element, while the prompt cache
has a time-based TTL (5-minute default, 1-hour tier) that does expire — and grounds the practical
answer: a sporadic return to a long-lived chat is a cold read, reprocessing full context at
cache-write cost, which bears directly on triage-session cadence. Second: what it would take for a
claude.ai project to have memory and skill access equivalent to a Claude Code SDK agent restricted
to one writable folder plus a listening coordinator. The assistant reframes equivalence as achieved
by protocol rather than platform and gives five concrete moves, then pushes back on the framing
itself — full parity may not be the right target, since the claude.ai project's comparative
advantage is triage/shaping rather than execution.

## Key Claims

- **Jon's original two-part question, verbatim, typos his** — "Find documentation. How slash when
  does do Claude. Ai conversations summarize or compact? If it's exclusively token based with no
  time element, does resuming a Claude.ai session ever cost extra token budget based on a long time
  vs zero time between messages as KV hashes expire? Or does it stay cashed as a rule?"
  ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T1]).
- **Two mechanisms are separated as structurally different: compaction is token-threshold-triggered
  with no time element; the prompt cache is time-based and does expire.** "Compaction: token-based,
  not time-based. Compaction triggers when the conversation reaches a token threshold approaching the
  context window limit — no time element... Prompt cache: time-based, and it does not stay cached as
  a rule. Cache entries expire after a period of inactivity. Current tiers: default 5-minute TTL,
  with a 1-hour option." [verbatim]
  ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T2]).
- **A specific documented incident is cited: a silent reversion from a 1-hour to a 5-minute TTL for
  Claude Code subagents in March 2026 caused measurable quota-consumption spikes for subscription
  users**, contrasted with the main conversation's documented 1-hour TTL on subscriptions.
  [verbatim, condensed]
  ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T2]).
- **The practical answer to Jon's cost question is stated as structurally yes, with an internal
  Anthropic tooling doc quoted and quota accounting explained** — cache-creation tokens count at full
  rate, cache reads run roughly 10% of input price on hits versus roughly 125% on 5-minute writes —
  and the claude.ai-specific TTL is explicitly flagged as ungrounded/assumed rather than confirmed.
  "Sleeping past 300 seconds means the next wake-up reads your full conversation context uncached —
  slower and more expensive... [UNGROUNDED → ASSUMED] The one gap: Anthropic doesn't publish the
  exact TTL claude.ai's web app uses... What's firmly grounded: resuming a chat after hours/days is a
  cold read — full context reprocessed as a cache write, consuming more usage budget than the same
  message sent within the TTL window. Rapid back-and-forth is the cheap regime; sporadic returns to a
  long chat are the expensive one. This directly bears on your triage-session cadence: a long-lived
  claude.ai session touched once a day pays near-full context cost per touch." [verbatim]
  ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T2]).
- **The SDK-parity question is reframed at the outset: equivalence is achieved by protocol, not
  platform, contrasting the SDK agent's guaranteed-fresh skill reads / file-based memory / hooks
  against the claude.ai project's injected files (staleness risk), auto project memory (lossy,
  unaudited), and the user's own manual refresh acting as the hook.** [paraphrase, framing sentence]
  ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T4]).
- **Move 1, named the single biggest lever: make the memory surface a file, not claude.ai's native
  memory** — a canonical distilled digest in the writable folder, read at session open, with the
  platform's auto project memory explicitly downgraded to `[UNGROUNDED]` convenience because it is
  recency-biased, unauditable, and carries no provenance tags. [verbatim, condensed]
  ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T4]).
- **Move 2 proposes a human-actuated SessionStart-hook substitute: version stamps in each skill's
  frontmatter plus a version manifest in the wiki index, so a session-open ritual can compare
  injected copies against the manifest and flag drift mechanically rather than by vibes.**
  [paraphrase] ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T4]).
- **Move 3 names a recurrence risk explicitly: write access to a folder means nothing if the
  coordinator doesn't poll it, framed as the coordinator-root defect class** — requiring a Surface
  Registry entry, the two-channel directives-out/questions-back pattern, and explicit acks so silence
  stays permanently uninformative in both directions. [verbatim, condensed]
  ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T4]).
- **Move 4 states the cold-probe gate as the literal test for packet self-containment: if a fresh
  coordinator instance can't act on a packet from the packet alone, the packet is defective** — since
  file-drop comms, unlike SDK-to-coordinator comms on shared session state, are always a cold read on
  pickup. [verbatim] ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T4]).
- **The session closes with a self-flagged pushback on its own five-move answer: full parity may be
  the wrong target, because the claude.ai project's comparative advantage is triage/shaping while the
  SDK agent's is execution, and pursuing full parity risks making the triage instance a worse shaper
  without making it a meaningfully better executor.** "[instinct, flagged] One pushback: 'equivalent'
  may be the wrong target. The claude.ai project's comparative advantage is triage/shaping
  (ambiguity-to-shape channel); the SDK agent's is execution (verbatim-to-commit). Full parity spends
  effort making the triage instance a worse executor instead of a better shaper. Items 1–3 are worth
  doing regardless; item 4 you mostly have; beyond that, parity for its own sake looks like scope
  creep." [verbatim]
  ([claude-ai-token-caching-compaction-and-project-sdk-parity-2026-08-05-10a99d:T4]).

## Conflicts

None found against existing wiki pages. id `10a99d` absent from `wiki/sources/**` before this page.
This page's claude.ai-TTL-unconfirmed flag should be checked against any later wiki page that
asserts a specific claude.ai prompt-cache TTL as grounded fact — per this session, that value was
never independently confirmed, only assumed by analogy to Claude Code's documented subscription
tiers.

## Cross-Wiki

None — this is CFL infrastructure content (token-caching mechanics, session-architecture parity
design), not personal/home/pro domain material. See [[wiki-query]] if present for the cold-probe
gate this session applies as a packet-self-containment test.
