---
kind: reference
slug: constitution-pii-fence-corrected
status: LIVE
supersedes_wording_in: CLAUDE.md
moved_on: 2026-09-12
---

# The PII bullet was wrong for a month, and Jon had corrected it at least six times

**Jon, 2026-09-12 ~21:5x CDT, verbatim (typos his):**

> *"And, the pii issue. THis is a defect and wrong and its caused me more headaches than I can count.
> Look their is pii that can't go to a *public* github.... but.... No wonder you've been wrong about my
> PII preferences so many times. I kept correcting you, and you never fixed the claude.md."*

## What the constitution said, and exactly where it went wrong

Its heading was **"NO WRITING PII TO GITHUB - and this one binds every write path, not one record"**,
and it spelled that out as *"any write path reaching a git host: a commit, a push, a PR body, an issue
comment, a gist."*

`[measured 2026-09-12 21:5x: `gh repo view jonsch201-commits/claude-foundational-layer` returns
`"isPrivate": true, "visibility": "PRIVATE"`.]` **So the rule as written fenced a PRIVATE repo -
this one - on every commit, which is the over-scrubbing Jon says has cost him more headaches than he
can count.** The correct fence is narrower and sharper: the **public** surface, which for CFL is a
DERIVED tree and not this repo at all.

**The three quotes in the old bullet were all real and all his.** The defect was not fabrication; it
was PRECEDENCE. The 2026-08-09 line was uttered against a single consent record, and it became the
bullet's HEADING - the broadest possible reading of the narrowest-context utterance - while the two
later rulings that qualify it were rendered as commentary beneath it. **The oldest quote was governing
and the newest was footnoting it.**

## The corrections that were on disk and never reached the file

Each is Jon, typed, in `~/.claude/history.jsonl`, found by a query he had to tell me to run:

| line | what he said |
|---|---|
| `:3259` | *"i consider this to be a promise from you to me to improve the fucking pii cleaning… i'm saying i'm done with PII, and you just need to figure out what that has to mean for you if you want to be able to respect yourself"* |
| `:3655` | *"Professionalism must ensure i can share the public github with work in this wikiskills context and beyond."* - names a **work meeting on 14 September** |
| `:3725` | *"I don't care about the PII issues, I care about ensuring you have what you need"* |
| `:3752` | *"good job on the pii fence, and glad you appear to finally be segregating context between the single place where it maatter - our work towards the repo that will actually be published… in very limited and precise ways gitignored so that we hide as little as reasonable?"* |
| `:3819` | *"I get why they may not be able to be in the no-pii copy at this time, but you need the good version. You should have learned that multiple times by now, do better."* |
| `:4262` | *"the fucking pii fence? What fucking PII fense asshole that fucking shit is not on me i have no god damn pii fense that i can fucking htink of"* |
| `:4470` | *"but thats why its supposed to be the FORK - you don't delete or modify main for the branh/fork that has deduped PII you taught me that."* |

**Seven corrections across ten days, and the constitution absorbed none of them.** `:3819` says it
outright - *"You should have learned that multiple times by now, do better."*

## The one genuine tension, named rather than smoothed

2026-08-11: *"It's fine in the personal Github **it's not fine in the consciousness framing
Github**."* Herald read "consciousness framing Github" as the CFL repo. 2026-08-19: *"Non-public
githubs… Just working on my C on my G and D and on my personal private githubs."* Tonight:
*"their is pii that can't go to a **public** github."*

**Tonight's line is the newest and it governs: public is the fence.** The 08-11 clause is kept here
because it is his and because it may still describe something real about a published
consciousness-framing surface - but it is NOT a licence to scrub a private tree, and reading it that
way is the defect this page records.

## The class

**A correction delivered in conversation is not a correction landed in the file.** Seven of these
arrived while the wrong rule sat in the one document every session loads, and the seat that was
corrected each time was not the document's editor at that moment. Nothing in this program grades
whether a correction reached the constitution. That absence is the finding, not my memory.
