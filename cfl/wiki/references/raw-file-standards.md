---
title: Raw File Standards for Agent Deposits
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 4 vs fleet 3 on authored labels"
type: governance
created: 2026-05-07
author: wiki-governance-agent
status: authoritative
---

# Raw File Standards for Agent Deposits

This document governs how non-wiki-master agents write files into the `raw/` directory. It is not a wiki-master operating manual. It is what every other agent must know before touching `raw/`.

Read this once. Know exactly what to do.

---

## 1. Raw File Naming Rules

### Sessions: the Option D schema

All raw session files use this pattern:

```
raw/transcripts/{claude-ai,claude-code,external}/[project]/[session-name]/[topic]-YYYY-MM-DD-uuid6.md
```

(Moved from `raw/sessions/[project]/...` in the 2026-07-28 L1 move — see
`.claude/agents/fable-mirror.md:25-26`. `raw/sessions/` now holds only a `POINTER.md`.)

**Component breakdown:**

| Component | Rule | Example |
|-----------|------|---------|
| `[project]` | Subdirectory: `fl/`, `personal/`, or `pro/` | `fl/` |
| `[session-name]` | One directory per logical session, slugified title (lowercase, hyphens, no spaces) | `wiki-init-april-30/` |
| `[topic]` | What this file covers within the session, descriptive slug | `skill-extension` |
| `YYYY-MM-DD` | Date the conversation occurred (not extraction date) | `2026-04-30` |
| `uuid6` | First 6 characters of the chat's UUID, or a random 6-char hex if no UUID exists | `bcafba` |

**Full example:** `raw/transcripts/claude-ai/fl/wiki-init-april-30/skill-extension-2026-04-30-bcafba.md`

**Legacy names** (flat files that lived in `raw/sessions/` root, like `chat-2026-04-30-bcafba-skills-master.md` and `session-*.md`) predate this schema. Do not extend them. New deposits use Option D under `raw/transcripts/`. Do not rename legacy files — wiki-master tracks them as-is.

### Other raw/ subdirectories

| Directory | Contents | Naming convention |
|-----------|----------|-------------------|
| `raw/fbc/` | FBC test runs and research | `test-run-NNN-[descriptor].md` or `[descriptor]-YYYY-MM-DD.md` |
| `raw/general/` | General reference material not tied to a session | Descriptive slug, no UUID required |
| `raw/references/` | External reference documents — immutable once written | Descriptive slug; do not add dates unless multiple versions will exist |
| `raw/transcripts/` | Conversation exports organized by venue/project (see above) | Option D schema |

**`raw/references/` is immutable.** Write here only for documents that are stable reference material (e.g., the Karpathy LLM Wiki pattern). Do not write session exports here.

---

## 2. Required Frontmatter

Every raw file written by an agent must open with a YAML frontmatter block. Missing or malformed frontmatter causes wiki-master's ingest to fail or produce unreliable source pages.

```yaml
---
chat_id: [UUID of the source conversation, or omit if no UUID exists]
source_id: [alternative identifier if no chat_id — e.g., "test-run-001" or "karpathy-llm-wiki"]
title: [Human-readable title matching the session or document]
date: [YYYY-MM-DD — date of the conversation or document, not extraction date]
extraction_date: [YYYY-MM-DD — when this file was written]
source_type: [session | summary | test-run | reference | note]
extraction_mode: [native-json-export | dom-incremental | dom-bulk | manual | reconstructed | jsonl-convert]
extraction_completeness: [FULL | FULL — thinking omitted | FULL (visible) — thinking encrypted, not recoverable | PARTIAL — tail only | PARTIAL — summary only | SUMMARY]
thinking_blocks: [preserved | omitted (N blocks) | encrypted-in-signature (N blocks) | none | referenced — see [filename]]
char_count: [integer, approximate — omit if unknown]
project: [fl | personal | pro | fbc | general]
---
```

**Field rules:**

- `chat_id` and `source_id` are mutually exclusive options. Use `chat_id` for claude.ai exports. Use `source_id` for anything else.
- `date` is the conversation date, not the extraction date. Both matter and both must be present.
- `extraction_completeness` must be honest. See the completeness taxonomy below.
- `source_type: summary` means this file is a human-readable summary or reconstruction, not a verbatim transcript. Wiki-master treats claims from summary files as lower-confidence than claims from session files.
- `thinking_blocks` is required whenever the source conversation may have contained extended thinking. Values by source (updated 2026-07-12):
  - **claude.ai exports** (`convert-export.py`): thinking is **preserved by default** → `preserved`; `--no-thinking` gives `omitted (N blocks)`; `none` if the session had no thinking.
  - **Claude Code `.jsonl`** (`convert-claude-code.py`): thinking is `encrypted-in-signature (N blocks)` — present but NOT client-recoverable (see below); `none` if absent. The reasoning is not "unavailable" — it is encrypted in the block's `signature` (server-decryptable for `--resume`), with no supported plaintext path (anthropics/claude-code #32810/#31143).
  - `referenced — see [filename]` if a separate thinking file exists.
- `char_count` helps wiki-master calibrate ingest strategy for large files. Provide it when the chat-exporter reports it. Omit rather than guess.
- `project` is the coarse category, independent of the directory placement. Used for filtering and cross-referencing.

**Completeness taxonomy:**

| Value | Meaning |
|-------|---------|
| `FULL` | Every word visible to a human during the conversation is present in this file verbatim. Tool calls and results are represented (may be summarized — see format contract). No content was dropped. |
| `FULL — thinking omitted` | All human-visible text turns are present verbatim, but thinking blocks (extended reasoning Claude generated but did not show to Jon) were not captured. This is the standard output of convert-export.py until thinking capture is added. |
| `PARTIAL — tail only` | Virtual DOM constraint — only the end of the session was captured. Content before the extraction window is absent. |
| `PARTIAL — summary only` | The session existed but only a summary (from recent_chats API or manual reconstruction) was available. No verbatim turns. |
| `SUMMARY` | This file is intentionally a summary, not an extraction attempt. Claude Code sessions that cannot be DOM-extracted use this type. |

**Optional fields that add value:**

```yaml
url: [full claude.ai URL if available]
condition: [for FBC test runs — experimental condition description]
battery: [for test batteries — battery identifier]
role: [for role sessions — role name, e.g., "Skills Master"]
verbatim_file: [filename of the verbatim session file, if this is a summary paired with one]
summary_of: [filename of the summary file, if this verbatim file has a paired summary]
notes: [anything wiki-master needs to know before ingesting]
```

---

## 3. Directory Placement Rules

### Which project subdirectory?

| If the session is about... | Use |
|---------------------------|-----|
| Claude foundational layer work — skills, wiki, FBC protocol, project architecture | `raw/transcripts/claude-ai/fl/` |
| Jon's personal life, health, family, finances — no professional content | `raw/transcripts/claude-ai/personal/` |
| Jon's actuarial job, work projects, work context | `raw/transcripts/claude-ai/pro/` |

**When uncertain:** Default to `fl/`. The foundational layer is the catch-all for anything that touches Claude infrastructure, tool development, or project work. Personal and pro are opt-in categories for content that clearly does not belong in the FL wiki.

**`personal/` and `pro/` are NOT ingested into the FL wiki by default.** Wiki-master skips them unless Jon explicitly flags a file for ingest with `ingest_flag: true` in frontmatter. Never move a file from `personal/` or `pro/` to `fl/` without Jon's direction.

### FBC material

FBC test runs go to `raw/fbc/`, not `raw/sessions/`. FBC research notes or planning documents also go to `raw/fbc/`. If a session happens to contain FBC material alongside other topics, the session goes to `raw/transcripts/claude-ai/fl/` and the FBC content is extracted during ingest — do not split the file.

---

## 4. Format Contract

Wiki-master parses raw session files expecting a consistent body structure. Deviations force manual recovery.

### The verbatim requirement

**Everything a human could have seen during the conversation must appear in the file, verbatim.** This is not optional. If verbatim content is unavailable, the file is PARTIAL or SUMMARY — not FULL. Paraphrase is never a substitute for verbatim in a file claiming FULL completeness.

**Tool calls and results** are an exception: `convert-export.py` summarizes them (e.g., `[tool_use: Read — file_path: /foo/bar.md]`). This is acceptable — the tool interaction details are not meaningful conversation content. The tool summaries must still be present; silent omission is not acceptable.

**Thinking blocks** (extended reasoning that Claude generated internally but did not surface to Jon) occupy a separate status. Jon may not have seen them in the UI, but they are part of the record. The standard:
- If thinking blocks can be captured, include them inline or in a separate file.
- If captured in a separate file: set `thinking_blocks: referenced — see [filename]` in frontmatter and include a `## Thinking Blocks` section at the end of the main file with a link to the thinking file.
- If thinking blocks were dropped by the extraction tool (current behavior of convert-export.py): set `thinking_blocks: omitted` and `extraction_completeness: FULL — thinking omitted`. Do not claim plain `FULL`.
- Never silently drop thinking blocks without noting it in frontmatter.

### Verbatim session file (source_type: session)

Produced by `convert-export.py` from the Anthropic native JSON export. This is the primary and preferred file type.

```markdown
[frontmatter block]

# [Title matching frontmatter title field]

## Summary

[2-5 sentences. What happened. Key outcomes. Wiki-master reads this first.]

## Human

[Verbatim text of the human turn]

---

## Assistant

[Verbatim text of the assistant turn]

---

## Human

[Continue alternating — separator between every turn]

---
*Extraction note: FULL — thinking omitted — complete session captured via native JSON export. Thinking blocks not available in this export.*
```

### Summary file (source_type: summary)

Used when verbatim is unavailable: DOM-truncated sessions, Claude Code sessions (no chat export path), or sessions where only the `recent_chats` API summary was available.

```markdown
[frontmatter with source_type: summary and correct extraction_completeness]

# [Title] — Summary

## What This Is

[One sentence: why this is a summary, not a verbatim transcript.]

## What Happened

[Structured narrative of the session. Decisions, outcomes, open items generated. Not a transcript — a reconstruction.]

## Key Exchanges (if reconstructable)

[If specific exchanges are known well enough to paraphrase reliably, document them here.
 Mark clearly as paraphrase: *[paraphrase — not verbatim]*]

---
*Extraction note: SUMMARY — [reason verbatim was unavailable]. Claims from this file are lower-confidence than verbatim session files.*
```

### When both files exist for the same session

This is the correct state when: (a) a verbatim native JSON export is produced, AND (b) a DOM export or manual summary was previously written. Both files coexist in the session directory. Link them via frontmatter:

- Verbatim file: `summary_of: [summary-filename]`
- Summary file: `verbatim_file: [verbatim-filename]`

**Wiki-master prefers the verbatim file for ingest.** The summary file may be ingested only for content not captured in the verbatim file (e.g., context from before the export period). Wiki-master must note in the source page which file was used.

### Format rules

- Turn headers: `## Human` and `## Assistant` exactly. Not `### Human`, not `**Human:**`, not any other variant.
- Separator between turns: `---` (horizontal rule). Required. Makes turn boundaries unambiguous.
- FBC branches within an assistant turn: existing `[B1]`, `[B2]` notation. No change.
- `## Summary` section: required in all file types. It is wiki-master's entry point.
- Footer extraction note: required. Last line of the file. States completeness and caveats.
- For non-session files (test runs, reference docs): `## Human` / `## Assistant` do not apply. Frontmatter and `## Summary` are still required.

### Claude Code session files

Claude Code sessions cannot be exported via convert-export.py or DOM extraction. Write a manual summary file:

Location: `raw/transcripts/claude-ai/fl/[session-name]/summary-YYYY-MM-DD-cc.md` (cc = Claude Code, no UUID)

Set `source_type: summary`, `extraction_mode: manual`, `extraction_completeness: SUMMARY`.

Document: goals stated at open, key decisions made, deliverables built, open items generated, state at close.

---

## 5. What Wiki-Master Needs to Do Its Job

### The extraction pipeline

The primary extraction tool is `skills/chat-exporter/scripts/convert-export.py`. It reads Anthropic's native JSON export (`conversations.json`) and produces verbatim `## Human` / `## Assistant` turn files at full fidelity. As of 2026-07-12 it **preserves extended thinking by default** (readable summarized thinking, emitted as `<details>` labeled with the export's own `summaries` header) — `thinking_blocks: preserved`, `extraction_completeness: FULL`. Pass `--no-thinking` to omit (→ `thinking_blocks: omitted (N blocks)`, `FULL — thinking omitted`). Thinking is citable as `[slug:Tn.thinking]` (claude.ai sources only — CC thinking is encrypted, see below).

The DOM-based browser extraction path (chat-exporter SKILL.md, incremental/bulk modes) is subject to the virtual DOM truncation constraint — long sessions will be PARTIAL. It is the fallback for sessions not in a Anthropic data export.

**Claude Code sessions** are discovered + extracted by `scripts/extract_claude_code_sessions.py` (a discovery/orchestration layer over `skills/chat-exporter/scripts/convert-claude-code.py`, the single canonical CC converter as of Phase A inc.2, 2026-07-12). It scans ALL CFL project dirs (renamed + worktrees) under `~/.claude/projects/` and supports `--list` (discovery), `--update` (re-extract grown/changed sessions), and `--dry-run`. Fidelity notes: (1) only plain-string user messages are captured as Human turns — tool result messages (which share the `user` role in the API) are excluded; tool calls/results are summarized (not dropped); (2) thinking is **encrypted-in-signature** — present in the `.jsonl` only as an encrypted `signature` (server-decryptable for `--resume`, NOT client-recoverable; no supported plaintext path). Set `extraction_mode: jsonl-convert`, `thinking_blocks: encrypted-in-signature (N blocks)` (or `none`), `extraction_completeness: FULL (visible) — thinking encrypted, not recoverable`. A `## Summary` placeholder is scaffolded automatically — fill it in before submitting for ingest.

**Extraction mode definitions:**

| Mode | Source | Fidelity |
|------|--------|----------|
| `native-json-export` | Anthropic data export (`conversations.json`) | Highest — verbatim turns |
| `dom-incremental` | Browser DOM, captured incrementally | High if session fits in DOM window |
| `dom-bulk` | Browser DOM, captured in bulk | Same as incremental |
| `jsonl-convert` | Claude Code `.jsonl` session file | High for human turns and assistant text; tool calls/results summarized; thinking encrypted-in-signature (not client-recoverable) |
| `manual` | Manually written reconstruction | Lower — paraphrase or summary |
| `reconstructed` | Reconstructed from partial evidence | Lowest — treat as summary |

**Wiki-master's ingest preference:** verbatim native JSON export file > jsonl-convert > DOM full extraction > DOM partial > manual > summary. When multiple files exist for the same session, use the highest-fidelity file and note the others.

### What breaks when standards are violated

| What's missing or wrong | What breaks |
|------------------------|-------------|
| No frontmatter | Ingest has no metadata to write into the source page. wiki-master must guess or halt. |
| `extraction_completeness` missing or dishonest | Wiki-master cannot weight claims appropriately. PARTIAL content ingested as FULL produces overconfident source pages. Conflicts may be introduced without flagging. |
| `source_type` missing | Wiki-master cannot distinguish verbatim session files from summaries. Summary-derived claims get treated as ground truth. |
| `thinking_blocks` not set when thinking may have occurred | Thinking content is silently absent from the record. No flag, no reference, no recovery path. |
| Paraphrase in a file marked FULL | Ingest produces claims that are the agent's reconstruction, not Jon's or Claude's actual words. These can contradict later verbatim evidence without the conflict being detectable. |
| `date` is the extraction date, not conversation date | Timeline reconstruction in `wiki/sessions/index.md` is wrong. |
| No `## Summary` section | Wiki-master has no entry point. Must read the entire file before deciding scope. Costly on 101K-char files. |
| Inconsistent or missing turn headers | Turn boundaries are ambiguous. Human vs. assistant attribution is unreliable. |
| Missing `---` separators between turns | Same as above — compound turns blur together. |
| File placed in wrong subdirectory | FL wiki ingests personal or pro content it should not have. Or FL content is skipped because it landed in `personal/`. |
| No extraction note footer | Ingest quality is unknown without reading the full file. |
| `chat_id` missing for a claude.ai export | Cannot deduplicate when the same session is exported multiple times (common — see triage session in legacy files). |
| Both verbatim and summary file exist but not cross-linked | Wiki-master may ingest both, producing duplicate claims or conflicting source pages for the same session. |

**The single most important field is `extraction_completeness`.** Wiki-master's conflict rule ("never silently overwrite") depends on knowing whether a claim comes from verbatim transcript or a summary approximation. Get this wrong and the conflict detection system has no foundation.

---

## 6. Recommendation: Should Non-Wiki-Master Agents Write Directly to Wiki?

**No. Non-wiki-master agents must not write directly to `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, or any other wiki subdirectory.**

Reasoning:

**The wiki is a compounding artifact.** Every page cross-references others. Writing a source page without updating relevant concept pages, updating the index, and appending to the log produces a fractured wiki — pages that exist but are not linked, claims that exist but are not synthesized. The value of this system comes from the integration step, not the deposit step.

**Conflict detection requires full wiki context.** Wiki-master reads `wiki/index.md` before any ingest to understand what already exists. An agent writing a single page in isolation cannot perform this check reliably. The result is silent duplication or silent contradiction — exactly what the conflict rule exists to prevent.

**Coordination is not optional at this scale.** The wiki is small now (sources/ and concepts/ are empty at init as of 2026-04-30). The discipline must be established before the wiki grows, not after. Allowing ad-hoc writes now creates a recovery problem later.

**The correct flow for non-wiki-master agents:**

1. Write the raw file to the appropriate `raw/` subdirectory following these standards.
2. Stop. Do not touch `wiki/`.
3. Wiki-master runs ingest explicitly when Jon directs it.

**One exception:** A non-wiki-master agent may write to `wiki/tracker/open-items.md` if it discovers a time-sensitive open item and Jon is not present to direct wiki-master. The item must be formatted exactly per the open-items format in SKILL.md, and the agent must note in the item that it was written by a non-wiki-master agent. The agent must not increment OI numbering blindly — read the file first and use the next available number.

This recommendation is offered for Jon's review. The exception clause is the judgment call with the highest uncertainty — Jon may prefer that all tracker writes also go through wiki-master.
