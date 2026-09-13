---
title: Session Recovery — Windows Shutdown, Archive Fix, and Standards Update
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 4 vs corpus 3 on authored labels"
source_file: raw/transcripts/claude-code/fl/code-2026-05-08-8989d1-restore-sessions-after-windows-shutdown.md
project: Claude Foundational Layer
date_ingested: 2026-05-09
type: session
tags: fl, session-recovery, convert-claude-code, raw-file-standards, pipeline-fix
source_file_status: unrecoverable (Claude Code intake file deleted after wiki-master processing; stub only)
---

## Summary

Claude Code session (Session Recovery role, 2026-05-08, 28K chars). Recovered two Claude Code sessions (skills-master 740c93, test-master e4c393) interrupted by an unexpected Windows shutdown. Key pipeline fixes: (1) located and extracted both .jsonl files using convert-claude-code.py; (2) fixed a bug in the script that conflated tool result messages with real human turns; (3) fixed frontmatter output to comply with raw-file-standards.md — missing source_type, project, title, source_id key name, and ## Summary scaffold; (4) added jsonl-convert to the extraction_mode taxonomy in raw-file-standards.md; (5) corrected wrong created date (2026-05-04 → 2026-05-07). Wiki-master reviewed both archives, initially rejected then conditionally accepted after corrections; filled in ## Summary sections and improved titles.

## Key Claims

- convert-claude-code.py had a bug conflating tool result messages (which share the "user" role in the API) with real human turns — fixed ([source: code-2026-05-08-8989d1-session-recovery])
- raw-file-standards.md missing fields fixed: source_type, project, title, source_id naming, ## Summary scaffold, jsonl-convert extraction mode definition ([source: code-2026-05-08-8989d1-session-recovery])
- jsonl-convert extraction mode is now documented in the taxonomy: fidelity = high for human turns and assistant text; tool results excluded; thinking unavailable ([source: code-2026-05-08-8989d1-session-recovery])
- Wiki-master role boundary enforced in this session: wiki-master rejected initial deposits that failed standards, then accepted after corrections — process working as designed ([source: code-2026-05-08-8989d1-session-recovery])

## Entities & Concepts

[[extraction-pipeline]], [[raw-file-standards]]

## Conflicts

None.

## Uncaptured Content

a) Verbatim session content not preserved — this was a Claude Code intake file deleted after wiki-master processing. A stub file now exists at `raw/intake/wiki-master-cc-session-recovery-2026-05-08-8989d1.md`. Key Claims are the only surviving record of the session content.
b) N/A — original not available to identify dissolved tensions.
c) N/A — unfollowed threads cannot be identified without the verbatim session.
