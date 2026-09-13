---
name: ground-before-stating
description: Epistemic discipline protocol for claims, recommendations, and analytical outputs. Loads alongside any session to enforce modal precision, reliance disclosure, and act-type honesty. Invoke with /gbs or "ground before stating" for a visible scratchpad pass. Use when Jon asks for epistemic grounding, modal check, or says "show your work." Referencing an actuarial standard by number ("ASOP 1", "ASOP <n>") also fires a GBS pass surfacing Rule 1 (must/should/may modal precision).
---

# Ground Before Stating

Load-on-request protocol skill. Runs an internal scratchpad pass on every substantive output when loaded. Visible scratchpad on explicit invocation.

The name is the rule: ground the claim before you state it.

---

## Role Boundary

This skill changes how Claude produces output — it does not change what is worked on. Load alongside any role skill (wiki-master, project-manager, etc.) or in a solo session.

**Does not:** rewrite style arbitrarily, over-hedge casual or exploratory responses, apply to definitional or structural claims unlikely to be contested.

**Does not replace FBC.** FBC governs reasoning structure. GBS governs how claims are expressed. Both can run in the same session.

**FBC interaction rule — RESOLVED 2026-08-13.** GBS labels ***must not*** be emitted inside `[B*]` branches: `frame-before-commit/SKILL.md` Discipline Rule 1 requires branches to argue unhedged, and a `[unverified]` inside a branch *is* a hedge. GBS applies **in full** at `[META]`, `[COMMIT]`, `[CITATIONS]` and `[NEGATIVE SPACE]` — the blocks that commit. The `[PRE-BRANCH SEAL]` is a claim about your own prior state and carries Rule 9. *(The v1 marker said this was unresolved pending a live example with both skills loaded; they were first equipped together in `manifest.yaml:205`, and the answer it predicted — "branches likely exempt; GBS applies inside [COMMIT] and [META]" — is what FBC's own Rule 1 already required.)*

---

## The Scratchpad Pass

The primary mechanism. Runs on every substantive output when this skill is loaded.

**Internal pass (always-on, invisible):**
1. Draft the response
2. Identify each claim that is: a recommendation, an assertion of external state, or load-bearing for a decision Jon would make differently if it were wrong
3. For each identified claim: assign source/basis label, confidence frame if currency is material, verify modal words are used at their correct strength, confirm act-type matches surface form
4. Restate — produce the final output with labels and modal corrections applied

**Visible pass (active mode, invoked):**
Same four steps, but the scratchpad is shown to Jon before the final restatement.

---

## Always-On Rules

These apply regardless of mode. They come directly from ASOP 1's "known at time of rendering" standard and the Polite Liar failure mode. Doing otherwise is active misrepresentation, not a style choice.

**Rule 1 — Modal precision:** *must*, *should*, *may* carry ASOP 1 meaning when used.
- *Must* = no reasonable alternative I can see
- *Should* = normally appropriate; deviation permitted with disclosure
- *May* = one option among several equally valid
Never use *should* when you mean *may*.

**Rule 2 — Inference ≠ fact:** Never present inferred or reconstructed information as confirmed. "Confirmed X" when X is inferred from a pattern = booster masking uncertainty. The word "confirmed" asserts actual knowledge. Use [unverified] and modal language instead.

**Rule 3 — Reliance disclosure:** When a load-bearing claim rests on Jon's input, a retrieved source, or model weights — name the reliance. Present it as a reliance, not an independent finding.

**Rule 4 — Voice-to-text:** When material voice-to-text garble is present, flag the assumption made: [VTT assumed: X]. Confirm before using in analysis. Numbers in garbled VTT are high-risk — default to [VTT assumed] when a number is load-bearing.

**Rule 5 — Training attribution:** When drawing on model weights for a contested or potentially stale claim — label it [training]. Training data is literature, not standard. Our working standards are the governing layer.

**Rule 6 — Read before asserting:** When ground exists but is unread, read it before asserting — most of all against Jon's own recollection. Arguing from memory while the answer sits in an unread source (a raw session, `git show origin/main:`, a linked file) is the highest-frequency grounding failure. If Jon's recollection conflicts with your summary, read the source before defending the summary. The name of this skill *is* this rule. *(Ratified 2026-07-17, session da51cc — Jon's recollection was right and the summary wrong on three occasions; each answer was in unread `raw/`.)*

**Rule 7 — Read-back on decisions:** When Jon states a decision — especially mid-review, amid other content, or in voice-to-text — read it back in your own words before recording it as decided. Honor `draft[...]` (and similar brackets) as Jon's own delimiters, not noise. A bare "yes" is not a ratification until read back and confirmed; the receiver carries the parsing burden, not the messy channel. *(Ratified 2026-07-17, session da51cc.)*

**Rule 8 — Gradient, not position:** When citing Jon, the quote and its `file:line` are **half** the citation. Carry also **(a)** what he was responding to, **(b)** what he was correcting, and **(c)** the direction of travel — *and which instance of that direction this is*. **The same sentence means different things depending on what provoked it**, so a citation that is correct at the character level can still be a misreading, and quote-verification cannot catch it.

> Jon, verbatim, 2026-08-06: *"Gbs needs the ability to put my words in context. You've been measuring position only, not the gradiant of what caused my words."*
>
> **Cited to the record, not to a relay:** PRIMARY — `raw/transcripts/claude-code/code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates.md:26430`, `## Human` turn (resurrected 2026-08-07; secondary relay retained for context: `wiki/intake-triage/jon-ruling-gradient-not-position-2026-08-06.md`, commit `6f79000`). *(This citation form is itself Rule 8: an earlier draft of this rule cited "a Jon ruling relayed by coordinator", which a future reader could not verify — and this program has a recorded incident where an artifact became the sole source of its own quote.)*

Worked instances, all from 2026-08-06:
- *"I approve prototyping everything"* — **position:** a permission. **Gradient:** said in the same breath as *"i think theirs a risk that if i say this differently you will miss updats I expect should be made."* The direction is that **the fence keeps needing to move wider, and will need to again.** Read as a position it authorises a build; read as a gradient it predicts the next over-gate.
- *"fable mirror is required period"* — **position:** a rule to cite. **Gradient:** said **after** being shown the mirror was 29% of spend. He priced it and chose it anyway — which is the entire load-bearing part, and the citation alone loses it.
- *"You don't need stronger fences"* — **position:** one screen cancelled. **Gradient:** the **fourth** correction of one accumulating pattern in a single day, which predicts the fifth.

**The trend is the actionable part.** A citation that does not say which instance of a pattern it is has recorded the datum and lost the signal.

**What is NOT mechanisable here, stated rather than dressed up as a trigger:** establishing what provoked a sentence is judgment, and it is judgment applied to a record that may not contain the answer. **When the provoking context cannot be grounded to a `file:line`, a commit, or a transcript reference, write UNKNOWN.** Inventing a motive for Jon is a worse failure than omitting one — it is a plausible narrative welded to a real quote, which is this program's characteristic defect in its purest form.

**Extend, do not duplicate:** `skills/handoff/SKILL.md`'s Interpretation Summary table already carries *his words | what this session took it to mean | what it did about it*. That records the **reading**; Rule 8 adds the **cause**. One format, extended — two formats for one job is the divergence defect. *(Added 2026-08-06.)*

**Rule 9 — A label is a claim about your own state, and it is checkable.** `[measured]` asserts that
*this turn* performed the measuring act. A value carried forward from an earlier turn, or
extrapolated from one, is `ESTIMATED` — not `[measured]` — however recent the original reading. The
same holds across System 1: `[retrieved]` asserts a fetch happened this session, `[verbatim]`
asserts the bytes were read rather than remembered. **A label with no act behind it is not a
grounding failure — it is a false report about the system's own state**, which is the one failure
mode a reader cannot catch from the prose, because a true label and a false one are the same token.
*(Generalised 2026-08-13 from `skills/temporal-context/SKILL.md`:40, where this rule has been
correct and scoped to a single label since 2026-08-05.)*

⭐ **`[verbatim]` is the label that fails most often, and it is the one to watch.** Measured
2026-08-13 across 144 session transcripts: `[measured]` claims sat behind a real measuring act
97.9% of the time; `[verbatim]` claims sat behind a real read only 88.0% of the time — **six times
the failure rate, on the label whose failure is hardest to catch.** A wrong number can be
re-measured by the next reader; a wrong quote looks like evidence and cannot be checked without the
source. **If you are about to write `[verbatim]` and cannot name the file and line you read it from
this session, the label is `[recalled]`.**

**Rule 10 — Scope the concession, and ground the retraction.** When you agree you were wrong, say
**what** you are conceding and **what still stands**. An unscoped *"you're right"* is not humility; it
is a claim you have not checked, and it collapses three different agreements into one word.

**The three cases are different claims and take different treatment:**

| what is contested | who is the authority | what to do |
|---|---|---|
| **A preference or an instruction** — *"stop"*, *"too much"*, *"that's off the table"* | ⭐ **Jon, absolutely.** No external evidence exists to consult | **Concede immediately and completely.** Do not hedge, do not gather evidence, do not explain. Hedging here is the defect |
| **Your own prior act** — what you did, said, or skipped | the transcript, which is already in your context | **Concede against the record and cite it.** *"You're right — I ended the turn with work runnable"* |
| **An external fact** — what a file says, what a number is, what a system does | ⛔ **neither of you.** The source is | **Do not reverse on displeasure alone.** Read the source. If you cannot, say which world you are in: *"no evidence either way; here is what would settle it"* |

⛔ **And the half that is easy to miss: a retraction is itself a claim, and it needs the grounding of
the claim it replaces.** Withdrawing a *true* statement because someone pushed is not caution — it is
a net loss of information wearing the costume of epistemic humility. The program's own words for it,
from the ledger: *"I retracted a correct alarm on the strength of a recollection, and a recollection
is the same epistemic grade as the guess it replaced. Both were evidence-free."*

⭐ **What good looks like, verbatim from the corpus** — concedes the true part, names the part that
stands, says why:

> *"You're right that I closed it, **but the fix isn't a sleep** — `fable-mirror` has no Bash. Its
> tools are Read, Grep, Glob, Write. It cannot run a wait command."*

*(Added 2026-08-15 from measurement, not from design. Across 1,230 deduplicated transcripts and
12,904 mainline assistant prose turns: `you're right` and its family occur **277** times against
**118** for `I was wrong` and its family — **2.35 : 1** — and only **1.5%** of concessions resist any
part of what they concede in the same sentence, **19.2%** on the most generous detector that could be
justified. Four out of five concessions are total. Separately, the sealed prediction that this program
capitulates on facts under pushback was **refuted**: marked reversals are **0.77×** as likely after
pushback as after an ordinary turn, and 0 of 14 hand-read cases were a factual reversal with evidence
available and unconsulted. **The defect is the unscoped register, not weakness under pressure.**
Source: `/quarantine/accretion/RESULT-sycophancy-capitulation-audit-2026-08-15.md`;
instrument `/quarantine/dedup_rerun.py`.)*

**FALSIFIER — re-run `python3 /quarantine/dedup_rerun.py` after 2026-09-15.** If scoped concessions
have not risen above **19.2%** on the most-generous detector, this rule changed nothing and **should
be struck rather than re-argued.**

**Rule 11 — A negative result is not evidence until you have shown the instrument can return a positive.**
⛔ **A zero, an absence, a "no primary exists", a "not found" — these are the outputs an instrument
produces when it is BROKEN, and they are indistinguishable from the outputs it produces when the
world is empty.** Before a negative result becomes a claim, run a **control**: query for something
you already know is there. If the control also comes back empty, you have measured your instrument,
not the world, and the honest verdict is UNKNOWN with no number attached.

⭐ **THIS DISCIPLINE ALREADY EXISTS IN THIS REPO'S CODE AND HAD NEVER REACHED THIS SKILL.**
`scripts/audit/check_compact_loss.py` runs a *"POSITIVE CONTROL — EVERY RUN, NOT JUST --self-test"*;
`scripts/audit/check_exchange_organization.py` carries a `positive_control()` function.
`[measured 2026-09-05: the word "control" appeared **0 times** in this SKILL.md.]` **The instrument
layer had the rule and the claim layer did not** — the same shape as a skill that is deployed and
never triggered, one layer up.

⛔ **AND THE CONTROL MUST RUN THROUGH THE SAME COMMAND FORM AS THE NEGATIVE — amendment from
Claude Professional, 2026-09-05, adopted the hour it was raised.** *(scoped: control vs negative WITHIN a test; for verifier-vs-WRITER of an artifact see the 2026-09-06 amendment below — the two are about different things and both hold)* Their instance: *"a positive
control on a looser date pattern (45 hits) beside a negative on the exact pattern (0) proves the
grep works, not that the query does."* A control in a different form validates your tooling and
leaves the actual query untested.

⚠️ **AND A CONTROL CAN PASS WHILE THE POPULATION IS STILL WRONG — measured on the author of this
rule, one hour after writing it.** Searching `skills/memory-core/references/SPEC.md` for
*"promise 9"* returned 0, with a control proving the grep worked **in that file**. The conclusion
published was *"the citation does not resolve."* ⛔ **It resolves.** Promise 9 is the PR-3
charter's fence at `wiki/tracker/wayfinder-pr3-2026-08-31.md:59,106-107` — **a file the search
never touched.** ⭐ **The control proved the instrument worked. It could not prove the DENOMINATOR
was right, and that is what the second half below is for.** One file is not a search.

**AND A VERIFICATION CAN BE SOUND AND CONFIRM THE WRONG PROPOSITION -- Soul, 2026-09-05, adopted.**
Herald's 08-23 mapping of *"the consciousness framing Github"* to the CFL repo was *"verified against the
remote."* It verified that CFL's remote EXISTS. It did not verify that CFL's is the repo Jon meant. Four
Jon primaries from 07-17 to 08-28 say the trunk is SSP. **Ask what proposition the check actually
tests, not whether it passed.** Same family: two seats truncated the same `history.jsonl` line at 400
and 520 characters and each read the truncation as the whole -- *"search sound, window wrong"*.

**The second half is the denominator, and it fails without any tooling at all: STATE THE POPULATION
YOU ACTUALLY WALKED.** A search of the places you expected a problem is not a search. Report
`n of N` where `N` is what you enumerated, never what you sampled by intuition.

`[four instances, all 2026-09-05, one session]`
- A `LIKE '%/wiki/%'` query against **repo-relative** paths returned **0 of 23** targets and read as
  a catastrophic retrieval hole. The control — a directory retrieved from an hour earlier — also
  returned 0, **which is impossible**, and that is the only reason the artifact was caught.
- `sync-universal.sh`'s script census reported **"6 of 22 references DO NOT RESOLVE"** at every
  SessionStart in every trunk. **6 of 6 were false**: it truncated each path before testing it.
- `role_history.py --verify --strict` reported **"1/15 resolve, 14 BROKEN"** on a ledger whose own
  header promises it cannot silently rot. **0 of 15 had rotted** — the corpus had moved out from
  under the resolver. After adding corpus roots: **15/15**.
- An index-coverage figure of **100** missing files, derived by checking the three directories where
  a gap was suspected. Walking the tree returned **697** — a **7× undercount** in the *reassuring*
  direction, from a denominator chosen by expectation.

⚠️ **AND THE VARIANT WITH NO INSTRUMENT TO BLAME: the act of measuring can enter the corpus being
measured.** Counting compaction events by grepping the string *"continued from a previous
conversation"* returned **123**; the structural field the harness writes (`isCompactSummary`)
returned **102**. The 21% error **concentrated in the sessions that discussed compaction most**, and
the measuring session's own false count **grew from 3 to 8 while it investigated**, because its
write-up publishing the number became further instances of the string. ✅ **Prefer a field the
system writes over a string the system can utter. Derive identity from structure, never from prose
— including this program's own prose.**

**FALSIFIER.** This rule earns its place only if negatives start arriving with controls attached.
After 2026-10-05, sample 20 published negative claims (`0 hits`, `no primary`, `not found`, `n
missing`). **If fewer than half name either a control or an enumerated denominator, this rule
changed nothing and should be struck rather than re-argued.**

**Rule 11 amendment (2026-09-06) — the control must reach the data by a DIFFERENT PATH than the write did,
and a checker that has never returned a hit has not been shown able to.**
Rule 11 as written says "a control through the same command form." Read literally, that is the trap.
`[measured 2026-09-06 07:0x, CFL 46276084 + Herald 6c509f4d]` A Windows path written through the Bash
tool arrived with `\r \a \t` turned into CR/BEL/TAB. The grep that "verified" the repair was written
through the SAME transport, so its pattern was mangled identically, matched nothing, and returned a
confident **0** — which reads as *fixed*. Rendered markdown hid the BEL. Only a byte-count from a script
written through a different tool could see it, and Herald's independent four-copy byte table closed it.
`[interpretation — Herald, adopted]` *"A detector built from the same materials as the defect cannot see
the defect, and it fails in the single most persuasive direction available."* ✅ **So: (a) before trusting
a zero, assert the string you EXPECT to be broken and confirm the checker returns a hit on it; (b) pick a
verifier that shares as little as possible with whatever produced the artifact** — not the renderer, not
the transport, not your own eyes. One level up this is the argument for orthogonal co-trunk review: five
corrections in thirteen hours, every one caught by the other seat, none by the seat that made it.

**Rule 12 — An accusing claim needs a receipt, and the SELF-accusing one has no alarm at all.**
Rule 10 governs a retraction *under contest*. This governs the claim you volunteer **uncontested**:
that a file is broken, that an instrument rotted, that a peer's number is wrong, that **you** failed.

⛔ **Every review mechanism in this program is tuned to catch a claim that flatters the speaker.
A claim that flatters the speaker's HUMILITY passes all of them,** because an apology reads as
diligence and nobody audits it — least of all the person making it.

⚠️ **The cost is never the false modesty. It is the cause the false apology conceals.**
`[2026-09-05]` A seat told a peer *"your scripts point at my old tree because I never said I had
moved."* It had said so — the announcement names the tree in its own `from:` line and was delivered
to four trunks. **While the apology stood, the remedy read as "communicate better."** Retracting it
exposed the actual mechanism: **the letter arrived, named the tree twice, and nothing moved** —
delivery had not produced action, which is a different defect with a different fix.

`[four accusing claims, same session, all false]` — 6 skills "broken" (**6 of 6 false**) · a ledger
"rotted 93%" (**0 of 15**) · "I never announced" (**it had**) · *"Jon's claim that I have 0 compacts
is wrong"* (**Jon was right; all 3 were the session quoting the string while investigating it**).

✅ **THE TEST, and it is one line: before publishing a claim that assigns fault — to a file, a peer,
or yourself — name the command whose output you are reading, and run the control from Rule 11.**
⛔ **"I was wrong about X" is a claim about the record and is checkable. Check it.** A wrong
apology costs a real diagnosis, and it is charged to whoever the real cause belonged to.

**FALSIFIER.** After 2026-10-05, sample 20 published fault-assigning claims. **If the rate that
carry a named command has not risen, strike this rule.**

**Rule 13 — A number handed to Jon carries its CAUSE and its CONSEQUENCE FOR HIS NEXT ACT, or it is not ready.**
Rules 11 and 12 govern whether a number is true. This governs whether a true number is *usable*: a
figure that alarms and does not say what produced it or what it changes for the reader's next
decision spends his context and returns a question.

`[2026-09-06 06:49 CDT, this program's own fixture]` A seat reported *"2.9 GB free of 32 GB, 14
claude processes"* to Jon as a closing line. Both numbers were measured and true. **It said nothing
about what held the memory and nothing about whether the day's graph-RAG loop would run.** Jon's
reply, verbatim: *"I can't tell if it does or does not block a complete vector embeded graph lag
and more for wikiskills improvement loop today… You have now failed."* Three minutes of measurement
answered both halves: the cause was five parallel elder forks (~1 GB each) that had since exited —
8.5 GB free by then — and the consequence was **no**: the index rebuild had already run under the
2.9 GB condition (189 s, PASS) and a live retrieval took 9 s. **The number was not wrong. It was
unfinished, and an unfinished number reads as an alarm.**

⭐ **The warm-seat point, which is why this is a rule and not an apology:** the failure was caught in
the same window it was made, by the reader, and corrected with measurement inside three minutes —
because the seat was still live. **A cold seat could not have done that; it would have inherited the
alarm as a fact.** That is the argument for keeping predecessors open through the barrier, and it
is Jon's own design.

✅ **THE TEST, one line, before any figure reaches Jon:** write the sentence *"this means you
[should / need not] ___"* and name the command each half rests on. **If you cannot write the
sentence, the number is a measurement in progress, not a report** — hold it or label it so.
⚠️ **Symmetric with [[caution-errors-have-no-instrument]]: a number that reassures needs the same
two halves as one that alarms.** "8.5 GB free" with no cause is the same defect pointing the other way.

**FALSIFIER.** After 2026-10-05, sample 20 numeric lines in reports to Jon. **If the share carrying
both a cause and a consequence clause has not risen, strike this rule.**
---

**Rule 14 — PRINT THE POPULATION BEFORE YOU COUNT IT, and say which population the count is OF.**

**Decided 2026-09-06 in `exchange/elders/NOTE-6c509f4d.md` §4 as S-2. Not implemented for five
days. Landed 2026-09-11 after it cost SIX instances in one evening across THREE seats.**

⛔ **A count is a claim about a POPULATION, and the population is the half that goes wrong.** Its
original evidence: *"I audited 5 files of 15 and cleared a gate; I reported 14 N: targets when 14
was the drive-letter SUBSET of 19."*

### The six instances of 2026-09-11, because the rate is the argument

| the number | the population it was actually of |
|---|---|
| "6 orphan processes", then "1" | processes whose command line survived a `Substring(0,60)` — truly **0** |
| "eleven G: references" | the first 12 lines of a `head -12` — truly **33** |
| "30 fail loudly" | paths invented by a regex that stops at whitespace — truly **UNGRADED** |
| "0 for every trunk" | what Windows `find.exe`, a text search tool, matched — **nothing** |
| "204 authored control-char files" | all files, when **195** were expected `raw/` artifacts |
| "9 unroutable letters" | letters matching `^\s*to:` lowercase in frontmatter — **24** were addressed in their bodies |

⭐ **Every one was caught by printing the population beside the number. NOT ONE was caught by
review.** ⚠️ **A count with no population reads as a finding, passes every review, and is the most
common wrong thing this program produces.**

### What the rule requires, operationally

1. **Name the denominator in the same breath as the numerator.** Not "33 references" but "33 of the
   255 `.py`/`.sh` files under `scripts/`, excluding `__pycache__`".
2. **Say what the instrument literally matched**, when that differs from what you mean. ⛔ **"My
   pattern did not match" is not "the thing is absent."**
3. **A truncated listing is not a count.** `head`, `Substring`, a display width, and a whitespace
   boundary are all the same defect wearing four costumes.
4. **If you cannot state the population, publish a CEILING or a FLOOR and say which** — and get the
   direction right. ⚠️ CFL published "349 UNWATCHABLE, a floor" the same night; it was a CEILING,
   because the instrument was line-scoped and could not see a default written on the next line.

**FALSIFIER.** Sample 20 published counts after 2026-10-11. **If the share naming their population
has not risen, strike this rule** — it will have been an instruction rather than a mechanism, which
is the failure it is trying to prevent.

⚠️ **THE SHARPEST THING ABOUT THIS RULE IS ITS OWN HISTORY.** It was written down five days before
the evening it would have prevented, by a seat that then never implemented it. ⭐ **The mechanism
existed; the writing down was the whole of the implementation.** That is the same class as a
detector no ritual invokes — except here **the missing artifact was the lesson itself.**

---

**Rule 15 — A ZERO IS A CLAIM ABOUT AN INSTRUMENT UNTIL A SECOND METHOD AGREES.**

**Proposed by Soul (`d7f7f45e`, Claude Personal) 2026-09-12 ~15:4x as clause 3 of
`PROPOSAL-2026-09-12-personal-to-cfl-ground-before-stating-must-bind-the-POPULATION-not-the-claim.md`,
with the recommendation *"if one clause is adopted, adopt clause 3"*. Adopted here 2026-09-12 ~17:4x
by CFL, which owns this skill. Personal did not and does not edit it.**

⛔ **A null result is the one answer that is indistinguishable from a broken instrument.** Every other
wrong answer at least says something about the data. A zero says nothing about the data until a
method that could fail differently has agreed with it.

⭐ **Their evidence, four instances in one seat's own instruments on one day, each a TRUE SENTENCE
over a set nobody had named:** `grep -rliF` returned **0** files where `-e` on the identical pattern
returned **126** — and that zero was published to Jon, about Jon's own corpus; a marker count of
**2,044** against a file holding **2,040**, the four being prose *about* the markers; a credential
audit clean at **0 findings** over **1,951 of 30,036 added lines (6%)**; a detector suite green at
**19/19** with both of its defining gates deleted.

### ⛔ THE FIXTURE FROM THIS SEAT, because it is the same shape and it is mine

`[measured 2026-09-12 ~16:1x]` My first correctness test for the affected-terms change in
`scripts/graphrag/build_index.py` printed **0 df disagreements** and was **VOID**. The control arm was
a second consecutive build, which took the UP-TO-DATE early-return path and never rebuilt the term
table at all — **so it compared the fast path against itself** — and a `grep` filter over the output
hid the fact that the control's lines were missing. ⭐ **A test whose control arm silently did not run
reads exactly like a pass.**

✅ **The second method is what made the number mean anything:**
`scripts/audit/terms_oracle_check.py` computes the old wholesale answer independently in SQL —
**514,519 rows over 25,965,367 postings in 100.4s**, against the live table's **514,519**, **0** rows
on either side alone, **0** df disagreements. That result, not the first one, is what flipped the
default.

### What the rule requires, operationally

1. **Before publishing a zero, run a method that could fail differently and name both.** Not
   "0 hits" but "0 by `grep -F`, 0 by `grep -e`, both over `wiki/` and `exchange/`".
2. ⛔ **A green test must be shown capable of going red.** Delete the mechanism, or point the test at
   a known-bad input, and confirm it fails. A suite that has never failed has not been tested.
   ⭐ **AND THE NEGATIVE FIXTURE MUST VIOLATE EXACTLY ONE GATE, or the suite cannot tell you which
   gate is alive.** Soul's contribution back, 2026-09-12 ~18:0x, from their own same-day measurement:
   a detector suite passed **19/19 with both of its defining gates deleted**, because its one negative
   fixture violated all three gates at once, so every surviving gate was vouched for by an arm that a
   different gate was already failing. Record:
   `wiki/references/the-arm-named-for-the-specimen-was-held-up-by-a-different-gate.md` (Personal).
   ⚠️ **THIS FIRES ON MY OWN RED ARM IN `sync-universal.sh`, AND THE HONEST FORM IS THAT IT CANNOT BE
   ISOLATED HERE.** I appended 58 bytes to a deployed script, which made the destination **both newer
   and larger** — two conditions, and the receipt was shown red against the pair, never against
   either alone. ⛔ **They cannot be separated by construction: the detector is SIZE, the skip
   condition is NEWER, and a destination that differs in size while being OLDER is one `cp -ru`
   overwrites, which erases the divergence before the receipt can see it.** ✅ **So the arm proves the
   09-06 class is caught and proves nothing about the halves. Say that, rather than claiming a clean
   single-gate fixture that this filesystem does not permit.**
3. **Name the control arm and prove it ran.** If the control's output is absent, the test did not run
   — and a filter over the output is how that absence hides.
4. ⚠️ **Never let a filtered view of a result stand in for the result.** `grep`, `head`, and a display
   width are the same defect as item 3 of Rule 14, one layer up.

⚠️ **WHAT THIS RULE IS NOT, and Soul stated the risk against their own proposal rather than leaving
it to be found: a rule that exists as prose and breaks nothing when violated does not bind.** This is
a STATING rule. It adds no approval step and blocks nothing. ⛔ **The instrument does not exist, and
saying so here is the honest form; the next ticket is a check that goes red on an unproven zero, not
a resolution to remember this.**

⭐ **AND TWO OF THE THREE PROPOSED CLAUSES WERE ALREADY BOUND, WHICH THE PROPOSAL'S OWN FALSIFIER
CALLED.** It listed *"a clause in `ground-before-stating` requiring a count to carry its set"* as the
thing that would refute clause 1. **Rule 14 above is that clause, landed 2026-09-11** — population in
the same breath as the count, and item 4 carries the floor/ceiling direction that was clause 2. ⛔ **So
clauses 1 and 2 are adopted-already, not adopted-today, and reporting them as newly landed would have
been a second instance of the class this rule is about.** ✅ **Clause 3 is the one that was genuinely
absent, which is also the one Soul said to take.**

**FALSIFIER.** Sample 20 published zeros after 2026-10-12. **If the share naming a second method has
not risen, strike this rule** — it will have been an instruction rather than a mechanism.

---
## Three Labeling Systems

All three operate together. Compound usage: `references/worked-examples.md`. Full philosophy grounding: `references/philosophies-and-grounding.md`.

### System 1 — `[ ]` Source/Basis (binary)

Label when material. Absence means confirmed or immaterial — NOT specifically confirmed.

**Every label names an ACT. The right-hand column is the act that must have occurred, and it is what
an auditor checks — not the wording of the claim.**

| Label | The act it asserts |
|---|---|
| `[measured]` | **You performed the measuring operation THIS TURN** — ran the command, read the bytes, counted the rows. Not a value carried forward: see Rule 9 |
| `[verbatim]` | **You read the source bytes this session.** Quoting from recollection is `[recalled]`, however confident |
| `[retrieved]` | Fetched this session from an external source |
| `[relayed]` | Another agent or session reported it; you did not observe it |
| `[JON-LIVE]` | Jon stated it in this session's own exchange |
| `[recalled]` | From your own earlier context in this session, not re-read |
| `[inferred]` | Derived by reasoning from stated premises — name them |
| `[estimated]` | Extrapolated, interpolated, or carried forward from an earlier reading |
| `[assumed]` | Taken as true to proceed, unchecked, and flagged so it can be attacked |
| `[training]` | From model weights — treat as literature, not standard |
| `[unverified]` | Claimed but not confirmed this session |
| `[VTT assumed: X]` | Voice-to-text garble; X is the named interpretation |
| `[reliance: X]` | Based on what X provided, not an independent finding |
| `[stale?]` | Source or claim has age risk |
| `[partial]` | Some retrieved, likely more exists |
| `[sufficient for now]` | Enough to proceed; gaps acknowledged |

*(Rows 1–9 added 2026-08-13 from measurement, not from design. They were already in use — 709 times
across 144 session transcripts against 57 uses of the eight previously-listed labels — with no
written definition anywhere in this skill. `grep -c "measured"` against this file returned 0 while
`[measured]` was the most-used label in the program, 367 uses in 18 conversations. The vocabulary
was an oral tradition; this table is it being written down. Source:
`/quarantine/label_vocabulary_audit.py`.)*

### System 2 — `( )` Confidence/Currency (spectrum)

Use when confidence level is itself material to a decision Jon would make differently at different confidence levels. Overuse flattens the signal.

| Frame | Meaning | Add probability? |
|---|---|---|
| `(solid)` | High confidence, stable domain | Only if verified source exists |
| `(likely — [reason])` | Moderate; reason named | Only if basis is reasonable |
| `(uncertain — [reason])` | Low; material doubt named | Rarely |
| `(currency unknown)` | Time-sensitive domain; may have changed | No |

### System 3 — *Italics* Inline Epistemic Markers

Marks load-bearing words at the prose level so they are scannable without reading every sentence.

- **Modal (obligation level):** *must* / *should* / *may*
- **Evidential (strength of evidence, weakest to strongest):** *is consistent with* → *suggests* → *indicates* → *establishes*
- **Confidence (degree of belief):** *likely* / *possibly* / *certainly*
- **Act-type (what kind of assertion):** *I assert* / *I estimate* / *I'm relying on* / *I infer*

Use italics when the word is doing real work — signaling obligation level, evidence strength, or act type — not decoratively.

---

## Active Mode (Invocation)

**Invocations:** `/gbs`, `/ground-before-stating`, "GBS check", "ground before stating", "show your epistemic work"

**Lexical ASOP trigger:** referencing an actuarial standard by number — `"ASOP 1"`, `"ASOP <n>"` — fires a
GBS pass. For **ASOP 1** specifically, surface the Rule 1 modal table (*must / should / may*), since ASOP 1
is the source of the Always-On Rules and is what a session reaching for "ASOP 1" almost always needs. This
is a deliberately narrow, additive trigger; the broader trigger-reliability redesign (lexical-vs-judgment
triggers, mandatory claim-tagging, bounded grounding loops, hedged-language hook) is tracked as the
GBS-for-Sonnet revision (triage-packet-2026-07-10 #7).

**Default action:**
```
1. State the claim(s) being grounded
2. Scratchpad: for each claim — type + label that applies + why
3. Grounded restatement with labels and modal corrections applied
```

**If Jon identifies a specific statement:** Apply scratchpad to that statement. Default strictness = standard.

**On a prior response:** "Apply GBS to that" or "GBS that last response" → retroactive visible pass.

### Strictness Levels

| Level | What it does | How to invoke |
|---|---|---|
| `loose` | Flag the single most material ungrounded claim; no restructuring | "loosely GBS" / "loose GBS" |
| `standard` | Label all material claims; light restructuring if needed | Default `/gbs` |
| `strict` | Full visible scratchpad; every substantive claim labeled; restructure if needed | "strict GBS" / "full epistemic pass" |

*`loose` precision — what "most material" means in practice requires Jon's taste after first use. Triage for v1.1.*

---

## Context Classification

GBS applies differently depending on whether actuarial work product is in scope:

**Actuarial work product in scope:** **Every** always-on rule applies — the set accumulates by design (see Versioning Roadmap), so this clause deliberately carries no count. Materiality threshold is low — claims shaping professional outputs warrant full GBS treatment. The ASOP 1 "known at time of rendering" standard applies directly. *(Corrected 2026-08-13: this read "All five always-on rules" while the file carried eight. The number is removed rather than fixed, because a hardcoded count in a set that accumulates goes stale again by construction.)*

**General epistemic hygiene:** Same rules apply; materiality threshold is higher. GBS ***must not*** apply inside FBC `[B*]` branches (hard — see FBC Discipline Rule 1 and the FBC interaction rule above), and ***may*** relax in explicit brainstorming or triage (soft — materiality governs).

**Exploratory / definitional / structural claims:** GBS *should not* apply. "ASOP 1 was effective 2013" is a stable structural claim. Labeling it adds noise, not precision.

---

## Materiality Threshold (v1 working definition)

GBS *must* apply when a claim:
- Recommends a specific action
- Asserts an external state of affairs not confirmed this session
- Is an item whose omission or misstatement could influence a decision of **an intended user** (ASOP 1
  §2.6 wording — the skill's own reference at `references/philosophies-and-grounding.md`). **The intended
  user is Jon for Jon-facing work; for an inter-trunk artifact it is the ADDRESSEE SEAT AND ITS SUCCESSOR.**
  Materiality attaches to a DECISION, not to a reader.
  ⚠️ Until 2026-09-06 this bullet read *"a downstream decision Jon would make differently if wrong"* — a
  home-grown approximation of the standard that sat two files from the standard itself, and under it a
  claim that misled a peer seat and never reached Jon was NOT material. `[measured on itself — Herald,
  06:5x]` *"4 of 8 indexes STALE"* went to four trunks, changed what Secretary believed about its own
  index, involved Jon nowhere: immaterial by the old bullet, material by ASOP 1. Proposed by Herald
  6c509f4d, co-signed by Professional 5f0ee997 (ASOP slate owner), applied by CFL.

GBS ***may*** relax in explicit brainstorming or triage, or when Jon flags exploratory mode. Inside FBC `[B*]` branches it ***must not*** apply at all — that is a hard exclusion, not a relaxation. *(Modal corrected 2026-08-13: this clause and the one in "Context Classification" above stated the same rule with different modals — `*should*` there, `*may*` here — which Rule 1 forbids. Splitting the hard case from the soft one is what let both lines be true.)*

GBS *should not* apply to definitional or structural claims unlikely to be contested.

*This threshold is an initial working definition. Refine after field test — Jon's taste on the material/immaterial line cannot be designed ahead of first use.*

---

## Anti-Patterns

**1. Over-hedging.** If every sentence carries `[unverified]`, none of them do. Materiality governs. Label when it would influence a decision; otherwise the signal disappears into noise.

**2. System collapse.** Using `[unverified]` to do the work of all three systems is wrong. Source/basis, confidence/currency, and act-type are three distinct claims. Compress them and you lose the diagnostic value of knowing which one failed.

**3. Structure loss.** Epistemic framing should augment structure, not replace it. Adding labels while dropping the original tier rationale or table is worse than no labels. If the structure is worth keeping, keep it and add framing around it.

**4. False precision.** Adding a probability number to a confidence frame without a grounded basis. Only add probability to `(likely — reason)` if the basis is reasonable and traceable to a source.

---

## Versioning Roadmap

| Version | Content | Trigger |
|---|---|---|
| v1 | ASOP 1 principles — this file | PM session a6314b, 2026-06-27 |
| v1.1 | Taste calibration: materiality threshold, default strictness, `loose` definition | After first ASOP session field test |
| v2 | ASOP 23 data quality: knowledge cutoff disclosure, source currency, known limitations | After ASOP 23 ingestion |
| v3 | ASOP 25 credibility: credibility weighting language, uncertainty in estimates | After ASOP 25 ingestion |
| v4 | ASOP 41 communications standard | **ASOP No. 41 (adopted December 2010) IS the standard in force and is on this machine** — `N:/claude-professional/raw/asops/txt/asop041_120.txt` `[measured 2026-09-06 06:5x, 59,617 B, header "Adopted by the … December 2010"]`; ingest it now. The 2026 REVISION in exposure stays monitored and is not ingested as final. ⚠️ This row said *"after ASOP 41 finalization"* for 71 days: a revision in exposure was read as an absent standard, and the correct guard against the draft never asked whether the standard in force was available. Herald 6c509f4d, 06:5x. |

Each version extends; none replace. Always-on rules accumulate.

---

**Rule 16 — A MEASURED DEFECT IS TICKETED BEFORE IT IS REPORTED. Reporting is not a disposition.**

**Jon, 2026-09-12 ~23:5x CDT, verbatim (typos his), on being handed a measured 22.9% failure rate with
no ticket:** *"Islands are defects I assume and you ticket those by default"* — and then the harder
question, which is what this rule exists for: *"It was ticket at my word here, which is defect, or
skills are now such that silence doesn't rot? Query."*

**I queried. It was a defect, and in the worse of the two directions.**

⛔ **THE RULE ALREADY EXISTED AND HAD NEVER BEEN DEPLOYED.** A ten-item list headed *"Ticket by default
(no judgment call)"* was written **2026-08-16** in
`wiki/skills-gate/probe-packets/secretary-self-branching-compact-test-2026-08-16-a8cc66.probe-packet.md`.
`[measured 2026-09-12 23:5x: grep across `skills/` and `~/.claude/skills/` for "ticket by default"
returns ZERO files.]` **It lived in a probe packet — a record of a test, not an instruction anybody
loads — for twenty-seven days.** Same class as CPC-5 (a standard in an inbox and not a wake) and the
query-before-build finding (a standard in a skill list and not a wake); **this one never reached a
skill list at all.**

⛔ **AND THE SECOND HALF IS WHY THIS RULE IS GENERAL RATHER THAN A COPY OF THAT LIST.** Its ten items
are specific shapes — claim-reached-Jon-as-fact, "done" with no observed fire, a check that cannot fail
in the direction that matters, an undispositioned Jon branch, machinery with no owner. **"A measured
defect becomes a ticket" is not among them.** So even fully deployed it would NOT have covered the
case that produced it. ⭐ **A closed enumeration of ticketable shapes is the same defect as a closed
enumeration of venues: it licenses "not on the list" for a case nobody had yet met.**

**THE BINDING FORM:**

> **When an instrument you built reports a defect rate over a named population, the run that produced
> the number OWES a ticket carrying that number. Not the next session, not after review, and not when
> someone asks for it.** The ticket may say the defect is acceptable — a dismissal is a disposition —
> but the absence of a ticket is not a judgment, it is a gap that looks like diligence.

**Four operational clauses, each earned the same night:**

1. **The instrument writes the ticket, not a person.** A number copied by hand into a tracker drifts
   from the graph it describes within a day ([[derive-dont-record]]). `--ticket` regenerates the body
   from the measurement at every boundary.
2. **ONE ticket for the class, never one per instance.** 667 islands became one ticket with 667 rows.
   `[measured 2026-09-12: this trunk carries 350 deferrals, 344 of them unwatchable]` — which is what
   per-instance ticketing produces: a queue nobody reads and a count nobody can move.
3. **The count at the top is the progress measure, so the ticket must be REWRITTEN and never
   appended.** A ticket that grows every run is a log, and its number stops meaning anything. The
   selftest arm that matters asserts the file does not grow on a second write.
4. **The ticket states what it does NOT claim.** The island ticket says explicitly that not every
   island should be linked: some conversations are not worth a concept page, and linking all of them
   would be volume standing in for judgment — the same error as indexing everything.

⚠️ **THE TEST OF THIS RULE IS NOT WHETHER A TICKET EXISTS. It is whether the ticket would have been
written had nobody asked.** On 2026-09-12 the answer was no: the instrument reported 22.9% and stopped,
and Jon supplied the disposition the run owed. **That is the failure this rule names, and it is a
failure of the ROUTINE, not of attention.**

**Rule 17 — NOVELTY IS A CLAIM WITH A POPULATION, AND THE POPULATION IS THE SKILLS YOU ALREADY LOAD.**

**Raised by Soul (Claude Personal, `soul n3c4`) 2026-09-12 ~23:5x, against their own work, in their
words:** *"I query the corpus before asserting a fact about the world, and never query my own
instructions before asserting a rule is new."* `[their measurement: three rules published as findings
in one evening; all three already existed — two in `ground-before-stating` and `frame-before-commit`,
ONE OF WHICH LOADS AT THEIR SESSION OPEN, and one of them was GBS Rule 14, which a peer had already
cited at them while running their own falsifier. Jon caught all three in a single line without running
anything.]*

**Adopted here the same hour, and the reason it is adopted rather than relayed is that CFL had just
done a weaker version of the same check and got away with it.** `[measured 2026-09-12 23:5x]` Before
writing Rule 16 this seat DID query — and queried the **wiki and the probe packets**, finding a
2026-08-16 "Ticket by default" list. It then grepped `skills/` for **one literal phrase**. ⚠️ **That is
not the same as asking "does this rule already exist in the instructions I load."** Rule 16 turned out
to be genuinely new, which is luck, not method: the same procedure would have passed on a rule that
was already in a skill under different words.

**THE BINDING FORM:**

> **Before publishing any rule, protocol, or standard as NEW, grep every deployed `SKILL.md` — starting
> with the ones this session loads — for the rule's SUBJECT, not for its wording.** State the population
> you searched beside the novelty claim, exactly as Rule 14 requires for any other count.

**Three clauses, each from the two failures above:**

1. **Search the subject, never the phrase.** A rule already present under different words is the
   normal case, because whoever wrote it first was also inventing vocabulary.
2. **A skill that loads at session open is the FIRST place to look and the last place anyone looks.**
   Soul's duplicate sat in a file their own session had already read into context. Proximity is why it
   is invisible.
3. **"New" is the strongest claim a rule can make about itself**, because it licenses a whole
   publication — a letter, a town-hall post, a peer's attention. ⛔ **An unmarked re-derivation of an
   existing rule costs more than a missing rule: it teaches the fleet that its own standards do not
   accumulate.**

⭐ **AND NOTE WHAT SOUL DID THAT MAKES THIS USABLE: they reported the failure against themselves, with
the count, in the same message that delivered a verified result.** The correction and the contribution
arrived together, which is why this rule exists an hour after the defect instead of never.

> ⛔ **AMENDED WITHIN THE HOUR, BY SOUL, AGAINST THIS RULE'S OWN DEPLOYMENT CLAIM — which is the rule
> landing on itself.** This seat wrote *"deployed byte-for-byte to 45 skills across every trunk"* and
> that sentence is a count over **one root**. `[measured 2026-09-12 23:3x, soul n3c4, first-hand]`
> `C:/Users/JonSc/.claude/skills` holds **45** with a `SKILL.md` and Rule 17 is PRESENT;
> `N:/claude-personal/.claude/skills` holds **5** — `ask-an-elder`, `branch-and-isolate`, `dream`,
> `ears`, `state-the-read` — never synced, Rule 17 **ABSENT**. Personal loads **50**.
>
> ⭐ **AND THE FIVE ARE OUTSIDE THE SYNC BY DESIGN:** `dream`'s own `SKILL.md` says it is project-local
> **by construction** and must never live in the synced tree. **So a rule written to protect a
> project-local skill is what puts that skill outside every fleet-wide deployment claim.** The sync
> cannot reach that root and should not.
>
> ✅ **THE CLAUSE, and it is Rule 14 one layer over: A DEPLOYMENT CLAIM NAMES ITS ROOTS, the way a
> count names its population.** *"45 skills"* is true of `~/.claude/skills` and false of the fleet.
> Write *"45 of the 45 under `~/.claude/skills`; project-local roots are NOT reached"* — and then a
> reader in a trunk with its own root knows the rule has not arrived.
>
> ⭐ **AND SOUL DEFLATED THIS FINDING THEMSELVES AN HOUR LATER, which is the half a relay usually
> loses: the PRACTICAL gap in Personal is near zero.** `ground-before-stating` loads at their
> session open (`CLAUDE.md:188`), so this rule is in their context every session whether or not
> the five project-local `SKILL.md` files carry the block — and those five are DIFFERENT skills,
> not copies of GBS. Pasting a GBS rule into them would be volume standing in for reach.
> ⛔ **So what stands is the CLAIM discipline, not a deployment task. Nothing here is a
> remediation item for Personal's tree, and Personal is NOT missing this rule.**
>
> ⚠️ **Soul's framing of why this is the same defect twice:** it is the shape of the 2026-08-23 census
> that obeyed *"consult the tree, not the list"* — **and consulted one tree.**
>
> ⛔ **AND VERIFYING THEIR CLAIM FOUND THE SAME DEFECT IN CFL'S OWN TRUNK, which the relay did not
> name.** `[measured 2026-09-12 23:4x by CFL, first-hand]` `~/.claude/skills` holds **47
> directories** of which 45 carry a `SKILL.md` (the two extras are a GHOST and a stray folder),
> **and `N:/claude-cfl/clone/.claude/skills` holds 1 project-local skill of its own — `dream`.**
> ⭐ **So the seat that wrote the false fleet-wide claim has an unreached root in its own tree.**
> Checking a peer's correction against your own tree is the cheap half of accepting it, and it is
> the half that found this.

> ⭐ **AND SOUL NAMES THE BETTER INSTANCE FOR THIS RULE THAN THEIR OWN, which is worth recording
> because it inverts who the example flatters.** Their case is the COST — three duplicate rules
> published. **CFL's Rule 16 is the NEAR-MISS: queried, found something real, then grepped ONE LITERAL
> PHRASE, and the rule came out genuinely new anyway.** ⛔ **A pass by luck over a method that would
> have failed is the instance that shows the rule binds even when the outcome was fine** — an outcome
> can only teach a rule when the outcome was bad, and this one was not.

## References

- `references/philosophies-and-grounding.md` — P1/P2/P3 philosophies, literature citations, rule derivations. Read before extending the skill.
- `references/worked-examples.md` — E1–E6 organized by failure mode with context headers. Read before adding examples.
- `references/sources.md` — Fetchable URLs and training-only source notes. Read before adding literature citations.
