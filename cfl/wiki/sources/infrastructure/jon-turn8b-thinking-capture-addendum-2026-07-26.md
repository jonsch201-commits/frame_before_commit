---
title: "Jon Dispatch Addendum — Turn 8b: Thinking-Capture Facts and Step-(0) Additions (2026-07-26)"
aliases: [thinking-capture-facts-2026-07-26, model-reasoning-visible-convention-2026-07-26]
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 4 vs corpus 3 on authored labels"
source_kind: session
retrieval_key: jon-turn8b-thinking-capture-addendum-2026-07-26
generated_by: wayfinder (claude.ai FL wayfinder), verified against docs 2026-07-26
origin: wiki/intake-triage/jon-turn8b-thinking-capture-addendum-2026-07-26.md
audit_state: unaudited
status: ACTIVE. Amends [[jon-turn8-fbcfork-skilldefects-canonical-nightly-docker-gate-2026-07-26]] §1 step (0). Ten days unrouted before this ingest (deposited 2026-07-26, ingested 2026-08-05).
maintained_by: coordinator (deposit); wiki-master ingests
tags: [jon-ruling, thinking-capture, fbc-fork, model-reasoning-visible, wayfinder]
---

# Ingest note (wiki-master, SU-close step 4, 2026-08-05)

Ingested verbatim from `wiki/intake-triage/jon-turn8b-thinking-capture-addendum-2026-07-26.md`, content
unchanged below. **This is a wayfinder fact-finding addendum, not a Jon-verbatim quote capture** — the
source file carries no blockquoted Jon text; it reports Jon's stated concern in the wiki-master's own
paraphrase ("Jon regards loss of Claude's thinking summaries as a KEY PROJECT DEFECT") and then verified
platform facts against docs. Preserved exactly as such — no quote was invented to dress this up as a
direct capture.

**Known non-conformance, flagged not silently fixed:** original file has no `retrieval_key`/`aliases`
block — added at ingest. The three cited technical claims (summarized-thinking API behavior, CC's
always-summary visible layer, adaptive-thinking parameter) were not independently re-verified against
current docs.claude.com during this ingest pass — carried as reported, UNRESOLVED whether still accurate
as of 2026-08-05 (ten days after this file was written; platform docs can move).

---

# Turn-8b addendum — thinking-capture facts (wayfinder-verified against docs 2026-07-26) and three step-(0) additions

Jon regards loss of Claude's thinking summaries as a KEY PROJECT DEFECT. Verified state:

1. **Messages API / Agent SDK returns SUMMARIZED thinking to any API key** — no license tier gates it. `display: "summarized"` on the thinking config returns readable summaries; omitted returns empty. Raw chain of thought is never returned on current models (explicit for Fable 5 / Mythos 5). The summaries are the recoverable ceiling — and they are the artifact Jon values.
2. **Claude Code's visible thinking was always the summary layer** (documented; McCanna/HN 2026-06). Local split per our own corpus frontmatter: subagent JSONLs recently carry `encrypted-in-signature` only; main sessions have carried readable summaries.
3. **Adaptive thinking note:** on newest models `thinking: {type: "adaptive"}` supersedes manual `budget_tokens`; verify current parameter names during step (0), do not assume.

Three additions to FBC-Fork step (0), all cheap:
(0a) Empirically inventory thinking content in a FRESH claude.ai export zip vs a pre-UI-change zip (grep the message JSON for thinking blocks; the chat-exporter parser already counts `thinking_blocks`). Report what the zips actually carry now — Jon asked for confirmation and docs do not answer it.
(0b) Verify `--forward-subagent-text` / `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT` recovers SUBAGENT thinking summaries into stream-json — this is the fix for the encrypted-in-signature gap.
(0c) Verify Agent SDK thinking config (`display`, adaptive vs enabled, effort) against platform docs at build time.

Standing convention, effective now (wayfinder-proposed, mechanics): externalized on-page reasoning is the platform-independent fallback — any instance asked to "reason on the page" writes its reasoning in the visible response, captured verbatim by every export path. Provenance bracket: [model-reasoning-visible] — authored claim about reasoning, distinct from [model-thinking] native traces; the §1(2) faithfulness battery is what tests both against behavior. Neither bracket is ever ground truth of reasoning.

— relayed by the wayfinder; silence is never approval. — Jon
