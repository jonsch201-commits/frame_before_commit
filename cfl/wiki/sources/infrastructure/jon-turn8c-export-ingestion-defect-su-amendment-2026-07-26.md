---
title: "Jon Dispatch Addendum — Turn 8c: Export-Ingestion Defect CONFIRMED, SU Definition Amended (2026-07-26)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 6 vs corpus 5 on authored labels"
source_kind: session
retrieval_key: jon-turn8c-export-ingestion-defect-su-amendment-2026-07-26
aliases: [export-ingestion-defect-confirmed-2026-07-26, su-corpus-recency-step-2026-07-26]
generated_by: wayfinder (claude.ai FL wayfinder), verified empirically 2026-07-26
origin: wiki/intake-triage/jon-turn8c-export-ingestion-defect-su-amendment-2026-07-26.md
audit_state: unaudited
status: ACTIVE — one confirmed defect, one standing-rule amendment, one narrowed check. Amends [[jon-turn8-fbcfork-skilldefects-canonical-nightly-docker-gate-2026-07-26]] and [[jon-turn8b-thinking-capture-addendum-2026-07-26]]. Ten days unrouted before this ingest (deposited 2026-07-26, ingested 2026-08-05).
maintained_by: coordinator (deposit); wiki-master ingests
tags: [jon-ruling, export-ingestion, standard-update, su-amendment, corpus-recency, thinking-capture]
---

# Ingest note (wiki-master, SU-close step 4, 2026-08-05)

Ingested verbatim from
`wiki/intake-triage/jon-turn8c-export-ingestion-defect-su-amendment-2026-07-26.md`, content unchanged
below. **The standing-rule amendment quotes Jon directly and is preserved exactly:** *"a standard update
should have occurred with your literal session logs in it based on the zips. If it hasn't that's a
defect."* This is a ruling, stated in the imperative, and is carried as such — not softened to a
suggestion.

**Known non-conformance, flagged not silently fixed:** original file has no `retrieval_key`/`aliases`
block — added at ingest. This ingest does not verify whether the "Immediate action" (ingest the
2026-07-25 export into `raw/`, re-run the recency check) was actually executed at any point in the ten
days between deposit and this ingest — that is an open operational question, not addressed by this wiki
page, and is flagged UNRESOLVED. Note also (from `exchange/RESUME-2026-08-05-su-halted.md`, read before
this ingest) that as of 2026-08-05 `raw/EXPORT-LOG.md`'s last logged watermark is still
`2026-07-27T01:21:39Z` with two later zips on disk and unlogged — i.e. **the corpus-recency defect this
file confirms was still live nine days after this file called for its fix.** That is a finding for the
coordinator's own tracking, not something this ingest resolves.

---

# Turn-8c — export-ingestion defect CONFIRMED; SU definition amended; thinking-capture verified on specimen

## Finding 1 — thinking capture WORKS (wayfinder-verified empirically, 2026-07-26)

Specimen: `raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-21-14536c-claudes-preference-for-clarity.md`. Frontmatter: `extraction_mode: native-json-export`, `thinking_blocks: preserved`, extraction note "3 extended-thinking block(s) preserved as <details>". The blocks contain substantive summary text, not headlines. Conclusion: claude.ai export zips preserve thinking summaries even after the UI change hid them from display. The turn-8b (0a) check NARROWS to: verify one file from the FRESHEST zip (post-UI-change) still carries `thinking_blocks: preserved` with non-empty content. Yes/no, one file, minutes.

## Finding 2 — DEFECT CONFIRMED: export-to-raw ingestion is silently broken

- Newest file in live `raw/transcripts/claude-ai/_routing/incoming/`: dated **2026-07-22**.
- Yet the 2026-07-25 fable-mirror consult (XC session 2b2ff8) used a scratchpad corpus "13 conversations, updated 2026-07-23 → 2026-07-25" — a fresher export EXISTS on the machine and was used ad-hoc without ever crossing into `raw/`.
- Consequence: the wayfinder's own sessions of 07-24/25 (turn-6 assembly, the rulings' native context) are absent from the corpus; the mirror is blind to them; at least two SUs ran without flagging the staleness. "Silently current" is the failure mode — the SU reported state without checking corpus recency.

## Standing-rule amendment (Jon's direction: "a standard update should have occurred with your literal session logs in it based on the zips. If it hasn't that's a defect.")

The Standard Update definition now includes a corpus-recency step: (a) locate the newest export zip on the machine (all known landing paths, including scratchpads); (b) if newer than the newest `raw/` ingest, ingest it (parser + attribution discipline as normal); (c) the SU report states the corpus-current-through date explicitly; (d) if no export newer than N days exists, the SU flags "export requested from Jon" as a named line — never silently reports current. Jon exports the zips manually; the system's job is to never let a zip sit unshipped and never claim freshness it didn't verify.

Immediate action: ingest the 2026-07-25 export (the XC scratchpad copy or the zip it came from) into `raw/`, then re-run the recency check.

## Settings verdict (Jon asked "help me change this setting if needed")

No setting change needed on current evidence: extended thinking is enabled (blocks exist), native JSON export preserves them, cleanupPeriodDays is fixed, accumulate-archive is live. Completeness is procedural (this amendment), not a toggle. If the Finding-1 fresh-zip check FAILS, escalate to Jon immediately — that would mean the export format changed and the [model-reasoning-visible] on-page convention becomes primary, not fallback, for material decisions.

## Formalization ruling context

Jon's framing: read first; if insufficient, formalize thinking-summarization. Wayfinder's read after inspection: sufficient in kind — summaries are captured and substantive. The [model-reasoning-visible] convention (turn-8b) stands as the material-decision overlay: on-page verbatim reasoning for load-bearing decisions, export-layer summaries for the ambient record. Not an emergency program; fold into growth-intent/citation-need drafting where reasoning-display is discussed (turn-8 §5's "reformatting messages to display reasoning maybe").

— relayed by the wayfinder; silence is never approval. — Jon
