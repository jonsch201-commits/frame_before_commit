---
format: cfl-page/v1
kind: pattern
slug: exit0-zero-bytes-fails-open
title: "Exit 0 + Zero Bytes Fails Open"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "exit code zero empty output fails open Drive EINVAL unreadable gate GREEN when disk cannot be read"
aliases: [exit0-0bytes-is-unknown, exit-code-only-trust, unreadable-file-exits-clean]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "reproduced first-hand this cycle on three CFL gates during a Drive EINVAL fault; mitigation stated as a rule (exit0+0bytes = UNKNOWN, never PASS), not yet wired as a wrapper every gate calls through."
probe_sealed: "During the 2026-09-01 ~23:1x Drive EINVAL fault, what did `python postcompact_pipeline.py` (and two other CFL gates) report, and was that report meaningful? => exit 0, 0 bytes output on all three — meaningless (the script file was present but unreadable; a MISSING script exits 2 loudly instead). TRUSTED"
---

## Struggle

A gate that prints a banner and checks its own exit code cannot distinguish "ran clean" from "could
not read the script at all" when the read itself fails silently (a Google Drive EINVAL fault, here)
— both report exit 0. A second, related shape: two independently-built readers of the same artifact
both chose to exit 0 on an empty/UNKNOWN input, so a future caller who checks only the exit code
cannot tell success from absence.

- `exchange/outbox/RECEIPT-2026-09-02-cfl-HOOK-AUDIT.md:66` [verbatim] (cropped) — "`python <gate>`
  on an unreadable file exits 0 with 0 bytes (Soul's finding, reproduced at 23:34 on three CFL
  gates) -- so step 9 after the fix is UNKNOWN until the next compact on a healthy mount ... the
  same blackout truncated `postcompact_pipeline.py` to 0 bytes on Drive through a silent `git show`
  feeding a `cp` (restored from HEAD; class: a producer that fails silently upstream of a copy
  makes the copy a deletion)."
- `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md:50` [verbatim] (cropped) —
  instance 17: "Two trunks (Secretary and CFL) each independently built a PostCompact-summary
  reader with the identical 'exit 0 on empty/UNKNOWN' blemish ... 'TWO TRUNKS NOW EXIT 0 ON
  UNKNOWN. A CALLER READING ONLY THE EXIT CODE CANNOT TELL... Agreement among sources that share an
  ancestor is a copy count, and I am the ancestor.' ... no detector guards against future callers
  trusting exit codes; both trunks added a comment as the only mitigation."

## Generalization

Exit code alone collapses at least three distinct states — "succeeded", "ran and found nothing",
and "could not run at all" — into one bit. Any gate whose caller trusts that bit without also
checking output size/content will read a dead disk, an unreadable file, or a genuinely empty result
as identical to a clean pass. The fix is structural (check exit AND non-empty output; treat
exit0+0bytes as UNKNOWN) rather than a per-script patch, because the failure recurs independently
in unrelated scripts (two different trunks built the same blemish without coordinating). Related: [[count-verified-mirror-hides-zero-byte-shells]] (the write-side twin: a copy whose source read returned nothing).

## Counter-evidence

none found, searched: `wiki/intake-triage/DREAM-2026-09-01-*.md` and
`wiki/intake-triage/DREAM-2026-08-30-*.md` for a gate in this bounded set that correctly
distinguished exit0-clean from exit0-unreadable at the time it ran (rather than in a later audit);
none of the read files show a gate catching this class live, only after-the-fact reproduction.

## Motivates

none yet — no `skills/` entry wraps "check exit code AND non-empty output" as a callable
convention; `RECEIPT-2026-09-02-cfl-HOOK-AUDIT.md:66` states the rule in prose only.

## Probe

Sealed question above. Falsified if a re-run of the three named CFL gates during a subsequent
Drive-unreadable window returns a nonzero exit code or a populated stderr instead of exit 0 with
empty stdout, or if `postcompact_pipeline.py`'s truncation-to-0-bytes is found to have been caught
by a size check before the `cp` overwrote the live file.
