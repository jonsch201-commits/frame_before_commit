---
name: skill-evolution-ratchet
description: Autonomous ratchet loop for iterative skill improvement. Based on Karpathy's autoresearch pattern adapted for skill files. Use when Jon says "ratchet this skill", "run the loop on X skill", "autoresearch on X", or "evolve this skill autonomously". Requires Claude Code. Human work happens BEFORE the loop (program.md equivalent) and AFTER (review results). The loop itself runs without interruption until stopping criteria are met or Jon intervenes. Do not pause mid-loop to ask for guidance.
---

# Skill Evolution Ratchet

Autonomous iterative improvement loop for skill files. One file to modify. One metric to optimize. Git as the rollback mechanism. Loop runs until stopping criteria met or human interrupts.

This is the exploitation phase. Use skill-evolution-framework (V1) when you need divergent candidate generation. Use this when you have a direction and want to drill down on it.

---

## Human Setup — Before the Loop

Human writes the program equivalent before the loop starts. Claude Code reads it and does not ask for clarification mid-loop.

**Required inputs from Jon:**

```
TARGET SKILL: [path to skill file — one file only]
TEST CASE: [the specific question or scenario to score against]
METRIC: [what "better" looks like — see Metric Definition below]
STOPPING CRITERIA: [when to stop — see below]
IN SCOPE: [what the agent may modify]
OUT OF SCOPE: [what must not change — core discipline rules, etc.]
HUMAN REVIEW FLAGS: [which dimensions require Jon's judgment after loop ends]
```

File this as: `harness/ratchet-[skill-slug]-[date]/program.md`

---

## Metric Definition

The metric is the most important decision. Bad metric = loop optimizes the wrong thing.

For FBC skill specifically, score each test run on:

```
DELTA quality:     Does [COMMIT] contain a real counterfactual? (0-2)
                   0 = no DELTA markers
                   1 = DELTA present but no counterfactual ("B2 changed my thinking")
                   2 = DELTA has explicit before/after ("Without B2 I would have said X, with it Y")

META specificity:  Does [META] name absences, not summaries? (0-2)
                   0 = "branches showed different perspectives"
                   1 = names what was present in other branches
                   2 = names what was ABSENT from the instinct branch

Branch independence: Did later branches anchor to B1? (0-2)
                   0 = explicit reproduction of B1 content
                   1 = implicit conceptual anchoring visible
                   2 = genuinely distinct frame

TOTAL: 0-6 per run
```

Define your metric before the loop. Do not change it mid-loop — that invalidates comparisons.

For other skill types: define a 0-N rubric with explicit, LLM-evaluable criteria. Binary yes/no per criterion is best. Avoid "how good is this overall" — that's not a metric, it's a vibe.

---

## Candidate Selection — 4+1+1 Rule

When proposing mutations, do not always pick the 6 highest-probability improvements. That's greedy search — finds local optima, misses insight.

Selection rule per iteration:
- **4 exploitative** — strongest candidates based on current best version
- **1 orthogonal** — genuinely different from all 4, even if seemingly weaker
- **1 flagged** — something you would have discarded but noticed something in passing

This is controlled noise. The +1+1 exist to prevent premature convergence. A branch that seemed bad sometimes unlocks insight elsewhere.

For single-candidate loops (one mutation per iteration): use FBC to generate the mutation proposal. Pick from the FBC branches using 4+1+1 weighting — don't always take the INSTINCT branch's proposal.

---

## Loop Structure

```
SETUP
├── Read program.md equivalent
├── Read current skill file (this is the baseline)
├── Run test case against baseline — record score as baseline_score
├── Initialize results.tsv with header
└── Confirm setup. Once confirmed: NEVER STOP.

LOOP (repeat until stopping criteria)
├── PROPOSE: FBC on "what single change to this skill would improve the metric?"
│     - Generate branches (minimum: INSTINCT, ADVERSARIAL, ORTHOGONAL, NULL)
│     - Select mutation candidate using 4+1+1 rule
│     - If mutation is mutually exclusive with current best: flag in results.tsv, proceed with best judgment
│
├── APPLY: Make ONE change to the skill file
│     - One logical change per iteration
│     - Keep diffs small and reviewable
│     - Do NOT modify anything in OUT OF SCOPE
│
├── TEST: Run test case against modified skill
│     - Score against metric rubric
│     - If test fails to run (malformed output, etc.): Ralph fix — attempt repair up to 3 times
│     - If still failing after 3 attempts: git reset, log RALPH-FAILED, continue loop
│
├── DECIDE:
│     - If score > current_best: git commit, update current_best, record KEEP in results.tsv
│     - If score <= current_best: git reset (discard), record DISCARD in results.tsv
│     - Always mutate from current_best — not from last failed attempt
│
└── LOG: Append to results.tsv
      [iteration | mutation_description | score | keep/discard | notes]
```

---

## Ralph as Crash Handler

Ralph is NOT a pre-step on every iteration. Ralph fires only when the test case cannot be scored — malformed output, broken format, incomplete run.

Ralph procedure:
1. Identify what broke
2. Fix the skill file change that caused it
3. Re-run test case
4. Max 3 Ralph iterations per experiment
5. If still broken: git reset, log RALPH-FAILED, continue to next iteration

Do not use Ralph to polish outputs that ran successfully. Ralph is error recovery only.

---

## NEVER STOP Rule

Once the loop has begun, do NOT pause to ask Jon if you should continue. Do NOT ask "should I keep going?" or "is this a good stopping point?" Jon may not be available.

Exceptions — stop and wait for human only when:
- A mutation would modify something explicitly listed as OUT OF SCOPE
- results.tsv shows 5 consecutive RALPH-FAILED (something structural is broken)
- Stopping criteria met

Otherwise: run until interrupted or stopped.

---

## Stopping Criteria

Define at least one in program.md. Options:

```
- N consecutive KEEPs with score >= threshold (e.g. 3 consecutive 6/6)
- N total iterations completed (e.g. 50 experiments)
- Score improvement rate drops below X per N iterations (plateau detection)
- Score reaches maximum possible (6/6 for FBC rubric)
```

When stopping criteria met: do NOT apply any more changes. Finalize results.tsv. Write summary. Wait for human review.

---

## Git Structure

One dedicated branch per run:

```bash
git checkout -b ratchet/[skill-slug]-[date]
```

Never run on main. This keeps diffs reviewable and the run reversible.

Commit message format: `ratchet: [iteration N] [mutation description] score:[X/Y]`

---

## Output Structure

```
harness/ratchet-[skill-slug]-[date]/
  program.md          ← human setup inputs
  results.tsv         ← untracked, append-only experiment log
  summary.md          ← written at loop end, before human review
```

results.tsv format:
```
iteration | mutation | score | baseline | delta | keep | notes
1         | added counterfactual requirement to DELTA | 5 | 4 | +1 | KEEP |
2         | tightened META as-if-external language | 4 | 5 | -1 | DISCARD |
...
```

summary.md written at loop end:
```
RATCHET SUMMARY — [skill] — [date]

Iterations: N
Starting score: X/Y
Final best score: X/Y
Improvement: +N (Z%)
Mutations kept: N
Mutations discarded: N

Most effective mutation types: [from results.tsv analysis]
Mutations flagged for human review: [list per program.md criteria]
Final diff: [what actually changed from baseline to current best]
Next direction suggestion: [what the loop found that it couldn't pursue within scope]
```

---

## Human Review After Loop

Jon reviews summary.md and the final diff. Not the individual iterations — that's what results.tsv is for if needed.

Human judgment required for items flagged in program.md. The loop accumulated them. Jon reviews them now.

If the final diff is "clearly better": promote to production (copy to skills/[skill]/SKILL.md, commit to main, sync).

If "different-but-unclear": Jon decides. Do not promote without explicit sign-off.

If "worse than baseline": something is wrong with the metric. Review before running again.

---

## Applying Improvements Immediately

When running autoresearch on a skill that will be used in subsequent iterations (e.g. FBC evolving FBC): after Jon approves the final diff, apply it to the production skill file before starting the next ratchet run. The loop always starts from the current best production version, not a cached baseline.

This is the compounding property. Each run starts smarter than the last.

---

## What This Skill Does Not Do

- Does not run exploration (use skill-evolution-framework V1 for that)
- Does not pause mid-loop for guidance
- Does not modify files outside the single target skill file
- Does not promote to production without human sign-off
- Does not change the metric mid-loop
- Does not treat Ralph as a quality polish step — crash recovery only
- Does not mutate the `## Standing Decisions` section of any skill file — that section is immutable to the ratchet. Standing decisions represent confirmed locked choices. A ratchet run that overwrites a confirmed decision has gone backwards without knowing it. If a standing decision needs reconsideration, Jon flags it explicitly before the run begins.

---

## Standing Decisions

Confirmed design choices for this skill. Maintained by skills-master. Do not mutate without Jon's explicit direction.

| Decision | Date confirmed | Source |
|----------|---------------|--------|
| 4+1+1 selection rule: 4 exploitative + 1 orthogonal + 1 flagged-but-interesting — prevents greedy argmax convergence | 2026-05-01 | skills-master-wiki-pipeline-2026-05-01-bcafba |
| NEVER STOP rule: no human checkpoints mid-loop | 2026-05-01 | skills-master-wiki-pipeline-2026-05-01-bcafba |
| Mutate from current best, not from last failure | 2026-05-01 | skills-master-wiki-pipeline-2026-05-01-bcafba |
| Standing Decisions sections in any skill file are immutable to the ratchet — do not mutate without Jon's explicit direction | 2026-05-16 | OI-008 skills-master session |
