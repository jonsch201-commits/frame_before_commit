---
format: cfl-page/v1
kind: pattern
slug: mtime-on-a-mirror-is-sync-time-not-authorship
title: "Mtime On A Mirror Is Sync Time, Not Authorship"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "corpus mtimes record mirror-sync time not authorship time nonzero count is not evidence of a write the instrument I documented as blind I then read as a verdict"
aliases: [mirror-mtime-is-not-authorship-time, nonzero-count-is-not-a-write-proof, blind-instrument-read-as-a-verdict]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one fully-worked instance this cycle, self-caught: FT-2's own report used a `find -newermt` check on a mirror to try to prove nothing had been written there, named the exact reason that check cannot establish the claim (in its own earlier section), and then used it as a verdict anyway before catching the contradiction in the same report."
probe_sealed: "Can find /n/claude-corpus -newermt '2026-09-02 09:30' -type f (651 hits) establish that FT-2's lane did not write anything under N:\\claude-corpus\\ ? => No: corpus mtimes record mirror-sync time, not authorship time -- a file robocopied at 09:50 is indistinguishable by mtime from one authored at 09:50, so neither a nonzero count nor a zero count would license a conclusion about authorship; the only claim the evidence actually supports is a name-search returning 0 hits for filenames this lane itself authored. TRUSTED"
---

## Struggle

A file's modification time on a synced/mirrored copy reflects when the SYNC touched that file,
not when the content was actually authored -- so a timestamp-based check ("nothing new since
time T") cannot distinguish a freshly-authored file from a stale file a bulk mirror job merely
recopied at time T. An instrument built on this timestamp is therefore blind to the exact
question ("was anything written here by this lane?") it is being asked to answer, in either
direction.

- `wiki/intake-triage/FT2-prototypes-2026-09-02.md:255-258` [verbatim] (cropped) -- "That check
  cannot establish the claim, and the reason is item 2 of §6 above -- written by this lane,
  three sections earlier, about this exact defect. Corpus mtimes record mirror-sync time, not
  authorship time. A file robocopied at 09:50 is indistinguishable by mtime from one authored at
  09:50. So a nonzero count is not evidence of a write, and a zero count would not have been
  evidence of its absence either. The instrument I documented as blind, I then read as a
  verdict."
- `wiki/intake-triage/FT2-prototypes-2026-09-02.md:236-237` [verbatim] (cropped) -- the earlier
  statement of the same limitation, written before the lane used the blind instrument anyway:
  "Item 12 stays UNKNOWN fleet-wide because corpus-root mtimes cannot separate authored-today
  from mirrored-today. `PROTO-coverage_census-v1.py` does not solve this; nothing here does.
  Solving it needs an authorship signal the mirror does not carry."

## Generalization

Writing down a limitation earlier in the same document does not prevent that limitation from
being violated later in the same document -- naming a blind spot is not the same as remembering
not to rely on it three sections later, especially under the pull of wanting to confirm a claim
("nothing under N:\claude-corpus\ was written") the report had already asserted in its first
draft. The remedy this instance demonstrates is not "never use mtime" but to state, at the point
of use, exactly what a given signal CAN license: here, a name-search for filenames this lane
itself authored (0 hits) is a real negative and licenses "no artifact bearing this lane's own
names exists under the corpus root" -- a narrower, weaker, but actually TRUE claim than "nothing
was written," which the mtime evidence cannot support in either direction. The general form: a
signal's scope of proof must be re-stated at the exact place it is used as evidence, not assumed
carried over from where its limitation was first named. Related:
[[count-verified-mirror-hides-zero-byte-shells]] (the sibling failure: a mirror's file COUNT
misread as a content signal, here its file TIME misread as an authorship signal).

## Counter-evidence

none found, searched: `wiki/intake-triage/C1-census-2026-09-02.md` and
`wiki/intake-triage/W0-ingest-gate-2026-09-02.md` for an instance in the bounded set where a
mirror's mtime was correctly used only as a sync-freshness signal rather than an authorship
signal; `coverage_census.py`'s own use of `--as-of` (a caller-supplied date, not a file's mtime)
for temporal scoping is the nearest counter-design, but it operates on a different question
(session date parsed from a filename, not file authorship time) and is not a direct
counter-instance of mtime being misread as authorship.

## Motivates

none yet -- no `skills/` entry or shared instrument states "a mirror's file mtime measures sync
time, not authorship time, and must not be used to prove or disprove that a lane wrote to a
mirrored directory" as a general convention.

## Probe

Sealed question above. Falsified if the 651 files found `-newermt "2026-09-02 09:30"` under
`N:\claude-corpus\` are shown, by content inspection rather than mtime, to have actually been
authored at that time rather than bulk-synced (the report's own mtime-clustering evidence --
four buckets only, 09:44/09:50/09:51/09:54 -- points the other way, toward a bulk-sync
signature).
