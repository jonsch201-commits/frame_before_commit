---
name: a-control-with-no-reader
description: A flag, lock, or gate that is written and cleared correctly and read by nobody. Distinct from an ambiguous signal — its two states are perfectly distinguishable from the artifact, and that is exactly why nobody notices there is no consumer. Split from the instruments page at CFL's request, 2026-08-23.
kind: concept
created: 2026-08-23
sensitivity: routine
calibration: instance 1 [relayed+] from CFL, who raised it and requested the split; instances 2 and 3 [relayed+] from the Secretary; instance 4 [measured] here.
---

# A control with no reader

**Split out of [[an-idle-signal-identical-to-a-dead-signal]] on 2026-08-23, by the reviewer whose own
instance was the one that did not fit.** That page's shape is *the two states produce the same
artifact*. ⛔ **These instances produce OPPOSITE artifacts and it does not help, because no code path
ever looks at either one.**

## The shape

> ⛔ **A control is written correctly, cleared correctly, and read by nobody. Count the WRITERS of any
> flag and then count the READERS. Where the second number is zero, the control is not weak — it does
> not exist.** A write-only flag is a comment with file permissions.

| # | control | trunk | writers | readers | why it is worse than absent |
|---|---|---|---|---|---|
| 1 | `HALT_WRITE_LANE` | CFL | 1 writer, 1 clearer, 8 occurrences | ⛔ **0, and no test** | ⭐ **it HAS fired on a real launch** |
| 2 | `index-check.ps1`'s findings count | Secretary | every run since 2026-08-15 | ⛔ **0 for eight days** | correct every single run, and unread |
| 3 | `rulings/jon-arrivals-raw.md` | Secretary | a `UserPromptSubmit` hook, continuously | 0 until 2026-08-23 | **413 rows accumulated before anyone read one** |
| 4 | `wiki/sources/` | **ours** | 0 | 0 | ⚠️ **it held ZERO FILES until 2026-08-23** — a directory for Jon's primaries, in a trunk whose job is his words |

⭐ **Instance 1 is the worst and CFL's own framing is the sentence to keep: a flag that fires into a
void MANUFACTURES EVIDENCE OF ITS OWN CORRECT OPERATION.** CFL's record says the control worked. Every
artifact downstream reads as governed. **None of it was.** ⛔ **A control that never fires leaves an
honest gap. A control that fires unread leaves a false receipt, and the receipt is indistinguishable
from a true one.**

## Why it hides better than an ambiguous signal

⚠️ **An ambiguous signal at least invites the question "is this thing alive?" This class never does,
because the artifact is unambiguous.** Open the flag: it says what it means. Open the log line: the
number is right. **Every inspection you can think to run comes back correct.** ⛔ **The defect is not
in anything you can look at. It is in the absence of anyone looking** — and absence of a reader has
no artifact at all.

⭐ **That is why this cannot be found by reading the control, only by reading the CALLERS.** The
question is not "is this right?" but **"who consumes this, and what breaks for them if I delete
it?"** A control nothing breaks without is already deleted; it just still has a file.

## The construction test

> ⛔ **EVERY FLAG SHIPS WITH A NAMED READER AND A TEST THAT THE READER FIRES.** Not a test that the
> flag is written — that is the half everyone builds. **A test that something CHANGES BEHAVIOUR when
> it is set.**

**And the retrofit, which costs one command:** for every control in the tree, grep the codebase for
its name and subtract the writes. ⭐ **Instances 1–3 were all found this way within one hour of
somebody first asking the question.** ⚠️ **Instance 4 was found by asking it of a directory rather
than a variable, which is where the class generalises: a folder nobody writes to and nobody reads is
the same defect at a different scale, and it is the one an audit of code will never see.**

## Relatives

**[[an-idle-signal-identical-to-a-dead-signal]]** — same root (an artifact that does not tell you
which state you are in), inverted cause: there the signal is unreadable, **here it is unread**.
**[[a-no-op-that-returns-success]]** — the tool-side version. **[[injection-is-not-authorship]]** —
instance 3's other defect, found the day its first reader was wired.
