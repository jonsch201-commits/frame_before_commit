---
format: cfl-page/v1
kind: pattern
slug: wrapper-silenced-by-the-timeout-above-it
title: "Wrapper Silenced By The Timeout Above It"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "wrapper converts silence to UNKNOWN but its own reporting logic runs after the call and never executes if the caller kills it first declared timeout vs harness cap"
aliases: [safety-logic-after-the-kill-point, timeout-outranks-the-wrapper, external-cap-silences-internal-check]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one measured instance (Professional's lint_hook.sh, killed at its declared 120s cap after 184,989ms of real runtime); the harness's own v4 fix (splitting TIMEOUT-DECLARED from TIMEOUT-HARNESS-CAP) is the generalized remedy, built the same day, in the same lane family."
probe_sealed: "Did Professional's lint_hook.sh wrapper -- built specifically to turn a lint failure into a reported UNKNOWN rather than silence -- ever get a chance to run that reporting logic on the run measured 2026-09-02? => No: the wrapper's own logic runs after `bash \"$1\"` returns, and the wrapper itself was killed by its declared 120s SessionStart timeout at 184,989ms (>15x over budget) before that return happened, so none of its UNKNOWN-reporting code ever executed. TRUSTED"
---

## Struggle

A wrapper is built specifically to catch a downstream failure and convert silence into a loud,
legible UNKNOWN -- but the wrapper's own reporting logic sits AFTER the call it wraps, so a
timeout imposed by something outside the wrapper (a hook-config `timeout` key, a harness's own
`--exec-cap`) can kill the wrapper before that logic ever executes. The very layer built to
prevent silent failure becomes a silent failure itself, and the wrapper's own selftest cannot
cover this because the kill signal originates in config the wrapper does not control.

- `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md:218` [verbatim] (cropped) — "the wrapper was
  written to turn 'lint could not run' into an UNKNOWN line, and all of that logic runs after
  `bash \"$1\"` returns, so when the wrapper itself is killed by the declared timeout none of it
  executes: a wrapper built to convert silence into UNKNOWN is silenced by the timeout above it,
  and its selftest cannot cover a kill that comes from the config." Measured the same line:
  `lint_hook.sh 184,989 ms vs declared 120 s ... killed on every SessionStart, all matchers; has
  never completed at a session boundary`.
- `wiki/intake-triage/H1c-harness-v4-2026-09-02.md:27-31` [verbatim] (cropped) -- the
  generalized fix, built the same day in the harness this class was found by: "Every row now
  carries both `declared_timeout_s` (settings.json's own `timeout` key ...) and `harness_cap_s`
  (the actual `min(declared, --exec-cap)` cap this run used). `TIMEOUT-DECLARED` fires when the
  hook's own declared budget is what expired ...; `TIMEOUT-HARNESS-CAP` fires when the harness's
  own cap cut the run short while still inside the declared budget."

## Generalization

Any wrapper whose safety-net logic (a fallback message, a fault ledger write, an UNKNOWN
verdict) is coded to run only after its wrapped call returns is silent-by-construction against
an external kill: the kill prevents the return, and the return is the only trigger the wrapper's
own logic has. This is distinct from the wrapper failing on its own terms (a bug in its logic) --
here the logic is correct and simply never runs, because the layer that could kill it (a
declared per-hook timeout, a harness's own execution cap) sits structurally above the wrapper and
is invisible to the wrapper's own error handling. The remedy is not "make the wrapper faster" (a
symptom fix) but to separate the two distinct causes a timeout can have -- the wrapped process
genuinely hanging past its OWN declared budget, versus an external cap cutting a run short while
still inside that budget -- and report which one happened, since only the first is evidence the
wrapped process is actually broken. Related: [[exit0-zero-bytes-fails-open]] (the underlying
per-invocation fail-open shape this wrapper family exists to catch).

## Counter-evidence

none found, searched: `wiki/intake-triage/H1-hook-harness-2026-09-02.md` and
`wiki/intake-triage/H1b-harness-v2-2026-09-02.md` for a wrapper in the bounded set whose
safety-net logic runs via a signal handler or `trap` rather than after-return, which would
survive an external kill; `py_closed.sh`/`sh_closed.sh` (H-3, H-3b) both do their fault-checking
BEFORE `exec`ing the wrapped command, which sidesteps this specific failure (there is nothing
left to run after a kill, because the wrapper has already handed off via `exec`) but that is a
different structural choice, not a counter-instance of a post-call wrapper surviving a kill.

## Motivates

none yet -- `scripts/audit/hook_harness.py` v4 implements the TIMEOUT-DECLARED /
TIMEOUT-HARNESS-CAP split as a harness feature, but no `skills/` entry states "a wrapper's
safety-net logic must not depend on the wrapped call returning" as a checkable authoring rule for
new wrappers.

## Probe

Sealed question above. Falsified if `lint_hook.sh` is re-measured to complete inside its
declared 120s budget on a subsequent run, or if its UNKNOWN-reporting logic is found to run via a
signal trap rather than after the wrapped call's return.
