---
title: Wiki Master Ingest Planning — First Ingest Schedule and Routing Strategy
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 8 vs skills 0 on authored labels"
source_file: raw/transcripts/claude-code/fl/code-2026-05-09-949f16-plan-first-wiki-ingest-schedule.md
project: Claude Foundational Layer
date_ingested: 2026-05-11
type: session
tags: wiki, ingest, planning, routing, personal, pro
source_file_status: OK
---

## Summary

Jon consulted wiki-master on the first ingest schedule for 116 exported conversations. Session covered routing strategy (FL vs. personal vs. pro wiki), deduplication policy for overlapping session formats, and priority ordering. Established the ingest methodology — screening criteria, routing rules, threshold for personal/pro wiki source pages — that was executed in subsequent sessions over 2026-05-09 through 2026-05-11.

## Key Claims

- **Routing by project assignment:** FL sessions → wiki/sources/; Personal Life Questions → wiki/personal/sources/; Professional Life Questions → wiki/pro/sources/; project assignment from claude.ai is the primary routing signal; unassigned conversations require manual screening ([wiki-master-ingest-planning-2026-05-09-949f16:T16])
- **Scope of full corpus:** 116 conversations in conversations.json — approximately 37 personal, 9 pro, 17 FL, 28 "How to use Claude", 30 unassigned; FL is priority ingest tier followed by personal/pro screening ([wiki-master-ingest-planning-2026-05-09-949f16:T10])
- **Deduplication policy:** same session appearing in multiple formats (DOM extract + Anthropic export) ingested once; verbatim Anthropic export preferred over DOM extract where both exist; source page notes the dedup decision ([wiki-master-ingest-planning-2026-05-09-949f16:T10])
- **Personal wiki ingest threshold:** higher bar than FL — session merits a source page if it contains a named research idea, design decision, or FL concept invocation; operational chats (logistics, home tech, medical) skipped; threshold produces ~5 ingested from 35 personal sessions screened ([wiki-master-ingest-planning-2026-05-09-949f16:T94])
- **Unassigned 30:** 30 conversations not assigned to any claude.ai project; several are clearly personal life content (car title, ballot guidance, island destinations); require manual screening before routing — not automatically personal ([wiki-master-ingest-planning-2026-05-09-949f16:T16])
- **Missing export gap:** 2 personal conversations in project map but with no export file (44fbe5, 5e02da); 3 FL conversations also missing from export (b60686, b04c8b, 1fe119 = T-003); a fresh Anthropic export is the resolution path (synthesized from session context — specific UUIDs not in raw file text)

## Entities & Concepts

[[extraction-pipeline]]

## Conflicts

None.

## Uncaptured Content

a) Full session (132 turns, ~2000 lines) contains extensive FL session routing detail and Surface_then_commit wiki restructure discussion — not captured in Key Claims as out of scope for core ingest methodology claims.
b) Jon's project assignment for philosophical sessions (89c6d7, 570573, etc.) was debated before being resolved as "Personal wiki" — dissolved tension not surfaced in Key Claims.
c) The 5 larger FL sessions (Skills Master 243K, Meta-PM 197K, etc.) were discussed as a separate ingest session — that thread continues in subsequent sessions; not followed here.
