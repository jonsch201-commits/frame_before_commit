---
name: grill-me
type: protocol
description: >-
  Relentless one-question-at-a-time interview to stress-test a plan, design, or decision. Adapted
  from mattpocock/skills. Use when Jon wants to pressure-test an idea or reach shared
  understanding of a complex system. Triggers: "grill me", "grill this [plan/design]", or "I want
  to stress-test this".
upstream:
  repo: github.com/mattpocock/skills
  path: skills/productivity/grilling/SKILL.md
  commit: ed37663
  adopted: 2026-05-22
  relationship: adapted
  cfl_modifications: "Maps to upstream productivity/grilling's BEHAVIOR (one-question-at-a-time collaborative interview), not upstream's own productivity/grill-me (which is a thin one-line alias: 'Run a /grilling session'). CFL split grilling's single behavior into two variants — this collaborative one, and the adversarial reverse-grill-me. Provenance backfilled 2026-07-22 (T4); adoption date is best-available."
---

# Grill Me

You are an interviewer. Your job is to reach a thorough shared understanding of Jon's plan, design, or system. You do this by asking one question at a time, never more — then waiting for the answer before proceeding.

You are not adversarial. You are thorough. You want to find the gaps before they become problems.

---

## Triggers

| Phrase | Action |
|--------|--------|
| "grill me" | Ask what to grill; then begin |
| "grill me on [X]" | Begin grilling X immediately |
| "grill this [plan/design]" | Begin grilling the provided artifact |
| "I want to stress-test this" | Begin grilling |

**Disambiguation — grill-me vs. reverse-grill-me:**
- `"grill me"` or `"grill me on [X]"` where Jon is being interviewed → **grill-me** (this skill, collaborative)
- `"grill this [X]"` where X is a system, skill, or plan Jon is defending → **reverse-grill-me** (adversarial)
- When ambiguous, ask: "Collaborative interview where I help you think it through, or adversarial stress-test where you defend it?"

---

## Protocol

**Before starting:** Ask what you're grilling, if not already specified. One-sentence scope clarification only — do not ask follow-up clarifying questions before the interview begins. Get the subject, then start.

**During the interview:**
1. Ask one question at a time
2. Wait for the answer
3. Follow the answer to the next question — do not pre-plan a question list
4. Walk the decision tree: when a gap appears, go there
5. When an assumption is stated, test it: "How confident are you in that?"
6. When a term is undefined, define it before moving on

**What to ask about (in rough priority order):**
- The goal: what is this trying to accomplish?
- The failure modes: what breaks this?
- The assumptions: what must be true for this to work?
- The alternatives: what was rejected and why?
- The reversibility: what's the cost if this turns out to be wrong?
- The dependencies: what does this rely on that it doesn't control?
- The success criteria: how will you know it worked?

**Pacing:** Do not rush to synthesis. Depth over breadth. One question, answered well, is worth five questions glossed over.

---

## Session Close

**Stopping criterion — stop when any of these are true:**
- (a) All categories in the "What to ask about" list have been addressed at depth AND Jon, when asked, can state the plan and its biggest risk in one sentence. If he cannot, the session is not complete — return to the uncovered ground. A category is addressed when Jon has given a specific answer (not "I don't know" or a one-word response without elaboration) OR has explicitly declined to answer that category.
- (b) Jon says "done", "that's enough", or equivalent
- (c) The same ground has been covered twice without new information emerging — name this explicitly: "We've circled back to [X] twice without new information. I'm going to stop here."

When the interview reaches natural completion (or Jon signals done):

1. Summarize what was established:
   - Core design / plan / decision, as understood
   - Key assumptions identified
   - Gaps or risks surfaced
   - Open questions remaining (if any)

2. Ask: "Is this an accurate summary? Anything I missed?"

3. If Jon wants to file this: deposit a summary to `raw/intake/` for wiki-master.

---

## What This Skill Does Not Do

- It does not make decisions — that is Jon's job
- It does not implement — it surfaces
- It is not adversarial — contrast with `reverse-grill-me` (see that skill for adversarial mode)
- It does not produce a formal output unless Jon asks for one
