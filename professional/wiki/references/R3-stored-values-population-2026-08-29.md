---
name: R3-stored-values-population-2026-08-29
description: "R-3 resolution asset (dated, frozen by design): the enumerated population of stored values on this wiki's live reference surfaces that should become printed commands — 56 files scanned, 19 clear candidates, 5 already false at enumeration time."
date: 2026-08-29
kind: reference — dated research artifact; the numbers ARE the finding and are deliberately frozen
status: CLOSED with its ticket (R-3, wayfinder-leading-from-the-rigor-seat-2026-08-29.md)
sensitivity: T1
audience_tier: any
reader_token_cost: ~1400
provenance: "[relayed — Explore subagent, fired 2026-08-29 14:2x by session 20690e2b; enumeration commands printed below per print-the-population]"
---

# R-3: the stored-values population, enumerated

**Scope:** `wiki/concepts/`, `wiki/references/`, `wiki/index.md`, `wiki/SCHEMA.md` — the live
reference surfaces. Excluded by design: `log.md`, `tracker/`, `sources/`, `sealed/`,
`intake-triage/` (historical records may store values).

**Population, printed:** 56 files = 42 `concepts/` + 12 `references/` + `index.md` + `SCHEMA.md`.

```bash
cd wiki
find concepts references -type f -name '*.md' | sort   # 54
ls index.md SCHEMA.md                                   # +2 => 56
grep -rnE '\b[0-9]+ (files?|pages?|chunks?|lines|bytes|B|KB|MB|checks?|commits?)\b' concepts references index.md SCHEMA.md
grep -rniE '(currently|as of today|now|still) (is|are|has|have|holds|contains|stands)' concepts references index.md SCHEMA.md
```

## (a) The 19 clear candidates — stores a derivable current fact

| # | file | stored value | derive with | state at enumeration |
|---|---|---|---|---|
| 1 | `SCHEMA.md` sources row | "RESERVED, currently empty by design" | `ls wiki/sources/ \| wc -l` | ⛔ ALREADY FALSE — 2 files |
| 2 | `SCHEMA.md` standing invariants | four numbered lint checks | `grep -cE '^check_[a-z_]*\(\) \{' scripts/lint.sh` | ⛔ STALE — 15 on disk |
| 3 | `SCHEMA.md` date-field note | "14 of 17 pages, measured 08-14" | `grep -lE '^created:' concepts/*.md \| wc -l` | STALE — 42 pages now |
| 4 | `conformance-professional.md` git row | HEAD `aa1c8db` | `git rev-parse --short HEAD` | ⛔ STALE |
| 5 | same, wake-note row | "4,987 B (budget 6,144)" | `wc -c WAKE.md` | ⛔ STALE |
| 6 | same, instruments row | "lint.sh — 4 checks" | as #2 | ⛔ STALE — 15 |
| ⭐ **20** | `cross-trunk-wiki-peer-review-2026-08-23.md` Professional row | **"`lint.sh` 9/9 checks, all 9 selftest-proven failable"** | as #2, and the banner `scripts/lint.sh` prints | ⛔ **STALE — 22 checks, 20 proven `[m 2026-08-30]`.** ⭐ **Found by a /dream cold probe on 08-30 asking the wiki *"how many checks exist?"* — the wiki's only stored total was this one, and it was seven days and thirteen checks out of date. THIRD instance of this same stored value going stale in one register (see #2 and #6), which is what promotes it from an error to a CLASS: the check count is the most-copied derivable fact in this trunk.** ⚠️ **And the sentence naming the class — *"a record can be true and stale"* — was DELETED from `WAKE.md` on 08-29 to pay a byte budget, and returned the next day as two fresh measured instances.** |
| 7 | same, transcript row | one 08-15 session id | `ls -t <proj>/*.jsonl \| head -1` | frozen |
| 8 | `index.md` concepts table | ~44 `[[slug]]` rows | `python scripts/index_gen.py` — INDEX-DERIVED **is** the printed form | ⚠️ 44 links vs 42 files |
| 9 | `index.md` frontmatter | "session 1 · updated 08-15" | `git log -1 --format=%cd -- wiki/` | 2 weeks stale |
| 10 | `index.md` standing gates | "No git remote" stored | `git remote -v` (lint C-gate prints it) | true but stored |
| 11 | `index.md` open items | tracker state duplicated | point at `wiki/tracker/tracker.md` | moved on |
| 12 | `index.md` correspondence | 08-07 outbox list | `ls exchange/outbox/` | 431 files now |
| 13 | `asop-register.md` | "57 PDFs and 57 txt" + currency table | `ls raw/asops/txt/*.txt \| wc -l`; `scripts/fetch_asops.sh` | page names its own decay |
| 14 | `graphrag-professional.md` build table | 413 files / 3,907 chunks / 42.7 MB | `scripts/graphrag.sh build` or a `--stats` print | STALE |
| 15 | same, tiering | "wiki 35 files / exchange 349" | `find`/`du` one-liners | ⛔ ~2× stale (71 / 431) |
| 16 | same `:194` | "sensitivity absent on all 35" | `grep -L '^sensitivity:' … \| wc -l` | stale denominator |
| 17 | `machine-record-sync.md` §1 | backup health row | `Get-ScheduledTaskInfo` + `LAST-RUN.txt` | daily-changing |
| 18 | same §2 | "35 dirs = 35 dirs" | diff two `ls \| wc -l` | decays daily |
| 19 | `supersession-trail.md` | checked-in generator output incl. `WAKE.md:47 "Models: main loop Fable"` | `bash scripts/derive-supersessions.sh` | ⛔ carries the exact retired value the type specimen removed |

**Highest-value swaps: #1, #2/#6, #5, #8, #13, #15, #19 — one-liners each, five already wrong.**

## (b) Borderline — dated stamps on surfaces whose function is current-state

`fable-mirror-grounding-professional.md` (load-bearing ⛔ claim resting on stored counts: "413
files, NOT ONE a claude.ai conversation"; "667 parsed transcripts") ·
`discord-other-friend-metadata-spec.md` (measured counts on a forward-looking spec) ·
`exposure-surface-measured.md` (the four-trunk `git remote -v` table asserting this trunk's most
consequential gate) · `graphrag-professional.md` frontmatter status · `conformance-professional.md`
provenance stamp (the freshness stamp that let rows 4–6 rot unnoticed) ·
`constitution-provenance-professional.md` + `resident-core-split-rule.md` byte figures (live
instrument is `constitution-budgets.tsv` + C8) · `asop-register.md` self-declared decay bound.

## (c) Rejected classes (considered, not candidates)

Dated audit artifacts where the numbers ARE the finding (the cross-trunk reviews, the noise-floor
pre-registration) · concept pages where the count is a defect's case history (print-the-population,
a-no-op-that-returns-success, the-object-moved-under-the-instrument, and thirteen more) · forensic
snapshots whose point is what was true then (ownership-is-not-reachability) · external facts not
derivable locally (ASOP numbering, third-party page counts) · budgets stated as constraints (the
budget stays stored; the current size beside it is the candidate) · Jon `[verbatim]` quotes
(provenance freezes).

## The side finding, and it is the sharpest sentence in the report

**This trunk already ships the print-the-command pattern for its index** — `INDEX-DERIVED.md` +
`lint.sh check_derived_index` — **and `wiki/index.md` is the hand-maintained twin that never got
retired.** Two lists, one truth: the same class as the three courier rosters. The successor ticket
(R-6) decides retire-or-reconcile rather than sweeping blind.
