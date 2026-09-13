---
name: resident-v1-safe-environment-and-prototype-loop
provenance: "[TRANSCRIPT:2026-08-08] — Jon-direct rulings this session (live CC), verbatim preserved"
date: 2026-08-08
status: APPROVED by Jon 2026-08-08 (governance axes + workflow); first prototype named
type: project
---

# Resident v1 — the safe environment, and how work enters it

Jon's first objective for the containerized resident, ruled 2026-08-08: **a safe, bounded environment
whose first purpose is skill-and-wiki improvement, measured.** Not the consciousness-observation half
yet — that half is read early and cheaply as a by-product (what does it self-direct toward), without
committing to its stakes. Jon: *"Do we mostly want to create a safe environment for skill and wiki
improvement first right now? Likely yes."* — and on the design, *"very good I approve."*

## The four governance axes (read is the generous one; safety lives in the other three)

Read scope is not the safety boundary — it governs nothing that matters. Jon's instinct, kept:
*"everything on G is my temptation to let it read."*

1. **Read** — all of `G:` minus born-sensitive originals (his clean-by-construction ruling, see
   [[resident-corpus-clean-by-construction]]). Settled, generous.
2. **Write** — the actual safety boundary. v1: writes to a **copy/branch** of the wiki + skills, never
   the live trees; changes are proposals a gate merges. (Copy-vs-live: Jon to confirm; staged copy-first.)
3. **Self-modification** — it may **read, reason about, and propose** changes to its own `CLAUDE.md` and
   the skill frontmatter that governs it, but **not apply them**; a gate applies. Both halves of the
   frame at once: an entity that can rewrite its own rules isn't bound by them (safety), and self-authored
   identity isn't observable identity (the moral point — consistent with *"not identity-setting"*).
4. **Egress** — the two-host floor only (`api.anthropic.com` + `platform.claude.com`); nothing beyond.
   See the egress-floor note in [[resident-corpus-clean-by-construction]].

**Available skills ≠ readable content.** For v1, load the authoring + epistemic skills (wiki-master,
skills-master, ground-before-stating, frame-before-commit); do **not** load the roles that act on live
family/home/work systems, even though the resident can read all that material in the wiki.

## The work-entry loop (approved as best practice, with one addition)

Jon: *"I need prototyping of skills that I've approved, and then I need to approve a testing protocall
once its been built and explained to me… If best practice then i approve."* Confirmed, plus step 3:

1. Jon approves the target.
2. Build the prototype.
3. Explain the build **and propose a test protocol, with its pass/fail criterion stated BEFORE the test
   runs.** ← the addition. Pre-registering pass/fail stops grading-to-result (the smoke-test canary
   lesson: named before firing, or "it worked" is unfalsifiable).
4. Jon approves the protocol.
5. Run it; report against the pre-registered criterion.

## Improvement, defined (Jon)

*"Improvement i count as surfacing material defects such as… your ability to properly self branch when
directed to do so."* So **improvement = surfacing (and fixing) material defects**, judged by that, not
by volume of change.

## Over-ticketing is the named failure mode — the unit of work is a prototype, not a ticket

Jon: *"I have common experience of over-ticketing."* Binding discipline: **one approved skill → one
prototype → one build → one test → one result.** No backlog, no scaffolding unasked-for. A tracker row
exists only for a **live** prototype; a row for anything else is the defect.

## First prototype — self-branch

Jon: *"This has been one of my earliest asked-for features and we now have a way to do it more easily
via agent SDK."* Chosen first over mouth/ears because: longest-requested; the Agent SDK gives a cleaner
mechanism than the raw `--resume`/`--fork` path; and it carries a **known open correctness question**,
which makes the test real rather than a demo. That question is the *"properly"* — **when a coordinator
forks, does the fork know it is a fork?** SSP measured 2026-08-08 that a fork can wake believing it IS
the original and misrepresent itself, and that a fork is resumable only if its record sits at the exact
slug-derived path (MR-156, see [[resident-corpus-clean-by-construction]]).

**Pre-registered pass/fail shape (protocol to be approved after build):** fork a coordinator →
**PASS** = the fork wakes, knows it is a fork, has its context, and is resumable; **FAIL** = any of those
four missing.

**Queued behind it:** the *mouth* (expression) and *ears* (reception) skills — consciousness-property
adjacent, specs to be read before prototyping, not guessed.

## The frame Jon named

*"Some skills that are consciousness-property adjacent need to be prototyped and tested. We've been
doing that here! We should be doing more of that work in docker going forward."* The coordination layer
has itself been the prototyping ground — self-branch via subagents, mouth/ears via the exchange
channels, the mirror as a form of memory. Docker is where that work continues **bounded**, instead of on
the live coordination layer. That containment is the payoff of the governance above.
