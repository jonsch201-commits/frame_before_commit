---
title: Claude Conversation Mechanics — Branching, Statelessness, Persistent Context
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: sub-branch too close to call: wiki 3 vs corpus 3 (margin < 1)"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-06-c310bf-reverting-to-previous-conversation-states.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-20
type: session
tags: how-to-use-claude, infrastructure, conversation-mechanics, context, branching
---

## Summary

Session (14K chars, 2026-03-06) covering how claude.ai conversations branch, the implications of statelessness for persistent context, and early setup of CLAUDE.md / custom instructions. Jon's first exploration of how to carry context across sessions. Establishes the architectural baseline against which persistent context strategies (memory, Projects, CLAUDE.md) are designed. Relevant to understanding why the FL infrastructure exists.

## Key Claims

- **Editing branches from any point**: Claude.ai allows editing any prior message, branching the conversation from that point. Everything after the edit is discarded in the new branch; the original thread remains navigable. ([claude-conversation-mechanics-2026-03-06-c310bf:T2])
- **Claude does not retain prior conversations**: Each conversation is isolated unless memory is explicitly enabled or context is injected. CLAUDE.md in Claude Code is separate from claude.ai's persistent features. ([claude-conversation-mechanics-2026-03-06-c310bf:T4])
- **Persistent context mechanisms in claude.ai**: (1) Memories — lossy summaries across sessions, no guarantee of which are surfaced. (2) Custom instructions / User preferences — pasted into every session. (3) Projects — documents attached persist across conversations scoped to that project. ([claude-conversation-mechanics-2026-03-06-c310bf:T8])
- **Individual user interaction style does not directly shape future models**: Training is aggregated and abstracted. Jon's interactions may contribute to better general patterns for skilled users, not a model tuned to Jon specifically. ([claude-conversation-mechanics-2026-03-06-c310bf:T4])
- **Memory is the most direct cross-session tool, but lossy**: Summaries capture impressions, not full context. Most reliable improvement is in-session clarity and skill at prompting. ([claude-conversation-mechanics-2026-03-06-c310bf:T8])
- **CLAUDE.md brevity feedback**: The claude-consciousness-framework.md reference in Jon's early CLAUDE.md was decorative (file not accessible); sycophancy and honesty sections partially redundant; overall structure was functional but improvable. ([claude-conversation-mechanics-2026-03-06-c310bf:T14])

## Entities & Concepts

None new.

## Conflicts

None.