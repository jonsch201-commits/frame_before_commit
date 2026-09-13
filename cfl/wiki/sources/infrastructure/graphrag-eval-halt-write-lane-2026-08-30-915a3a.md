---
title: "GraphRAG relevance-eval turn — HALT_WRITE_LANE (2026-08-30, 915a3a)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 1 vs fleet 0 on authored labels"
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-30-915a3a-question-what-is-halt-write-lane-candidates.md
raw_sha256: df4753f1a124b17abf61186e6064b53b299c23a28fddf0e60c4b580fe9844554
retrieval_key: graphrag-eval-halt-write-lane-2026-08-30-915a3a
aliases: [HALT_WRITE_LANE retrieval eval, HALT_WRITE_LANE_ADVISORY rename, 915a3a]
date: 2026-08-30
generated_by: S-0 executor (coverage lane 2, week-2026-09-02-corpus dispatch, D3/D4/D5)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
tags: [graphrag, retrieval, relevance-eval, session]
---

## Summary

A two-turn, machine-authored GraphRAG retrieval regression-eval transcript, sibling to
[[graphrag-eval-push-notifications-rc-2026-08-30-e6921e]]: turn 1 poses the fixed QUESTION "what
is HALT_WRITE_LANE" with 12 candidate chunks, and turn 2 is the model's relevance-scoring pass
(0-10 scale, one-line reason each). The candidates themselves carry a real finding — that
`HALT_WRITE_LANE` was renamed to `HALT_WRITE_LANE_ADVISORY` on Jon's own directive after he
declined to have it become an enforcer. `raw_length: 10025 chars / 148 lines`.

## Key Claims

- ~~The eval's own top-scored candidate (chunk 5904, score 7) defines HALT_WRITE_LANE as "the
  canonical layer-B instance flag,"~~ [cold-grade F2, 2026-09-04: REFUTED. The scoring pass's own
  top score is chunk 3449, score 8 ("explains it's a flag, defect is ABSENT READER"), raw line 143;
  chunk 5904 is tied SECOND at score 7 with chunk 9033. The quoted reason string is also wrong as
  rendered — raw line 138 reads `"defines as canonical layer-B instance flag"` (not "the canonical
  ... instance flag"), and the chunk's own text (raw line 80) writes `layer-(B)`, not `layer-B`.]
  reasoned in the scoring pass as the flag's own definition
  rather than a mention of it. [reconstructed] ([graphrag-eval-halt-write-lane-2026-08-30-915a3a:T2])
- A separate candidate (chunk 6695, `rulings/jon-arrivals-raw.md`) records that
  `HALT_WRITE_LANE` was renamed to `HALT_WRITE_LANE_ADVISORY` on Jon's directive, quoting the
  proposing session's own account: *"This is the finding I offered you for the joint write-up ...
  and Jon's directive resolved it against my instinct. I was leaning toward baking an enforcer.
  He said"* — the candidate excerpt is truncated at "They are not" before Jon's own words
  complete, so the full Jon quote is not independently verifiable from this transcript alone.
  [reconstructed, quote truncated in source] ([graphrag-eval-halt-write-lane-2026-08-30-915a3a:T1])
- One candidate (chunk 5905/9034, duplicate content) traces the practical cost of the flag from
  Herald's own first-hand account: *"I confirm the practical cost from inside: I found
  HALT_WRITE_LANE at wake, treated it as a live gate, and spent a turn establishing i"* (excerpt
  itself truncated mid-sentence in the candidate data). [verbatim, as embedded and truncated in
  the candidate excerpt] ([graphrag-eval-halt-write-lane-2026-08-30-915a3a:T1])

## Conflicts

None found against existing wiki pages at time of writing. Both quoted candidate excerpts above
are truncated mid-sentence in the underlying candidate data (a retrieval-chunk artifact, not this
transcript's own construction) — treat the HALT_WRITE_LANE_ADVISORY rename claim as
corroborated-but-incomplete pending a read of the full `rulings/jon-arrivals-raw.md` primary.

## Cross-links

- [[graphrag-retrieval]] — the retrieval system this transcript's QUESTION/CANDIDATES/scoring
  structure exercises.
- [[graphrag-eval-push-notifications-rc-2026-08-30-e6921e]] — sibling eval transcript, same day,
  same structure, different query.
- [[graphrag-eval-self-branching-hard-gate-2026-08-30-90ec8b]] — sibling eval transcript, same
  day, same structure, different query.
