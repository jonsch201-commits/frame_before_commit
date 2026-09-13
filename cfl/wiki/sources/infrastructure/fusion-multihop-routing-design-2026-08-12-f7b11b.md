---
title: "Fusion — Haiku hop-routing to core-memory JSON, verbatim-propagation objection, and a pre-registered offline prototype (claude.ai session f7b11b, 2026-08-12)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: f7b11b
source_kind: session
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-12-f7b11b-untitled.md
raw_sha256: 7eda7cc050b577923f0a6cdc9da6eb0d1e86c17d6412e8706cb54941bbacdf16
raw_length: 9132 chars / 92 lines (verified turn_count 2, turn_index.py, header_style md)
date: 2026-08-12
retrieval_key: fusion-multihop-routing-design-2026-08-12-f7b11b
aliases: ["Fusion architecture proposal 2026-08-12", "Haiku hop routing core memory", "verbatim ID
  propagation objection", "F-1 through F-6 Fusion findings", "multi-model fusion prototype
  pre-registration"]
generated_by: S-augM-02 synthesis lane (week-2026-09-02 corpus lane), reading the claude.ai native
  export extract directly (raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-12-f7b11b-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [fusion, multi-model-routing, core-memory, haiku-routing, surface-registry, prototype-design]
---

# Fusion — Haiku hop-routing, the verbatim-propagation objection, and a pre-registered prototype

## Summary

An untitled claude.ai session in which Jon deposited a single long design message proposing
"Fusion": a Haiku-fronted hook that copies his verbatim text to a chat log, then a Haiku call
decides which core-memory JSON(s) to activate (soul/CFL/Herald/professional), typically routing
first through an Opus "ears" executor to decompose/clarify/reformat before a second Haiku call
resumes the right JSON and a coordinator opens a thread. Jon flagged this as unfinished ("Nit sure
on all final details, must be worked out in context. To prototype!"). The assistant identified
"Fusion" as an existing wiki term with prior art it had not yet read, raised a load-bearing
objection (a chat log alone is not enough — verbatim propagation needs an ID that survives every
hop, not just a searchable log), enumerated six findings (F-1 through F-6) against the design, and
proposed a smallest-testable prototype (an offline replay of ~10 real Jon messages through a 2-hop
chain, scored on hedge-survival and routing-match) with thresholds to be pre-registered before any
build. Nothing was written or deposited in this session; two questions to Jon are open at close.

## Key Claims

- **Jon's design proposal for "Fusion": a hook copies his verbatim message to a chat log; Haiku
  decides which core-memory JSON(s) to activate, possibly in parallel; the message is typically
  routed first to an Opus "ears" executor to decompose/reformat/clarify; a second Haiku call then
  routes the ears output to resume the right JSON; a coordinator opens a thread and continues.**
  Explicitly framed as unfinished design, not a decision. [verbatim]
  ([fusion-multihop-routing-design-2026-08-12-f7b11b:T1])
- **"Fusion" is already a wiki term with unread prior art**: `sources/infrastructure/
  triage-project-model-direction-2026-07-11-a3e6cf.md` is titled covering "Multi-Model Fusion,"
  plus `concepts/multi-agent-orchestration.md` (7 sources) and `concepts/coordinator.md` (4
  sources) — the assistant states it read none of these before responding and flags they should be
  read before design, not after. [paraphrase]
  ([fusion-multihop-routing-design-2026-08-12-f7b11b:T2])
- **Load-bearing objection: a chat log is not sufficient; verbatim propagation needs a durable ID,
  not just searchability.** Cites the mid-turn-message finding from
  `close-fable-mirror-standard-update-2026-08-02.md` — nine messages Jon typed to the mirror, none
  of which reached main as principal input, recovered only afterward from subagent JSONL and
  becoming primary evidence correcting six downstream captures. Concludes: "Fusion doesn't fix that
  surface — it multiplies it by the number of hops," and that what's missing is an ID propagating
  through every derived message back to its verbatim source turn. Ties this to the Surface
  Registry, described as still "recommended, not approved" as of `cfl-video-implementation-
  planning-2026-07-26`. [paraphrase] ([fusion-multihop-routing-design-2026-08-12-f7b11b:T2])
- **Six enumerated findings (F-1 through F-6) against the design as stated**: F-1 — Haiku on hop-1
  routing is the cheapest model on the highest-variance decision; proposes asymmetric labels
  (default to ears, require high confidence to bypass) rather than upgrading the router model. F-2
  — hop-2 routing must see Jon-verbatim AND the ears output, not derived text alone, or an ears
  misread propagates unchecked. F-3 — disputes the "cheaper" framing as unmeasured; decomposition
  wins only when subtasks parallelize/downsize/resume, and needs an explicit bypass lane plus a
  pre-registered cost number. F-4 — model selection is already solved in `.claude/agents/`
  frontmatter (PR #51 merged config), but effort-binding for mid-session fleet registration is
  logged unverified (PR #52, "re-observe on next cold dispatch") and Fusion depends on that
  binding. F-5 — the verbatim hook has a known landmine: `agent_end_ingest.py` already had to write
  to gitignored space because writing to tracked space aborted `git pull --ff-only` at
  SessionStart, measured three times; a new verbatim hook must avoid repeating this. F-6 — the
  coordinator-dispatches-never-adopts invariant applies: in Fusion the coordinator opening the
  thread and writing the first message is dispatch, not adoption, and should be made explicit in
  the design. [paraphrase] ([fusion-multihop-routing-design-2026-08-12-f7b11b:T2])
- **Proposed smallest-testable prototype, not built**: replay ~10 real Jon messages spanning the
  ambiguity range through a 2-hop chain (Haiku route -> ears decompose -> Haiku route), scoring at
  each hop whether every hedge/qualifier survived (named failure mode:
  `hedge-flattening-and-invented-rulings.md`, with a measured prior instance) and whether hop-2
  routes the same as an Opus reading of the verbatim would. Explicitly offline, against the
  existing corpus (1,214 indexed Jon-turn rows), no live system or Docker, pass thresholds to be
  pre-registered before running. [paraphrase]
  ([fusion-multihop-routing-design-2026-08-12-f7b11b:T2])
- **Session closes on two open questions to Jon, neither answered in this raw**: (a) whether the
  assistant should read the 2026-07-11 Multi-Model Fusion page and reconcile before proceeding, or
  treat this as a deliberately fresh design, and (b) whether Jon wants a Claude Code handoff for the
  replay harness. [uncaptured] ([fusion-multihop-routing-design-2026-08-12-f7b11b:T2])

## Jon

> "Fusion. I send Haiku a message, a hook fires to copy my text verbetum to the chat log. Haiku
> determines based on policy which json (core memory) to activate with my message. It can choose to
> activate multiple in parallel, or just one. It is loaded with skills to determine the rules. E. G.
> To soul or CFL or Herald or professional, fable or Opus, coordinator or project manager or
> executor. This message, for example, would likely be first sent to an Opus executor(ears) to
> decompose and reformat and clarify and route further. It's gonna have many parts, and have non
> clarity sometimes, and may need reformatting for clarity, or routing to multiple agents in pieces.
> That said, the chat log is the log. Questions open, and 'what did Jon actually say' is a good
> one, as is 'did the ears misunderstand something' often helps. Either way, the message being sent
> would again activate haiku to consider the best json to resume for the task based on the message
> the ears executor sent. From there, a coordinator would open a new thread and write a message
> there, and it would continue. But as you go deeper like this, you must ensure good model
> selection choices. We're breaking down problems to their components to make them more digestible
> and reviewable and cheaper and easy to 'remember' (can always resume json from point it ended).
> Executors should be sonnets or Opus, depending on the complexity of the task. Nit sure on all
> final details, must be worked out in context. To prototype!"
> — [fusion-multihop-routing-design-2026-08-12-f7b11b:T1] (verbatim, typos his: "verbetum", "Nit
> sure")

## Decisions and open items

- No decision was ratified in this raw — Jon's own framing is "To prototype!" and the assistant's
  response is a proposal with two open questions, not a build.
- Open: whether to reconcile with the existing 2026-07-11 Multi-Model Fusion page before further
  design, or treat Fusion as deliberately fresh — not answered here.
- Open: whether Jon wants the Claude Code handoff for the offline replay-harness prototype written
  — not answered here.
- Open, cited as a standing gate: Surface Registry approval, still "recommended, not approved" as
  of the 07-26 reference cited in T2.
- Open, cited as a dependency: PR #52's effort-binding-for-mid-session-fleet-registration is logged
  unverified and Fusion's model-selection design (F-4) depends on it holding.

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[frame-before-commit]] (F-6's coordinator-dispatches-never-adopts invariant is the same discipline
class), Surface Registry, core-memory JSON activation, multi-hop routing, Haiku/Opus/Sonnet model
selection, `hedge-flattening-and-invented-rulings`.

## Uncaptured Content

- **The two prior-art wiki pages named (`triage-project-model-direction-2026-07-11-a3e6cf.md`,
  `concepts/multi-agent-orchestration.md`, `concepts/coordinator.md`) are cited by title only** —
  the assistant explicitly states it had not read them before responding in this session, so this
  page does not draw on their content, only on the fact of their existence as flagged prior art.
- **No reply from Jon exists in this raw** — the session as captured ends on the assistant's two
  open questions; whether or how Jon answered is not known from this file.
