---
format: cfl-page/v1
kind: pattern
slug: name-matched-as-location
title: "Name Matched as Location"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "name substring matched wrong page same name confident plausible wrong answer glob date mismatch"
aliases: [wrong-page-under-same-name, glob-name-collision, confident-plausible-wrong]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "two distinct instances measured (a concept-page name collision, a filename-date glob mismatch); no fleet-wide sweep for the class exists."
probe_sealed: "Does `wiki/concepts/personal-role-architecture.md` describe the fleet trunk 'Personal', or Jon's household-role framework? => Jon's household-role framework — a session searching the fleet-trunk name lands on this page and gets a confident, plausible, wrong answer. TRUSTED"
---

## Struggle

A search or a glob matches on a NAME (a filename fragment, a date-in-a-filename, a concept-page
title) and treats the match as if it located the right THING — when a second, unrelated referent
shares the same string, the searcher gets a confident, plausible, wrong answer instead of a miss it
could notice.

- `wiki/intake-triage/DREAM-2026-08-30-pass-two-ingest-pipeline-stopped-0822-and-the-name-collisions.md:31-34`
  [verbatim] (cropped) — "Two resolve to **WRONG pages under the same name** —
  `wiki/concepts/personal-role-architecture.md` and `wiki/concepts/herald-of-home-and-life.md`
  document Jon's household-role framework, not the fleet trunks: a session searching those names
  gets a confident, plausible, wrong answer. That failure mode is worse than a blank gap."
- `wiki/intake-triage/DREAM-2026-09-01-explicit-cycle-post-reboot-six-sweeps-and-the-queued-command-class.md:44-47`
  [verbatim] (cropped) — "the lane reported 'no transcript files in range' -- **false negative**:
  `ls raw/transcripts/claude-code/fl/ | grep 2026-09-0[12]` = 3 windows (all 9041f3). Cause: the
  lane globbed `code-2026-09-01-*` and the windows are UTC-date-named `code-2026-09-02-*` (the
  mirror hit the same trap and named it)."

## Generalization

A name is a pointer chosen at authoring time for a purpose the name's string does not encode
(role-terminology reuse; a UTC-vs-local date in a filename). A later instrument that resolves by
name-substring rather than by the thing's actual identity/provenance inherits whatever collision
the name happens to carry — and the failure is silent precisely because a match was found, so
nothing signals "check this." The second instance is the sharper case: TWO independent lanes
(a coordinator lane and, separately, "the mirror") hit the identical UTC-date naming trap, which
means the trap is in the naming convention itself, not in one searcher's carelessness. Related:
[[derive-dont-record]] (a checker trusting a stale name-to-referent mapping).

## Counter-evidence

none found, searched: `wiki/skills-gate/LEDGER.md` and
`wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md` for an instance where a
name-substring match was checked against provenance before use and the check caught the collision
BEFORE publication (rather than after, as both instances above were). No such pre-publication catch
appears in the bounded set.

## Motivates

none yet — the DREAM-08-30 packet proposes (not built) "a disambiguation note atop the two
colliding concept pages" and "entity pages for Secretary, Professional, Soul, Antigravity,
Personal-the-trunk, Herald-the-trunk"; neither exists in `skills/` as a checkable convention.

## Probe

Sealed question above, plus a second check: does a fresh glob for `code-2026-09-01-*` under
`raw/transcripts/claude-code/fl/` in the clone return 0 files while `code-2026-09-02-*` returns the
files actually written on 09-01 local time? Falsified if either check returns the opposite of what
is stated (the concept page correctly describes the fleet trunk, or the date-globs now agree).
