---
format: cfl-page/v1
kind: pattern
slug: later-instrument-blames-earlier
title: "Later Instrument Blames Earlier (Hook-Order Race)"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "later instrument blames earlier hook race PostCompact parallel matcher FAIL crashed"
aliases: [hook-order-race, parallel-hook-blames-verifier, postcompact-race]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "one closed instance (RP-30, CFL's own PostCompact); the general form (any trunk with >1 entry under one matcher where a later entry reads what an earlier one wrote) is stated but not swept fleet-wide."
probe_sealed: "What did CFL's PostCompact step-9 check report about the verifier before the 2026-09-01 fix, and was it true? => the verifier 'likely crashed' — FALSE; it was still running, 4 minutes vs the pipeline's 37.5 s, under Claude Code's concurrent-matcher-entry execution. TRUSTED"
---

## Struggle

Two hooks are wired under one matcher as if sequence were guaranteed; Claude Code runs entries
under one matcher concurrently; the later one reads state the earlier one has not written yet, and
grades that absence a defect in the earlier one rather than a race in itself.

- `exchange/outbox/RECEIPT-2026-09-02-cfl-HOOK-AUDIT.md:34` [verbatim] — "PostCompact in CFL was
  two hook entries under one matcher: `postcompact_verify.py` then `postcompact_pipeline.py`.
  Claude Code runs entries under one matcher concurrently. The verifier greps the Drive tree for
  quoted spans and took about four minutes tonight ... the pipeline finished in 37.5 s ... and its
  step 9 read the postcompact directory before the verifier wrote, found the newest artifact older
  than the newest receipt, and graded FAIL with the note 'verifier likely crashed'. The verifier
  had not crashed."
- `wiki/tracker/wayfinder-pr3-record-pipeline-2026-08-31.md:94` [paraphrase] — RP-30 row: "Two
  entries under one PostCompact matcher run CONCURRENTLY ... step 9 graded FAIL 'verifier likely
  crashed' on a verifier that had not crashed. Fix: ONE chained entry `verify; pipeline` (timeout
  900) ... Test after: sequential re-run graded step 9 PASS." State: CLOSED (for this one pair).

## Generalization

When two instruments are wired to run "in order" but the harness only guarantees they run under
the same trigger, not in sequence, the faster one's read of the slower one's not-yet-written output
gets misread as the slower one's failure — an accusation authored by timing, not by evidence. The
receipt names the general form directly (`RECEIPT-...-HOOK-AUDIT.md:38`, paraphrase): "any trunk
with more than one entry under one PostCompact or SessionStart matcher, where a later entry reads
what an earlier one writes, has this race."

## Counter-evidence

none found, searched: grepped `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md`
and the three DREAM packets in the bounded set for a second closed instance of this exact
mechanism (parallel-matcher race misdiagnosed as a crash); only RP-30 (CFL's own) was found
closed. The HOOK-AUDIT receipt's fleet table (§1) reports the *general* hazard as unswept for
Personal (11 SessionStart entries) and Secretary (two events, order unchecked) — those are open
risk, not counter-evidence that the pattern fails elsewhere.

## Motivates

none yet — the fix that closed RP-30 (chain the two entries: `verify; pipeline`, one matcher) is a
one-off `.claude/settings.json` edit, not yet generalized into a skill or a linter that would flag
a second live entry under one PostCompact/SessionStart matcher fleet-wide.

## Probe

Sealed question above. Falsified if a re-read of `RECEIPT-2026-09-02-cfl-HOOK-AUDIT.md:34` shows
the step-9 note attributing the FAIL to something other than the verifier's slower runtime under a
concurrent matcher, or if `.claude/settings.json`'s PostCompact entry is found to be un-chained
(two live entries) after the stated fix date. Related: [[exit0-zero-bytes-fails-open]] (a
different way a fast reader misjudges a slow producer's state).
