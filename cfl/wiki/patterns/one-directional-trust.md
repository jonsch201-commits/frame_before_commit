---
format: cfl-page/v1
kind: pattern
slug: one-directional-trust
title: "One-Directional Trust"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "size -ge bigger is fresher skip guard newer-or-equal larger-or-equal one direction only pins forever"
aliases: [bigger-means-fresher, ge-skip-guard, size-comparison-only-one-way]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one fully-worked instance this cycle: corpus-sync.sh's skip guard, measured to permanently pin 608 of 659 files it should have re-copied."
probe_sealed: "Does corpus-sync.sh's skip guard (dst mtime >= src mtime AND dst size >= src size) ever refuse to re-copy a file whose destination is larger but WRONG? => Yes, measured: a CRLF-translated copy is always larger than its LF source, so once such a copy exists with a not-older mtime, the -ge-on-size guard skips it on every future run, permanently -- 648 of 659 files skipped on the measured run, all 608 line-ending-diverged files inside that 648. TRUSTED"
---

## Struggle

A predicate that is correct in one direction (a bigger/newer destination is usually the result
of a completed write, so skipping it avoids clobbering good data) is applied as if it were
correct in both directions, so a destination that is bigger for the WRONG reason -- corruption,
a format translation, an unrelated second writer -- is treated as equally trustworthy as one
that is bigger because it is genuinely current.

- `N:\claude-gists-private\FINDING-2026-09-02-professional-C23-IS-976-PERCENT-NOISE-OF-ITS-OWN-MAKING.md:96-100`
  [verbatim] — "`corpus-sync.sh` skips a file when the destination is newer-or-equal AND
  larger-or-equal: `[ "$(stat -c %Y "$dst")" -ge "$(stat -c %Y "$f")" ] && [ "$(stat -c %s "$dst")"
  -ge "$(stat -c %s "$f")" ]` ... A CRLF COPY IS ALWAYS LARGER THAN ITS LF SOURCE. So once such a
  copy exists and its mtime is not older, `-ge` PINS IT PERMANENTLY: the sync will skip it on
  every future run, forever."
- `N:\claude-gists-private\FINDING-2026-09-02-professional-C23-IS-976-PERCENT-NOISE-OF-ITS-OWN-MAKING.md:121`
  [verbatim] (cropped) — "The guard's own comment says it exists so that 'mtime alone misses a
  truncated copy from a failed run' -- a real defect, correctly guarded. The `-ge` on SIZE is a
  one-directional trust: it assumes a bigger destination is a better one. That is true for
  truncation and false for every other divergence."

## Generalization

A guard built to catch one specific failure mode (a truncated, partial copy -- smaller and
older) is stated as an inequality (`>=`) that also silently licenses the opposite failure mode
(a corrupted-but-larger copy) as safe. The asymmetry is invisible at write time because the
guard's positive control (does it stop truncation?) passes, and nobody tests the negative
direction (does a bad-but-bigger destination get skipped forever?) because the guard's own
comment only names the case it was built for. The remedy the same finding proposes --
compare content or hash, or require size-inequality checked in EITHER direction, keeping the
truncation guard as a separate explicit test -- generalizes to any freshness/quality gate
expressed as a single-direction comparison: state which direction the comparison is meant to
police, and add an explicit test for the other direction before trusting the gate's silence.
Related: [[count-verified-mirror-hides-zero-byte-shells]] (a different mirror-integrity failure
mode: a count or copy read as proof of content).

## Counter-evidence

none found, searched: `wiki/intake-triage/C1-census-2026-09-02.md` and
`wiki/intake-triage/FT2-prototypes-2026-09-02.md` for a size- or mtime-based comparison gate in
the bounded set that is checked in both directions rather than one; `PROTO-boundary_receipt_census-v1.py`'s
`--dedupe` flag (FT2 §3) is the nearest counter-design -- it treats a *repeated* value as
suspect rather than trustworthy by default -- but it operates on a different signal (identical
triples across sessions, not size/mtime comparison) and is not a direct counter-instance of this
pattern.

## Motivates

none yet -- no `skills/` entry states "a size- or mtime-based freshness comparison must be
tested in both directions before it is trusted" as a checkable convention.

## Probe

Sealed question above. Falsified if a re-run of `corpus-sync.sh` against the measured 608
line-ending-diverged files (e.g. `wiki/SCHEMA.md`, G: 4067 B CR=0 vs corpus 4130 B CR=63) copies
them cleanly rather than skipping them, or if the guard is found to already compare content/hash
rather than raw byte size.
