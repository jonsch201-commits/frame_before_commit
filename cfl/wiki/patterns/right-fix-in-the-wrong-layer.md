---
format: cfl-page/v1
kind: pattern
slug: right-fix-in-the-wrong-layer
title: "Right Fix in the Wrong Layer"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "fix applied to the artifact a hook reads while the cause sits in the config that runs the hook; intended state published as measured state; settings.json not read back; a right fix in the wrong layer reads exactly like a right fix"
aliases: [fix-at-the-artifact-cause-in-the-config, intended-state-as-measured-state, wrong-layer-fix, one-file-miss]
generated_by: lane W-1b (fable) session e515d858
state: current
state_note: "three instances: both elders' one-file misses in the 2026-09-02 three-way consult (same file, .claude/settings.json, from opposite sides) and the 2026-08-10/08-17 sync-universal CLAUDE.md case; paired with Professional's inverse (decisions that read as accidents). Mitigation stated as a review rule, not yet a lint."
probe_sealed: "In the 2026-09-02 three-way consult, did either elder's one-file check close on the file the fix TOUCHED rather than the file that RUNS the hook, and were both misses the same file? => Yes: the pre-compact elder's Blue Hat at L263 closed on the artifact the hook reads while the cause sat in .claude/settings.json (opened only at L611); the pre-restart elder published 'one ordered entry' (L11321) without reading back .claude/settings.json, and the race was found nineteen hours later. Same file, opposite sides. TRUSTED"
---

## Struggle

A fix is applied to the artifact a mechanism CONSUMES (the file a hook reads, the table a
constitution routes by) while the cause sits one layer up, in the thing that RUNS or
DISTRIBUTES the mechanism (the hook wiring in `.claude/settings.json`, the sync script that
copies one trunk's file to every trunk). The fix is correct at its own layer, passes every review
that checks the fix against the finding, and the defect keeps running because nobody read the
layer above.

- `exchange/elders/THREE-WAY-CONSULT-2026-09-02.md:45` [verbatim] (cropped) -- "Elder's own
  one-file miss: the Blue Hat at L263 closed on the artifact the hook reads while the cause sat
  in .claude/settings.json, opened only at L611; \"a right fix in the wrong layer reads exactly
  like a right fix.\" Both elders' one-file misses are the same file, from opposite sides."
- `exchange/elders/THREE-WAY-CONSULT-2026-09-02.md:42` [verbatim] (cropped) -- "(4) the
  elder's own one-file check: it published \"one ordered entry\" (L11321) without reading back
  .claude/settings.json, the race found nineteen hours later; intended-state-as-measured-state,
  the same defect it had rejected AG's PROP-004 for at L10828".
- `CLAUDE-UNIVERSAL.md:13-18` [verbatim] (cropped) -- "Until 2026-08-17, `sync-universal.sh`
  copied CFL's project `CLAUDE.md` to `~/.claude/CLAUDE.md` on every `SessionStart`. ... the two
  files were byte-identical ... So every trunk on this machine loaded one trunk's project
  constitution as its global layer". The 08-10 fix qualified the routing TABLE (the artifact every
  trunk reads); the sync script that made one trunk's table every trunk's table kept running for
  six more days (`CLAUDE-UNIVERSAL.md:35-37`: "neither party turned a correctly-diagnosed cause
  into a ticket. MISSING ARTIFACT, NOT MISSING INSIGHT").
- `exchange/inbound/herald-to-cfl-REVIEW-VERDICT-B4-0810-fix-CLOSED-and-the-architecture-defect-was-never-in-my-finding-2026-08-17.md:47-49`
  [verbatim] (cropped) -- the fixer's own 08-10 commit message already named the upper layer:
  "CLAUDE.md syncs to the global layer -- so a table written from one trunk's layout was routing
  every trunk" / "That is the architecture defect, stated correctly, on 2026-08-10, by the fixer.
  It then sat six" days. The review of the table fix returned CLOSED-AND-REVIEWED (`:19`) and was
  right to; the architecture defect was outside the finding.

## Generalization

Every mechanism in this program has at least two layers: the artifact it reads and the
configuration that decides whether, when, and in what order it runs. A fix to the artifact is
verifiable by opening the artifact, so that is where a one-file check lands -- and the check
passes, because the artifact IS fixed. The layer above (the hook matcher, the sync script, the
distribution path) is not opened, because the finding never named it and the fix did not touch
it. "Intended state as measured state" is the same defect seen from the writer's side: the seat
that wrote "one ordered entry" published what it MEANT settings.json to hold and never read the
file back. The remedy is a review rule, not a new gate: before closing a fix, name the layer that
RUNS the thing you fixed and open that file too; a fix whose stated cause is broader than the
artifact it touched is not closed until the broader cause has a disposition
([[finder-closes-the-loop-never-the-author]] carries the reviewer half of the same rule).

**The inverse, found by Professional the same day and paired here on purpose.** Where this
pattern is a right fix that reads as a right fix while the cause runs on, Professional's
finding is a deliberate DECISION that a successor reads as an ACCIDENT and tidies away:
`N:\claude-gists-private\professional-tree\wiki\intake-triage\dream-2026-09-02-elders-and-the-reasoning-is-not-on-disk.md:21-24`
[verbatim] (cropped) -- "never ask an elder \"why did you decide X.\" ... Ask what it MEASURED,
what it left MID-FLIGHT, and what it DECIDED that a successor would read as an accident"; and
`:94-95` -- "Record the four \"decisions that read as accidents\" somewhere a successor reads
BEFORE tidying." Both are the same blindness from opposite ends: a review that checks an artifact
against a finding sees neither the cause above the artifact nor the intent behind it. The receipt
the wake brief named for this pairing
(`exchange/inbound/pro-to-cfl-secretary-RECEIPT-converter-confirmed-and-I-quarantined-four-WITHHOLDs-*-2026-09-02.md`)
is UNKNOWN: 0 matches under `exchange/inbound/`, `N:\claude-gists-private\` root, and
`N:\claude-gists-private\professional-tree\` at write time, so the dream page above is cited in
its place, plus the consult file's own pairing of the two elders' misses (`:45`).

## Counter-evidence

none found, searched: `exchange/elders/THREE-WAY-CONSULT-2026-09-02.md` (all 45 lines) and
`exchange/inbound/herald-to-cfl-REVIEW-VERDICT-B4-*-2026-08-17.md` for an instance in this bounded
set where a one-file check opened the RUNNING layer (settings.json, sync-universal.sh) before
closing on the artifact; the only opening of `.claude/settings.json` in the consult record is at
L611, after both closes, and the 08-17 review explicitly scopes itself to the finding and names
the architecture defect as still live (`:62`).

## Motivates

none yet -- no `skills/` entry states "before closing a fix, open the file that RUNS the thing you
fixed" as a checkable step; `CLAUDE-UNIVERSAL.md:39-40` states the reviewer-side half (check the
fix against the finding AND against the cause the fixer named) in prose only.

## Probe

Sealed question above. Falsified if the consult record shows `.claude/settings.json` opened
before L263 by the pre-compact elder, or read back by the pre-restart elder before it published
"one ordered entry" at L11321; or if the 08-10 commit that qualified the routing table is found
to have also changed `sync-universal.sh` (in which case the fix was in both layers and the
six-day run had another cause).
