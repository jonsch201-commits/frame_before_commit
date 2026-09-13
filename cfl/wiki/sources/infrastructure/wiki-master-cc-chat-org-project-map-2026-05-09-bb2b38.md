---
title: Wiki Master — Chat Organization, Project Map, and CDP Extraction Gap
trunk: fl
branch: [cfl]
sub_branch: [corpus]
branch_reason: "R-SRC-INFRA; sub: corpus 8 vs wiki 6 on authored labels"
source_file: raw/transcripts/claude-code/fl/code-2026-05-09-bb2b38-review-chat-organization-and-project-categorization.md
source_file_status: markdown-export (claude-code-session; turn numbers = message sequence)
project: Claude Foundational Layer
date_ingested: 2026-06-08
type: session
tags: fl, wiki-master, chat-org, cdp, project-map, data-extraction, raw-structure
---

## Summary

Wiki-master session (231K chars) focusing on organizing the 2026-05-09 full Anthropic export. Key finding: the Anthropic data export format does not include `project_uuid` — the export is flat. The Data Master had already solved this via CDP: `raw/exports/project-map.json` contains 105 conversations with real project_uuid values pulled from the live claude.ai API. Session also diagnosed that the raw/sessions/ folder structure (fl/, personal/, pro/) IS the project categorization. Jon's key correction: "check raw/ before writing code."

## Key Claims

- Anthropic export (conversations.json) strips project_uuid for all conversations — export format is flat. CDP is the only bridge to project assignment. ([wiki-master-cc-chat-org-project-map-2026-05-09-bb2b38:T7])
- raw/sessions/ folder structure (fl/, personal/, pro/) was the Data Master's categorization artifact — it already existed before this session's Python script was written. ([wiki-master-cc-chat-org-project-map-2026-05-09-bb2b38:T8])
- project-map.json: 105 conversations, 91 with project_uuid, 14 null (no project). 116 export vs. 105 map = 11 gap (deleted/expired since export date). ([wiki-master-cc-chat-org-project-map-2026-05-09-bb2b38:T9])
- 5 conversations in project-map but NOT in export (b60686b6, 44fbe52b, 5e02da3b, b04c8b74, 1fe1190b) — newer sessions or export gaps. ([wiki-master-cc-chat-org-project-map-2026-05-09-bb2b38:T10])
- Jon's operational principle: "raw/ before writing code" — check existing structure before building analysis scripts. ([wiki-master-cc-chat-org-project-map-2026-05-09-bb2b38:T8])
- Claude Code sessions (740c93, e4c393, 8989d1) were absent from the export — correct, they originate from Claude Code JSONL not claude.ai. ([wiki-master-cc-chat-org-project-map-2026-05-09-bb2b38:T6])

## Entities & Concepts

[[extraction-pipeline]], [PERSONAL: jon]

## Conflicts

None.
