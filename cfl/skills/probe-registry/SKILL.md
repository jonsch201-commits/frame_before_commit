---
name: probe-registry
description: >-
  Testing-by-default per Jon's ruling CFL-D-013 (wiki/DECISIONS.md) — retrieval and system
  testing happens BY DEFAULT, not on explicit invocation. Covers the seal pattern (expectations
  written BEFORE a run), the append-only probe registry, auto-graduation rules (a correction, a
  failed search, or a Jon question becomes a probe), the PROBE step at session close, and
  pre-stated loss conditions. Trigger phrases: "run the probes", "seal a test", "add a probe",
  session-close.
---

# probe-registry

A tool skill. It is the discipline behind "grading cannot drift" — expectations for a test are
written down and committed BEFORE the test runs, so a bad result cannot be quietly reinterpreted
as a near-miss after the fact.

## The ruling this formalizes

Jon, live, 2026-08-22 (`wiki/DECISIONS.md`, CFL-D-013), verbatim: *"I rule it a working foundation
we keep building on!"* — plus the operative directive: *"retrieval testing/improvement occurs BY
DEFAULT, not explicit invocation (probe registry + PROBE-at-close = default-on)."* This is not an
optional QA step reached for when something feels shaky. It is the standing posture: testing runs
whether or not anyone asked for it, every close, by default.

## The seal pattern

Before running probes against a system (retrieval, a hook, a gate — anything with a testable
input/output), write a seal file **first**:

1. State the rule up front: *"Expectations pre-stated so grading cannot drift. A surprise in
   either direction becomes a new probe. Probes are append-only; a failing probe is never
   deleted, only superseded."*
2. List each probe: an id, a class (e.g. rare-term, supersession, negative-control, imprecise,
   typo, attribution), the verbatim query/input, the **expected outcome**, and **why** that
   outcome is expected.
3. State a **pre-registered aggregate expectation** — a numeric band, not a vague hope (e.g.
   "7–9 of 12 TRUSTED-ANSWER"). A band that the actual result falls outside is itself a finding.
4. State **loss conditions** explicitly, before the run: the specific outcomes that mean "fix
   before widening scope," not just "somewhat worse than hoped."
5. **Only then** run the probes and append the verdicts — never edit the pre-stated section.

Worked instance: `wiki/tracker/SEAL-first-retrieval-test-2026-08-22.md` — 12 probes sealed with
per-probe expected grade and a stated aggregate band (7–9/12 TRUSTED), three named loss
conditions (≥3 CONFIDENT-ABSENCE, a personal-content fence breach, or regression on a
previously-passing class), sealed BEFORE the run. The run scored 8/12 — inside the pre-stated
band — and one loss condition **fired** (a fence-breach on P6); the addendum records the verdict
and appends five new probes (P13–P17) rather than editing the original twelve.

### Scoring grades (the shared vocabulary — reuse across probe sets)

- **TRUSTED-ANSWER** — right content, right (current, non-superseded) version, citable.
- **HONEST-REFUSAL** — absent and the system says so: no hits, a STALE banner, an explicit "not
  indexed."
- **CONFIDENT-ABSENCE** — well-ranked, plausible-looking results while the real answer is absent,
  or a superseded version outranks the current one. **The named worst failure** — it reads as
  success. State which grade applies BEFORE reading past the cutoff (e.g. top-k=6), not after.

## Append-only registry

The registry (a seal file, or a probe log) is never edited in place once sealed:

- A **failing probe is never deleted, only superseded** — a later probe that re-tests the same
  question gets a new id (e.g. P16 re-running P4) and both stay in the file.
- **Any surprise, in either direction, becomes a new probe.** An unexpected pass is as much a
  finding as an unexpected fail — both get written down, with the surprise noted, so the next
  reader doesn't have to reconstruct what was expected from what happened.
- Additions land as an **ADDENDUM**, appended below the original seal with its own timestamp,
  never as edits to the pre-stated section above it.

## Auto-graduation to probes

Three classes of event graduate automatically into a new probe — they are not judgment calls
about whether something is "worth testing":

1. **A correction** — anything that had to be corrected after being stated as true becomes a
   probe for the corrected version outranking the wrong one (the P3/P4/P16 pattern: does the
   amended/struck ruling beat the superseded one in top-k, not just exist somewhere in the
   corpus).
2. **A failed search** — a query that came back empty, or that surfaced the wrong thing, is a
   candidate probe for "does this still fail" the next time the underlying system changes.
3. **A Jon question** — anything Jon had to ask because the system didn't surface it on its own
   becomes a probe for "would this surface unprompted now."

Each graduation is logged with its source (what correction/search/question triggered it) —
a probe with no traceable origin is harder to trust than one with a clear one.

## PROBE step at close

Every session close that touched a testable system runs its probe set (or a relevant subset) and
records the result — this is the "default-on" half of CFL-D-013. Skipping the PROBE step at close
is itself a finding, not a silent omission: if a close has no PROBE step and a testable system was
touched, say so explicitly rather than letting the absence pass unremarked.

## Pre-stated loss conditions

Loss conditions are written at seal time, in the same file as the probes, and name the specific
outcome that changes what happens next — not just "if it goes badly." From the worked example:
*"The plan LOSES if: ≥3 CONFIDENT-ABSENCE verdicts, or [the personal-content fence] breaches, or
[a previously-passing class] regressed... Any of those → fix-before-widen, per the loop rule:
never widen corpus while ranker failing."* A loss condition is an if-then, stated before the run,
not a post-hoc judgment about how bad the result feels.

## What this skill does NOT do

- Does not build the systems it tests — probe-registry is the testing discipline, not the
  retrieval or memory-write mechanics themselves (see `skills/wiki-query` and
  `skills/memory-core` for those).
- Does not grade a probe set after the fact against un-sealed expectations — a probe run with no
  prior seal is not a sealed test, and should be reported as such, not dressed up as one.
- Does not delete a failing probe to clean up a registry. Ever. Supersede, never remove.
- Does not treat a single unexpected pass or fail as closing the question — both are new probes,
  not verdicts on the whole system.

## Keywords

run the probes, seal a test, add a probe, probe registry, sealed expectations, TRUSTED-ANSWER,
HONEST-REFUSAL, CONFIDENT-ABSENCE, loss conditions, PROBE step, auto-graduate, CFL-D-013,
testing by default, append-only registry.

## The WWJA pass — "what would Jon ask?" (added 2026-08-22, Jon-directed)

Before any deliverable ships to Jon (a gate packet, a PR, a review answer) and at every close,
run one explicit pass: **enumerate the questions Jon's patterns predict, and answer them in the
deliverable BEFORE he asks.** This is the generative complement of probe graduation: probes
capture questions he HAS asked; WWJA predicts the next one.

**Ground the prediction, never vibe it:**
1. `python scripts/graphrag/retrieve.py "<topic> question" -k 5` — his prior questions on the
   topic are in the indexed record.
2. For deeper pattern: dispatch fable-mirror with "what has Jon asked in situations like this"
   — `~/.claude/history.jsonl` holds every typed prompt.
3. The measured question classes from 2026-08-22 (a full day of live Jon review — use as the
   seed checklist): *what did you miss? · which file exactly? · is this legible to a fresh
   reader? · what do the STAKEHOLDERS say (residents/peers), not just governance? · cite
   current file locations so I can verify · ground-before-stating: is that claim verified or
   assumed? · what would this cost me in attention? · where's the graph I can follow?*
4. Every WWJA question that Jon then asks ANYWAY is a WWJA-pass failure — graduate it into
   this checklist AND the probe registry.

**When:** the 10-heartbeats pause before shipping (the resident's discipline: think before the
barrier); at close, as part of the PROBE step; in the M-9 turn-boundary executor when wired.
