---
title: Claude Data Privacy, Conversation Training Use, and Topic Constraints
trunk: fl
branch: [cfl]
sub_branch: [corpus]
branch_reason: "R-SRC-INFRA; sub: corpus 2 vs wiki 0 on authored labels"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-11-1d3d2e-topics-to-avoid-discussing.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-20
type: session
tags: how-to-use-claude, infrastructure, privacy, data, claude-constraints
---

## Summary

Session (3.2K chars, 2026-03-11) covering two topics: Claude's constraints on what it won't engage with (narrow: mass-harm content, CSAM, actual malware), and the more practically material data privacy considerations for regular use. Jon's early session establishing what can and can't be shared with Claude. Reference value for data handling decisions in CFL sessions.

## Key Claims

- **Hard refusals are narrow**: Claude won't produce content enabling mass harm, CSAM, or actual malware. All other topics are engageable — the more useful frame is "what to be skeptical of in Claude's outputs," not "what to avoid discussing." ([claude-data-privacy-2026-03-11-1d3d2e:T2])
- **Conversation data may train future models**: By default on claude.ai, conversations can be used for model training unless opted out in Settings → Privacy. ([claude-data-privacy-2026-03-11-1d3d2e:T4])
- **Categories worth caution in sharing**: Personal health info, other people's data without consent, proprietary/trade secret business info, financial account details, combinations of details that profile third parties. ([claude-data-privacy-2026-03-11-1d3d2e:T4])
- **Claude is more dangerous confidently wrong than it is engaging with difficult topics** — framing pushback from session. ([claude-data-privacy-2026-03-11-1d3d2e:T2])
- **Stateless design is also a security property**: Nothing persists server-side between turns, reducing tampering risk. ([claude-data-privacy-2026-03-11-1d3d2e:T4])

## Entities & Concepts

None new.

## Conflicts

None.