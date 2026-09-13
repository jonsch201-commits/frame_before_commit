---
title: "PR-1 Promise Retrospective — Score Moved 5/6/1 to 4/7/1 to 3/8/1"
source_kind: analysis
trunk: fl
branch: [cfl]
sub_branch: [pr2]
branch_reason: "R-SOURCES; promoted 2026-08-23 per Jon's 'forcing a wiki update' directive"
source_file: none
aliases: ["PR-1 promise retrospective", "3 kept 8 half-kept 1 not done", "promise retrospective", "P2-1"]
first_seen: exchange/FOR-JON-REVIEW/P2-1-promise-retrospective-2026-08-23.md
last_updated: 2026-08-23
maintained_by: wiki-master (proposal, this promotion pass — unratified)
---

# PR-1 Promise Retrospective

## Thesis

PR-1 made twelve promises. The retrospective that graded them was itself graded twice more after
publication, both times downward, both times because a later lane built the actual instrument that
measures the promise rather than relying on a proxy (file existence, a term-presence test, a flat
grep). The retrospective's own instability is more informative than any single score in it.

## Synthesized claims

- **Claim 1.** The retrospective's headline score moved from an initial 5 VERIFIED / 6 PARTIAL / 1
  NOT DONE, to 4/7/1, to the current 3/8/1 — two downgrades, no upgrades.
  Anchors: `exchange/FOR-JON-REVIEW/P2-1-promise-retrospective-2026-08-23.md` (initial grading,
  cited at `wiki/tracker/wayfinder-pr2-2026-08-23.md:206-212`); downgrade 1 at
  `wiki/tracker/wayfinder-pr2-2026-08-23.md:229-236`; downgrade 2 at
  `wiki/tracker/wayfinder-pr2-2026-08-23.md:267-279`; current score restated at `wiki/index.md:42`.

- **Claim 2.** Downgrade 1 (promise 5, "every barrier writes its record") was forced by building
  `write_barrier_memory.py --verify` against real instances rather than counting files; the true
  rate at the two barriers the promise is actually about (compact, close) was 1 filled record of 7.
  Anchor: `wiki/tracker/SEAL-unsaid-ledger-mechanism-2026-08-23.md:90-107`. See [[memory-core]] and
  [[unsaid-ledger]] for the full mechanism.

- **Claim 3.** Downgrade 2 (promise 7, the PII-supersession fix) was forced by a full-corpus
  retrieval rebuild showing the superseded 2026-08-09 PII wording still outranks its 2026-08-19
  amendment by 2.5%, in the same file, which the structural `supersedes`-edge fix cannot correct
  because supersession edges are file→file. Anchor:
  `wiki/tracker/wayfinder-pr2-2026-08-23.md:274-279`. See
  [[supersession-and-old-rules-outranking-amendments]].

- **Claim 4.** What genuinely landed and was not downgraded: the memory-core spec reached its
  official home; federation actually ran and its leak fix is in the code; barrier count grew from 1
  compact template to 4; the version-confusion probes recovered once (before regressing again per
  Claim 3); hooks remain honestly proposal-only (promise 9 intact by design). Anchor:
  `wiki/tracker/wayfinder-pr2-2026-08-23.md:207-209`.

- **Claim 5.** What was never done at all: the glossary was never written; the template-eval loop
  is designed but has never run; the unsaid ledger produced zero artifacts across all 28 barrier
  instances at any point, including at the two boundaries reached since it was fixed; consolidation
  and index-rebuild remain ritual text rather than enforced mechanism. Anchor:
  `wiki/tracker/wayfinder-pr2-2026-08-23.md:209-212`.

- **Claim 6.** `[inferred]` The pattern across Claims 2 and 3 — a score downgraded specifically
  because a lane built the actual measuring instrument instead of trusting a proxy — is the same
  shape named generally in [[disposition-and-delivered-is-not-received]], and this page is the
  concrete instance that motivated collecting that pattern as its own concept.

## Cross-wiki links

[[memory-core]] · [[unsaid-ledger]] · [[supersession-and-old-rules-outranking-amendments]] ·
[[disposition-and-delivered-is-not-received]] · [[probe-registry]]

## Uncaptured

The original P2-1 promise-by-promise grading table
(`exchange/FOR-JON-REVIEW/P2-1-promise-retrospective-2026-08-23.md`) was not independently re-read
in full by this promotion pass — this page summarizes it via the tracker's own citations of it
rather than re-verifying each of the twelve promise texts against the PR-1 body itself. That file
is the next read for anyone auditing this page's Claim 1 further than its downgrades.
