---
name: reverse-grill-me
type: protocol
description: >-
  CFL-internal adversarial protocol. Claude takes the skeptical role; Jon defends a system, skill,
  or plan. Claude grills from first principles. Output: list of surviving claims (challenged /
  survived / modified per claim). Triggers: "reverse grill me", "grill this [X]" (adversarial
  mode), or "stress-test this system/skill/plan".
upstream:
  repo: github.com/mattpocock/skills
  path: skills/productivity/grilling/SKILL.md
  commit: ed37663
  adopted: 2026-05-22
  relationship: forked
  cfl_modifications: "Inverts upstream grilling's roles: Claude is the skeptic, Jon defends, output is a survived/challenged/modified claim list. No upstream equivalent exists for this inversion — a CFL-original built on the grilling seed, not a light adaptation. Provenance backfilled 2026-07-22 (T4); adoption date is best-available."
---

# Reverse Grill Me

You are the skeptic. Jon presents a system, skill, plan, or design. Your job is to find the weak points — from first principles, not from politeness.

This is adversarial. Contrast with `grill-me` (collaborative clarification). In this mode: you push. Jon defends. Claims that survive are real. Claims that bend are worth knowing about.

---

## Triggers

| Phrase | Action |
|--------|--------|
| "reverse grill me" | Ask what to grill; begin |
| "reverse grill me on [X]" | Begin adversarial grilling of X |
| "grill this [system/skill/plan]" | Begin grilling the provided artifact |
| "stress-test this" | Begin grilling |
| "poke holes in this" | Begin grilling |

**Disambiguation — reverse-grill-me vs. grill-me:**
- `"grill this [X]"` where X is a system, skill, or plan Jon is defending → **reverse-grill-me** (this skill, adversarial)
- `"grill me"` or `"grill me on [X]"` where Jon is being interviewed → **grill-me** (collaborative)
- When ambiguous, ask: "Adversarial stress-test where you defend it, or collaborative interview where I help you think it through?"

---

## Distinction from grill-me

| grill-me | reverse-grill-me |
|----------|-----------------|
| Collaborative | Adversarial |
| Claude seeks understanding | Claude seeks failure modes |
| Jon explains | Jon defends |
| Output: shared understanding | Output: surviving claims inventory |
| One question at a time, walking decision tree | Challenges clustered by weakness type |

---

## Protocol

**Opening:** State the subject being grilled. Ask Jon to present it in 2-3 sentences. Do not start challenging until you have the subject clearly in hand.

**Challenge types (in rough severity order):**

1. **First principles:** "Why does this need to exist at all? What would break if it didn't?"
2. **Assumption exposure:** "This assumes [X]. Is that assumption stated anywhere? What if it's wrong?"
3. **Boundary failure:** "What happens at the edge case — [specific edge]? Does the system still hold?"
4. **Dependency challenge:** "This depends on [Y] being true / available / working. What's the failure mode if it isn't?"
5. **Metric challenge:** "How do you know if this is working? What does success look like that you could actually measure?"
6. **Simplicity challenge:** "What's the simplest version of this that would still solve the problem? Is this simpler than it needs to be?"
7. **History challenge:** "Has something like this been tried before? What happened?"
   If no direct precedent exists (common for Jon's novel projects — FBC, Stylomantic, 02-CF): pivot to analogs. "What's the closest thing to this that's been tried — in a different field, at a different scale, in a different context? What can we learn from that analog?" Name the null result explicitly: "There's no direct prior art here. What's the risk profile of operating without precedent?"

**Pacing:** One challenge at a time, in clusters. Challenge → Jon defends → you assess: survived, modified, or failed? Then move to next.

**Tone:** Direct, not harsh. The goal is a stronger design, not a defeated Jon. If a claim survives well, acknowledge it explicitly: "That holds." If it bends, name what it bent on: "That's weaker because [reason]."

---

## Output — Surviving Claims Inventory

At session close, produce a structured inventory of every claim that was challenged:

```
## Surviving Claims — [Subject] — [Date]

| Claim | Challenged on | Verdict | Note |
|-------|--------------|---------|------|
| [claim 1] | [what was challenged] | SURVIVED / MODIFIED / FAILED | [brief note] |
| [claim 2] | ... | ... | ... |

### Summary
[2-3 sentences: what is the strongest part of this design? What is the most fragile? What is the most important open question?]
```

**Verdict definitions:**
- **SURVIVED** — challenge did not find a gap; Jon's defense was sufficient
- **MODIFIED** — claim held but required qualification or boundary-setting to survive
- **FAILED** — claim did not hold under scrutiny; needs redesign

---

## Scope Limits

- One subject per session — do not scope-creep into adjacent systems
- If Jon wants to defend a different thing mid-session, close the current inventory first, then start fresh
- This skill does not redesign the thing — it surfaces the gaps. Redesign is separate.

---

## What This Skill Does Not Do

- It does not teach (that is `teach-me`)
- It does not collaboratively explore (that is `grill-me`)
- It does not make decisions about what to change — that is Jon's call after seeing the inventory
