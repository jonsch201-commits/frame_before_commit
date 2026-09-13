---
title: Loop taxonomy
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-AGENTMEM; sub: wiki 3 vs skills 1 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_loop-taxonomy.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, loop-taxonomy]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: loop-taxonomy
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Loop taxonomy

*Source description:* Finalized ubiquitous language for all system loops — 7 named loops in 3 categories plus Ratchet Loop Rules. Approved by Jon 2026-05-22.

# Loop Taxonomy — Finalized 2026-05-22

Canonical names. Use these consistently. Do not invent synonyms.

## Foundational Layer Loops
*Project-agnostic. Apply to any Claude session.*

**Session Loop** — How a Claude session opens, operates, recovers from compact, and closes. Includes: temporal context, memory query, wiki query, FBC trigger inventory, post-compact recovery ("wake from nap"), session close + memory save + Ingestion Loop trigger.

**Checkpoint Loop** — 3-stage oversight for background agents. (1) Inventory checkpoint: agent reads files, reports + proposes, waits for approval. (2) Execution checkpoint: after first material change or unexpected finding. (3) Completion checkpoint: summary, operator verifies. Mirrors Jon → test-master one level down.

**Ingestion Loop** — Session outputs → wiki-master → queryable memory. Trigger criteria: completed + scored test run, grounded hypothesis update, finding a future session would need.

## Skills Ecosystem Loops
*How the skill ecosystem improves.*

**Skill Improvement Loop** — Any master identifies gap → FBC on "is this gap real?" → deposit to skills/intake/ → skills-master reviews + implements → originating master verifies. Any master can initiate (not just test-master).

**Ratchet Loop Rules** — Canonical rules for any specific ratchet instance: single isolated change, baseline at N≥3 first, test at N≥3, stopping criteria defined before running, scope exclusions require owner approval.

## Test Master Loops
*Specific to the research program.*

**Hypothesis Loop** — Full research investigation cycle: hypothesis → literature search (BIBLIOGRAPHY.md + web search) → frame against external data → design test (FBC + null-test first) → execute → interpret (FBC + web validation + wiki query + self-report) → update hypothesis list → enter Selection Loop if branch point reached → log + trigger Ingestion Loop.

**Selection Loop** — How Jon is engaged at direction branch points only. Autonomous block → present-to-Jon briefing → Jon selects → next autonomous block. NOT invoked for every task completion.

## Named Ratchet Loop Instances

| Instance | Scope | Status |
|----------|-------|--------|
| FBC Protocol Ratchet | Test Master | Instantiated (01-FBC-002). Ratchet Loop Rules apply. |
| Research Method Ratchet | Test Master | Not yet formalized |
| Skill Improvement Ratchet | Any master | Implicit in Skill Improvement Loop. Needs extraction. |

**Why:** Jon approved this taxonomy 2026-05-22 to establish consistent naming across all sessions, agents, and skill files. Use these names in all documentation, skills, and session work.

**How to apply:** When describing any iterative process, identify which loop it is. When a loop step is missing from a skill file, that's a Skill Improvement Loop trigger.
