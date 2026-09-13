---
format: cfl-page/v1
kind: pattern
slug: the-later-instrument-can-also-be-silent
title: "The Later Instrument Can Also Be Silent"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "RACE-OPEN silent variant later reader under-counts arrivals reports nothing new with no error text no failure text names a sibling"
aliases: [silent-race-variant, under-count-reads-as-nothing-to-do, quiet-agreement-instead-of-a-crash]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "direct counterpart to the existing [[later-instrument-blames-earlier]] page: same parallel-hook-race mechanism, opposite symptom (a quiet under-count rather than a loud accusation), found in Secretary's own trunk the same day CFL's loud variant was published fleet-wide."
probe_sealed: "When Secretary's index-check.ps1 loses the race against capture-jon-reconcile.ps1 on rulings/jon-arrivals-raw.md, does it emit any error or blame text naming a sibling, the way CFL's postcompact_pipeline.py did? => No: Secretary checked explicitly (Q2) and found zero blame-text hits; the later reader instead reports 'nothing new' -- an under-count that reads as a correct, quiet conclusion rather than a visible failure. TRUSTED"
---

## Struggle

Two hook entries racing under the same matcher on a shared artifact can produce either of two
opposite-looking symptoms depending on which side of the read/write race the LATER-firing
instrument sits: a reader that reads a not-yet-written output can either accuse the writer of
having crashed (loud, self-flagging), or it can silently under-count and report a clean-looking
"nothing new" (quiet, self-concealing) -- and the quiet variant is structurally harder to find
because it produces no text pattern to grep for.

- `N:\claude-gists-private\RECEIPT-2026-09-02-secretary-HOOK-RACE-CHECK.md:47,52-53` [verbatim]
  (cropped) -- "An under-count of arrivals reads as 'nothing new to [disposition]' ... CFL's race
  made the later instrument ACCUSE a sibling of crashing -- loud, wrong, and visible every
  compact. Mine makes an instrument quietly agree that there is nothing to do. CFL's was findable
  by reading its own output. Mine is not."
- `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md:204,206` [verbatim] (cropped) -- CFL's own
  classification of the receipt: "Class: RACE-OPEN, silent variant: the later reader under-counts
  arrivals before this compact's captures land and reports 'nothing new', with no error text; no
  failure text names a sibling (Q2 answered NO)." And the fleet-wide tally naming both variants
  side by side: "Professional 1 RACE-OPEN (loud-then-silent: acceptance satisfied by sibling);
  Secretary 4 BROAD / 3 writer-reader confirmed RACE-OPEN (silent under-count)."

## Generalization

A hook-race audit built to catch the loud variant (grep for blame text: "crashed", "did not
run", "predates") will systematically miss the quiet variant, because the quiet variant produces
no distinctive vocabulary -- it produces a normal-looking, low, or zero count with no accompanying
error. Secretary's own explicit check (Q2: does any failure text name a sibling as crashed?)
returned two hits and both were the OPPOSITE of the defect -- prior, deliberate prose
distinguishing "did not run" from "ran and found nothing" -- which shows that even a trunk that
has already thought carefully about this distinction in its own comments can still have an
unordered race on its most important artifact, because naming the distinction in prose is not the
same as enforcing an ordering in the hook config. The general lesson for any fleet-wide race
sweep: a grep for blame-text vocabulary finds only the loud variant; a race audit that stops
there under-reports, because the quiet variant (a reader silently agreeing there is nothing new)
is at least as consequential -- here, on the artifact holding Jon's own captured words -- and
leaves no textual signature to search for. Related: [[later-instrument-blames-earlier]] (the
loud variant of this same parallel-hook-race mechanism).

## Counter-evidence

none found, searched: `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md` §2 (Antigravity) and
§3 (Professional) for a silent-variant race in the bounded set that was found by the same
blame-text grep method CFL used for the loud variant; every silent-variant instance in the
bounded set (Secretary's PreCompact matcher) was found only by a manual writer/reader
cross-reference of variable names (`$dest` vs `$arrivalsPath`), never by a text-pattern grep --
confirming the grep method structurally cannot find this variant.

## Motivates

none yet -- no `skills/` entry or shared instrument states "a hook-race sweep must check for
BOTH a loud blame-text variant (grep-findable) and a silent under-count variant (findable only by
writer/reader cross-reference of shared artifact paths)" as a combined method.

## Probe

Sealed question above. Falsified if a re-run of Secretary's `hook-race-check.py` on the same
`.claude/settings.json` shows `index-check.ps1` emitting any error text when it reads
`rulings/jon-arrivals-raw.md` before `capture-jon-reconcile.ps1` has finished writing it, or if
the ordering fix (writers before readers, one chained entry) is found to have already landed.
