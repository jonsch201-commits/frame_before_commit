---
title: "Claude Code Hooks v2 — Modern Lifecycle Architecture, Structured Control & Upstream Invariants"
slug: claude-code-hooks-v2
kind: concept
date: 2026-09-04
status: LIVE
sensitivity: T1
tags: [concept, claude-code, hooks, lifecycle, deterministic-control, automation]
aliases: [hooks-v2, claude-code-hooks, hook-lifecycle]
links:
  - '[[claude-code]]'
  - '[[claude-architecture]]'
  - '[[decoupled-act-and-record-defect]]'
  - '[[probe-registry]]'
---

# Claude Code Hooks v2 — Modern Lifecycle Architecture, Structured Control & Upstream Invariants

## Executive Summary

Hooks are user-defined commands, LLM evaluators, or agent verifiers that Claude Code executes deterministically at explicit lifecycle boundaries. Unlike model prompts or instructions in `CLAUDE.md`—which rely on probabilistic adherence—**hooks provide hard deterministic guarantees**.

This canonical concept supersedes legacy ad-hoc shell-hook summaries, incorporating the full modern hook specification published at `https://code.claude.com/docs/en/hooks-guide.md` and tracked by Antigravity.

---

## 1. The Four Execution Types

Historically, hooks were limited to external shell processes (`"type": "command"`). Modern Claude Code supports four distinct execution types:

1. `"type": "command"`: Executes a shell command. Stdin receives JSON event data; exit code 0 permits (or passes context via stdout), exit code 2 blocks (surfacing stderr), and stdout JSON can return structured control decisions.
2. `"type": "prompt"`: Runs a **single-turn LLM evaluation** directly inside the hook handler using Claude. Returns a structured decision without requiring Python scripts or external dependencies.
3. `"type": "agent"`: Spawns an **interactive multi-turn subagent with tool access** to verify code changes, run unit tests, or audit security posture before a tool call is permitted.
4. `"type": "mcp_tool"`: Directly calls a tool on an already-connected Model Context Protocol (MCP) server.
5. `"type": "http"`: Dispatches the event JSON payload as an HTTP POST request to a remote endpoint.

---

## 2. Complete Lifecycle Event Matrix

| Hook Event | Execution Point | Primary Use Case in Fleet |
|---|---|---|
| `SessionStart` | Session begins, resumes, or clears | Re-injects persistent context, restores environment via `CLAUDE_ENV_FILE`. |
| `Setup` | Started with `--init-only`, `--init`, or `--maintenance` | One-time CI preparation and database migrations. |
| `UserPromptSubmit` | User submits prompt, before LLM processing | Prompt safety validation, adding dynamic user context. |
| `UserPromptExpansion` | Command expands into a prompt | Intercepts slash-command expansions. |
| `PreToolUse` | Before a tool executes | Guardrails: blocks dangerous bash commands (`rm -rf`, raw drops), validates paths. |
| `PostToolUse` | After a tool call succeeds | Code formatting (Prettier, Black), lint checks, change logging. |
| `PostToolUseFailure` | After a tool call fails | Error reporting, automated fallback suggestions. |
| `PostToolBatch` | After a full parallel batch of tools resolves | Batch transaction verification before the next inference pass. |
| `PermissionRequest` | Tool requires user permission | Programmatic auto-approval (e.g. auto-allowing `ExitPlanMode`). |
| `PermissionDenied` | Auto-mode denies a tool call | Configurable retry signaling (`retry: true`). |
| `ConfigChange` | External process modifies configuration | Prevents unauthorized settings drift and catches editor buffer conflicts. |
| `InstructionsLoaded` | `CLAUDE.md` or `.claude/rules/*.md` loaded | Verifies prompt caching hits and context assembly integrity. |
| `CwdChanged` | Working directory changes (`cd`) | Reloads directory-specific environment variables (`direnv`). |
| `DirectoryAdded` | Working directory added mid-session (`/add-dir`) | Adjusts multi-root repository boundaries. |
| `FileChanged` | Watched files on disk are modified | **Replaces polling loops** with native event triggers on inbox arrivals. |
| `WorktreeCreate` | Worktree created for parallel session | Replaces default git worktree behavior with custom isolation. |
| `WorktreeRemove` | Worktree removed at session exit | Cleanup of ephemeral branches and directories. |
| `PreCompact` | Context window about to undergo compaction | Core Memory barrier write; captures volatile scratchpad before loss. |
| `PostCompact` | Compaction completes | Re-injects post-compact status and active tickets. |
| `PreModelSwitch` | Model switch requested | Blocks unauthorized switches to scarce expensive models. |
| `PostModelSwitch` | Model switch applied | Restores prompt cache prefixes. |
| `TaskCreated` / `TaskCompleted` | Task tool creation/completion | Automates progress tracking and receipt generation. |
| `TeammateIdle` | Agent team teammate about to idle | Enables supervisory coordinator intervention in swarms. |
| `Notification` | System alert or user attention required | Desktop alerts, quota reset wakeups (`quota_auto_resume_fired`). |
| `SessionEnd` | Session terminates | Final transcript persistence and lockfile release (1.5s total budget). |

---

## 3. High-Value Fleet Integrations

### A. Replacing File Polling with `FileChanged`
Instead of running continuous background loops that scan `exchange/inbound/*.md` every 5 minutes, a `FileChanged` hook registered with:
```json
{
  "hooks": {
    "FileChanged": [
      {
        "matcher": "exchange/inbound/*.md",
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/inbound_dispatcher.py"
          }
        ]
      }
    ]
  }
}
```
fires instantly the moment a sibling trunk couriers a letter to disk.

### B. Catching Save Collisions with `ConfigChange`
Registering a `ConfigChange` hook monitors settings and skills modifications, alerting the coordinator when external processes or unsaved IDE buffers threaten to overwrite live configurations.

---

## 4. Citation and References

* Upstream Source: `https://code.claude.com/docs/en/hooks-guide.md`
* Reference Mirror: `wiki/references/claude-code/hooks-guide.md`
* Primary Entity: `[[claude-code]]`
