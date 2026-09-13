---
title: Skills System
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (skills); sub: skills 6 vs fleet 5 on authored labels"
type: concept
first_seen: skills-master-wiki-pipeline-2026-05-01-bcafba
source_count: 8
last_updated: 2026-06-08
---

## What This Is

The mechanism by which persistent, reusable behaviors are injected into Claude sessions. In claude.ai: skills are markdown files in the Project that shape every conversation. In Claude Code: skills are CLAUDE.md files and slash commands read automatically at session start. The system allows a set of operational behaviors — [[frame-before-commit]] protocol, session order, timestamp discipline, wiki operations — to be reproduced without relying on memory injection.

## What the Wiki Says

### Injection Mechanisms

**claude.ai project:** Skills live as markdown files uploaded to the Project. They're injected into every conversation via the project context. Lossy summarization can occur.

**Claude Code / CLAUDE.md:** CLAUDE.md is read at session start automatically. Content is the full file — no lossy summarization. Functionally equivalent to claude.ai project injection, arguably more reliable. The ~/ CLAUDE.md (user-level) plus per-project CLAUDE.md (repo-level) stack: user-level applies globally, repo-level applies to that project. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

**Slash commands:** Defined in `.claude/commands/` as markdown files. Not ambient — require explicit invocation. Used for discrete operations (e.g., `/ingest`, `/lint`). ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Known Skills (as of 2026-05-01)

| Skill | File | Purpose |
|-------|------|---------|
| wiki-master | skills/wiki-master/SKILL.md | Wiki operations: init, ingest, query, lint |
| frame-before-commit | skills/frame-before-commit/ | FBC protocol execution |
| temporal-context | TEMPORAL-CONTEXT-SKILL.md | Timestamp discipline every response |
| session-order | SESSION-ORDER-SKILL.md | Cold session open reading order |

All four created or canonized by 2026-05-01. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Role Boundary and Wiki-Master Isolation

Wiki-master (see [[wiki-master-origin]] for the origin concept) is the only agent that writes to wiki/ (including all subdirectories: wiki/sources/, wiki/concepts/, wiki/entities/, wiki/personal/, wiki/pro/, wiki/tracker/). All other agents deposit to raw/intake/ and wait. Wiki-master reviews and approves before ingesting. This boundary was added after a Skills Master instance wrote directly to wiki/sources/ — Jon caught and deleted the file mid-session. The fix: SKILL.md now makes the separation explicit and adds intake-review as a gating operation. ([skills-master-cc-restore-2026-05-08-f9cdf4], [skills-master-cc-intake-org-2026-05-07])

Root cause of the collision: wiki-master was being invoked as a mode the calling agent operated in, rather than as a dedicated separate agent. The SKILL.md now specifies it runs as a dedicated agent, not a mode.

### intake-review Operation

Added in f9cdf4 session. When files are in raw/intake/, wiki-master: (1) lists all files, (2) reads each fully, (3) checks compliance against raw-file-standards.md, (4) states APPROVE/NEEDS-FIX/DENY per file, (5) presents the full list to Jon. Ingestion is never automatic — approval and ingest are separate explicit steps. ([skills-master-cc-restore-2026-05-08-f9cdf4])

### Skill Reproducibility Principle

A well-structured MD file is the skill. Any Claude instance that reads it cold has what the original chat "learned." Chat history is irrelevant if the MD file is complete. This dissolves the lock-in problem: no special chat, no memory state required — the wiki plus the skill file is the full knowledge base. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Design/Execution Split

Skill design and iteration happens in claude.ai (conversational, iterative, suited to working things out). Skill execution happens in Claude Code (filesystem access, git, programmatic API calls, durable outputs). The split is not a compromise — it's an architectural choice. Claude Code without the design layer produces unbounded execution; claude.ai without the execution layer produces theater. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

See also: [[design-execution-split]]

### sync-universal.sh

The mechanism for syncing skill files from the repo to ~/.claude (where Claude Code reads them). Scaffolded in skills-master session. Rsync not available in Git Bash on Windows — required workaround. Status: functional at time of session but rsync gap noted. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Loading Tier Architecture

Two tiers established in project-manager-architecture-2026-04-30-f8cc02:

**Critical tier** — guaranteed loaded every session → must live in project files, referenced from SESSION-ORDER-SKILL.md. Example: FBC protocol, working context.

**Reference tier** — available on demand → repo is sufficient. Example: deep background files.

Memory cannot hold skill files — Claude's memory is a short lossy summary, not a document store. Skills must be in project files to be guaranteed loaded. ([project-manager-architecture-2026-04-30-f8cc02])

### SESSION-ORDER-SKILL Loading Chain

Instructions field → README → SESSION-ORDER-SKILL.md → conditional/reference files (per rules in SESSION-ORDER-SKILL). Adding one line to SESSION-ORDER-SKILL makes a repo skill effectively guaranteed-available for the session. ([project-manager-architecture-2026-04-30-f8cc02])

### Role Ecosystem and roles-overview.md

First skills-master session (2026-05-15) settled the architecture question: **separate skill files per role is correct.** A unified "roles" file would require loading all role definitions to access one — heavier context, harder navigation, no benefit. Cross-role isolation means updating wiki-master doesn't touch skills-master. ([skills-master-role-architecture-2026-05-15-2e2c62])

A non-executable cross-role reference, `skills/roles-overview.md`, was created to answer: who exists, how they relate, the intake flow, coordination model, and the conductor gap. This is the document Jon was asking for when considering a "roles skill" — it's a reference document, not an executable skill.

### Entry Point = Skill Threshold Principle

If a tool is only accessed through another skill, it's a section in that skill, not a separate skill. Applied directly to the Ollama wiki operator question: since it is only invoked after reading wiki-master, it's a section in wiki-master, not its own skill. This principle is now in `skills/skills-master/SKILL.md` under "New Skill Threshold." ([skills-master-role-architecture-2026-05-15-2e2c62])

### Triage-Master Division of Labor (Q1 Resolved)

Triage-master is the **decision authority**, not just for contested cases. Wiki-master makes obvious inline ingest calls during a session, but escalates anything unclear to triage-master. Triage-master decides, logs, and flags to Jon if needed. Triage-master does not ingest — that remains wiki-master's job. The pipeline: triage-master decides → wiki-master ingests what was approved. ([skills-master-role-architecture-2026-05-15-2e2c62])

### Skills vs. Wiki Distinction (Jon Confirmed)

"Skills are operational — they tell Claude what to do in a session. Wiki is reference — it documents what is known, what decisions were made, and what happened. The wiki should reference skills as examples of the system working. Skills should not live inside the wiki." ([skills-master-role-architecture-2026-05-15-2e2c62])

### Self-Review Protocol

Skills-master changes to its own SKILL.md require Jon's direct approval before writing. This protocol was added after identifying the conflict-of-interest in unilateral self-review. ([skills-master-role-architecture-2026-05-15-2e2c62])

### Known Roles (as of 2026-05-15)

| Role | Status | Owns |
|------|--------|------|
| wiki-master | Production | wiki/ |
| skills-master | Production | skills/ |
| test-master | Draft | wiki/test-outputs/ |
| project-manager | Stub (DEFERRED) | wiki/tracker/ |
| triage-master | Stub (DEFERRED) | routing decisions |
| data-master | Deferred indefinitely | raw/, scripts/ |

Data-master deferred: pipeline work is largely complete; no dedicated role needed now. Revisit if new pipeline tasks emerge. ([skills-master-role-architecture-2026-05-15-2e2c62])

### Cite, Don't Replicate

A skill that needs behavior from another skill cites it ("see wiki-master Ollama delegation section") rather than reproducing the content. Duplication causes drift. Defined in `skills/roles-overview.md`. ([skills-master-role-architecture-2026-05-15-2e2c62])

### Harness-Creator Skill

`skills/harness-creator/SKILL.md` — multi-agent FBC harness. 6 subagents, isolated contexts. Synthesis routed to a cold dedicated agent (not the orchestrator) to prevent colonization. Agent Teams feature required: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in environment or settings.json. Log-then-answer pattern: subagents write full output to `subagents/run-[date]-[id]/agent-N-output.md` before returning summary. Orchestrator sees summary only. GROUNDING-EXAMPLES.md alongside SKILL.md: three worked examples + smoke-test. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Session-Lifecycle Skill

`SESSION-LIFECYCLE-SKILL.md` — handles session re-open, mid-session status check ("status" / "where are we"), and project status ("project status" / "full status"). Rationale: keep cold-open SESSION-ORDER skill lean; lifecycle triggers only load when needed. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Skill-Evolution Framework

`skills/skill-evolution-framework/SKILL.md` — 8-stage pipeline: Auto-research → Orchestrator FBC → Subtask creation → Parallel subagents + Ralph self-check → Audit agent → Synthesis agent (comparison report, not verdict) → Jon selects winner → Skill-improve-skill applies it. Three-level distinction: Level 1 (build now — bounded, testable), Level 2 (after Level 1 — mutex subtasks Ralph-looped), Level 3 (research problem). ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Skill-Evolution-Ratchet V2

Based on Karpathy autoresearch design (github: karpathy/autoresearch, 11.5K forks). Key V2 rules: NEVER STOP (no human checkpoints mid-loop), mutate from current best (not from last failure), one file per experiment, git reset on failure / git commit on improvement. 4+1+1 selection: 4 strongest + 1 orthogonal + 1 flagged-but-interesting — prevents greedy argmax convergence. V1 = exploration (orthogonal candidates); V2 = exploitation (ratchet). Both needed. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Subagent Architecture Patterns

From harness-creator development:
- **File-mediated coordination:** Subagents cannot spawn other subagents directly; file-as-message-bus routes around this. Main session acts as broker.
- **Escalation-while-running:** Subagent writes request file, continues reasoning, polls for primary reply. Primary does depth routing (shallow/medium/deep), not supervision.
- **Reconstruction package:** For mid-subagent branching — verbatim task + full reasoning trace + state at branch point + branch instructions + files read/written + do-not-repeat list. Write-as-you-go means the log IS the reconstruction package.
- **Write-as-you-go:** FBC subagents write reasoning as they go (not reconstructed at end); self-validating — if branch agents can pick up from the log, the format is proven inhabitable.

([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Claude.ai GitHub Injection Behavior

GitHub-connected files are injected by claude.ai selectively and automatically — Claude cannot pull them with the view tool. Skill design implication: instructions should say "flag if skill referenced but not visible in context" rather than assuming availability. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Skills-Master Intake Flow: Packet-First, Collaborative

From skills-master-cc-intake-queue-b40394-2026-05-23: when multiple packets have accumulated for skills-master (from test-master, wiki-master, herald, or Jon directly), the correct opening move is to surface ALL waiting packets before processing any. Packets are dual-purpose — some require skills-master action, others are for Jon to review or act on; the two are not always separable. The Herald packet pattern (Jon provided it directly because it couldn't be surfaced from the wiki) illustrates that skills-master cannot always discover all inputs independently. Session start protocol: read SKILL.md → read role-sketches.md → inventory skills/ → check intake/ → report before acting. ([skills-master-cc-intake-queue-b40394-2026-05-23])

### T-006: Agent Gap-Fill Behavior

When skills are underspecified, agents gap-fill with local context — producing locally reasonable but globally inconsistent behavior. Named example (2026-05-13): an agent renamed an artifact folder without provenance verification. The root cause was not a bad agent but an underspecified skill. Mitigation requirement: explicit artifact preservation defaults must be written into skill definitions, not assumed. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e])

### Post-Compaction Resume Protocol

Added to wiki-master SKILL.md 2026-05-13: when re-entering a session after context compaction, read index.md, SCHEMA.md, relevant concept pages, and log.md BEFORE writing anything. Rule is a direct response to the risk of writing from stale in-context knowledge — the index.md you had before compaction is not the current state. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e])

## Conflicts

None.

## Related

[[design-execution-split]], [[wiki-master-skill]], [[frame-before-commit]], [[consciousness-framework-research]]
