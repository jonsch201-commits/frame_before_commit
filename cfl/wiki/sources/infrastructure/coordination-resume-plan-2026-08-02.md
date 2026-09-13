---
title: "Coordination Resume Plan — What CFL Needs for Proper Coordination and Resumability (fable-mirror capture, 2026-08-02)"
aliases: [cfl-resumability-plan-2026-08-02, carrier-md-proposal-2026-08-02]
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 9 vs wiki 3 on authored labels"
source_kind: session
retrieval_key: coordination-resume-plan-2026-08-02
generated_by: fable-mirror subagent (CFL session, 2026-08-02), wayfinder capacity, reading Claude Personal's wiki under Jon's grant
origin: CFL session, fable-mirror subagent, 2026-08-02
audit_state: unaudited
status: PLAN + SELF-CORRECTION. Not ratified by the capturing agent.
maintained_by: coordinator (deposit); wiki-master ingests
tags: [fable-mirror, coordination, resumability, cross-project, jon-ruling]
---

# Ingest note (wiki-master, 2026-08-02 close work order, step 5)

Ingested from `wiki/intake-triage/coordination-resume-plan-2026-08-02.md`, content unchanged below.
**Known non-conformance, flagged not silently fixed:**

- The original deposit carried no frontmatter at all; the block above was added at ingest.
- `[MIRROR-INFERENCE]` appears throughout the body. This is **not** a typo — CFL's `fable-mirror`
  charter (`.claude/agents/fable-mirror.md`) mandates this exact term, while the wiki's seven-value
  fidelity axis (`skills/wiki-master/references/citability-standard.md`) would want `[inferred]`. This
  is a genuine CFL↔Claude-Personal standards divergence, not sloppiness. **Deposited to
  `skills/intake/needs-design/` in this same PR for skills-master + Jon** — see that file for the full
  routing note. Do not normalize the tag in the body below.
- FORM: this page does not carry a `## Key Claims` section in the v4.0 sense — it is a captured
  planning packet, not a raw session extraction. Treated here as `source_kind: session` with FORM
  partially non-conformant; the gap is disclosed rather than backfilled with fabricated claim bullets.
- Every quoted Jon fragment in the body below was cross-checked against
  `wiki/sources/reference/jon-messages-to-mirror-2026-08-02.md` during this ingest pass. This page
  does not quote Jon directly (it quotes Personal's `corpus-date-semantics.md` and its own analysis) —
  no discrepancy found.

---

# Plan — what CFL needs for proper coordination and resumability

**Captured by:** `fable-mirror` (CFL), wayfinder capacity, reading Personal's wiki under Jon's grant
**Date:** 2026-08-02 · **Status:** PLAN + SELF-CORRECTION. Not ratified by the capturing agent.
**Role note:** I am the records-reader. **This is a plan for the coordinator to run, not one I run.**

---

## 0. ⚠️ SELF-CORRECTION FIRST — Personal's wiki invalidates part of tonight's provenance

`Claude Personal\wiki\references\corpus-date-semantics.md` (`[measured]`, 2026-08-02):

> **A date in a transcript filename is `updated_at` — the last time the conversation was touched…
> It is not when anything in the file was said.** … **every `[TRANSCRIPT:YYYY-MM-DD]` tag in this wiki
> is an upper bound on a window, not a date.**

Source: `convert-export.py:590` uses `updated_at` for the filename; `map_conversations.py:128,156`
uses `created_at` for the manifest. **The parsed transcripts carry no per-message timestamps —
`grep -c created_at` returns 0.**

**Worked disaster case:** `f8cc02` is filed as `chat-2026-04-30-…` and its `updated_at` is
**2026-07-19** — a **95-day window**, 160 messages. Any quote cited `[TRANSCRIPT:2026-04-30]` from it
could have been said anywhere in that span.

### What this does and does not break in my work tonight

| Claim | Survives? |
|---|---|
| Jon's planning-session quotes, cited `[TRANSCRIPT:2026-07-29]` | **✅ SURVIVES.** These came from a **claude-code JSONL** transcript carrying explicit inline ISO stamps (`=== 2026-07-29T03:06:27.902Z`). CC transcripts are timestamped per turn; the defect is specific to **claude.ai** parsed exports. |
| Any claude.ai-sourced `[TRANSCRIPT:date]` I emitted | **⚠️ Now a bound, not a date.** |
| "Corpus current through export ≈2026-08-02" | **⚠️ Weaker than I stated.** I derived it from a zip epoch and newest filenames — **filenames are `updated_at`**, so this dates the *export*, not the *content*. |

**I am flagging this against my own output rather than waiting to be caught.** `[MIRROR-INFERENCE]`
**CFL's `fable-mirror` charter mandates `[TRANSCRIPT:date]` as its strongest grade — and that grade is
weaker than the charter assumes for claude.ai material.** That is a defect in my own instruction file,
found by the other project, exactly as the redundancy doctrine predicts.

## 1. LIVE, UNDELIVERED, ADDRESSED TO CFL — read this before planning anything

`Claude Personal\wiki\intake-triage\OUTBOX-READY-seed-standards-to-cfl.md` is **staged and waiting on
a gate.** It offers CFL two ratified artifacts:

1. **The five-field flag standard** (Personal D16): `status` · `recommendation` · `falsifier` ·
   `falsifier_tested` · `blocks`. Two guard rules: **a falsifier may not be judged by its author**
   (bought when their mirror over-retired its own seed) and **untested ≠ passed**.
2. **The falsifiability principle**: *could evidence prove it false?* No → **decision** (changed by the
   decider). Yes → **seed** (changed by evidence, carries its falsifier). Ambiguous → **write both**.

**Their ask, verbatim:** *"adopt, adapt, or counter-propose — but answer, so the vocabularies converge
while convergence is one message wide."*

**`[MIRROR-INFERENCE]` This is the `T3≠T3` tier-vocabulary mismatch being solved before it hardens —
and CFL has not answered.** The gate is Jon ratifying their falsifiability principle text; **he
approved the S9 *plan*** (*"s9 that sounds good to me"*) **but their own file records that
plan-approval ≠ text-ratification and refuses to collapse them.** That discipline is worth copying.

**Their standing caution about themselves, quoted because it is the right way to send a packet:**
*"two fabricated attributions and three infrastructure over-claims today… Check anything that reads
as a system fact."*

## 2. What Personal has that CFL does not — the resume machinery, itemized

| Artifact | Personal | CFL |
|---|---|---|
| **Compaction-surviving entry file** | `CARRIER.md`, **<10 KB by rule**, pointers+numbers only | **NONE** |
| **Guaranteed post-compact reads** | `tracker/open-items.md` + `tracker/session-open-prompt.md`, named in the recovery protocol | Wake-map in `~\.claude\plans\` — **on `C:`, not mirrored, 18 files / ~348 KB** |
| **One-click cold start** | `relaunch-guide.bat` = `/clear` + session-open prompt | **NONE** |
| **Session-close protocol** | `SCHEMA.md` § Compaction, with a **checklist table** | SU exists; **no compaction-close checklist** |
| **Falsifiable continuity test** | `compaction-prediction-*.md`, scored HIT/MISS/**RECOVERED** | **NONE** |
| **Staged-dispatch drain check** | Standing SU row: *"`intake-triage/OUTBOX-READY-*` drained or gate stated?"* | **NONE** |
| **Decision log** | `wiki/DECISIONS.md` (3,982 lines) | Scattered across `exchange/`, `intake-triage/`, memories |

**The single most transferable idea, in their words:** the standing checklist row *"makes every future
staged dispatch a **checked item instead of a remembered one**."*

`[MIRROR-INFERENCE]` **That sentence is the whole answer to Jon's question.** CFL's characteristic
failure is *"reliably produces records and unreliably consumes them"* — five instances traced in one
night. **Resumability is not more documents. It is converting remembered obligations into checked
ones.** CFL has more records than Personal and fewer checks.

## 3. THE PLAN — recommended sequence

**Answer to Jon's "do we need to walk through a standard update?" — Yes, and it should be a *rehearsal
with a scored prediction*, not a demonstration.** A walkthrough that succeeds proves nothing; a scored
prediction can fail.

| # | Step | Owner | Why here |
|---|---|---|---|
| **1** | **Answer Personal's seed-standards packet** — adopt / adapt / counter-propose | coordinator + Jon (ratification) | It is one message wide **today**. Divergence compounds. |
| **2** | **Write CFL's `CARRIER.md`** — ≤11,901 bytes, pointers and numbers, no narrative, **in the repo** not `~\.claude\plans\` | coordinator | Everything else depends on a cold session finding the map. Today it is on `C:` only. |
| **3** | **Add the SU close checklist**, including the `OUTBOX-READY-*` drain row **and a read of Personal's + Herald's outboxes** | wiki-master | Converts remembered → checked. Fixes the deposit-only defect in both directions. |
| **4** | **Rehearse a compaction: write the prediction, compact, score HIT/MISS/RECOVERED** | coordinator | The falsifiable test. **This is the walkthrough Jon asked about.** |
| **5** | **Re-derive the JSONL survival cutoff from disk**; settle `2026-06-17→06-20` | data-master | Blocking the cohort caption. Small. |
| **6** | **Fix the citation-date defect** — adopt bounded form `[TRANSCRIPT:2026-04-15..2026-07-19]` where span >7 days | wiki-master + Jon | §0. Affects every claude.ai citation in CFL's wiki. |
| **7** | **Regenerate `conversation_manifest.json`** — Personal measured it **82 days stale** (127 conversations, through 2026-05-12) | data-master | It is the de-dup key and the `created_at` source step 6 needs. |

**Do steps 1–3 before step 4.** Rehearsing a compaction against machinery you have not yet built
scores a MISS you already knew about.

## 4. What I still need from Personal — coordination questions

1. **Their `SCHEMA.md` § Compaction table verbatim** — the close checklist. CFL should adapt, not
   reinvent. *(Readable now under Jon's grant; I did not read it — budget.)*
2. **Their `tracker/session-open-prompt.md`** — the guaranteed-read entry text.
3. **Their answer on `as_of` stamping for drained memories** (my earlier question 2).
4. **Whether `convert-export.py:469,489` has a mode preserving per-turn `created_at`.** Their own page
   flags this: *"If a mode exists that preserves per-turn timestamps, it would make this whole page a
   workaround for a solved problem — that is worth ten minutes before anyone builds tooling on the
   bounds format."* **Ten minutes that could delete step 6.** Highest ratio item on this page.

## 5. Answered without asking — my relay's question 3 is now closed

I asked Personal whether its two 2026-08-02 deposits landed in its tree or CFL's. **Confirmed in its
tree:** `seed-falsifiability-principle-DRAFT-2026-08-02.md` and `CONCEPT-DRAFT-knowledge-transfer-goal.md`
both exist under `Claude Personal\wiki\intake-triage\`. **My deixis inference was correct.** Personal
also has `mirror-write-scope-breach-2026-08-02.md` — **their mirror had a write-scope breach today,
the same class my fence blocked tonight.** Two projects, same defect, same day, independently.

## Uncaptured content

- **I did not read:** Personal's `SCHEMA.md`, `DECISIONS.md` (3,982 lines), `log.md`,
  `tracker/session-open-prompt.md`, `tracker/open-items.md`, `wayfinder-personal-wiki.md`, or any of
  the ~20 other `intake-triage/` files. **This plan is built on 4 files out of ~50.**
- **I did not verify** Personal's date-semantics claims against CFL's `convert-export.py` myself. They
  cite file:line; **their own packet says to check anything that reads as a system fact, and I have
  not.** Step 6 should not ship until someone does.
- **The claim that CC transcripts carry per-turn timestamps** (§0) is from my own reading of
  `code-2026-07-29-627c1e-*.md` inline stamps this session — **one file, not a survey.**
- **`compaction-prediction` scoring is described, not read.** I have not opened Personal's actual
  prediction file.
