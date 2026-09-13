---
title: "Claude Code Function Hooks & Plugin Authoring — Next-Gen Middleware Architecture"
slug: claude-code-function-hooks
kind: concept
date: 2026-09-04
status: LIVE
sensitivity: T1
tags: [concept, claude-code, function-hooks, middleware, plugins, security, zero-knowledge-secrets]
aliases: [function-hooks, plugin-authoring, claude-code-middleware]
links:
  - '[[claude-code]]'
  - '[[claude-code-hooks-v2]]'
  - '[[decoupled-act-and-record-defect]]'
  - '[[citability-standard]]'
---

# Claude Code Function Hooks & Plugin Authoring — Next-Gen Middleware Architecture

## Executive Summary

**Function Hooks** represent a paradigm shift in Claude Code customization, moving beyond external shell scripts into an **in-process, Express.js-style TypeScript middleware pipeline**. Enabled via the runtime feature flag `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`, function hooks introduce native tool interception, input rewriting, short-circuit caching, zero-knowledge secret redaction, custom terminal UI elements, interactive user dialogues, and embedded `$model` / `$http` invocations.

This concept document details the mechanics, configuration schema, and architectural breakthroughs of function hooks, specifically framing their application to fleet governance and the elimination of the Decoupled-Act-and-Record defect.

---

## 1. Activation & Environment Setup

Function hooks are enabled at launch via environment variable:

```bash
CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1 claude
```

### Built-in Capabilities Unlocked:
* **`/plugin-authoring`**: An interactive built-in agent skill dedicated to scaffolding, writing, and debugging function-hook plugins.
* **`/reload-plugins`** (or `/reload plugins`): Dynamically hot-reloads plugin code without restarting the host Claude Code session.

---

## 2. Structural Architecture: Express-Style Middleware

Traditional Claude Code hooks operate as external out-of-process shell commands (`PreToolUse`, `PostToolUse`) communicating via stdin JSON and exit codes (0 or 2). They cannot modify user prompts, rewrite tool arguments, inject dynamic UI rows, or maintain state across turns.

Function hooks operate as **in-process middleware functions** written in TypeScript (`.ts`), configured via:
* `.claude/plugins.json`: Plugin registration and metadata.
* `.claude/hooks.json`: Event matchers and middleware pipeline ordering.
* `.claude/<hook_name>.ts`: The executable TypeScript middleware logic.

```
                  USER PROMPT / TOOL CALL
                             |
                             v
               +-----------------------------+
               |  FUNCTION HOOK MIDDLEWARE   |
               |  (Input Rewriter / Proxy)   |
               +--------------+--------------+
                              |
              +---------------+---------------+
              |                               |
       (Short-Circuit)                 (Allow / Mutate)
              |                               |
              v                               v
      [ Return Cached Copy ]          [ Downstream Tool / Model ]
```

---

## 3. The 9 Breakthrough Primitives

### 1. Input Rewriting
Middleware can intercept tool inputs and rewrite arguments before execution.
* *Fleet Example:* Automatically intercepting `Bash` tool calls to rewrite `npm install` to `pnpm install`, or transforming raw shell scripts into sandboxed wrappers.

### 2. Built-in Tool Overriding & Proxy Routing
Function hooks can override default native tools (`WebSearch`, `WebFetch`) with enterprise alternatives:
* *Example:* Intercepting `WebSearch` to query internal enterprise search or private search APIs (Exa, Brave), with automatic fallback to native web search if API keys are absent.
* *Example:* Routing `WebFetch` through private corporate proxy tunnels.

### 3. Short-Circuiting & Caching
Hooks can inspect an internal cache store. If a URL or query has already been executed within the session or fleet cache, the hook returns the cached payload immediately, bypassing the tool execution and saving time/tokens.

### 4. Zero-Knowledge Secret Redaction (Transcript Protection)
A critical security breakthrough for agentic development:
* The middleware intercepts user input containing API keys or credentials before it reaches the session transcript.
* The secret is replaced with an opaque surrogate identifier (e.g. `__SECRET_ID_01__`) and stored in an isolated in-memory store.
* When the agent subsequently makes an API call using that identifier, the function hook intercepts the outgoing request and swaps the real secret back in.
* **Result:** The LLM uses the secret, the tool call succeeds, but **the session transcript and raw logs contain zero plaintext credentials**.

### 5. In-Memory & Persistent Variable Stores
Function hooks provide two native state stores:
* **Variable Store (In-Memory):** Ephemeral state accessible across successive hooks and turns within a session.
* **Persistent Store (Disk):** Key-value state persisting across session restarts and context compactions.

### 6. Custom Terminal UI Rendering
Function hooks can inject dynamic UI panels directly into the Claude Code terminal interface:
* Live deployment progress bars (e.g. tracking Vercel/GitHub Actions deployment status).
* Mode indicators (e.g. prominent banners: `[PRODUCTION MODE]` vs `[DRY-RUN MODE]`).
* Interactive toggles and buttons allowing the user to hide/show telemetry panels.

### 7. Interactive User Dialogues (`ask`)
Hooks can programmatically halt execution to ask the user interactive questions:
* *Refactoring Gate:* Automatically prompting the user whenever a file edit exceeds 1,000 lines: *"File exceeds 1,000 lines. Would you like to refactor into smaller modules?"*
* *PR Comprehension Quiz:* Halting PR creation until the user confirms understanding of the diff.

### 8. Native Model Calls (`$model`)
Hooks can invoke Claude models (e.g. Claude Haiku) asynchronously or synchronously within the hook logic:
* Running automated epistemic checks or summarizations without polluting the main conversation context.
* Feeding turn outputs to a model to generate concise status summaries.

### 9. Auditing & External Telemetry (`$http`)
Hooks can dispatch real-time structured telemetry to corporate SIEMs, databases, or logging pipelines on every single event, fulfilling enterprise compliance and SOC 2 / NAIC requirements.

---

## 4. Application to the Fleet & Open Problems

| Fleet Defect / Goal | Function Hook Remedy |
|---|---|
| **Decoupled-Act-and-Record Defect** | A PostToolUse function hook measures file hash and byte delta before permitting the tool success receipt to return to the model. |
| **Transcript Credential Leaks** | Zero-knowledge secret redaction keeps API tokens out of `subagent-logs/` and session JSONL. |
| **Cross-Trunk Polling Latency** | Direct `$http` or in-memory store signaling between sessions on the same machine. |
| **Unbounded File Bloat** | Interactive `ask` gate triggering refactoring before files expand past 1,000 lines. |

---

## 5. Upstream Provenance

* Feature Flag: `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`
* Primary Tools: `/plugin-authoring`, `/reload-plugins`
* Changelog Reference: Claude Code v2.1.260 (September 3, 2026)
