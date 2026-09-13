---
kind: reference
slug: export-30-day-rolling-window
date: 2026-09-04
status: MEASURED
owner: cfl
---

# The claude.ai export stopped being an archive. It is now a 30-day rolling window.

`[measured 2026-09-04 16:1x CDT by opening both exports' conversations.json]`

## Two changes, and the second one is the dangerous one

**Change 1 — DELIVERY.** Anthropic no longer drops a zip on disk. It writes
`manifest-<id>-<ts>-<hash>-<date>.json` carrying **single-use `export_url`s** that
someone must fetch. Three manifests exist and **none had been fetched**: 08-24, 09-02,
09-03. Last zip on disk before Jon fetched one by hand: **2026-08-16**.

**Change 2 — POPULATION, and nothing announced it.** The export used to be CUMULATIVE.

| export | conversations |
|---|---|
| extracted-1786397605 (08-10) | 233 |
| extracted-1786507778 (08-11) | 236 |
| extracted-1786933322 (08-16) | **249** |
| extracted-1788478575 (09-03) | **35** |

**uuid overlap, measured:** in both **24** · only in new **11** · **only in old: 225**.

**The boundary is a DATE, not a project or a size:**

- new export `created_at` range: **2026-08-05 -> 2026-09-03** (29 days)
- the 225 dropped span `updated_at` **2026-03-02 -> 2026-08-17**

**So an export downloaded more than ~30 days after a conversation happens does not
contain that conversation.** The 18-day claude-ai outage did not cost data only because
every earlier export was archived on disk. **A 31-day outage would have been permanent.**

**BOUND, stated because the alternative is not ruled out:** three of the four 09-03
files (`projects-000.zip`, `memories-000.zip`, `light_metadata-000.zip`) are still
undownloaded. A project-conversation split could in principle explain a smaller
`conversations` file. **It does not explain a clean cut at a date**, which is why the
window is the reported reading — but the other three zips are **UNKNOWN, not absent.**

## What this changes

1. **`memories` and `projects` are NEW CATEGORIES the old zips never had.** The
   2026-07-24 sidecar audit recorded `memories.json` as deliberately not captured and
   Jon-gated. It is now a separate downloadable file.
2. **Download cadence is now a RETENTION policy, not a convenience.** Anything not
   fetched inside the window is gone from the export surface.
3. **`scripts/lanes/transcript_corpus_diff.py:33` still points `DEFAULT_OUT` at
   `raw/sessions/claude-ai-transcripts`** — the pre-2026-07-28 corpus root, which is now
   a `POINTER.md`. The L1 move never reached this script. Ticket **EXP-2**.

## What was landed today

`python scripts/lanes/transcript_corpus_diff.py <extracted-1788478575> --out
N:/claude-corpus/cfl/raw/transcripts/claude-ai/_routing/incoming`
-> **32 conversations parsed (30 new, 2 updated), 691 corpus files, feed age 0.0d.**
Both feeds now read `ok` under `scripts/audit/feed_liveness.py`; claude-ai had read
**18.2d STALE** an hour earlier.

## The process finding, which is Jon's and is worth more than the data

**Jon, 2026-09-04 ~16:1x CDT, verbatim, typos his:**

> I am confident taht a cfl or other coordinator or agent has done this before based ont he other files in that folder i can see with my eyes that should ahve been opbiovus to yuou.

**He is right, and the evidence was in the same directory listing this lane had already
printed:** 27 `extracted-*` directories, each produced by
`skills/chat-exporter/scripts/convert-export.py` — **the one canonical extractor, wrapped
by `skills/transcript-parser`, ratified 2026-07-21.** This lane began hand-rolling a
`zipfile` extraction instead of running it. **The tool existed, the tool's OUTPUT was
visibly on screen, and the lane still started building.** [[derive-dont-record]]

**And second, verbatim:**

> I don't understand why you trie dto ask for my help before hand and that sounds like a key all-trunks clarification issue that should be routed through secretary by default not me by default.

**Standing route, adopted: a blocked capability is a SECRETARY question by default, not
a Jon question.** "I cannot do X, can you" goes to the trunk that routes, and reaches Jon
only if no trunk can. **Escalating straight to Jon is the same defect as the 397 rows
marked "needs Jon" — the most comfortable sentence in the program, and nobody audits it.**
