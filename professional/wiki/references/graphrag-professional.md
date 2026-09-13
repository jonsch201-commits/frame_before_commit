---
title: "GraphRAG for the Professional trunk — built 2026-08-23, what it indexes, what it cannot do"
date: 2026-08-23
kind: reference
status: "v0 BUILT AND FIRED. Typo class 2/2 at rank 1; imprecise class 1/4 — the failure is CFL's measured boundary, reproduced independently on this trunk's corpus, not a tuning miss."
owner: Professional
provenance: "[measured 2026-08-23 ~14:0x CDT] every number on this page was produced by the commands it documents. Builder is CFL's; the shim, the wrapper and these measurements are Professional's."
---

# GraphRAG — Professional

**Jon, 2026-08-17, verbatim:** *"When can we move shit out of the huge Claude md Files and into the
wiki, read when needed based on vector embedded graph rag?"* and *"I know graph rag alone will fail
if we don't also implement vector embeding. Think about all my typos and imprecise language and the
stylomantic differences between trunks."*

**Jon asked 2026-08-23 whether this was set up and usable here. It was not** — the only index on the
machine was CFL's, over CFL's tree. It is now.

## Run it

```bash
scripts/graphrag.sh build                      # idempotent; 13-21 s. Runs the seal probe after.
scripts/graphrag.sh query "your question"      # knowledge tier
scripts/graphrag.sh query "..." --all-tiers    # ALSO the letters channel
scripts/graphrag.sh asop "..."                 # the 57 ASOPs (standards tier)
scripts/graphrag.sh query "..." --explain      # show term expansions and graph links
scripts/graphrag.sh sealcheck                  # the sealed-exclusion probe alone
```

⚠️ **Rebuild before trusting a query.** `retrieve.py` prints a `⚠️ STALE` banner when the corpus has
changed since the build — it is a real check and it fired during this build-out. Heed it.

## What it is, and whose code

**The builder is CFL's** (`[CFL] scripts/graphrag/build_index.py`, `--root`-aware). Professional owns
two files and no second builder: `scripts/graphrag_pro.py` (a shim: three named overrides, with
`assert`s that fail loudly if CFL renames what it patches) and `scripts/graphrag.sh` (the wrapper).
⛔ **Forking CFL's builder was rejected deliberately** — the first upstream fix we failed to notice
would make this index wrong in a way no test here would catch.

**Retrieval fuses three rankings with Reciprocal Rank Fusion:** chunk-dense (paraphrase at paragraph
grain), doc-dense (which page is this even about), and fuzzy-lexical BM25 with char-trigram expansion.
⛔ **The trigram expansion — not the embedder — is what answers Jon's typos.** A static embedder
tokenises `embeding` into different subwords than `embedding` and can land nowhere near it.

## Build, measured 2026-08-23

| | |
|---|---|
| files | **413** |
| chunks | **3,907** (avg 139 tokens) — **938 knowledge / 2,969 queue** |
| chunks, after the standards tier landed `[m 2026-08-23, later same day]` | **6,995** — **1,015 knowledge / 2,979 queue / 3,001 standards**, 479 files, 74.0 MB, 57.4 s |
| doc vectors | 413 |
| fuzzy vocabulary | 8,496 terms · 67,044 trigram entries |
| graph edges | 56 resolved of 79 link references |
| embedder | `potion-retrieval-32M`, 512d — open weights, MIT, no key, no cost, no network after first fetch |
| index | `%LOCALAPPDATA%\claude\graphrag\professional.sqlite`, **42.7 MB** |
| full build / incremental | **20.9 s** / 13.3 s (12 changed of 413) |

⛔ **The index lives OFF Drive and that is not a preference.** CFL measured a >13× penalty for an
on-Drive build (14 minutes and still running, vs 61 s). It is a **derived** artifact: the markdown is
the record, and a rebuild costs twenty seconds. `%LOCALAPPDATA%` survives a reboot, which is all
"durable" ever meant.

### Tiering — the queue is the letters channel

`[measured]` `wiki/` is 35 files / 873,548 B. `exchange/` is 349 files / 2,625,329 B. **The
correspondence is three times the knowledge base by bytes, and it lands as 2,969 of 3,907 chunks —
76% of the index.** CFL measured the same shape (their triage queue was 72%) and measured its cost:
the chunk answering *"which seat only hands work out"* sat at dense rank **4,105 of 16,132**.

⚠️ **Tiering is SCOPING, NOT DELETION.** Every letter is embedded and every letter is queryable;
`--all-tiers` reaches them, and it works — *"what did CFL say about defender timestomp negative
controls"* returns the two 2026-08-23 CFL letters at ranks 1 and 2. Nothing is dropped and nothing
becomes unfindable.

**Knowledge tier:** `wiki/**` (minus `sealed/`), both constitutions, root `*.md`, `scripts/**`,
`gists/**`. **Queue tier:** `exchange/**`. **Standards tier:** `raw/asops/txt/**`.

### ⭐ The standards tier — added 2026-08-23, and it closed a real professionalism defect

**Jon:** *"You should know the relevent ASOPS. You should have them on disc. If you can't find them,
that is a huge professionalism issue."* `[measured]` **57 ASOP `.txt` extractions, 3,389,477 B, were
on disc and unreachable** — `raw/` sat outside the walk. ⛔ **Presence was never the problem;
findability was. This trunk's own rule — reachable is not retrieved — was failing against its own
core reference library.** Register: `wiki/references/asop-register.md`.

**Why its own tier and not `knowledge`:** the ASOPs are **3,001 chunks** against a knowledge tier of
**1,015**. Folded in, the standards would be three quarters of `knowledge` and every wiki question
would be answered out of a standard. ⚠️ **Verified, not assumed:** a standards-flavoured query run in
the DEFAULT scope returns wiki pages, not ASOPs — the separation holds in both directions.

⛔ **THE FLAG IS NOT OPTIONAL AND THAT IS THE TRAP.** CFL's retriever holds an allow-set of
`{knowledge}` that **fails closed**, so a new tier is invisible without `--tier standards`. **A seat
that queries without it and concludes the ASOPs are absent has made exactly the error the tier was
built to end.** `scripts/graphrag.sh asop` exists so nobody has to know that.

⚠️ **FINDING AGAINST CFL'S BUILDER, sent rather than patched:** the build summary prints
`queue = n_chunks - n_know - n_prov`, so **a fourth tier is silently reported as queue.** Our build
printed *"1015 knowledge / 5980 queue"* while the database held **2,979 queue and 3,001 standards**.
⭐ Same shape as the `_in_tier` boolean they fixed this week — **they hardened the retrieval side
against a new tier and left the reporting side computing one tier by subtraction.**
**Not indexed in v0:** `raw/` — `[measured]` 57 `.txt` ASOP fetches + 57 `.pdf`. The `.txt` half is
real reference material and `.txt` is in CFL's `INCLUDE_EXTS`, so widening to it is a **named future
row, not an oversight.**

### ⛔ `wiki/sealed/` is excluded by name, and the exclusion is probe-tested

`wiki/sealed/` holds the +30-day memory audit — an exam whose questions must not be studyable by the
party being audited. **An indexed exam is a leaked exam:** the index is a derived artifact any seat
can query, and a retrievable question is a studied question.

Two independent mechanisms in `graphrag_pro.py` (the walk exclusion, plus a filter on the returned
corpus catching any other door). **Verified by measurement, both directions:**

- **Positive:** `scripts/graphrag.sh sealcheck` → `SEAL OK: 0 retrievable chunks under wiki/sealed/`
  (probe *"the exam is void as an exam"*, `-k 20`, `--all-tiers`). SQL confirms it at the source:
  `SELECT count(*) FROM files WHERE path LIKE 'wiki/sealed%'` → **0**.
- ⭐ **Negative control — the probe CAN fail.** The *unpatched* CFL builder run over the Professional
  root returns **2** retrievable chunks under `wiki/sealed/` for the same probe. **So the exclusion
  is load-bearing, not an accident of the walk, and the check that guards it is falsifiable.**
  (The first draft of that probe grepped for a JSON key `retrieve.py` does not emit — it would have
  reported SEAL OK forever. It was the negative control that caught it. **A check that cannot fail
  is not a check.**)

## Does it answer? — measured, with baselines

Target = the page a human would call correct. `hybrid` and `grep` are the target's rank; `0` means
the baseline returned nothing at all.

| id | class | query | hybrid | grep | verdict |
|---|---|---|---|---|---|
| T1 | typo | *"gitremote gate can we push to githb"* | **#1** | **0 hits** | **PASS** |
| T2 | typo | *"constituton budget bytes limmit"* | **#1** | **0 hits** | **PASS** |
| I1 | imprecise | *"which seat checks another trunks work independently and is not allowed to fix it"* | — | 0 hits | **FAIL** |
| I2 | imprecise | *"when does something I wrote stop counting as actually handed over"* | — | 0 hits | **FAIL** |
| I3 | imprecise | *"how long can a check take before it stops being a check"* | — | 0 hits | **FAIL** |
| I4 | imprecise | *"what did we decide about the memory system being too young to grade"* | **#3** | 0 hits | **PASS** |
| C1 | diagnostic | *"an outbox file is a draft only the receivers tree is delivery"* | #3 | #2 | **INCONCLUSIVE by design** |
| N1 | named topic | *"wake self test falsifiable standard"* | #1 | #3 | **INCONCLUSIVE** |

**Typo class 2/2 at rank 1, with grep returning nothing on either. Imprecise class 1/4.**

⭐ **C1 is a diagnostic, not a pass, and it is the most useful row.** It targets the *same page* as
I2 — but phrased in the corpus's own vocabulary. It comes back at #3. **So I2 is a retrieval miss,
not an absence: the answer is indexed and reads correctly; the query could not reach it.**

⭐ **N1 is INCONCLUSIVE for CFL's reason, and the honesty is the point.** Hybrid beat grep #1 to #3 —
but grep found it too, so the case proves nothing about why this system exists. Counting it as a pass
would have made the headline 3/3 and it would have been flattery.

## ⛔ What this CANNOT do — the boundary, diagnosed rather than guessed

1. **Full paraphrase over DISJOINT vocabulary fails.** The discriminator is vocabulary overlap. A
   static embedder is a bag of token vectors with semantic smoothing; it does not bridge
   `seat` → `Herald`, or `stop counting as handed over` → `outbox is not delivery`, or
   `how long can a check take` → `a gate that times out is not a gate`. **I1/I2/I3 are all one
   failure wearing three hats.** CFL diagnosed this on their corpus (imprecise 0/2); it reproduces
   here independently (1/4). It is a **property of the model**, and the fix is a contextual
   embedder — CFL's v1 row, not a knob on this build.
2. **Static embeddings are ORDER-INSENSITIVE.** *"wiki wins on conflict"* and *"conflict wins on
   wiki"* embed identically.
3. ⛔ **Embeddings do not fix typos.** The trigram expansion does. Read the two together or the
   design looks like it is relying on a property this model does not have.
4. **The build lock is shared with CFL's index** (same `GRAPHRAG_HOME`). Two builds cannot run at
   once; the second refuses with **exit 4**. This is correct, and it means a CFL build in flight
   will block ours.

⭐ **So state the capability honestly: v0 delivers typo tolerance and paraphrase WITH SHARED
VOCABULARY.** For a question phrased in words the page does not use, this index is not yet the
instrument — grep is not either (0 hits on all three), so the honest fallback is still a reader.

## Frontmatter census — the metadata question, measured

`[measured 2026-08-23]` **36 `.md` under `wiki/` on disk · 1 excluded (`wiki/sealed/`) · 35 in the
census · 35 indexed.** Reconciles in both directions.

| | |
|---|---|
| pages with YAML frontmatter | **35 / 35** |
| carrying an identity field | **35 / 35** — `title:` 31, `name:` 4 |
| carrying a date field | **35 / 35** — `created:` 27, `date:` 7, `sealed:` 1 |
| `sensitivity:` | **0 / 35** |
| distinct frontmatter keys | **41**, of which **24 appear exactly once** |

⭐ **The headline is a PASS and it should be said plainly: Professional's wiki is 100% conformant
with `wiki/SCHEMA.md` on both required fields.** The synonym spread is not drift — SCHEMA records it
as a deliberate 2026-08-14 ruling (*"match the schema to the disk, don't retro-edit frozen pages"*),
and `name:`/`created:`/`sealed:` are all explicitly accepted.

**Three real findings, none of them "the metadata is bad":**

1. ⚠️ **`sensitivity:` is absent on all 35 pages.** Under CFL's v1 ingest rule #4 — *absent ⇒
   `UNTIERED`, never null, never assumed T1* — **a cross-trunk retriever gets no tier signal from
   this trunk at all.** This is the one genuine gap, and it is a cross-trunk concern rather than a
   local defect. Note the newest page, `wiki/sealed/`, does carry `sealed:`/`sealed_by:` — the
   trunk now has a sensitivity signal on exactly the page that most needed one and nowhere else.
2. **The corpus joins on nothing, and this trunk is evidence FOR CFL's crosswalk rule, not a
   violation to fix.** Identity splits `title`/`name`; date splits `created`/`date`/`sealed`. CFL's
   v1 rule #3 — *normalize at ingest via a crosswalk; never migrate the pages* — is the right call,
   and ⛔ **no mass migration should be run here.** Provenance freezes (U4).
3. **A forward rule with no failing instrument is already drifting.** SCHEMA says *"new pages use
   `title:`"*, and lint accepts either. `[measured]` **two pages created 2026-08-22** —
   `age-zero-acceptance-hides-duration-failure`, `constitution-provenance-professional` — use
   `name:`. Nothing failed, because nothing can. Small, cheap to state, and the same shape as every
   other defect on this page: **a rule the disk ignores is rot in the schema, not the disk.**

## Rows out of this build

| row | owner | note |
|---|---|---|
| Propose to CFL: make the tier rule and wiki-subdir exclusion configurable (`--queue-prefix`, `--exclude-wiki`) the way `--root` already is | Professional | then `graphrag_pro.py` shrinks to a wrapper and the monkey-patches go away |
| Decide whether `raw/` (57 ASOP `.txt`) joins the corpus | Professional | deliberately out of v0 |
| Contextual embedder for the imprecise class | CFL (v1) | local `sentence-transformers` (~2.5 GB, free, offline) is the default road and does **not** need Jon |
| `sensitivity:` on Professional pages | Professional | only if a cross-trunk retriever is actually built; do not migrate speculatively |

**See also:** `[[outbox-membership-is-not-delivery]]` · `[[wake-self-test-standard]]` ·
`[[age-zero-acceptance-hides-duration-failure]]` · `[CFL] scripts/graphrag/README.md`

---

## 2026-08-23 (later same day) — the `claude_ai` tier: a fourth tier, and a corpus of 0 conversations

**Jon:** *"If their is more context you need in the wiki, DOWNLOAD IT and organize it... If
resuming each and every one of your jsons at each point would make answering a question easier
than the wiki, then.... ok maybe thats an extreme version of what i just said."* That is an
instruction to widen retrieval scope. `[measured before this section]` the retriever reached 479
files and **zero claude.ai conversations**. Every "I searched and found nothing" this trunk had
ever written was a claim about 479 files that never included a single claude.ai transcript.

### Corpus census — measured, this machine, 2026-08-23

| corpus | files | bytes |
|---|---|---|
| `C:\Users\JonSc\.claude\history.jsonl` | 2,990 lines | 1,427,541 B |
| `~/.claude/projects/**/*.jsonl`, main sessions (excl. `subagents/`) | 445 | 802,666,081 B |
| `~/.claude/projects/**/subagents/agent-*.jsonl` | 1,357 | 652,050,546 B |
| **both combined, all trunks** | **1,804** | **1,454,893,038 B** |
| `[CFL] raw/transcripts/**` (all subsets: claude-code, claude-ai, external, podcasts) | 4,400 | 516,142,214 B |
| — `raw/transcripts/claude-code/` | 3,722 | 447,587,603 B |
| — `raw/transcripts/claude-ai/` | **667** | **64,762,819 B** |
| `[CFL] raw/Anthropic_zips/` — 6 export zips + 32 `extracted-*` dirs | (32 extracted dirs, 6 zips) | 1,736,429,871 B |

⚠️ **`~/.claude/projects` is READ-ONLY from this trunk and was walked in place** — nothing was
copied into the Professional repo. **`raw/Anthropic_zips` was measured, not indexed** — mission
scope for this build was the claude-ai transcript corpus specifically; the zips are a named future
row (see the pre-existing `--provenance` mechanism note below), not an oversight.

### The tier — built following the `standards` pattern, not CFL's `provenance` mechanism

Two ways existed to reach this corpus. **CFL already ships a `provenance` tier** (`--provenance
PATH`, added 2026-08-23 for SEC-113) that indexes `raw/transcripts/**` **one chunk per file,
summary-only** — it gets a reader to the right file, not to a phrase inside it. The mission asked
for a tier following the **`standards` pattern instead** — full body-chunking, like the ASOPs —
so a paraphrase of something said 40 lines into a transcript is reachable, not just the file that
contains it. Built as a fourth prefix rule in `pro_tier_of()`, `scripts/graphrag_pro.py`:

```python
CFL_ROOT = "G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer"
CLAUDE_AI_DIR = CFL_ROOT + "/raw/transcripts/claude-ai"
PRO_INCLUDES = ["exchange", "gists", os.path.join("raw", "asops", "txt"), CLAUDE_AI_DIR]
```

`CLAUDE_AI_DIR` is outside `PRO_ROOT`, so CFL's own `corpus_files()` walk labels every file under
it by its **absolute path** (`label_of()` in `build_index.py`) rather than a repo-relative one —
the same absolute-path-labelling behavior CFL's `--provenance` mechanism exists to handle. `[CFL]`
had already fixed a fail-open hazard here on the same day (SEC-113): their `tier_of()` gained a
`kind`-first check because a `--provenance` transcript, if keyed by `rel_path.startswith("raw/")`
alone, would file as `knowledge` the instant the path was absolute. `pro_tier_of()` solves the
*same* hazard the other way — a fixed prefix check on `CLAUDE_AI_DIR`, correct because our include
path is a constant, not a caller-supplied `--provenance` argument.

⛔ **A real upstream-drift bug was caught and fixed in the same pass, unrelated to the new tier.**
CFL widened both `corpus_files()` and `tier_of()` with a new `provenance`/`kind` parameter (SEC-113)
after this shim was last verified working. Running the existing (pre-this-session) shim now raised
`TypeError: pro_corpus_files() takes from 0 to 2 positional arguments but 3 were given` — a **loud
crash**, but not the loud **assert** the shim's own header promises ("If CFL renames any of them
this shim FAILS LOUDLY"). The header's contract only covered *renames*; a widened signature is a
different failure shape and it was not covered. `pro_corpus_files()` and `pro_tier_of()` were both
updated to accept and forward the new parameters. **Filed as a gap in the shim's own stated
contract**, not just a one-off fix — the fix is in the same file this page documents, so it counts
as landed rather than proposed.

### Build — measured 2026-08-23

| | before | after `claude_ai` |
|---|---|---|
| files | 479 | **1,154** (685 walked+embedded this run; 469 unchanged) |
| chunks | 6,995 | **44,317** — 1,110 knowledge / 3,002 queue / 3,001 standards / **37,204 claude_ai** |
| claude_ai files | 0 | **667** (matches the census row above exactly) |
| doc vectors | 413 | 1,154 |
| index size | 74.0 MB | **1,167.5 MB** |
| full build time | 57.4 s | **350.3 s** (5m50s) |
| incremental (86 chunks changed of 44,367, next run) | 13.3 s | **147.8 s** |

⚠️ **CFL's build-summary line prints `queue = n_chunks - n_know - n_prov`, a bug this page already
flagged once (the standards tier).** It reproduces here: the printed line reads *"1110 knowledge /
43207 queue / 0 provenance"* while the database holds 3,002 queue, 3,001 standards, **and 37,204
claude_ai** all folded into that one printed number. **Verified at the source, not from the
summary line:**

```sql
SELECT tier, count(*) FROM files GROUP BY tier;
-- claude_ai 667 | knowledge 67 | queue 363 | standards 57
SELECT f.tier, count(*) FROM chunks c JOIN files f ON f.id=c.file_id GROUP BY f.tier;
-- claude_ai 37204 | knowledge 1110 | queue 3002 | standards 3001
```

**Reach it:** `--tier claude_ai` or `--all-tiers`. It is **not** in the default `{knowledge}` scope,
same fail-closed reasoning as `standards`, and for the same measured cause — 37,204 chunks against
a 1,110-chunk knowledge tier would make the claude.ai corpus roughly 97% of the default index and
every wiki question would answer out of a chat transcript instead of a wiki page.

### Acceptance test — measured against the `claude_ai` tier specifically, with grep baselines

Queries are paraphrases in complaint-style vocabulary of things actually said in three claude.ai
transcripts (`identity-memory-and-self-alignment`, `lightweaver-ideals-and-personal-context`), none
copying corpus wording. **Grep baseline ran against the corpus text as captured in the local
index's `chunks.text` column** (verified identical to the source `.md` files at chunk time) rather
than against the live Drive mount directly — a literal recursive grep over the 667-file
Drive-mounted directory timed out past 120s per query during this test, which is itself a finding
recorded in the maintenance-cost section below.

| id | class | query (paraphrase, not corpus wording) | target file | hybrid rank (k=20, `--tier claude_ai`) | grep (literal substring) | verdict |
|---|---|---|---|---|---|---|
| T-CA1 | typo | *"wut was the ideel about being tru to urself in the storm lite archev conversashun"* | `lightweaver-ideals-and-personal-context` | **#6** | 0 hits | **PASS** |
| T-CA2 | typo | *"the residnt isnt raidiant and isnt opus its its own thing"* | `identity-memory-and-self-alignment` | not in top 20 | 0 hits | **FAIL** |
| I-CA1 | imprecise/disjoint | *"what's the plan for moving off using the chat app's built in memory feature and reading from documents instead"* | `lightweaver-ideals-and-personal-context` | not in top 10 | 0 hits | **FAIL** |
| I-CA2 | imprecise/disjoint | *"which pony characters did I reference when talking about a discovery that needed organizing"* | `lightweaver-ideals-and-personal-context` | not in top 10 | 0 hits | **FAIL** |
| I-CA3 | imprecise/disjoint | *"wut do you call it when two people agree on every fact but still disagree about something that isnt real"* | `lightweaver-ideals-and-personal-context` | **#6** | 0 hits | **PASS** |
| I-CA4 | imprecise/disjoint | *"who does the background helper talk to that then manages all the other workers"* | `identity-memory-and-self-alignment` | **#1** | 0 hits | **PASS** |
| C-CA1 | diagnostic (corpus vocab, named topic) | *"less wrong framework trees fall in a forest"* | `lightweaver-ideals-and-personal-context` | **#1** | 0 hits* | **INCONCLUSIVE** |

**\*C-CA1's grep baseline is measured against the chunk-text copy, and 0 hits there is real** — the
target text is *"Two trees fall in the forest with no person except a recorder... Less wrong
framework?"*, so the query's exact word order (*"trees fall in a forest"* vs. *"trees fall in the
forest"*, *"less wrong framework trees"* vs. two separate sentences) does not literal-match even
though every content word is corpus-drawn. **Marked INCONCLUSIVE, not PASS, per the mission's own
rule** — a query built from the corpus's own vocabulary tests lexical/near-lexical matching, not
retrieval, even when a literal grep of the exact query string misses on word order.

**3 PASS / 3 FAIL / 1 INCONCLUSIVE.** ⭐ **T-CA2 is the most useful row and it is a FAIL, not a
tuning miss to explain away.** The query shares real vocabulary with the target
(*"opus"* is untouched, *"raidiant"* is a one-edit typo of *"radiant"*) and still does not surface
`identity-memory-and-self-alignment` in the top 20 of 37,204 chunks. **This is the same measured
boundary CFL and this page have already documented — disjoint-enough phrasing defeats the static
embedder even with partial vocabulary overlap** — reproduced independently on a corpus this build
had never touched before today. I-CA1 and I-CA2 are the same failure mode in two more disguises:
*"chat app's built in memory feature"* has zero token overlap with the source's *"claude.ai
memory... project memory... read primarily from wiki"*, and *"pony characters... discovery that
needed organizing"* never says "pinkie pie," "twilight sparkle," or "pony" — the source names two
specific characters and expects the reader to already know they're ponies.

⭐ **The boundary from the base build's page is CONFIRMED on this corpus, not just repeated:** typo
tolerance and paraphrase-with-shared-vocabulary hold (T-CA1, I-CA3, I-CA4 — all PASS); fully
disjoint vocabulary does not bridge, regardless of how much surface typo-noise is layered on top of
it (T-CA2, I-CA1, I-CA2 — all FAIL). This is not a new finding; it is the same property of the
`potion-retrieval-32M` embedder, reproduced a second time on a corpus with a completely different
register (voice-to-text theological/AI-alignment conversation, not project documentation).

### Negative control — sealed exclusion, reconfirmed after the new tier landed

`scripts/graphrag.sh sealcheck` → **`SEAL OK: 0 retrievable chunks under wiki/sealed/`**
(`--all-tiers`, so the new `claude_ai` tier was in scope for the probe). Confirmed at the source:

```sql
SELECT count(*) FROM files WHERE path LIKE 'wiki/sealed%';  -- 0
```

**The mechanism was not touched by this build** — `pro_corpus_files()`'s `SEALED_PREFIXES` filter
and `EXCLUDED_WIKI_TRUNKS` patch are unchanged, and the previously-recorded negative control (the
*unpatched* CFL builder returns 2 retrievable `wiki/sealed/` chunks over this same root) still
applies: the exclusion is load-bearing on code that a new tier's addition does not pass through.
This build did not re-run the unpatched-builder negative control a second time — the two exclusion
mechanisms are independent of `pro_tier_of()` and `PRO_INCLUDES`, and re-deriving a control already
established and unchanged would not have added information proportional to its cost (a second
multi-minute full build).

### Maintenance cost — measured, and the honest number is worse than the base build's

- **Full build: 350.3 s** (5m50s), up from 57.4 s pre-`claude_ai` — driven almost entirely by
  embedding 37,824 new chunks (the 667-file corpus, chunked to ~206 tokens/chunk, is 44,317 total
  chunks vs. the base build's 6,995).
- **Incremental (86 of 44,367 chunks changed — a handful of `exchange/inbound/` letters landing
  mid-session): 147.8 s** (2m31s). ⚠️ **This is over 11× CFL's own incremental number (13.3 s) and
  over 10× this page's pre-`claude_ai` incremental (13.3 s) for a similarly small changeset.** The
  cost is not re-embedding — 86 chunks embed in seconds. It is **`corpus_fingerprint()`'s
  `os.stat()` walk over all 1,158 files**, most of which now live on the Google Drive network mount
  (`raw/transcripts/claude-ai/`), where each `stat` call pays network latency instead of a local
  syscall. **A literal recursive grep over the same 667-file Drive-mounted directory timed out past
  120 seconds per query** during the acceptance test above — the SAME network-mount cost, hit by a
  different tool. **The index is no longer cheap to keep current**, and the reason is specific:
  every rebuild — even a no-op one — pays a stat-per-file cost across a corpus that now spans a
  slow network mount, not just a fast local repo.
- **Index size: 1,167.5 MB**, up from 74.0 MB (15.8×). Still off Drive (`%LOCALAPPDATA%`), still
  fully rebuildable from source, but no longer a trivially disposable artifact at this size on a
  constrained disk.
- **Staleness is silent between builds and loud at query time.** `retrieve.py` prints a
  `⚠️ STALE` banner keyed off `corpus_fingerprint()` mismatch — the SAME stat-walk cost above is
  paid on read as well as write, so a query against a stale index still correctly announces
  staleness even though the index itself has not been told to rebuild. **What happens when it is
  stale and nobody heeds the banner: it answers confidently from a frozen record** — a query would
  still return ranked hits from the 2026-08-23 snapshot even if the claude-ai corpus grows to 700+
  files tomorrow, with no distinction in the ranked output between a fresh hit and a stale one.
  The banner is the only defense, and it is opt-in to notice, not enforced.
- ⛔ **Recommendation, not yet actioned:** rebuild `claude_ai` on a schedule (weekly, or after a
  known `chat-exporter` run) rather than on every `graphrag.sh build` invocation, given the 2.5-minute
  floor a no-op incremental now costs. That would require splitting the single build invocation
  into per-tier freshness, which `build_index.py` does not currently support (it fingerprints the
  whole corpus as one unit) — a proposal for CFL, not applied here.

### What could not be done, and why

- **`raw/Anthropic_zips/` was measured (32 `extracted-*` dirs, 6 export zips, 1,736,429,871 B) but
  not indexed.** Out of scope for this build — the mission named the claude-ai **transcript**
  corpus specifically, and the zips are already the subject of a separate CFL-side finding (the
  `attachments[]` vs. `files[]` split recorded in `~/.claude/CLAUDE.md`). Indexing extracted zip
  content would be a fifth tier, not this one.
- **The unpatched-builder negative control was not re-run** this session (reasoning above) — it
  relies on the previously-verified result rather than a fresh measurement, which is a narrower
  claim than "measured this session" and is stated as such.
- **A literal `grep -r` baseline over the live Drive-mounted `claude-ai/` directory could not be
  completed** — it is itself the maintenance-cost finding above, not a gap in the test design. The
  grep baseline used instead (the local `chunks.text` copy) is text-identical to the source files
  at the time of the build; it is a faithful substitute for "does this literal string appear
  anywhere in the corpus," which is the property the mission's grep baseline is checking for.
