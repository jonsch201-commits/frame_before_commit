---
title: Wayfinder — status of the layer above the Coordinator (UNDETERMINED — Jon Gate open)
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (fleet); sub: fleet 3 vs wiki 2 on authored labels"
type: concept
first_seen: jon-wayfinder-vision-2026-08-05-ab3ddc
source_count: 2
last_updated: 2026-08-06
---

## What This Is

**The wayfinder is not defined anywhere in this repo as a session role.** What exists is
`skills/wayfinder/SKILL.md` — an adopted-upstream **skill** (Matt Pocock pack, adopted 2026-07-22,
`skills/wayfinder/SKILL.md:6-11`) that specifies a planning *method*: chart a big, foggy effort as
a **map** (Destination · Notes · Decisions so far · Not yet specified · Out of scope,
`SKILL.md:50-72`) with **decision tickets** typed `research` / `prototype` / `grilling` / `task`
(`SKILL.md:84,96-99`), worked one ticket per session (`SKILL.md:124`), each closed by recording the
answer, closing the ticket, and appending to Decisions so far (`SKILL.md:144`, restated at
`wiki/tracker/wayfinder-cfl.md:143-145`).

**This page's job is to name the gap, not paper over it.** `exchange/coordination-charter-2026-07-21.md`
never once names "wayfinder" (`grep -i wayfinder exchange/coordination-charter-2026-07-21.md` — zero
hits, checked 2026-08-06), and `skills/roles-overview.md` — the ratified 2026-07-22 role hierarchy,
"Net 4→2 standing roles: Coordinator, Project-Manager" (`roles-overview.md:29-30`) — does not list a
wayfinder role either. A skill that produces a governing artifact (the map) exists; a chartered role
that answers for that artifact does not.

## The skill is not the role

Conflating these two is the exact failure this page exists to prevent, so the distinction is stated
plainly:

- **The skill** (`skills/wayfinder/SKILL.md`) is a *procedure* — how to chart a map, how to type a
  ticket, how to close one. It is invoked, not staffed. Any session can load it.
- **A role**, by the pattern this wiki already uses for [[coordinator]], is a *standing charter* —
  who holds it, what it may and may not do, how it hands off. The coordinator has exactly this:
  ratified 2026-07-21, "foreground, interactive, top-tier session that runs nothing itself... it
  coordinates project managers... and always closes a run by coordinating a standard update"
  (`exchange/coordination-charter-2026-07-21.md:12-16`, Jon's own words per the file's
  `consent_note`). **No equivalent sentence exists for wayfinder, anywhere.**

## Candidate distinction, tested against the record — partially holds

The brief that produced this page proposed: *the coordinator answers "who does the next thing," the
wayfinder answers "which thing is next, and where are we going."* Route-setting versus dispatch.
Evidence for and against:

**For.** The skill is explicitly planning, not execution: "Wayfinder is **planning** by default:
each ticket resolves a decision... Plan, don't do" (`SKILL.md:30-32`). That is a route-setting
description, distinct from the coordinator's dispatch verbs ("dispatches, verifies, and closes
loops," charter `:33-34`). The **EM-kill standing invariant** — "A session that plans the portfolio
does not execute work packets in the same context" (charter `:85-90`) — is the same seam: planning
and execution are meant to stay in different contexts, and the map is the planning artifact.

**Against, or at least complicating.** The live map's own frontmatter reads `owner: coordinator
(CFL)` (`wiki/tracker/wayfinder-cfl.md:5`) — as instantiated today, the coordinator *is* the party
holding the map, not a distinct party route-setting for the coordinator to dispatch against. And
ticket resolution is not purely route-setting: a `grilling` ticket is worked live, one question at a
time, inside the resolving session (`SKILL.md:98`), and a `task` ticket "does rather than decides"
(`SKILL.md:99`) — both read as execution happening in the same context that is supposedly only
planning, which is the exact seam the EM-invariant was written to prevent. Whether ticket resolution
is "planning" or "execution" is not resolved by the skill text.

**A third data point, not reconciled with either reading.** `exchange/wayfinder-confidence-gate-2026-07-26.md:44-47`
uses "the wayfinder" as a *party* distinct from the coordinator — "Jon's own turn-8 dispatch was
written by the wayfinder into `wiki/intake-triage/`... the wayfinder could not read back the
dispatch it had just authored" — which describes a claude.ai-side session working through the
Drive connector, writing into fable-mirror's escalation-only path. This predates the live map
(created 2026-08-06) by 11 days and does not match the map-and-tickets mechanism at all. **Two
different things have been called "the wayfinder" in this repo's own record**, and this page cannot
adjudicate between them.

## What is measured, stated separately from what it implies

- `skills/wayfinder/SKILL.md` exists, is adopted, 14,153 B, defines a method. (Measured: file read
  2026-08-06.)
- `exchange/coordination-charter-2026-07-21.md` contains zero occurrences of "wayfinder," case
  insensitive, including its 2026-08-06 amendment A1–A4. (Measured: grep, 2026-08-06.)
- `skills/roles-overview.md`'s ratified role hierarchy lists Coordinator and Project-Manager only;
  no wayfinder row. (Measured: file read 2026-08-06.)
- `wiki/tracker/wayfinder-cfl.md` frontmatter declares `owner: coordinator (CFL)`; its per-ticket
  `Who` column is blank/unclaimed for every open ticket except the one closed ticket, W-1, claimed
  by "executor" (`wayfinder-cfl.md:156-168`). (Measured: file read 2026-08-06.)
- **Interpretation, marked as such:** the ownership line plus the mostly-unclaimed ticket column is
  consistent with a reading where "wayfinder" names *whichever session is presently working the map*
  — coordinator, an executor subagent, or Jon himself on a grilling ticket — rather than a distinct
  standing seat. This is a plausible reading of the evidence above, not a settled one.

## What is open — reserved for W-7b (`grilling`, Jon's)

This page sharpens the question; it does not answer it. `wiki/tracker/wayfinder-cfl.md:166` blocks
W-7b (amend the charter to name this layer) on this page, with the note "The hierarchy is Jon's."
The options, as they read from the record above, each with its consequence:

1. **Wayfinder is a hat the coordinator wears** — no new role, just a mode of the existing
   coordinator session governed by the skill. *Consequence:* no charter amendment needed beyond
   maybe a cross-reference; the EM-invariant tension above (planning vs. execution in one context)
   becomes a coordinator-charter compliance question, not a new-role question.
2. **Wayfinder is a distinct session role**, parallel to project-manager, that holds the map and
   dispatches tickets to executors, while the coordinator dispatches wayfinder itself. *Consequence:*
   a new charter section is needed (who staffs it, hand-off rules, its own stop-ritual) — real
   design work, not a naming fix.
3. **Wayfinder is a layer above the coordinator** — the reading this ticket's brief floated as a
   hypothesis (the coordinator answers "who," wayfinder answers "which/where"). *Consequence:*
   inverts today's `owner: coordinator (CFL)` framing on the live map and would require re-deriving
   who *dispatches the coordinator* — a bigger structural change than options 1 or 2, and the
   weakest-supported of the three against the evidence gathered here (nothing in the charter, the
   role hierarchy, or the map's own frontmatter currently treats the coordinator as subordinate to
   anything but Jon).

The `exchange/wayfinder-confidence-gate-2026-07-26.md` usage (a fourth, connector-side sense of "the
wayfinder") is flagged above but not folded into these three options — it may be an obsolete usage
from before the map existed, or it may indicate the term was already doing work this page hasn't
captured. **UNKNOWN; not investigated further here** — the brief's read budget did not extend to a
full history of every "wayfinder" occurrence in `exchange/`.

## Related

[[coordinator]]
