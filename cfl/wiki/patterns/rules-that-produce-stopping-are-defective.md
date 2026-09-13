---
format: cfl-page/v1
kind: pattern
slug: rules-that-produce-stopping-are-defective
title: "Rules That Produce Stopping Are Defective"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "rules in defect with my clear stated intent I cant even read them in 10 seconds standard update completed before they can be run qualified 2026-08-20"
aliases: [jon-2026-08-03-stopping-ruling, questions-are-guidance-not-gaps, wider-fence-than-you-assume]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "Jon's own ruling, later qualified by Jon himself (2026-08-20) — the qualifier narrows the ruling's original context (a specific period when the wiki was in bad shape) without repealing the general instruction; both the original and the qualifier are in the same file."
probe_sealed: "Is the 2026-08-03 'rules that produce stopping are defective' ruling unqualified, or did Jon later add context to it? => Qualified 2026-08-20 (CLAUDE.md/CLAUDE-UNIVERSAL.md, same section): Jon says it was said 'when the wiki was shit and was me complaining about how you wouldn't improve the wiki,' and adds 'their will come a time where you can relax more... Their should always be a balance in all things.' The instruction against defect-rules stands; it was never a blanket ban on all caution. TRUSTED"
---

## Struggle

An operating rule, procedure, or gate is written so that following it exactly requires stopping to
seek clarification or complete a prerequisite before any forward motion is possible — and Jon has
ruled, twice in this project (once as the original statement, once as a later self-qualification),
that a rule shaped that way is itself the defect, not a safety feature.

- `CLAUDE.md:402-408` [verbatim] — "Rules that produce stopping are defective rules." ...
  `~/.claude/projects/.../9e21da9b-…/subagents/agent-ad4f469d3bbc886f3.jsonl:165`, `isMeta: true`,
  2026-08-03T17:58:39.564Z: "Look if your rules are making it think you need to keep stoping those
  are rules in defect with my clear stated intnet. I don't know how to fucking follow your
  instructions in 10 seconds i cna't even read them in 10 seconds and they require a standard
  update be completed before they can be run."
- `CLAUDE.md:411-419` [verbatim] (cropped) — the 2026-08-20 qualifier, `~/.claude/history.jsonl:2611`:
  "'if your rules are making it think you need to keep stoping those are rules in defect with my
  clear stated intnet.' - yes and the stylomantic rephrame - your valid and key too - look **this
  was said when the wiki was shit and was me complaining about how you wouldn't improve the wiki.
  I also was wrong about how to help you, and i just want you to remember - their will come a time
  where you can relax more, as it were. Their should always be a balance in all things.**"

## Generalization

A rule whose ONLY compliant path is "stop and wait for a prerequisite / a ruling / an update" is,
by Jon's standing ruling, functioning against his stated intent — regardless of how well-intentioned
its caution is. This is not an instruction to never pause (the 2026-08-20 qualifier explicitly
preserves room for "a time where you can relax more" and "balance in all things"), but it does mean
a gate, checklist, or process step whose failure mode is universal blocking (rather than degrading
to a flagged UNKNOWN and continuing — see [[unknown-dominates-pass]]) should be treated as a design
defect to fix, not a feature to defend.

## Counter-evidence

none found, searched: `wiki/skills-gate/GATE-SPEC.md` and the LEDGER for a case where a gate's own
design was found to require universal stopping and that design was defended rather than revised;
the pattern's own evidence (`check_before_dispatch.py`'s degrade-to-UNKNOWN-not-crash design,
`[[unknown-dominates-pass]]`) is built explicitly to avoid this failure, consistent with the ruling
rather than contradicting it.

## Motivates

`[SKILL: exchange-letters]` — PROP-002's silence-negation lint is built "refuse-not-warn" but with
stated exemptions rather than a universal block, and PROP-003's on_silence_report.py is explicitly
"report-only" (see [[write-is-not-delivery]]) — both are gate designs that degrade to reporting
rather than halting all downstream work, consistent with this ruling though not citing it directly
in the ledger rows read for this page.

## Probe

Sealed question above. Falsified if a future edit to `CLAUDE.md` or `CLAUDE-UNIVERSAL.md` is found
to have removed the 2026-08-20 qualifier, leaving only the unqualified original — or if a re-read
of `~/.claude/history.jsonl:2611` (outside this bounded clone, checkable only via the constitution's
own transcription) is found to contradict the quoted text.
