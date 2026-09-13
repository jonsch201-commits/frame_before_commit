---
title: "Source-Data Schemas — CC Session JSONL + claude.ai Export JSON"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; the canonical page for the two source-data schemas the program lives on"
source_kind: reference
layer: L4
domain: fl/cfl/wiki
retrieval_key: source-schemas
status: LIVE — empirical, re-measure on drift WARN
maintained_by: coordinator; re-sync on every WARN from scripts/audit/check_source_schema_drift.py
last-updated: 2026-08-22, measured against session 643640a7-f68a-4ed3-ba42-7dbaaaeb7b32
  (harness versions 2.1.226-2.1.241 observed in that single file) and export
  extracted-1786933322/conversations.json (249 conversations)
links:
  - wiki/references/agent-memory/cc-jsonl-thinking-signature-only.md (thinking-encryption
    version boundary, v2.1.72+)
  - wiki/references/record-architecture-v1.md (L0-L4 layer model this page's `layer:` uses)
  - CLAUDE.md "Transcript Corpus (mirror corpus)" section (46/250 attachments/files split,
    provenance grades)
  - skills/chat-exporter/SKILL.md (convert-export.py, the only consumer of Section 2's
    export schema)
  - skills/probe-registry/ (the seal-pattern this page's drift probe implements)
  - scripts/audit/check_source_schema_drift.py (the maintenance instrument for this page)
---

# Source-Data Schemas — CC Session JSONL + claude.ai Export JSON

## Why this page exists

Jon, 2026-08-22, ruling-shaped observation: **"if retrieval is needed to get the right
answer the right time, then you have a wiki defect."** Load-bearing schema knowledge for
this program's two source formats was scattered — a field here in `convert-export.py`'s
comments, a boundary date in one agent-memory drain page, consumer knowledge nowhere
written down at all. This page is the single landing point. **Nothing here is recalled;
every field below was measured from a real file on 2026-08-22, and the probe/instrument
that measured it is cited.**

⛔ **NO PUBLISHED SCHEMA EXISTS for either format.** Anthropic does not document the CC
session JSONL wire format or the claude.ai export JSON format. Everything in Sections 1
and 2 is empirical — reverse-engineered from files on disk, subject to change on any
harness or export-pipeline update without notice. Section 3 exists because of that: a
schema page built this way goes stale silently unless something re-measures it.

---

## Section 1 — CC session JSONL

**Location:** `~/.claude/projects/<slug>/*.jsonl` (main session transcripts) and
`~/.claude/projects/<slug>/<session-uuid>/subagents/agent-*.jsonl` (+ matching
`.meta.json` sidecar) for subagent transcripts.

**Measured against:** the newest CFL session JSONL,
`643640a7-f68a-4ed3-ba42-7dbaaaeb7b32.jsonl` (21,530 lines, 0 JSON-parse failures),
plus subagent file `.../643640a7-.../subagents/agent-a0162581aa379b21d.jsonl` (108
lines: 69 assistant, 37 user, 2 attachment) and its sidecar
`agent-a0162581aa379b21d.meta.json`.

**Harness version at measurement:** present in the record itself (`version` field on
most record types) — **NOT UNKNOWN**. The single measured file spans harness versions
`2.1.226`, `2.1.233`, `2.1.239`, `2.1.241` (the file covers multiple CC upgrades across
its lifetime; a session file is not pinned to one build).

### Record types observed (16, main-session file)

Every `type` value seen in the 21,530-line probe, with per-type line count and the
field set every observed instance of that type carries (a **floor**, not a ceiling —
individual records may carry more):

| `type` | count | always-present fields (measured) |
|---|---|---|
| `user` | 3,590 | `type, message, uuid, timestamp, sessionId, version, userType` (+ situational: `isMeta`, `origin`, `isSidechain`, `promptId`, `toolUseResult`, `isCompactSummary`, `isVisibleInTranscriptOnly`, `queuePriority`, `toolDenialKind`, `turnCompanion`, `sourceToolAssistantUUID`, `classifierMetaLines`, `imagePasteIds`, `interruptedMessageId`) |
| `assistant` | 6,567 | `type, message, uuid, timestamp, session_id, userType` (note: **`session_id` snake_case here, `sessionId` camelCase on `user`/`system`/most others** — a real, measured inconsistency, not a documentation error) |
| `system` | 789 | `type, subtype, uuid, timestamp, sessionId` (+ situational: `hookEvent`-shaped rows carry `hookInfos`/`hookErrors`/`hookAdditionalContext`/`hookCount`/`preventedContinuation`/`stopReason`/`hasOutput`/`level`; other subtypes carry `compactMetadata`, `choice`, `content`, `durationMs`, `fallbackModel`, `originalModel`, `messageCount`, `persistedAsDefault`, `pendingBackgroundAgentCount`, `url`) |
| `attachment` | 2,208 | `type, attachment, sessionId, cwd, entrypoint, gitBranch, isSidechain, parentUuid, timestamp, uuid, version` |
| `file-history-snapshot` | 184 | `type, messageId, snapshot, isSnapshotUpdate` |
| `file-history-delta` | 199 | `type, messageId, trackingPath, backup, snapshotMessageId, timestamp` |
| `last-prompt` | 1,070 | `type, sessionId, lastPrompt, leafUuid` |
| `mode` | 1,069 | `type, sessionId, mode` |
| `permission-mode` | 1,069 | `type, sessionId, permissionMode` |
| `ai-title` | 1,068 | `type, sessionId, aiTitle` |
| `bridge-session` | 1,070 | `type, sessionId, bridgeSessionId, lastSequenceNum, ownerAccountUuid, ownerOrganizationUuid` |
| `queue-operation` | 792 | `type, sessionId, operation, content, timestamp` |
| `pr-link` | 1,298 | `type, sessionId, prNumber, prRepository, prUrl, timestamp` |
| `custom-title` | 166 | `type, sessionId, customTitle` |
| `agent-name` | 166 | `type, sessionId, agentName` |
| `atis-latch` | 119 | `type, sessionId, atis` |

**Subagent-file-only fields (measured on `agent-a0162581aa379b21d.jsonl`):**
`isSidechain: true` on every record, `agentId` on the seed `user` record (matches the
filename's `agent-<agentId>.jsonl`), `parentUuid: null` on the seed record (a subagent
transcript is its own root, not a continuation of the main session's uuid chain), and
**no top-level `sessionId`** on the seed record — the subagent's identity is carried by
`agentId` + the `.meta.json` sidecar, not by the main session's id. The sidecar
(`agent-a0162581aa379b21d.meta.json`, measured verbatim):
```json
{"agentType":"security-builder","description":"Land E-1/E-2 equip pipeline","toolUseId":"toolu_01HkxfH7MgzcNERF7py9EHYh","spawnDepth":1,"model":"sonnet"}
```
`toolUseId` here is the join key back to the dispatching `Agent`/`Task` tool_use block in
the PARENT session's JSONL.

### `message.content` block shapes (measured, redacted)

On `assistant` records, `message.content` is a list of blocks. Three shapes observed:

**thinking** (v2.1.226, post-boundary — see the version-boundary note below):
```json
{"type": "thinking", "thinking": "", "signature": "CAIS+wYKhwEIEBgCKkD0rwl5PP246yZt..."}
```
`thinking` is **always the empty string** post-boundary; the real content lives only in
the opaque, server-decryptable `signature` blob.

**text**:
```json
{"type": "text", "text": "I'll start with the cold-open read chain and the i..."}
```

**tool_use**:
```json
{"type": "tool_use", "id": "toolu_01Jf1N4QuEXL3y9cjyprWzkd", "name": "PowerShell",
 "input": {"command": "...", "description": "..."}, "caller": {"type": "direct"}}
```
`caller.type` distinguishes a directly-invoked tool from one issued by/through a
subagent context (measured value: `"direct"`; other values not enumerated in this
probe — treat as UNVERIFIED beyond `"direct"`).

On `user` records that carry a tool result, `message.content` holds a `tool_result`
block and the **top-level** `toolUseResult` field (sibling to `message`, not inside it)
carries the executed shape:
```json
{"message": {"content": [{"tool_use_id": "toolu_01Jf1N4QuEXL3y9cjyprWzkd",
  "type": "tool_result", "content": "2026-08-08 00:00:53 -05:00\r\n---\r\n88fb610...",
  "is_error": false}]},
 "toolUseResult": {"stdout": "...", "stderr": "", "interrupted": false, "isImage": false},
 "sourceToolAssistantUUID": "1800d448-fa26-463f-ae72-be4fe8565581"}
```
`toolUseResult`'s shape varies by tool (Bash/PowerShell give `stdout`/`stderr`; other
tools give tool-specific shapes) — **not exhaustively probed here.**

### `isMeta` / `origin.kind` — the mid-turn and human-provenance signal

Two DISTINCT, independently-set fields on `user` records, per the standing constraint
in `CLAUDE.md` ("Jon Messages Subagents Mid-Turn — Main Never Sees It"):

- **`origin: {"kind": "human"}`** — this record is a human-typed turn. Measured example
  (redacted), `origin_human` sample, `643640a7...jsonl`:
  ```json
  {"type": "user", "message": {"role": "user", "content": "Overnight directive..."},
   "origin": {"kind": "human"}, "promptSource": "typed", "timestamp": "2026-08-08T04:56:05.528Z"}
  ```
- **`isMeta: true`** — a harness-injected or mid-turn-dispatched message, NOT a normal
  turn boundary. Measured example, wake-skill injection:
  ```json
  {"type": "user", "isMeta": true, "turnCompanion": true,
   "message": {"role": "user", "content": [{"type": "text", "text": "# /wake — open the session..."}]}}
  ```
  `isMeta: true` also covers Jon's real mid-turn messages TO a running subagent — the
  exact case the standing constraint warns about. Measured on the subagent file: a
  plain-string `user` message mid-transcript reading `"they finished - i need someone
  else to review though you have to review something from soul. how do we solve the
  hard blocker bake_shelf"` with no `isMeta` flag set in that instance (it was the
  seed dispatch context, not a mid-run interjection) — **the discriminator that
  actually separates "Jon typed this mid-run" from "harness injected this" is
  `origin.kind == "human"` combined with position in the transcript (not the seed
  record), not `isMeta` alone; `isMeta` alone is necessary but not sufficient.**
  Confirm both fields before attributing a quote to Jon.

### Task-notification wrapper (subagent-completion signal in the PARENT transcript)

Measured verbatim from `agent-a0162581aa379b21d.jsonl` (this shape appears in a
DISPATCHING session's JSONL, as the content of a `user` record, when a background
agent/task reports back):
```
<task-notification>
<task-id>a98deb11808fc523c</task-id>
<tool-use-id>toolu_0197eVahsRJmfAFhVYMQ4Q8B</tool-use-id>
<output-file>C:\Users\JonSc\AppData\Local\Temp\claude\...\output.txt</output-file>
</task-notification>
```
A stopped/errored variant, also measured, omits `<output-file>` and adds `<status>` +
`<summary>`:
```
<task-notification>
<task-id>bxpuky83m</task-id>
<tool-use-id>toolu_01PB2gaqeLoKkpqng9uwAjjz</tool-use-id>
<status>stopped</status>
<summary>No completion record was found for this background shell co...</summary>
</task-notification>
```
Per the standing memory item "Subagent Final Reports Get Swallowed": the notification
is NOT the report — `<output-file>` names a file, and the real content is the largest
assistant text block in the SUBAGENT's own JSONL, not this wrapper.

### Compact-summary wrapper (`isCompactSummary`)

Measured (redacted), a `user` record marking a context-compaction boundary:
```json
{"type": "user", "isVisibleInTranscriptOnly": true, "isCompactSummary": true,
 "message": {"role": "user", "content": "This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion..."}}
```

### `sessionId` / `session_id` / `uuid` / timestamps

- **`sessionId`** (camelCase) — the field name on `user`, `system`, and nearly every
  non-`assistant`/non-file-delta type. Matches the `.jsonl` filename stem.
- **`session_id`** (snake_case) — the field name specifically on `assistant` records
  (and on `user` tool-result records, alongside `sessionId` — both present there).
  **A consumer that only greps `sessionId` will silently miss it on `assistant` rows.**
- **`uuid`** — this record's own id; **`parentUuid`** — the immediately preceding
  record in the same chain (linked-list structure, not a flat log). `promptId` groups
  all records belonging to one user turn.
- **Timestamps** — ISO-8601 UTC (`Z` suffix), field name `timestamp`, present on
  essentially every type that isn't a pure per-session-singleton marker.

### Consumers (measured by grep, `scripts/` + `.claude/` + `skills/`)

| Field / concept | Files that read it (non-exhaustive, `.pyc` excluded) |
|---|---|
| `isMeta` | `scripts/extract_claude_code_sessions.py`, `scripts/audit/scan_midturn_messages.py`, plus others matched by `.pyc` cache only (source not re-verified) |
| `origin.kind` / `hookEvent` / `isSidechain` / `agentId` / `toolUseResult` / `isCompactSummary` / `promptSource` / `attributionSkill` / `stop_hook_summary` | `scripts/audit/heartbeat_battery.py`, `turn_boundary_executor.py`, `turn_index.py`, `turn_cost_report.py`, `agent_end_ingest.py`, `token_spend.py`, `route_agent_return.py`, `jon_says.py`, `session_finalise.py`, `jon_utterances.py`, `token_ledger.py`, `drain_routing_ledger.py`, `cc_corpus_gap.py`, `scripts/extract_jsonl_metadata.py`, `scripts/extract_claude_code_sessions.py` |
| `sessionId` / `session_id` | `scripts/extract_claude_code_sessions.py`, `route_agent_return.py`, `session_finalise.py`, `i2_session_page.py`, `token_ledger.py`, `session_clock.py`, `scripts/reconstruct_session.py`, `cc_corpus_gap.py`, `scripts/extract_live_session.py`, `scripts/lanes/nightly_corpus_delta.py` |

**UNCONSUMED, measured by absence from the same grep sweep:** `caller.type` on
`tool_use` blocks, `bridge-session`/`atis-latch`/`custom-title`/`agent-name` record
types, and the `queue-operation` `operation` field value space — none matched in
`scripts/`, `skills/`, or `.claude/agents/`. These are recorded here because they
exist on disk, not because anything reads them; if that changes, update this row.

### Drift risk

**HIGH.** No published spec; the harness team can add, rename, or restructure any
field on any release with no changelog this repo tracks. The `sessionId`/`session_id`
inconsistency above is itself evidence the shape is not internally disciplined.
Section 3 exists specifically to catch this without relying on a human noticing.

---

## Section 2 — claude.ai export JSON

**Location:** `raw/Anthropic_zips/*.zip` → `extracted-<epoch>/conversations.json`
(one JSON array of conversation objects; sibling files `users.json`, `projects/`,
`memories.json`, `login_history.json` in the same extraction — not probed here).

**Measured against:** the newest extraction, `extracted-1786933322/conversations.json`
(86 MB, 249 conversations).

### Conversation object shape

```
conversation keys: account, chat_messages, created_at, name, summary, updated_at, uuid
```
Sampled conversation's first message set: 8 `chat_messages`.

### `chat_messages[]` shape

```
message keys: attachments, content, created_at, files, parent_message_uuid, sender, text, updated_at, uuid
```
`content` is a list of typed blocks (see below). `text` is a flattened top-level
convenience string (convert-export.py warns, in its own source comment at line 54,
that some legacy renderers read ONLY `block['text']` and drop everything else — a
named historical loss mode, not this page's invention).

### `content[]` block types (measured)

| block `type` | shape notes (measured) |
|---|---|
| `text` | `start_timestamp, stop_timestamp, flags, type, text, citations` |
| `thinking` | `thinking` (readable string, pre-boundary) OR empty + `thinking_hidden: true` (post-boundary — see version-boundary note); ALSO carries `summaries` (list of `{"summary": "..."}`), `cut_off`, `truncated`, `hidden`, `alternative_display_type`, `signature` |
| `tool_use` | `id, name, input` (structured, tool-specific — e.g. `ask_user_input_v0`'s `input.questions[]`) |
| `tool_result` | `tool_use_id, name, content[], is_error, structured_content, message, integration_name, mcp_server_url, integration_icon_url, icon_name, display_content` |
| `flag` | `flag` (e.g. `"election"`), `helpline: {id, name, phone_number, sms_number, web_chat_url, url}` — a UI-surfaced crisis/civic-resource flag, not a content block in the ordinary sense |
| `token_budget` | `remaining` (observed `null` in this sample — not populated in this export) |

### `attachments[]` vs `files[]` — the measured 46/250 split

Per `CLAUDE.md` ("Transcript Corpus (mirror corpus)" / the 2026-08-17 correction),
measured against the 08-16 export and re-confirmed structurally here against
extracted-1786933322:

| class | count (08-16 export) | fields (measured, this export) |
|---|---|---|
| `attachments[]` | 46 | `file_name, file_size, file_type, extracted_content` — **content IS present**, pulled at upload time |
| `files[]` | 250 | `file_uuid, file_name` **ONLY** — no content field exists in the object at all |

Measured `files[]` entry (redacted):
```json
{"file_uuid": "019dad2a-d233-755e-9219-6951930df50a", "file_name": "SPC Bap..."}
```
Measured `attachments[]` entry (redacted):
```json
{"file_name": "CLAUDE.md", "file_size": 10409, "file_type": "", "extracted_content": "..."}
```

### What `convert-export.py` consumes (read from source, `skills/chat-exporter/scripts/convert-export.py`)

Confirmed by direct grep of the script's own field accesses:
- Thinking blocks: `block.get('thinking')`, `block.get('summaries')`, `block.get('signature')` — `thinking_fidelity()` derives RAW vs SUMMARY vs HIDDEN from exactly these three.
- Tool blocks: `block.get('name')`, `block.get('input')`, nested `tool_result` content text via `nb.get('text')`.
- Attachments: `a.get('file_name')`, `a.get('file_size')`, `a.get('file_type')`, `a.get('extracted_content', '')` — **all four**, matching the "content IS present" row above.
- Files: `f.get('file_name')`, `f.get('file_uuid')` — **only these two fields are ever read**, structurally confirming files[] content is never extracted because there is nothing to extract.
- Citations: `c.get('start_index')`, `c.get('end_index')`, `c.get('uuid')`, `c.get('details')`.
- Threading: `parent_message_uuid` used to build a sibling map for branch reconstruction.

### Thinking-block presence and the version boundary

**Boundary is a DATE, not a version number**, and lives on
[`wiki/references/agent-memory/cc-jsonl-thinking-signature-only.md`](agent-memory/cc-jsonl-thinking-signature-only.md)
(cited here per the task's instruction to find and cite it, not restated in full):

- **CC `.jsonl` (harness v2.1.72+):** thinking is `{type:"thinking", thinking:"", signature:"<encrypted>"}` — discarded before write, never client-recoverable. Pre-boundary CC files (e.g. `1e609faf`, 2026-04-26) carry plaintext `thinking`.
- **claude.ai export:** readable summarized thinking through ~2026-07-23, then `thinking_hidden: true` signature-only from ~2026-07-24 for fable-5/opus-5 (per-block stamp at generation time, not retroactive — pre-boundary blocks in the SAME export stay readable). `summaries[]` remains present even when hidden, so THINKING-SUMMARY-grade capture survives the boundary; full RAW does not.

### Loss classes (export → wiki, table form)

| Loss class | What's lost | Measured / cited evidence |
|---|---|---|
| `files[]` content | 250 of 296 file references (08-16 export) have no content field at all — only `file_uuid`+`file_name` | `CLAUDE.md` 46/250 table; structurally re-confirmed above via `convert-export.py`'s own field reads |
| AskUserQuestion selections | Jon's UI selections through `ask_user_input_v0`-style widgets are not captured as his answer — only the assistant's restatement survives | `wiki/references/agent-memory/askuserquestion-answers-not-captured.md` |
| Deleted conversations | Export contains only conversations that existed at export time; anything deleted before export is gone from this channel entirely | CLAUDE.md "Lossy; wiki wins" — exports "drop deleted conversations / project structure" |
| Thinking = summaries (post-boundary) | From ~2026-07-24, `thinking` block text is not full reasoning even when present — it's the UI-displayed summary, double-discounted per the provenance-grade table (`[THINKING-SUMMARY:date]` < `[TRANSCRIPT:date]`) | `cc-jsonl-thinking-signature-only.md` 2026-07-28 correction |

### Consumer / drift risk

**Sole documented consumer:** `skills/chat-exporter/scripts/convert-export.py`
(wrapped by the `chat-exporter` and `transcript-parser` skills). No other script in
`scripts/` was found reading `conversations.json` directly in this probe. **Drift
risk MODERATE-HIGH**: Anthropic controls the export format unilaterally; the
46/250 split itself was discovered only because Jon's own words ("anthropic zips
don't include attachments") contradicted the prior table and forced re-measurement —
i.e., this schema has already drifted once, silently, before being caught.

---

## Section 3 — drift detection

**Instrument:** `scripts/audit/check_source_schema_drift.py`. Parses the newest CC
session JSONL under a given `--projects-root`, and diffs the observed
`type` → field-set map against `DOCUMENTED_FIELDS`/`DOCUMENTED_TYPES` in that script
(hand-synced against Section 1's table above — see `SCHEMA_UPDATED_WITH` in the
script). Never crashes on an unrecognized shape: a new record type or a documented
field gone missing is a **WARN naming the delta**, never a hard failure. An
unrecognized *extra* field on a known type is NOT a WARN — the documented sets are a
floor, not a ceiling, so the probe cannot be defeated by the harness team simply
adding fields.

Wired for the heartbeat battery / probe registry per `skills/probe-registry`: run it
at barriers (close / compact / ship-to-Jon), not on a timer.

```
python scripts/audit/check_source_schema_drift.py --as-of <ISO-8601> [--projects-root <dir>] [--strict]
python scripts/audit/check_source_schema_drift.py --selftest
```

### Selftest run (2026-08-22)

Synthetic 3-record JSONL: one normal `user` record, one `system` record with its
documented `subtype` field deliberately dropped, and one never-seen `type` value
(`quantum-flux-event`). Result:

```
=== selftest: novel type + missing field must both WARN ===
[ 1] PASS    file-found                   <tmpfile>.jsonl
[ 2] INFO    lines-parsed                 3 lines, 0 failed JSON parse
[ 3] INFO    harness-version              9.9.999
[ 4] WARN    new-record-types             undocumented type(s) seen: ['quantum-flux-event'] -- add to source-schemas.md Section 1
[ 5] WARN    missing-documented-fields    system: missing ['subtype']
SELFTEST PASS: both injected drift cases produced WARN as required.
```
Exit 0. Both injected drift cases produced the required WARN.

### Real run (2026-08-22, `--as-of 2026-08-22T21:00:00-05:00`)

```
[ 1] PASS    file-found                   ...\643640a7-f68a-4ed3-ba42-7dbaaaeb7b32.jsonl
[ 2] INFO    lines-parsed                 21530 lines, 0 failed JSON parse
[ 3] INFO    harness-version              2.1.226, 2.1.233, 2.1.239, 2.1.241
[ 4] PASS    new-record-types             all 16 observed types are documented
[ 5] PASS    missing-documented-fields    every documented field present on every type it was checked against

summary: 5 checks, 0 WARN, 0 UNKNOWN
```
The live CFL session file matches Section 1's documented shape exactly as of this
measurement. Exit 0.

**No equivalent drift probe exists yet for Section 2 (the claude.ai export).** That
format changes on Anthropic's schedule, not a per-session basis, so a per-run probe is
lower-value than a per-EXPORT check; building one is future work, named here so its
absence is a stated bound rather than a silent gap.

---

## Bounds — what this page could NOT measure

- **`toolUseResult` shape per tool** — only Bash/PowerShell's `{stdout, stderr,
  interrupted, isImage}` shape was probed. Other tools (Read, Edit, WebFetch, MCP
  tools) almost certainly have distinct `toolUseResult` shapes; not enumerated here.
- **`caller.type` value space on `tool_use`** — only `"direct"` was observed in this
  probe; whether a value like `"subagent"` or similar exists was not confirmed.
- **`queue-operation.operation` value space** — field exists, no instance content was
  inspected beyond its presence.
  **`system.subtype` full enumeration** — only `stop_hook_summary` was pulled in
  detail; the 789 `system` records almost certainly span several distinct subtypes.
- **Section 2, message-attachment `extracted_content` size/format limits** — not
  probed (e.g. whether large attachments are truncated).
- **Section 2, `flag`/`token_budget` block prevalence** — observed as block TYPES
  that exist; frequency and full field enumeration not measured.
- **No drift probe for Section 2** — see Section 3 note above; this is a named gap,
  not an oversight.
- **Consumer sweep for Section 1 fields used `grep -rl` over `scripts/`, `skills/`,
  `.claude/` only** — `.claude/worktrees/` (active worktree copies) and any
  out-of-repo automation were not swept; a consumer could exist there unseen.
