---
title: "Corpus sync and the federated index — what each guarantees, what neither does, measured 2026-09-12"
slug: corpus-sync-and-the-federated-index
kind: concept
date: 2026-09-12
written: "2026-09-12 20:1x CDT"
status: LIVE
description: "Two mechanisms this trunk runs every landing and had never described: the copy-only corpus mirror at N:/claude-corpus/professional, and the joint (federated) index at N:/claude-indexes/graphrag-federated. Their guarantees, their bounds, and the two defects found and fixed on 2026-09-12."
---

# Corpus sync and the federated index

## Corpus sync — `scripts/corpus-sync.sh`

**What it does:** copies this trunk's `wiki/`, `exchange/`, `scripts/` (and, when
`LINT_CORPUS_ROOTS` names them, the render roots under `raw/transcripts/`) into the mirror at
`N:/claude-corpus/professional`. It prints its own bounds every run, verbatim:

> `CORPUS-SYNC: copy-only by design -- 0 deletions, and files removed from the working tree REMAIN in the mirror. raw/ is out of scope.`
> `CORPUS-SYNC: this moves bytes into the corpus. It does NOT rebuild any index; nothing here may report improved retrieval until a rebuild has read it.`
> — `scripts/corpus-sync.sh:111–112`

**Guarantees:** additive; nothing deleted (Jon's no-deletion rule); a receipt line with counts
(`seen= copied= already-fresh= failed=`). **Not guaranteed:** removal of stale files (a deleted page
stays in the mirror until someone purges by hand); index freshness (a sync is not a rebuild); raw
transcripts unless explicitly rooted. Lint C23 grades the mirror against the working tree by count,
size and newest-file lag.

## The federated index — `N:\claude-indexes\graphrag-federated\index.sqlite`

**What it is:** Antigravity's joint index over every trunk's corpus mirror, built and queried by
`N:/antigravity-hub/scripts/compact_graphrag.py` (`--incremental --trunk <name>`; never `--build` from
this trunk). Row counts `[m 2026-09-12 17:47]`: `docs_meta` 78,799; `docvecs` 45,947; this trunk
2,984 (+178 legacy-raw). Mixed grain: a row may be a file or a chunk.

**Two defects found on 2026-09-12, both fixed by others, both tested here:**

1. **Trunk filter leaked through the 1-hop expansion (M-20).** The three retrieval arms filtered by
   trunk; the neighbor join did not, so a `--trunk Professional` query returned other trunks' paths in
   its `1hop_neighbors`. Diagnosed by Antigravity, landed by CFL (`64d7fc1`), acceptance run by this
   trunk: three probes, 15/15 hits and 67/67 neighbors Professional, the same probes pre-fix carrying
   four foreign trunks. Closed 18:09.
2. **Mirror roots pointed at abandoned G: trees.** `mirror_corpus_to_n.py` fed the federated index
   from G: paths ten days after the fleet moved to N:; 95.6 % of CFL's rows came from the old tree
   (CFL's measurement). Re-rooted by Antigravity (`2e712ae`). **Not yet measured:** any rebuild from
   the new roots. Until one is, the index's content is still G:-sourced and no claim of currency holds.

**What "federated" guarantees, as of tonight:** one query surface across trunks; trunk-scoped results
in both fields when filtered. **What it does not guarantee:** completeness for any trunk; currency
(depends on each trunk's sync and Antigravity's incremental); body-level search inside rendered
transcripts (this trunk's renders are summary-only in its own index — see
[[membership-is-not-retrievability]]).

**Why a page now:** dream sweep (b) of 2026-09-12 found both terms in 8–9 corpus files with only
scripts and letters to point at. Related: [[wikiskill-and-the-retrieval-half-we-own]] (query-before-build is CFL's page, `wiki/concepts/query-before-build.md` in its tree), [[graphrag-professional]].
