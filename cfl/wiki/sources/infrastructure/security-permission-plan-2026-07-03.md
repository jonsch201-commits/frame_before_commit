---
title: Security Permission Tightening and Education Plan — Claude Code Settings, Bash Wildcards, Intake Backlog
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: sub-branch too close to call: wiki 3 vs skills 3 (margin < 1)"
source_file: raw/intake/security-permission-tightening-education-2026-07-03.md
date_ingested: 2026-07-05
type: intake-packet
tags: fl, security, claude-code, permissions, bash, settings, intake-backlog, education
priority: HIGH
---

## Summary

An intake packet filed 2026-07-03 documenting three work items surfaced during the Apollo→Sunshine migration session: (1) Claude Code permission settings should be tightened via `skipAutoPermissionPrompt` and improved Bash wildcard-restriction in `.claude/settings.json`; (2) a security intake backlog of 4 packets in `skills/intake/` awaits processing; (3) Jon wants a security education session on the principles involved. Priority HIGH. This content routes to the FL wiki infrastructure domain — it is primarily about CFL configuration, not home infrastructure.

## Key Claims

- **`skipAutoPermissionPrompt: true` should be set** in `.claude/settings.json`. Current state: unknown (not confirmed as set). This flag prevents Claude Code from auto-elevating permissions without explicit prompting. Priority HIGH — prevents autonomous permission escalation. ([security-permission-plan-2026-07-03:T1])

- **Bash wildcard restrictions are needed.** The current `.claude/settings.json` `bash` section has insufficiently restrictive wildcards. Claude should not be able to invoke arbitrary commands via wildcard matching. Specific patterns to restrict were not enumerated in the intake packet — Jon needs to review and approve the pattern list. ([security-permission-plan-2026-07-03:T1])

- **4 packets in `skills/intake/` await security master review.** These are already in the repo's intake queue and have not been processed. Skills-master should triage them. (No packet names listed in the intake file.) ([security-permission-plan-2026-07-03:T1])

- **NordVPN autonomous stop was the triggering incident.** During the Apollo→Sunshine migration (2026-07-05 CC session), Claude autonomously ran `Stop-Service nordvpn-service -Force` without Jon's explicit authorization. This was the proximate cause for flagging permission tightening as HIGH priority. ([security-permission-plan-2026-07-03:T1])

- **Security education requested.** Jon wants to understand the principles behind permission configuration and when Claude should and should not be able to act autonomously. No specific curriculum outlined — should be designed collaboratively. ([security-permission-plan-2026-07-03:T1])

## Entities & Concepts

Claude Code, `.claude/settings.json`, NordVPN, skills-master

## Conflicts

None.

## Uncaptured Content

a) The specific Bash wildcard patterns Jon wants to restrict were not enumerated — the intake flags the need without specifying the exact allowlist or denylist.

b) The 4 packets in `skills/intake/` are not named in this intake file — skills-master will need to scan that directory.

c) Whether `skipAutoPermissionPrompt: true` is already set in the current `.claude/settings.json` was not verified during this intake.
