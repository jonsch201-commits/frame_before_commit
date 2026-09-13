---
title: "Headless probe — cwd + wiki .md count, 2026-08-23"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-code/code-2026-08-23-7fcb8c-reply-with-only-this-exact-line-and-nothing-else-p.md
source_kind: session
date: 2026-08-23
retrieval_key: headless-probe-cwd-wiki-count-2026-08-23-7fcb8c
aliases: [PROBE cwd files_in_wiki, headless liveness probe 7fcb8c, Claude Personal cwd probe]
generated_by: coverage lane 3 executor (week-2026-09-02-corpus branch), Z-class census promotion
raw_sha256: a8ae350886e25a3773d2314537c65c4712b810e65aeb9e6df2fa36806f4478dc
raw_length: 2356 chars / 74 lines
uncaptured_assessed: populated
fidelity: verbatim
tags: [headless-probe, liveness-check, claude-personal, wiki-count-probe, harness-cron, zero-footprint]
---

# Headless probe — cwd + wiki .md count, 2026-08-23

## Summary

A single-turn liveness probe fired against a Claude Personal session, requiring the exact reply
`PROBE cwd=<cwd> files_in_wiki=<count>` with no preamble. The session ran `pwd` and a recursive
count of `.md` files under `wiki/`, then answered `PROBE cwd=G:\My Drive\Claude\Claude Personal
files_in_wiki=790`. No further work occurred — the session's own closing line states nothing moved
that the fable-mirror would need to refresh. Zero-footprint by design: this is a harness
health-check, not a work session.

## Key Claims

- **The probe instruction, verbatim.** Jon (or a scheduling harness acting under his standing
  cron authorization) required an exact-format, no-preamble reply: "Reply with ONLY this exact
  line and nothing else: PROBE cwd=<your cwd> files_in_wiki=<count of .md files under wiki/ or
  NA>. No preamble, no closing remarks." [verbatim] ([headless-probe-cwd-wiki-count-2026-08-23-7fcb8c:T1])
- **Measured result.** The session answered `PROBE cwd=G:\My Drive\Claude\Claude Personal
  files_in_wiki=790` — a Claude Personal trunk wiki count of 790 `.md` files as of 2026-08-23,
  useful as a dated cross-trunk wiki-size data point. [verbatim] ([headless-probe-cwd-wiki-count-2026-08-23-7fcb8c:T4])
- **Self-reported no-op.** The session's closing note states explicitly no work moved and the
  fable-mirror does not need a refresh from this session. [paraphrase] ([headless-probe-cwd-wiki-count-2026-08-23-7fcb8c:T5])

## Conflicts

None found. Consistent with the probe-registry seal-then-run pattern described in
[[probe-registry]] — this session is itself an instance of that class of check, run against a
live session rather than a wiki artifact.

## Cross-Wiki

Claude Personal trunk cwd/wiki-count data point (790 `.md` files, 2026-08-23) — of reference value
to any cross-trunk wiki-size comparison; this page itself lives in the CFL trunk per this lane's
scope.
