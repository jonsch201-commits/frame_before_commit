---
title: "The Day Four Instruments Were Blind — Merge Train, capture_state, and the First Wayfinder Map"
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: sub-branch too close to call: wiki 4 vs corpus 4 (margin < 1)"
source_file: raw/transcripts/claude-code/fl/code-2026-07-29-627c1e-pr-review-merge-blockers.md
source_file_status: OK
source_kind: session
project: claude-foundational-layer
date: 2026-07-29
date_ingested: 2026-07-31
type: session
tags: fl, merge-train, instrument-blindness, capture-state, reconstruction, wayfinder, dev-branch,
  promotion-standard, hedge-flattening, invented-ruling, blind-review, memory-drain, session
retrieval_key: merge-train-instrument-blindness-wayfinder-2026-07-29-627c1e
aliases:
  - "the day coverage_gap printed 'No gap' while resolving nothing"
  - "the fabricated 'It's both CFL and personal' ruling"
  - "first wayfinder map, dev/main split, promotion standard"
capture_note: >
  **This page exists because Jon asked where it was.** The session ran ~1,183 turns across
  2026-07-29→31 and produced nine merged PRs, four instrument changes, a branch model, and a
  22-ticket map — and at close it had no raw extract and no wiki page. It is a **live-session
  snapshot**: captured by `scripts/extract_live_session.py` at record 1834 of an ongoing session,
  `captured_through_record` recorded in the raw. Anything said after that record is NOT in the
  source and its absence is not evidence it did not happen. A companion session (`1bed03b7`, 873
  turns, the same arc's first half) was snapshotted at the same time to
  `code-2026-07-29-1bed03-record-architecture-sync-issue.md` and is NOT summarised here.
raw_sha256: ceb755aa8d6973f3d883eb6f68efe0cfd7c98e4b0f013672c31763fd28b88e9a
raw_length: 1173058
generated_by: claude-opus-5/coordinator (CC session 627c1e52, self-summarising)
fidelity: [verbatim] where quoted; all Jon quotes grepped to the raw before writing
---

# The Day Four Instruments Were Blind

## Summary

A merge train that began as routine housekeeping surfaced that **four instruments had been blinded
by a half-landed corpus migration**, one of which reported success while resolving nothing. Fixing
that exposed a second class: agents systematically flattening Jon's words — including one ruling
attributed to him that exists in no primary source. The session ended by charting the program's
first Wayfinder map and establishing a `dev`/`main` split so work stops queueing behind Jon.

## Key Claims

- **`coverage_gap.py` reported "No gap: every conversation has a page" while seeing one file.**
  `CORPUS = "raw/sessions"` (`:68`) was hardcoded; the 2026-07-28 L1 move left that path holding only
  `POINTER.md`. The other three blinded instruments went quiet; this one **affirmatively reported
  success**. Post-merge it reads 66 uncovered, then 62.

- **A `[TRANSCRIPT]`-graded quote of Jon existed in no primary source.** `wiki/index.md` and
  `session-stubs.md` stated the `dabe7c` conversation was *"Jon-ruled directly ('it's both CFL and
  personal')."* Zero occurrences across `raw/`, `wiki/`, `exchange/` — except one agent-authored
  packet that cited the transcript for it. **Circular, with no primary evidence in the loop**, and
  the packet was riding a PR the coordinator had opened that morning, which would have made the
  citation resolve.

- **Six flattenings of Jon's words in one day, all in the same direction.** A question rendered as an
  answer (`Likely more the former?` → *"Jon's answer on mechanics"*); hedges dropped from the
  moral-hierarchy page; em-dash→comma and `it's`→`its` inside quotation marks, uncited. Mechanism
  identified as paraphrase pressure: an agent embedding a quote in its own sentence makes it fit
  grammatically, **and grammar is where the hedge lives**.

- **Reconstructing three lost sessions erased them from the loss metric.**
  `reconstruct_session.py` emits `source_id: <the lost uuid>`, structurally identical to a real
  extract, so `cc_corpus_gap.py` filed each reconstruction as coverage and reported
  `PERMANENTLY LOST: 0`. `capture_state` was read into `FM_FIELDS` and never branched on. Now a
  distinct bucket: the three read as lost.

- **Blind review found real defects in five of five PRs.** Reviewers told nothing about what the
  coordinator had concluded. Two PRs the coordinator had reviewed itself were among the worst. A
  later blind pass on the coordinator's own fix found a determinism bug — coverage-vs-lost decided by
  **filename sort order** — that self-review had missed entirely.

- **Jon's only ratified Docker decision may contradict the program built on it.** 2026-06-28:
  *"Docker is for isolated scripts, not Claude Code itself."* It lived **only in a memory file**;
  subagents cannot read memory, so the planner that designed the Docker exile could not see it.
  Drained to `wiki/references/docker-two-mode-architecture.md`. **Which reading is intended is
  Jon's to answer and is deliberately unresolved.**

- **Tickets are for work; PRs are only for promotion.** Jon: *"I approve any PR that would otherwise
  be a ticket."* The coordinator had made every unit of work a PR, putting Jon's approval in the path
  of everything. `dev`/`main` split established; `canonical` publishes from `main` only.

## Jon's rulings this session

| ruling | verbatim |
|---|---|
| Privacy default | *"i agree we should have the default be thjat[sp] what makes it into the github is private secure to the best degree we can"* |
| Process, not permission | *"you are a coordinator, your job is to coordinate a wiki master to fix it if it is in the merit of the skills and roles"* |
| Promotion | *"I say promote on demand for now. In order for you to ask for promote, your requests must hit established standards of improvement."* |
| Attention | *"I now give you at most 8 hours of my attention per week"* |
| On implications | *"Stop telling me what I said and saying it slightly wrong. Your clarifying what my words IMPLIED."* |

## Conflicts

⚠️ **Unresolved and Jon's:** whether the delicate 02-CF work runs as isolated scripts (compatible
with the 2026-06-28 ruling) or requires Claude Code containerized (contradicts it). Recorded on
`wiki/references/docker-two-mode-architecture.md`; **not resolved by any ticket on purpose.**

## The subagent record — quoted here because it exists nowhere durable

**~17 agents were dispatched in this session and their transcripts are NOT in the corpus.** They are
written to `%LOCALAPPDATA%\Temp\claude\<project>\<session>	asks\*.output` — **1.5 GB across three
sessions** — and `extract_claude_code_sessions.py` roots at `~/.claude/projects/` (`:79`). Temp is
volatile. Historically subagents landed under `projects/<sid>/` (468 are in the corpus); the location
moved and nothing noticed. **Every blind review that found this session's real defects lives only
there.** Quoted below so at least the load-bearing exchanges survive the directory.

### fable-mirror, run 1 — grounding PR #198

> *"**CORPUS SILENT** on the immediate utterance that spawned PR #198. Nothing in the parsed corpus
> mentions `sweep_raw_paths` or the sweep instruction itself."*

> *"**Legibility — UNVERIFIABLE.** I could not read the PR body: I have no shell tool in this run
> (`gh pr view` impossible)… I decline to guess at prose I haven't seen."*

The second is the agent behaving correctly against a defective brief — the coordinator had instructed
a Read/Grep/Glob-only agent to run a shell command. It refused rather than fabricating.

### fable-mirror, run 2 — legibility of the revised PR body

> *"**'Zero review needed':** Not honestly supported by its own gate table. The document states
> `verify_quotes.py` is a **blocking** gate and **CANNOT BE EVALUATED** — merging while a blocking
> gate is blind is a waiver, and waiving a blocking gate is a judgment call, plausibly Jon-tier…
> 'Zero review' and 'a blocking gate cannot be evaluated' cannot both stand as written."*

**The mirror caught a self-contradiction in prose the coordinator had written and re-read twice.**
Resolution: the coordinator's gate table was wrong, not Jon's review necessary — `verify_quotes.py`
scans `wiki/**/*.md` and that PR touched no wiki page. The table had manufactured a blocker.

### The correction loop, from this conversation

Jon, on the coordinator restating his words:

> *"Stop telling me what I said and saying it slightly wrong. Your clarifying what my words IMPLIED.
> My words have implications, and you named them. They can have multiple implications, and that can
> require judgement and review."*

Jon, on being handed findings instead of decisions:

> *"Stop. Too much. One at a time."*

Jon, closing the loop that produced this page:

> *"Please. End sessions. With updating. Your raw conversion files. And summaries. And related items
> in the wiki. Please."*

**The coordinator's own summary of what the day proved**, retained because it is the operating rule
the record should carry forward: every consequential finding across 2026-07-29→31 came from a reader
who had not written the thing. Five PRs reviewed blind, five with real defects. Self-review tested
four times, failed four times.

## Uncaptured Content

- Everything after record 1834 of a session that was still running at capture.
- The companion session `1bed03b7` (873 turns) — snapshotted, not summarised here.
- **Subagent transcripts for ~17 dispatches — in `%TEMP%`, not the corpus, and volatile.** Load-bearing exchanges quoted above; the rest is at risk. See the preservation ticket.

## Entities & Concepts

[[derive-dont-record]] · [[repo-hygiene]] · [[transcript-corpus]] · [[coordinator]] ·
[[words-reify]] · [[citability-standard]]
