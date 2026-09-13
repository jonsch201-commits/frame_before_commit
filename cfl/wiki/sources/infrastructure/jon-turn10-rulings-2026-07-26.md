---
title: "Jon Turn 10 — Four Answers and a Standing Instruction on Pacing (2026-07-26)"
aliases: [done-ratified-2026-07-26, ratchet-goalpost-coverage-2026-07-26, ghost-skill-quarantine-2026-07-26, question-budget-spent-2026-07-26]
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 3 vs fleet 2 on authored labels"
source_kind: session
retrieval_key: jon-turn10-rulings-2026-07-26
generated_by: Jon, direct, Claude Code coordinator session 0fb7ca
origin: wiki/intake-triage/jon-turn10-rulings-2026-07-26.md
audit_state: unaudited
status: ACTIVE — JON-DIRECT, every quoted line is Jon's own typed text in the producing session. Ten days unrouted before this ingest (deposited 2026-07-26, ingested 2026-08-05).
maintained_by: coordinator (deposit); wiki-master ingests
tags: [jon-ruling, done-ratified, ratchet-goalpost, ghost-skill, question-budget, pacing, coordinator-session]
---

# Ingest note (wiki-master, SU-close step 4, 2026-08-05)

Ingested verbatim from `wiki/intake-triage/jon-turn10-rulings-2026-07-26.md`, content unchanged below.
This is the strongest-authority file of the seven-file unrouted batch: its own `provenance_note` states
the producing session (`0fb7ca`) was itself snapshotted into the corpus at
`2026-07-27T13:25:01Z, captured_through_record 4831` — i.e. this file's quotes are independently
checkable against a live-session extraction, not only against this hand-authored capture. That
cross-check was **not** re-run during this ingest pass (would require locating and grepping the
`0fb7ca` extract); flagged as a cheap high-value follow-up, not performed here.

**Quote fidelity — nothing softened, nothing hardened.** All five blockquoted Jon lines (§1 "I approve the
packet," §2 "My 40 mintues only included the one file…," §2 "Did you even read my PR comments? I merged
it.," §3 "That sounds great.," §4 "I don't understand the purpose of the ghost skill…," §5 "Plan to ask me
no more questions for the day.," "Ask fabel mirror good questions.," "When you stop too long, it increases
costs.") are carried exactly as they appear in the source file, typos included (e.g. "mintues," "YOu must
use," "wont'"). No correction was applied inside any quote.

**Cross-link note:** §1 explicitly states the turn-9 §4 ratification-label fork was **"retired, not
answered"** by Jon's plain approval, not resolved by either of the two offered words ("closed" /
"on return"). See [[jon-turn9-growth-intent-commented-fold-and-revise-2026-07-26]] §4, which is left
unedited and cross-linked rather than retroactively marked "closed" or "on return" — neither would be
accurate per this page's own account.

**§3's ratchet number is deliberately NOT written here** — the page itself states "His standing ruling
is *'The number is mine'*" and reports only the axis (coverage-of-conversations) as ratified. The
measurement given (172 of 241, 71%, 42 uncovered) is carried as a point-in-time figure from 2026-07-26,
not updated in this ingest pass — a fresher count may exist as of 2026-08-05 and was not re-run here.

---

# Turn 10 — four answers, and a standing instruction on pacing

## §1 — `done` is RATIFIED

> **"I approve the packet."**

His own adopted condition named this exact event: *"When I approve that package, done becomes
RATIFIED."* **The condition is closed and the record moves from CONDITIONAL to RATIFIED.**

**Turn-9 §4's two-word fork is retired, not answered.** It offered `closed` (at the comment fold) or
`on return` (at his look at the return package). Neither happened. He approved, explicitly, which is
what his condition actually required — and the coordinator's earlier finding that the fork was
malformed is confirmed by the way it resolved.

## §2 — What his forty minutes actually covered

> **"My 40 mintues only included the one file that I massively commented, but everything else
> seemed immaterial to my direct review."**

**Recorded as stated, not tidied.** The three worked examples were present in PR #122 and available
to him; **he did not review them**, judged them immaterial to his direct review, and approved the
package anyway.

This matters because his Q2 condition was *"need examples in front of me… can't be ratified till I
see an example in context."* The examples were in front of him. He decided what counted as
sufficient. **No document may say he reviewed the examples.**

He also said, of the review comments:

> **"Did you even read my PR comments? I merged it."**

Fair. All eleven were read and folded into draft-3 (PR #150), but **the merge of #122 was itself a
signal that went underweighted** while an elaborate apparatus was built around a ratification
question he had substantially already answered.

## §3 — The first ratchet goalpost is set on coverage, not density

Recommended to him: *set the next goalpost on coverage-of-conversations rather than
citation-density, because a missing page costs more than a weakly-anchored one.*

> **"That sounds great."**

**The AXIS is ratified. The NUMBER is not, and must not be written.** His standing ruling is
*"The number is mine"* — the first goalpost's value stays `[JON — first goalpost value]` in
PR #128 until he sets it. Current measurement: 172 of 241 conversations covered (71%), **42
uncovered** with no page and no stub decision.

## §4 — Ghost skill: delegated, and executed

> **"I don't understand the purpose of the ghost skill or how it might relate to echos or how it
> relates to our syncing standards. YOu must use your best judgement here. We can always revert
> decisions if needed if it wont' be disruptive."**

**Executed: `~/.claude/skills/triage-packet/` moved to quarantine**, not deleted — recoverable at
`Temp/claude/skill-ghost-quarantine-2026-07-26/` and independently recoverable from git history at
the rename commit `4c90cad`. Deployed and repo trees now agree at 35 skills each;
`cross-venue-intake` (the rename target) verified intact.

**Reasoning, since he asked what it was:** `triage-packet` was renamed to `cross-venue-intake` in
`4c90cad`. `sync-universal.sh` **copies but never deletes**, so the pre-rename version stayed live
and auto-invokable beside its replacement — two skills with overlapping trigger descriptions, one of
them superseded and carrying pre-Reviewability-Standard content.

**His "echos" instinct is the correct frame and is now the durable fix.** This repo already names
the pattern in the worktree rule — *multi-hit title search = worktree echo* — a stale copy that
answers as though it were live. **A ghost skill is that same failure in the skills layer**, and
**every skill rename or deletion in this repo's history has left one.** Removing this ghost fixes
one instance; `scripts/audit/sync_parity.py` (in flight) makes the class detectable, separating
GHOST (deployed, not in repo) from MISSING and DIVERGED, since those have different causes and
different fixes.

## §5 — Standing instructions

> **"Plan to ask me no more questions for the day."**

Question budget for 2026-07-26 is **spent**. The four-item live queue is closed. Nothing further
reaches him today; findings get recorded, forks get held for the next cycle.

> **"Ask fabel mirror good questions."**

Restated as standing: the mirror is the first resort, not the fallback. **The binding constraint has
never been the data — it is question quality.** G0 in `wiki/tracker/questions-for-jon.md` exists for
this.

> **"When you stop too long, it increases costs."**

**A pacing instruction with a real mechanism behind it.** Long idle gaps between turns lose the
prompt cache and re-pay for context already bought. Operationally: **keep work in flight rather than
pausing to report**, batch reporting to natural completion boundaries, and never stop merely to
confirm something that could be verified instead.

---

**Cross-links:** `exchange/turn9-s4-finding-the-fork-is-malformed-2026-07-26.md` (the fork this turn
retires) · `exchange/mirror-finding-ratify-vs-execute-2026-07-26.md` (the bias this turn's explicit
approval avoids) · `wiki/tracker/questions-for-jon.md` (queue now closed) · PR #150 (draft-3) ·
PR #128 (the ratchet) · [[jon-turn9-growth-intent-commented-fold-and-revise-2026-07-26]]
