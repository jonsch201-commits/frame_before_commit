---
title: "Claude Code Hooks and Agent Engine — Canonical Reference & Upstream Grounding"
slug: claude-code-hooks-and-agent-engine
kind: concept
date: 2026-09-11
status: PROPOSED
sensitivity: T1
tags: [claude-code, hooks, agent-engine, subagents, agent-teams, upstream-docs]
links:
  - '[[claude-architecture]]'
  - '[[citability-standard]]'
  - '[[multi-agent-orchestration]]'
  - '[[decoupled-act-and-record-defect]]'
---

# Claude Code Hooks and Agent Engine — Canonical Reference

## 1. Upstream Grounding & Automatic Tracking

This concept is maintained autonomously by `scripts/watch_claude_code_docs.py` tracking upstream `https://code.claude.com/docs/`.
Latest upstream synchronization: `2026-09-11T14:19:04.209524+00:00`.

### Tracked Upstream Artifacts:
- **[settings-reference.md](https://code.claude.com/docs/en/settings-reference.md)**: `436256 bytes`, `sha256: c428e5975d76c405...`

## 2. The Modern Hook Lifecycle (v2.1+)

Claude Code hooks execute deterministically at key lifecycle boundaries, allowing rigorous behavioral control over agent sessions.

### Execution Types
Beyond traditional shell commands (`"type": "command"`), Claude Code natively supports:
1. `"type": "prompt"`: Single-turn LLM evaluation directly in the hook loop.
2. `"type": "agent"`: Multi-turn subagent verification with tool access before proceeding.
3. `"type": "mcp_tool"`: Invocation of tools on registered MCP servers.
4. `"type": "http"`: Structured webhook payload dispatch.

### Critical Modern Lifecycle Events
| Event | Trigger Point | Fleet Utility |
|---|---|---|
| `ConfigChange` | External process modifies configuration | Prevents unauthorized settings drift and catches editor buffer conflicts. |
| `FileChanged` | Watched files modified on disk | Eliminates manual polling loops across inter-trunk inboxes. |
| `TaskCreated` / `TaskCompleted` | Task tool creation/completion | Automates progress tracking and receipt logging. |
| `TeammateIdle` | Teammate in Agent Teams about to idle | Enables supervisory steering in multi-agent swarms. |
| `InstructionsLoaded` | CLAUDE.md or rules loaded | Epistemic verification of prompt caching and context injection. |
| `PreModelSwitch` / `PostModelSwitch` | Model change requested/applied | Guards token budget tiers (Opus vs Sonnet vs Haiku). |

## 3. Graph RAG Indexing
This concept connects upstream documentation directly into the federated vector and FTS5 Graph RAG index (`N:\claude-indexes\graphrag-federated\index.sqlite`), enabling cross-trunk semantic retrieval across all 6 project seats.
