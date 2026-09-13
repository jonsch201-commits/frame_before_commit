---
format: cfl-page/v1
kind: pattern
slug: healthy-mount-is-not-the-case-you-raised
title: "Healthy Mount Is Not The Case You Raised"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "0 FAIL-OPEN-SILENT measured with G healthy says nothing about the degraded-mount case carried as healthy mount degraded case UNMEASURED"
aliases: [zero-defects-under-healthy-conditions-only, headline-number-scoped-to-the-wrong-state, unmeasured-degraded-case]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one fully-worked instance this cycle: Secretary's v2 headline '0 FAIL-OPEN-SILENT' caught by its own next lane as measured only under a healthy mount, not the faulted-mount case the whole hook-reliability effort exists to cover; fixed by adding a --degrade mode as the safe proxy for the untestable real fault."
probe_sealed: "Did Secretary's v2 harness run's headline '0 FAIL-OPEN-SILENT' claim cover the case a fleet-wide hook-reliability effort actually cares about (an unreadable/corrupted script during a real Drive fault)? => No: it was measured with G: healthy, so it says nothing about the degraded-mount case; carried forward explicitly as '0 (healthy mount; degraded-mount case UNMEASURED)' and closed only by v4's --degrade mode, which truncates each hook's script copy to 0 bytes inside the scratch clone as the safe proxy for an unreadable program text. TRUSTED"
---

## Struggle

An instrument reports a clean result (zero defects, zero races, zero FAIL-OPEN-SILENT rows)
under whatever conditions happened to hold at measurement time, and that result is read as
general -- covering the fault condition the whole exercise exists to catch -- when the
conditions that actually held (a healthy mount, no fault present) are precisely the case where
the defect being hunted cannot occur.

- `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md:222` [verbatim] (cropped) -- "The headline
  '0 FAIL-OPEN-SILENT' was measured with G: healthy and says nothing about the degraded-mount
  case: carried as '0 (healthy mount; degraded-mount case UNMEASURED)'; v4 adds a --degrade mode
  that truncates each hook's script copy to 0 bytes INSIDE the scratch clone and re-grades, which
  is the safe proxy for an unreadable program text."
- `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md:226` [verbatim] (cropped) -- the same
  qualifier carried forward, unresolved, one addendum later: "Secretary row now: 5-entry
  PreCompact matcher, 3 confirmed writer/reader races, 0 FAIL-OPEN-SILENT (healthy mount;
  degraded case UNMEASURED pending v4 --degrade)."

## Generalization

A reliability claim is only as general as the conditions under which it was measured, and a
number produced under the LEAST stressful available condition (nothing broken, nothing
concurrent, no fault injected) is structurally incapable of demonstrating the property a
fault-hunting instrument exists to check. The discipline this instance models: the qualifier
("healthy mount") is carried alongside the number every time it is repeated, rather than dropped
once the number starts sounding established -- and the gap it names ("degraded-mount case
UNMEASURED") is treated as an open item with a concrete remedy (a `--degrade` mode simulating the
real fault via truncation, since the real fault itself cannot be safely induced on demand) rather
than left as a caveat nobody acts on. This is the general form of "don't report the easy case as
the hard case" -- a headline number's scope (what conditions it was measured under) is as much a
part of the finding as the number itself. Related: [[a-limitation-rendered-as-a-completed-measurement]]
(the broader class this instance belongs to: a scope-limited result read as a general one).

## Counter-evidence

none found, searched: `wiki/intake-triage/H1c-harness-v4-2026-09-02.md` and
`wiki/intake-triage/H3b-sh-closed-2026-09-02.md` for an instance in the bounded set where a
"clean under normal conditions" result was reported WITHOUT the healthy-condition qualifier
attached; `hook_harness.py`'s own `--degrade` mode (H-1c) is the direct, applied counter-design
-- it explicitly measures the degraded case rather than assuming a healthy-mount result
generalizes -- and both H-1c's baseline (12 OK, 4 FAIL-OPEN-SILENT, healthy) and degraded (11
FAIL-CLOSED-VISIBLE, 5 FAIL-OPEN-SILENT) phases are reported side by side, never one alone.

## Motivates

none yet -- `hook_harness.py`'s `--degrade` flag and Secretary's `--degrade` mode both implement
the remedy as instrument features, but no `skills/` entry states "a clean result must name the
condition it was measured under, and a fault-hunting instrument's headline number is incomplete
without its degraded-condition counterpart" as a general reporting convention.

## Probe

Sealed question above. Falsified if Secretary's v2 run is shown to have actually included a
truncated or corrupted script among its 16 rows (i.e. the healthy-mount qualifier was
unnecessary), or if v4's `--degrade` mode is shown to produce 0 FAIL-OPEN-SILENT on Secretary's
PreCompact matcher as well as the baseline.
