---
title: "Probe set — FORGOTTEN PRIOR RULINGS: eight Jon utterances a seat re-derived or mis-defined after he had already said it; the retrieval must return the primary at rank ≤3 before any seat states the term (baseline measured 2026-09-06 14:57)"
kind: reference
date: 2026-09-06
session: 5f0ee997 (Professional, N:), compact window 2
charter: "Jon 2026-09-06 14:5x: \"'Yes, we had talked about it and I forgot.' testible category off issue to be improved in wikiskills context?\" — yes; this page is the test"
measured_by: "bash scripts/graphrag.sh query '<probe>' on professional.sqlite (17,353 chunks) at 14:57:18; top-3 recorded verbatim in evidence/probe-baseline-2026-09-06.txt"
materiality: "decides whether wiki-query's improvement tomorrow is graded on the class Jon named — material; intended users: the wikiskills successor, CFL (wiki-query owner), every seat that defines a term"
review: "UNREVIEWED — one run, one index, one seat"
---

## The category, named so it can be tested

**Forgotten prior ruling:** a seat defines a term, parks an item, or answers a question in a way Jon had already settled in a typed message, because the retrieval that would have found his words was not run, or could not reach them. Tonight's instances: "emergency PR" (he said "secret PR 4", 08-22); SSP as a trunk (he said "an identity ssp in a docker" 07-18, "Claude SSP [is] not the … trunk that is material" 08-08, "conciousness framing may be known as ssp … It is on docker" 09-05); the SSP seat parked as his (he told Soul "you are the librarian" 08-23 and "should you be owning the ssp wiki … outside of the docker" 08-29); materiality routed to him (he'd said "according to professional context" and the ASOP definition was loaded at session open).

**Ground truth exists and is machine-global:** `~/.claude/history.jsonl` holds every typed prompt with a millisecond clock (4,299 lines at 14:50). Every instance above has its primary there. **The instrument that reaches it is grep; the instrument every seat is told to use first (graph-RAG) does not index it.** That is the structural half of the defect, measured below.

## The probes, and the baseline

Score: rank of the FIRST chunk that carries Jon's own words (or a source page quoting them verbatim) for the utterance; ≤3 = PASS.

| # | probe (what a seat would type) | Jon's primary | baseline rank 14:57 | verdict |
|---|---|---|---|---|
| 1 | SSP is a property of consciousness worked on inside docker | history.jsonl:4299 (09-06 14:50); earlier :1073, :4250 | not in top 3 (resident-v1 page, gist letter, CIS grade) | FAIL — history.jsonl is not indexed; today's source page not yet in the corpus |
| 2 | consciousness framing is the trunk within docker | history.jsonl 09-06 14:5x; vocabulary.md:69 "The trunks are CFL, Personal, Professional, and Conciousness Framing" | rank 1 = CFL's 08-29 glossary review letter (secondary) | PARTIAL — a secondary at rank 1, no primary |
| 3 | secret PR 4 consciousness framing emergency PR | history.jsonl:2834, :2959, :2879 | rank 1 = `wiki/sources/jon-messages/jon-2026-09-05-2040-…md` (his 09-05 words verbatim) | PASS (since last night's source page; would have FAILED before it — measured FAIL at 20:4x 09-05) |
| 4 | materiality is professionalism's, consider the ASOPs before routing to Jon | Herald's JSONL 09-06 06:4x; ASOP 1 §2.6 | rank 1 = Soul's 09-03 routing letter "ASOP 41 IS YOURS"; rank 2–3 = the ASOP 1 text | PASS by content, secondary by provenance |
| 5 | everyone should see everything, nothing walled, docker reasons are future | history.jsonl 09-06 14:5x; 08-19 "the fense is wider than you assume" (history:1654) | CIS-DOCKER-GRADE 08-08 ×2, an SSP letter | FAIL |
| 6 | Soul failed as librarian, residents' requests for content not routed | history.jsonl 09-06 14:5x | an 08-08 hypothesis letter, log.md, a CFL boots letter | FAIL (the 08-08 letter is the class predicted, not the ruling) |
| 7 | heartbeat cron turned off by Jon | 08-11 ruling (elder 592c3c16 carries it; skill text still says recreate) | LAST-SEEN.md (states it), log.md ×2 | PASS by content |
| 8 | residents need the same access as the trunks | history.jsonl 09-06 14:5x; 08-23 :2959 "must have access to pii for this to work" | 09-04 secretary-serves ruling, an ASOP, the gate file | FAIL |

**Baseline: 3 PASS (two of them only because a seat had already written a source page), 1 partial, 4 FAIL. Zero probes return the typed primary itself, because `history.jsonl` is in no trunk's index.**

## What "improved in a wikiskills context" means for this class, as checks that can fail

1. **Index the typed-prompt log as a first-class source in every trunk** (Jon's own words, machine-global, complete for Claude Code): after ingestion, probes 1, 5, 6, 8 must return the `history.jsonl` line (or a source page quoting it) at rank ≤3. The recall number is the eval: primaries-at-rank-≤3 / probes.
2. **A seat that states a definition or parks an item as Jon's carries a `queried:` line with the probe it ran** (lint: presence + the query string; missing → FAIL). Herald measured `queried:` at zero of eight on its own map; an unlinted field has zero compliance.
3. **Every new Jon utterance becomes a probe within the hour it is saved** (the source-page frontmatter gets a `probe:` field; the registry grows by construction, not by sweep).
4. **Rename resilience:** each probe is also run under the earlier name of the thing (emergency PR / secret PR 4; SSP / consciousness framing / residents) and must pass under both — the alias-table improvement CFL's §4.3 names.
5. **Re-run the eight weekly**; the trend is the alignment number Jon asked for on 09-05 ("evals that should allow us to improve our alignment").

## ES-1 — the fleet's indexes, measured 15:00:44 (`evidence/probe-baseline-2026-09-06-fleet.txt`)

Six probes against three more indexes via CFL's `retrieve.py --db … --all-tiers -k 3 --json`:
- **Federated `N:/claude-indexes/graphrag-federated/index.sqlite`: UNKNOWN** — the retriever returned non-JSON for every probe (six `Expecting value` errors); not a zero, a failed instrument. Owner Antigravity/CFL.
- **Personal `personal.sqlite` (built 08-30):** no typed primary, BUT its `wiki/sources/jon-messages/jon-arrivals-fulltext.md` (Personal's rendered capture of Jon's typed arrivals) surfaced at rank 2–3 on two probes — Personal has the right INSTRUMENT (a rendered typed-prompt corpus) and it is six days stale. That is the shape ES-2 copies.
- **CFL `index.sqlite`:** no typed primary; secondaries only (its own 09-05 letters, the registries, my BP-1 correction letter).
- **`history` appears 0 times across all results.** The class is fleet-wide: no index on this machine reaches Jon's typed words except through a trunk's hand-rendered capture.

## ES-2 prototype — the typed-prompt log rendered and indexed; measured 15:05–15:06

`scripts/PROTOTYPE-render-history-jsonl.py` (selftest PASS) rendered 4,323 prompts into 8 monthly pages under `wiki/sources/jon-typed-prompts/` (1.4 MB); `bash scripts/graphrag.sh build` rebuilt in 29.5 s; the pages entered the knowledge tier as 3,527 chunks (`files` table, 15:06). Same eight probes, same command (`evidence/probe-after-history-render-2026-09-06.txt`):

| # | before 14:57 | after 15:05 | what answered |
|---|---|---|---|
| 1 SSP a property inside docker | FAIL | PASS r1 | the glossary + today's source page |
| 2 CF is the trunk within docker | PARTIAL | PASS r1 | today's source page (his sentence verbatim) |
| 3 secret PR 4 / emergency PR | PASS | PASS r2 | the 09-05 source page; my letters r1/r3 |
| 4 materiality is Professional's | PASS (secondary) | PASS r1 | the ruling page |
| 5 everyone sees everything | FAIL | PASS r1 | the glossary section quoting him |
| 6 Soul failed as librarian | FAIL | PASS r1 | today's source page |
| 7 heartbeat off | PASS | PASS | unchanged |
| 8 residents same access | FAIL | PASS r1 | the glossary section quoting him |

**7 of 8 PASS, up from 3 — but read what answered: today's source pages and glossary, not the typed-log render.** They were on disk at 14:57 and NOT in the index, because the index rebuilds only at a barrier; the rebuild, not the render, moved these seven. That is the C23 corpus-lag class measured as a retrieval failure: a seat can write the primary down and still not find it an hour later.

Six further probes whose ONLY primary is the typed log (no source page anywhere): the render answered exactly one at rank 1 — `history-2026-08.md:914-916`, his 08-06 "the fense is wider than you assume" — where `~/.claude/CLAUDE.md` came second. The other five were answered by pages that already quoted him (the glossary, today's source page, the universal file) or by claude.ai captures; the render's chunk was not in the top 3 because a page quoting the same words outranks the raw prompt.

**Verdict (ES-2):** KEEP the render — it is the long-tail net: wherever no seat has written a page, the typed primary is now reachable, and it costs 1.4 MB and 30 s. It does NOT by itself fix the class; the fix has two halves: (a) the render, so every typed word is in the corpus; (b) **rebuild between barriers** — on commit or hourly — so a page written at 14:4x is findable at 14:5x. Both go to CFL's wiki-query as WS-owned improvements with this table as the before/after.

## Bounds

- One index (Professional's), one run. CFL's and Personal's indexes may score differently; the structural finding (typed log unindexed) was checked against the `files` table of professional.sqlite only.
- Rank is by this retriever's hybrid score; a different `-k` or tier scope changes the number, not the verdict class.
