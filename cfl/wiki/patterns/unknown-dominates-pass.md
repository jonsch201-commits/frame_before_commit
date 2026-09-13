---
format: cfl-page/v1
kind: pattern
slug: unknown-dominates-pass
title: "Unknown Dominates a Pass"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "unreachable space said out loud never silently skipped SPACE UNREACHABLE UNKNOWN dominates a PASS pre-dispatch gate"
aliases: [unreachable-space-said-out-loud, degrade-to-unknown-not-crash, unswept-space-is-not-a-clean-space]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "the rule is implemented and self-tested in one CFL script (M-14, check_before_dispatch.py); it is stated as a design principle but not confirmed as a linted convention applied to other gates in the bounded read-set."
probe_sealed: "In `scripts/audit/check_before_dispatch.py`, what happens when one of the three UNINDEXED_SPACES (exchange/, the SSP quarantine-mirror, Personal's wiki/tracker) is not reachable from the running trunk — does the gate silently skip it or report something? => It prints 'SPACE UNREACHABLE: <name> [<root>]' followed by '-> UNKNOWN dominates a pass. Sweep this space by hand before dispatch.' and marks that space's result None rather than omitting it. TRUSTED"
---

## Struggle

A gate that sweeps several sources for evidence before allowing a PASS can encounter a source it
cannot reach (a path that does not exist from this trunk, a subprocess that errors) — the failure
mode this pattern names is treating that unreachable source as simply absent from the output
(silently narrowing the denominator) rather than as an explicit UNKNOWN that should prevent the
gate from reading as a clean, exhaustive PASS.

- `scripts/audit/check_before_dispatch.py:16` [verbatim] — docstring rule: "Unreachable space =>
  said out loud, never silently skipped. UNKNOWN dominates a PASS."
- `scripts/audit/check_before_dispatch.py:130-136` [contextual] — implementation:
  `if not os.path.isdir(root): out("SPACE UNREACHABLE: %s  [%s]" % (name, root)); out("  -> UNKNOWN
  dominates a pass. Sweep this space by hand before dispatch."); results[name] = None`.

## Generalization

The rule generalizes past this one script: any multi-source check (a coverage sweep, a
cross-trunk read, a stakeholder checklist) that silently drops a source it could not reach produces
a report whose confident PASS is indistinguishable, to a reader, from a report that genuinely swept
everything. Naming the gap out loud — and returning a distinguishable UNKNOWN rather than a zero or
an omission — is what lets a later reader tell "checked and clean" apart from "never checked." This
is the same shape the LP-1 census's own headline names for cross-trunk claims generally (a read of a
moving or partially-reachable target published as if it were a stable, total one). See also
[[caution-errors-have-no-instrument]] for the inverse failure this discipline does not by itself
catch.

## Counter-evidence

none found, searched: `wiki/intake-triage/DREAM-2026-08-30-three-sweeps-curated-wiki-is-blind-after-0824.md`'s
sweep e (dangling-link + orphan sweep) for a case where an unreachable resource (there,
`orphan_census.py` absent in this trunk) was silently treated as zero orphans rather than reported;
that sweep in fact follows the same discipline — "SKIPPED — orphan_census.py absent in this trunk"
is reported explicitly, not silently absorbed into a clean result — so it is a second confirming
instance, not a counter-example, and is not counted as a second locator here to avoid double-use.

## Motivates

`[SKILL: wiki-query]` — the wiki-query skill's stated honesty layer ("REACHABLE is not RETRIEVED,
confident-absence is a named failure grade") is the closest existing skill-level statement of this
same discipline, though `check_before_dispatch.py` itself is not registered as a skill.

## Probe

Sealed question above. Falsified if a future read of `scripts/audit/check_before_dispatch.py`
shows the unreachable-space branch removed or changed to silently continue without printing the
UNREACHABLE line, or if `results[name]` is found set to an empty list `[]` instead of `None` for an
unreachable space (collapsing "swept, found nothing" and "never swept" back into one state).
