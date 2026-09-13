---
name: age-zero-acceptance-hides-duration-failure
description: A single live acceptance sitting measures a system at duration zero, which is precisely where duration-dependent failure modes are invisible. Named 2026-08-22 while reviewing CFL memory-core v0 for G-2.
created: 2026-08-22
kind: concept
---

# A one-sitting acceptance measures duration zero, and that is where duration-dependent failure is invisible

## 1. The measurement that named it

`[measured 2026-08-22 14:15–14:16 CDT]` Reviewing CFL's memory-core v0 against gate G-2
("Jon reacts to the working system, one sitting"), this trunk ran the pack's own
consolidation tool against its own 17 real records, in a scratch copy.

| run | `--as-of` | records | merge | decay | promote | `INDEX-tier0.md` |
|---|---|---|---|---|---|---|
| 1 | 2026-08-22 (today) | 17 | 0 | **0** | 0 | not created |
| 2 | 2026-09-21 (+30 d) | 18 | 0 | **18** | 0 | not created |

Same code, same records, same exit 0. **At age zero the report reads `0/0/0` and looks
clean. At age thirty days the same code decays every record in the store.** Nothing about
run 1 hints at run 2.

The mechanism, read rather than inferred: decay fires at `age >= 14 days AND uncited`;
promotion requires a record cited by two or more others; and no barrier template writes
citations. So the steady state is universal decay, zero promotion, and an index that
never comes into existence — none of which is observable on the day the system is built.

## 2. The generalisation

**An acceptance sitting is a point estimate at t=0.** Any property whose failure requires
elapsed time — decay, staleness, index growth against a cap, cache invalidation, retention
sweeps, credential expiry, log rotation, a queue that only backs up under sustained load —
is *guaranteed* to pass that sitting regardless of whether it works.

This is not a criticism of acceptance sittings. It is a statement about what they can
measure. A sitting measures **shape**. It cannot measure **behaviour at duration**, and a
reviewer who treats a clean sitting as evidence about duration has confused the two.

The actuarial form is familiar: this is a reserve question. Nobody would accept a
development triangle's first diagonal as evidence about ultimate. The first diagonal is
real, measured, and clean, and it says almost nothing about tail behaviour. **A system at
duration zero has no diagonal at all.**

## 3. What to do instead — and it is cheap

The instinct is to ask for another gate. That is usually the wrong answer, because the
scarce resource is the reviewer's attention, and a second sitting still measures a point.

**The fix is a time-shifted rehearsal, presented inside the sitting that was already
scheduled.** Where a tool takes a clock parameter, run it at t+30d and t+90d against the
real store and put the outputs in front of the reviewer as exhibits. Two commands. Zero
additional attention. It converts an unobservable property into something the reviewer can
look at while accepting.

Where a tool takes no clock parameter, that is itself the finding: **a duration-dependent
system with no injectable clock cannot be rehearsed, and cannot honestly be accepted on a
sitting.** Adding the parameter is the smallest fix, and it is smaller than a gate.

## 4. The reviewer's rule this yields

> Before accepting on a sitting, enumerate which of the system's failure modes require
> elapsed time to appear. For each one, either rehearse it with a shifted clock and show
> the output, or state in the acceptance record that it was not measured. **An
> unrehearsable duration failure is a disclosure, never a pass.**

The disclosure half matters as much as the rehearsal half. This trunk's standing method
rule — *a qualified statement reported as unqualified is this program's most repeated
error* — applies directly: "the acceptance sitting passed" is a qualified statement, and
the qualifier is *at duration zero*.

## 5. Limits of this page

`[measured]` The table in §1 is one system, one tool, two clock offsets. The
generalisation in §2 is reasoning, not measurement, and is offered as such. The page does
not claim that every one-sitting acceptance is defective — only that a sitting is silent
about duration, and that silence has repeatedly been read as a pass.

Related: [[outbox-membership-is-not-delivery]] — the same shape one layer down. A healthy
tick over a quiet day and a healthy tick over twelve stuck letters are the same bytes; a
clean consolidation at age zero and a clean consolidation over a healthy store are the
same report. **In both cases the instrument is honest and the reader supplies the false
conclusion.**
