---
title: Extraction Pipeline
trunk: fl
branch: [cfl]
sub_branch: [corpus]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (corpus); sub: corpus 6 vs wiki 1 on authored labels"
type: concept
first_seen: skills-master-cc-wiki-infrastructure-2026-05-04-740c93
source_count: 10
last_updated: 2026-06-08
---

## What This Is

The system for converting Claude conversations into structured raw/ files suitable for wiki ingest. Established in the Skills Master session (2026-05-04). Two extraction paths exist: one for claude.ai sessions (Anthropic JSON export), one for Claude Code sessions (.jsonl files). The architectural reason this pipeline exists is Claude's stateless design — see [[claude-architecture]]. The [[wiki-master-origin]] concept covers the broader LLM wiki pattern this pipeline feeds.

## What the Wiki Says

### Primary Path — Anthropic JSON Export

Tool: `skills/chat-exporter/scripts/convert-export.py`

Source: `intake/Anthropic download YYYYMMDD/conversations.json`

Fidelity: Highest — verbatim turns. Known limitation: thinking blocks currently skipped silently. All output must be flagged `thinking_blocks: omitted` and `extraction_completeness: FULL — thinking omitted`.

Run modes: `--inspect`, `--dry-run`, `--run`. Use `--ids` to select specific conversations. Use `--out` to route to correct project raw/ directory.

**Pipeline format note:** The input to this path is JSONL (the Anthropic data export format, `conversations.json`). The output is markdown files in `raw/transcripts/` (moved from `raw/sessions/` in the 2026-07-28 L1 move — see `.claude/agents/fable-mirror.md:25-26`). The markdown output is the citation-facing format used by the wiki — JSONL is not directly cited. See [[citability-standard]] for the citation format specification.

### Secondary Path — Claude Code .jsonl

Tool: `skills/chat-exporter/scripts/convert-claude-code.py`

Source: `C:\Users\JonSc\.claude\projects\<project-slug>\<session-uuid>.jsonl`

Fidelity: High for human turns and assistant text; tool results excluded (share "user" role in API, excluded after bug fix in session-recovery 2026-05-08); thinking unavailable in .jsonl format.

Set `extraction_mode: jsonl-convert`, `thinking_blocks: omitted`, `extraction_completeness: FULL — thinking omitted`. The ## Summary scaffold is generated automatically — must be filled in before submitting for ingest.

### Tertiary Path — Chrome DevTools Protocol (CDP)

Tool: Chrome DevTools Protocol browser session (manual; no script in repository)

Source: Live claude.ai API intercepted via CDP

Purpose: **Project mapping only** — linking conversation UUIDs to claude.ai project assignments. This is the only path that retrieves project_uuid, which Anthropic's data export omits entirely.

**CDP for chat extraction is demoted to fallback.** The session cookie + direct API request approach is the chosen primary for any non-export-file extraction. CDP flaw for auth: fresh `--user-data-dir` has no auth cookies; requires real Chrome profile path (`C:\Users\[username]\AppData\Local\Google\Chrome\User Data`). Session cookie walk-through: F12 → DevTools → Application → Cookies → claude.ai → `sessionKey` or `__Secure-next-auth.session-token`. ([data-master-pipeline-extraction-2026-05-01-f23519])

Key findings from 2026-05-09 CDP fetch: 105/116 conversations mapped; project_uuid confirmed present in the live API response; result written to raw/exports/2026-05-09-full/project-map.json. 11 conversations unmappable (API response gap, cause undiagnosed). ([data-master-cdp-mapping-2026-05-09-02ff5b])

**Critical export format gap:** conversations.json (the Anthropic data export format) does NOT include project_uuid for any conversation. Projects are exported separately with their documents, but the join key is missing from the conversation records. CDP is required for any project-routing task. ([data-master-cdp-mapping-2026-05-09-02ff5b], [wiki-master-cc-fl-wiki-completion-2026-05-09])

### Legacy Path (Deprecated)

DOM-based browser extraction (Claude in Chrome extension). Subject to virtual DOM truncation constraint — long sessions are PARTIAL. Fallback only for sessions not in Anthropic data export.

**Virtual DOM truncation documented in data-master-pipeline-extraction-2026-05-01-f23519:** Claude.ai uses virtualized rendering — only mounts messages near the viewport (~last 4KB visible). Long sessions appear complete in browser but only recent messages are in the DOM. Scrolling to top doesn't trigger React to re-render early messages within tool call limits. This is why `raw/sessions/archive_attempt_incomplete/` files are partial. ([data-master-pipeline-extraction-2026-05-01-f23519])

### Standards Governance

`raw/references/raw-file-standards.md` — authoritative deposit standards document. Created by wiki-governance agent (2026-05-07). Governs frontmatter requirements, format contract, directory placement, and what breaks when standards are violated. ([skills-master-cc-wiki-infrastructure-2026-05-04-740c93])

### EXPORT-LOG.md Watermark

The canonical watermark file is `raw/EXPORT-LOG.md`. It stores the last export timestamp as a parseable final line. `MANIFEST.md` is the predecessor (as of 2026-04-19 watermark) — renamed to EXPORT-LOG.md in the chat-exporter skill 2026-04-30. The chat-exporter skill (chat-exporter/SKILL.md) is designed for incremental session-close use; completeness tags: FULL / PARTIAL / TAIL-ONLY. ([data-master-pipeline-extraction-2026-05-01-f23519])

### .env Location

`C:\Users\JonSc\.claude\.env` — centralized env file, not in repo root. ([data-master-pipeline-extraction-2026-05-01-f23519])

### 30-Day Export Window Caveat

The Anthropic data export is a rolling 30-day window, not a complete history. Conversations older than 30 days at download time may not be covered. Implication: T-003 (or other early sessions) may not appear in a new export if downloaded months after those sessions occurred. Systemic check before any routing decision: verify session date vs. export download date. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e])

### Provenance and KV-Hash Integrity

Source zip files must be traceable to wiki claims before any folder restructuring. The canonical provenance concern: if a zip is renamed or moved, the link between a wiki citation and the underlying raw source can silently break. Design requirement: restructuring operations must verify KV-hash of source zips before and after. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e])

### "Check raw/ Before Writing Code" Principle

Operational rule established 2026-05-09: check the existing raw/ structure before writing analysis scripts. The folder structure (raw/transcripts/claude-ai/fl/, raw/transcripts/claude-ai/personal/, raw/transcripts/claude-ai/pro/) is itself the project categorization artifact — Data Master had already implemented project routing through folder placement before any Python script was needed. ([wiki-master-cc-chat-org-project-map-2026-05-09-bb2b38])

### Known History

- Legacy raw/sessions/ files (pre-2026-05-04) are reconstructed summaries averaging 4-12 KB; real conversations are 100K–300K chars — 10-50x discrepancy ([skills-master-cc-wiki-infrastructure-2026-05-04-740c93])
- convert-claude-code.py bug fixed 2026-05-08: was conflating tool result messages (user role) with real human turns ([wiki-master-cc-session-recovery-2026-05-08-8989d1])
- jsonl-convert added to extraction_mode taxonomy in raw-file-standards.md 2026-05-08 ([wiki-master-cc-session-recovery-2026-05-08-8989d1])
- Ongoing conversations continue after extraction — no prior staleness flag mechanism. Discovered 2026-05-16 when babab4 showed 88 messages in latest export vs 84 stored. Systemic check recommended: compare stored char_count against latest export before ingest decisions.

## Conflicts

Framing resolved 2026-06-04: this page's "Primary Path — Anthropic JSON Export" describes JSONL as the pipeline input format. [[citability-standard]]'s "markdown-primary" framing describes the pipeline output/citation format. Both are correct in their respective frames — JSONL is what `convert-export.py` reads; markdown is what it produces and what the wiki cites.

## Related

[[raw-file-standards]], [[frame-before-commit]]
