---
title: "GraphRAG v0 — Hybrid Retrieval Over the Wiki"
aliases: ["GraphRAG", "graph rag", "vector embedded graph rag", "vector embed graph rag", "hybrid retrieval", "the ranker", "RRF fusion", "the retrieval index", "wiki retrieval"]
kind: concept
trunk: fl
branch: [cfl]
sub_branch: [retrieval]
branch_reason: "R-CONCEPTS; promoted 2026-08-23 from 16 days of frozen tracker material per Jon's 'forcing a wiki update' directive"
type: concept
first_seen: scripts/graphrag/README.md (built 2026-08-17)
source_count: 3
last_updated: 2026-08-23
maintained_by: wiki-master (proposal, this promotion pass — unratified)
---

# GraphRAG v0

**What it is for — context economy, not "search."** Jon, 2026-08-17, verbatim:

> *"When can we move shit out of the huge Claude md Files and into the wiki, read when needed
> based on vector embedded graph rag?"*

`[measured 2026-08-17]` global `CLAUDE.md` (21,459 B) + CFL project `CLAUDE.md` (29,787 B) ≈ 51 KB
≈ ~13k tokens paid by every session before a word of work. GraphRAG is the mechanism that buys
that back: material moves to the wiki and is read when needed, not carried in every context. It is
a **move, not a trim** — nothing is deleted.

## Why three signals, not one

Jon named three distinct failure modes in one sentence and no single mechanism answers all three
(`scripts/graphrag/README.md:16-26`):

| failure mode | example | mechanism |
|---|---|---|
| typos | "vector embeding", "fense" | fuzzy lexical expansion (trigram) |
| imprecise language | "how much budget is left" | dense embeddings |
| stylomantic drift | one trunk's words ≠ another's | dense + graph scoping |

**Embeddings do not fix typos.** A static embedder tokenises `embeding` differently from
`embedding` and can land nowhere near it. The typo half is carried by expanding a query term to
corpus terms sharing character trigrams — a mechanism that never needed a model.

## Architecture

Three rankings fused by **Reciprocal Rank Fusion (RRF)**, deliberately chosen because cosine
similarity and BM25 scores live on incomparable scales and a weighted sum is an unmaintained
calibration constant; RRF fuses ranks, so it cannot be silently miscalibrated.

| signal | grain | answers |
|---|---|---|
| chunk-dense | ~135 tokens | paraphrase at paragraph grain |
| doc-dense | whole file | "which page is this even about" |
| fuzzy-lexical | BM25 + trigram expansion | typos |

The doc-level vector exists because of a measured miss, not as a flourish: `[measured 2026-08-17]`
the chunk answering "which seat only hands work out" sat at chunk-dense rank 4,105 of 16,132 — a
broad question hits the document, not one paragraph. 819 doc vectors fixed the grain mismatch.

**Model:** `minishlab/potion-retrieval-32M` — open weights, MIT, retrieval-tuned static
embeddings, numpy + tokenizers only, no torch/CUDA/key/cost/network after first fetch. Chosen
because Anthropic ships no embeddings model (verified from their own docs) and a hosted API is a
money-and-key decision that would have needed Jon's sign-off; the open-weight road kept that
question away from him. `[measured]` full corpus embedded in 61 seconds.

**Index location:** off Drive, `%LOCALAPPDATA%\claude\graphrag\`. The first build wrote to
`wiki/.graphrag/` on Drive and was still running at 14 minutes / 60 MB of journal churn; the
identical build off Drive took 61 seconds — a >13× difference. "Durable" is satisfied because the
index is a file that survives a reboot, not because it syncs to the cloud.

## Tiers — scoping, not deletion

`[measured]` `wiki/intake-triage/` is 11,706 of 16,132 chunks (72%) — an operational queue, not
knowledge. Retrieval defaults to the `knowledge` tier; `--tier NAME` selects; `--all-tiers` reaches
everything. Nothing is dropped; a packet is one flag away.

**`provenance` tier, added 2026-08-23 (SEC-113):** Jon's demand was that retrieval "track all the
way to the actual conversations." It could not, because the walk config never walked `raw/**` at
all — a photos query returned a *stub row saying photo sessions exist*, not the conversation. "A
stub about a conversation is not a conversation." The `provenance` tier now covers
`raw/transcripts/**` only (`[measured 2026-08-23]` 4,376 of 6,079 `.md` files under `raw/` —
superseded parse trees like `_backup-sessions-2026-07-24/` and `_quarantine/` are excluded because
every live primary has a counterpart under `raw/transcripts/`, and indexing all four would bury the
live copy under three near-duplicates). One chunk per file (title + Jon's `## Human` turns, or a
sidecar summary) — a phrase buried mid-transcript is not retrievable by this tier; it gets you to
the file, `grep` gets you to the line. The tier gate was a boolean until this landed and **failed
open** (`tier != "queue"` would have silently admitted any new tier to the default scope); it is
now an allow-set — a tier nobody has named is not searched until somebody names it.

**Privacy boundary for `provenance`, all three facts must hold together:** (1) `raw/` is
gitignored, so this walk creates no commit/push/PR/issue; (2) the index lives off Drive on `C:`,
inside Jon's 2026-08-19 trust zone ("Just working on my C on my G and D"); (3) the tier is off by
default. The cutting half: over-scrubbing is itself a violation of Jon's 2026-08-11 ruling ("don't
make key PII info harder to use... fine in any file the resident can read") — excluding the
personal corpus from a local-only index would break that rule as surely as a leak would.

## What it measurably fixes, and what it does not (`scripts/graphrag/acceptance.py`)

Criterion: a query with Jon's typos/imprecise phrasing must retrieve the right page where
exact-match search returns nothing, and grep/graph baselines must FAIL.

| case | class | verdict |
|---|---|---|
| T1 "stylomantic diffrences betwen the trunks" | typo | PASS |
| T2 "stocastic retreival relevence band sampeling" | typo | PASS |
| T3 "the fense is wider than you assume" | typo | INCONCLUSIVE |
| T4 "cleanupperioddays retention deleteing my sesions" | typo | PASS |
| I1 "which seat is not allowed to do the work itself…" | imprecise | **FAIL** |
| I2 "what happens when something written down once drifts…" | imprecise | **FAIL** |

⭐ **Typo 3/4, imprecise 0/2.** Static embeddings need vocabulary overlap; the imprecise/paraphrase
boundary needs a contextual model this system does not have. Grep found the target in 1/6, graph-
only in 0/6 — so GraphRAG beats both baselines while still failing half its own acceptance set.
This is the honest bound stated in `wiki/concepts/superintelligence-bostrom.md`'s sibling memory
entry ("Boundary Model") — do not read the PASS column alone.

## Supersession — a live, unfixed defect this ranker inherits

See [[supersession-and-old-rules-outranking-amendments]] for the full account. In short: a
`kind='supersedes'` edge type was added 2026-08-23 (P2-3) and demotes a superseded page's rank by
0.6 — proven on the source-page-standard v4→v1 lineage (v1 fell from rank 1 to rank 3). **But the
PII-rule regression this was meant to fix is still live**: the superseded 2026-08-09 wording in
`CLAUDE.md:248-261` outranks its own 2026-08-19 amendment at `:266-287` by 2.5%, because both
chunks live in the **same file** and edges are file→file — the structural fix cannot discriminate
within one document. Probe P16 in [[probe-registry]] tracks this by id; its highest run is FAIL.

## Ratified by Jon

CFL-D-013, 2026-08-22, live: *"I rule it a working foundation we keep building on!"* Plus a
directive that retrieval testing/improvement is BY DEFAULT, not explicit invocation — the origin
of [[probe-registry]].

## See also

- [[probe-registry]] — the append-only test mechanism this page's own claims are graded against.
- [[supersession-and-old-rules-outranking-amendments]] — the live defect P16 exposes.
- [[de-pii-deriver]] — a downstream consumer of the same corpus this index walks.
