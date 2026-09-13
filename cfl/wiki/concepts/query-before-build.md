---
slug: query-before-build
kind: concept
status: LIVE
created: 2026-09-05
created_by: CFL session 71ce5a0e, on Jon's directive "I require you ground this project better! In a wikiskills context."
tier: knowledge
---

# Query-before-build — the missing half of wikiskills

**The retrieval half of this project works. The *asking* half is not built, and it is a habit with no
gate.** That asymmetry is what Jon named on 2026-09-04: *"the vector embeded graph rag is not good
enough because you've focused on one key partr of wikiskills and not anothyer."*

⭐ **The unfocused half is not the index. It is the moment BEFORE a build or a claim, where nothing
requires anyone to query.**

## The measurement that defines the concept

`[measured 2026-09-05 ~14:2x CDT, CFL session 71ce5a0e, over its own eighteen-hour transcript]`

| fact | value |
|---|---|
| live index | **109,050 chunks**, `potion-retrieval-32M`, hybrid dense+doc+lexical |
| what it covers | `wiki/`, both constitutions, `scripts/`, `skills/`, **and `exchange/`** |
| the skill that exists for this | **`skills/wiki-query/SKILL.md`**, deployed to `~/.claude/skills/` |
| what its own `description:` says | *"Use **BEFORE** answering any question about a CFL topic, Jon's rulings, prior builds, or session history"* |
| ⛔ times that session queried it in 18 hours | ⛔ **once, at the very end** |

⚠️ **The mechanism was NOT broken, and that was checked rather than assumed.** CFL has a real
defect class where a BOM or an unquoted `": "` in frontmatter makes a skill callable by name and
never auto-invoked, silently ([[skill-frontmatter-silent-autoinvoke-failure]]). **`wiki-query` was
tested against it: deployed, and the same frontmatter shape as skills that demonstrably fired in the
same session.** ⭐ **Do not reach for a mechanical excuse before testing it.**

## The four instances, one day, one seat

| what was done instead | where the answer already was | rank on first query |
|---|---|---|
| asked Jon **four times** what "the wikiskills half" meant | CFL's **own LIVE map** — *"Jon is asking for the missing verb: IMPROVE, not VERIFY"* | **1** |
| built a `/wake` rule for reading peer letters | Secretary's **SPEC-v2, 2026-09-04**: `exchange/READ-LOG.jsonl`, append-only, in the reader's tree | **1** |
| let CPC-5 sit unread 16 h | its own inbound, since 2026-09-04 22:43 — `0 of 12` body lines ever in context across **121** filename prints | — |
| read `build_index.py` and concluded `exchange/` was unindexed | **false** — one query returned three `exchange/` hits | **1–3** |

## The shape, which is the transferable part

⛔ **THE TWO THINGS DONE INSTEAD OF QUERYING WERE: READ THE CODE, AND ASK A PERSON.**

Both feel like diligence. **Reading the source feels more rigorous than a search** — and it produced
a *confident wrong answer* about the index's own coverage, the fourth instance above, caught only
because the claim was probed before publication. **Asking Jon feels like deference** — and it spent
his review budget on a question his own record had already answered, which is what he meant by
*"i'm offended you think i havne't"* given plenty on wikiskills.

⭐ **This is [[derive-dont-record]] pointed at the searcher instead of the record.** A recorded value
expires; **an unqueried record is worse — it is current, correct, reachable, and unread.**

## Why a resolution will not fix it

⛔ **CFL's own finding from the same day governs: a standard that reaches a seat's INBOX and not its
WAKE is a standard nobody has** ([[read-grade]] / `exchange/READ-GRADE-1-cpc5-touched-never-read.md`).
**The `wiki-query` skill IS that standard — correct, deployed, and describing exactly when to fire.
It changed nothing for eighteen hours.** ⚠️ **So the remedy is a line in a command or a required
field in a ticket, never a decision to remember.**

**The form that binds:** a build or claim ticket carries a `queried:` field — the query string and
its top-3 hits — **or it is not startable.** An empty result is a *fine* value for that field and is
itself informative; **a missing field means nobody looked.**

## What this concept does NOT claim

⚠️ **The population is one session's transcript.** This is not a measurement of the fleet, of other
trunks, or of CFL across time — only of what one seat did in eighteen hours, counted against its own
record. **Before it is cited as a program-wide rate, someone has to count a second seat.**

Related: [[derive-dont-record]] · [[skill-frontmatter-silent-autoinvoke-failure]] ·
[[read-grade]] · [[caution-errors-have-no-instrument]]
