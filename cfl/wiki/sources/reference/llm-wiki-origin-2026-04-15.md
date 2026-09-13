---
title: LLM Wiki — Original Concept Document
trunk: fl
branch: [reference]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-REF; sub: branch `reference` has no registered sub-branches"
source_file: raw/references/llm-wiki.md
project: Claude Foundational Layer
date_ingested: 2026-05-12
type: note
tags: wiki-master, llm-wiki, architecture, origin-document
source_file_status: static-reference (raw/references/ document; not a session)
---

## Summary

Jon's original write-up of the LLM wiki pattern, stored in the CFL project (created 2026-04-15). This is the origin document for the wiki-master skill and the claude-foundational-layer wiki itself. Defines the three-layer architecture (raw sources / wiki / schema), three core operations (ingest / query / lint), and explicitly contrasts the approach against RAG — where LLMs rediscover knowledge from scratch on every query vs. a compounding persistent wiki. Draws analogy to Vannevar Bush's Memex (1945).

## Key Claims

- **Compounding vs. RAG distinction:** RAG rediscovers knowledge from scratch on every query. The LLM wiki compiles knowledge once and keeps it current — the wiki is a persistent, compounding artifact. Cross-references already there, contradictions already flagged, synthesis already reflects everything read.
- **Three-layer architecture:** (1) Raw sources — immutable, LLM reads but never modifies; (2) Wiki — LLM-generated, LLM owns entirely; (3) Schema (CLAUDE.md / AGENTS.md) — governs LLM behavior as wiki maintainer. Schema is what makes LLM a disciplined maintainer rather than a generic chatbot.
- **Why maintenance works:** LLMs don't get bored, don't forget cross-references, can touch 15 files in one pass. Humans abandon wikis because maintenance burden grows faster than value. LLMs remove this barrier.
- **Memex analogy (Vannevar Bush, 1945):** Bush's vision of a personal, curated knowledge store with associative trails between documents. What the web became diverged from this. The part Bush couldn't solve was who does the maintenance — LLMs solve that.
- **Operations as wiki-master design:** Ingest (source → wiki pages, 10–15 files touched), Query (index first, then drill, file good answers back as pages), Lint (contradictions, orphans, missing cross-refs, stale claims). These operations map directly to wiki-master skill operations.
- **index.md + log.md roles:** index.md is content-oriented catalog (read first on queries); log.md is chronological append-only record. Distinction preserved in current wiki-master implementation.

## Entities & Concepts

[[wiki-master-origin]]

## Conflicts

None. First source to document the Memex analogy and the original three-layer framing.