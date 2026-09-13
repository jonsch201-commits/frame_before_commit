---
title: "Implementing CFL hooks effectively — board-of-advisers corpus fencing, ears/mouth organ mapping, PreCompact capture-not-canonize — claude.ai chat 217404, 2026-08-01"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 217404
source_kind: session
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-01-217404-implementing-cfl-hooks-effectively.md
raw_sha256: 68c3c04033f40bbd8db7b1a5053447ab9d4fd286214e690549b649ac34885176
raw_length: 13562 chars / 132 lines (verified turn_count 8, turn_index.py, header_style md)
date: 2026-08-01
retrieval_key: cfl-hooks-organs-framework-precompact-capture-217404-2026-08-01
aliases: ["implementing CFL hooks effectively", "board of advisers corpus fence", "eyes ears mouth brain organs framework", "PreCompact capture not canonize"]
generated_by: S-augM-07 executor (week-2026-09-02-corpus lane), reading the raw claude-ai export directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [hooks, organs-framework, precompact, corpus-fence, cfl-infra]
---

# Implementing CFL hooks effectively — advisory-lens fencing, organs framework, PreCompact design — 217404, 2026-08-01

## Summary

Jon asked what a reviewed video's ideas were worth to CFL, given CFL "already exceeds it on every
axis." The session surfaced one structurally novel pattern (a corpus-fenced "board of advisers"
generalizing the fable-mirror architecture to external experts' public corpora) and two smaller
ones, then — across three follow-up turns — designed a citation/fencing scheme for external
corpora, mapped Jon's own "eyes/ears/mouth/brain" organs framework onto the Jon-Claude interface
itself (an `UserPromptSubmit` hook as "ears," Stylomantic as "mouth"), and reasoned through
PreCompact-hook design, landing on "capture, not canonize" as the governing rule.

## Key Claims

- **The board-of-advisers idea is explicitly gated behind a hard anti-pastiche rule and a
  conflict-of-interest self-flag.** Verbatim: "the CFL-native version is a **corpus-grounded
  advisory lens** with tags like `[CORPUS:person@source]` and a hard rule against pastiche
  presented as the person's view ... COI note: I have a mild pull toward validating item 1
  because it flatters an architecture I'm part of — discount accordingly." [verbatim]
  ([cfl-hooks-organs-framework-precompact-capture-217404-2026-08-01:T2])
- **The proposed external-corpus fencing is explicit that training-data bleed is the main hazard,
  not a side concern.** Verbatim: "The model already 'knows' any public figure from training and
  will blend pastiche with corpus content unless fenced ... labels like `[CORPUS:name@work:¶n]`
  for grounded content and `[ADVISOR-INFERENCE:name]` for extrapolation ... Never unlabeled 'X
  would say.'" [verbatim] ([cfl-hooks-organs-framework-precompact-capture-217404-2026-08-01:T4])
- **"Improve-system" capture is explicitly recommended NOT to fire on every compact, with the
  reasoning stated.** Verbatim: "Compaction fires under context pressure, which is precisely when
  capture fails (the 1.65M-char queue vanished under the words 'nothing lost'). Wrong trigger.
  Better: capture at correct-then-accept — the moment you revise a draft and then approve it,
  that delta is signal by definition." [verbatim]
  ([cfl-hooks-organs-framework-precompact-capture-217404-2026-08-01:T4])
- **Jon's own prior "eyes/ears/mouth/brain" organs framework is extended, by his own framing, from
  CFL's internal organs to the Jon-Claude interface itself** — "ears" proposed as a cheap
  `UserPromptSubmit` hook producing a paired `{command: raw verbatim, intent: normalized}` object,
  with an explicit fence that the normalizer "never replaces raw, only appends, and must be
  conservative ... since normalization is itself a hop hedges must survive"; "mouth" identified
  as Stylomantic's existing conditional-logit re-ranker, reframing its priority as already-built
  rather than a queued item. [paraphrase]
  ([cfl-hooks-organs-framework-precompact-capture-217404-2026-08-01:T6])
- **A PreCompact hook is explicitly recommended to capture rather than canonize**, pushing back on
  Jon's own framing that it might "self-branch into wiki-master." Verbatim: "A PreCompact hook
  that self-branches into wiki-master and writes wiki proper is an ungated durable write at
  exactly the moment quality control is weakest. Better: hook dispatches a capture-only pass ...
  and wiki-master ingests through the normal SU gate ... Capture beats the loss event; the gate
  stays intact." [verbatim]
  ([cfl-hooks-organs-framework-precompact-capture-217404-2026-08-01:T8])
- **A concrete memory-edit is proposed and explicitly gated on Jon's confirmation, not written
  unilaterally**: "The CFL wiki is the sole source of truth and grounding. Memories are a
  cache/pointer layer only ... On conflict, wiki wins." — offered with "added on your confirm."
  [verbatim] ([cfl-hooks-organs-framework-precompact-capture-217404-2026-08-01:T8])

## Conflicts

None with existing wiki content.

## Entities & Concepts

Fable-mirror architecture (board-of-advisers generalization), [[record-architecture-v1]]
(Source-Page Standard extension for external corpora), PreCompact hook design,
Surface Registry (named as a blocking prerequisite for organ hooks), Stylomantic, write-gate
("no write without 'write it'").

## Uncaptured Content

- **No intake-triage packet had been written as of the session's end** — every design element
  (advisory-lens architecture, organ-hooks spec, PreCompact capture-only pass) is stated as
  pending Jon's explicit "write it," and this raw does not show that authorization being given.
- **The referenced "video" this session opens by evaluating is not itself read or summarized
  here** — only the session's judgment of what survives from it is captured.
