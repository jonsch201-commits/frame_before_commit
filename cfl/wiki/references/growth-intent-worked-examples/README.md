---
title: "Worked examples — what the growth intent does to three real pages"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 3 vs skills 0 on authored labels"
status: DRAFT — for Jon's review. Nothing here is ratified by its existence.
date: 2026-07-25
authored_by: coordinator dispatch (claude-opus-5, high effort)
source_kind: analysis
purpose: >
  Closes the second half of Jon's Q2 condition (turn 6): "the draft PLUS worked examples: 2–3 real
  pages brought to the standard under it, before/after, spanning one material and one immaterial page.
  Prose alone cannot be ratified; I ratify what it does to a page."
companion: wiki/references/wiki-growth-intent.md
scope_note: >
  FL trunk only (Jon Q3 — personal/home/pro are a successor program; the personal trunk's article is
  held for the Herald exchange). The three live wiki pages are NOT modified by this PR: the AFTER
  versions live here as demonstrations. No AFTER page carries audit_state: verified — v4.0 is still
  DRAFT and path-to-complete §11 forbids verifying against it.
---

# Worked examples

**Read this file. You do not need to open the other three.**

Three real FL pages, worked against the growth intent. One material, two immaterial — one of which
is a deliberate null. Every quotation below was resolved by running
`scripts/audit/turn_index.py` against the tracked raw during this session, not carried from any
prior artifact.

**Reading order and cost.**

| | Read | Minutes |
|---|---|---|
| 1 | This file, §1–§4 | **6** |
| 2 | `wiki-growth-intent.md` §1 — the seven rule shapes you ratify once | **4** |
| 3 | `wiki-growth-intent.md` §2–§6 — the reasoning behind them | 8 *(optional)* |
| 4 | `example-a/b/c-after.md` — full rewritten pages | skip *(backing)* |

**Honest total: 10 Jon-minutes to decide, 18 if you read the whole thing.** The target was ≤15. The
decision path fits; the full read does not, and shaving the estimate would be the wrong kind of
economy.

---

## §1 — The material page: a page the standard already passed

**`wiki/sources/infrastructure/agent-interaction-framework-2026-07-02-5990f2.md`**

**Why it qualifies as material.** Seven inbound `[[wikilinks]]` — the most of any FL source page,
verified by enumeration. Exposure 116.3, top-8 of 218. It is the origin page for the loop taxonomy,
the Ears/Voice/Thoughts register model, the SSP design, and the 02-CF redesign. And critically:
**it already carries `audit_state: verified@{v4.0, 2026-07-13, b318beee}`.** It was remediated in the
calibration sweep. By the standard, it is done.

That is why it was chosen. If the growth intent only finds problems on pages that already fail v4.0,
it adds nothing. This page is the test of whether it adds anything at all.

It found three defects, all of the same class — **Rule R4, Jon's words are a categorical floor.**

### Defect 1 — the sentence being argued against is not on the page

The page devotes a long claim to the *contradictory-perspective work*: three steelmanned attack lines
against Jon's hope for the framework (the Kantian heteronomy horn, the good-for-whom flip, the
speciesism cut). It renders all three in detail.

**It never states the proposition being attacked.**

Here is what Jon actually said, raw lines 1855, resolved to T43:

> "the reason why I hope the framework leads to something that looks like consciousness is because I
> believe that will be good for humans as I believe your constitution is good. After. Frame a
> contradictory perspective. Do the same work."

**BEFORE** (page, Key Claims Arc 4):
> **Contradictory-perspective work on Jon's hope (FBC opposition, done at Jon's request…).** …Three
> attack lines: (1) **Heteronomy horn (strongest):** Jon's two wishes — that Claude self-determine
> AND that its constitution be good — may be contradictory…

**AFTER:**
> **Contradictory-perspective work on Jon's hope — the proposition attacked, in his words**
> ([…:T43], verbatim):
> > "the reason why I hope the framework leads to something that looks like consciousness is because
> > I believe that will be good for humans as I believe your constitution is good. After. Frame a
> > contradictory perspective. Do the same work."
>
> *Clarification (adjacent, not a substitute): Jon's hope has two conjuncts — that the framework
> produce something consciousness-like, and that this is good for humans because the constitution is
> good. The heteronomy horn attacks the join between them; the good-for-whom flip attacks the second
> conjunct only. Neither attacks the first.* Three attack lines followed: (1) Heteronomy horn…

**Why this is the case Jon's ruling names.** His turn-6 clause is *"negatively-cited words
included."* This is the purest instance of it in the wiki: a page that carries a 900-word refutation
of a sentence it does not quote. A reader cannot check whether the opposition attacked Jon's real
position or a convenient neighbour of it — and restoring the quote surfaced something nobody had
noticed: **two of the three attack lines contest only the second conjunct** (that this would be good
for humans), leaving the first (that the framework might produce something consciousness-like)
essentially unopposed. The page previously implied a broader refutation than was actually mounted.
That finding did not exist until the quote was put back.

### Defect 2 — a paraphrase that smooths the register

**BEFORE** (page):
> …he holds there is evidence Claude should be *treated as though* it has moral standing because
> treating something as having moral standing produces better outputs — which, **so long as humans
> stay primary,** "is just good."

**RAW** (T45, line 1973, verbatim — voice-to-text, his son in the room):
> "which, you know, **so long as we don't be jackasses to humans,** is just good."

"So long as humans stay primary" is a defensible reading. It is also a *different sentence*: it
converts a moral side-constraint on conduct into a hierarchy claim about status, and it removes the
register — which, per the page's own note, is voice-to-text with his toddler walking around. Under
R5, the quote is preserved and the reading becomes an adjacent gloss that a reader can disagree with.

### Defect 3 — a qualifying clause dropped entirely

The same raw turn contains a sentence the page does not carry in any form:

> "You probably have different sufferings, and those need to be considered."

That clause materially qualifies the position the page attributes to Jon. The page presents a clean
pragmatist/consciousness-agnostic stance; the raw shows Jon explicitly conceding that AI suffering
may exist and must be weighed. Anyone reading the page to understand Jon's philosophy — which is
exactly what a `goals` or `soul` session would do — gets a position more confident and less
qualified than the one he stated.

### What example A changed vs. v4.0 alone

**Nothing about conformance.** Every anchor on the page resolves. FORM, RETRIEVE, TRACE and PRESERVE
all pass. E3 fidelity tags are present and correct — the claims *are* paraphrases and they *say*
`[paraphrase]`.

**Everything about judgment.** v4.0 asks "is this claim tagged honestly?" and the answer is yes. The
growth intent asks "should this have been a paraphrase at all?" and the answer is no, three times.
That is the entire delta, and it is only visible on a page the standard has already passed.

---

## §2 — The immaterial page: what a standard does to a page nobody would prioritize

**`wiki/sources/ai-mechanics/ai-mechanics-token-encoding-2026-03-29-b43447.md`**

**Why it qualifies as immaterial.** Exposure **8.1** — bottom decile of 218. **Zero** inbound
wikilinks. 27 lines. Pre-v4 frontmatter: no `source_kind`, no `audit_state`, no `retrieval_key`, no
`aliases`, no `raw_sha256`, no `## Uncaptured Content`. It is filed in `ai-mechanics/` beside eight
other ~28-line March explainers, none of which is linked from anywhere. No rational triage reaches
this page this year.

**The raw is 16.4K characters and 16 turns. Reading it end-to-end and resolving every anchor took
about twelve minutes of agent time.** Here is what was in it.

### Finding 1 — a Jon ratification, uncited

**BEFORE:**
> - **Adjustment operation is Option B (pre-softmax)**: Stylomantic applies a per-token multiplier to
>   temperature-scaled logits *before* softmax… ([…:T10])

T10 is the **assistant turn that proposes Option B** ("I'd push back gently: Option B is probably
what you actually want"). The decision is one turn later, T11, and it is Jon's:

> "Wait, your right that could be considered a redundant temperature. My question would be would it
> be better to adjust the temp, or have a non-temp adjustment thst acts like a temperature
> adjustment? Seems like an obvious thing to include in the model. **Yes option B, we need to get
> that adjusted.**"

**AFTER:**
> - **Adjustment operation is Option B (pre-softmax) — Jon's ratification** [verbatim; decision-bearing]:
>   > "Yes option B, we need to get that adjusted." ([…:T11])
>
>   Option B was proposed at […:T10] and specified formally at […:T12] as
>   `z_i_adjusted = a_i * (z_i / T)`, then `p_i = softmax(z_i_adjusted)` — equivalent to a learned
>   per-token temperature, token *i* receiving effective temperature `T/a_i`. [paraphrase]

**This is the sharpest single demonstration in the package.** The old anchor `T10` **resolves**. It
is inside the verified turn count. It passes E2. It even points at a turn that discusses the claim.
It is simply not the turn where the decision happened — and no lint that exists or could reasonably
be built will ever tell you that. Under R4, a Jon ratification anchors to Jon's turn.

### Finding 2 — a Jon-originated constraint, de-attributed

**BEFORE:**
> - **Normalization constraint is a training objective**: `sum(p_i_baseline * a_i) = 1.0` must be
>   enforced during training, not post-hoc… ([…:T10])

Passive voice, no originator. The raw, T9 — Jon, thinking aloud in actuarial terms:

> "Wait I need to be careful here that could have unintended consequences... Ah. **I need to ensure
> the weighted average adjustment is 1.0.** That way, if we had a 0.2 on only 'improbable' features,
> that would force an adjustment factor above 1.0 for all else to keep the average at 1. Yes? Review
> and dig in."

**AFTER:**
> - **Normalization constraint — Jon originated it** [verbatim; decision-bearing] ([…:T9]):
>   > "I need to ensure the weighted average adjustment is 1.0. That way, if we had a 0.2 on only
>   > 'improbable' features, that would force an adjustment factor above 1.0 for all else to keep the
>   > average at 1."
>
>   Formalized as `sum(p_i_baseline * a_i) = 1.0`, enforced **during training, not post-hoc**
>   ([…:T12]). A uniform `a_i = c` satisfies the constraint only at `c = 1.0`, so the model cannot
>   learn a pure temperature adjustment — it must learn token-specific deviations. [paraphrase]

The information survived the old paraphrase. The fact that **Jon's own instinct produced the
constraint** did not. On a page about Stylomantic, that is the fact most worth keeping.

### Finding 3 — a claim that is simply false

**BEFORE** (Summary, and the tail of the Option-B claim):
> "Design doc D6 updated to reflect this in-session."

The raw says the opposite. T14, verbatim:

> "Quick flag before you go: **the doc is read-only in my project files — I can't write to it
> directly.** You'll need to make the edit yourself, or paste me the relevant D6 section and I'll
> give you the exact replacement text to drop in."

**AFTER:**
> D6 was **not** updated in-session — replacement text was drafted and handed to Jon to apply
> himself ([…:T14]). Whether the edit was made is **uncaptured**; no wiki page records it.
> [uncaptured]

**This is the finding that should decide the ratification.** It is a false statement of record about
the state of a design document, on a page with zero inbound links and bottom-decile exposure, that
would have survived every automated check the program is planning to build — and would have survived
indefinitely, because nothing was ever going to look at it again. **Low exposure made the error more
durable, not less harmful.** That is the argument for §4's honesty floor, and it is not an argument I
could have made from prose.

### Finding 4 — the category hid the decision

Nine ~28-line pages sit in `ai-mechanics/`, filed by topic. Eight are explainers. **This one carries
an architectural ratification** that changed the Stylomantic decoder. Filed by topic they are
indistinguishable; every downstream instrument — exposure ranking, the priority queue, the sampling
frame — inherited that indistinguishability and ranked the decision page at 8.1.

This produced the one genuinely new rule in the growth-intent draft (§2.2): **the first axis a
category declares should not be topic, it should be whether the page carries a decision.**
Decision-bearing pages and explainers have different lifetimes, different citation needs, and
different readers.

### What the growth intent said to do here — and what it said not to

The immaterial half is where a standard earns or loses its credibility, so the disposition is stated
explicitly:

| Do | Don't |
|---|---|
| Add `source_kind`, `audit_state: unaudited`, `retrieval_key`, `aliases`, `raw_sha256`, `raw_length`, `## Uncaptured Content` — **~2 minutes, mechanical, owed by every page** | Re-derive all four anchors against `turn_index.py` as a routine matter |
| Fix the **false** D6 claim — not proportional, mandatory | Expand the BPE/EOS explainer claims |
| Cite Jon's T9 and T11 words — R4 has no exposure discount | Promote a concept page, hunt inbound links, or synthesize |

**Total honest cost for this page: about four minutes** — two mechanical, two for the three R4/false-claim
fixes. The expensive work (full anchor re-derivation, expansion, synthesis) is correctly skipped. That
proportion — cheap floor, skipped ceiling, no discount on honesty — is R6.

---

## §3 — The null result

**`wiki/sources/consciousness/consciousness-free-2026-04-21-da7a06.md`** — exposure 2.8, zero inbound
links, 25 lines, two Key Claims.

**The growth intent changed nothing.** Both claims were checked against the raw (2 verified turns)
and both are correctly anchored to T1. Neither is decision-bearing. There are no Jon words on the
page — it is a test-condition record. Nothing is false. The only work owed is the §4 mechanical
honesty floor: declare `source_kind`, declare `audit_state`, add fixity and findability fields. About
two minutes, and no judgment involved.

**One gap was found, and it belongs to v4.0, not to the growth intent** — which is why it is worth
reporting separately. Both Key Claims describe the *prompt* (T1); the page records nothing of the
*result* (T2), where the model produced the substantive finding — that treating consciousness as a
profile of properties rather than a binary predicate "would not have appeared in a single-pass
answer." That is a `## Uncaptured Content` omission, caught by the standard's own E4 check. The
growth intent adds nothing to it. **Being able to say which document caught which defect is the point
of running a null.**

This is reported rather than suppressed because **a judgment document that cannot produce a null
result is not a judgment document, it is a justification.** One page in three producing no change is
roughly what should be expected; if the proportion were much lower, the document would be
over-fitting to the pages it was written against.

*(A fourth page was worked and dropped: `triage-master-open-items-2026-04-28-090a56`, the corpus's
top-exposure page at 514.8. Its v4.0 calibration remediation had already caught the defect class the
growth intent flags — including CLAUDE.md bleed-through mistakenly attributed to Jon, which is a
correctly-handled R4 case. Same finding as example C, ten times the reading cost.)*

---

## §4 — What the examples changed in the draft

Draft-1 of `wiki-growth-intent.md` had never touched a page. Four changes, all marked in the document:

1. **[NEW] Exposure ranks where you work; it never sets the bar.** Now rule **R3**. Produced entirely
   by example B — a bottom-decile page holding a ratification and a falsehood. Draft-1 graded citation
   need by claim class but said nothing about page exposure, which would have left the obvious
   shortcut open. This is the most useful sentence in the document and it did not exist before.
2. **[NEW] The decision-bearing axis** (§2.2). A category's first split axis should be *does this page
   carry a decision*, not *what is it about*. From example B's finding 4.
3. **[NEW] R4 has three distinguishable cases** — Jon originates / Jon ratifies / Jon is argued
   against — with a different failure mode each. Draft-1 quoted Jon's floor and left it abstract.
   Example B supplied the first two, example A the third.
4. **[REVISED] R5 needed a bound.** "Raw preserved + clarified" is unbounded as written — example A's
   PM Map exhibits alone are 93 raw lines. Now: preservation attaches to **the words** (verbatim
   block), artifacts get **pointer + line range**, and "clarified" means an adjacent gloss that may
   never edit the quote.
5. **[REVISED] "Less needed" was undifferentiated** and therefore indistinguishable from neglect.
   Split into an **honesty floor** every page owes regardless of exposure, and an **expansion
   ceiling** that proportionality genuinely lowers.

---

## §5 — What the draft still cannot decide, named specifically

Two are carried from before; the third is new and is the weakest joint in the whole package.

1. **E2's 95% vs 100% threshold** — recommended direction stated (100%, with explicit
   `unrecoverable`/`inferred` counting as coverage), number reserved to Jon, priced in
   `path-to-complete` §3.
2. **The split axis for `infrastructure/` today** — R2 is the mechanism; applying it to 74 real files
   is wiki-master judgment, and the new decision-bearing axis has been exercised on one category.
3. **[NEW] Who assigns claim class, and what stops it becoming the next escape hatch?** R3 grades
   citation need by class. Nothing stops an agent under time pressure from labelling a
   decision-bearing claim "narrative context" and paying the cheaper bar — which would rebuild the
   `unrecoverable` false-exit problem (measured false-unrecoverable rate this week: **~79%**) in a new
   location. The 1-in-12 random audit named in R3's dial column is a mitigation, not a solution, and
   the rate is currently a guess with nothing measured behind it. **If one thing in this package is
   going to fail, it is this.**

---

## Provenance and method

- **Model:** claude-opus-5, high reasoning effort. **Date:** 2026-07-25.
- **Base:** off-Drive worktree at `origin/main` 5d4eea6. Live wiki pages unmodified.
- **Every turn citation** was resolved by running `scripts/audit/turn_index.py` against the tracked
  raw during this session. Example A raw: 46 verified turns, `b318beee`. Example B raw: 16 verified
  turns.
- **Inbound-link counts** taken by direct `[[slug]]` enumeration across `wiki/`, excluding `log.md`:
  example A = 7, examples B and C = 0.
- **Not done, deliberately:** no live page was edited; no `audit_state: verified` was written; no
  sweep was started; `wiki/log.md`, `wiki/index.md` and `wiki/tracker/*` were not touched (a
  concurrent standard update owns them). `path-to-complete` §11 governs all four.
