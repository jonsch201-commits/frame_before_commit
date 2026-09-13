---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

---

# CFL Adaptation Note — adopted 2026-08-08

**Upstream:** `github.com/mattpocock/skills`, `skills/engineering/domain-modeling/`, commit `84fdeff`,
MIT. Body above is **verbatim**; everything below this line is CFL's.

## Substitutions

| Upstream | CFL |
|---|---|
| `CONTEXT.md` at repo root | **`wiki/references/vocabulary.md`** — the glossary already exists here under a different name. **Do not create a second one.** |
| `docs/adr/` | `wiki/tracker/wayfinder-cfl.md` `Decisions so far` + the `D`-rows. ADR-FORMAT.md is kept for reference; CFL records decisions in the map. |
| "cross-reference with code" | **cross-reference with the RECORD** — the ratified registries, chiefly `wiki/references/registries/trunks.md`. |

## ⛔ Why this was adopted, stated as the failure it is meant to prevent

**2026-08-08.** Four coordinators argued for hours about whether "Herald" named a trunk, a coordinator
or a project. **A ratified registry defining the term had existed since 2026-07-28 and none of them
opened it.** Four letters used "Herald trunk"; the registry says *"Herald of Home and Life"* is a
**PROJECT branch under Personal**. **`trunk` and `coordinator` had ZERO entries in the glossary.**

⭐ **And the root cause was where our rule fired, not whether we had one.** `/su-compact` Step 4b says
to add contested terms to the glossary **at close**. Upstream's own docs name this exactly:

> *"It writes a resolved term into `CONTEXT.md` at the moment it is resolved, in the middle of the
> conversation, rather than producing a tidy glossary at the end — because the batched version is a
> summary of a session, and the inline version is the session's actual output."*

**A glossary written at close is a summary of the session, and this project has a whole gist about
what summaries do to attribution. Capture inline. That is the entire adoption.**

## ⚠️ ITS OWN FAILURE MODES — Jon, 2026-08-08: *"it has its own failure modes too, which should be considered while we set ourselves up for success."*

**He also said: *"It is stylomantic. It is translation. It is a key."*** Stylomantic is CFL's
personalized **decoding layer** — it separates *what to steer toward* from *how to steer*, and its
target is a pluggable parameter. **A glossary is the hand-written, inspectable version of what
Stylomantic tries to learn.** So its documented failure modes translate, and they are listed here
rather than rediscovered:

1. ⛔ **SILENT FAILURE — no correction mechanism.** Stylomantic is *"a single-shot intervention — no
   correction mechanism. Silent failure mode rather than visually detectable failure."* **A glossary
   is single-shot too:** once a term is written, every later use inherits it and nothing re-checks.
   ⭐ **Tonight the registry was RIGHT and still failed. A registry that is WRONG fails invisibly and
   makes everything downstream confidently consistent with it.** *Mitigation:* every entry carries
   its primary; challenging an entry against its source is part of the skill, not a favour to it.

2. ⛔ **THE INVISIBLE TAIL.** Stylomantic sees the top-20 of ~50,000 tokens; the *"other"* bucket is
   **20–40% of probability mass** and is a *"known hard ceiling on what's learnable."* **The glossary
   equivalent: you can only define the terms somebody noticed were ambiguous.** `trunk` and
   `coordinator` were not missing because they were hard — **they were missing because nobody
   experienced them as ambiguous until the argument.** *Mitigation:* the trigger is a term used in a
   **second sense**, not a term that feels unclear.

3. ⛔ **THE REDUNDANT FLAT SCALAR.** Stylomantic enforces a normalization constraint *during
   training* specifically to stop the model learning *"a redundant flat temperature scalar"* — a
   no-op that fits. **The glossary version is an entry that restates the obvious.** A glossary of
   *"wiki = the wiki"* fits perfectly and steers nothing. *Mitigation, already CFL practice and now
   load-bearing:* **every entry carries its NEGATIVE half — the meanings the term must NOT carry.**
   That is what makes an entry non-flat.

4. ⛔ **"A KEY" HAS A SCAR HERE, AND THE TWO KINDS OF KEY MUST NOT MERGE.** A *decoding* key lets a
   reader translate. A *retrieval* key decides what a search returns. **On 2026-08-07 CFL mined
   Jon's utterances into `aliases:` and they became the highest-weighted retrieval keys in the wiki
   — `W=200 EXACT`, above every body match.** *"the difference between"* scored **263.0**;
   *"human review"* returned an **ARCHIVED** page over 616 qualifying ones. The set was revoked and
   76 hand-authored sets restored. ⛔ **The ubiquitous language must never be wired into retrieval
   weighting. Same words, different job, and we have measured what happens.**

5. ⚠️ **UPSTREAM NAMES ITS OWN WEAKEST POINT, AND GIVES US A FREE DETECTOR.** *"automatic invocation
   is the weakest part of the skill… models frequently load `grilling` and skip this one. If a
   grilling session runs and `CONTEXT.md` is untouched at the end, that is what happened."*
   **Detector: a session that resolved terminology and left `vocabulary.md` untouched did not run
   this skill.** Invoke it by name alongside `grill-me`.

6. ⛔ **FOUR COORDINATORS, AND THE GLOSSARY IS THE THING THEY MUST SHARE.** If each trunk keeps its
   own, we get four decoding layers that drift — **which is 2026-08-08 at a larger scale.** But a
   shared glossary still needs **one writer per region** (the record method). *Unresolved:* whether
   the trunk vocabulary lives once, centrally, or is mirrored. **Named here rather than assumed.**

## What this skill still does NOT fix

**It sharpens terms in sessions that run it.** It cannot reach a term that was settled in a venue
nobody reads back — Jon's clarification of **OKF** happened in conversation and had **zero
occurrences on disk** until it was written down by hand. **The skill is a discipline, not a capture
mechanism.**
