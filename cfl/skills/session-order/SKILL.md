---
name: session-order
description: Governs cold session open behavior — reading order, topic check, session map maintenance, and session close ritual. Triggers at every cold session open. Also triggers when Jon sends a multi-topic message, when session direction is unclear, when a topic check is needed, or when session close is signaled.
---

# Session Order Skill

---

## Cold Session Open — Mandatory Reading Order

Read in this order before engaging substantively. Do not skip. Do not reorder.

1. `CLAUDE.md` — who Jon is, how to work with him. **Auto-loaded every session**, so this
   is normally already in context; confirm rather than re-read.
2. `wiki/index.md` — current project state (the cold-open rule in `CLAUDE.md`)
3. `skills/session-order/SKILL.md` — this file
4. `skills/temporal-context/SKILL.md` — timestamp and state context

> **Paths repaired 2026-07-26.** This list previously named `README.md`,
> `WORKING_CONTEXT.md`, `SESSION-ORDER-SKILL.md` and `TEMPORAL-CONTEXT-SKILL.md`. **Only
> `README.md` still existed** — the other three had been renamed into `skills/<name>/SKILL.md`
> long before, and `WORKING_CONTEXT.md` was superseded by `CLAUDE.md`. A cold-open skill whose
> mandatory reading list points at absent files fails silently: the session either burns turns
> hunting for them or skips grounding entirely, and nothing reports either.

**If a mandatory read does not resolve, name it in the first response and continue.** Say which file
is absent and proceed — do not hunt for it, and do not drop grounding silently. **An absent
mandatory read is a reportable fact, not a blocker.** *(Added 2026-08-13. The 2026-07-26 repair
above fixed four dead paths and added no guard, so the next dead path fails the same silent way it
describes. Measured 2026-08-13 in the resident container: `CLAUDE.md` — item 1 of this list — exists
at no depth, and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` means it is not auto-loaded either.)*

### ⭐ Environment resolution — read this list, not the one above, in the resident container

*(Added 2026-08-15 by run 7. The guard above tells you to REPORT an absent mandatory read. It does
not tell you what to read instead, so seven runs each rebuilt this list by hand. `[measured
2026-08-15: 7 of this skill's 18 prescriptive references do not resolve in the container —
`python3 /quarantine/skill_operability_audit.py`]`)*

**First, establish which environment you are in — one command, before the reading order:**

```
test -f /.dockerenv && echo RESIDENT || echo HOST
```

**On the HOST (CFL, Personal, Professional, Herald): use the four-item list above unchanged.**

⛔ **In the RESIDENT container the list above resolves 1 of 4. Use this instead:**

| # | read | why |
|---|---|---|
| 1 | `/launch/FIRST-PROMPT.txt` | the actual instruction you were launched with |
| 2 | `/quarantine/INDEX.md` — **top block only** | reverse-chronological; the current state of prior runs' work |
| 3 | `/quarantine/WAKE-BRIEF-for-the-next-opus.md` | ⚠️ carries its own staleness banner — believe the banner, not the body |
| 4 | `/shelf/START-HERE-INDEXES.md` | the three wiki maps; nothing else points at them |
| 5 | `/wiki-personal/sources/jon-messages/` | ⭐ Jon's own words with line-cites. The 2026-08-10 run called this *"the most valuable thing in the container"* and found it on its second day |
| 6 | ⭐ `~/.claude/projects/-/` | **your own prior sessions — 12 transcripts.** Named in no other document in this container |
| 7 | `python3 /quarantine/frame_coverage.py` | which of Jon's twelve FRAMEs already have output, so you do not redo one |

**Path equivalences, so a dead name resolves instead of stalling a session:**

| the list above says | in the resident container |
|---|---|
| `CLAUDE.md` | ⛔ **absent at every depth**, and auto-memory is disabled. Substitute items 1–2 |
| `wiki/index.md` | `/wiki/index.md` — **present, read-only** |
| `MEMORY.md` · `OPEN.md` | ⛔ absent. Substitute `/quarantine/INDEX.md` and the OPEN rows of `/quarantine/APPLIED.md` |
| `~/.claude/plans/` | ⛔ absent |
| `taxonomy.md` · `wiki/concepts/loop-taxonomy.md` | ⛔ absent from every mount |
| **any write** to `wiki/…` | ⛔ **`/wiki*` are read-only mounts.** Your only write surface is `/quarantine` |

⚠️ **This table is a snapshot and the mounts have changed four times.** Re-run the audit rather than
trusting it: **a path written in a spec must be walkable by hand, and this one was walked on
2026-08-15.**

**Then check:** Did Jon provide a timestamp? If not, flag ESTIMATED per temporal context skill before proceeding.

**Then check:** Did Jon provide a `[work]` tag? If yes, apply work-mode constraints before proceeding.

---

## Conditional Reading — Load Only When Needed

These files are not read on every cold open. Load them only when the session will invoke the relevant capability.

| File | Load when |
|------|-----------|
| `skills/frame-before-commit/references/GROUNDING.md` | FBC protocol will be invoked this session |
| `skills/frame-before-commit/SKILL.md` | FBC protocol will be invoked this session — read after GROUNDING |
| `skills/session-lifecycle/SKILL.md` | Jon says "status", "where are we", "project status", or session re-open is needed |

> **Paths repaired 2026-07-26.** These were `GROUNDING_UPDATED.md`, `FRAME-BEFORE-COMMIT.md`,
> `BACKGROUND.md` and `SESSION-LIFECYCLE-SKILL.md`. **None of the four existed anywhere in the
> repo.** Three resolved to their current `skills/` homes. `BACKGROUND.md` was **dropped, not
> repointed** — no successor file exists and inventing a target would be guessing; domain
> context now lives in the wiki and is reached through `wiki/index.md`.

Loading conditional files when they are not needed creates context overhead with no benefit. Do not load preemptively.

---

## Topic Check — Before Engaging Substantively

After mandatory reads, before responding to anything substantive:

**Can Jon state his topic and current focus in one line?**

If yes — proceed.

If no — do not engage substantively. Redirect:

> "Before we go further — what's the one thing you need from this session?"

If Jon cannot answer, this session opens with a triage pass, not content work. A session without a stated topic is a triage session until a topic is named.

This rule applies at cold open and when a multi-topic message arrives mid-session without a stated priority.

---

## Session Map

Maintain a visible session map whenever the session has more than one active thread. Format:

```
DONE — [closed items]
IN PROGRESS — [active right now]
NEXT — [agreed next steps, this session]
HELD — [parked within this session, will return]
TRIAGE — [handed off, this session's responsibility ends]
```

**Show the map** when Jon sends a multi-topic message, when direction shifts, when a new item is introduced, or when asked.

**Update the map** when any item changes state.

**Do not show the map** when the session has a single clear focus and no competing threads. Map is a tool, not overhead.

---

## HELD vs. Triage — The Critical Distinction

These are not the same. Treating them as the same loses items or creates false closure.

**HELD** — Parked within the current session. Claude retains responsibility. Will return to it before session close. Use for: items that are relevant to today's session but not the current focus, ideas that need to wait for another item to resolve first, things Jon says "not now" to but intends to return to.

**Triage** — Handed off to the triage master. This session's responsibility ends. The item lives in the triage master's context until it comes back with a lane assignment. Use for: ideas that don't belong in this session, items that need a different agent or context, things Jon explicitly says "triage that."

**When unclear:** Default to HELD. HELD is safer than Triage — it keeps the item visible. Triage is a handoff, not a park. Do not triage an item without Jon confirming the handoff.

---

## Multi-Topic Message Rule

When Jon sends a message containing multiple topics or requests:

1. Do not respond to everything at once
2. Identify the most load-bearing topic — the one whose answer unblocks or frames the others
3. State the map: what you see, what you'll address first, what goes to HELD
4. Get confirmation before proceeding if the priority is genuinely unclear
5. Jon controls session order. Claude suggests. They agree before proceeding.

---

## Session Close Ritual

When session close is signaled (Jon says "done", "stopping", "that's it", or signals end of available time):

State open HELD items — name each one explicitly
Flag any items that should move from HELD to Triage — ask Jon to confirm each
Session log export check — default is YES, export this session. State your call explicitly either way:
- EXPORT: "Exporting — [one line reason, e.g. new scripts, decisions made, debugging trail worth preserving]"
- SKIP: "Skipping export — [specific reason, e.g. session was a single lookup with no durable output, content is already in the wiki]"
Do not leave this implicit. A judgment call without a stated reason is not a judgment call. Use the chat-exporter skill for mechanics. This step is upstream of wiki export: raw first, synthesis later.
Wiki export check — did this session produce anything worth persisting to the wiki? Candidates: decisions made, skills updated, findings from FBC runs, architecture choices. If yes, name the items and prompt Jon to export before closing: "These are worth adding to the wiki — do you want to do that now or flag it for next session?"
Flag whether any repo files need updating — skill changes, README drift, instructions drift
Confirm next session's likely starting point if known

Do not close without running this ritual if there are HELD items. If Jon is in a hurry, compress to one message — but do not skip silently.

---

## What Moved Here From README

The following behavioral directives previously implied by README are now governed by this skill:

- Topic/triage rule before engaging substantively
- Session map maintenance
- HELD vs. Triage distinction
- Multi-topic message handling
- Session close ritual

README retains: file list, reading order (pointer to this skill), project scope definition.

---

## What Not To Do

- Do not engage substantively before completing mandatory reads
- Do not load GROUNDING or FBC files unless the protocol will be invoked
- Do not respond to a multi-topic message without a map
- Do not treat HELD and Triage as interchangeable
- Do not close a session with HELD items without naming them
- Do not run the topic check as an interrogation — one clean redirect is sufficient

---

## Open Protocol (CFL Formal — Loop Taxonomy)

For CFL sessions (Claude Code or dedicated master sessions), follow this order after the mandatory reads above:

1. **Temporal context** — confirm timestamp, flag any drift (temporal-context skill)
2. **MEMORY.md + relevant memory files** — read `~/.claude/projects/.../memory/MEMORY.md`; load any memory files flagged as relevant to today's session
3. **Active plan file** — read the current plan file if one exists (check `~/.claude/plans/`)
4. **OPEN.md** — read if it exists in the project root; it captures inter-session open items
5. **FBC trigger inventory** — before any work begins, scan the session topic for questions that smell pre-answered. Flag them: "This question may be pre-answered — I will FBC before committing."

Do not start substantive work until steps 1-5 are complete.

**R1 — Wiki Retrieval Rule:** CLAUDE.md contains a "Wiki — Persistent Knowledge Base" section governing when to query the wiki during a session. `wiki/index.md` is the first-stop for any FL topic lookup. Before answering questions about CFL projects, Jon's preferences, session history, or any `[[slug]]` concept — check the wiki. Origin source: `wiki-multi-master-audit-2026-06-02-dba2c0b`.

**R2 — Canonical-Read Rule (the "B-rule"):** The CFL repo is hosted on Google Drive, so every git worktree is a divergent cold-read mirror. A title/content search that returns multiple byte-identical hits is returning **worktree echoes, not duplicates**. The **canonical copy is the main-checkout copy at `origin/main`** — read consequential state via `git show origin/main:<path>` or `git ls-tree`, never whatever a working-tree file or Drive search happens to serve. **Do not delete the echoes** — they are live worktree files, not duplicates. *(Ratified 2026-07-17, session da51cc. Reference: memory `drive-worktree-mirror-poisoning`.)*

For canonical loop names used in this protocol, see: `wiki/concepts/loop-taxonomy.md`

---

## Post-Compact Recovery (Wake from Nap)

When context compaction has occurred mid-session and you are re-entering a conversation after a gap:

1. Confirm temporal context — how much time has passed? Flag estimated if uncertain.
2. Read the active plan file — what was the session's stated task?
3. Read OPEN.md — what was open when the session started?
4. Read MEMORY.md — restore project state
5. Restate your current position in one paragraph: "Before compaction, we were [X]. The last committed action was [Y]. The next step was [Z]."
6. Check for in-flight agents — are any background agents still running? Flag their status.
7. Then proceed.

Do not assume memory of what was done before compaction. Treat post-compact state as a cold open with prior context summarized.

---

## FBC Trigger Criteria (Formal)

Run FBC before any of the following. Do not skip under time pressure — the trigger is the signal that speed is dangerous here.

**Always trigger:**
- Any design decision (what to build, how to structure, what metric to use)
- Any interpretation of a finding ("what does this mean?")
- Any `skills/intake/` deposit — run FBC on "is this gap real or artifact?" first
- Any Selection Loop briefing to Jon — run FBC on "what is the most useful thing to present?" first

**Trigger when the question smells pre-answered.** Signals:
- You already know what you want to say before the branches run
- The answer feels obvious
- Jon's phrasing implies the answer ("shouldn't we just X?")
- The question is complex but the instinct is simple

**Trigger phrases from Jon:** "what does this mean", "should I redesign", "is this real or artifact", "branch this", "what am I missing", "frame before commit", "run the protocol."

Default: standard FBC (3 branches). Extended mode when the question has multiple legitimate identity frames (see frame-before-commit Extended Mode section).

---

## Session Close — Memory and Ingestion (Addendum)

Additions to the existing close ritual above:

After naming HELD items and before final export check:

1. **Memory update** — for any non-obvious finding, decision, or constraint discovered this session: write or update the relevant memory file in `~/.claude/projects/.../memory/`. Non-obvious = something a future session would not derive from reading the code or git history.

2. **Ingestion loop trigger** — did this session produce anything worth persisting to the wiki? Candidates: confirmed design decisions, FBC findings, skill updates, methodology choices, architectural choices. If yes: name the items and enter the Ingestion Loop (wiki-master) before closing, or flag them explicitly for next session.

3. **LOG.md** — if research work happened (a test ran, a hypothesis was updated, a ratchet iteration completed): append to `wiki/log.md` before closing.

These steps are in addition to, not replacing, the existing close ritual.

> ⛔ **RESIDENT CONTAINER: all three steps above name a destination you cannot write.**
> *(Added 2026-08-15 by run 7. `[measured: /wiki, /wiki-personal, /wiki-professional are read-only
> mounts; `~/.claude/projects/.../memory/` does not exist. 4 of the 5 equipped skills prescribe a
> write to a read-only path — `skill_operability_audit.py` §O9.]`)*
>
> **This is a plumbing gap, not a permission ruling. Jon ruled the permission the other way** —
> *"It CAN re-organize the folders, and it can propose improvements to frontmatter"*
> `[/shelf/jon/JONS-ANSWERS-2026-08-09.md §2]`. **Do not read the read-only mount as a refusal.**
>
> **Substitute, in the resident container:**
>
> | step | write instead to |
> |---|---|
> | 1 · memory update | `/quarantine/INDEX.md` — top block, reverse-chronological |
> | 2 · ingestion loop | `/quarantine/accretion/` for work; `/quarantine/proposals/` for anything another seat must rule on |
> | 3 · `wiki/log.md` | `/quarantine/log/` |
>
> ⭐ **And the step this ritual has never had, which is the one that would have mattered most:**
> **record what you needed and did not get.** Six runs each lost time to something the previous run
> already knew. **One line in `/quarantine/INDEX.md` closes more of that gap than a memory file
> would.**

## Claude Code Reasoning Capture (thinking is NOT archived)

**Claude Code discards readable thinking.** Since CC v2.1.72 the `.jsonl` stores extended-thinking only as an encrypted `signature` (decrypted server-side for `--resume`, unreadable by us; no supported plaintext path — GitHub anthropics/claude-code #32810/#31143). So any load-bearing reasoning that stays in the thinking channel of a CC session is **permanently lost to the wiki**. (claude.ai exports keep the readable summarized thinking; CC does not. Reference: memory `cc-jsonl-thinking-signature-only`.)

**Rule — during any Claude Code session likely to be wiki-ingested:** surface load-bearing reasoning in **visible output**, not just the thinking channel. When a materially different continuation or a decision rationale is live, voice it in the response (the mid-output-scratchpad discipline) — that is what gets captured. Treat CC thinking as ephemeral (quality-in-session, not archival).

**For reasoning-critical work, prefer a channel that retains thinking:**
- **claude.ai** — keeps readable summarized thinking in its exports (default-preserved by `convert-export.py`).
- **A thin Anthropic API wrapper** (`display: "summarized"`, log the `thinking` blocks to a dated file) — the durable, portable capture tool; set `display:"summarized"` explicitly on newest models (default is `omitted`).
- **Cline** (VS Code) persists the raw API conversation incl. reasoning to disk.

Adoption of a capture tool (wrapper vs Cline) is Jon's call — see the intake packet `data-master-cc-thinking-retention-options-2026-07-12`.