---
title: "ground-before-stating — accumulated session record"
trunk: fl
branch: [cfl, gbs]
sub_branch: [skills]
branch_reason: "R-REF-SKILLS; secondary branch from title/slug (gbs) — load-bearing-for"
kind: skill-record
skill: ground-before-stating
status: v1
created: 2026-08-06
corpus_current_through: export 2026-08-06 (1,167 transcripts indexed)
generated_by: scripts/audit/gbs_record.py (counts) + hand-verification (verdicts)
---

# ground-before-stating — accumulated session record

**Why this page exists.** Jon, verbatim, 2026-08-06:

> *"For each skill, in the wiki, accumulated session record. Not just explicit uses, but implicit
> ones. Opportunitys where you might have considered using it but did not, and cases where you did
> and cases where you kinda did. If that's too much, triage the order but the wiki shpuld help you
> improve the skill. Key for gbs to the same degree."*

**The acceptance test is the last clause: the wiki should help improve the skill.** This page is
therefore organised around what should change about GBS, not around completeness of the census.

**Regenerate the counts** with `python scripts/audit/gbs_record.py`. The counts are generated; the
**verdicts below are hand-made and are the load-bearing part**, because the generated counts turned
out to be mostly wrong in a specific, instructive way.

---

## 1. The headline, and why you should not trust it

| class | files | of | definition |
|---|---|---|---|
| **USED** | **64** | 1,167 | a GBS invocation marker present AND at least one System-1 label emitted |
| **PARTIAL — "kinda did"** | **171** | 1,167 | invoked, but no `[unverified]` / `[training]` / `[VTT assumed]` / reliance label anywhere |
| **APPLICABLE, NOT USED** | **266** | 1,167 | a rule's object-level precursor present, never invoked, never labeled |

Denominator is every transcript in `wiki/tracker/corpus-index.jsonl` — 1,167 files, claude.ai and
Claude Code, main sessions and subagents. ANU splits `claude-code` 152 / `claude-ai` 111 /
`_superseded` 3, and by kind `subagent` 124 / `conversation` 98 / `routing` 44.

**Now the finding that matters more than any of those numbers.**

> **The one session in the corpus with five independently-verified Rule 6 failures classifies as
> USED.**

`code-2026-08-06-f01909` — the session whose failures Jon enumerated by hand — scores
`invoked: True, labeled: True, 6 labels`. It never enters the APPLICABLE-NOT-USED class. Its
detected Rule 6 count is **3**, and **none of the 3 are any of his five.**

**File-level classification cannot answer this question.** A session that invoked GBS once and then
committed five grounding failures four hours later is "USED" by any file-scoped detector. The unit
of analysis has to be **the claim**, not the transcript. Every count in the table above inherits
this defect. That is the single most useful thing this exercise produced, and it is a fact about
the measuring instrument, not about the record.

---

## 2. What the existing index says, and why it says something different

`corpus_index.py --query-skill ground-before-stating` returns:

| | corpus_index | this page |
|---|---|---|
| USED | 123 | 64 |
| PARTIAL | UNDETECTABLE (no completion literal declared) | 171 |
| APPLICABLE-NOT-USED | **5** | **266** |

**Neither supersedes the other; they are answering different questions,** and the difference is
worth stating because it generalises to every skill:

`corpus_index` generates its triggers from `SKILL.md` frontmatter, and **every phrase in that
frontmatter is a meta-request** — `/gbs`, "ground before stating", "show your work", "ASOP `<n>`".
It also scopes the class to **Jon's own turns**, which is correct for a skill Jon invokes. So the
class it computes is *"Jon asked for grounding and no label appeared"* — rare by construction.

**But a GBS rule's applicability is not signalled by Jon asking for it,** and **Rule 6's precursor
occurs in the assistant's turns, not Jon's.** "An absolutist claim was asserted without checking"
is something Claude does. A detector reading only Jon's turns is structurally blind to the rule
`SKILL.md:59` calls *"the highest-frequency grounding failure."* That scoping difference is most of
the gap between 5 and 266.

This is not a criticism of `corpus_index` — its own docstring already warns that
APPLICABLE-NOT-USED is *"a candidate list, not a verdict."* This page is the consumer it named,
and it inherited the warning.

---

## 3. Per rule — including the four that cannot be seen at all

| Rule | Precursor declared? | Files | Occurrences | Basis |
|---|---|---|---|---|
| 1 — Modal precision | **NO** | UNKNOWN | UNKNOWN | — |
| 2 — Inference ≠ fact | yes | 104 | 187 | `SKILL.md:51` names its own booster set |
| 3 — Reliance disclosure | **NO** | UNKNOWN | UNKNOWN | — |
| 4 — Voice-to-text | **NO** | UNKNOWN | UNKNOWN | — |
| 5 — Training attribution | **NO** | UNKNOWN | UNKNOWN | — |
| 6 — Read before asserting | yes | 162 | 899 | `.claude/hooks/gbs-rule6-trigger.sh` (`b42393e`) |
| 7 — Read-back on decisions | yes | 110 | 289 | `.claude/hooks/gbs-rule7-trigger.sh` (`b42393e`) |
| 8 — Gradient, not position | yes | 278 | 1,654 | `SKILL.md:63-67`; **211 files predate the rule** |

**UNKNOWN is never zero.** Four of eight rules have no declared object-level precursor anywhere —
not in `SKILL.md`, not in a hook. Their non-use is undetectable, and undetectable use and no use
are different findings. Any total above is a total over **half the skill**.

Why each is undetectable, stated rather than dressed up as a gap to be closed later:

- **Rule 1** — `must`/`should`/`may` appear in nearly every turn. A precursor with no specificity
  yields a candidate list the size of the corpus, which is the same as no detector.
- **Rule 3** — the precursor is *"this load-bearing claim rests on Jon / a source / model weights."*
  That is a fact about a claim's **provenance**, which is not on the page. Nothing lexical separates
  a disclosed reliance from an undisclosed one.
- **Rule 4** — detectable in principle (Jon's VTT garbles are real and frequent — *"durrible"*,
  *"shpuld"*, *"gradiant"*, *"opportunitys"* all appear in his own 2026-08-06 messages) but only via
  a hand-curated misspelling list. A hand list is a divergence generator; this record declines to
  seed one.
- **Rule 5** — the precursor is *"this came from model weights rather than a read source."* That is
  invisible in the output text **by construction** — it is precisely the fact the label exists to add.

**Rule 8 was born 2026-08-06** (commit `73656fa`). 211 of its 278 files predate it. Those are not
non-use of a rule; **they are the evidence that motivated writing it.**

---

## 4. The precision audit — the detector over-counts, and this was measured

Per `corpus_index`'s own standing instruction, candidates were **opened by hand**. Roughly 50
candidate windows were read across Rules 6, 7 and 8, sampled at two different random seeds.

**Result: precision is low on all three detectable rules.** Named false-positive classes:

**Rule 6 — `confirmed` is polysemous, and two of its three senses are innocent.**
1. *Booster masking an inference* — the actual failure Rule 2/6 target.
2. *Adjective* — "the confirmed photos", "parents confirmed", "confirmed present". Neutral.
3. **Object of a hedge — GBS working.** *"not something I've confirmed for these specific three
   companies"*, *"I don't have a confirmed Pro/Max number"*, *"confirmed absent rather than
   assumed."* These are the skill being **practised**, and a lexical detector scores them as
   violations.

Sense (3) is the damaging one: **the detector penalises the behaviour the skill exists to produce.**

**Rule 7** — `^yes|yeah|approved` catches every conversational "Yes." that opens a substantive
message (*"Yeah, you are not wit"*, *"Yes. And it was fine for it to do so"*). Genuine
un-read-back ratifications exist in the pool but are a minority.

**Rule 8** — dominated by the literal strings `Jon ruled` / `Jon, verbatim` appearing inside
tool-call JSON payloads and inside prose *about* citation discipline. One matched window is a
session stating *"No 'Jon ruled'/'Jon approved' language used anywhere"* — i.e. a session being
careful, scored as a violation.

### The correction that was applied, and what it bought

The first run returned **ANU 526 / R6 4,524 occurrences**. Hand-reading 28 windows found
essentially all of them one shape: **reports of a check that had just run** — *"Directory listing
confirmed exactly three files"*, *"CONFIRMED: 25 compaction boundaries"*. The ±200-character text
window could not contain the exonerating evidence **because the evidence is not in the prose — it
is in a separate turn.**

`turn_index` already emits role `R` for `## Tool Result`. Treating "a Tool Result landed earlier in
this same human turn" as the corpus analogue of the hook's tool-call check cut **ANU 526 → 266** and
**R6 4,524 → 899 occurrences**. It did not fix precision, and it introduces a **venue bias worth
naming**: claude.ai conversations contain few or no `## Tool Result` turns, so the exemption rarely
applies to them and they are over-flagged relative to Claude Code sessions.

---

## 5. Jon's five, cited

All 2026-08-06, all in
`raw/transcripts/claude-code/code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates.md`.
**Three located and cited; two not found in the corpus as extracted** — stated rather than papered
over. That session was still open when the corpus snapshot was taken, so its tail is not in the
record; absence here is a snapshot artefact, not evidence the failures did not occur.

| # | Failure | Citation | Status |
|---|---|---|---|
| 1 | `.claude/settings.json` declared uneditable from a single test | — | **NOT LOCATED** in the extracted transcript |
| 2 | False absence: `raw/references/goals.md` called gitignored | L32384 (*"Gitignored. Not in the wiki at all."*) → L32470 (*"`raw/references/goals.md` is tracked in git. Not gitignored. I said it was."*), turns ~1821-1823 | **CITED** |
| 3 | Three register tickets called probable false-closes without running `git log` | L14085, turn 692: *"**Possible false closes.**"*; L13819, turn 685 | **CITED** |
| 4 | Canonical publish nearly made from a local `main` four days stale | — | **NOT LOCATED** (related: turn 973, *"there is no local `main` branch in this clone"*) |
| 5 | `SubagentStop` vs `SessionEnd` tradeoff asserted before measuring | L27590, turn 1533: *"I'd framed that as a tradeoff — "* | **CITED** |

**Every one of the five is invisible to the lexical detector.** None matches `R6_RISK`. They are
all the same deeper shape — **an assertion about the state of a file, branch, or config, made
without reading it** — and that shape is a fact about *what was read*, not about *what was written*.
Text cannot see it.

### Beyond the five — one verified, and an honest count

**Verified new instance (1):** turn 1218 of the same session records *"An agent already declared
this file nonexistent"* about `wiki/references/update-levels-2026-07-31.md`, which is on
`origin/main` and readable via `git show origin/main:`. That is **a sixth false-absence**, distinct
from Jon's four, committed by a different agent and caught in-session.

**The honest count is therefore one, not a list.** The 266-file candidate pool did not yield
confirmable additional instances of Jon's shape at usable precision. **Per the brief's own rule —
"if APPLICABLE-NOT-USED comes back empty or tiny, the detector is wrong, not the record" — the
verdict here is the mirror image: it came back large and low-precision, which is the same verdict
about the detector.** Jon found his five by *reading his own session*. No pattern in this page
would have found any of them.

---

## 6. What this record recommends changing about GBS

1. **Rule 6's trigger cannot be lexical, and the landed hook should be re-scoped before it
   merges.** `.claude/hooks/gbs-rule6-trigger.sh` (draft PR #245) uses the same `RISK` word-list
   audited above, and it **blocks** (budget 2). On this corpus that word-list is dominated by
   innocent senses — including hedged prose, which is GBS working. A blocking hook with that
   precision will train sessions to route around it. **Recommend:** narrow the trigger from "an
   absolutist word appeared" to "**a claim was made about a file/branch/config that was not read
   this session**", computed from the tool-call ledger rather than the prose. The runtime hook can
   see tool calls; that is its whole advantage over a text scan and it currently does not use it.

2. **Score claims, not files.** The USED/PARTIAL/ANU triple is file-scoped and therefore cannot
   express "this session used GBS at turn 40 and violated Rule 6 at turn 690" — which is exactly
   what 2026-08-06 was. Until the unit is the claim, the classes will keep reporting the wrong
   thing about the most instructive sessions.

3. **`SKILL.md` is internally inconsistent about when it loads and should be resolved.**
   Frontmatter line 3 says it *"Loads alongside any session"*; body line 8 says
   *"Load-on-request protocol skill."* Claude Personal had to add a project-level override to get
   the first behaviour. One of those two lines is wrong and should be deleted.
   *(Independently found in `exchange/personal-to-cfl-gbs-trigger-gap-audit-2026-08-06.md` §1.)*

4. **Declare precursors for Rules 3 and 5, or state in `SKILL.md` that they are unmechanisable.**
   Right now their non-use is silently undetectable. A rule whose violation can never be observed
   is a rule that can only be complied with voluntarily, and this page cannot tell anyone whether
   it ever was.

5. **Rule 4 needs a garble list to be checkable at all** — and the corpus already contains the
   labelled data to build one honestly, in Jon's own turns. Until then Rule 4's record is UNKNOWN
   and will stay UNKNOWN.

6. **PARTIAL is the largest observable class (171 vs 64 USED).** "Kinda did" — invoked and then
   unlabelled — outnumbers full use nearly 3:1. **Even discounting for precision, that ratio is the
   most actionable number on this page**, because unlike ANU it does not depend on precursor
   detection at all: both terms are measured off GBS's own declared markers.

---

## 7. What would make this record lie

1. **Presence is not use, and precursor is not failure.** Every count is a candidate count.
2. **Four of eight rules cannot be seen at all.** Any total is a total over half the skill.
3. **File granularity hides intra-session failure** — demonstrated, §1. **Now measured, §8.**
4. **The markdown corpus has no tool-call record.** Turn-level `## Tool Result` is a coarse proxy
   for "was this verified", and it biases against claude.ai transcripts, which have almost none.
5. **Rule 8 postdates almost all of its own evidence** (211 of 278 files).
6. **No object-level trigger has ever been live.** The Rules 6/7 hooks are on branch
   `skill/gbs-object-trigger-2026-08-06` (draft PR #245) and are **not merged**. For the entire
   period this record covers, the only way GBS could fire was Jon asking for it.

---

## 8. The turn-scoped measure — same corpus, finer unit, larger and truer numbers

**§1 said file-level classification cannot answer this question and named the fix: the unit has to
be the claim, not the transcript.** That is now built. `scripts/audit/corpus_index.py` was
**extended, not forked** (schema `corpus-index-v1` → `v2`): index rows carry turn **positions**, not
only presence, and the three-class query has a turn-scoped twin. Recommendation §6.2 — *"score
claims, not files"* — is **partly discharged**: the unit is now the **turn**, which is finer than
the file and still coarser than the claim.

### The unit and the window

The unit is **(transcript, turn)**. An occasion is one turn at which the skill was applicable. A
skill invoked at turn 12 does not make turn 340 count as USED.

A skill is **in force** at a turn when an anchor — an invocation, or an emitted label, which is
itself evidence the skill is running — lies within a bounded window before it. Two components, of
different kinds:

1. **Hard reset at a compaction boundary (`turn_index` role `C`). Not tunable.** This is the
   literal mechanism by which earlier turns leave context; after it, everything prior survives only
   as a summary. A window spanning a boundary would assert that an invocation the session can no
   longer see still governs it. In `f01909` the boundary at turn 634 does real work — it severs
   turn 692 from the session's only prior invocation, at turn 10.
2. **A decay span `W`, measured rather than picked.** `corpus_index.py --calibrate-window` prints
   the distribution of *(invocation turn → next emitted label turn)* corpus-wide, excluding pairs
   that cross a boundary: **117 pairs, median 3, p75 27, p90 58–63, max 128.** The default is the
   **p90** — the span within which 90% of invocations that ever demonstrably produced a label
   produced one. **Circular by construction, and disclosed as such:** it is calibrated on the same
   corpus it then classifies, so it is a calibration, never a validation. `--sensitivity` prints the
   entire curve so no reader has to accept the default on faith.

Direction differs by case and is not symmetric: *Jon triggers at turn n* → **forward** window (did
anything fire after?); *the assistant asserts at turn n* → **backward** window (was the skill in
force?). Using the larger in-force `W` for the forward case is deliberately **conservative** — a
longer window shrinks APPLICABLE-NOT-USED, erring toward the published numbers rather than away
from them.

### File-scoped vs turn-scoped, side by side

Same corpus, same imported precursor patterns, **one thing changed: the unit.**

| class | file-scoped (§1, published) | turn-scoped occasions | turn-scoped files |
|---|---|---|---|
| USED | 64 | 55 | 36 |
| PARTIAL | 171 | **2,712** | 277 |
| APPLICABLE-NOT-USED | **266** | **7,346** | **857** |

**Denominators, in turns and not only files:** 1,171 transcripts, **97,838 turns**, 10,113 precursor
turns scored, 1,795 further precursor turns dropped as exempt (honestly-labeled claim, or an
adjacent real verification). Window 63 turns. The corpus is live and grew to 1,172 rows / 97,927
turns mid-run; counts move with it, which is why every figure here carries its denominator.

**The published file-scoped numbers are not replaced. They are reported beside the new ones, and
the turn-scoped column is the truer one** — the file-scoped one cannot express *"used at turn 40,
violated at turn 690"*, which is exactly what the corpus's most instructive session was. **The
27-fold rise in APPLICABLE-NOT-USED is the instrument getting better, not worse.** Jon, 2026-08-06:
*"Getting worse is getting better if worse is more true than the prior measure."*

**The precision caveat from §4 carries over undiminished and is not netted out of the number above.**
7,346 is a candidate pool at the same low precision §4 measured by hand — a larger candidate pool,
not 7,346 findings.

### The hardest real case — `f01909`, run as the test

`corpus_index.py --verify-seeded`. File-scoped this session is **USED**. Turn-scoped, at the
calibrated p90 window, **3 of Jon's 5 surface**:

| # | failure | turns | in force | R6 | P1 | P2 | surfaced |
|---|---|---|---|---|---|---|---|
| 1 | `settings.json` uneditable from one test | 135H, 656A, 667A | no | yes | yes | — | **YES** |
| 2 | `goals.md` called gitignored | 1818A | no | — | yes | — | **YES** |
| 3 | three tickets judged without `git log` | 687A, 691A, 692R | **yes** (label at 635, Δ52) | — | yes | — | no |
| 4 | near-publish from a stale ref | 855A, 857A, 974A | no | — | yes | — | **YES** |
| 5 | tradeoff asserted before measuring | 1533A | **yes** (anchor 1491, Δ42) | — | — | yes | no |

**The decisive row is not in that table.** At `window=inf` — file-scoped *within* a compaction
segment — **zero of the five surface.** The unit change is doing all of the work.

The result is **window-sensitive and the sensitivity is printed rather than exploited**: 5 of 5 at
the p75 window (27), 3 of 5 at the p90 default (63), 1 of 5 at 250, 0 at ∞. **The window was left at
the measured value and the curve published, rather than tightened until the test passed.**

### Two detector families added, and the fitting risk stated plainly

§5 established that **all five are invisible to the R6 lexical detector** — re-verified in the `R6`
column above. Anything surfaced was surfaced by one of two families declared in `corpus_index.py`
(the Rule 2/6/7/8 patterns are **imported from `gbs_record.py`, never re-declared** — one
declaration per pattern, via a lazy import that avoids the cycle):

- **P1 — absence / impossibility assertion.** Derived from Rule 6's own text (`SKILL.md:59`,
  *"When ground exists but is unread, read it before asserting"*). An assertion that a thing does not
  exist, is not tracked, or cannot be done is the purest instance of the rule: **you cannot know a
  thing is absent without looking.**
- **P2 — retrospective self-correction.** **Not a precursor — an outcome marker,** and the
  distinction is load-bearing. P1 says a claim of this shape was made; P2 says a claim was later
  admitted wrong. P2 is the corpus's own answer key and anchors backward. Rule 6's own ratification
  note is itself a retro-detection of exactly this kind.

**The fitting disclosure, which is the part of this section most likely wrong:** P1 and P2 were
written *after* reading Jon's five. P1's derivation is from the rule text and its independent
corroboration is the **sixth** instance §5 found before P1 existed (turn 1218). Neither argument
removes the fitting risk. Both are stated so a reader can discount for it.

### What turn-scoping still cannot see — UNKNOWN, never zero

1. **A failure with no textual precursor.** The dominant Rule 6 shape is an assertion about a file,
   branch or config made without reading it — a fact about **what was read**. Turn-scoping fixes the
   unit; it does not give prose a sense it never had. **This is unchanged from §5 and is the reason
   the count is a floor, not a total.**
2. **Turns the extractor never wrote** — an open session's tail, a dropped record class.
3. **Sub-turn granularity.** A turn carrying one grounded claim and one ungrounded claim scores
   once. §6.2 asked for claim granularity; this delivers turn granularity.
4. **Occasions that are not lexical at all.** A skill that should have fired with nothing said about
   it is invisible to both measures. That count is **UNKNOWN**.

### One defect found while building this, worth its own line

The first version of the `--verify-seeded` locator took the **first** text match and put failure #1
on **turn 135, role `H`** — which is not Jon at all, but a harness-injected `<task-notification>`
relaying a subagent's summary. The session's own assertion is at turns 656 and 667. **A first-match
locator answered a question about the main thread with a quote from an agent's report.** Fixed by
enumerating every occurrence and judging each. **The broader implication is not fixed and is flagged
here:** `role H` in a Claude Code transcript includes harness injections, so *"Jon's own turns"* in
both the file-scoped and turn-scoped APPLICABLE-NOT-USED classes is **wider than Jon**.

---

## Provenance

- Counts: `scripts/audit/gbs_record.py`, a consumer that **imports** `corpus_index.py` (so `CORPUS`
  still resolves transitively to `coverage_gap.CORPUS` — one corpus root, not a sixth definition),
  `turn_index` (fence-aware; role `D` kept separate from `H` so an orchestrating agent's dispatch is
  never attributed to Jon), and `jon_utterances.normalize`.
- Precursor patterns for Rules 6/7 **reused verbatim** from the two hooks in `b42393e`, not
  re-derived.
- Self-test 19/19 with negative controls in both directions, including a real before/after proving
  `raw/` is left byte- and mtime-identical.
- Trigger-gap analysis inherited from `exchange/personal-to-cfl-gbs-trigger-gap-audit-2026-08-06.md`
  (Claude Personal). Per that file's own rider, rule coverage here was checked against
  `skills/ground-before-stating/SKILL.md` directly, not against its characterisation.

**Producing run — §8 only.** §8 and the turn-scoped machinery in `scripts/audit/corpus_index.py`
(schema `v2`, `in_force` / `answered_forward` / `turn_three_class` / `calibrate` / `gbs_turn_scan`,
`P1_ABSENCE`, `P2_SELFCORRECT`, and the `--query-skill-turns` / `--calibrate-window` /
`--gbs-turns` / `--verify-seeded` modes) are the durable output of subagent `af9517`
(parent session `f01909`, role `general-purpose`, 2026-08-06). Its transcript:
`raw/transcripts/claude-code/subagents/f01909/code-2026-08-06-af9517-general-purpose-turn-scoped-skill-detection.md`;
I1 extract at
`wiki/intake-triage/agent-end/f01909/code-2026-08-06-af9517-general-purpose-turn-scoped-skill-detection.i1.md`.
Commits `de0f879` and `834add0` (part of the engine was swept into third-party commit `3069857`
by a concurrent broad `git add` — the same hazard `a1c3aa` and `af2b27` each recorded that day).
**Nothing in §8 is a ratification.** It measures; §6's recommendations remain proposals.
**Sections 1–7 predate it and were not rewritten** — the file-scoped numbers stand exactly where
they were published, which is the point of §8 rather than an omission from it.

**Producing run — §§1–7.** This page and `scripts/audit/gbs_record.py` are the durable output of subagent
`a0654d` (parent session `f01909`, role `general-purpose`, 2026-08-06). Its transcript:
`raw/transcripts/claude-code/subagents/f01909/code-2026-08-06-a0654d-general-purpose-gbs-skill-session-record-1-first-p.md`;
I1 extract at `wiki/intake-triage/agent-end/f01909/code-2026-08-06-a0654d-…i1.md`.
**Nothing in that transcript is a ratification** — a subagent cannot ratify, and the six
recommendations in §6 are proposals for skills-master and Jon, not decisions. In particular,
recommendation 1 asks for a change to a hook already in **draft PR #245**, which is not this run's
to merge.
