---
title: "GraphRAG relevance-eval turn — self-branching is a hard gate (2026-08-30, 90ec8b)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 1 vs fleet 0 on authored labels"
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-30-90ec8b-question-self-branching-is-a-hard-gate-not-a-nice.md
raw_sha256: 55a18b603438305d059c9f2ab7f38b8302767575d019f205949cf875bea8269f
retrieval_key: graphrag-eval-self-branching-hard-gate-2026-08-30-90ec8b
aliases: [self-branching hard gate retrieval eval, 90ec8b]
date: 2026-08-30
generated_by: S-0 executor (coverage lane 2, week-2026-09-02-corpus dispatch, D3/D4/D5)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
tags: [graphrag, retrieval, relevance-eval, session]
---

## Summary

A two-turn, machine-authored GraphRAG retrieval regression-eval transcript, sibling to
[[graphrag-eval-push-notifications-rc-2026-08-30-e6921e]] and
[[graphrag-eval-halt-write-lane-2026-08-30-915a3a]]: turn 1 poses the fixed QUESTION
"self-branching is a hard gate not a nice to have" with candidate chunks pulled from the wiki
corpus, and turn 2 is the model's relevance-scoring pass. The top candidate points to an existing
wiki concept page (`wiki/concepts/self-branching-is-a-hard-gate.md`, not present in this checkout
at the time of writing — see Conflicts) sourced to a named Jon ruling dated 2026-08-15.
`raw_length: 9115 chars / 146 lines`.

## Key Claims

- The eval's own top candidate (chunk 2422) is the frontmatter of
  `wiki/concepts/self-branching-is-a-hard-gate.md` itself, which declares
  `source: rulings/2026-08-15-jon-defect-self-branching-required.md` and `date: 2026-08-15` —
  i.e. the concept page's own primary is a named Jon ruling on self-branching being required, not
  optional. [reconstructed, from the candidate's own frontmatter excerpt] ([graphrag-eval-self-branching-hard-gate-2026-08-30-90ec8b:T1])
- A second candidate (chunk 5619, `wiki/intake-triage/dream-sweep-2026-08-24.md` [target not found on disk under this exact name; see wiki/patterns/self-citation-moves-the-class.md for the related "08-24 census document" reference]) is unrelated to
  self-branching directly — it documents a 2026-08-24 dangling-link sweep finding 2 of 55
  wikilink targets genuinely dangling, included by the retrieval system as a lower-relevance
  match (topical overlap on wiki-hygiene concepts, not the query itself). [reconstructed] ([graphrag-eval-self-branching-hard-gate-2026-08-30-90ec8b:T1])
- The scoring pass (turn 2) is the model's own machine self-grading of these candidates against
  the fixed query, not new factual content. [reconstructed] ([graphrag-eval-self-branching-hard-gate-2026-08-30-90ec8b:T2])

## Conflicts

⚠️ The concept page `wiki/concepts/self-branching-is-a-hard-gate.md` that this transcript's top
candidate excerpts from is **not present in this repo checkout** as of this page's writing
(`test -f` against the working tree returns missing) even though the candidate excerpt (captured
2026-09-02 by the extraction pipeline that produced this transcript) shows its frontmatter as
live content at that time. This is either a since-pruned/renamed page or a sync gap between the
retrieval index's source corpus and this checkout — flagged for wiki-master, not resolved here.

## Cross-links

- [[graphrag-retrieval]] — the retrieval system this transcript's QUESTION/CANDIDATES/scoring
  structure exercises.
- [[graphrag-eval-push-notifications-rc-2026-08-30-e6921e]] — sibling eval transcript, same day,
  same structure, different query.
- [[graphrag-eval-halt-write-lane-2026-08-30-915a3a]] — sibling eval transcript, same day, same
  structure, different query.
