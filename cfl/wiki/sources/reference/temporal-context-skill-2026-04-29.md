---
title: Temporal Context Skill Document
trunk: fl
branch: [reference]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-REF; sub: branch `reference` has no registered sub-branches"
source_file: none  # skill file moved to skills/ directory
project: Claude Foundational Layer
date_ingested: 2026-05-12
type: note
tags: temporal-context, skills, timestamps, session-state
source_file_status: static-reference (raw/references/ document; not a session)
---

## Summary

The Temporal Context Skill document as stored in the CFL project (created 2026-04-29). Defines timestamp format [YYYY-MM-DD HH:MM CDT], source priority (user-provided > web search for date only > estimated), clock behavior within sessions, state inference by time window, and staleness flagging. Always CDT regardless of DST. The timestamp informs how Claude interprets everything that follows — Jon's state, decision staleness, context age.

## Key Claims

- **CDT always:** Jon is Central US time. Use CDT as the stable label regardless of season (CDT = UTC-5, CST = UTC-6). DST applies March second Sunday through November first Sunday.
- **Source priority:** User-provided is most accurate and takes precedence. Web search is reliable for date only, never for exact time. Estimated = dead reckoning from last known anchor, marked explicitly with "(ESTIMATED — check reasonability)".
- **Flag ESTIMATED once, then suppress:** Flag at session open if no time provided. Suppress on subsequent messages unless estimate has drifted >30 min without a new anchor.
- **Time window state inference:** 06:00–08:00 = compact, flag desk-time items; 08:00–17:00 = depends on [work] tag; 17:00–20:00 = triage mode, shorter; 20:00–23:30 = ideas-mode, flag scope creep; 00:30–06:00 = park aggressively. These are patterns, not rules — Jon overrides explicitly.
- **[work] tag at session open:** Jon is at his job. Tighter scope, shorter responses, no rabbit holes, no bleed into work context.
- **Claude Code environment:** Use `date` shell command — no estimation needed. claude.ai chat: no live clock, user-provided time is only reliable source.

## Entities & Concepts

[[skills-system]]

## Conflicts

None. Source document for the temporal-context skill.