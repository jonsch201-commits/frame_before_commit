---
title: "Docker Readiness Plan Status — and the Reading-Surface Defect Named"
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 2 vs skills 1 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-21-085e60-docker-readiness-plan-status.md
chat_id: 085e6037-317a-40f8-b756-f9025b7f2dea
date_ingested: 2026-07-21
type: session
tags: docker, packet-a, coordinator, reading-surface-defect, gate-1, intake, session
---

## Summary

A short claude.ai session (2026-07-20 evening) in which Jon, frustrated that he "can't tell the status" of the Docker-readiness plan and suspects the wiki/skill work was abandoned, asks for a status reconciliation. The answer: the Packet A plan **mostly shipped** in the 07-19 merge wave (#44–#57) but the *status surfaces* Jon would check were never updated, so the progress is invisible. The session's durable contribution is naming a recurring failure class — **state gets written to surfaces the next reader doesn't read** — and producing a coordinator work-order to fix the class, not the instances.

## Key Claims

- **Packet A GATE-1 status reconciled item-by-item** ([085e60:T2]): #2 security/deny-policy DONE (PR #46, verify script OK); #4 triage-packet skill DONE (PR #42); #6 questions-for-jon.md DONE (PR #47, ADOPTED); #1 SessionStart hook STRANDED→recovered as PR #58 (still open); #3/#5 assumed-in-#44 but individually unverified; #7a Drive selective-sync + DS-3 are Jon's; #8 intake-queue (L4) never dispatched.
- **The "abandoned" feeling is a real defect, not a mood** ([085e60:T2]): trackers `tracker/skills.md` and `open-items.md` are dated 2026-04-30 while the work lives in merged PRs; the Packet A checklist was never promoted to a tracked page. Work landed; the status surface didn't move with it.
- **The reading-surface defect, named** ([085e60:T4]): three findings this week are one finding — gitignored `raw/intake/` (deposits untracked by construction), the stranded SessionStart hook (freshness guarantee that never reached main), and 04-30 trackers. State is repeatedly written where its consumer won't read it. Fix the class, not the instances.
- **A new Fable coordinator "can't see the files"** ([085e60:T2–T4]): initially framed as a claude.ai Drive-visibility problem (the `'ID' in parents` vs `parentId = 'ID'` silent-fail syntax; ~10 worktree mirror copies on Drive), then corrected by Jon — it is a **Claude Code** coordinator, so it sees git; the real cause is the reading-surface class above.
- **Coordinator work-order drafted** ([085e60:T4]): review/ready PR #58; propose ONE fix for the gitignored-intake root cause (tracked `intake/` dir or deposit-plus-manifest); dispatch L4 after two merges; refresh `tracker/skills.md`/`open-items.md` and convert the Packet-A checklist to a tracked page; re-run GATE-1 against main. DS-3 and 7a remain Jon's; Packet B stays gated; nothing touches the Docker run.

## Entities & Concepts

[[extraction-pipeline]], [[skills-system]], [[multi-agent-orchestration]]

Packet A, GATE 1, Docker isolation (NO-GO), Coordinator role, SessionStart auto-sync hook (PR #58), gitignored-intake root cause, reading-surface defect, DS-3, Drive selective-sync (7a).

## Conflicts

None. This session's status reconciliation is consistent with the post-merge-wave state recorded in `wiki/index.md` and `wiki/log.md`; it predates and motivates the coordinator dry-run findings (`raw/intake/2026-07-20-coordinator-dryrun-findings.md`).

## Uncaptured Content

- **Unfollowed threads:** the "months-long defect Jon can't articulate" is named here as the reading-surface class but not yet turned into a durable protocol/skill change — candidate for skills-master.
- **Absent technical details:** whether `exchange/` syncs to Drive at all was tagged `[UNGROUNDED]` in-session and left unresolved.
