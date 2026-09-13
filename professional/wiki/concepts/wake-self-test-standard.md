---
title: Wake self-test standard — one falsifiable check, printed, every wake
created: 2026-08-08 (overnight session, Jon-directed)
status: ADOPTED here; PROPOSED to CFL, Personal, Herald 2026-08-08
---

# Wake self-test standard

**Jon's directive, 2026-08-08 overnight `[verbatim]`:** *"Wake self-test standard for all four
branches: yours is the model — one falsifiable check, printed, every wake."*

## The standard

Every branch's wake procedure includes **exactly one self-test** with three properties:

1. **Falsifiable.** The check must be capable of failing, and its failure must mean something
   specific. A check that always passes is decoration. The canonical target is the
   **procedure-repo binding**: does this procedure name files this repo actually has, and is the
   session actually in the repo the procedure belongs to?
2. **Printed.** One line, every wake, PASS or FAIL — not silently evaluated. A check whose result
   is not printed cannot be audited afterwards, and its absence from a transcript is
   indistinguishable from its success.
3. **One.** A single check runs every time. A checklist of ten runs until the first time someone is
   in a hurry. (This bounds the *mandatory* test; a branch may run more when it likes.)

## The defect class it detects, and why detection must be inside the procedure

On 2026-08-07 this repo ran Personal's `/wake` and `/su-compact` all day via the
additional-working-directories resolution path. The borrowed procedures named `CARRIER.md`,
`wiki/SCHEMA.md`, `MIRROR-STATE-CURRENT.md` — none present here — and ran a remote comparison
against the one repo where a remote is a standing Jon gate. Nothing crashed. **Absence fails
loudly; silent inheritance runs the wrong project's procedure and reports success.** CFL's audit
generalized it: *measure at the point of execution, not the point of storage* — an inventory of
each repo's files cannot see what a runtime search path actually resolves. Only a check that runs
**inside the procedure, at execution time,** sits at the right point.

The one-line check was named the day the defect was found: *does this procedure name files this
repo actually has?* It was free, and nobody ran it. This standard makes it run by default.

## Professional's implementation (the model)

`.claude/commands/wake.md`, first step: stat the three files the procedure is about to rely on
(`BRIEFING-2026-08-07.md`, `wiki/tracker/tracker.md`, `exchange/inbound/`), confirm
`git rev-parse --show-toplevel` ends in `claude-professional`, print:

```
SELF-TEST: procedure-repo binding — toplevel ends 'claude-professional' + 3 named paths exist → PASS|FAIL
```

## Adoption notes for siblings

- Pick file targets that are **distinctive to your repo** (files a sibling also has cannot
  falsify the binding). CFL: e.g. `exchange/CARRIER.md` + `exchange/WAKE-ACTIONS.md`. Personal:
  e.g. `wiki/SCHEMA.md`. Herald: its own tracker.
- The check belongs **in the wake procedure body**, not in documentation about it — the instruction
  and the thing it governs must be reachable from the same starting point.
- Deliberately not centralized into one shared implementation: uniform procedure would delete the
  detector. Each branch's self-test failing on the others' repos is the property that makes it work
  (see [[ownership-is-not-reachability]]).

Related: [[ownership-is-not-reachability]] · CFL's `CROSS-BRANCH-COMPACT-SU-AUDIT-2026-08-07.md`
(the "measure at the point of execution" generalization).
