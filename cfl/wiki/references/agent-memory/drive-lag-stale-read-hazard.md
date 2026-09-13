---
title: Drive-lag stale-read hazard
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_drive-lag-stale-read-hazard.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, drive-sync, stale-read]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: drive-lag-stale-read-hazard
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Drive-lag stale-read hazard

*Source description:* Google-Drive-synced repo can serve a stale working file while git status reports clean — read consequential state from git show HEAD

On 2026-07-06/07, PM opened a false "DS-3 gate violation" because the working copy of `wiki/tracker/projects.md` read at session open was a **Google-Drive-lagged** copy showing superseded 2026-07-03 rows, while `git status` reported the tree **clean**. The real HEAD file was already the 2026-07-08 wiki-master update with DS-3 closed and Jon-approved. The same class bit twice in one session: a stale `origin/main` remote-tracking ref falsely reported local `main` as 123 commits ahead.

**Why:** This repo lives on `G:\` (Google Drive). Drive sync lag desyncs the on-disk working file from what git has tracked, and `git status` won't flag it because git compares its index against the (already-committed) tree, not against Drive's pending sync.

**How to apply:** When a stale read would be consequential (tracker / log / prior-decision state), read via `git show HEAD:<path>` or work from a freshly-materialized worktree — not the main checkout's working file. Run an explicit `git fetch` before trusting ahead/behind counts. Logged in `wiki/tracker/projects.md` Notes (via [[session-close-2026-07-07-backlog-plan]] PR #2). Candidate for a wiki-master intake packet. Related: [[active-work-state]].

**Second, distinct mechanism (2026-07-20, session 49a1c0):** same symptom (plain file reads return stale content) from a different, non-Drive cause: the local `main` checkout simply hadn't been pulled after a merge wave landed on `origin/main` — 13 commits behind. `git log origin/main` was accurate (reads via remote ref), but `cat`/`tail`/`grep`/`Read` on any tracked file silently returned the pre-merge-wave local copy, with no error or warning. This produced a false "wiki/log.md is missing an entry" finding that a dispatched wiki-executor correctly caught by re-verifying against `origin/main` directly rather than trusting the brief. **Fix, generalized:** before trusting any file read of consequential git-tracked content, run `git fetch && git status --short --branch` and check for "behind N" — not just after a suspected desync, but as standing practice any time a merge wave may have landed between sessions. If behind, either pull first or read via `git show origin/main:<path>`, never the plain working-tree file.
