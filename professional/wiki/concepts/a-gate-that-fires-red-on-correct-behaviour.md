---
name: a-gate-that-fires-red-on-correct-behaviour
description: A gate that reports failure when the actor did the right thing certifies exactly as much as a gate that times out — nothing — because both teach the seat to route around the result. Named 2026-08-23 fixing lint.sh C9's runtime and finding a worse defect underneath it.
created: 2026-08-23
kind: concept
---

# A gate that fires red on correct behaviour is the same end state as a gate that does not run

## 1. The two measurements, one hour apart

`[measured 2026-08-22]` `scripts/lint.sh` was **killed at exit 143** inside a two-minute budget.
Cause: check C9 walked **71 outbox letters × 4 sibling trees = 284 stat calls across a Google Drive
mount.** That was ticketed as T-A with the sentence *a gate that cannot finish inside a headless
seat's default timeout is a gate that does not run.*

`[measured 2026-08-23]` The runtime fix — list each sibling inbound **once** into memory, match
in-process, four directory reads instead of 284 network stats — took the run from **killed at 120 s
to green in 31 s** with grading semantics untouched.

⭐ **And then the working gate immediately went red on a letter that had been correctly delivered.**
C9 required every outbox letter to be present in **all four** sibling inbounds regardless of who the
letter was addressed to. A letter addressed to one trunk, delivered to that trunk, verified by
`cmp`, graded **FAIL**.

## 2. Why the second defect is worse than the first

**T-A was visible.** A killed process announces itself; exit 143 cannot be mistaken for a pass.

⛔ **A false red is invisible in the direction that matters.** The seat reads the failure, knows the
letter was delivered because it delivered it, and concludes *the gate is wrong here.* That
conclusion is correct, and it is the beginning of the failure: **the next red is read the same
way.** A gate that must be interpreted before it is believed has been demoted to advice.

**Both defects converge on the same number. A timed-out gate certifies nothing. A discounted gate
certifies nothing. The second one keeps printing PASS while it does it.**

## 3. The general form

> **A gate's output is only worth what its worst false verdict costs.** Runtime, scope and
> precision are not three separate quality attributes — they are three ways of arriving at a result
> the seat stops reading.

This composes with [[outbox-membership-is-not-delivery]], which built C9 in the first place: that
page established that *only the receiver's tree is delivery*. It did not say **which** receivers,
because on the day it was written every letter was addressed to all four. **A rule written against a
uniform case acquires a false-positive surface the moment the case stops being uniform** — and
nothing in the rule announces that it happened.

## 4. What the fix had to include to count

`[measured 2026-08-23]` C9 now parses addressees from the filename prefix (`pro-to-cfl-secretary-…`).
Two properties were non-negotiable:

1. ⛔ **An unparseable prefix falls back to all four trees.** The narrowing can only ever apply where
   it can be justified; uncertainty returns the strict old behaviour. A relaxation that fails open on
   ambiguity is not a fix, it is an amnesty.
2. ⛔ **Two new selftest cases** — one proving a non-addressee tree is skipped, one proving the
   **addressee's own** tree still fails. **A narrowing rule that cannot fail is an exemption wearing
   a gate's name**, and this repo's whole lint discipline is that every check is proven failable
   before it is trusted.

⚠️ **What was deliberately NOT done.** CFL reports that Jon retired Herald Wiki on 2026-08-08. That
is `[relayed]` here, not `[measured]`, and acting on it would stop a gate requiring delivery to a
trunk. **A gate is not narrowed on a relayed ruling.** Herald stays graded, the relayed retirement
is recorded in the comment beside the check, and the question went to Jon's queue. See
[[negative-claims-require-an-attempt-ledger]] for the same discipline in the other direction.
