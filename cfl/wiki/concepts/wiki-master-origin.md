---
title: Wiki-Master Origin — LLM Wiki Concept
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (wiki); sub: wiki 9 vs skills 0 on authored labels"
type: concept
first_seen: llm-wiki-origin-2026-04-15
source_count: 2
last_updated: 2026-05-13
---

## What This Is

The conceptual origin of the wiki-master skill (see [[skills-system]]) and the claude-foundational-layer wiki. Jon's original LLM wiki pattern document (2026-04-15) defined the three-layer architecture, three core operations, and the compounding vs. RAG distinction that became the wiki's design foundation. The Vannevar Bush Memex analogy is also introduced here. The [[extraction-pipeline]] is the operational mechanism that feeds raw content into this pattern.

## What the Wiki Says

### Compounding vs. RAG

RAG (Retrieval-Augmented Generation) rediscovers knowledge from scratch on every query — the LLM retrieves relevant chunks at query time and generates an answer. Nothing accumulates. The LLM wiki pattern differs: the LLM incrementally builds and maintains a persistent wiki that sits between the user and raw sources. Knowledge is compiled once and kept current. The wiki is a persistent, compounding artifact — cross-references already there, contradictions already flagged, synthesis already reflects everything read. ([llm-wiki-origin-2026-04-15])

### Three-Layer Architecture

1. **Raw sources** — immutable source documents. LLM reads but never modifies. Source of truth.
2. **Wiki** — LLM-generated markdown files. Summaries, entity pages, concept pages, overview, synthesis. LLM owns this layer entirely.
3. **Schema** (CLAUDE.md / AGENTS.md) — governs LLM behavior as wiki maintainer. This is what makes the LLM a disciplined wiki maintainer rather than a generic chatbot.

([llm-wiki-origin-2026-04-15])

### Three Core Operations

- **Ingest:** Source → wiki pages. LLM reads source, writes summary page, updates index, updates relevant concept/entity pages, appends to log. A single source might touch 10–15 wiki pages.
- **Query:** Index first, then drill into relevant pages, synthesize with citations. Good answers filed back into wiki as pages — explorations compound.
- **Lint:** Health-check — contradictions, orphan pages, stale claims, missing cross-references.

([llm-wiki-origin-2026-04-15])

### Why LLM Maintenance Works

Humans abandon wikis because maintenance burden grows faster than value. LLMs don't get bored, don't forget cross-references, can touch 15 files in one pass. The cost of maintenance is near zero, so the wiki stays maintained. ([llm-wiki-origin-2026-04-15])

### Memex Analogy

Vannevar Bush's Memex (1945) — a personal, curated knowledge store with associative trails between documents — was closer to this pattern than what the web became: private, actively curated, with connections between documents as valuable as the documents themselves. The unsolved problem was who does the maintenance. LLMs resolve that. ([llm-wiki-origin-2026-04-15])

### T-24 — Diff-as-Ingest (from wiki-master-cc-t24-diff-ingest-2026-05-09-b60686)

**Gap identified:** `pipeline.py` ingests full files only; no diff capture. When a raw source updates after initial ingest, wiki pages citing it become silently stale. A validity failure, not a logging gap.

**op_update design:**
- Receive diff, not full file — re-reading the full file risks overwriting valid synthesis with a redundant re-read
- Identify affected pages by citation slug: `grep -r "source-slug" wiki/` across all wiki pages
- Log event explicitly per diff, with changed summary, affected pages list, and status
- Mark affected pages: `⚠️ STALE-CHECK: source [slug] updated [date]. Review citations.` — flag persists until wiki master explicitly clears it
- Auto-rewrite of affected pages rejected: flag and log, assess before acting

**op_update vs op_ingest branching:** pipeline.py detects whether file has prior ingest record. New file → op_ingest. Changed file → op_update. GitHub Action needs no changes.

**Multiple diffs before review:** Accumulate per-event log entries; staleness flag notes most recent update date. Change history reconstructable from log.

([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686])

### Judgment Project (from wiki-master-cc-t24-diff-ingest-2026-05-09-b60686)

A proposed project within a "wiki improvement" category. Goal: surface when model intuition is likely wrong, when misalignment is probable, when the answer is certain vs. uncertain.

Three candidate input domains: (1) documented confident failures (known-failures.md), (2) domain reliability flags for domains where training is known to be unreliable (domain-reliability.md), (3) real-time uncertainty self-reporting protocol. Design questions left open for Jon: granularity, who triggers known-failures writes, whether judgment gets its own lint pass.

([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686])

## Conflicts

None.

## Related

[[extraction-pipeline]], [[skills-system]]
