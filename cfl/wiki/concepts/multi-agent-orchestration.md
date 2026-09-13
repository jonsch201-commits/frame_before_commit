---
title: Multi-Agent Orchestration — Subagent Patterns, Handoff Protocol, and Agent Architecture Gap
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (fleet); sub: fleet 11 vs wiki 3 on authored labels"
type: concept
first_seen: skills-master-wiki-pipeline-2026-05-01-bcafba
source_count: 9
last_updated: 2026-07-05
---

## What This Is

The theory and practice of coordinating multiple Claude instances in the CFL infrastructure. Covers subagent spawning patterns (when and why), file-mediated coordination, the briefing standard for background agents, handoff discipline across sessions, and the open "agent architecture gap" — the design problem of creating proper agent definitions for Claude Code subagent invocation.

## What the Wiki Says

### Subagent Architecture Patterns

Established in harness-creator development (skills-master-wiki-pipeline-2026-05-01-bcafba):

- **File-mediated coordination**: Subagents cannot spawn other subagents directly. File-as-message-bus routes around this. Main session acts as broker.
- **Escalation-while-running**: Subagent writes a request file, continues reasoning, polls for primary reply. Primary does depth routing (shallow/medium/deep), not supervision.
- **Reconstruction package**: For mid-subagent branching — verbatim task + full reasoning trace + state at branch point + branch instructions + files read/written + do-not-repeat list. Write-as-you-go means the log IS the reconstruction package.
- **Write-as-you-go**: FBC subagents write reasoning as they go (not reconstructed at end); self-validating — if branch agents can pick up from the log, the format is proven inhabitable.

([skills-master-wiki-pipeline-2026-05-01-bcafba])

### Briefing Standard for Background Agents

Any background agent expected to run >30 tool calls must write a status file at `raw/agent-status/{agentId}-status.md` before beginning work, update it at each major checkpoint, and write final status on completion or failure. This lets the orchestrating session read mid-run state at any time without needing session continuity.

Format:
```
# Agent Status — {agentId}
started: {timestamp}
role: {skill name}
task: {brief task description}
status: IN-PROGRESS | COMPLETE | FAILED
last_checkpoint: {timestamp} — {what was done}
next: {what comes next}
```

Subagent briefing must include: (1) FL concept context, (2) INGEST/SKIP criteria, (3) spot-check 2 claims minimum, (4) declare all files the agent will read and write. ([wiki-master-phase3-subagent-log-2026-06-01-ad8e70], SKILL.md standing rule)

### Handoff Discipline

All handoffs must go to the main branch — worktree deposits are invisible to receiving agents. This applies without exception: if agent A deposits a file to a worktree branch, agent B will not see it. Discovered as a failure mode in CFL infrastructure work; formalized as a standing rule. ([feedback-handoff-discipline in memory], [wiki-master-cc-testmaster-handoff-gap-2026-05-22-73ecce])

Diagnostic case (2026-05-22): test-master ran research on a worktree branch and deposited findings to `wiki/test-outputs/test-log.md` on that branch. Wiki-master, operating on main, could not see the file. Three root causes: (1) role boundary ambiguity — wiki-master SKILL.md claims exclusive wiki/ ownership, but test-master SKILL.md header says it maintains wiki/test-outputs/test-log.md (direct conflict requiring design resolution); (2) test-master didn't merge the worktree branch before wiki-master invocation; (3) the brief was deposited to the worktree's skills/intake/, not to raw/intake/ on main. The brief pattern itself is sound; the deposit location was wrong. ([wiki-master-cc-testmaster-handoff-gap-2026-05-22-73ecce])

Session-to-session handoff: the grill-me + handoff skills (from mattpocock/skills) provide structure for transferring context across sessions. Skills-master used these in e52ed2 to triage the intake queue across two sessions. Handoff packet contains: group-by-group triage status, open design questions, exact restart message, skills to load for receiving session. ([skills-master-intake-grill-2026-05-27-e52ed2])

### Agent Architecture Gap

Identified in skills-master-intake-grill-2026-05-27-e52ed2 (T26): current role SKILL.md files are invocation guides for claude.ai sessions; what's needed is solid SKILL.md + **paired agent definitions** for Claude Code subagent invocation. A paired agent definition specifies: what the agent can do, what it can't, what it reads, what it writes — so it can be invoked cleanly as a subagent in Claude Code. This pattern does not yet exist for any role as of 2026-05-28.

Jon confirmed (e52ed2 T25): the gap connects to needing subagent invocation to work reliably across roles. Logged as a new intake packet for skills-master. Open design question OD-1. ([skills-master-intake-grill-2026-05-27-e52ed2])

### KV Caching and Background Agent Efficiency

From skills-master-intake-grill-2026-05-27-e52ed2 (T28): when Herald or any background agent always opens with the same token prefix (same wiki index), the KV cache means the compute cost for that prefix is not re-paid on every call. If a background agent has a cacheable index prefix, repeated invocations get cheaper. Disposition: empirical test, not further design. Open design question OD-2. ([skills-master-intake-grill-2026-05-27-e52ed2], [herald-skill-execute-2026-05-28-6bc1d2])

### Herald as Background Agent Pattern

Herald (of Home and Life) was designed partly as a potential background agent: given a wiki index prefix, it could be invoked repeatedly between other tasks. This is a concrete instance of the KV caching opportunity. As of 2026-05-28, Herald is operational in Claude Code (commit f0a9a4f) with a 4-file wiki index load at session open. ([herald-skill-execute-2026-05-28-6bc1d2])

### Subagent JSONL Log Ingestion

Subagent JSONL transcripts are stored at `~/.claude/projects/{session}/subagents/agent-{agentId}.jsonl`. These are first-class knowledge sources when the subagent: runs >50 tool calls, makes commits, exercises judgment on citability or scope → INGEST as source page in `wiki/sources/infrastructure/`, type: `subagent-log`. The wiki-master-phase3-subagent-log-2026-06-01-ad8e70 is an example of a subagent log source page. ([wiki-master-phase3-subagent-log-2026-06-01-ad8e70], SKILL.md)

### Epistemic-Layer Architecture (2026-07-02, agent-interaction-framework-5990f2)

Three layers for multi-agent orchestration design:

- **Epistemic layer** (FBC governs divergence-before-commit; GBS governs claim grounding — per-agent disciplines applied inside any agent regardless of role)
- **Interaction layer** (roles/masters, escalation-while-running, handoff packets, Herald/PM coordination — where loops live; open work: typed handoff schema, run-state persistence, stop rules)
- **Governance layer** (Jon Gates as formal interrupts, Security Master approval, wiki as ground truth, Judgment project as trust-tracking)

Key finding: the external world has solved orchestration mechanics but has largely failed at the epistemic layer. Multi-agent debate research shows agents frequently shift from correct to incorrect answers in response to peer confidence, favoring agreement over challenging flawed reasoning. FBC/GBS is the differentiator; the substrate (fork) is now commodity.

([agent-interaction-framework-2026-07-02-5990f2])

### Ears/Voice/Thoughts — Single Agent Node Anatomy

Channel taxonomy for a single agent, developed in 2026-07-02 session:

- **Ears** — everything entering context (untrusted by default, labelable — GBS source labels attach here; prompt injection is an ears problem)
- **Thoughts** — generated but uncommitted (private, unverifiable, ephemeral — agent cannot re-hear past thoughts once tokens scroll past, unless voiced)
- **Voice** — committed output (persistent, auditable — the only register where enforcement can live; hooks can gate voice, nothing can gate thoughts)
- **Activations** — below thoughts (unhearable even by the agent); CoT-faithfulness research shows thoughts may not faithfully report activations

Three design rules:
1. **Wiring**: Agent A's voice is agent B's ears. Thoughts never cross agents (physics, not discipline). Multi-agent FBC gets independence for free — ID-only reference becomes structural.
2. **Gate placement**: GBS is the ears→voice gate; FBC is the thoughts→voice gate; Hooks are mechanical enforcement at the voice boundary. Every CFL discipline is a gate on a specific channel transition.
3. **The recorder**: FBC branches written to run artifacts = "recorded thoughts" register (persistent like voice, private like thoughts). T-22 (the unsaid) is the deliberate inverse — thoughts permanently denied voice.

"Voice" naming conflict: Jon's literal voice capture (T-43, T-56, Voicenotes) uses "voice" for the system's *ears*. Define terms before the inter-agent PM session to prevent sprawl.

([agent-interaction-framework-2026-07-02-5990f2])

### True Branching — Tier Definitions and Claude Code Mechanics

Three tiers of branching (2026-07-02):

- **Tier 1 (token-identical prefix)**: both branches condition on exact same transcript bytes — the scientifically valid definition; available everywhere today
- **Tier 2 (shared compute/KV reuse)**: branches reuse same prefix computation; Anthropic prompt caching gives this server-side; adds cost savings, not additional validity
- **Tier 3 (mid-thought fork, between T-tags inside a generation)**: NOT available anywhere hosted; escalation-while-running remains the workaround

**SUPERSEDES** prior "KV cache forking not API-accessible" claim (bcafba source page): that finding was true only for mid-generation (Tier 3) forking. Tier 1 and Tier 2 are available. Old claim is now [superseded in scope, high confidence].

Claude Code `/branch` (v2.1.77): creates a true copy of conversation, original intact in session picker. `--fork-session` for programmatic branching. Note: `/rewind` has a May 2026 bug (mutates in place) — use `/branch` and `--fork-session`. Tier 3 at a message boundary resolves to Tier 1 (fork before tool result).

([agent-interaction-framework-2026-07-02-5990f2])

### PM Map v0.2 — Five-Piece Stack and S1–S10 Build Order (2026-07-03)

Five-piece stack (P-numbered by build dependency):
- **P0** — FBC/GBS disciplines (epistemic core, already built)
- **P1** — Interaction layer (roles, loops L1–L7, escalation — the main design surface)
- **P2** — Node anatomy (Ears/Voice/Thoughts + frame taxonomy)
- **P3** — True branching (Tier 1–3 substrate)
- **P4** — Probabilistic routing (Thompson sampling, shadow register)
- **P5** — Stylomantic research (production system)

Build order S1–S10: S1 terminology → S1b harvest → S2 first true-branch test → S3 interaction schema → S4 synthesizer skill → S5 hooks → S6 label pipeline → S7 routing v0 → S8 Stylomantic ladder → S9 features → S10 partial pooling. Core path S1–S7: ~6–10 desk sessions. S8–S10 not estimable.

**Kill criteria gap:** the map lacks pre-stated falsifiers. What result would tell Jon to simplify rather than extend? This is identified as a design-level gap to address at the desktop PM session.

([agent-interaction-framework-2026-07-02-5990f2])

### Probabilistic Routing — P4, Thompson Sampling, Shadow Register (2026-07-03)

P4 is the routing layer: each routing option (branch vs. single-agent, invoke loop vs. skip) gets a Beta distribution updated from outcomes. Thompson sampling draws a probability from each Beta, picks the highest. **Shadow register:** when policy overrides model judgment, record both — the policy choice and the counterfactual (what the model would have chosen). Shadow register disagreements feed Judgment project credibility measure and are one of the Herald's four listening posts. No probability numbers until n is sufficient; routing v0 is trivial rules.

([agent-interaction-framework-2026-07-02-5990f2])

### Missing Pieces (Genuinely Absent)

1. **Run-state persistence**: wiki persists knowledge; nothing persists loop state; LangGraph's checkpointing with time-travel is the import concept
2. **Sycophancy resistance between agents**: nothing stops verifier capitulation to a confident producer; explicit rule needed (verifier must state disagreement before seeing producer's justification)
3. **Independence verification**: Tier 1 fork gives context identity, but inter-model branching (model heterogeneity significantly improves debate outcomes) isn't a routine option yet
4. **Routing/cost policy**: when is a loop worth invoking? FBC has contraindications; agent layer has none; multi-agent burns ~10x tokens
5. **Typed handoff schema**: no message schema (item ID, provenance, GBS labels, requested action, completeness declaration) — every comparable framework has one; CFL has prose

**Inter-agent FBC semantics is the load-bearing gap**: who the synthesizer is, what it receives (blinded? labeled?), whether ID-only reference maps to context isolation — all undefined. Identified as first design session priority.

**Failure taxonomy reference**: Cemri et al. 2025 documents coordination quality degradation patterns — a ready-made seed for the Judgment known-failures log.

([agent-interaction-framework-2026-07-02-5990f2])

## Conflicts

⚠️ CONFLICT: bcafba source page (skills-master session) contains the claim "KV cache forking not API-accessible." The agent-interaction-framework-2026-07-02-5990f2 session supersedes this: that claim applies only to mid-generation (Tier 3) forking. Tier 1 (message-boundary fork) and Tier 2 (cached prefix reuse) are available. The bcafba source page should be annotated [superseded in scope].

## Related

[[skills-system]], [[herald-of-home-and-life]], [[wiki-master-origin]], [[frame-before-commit]], [[loop-taxonomy]]
