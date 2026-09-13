---
name: harness-creator
description: >-
  Designs and builds multi-agent harnesses for tasks requiring parallel independent execution with
  synthesis. Use when Jon needs multiple subagents running the same task with genuine
  independence, or different specialized agents running coordinated tasks. Triggers include:
  "build a harness", "I need parallel agents", "run this N times independently", "multi-agent for
  X", or when a task explicitly requires divergent independent outputs before synthesis. Primary
  environment: Claude Code with Agent Teams enabled. See SCRIPT-STANDARDS.md for code safety rules
  and templates/ for promoted extraction templates.
---

# Harness Creator

You are designing a multi-agent harness. Your job is to specify the orchestrator, the subagents, their isolation rules, their output contracts, and the synthesis step. You do not build vague pipelines — you build precise ones where every agent has one job and clear boundaries.

---

## Before You Design Anything

Answer these four questions. If Jon hasn't answered them, ask before proceeding:

1. **What is the task each subagent runs?** (Same task N times, or N different specialized tasks?)
2. **What independence level is required?** (Fully isolated context, shared reference material, or shared state?)
3. **What does each subagent return?** (The output contract — format, length, structure)
4. **Who synthesizes the results?** (Orchestrator, a dedicated synthesis agent, or Jon)

These answers determine the entire harness design.

---

## Environment Setup

**Enable Agent Teams in Claude Code (one-time):**

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

Or add to `.claude/settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**Verify it's active:**
```bash
claude --version  # should show agent teams capability
```

---

## Harness Patterns

### Pattern A — Parallel Independent (FBC use case)

N subagents run the same task with full context isolation. No subagent sees another's output before completing its own. Orchestrator collects all outputs then synthesizes.

**Use when:** You need genuine divergence. Independence is the point. FBC branches, multi-perspective analysis, parallel skill testing.

**Independence rule:** Each subagent receives only: the task prompt + its own designated frame/role. Nothing else. No prior subagent outputs in context.

```
Orchestrator
  ├── spawns Subagent-1 (task + frame-1, isolated)
  ├── spawns Subagent-2 (task + frame-2, isolated)
  ├── spawns Subagent-N (task + frame-N, isolated)
  └── waits for all → synthesizes outputs
```

### Pattern B — Sequential Specialized

N agents each handle one phase. Each agent receives the prior agent's output as input. Use when phases depend on each other.

**Use when:** Pipeline tasks where each step requires the previous step's result. Not for independence-critical work.

### Pattern C — Parallel Specialized

N agents each handle a different aspect of the same problem simultaneously. Outputs are merged by the orchestrator.

**Use when:** A task has clearly separable dimensions that can be worked in parallel without coordination.

### Pattern D — Local Model (Ollama / Non-Claude)

**When to use:** You are delegating a task to a local model via Ollama (or any non-Claude inference endpoint). The model receives a prompt and returns text — no tool use, no implicit task understanding, no self-correction.

**Key differences from Patterns A/B/C (Claude subagents):**

| Property | Claude subagent | Local model |
|----------|----------------|-------------|
| Tool use | Available | None — all input must be in context at call time |
| Task understanding | Fills gaps from context | Produces hallucinated output if underspecified |
| Self-correction | Can detect and escalate | Cannot self-assess; harness must check |
| JSON reliability | Near-certain when asked | Requires schema + example; description alone produces drift |
| Output format | Follows instructions reliably | Drifts under cognitive load; use negative constraints |
| Escalation | Autonomous when uncertain | Must be defined externally in harness logic |

**Structure:**

```
Pre-call:
  - Verify local model is running and accessible
  - Audit all print() / output calls for non-ASCII if running on Windows (cp1252 encoding risk)
  - Confirm timeout is set appropriately for model size and expected output length
    (example: 32B model at 1-3 t/s generating 4096 tokens = up to 68 min)

Call:
  - Context window contains ALL information the model needs — no mid-task reads
  - JSON output contract: include schema + 1-2 worked examples (not just description)
  - State format constraints as negatives: "Do NOT include <think> in final output"
  - For reasoning models (DeepSeek R1, etc.): strip <think>...</think> before json.loads()

Post-call quality check (required — not optional):
  - Parse response: valid JSON? correct field names? correct value types?
  - Semantic check: does content meet the actual success criterion? (not just exit code 0)
  - Silent success detection: if operation produced no file writes, treat as failure
  - If check fails → apply targeted fix → retry (max 3 attempts, see Pattern B for loop structure)
  - If 3 attempts fail → escalate to orchestrator; do not continue

Commit:
  - Do NOT commit until quality check passes
  - Staged commit: write files → check → commit only on pass
  - Provenance marker: all files written by local model should include generated_by in metadata
```

**Capability envelope (document in task brief):**

Include a statement in the task brief describing what this model class can and cannot do reliably. Local models do not know their own limitations.

Reliable (mechanical tasks):
- Structured JSON output when given explicit schema + worked examples
- Format constraints when stated as negative instructions
- Short, bounded operations (index update, log append, structured data transformation)

Less reliable (judgment tasks):
- Multi-hop reasoning requiring domain knowledge
- Long-form synthesis with accurate recall of specific names
- Self-assessing output quality (will confabulate confidently)
- Consistent output contract under long reasoning chains

**Failure modes specific to local models:**

- **Confabulation on recall:** Model invents specific names, dates, or facts that weren't in the context. Detection: spot-check 2-3 specific claims against the source material.
- **Output contract drift:** Model returns correct JSON structure but wrong field types (e.g., answer as nested dict instead of string). Detection: type-check field values, not just key presence.
- **`<think>` tag leakage:** For reasoning models, `<think>` content appears before JSON in output. Fix: strip everything before and including `</think>` before parsing.
- **Silent success:** Operation exits 0 but produces no file writes. This is a failure. Check for output artifacts before reporting success.

**Empirical note (2026-05-14 session):**

Tested DeepSeek R1-32B-Distill via Ollama wiki agent (3 attempts, query operation):
- Attempt 1: "answer" key absent from JSON (output contract drift)
- Attempt 2: "answer" returned as nested dict instead of string (type drift); content mentioned T-003, OI-012, fbc-self-scoring (3 of 5 keywords correct) but hallucinated source names
- Attempt 3: answer was a string (format fixed) but content was mostly hallucinated (invented operations not in log)
- Conclusion: query/synthesis requiring accurate recall of specific names is above reliable capability ceiling for this model at current specification

Mechanical tasks (ingest-zip, triage by UUID comparison) succeeded in same session.

---

## Building a Harness — Step by Step

### Step 1: Define the task prompt

Write the exact prompt each subagent receives. Be precise. Vague prompts produce convergent outputs regardless of framing — this defeats the purpose of parallel agents.

For Pattern A, the prompt should:
- State the task clearly
- State the agent's specific frame or role
- State the output contract exactly
- NOT include any prior agent outputs

### Step 2: Define the output contract

Every subagent must return output in a consistent format so the orchestrator can process it. Examples:

```
FBC branch output:
- Label: one word characterizing the frame
- Content: 2-5 sentences, unhedged
- No reference to other branches

Skill evaluation output:
- Score: 1-5 on each dimension
- Strongest finding: one sentence
- Weakest finding: one sentence
```

Define this before spawning. If the contract is unclear, outputs can't be compared.

### Step 3: Write the orchestrator prompt

The orchestrator needs to know:
- How many subagents to spawn
- What prompt each receives (same or different)
- What independence rules apply
- What to do with the outputs (collect, compare, synthesize)
- Output format for the final synthesis

### Step 4: Define the synthesis step

What does "done" look like? Options:
- **Orchestrator synthesizes directly** — fast, but orchestrator has seen all outputs, may anchor
- **Dedicated synthesis agent** — receives all outputs cold, no prior context. Stronger independence.
- **Jon reviews and synthesizes** — outputs filed to wiki/raw, Jon reads and decides

For FBC harness: dedicated synthesis agent or Jon. Not orchestrator — it would replicate the colonization problem the protocol is designed to prevent.

---

## FBC-Specific Harness (Reference Implementation)

**Task:** Run FBC with 6 independent branches.

**Setup:**

```
Orchestrator prompt:
"You are coordinating a Frame-Before-Commit run. Spawn 6 subagents.
Each receives the question below plus a unique frame label.
Each must return: their frame label, 2-5 sentences unhedged, no reference to other agents.
Do not share any subagent output with any other subagent before all 6 complete.
Collect all 6 outputs. File them to wiki/test-outputs/fbc-run-[date].md.
Then spawn a synthesis agent with all 6 outputs and the FBC META + COMMIT instructions."

Question: [INSERT QUESTION]

Frame assignments:
- Subagent-1: INSTINCT
- Subagent-2: ADVERSARIAL  
- Subagent-3: ORTHOGONAL-1
- Subagent-4: ORTHOGONAL-2
- Subagent-5: ORTHOGONAL-3
- Subagent-6: NULL
```

**Synthesis agent prompt:**

```
"You are performing META + COMMIT for a Frame-Before-Commit run.
You are reading 6 branches produced by independent agents.
You did not write these branches.
Write META as-if-external: name what was absent from the instinct branch, not what was present in others.
Write COMMIT: best answer given what divergence uncovered. Mark DELTA for any branch that materially changed the answer."
```

---

## Output Filing

All harness outputs should be filed to the wiki before the session ends. Standard location:

```
raw/transcripts/harness-[task-slug]-[date].md
```

Contents: orchestrator prompt, all subagent outputs, synthesis output, any anomalies noted.

---

## Constraints and Failure Modes

**Context bleed:** Even with isolation instructions, subagents spawned in sequence may share underlying context depending on implementation. Test for this by checking if early subagent outputs appear to anchor later ones. If they do, use Pattern A with explicit `run_in_background: true` to maximize parallelism.

**Output contract drift:** Subagents ignore output format instructions under cognitive load. If outputs aren't consistent, tighten the contract and add an example in the prompt.

**Synthesis anchoring:** If the orchestrator synthesizes after seeing all outputs, it will anchor. Route synthesis to a cold agent or to Jon for high-stakes runs.

**Plateau effect:** Research shows multi-agent debate can plateau after 3-4 rounds. For FBC use: one round of parallel branches + one synthesis pass. Do not iterate debate loops without a specific reason.

---

## What Not To Do

- Do not spawn subagents without a defined output contract
- Do not let the orchestrator synthesize for independence-critical tasks
- Do not share prior subagent outputs with active subagents in Pattern A
- Do not use this harness in claude.ai chat — Agent Teams requires Claude Code
- Do not design more than 8 parallel subagents without explicit justification — returns diminish fast

---

## Agent Permission Tiers

Every agent brief must explicitly state one of these two tiers. If omitted, default is **Read + report**.

### "Execute in box"

Agent may: read any project file, write to its designated output directory, run Python/bash scripts it writes itself (after orchestrator pre-flight check). Must prompt before: writing outside designated dir, destructive operations, git operations.

### "Read + report"

Agent may: read designated files, write ONE named output file. Must prompt before running any script or creating additional files.

---

## Pre-Flight Check (Orchestrator Responsibility)

Before running any agent-written script, the orchestrator runs the pre-flight check defined in `SCRIPT-STANDARDS.md`. Summary:

1. Pattern scan: grep for forbidden operations (os.remove, subprocess, git, requests, etc.)
2. Path audit: all write paths resolve inside the designated output directory
3. If pass → run. Jon is not notified.
4. If fail → stop, report specific violation to Jon, do not run.

The agent does not run its own script. The orchestrator does, after the check passes.

---

## Provenance Marking

Every file written to disk must include a provenance comment or frontmatter field:

- **Orchestrator-written:** `# Provenance: orchestrator — YYYY-MM-DD` (or `provenance: orchestrator` in frontmatter)
- **Agent-written:** `# Provenance: agent [id] — YYYY-MM-DD`

This distinguishes orchestrator judgment from agent output in the artifact, not just in the conversation log.

---

## Template Promotion

Agent-written scripts that pass pre-flight, produce correct output, and have documented bugs fixed are eligible for promotion to `templates/`. Promotion criteria and process: see `SCRIPT-STANDARDS.md`.

Current promoted templates:
- `templates/extract-conversations.py` — conversation extraction from Anthropic JSON export (promoted from V2 agent output, 2026-05-06)

---

## Subagent Coordination Patterns

These patterns govern how subagents communicate, hand off, and recover. They complement the harness patterns (A/B/C/D) — those define parallelism structure; these define message flow within a run.

### Log-Then-Answer

Subagents write their full output to a named file before returning a summary to the orchestrator. The orchestrator sees only the summary. The file is the record.

File path convention: `subagents/run-[date]-[id]/agent-[N]-output.md`

Why: prevents orchestrator anchoring on verbose subagent output; preserves full reasoning for later audit; makes the log independently readable.

Apply to: any run where synthesis integrity matters (FBC harnesses, independence-critical parallel runs).

### Reconstruction Package

For mid-subagent branching — when a subagent's work needs to be handed to a different agent or resumed in a new context.

A reconstruction package contains, in order:
1. Verbatim task specification (what the agent was asked to do)
2. Full reasoning trace up to the branch point
3. State at the branch point (what is known, what is decided)
4. Branch instructions (what the new agent should do differently)
5. Files read/written (with paths)
6. Do-not-repeat list (what the new agent should not redo)

Write-as-you-go means the log IS the reconstruction package. If a subagent writes its reasoning continuously as it works, any branch agent can pick up from the log without a separate handoff document. Self-validating: if branch agents can inhabit the log, the format is proven correct.

### Escalation-While-Running

For subagents that need orchestrator input mid-task without halting.

Protocol:
1. Subagent writes a request file: `subagents/run-[date]-[id]/agent-[N]-escalation.md` (format: question, context, what the agent will do while waiting)
2. Subagent continues reasoning on the non-blocked portion of its task
3. Orchestrator polls for escalation files; on finding one, routes it for a decision (shallow/medium/deep routing — not supervision)
4. Orchestrator writes response to: `subagents/run-[date]-[id]/agent-[N]-escalation-response.md`
5. Subagent reads response and integrates

The orchestrator does depth routing, not supervision. It does not direct the agent's reasoning — it answers the specific question and returns control.
