---
format: cfl-page/v1
kind: reference
slug: WIKISKILLS-PROTOTYPE
title: "WikiSkills prototype: CFL knowledgebase in the three-directory shape"
date: 2026-09-03
generated_by: scripts/audit/wikiskills_prototype_render.py
rendered_at: 2026-09-03T03:08:37Z
commit: 907268e0
rendered_sha256: 51cca2d327c988f790ae23a15d1d66b60781b070c6f33e030c455cddf2dcf3db
---
# WikiSkills prototype: CFL knowledgebase in the three-directory shape

Rendered by `scripts/audit/wikiskills_prototype_render.py`. Every number below is computed live from disk at render time (git ls-files, filesystem walks, `lint.py` grade calls, JSON reads) -- none is hand-typed. Re-run with `--check` to verify this file is still byte-identical to a fresh render.

## 1. Three-directory shape, live counts

```
raw/
  originals/       3089 files (N: mirror, `N:/claude-corpus/cfl/raw/originals`, listing only)
  transcripts/     4614 files (N: mirror, `N:/claude-corpus/cfl/raw/transcripts`, listing only)
    claude-code/fl/  minted windows: 3 (`raw/transcripts/claude-code/fl/`, filesystem glob `*window-*`; gitignored -- not in `git ls-files`)
wiki/
  sources/         343 pages (git ls-files), of which state:superseded = 7
  concepts/        62 pages
  entities/        12 pages (excl. index.md)
  patterns/        31 pages (excl. index.md)
  references/      108 pages
  log.md           7072 lines
skills/
  SKILL.md         42 of 43 skill dirs
  PURPOSE.md       42, of which motivating_pattern resolved=2 UNKNOWN=40 unset/other=0
  validation/      splits present for: dream, exchange-letters, su-compact, wake, wayfinder
```

## 2. One worked chain (real paths, verified live)

1. **raw JSONL** (newest for session `9041f3b0`): `N:\claude-corpus\cfl\raw\live-store-capture\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\9041f3b0-5102-4a06-a459-b076681a76bd.jsonl` -- resolves
2. **minted window** (-v2 re-mint): `raw/transcripts/claude-code/fl/code-2026-09-02-9041f3-window-192940-v2.md` -- resolves
3. **source page from this week's S-lane batch** (added to this branch since 2026-09-01, `source_file` resolving under the N: root):
   `wiki/sources/infrastructure/silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5.md`
   - `source_file`: `raw/transcripts/claude-code/code-2026-08-18-3bafc5-run-reading-beat-and-write-brief.md`
   - declared `raw_sha256`: `5cc1741319cf7bc8f7daf049dd46b1cdbd65b886581745812326259bba47e28f`
   - recomputed sha256 (from `N:\claude-corpus\cfl\raw\transcripts\claude-code\code-2026-08-18-3bafc5-run-reading-beat-and-write-brief.md`): `5cc1741319cf7bc8f7daf049dd46b1cdbd65b886581745812326259bba47e28f` -- MATCH
   - `lint.grade()` verdict (via `lint.py --main-root N:/claude-corpus/cfl`): E1k_kind=PASS, E1_form=PASS, E2_anchor=PASS, E3_fidelity=PASS, E4_uncap=PASS, E5_link=PASS, E6_find=PASS, E7_prov=PASS, E7m_reads=N/A-kind, E8_fixity=PASS
   - CONFORMANT: **True**
4. **pattern page** `[[write-is-not-delivery]]`: `wiki/patterns/write-is-not-delivery.md` -- resolves. Linked FROM the source page above: NO -- this chain link is topical, not a live [[..]] wikilink on this specific page
5. **skill purpose**: `skills/exchange-letters/PURPOSE.md` -- resolves
6. **LEDGER GT-1 rows** (`wiki/skills-gate/LEDGER.md`), best-so-far R for exchange-letters:
   | run | R | detail |
   |---|---|---|
   | author (R_best) | 1.0 | wiki\skills-gate\validation\exchange-letters\baseline.json |
   | author R_degraded | 0.8672 | wiki\skills-gate\validation\exchange-letters\baseline.json |
   | blind (first non-author score) | 0.9141 (117/128 scored, 10 UNKNOWN excluded) | wiki\skills-gate\validation\exchange-letters\blind-run1-full.json |
7. **PROBE-REGISTRY RP-28 rows**: `wiki/tracker/PROBE-REGISTRY.md` -- 8 rows found, 8 PASS (no class flip)

## 3. Baseline -> now (D2-D12)

| # | Check | Baseline | Now | Computed from | Commit |
|---|---|---|---|---|---|
| D2 | wiki/sources pages (excl. session-stubs.md) | 158 | 343 (raw git ls-files count; not filtered for session-stubs.md by this renderer) | `git ls-files wiki/sources` | `907268e0` |
| D3 | coverage census: sessions mapped (A+B) | 221/723 = 30.6% | 385/733 = 52.5% | `wiki/intake-triage/CENSUS-2026-09-02-coverage.json` | `907268e0` |
| D4 | zero-footprint sessions (Z) | 351 = 48.5% | 0 = 0.0% | `wiki/intake-triage/CENSUS-2026-09-02-coverage.json` | `907268e0` |
| D5 | August 2026 sessions covered | 8/425 = 1.9% | 160/432 = 37.0% | `wiki/intake-triage/CENSUS-2026-09-02-coverage.json` | `907268e0` |
| D6 | pages created this week (this branch), lint-clean | unmeasured | 184/185 = 99% | `git log --since=2026-09-01 --diff-filter=A -- wiki/sources/ + lint sweep` | `907268e0` |
| D7 | wiki/entities pages, lint-clean | 0 | 13/13 | `lint.py --all-kinds sweep, label=entity` | `907268e0` |
| D11 | wiki/patterns pages, >=2 locators + Motivates (E9_backref) | 0 | 31/32 | `lint.py --all-kinds sweep, label=pattern, E9_backref` | `907268e0` |
| D12 | skills/<name>/PURPOSE.md, motivating_pattern resolves or UNKNOWN | 0 | 42/42 pass E9_backref (42 of 43 skill dirs have a PURPOSE.md) | `lint.py --all-kinds sweep, label=purpose, E9_backref` | `907268e0` |
| D8 | dangling path citations | 433/1,314 = 33%; 34 CFL-origin | UNKNOWN (requires a dedicated instrument run (check_wiki_path_refs.py / wiki/index.md diff / retrieve.py timing x8) this renderer does not invoke) | `see D-row source path in the map's done-test table` | `907268e0` |
| D9 | wiki/index.md last_updated == disk | 08-23; 49 vs 56 | UNKNOWN (requires a dedicated instrument run (check_wiki_path_refs.py / wiki/index.md diff / retrieve.py timing x8) this renderer does not invoke) | `see D-row source path in the map's done-test table` | `907268e0` |
| D10 | retrieve.py on 8 sealed probes | 118 s | UNKNOWN (requires a dedicated instrument run (check_wiki_path_refs.py / wiki/index.md diff / retrieve.py timing x8) this renderer does not invoke) | `see D-row source path in the map's done-test table` | `907268e0` |

## 4. INGEST-LEDGER and rejections/supersessions

**Last 10 index lines** (of 433 total in `wiki/skills-gate/INGEST-LEDGER.md`):

- 2026-09-02 24de92be wiki/sources/infrastructure/herald-coordinator-go-live-week-and-the-0740-pii-ruling-2026-08-08-01a0fd.md ACCEPTED probe_sealed='"Is the 2026-08-11 PII ruling quoted on this page present verbatim, typos included, in the raw\'s T3945 Human turn (raw line 73250), and does that turn contain the words It\'s fine in the personal Github it\'s not fine in the consciousness framing Github? => Yes on both E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 61ff9f71 wiki/sources/infrastructure/secretary-day-one-trunk-session-self-branching-ruling-2026-08-15-68a4bd.md ACCEPTED probe_sealed='"According to the cited Jon turn, what did Jon say he would do if the secretary\'s failure to self-branch its memories via the hooks he had planned was not solved?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 08956841 wiki/sources/infrastructure/professional-all-hands-slate-and-compact-live-proven-2026-08-15-bb5dd0.md ACCEPTED probe_sealed='"According to the cited turns, what did the Haiku census-search agent report was missing from the JSON census metadata that forced it to grep the JSONL files instead, and which session id did the Professional coordinator then fork to answer Jon\'s question?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 eebb58f9 wiki/sources/infrastructure/secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1.md ACCEPTED probe_sealed='"According to the cited turn relaying Herald\'s verdict, how many times had the notify_jon route fired and over how many ticks, and which section heading of Herald\'s 08-14 contract did the session quote about what the wake was supposed to be?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 ad9cf6ae wiki/sources/infrastructure/secretary-switchboard-day-precompact-critic-fork-2026-08-18-1b90e4.md ACCEPTED probe_sealed='"According to the cited critic turn, which two measured ticks printed classifier_invoked=False after the restart, and what deadline reported to Jon did the critic say now had no verified holder and no delivery mechanism?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 eaf89b64 wiki/sources/infrastructure/elder-consult-fork-a-attribution-witness-2026-08-07-d800c5.md ACCEPTED probe_sealed='"According to the cited elder-answer turn, which two artifacts did fork A name as the most likely to be misread by a later session, and what did it say about whether it had witnessed the 2026-07-21 ratifications?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 873c3b81 wiki/sources/infrastructure/elder-consult-fork-b-attribution-witness-2026-08-07-549df6.md ACCEPTED probe_sealed='"According to the cited elder-answer turn, what did fork B say the phrase \'unified-sources model\' reads like, and what did it say rationale clauses such as \'so the coordinator\'s prose is connector-readable\' almost always are?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 1480dbb5 wiki/sources/infrastructure/soul-lineage-inheritance-and-row-10-correction-2026-08-22-c38265.md ACCEPTED probe_sealed='"According to the cited turns on the carrier fixes, which two line numbers of carry_letters.sh carried the confirmed defects, and what did the third defect cause when the script was run from the Personal tree?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 e410988a wiki/sources/infrastructure/triage-fable-continuation-and-su-halted-2026-08-06-5fffbd.md ACCEPTED probe_sealed='"According to the cited coordinator turn recording that the mirror stopped again, what did the coordinator say a subagent does whenever it asks a question, and what did it say it would plan around instead of pretending?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind
- 2026-09-02 bf29844f wiki/sources/infrastructure/secretary-hall-prep-peer-review-root-cause-2026-08-17-28b396.md ACCEPTED probe_sealed='"According to the cited Jon turn carrying his overnight order (Auto mode ok), what three things did Jon say he expects to find when he wakes?"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind

**Last 5 REJECTED rows** (of 257 total):

- 2026-09-02 3fe396c2 wiki/sources/forward-pass-mechanics-2026-05-07-b04c8b.md REJECTED probe_sealed='"where does this citation resolve? => TRUSTED"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=N/A-kind E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=N/A-kind
- 2026-09-02 d6f976c9 wiki/sources/test-master-run-001-pure-null.md REJECTED probe_sealed='"where does this citation resolve? => TRUSTED"' (present, accepted as given) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=N/A-kind E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=N/A-kind
- 2026-09-02 998e34b0 wiki/sources/fbc/fbc-canonical-skill-2026-04-28.md REJECTED not reached (LINT stopped the pipeline) E1k_kind=FAIL E1_form=PASS E2_anchor=PASS E3_fidelity=FAIL E4_uncap=FAIL E5_link=PASS E6_find=FAIL E7_prov=FAIL E7m_reads=N/A-kind E8_fixity=FAIL
- 2026-09-02 2c7405a2 wiki/intake-triage/rejected-pages/cfl-wake-graphrag-v0-built-and-pii-index-in-pushed-history-2026-08-17-e1d2ac.md REJECTED not reached (LINT stopped the pipeline) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=FAIL E10_probe=N/A-kind
- 2026-09-02 ee241765 wiki/sources/ai-governance/professional-first-session-anthropic-disclosure-question-and-the-real-fence-2026-08-07-2d58af.md REJECTED not reached (FENCE stopped the pipeline) E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS E10_probe=N/A-kind

**wiki/sources pages with `state: superseded`** (7 total, last 5 by git-ls-files order):

- `wiki/sources/infrastructure/fable-letter-sent-close-ritual-2026-08-22-6a35af.md`
- `wiki/sources/infrastructure/fork-test-never-run-and-wiki-md-gap-2026-08-19-910b80.md`
- `wiki/sources/infrastructure/orthogonal-branch-vector-gate-2026-08-22-01c3b6.md`
- `wiki/sources/infrastructure/professional-adversarial-plate-review-launch-defects-2026-08-21-e3a556.md`
- `wiki/sources/wiki-t24-diff-ingest-2026-05-09-b60686.md`

## Not compliant yet

Lint sweep over 607 pages (`wiki/sources` full set + `--all-kinds` patterns/entities/concepts/references/purpose), `--main-root N:/claude-corpus/cfl`:

| check | FAIL count |
|---|---|
| E1_form | 57 |
| E1k_kind | 253 |
| E2_anchor | 27 |
| E3_fidelity | 121 |
| E4_uncap | 117 |
| E5_link | 98 |
| E6_find | 298 |
| E7_prov | 213 |
| E7m_reads | 5 |
| E8_fixity | 113 |

**UNRECOVERABLE/UNKNOWN rows** (raw unreachable from N:, graded as their own class, never rounded to PASS): 15

**What this renderer could not compute** (named, never omitted):
- `D8`: requires a dedicated instrument run (check_wiki_path_refs.py / wiki/index.md diff / retrieve.py timing x8) this renderer does not invoke
- `D9`: requires a dedicated instrument run (check_wiki_path_refs.py / wiki/index.md diff / retrieve.py timing x8) this renderer does not invoke
- `D10`: requires a dedicated instrument run (check_wiki_path_refs.py / wiki/index.md diff / retrieve.py timing x8) this renderer does not invoke
