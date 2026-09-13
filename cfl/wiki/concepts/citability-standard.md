---
title: Citability Standard
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (wiki); sub: wiki 4 vs corpus 1 on authored labels"
type: concept
first_seen: wiki-multi-master-audit-2026-06-02-dba2c0b
source_count: 3
last_updated: 2026-06-03
---

## What This Is

The citability standard defines how Key Claims on wiki source pages are anchored to specific turns in raw source files. Format: `[slug:T{n}]` for turn-level citations, `[slug:T{n}.P{p}]` for paragraph-level citations. The standard was designed in the multi-master wiki improvement session (dba2c0b) as R6 of the R1–R6 improvement framework, then formally specified and maintained by skills-master.

The reference specification lives at `skills/wiki-master/references/citability-standard.md`. This concept page is the queryable wiki synthesis — it captures key findings, edge cases, and open gaps as discovered through the Phase 3 annotation run, without duplicating the full specification.

## What the Wiki Says

### Core Format

Turn-level: `[slug:T{n}]` — `slug` is the source page slug (not the raw file slug if they differ); `T{n}` is the 1-indexed turn number counted from T1 at the top of the file.

Paragraph-level: `[slug:T{n}.P{p}]` — adds paragraph number within the turn (1-indexed, paragraphs delimited by `\n\n`). Use when a turn contains 3+ separable, independently citable claims.

([wiki-multi-master-audit-2026-06-02-dba2c0b:T93])

### Source Format Detection

The standard applies differently depending on source format. The Phase 3 subagent confirmed that all FL raw sources are markdown exports, not JSONL — the markdown-export path is primary.

| Signal | Format | Turn counting |
|--------|--------|---------------|
| `## Human` / `## Assistant` headers | Markdown export (claude.ai) | Count `## Human` / `## Assistant` in sequence from T1 |
| `**Jon**` / `**Claude**` bold-name headers | Claude Code session MD | Count bold-name markers in sequence from T1 |
| Raw `.jsonl` (one JSON object per line) | JSONL subagent log | Line number (1-indexed) |
| File in `raw/references/` or has `source_file_status: static-reference` | Static reference | No `T{n}` anchors — omit entirely |

([wiki-master-phase3-subagent-log-2026-06-01-ad8e70:T1])

### Markdown-Export Path Is Primary

The Phase 3 agent discovered that all FL raw sources produced by `convert-export.py` or `convert-claude-code.py` are markdown exports. JSONL is the secondary format — used only for raw subagent logs cited directly. Skills-master patched the standard to make this explicit after Phase 3 raised it. The previous framing implied JSONL was primary. ([wiki-multi-master-audit-2026-06-02-dba2c0b:T150])

### Bold-Header Format Now Citable

The seven FL source pages with `**Jon**`/`**Claude**` bold-name headers (Claude Code session MD format) were initially marked `non-standard-format` and exempted from citability. In the Phase 3e session, the exemption was removed — bold-header format uses the same message-sequence turn counting as claude.ai exports. The `non-standard-format` status was replaced with `OK` across all seven pages. ([wiki-multi-master-audit-2026-06-02-dba2c0b:T200])

### Slug Mismatch Rule

When a source page's slug differs from its raw file's filename (shortened at ingest time), citations must use the SOURCE PAGE slug, not the raw file slug. These differ in a nontrivial fraction of the corpus. The Phase 3 agent applied this consistently: e.g., `skills-master-wiki-pipeline-2026-05-01-bcafba` not a shorter raw file name. ([wiki-master-phase3-subagent-log-2026-06-01-ad8e70:T1])

### source_file_status Frontmatter Field

The Phase 3 agent invented and consistently applied a `source_file_status` frontmatter field to all processed pages. As of Phase 3 completion, the field is present on ~45 source pages. Skills-master has been flagged to formalize the field in the citability standard and SCHEMA.md. ([wiki-master-phase3-subagent-log-2026-06-01-ad8e70:T1])

### Phase 3 Completion State

R6 annotation reached approximately 70% completion (45 of 78 FL source pages). 17 session-type pages remain unannotated as of Phase 3 session termination. The full list of remaining pages is in `wiki-master-phase3-subagent-log-2026-06-01-ad8e70.md`. ([wiki-master-phase3-subagent-log-2026-06-01-ad8e70:T1])

### Open Gap: Synthesis Claims

The standard is currently silent on how to cite wiki-master synthesis claims — inferences not verbatim in the source. The Phase 3 agent identified one such claim in `claude-data-privacy-1d3d2e` ("Stateless design is also a security property") and cited the nearest supporting turn with a flag. No resolution has been specified. The edge case remains open. ([wiki-master-phase3-subagent-log-2026-06-01-ad8e70:T1])

### Rationale

Character offsets are brittle across re-exports, encoding differences, and whitespace normalization. Message-sequence counting using `## Human`/`## Assistant` or `**Jon**`/`**Claude**` delimiters produces stable turn numbers because conversations are append-only — existing T{n} values never shift when new turns are added. Paragraph-level subdivision adds granularity without character-offset fragility.

### Connection to R1–R6 Framework

The citability standard is R6 of the six-improvement framework designed in dba2c0b. It is downstream of R5 (sources table categorization) and was formalized by skills-master before wiki-master implemented it. The multi-master coordination pattern (skills-master schema before wiki-master implementation) was explicitly noted as the correct sequencing. ([wiki-multi-master-audit-2026-06-02-dba2c0b:T93])

## Conflicts

Framing resolved 2026-06-04: [[extraction-pipeline]]'s JSONL-primary framing refers to pipeline input (`convert-export.py` reads JSONL); this page's markdown-primary framing refers to pipeline output and citation format. Both are correct. No contradiction.

## Related

[[extraction-pipeline]], [[wiki-ingest-methodology]], [[multi-agent-orchestration]]
