---
title: "Jon Dispatch — Turn 7: E2 Ratified, Connector Unfrozen, Merge Model Stated (2026-07-25)"
aliases: [turn7-e2-ratification-2026-07-25, connector-freeze-lifted-2026-07-25, merge-model-g-vs-github-2026-07-25]
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: sub-branch too close to call: wiki 4 vs fleet 4 (margin < 1)"
source_kind: session
retrieval_key: jon-turn7-e2-connector-mergemodel-2026-07-25
generated_by: Jon, authored directly in the CC coordinator session, 2026-07-25 evening
origin: wiki/intake-triage/jon-turn7-e2-connector-mergemodel-2026-07-25.md
audit_state: unaudited
status: JON-AUTHORED — rulings, not proposals. Ten days unrouted before this ingest (deposited 2026-07-25, ingested 2026-08-05).
maintained_by: coordinator (deposit); wiki-master ingests
tags: [jon-ruling, e2, connector, canonical, merge-model, verifier-tier, citation-coverage]
---

# Ingest note (wiki-master, SU-close step 4, 2026-08-05)

Ingested verbatim from `wiki/intake-triage/jon-turn7-e2-connector-mergemodel-2026-07-25.md`, content
unchanged below. This file's own frontmatter already carries `capture_rule: VERBATIM, typos and
capitals preserved, zero paraphrase` and separates Jon's quoted text from coordinator notes (§ marked
"Coordinator notes — NO AUTHORITY"). That separation is preserved as-is; no line was reworded, no typo
corrected, no hedge hardened.

**Known non-conformance, flagged not silently fixed:** original file has no `retrieval_key`/`aliases`
block — added at ingest, matching the convention of
[[jon-ruling-cohort-split-and-mirror-deliberation-2026-08-02]]. No independent primary-transcript
re-verification was performed against a claude.ai export for this pass — this file's own frontmatter
states it IS a direct capture ("authored directly in the CC coordinator session"), so it is treated as
the primary artifact of record, not a summary of one.

**Cross-reference to the coordinator's own note in §7 below:** the file records that the mirror corpus
could not confirm Jon's "how many times did I say that" claim because corpus coverage stopped at
2026-07-22. That gap is a fact about corpus freshness, not about this quote's fidelity — the M3-A/M3-B
PASS quote in §1 is Jon's own typed text in this session and is carried as-is.

---

# Jon dispatch — turn 7: E2 ratified, connector unfrozen, merge model stated (2026-07-25)

## 1. M3-A / M3-B pass-gate calls (VERBATIM)

> "OH MY FUCKING GOD YES M3A M3B IS PASS PASS HOW MANY TIMES DID I SAY THAT!"

**M3-A = PASS. M3-B = PASS.** Recorded in PR #125; OI-017, OI-018 and the da51cc close-out all closed
2026-07-25. See the coordinator note on relay loss below.

## 2. Verifier tier (VERBATIM)

> "verifier tier look you go opus first and elevate to fabel when needed that should be obvious.
> Merege 120 + 121"

**This is a routing rule, not a ranking.** Opus is the default tier; Fable is the escalation target when
the work warrants it. It resolves the apparent inconsistency in the 2026-07-21 model-gate ruling capture
(fable-mirror → Fable, fleet executors → Opus, same day): "top-tier-available-in-CC" applies at the
escalation point, not as a floor. **No agent definition needs changing** — all nine already carry alias
pins (`opus`, `sonnet`, `haiku`, `fable`), which is the correct implementation.

## 3. Connector (VERBATIM) — FREEZE LIFTED

> "Unfreeze the connector!!!!! I've been asking for ways to ensure the wayfinder reads through the latest
> branch my gosh."

Scope as proposed to him and approved in this exchange: **publish `wiki/` minus `wiki/personal/`,
`wiki/home/`, `wiki/pro/`** — the FL trunk only, consistent with his Q3 staging. Widening is a later
Herald-scoped decision.

## 4. E2 — RATIFIED, with three amendments (VERBATIM)

> "E2 yes lets use your third option, but lets track where that hits us in terms of yoru e2 threshold %,
> and I do believe we should measure the coverage by various categories in the wiki as that will improve.
> Further, theri are multiple way syou could measure this and so I expect you should test a 95% threshold
> im multiple ways and I expect you currently are not. But, I hope that helps."

**Ratified:** option 3 — 100% coverage, with explicit `unrecoverable`/`inferred` counting as coverage.
**Three amendments, all binding:**
1. Track where option 3 lands relative to a 95% threshold — i.e. report the *strict* number alongside the
   option-3 number; the gap is the honest residual.
2. Measure coverage **by category**, not only in aggregate.
3. Test the threshold **by more than one method**. His parenthetical — *"I expect you currently are not"* —
   is correct and was verified: see coordinator notes.

## 5. Merge model / G-vs-GitHub (VERBATIM)

> "re merge class authorization I trust your judgement i don't understand your question. Look for
> everythign in github I just want whats on G to be what you expect I would say is the best. In most cases
> thats gonna be all branches merged. But I understand why, for approval reasons you would want to gate
> that within the github at least. And I understand why *eventually* we will need to wait before merging
> some chainges from github to G."

**Coordinator's stated interpretation, for his correction:** the Drive working tree (`G:`) should reflect
the best current state — normally all branches merged — rather than sitting stale behind a PR queue.
GitHub retains the approval record. Merges of coordinator-produced work proceed on coordinator judgment;
he anticipates a future class of change that must wait before reaching `G:`. **This does not extend to
gates, ratifications, or identity-adjacent items**, which turn-6 reserved to him and which nothing here
alters.

## 6. The operating pattern (VERBATIM)

> "And yes, the pattern worth naming tonight should be directlyh solvable via the updates you are
> coordinating."

Refers to the coordinator's self-report that it builds decision structures around questions Jon has
already settled or finds obvious.

## 7. Session-management questions (VERBATIM)

> "Continue coordination? Explain your reasoning. And how well are you using the fabel mirror? How well are
> you considering your 100% token budget and the very low jon-attention budget? I'm gonna let you do plan
> mode here. Should you take a nap after this plan and resume coordination after (via nap, and or standard
> update) or...? Continue from current context?"

---

## Coordinator notes — NO AUTHORITY

### On "how many times did I say that"

Searched the tracked repo and the corpus. **Every hit is a document stating the call is Jon's and still
blank; no record of him giving it was found.** That is *not* evidence he did not — the mirror corpus is
current only through **export 2026-07-22**, and his claude.ai turns after that date are invisible to it.
His turn-6 dispatch reached the coordinator with literal `___` blanks in it. **Most likely reading: he
answered on the claude.ai side and the answer did not survive relay.** Fourteen stale "still blank"
statements across five files were carrying the false claim; all corrected in PR #125.

### His amendment 3 was correct — verified, not assumed

Checked directly on 2026-07-25:
- **E2 as written carries no percentage and no defined population.** `source-page-standard-v4.md:40-45`
  specifies anchor *form* and resolution; `:89` lists the threshold as unresolved. The `≥95% of
  substantive Key Claims` figure exists only in the **deprecated v3** document.
- **"Substantive" is nowhere operationally defined**, and **claims-vs-anchors is unresolved in the text.**
- Three implementations measure three different populations: `lint.py:63` a page-level any-anchor boolean;
  `lint.py:102` % of *pages*; `lint_citation_coverage.py` % of *pooled claims corpus-wide* (766/1614 = 47%
  today) under a **looser predicate than E2** — it accepts `[[link]]`/`[inferred]` on session pages, so 47%
  is an **upper bound** on E2-session coverage; `census.py:77` a raw anchor count.
- **No implementation applies the 95% gate to E2's stated population.**

### His amendment 2 is also a restatement, not a new request

Per a fable-mirror records query: Jon asked for trunk-and-type stratification on **2026-07-17**, verbatim —
*"stratified random sample… Of conversation summaries, and other types of articles. In all 4 trunks"* — and
for multi-method testing of a single measure on **2026-04-10**, verbatim — *"I know their are multiple ways
we should test this. You should too."* Neither was built. **Category slicing exists in no form today:**
`trunk` and `kind` are row attributes in the generated tables but no metric is grouped by them, and both
scripts' `trunk_of()` discards the `wiki/sources/<domain>/` subdirectory entirely.

The per-directory anchor table is the argument for his amendment: `sources/reference` **0 of 5** pages
anchored, `personal/sources` **13 of 49**, while `sources/fbc` is **14 of 19**. An aggregate hides a 0%
bucket behind a 74% one.

### Two findings he has not yet been told, flagged for the next batch

1. **`audit_state`'s hash is of the RAW SOURCE FILE, not the wiki page.** A page marked
   `verified@{v4.0, …}` can have its claims rewritten and its anchors changed and **the stamp still reads
   verified** — page edits are not in the re-verification trigger set. This is material to T1.
2. **The conformance ledger discards the version from `audit_state`** (`lint.py:84` splits on `@`), so the
   one page verified at **v3.0** is indistinguishable from the eleven at v4.0 — defeating the G3 authority
   rule the field exists to serve.

### Cross-links

`[[coordinator]]` · `wiki/intake-triage/jon-turn6-six-answers-and-su-first-2026-07-25.md` ·
`wiki/references/source-page-standard-v4.md` · `exchange/path-to-complete-2026-07-25.md` ·
`scripts/lint_citation_coverage.py`
