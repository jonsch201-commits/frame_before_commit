---
title: "Census — every JSONL on this machine that carries a message typed by Jon, graded for archive / render / index presence, recency-bucketed (the FLOOR for passing wikiskills on 2026-09-06)"
kind: reference
date: 2026-09-05
session: 5f0ee997 (Professional, N:)
measured_at: "2026-09-05 22:21:33 CDT"
measured_by: "scratchpad/jon_census2.py (one Python pass over every *.jsonl under ~/.claude/projects, main + subagents/); index membership from the `files` table of %LOCALAPPDATA%/claude/graphrag/*.sqlite; raw rows in evidence/jon-direct-input-census-2026-09-05.tsv (826 rows), index dump in evidence/graphrag-index-files-2026-09-05.tsv"
charter: "Jon 2026-09-05 22:1x (wiki/sources/jon-messages/jon-2026-09-05-2217-wake-…md): identify each json that had input from me directly … must be complete for all jsons that got a message direclty from me at least (even the fable mirros i sometimes messaged, even some non-coordiantor forks of you) as the floor for passing the wikiskills tomorow — with more recent ones being more important in terms of actuarial credibility"
status: MEASURED; the floor is DEFINED here and NOT MET — see §3; §3's 13 B-era gaps CORRECTED to 2 sessions in §6 (22:4x)
---

## 1. Definitions, so the numbers can be re-derived

- **direct turn** = `type: user`, not `isMeta`, human text (a string, text blocks, or a `<command-name>` wrapper carrying his `/wake`-style arguments), with no `tool_result` block, not a `<system-reminder>` / `<local-command-*>` wrapper. In SUBAGENT files the first user turn is the coordinator's dispatch prompt, so direct is forced to 0 there.
- **meta_jon** = `isMeta: true` user turns NOT opening with "The coordinator sent a message". MIXED CLASS: the universal file's row 2 says these are Jon's mid-turn messages to a subagent, and a relay in other wording would also land here. Counted, not asserted.
- **queued** = `type: attachment` / `queued_command` entries: his messages typed while a turn ran (universal file, 09-01 row).
- **archived** = `raw/session-archive/<id>/` in any trunk tree. **rendered** = a `.md` under any trunk's `raw/transcripts/**` or `N:/claude-corpus/**` whose name carries the 6-char prefix (the renderer's convention; 8-char matching is a false negative, measured tonight). **indexed** = a path in the graphrag `files` table carrying that prefix.
- **era** by LAST direct turn, Jon's grades: **B** ≥ 2026-09-04 16:00 CDT (last all-trunk compact) · **D** ≥ 08-29 21:45 (PR-2 merge) · **C** ≥ 08-22 22:26 (PR-1 merge) · **OLDER**.
- Newer JSONLs carry `origin.kind: human` on his turns (this session: 9 such lines); older ones do not, so the census uses the structural test above for all and reports the field as a bound, not a filter.

## 2. Population

| class | files | Jon turns |
|---|---|---|
| JSONLs scanned (main + subagent, every project key) | 2,679 | — |
| carry any Jon input | 826 | — |
| MAIN with ≥1 direct turn | 661 | 9,425 direct + 6,282 queued |
| of which EXCLUDED from the floor: `G--My-Drive-Claude--switchboard` (each 1 turn, text "Coordinator has been dormant N minutes…" — the switchboard's injected prompt, not Jon) | 106 | 106 |
| of which EXCLUDED: one-shot lane runs under `C--Users-JonSc-AppData-Local-Temp-*` scratchpad / rerank / branchproto / wt-* / jobs-* / relay-* keys | 50 | 50 |
| **FLOOR population: MAIN sessions with a direct Jon turn in a trunk, worktree, XC-Exchequer, or personal-project key** | **505** | **9,259 direct + 6,282 queued** |
| SUBAGENT files with meta_jon turns (Jon-possible, mixed class) | 165 | 403 |

Exclusions are listed so they can be reversed; the 156 excluded files are in the TSV with their sample text. `D--Kevin-Image` (54 turns), `Temp-claude-pastself` (169), `Temp-claude-pit`/`pit2` (59 each) are INCLUDED: multi-turn conversations are his even under a scratch key.

## 3. The floor, graded — NOT MET

| era | floor sessions | direct turns | rendered anywhere | archived (raw/session-archive) | in THIS trunk's index |
|---|---|---|---|---|---|
| B (since 09-04 16:00) | 66 | 1,279 | **53** | 2 | 2 |
| D (since 08-29 21:45) | 100 | 1,303 | 100 | 3 | 3 |
| C (since 08-22 22:26) | 68 | 1,385 | 68 | 2 | 2 |
| OLDER | 271 | 5,292 | 271 | 34 | 34 |
| **total** | **505** | **9,259** | **492** | **41** | **41** |

**Rendered** is the only column near complete, and the 13 gaps are ALL in the B era — tonight's sessions, the ones he weights highest:

| key | session | direct turns | last |
|---|---|---|---|
| G Secretary | c16b7543 | 36 | 09-05 |
| N Personal | d6a82788 | 11 | 09-05 |
| G Personal | c19e5d21 | 11 | 09-05 |
| N corpus-personal | 9e525859 | 7 | 09-05 |
| G Personal | 70a366bb, 384e93eb | 7, 7 | 09-05 |
| N CFL clone | d8fa6bf3 | 4 | 09-05 |
| N Personal | 0d96cd33 | 3 | 09-05 |
| G Personal | 5571c67f, 5ead92da | 2, 2 | 09-05 |
| N Personal | 8820449b; G Personal 6b327540, 040b4ec7 | 1 each | 09-05 |

**Archived** = Professional only (this trunk keeps `raw/session-archive/`; the other trunks render and do not archive). **Indexed in this trunk's index** = Professional's own 41; the indexes are federated per trunk, so the fleet answer is the next table.

### Fleet indexes, transcript coverage `[measured 22:2x from the sqlite files table]`

| index file | files | transcript-class files | chunks | built |
|---|---|---|---|---|
| index.sqlite (CFL) | 11,229 | 6,162 | 109,301 | 2026-09-05 15:20 |
| professional.sqlite | 1,340 | 197 | 17,353 | 2026-09-05 21:00 |
| personal.sqlite | 1,673 | 537 | 22,104 | **2026-08-30 07:41 — six days stale** |
| index.resident.sqlite / index-v2-sec113.sqlite | 5,068 / 5,537 | 4,378 / 4,380 | 13,197 / 31,833 | 2026-08-23 |

Bound on the CFL number: M-13 (tracker) measured its transcript tier as ONE HEAD-ONLY CHUNK PER FILE, so a transcript file being "in the index" there does not mean its body is retrievable. Secretary has no index file under this path at all. **No index on this machine holds the B-era sessions' bodies as of 22:2x.**

### Subagents (the A grade)

165 subagent JSONLs carry 403 Jon-possible mid-turn messages; **1 is rendered, 0 are indexed, 0 have identity pages.** By key: CFL G 74 files / 157 turns; Personal G 37 / 167; CFL N 27 / 39; Professional G 12 / 27; Secretary G 11 / 11.

## 4. What "complete" has to mean tomorrow, stated as checks that can fail

1. **Render**: every floor session has a markdown render in its trunk's `raw/transcripts/` (6-char prefix match) — 492 of 505 now; the 13 B-era gaps first.
2. **Index**: every floor session's render is in its trunk's graphrag index with body chunks, not a head chunk — checkable as `chunks per transcript file > 1` and the newest floor session's last direct turn retrievable by a quoted phrase.
3. **Recency**: the B set (66) is the acceptance set; D (100) and C (68) next; OLDER last. A trunk whose index lags its newest session by more than one compact fails on his data standard.
4. **Subagents**: the 165 meta_jon files rendered and indexed, or listed with the reason they cannot be.
5. **Mixed classes printed, never folded**: switchboard prompts and lane runs are excluded and named; meta_jon is a candidate class until a reader confirms it turn by turn.

## 4b. Content screen — a census that selects on SPEAKER cannot enforce a CONTENT rule (Herald, 2026-09-06 15:5x)

Herald, marking the OV-3 renders: three of the "Jon input" sessions were XC-Exchequer builds — a T2/T3 content class whose no-remote rule is ABSOLUTE. The floor selected on who spoke and correctly swept them in; only `.gitignore` kept them out of git. Measured here the same minute: the tracked typed-prompt render (`wiki/sources/jon-typed-prompts/`) carried **158** prompts typed into the XC-Exchequer project. Fixed 15:5x: the render script screens on project and writes those prompts untracked under `raw/jon-typed-prompts-exchequer/`; the tracked pages carry 0. Rules that follow: (1) the floor's definition stays "rendered anywhere ON DISK" and must never tighten to "in a tracked or pushed path" without a content screen; (2) every render that targets a tracked path screens on the XC-Exchequer project key and on money identifiers before writing; (3) the publication gate never derives `wiki/sources/jon-typed-prompts/` into the public tree without the same screen re-run on the derived copy. Other trunks' censuses were built the same way — UNKNOWN whether they hold the class; UNKNOWN dominates.

## 5. Bounds

- One pass, one machine, one clock. Sessions Jon had on claude.ai are OUTSIDE this population by construction (universal file, claude.ai-seat row).
- "rendered anywhere" credits a render in ANY tree, including G: mirrors; a trunk's own coverage is lower.
- Prefix matching can over-credit: two sessions sharing a 6-char prefix would both read as rendered. Not observed; not excluded.
- The panel of prior Professional sessions (BP-2) had not returned when this page was written.

## 6. Correction 22:4x — the 13 B-era gaps are TWO sessions (Secretary's containment rule + the harness's own provenance marker)

The Secretary measured at 22:4x that c16b7543's 1,748 records are a strict subset of 94ef20e7, rendered at 22:17: **a session is covered when its RECORDS are covered, not when its name appears in a filename.** Re-run here over all 13 (`evidence/jon-direct-input-census-2026-09-05-CONTAINMENT.md`), then a second predicate this page lacked: on 09-05 JSONLs the harness marks Jon's typed turns `origin.kind: human`.

| predicate | result |
|---|---|
| containment (record uuids ⊆ a rendered session) | 1 covered (c16b7543 ⊂ 94ef20e7); 12 survive |
| provenance (`origin.kind: human` turns > 0) | 7 of the 12 have ZERO — their "direct turn" was a `-p` lane's opening prompt or a continuation summary |
| survive both | **2 sessions**, each present under several ids with identical content: d6a82788 / c19e5d21 (8 human turns) and 9e525859 / 70a366bb / 384e93eb (4 human turns) |

So §3's "13 gaps, all B-era" is corrected to **2 sessions, ~12 of Jon's turns**, and §1's structural test over-counts wherever a MAIN JSONL was launched with `-p`: the 505-session floor population is therefore an UPPER bound. The recount by `origin.kind` across the whole population is owed (the field is absent from older JSONLs, so a fallback and its label are needed). The predicate order for any future census: containment → provenance → filename, each printed. Both letters built from §3 (OV-3) were corrected the same hour.
