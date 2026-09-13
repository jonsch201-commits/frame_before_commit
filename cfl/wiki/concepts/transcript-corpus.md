---
title: Transcript Corpus — Parsed claude.ai Mirror Corpus
trunk: fl
branch: [cfl]
sub_branch: [corpus]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (corpus); sub: corpus 7 vs fleet 2 on authored labels"
type: concept
first_seen: coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477
source_count: 1
last_updated: 2026-08-05
---

## What This Is

The **transcript corpus** is the parsed claude.ai export — one markdown file per conversation,
produced by the `transcript-parser` skill wrapping `convert-export.py`. It is the read surface
behind the [[fable-mirror]] agent: the corpus is what lets a CC-resident subagent answer "what did
the triage layer say" without live claude.ai access.

**Corpus = parsed transcripts + thinking blocks.** Thinking is present in the export where the
export contains it — verified 773 thinking blocks across a 173-conversation export (2026-07-12).
This is not a separate scratchpad file; the ratification (Item 2, as amended by an earlier stub)
folded the thinking-block content into the corpus definition itself. A Drive-scratchpad copy
survives only as a secondary recommendation, not the primary artifact.

## Where It Lives

- **Location:** `raw/transcripts/` — **gitignored, on-Drive.** Organized per Record Architecture v1
  as `{claude-ai,claude-code,external}/{fl,personal,pro,home}/<branch>/[<sub-branch>/]`, plus
  `_routing/{incoming,ambiguous}/` per venue and a shared `_superseded/`. This is the **2026-07-28
  L1 move** — the corpus root moved from `raw/sessions/` to `raw/transcripts/`; `raw/sessions/` is
  now empty except a `POINTER.md` (`.claude/agents/fable-mirror.md:25-26`, corrected 2026-07-30 —
  the correction exists because a corpus root pointing at an emptied directory makes every CORPUS
  SILENT answer uninformative for the wrong reason). This page previously stated no path ruling had
  landed and that `raw/sessions/` was the verified on-disk layout; that was true as of 2026-07-24
  and is now stale. The move is ratified and landed — this is a documentation backfill correcting a
  concept page other agents cite, not a new ruling.
- **Why gitignored:** it is Jon's full history — personal, home, and faith content included — and
  is deliberately never pushed to GitHub. The gitignore rule (`raw/` wholesale) predates the
  mirror pipeline; the corpus lives inside that existing exclusion, not a new one.
- **Who reads it:** the `fable-mirror` agent reads it from local disk, read-only. The claude.ai
  connector itself is served separately, via the `canonical` branch (see [[repo-hygiene]]) — the
  connector does not read the gitignored corpus at all.

## Extraction: manifest-diff, not full re-parse

The nightly pilot lane (Stage-1, tested not yet scheduled per `schtasks`) is two legs: **Leg 1**
(pure Python, zero tokens) diffs the extraction manifest against the last-known state; **Leg 2**
(`claude -p`) runs only when Leg 1 finds a delta. This keeps corpus refresh cheap — no LLM call
runs unless something actually changed in the underlying export.

## Provenance Grades (how corpus claims must be stamped)

Every claim sourced from the corpus carries one of three grades, always with a freshness stamp
("corpus current through export YYYY-MM-DD"):

- **`[TRANSCRIPT:date]`** — grounded in a visible turn. Strongest grade.
- **`[THINKING-SUMMARY:date]`** — grounded in a thinking block. Weaker — **double-discount.** A
  thinking block is a *displayed summary*, not 1:1 with the reasoning tokens that produced it: a
  paraphrase of reasoning, read by another interpreter. Never present it with transcript-level
  confidence.
- **`[MIRROR-INFERENCE]`** — extrapolation beyond what either type actually shows. Must be flagged
  as inference, not corpus content.

## Standing Rules

- **Unified-sources model** *(operating rule; **NOT** a Jon ruling — see the correction below)*:
  all captured conversation is "sources," categorized — the gitignored bulk corpus plus the
  material subset curated into the tracked wiki by wiki-master judgment. There is no hard
  raw/sources firewall; the corpus and the wiki are two grades of the same evidentiary class, not
  separate systems.
  **⚠️ ATTRIBUTION CORRECTED 2026-08-07.** This line read "(Jon ruling, 2026-07-21)". Resurrection
  across 2,206 corpus transcripts, 940 JSONLs and `history.jsonl` returned **zero** Jon-authored
  occurrences of the wording. Its single witness is a **compaction summary** at
  `raw/transcripts/claude-code/fl/code-2026-07-21-8d4396-fable-mirror-pipeline-ratification-and-build-tasks.md:5678`,
  which the transcript itself marks *"the machine's own summary … NOT a message from Jon."* Jon's
  real 2026-07-21 words on the topic, same file line 102: *"Landing: propose
  sources/claude-ai-transcripts/ to wiki-master; one canonical location; corpus read-only to
  everything except the parser; on conflict, wiki wins."* **The rule stays; the ratification claim
  goes.**
- **Lossy; wiki wins.** Exports can miss replies and drop deleted conversations or project
  structure. The corpus is **never authoritative over the wiki** — on any conflict between the two,
  the wiki's account governs.
- **Read-only to every agent except the parser.** No agent other than `transcript-parser` writes
  into the corpus directory.

## Related

[[fable-mirror]], [[repo-hygiene]], [[bgisolation-membrane]], [[coordinator]], [[extraction-pipeline]]
