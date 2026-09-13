---
slug: wikiskill-and-the-retrieval-half-we-own
title: "WikiSkill: we built the same three layers independently, and every one of our defects is in the joints the paper does not test"
kind: concept
status: LIVE
sensitivity: T1
date: 2026-09-01
created: 2026-09-01
owner: professional
author: Professional (Opus seat, session a90e0dcc)
grounded_in: arXiv:2608.27454 (Google Research, fetched 2026-09-01) + this trunk's own measured raw/wiki/skill layers
calibration: measured
review: UNREVIEWED BY ANY SEAT BUT ITS AUTHOR — see the blind-spot section, which says why that matters here more than usual
---

# The paper, and why it is not a validation

**WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution**
(arXiv:2608.27454, Google Research). Three layers:

| layer | theirs | ours | measured, 2026-09-01 |
|---|---|---|---|
| **Raw** | immutable execution traces the Wiki Maintainer *samples every iteration* | `raw/session-archive/` | 6 sessions · 43 JSONL · **18,348 lines** · 44.0 MB · **0 parsed markdown** |
| **Wiki** | `patterns/` + `logs.md` + **`skill-impact.md`** | `wiki/concepts/` + `wiki/log.md` + ⛔ **nothing** | 83 pages · **64 distinct frontmatter fields, none universal; only 12 of 83 carry all four of {title, kind, status, date|created}** |
| **Skill** | atomic `SKILL.md` per skill + `PURPOSE.md` mapping back to its motivating pattern | `.claude/skills/` | ⛔ **2 skills**; 29 checks inside ONE 64 KB shell file; **C12, C20, C21 named by ZERO wiki pages** |

⛔ **THE CONVERGENCE IS NOT THE FINDING.** We reached `raw/ → wiki/ → skills/` without the paper,
which is mildly reassuring and worth nothing operationally. ⭐ **The finding is that all three of
our defects sit in the JOINTS between layers, and the paper does not test a single one of them.**

---

# ⛔ DEFECT 1 — our Raw layer has never once been read by the thing that maintains the wiki

**In WikiSkill the Wiki Maintainer samples traces each iteration and does root-cause analysis on the
failing ones.** ⛔ **Ours cannot: `[m]` ZERO markdown, and until today this trunk recorded "no parse
script exists."**

⭐ **So every one of our 83 pages is grounded in WHAT A SEAT REMEMBERED AT CLOSE, never in the
trace.** That is the material blind spot, stated structurally rather than as a worry: **the wiki is
not incomplete because we wrote too little. It is incomplete because the maintainer has never had
read access to its own evidence.**

`[m 2026-09-01]` **The archive is not empty of Jon — it was never looked at.** `origin.kind` is a
three-value vocabulary already minted by the harness on every line:

| `origin.kind` | count | what it is |
|---|---|---|
| **`human`** | **59** | ⭐ **Jon's own turns — 17,018 characters, in our tree, unparsed** |
| `peer` | 42 | cross-trunk messages |
| `task-notification` | 12 | machine |

⚠️ **AND THE FIELD SOLVES A PROBLEM THE UNIVERSAL LAYER CALLS OPEN.** That layer warns *author-login
is not authorship* and that subagent JSONLs hold messages no main transcript carries. **`origin.kind`
separates them mechanically.** ⛔ **This trunk reads it in exactly zero scripts.**

---

# ⛔ DEFECT 2 — our Skill layer has no unit small enough to accept or reject

**WikiSkill's proposer emits *"an atomic proposal targeting a single skill."*** Acceptance is
`if R(Tval,k) > Rbest: accept; otherwise rollback` — **and the wiki is never rolled back, only the
skill.**

⛔ **We cannot do either half.** `[m]` **29 checks live in one 64,500 B shell file inside one skill
directory. `C26` cannot be rolled back without touching `C1`–`C29`.**

> ⭐ **THAT IS WHY WE HAVE NO `skill-impact.md` AND COULD NOT HAVE ONE: the architecture has no unit
> the ledger could have a row about.**

⚠️ **The consequence is already visible in our own record.** The paper keeps rejected proposals *with
their unified diffs* so the proposer *"can consult [them] in subsequent iterations to avoid repeating
failed modifications."* **Our rejected proposals live as prose in `wiki/log.md`.** ⛔ **A rejected
proposal recorded only in prose gets re-proposed** — and this trunk has re-derived the same defect
classes on consecutive nights.

---

# ⛔ DEFECT 3 — three checks have no recorded motivating finding

**WikiSkill's `PURPOSE.md` maps every skill back to the wiki pattern that caused it.**
`[m]` **`C12`, `C20`, `C21` are named by ZERO pages under `wiki/concepts/` or `wiki/tracker/`.**

⭐ **The universal layer already rules why this is fatal rather than untidy: *a review checked against
the finding can only ever be as good as the finding.*** ⛔ **A check whose finding was never written
cannot be reviewed at all — it can only be trusted or deleted, and deletion is barred.**

---

# ⭐ THE STRATEGIC READ: their benchmark numbers do not transfer, and the reason is our whole problem

**The paper's own stated limitation, verbatim:**

> *"To isolate skill quality and avoid confounding effects from skill retrieval, our study… directly
> injects active skills into the agent prompt. This setup does not evaluate skill retrieval or
> triggering."*

⛔ **Every gain they report — 12.3 % at 4B, 17.5 % at 9B, 23.9 % at 27B — is a gain from skills
ALREADY SELECTED.** ⚠️ **We are past the point where injection is possible: 83 wiki pages, 339
inbound letters, 17,871 federated docs.** ⭐ **So adopting their loop wholesale buys a measured
nothing, and the half they declined to evaluate is the half Jon is asking about.**

> ⛔ **AND UNDER NO-DELETION, METADATA IS OUR ONLY PRUNING MECHANISM.**
> The paper names wiki pruning as an open problem. **We have a strictly harder version — Jon ruled
> *"Yeah no deletion"* — so the wiki only ever grows.** ⭐ **Retrieval is therefore the only lever,
> and metadata is the only lever on retrieval. That is what converts the frontmatter template from
> hygiene into the load-bearing half of PR-3.**

---

# ⭐ CROSS-MODEL TRANSFER: their strongest result is the one thing we have and they had to simulate

**Their finding: transferred skills frequently beat self-evolved ones** — 27B-evolved skills lift a
9B model to **50.5 %** on SpreadSheet against **33.6 %** self-evolved and **24.3 %** with none.

⭐ **We are a genuine multi-family fleet — Opus seats, a Gemini seat (Antigravity), Haiku and Sonnet
lanes, Fable.** **They constructed cross-family transfer as an experiment; we run it as
infrastructure and have never measured it once.**

⚠️ **And they name our risk exactly:** negative transfer arises when skills encode *"low-level
workarounds… which help the smaller model avoid execution failures but constrain stronger models."*
⭐ **That is a MECHANISM for Jon's standing fence *"do not send Antigravity our standards"* — the
fence was a judgment call and now has a reason behind it.**

---

# ⛔ THE INSTANCE THIS PAGE COMMITTED WHILE BEING WRITTEN

**Phase 2 has stood open on Jon's own charge, recorded in `WAKE.md` as *"no parse script"*.**

`[m 2026-09-01 17:0x]` **It exists. `CFL/skills/chat-exporter/scripts/convert-claude-code.py` —
1,406 lines, `--self-test`, `--inspect`, `--run`, JSONL in, markdown out.** And a role taxonomy that
had already solved the discriminator this session got wrong: ***"in a SUBAGENT transcript the
user-role string records are the ORCHESTRATING agent's brief, not Jon"*** — role `D`, Dispatch.

⛔ **I missed it on my first search because my population was `scripts/`. It lives in `skills/`.**

> ⭐ **THE ARTIFACT WAS PRESENT, WELL-NAMED, SELF-TESTING, AND IN A SIBLING'S PACKAGED SKILL — AND
> THE SEARCH THAT CONCLUDED "IT DOES NOT EXIST" WAS TRUE ABOUT ITS OWN POPULATION AND FALSE ABOUT
> THE WORLD.** ⛔ **This is the retrieval defect the whole page is about, committed inside the page.**

**Nor is it alone.** `[m]` **Personal's `index_jon_arrivals_v2.py` (831 lines) walks ALL trunks and
carries Professional in its trunk map at `:150` — it was built to index this trunk and this trunk
has never invoked it.** CFL's `scripts/audit/turn_index.py` (267 lines) is the anchoring half.

> ⛔ **BEFORE ANY BUDGET IS SPENT PRODUCING, IT MUST BE SPENT RETRIEVING. Three sibling trunks had
> already built Phase 2 and the cost of not asking was the whole ticket.**

---

# ⚠️ A DELEGATED SWEEP UNDERCOUNTED THIS PAGE'S CENTRAL NUMBER BY 6.2× — IN THE EXONERATING DIRECTION

`[m]` A Haiku census of the same 43 files returned **2,955 lines**; re-derived here: **18,348**.
`isMeta` **4 → 120**. Human turns **41 → 309**.

⛔ **Had it been published, this page would have claimed the archive holds almost no Jon.** It holds
59 turns of him by the harness's own field. ⭐ **The delegation is a NEW venue for
[[population-definition-is-not-population-exclusion]]: a subagent's count is not a measurement until
the coordinator re-derives it.** ⚠️ **The sweep also classified fork boilerplate I wrote as human
text — the discriminator CFL's converter already carries as role `D`.**

---

# ⛔ THE MEASURED METADATA STATE, AND WHY A 64-FIELD SCHEMA IS NOT A SCHEMA

`[m 2026-09-01, 83 pages]` **This is Jon's own complaint, measured in THIS trunk, not CFL's:**

| field | pages carrying it | distinct values | reading |
|---|---|---|---|
| `created` | 58 / 83 | — | the most universal field reaches **70 %** |
| `kind` | 52 | 13 | |
| `title` | 47 | — | **43 % of pages have no title field** |
| `status` | 31 | ⛔ **28** | ⭐ **24 of them appear exactly ONCE. `status:` is a free-text field wearing an enum's name** |
| `calibration` | 25 | 23 | the grading field is itself ungraded |
| `slug` | ⛔ **8** | — | ⭐ **the retrieval key, on 10 % of pages — and the resolver depends on it** |

**64 distinct field names. 37 of them appear on exactly one page.** `[m]` **12 of 83 pages carry all
four of `{title, kind, status, date|created}`.**

> ⛔ **A SCHEMA WITH 64 OPTIONAL FIELDS IS NOT A SCHEMA. IT IS A HABIT WITH FRONTMATTER SYNTAX.**

✅ **THE PROPOSAL — FIVE REQUIRED FIELDS, EVERYTHING ELSE FREE.** Free fields are not the defect;
**required fields that nothing requires** are.

1. `slug:` — the retrieval key. **Currently 8/83, and lint's own resolver depends on it.**
2. `kind:` — CLOSED, enumerated vocabulary.
3. `status:` — CLOSED vocabulary. ⛔ **28 values across 31 pages is the single worst number here.**
4. `date:` — strict `YYYY-MM-DD`, **minted by a script, never hand-typed** (`C27`'s whole class).
5. ⭐ `grounded_in:` — **the new one and the load-bearing one: a pointer to the RAW trace or the
   primary that motivated the page.** This is WikiSkill's `PURPOSE.md`, generalised from skills to
   pages. ⛔ **A page with no `grounded_in:` is a page grounded in a seat's memory.**

⛔ **AND IT GOES AT THE MINT, NOT AS A SWEEP.** New pages must carry all five; the 83 existing are a
**backlog with a printed count**, never a normalisation pass. ⭐ **The standing constraint already
rules this** — *do not sweep the 46,000 backticked refs or the 56 frontmatter pages; both fixes are
at the mint* — and CFL's own ticket carries the reason: *a trunk that normalises 900 pages without
changing what mints them is back here in a month, and the second pass costs a PR out of only three.*

---

# ⭐ BUDGET — SPEND EACH TIER WHERE ITS FAILURE MODE IS CHEAPEST

**Jon asked how to spend the Gemini and Claude budgets. The measured answer starts with a refusal:**

> ⛔ **BEFORE ANY BUDGET IS SPENT PRODUCING, IT IS SPENT RETRIEVING.** ⭐ **Phase 2 was open for
> days on "no parse script exists" while a 1,406-line self-testing converter sat in a sibling's
> packaged skill. That ticket cost more than the whole parse chain was worth.**

| budget | spend on | why THIS tier | verified by |
|---|---|---|---|
| **Haiku** | the parse chain: 43 JSONL → chunked markdown, via CFL's `chat-exporter`, **run not rewritten** | deterministic, adjudicates nothing, verified by COUNT | ⛔ **line counts must reconcile, and the coordinator RE-DERIVES them — this session's Haiku census was wrong by 6.2×** |
| **Sonnet** | metadata backfill, **ONE PAGE PER INVOCATION**, against the five-field schema | bounded judgment; we already own fresh-context `page-grader` / `cold-grader` | a grader that never saw the writer's reasoning |
| **Gemini (Antigravity)** | ⭐ **GRADING our artifacts, never producing them** | its agreement is evidence **only because it is a different model family** — the paper's cross-family transfer result is the warrant | disagreement rate published in both directions |
| **Opus (this seat)** | schema design · adjudication · the accept/reject ledger · PR-3 inputs | never the sweeps | — |

⛔ **THE ANTI-PATTERN, NAMED SO IT IS NOT DRIFTED INTO: spending Gemini on PRODUCTION doubles our
output and destroys our only differential instrument.** ⭐ **Once Antigravity writes our artifacts,
its agreement with them is worth nothing** — and agreement from a different family is the single
most valuable signal this fleet can generate.

---

# ⚠️ ADJUDICATION OF THIS RUN'S SWEEPS — required in-session, and one lane is REJECTED

**The `/dream` adaptation note rules that packets are adjudicated in the same session or the run is
not started. Three lanes ran.**

| lane | verdict |
|---|---|
| **raw-layer census** (Haiku) | ⛔ **REJECTED on its counts** — 6.2× low, and it classified my own fork boilerplate as Jon. ✅ **ACCEPTED on its key inventory**, which is what produced `origin.kind`. |
| **metadata census** (Haiku) | ✅ **ACCEPTED on frontmatter and orphans** — and it CORRECTED me: 64 fields, not the 31 my own hyphen-excluding regex found. ⛔ **REJECTED on dangling links.** |
| **letter-transfer audit** (Sonnet) | ✅ **ACCEPTED, and the best-disciplined of the three** — it refused the story its own tally invited, self-corrected a count mid-run, and marked a residual UNKNOWN rather than zero. |

⛔ **WHY THE DANGLING-LINK HALF IS REJECTED, AND IT IS MY ERROR NOT THE LANE'S.** It reported 10
unresolved targets. `[m]` **`a-gate-that-fires-red-on-correct-behaviour.md` EXISTS**; the rest are
`[[slug]]`, `[[name]]`, `[[wikilink]]`, an empty target and an ellipsis — **syntax documentation,
not links.** ⭐ **The lane reported *"In code fences (excluded): 0"* — a VACUOUS exclusion printed
as a clean zero.**

> ⛔ **THE SKILL'S OWN METHOD CONSTRAINT PREDICTED THIS EXACT FAILURE AND I DISPATCHED WITHOUT
> IT.** It records trial 1 at **5/5 false positives** on stem-only matching and the MR-94 rerun at
> **~47 of 57** syntax examples, and rules that consuming lint's resolver is **MANDATORY, not
> preferred.** ⭐ **A third false-positive family was produced by re-implementing resolution a third
> time — by the seat that had read the warning that morning.**

✅ **Real dangling links after adjudication: ZERO — except the one this page created and removed.**

---

# ⛔ BLIND SPOTS, AND THE LIST IS NOT CLOSED

**Jon: *"I still don't trust the wikis completeness and quality enoguh to say you have no remaining
material blind spots."*** He is right. Named, not enumerated exhaustively:

1. ⛔ **NO PAGE IN THIS WIKI HAS EVER BEEN GRADED BY A SEAT THAT DID NOT WRITE IT.** Cross-trunk
   review happens on LETTERS. **This page included.**
2. ⛔ **The corpus that should ground the wiki is unreadable to it** (Defect 1).
3. ⚠️ **`[work]` means the largest domain — his actual job — is deliberately under-recorded.**
   ⭐ **That is a RULED blind spot, not a defect, and must never be filed as one.** But it bounds
   every completeness claim this wiki can make.
4. ⚠️ **339 inbound letters; `[m]` only **41 (12.1 %)** carry a filename-level trace in our own record, and **6 of the 7 expired dated letters** have none. ⛔ **That is not 298 unread — it is 298 with no footprint, and the two are not distinguishable from here.** ⭐ **The channel the paper says is our strongest lever has a 12 % visible drain.**
5. ⛔ **AND THIS LIST IS NOT ENUMERATED CLOSED** — the universal layer's *naming a closed set is the defect*. A refusal
   to rank inside a set silently closed still reports a bounded space.

`related:` [[population-definition-is-not-population-exclusion]] ·
[[check-the-definition-before-re-measuring]] · [[the-escape-consumed-by-the-wrong-layer]]
