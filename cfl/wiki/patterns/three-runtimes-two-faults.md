---
format: cfl-page/v1
kind: pattern
slug: three-runtimes-two-faults
title: "Three Runtimes, Two Faults"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "python bash powershell unreadable empty exit code matrix a failed copy produces the empty case for all three fail open fail closed"
aliases: [runtime-exit-code-matrix, unreadable-vs-empty-per-interpreter, failed-copy-produces-empty]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one fully-worked cross-fleet measurement (Addendum 8), with the shared root cause (a failed copy produces the empty case) corroborated by Professional's own 1,068-zero-byte poisoned mirror measured the same day."
probe_sealed: "Across python, bash, and PowerShell -File, does the same fault condition (an unreadable script file vs a zero-byte script file) produce the same exit-code shape in every runtime? => No: python fails OPEN on both unreadable and empty (exit 0, 0 bytes both); bash fails CLOSED on unreadable (126) but OPEN on empty (0); PowerShell -File fails CLOSED on unreadable (exit 1) but OPEN on empty (exit 0, 0 bytes) -- two of two fault conditions cross runtime boundaries differently, measured first-hand per runtime the same day. TRUSTED"
---

## Struggle

A single mitigation built against one runtime's failure shape (python's exit-0-on-anything) does
not generalize to a fleet where hooks run under three different interpreters, because each
interpreter fails differently depending on WHICH of two distinct fault conditions -- an
unreadable file versus a zero-byte file -- it hits, and a Drive-transient fault or a failed copy
produces exactly the fault condition (empty) that is hardest to detect across all three.

- `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md:230` [verbatim] (cropped) -- "python fails
  OPEN on unreadable AND on empty (exit 0, 0 bytes both); bash fails CLOSED on unreadable (126)
  and OPEN on empty (0); PowerShell -File fails CLOSED on unreadable (exit 1, 'Incorrect function
  / CommandNotFoundException') and OPEN on empty (exit 0, 0 bytes) ... A failed copy produces the
  empty case for all three; Professional's poisoned mirror was 1,068 zero-byte files."
- `N:\claude-gists-private\REPORT-2026-09-02-personal-S1-queued-ingest-and-schema-audit.md:48-51`
  [verbatim] (cropped), the independent same-day corroboration of the shared root cause across a
  fourth measurement (`wc -l`, not a hook runtime but the same class): "under the `G:` fault
  `wc -l` exits nonzero, writes its error to stderr, and prints `0 <file>` to STDOUT. Anything
  parsing a count off stdout gets a plausible, wrong, silent zero. Three instruments now known to
  fail toward a believable number rather than toward an error."

## Generalization

A fleet running hooks under multiple interpreters cannot rely on one runtime's exit-code
contract as a universal signal, because "unreadable" and "empty" are two DISTINCT fault
conditions that each runtime handles independently -- bash and PowerShell both fail CLOSED
(loudly) on unreadable but OPEN (silently) on empty, while python fails OPEN on both. The
practical consequence, stated in the same finding: a wrapper design (read-then-check-size-then-
exec, as `py_closed.sh`/`sh_closed.sh`/`PROTO-ps_closed-v1.ps1` all independently converged on)
must perform its own real read and size check BEFORE invoking the interpreter, because relying on
the interpreter's own native exit behavior means trusting a contract that silently changes shape
between the empty case and the unreadable case, and between runtimes. And because the single most
common real-world trigger for the "empty" condition specifically is a failed or partial copy (not
a permissions fault, which produces "unreadable"), any fleet-wide fix must cover the empty case
in every runtime, not just the loud unreadable case that bash and PowerShell already report for
free. Related: [[exit0-zero-bytes-fails-open]] (the python-only instance of this same class,
generalized here to bash and PowerShell).

## Counter-evidence

none found, searched: `wiki/intake-triage/H3-py-closed-2026-09-02.md` and
`wiki/intake-triage/H3b-sh-closed-2026-09-02.md` for a runtime in the bounded set that fails
CLOSED on BOTH conditions (which would make a wrapper unnecessary for that runtime); none of the
three measured runtimes does -- every one of them fails OPEN on at least the empty case, which is
exactly why all three trunks independently built a read-before-exec wrapper rather than relying
on any runtime's native behavior.

## Motivates

[SKILL: probe-registry] -- a cross-runtime fault matrix like the one measured here is exactly the
kind of pre-stated, falsifiable expectation the skill's seal-before-run discipline is meant to
carry forward, though the skill's current text does not name interpreter-specific exit-code
behavior.

## Probe

Sealed question above. Falsified if a re-measurement of `bash <0-byte-file>` or
`python <0-byte-file>` on this same box returns a nonzero exit code, or if `PowerShell -File`
against a genuinely unreadable (not merely missing) script is shown to exit 0.
