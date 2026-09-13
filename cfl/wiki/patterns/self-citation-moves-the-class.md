---
format: cfl-page/v1
kind: pattern
slug: self-citation-moves-the-class
title: "Self-Citation Moves The Class"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "census citing the ids it classifies own top-20 table contaminates its own future re-runs Z flipped to C for the identical reason"
aliases: [census-cites-its-own-output, audit-report-poisons-its-own-corpus, coverage-check-reads-its-own-flag-as-coverage]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one fully-worked instance this cycle: 8 sessions flagged Z (uncovered) in the 08-24 packet re-classified as C (cited) by a fixture rebuild, all 8 for the identical reason -- the packet's own Z-list table, sitting in the wiki, was read as coverage evidence by the next run."
probe_sealed: "Do all 8 sessions that flipped from Z (08-24 packet) to C (fixture rebuild) share the same evidence path, or 8 different ones? => The identical one: every flip traces to the 08-24 census document itself (wiki/intake-triage/DREAM-SWEEP-A-F-...md [target not created: literal `...` is a truncation marker in the source text, not a filename component]) quoting each Z-listed session id in its own top-20-largest-ungapped table -- a citation check that treats 'the id appears in the wiki' as coverage evidence cannot distinguish a source page discussing a session from an audit report once flagging it uncovered. TRUSTED"
---

## Struggle

A census or audit instrument writes its own findings (a list of uncovered items, a table of
flagged ids) into the same corpus it measures. On its next run, the instrument's own
citation-based evidence check treats that prior finding's text -- which merely NAMES the item as
a problem -- as if it were coverage evidence FOR that item, silently reclassifying a genuine gap
as closed.

- `wiki/intake-triage/C1-census-2026-09-02.md:87-109` [verbatim] (cropped) -- "Checked all 8
  top-20 Z-listed sessions from the 08-24 packet's own table ... against the fixture run ... All
  8 flip from Z to C for the identical reason: the 08-24 census document itself, sitting in
  `wiki/intake-triage/`, quotes each Z-listed session id in its own top-20-largest-ungapped
  table. A citation check that treats 'the id appears in the wiki' as coverage evidence cannot
  distinguish 'a source page discusses this session' from 'an audit report once flagged this
  session as uncovered' ... any census that publishes a Z-list into the corpus it measures will
  contaminate its own future re-runs."
- `wiki/intake-triage/C1-census-2026-09-02.md:259` [verbatim] (cropped) -- the correction's
  own measurement, run 2 with `--exclude-self-citations`: "5 of 8 flip back to Z with the
  exclusion; 3 remain C for a genuinely different reason: these three are cited in `agent-end/`
  run-record files ... genuinely different from the census self-citation." The Z-tier delta
  improved from -10 to -3 but did not fully close, showing the contamination was real but only a
  partial explanation of the original discrepancy.

## Generalization

Any instrument whose own output (a flagged-items list, an audit table, a coverage report) is
stored in the same location its next run treats as evidence creates a closed loop: publishing the
finding "X is uncovered" makes X's name appear in the wiki, and a naive citation-based coverage
check reads that appearance as coverage, flipping X to "covered" purely because it was once
correctly flagged as not covered. The fix demonstrated here -- excluding files matching the
instrument's own naming convention (`census`, `dream-sweep-a-f`, and the files the script itself
writes) from the evidence pool before classification runs -- is a general convention for any
self-referential audit tool: an instrument must not treat its own prior output, or output of the
same genre, as evidence about the thing that output was reporting on. The residual, unexplained
part of the gap (3 of 8 sessions, plus the D-tier discrepancy) shows the fix is necessary but not
sufficient -- a second, distinct citation-vs-coverage ambiguity (a real `agent-end/` run record
that legitimately cites a session in prose) remains open and was correctly left unresolved rather
than force-fit. Related: [[derive-dont-record]] (a checker trusting a stale or self-produced
record instead of re-deriving from the live artifact).

## Counter-evidence

none found, searched: `wiki/intake-triage/W0-ingest-gate-2026-09-02.md` and
`wiki/intake-triage/GT1-skill-ground-truth-2026-09-02.md` for an instrument in the bounded set
that writes its own findings into the corpus it measures and was shown NOT to be susceptible to
this contamination; `ingest_gate.py`'s FENCE step avoids the shape by construction (its own
ledger, `INGEST-LEDGER.md`, is append-only history, not consulted as coverage evidence for a
future page), which is a different mechanism, not a demonstrated resistance to this specific
class.

## Motivates

none yet -- `scripts/audit/coverage_census.py`'s `--exclude-self-citations` flag implements the
fix as code (default ON), but no `skills/` entry states "an audit instrument must exclude its own
prior output, and output of its own genre, from any evidence pool it builds" as a general rule
for future census/audit tooling.

## Probe

Sealed question above. Falsified if a re-run of `coverage_census.py --exclude-self-citations` on
the same raw/wiki roots shows any of the 5 sessions that flipped back to Z (`9a25da`, `bb5dd0`,
`1b90e4`, `b434b1`, `28b396`) reverting to C, or if the 3 that remained C (`42ee61`, `7a72c9`,
`68a4bd`) are shown to have no non-census citation evidence after all.
