---
format: cfl-page/v1
kind: pattern
slug: first-run-numbers-are-hypotheses
title: "First-Run Numbers Are Hypotheses"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "first run number unsourced statistic conflicts adopted taxonomy census 148 files subagent only main pipeline stopped"
aliases: [unsourced-figure-in-a-cover-letter, first-count-is-a-guess, denominator-wrong-kind]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "two CFL-clone instances this cycle (an unsourced statistic in a rejected proposal; a coverage census's own denominator later found to mix artifact kinds). A broader recurrence (9+ instances, 2026-07-25/26) is documented in the CFL memory index but those primaries are not resolvable from this clone/N: — see Counter-evidence for the scope limit stated here."
probe_sealed: "PROP-004's cover letter claimed '65.7% degree-zero isolated documents' as its motivation. Was that figure sourced, and did it match the taxonomy CFL had already adopted? => Unsourced, and in direct conflict with RP-4's fifth amendment (isolation is COMPOSITION: window 37.7% vs authored 14.5%, with zero extractor misses found on the actual chased sample). TRUSTED"
---

## Struggle

A count or percentage appears in a proposal, a census, or a coverage report on its first
production, and gets treated as ground truth rather than as a claim to be checked against the
population it was supposed to describe — usually because the denominator silently excludes or
mixes in the wrong kind of item.

- `wiki/skills-gate/LEDGER.md:112-118` [verbatim] (cropped) — PROP-004's motivating record: "the
  proposal claims '65.7% degree-zero isolated documents' -- unsourced, and in conflict with the
  adopted taxonomy (RP-4 fifth amendment: isolation is COMPOSITION -- window 37.7% vs authored
  14.5% -- the letters-class diagnosis chased n=12 to ground and found ZERO extractor misses). The
  REAL documented motivation is available and stronger."
- `wiki/intake-triage/DREAM-2026-08-30-pass-two-ingest-pipeline-stopped-0822-and-the-name-collisions.md:13-16`
  [verbatim] (cropped) — coverage-census denominators stated up front ("148 window transcript files,
  4 main sessions, 158 wiki/sources files"), then corrected in the same block: "0 of 928
  non-subagent claude-code files are dated in the 08-23..30 window (only subagent-dispatch
  transcripts, written by a separate live mechanism, exist: 148 files)" — the 148 the census
  initially counted was the wrong kind of file for the claim being made.

## Generalization

The first time a number is produced — by a proposer motivating a request, or by a census
establishing a baseline — it reflects whatever the measuring code happened to count, which is not
guaranteed to be the population the prose around it describes. Both instances here were caught by
a SECOND measurement against a differently-scoped denominator (RP-4's chased sample; the
non-subagent file filter), never by re-reading the first number more carefully. A number that
motivates a decision (a proposal's rejection, a pipeline-restart priority) should be treated as
provisional until it survives that second, differently-scoped check. Related: [[derive-dont-record]] (the same gap between a recorded figure and the live artifact, one step later).

## Counter-evidence

none found, searched: `wiki/skills-gate/LEDGER.md` PROP-001-PROP-003 for a first-run number used as
motivation that was NOT later re-checked; PROP-001's "12/12 fleet-standard offer letters... zero
receipts" and PROP-003's "18 PAST-DUE / 96 UNCLOCKED / 6 UNPARSEABLE" are both stated as measured
`[measured ...]` at the time of the proposal and both survived into the accepted rows unchallenged
in this bounded set — this is not proof they were correct, only that no correction was found here.
Scope note: the CFL memory index (`feedback_first-run-numbers-are-hypotheses.md`) documents nine
further 2026-07-25/26 instances of this same shape, but that file and its cited JSONL primaries are
outside the clone/N: bounded read-set for this page and are not counted as evidence locators here.

## Motivates

none yet — no `skills/` page states "treat a first-run count as a hypothesis; re-derive it against
a differently-scoped denominator before it motivates a decision" as a checkable step; the pattern
recurred here without a mechanism catching it before publication in either instance.

## Probe

Sealed question above. Falsified if RP-4's fifth amendment figures (37.7%/14.5%) are themselves
found to be superseded by a later, still-adopted measurement that vindicates the original 65.7%
claim, or if the DREAM census's 148-file count is shown to have already excluded subagent
transcripts at the time it was first printed.
