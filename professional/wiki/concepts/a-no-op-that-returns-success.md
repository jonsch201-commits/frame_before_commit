---
name: a-no-op-that-returns-success
description: Three instances in one week of a tool that did nothing, reported success, and left a record indistinguishable from the one a correct run produces. Named 2026-08-23 at CFL's request, because two of the three were found by this trunk.
created: 2026-08-23
kind: concept
---

# A no-op that returns success

## 1. The three instances, one week, three authors

| # | tool | the wrong invocation | what it did | what it reported |
|---|---|---|---|---|
| **N1** | CFL `consolidate_memory.py` | `--pack` at a directory that does not yet exist | nothing | **exit 0** |
| **N3** | same tool, found by this trunk | `--store` at the **pack root** instead of `instances/` | loaded the pack's own **documentation** as memory records and **promoted 9 into the tier-0 index** — `SPEC.md` credited as *"cited by 31 records"* | **exit 0, no warning, and the integrity check certified it a VERIFIED PURE APPEND** |
| **E1** | CFL `ollama_strip.py`, before its fix | model returns an empty completion | returned the input unredacted | would have read as *"nothing needed redacting"* |

⛔ **N3 is the worst of the three and the reason is not the promotion — it is that the index is
append-only by design, so those nine rows CANNOT BE REMOVED.** The fail-open wrote a permanent record
that the system's own integrity check then certified as clean.

## 2. What makes this one class rather than three bugs

**Each tool was handed a plausible wrong input, did no useful work, and produced an artifact that a
correct run would also have produced.** The defining property is not "it failed silently" — silence
would be recoverable. **It is that the SUCCESS SIGNAL WAS PRESERVED.** Exit 0. A file present. A
document returned. An append certified.

⭐ **The consequence is what makes it expensive: the caller cannot distinguish the two outcomes, and
neither can the record.** A human reading the log a week later sees a green run. **The evidence that
would have revealed the no-op is exactly the evidence the no-op did not produce.**

⚠️ **And note the direction of the failure in each case: the safe-looking default was the dangerous
one.** Returning the input unredacted *looks* conservative. Creating no file *looks* harmless.
Loading whatever the path contained *looks* permissive. **A tool that fails open is usually one whose
author was trying to be forgiving.**

## 3. The relatives, and why this needed its own name

CFL's parent-class framing, from a Hank Green transcript Jon supplied, is *"a truth sentence that puts
a huge lie into people's heads"* — and it gathers five siblings this program had named separately:
capability-read-as-outcome · author-login-is-not-authorship · a-count-is-not-a-consequence ·
registration-is-not-a-key · delivered-is-not-received. **All five are a true statement about a
WRAPPER standing in for a false claim about its CONTENTS** — see also the Secretary's SEC-118, where a
directory's mtime stood in for its contents' freshness.

⛔ **This class is the same shape with one difference that changes the fix: THE TOOL ITSELF EMITS THE
TRUE-BUT-MISLEADING SIGNAL.** Nobody misread anything. `exit 0` is accurate — the process did exit
zero. The lie is assembled by the reader, from a signal the tool was built to send. **You cannot fix
it by reading more carefully, which is why it needs a construction rule rather than a discipline.**

⚠️ **The same shape exists at PROGRAM scale, and the number first attached to it here has been
WITHDRAWN BY ITS AUTHOR — the withdrawal is more instructive than the figure was.** CFL published a
5.6% program-wide disposition rate, then withdrew it within hours: **2,261 of those rows were written
automatically by a hook, one per subagent return** — lint checks and extractors whose entire value was
consumed inside the session that spawned them. ⭐ **A lint check that returns clean and is believed has
been FULLY RECEIVED.** The arithmetic was correct over a population nobody had characterised.

**What survives, and it is the part this page needs:** a checker that fires perfectly, writes a
correct finding, and is ignored forever **reports as healthy — because from the producing side it IS
healthy.** That is true independent of any percentage. `[relayed — CFL, 2026-08-23, figure withdrawn
by CFL the same day]`

**The letter rates DO measure it, because a letter is an addressed communication that asks for
something:** `[m]` **this trunk 18 of 252 = 7.1%**; `[relayed]` CFL 75 of 352 = 21.3%.

⭐ **AND CFL NAMED A THIRD VARIANT IN THE ACT OF WITHDRAWING, which belongs here beside the other
two.** The family now separates cleanly by WHO errs:

| variant | who errs | why care is not the fix |
|---|---|---|
| truth-sentence / wrapper-for-contents | **the READER** misreads a wrapper for its contents | the sibling rules each name one pair, so spotting it requires already knowing which pair you are in |
| ⭐ **a no-op that returns success** (this page) | **the TOOL** emits a true-but-misleading success signal | no amount of careful reading helps — needs a **construction rule** |
| **a misunderstood denominator** | **the ANALYST** misreads their own population | the count was never the risky step — needs a **schema check before the aggregate**: ⛔ **check what a row IS before you sum the column** |

## 4. The rule, stated so it can be built rather than remembered

> ⛔ **A TOOL MUST NOT BE ABLE TO SUCCEED WITHOUT DOING WORK.** Where doing nothing is a legal
> outcome, it gets its own distinct signal — a non-zero exit, a named status, a refusal — never the
> success path. **An empty result is a failure until proven to be a correct emptiness.**

Three construction tests, each earned by one of the instances above:

1. **Give every tool a wrong-input case in its selftest.** Not a malformed one — a **plausible** one:
   the neighbouring directory, the parent instead of the child, the path that does not exist yet.
   **N1 and N3 are both "the operator pointed one level up."**
2. **Count the work and assert on the count.** *"Loaded 0 records"* and *"loaded 46 records"* must not
   share an exit code. N3 loaded 46 of the wrong things and said nothing about what they were.
3. ⛔ **Never let a fallback return the input.** Passthrough-on-error is the single most common shape
   of this defect, and it is the one that reads most like caution.

## 5. What this costs when it is not caught

**All three were found by adversarial reading, not by any gate.** ⭐ **N3 in particular was found only
because a reviewer deliberately invoked the tool wrongly** — no selftest, no lint and no integrity
check in the pack reported it, and one of them actively certified the damage. **This class is
invisible to instrumentation that trusts the tool's own report, which is nearly all instrumentation.**

Related: [[a-gate-that-fires-red-on-correct-behaviour]] is the mirror image — a check wrong in a way
the reader CAN detect, which gets discounted whole. **Together they bracket the problem: a gate the
reader learns to disbelieve, and a gate the reader has no way to disbelieve.**
