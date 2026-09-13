---
title: Discord Export for Stylomantic — Data Pipeline and Subagent Pattern
trunk: fl
branch: [stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-STYLO; sub: branch `stylomantic` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-03-22-57c322-exporting-discord-chat-history.md
source_file_status: unrecoverable (raw session not preserved at ingest; stub only)
project: non-project
date_ingested: 2026-05-12
type: session
tags: stylomantic, discord, data-pipeline, subagent-pattern, extraction-pipeline
---

## Summary

Jon's session planning how to export Discord chat history for Stylomantic's tone modeling use case. Covers Discord's export options (official data request vs. DiscordChatExporter), Claude Code for file wrangling, and a subagent map-reduce pattern for processing large corpora without exceeding context limits. Establishes that Discord history is the primary intended data source for Stylomantic, and that the subagent coordinator pattern is the appropriate architecture for processing it.

## Key Claims

- **Discord as Stylomantic data source:** Jon explicitly wants Discord chat history "to better have you understand my tone" — directly naming the Stylomantic use case. Discord is the primary intended training corpus for the personalization layer.
- **DiscordChatExporter (Tyrrrz/DiscordChatExporter):** Recommended third-party tool for targeted channel/server exports to HTML, JSON, or CSV. More practical than Discord's full data request (which takes up to 30 days and produces unwieldy JSON).
- **Context window constraint documented:** Full Discord history for an active user could be millions of words; Claude can hold ~200K tokens. Full dump is not processable — curated excerpts or subagent processing required.
- **Subagent map-reduce pattern:** Jon proposes, Claude confirms: (1) coordinator instance handles overall task, (2) subagents process individual export files/chunks and return only summaries or representative samples, (3) coordinator synthesizes. This is the legitimate use case for the subagent pattern on large corpora.
- **Claude Code preferred over Cowork:** For file wrangling JSON exports, Claude Code is better suited (CLI tool designed for this). Cowork oriented toward non-developer automation.
- **Practical data pipeline for tone capture:** 20–50 representative message samples across different contexts (casual, serious, heated, joking) synthesized into a tone profile — more useful than attempting to process everything.

## Entities & Concepts

[[stylomantic]]

## Conflicts

None.

## Uncaptured Content

a) Raw session not preserved at ingest (2026-05-12) — verbatim text is not available; only this source page's Key Claims survive. Stub file created at source_file path to make the link non-broken.
b) No tensions to report — single ingestion event with no contradicting sources.
c) Full session content is the unfollowed thread. Re-extraction from Anthropic zip (if available) could recover verbatim text. Consistent with Stylomantic concept page (Discord history as primary data source). Subagent map-reduce pattern consistent with extraction-pipeline concept.