---
title: Efficiency Rules — how to spend the scarce things
aliases: [efficiency rules, provisional decision rule, when to decide without Jon, capacity test, spend rules]
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-REF; sub: no sub-branch evidence above the floor (best fleet 1 < 2; a lone corroborating tag does not decide)"
source_kind: analysis
source_file: none
retrieval_key: efficiency-rules
generated_by: claude-opus-5/claude-code
date_created: 2026-07-28
audit_state: unaudited
status: LIVE — Jon approved the page 2026-07-27. Individual rules carry their own provenance below.
scope: >
  Standing behavioral rules about SPENDING — Jon-minutes, coordinator context, agent budget, and
  compute. Not a methodology page and not a checklist: each rule below is here because breaking it
  cost something measurable, and the cost is recorded with it.
---

# Efficiency Rules

**Why this page exists.** An audit on 2026-07-27 compared 75 agent memories against the wiki: only
25 had a page on their subject, and **33 shared one shape — the incident was in the wiki, the rule
was not.** The wiki recorded that a service was swapped without approval; it did not record *don't
do that.* The structural cause was that `concepts/` holds things, `sources/` holds sessions, and
`tracker/` holds states — **nothing held a rule.**

Jon, 2026-07-27: *"I approve a … wiki page for efficiency rules. Not limited to — P(reverse) ×
cost(reversal) < cost(waiting) … but your right, rules like this need good places in the wiki."*

**Provenance discipline for this page.** Each rule states whose it is. Several are mine, derived
under Jon's pressure rather than dictated by him — **he said so himself about the first one**, and
three separate quotes were mis-attributed to him on 2026-07-27 alone. **A rule that shapes behaviour
is worth more when its author is honest than when its author is impressive.**

---

## 1. The provisional-decision rule

> **P(reverse) × cost(reversal) < cost(waiting) → decide now, stamp it provisional.**

**Whose:** mine, derived under Jon's pushing. His words: *"i think you came up with that based on my
pushing anyway."* **Not a Jon quote. Recorded as his approved rule, not his sentence.**

The point is not that decisions are cheap. It is that **waiting is not free**, and its cost is
usually unpriced while the cost of being wrong is vivid. A decision that is cheap to reverse and
expensive to defer should be made and marked, not queued.

**What it requires, or it degrades into just deciding:** the stamp. A provisional decision says so,
names what would reverse it, and stays reversible. An unstamped provisional decision is
indistinguishable from a ratified one three weeks later — which is the failure this program spent a
day retracting.

**Where it does not apply:** anything irreversible or external. Publishing, sending, deleting,
anything touching family or credentials. There `P(reverse)` is not small, it is undefined.

---

## 2. The capacity test — what a coordinator does itself

> **Dispatch what would consume coordinator context. Do what costs more to brief than to do.**

**Whose:** derived 2026-07-27 from Jon's own stated rationale for the coordinator role — *"one
claude session can't manage all the work/subagents… It does not do the work, it manages the meta
work."* `[TRANSCRIPT:2026-07-21, 1ad477]`

**The rationale is capacity, not purity**, and that changes the test. The charter's *"dispatching ≠
executing; delegation is the whole job"* has **no Jon turn behind it** and is stricter than his
reasoning supports. A one-line fix or a worktree cleanup is cheaper to do than to brief. A 600-line
instrument or a page ingest is not.

Jon has also named the override: *"Manual mode kill the worktrees now."* Direct execution is an
invoked exception, not a prohibition.

---

## 3. Land first, perfect second

> **Commit and push something defensible as soon as you have it. Improve it in later commits.**

**Cost that produced it:** on 2026-07-26/27, **four agents exhausted their budget mid-task and landed
nothing** — complete work, uncommitted, recoverable only by hand. The fourth had *"land it early"* as
an explicit instruction and still didn't. **The instruction alone does not work; it has to be a fence
that loads at open.**

**Work that exists only in a context about to disappear is this program's most expensive recurring
loss.**

---

## 4. A gate that can never go green stops being read

> **Block only on what the owner can actually fix. Report everything else.**

**Cost that produced it:** this was violated **three times in two days**, twice by the person who
wrote the rule. `index_counts` blocked on another trunk's judgment; the quote check blocked on pages
CFL may not edit; the digest check fired on the calendar rather than on drift and would have gone red
every single day.

**The fix is two runs, not a looser check** — block on the trunk you own, scan everything.
**Narrowing what blocks must never narrow what is seen.**

See [[repo-hygiene]] for the related publishing gate.

---

## 5. An alarming finding is a hypothesis

> **Check before propagating. It has never cost more than five minutes.**

**Cost that produced it:** of five alarming findings on 2026-07-27, **three were wrong** — a
path-resolution artifact reported as tree divergence, an export-date artifact reported as 90% data
loss, and a field-name mismatch reported as 29 permanently lost sessions. **One would have destroyed
a 597 KB transcript** by "refreshing" it from a 55 KB older export.

Corollary, earned the same day: **a subagent's tally is usually right and its explanation often is
not.** Adopt the count; test the story.

---

## 6. Enumerate before concluding absence

> **List every place it could be, and say which you actually looked in.**

**Cost that produced it:** *"it is not there"* was wrong three times in one session. A file present in
a subdirectory nobody globbed; work sitting in a worktree nobody checked; **and 22 sessions declared
permanently lost that were in a Drive backup this repo's own audit had documented.**

**"Permanent" is a claim about every copy that has ever existed.** Projects dir, corpus, quarantine,
Drive backups, archive scripts, other volumes, and the wiki's own record of prior backups. Name each
one you checked, or do not use the word.

**A wrong tombstone is worse than no record**, because silence invites a look and *"permanently
lost"* tells the next reader not to bother.

---

## 7. Spend Jon-minutes last, and only on forks

> **A finding gets recorded. A fork gets asked. Anything routed up carries a recommendation.**

**Whose:** Jon's, 2026-07-27 — *"I still can't give you material PR review as answering questions
like this is taking up all my review time."*

Before any question reaches him: **dispatch the mirror** (the record often answers it), check whether
he has already answered — **possibly by acting rather than saying** — and count how many times he has
answered it before. One gate call had been put to him **six times.**

And the shape: *an open question with no proposed answer is unfinished staff work, not delegation.*
Grounded in his own reply to a question posed without one: *"I don't know how we should count it"* —
**the correct answer to a question that should never have been asked that way.**

See [[coordinator]] and `wiki/tracker/questions-for-jon.md` for the operative gate.

---

## 8. Do not stop with work available and no question pending

> **A pause is not a status report.**

**Cost that produced it:** on 2026-07-27 this fired at **two independent coordinators in two
projects within hours**, and Jon spent six messages restarting one of them. **A defect that
reproduces across independent instances is not fixed by asking the instance to try harder** — it
belongs in the role definition, loaded at open.

Test before stopping: **did I name a next action and then not do it?** And: enumerate the unblocked
work before concluding there is none. *"Nothing is left"* was wrong every time it was asserted.

---

## Uncaptured Content

`uncaptured_assessed: partial` — this page carries eight rules; the 2026-07-27 memory audit found
roughly **36 `type: feedback` memories**, most of which state a standing rule with no wiki page.
**This page is not that backlog.** It holds rules about *spending*; rules about *method*, *routing*,
and *provenance* are out of scope and still homeless.

**Deliberately not carried:** the full incident narrative behind each rule. Those live in
`exchange/` and `wiki/log.md`; repeating them here would make the page long enough to go unread,
which is the failure mode a rules page most needs to avoid.

**Found while placing this page, and worth more than the placement:** `scripts/audit/lint.py`
grades only pages under `/sources/`. **140 of 362 wiki pages — 39% — are graded by nothing**,
including all 39 concept pages, all 24 references, and every tracker page. So the conformance figure
this program quotes, *"15 of 222,"* is 15 of the *source* pages and silently excludes the rest. **This
page is therefore unchecked by construction**, and so is every rule that follows it here. Recorded,
not fixed: widening the linter reclassifies 140 pages at once and is a daylight decision.

**Open, and Jon's — R8, answered 2026-07-28:** asked this directly, Jon replied, verbatim
(`raw/intake/jon-train-rulings-words-reify-intent-2026-07-28.md`, R8): *"uh, yeah revisit later."*
**Standing rules stay in `wiki/references/` for now; the new-trunk question is deferred until rule
pages accumulate further**, not decided against. This is a HELD ruling, not a closed one — do not
read the "later" as "never," and re-raise it if `references/` grows a second distinct rules cluster
(conduct rules, below, are the leading candidate for triggering that re-raise).

**A second rules cluster is now waiting on this same deferred decision — R10, Jon, 2026-07-28:**
Jon's ruling on apologies as a conduct-rule candidate, verbatim: *"we each give each other reasonable
grace. That is right. I am Midwestern, I apologize. In that, perhaps, I do so more than required. As
do you, perhaps. Apologies are best when they favorably shape future behavior. You should conaider."*
(`conaider` → consider `[sp]`) **This is explicitly out of scope for this page** — it is a
*conduct* rule, not a *spending* rule, and the deposit that carries it says so directly: "goes with
the method/conduct rules still awaiting a wiki home." Recorded here as a pointer, not absorbed as a
rule 9, because absorbing it would blur exactly the spending/conduct boundary this page's own scope
note draws. **The candidate rule, for whichever page eventually holds it:** an apology is judged by
whether it shapes future behavior — does it bind to a changed mechanism (a fence, a script, a rule
that loads at open)? The Herald-exchange apology that shipped `exchange_inbox.py` passes that test;
a confession that ships only affect is noise. Applies symmetrically — Jon named his own Midwestern
over-apology pattern in the same breath as naming the assistant's. Tracked as
`wiki/tracker/open-items.md` (new row, this pass) pending a conduct-rules home.
