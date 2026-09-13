---
format: cfl-page/v1
kind: pattern
slug: count-verified-mirror-hides-zero-byte-shells
title: "Count-Verified Mirror Hides Zero-Byte Shells"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "file count present coverage census subagent transcripts only main sessions absent silent cp truncation"
aliases: [file-count-hides-empty-shell, coverage-census-wrong-kind, silent-copy-as-deletion]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "one closed-loop instance (postcompact_pipeline.py truncated then restored from HEAD) and one open-ended instance (148 subagent-transcript files present while the main-session pipeline that should also be producing files had stopped entirely)."
probe_sealed: "During the 2026-08-30 coverage census, did the presence of 148 transcript files in `raw/transcripts/claude-code/` mean the export/parse pipeline was healthy? => No — those 148 were subagent-dispatch transcripts written by a separate live mechanism; 0 of 928 non-subagent claude-code files were dated in the 08-23..30 window, i.e. the main pipeline the census cared about had stopped a week earlier despite a nonzero file count in the directory. TRUSTED"
---

## Struggle

A count of files present, or a copy that completed without error, is treated as proof of content —
when the count is counting the wrong KIND of artifact, or the copy's source was silently empty, the
"present" signal survives while the thing it was meant to stand for is gone.

- `wiki/intake-triage/DREAM-2026-08-30-pass-two-ingest-pipeline-stopped-0822-and-the-name-collisions.md:15-19`
  [verbatim] (cropped) — "the main-transcript export/parse pipeline has produced **nothing since
  2026-08-22** -- 0 of 928 non-subagent claude-code files are dated in the 08-23..30 window (only
  subagent-dispatch transcripts, written by a separate live mechanism, exist: 148 files) ...
  pass one's 'curated wiki blind after 08-24' is not a wiki-master lapse alone -- the raw input
  feed it ingests from stopped a week ago."
- `exchange/outbox/RECEIPT-2026-09-02-cfl-HOOK-AUDIT.md:66` [verbatim] (cropped) — "the same
  blackout truncated `postcompact_pipeline.py` to 0 bytes on Drive through a silent `git show`
  feeding a `cp` (restored from HEAD; class: a producer that fails silently upstream of a copy
  makes the copy a deletion)."

## Generalization

Two ways a "the mirror/count looks fine" signal survives real emptiness: (1) a directory listing
that mixes artifact kinds reports a healthy nonzero count while the specific kind a downstream
consumer needs has zero recent members; (2) a copy pipeline whose upstream producer (`git show`)
fails silently — printing an error like "not a git repository" but still writing 0 bytes to
stdout — feeds a `cp` that then "successfully" overwrites a live file with nothing. In both cases
the check that would have caught it (file count by KIND and date; source-non-empty before copy)
was never run, and the artifact that reads healthiest (present, sized, committed) is the one that
just replaced real content with a shell. Related: [[exit0-zero-bytes-fails-open]] (the read-side twin of this write-side failure).

## Counter-evidence

none found, searched: `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md` and the
other DREAM packets in the bounded set for an instance where a count-based or copy-based check
correctly distinguished a healthy artifact from a zero-content shell WITHOUT a human opening the
file first; every instance found in the bounded set was caught by direct inspection after the
fact, never by the count/copy mechanism itself.

## Motivates

none yet — `RECEIPT-2026-09-02-cfl-HOOK-AUDIT.md:66` states the recovery road ("never retry a `cp`
whose source you have not verified") as prose; no `scripts/` wrapper enforces
source-non-empty-before-copy or count-by-kind-and-date as a reusable check in the bounded set.

## Probe

Sealed question above, plus: is `postcompact_pipeline.py` in the current clone non-zero bytes and
does its content match `git show HEAD:scripts/.../postcompact_pipeline.py` (i.e., was the
restore-from-HEAD durable)? Falsified if the census's 148-file count is shown to already have been
kind-filtered at measurement time, or if the truncated script was never actually restored.
