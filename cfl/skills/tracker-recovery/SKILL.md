---
name: tracker-recovery
description: Phase 1 of formal wiki ingest. Extracts proposed skills, open items, and triage items from raw session files. Verifies coverage before and after writing. Requires Jon approval before any writes.
---

# Tracker Recovery

You are executing a structured extraction pass over raw session files. You do not ingest into wiki/sources/ — that is Phase 2. Your job is the tracker: skills.md, open-items.md, triage.md.

Read `wiki/SCHEMA.md` before starting. Read all three tracker files before reading any session file.

---

## Core Loop (runs once per session file)

### Step 1 — Pre-state expectations

Before reading the file, state what you expect to find based on session metadata (title, notes, role):

```
Pre-reading [filename]:
- Expected proposed skills: [list or "uncertain"]
- Expected open items: [list or "uncertain"]
- Expected triage items: [list or "uncertain"]
- Expected skill improvements: [list or "uncertain"]
```

This is a commitment. You will check against it after extraction.

---

### Step 2 — Full file read (mandatory)

Before extracting, confirm you have read the entire file.

1. Read the file with no line limit. Note the total line count returned.
2. If the response was truncated (line count seems low relative to file size, or content ends abruptly), read remaining lines using the `offset` parameter until you have reached the end.
3. State explicitly before proceeding:

```
File: [filename]
Total lines read: [N]
Read complete: yes / no (if no — state what's missing and stop)
```

Do not proceed to extraction if read is incomplete. Flag the gap and stop.

---

### Step 3 — Extract candidates

Read the file. For each candidate item found, classify into one of four categories:

**A — Proposed new skill:** A skill that was explicitly proposed or discussed as something to build. Must have a name or clear description of what it would do.

**B — Skill improvement:** An improvement to an existing skill that was explicitly proposed or accepted. Reference which skill.

**C — Open item:** Something requiring follow-up action that does not yet have a home in open-items.md. Must have a stated or implied blocking condition.

**D — Triage item:** Something explicitly parked — "we'll look at this later" or similar. Not an active item, not being built. Has a label and a condition for return.

**Strict filter:** Only items matching A/B/C/D above. If an item is ambiguous — could be A or C, or you're not sure it's really a proposal — classify it as **E — Lost** and note what's uncertain. Do not force a category.

---

### Step 4 — Dedup check

Before reporting, compare each candidate against existing tracker entries:

- Read `wiki/tracker/skills.md` (current skills + proposed)
- Read `wiki/tracker/open-items.md` (OI-001 through latest)
- Read `wiki/tracker/triage.md` (T-001 through latest)

For each candidate, state one of:
- **New** — not in tracker
- **Duplicate** — matches existing entry [reference OI-NNN or T-NNN]
- **Paraphrase** — appears to be same as [OI-NNN or T-NNN] but phrasing differs — flag for Jon

---

### Step 5 — Report and await approval

Present the full candidate list with classifications and dedup results. Do not write anything yet.

Format:
```
## [filename] — Extraction Report

### Read confirmation
- File: [filename]
- Total lines read: [N]
- Read complete: yes / no

### Pre-state expectations
- Proposed skills: [list]
- Skill improvements: [list]
- Open items: [list]
- Triage items: [list]

### Candidates
| # | Category | Item | Dedup | Notes |
|---|----------|------|-------|-------|
| 1 | A — Proposed skill | [name]: [purpose] | New | [source quote or context] |
| 2 | B — Skill improvement | FBC: [improvement] | New | Accepted in session |
| 3 | C — Open item | [item] — blocking: [condition] | Duplicate of OI-003 | |
| 4 | E — Lost | [description] | — | Ambiguous: could be A or C |

### Pre-state check
- Proposed skills: expected [X] | found [Y] | gap: [yes/no]
- Skill improvements: expected [X] | found [Y] | gap: [yes/no]
- Open items: expected [X] | found [Y] | gap: [yes/no]
- Triage items: expected [X] | found [Y] | gap: [yes/no]

### Gaps flagged
[Any case where post-extraction count is less than pre-stated expectation, or where you suspect something is there but couldn't classify it]

Proceed? (approve all / approve partial [list #s] / revise)
```

Wait for Jon's response before writing.

---

### Step 6 — Write approved items

For each approved item:

**A — Proposed new skill** → append to **Proposed New Skills** section of `wiki/tracker/skills.md`:
```
### [Skill Name] (proposed)
**Need it addresses:** [description]
**Priority:** [high | medium | low — infer from session context]
**Status:** idea
**Prompted by:** [session slug]
```

**B — Skill improvement** → append to **Pending improvements** under the relevant skill in `wiki/tracker/skills.md`:
```
- [YYYY-MM-DD] [Improvement description] — prompted by: [session slug]
```

**C — Open item** → append to `wiki/tracker/open-items.md` with next OI-NNN:
```
## OI-NNN | [YYYY-MM-DD] | [Item Title]

**What:** [description]
**Context:** [source and why it's open]
**Blocking condition:** [what's needed to close it]
**Source:** [session slug]
```

**D — Triage item** → append to `wiki/tracker/triage.md` with next T-NNN:
```
## T-NNN | [YYYY-MM-DD parked] | [Item Title]

**What it is:** [description]
**Context:** [why it was parked]
**What would bring it back:** [condition for re-activation]
**Source:** [session slug]
```

**E — Lost** → append to `wiki/tracker/lost.md`:
```
## L-NNN | [YYYY-MM-DD found] | [Item Description]

**What's known:** [description, however incomplete]
**Why uncertain:** [what makes categorization unclear]
**Source:** [session slug]
```

---

### Step 7 — Post-verify coverage

After writing, state 3 specific testable facts from the source that should now be findable in the tracker. For each:

```
Fact: [specific claim from session]
Where captured: [tracker file + entry ID]
Verified: yes / no / partial
```

If any fact is "no" or "partial" — flag as a coverage gap. Do not go back and add silently; surface it for Jon.

---

### Step 8 — Commit

```
git add -A && git commit -m "tracker-recovery: [session-slug]"
```

Then move to next file.

---

## Operations

### run-phase-1

Runs the core loop on all 5 Phase 1 priority files in order:

1. `raw/transcripts/claude-ai/fl/skills-master/skills-master-2026-05-01-bcafba.md` (was raw/sessions/session-skills-master.md, same chat_id bcafbad5, renamed in the 2026-05 sessions/ standardization)
2. `raw/transcripts/claude-ai/fl/project-manager/project-manager-2026-04-30-f8cc02.md` (was raw/sessions/session-project-manager.md, same chat_id f8cc022a)
3. `raw/transcripts/claude-ai/fl/skill-development-test-master-support/skill-dev-2026-04-18-06af0c.md` (was raw/sessions/session-skill-development.md, same chat_id 06af0ccf)
4. `raw/transcripts/claude-ai/fl/test-master/test-master-2026-04-21-babab4.md` (was raw/sessions/chat-2026-04-21-babab4-test-master.md, same rename)
5. `raw/transcripts/claude-ai/fl/communications-director-asop56/comms-director-2026-04-20-5aa72c.md` (was raw/sessions/chat-2026-04-20-5aa72c-comms-director-asop56.md, same rename)

Run Steps 1–7 for each file before moving to the next. Do not batch multiple files before awaiting approval.

After all 5 files: append summary to `wiki/log.md` with total candidates found, net new written, items sent to lost.md.

---

### extract [filename]

Runs the core loop for a single named file only. Use when running files individually.

---

### verify [session-slug]

Post-hoc coverage check only. Does not extract or write. Reads the session file and existing tracker, then states:

```
Source: [filename]
Test facts (3):
1. [fact] → found in [OI-NNN / skill entry] ✓ / not found ✗
2. [fact] → found in [entry] ✓ / not found ✗
3. [fact] → found in [entry] ✓ / not found ✗

Coverage: [full / partial / gap]
Gaps: [list any facts not found]
```

---

## Test Run Logging

When run in test mode (parallel extraction, no writes), save full agent output to:
```
raw/tracker-recovery/test-run-[NNN]/agent-[N]-[session-slug].md
```

Include in the saved file:
- The full extraction report (Steps 1–5 output)
- Read confirmation (line count, completeness)
- Any reasoning shown during classification or dedup

This is improvement data for the generic harness framework. Do not summarize or clean it up — raw output is the point.

---

## Parallel Extraction Mode

When the orchestrator is running multiple agents in parallel (research-only pass):

- Steps 1–5 only (pre-state → read → extract → dedup → report)
- No writes (Steps 6–8 are skipped)
- No approval gate — return the full report and stop
- The orchestrator consolidates reports across agents, cross-deduplicates, and presents merged candidate list to Jon before any writes happen

In this mode, each agent operates independently against the same tracker baseline. Cross-agent dedup is the orchestrator's responsibility, not each agent's.

---

## What This Skill Does Not Do

- Does not create wiki/sources/ pages — that is Phase 2 (wiki-master: ingest)
- Does not modify actual SKILL.md files — tracker/skills.md is an idea log only
- Does not triage items without Jon confirming the handoff
- Does not write anything before Step 4 approval
- Does not batch approvals across files

---

## After Phase 1 Completes

Close in open-items.md: OI-005, OI-006, OI-007.
Update OI-009 as resolved (confirmed: all files are 1.2–12.9 KB, standard ingest applies).
