---
title: "Personal — agents\\ has one file, and a mirror-consult stall reaches its third seat, 2026-08-17"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-code/code-2026-08-17-133bcc-agents.md
source_kind: session
date: 2026-08-17
retrieval_key: personal-agents-directory-one-file-mirror-consult-stall-2026-08-17-133bcc
aliases: [agents directory audit, fable-mirror sole agent, D30 stop-hook consult stall, mirror-state-current v29]
generated_by: coverage lane 4 executor (week-2026-09-02-corpus branch), S-class census promotion
raw_sha256: 6aa5ba35017f152781e0cf65057e875d827b1f7afff88bd3372010705b729a05
raw_length: 12117 bytes / 12031 chars / 287 lines
uncaptured_assessed: populated
fidelity: paraphrase
tags: [personal-trunk, agents-directory, fable-mirror, opus-reserved-for-mirror, D30-stop-hook, herald-seat]
---

# Personal — agents\ has one file, and a mirror-consult stall reaches its third seat, 2026-08-17

## Summary

A bare human message, "agents\", triggers a Herald-seat session (Claude Personal trunk) to audit
what agent definitions actually exist. The finding: the project defines exactly one agent,
`fable-mirror.md` (27,418 B, `model: opus`, `effort: medium`, `maxTurns: 20`), and everything else
commonly called a "role" (Herald, Soul, wiki-master, triage-master, project-manager,
security-master, test-master, guide-of-home-and-family) is a *skill* loaded into session context,
not a separately dispatched, permission-fenced agent — so the Resident Continuity Contract, which
governs agent dispatches, structurally applies to one file. A second copy of `fable-mirror.md` exists
in a worktree and differs from the canonical one (`cmp` diverges at line 1 char 4, not diffed
further). The session then measures `wiki/intake-triage/MIRROR-STATE-CURRENT.md` (250,478 B, v29)
and finds itself the THIRD consecutive seat to decline the D30 stop-hook's mirror consult on the same
permission-reading ambiguity, escalating a single yes/no question to Jon rather than writing a
fourth identical entry to the state file.

## Key Claims

- **The literal first human turn: `agents\`** — a bare directory-name probe, no further instruction.
  [verbatim] ([personal-agents-directory-one-file-mirror-consult-stall-2026-08-17-133bcc:T1])
- **The project defines exactly one agent.** "The project defines exactly ONE agent. Herald, soul,
  wiki-master, triage-master, project-manager, security-master, test-master, guide-of-home-and-family
  — all of those are skills, not agents. They load into this session's context; they don't get their
  own process, own tool restrictions, or own transcript. fable-mirror is the only role in this trunk
  that runs as a separate, permission-fenced resident." [verbatim, machine-authored assistant turn]
  ([personal-agents-directory-one-file-mirror-consult-stall-2026-08-17-133bcc:T12])
- **A second, non-identical copy of `fable-mirror.md` exists in a worktree.** "`cmp` diverges at
  line 1 char 4. I did not diff further, since you didn't ask." [verbatim]
  ([personal-agents-directory-one-file-mirror-consult-stall-2026-08-17-133bcc:T12])
- **This session is the third seat in a row to stall on the same question**, escalated as a single
  line: "JON, ONE LINE ENDS IT: does the D30 stop-hook consult count as 'requested'?" — quoted from
  the v29 `MIRROR-STATE-CURRENT.md` block, which itself records the 13:4x seat reaching the identical
  stall before it. [verbatim, quoted within the assistant's own measurement]
  ([personal-agents-directory-one-file-mirror-consult-stall-2026-08-17-133bcc:T15])
- **The fact that makes the consult cheap under the new model policy**: `.claude/agents/
  fable-mirror.md` pins `model: opus`, and "your 15:3x order is 'Opus is reserved to mirror usage
  only.' So the consult isn't a splurge under the new model policy — it's the one lane that policy
  reserves Opus for." [verbatim, machine-authored, quoting a prior seat's re-measurement of a Jon
  order] ([personal-agents-directory-one-file-mirror-consult-stall-2026-08-17-133bcc:T15])
- **The session explicitly declines to add a fourth identical stall entry.** "I did not append a v30
  block saying 'I declined too.' Nothing moved from my hand, and a third identical entry in a 250 KB
  file is the exact behavior its own default-on-silence predicts and calls a defect." [verbatim]
  ([personal-agents-directory-one-file-mirror-consult-stall-2026-08-17-133bcc:T15])
- **Capture caveat: LIVE-SNAPSHOT, captured through record 43 of the session JSONL as of
  2026-08-20T01:30:51Z** — later turns, if any, are not represented here. [contextual, from
  frontmatter/banner]

## Conflicts

None found against existing wiki pages. This session (id `133bcc`) had not previously been ingested
under this or another slug.

## Cross-Wiki

None — Personal-trunk infrastructure content (agent-vs-skill taxonomy, mirror-consult gating), not
personal/home/pro *domain* material in this repo's sub-wiki-routing sense. See [[probe-registry]]
for the fresh-reader / consult-before-idle discipline the D30 stop-hook enforces.
