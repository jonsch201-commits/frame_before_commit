---
title: "Headless probe — cwd + git branch + HEADLESS-PROBE-OK, 2026-08-23"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-code/code-2026-08-23-c42649-print-exactly-three-lines-and-nothing-else-1-your.md
source_kind: session
date: 2026-08-23
retrieval_key: headless-probe-cwd-branch-2026-08-23-c42649
aliases: [HEADLESS-PROBE-OK, headless liveness probe c42649, Claude Personal branch probe]
generated_by: coverage lane 3 executor (week-2026-09-02-corpus branch), Z-class census promotion
raw_sha256: 81679d2bc258c3345022df864285066d3fb2e3221e5bffb3b7d4b3ac442c9607
raw_length: 2342 chars / 76 lines
uncaptured_assessed: populated
fidelity: verbatim
tags: [headless-probe, liveness-check, claude-personal, git-branch-probe, harness-cron, zero-footprint]
---

# Headless probe — cwd + git branch + HEADLESS-PROBE-OK, 2026-08-23

## Summary

A three-line liveness probe against a Claude Personal session: cwd, git branch, and the literal
token `HEADLESS-PROBE-OK`, tool use restricted to only what those three facts require. The session
ran `pwd && git branch --show-current`, answered `G:\My Drive\Claude\Claude Personal` /
`master` / `HEADLESS-PROBE-OK`, and closed noting no work moved (read-only probe, no mirror
refresh needed). Same harness-cron probe family as [[headless-probe-cwd-wiki-count-2026-08-23-7fcb8c]], run four minutes apart per the corpus filename/id proximity, distinct instruction shape (three lines vs one).

## Key Claims

- **The probe instruction, verbatim.** "Print exactly three lines and nothing else: (1) your
  current working directory, (2) the git branch, (3) the literal word HEADLESS-PROBE-OK. Do not
  use any tools other than what you need for those three facts." [verbatim] ([headless-probe-cwd-branch-2026-08-23-c42649:T1])
- **Measured result.** cwd `G:\My Drive\Claude\Claude Personal`, branch `master`, plus the literal
  compliance token `HEADLESS-PROBE-OK` — confirms the Claude Personal trunk was on its `master`
  branch as of 2026-08-23. [verbatim] ([headless-probe-cwd-branch-2026-08-23-c42649:T4])
- **Self-reported no-op.** Closing note: read-only probe, no work moved, mirror refresh not
  needed. [paraphrase] ([headless-probe-cwd-branch-2026-08-23-c42649:T5])

## Conflicts

None found. Same probe-registry class as [[probe-registry]] and
[[headless-probe-cwd-wiki-count-2026-08-23-7fcb8c]].

## Cross-Wiki

Claude Personal trunk branch state (`master`, 2026-08-23) — a dated cross-trunk data point; this
page itself lives in the CFL trunk per this lane's scope.
