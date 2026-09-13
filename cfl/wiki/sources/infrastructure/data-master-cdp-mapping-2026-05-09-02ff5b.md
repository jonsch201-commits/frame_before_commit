---
title: Data Master CDP Mapping — Project Map and Export Format Discovery
trunk: fl
branch: [cfl]
sub_branch: [corpus]
branch_reason: "R-SRC-INFRA; sub: corpus 5 vs wiki 0 on authored labels"
source_file: raw/transcripts/claude-code/fl/code-2026-05-09-02ff5b-export-claude-ai-chat-conversations-to-wiki.md
source_file_status: unrecoverable (Claude Code intake file deleted after wiki-master processing; stub only)
project: Claude Foundational Layer
date_ingested: 2026-05-11
type: session
tags: data-master, cdp, project-map, extraction-pipeline, anthropic-export
---

## Summary

Data Master execution session. Jon provided a task packet prepared by the claude.ai Data Master directing a Chrome DevTools Protocol (CDP) scrape of the live claude.ai API to map all 116 conversations to their projects. Key outcomes: 105/116 conversations mapped with project_uuid confirmed present in the API; project-map.json written; critical discovery that Anthropic's data export conversations.json does NOT include project_uuid (design limitation). This session established the authoritative project mapping for the personal/pro wiki routing.

## Key Claims

- **project_uuid IS in the claude.ai API:** The CDP fetch confirmed that the live claude.ai conversation API response includes project_uuid for each conversation — the Anthropic data export omission is a deliberate design choice or oversight, not a fundamental impossibility
- **Anthropic export missing project_uuid:** conversations.json (the Anthropic data export format) does not link conversations to projects; projects are exported separately with their docs, but the join key is missing from the conversation records — this is why CDP was required for project mapping
- **105/116 conversations mapped:** 11 conversations could not be mapped (project_uuid not returned in API response for those records); root cause not fully diagnosed — may be deleted conversations or API pagination gaps
- **Project map written:** raw/exports/2026-05-09-full/project-map.json — the authoritative routing file for the ingest pipeline
- **CDP as extraction path:** Chrome DevTools Protocol (browser session + CDP) gives access to the live claude.ai API that is not available via the standard UI or export mechanisms; this is a distinct third extraction path alongside Anthropic export and DOM extraction
- **Data master execution model:** Execution role operates from a pre-scoped task packet; does not design, does not improvise, reports unexpected results and stops — this design constraint prevents scope creep during execution

## Entities & Concepts

[[extraction-pipeline]]

## Conflicts

None. CDP extraction path is new; adds to existing extraction-pipeline documentation.

## Uncaptured Content

a) Verbatim session content not preserved — this was a Claude Code intake file deleted after wiki-master processing. A stub file now exists at `raw/intake/code-2026-05-09-02ff5b-data-master-execution-packet.md`. Key Claims are the only surviving record of the session content.
b) N/A — original not available to identify dissolved tensions.
c) N/A — unfollowed threads cannot be identified without the verbatim session.
