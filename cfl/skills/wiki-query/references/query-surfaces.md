---
kind: skill-reference
skill: wiki-query
slug: wiki-query-surfaces
status: LIVE
date: 2026-09-12
---

# What there is to query, what each surface covers, and the bound every answer inherits

**Jon, 2026-09-12 22:43:33 CDT, `~/.claude/history.jsonl:5068`, verbatim (typos his):**
*"'the third skill' is the graph query skill, i have assumed this is needed"* — and, on the same
evening, **"query all graphs"**. This page exists because "query the graph" is under-specified: there
is more than one graph, each covers a different slice, and **an answer is only as wide as the surface
it was asked of.**

## 1. There is not one graph

| surface | what it holds | how to reach it |
|---|---|---|
| **this trunk's index** | this tree's wiki, exchange, scripts, and its own raw record | `scripts/graphrag/retrieve.py` |
| **the federated index** | every trunk's slice, built from the shared corpus mirror | `--db` at the federated path; built by `compact_graphrag.py --all-trunks` |
| **a derived resident index** | a narrowed copy with a deny-list applied | `derive_resident_index.py` output |

⛔ **A derived copy can never be richer than its source.** If a narrowing copy is missing something,
adding it to the copy is impossible — the fix belongs upstream. `[measured 2026-09-12: a resident copy
was 20 days stale because nothing re-derived it; it never errored, it answered from three weeks
earlier.]` **Check a derived index's mtime against its source before trusting it.**

## 2. The default scope is a small fraction of the index, and a zero inside it means nothing

`[measured 2026-09-12, this trunk]`

| tier | files | chunks | share |
|---|---|---|---|
| `provenance` — the raw record | 12,693 | 394,539 | **77%** |
| `queue` — intake, archive | 1,965 | 73,742 | 14% |
| **`knowledge` — the DEFAULT** | 4,580 | 46,126 | **9%** |

⛔ **A query that returns nothing has, by default, searched 9% of the index.** Widen with `--all-tiers`
or `--tier provenance` before concluding anything. **Retrieval prints this bound on every run** — read
it. It also prints, explicitly, that Jon's ~4,900 typed prompts sit in `provenance`, so **a zero in the
default scope is not absence from his record.**

## 3. Fidelity is not uniform, and the graph will not tell you unless you ask

`[measured 2026-09-12]` **2,909 provenance transcripts are held as ONE ~2,200-character summary each:
550.6 MB of source represented by 6.4 MB of index — 1.17%.** The rule is age: a provenance file older
than fourteen days is reduced.

⚠️ **So a hit on an old transcript is a hit on a summary of it.** You can quote a summary as a summary;
you cannot quote it as the conversation. **Open the file.** Which requires:

- the cited path to resolve — `[measured: 32.6% of cited paths did not resolve on 2026-09-12; the
  cause was an unpopulated mirror root, and 98.2% of them were alive on another disk the whole time]`;
- the file to still exist — `[130 did not; 72 of those are unrecoverable, their full text gone]`.

⭐ **Retrieval now flags this per result: silence when the file is at its cited path,
`⚠ ROOT MOVED -- readable at <path>` when it resolves elsewhere, `⛔ PATH GONE` only when neither.**

## 4. Reachability is the standard, and it is currently ~80%

Jon, 2026-09-12 ~23:2x, verbatim (typos his): *"i think it might be fine if the graph doesn't have raw
conversations in it if our ontologies and synthesis are good enough, and so long as the raw
conversatrion is still *reachable* via the graph - from key concepts etc."*

That makes reachability testable, and `[measured]` it holds for about four fifths:

| clause | result |
|---|---|
| the summary's cited path resolves | **98.2%** |
| something in the knowledge tier names the file | 47.4% by filename, +32.4% by session id only |
| ⛔ **pointed at by nothing** | **20.2% — 587 transcripts** |

⛔ **587 reduced transcripts are islands: reachable only by guessing a phrase they contain.** When a
query about an old topic comes back thin, that is a live candidate cause — **not evidence that the
record is thin.** Say "not reachable from any concept page I can find", never "it isn't there."

## 5. The one-line rule

⭐ **EVERY RESULT INHERITS THREE BOUNDS: the SURFACE you asked, the TIER you scoped, and the FIDELITY
of the hit.** State them with the answer. An answer without its bounds is a guess wearing a citation.
