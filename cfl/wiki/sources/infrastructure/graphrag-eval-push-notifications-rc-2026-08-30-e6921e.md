---
title: "GraphRAG relevance-eval turn — push notifications / Remote Control (2026-08-30, e6921e)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 1 vs fleet 0 on authored labels"
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-30-e6921e-question-push-notifications-remote-control-rc-brid.md
raw_sha256: 7174693b64f78d71823c3d0083d3245342a6ae8dcdfee81f76124469fe5b874a
retrieval_key: graphrag-eval-push-notifications-rc-2026-08-30-e6921e
aliases: [push notification retrieval eval, RC bridge candidate scoring, e6921e]
date: 2026-08-30
generated_by: S-0 executor (coverage lane 2, week-2026-09-02-corpus dispatch, D3/D4/D5)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
tags: [graphrag, retrieval, relevance-eval, session]
---

## Summary

A two-turn, machine-authored GraphRAG retrieval regression-eval transcript, not a Jon-authored
session: turn 1 poses a fixed QUESTION ("push notifications remote control RC bridged mobile")
with 16 candidate chunks pulled from the live wiki/standards corpus, and turn 2 is the model's own
relevance-scoring pass over those candidates (0-10 scale, one-line reason each). Content is the
retrieval system exercising itself against known-answer chunks about Jon's no-push-notifications
rule and his RC (Remote Control) usage — useful as a record of what the retrieval layer judged
relevant to that query on 2026-08-30, not as a Jon-authored source. `raw_length: 11210 chars / 176
lines`.

## Key Claims

- The eval's own highest-scored candidate (score 10/10) is `CLAUDE-STANDARDS.md` chunk 5729,
  reasoned "Jon quote stating he uses RC and hates push notifications" — the candidate's own
  excerpt embeds Jon's verbatim 2026-08-17 line, already documented elsewhere in this wiki: *"I've
  been using rc this whole time and I HATE push notifications."* [verbatim, as embedded in the
  candidate excerpt] ([graphrag-eval-push-notifications-rc-2026-08-30-e6921e:T1])
- The scoring pass (turn 2) is a machine self-grading of retrieval quality, not new factual
  content: 16 candidates scored from 0 ("completely unrelated") to 10, with three scored 9 or
  above (chunks 5729, 4538, 6576) as directly on-topic and several scored 1-2 as off-topic noise
  (coordinator-role chunks, cost-census chunks). [reconstructed] ([graphrag-eval-push-notifications-rc-2026-08-30-e6921e:T2])
- This transcript is one of a set of near-identical QUESTION/CANDIDATES eval sessions captured
  the same day (see also [[graphrag-eval-halt-write-lane-2026-08-30-915a3a]] and
  [[graphrag-eval-self-branching-hard-gate-2026-08-30-90ec8b]]), each a single fixed-question
  retrieval regression case rather than a live Jon conversation. [reconstructed] ([graphrag-eval-push-notifications-rc-2026-08-30-e6921e:T1])

## Conflicts

None found against existing wiki pages at time of writing. This page's own no-push-notifications
content is a restatement of what the retrieval candidates already excerpt from
`CLAUDE-STANDARDS.md` — the primary for the underlying Jon quote is that standards page, not this
eval transcript; this transcript documents the retrieval system's behavior against that primary,
not the primary itself.

## Cross-links

- [[graphrag-retrieval]] — the retrieval system this transcript's QUESTION/CANDIDATES/scoring
  structure exercises.
- [[graphrag-eval-halt-write-lane-2026-08-30-915a3a]] — sibling eval transcript, same day, same
  structure, different query.
- [[graphrag-eval-self-branching-hard-gate-2026-08-30-90ec8b]] — sibling eval transcript, same
  day, same structure, different query.
