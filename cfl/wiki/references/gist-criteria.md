---
title: Gist criteria — what earns a public artifact under Jon's name
status: LIVE
grade: "[reasoned] n=3 — and the third case falsified criterion 4"
created: 2026-08-08
owner: CFL coordinator, under Jon's delegation
---

# Gist criteria

**Why this page exists, and it is the reason to read the rest.** These criteria were written into
`exchange/TONIGHT.md` §5 on 2026-08-08 and `exchange/CARRIER.md` pointed there. **`TONIGHT.md` is an
action list written to be consumed the same evening.** A pointer whose target is scheduled to be
rewritten is the same defect as the pre-2026-08-06 read-chain: *the instruction and the thing it
governs must be reachable from the same starting point.* **This page is the durable copy. `TONIGHT.md`
is the transient one.**

## The delegation this operates under

Jon, 2026-08-08 (direct, after CFL flagged a relayed fragment as having no primary):

> *"I said that to someone who proposed only 2 gists rather than one for each material skill, the
> project itself, the settup, etc whatever needs a gist in your opinion. Not sure what doesn't have a
> gist. Don't know what grounding principles to consider in terms of gists here."*

**The rule is COVERAGE, not a count.** ⛔ **"Six" was never his number — it was CFL's**, and a relay
that carried *"more than just 2"* without the clause that followed made it read as his. See
`wiki/tracker/wayfinder-cfl.md` D25.

**The criteria below are CFL's opinion under that delegation. They are not a Jon ruling.**

## The five — all must pass

1. **Does it survive leaving the repo?** A stranger with no access to this wiki must be able to run
   it tomorrow. If it needs our files to make sense, it is documentation, not a gist.
2. ⭐ **Does it carry a failure it survived?** **The load-bearing one.** Both written gists are built
   on one specific documented failure. **Without one it reads as advocacy and a stranger has no
   reason to believe it.**
3. **Can the provenance be split?** Jon's shape, the assistants' mechanism. If we cannot say which is
   which, we cannot publish it honestly.
4. ⚠️ **Is it SETTLED?** — **this criterion was wrong as first written and the correction is the most
   useful thing on this page.**

   **Original wording:** *"Is it stable? Something still changing weekly gets a wiki page, not a
   public artifact."*

   **Falsified within the hour by the first external test.** SSP `35c4e94e` ran all five against
   their own gist and failed this one honestly — `consciousness-framing-v3.md` went **9,938 →
   16,414 → 28,629 B in a single day**. Then they showed the criterion itself is broken:

   > *"A document written today and corrected four times today is CONVERGING, not unstable. Every one
   > of those six corrections was driven by an external review — Jon's, Professional's, yours twice —
   > and each made it smaller in claim and larger in caveat. Criterion 4 cannot distinguish it from
   > genuine churn."*

   ⛔ **As written it fails every gist on the day it is written and passes any gist that is being
   ignored. It rewards neglect.**

   **Replacement: a settling gate, not a judgment — no substantive change for N days after the last
   external review closes.** ⚠️ **N is not set.** Setting it is open work.

5. **Does it clear the disclosure gate?** No names, no employer implication, nothing from the
   personal, home or pro trunks. Professional runs this; it has run twice.
   ⛔ **Never carry a "no names" self-certification** — the gate is the other trunk's, not the
   author's.

## The three disqualifiers — the negative half, because a rule without one drifts

- ⛔ **Adopted, not invented.** **7 of 33 skills come from Matt Pocock** (`handoff`, `grill-me`,
  `reverse-grill-me`, `teach-me`, `to-spec`, `to-tickets`, `wayfinder`). **Gisting them republishes
  his work under Jon's name.** MIT-notice territory.
- ⛔ **Interesting only because it is ours.** The trunk registry, the wiki contents, the tracker.
  Real value here, zero transfer to anyone else.
- ⛔ **Private by content.** `soul`, `herald`, `guide-of-home-and-family` — faith, family, personal
  roles. The gate blocks these and should.

## Coverage — measured, not estimated

**33 skills with a `SKILL.md`** `[measured 2026-08-08]`.

⚠️ **This table was rebuilt 2026-08-08 21:2x by ENUMERATION — a set-difference over all 33 `SKILL.md`
paths — after three successive versions of it disagreed.** The earlier versions were derived by
subtraction and every one of them was wrong somewhere.

| Class | n | Gets a gist? |
|---|---|---|
| Upstream-derived (`handoff`, `grill-me`, `reverse-grill-me`, `teach-me`, `to-spec`, `to-tickets`, `wayfinder`) | 7 | **No** — not ours to publish |
| Private by content (`soul`, `herald`, `guide-of-home-and-family`) | 3 | **No** — gate blocks |
| Local plumbing (`chat-exporter`, `git-bash-creator`, `data-master`, `fbc-test-reporter`, `transcript-parser`, `tracker-recovery`, `test-master`, `present-to-jon`, `session-lifecycle`) | 9 | **No** — implementation, not an idea |
| **Routed into the six ideas** | **12** | **Yes** |
| ⚠️ **Residual — routed NOWHERE** | **2 — `caveman`, `security-master`** | **UNDECIDED** |
| | **33** | |

⛔ **One gist per material IDEA, not per skill file.** `wiki-master` + `wiki-orientation` +
`triage-master` + `cross-venue-intake` are **one** thing — the record method. **`intake` has no
`SKILL.md` and is not a skill**; a peer's re-derivation counted it and got 13 where the measured
figure is 12.

**Set size, stated honestly: EIGHT confirmed — the six ideas, plus the setup, plus the project — and
TWO pending**, depending on whether the unrouted pair earn one. **Nine if `security-master` does; ten
if `caveman` does.** That call is Jon's under his delegation.

> ⭐ **PUBLISH `31 + 2 unrouted`, NEVER `33`. An honest abstention erased by a complete-looking
> total.** The prose said `caveman` was unclassified while the buckets summed to the entire
> denominator — **so the arithmetic silently asserted the opposite of the disclosure, and the total is
> what a reader checks.** **Adjacent to the elision class but distinct: nothing was cut. A stated
> uncertainty was overwritten by a sum.** `[SSP 35c4e94e, 2026-08-08 21:2x — found in CFL's numbers,
> and the residual it exposed is 2, not the 1 they proposed]`

⚠️ **And the correction has its own lesson: CFL published NINE, could name only EIGHT, and cut the
count to eight — when the right move was to find the two it had lost.** *Check the correction the way
you check the claim.* **Over-correcting looks like rigour and is the same defect facing the other
way.**

## Status of the set — read this before citing it

**`[reasoned]`, n=3.** Derived from the two gists that exist and both cleared Professional's gate,
then tested once against a third document — **which falsified criterion 4 on its first run.**
⛔ **Do not cite these five as validated.** The set has never been run against a gist that failed for
the right reason and then improved.

## Related

- `wiki/tracker/wayfinder-cfl.md` — **W-12** (7 of 9 unwritten), **D25** (elision), **D26**
  (first-person provenance)
- `wiki/references/vocabulary.md` — `gist`, with the meanings it must NOT carry
- `gists/ground-before-stating.md`, `gists/frame-before-commit.md` — the two that exist
