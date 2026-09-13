---
name: session-lifecycle
description: >-
  Handles session re-open, mid-session status check, and project status. Loaded on demand — do not
  load on every cold open. Triggers: "status", "where are we", "session re-open", "project
  status", "full status".
---

# Session Lifecycle Skill

This skill is not ambient. Load it only when one of its triggers fires. Its purpose is to keep SESSION-ORDER-SKILL lean — lifecycle behaviors load here on demand rather than adding overhead to every cold open.

---

## Triggers

| Phrase | Operation |
|--------|-----------|
| "status" / "where are we" | → mid-session status check |
| "project status" / "full status" | → project status |
| Re-entering a session that was in progress | → session re-open |

---

## Session Re-Open

Use when: returning to a session that was interrupted or paused mid-work. The conversation history is present but orientation is needed before continuing.

Steps:
1. Read the session map if one was maintained (DONE / IN PROGRESS / NEXT / HELD / TRIAGE)
2. If no session map is visible, scan recent messages to reconstruct current state
3. State: what was in progress, what is HELD, what was last completed
4. Ask Jon: "Ready to continue with [in-progress item]?" — do not assume; confirm before resuming

If context compaction has occurred:
- Re-read the skill file for any role that was active
- Do not rely on what you "remember" writing or deciding
- State explicitly that compaction occurred and that you are re-reading before continuing

---

## Mid-Session Status Check

Use when: Jon asks "status" or "where are we" during an active session.

Steps:
1. State the current session map:
   - IN PROGRESS: what is being worked on right now
   - NEXT: agreed next steps this session
   - HELD: parked items that will return
   - TRIAGE: items handed off
   - DONE: completed this session
2. Flag if any HELD items are at risk of being dropped (session time running short)
3. If no session map exists, reconstruct from recent conversation

Output: compact — 5-8 lines. Do not summarize content, only state. The map is a navigation tool, not a recap.

---

## Project Status

Use when: Jon asks "project status" or "full status" — a higher-level view of the entire FL project, not just this session.

Steps:
1. Read `wiki/tracker/open-items.md` — count and surface open OI-items, identify BLOCKED items
2. Read `wiki/tracker/triage.md` — count open T-items, flag any stale (open multiple sessions without movement)
3. Read `wiki/log.md` (last 20 lines) — what was last ingested?
4. State:
   - Open OI-items: count + top 3 by urgency
   - Open T-items: count + any requiring Jon's decision
   - BLOCKED items: name each one and its blocker
   - Last wiki activity: what was last committed

Output: 10-15 lines. Jon uses this to decide which role to invoke next or which item to prioritize.

If project-manager is available as a dedicated role in this session, prefer invoking it for project status rather than running this operation. This operation is a lightweight fallback for sessions where project-manager is not active.

---

## What This Skill Does Not Do

- It does not replace the session-close ritual in SESSION-ORDER-SKILL
- It does not make triage decisions — that is triage-master's job
- It does not update the tracker — that is project-manager's job
- It does not ingest anything — that is wiki-master's job

It orients. Other skills act.
