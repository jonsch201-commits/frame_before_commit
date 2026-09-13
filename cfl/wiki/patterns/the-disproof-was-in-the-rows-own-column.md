---
format: cfl-page/v1
kind: pattern
slug: the-disproof-was-in-the-rows-own-column
title: "The Disproof Was In The Row's Own Column"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "verdict contradicted a field in its own row side_effects beside FAIL-OPEN-SILENT classifier read the exit code and never the side-effect list it had collected"
aliases: [verdict-contradicts-its-own-row, side-effects-beside-the-false-verdict, classifier-didnt-read-its-own-output]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one fully-worked instance this cycle (CFL's harness misclassifying precompact-capture.sh), corrected the same day and landed as a v3 rule; corroborated by the adjacent GT-1 instance where the live gate_check.py failure was reproduced at HEAD and shown to be pre-existing, visible in the ledger's own text."
probe_sealed: "Did hook_harness.py's v1/v2 classifier have the evidence to know precompact-capture.sh's FAIL-OPEN-SILENT verdict was wrong, before v3 fixed it? => Yes: the same row that carried class=FAIL-OPEN-SILENT and stdout_bytes=0 also carried side_effects=[' M exchange/last-precompact-receipt.md', ' M exchange/precompact-receipts.log'] -- the script had modified both files, and the classifier consulted only the static source heuristic (does the script contain print/echo) rather than the side-effects field it had already collected in the same row. TRUSTED"
---

## Struggle

A classifier or grader collects several fields into one row (an exit code, a stdout byte count,
a list of side effects, a static source-text heuristic) and reaches a verdict using only a
subset of them -- while a different field, sitting in the same row, already contradicts that
verdict. The disproof was never missing; it was measured, stored, and printed, one column over
from the field the verdict actually used.

- `N:\claude-gists-private\FINDING-2026-09-02-professional-C29-CANNOT-SEE-THE-BOUNDARY-WHOSE-RECORDER-DIED.md:94`
  [verbatim] -- "IT MODIFIED BOTH FILES. THE VERDICT CONTRADICTED A COLUMN IN ITS OWN ROW." In
  full context, same finding: "The script's echoes are inside a redirected block ... ZERO STDOUT
  IS THE DESIGN. And the harness's own row carried the disproof one field over: `class:
  FAIL-OPEN-SILENT`, `stdout_bytes: 0`, `side_effects: [' M exchange/last-precompact-receipt.md',
  ' M exchange/precompact-receipts.log']`."
- `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md:214` [verbatim] (cropped) -- "the
  classifier read the source body and the exit code and never read the side-effect list it had
  collected: a verdict contradicting a field in its own row (Professional's instance eleven).
  Fixed as the v3 rule in `scripts/audit/hook_harness.py`: non-empty side_effects dominates the
  static stdout heuristic unless the script is 0 bytes/unreadable."

## Generalization

When an instrument computes multiple signals about the same event and then decides a verdict
from only one of them (here: a static "does the source normally print" text heuristic, rather
than the `git status --porcelain` diff the same run had already captured as `side_effects`), the
richer signal is not absent from the audit trail -- it is present, adjacent, and unused. This is
a distinct failure from a missing measurement: the fix is not "collect more data" but "make the
verdict logic actually consult the data already collected," and the correct priority ordering
between competing signals (a real file-write is stronger evidence of a completed action than the
mere presence of a `print(` call in source text) has to be stated explicitly, because nothing
forces a classifier to prefer the stronger signal on its own. The GT-1 report's own live-gate
reproduction (`skills_gate_check.py` failing identically at HEAD, before any of that lane's own
edits) is the adjacent shape: the ledger's own text already carried the field-name mismatch
(`**Run:**`/`**Probes:**`/`**Verdict:**` instead of G2's five required fields) that explains the
FAIL, and the fix requires reading what the row already says rather than assuming the failure is
new. Related: [[recorder-and-check-cannot-see-the-same-loss]] (the adjacent failure: not a
column unread within a row, but a row that never gets created at all).

## Counter-evidence

none found, searched: `wiki/intake-triage/H1c-harness-v4-2026-09-02.md` and
`wiki/intake-triage/H3b-sh-closed-2026-09-02.md` for an instance in the bounded set where a
richer collected signal (side_effects, stderr_head) was consulted BEFORE the verdict was first
published rather than after a correction; H-1's own report explicitly declines to automate this
for its five UNCORROBORATED FAIL-OPEN-SILENT rows ("corroboration is not automated into the
class name itself, which is a deliberate choice: automating it further risks quietly downgrading
a real crash into 'probably fine'"), which is a stated, deliberate non-automation rather than a
counter-instance of the pattern being avoided by design.

## Motivates

none yet -- the v3 side-effects-dominates rule lives in `scripts/audit/hook_harness.py`'s own
code, not as a stated `skills/` convention that a new classifier should consult its own richer
fields (side effects, stderr) before a weaker static heuristic.

## Probe

Sealed question above. Falsified if `precompact-capture.sh`'s row is found to have carried an
empty `side_effects` list at the time v1/v2 classified it FAIL-OPEN-SILENT, or if the v3 rule is
shown to ignore side_effects in favor of the stdout heuristic on a subsequent CFL run.
