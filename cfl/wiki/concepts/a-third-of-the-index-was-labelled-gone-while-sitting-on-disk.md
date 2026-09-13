---
kind: concept
slug: index-labelled-gone-while-on-disk
status: LIVE
date: 2026-09-12
owner: cfl
queried: "remove files from the graph index narrowing exclusion advised -> build_index.py narrowing guard (rank 1), herald 54%-uncitable letter (rank 2), HALF-THE-INDEXED-CORPUS one-chunk-per-file (rank 3)"
---

# A third of the index was labelled GONE while sitting on disk — and the label was the evidence for my own advice to prune it

**Jon, 2026-09-12 ~22:4x CDT, verbatim (typos his):** *"separate - removing files from the
non-wikiskills version of the graph. You've advised this several times and i've ignored you each time
so far. Lets discuss?"*

## The measurement that ends the discussion

`[measured 2026-09-12 22:4x–22:5x, this session]`

| | |
|---|---|
| indexed files | **19,238** |
| indexed files not at their cited path | **6,279 = 32.6%** |
| of those, sharing ONE root (`N:/claude-corpus/cfl/raw`) | **6,261** |
| **of those, resolving today under the G: FL tree** | **6,148 = 98.2%, 846.1 MB** |
| genuinely unfindable | **113** |

**The mirror root was never populated, not emptied.** The corpus-sync spec covers
`wiki | exchange | scripts`; `raw/` has never been in it. The files live at
`G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer/raw/transcripts/…` — Jon's
claude.ai chat corpus, personal and home and faith and family included.

## Why this is a lesson and not a bug report

**I advised pruning the graph several times, and my headline evidence was the dead-path count.**
Executing that advice on any night when the mirror was unpopulated would have dropped 846 MB of
indexed provenance — the exact corpus Jon has pushed hardest to keep searchable (*"I bet we don't even
have the full knowledge base"*, *"you need the good version"*). **Nothing would have errored. It would
have read as hygiene.** He ignored the advice every time, and the record now says he was right to.

**The premise had also already collapsed, by my own measurement four hours earlier.** The advice was
motivated by retrieval feeling slow. The cause was a missing covering index: adding
`postings(term, chunk_id)` took the terms phase from **20.3 ms/term to 0.117 ms/term** and the oracle
from **104.0s to 2.8s**. The graph was never too big.

**And the flag that produced the number had a comment admitting the truth.** It read *"the content is
not necessarily lost (the mirror RELOCATED, it did not delete)"* — and then printed
`⛔ PATH GONE (indexed file not on disk)`. ⭐ **The prose was right and the string a reader sees was
wrong, and only the second one counts.** Corrected the same night to three states: silence when the
file is at its cited path, `⚠ ROOT MOVED -- readable at <path>` when it resolves under a measured root
alias, and `⛔ PATH GONE` only when neither holds. The alias table resolves; it never rewrites a
citation, because a citation must keep naming what was indexed, and an alias whose target is absent
fails to match rather than reassuring anyone.

## What the index actually contains, for the next person who proposes trimming it

| tier | files | chunks | text |
|---|---|---|---|
| provenance (the raw record) | 12,693 | 394,539 — **77%** | 214 MB |
| queue (intake, archive) | 1,965 | 73,742 — 14% | 63 MB |
| knowledge (the default query scope) | 4,580 | 46,126 — **9%** | 44 MB |

**5.00 GB of database against 321 MB of text.** The 15× is postings (30.2M rows), vectors (514k) and
trigrams (2.9M) — index structure, not corpus. **Byte-identical duplicates total 161 files / 14.1 MB.**
There is no fat of the kind "remove files" was proposing to cut.

## The rule

⛔ **A NOT-FOUND IS A CLAIM ABOUT WHERE YOU LOOKED. Resolve against every known root before calling a
file gone, and never let a count of unresolved paths become the evidence for a deletion.** It is the
same instrument error as the 2026-07-25 loss registry — 29 sessions declared permanently gone, 23 of
them on disk in an archive the audit itself had documented — and it is Rule 15 of
`skills/ground-before-stating`: a zero is a claim about an instrument until a second method agrees.
