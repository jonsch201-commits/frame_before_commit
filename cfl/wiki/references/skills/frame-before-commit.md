---
title: "frame-before-commit — accumulated session record"
trunk: fl
branch: [cfl, fbc]
sub_branch: [skills]
branch_reason: "R-REF-SKILLS; secondary branch from title/slug (fbc) — load-bearing-for"
kind: skill-record
skill: frame-before-commit
status: v1
created: 2026-08-06
corpus_current_through: export 2026-08-06 (1,167 transcripts indexed; 1,132 re-read here)
generated_by: scripts/audit/skill_record.py (counts) + hand-verification (verdicts)
---

# frame-before-commit — accumulated session record

**Why this page exists.** Jon, verbatim, 2026-08-06:

> *"For each skill, in the wiki, accumulated session record. Not just explicit uses, but implicit
> ones. Opportunitys where you might have considered using it but did not, and cases where you did
> and cases where you kinda did… the wiki shpuld help you improve the skill."*

**The acceptance test is the last clause.** This page is organised around what should change about
FBC. Regenerate the counts with `python scripts/audit/skill_record.py --skill frame-before-commit`.

**Read `wiki/intake-triage/B-8-improving-fbc-and-gbs-2026-08-06.md` first.** This page does not
re-derive B-8; it measures what B-8 asserted, and **corrects it in two places** (§5, §6).

---

## 1. The headline three classes — and the first thing to know is that they are not three classes

`corpus_index.py --query-skill frame-before-commit`, verified today over **1,167 indexed
transcripts**:

| class | count | what the query actually tests |
|---|---|---|
| USED | **252** | the marker string is present *anywhere* in the file |
| PARTIAL | **134** | marker present, no `[COMMIT]` |
| APPLICABLE-NOT-USED | **13** | a declared trigger phrase in **Jon's own turns**, no marker |

**`PARTIAL` is a subset of `USED`. Overlap: 134 of 134 — measured, not inferred.** Read
`three_class`: `USED` is every marker-bearing row; `PARTIAL` is the subset of those lacking the
completion literal. So "252 USED against 134 PARTIAL" is not a ratio between two classes. It is
**252 files, of which 134 never reach `[COMMIT]`** and 118 do.

The brief that commissioned this page quoted **251**. Today's index says **252**. The difference is
one file and it is not interesting; the fact that a headline number moved by one between two
readings a few hours apart, with nobody able to say which file, is the reason denominators are
printed on every run.

### Disjointly, after deflation

| | files | note |
|---|---|---|
| carry the marker string | 252 | |
| …**template/documentation only** | **28** | `{N} branches`, `label: TBD`, `[DELTA: Bn (LABEL)` — SKILL.md pasted into a brief |
| **run-shaped** | 89 | numeric branch count, or a real `[BRANCH REGISTRY]`, or a `[COMMIT]` carrying the mandated opening sentence |
| …minus re-emissions (extraction subagents, `_superseded/`) | −17 | B-8 §9.1 measured the same duplication: one delta in five files |
| …minus **this audit's own agents** | −4 | an audit of FBC emits FBC's markers; B-8 §9.2 caught this and so must any successor |
| **original runs** | **69** | |
| …of which doc-*reading* agents (`explore-read-fbc-skill`, `wiki-fbc-pages`, citation audits) | 14 | a subagent sent to *read* FBC quotes `[COMMIT]` and the word "converged" |
| **STRONG runs** — numeric header **or** the mandated opening sentence, readers excluded | **51** | the number this page uses |

**252 → 51 is the whole measurement problem in one row.** Four out of five marker-bearing files are
not runs.

---

## 2. The 13 APPLICABLE-NOT-USED, enumerated — and the class is measuring the wrong thing

The brief called this "the most valuable number on the page." It is valuable, but not for the
reason expected: **it is valuable as a diagnosis of the detector.**

| date | file (under `raw/transcripts/`) |
|---|---|
| 2026-03-29 | `claude-ai/fl/how-to-use-claude/chat-2026-03-29-280197-stylomantic-decoding-layer-planning.md` |
| 2026-05-06 | `claude-code/fl/code-2026-05-06-e4c393-continue-improved-testing-framework.md` |
| 2026-05-25 | `claude-ai/personal/herald-of-home-and-life/herald-origin-2026-05-25-06f683.md` |
| 2026-05-26 | `claude-ai/_routing/incoming/chat-2026-05-26-06f683-herald-of-home-and-life.md` |
| 2026-06-08 | `claude-ai/personal/chat-2026-06-08-2c2870-brother-hl-l2380dw-scanning-not-working-on-windows.md` |
| 2026-06-19 | `claude-ai/_routing/incoming/chat-2026-06-19-7f2022-gulf-states-and-nuclear-agreements-fact-checking.md` |
| 2026-06-27 | `claude-ai/_routing/incoming/chat-2026-06-27-a6314b-planning-asops-ingestion-and-implementation.md` |
| 2026-07-02 | `claude-ai/fl/agent-interaction/agent-interaction-framework-2026-07-02-5990f2.md` |
| 2026-07-17 | `claude-ai/_routing/incoming/chat-2026-07-17-a3e6cf-model-triage-and-weakness-detection.md` |
| 2026-07-25 | `_superseded/chat-2026-07-25-12341c-herald-family-planning-framework-and-governance-se.md` |
| 2026-07-27 | `claude-ai/_routing/incoming/chat-2026-07-27-12341c-herald-family-planning-framework-and-governance-se.md` |
| 2026-07-30 | `claude-ai/_routing/incoming/chat-2026-07-30-4b4655-untitled.md` |
| 2026-07-30 | `claude-ai/_routing/incoming/chat-2026-07-30-d1321c-pressure-and-effort-as-training-rewards.md` |

**Structural notes before anyone treats these as thirteen missed opportunities.** Rows 10 and 11 are
**the same conversation** (`12341c`), once in `_superseded/` and once live — so the class holds **12
distinct conversations**, not 13. Two are personal-trunk (`06f683` herald-origin, `2c2870` printer
troubleshooting); a printer that will not scan is not an occasion for divergent reasoning, and
`corpus_index` prints the reason it fires anyway: *"a mention and a request are the same string."*
Its own hand-check found **4 of 4 FBC candidates were Jon discussing the protocol, not asking for
it.** Treat this table as *worth reading*, never as *a skill was missed*.

### The brief's test, answered: the detector is wrong, not the claim

The brief said: *"'Zero genuine runs since 2026-07-19' means the not-used class should be large in
recent months; if it is not, say whether the detector or the claim is wrong."*

**It is not large — 6 of 13 are dated 2026-07 or later and none are in August — and the detector is
what is wrong.** The reason is structural and is the same defect `gbs_record.py` found in GBS:

> Tier-1 APPLICABLE-NOT-USED fires on **a declared trigger phrase in Jon's turns** — `"frame before
> commit"`, `"what am I missing"`, `"run the protocol"`, `"explore alternatives"`. Every one of
> those is a **meta-request**. So the class measures *"Jon asked for FBC and no branches appeared."*
> **A class defined that way cannot grow when Jon stops asking. It shrinks.** The signal that FBC
> fell out of use and the signal the detector uses are the same signal, pointed in opposite
> directions.

**An FBC occasion is not signalled by Jon naming FBC.** It is signalled by the object-level
situation the skill exists to catch — FBC's own frontmatter: *"especially valuable for design
decisions, research framing, statistical choices, and any question where motivated reasoning or
anchoring is a real risk."*

### Tier 2 — the object-level precursor

`skill_record.py` adds a second tier: **a commitment made on a design question with no alternatives
anywhere in the window, in a file with no run.** Result: **69 files, 106 occasions.**

| month | 2026-03 | 04 | 05 | 06 | 07 | 08 |
|---|---|---|---|---|---|---|
| Tier-2 occasions | 2 | 3 | 9 | 6 | **35** | **14** |

**That is the shape Tier 1 could not produce.** Unbranched design commitments rise sharply in July
and continue through August — exactly the months in which FBC use thins out. The two tiers are
anti-correlated because they measure opposite things.

**This over-counts and is a candidate list.** "A design decision was made without alternatives" is
not a string; the negative condition is a ±400-character window, and a window is not a document.

---

## 3. Deltas: 787 hits, 263 distinct, and 195 of them are the template

| | count |
|---|---|
| `[DELTA:` raw occurrences | **787** |
| distinct after dedupe on normalised text | **263** (deflator 524 = re-quotes across files) |
| **EMPTY** — the SKILL.md template left in the output | **195** |
| **MISCREDITED** — source is not a branch (`[DELTA: your messages — …]`) | **9** |
| credited to a branch id (Rule 6's required shape) | 465 |
| credited to nothing identifiable | 118 |
| of the branch-credited, **lexically cosmetic** | **54** — *lower bound only* |
| **distinct NON-EMPTY assertions** | **231** |
| real vs cosmetic | **UNKNOWN — needs a cold grader** |

B-8 §9.1 reported *"~274 real delta assertions."* The distinct count is **263**, and **231** once
template placeholders are removed — close enough that B-8's arithmetic is sound. **The word that
was not earned is "real."** Whether an outcome changed is a judgment, not a string; B-8's own
Revised Improvement 2 asks for the cold grader that would settle it, and it has not been run.

**195 empty deltas — a quarter of all delta occurrences — are Discipline Rule 6's own template
emitted verbatim**: `[DELTA: Bn (LABEL) — Without this branch, commit would have said: X. With it,
commit says: Y instead.]`, and variants that trail off mid-sentence (`changed the committed answer
by: ...`). A rule whose compliance shape is a fill-in-the-blank gets filled in with the blank.

---

## 4. Reconciling 274 deltas with a flagship run that moved nothing

This is the tension the page was commissioned to state rather than smooth, and the resolution is
mechanical rather than rhetorical.

**The flagship, `chat-2026-07-18-a8bbda`.** Its `[COMMIT]`, verbatim (B-8 §9.4):

> *Without branching, I would have said: intimate; NO-GO until Packet A; full plan attached.*
> ***With branching, that stands, amended four ways…***

Measured today, that file carries **`[META]`, `[COMMIT]`, the mandated opening sentence, three
branch-credited deltas, and convergence language** — while its headline verdict is word-for-word the
pre-branch instinct.

**Those two facts are not in tension, and that is the finding.**

> **A `[DELTA]` is scored per branch. The verdict is scored once. Nothing in the protocol connects
> them.** Discipline Rule 6 asks each branch whether it changed *"what commit would have said"* —
> and a branch that adds a caveat, an amendment, or a footnote answers *yes*, truthfully. Three
> honest deltas are therefore fully compatible with a headline that never moved. **FBC has no field
> for "did the verdict move," so 787 delta assertions carry no information about whether any
> decision changed.**

Across the **51 strong runs**:

| | count | of |
|---|---|---|
| runs whose text **names convergence** as a finding | **24** | 51 |
| runs that reached `[COMMIT]` with **zero non-empty deltas** | **7** | 51 |
| **both at once** | **6** | 51 |

**Those 6 are the structural trap, counted.** Discipline Rule 7 blesses honest convergence
(*"forced divergence is worse than honest convergence"*); Self-Scoring calls zero deltas *"a red
flag, not a good result."* A run in that cell satisfies both readings simultaneously, so **no
instrument the protocol carries can call it a failure.** A session found this in-corpus and said it
plainly (`code-2026-07-08-774a3a`): *"zero deltas is labeled a 'failure mode' by the protocol's
scoring — meaning zero-delta results cannot be used as evidence against the protocol."*

**And the counter-evidence, same corpus, and it is decisive about the fix.** B-5 §0 (2026-08-06) is
a PURE 4-branch run that **wrote its instinct to a file before generating a single branch**, with
four enumerated commitments, and scored `[COMMIT]` against that sealed text rather than a
recollection. **Three of its four commitments were overturned.** That is FBC working — and it works
precisely because it removed the step FBC's own Condition A names as the defect: *"the model is not
a reliable narrator of what it would have said had a branch not existed."*

**So the honest reading is not "FBC does not work."** It is: **FBC produces real movement when the
counterfactual is sealed in advance, and unfalsifiable movement when it is not.** The 787 deltas are
mostly the second kind. `skills/frame-before-commit/SKILL.md` gained a mandatory pre-branch seal on
2026-08-06 for this reason.

---

## 5. CORRECTION to B-8 §9.2 — "zero genuine runs since 2026-07-19" is wrong

B-8 concluded: *"Last genuine FBC execution anywhere: 2026-07-19… **Zero in August.**"* Measured
against run shape rather than filename-date histograms, **that is false in both halves.**

Strong runs dated 2026-07-19 or later, with structure verified per file:

| date | file | shape |
|---|---|---|
| 2026-07-19 | `subagents/49a1c0/…a4b958-general-purpose-l3-wikisettings-executor` | registry, META, COMMIT, 2 deltas (**both EMPTY**), convergence |
| 2026-07-21 | `claude-code/fl/code-2026-07-21-8d4396-fable-mirror-pipeline-ratification…` | **numeric header**, registry, META, COMMIT, 2 deltas, convergence |
| 2026-07-22 | `subagents/8d4396/…a216c1-cross-verifier-cold-review-of-76-taxonomy-packet` | numeric header, registry, META, COMMIT, 2 deltas |
| 2026-07-25 | `subagents/0fb7ca/…a14db3-fable-mirror-mirror-consult-on-lost-session-period` | numeric header ×2, META, COMMIT, 0 deltas |
| **2026-08-05** | `claude-code/code-2026-08-05-a69f31-fix-claude-code-settings-hook-configuration` | META, COMMIT, opening sentence, **7 deltas**, convergence |
| 2026-08-06 ×5 | today's wave — B-5, B-3, cold-fbc-synthesis, intake-executor, the FBC-seal run | genuine runs, but **produced by this programme of work**, not by ordinary use |

**The 2026-08-05 run is the load-bearing correction**: it predates this audit entirely and is an
ordinary working session. **August was not zero before anyone went looking.**

**Confidence: moderate, and the residual doubt is named.** These are structural verdicts — header,
registry, `[META]`, `[COMMIT]`, opening sentence, delta payloads — not hand-reads of each
transcript. A session that *pasted* a prior run would present the same structure. The 07-21 file is
a main session rather than a subagent, which makes a paste less likely but does not exclude it.

**What survives of B-8's claim, and it is the part that mattered:** original runs collapse from **23
in May to 12 in July**, six of August's belong to today's own audit wave, and Tier-2 unbranched
commitments rise to 35 in July and 14 in August. **Use did thin out sharply. It did not stop on
2026-07-19.**

---

## 6. CORRECTION — the most consequential run in the record is invisible to the marker registry

`corpus_index` scores `chat-2026-07-18-a8bbda` as carrying **no FBC marker at all**. It is not in
the 252. Yet it is the run B-8 §9.4 built its central finding on.

**Why:** SKILL.md:69 mandates both `[FRAME-BEFORE-COMMIT — {MODE} — {N} branches]` and
`[BRANCH REGISTRY]`. **The flagship emitted neither.** It went straight to `[META]` / `[COMMIT]`
with the required opening sentence. Every marker-presence instrument — `corpus_index`, and this
file's first two detector arms — is blind to it. A third arm (a `[COMMIT]` carrying the mandated
opening sentence) was added today for exactly this reason, and it recovers **5 of the 51 strong
runs** that both other arms miss.

**This is a compliance finding, not only a tooling finding.** The runs least compliant with FBC's
own output contract are invisible to every count anyone has published about FBC — including B-8's
and including the ones above.

---

## 7. What this record says should change about FBC

Ordered by evidence-per-unit-cost. None of these are ratified; all are for skills-master and a Jon
Gate.

1. **Add a verdict-level delta, distinct from branch-level deltas.** One line in `[COMMIT]`:
   `[VERDICT: moved | unmoved | narrowed]`, scored against the **sealed pre-branch instinct**.
   *Evidence:* §4 — 787 branch-level deltas carry zero information about whether a decision changed,
   and the flagship emitted three of them while its verdict stood. *Falsifier:* if across 10 runs
   `VERDICT: unmoved` never once appears, the field is decorative and the seal is not being honoured.

2. **Keep the pre-branch seal mandatory, and make the COMMIT cite it.** Added 2026-08-06.
   *Evidence:* B-5 §0 — a sealed run overturned 3 of 4 of its own commitments; the flagship, unsealed,
   overturned none. *Falsifier:* sealed runs should show a materially higher rate of overturned
   commitments than unsealed ones. If they do not, the seal is ceremony.

3. **Delete the fill-in-the-blank from the `[DELTA]` template, or make an unfilled one an error.**
   *Evidence:* §3 — **195 empty deltas, 25% of all occurrences**, are the template emitted verbatim.

4. **Resolve Rule 7 against the zero-delta red flag.** They currently make the protocol
   unfalsifiable by its own instruments (§4, 6 runs in the trap). The cheapest repair: convergence
   is only an honest finding **when reported against the sealed instinct** — otherwise it is
   unscored, not blessed.

5. **Make the header and `[BRANCH REGISTRY]` non-optional, or stop counting by marker.** §6 — the
   flagship is invisible to every published count. Pick one; carrying both is how a measurement
   programme gets a number it cannot check.

6. **Retire the trigger-phrase definition of "FBC was applicable."** §2 — it structurally cannot
   detect the failure mode it exists to detect. Tier-2 object-level precursors are the replacement,
   and they are candidate lists that need a grader, not a verdict.

7. **Still unbuilt, and it outranks all of the above:** the one-line-per-run decision log Jon named
   in April (B-8 §9.6) — *"Nothing logs whether the protocol changed a real decision."* Everything
   on this page is a proxy for that log.

---

## 8. What this record cannot see

- **Real vs cosmetic deltas** — printed `UNKNOWN`, never zero. Needs a cold grader.
- **Whether a Tier-1 or Tier-2 candidate was genuinely an occasion** — a judgment, not a string.
- **Whether a "strong run" was executed or pasted** — structure cannot distinguish them (§5).
- **Conversational FBC that left no markers** — by construction, invisible. The flagship proves this
  class is non-empty (§6).
- **Anything outside the export.** Corpus current through **export 2026-08-06**; the corpus is
  lossy and the wiki wins on conflict.

**Two instrument caveats recorded because they will bite the next reader.** (1) The template
deflator is lexical — a brief paraphrasing the format without `{N}` still counts. (2) Dates come
from filenames, so a re-quote carries the *quoting* file's date; the month histogram is over
original runs only and still over-reports recent months.

---

*Counts generated by `scripts/audit/skill_record.py` (self-test: 29 controls, 0 failures, negative
controls first). It reads `raw/` and writes nothing there. Verdicts are hand-made. No skill text was modified
by this page; nothing here is ratified.*
