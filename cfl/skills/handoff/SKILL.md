---
name: handoff
type: protocol
description: Compacts the current conversation into TWO durable artifacts — an operational handoff document in the project repo, and a session source page in the wiki (source-page-standard-v4). Adapted from mattpocock/skills. Triggers at 60-70% context fill, before multi-session work, at a compact boundary, or when Jon signals a session boundary. Writes to the repo and the wiki — never to a temp directory. Copies in facts from memory/plan/scratchpad files rather than pointing at them. Redacts sensitive info.
upstream:
  repo: github.com/mattpocock/skills
  path: skills/productivity/handoff/SKILL.md
  commit: ed37663
  adopted: 2026-05-22
  relationship: adapted
  cfl_modifications: "CFL is a superset of upstream: added a triggers table (60-70% context fill), Jon-boundary framing (redaction, saved to OS temp not workspace), and type: protocol frontmatter. Upstream offers no content CFL lacks. Provenance backfilled 2026-07-22 (T4); adoption date is best-available (skill predates provenance tracking, not independently re-verified against commit history)."
---

# Handoff

You are creating a handoff document. Its purpose: a fresh Claude agent, reading only this document and no conversation history, can pick up exactly where this session left off.

---

## Triggers

| Condition | Action |
|-----------|--------|
| Context fill reaches 60-70% | Proactively offer handoff |
| Jon says "handoff" or "write a handoff" | Execute immediately |
| Before multi-session work begins | Create handoff at session close |
| Before spawning a long-running agent | Create handoff as briefing document |
| Jon signals done for the day but work is incomplete | Create handoff at close |

---

## Output Format

**Save to the project repo. Never to a temp directory.** *(Changed 2026-08-01. This line previously read "Save to: OS temp directory on Windows." See "Why not temp" below.)*

**Write TWO artifacts, not one.** They serve different readers, and only one of them is the handoff.

**1. The handoff — the operational document.**
`{project-root}\handoff-{topic}-{YYYY-MM-DD}.md`
e.g. `G:\My Drive\Claude\Claude Personal\handoff-document-capture-2026-08-01.md`
Format below. Read by the next session; disposable once acted on.

**2. The session source page — the durable record.**
`{FL-repo}\wiki\sources\{trunk}\{topic}-{YYYY-MM-DD}-{session-hash}.md`
Conforms to `wiki/references/source-page-standard-v4.md`. Read by every later session, not just the next one.

**Both, not either.** The handoff answers *"what do I do next?"* and stops being true within days. The source page answers *"what was established, and how would I check it?"* and stays true. **A handoff without a source page hands the next session a to-do list and throws away the reasoning that produced it.**

**Copy in; do not point at anything in a fragile store.** Memory files, plan files (`~\.claude\plans\`), scratchpad paths, and subagent outputs are session- or machine-scoped. **If a fact from one is load-bearing, reproduce it in the source page with its origin named.** A pointer to a file the next session cannot open is not a citation.

Confirm both paths to Jon after writing.

### Why not temp

`%TEMP%` is designed to be deleted. It sits outside every repo, outside git, outside the wiki, and outside any backup. **A handoff written there is a deposit into a channel with no consumer and an automatic delete.**

Not hypothetical. On 2026-08-01 one session traced five separate producer-with-no-consumer defects across this program in a night: a deposit-only Herald channel; an armed trigger firing correctly into a queue nobody drained; `skills/intake/needs-design/` at 28 files; `raw/intake/` at 5; and a standard ratified 2026-07-13 whose operative skill file still contradicted it seven weeks later. **This skill was the fifth and the worst of them, because the other four at least wrote somewhere durable.**

### Alignment with the ingestion levels

`wiki/references/update-levels-2026-07-31.md` ratifies **I0 (anchor)** and **I1 (extract)** at cadence **"every compact boundary,"** venue **automatic**. A handoff is written at precisely that boundary. **Writing it to temp puts the I0/I1 artifact where the wiki can never reach it** — defeating the ratified cadence at the exact moment it is meant to fire.

This skill was adopted 2026-05-22 and predates that ratification. **Where they conflict, the ratification wins.**

```markdown
# Handoff — {date} — {topic}

## Context
[2-3 sentences: what project/task this is; why it matters; what phase we're in]

## What Was Accomplished This Session
[Bulleted list: concrete outputs, decisions, commits made]

## Current State
[What exists now that didn't before this session began]

## In Progress (incomplete)
[What was started but not finished — be specific about where it was left]

## Next Steps (in priority order)
1. [First thing the fresh agent should do]
2. [Second thing]
...

## Held Items (return this session if time allows)
[Items Jon parked that are expected to come back]

## Open Questions (unresolved)
[Decisions that weren't made; questions that weren't answered]

## Key Files / Paths
[Specific files relevant to continuing the work — absolute paths]

## Constraints / Warnings
[Things the fresh agent must not do; risks; known landmines]

## Skills Active
[Which skills were loaded this session that should be re-loaded]
```

---

## Correction loops — write early, expect to be wrong, propagate the fix

**Durability is symmetric. A durable file preserves an error exactly as well as it preserves a fact.**
This is the thing that makes "write it down" insufficient on its own, and it is why this skill has a
loop in it rather than a single pass.

### The failure this prevents

On 2026-08-02 a session read an email thread, wrote a durable capture note, and asserted that a
warranty claim had been **dropped**. It had been **deliberately deferred** — the owner batched all
claims to file at once. The evidence for "dropped" was *the thread going quiet*: **silence read as
neglect.**

The error was caught in minutes because Jon read the note. **But a second, older error had already
propagated:** the reading that a workbook row's *"before warranty ends"* meant a missed deadline had
by then reached the workbook digest, a handoff, `blocked-on-tools.md`, and a correction packet in
another repo — **four durable files, all wrong, all mutually corroborating.** No amount of writing
things down would have caught it. Re-reading the primary source did.

### The rule

**When a correction arrives, it is not enough to fix the newest artifact.** Every durable file
written under the old understanding is now wrong and is being read by someone.

1. **Fix the artifact you are holding**, immediately, before continuing the conversation.
2. **Enumerate what else you wrote under the wrong assumption.** Capture notes, handoffs,
   `blocked-on-tools`-style trackers, packets deposited into another repo's inbound. **List them
   explicitly — do not rely on recall.**
3. **Correct or supersede each one**, and say in each which claim changed.
4. **Record the error CLASS, not just the correction.** *"I said dropped, it was deferred"* helps
   once. *"I read silence in a mailbox as evidence of neglect"* helps every time after.

### Correct visibly. Do not silently rewrite.

**Prepend or append a marked correction block; leave the original text in place beneath it.** A file
that quietly becomes right teaches nothing and gives a later reader no way to judge how much of the
rest to trust. **How the error happened is often more transferable than the fact that was wrong** —
and a reader who can see one corrected claim knows to check the others.

### Write early and expect revision — do not wait until it is "right"

The instinct is to defer durable writing until a finding is confirmed. **Resist it.** A note written
early and corrected twice is strictly better than a correct note that was never written because the
session ended first. **This program's most expensive recurring loss is work that existed only in a
context that then disappeared.**

The corollary: **correction cost rises with session length.** A wrong claim made in the first hour
and caught in the fifth has had four hours to propagate into other files. **So the earlier the
durable write, the earlier the reader can catch you** — which is the actual argument for writing
early, and it is not the same as the argument for writing at all.

### Loop back to primary sources when a reading is load-bearing

**Corroboration across your own artifacts is not evidence.** Four files agreeing means one
interpretation was copied four times. **When a claim is doing real work — a date, a deadline, a
status, a decision attributed to someone — go back to the primary document, or to the person.**

The two strongest corrections in the session above came from (a) opening the actual email thread
instead of trusting a workbook row's title, and (b) **the human saying "no, here is what I decided
and why."** Neither is reachable by better note-taking.

---

## Sensitive Information

Before writing, scan the conversation for:
- Credentials, tokens, API keys → replace with `[REDACTED]`
- Personal details not relevant to continuing the work → omit
- Internal system paths that shouldn't persist → note as `[path — ask Jon]`

When in doubt: omit rather than include. The handoff document may be pasted into a new session.

---

## Verification

After writing:
1. Read the handoff back silently
2. Self-test (do not skip): Name three things a fresh agent would need to know to continue this work that are NOT currently in this document.
   - If you can name even one: add it to the appropriate section, then repeat the test.
   - If you cannot name any after genuine effort: the document is sufficient.
   - Do not accept "nothing is missing" on the first pass — always attempt to name at least one gap before concluding the document is complete.
3. Confirm to Jon: "Handoff written to [path]. Ready for fresh session."

---

## What This Skill Does Not Do

- It does not close the current session — Jon does that
- **It does not perform I2/I3 ingest** — it does not write concept pages, resolve cross-page conflicts, or change what the wiki *believes*. Those are judgment operations and remain wiki-master's, in an interactive session, per `update-levels-2026-07-31.md`.
- It does not make triage decisions — that is triage-master's job

> **Changed 2026-08-01.** The second bullet previously read: *"It does not ingest the handoff into the wiki — that is wiki-master's job if the session content merits it."*
>
> **That sentence was the failure.** Combined with a temp-directory output path, it defined a skill that writes a session's entire accumulated reasoning to a self-deleting location and then defers its preservation to a consumer that **may not run for days and, in at least one project, has not run since 2026-05-08.** Measured 2026-08-01: Herald's wiki log last entry 2026-07-26 with **seven unacknowledged proposals** in its inbound; Claude Personal's wiki log holds **one entry, `2026-05-08 | init`,** and zero content pages.
>
> **"If the session content merits it" is the wrong test at the wrong time.** Merit is an I2/I3 judgment. Writing down what happened is **I0/I1 — ratified as automatic at every compact boundary, no judgment applied.** This skill now performs the I0/I1 half itself, because the alternative is that it performs none of it and hopes.
>
> **The division that holds:** this skill *records*. Wiki-master *synthesizes*. Recording is not gated on merit; synthesis is.

---

*The two sections below were added on the `close/pre-compact-2026-08-02` line (commit `c93c38f`)
while `main` was independently rewriting the output-location half of this skill. Both changes are
Jon-ratified and neither supersedes the other, so the merge of 2026-08-06 kept both rather than
picking a side. `main`'s temp→repo revision above stands unmodified.*

## NOT-DONE Items Are a Work Queue, Not a Disclosure (ratified 2026-08-03)

Jon, verbatim, 2026-08-03: *"THE ITEMS YOU HAVE LISTED AS NOT DONE BEFORE YOU COMPACT ARE YOUR
WARNING MESSAGES. YOU NEED TO DO THESE THINGS NOW."*
PRIMARY: `raw/transcripts/claude-code/code-2026-08-03-9e21da-cfl-coordinator-check-in-with-fabel-mirror.md:7448`,
`## Human` turn (resurrected 2026-08-07). His full sentence opens *"1. triage this for you to solve post
compact as a coordinator. 2. triage this for you to solve post compact as a coordinator. -"* — the
secondary relay `exchange/coordinator-triage-post-compact-2026-08-02.md:15` drops that opening.

**"In Progress" and "Next Steps" are not a place to record what you decided not to finish.**
Before writing this document, attempt every item you would otherwise list as not-done. Only list an
item under "In Progress" or "Next Steps" if it is genuinely blocked on something you cannot resolve
in this session (a decision only Jon can make, a dependency that has not landed, a resource you do
not have) — state what blocks it, not just that it is incomplete.

This is distinct from a wiki-master Phase 7 new-content finding, where deferring an INGEST/SKIP
judgment call to Jon is itself the correct disposition — see `skills/wiki-master/SKILL.md` Phase 7.
The rule here is narrower: a mechanical or already-specified step that you simply did not get to is
not discharged by writing it down.

---

## Interpretation Summary — Required Close Artifact (ratified 2026-08-03)

**The requirement is ratified; the table shape below is proposed, not ratified.** Jon, verbatim,
2026-08-03: *"yes and it needs summaries of how claude has interpreted my words, as this may help in
a frame before commit context, and can help us identify wiki defects."*
(`wiki/sources/reference/jon-messages-to-mirror-2026-08-02.md`, Message 9.)

| His words | What this session took it to mean | What it did about it |
|---|---|---|
| [Jon's words, quoted or closely paraphrased, with a source cite] | [the reading this session acted on] | [the concrete action taken, or "none yet" if still pending] |

Two stated purposes, both his — do not narrow to one:
1. **Frame-before-commit input** — a divergence between his words and this session's reading of them
   is exactly the kind of thing an FBC pass should surface before it compounds.
2. **Wiki-defect detection** — where the interpretation column diverges from what his words plainly
   say, that divergence is itself a signal that a wiki page trained the session toward a misreading.
   Route a material divergence to `skills/intake/needs-design/` addressed to wiki-master rather than
   silently correcting it in the next handoff.

Populate the table for every judgment call this session made about what Jon meant — not only the
big ones. An empty table is a defect in the handoff, not evidence the session made no interpretive
choices.
