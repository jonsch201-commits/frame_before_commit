---
title: Token Size, Context Window Scale, and API Transmission Mechanics
trunk: fl
branch: [mechanics]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-MECH; sub: branch `mechanics` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-26-8b5b19-understanding-token-size-and-api-data-transmission.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: How to use Claude
date_ingested: 2026-05-20
type: session
tags: how-to-use-claude, ai-mechanics, tokens, api, context-window
---

## Summary

Session (3.5K chars, 2026-03-26) covering token size fundamentals, what is actually transmitted in each API call, and Anthropic's stateless architecture. Short but establishes baseline technical understanding of context window mechanics and why the stateless design exists — relevant to any FL work that reasons about context overhead and persistent context patterns.

## Key Claims

- **Token ≈ ¾ word, 4 bytes**: ~3-4 chars per token; 200K tokens ≈ 800KB, ~500 pages. ([ai-mechanics-token-api-2026-03-26-8b5b19:T2])
- **Every message sends the full context**: System prompt, project files, userMemories, document attachments, and message history all transmitted on each request. Context starts at thousands of tokens overhead before user types a word. ([ai-mechanics-token-api-2026-03-26-8b5b19:T4])
- **Stateless architecture is deliberate**: No server-side session state. Each request is a fresh inference. This eliminates session corruption and stale-context bugs at the cost of full re-transmission. ([ai-mechanics-token-api-2026-03-26-8b5b19:T4])
- **Prompt caching partially offsets cost**: Repeated prefixes (system prompt) can be cached at reduced compute cost even if the bytes still travel the wire. ([ai-mechanics-token-api-2026-03-26-8b5b19:T4])
- **The model has no memory of prior conversations** unless explicitly retrieved via past_chats tools — context window assembly is the sole mechanism for "memory." ([ai-mechanics-token-api-2026-03-26-8b5b19:T2])

## Entities & Concepts

None new.

## Conflicts

None.