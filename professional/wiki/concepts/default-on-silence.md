---
title: "Default-on-silence — every ask names what happens if nobody answers, and the waiter states it"
slug: default-on-silence
kind: concept
date: 2026-09-12
written: "2026-09-12 20:1x CDT"
status: LIVE
description: "The row-completeness rule this trunk has applied since 08-18 without a page: an ask, a gate, or a letter carries the outcome of silence and a clock; the default is stated by the party who waits, not granted by the party waited on."
---

# Default-on-silence

**The rule.** Anything that waits on someone — a row on Jon's review surface, a letter to a sibling,
a ticket with an owner — carries two fields: what happens if no answer comes, and by when. A row
without them is a defect in the row, not a patience problem in the reader.

**Grounding, this trunk's log, verbatim:**

> *no coordinator waits on another without a stated default-on-silence and a deadline* — **and THE
> DEFAULT IS STATED BY THE WAITER, NOT GRANTED BY THE WAITED-ON. A waiter can always state its own; a
> blocker cannot always know it is one.**
> — `wiki/log.md:4450–4452`, Herald's mechanism adopted with this trunk's amendment

> *J4 conflates an INPUT he holds with an ACT only he can perform, and they have opposite
> default-on-silence shapes — an input can be defaulted and stated; an act can only be worked around.*
> — `wiki/log.md:4593–4595`

> *CFL routed it as `FOR-JON-REVIEW`: ninety seconds, one ask, default-on-silence-nothing-changes.*
> *"Protect his context" does not mean fewer asks. It means asks priced correctly.*
> — `wiki/log.md:3550–3552`

**The two shapes, because they are not the same field:**

| what is waited for | default-on-silence shape | example |
|---|---|---|
| an **input** the other party holds (a number, a preference, a wording) | a stated default runs at the clock; the record says *"default ran"* | PR 4's six questions, defaults executed 2026-09-12 12:0x (`00-INDEX.md` row 12) |
| an **act** only the other party can perform (a push, a signature, a credential) | no default can run; the waiter works around or waits, and says which | the public push (Jon's), Soul's second signature (worked around by holding DRAFT) |

**A gate is a reserved class:** its default executes nothing. Silence on a gate leaves the world
unchanged and says so (*"on silence nothing publishes"*). Silence on an input runs the stated default.
Confusing the two is the J4 pushback above.

**Where it lives in this tree:** every row of `exchange/FOR-JON-REVIEW/00-INDEX.md` carries a
`default-on-silence` column; every letter in `exchange/outbox/` carries an `on_silence:` frontmatter
field; lint C8 grades budget rows for a deadline. **What does not exist:** a check that a tracker row
names its default. Detector owed, not claimed.

**Why a page now:** dream sweep (b) of 2026-09-12 found the term in 8 corpus files and 5 log passages
with no page to point at — a rule applied for 25 days as prose. Related: [[grounding-principles]],
[[a-control-with-no-reader]], [[wikiskill-and-the-retrieval-half-we-own]] (query-before-build is CFL's page, `wiki/concepts/query-before-build.md` in its tree).
