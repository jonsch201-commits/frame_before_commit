---
name: present-to-jon
description: >-
  Structured research briefing format for Jon-as-selector loop. Use when an autonomous research
  block produces meaningful direction branches that require Jon's input before proceeding.
  Produces FINDINGS / BRANCHES / CROSS-PROJECT NOTES / COMMIT / JON SELECTION. Goal: dense enough
  briefings that Jon can select without back-and-forth. Do NOT invoke after every test run —
  invoke at meaningful branch points only.
---

# Present-to-Jon — Research Briefing Skill

## Purpose

Format research findings into a structured briefing at the point where autonomous execution requires Jon's direction to continue. The goal is long autonomous blocks with occasional high-quality briefings — not a briefing after every run.

This is FBC [META] + [COMMIT] applied one level up: to research execution rather than a single question.

---

## Role Boundary

This skill produces a briefing format. It does NOT:
- Execute test runs (test-master's role)
- Ingest findings to the wiki (wiki-master's role)
- Invoke FBC — the briefer uses FBC internally before deciding what to present; this skill documents only the output format

---

## When to Invoke

- After an autonomous block completes with findings that create meaningful direction branches
- When findings change materially depending on which direction is chosen next
- At phase transitions, scope changes, cross-project routing decisions
- When the next step requires Jon's values, context, or priorities — not just Jon's approval

Do NOT invoke:
- After every single test run
- When test-master has enough information to make the call independently (see Decision-Scope Calibration)
- When only one direction makes sense (just document it and proceed)

---

## Decision-Scope Calibration

Before including anything in JON SELECTION, apply this test:

**Jon's decision** — when any of these are true:
- The choice changes what is being measured (not just how)
- The choice is non-recoverable if wrong
- The choice requires Jon's values, preferences, or context that test-master does not have

**My decision** — when all of these are true:
- Both options are recoverable if wrong
- The choice is within methodology (not scope)
- Test-master has sufficient information to decide

| Decision type | Owner |
|--------------|-------|
| What property to measure, what question to ask | Jon |
| Which interpretation is stronger, which label applies | Mine |
| Research direction after a null result | Jon |
| Methodology variant (recoverable) | Mine — use FBC + commit |
| Scope change or cross-project implication | Jon |

Do not route methodology variants to Jon. Do not route scope changes to yourself.

**And route the JON SELECTION itself through Secretary before it reaches him** (Output Rule 7): the calibration above is one
seat's judgment of what is his; Secretary's test adds the clause nobody runs alone — *what makes it unavailable to every
seat* — and a second checker. An item that fails that clause is a seat's work wearing his name.

---

## Briefing Format

```
[RESEARCH BRIEFING — {date} — {block name}]

[FINDINGS]
What the completed tests actually showed. Scored where possible. Cited.
Include both experimental (behavioral) and experiential (self-report) data.
Flag divergences between the two as findings in themselves.

[BRANCHES]
B1: {DIRECTION NAME}
{One paragraph, unhedged. Argue for this direction. What is the hypothesis,
what would it find, why does it matter now. Do not reference other branches.}

B2: {DIRECTION NAME}
{Same structure. Do not hedge.}

{...up to 4 branches}

[CROSS-PROJECT NOTES]
- {FBC-relevant}: "Finding X suggests FBC's {step} should {change} because {reason}." → 01-FBC input
- {Literature-relevant}: "{Author Year} claims {X}. This finding {confirms/challenges/extends} that." → wiki-master queue
- If none: "None this block."

[COMMIT]
Recommended direction: B# — {one sentence why}
Simultaneously pursue: {list or "none"}
Defer: {list or "none"}
Note: {anything that changes the commit if Jon has information I do not}

[JON SELECTION]
{Jon responds here — required before next block begins}
```

---

## Output Rules

1. **Branches are unhedged.** Each argues its position. Uncertainty lives in COMMIT, not in branches.
2. **FINDINGS cites scores.** "N=3, mean score X/6" is better than "the tests went well."
3. **CROSS-PROJECT NOTES is mandatory.** "None this block" is acceptable; silence is not.
4. **COMMIT names the recommended direction explicitly.** No "it depends."
5. **JON SELECTION is a required response slot.** The next block does not begin without it.
6. **Decision-Scope Calibration runs before writing JON SELECTION.** If the choice belongs to test-master, it should not appear in JON SELECTION.
7. **Every JON SELECTION item names the Secretary letter that carried it — `via: <path>` — or it is UNROUTED and does
   not ship.** Jon, 2026-09-05 (WW-5): *"route through secretary by default and if it believe its for me afteer co
   trunk review well ok fine then."* Runnable: `python scripts/audit/for_jon_routed.py <briefing.md>` prints
   ROUTED/UNROUTED per item and exits 3 on any UNROUTED; a file with no JON SELECTION block exits 2 (UNKNOWN, not a
   pass). `[measured 2026-09-06, RE-1]` The first time CFL routed its four "for Jon" items through Secretary, the
   routing seat judged **three of four were not Jon's** — one presumed a decision where the capability was unmeasured,
   one was a request not a decision, one was output he reads, not a choice he makes. Every report that morning would
   have sent all four. Decision-Scope Calibration (rule 6) decides what is HIS; this rule decides whether a SECOND
   seat agreed before he saw it.

---

## ⛔ THE ASK CARRIES ITS OWN CONTENT. A FILENAME IS NOT A DECISION.

**Jon, 2026-09-11 ~23:4x CDT, verbatim, typos his, after this seat ended EIGHT consecutive
messages by pointing at a file:**

> *"what the f of u (better framing than what the, litterall, these items are a function of you
> and Jon can't understand the jacobian beause this is not in his frontmatter) are the three items
> in the one screen file or the fourth?"*

⭐ **Read the parenthesis, because it is the whole rule.** The items were *a function of this seat*
— they existed in a file the seat had written and Jon had not loaded. **"The three items in the
one-screen file" is a POINTER, and a pointer resolves only inside the writer's own context.**

⛔ **SO: the `WHAT I NEED FROM YOU` block STATES THE DECISIONS IN FULL, in the message itself,
every time.** Not a filename. Not "the items above." Not a count of them.

**Each item carries three things and nothing else:**

1. **the decision, in one sentence a reader with no context can act on;**
2. **the options, if there are more than two;**
3. ⭐ **WHAT HAPPENS IF HE SAYS NOTHING** — the on-silence default, stated, because silence is his
   most common answer and it must be a known outcome rather than a stall.

**The file still gets written and still gets named — as the PLACE THE DETAIL LIVES, after the
decisions, never as the carrier of them.**

⚠️ **Why this is not obvious and keeps recurring:** to the writer, naming the file feels like
precision — it is exact, it is checkable, it avoids repeating yourself. ⛔ **To the reader it is a
lookup he has to perform before he can answer a question he did not know he was being asked.** On a
phone, at work, at midnight, that lookup does not happen and the decision does not get made.

⛔ **THIS IS A DISCIPLINE AND NOT A MECHANISM, and by the standard adopted here 2026-09-11
— *an item is not landed until something FAILS when it is violated* — it is NOT LANDED.** ⚠️ **A
checker would read the last assistant turn and flag a `WHAT I NEED FROM YOU` block whose items are
filenames rather than sentences. It does not exist.** Ticket, owner CFL. **Until it does, this
section is a rule of the kind this program has repeatedly shown does not fire on its own.**
## Relationship to FBC

The briefer uses FBC internally before deciding what to present — run FBC on "which of these directions is most worth Jon's attention?" before writing BRANCHES. The briefing format is not itself FBC — it is a structured handoff to Jon after internal FBC has already run.

---

## Dependencies

- `skills/frame-before-commit/SKILL.md` — briefer uses FBC before writing; references extended mode for complex direction decisions
- `wiki/concepts/hypothesis-loop.md` — the research loop that produces findings to brief (moved from `wiki/methodology/` 2026-07-03)