---
name: chat-exporter
description: >-
  Exports claude.ai conversation history to markdown files for ingestion into raw/. Two paths: (1)
  Native JSON export via convert-export.py — full fidelity, all projects, no DOM constraint; (2)
  DOM-based browser extraction — real-time capture, subject to virtual DOM truncation. Use when
  Jon says "export chats", "export since last time", "grab recent sessions", "export this
  session", or any variant. Primary use: feed raw/ directory for wiki ingestion. This skill is the
  bridge between ephemeral claude.ai sessions and the persistent wiki.
---

# Chat Exporter Skill

## Purpose

Convert claude.ai conversation sessions into markdown files suitable for `raw/` ingestion.

Two extraction paths exist. Use the right one for the situation:

| Path | When to use | Completeness | Coverage |
|------|-------------|--------------|----------|
| **Native JSON export** (`convert-export.py`) | Bulk historical export from Anthropic data download | Always FULL — no DOM constraint | All projects in account |
| **DOM-based browser extraction** | In-session capture, incremental since last export | FULL if done at session close; PARTIAL/TAIL-ONLY for long retroactive sessions | Current project only |

---

## Native JSON Export Mode (convert-export.py)

### When to use

Jon has requested a data export from Anthropic (Settings → Privacy → Export data). The downloaded zip contains `conversations.json` — a complete account-level export with no virtual DOM truncation.

**This is the preferred path for bulk historical extraction.** It captures every message in every conversation, including tool calls and thinking blocks, at full fidelity.

### Script location

`skills/chat-exporter/scripts/convert-export.py`

### Modes

```bash
# Inspect: list all conversations with date, UUID, message count, char count
python convert-export.py <export-dir> --inspect

# Dry run: show what would be written without writing anything
python convert-export.py <export-dir> --dry-run --since 2026-04-12 --out raw/transcripts/claude-ai/fl

# Run: write files
python convert-export.py <export-dir> --run --since 2026-04-12 --out raw/transcripts/claude-ai/fl
python convert-export.py <export-dir> --run --ids uuid1,uuid2 --out raw/transcripts/claude-ai/fl
python convert-export.py <export-dir> --run --ids uuid1,uuid2 --out raw/transcripts/claude-ai/fl --force
```

### Filters

- `--since YYYY-MM-DD` — only conversations updated on or after this date
- `--ids uuid1,uuid2` — comma-separated full UUIDs or 6-char prefixes
- `--force` — overwrite existing files (default: skip if UUID6 already present in out dir)
- `--no-thinking` — omit extended-thinking `<details>` blocks from the primary file (preserved by default)
- `--no-sidecar` — skip the manifest-v2 companion file (written by default; see below)

### Known issue — dedup bug

The dedup check uses `parts[3]` (day of month) instead of `parts[4]` (UUID6 prefix) when scanning existing files. Files in the output directory are not correctly detected as duplicates. Fix pending: change `parts[3]` to `parts[4]` in `existing_uuid_prefixes()`.

### Content block handling

The JSON export contains 5 content block types. The primary `.md` file's inline
rendering (unchanged since before manifest-v2, below) handles them as follows:

| Block type | Handling in primary `.md` |
|------------|------------|
| `text` | Extracted and stripped |
| `tool_use` | Summarized: `[tool_use: name — key: val]` |
| `tool_result` | Summarized: `[tool_result: name — content[:200]]` |
| `thinking` | Preserved by default as a `<details>` collapsible (corrected 2026-07-24 — was stale here; see `--no-thinking` above) |
| `flag` | Skipped silently |

Use `content` blocks as authoritative — the top-level `text` field differs in ~13% of messages.

### Extraction manifest v2 — sidecar file (PRESERVED BY DEFAULT, 2026-07-24)

The primary `.md` file's inline summaries above (`tool_use`/`tool_result` truncated
to 200c, no block timestamps, no attachment text, no branch metadata) are unchanged —
the wiki citation system anchors to primary-file turn numbers (`[slug:Tn]`) and cannot
be renumbered. Instead, `convert-export.py --run` now also writes one companion file
per conversation: `<primary-stem>.sidecar.md` (e.g.
`chat-2026-07-24-aaaa11-demo.sidecar.md`), containing losslessly:

- per-block `start_timestamp`/`stop_timestamp` and message `created_at` for every turn
- `model` if the source carries one (claude.ai exports do not — PROVEN-ABSENT)
- full, untruncated `tool_use` input and `tool_result` content/`structured_content`
- attachment `extracted_content` (full uploaded-doc text) and `files[]` references
- thinking with a fidelity tag (RAW/SUMMARY/SIGNATURE-ONLY/ABSENT — claude.ai is always RAW)
- `parent_message_uuid` per message, with a `branch_point` flag (not expanded — branch
  expansion would change which messages get a turn number, so it is a separate,
  Jon-gated citation-migration)

Sidecar `T{n}` headings are computed by the identical walk that numbers the primary
file's turns, so they always match. Messages that get no turn in the primary file
(no visible text) are still captured under an "Unindexed" heading in the sidecar,
explicitly outside the `Tn` sequence.

Pass `--no-sidecar` to skip. Source-field provenance and priority order:
`exchange/anthropic-zip-source-audit-2026-07-24.md`. Reserved citation formats
`[slug:Tn.thinking]` / `[slug:Tn.tool]` / `[slug:Tn.tool{k}]` / `[slug:Tn.result]`
(`skills/wiki-master/references/citability-standard.md`, "Extended Content Citation
(Reserved)") can now resolve into this file once wiki-master wires them — not done
by this change.

### Project identification

**The Anthropic export has no project field.** Project membership cannot be determined programmatically. Use `--since` with the FL project creation date (2026-04-12) as a primary gate, then triage conversation titles manually. FL vs personal life vs professional must be assigned by Jon at triage time.

### Output and watermark

`cmd_run` prints an EXPORT-LOG.md entry to stdout. Paste this into `raw/EXPORT-LOG.md` manually. The watermark line is the last line of that file.

---

## Raw File Naming and Directory Schema

### Directory structure (Option D — confirmed 2026-05-06; moved under `raw/transcripts/` in the
2026-07-28 L1 move, see `.claude/agents/fable-mirror.md:25-26`)

```
raw/transcripts/claude-ai/
  fl/                          ← Claude Foundational Layer sessions
    master-of-triage/          ← one directory per logical session
      [topic]-2026-04-28-090a56.md
    skills-master/
      [topic]-2026-05-01-bcafba.md
  personal/                    ← personal life sessions (NOT ingested into FL wiki)
  pro/                         ← professional/work sessions (NOT ingested unless flagged)
```

**Session directory** = slugified session name (one directory per logical conversation, even if it spans multiple UUIDs).

**Filename** = `[topic-description]-YYYY-MM-DD-uuid6.md`

### Note on current state

`convert-export.py` currently produces `chat-YYYY-MM-DD-uuid6-slug.md` (flat, no project subdirectory). Updating the script to produce Option D format is a pending task. Files in `raw/first_intake_v1/` use the old format and will need sorting into the new structure.

---

## The Core DOM Constraint (Browser Extraction Path)

---

## The Core Constraint (Read First)

Claude.ai renders conversations lazily. Only content near the current scroll position exists in the DOM. For sessions longer than ~8,000 characters:

- **Content below the fold:** not in DOM, cannot be extracted
- **Content above the fold:** unmounted as you scroll down, cannot be extracted retroactively
- **The tail end:** always available (most recently rendered)

**Implication:** Incremental exports at session close are reliable. Retroactive bulk exports of long sessions are partial. The skill flags all gaps explicitly — never silently drops content.

---

## Modes

### 1. Incremental Export (primary mode)

Use when: Jon asks to export since last export, or at session close.

The skill uses a **watermark** — a stored timestamp of the last successful export. On each run, it exports only sessions updated after the watermark, then updates the watermark.

**Watermark storage:** The watermark is recorded in `raw/EXPORT-LOG.md` as the last line:
```
WATERMARK: YYYY-MM-DDTHH:MM:SSZ
```

If no watermark exists, ask Jon: "No previous export found. Export all available sessions, or set a start date?"

### 2. Single Session Export

Use when: Jon says "export this session" or provides a specific chat URL or ID.

Navigates directly to that session and extracts.

### 3. Bulk Retroactive Export

Use when: Jon explicitly requests historical export with a date range.

**Honest constraint:** Long sessions will be partial. The skill runs extraction on each session, reports the character count captured, and flags sessions where captured content appears truncated (ending mid-sentence or significantly shorter than expected).

---

## Incremental Export Protocol

### Step 1 — Read watermark

```
Read raw/EXPORT-LOG.md
Extract WATERMARK timestamp
```

If no file: watermark = null, ask Jon for start date or confirm "all available."

### Step 2 — Retrieve sessions since watermark

```
Use recent_chats tool with after=watermark
Retrieve up to 20 sessions per call
Paginate if needed (use before= parameter with earliest updated_at)
Stop when all sessions since watermark are retrieved
```

Note: `recent_chats` is scoped to the current project. Sessions outside this project require Jon to navigate to them manually.

### Step 3 — Extract each session

For each session:

1. Navigate browser to session URL
2. Scroll to top of conversation container (forces React to mount earlier content)
3. Extract full page text
4. Check character count — flag if <3000 chars and session appears substantive
5. Attempt scroll-and-re-extract once if initial extraction seems truncated

```javascript
// Scroll the conversation container to top
(() => {
  const allElements = document.querySelectorAll('*');
  for (const el of allElements) {
    if (el.scrollTop > 1000) el.scrollTop = 0;
  }
  return { scrolled: true };
})()
```

Wait 2 seconds after scroll for React to re-render, then extract.

### Step 4 — Write markdown files

One file per session. Filename format:
```
chat-[YYYY-MM-DD]-[first-6-chars-of-id]-[slugified-title].md
```

Example: `chat-2026-04-30-babab4-test-master.md`

File format:
```markdown
---
chat_id: [full UUID]
title: [session title]
date_updated: [ISO timestamp]
url: https://claude.ai/chat/[id]
extraction_date: [today]
extraction_mode: incremental | single | bulk
extraction_completeness: FULL | PARTIAL | TAIL-ONLY
char_count: [N]
---

# [Session Title]

[extracted content]

---
*Extraction note: [FULL — complete session captured | PARTIAL — [N] chars captured, session may be longer | TAIL-ONLY — virtual DOM limit reached, only final portion captured]*
```

### Step 5 — Update watermark

After all sessions extracted and files written:
```
Append to raw/EXPORT-LOG.md:
## [YYYY-MM-DD HH:MM CDT] export | [N] sessions | watermark updated
WATERMARK: [current UTC timestamp]
```

---

## Retroactive Bulk Export Protocol

Same as incremental but with explicit date bounds and more aggressive scroll attempts.

**For very long sessions (scroll depth >20,000px):**

1. Scroll to top
2. Wait 3 seconds
3. Extract — record char count (attempt 1)
4. Scroll to middle of conversation container
5. Wait 2 seconds
6. Extract again — append any new content not already captured
7. Scroll to top again
8. Final extract

This multi-scroll approach captures more of long sessions but cannot guarantee completeness. Report total chars captured and flag as PARTIAL if the session's recent_chats summary suggests substantially more content exists.

**For sessions that are 404 (deleted or bad URL):**
Log in EXPORT-LOG.md as NOT-FOUND. Do not create a file. Record whatever is known from recent_chats summary.

---

## EXPORT-LOG.md Format

```markdown
# Chat Export Log

This file records all export runs and the current watermark.
The WATERMARK line is always the last line of this file.

---

## [YYYY-MM-DD] export | N sessions | incremental since [date]

Sessions exported:
- chat-2026-04-30-babab4-test-master.md — FULL — 12,450 chars
- chat-2026-04-29-da7a06-consciousness-test.md — PARTIAL — 8,094 chars (truncated)

Sessions not found (404):
- c6154b3f — 4-branch directed test — content partially known from search

---

WATERMARK: 2026-04-30T22:00:00Z
```

The watermark is always the last line. Parse by reading the last line of the file.

---

## Invocation Triggers

| Jon says | Mode | Action |
|---|---|---|
| "Export chats" | Incremental | Export since watermark |
| "Export since last time" | Incremental | Export since watermark |
| "Export this session" | Single | Export current session |
| "Export [chat URL]" | Single | Export that URL |
| "Export everything" | Bulk | Ask for date range or confirm all |
| "Export since [date]" | Bulk with bound | Export from that date forward |
| "What's been exported" | Status | Read and report EXPORT-LOG.md |
| "Update the watermark" | Admin | Set watermark without export |

---

## Failure Modes and Responses

| Failure | Response |
|---|---|
| Chrome extension not connected | "Browser tool not connected. Check Chrome extension is open and signed in, then retry." |
| Session 404 | Log as NOT-FOUND, continue with remaining sessions |
| Extraction <500 chars on substantive session | Flag as TAIL-ONLY, attempt scroll-and-retry once |
| recent_chats returns nothing | "No sessions found since [watermark]. Either no new sessions exist or the watermark is ahead of actual sessions. Confirm?" |
| Watermark missing | Ask Jon: start date, or export all available |

---

## What This Skill Does Not Do

- **Does not guarantee full extraction of long sessions.** The virtual DOM constraint is architectural. Flag it, work around it, but never claim completeness on sessions where truncation is likely.
- **Does not export sessions from other projects.** recent_chats is project-scoped. Cross-project export requires Jon to navigate manually.
- **Does not modify raw/ files once written.** If a session needs re-export (e.g., more content captured after scroll), write a new file with `-v2` suffix and note the update in EXPORT-LOG.md.
- **Does not ingest.** Export creates files in raw/. Ingestion is a separate step handled by the wiki-master skill.

---

## Integration with Wiki

After export, the standard handoff is:
```
"Ingest new files in raw/ since [date]"
```

The wiki-master skill handles ingestion from there. The chat-exporter skill's only job is getting raw content into raw/.

---

## Session Close Reminder

The highest-reliability window for export is immediately at session close, before the conversation scrolls out of the viewport. If Jon signals session end, prompt:

> "Before we close — want me to export this session to raw/? It's most complete right now."

This is optional and should not delay session close if Jon is in a hurry.
