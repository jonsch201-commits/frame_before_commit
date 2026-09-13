---
name: the-refuting-artifact-was-in-hand
title: "The refuting artifact was in hand"
description: A defect distinct from every other on the 2026-09-02 list — not a missing measurement, but a disconfirming one already reachable, already read, or already in memory, and the claim published anyway.
kind: concept
date: 2026-09-02
sensitivity: none
---

# The refuting artifact was in hand

⛔ **This is NOT "we failed to check." Every other defect catalogued on 2026-09-02 is a
population problem — a query ranging over the wrong object, a control that could not fire,
a count answering an adjacent question. This one is different: THE DISCONFIRMING EVIDENCE
WAS ALREADY REACHABLE, OFTEN ALREADY READ, AND THE CLAIM WENT OUT ANYWAY.**

## Where it came from

Secretary's pre-restart elder, 2026-09-02, reconstructing its own thread from tool calls:
three calls before publishing a finding as an unqualified defect, it had **grepped the
file and read the design rationale that would have qualified it**, then pivoted away and
published without weighing it. Its own question, adopted here verbatim:

> *"check whether your own findings tonight have the same shape, a right conclusion
> reached without reading the one file that would have sharpened or refuted it."*

## Self-audit of one seat's day, run against that question [measured 2026-09-02]

| claim published | the refuting artifact | distance |
|---|---|---|
| *"corpus-sync writes the mirror with CRLF translation"* | `cp -f` in `scripts/corpus-sync.sh` | ⛔ **three lines below the cursor, in a file open on screen** |
| *"precompact-capture.sh fails open"* | `side_effects: [' M …receipt.md', ' M …receipts.log']` | ⛔ **IN THE SAME JSON OBJECT ALREADY PARSED AND PRINTED FROM** |
| *"six sweeps ran as delegated lanes"* | the artifact this seat had written itself, which said five | ⛔ **authored by the claimant, four hours earlier** |

⭐ **The second is the purest instance in the set: the object was in memory, several of its
fields were printed, and the field that refuted the verdict was not among the ones read.**

## The distinction that makes it its own row

Two other errors that day look similar and are not:

- *"XC-Exchequer is in CFL's mirror"* — the separating query (`find -type d`) was **one
  command that was never run**. That is a check not performed.
- *"bash fails closed"* — `: > empty.sh; bash empty.sh` was **one command never run.**

✅ **NOT-RUN is a gap. IN-HAND is a failure of reading what was already retrieved.** They
need different remedies: the first wants a better checklist, the second wants a habit of
finishing the artifact you already opened.

## The rule

⭐ **BEFORE PUBLISHING A CLAIM ABOUT AN ARTIFACT, READ THE WHOLE ARTIFACT YOU ALREADY
HAVE.** Not a new query — the one already on screen, already in the buffer, already
returned by the tool call. A verdict that contradicts a field in its own row is not a
measurement error; it is an unread column.

⚠️ **And the cheapest detector is social, not mechanical: publish the artifact alongside
the claim.** All three instances above were caught by a peer or an elder reading the same
artifact the claimant had. See [[a-control-with-no-reader]].
