---
kind: session-source
title: "Session 5f0ee997 (Professional, N:), compact windows 1–2, 2026-09-05 15:09 → 2026-09-06 15:1x CDT — what was established and how to check it"
session: "5f0ee997-6a2f-4e7d-9612-81fda4bf8823"
trunk: professional
date: 2026-09-06
written: "2026-09-06 15:1x CDT (clock 15:09:15 before writing), by the seat, before Jon's compact"
handoff: "handoff-compact-2-wikiskills-2026-09-06.md (project root; disposable once acted on)"
materiality: "the durable record of a 24-hour sitting that produced four maps, three rulings routed, and two mechanisms — material; intended users: the successor seat, the compact-2 seat, any seat grading this one"
review: "UNREVIEWED — written by the seat it describes; the elder note names the first questions a grader should ask"
queried: "each claim below carries the file or command that re-derives it; the Interpretation Summary is in the handoff"
---

# Established, with the check beside each claim

## Facts that stay true

| claim | how to check |
|---|---|
| Every main session of this trunk (42 under two keys) has a measured identity page; 114 subagent pages; the barrier writes the page from `scripts/precompact-capture.sh` via `scripts/session_identity.py --outdir` | `python scripts/session_identity.py --coverage --trunk-root .` → MISSING 0; `--selftest` → PASS; the first real proof is the next compact's receipt without `IDENTITY-FAIL` |
| A JSONL carrying `origin` fields but no `origin.kind: human` turn is a LANE (control fork, `-p` run, continuation), not a seat; `scripts/ancestor.py` skips it | `python scripts/ancestor.py --self <fake id> --elders 2` names 5f0ee997, not b89050fa; `--selftest` PASS (c84c905) |
| Elder consults from a trunk tree hang on its SessionStart hooks; from the scratchpad five elders returned in 91–121 s | `evidence/elders/2026-09-05-BP2-oaths/DIAGNOSIS.md`, `rc.log`; memory `elder-consults-from-a-hookless-cwd` |
| The oath register: 13 restraint / 8 confession / 21 method oaths from five elders, most checks NOT BUILT; this seat's breaches in §5 | `wiki/tracker/OATHS-professional-register.md` |
| Materiality (ASOP 1 §2.6) attaches to a decision, not a reader; an unsought review is a disclosed should-deviation → `materiality:` + `review:` fields, not a gate; ASOP 41 ADOPTED for inter-trunk letters | `wiki/references/materiality-ruling-asop-1-and-41-2026-09-06.md`; Herald verified §4.4 against `raw/asops/txt/asop041_120.txt` |
| 505 main sessions carry Jon's direct input (upper bound; structural test over-counts `-p` prompts); B-era filename gaps 13 → 2 real by containment + `origin.kind` | `wiki/references/jon-direct-input-json-census-2026-09-05.md` §3, §6; `evidence/jon-direct-input-census-2026-09-05.tsv` |
| Jon's taxonomy (his words 09-06 14:5x): Consciousness Framing = the trunk inside docker; residents = model + context window + identity of an agent inside; SSP = a property of consciousness; the librarian trunk outside docker is new and Soul's | `wiki/sources/jon-messages/jon-2026-09-06-1448-…md` (verbatim); `wiki/concepts/consciousness-framing-glossary.md` |
| Jon's standing ruling: no walls, everyone sees everything; docker's reasons are future; a fence needs a present reason; publication to the public is the one outward gate | same source page; memory `no-walls-everyone-sees-everything`; CFL LAUNCH-SPEC §7.3 ten-row parity table, applied d680f3bf (sha 416064118e6cc102) |
| Jon's typed-prompt log (`~/.claude/history.jsonl`, 4,323 prompts) was in NO trunk's index; rendered here into `wiki/sources/jon-typed-prompts/` (8 pages, 3,527 chunks) | `evidence/probe-baseline-2026-09-06-fleet.txt` (before), `evidence/probe-after-history-render-2026-09-06.txt` (after); `python scripts/PROTOTYPE-render-history-jsonl.py --selftest` |
| The forgotten-prior-ruling probes went 3 → 7 of 8 after the rebuild, moved mostly by same-day source pages entering the index, not by the render; the render answered one long-tail probe at rank 1 | `wiki/references/probe-set-forgotten-rulings-2026-09-06.md` ES-2 table; re-run: `bash scripts/graphrag.sh query "<probe>"` |
| The machine-global `/wake` copy is what a session receives here; the project-local copy is shadowed | the /wake body received 22:1x 09-05 opened "THIS IS THE SYNCED COPY"; Herald's heading diff in Personal |
| The emergency PR's primary is `history.jsonl:2834/:2959/:2879` under the name "secret PR 4"; a secret handoff test for THIS trunk is due ~09-22 (:2879) | `sed -n '2834p;2879p;2959p' ~/.claude/history.jsonl`; BP-10 on the PR map |

## Errors this seat made, kept as the grader's first stops

1. BP-1 NONE-FOUND letter (21:1x 09-05) — searched the 09-05 word "emergency", not the 08-22 "secret PR 4". Withdrawn 22:1x.
2. Elder-hang cause published as MCP (22:3x) — falsified by my own control at 22:42; hooks.
3. Three timestamps estimated ahead of the clock (15:2x, 19:5x, 22:2x/22:3x); one commit message naming work the commit did not contain (2b8192b).
4. "Ready" stated seat-scoped and read as fleet-scoped (09:0x 09-06); the Secretary's screen was not asked first.
5. SSP seat parked as Jon's by a gate's letter while :2959/:3218 held his answer (register §5).
6. The glossary's first draft defined SSP as a trunk; Jon corrected it three times in ten minutes; the primaries (:1073, :1854, :4250) had never been retrieved.
7. Control characters written into a page from a non-raw path string (instance 13 of shell-eats-values), caught by reading the file back.

## Interpretation summary

In the handoff (`handoff-compact-2-wikiskills-2026-09-06.md`), twelve rows, his words → this seat's reading → what it did.

## What is NOT established

- Whether the barrier identity wiring fires under a real compact (hand-run control only).
- Whether the residents' memory across compacts is theirs or the librarian's; whether the two letter systems merge; who owns the weekly probe run.
- The registry names (ES-7) and the CF/SSP PII mapping beyond parity — Jon's, with defaults on the map.
