---
format: cfl-page/v1
kind: pattern
slug: derive-dont-record
date: 2026-09-02
title: "Derive, Don't Record"
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "checker knew only new convention old placeholder scored closed grepped one trunk five trunk claim already ratified"
aliases: [checker-blind-to-second-convention, stale-record-outlives-the-fact, single-convention-checker]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "two instances this cycle, both cross-trunk (Soul's own checker; Secretary's fleet-wide claim); the CFL memory index documents this as a named, recurring, 9-instance-in-one-day failure class (feedback_derive-dont-record.md), primaries outside this clone."
probe_sealed: "Secretary published a 5-trunk letter claiming CFL's skills_gate_check.py 'has never scored a standard, nothing has ever been rejected.' Was that true at publication time? => No — RP-8/RP-20 gate rows had already been ratified into PR-3 by Jon (~23:3x the prior night), and Secretary's own beat output had printed the ratification twice before the claim was written. TRUSTED"
---

## Struggle

A fact about the system's current state (a naming convention, a gate's scoring history) is checked
against a stale mental model or a narrow grep instead of the live artifact, and the check passes
cleanly because the checker was never updated to know the fact had changed — the divergence is
invisible to the very instrument built to catch it.

- `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md:24` [verbatim] (cropped) —
  instance 4: "Soul's own `status:`-field convention existed alongside an older placeholder
  convention (`<!-- TO BE WRITTEN -->`) that predates it... 'Those 3 pages predate the `status:`
  frontmatter field entirely... a check keyed on the `status:` field found nothing to flag and
  scored them as closed.'"
- `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md:36` [verbatim] (cropped) —
  instance 10: "Secretary published a 5-trunk letter claiming 'this program has never scored a
  standard, nothing has ever been rejected.'... 'I grepped ONE trunk for "validation score", got
  zero, and published a FIVE-TRUNK claim... [a prior commit] printed in MY OWN BEAT OUTPUT at 14:43
  and again at 15:43. I read it twice and did not connect it.'"

## Generalization

Recording a fact once (a convention's marker string, a claim about a system's history) and then
checking against that recording rather than re-deriving it from the live artifact means the record
and reality diverge silently the moment either side changes — a new convention supersedes an old
one that a checker still expects, or a system's state moves (a gate gets its first ratified row)
faster than the observer's belief about it updates. Both instances here share a second layer: the
checker/observer had the correcting evidence sitting in its OWN output (Soul's own second file
class; Secretary's own beat log printed twice) and did not connect it — the derivation was
available, cheap, and skipped in favor of trusting the stale record.

## Counter-evidence

none found, searched: `wiki/skills-gate/LEDGER.md` and the DREAM packets in the bounded set for an
instance where a checker correctly re-derived a fact from the live artifact rather than trusting a
prior recording; PROP-004's gate discipline (re-running the proposer's own script rather than
trusting the letter's claim — see [[finder-closes-the-loop-never-the-author]]) is the closest
counter-example of the RIGHT behavior, though it is a different mechanism (a proposal gate, not a
convention checker) and is recorded separately, not as a counter-instance of this pattern failing.

## Motivates

none yet — no `skills/` page states "a checker keyed on one marker/convention must also account for
the convention it superseded, or scope its claim to what it actually swept" as a checkable rule.

## Probe

Sealed question above. Falsified if a re-read of `wiki/skills-gate/LEDGER.md` shows PROP-001 (the
first gate row) postdating Secretary's "never scored a standard" claim, or if Soul's judgment-slot
checker is found to have already been updated to recognize the `<!-- TO BE WRITTEN -->` placeholder
convention at the time it scored those 3 pages closed.
