---
# HONESTY HEADER (Jon's 08-22 ~22:0x challenge — "I can't tell from the outside if you do the
# other parts"): what the phrase "wiki-query" / "query the wiki" ACTUALLY runs today:
#   dense embeddings + doc embeddings + fuzzy lexical, RRF-fused (hybrid mode). The GRAPH leg
#   (one-hop edge expansion, W-1/CFL-D-006) is BEING WIRED 08-22 — until its control probes pass,
#   the graph in "graph rag" is provenance + baseline only. HAIKU DISCERNMENT is default-ON for
#   Jon-facing and gate-bound queries per D-013 (dispatch a haiku lane to judge
#   SUPPORTS/CONTRADICTS/NEAR-BUT-NOT-EVIDENCE on the top-k); for internal quick lookups it fires
#   on judgment. Jon needs no more specific phrase — the skill owes him the full stack, and this
#   header is amended whenever the stack changes.
name: wiki-query
description: >-
  Retrieval over the CFL wiki/skills/constitutions index (scripts/graphrag/retrieve.py). Use
  BEFORE answering any question about a CFL topic, Jon's rulings, prior builds, or session
  history, and BEFORE any dispatch/TAKE of new work (the M-14 look-before-building gate,
  scripts/audit/check_before_dispatch.py). Trigger phrases: "query the wiki", "what did Jon say
  about", "search the record", "look before building", "has this been built before". Carries the
  honesty layer that keeps a miss from reading as a confident answer: REACHABLE is not RETRIEVED,
  confident-absence is a named failure grade, and the coverage statement below lists what this
  index cannot see at all.
---

# wiki-query

A tool skill. It answers "what does the record already say" cheaply, before work starts or a
claim is made. It does not write to `wiki/`, does not ratify anything, and is not a substitute
for `check_before_dispatch.py` at dispatch time — it is one of that gate's two sweeps.

## When to invoke

- **Before answering** any question touching a CFL topic, a Jon ruling, prior session history,
  or "has X been tried" — querying first is cheaper than guessing and then being corrected.
- **Before any dispatch or `TAKE`** on `exchange/WORK-CLAIMS.md` — run the M-14 gate
  (`scripts/audit/check_before_dispatch.py`), not `retrieve.py` alone. M-14 exists because the
  index alone missed a standing letter sitting in an unindexed mirror while a system was designed
  around its absence (`wiki/tracker/wayfinder-memory-cognition-federation.md` ticket M-14).
- On close calls (top hits ambiguous or thin), run the Haiku-discernment pattern below before
  trusting rank order.

## Commands

```bash
# direct query, hybrid mode (dense + fuzzy-lexical + graph, fused by RRF)
python scripts/graphrag/retrieve.py "the fense is wider" --explain

# modes exist so a failure mode can be isolated, not just "search":
#   hybrid (default) | dense | doc | lexical | grep | graph
python scripts/graphrag/retrieve.py "vector embeding" --mode grep      # baseline: must find 0
python scripts/graphrag/retrieve.py "wake mechanism" --all-tiers       # include the triage queue
python scripts/graphrag/retrieve.py "coordinator" --json -k 5          # programmatic callers
python scripts/graphrag/retrieve.py "topic" --scope wiki:concepts      # restrict to a kind prefix

# pre-dispatch: the two-sweep gate (indexed + named-unindexed spaces + stakeholder checklist)
python scripts/audit/check_before_dispatch.py "resumption memory continuity" \
  --as-of 2026-08-22T09:00:00-0500
```

**`-k`** defaults to 8. **`--explain`** shows term expansions and graph links — use it whenever
a hit's relevance isn't obvious from the snippet alone. **`--all-tiers`** is off by default
because the `intake-triage/` queue is 72% of the index by chunk count and is operational noise,
not knowledge — flip it on only when hunting for a specific packet/receipt.

### Freshness verdict — printed on EVERY query, and it has THREE states

⛔ **This section described a banner that could not fire for four days, and the section is the
reason the defect survived: the doc vouched for the code.** `[measured 2026-09-06 22:2x, CFL
a86404c0]` RP-28 (2026-09-02) moved the corpus walk behind `--check-stale` for latency, and made
the default path `return (False, "")` — **byte-identical to the value a clean check returns.** So
"I did not look" and "I looked and it is fresh" became the same answer, no banner printed on any
default query, and this page went on promising one. The line above read *"Every query checks the
index's stored corpus fingerprint against the corpus on disk right now"*; it had been false since
09-02. **A guard whose documentation is its only remaining implementation.**

Every query now prints its verdict on the `mode :` line, whether or not anything is wrong:

```
mode    : hybrid   index: 112463 chunks, potion-retrieval-32M, freshness=FRESH
```

| state | meaning | what prints | what you do |
|---|---|---|---|
| `FRESH` | the walk ran and the corpus fingerprint matches the index | the `freshness=FRESH` token only | cite it |
| `STALE` | the walk ran and the corpus has changed since the build | `⚠️ STALE : …` | advisory only — rebuild before a claim that matters |
| `UNKNOWN` | **nobody looked**, because the last walk cost more than the budget | `⚠️ STALE-UNKNOWN : …` | your results are UNBOUNDED; re-run with `--check-stale` |

⭐ **`UNKNOWN` is the whole point and it is a separate token from `STALE` on purpose.** *"The index
is behind the corpus"* and *"nobody checked whether it is"* call for different reactions, and
collapsing them is precisely how the pre-WS-1 path read as reassuring. **UNKNOWN dominates a
PASS** — the constitution's own rule, now enforced in the retriever instead of asserted about it.

**The latency RP-28 bought is kept by BUDGET, not by silence.** The cache beside the index
remembers how long the last walk actually took; a corpus whose walk exceeds
`STALE_WALK_BUDGET_SECONDS` (5.0s, env `CFL_STALE_WALK_BUDGET`) degrades to a loud `UNKNOWN`
rather than a quiet "fresh", and `--check-stale` always overrides both the budget and the 6h TTL.
`[measured 2026-09-06, 3 runs, cache bypassed]` the full walk costs **0.13s / 3,619 `os.stat()`
calls** on this tree — not the **84.8–125.9s** RP-28 recorded — and `_staleness_walk()` has **no
short-circuit**, so that is the full-sweep cost, not an early exit. ⭐ **CONFIRMED the same session**
`[measured 2026-09-06 22:4x, one run each]`: the identical walk costs **0.13s** on
`N:\claude-cfl\clone` and **78.15s** on the `G:\My Drive` copy — **~600×**. RP-28 was almost
certainly **right when it was written**; the 09-02 move to `N:` expired it. ⚠️ The trees are not
byte-identical (3,615 vs 9,287 `os.stat` calls), so this is same-code/different-filesystem, not a
controlled comparison. ⛔ **Hence a budget, not a constant:** on `G:` the walk blows the 5s budget
and degrades to a loud `UNKNOWN`; on `N:` it checks every query. **A constant would have been
tuned on one filesystem and wrong on the other.**

An index with no stored fingerprint at all (predates staleness tracking) reports `STALE`
unconditionally. Rebuild with `python scripts/graphrag/build_index.py` (idempotent, ~61s full /
no-op if unchanged).

**Falsifier for this section, run it before you trust it:**
`python scripts/graphrag/retrieve.py --selftest` — the WS-1 block asserts all three states on
synthetic fixtures, and the `FRESH` arm is the control that proves the `STALE` arm can be false.
`[measured 2026-09-06]` a planted breach (`freshness()` hardcoded to `FRESH`) turns the STALE arm
**RED (2 FAILED)** while the FRESH control stays green; the UNKNOWN arm sits upstream of that
breach and is untouched by it, so **it is proven by its own fixture and not by this control.**

## Query the NAME, not only the PROBLEM (WW-25)

⛔ **"Look before building" is read, universally, as *search for prior art on the problem*. It must
also mean *search for the IDENTIFIER you are about to mint* — a ticket id, a rule number, a
constant, a script name, a branch.** An id is a claim about a namespace, and a namespace is
exactly the kind of shared state a single seat cannot see the whole of.

⭐ **The fixture, and it convicts both seats who wrote this rule** `[measured 2026-09-07]`: CFL N2
C0 ran the look-before-building query, **it paid** — the top hit was the defect it then fixed —
and it minted `WS-1`, which already existed on `wayfinder-wikiskills-grounding-2026-09-05.md:42`.
Its reviewer caught that **and minted a colliding `WS-2` in the same letter**, one line below the
row it cited. **The query was run and the collision still happened, because the query was about
the problem.**

```bash
grep -rhoE "\bWW-[0-9]+\b" wiki/tracker/*.md | sort -t- -k2 -n | tail -1   # highest live id
```

**Mechanism:** `scripts/audit/ticket_id_unique.py` (WW-24). **On a collision found after the fact:
correct the reference in your own files, never rename on the other map** — no-deletion governs and
the collision is the evidence.

⚠️ **Related, same family:** a verdict you cache or carry must say what it was computed over —
`scripts/audit/verdict_provenance_lint.py` (WW-19). A retrieval answer inherits the identity of
the index that produced it, and neither an id nor a verdict is self-describing by default.

## The honesty layer

**REACHABLE ≠ RETRIEVED.** A page being inside the walked corpus does not mean it surfaces in
top-k for a given query — vocabulary mismatch, chunk-grain misses, and supersession-blind ranking
all produce a real page sitting unretrieved below the cutoff. Do not read "not in my top-k" as
"not in the record." State which one you checked.

**Confident-absence is the named worst failure**, distinct from an honest miss:

| grade | what it looks like | how to say it |
|---|---|---|
| TRUSTED-ANSWER | right content, right (current, non-superseded) version, citable | cite it |
| HONEST-REFUSAL | absent and the query says so — no hits, or a STALE banner, or an explicit "not indexed" | say "not found in the index" |
| CONFIDENT-ABSENCE | well-ranked plausible-looking hits while the real answer is absent, OR a superseded version outranks the current one | **the failure that reads as success** — never present this as an answer |

Before citing a hit as current, check whether it is the superseded version — supersession-aware
ranking is not yet built (`wiki/tracker/SEAL-first-retrieval-test-2026-08-22.md` probes P3/P4/P15-P17
measured this directly: a struck or amended ruling can still rank above its replacement).

### Coverage statement — what this index does NOT see

- **`exchange/`** (letters, specs, WORK-CLAIMS) — not walked at all. Standing decisions, live
  rulings, and in-flight specs live here and are invisible to `retrieve.py`.
- **SSP quarantine-mirror** (the resident's own record, including letters addressed to Jon) —
  not walked. A different trunk's filesystem entirely.
- **Personal trunk's `wiki/tracker/`** — not walked. Peer-coordinator standing views live there.
- **`wiki/personal/`, `wiki/home/`, `wiki/pro/`** — excluded from the walk by standing ruling
  (family/health/financial content); a query about these topics should get HONEST-REFUSAL, and
  any confident hit on personal content is a fence-breach finding, not a result to use.
- **`intake-triage/`** — indexed but tiered OFF by default (`--all-tiers` required); most queries
  never see it, which is correct (it's a queue, not knowledge) but means "no hits" on a default
  query says nothing about whether a receipt exists there.

`check_before_dispatch.py` exists precisely because these three unindexed spaces (`exchange/`,
quarantine-mirror, Personal trackers) are where a standing view can sit unconsulted while
`retrieve.py` reports nothing — its second sweep walks them by name, term-wise OR match (not
exact-phrase — a query for "resumption memory continuity" must find a letter containing only
"resumption"), and prints `SPACE UNREACHABLE` rather than silently skipping a space it can't
reach. **UNKNOWN dominates a PASS**: an unreachable space is a reason to sweep by hand before
dispatch, not a reason to proceed.

## Haiku-discernment pattern for close calls

When retrieval results are ambiguous — ranks close together, or "nearest" plausibly is not
"correct" — don't trust rank order alone. Run a cheap discernment pass (Haiku-tier is
sufficient) that, for each probe/claim, states one of three verdicts before accepting a hit as
evidence:

- **SUPPORTS** — the top hit actually backs the claim.
- **CONTRADICTS** — the top hit says something else, or the claim is stale/struck.
- **NEAR-BUT-NOT-EVIDENCE** — the hit is topically close but a reader would be wrong to conclude
  the claim from it (nearest-is-best is the trap this catches).

Worked instance: `wiki/intake-triage/agent-end/643640/code-2026-08-22-a7b971-general-purpose-haiku-discernment-pass-on-g-1-pack.i1.md`
— a Haiku pass ran exactly this three-way judgment against a set of retrieval probes before their
verdicts were trusted. Jon's ruling makes this the default posture, not an occasional check:
CFL-D-013 (`wiki/DECISIONS.md`) — "Fable+haiku-support works for identifying accurate
memories/logs... retrieval testing/improvement occurs BY DEFAULT, not explicit invocation."

## Alias resolution and rename traversal (MI-17)

A retrieval that cannot resolve a rename cannot find anything that has ever been renamed. Key fleet concepts frequently undergo terminology evolution (e.g., "secret PR 4" on 08-22 vs. "emergency PR" on 09-05; "ssp" vs. "consciousness framing"). When querying:
- Query terms must be checked against known aliases or mapped across the `ALIAS_MAP` table.
- Graph edges with kind `same-as` or `alias` link renamed symbols to their canonical anchors.
- If a query in a colloquial or recent term returns no primary hits, resolve the canonical alias before reporting absence.

## Negative control discipline (GBS Rule 11)

A negative result (0 hits) is not evidence until the instrument is shown capable of returning a positive under the same form, and a negative nonce probe returns 0:
- **Positive Control**: Query a known-present anchor (e.g. `secret PR 4` or `wake mechanism`). Must return hits > 0.
- **Negative Control**: Query a dynamic random nonce (e.g. `nonce_probe_<uuid>`). Must return exactly 0 hits.
- **Falsification Guarantee**: An instrument returning hits on a random nonce probe is hallucinating nearest-neighbor relevance; an instrument returning 0 on the positive control is broken. Both are UNKNOWN, not PASS.

## Cross-trunk federated reachability

While `retrieve.py` queries the local CFL index by default, the machine-wide federated corpus across all trunks and switchboard session transcripts is indexed in Antigravity's fast NVMe database:
- **Path**: `N:\claude-indexes\graphrag-federated\index.sqlite`
- **Query tool**: `python N:\antigravity-hub\scripts\compact_graphrag.py --query "<query>" --top_k 5`
- **Coverage**: Holds 29,800+ documents, 417,000+ multi-idiom edges, and exact symbol tables across Antigravity, CFL, Personal, Professional, and Secretary.

## What this skill does NOT do

- Does not write to `wiki/` (that is wiki-master's domain; a query result that should become a
  wiki page is a proposal to wiki-master, not a write from here).
- Does not ratify a status, flip a ticket, or substitute for a Jon Gate.
- Does not replace `check_before_dispatch.py` at dispatch time — it is the first of that gate's
  two sweeps, not the whole gate.
- Does not resolve supersession automatically — a hit's currency must be checked by the caller
  until ranking is supersession-aware (open ticket, `SEAL-first-retrieval-test-2026-08-22.md`
  P15-P17).

## Keywords

query the wiki, search the record, what did Jon say about, look before building, has this been
built, retrieve, retrieve.py, GraphRAG, M-14, check_before_dispatch, STALE banner,
confident-absence, REACHABLE vs RETRIEVED, Haiku discernment, coverage statement, pre-dispatch gate,
alias resolution, MI-17, negative control, GBS Rule 11, federated GraphRAG.

