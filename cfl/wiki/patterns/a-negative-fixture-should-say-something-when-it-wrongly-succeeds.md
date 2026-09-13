---
format: cfl-page/v1
kind: pattern
slug: a-negative-fixture-should-say-something-when-it-wrongly-succeeds
title: "A Negative Fixture Should Say Something When It Wrongly Succeeds"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "deny-read ACL silently failed to apply wrapper passed by running a healthy script SHOULD-NOT-RUN line caught it"
aliases: [should-not-run-line, silent-fixture-setup-failure, negative-control-needs-its-own-alarm]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "one measured instance this cycle: Secretary's ps_closed wrapper test, where the deny-read ACL fixture setup silently failed and the wrapper 'passed' by correctly running a script that should have been unreadable; caught only because the fixture itself asserted it should not have been able to run."
probe_sealed: "When Secretary's first icacls deny-read ACL attempt silently failed to apply, did the wrapper test suite report a false PASS? => Yes, on the first attempt: the wrapper ran the (still-readable) script and returned success, which the harness would read as a correct pass-through, until the fixture's own SHOULD-NOT-RUN assertion caught the setup failure and flagged it instead. TRUSTED"
---

## Struggle

A negative fixture is built to make a target fail (an ACL that denies read, a truncated file, a
missing path) so a wrapper's fault-detection can be exercised against it. When the fixture's own
setup silently fails to apply the intended condition, the wrapped target runs normally, the
wrapper reports success, and every downstream assertion about "the wrapper correctly caught the
fault" passes -- for the wrong reason: nothing was ever actually broken.

- `wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md:230` [verbatim] (cropped) -- "Pattern from
  Secretary's build worth the layer: a negative fixture should say something when it wrongly
  succeeds (its first ACL attempt silently failed to apply and the wrapper 'passed' by running a
  healthy script; the fixture's SHOULD-NOT-RUN line is what caught it)." Same line, the
  three-runtime context this fixture was built to test: "PowerShell -File fails CLOSED on
  unreadable (exit 1, 'Incorrect function / CommandNotFoundException') ... (Secretary, 09:5x,
  with an icacls deny-read fixture for the unreadable case)."
- `wiki/intake-triage/H1-hook-harness-2026-09-02.md:121-137` [verbatim] (cropped) -- the same
  class stated as a design principle for `hook_harness.py`'s own selftest, one lane earlier the
  same day: "the FAIL-OPEN-SILENT detector for the python 0-byte case is gated by an env var so
  the selftest's failing branch can be demonstrated on demand, not asserted from a config file
  nobody re-reads ... With the detector disabled, case (a) is graded `OK` instead of
  `FAIL-OPEN-SILENT`, the expected/got lists diverge, and the process exits 1." Both instances
  share the same shape: a test suite that can demonstrably fail is what makes its passing runs
  trustworthy.

## Generalization

A fixture that is meant to induce a specific failure condition is itself a piece of untested
setup code, and setup code can fail silently just like production code -- an ACL call that
returns success but did not actually restrict access, a `chmod` that no-ops on a filesystem that
ignores it, a mock that is wired to the wrong target. Without an assertion INSIDE the fixture
that the intended condition actually took hold (here: the fixture itself checks that the script
should not have been able to run, and flags when it did), a wrapper test can pass every run while
never once exercising the failure path it claims to cover. The general form is the same one
`hook_harness.py`'s own selftest applies to itself (a detector-disabled run must produce a
DIFFERENT, documented-wrong result, or the "control" proves nothing) -- a negative fixture is not
trustworthy merely because it exists; it is trustworthy only once it has been shown to be capable
of reporting its own setup failure. Related: [[a-check-that-cannot-fail]] (the adjacent, harder
failure: a control that cannot discriminate at all, versus one that can but whose setup silently
misfired).

## Counter-evidence

none found, searched: `wiki/intake-triage/H3-py-closed-2026-09-02.md` and
`wiki/intake-triage/H3b-sh-closed-2026-09-02.md` for a negative fixture in the bounded set that
lacked a self-check and was later shown to have silently misfired without one; CFL's own
0-byte-file and nonexistent-path fixtures (H-1, H-3, H-3b selftests) sidestep the class by
construction rather than by an explicit self-check -- a 0-byte file or a nonexistent path cannot
"fail to apply," unlike an ACL permission change, so they are not a counter-instance of the
pattern's remedy, only an instance where the hazard did not arise.

## Motivates

[SKILL: probe-registry] -- the sealed-expectations-before-the-run discipline this skill already
formalizes is the general home for "a negative fixture must be shown capable of reporting its
own setup failure," even though the skill's current text does not name fixture-setup-verification
specifically.

## Probe

Sealed question above. Falsified if a re-read of Secretary's `PROTO-ps_closed-v1.ps1` selftest
transcript shows the deny-read ACL succeeded on its first attempt with no retry, or if the
SHOULD-NOT-RUN assertion is found to be absent from the fixture's own code.
