---
title: Skills Master — Wiki Infrastructure, Architecture Decisions, FBC Protocol, and Harness/Ratchet Framework
trunk: fl
branch: [cfl, fbc]
sub_branch: [skills]
branch_reason: "R-SRC-INFRA; secondary branch from title/slug (fbc) — load-bearing-for; sub: skills 5 vs wiki 4 on authored labels"
source_file: raw/transcripts/claude-ai/fl/skills-master/skills-master-2026-05-01-bcafba.md
source_file_status: markdown-export (native-json-export via convert-export.py; turn numbers = message sequence)
project: Claude Foundational Layer
date_ingested: 2026-05-16
date_updated: 2026-06-27
type: session
tags: fl, wiki-master, skills, architecture, fbc, claude-code, extraction-pipeline, t-tag, harness, ratchet, subagent
---

## Summary

Primary skills-building session (304K chars). Spans 2026-05-01 through 2026-05-06. Initial work: wiki-master SKILL.md, SCHEMA.md, pipeline.py, architecture decisions (design/execution split, three-layer model), T-tag notation, FBC protocol updates. Continuation (2026-04-30 afternoon through 2026-05-06): SESSION-LIFECYCLE-SKILL.md, harness-creator skill, skill-evolution-framework, skill-evolution-ratchet V2, subagent architecture patterns (log-then-answer, reconstruction package, escalation-while-running, 4+1+1 selection), Karpathy autoresearch comparison, claude.ai GitHub injection discovery.

## Key Claims

- Wiki infrastructure (SKILL.md, SCHEMA.md, pipeline.py, GitHub Action) built and tested end-to-end with mock API in this session — the canonical origin of the wiki-master skill ([skills-master-wiki-pipeline-2026-05-01-bcafba:T2])
- Architecture decision: Cowork eliminated from priority list; stack is claude.ai (design) + Claude Code (execution) + GitHub wiki repo ([skills-master-wiki-pipeline-2026-05-01-bcafba:T12])
- CLAUDE.md is the injection mechanism — equivalent to this project's memory injection but via file read; same functional result, arguably more reliable because it's the full document not a lossy summary ([skills-master-wiki-pipeline-2026-05-01-bcafba:T18])
- Three-layer architecture established: claude.ai (relational/orienting), wiki (compounding operational knowledge), Claude Code (hands). Not a migration problem — two layers doing genuinely different jobs ([skills-master-wiki-pipeline-2026-05-01-bcafba:T18])
- Test master concept: knowledge captured in a well-structured MD file makes the test master reproducible — any Claude instance reading it cold has what it needs ([skills-master-wiki-pipeline-2026-05-01-bcafba:T16])
- T-tag notation proposed and accepted in this session: sub-thoughts within a branch tagged B1T1, B1T2, etc. The T-tag forces a commit-before-continuing that continuous generation doesn't impose; it surfaces thoughts that would otherwise be absorbed ([skills-master-wiki-pipeline-2026-05-01-bcafba:T40])
- FBC protocol update: as-if-external META (treat [META] as written by an external reviewer, not the author of the branches) — prevents the moderator-as-party problem ([skills-master-wiki-pipeline-2026-05-01-bcafba:T40])
- FBC pure run in session (MIGRATION/RELATIONAL/ARCHITECTURAL): 2 deltas — B2 (RELATIONAL) forced the question of what claude.ai does that migration would break; B3 (ARCHITECTURAL) reframed from migration to two-layer architecture ([skills-master-wiki-pipeline-2026-05-01-bcafba:T18])
- FBC directed run in session (INSTINCT/ADVERSARIAL/ORTHOGONAL/NULL): 3 deltas — B2 (ADVERSARIAL) surfaced prior error history as load-bearing; B4 (NULL) established design/execution split; B3 (ORTHOGONAL) named activation energy as the real constraint ([skills-master-wiki-pipeline-2026-05-01-bcafba:T22])
- Stylomantic position-0 failure is a heap problem at inference: first token selected before attention reweighting, sets trajectory downstream attention treats as prior context ([skills-master-wiki-pipeline-2026-05-01-bcafba:T26])
- LLM training shape: petabyte corpus → filtered heap → flows through net (parameters fixed before training) → weights encode statistical regularities; attention is the inference-time summarization function ([skills-master-wiki-pipeline-2026-05-01-bcafba:T28])
- sync-universal.sh scaffolded in session; rsync not available in Git Bash on Windows — required workaround ([skills-master-wiki-pipeline-2026-05-01-bcafba:T130])
- Project FRAME-BEFORE-COMMIT.md in claude.ai project was stale at time of session — updated version with T-tags, as-if-external META, counterfactual delta format, inter-model branching, and contraindications existed only as an output file ([skills-master-wiki-pipeline-2026-05-01-bcafba:T66])

- SESSION-LIFECYCLE-SKILL.md created: handles session re-open, mid-session status check ("status" / "where are we"), and project status. Rationale: keep cold-open skill lean; lifecycle triggers load only when needed. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T160])
- SESSION-ORDER-SKILL.md updated: topic check softened, "Moved from README" section removed, wiki export added as step 3 of close ritual. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T162])
- harness-creator SKILL.md created: multi-agent FBC harness — 6 subagents, isolated contexts, synthesis routed to a cold dedicated agent (not orchestrator) to prevent colonization. Agent Teams feature: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T164])
- Log-then-answer pattern: each subagent writes full output to subagents/run-[date]-[id]/agent-N-output.md before returning summary. Orchestrator sees summary only; full reasoning archived. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T166])
- skill-evolution-framework SKILL.md created: 8-stage pipeline — Auto-research → Orchestrator FBC → Subtask creation → Parallel subagents + Ralph self-check → Audit agent → Synthesis agent → Jon selects winner → Skill-improve-skill applies it. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T174])
- skill-evolution-ratchet V2 (vs. V1): V2 rules — NEVER STOP (no human checkpoints mid-loop), mutate from current best, one file per experiment, git reset on failure/git commit on improvement. V1 = exploration (orthogonal candidates); V2 = exploitation (ratchet loop with known mutation direction). Both needed. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T180])
- 4+1+1 selection formalized: 4 strongest + 1 genuinely orthogonal + 1 flagged-but-interesting. Prevents greedy/argmax; analogized to temperature in sampling. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T178])
- Subagent architecture key findings: subagents cannot spawn other subagents directly (file-mediated coordination routes around this). Escalation-while-running: subagent writes request file, continues testing its own reasoning, polls for primary reply. Reconstruction package format for mid-subagent branching: verbatim task + full reasoning trace + state at branch point + branch instructions + files read/written + do-not-repeat list. Write-as-you-go: FBC subagents write reasoning AS THEY GO so the log IS the reconstruction package. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T184])
- Depth calibration: primary's job is shallow/medium/deep routing, not supervision. N = minimum to resolve uncertainty. Time cost is parallel-flattened; token cost is N-linear regardless of parallelism. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T188])
- Claude.ai GitHub project injection discovery: GitHub-connected files are injected selectively and automatically by claude.ai, not on-demand. Cannot be pulled with view tool. Implication: skill design should say "flag if skill referenced but not visible in context" rather than assuming availability. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T152])
- GROUNDING-EXAMPLES.md created alongside harness-creator: three worked examples including one using consciousness framework question, plus four-step smoke-test. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T202])
- Docker/sandcastle triaged: Claude Code already uses Linux bubblewrap + macOS Seatbelt. Docker overkill for single-model trusted-subagent FBC harness. ([skills-master-wiki-pipeline-2026-05-01-bcafba:T166])

- **Venv decision for AI-assisted scripting (continuation, May-June 2026):** Don't enforce venv as default in Jon's context (solo, Windows, AI-assisted, one main repo). The forcing function for venv (Debian-based externally-managed-environment error) doesn't apply on Windows. Real material risk is version conflict between projects — hypothetical for one-repo setup. In AI-coding context, forgotten activate step is a common friction source (ModuleNotFoundError, packages split across environments, debugging unrelated to actual task). Recommendation: use system Python directly; add venv to a specific project only if a real version conflict emerges. Middle ground: keep requirements.txt per project as light hygiene (documents deps without enforcing isolation). ([skills-master-wiki-pipeline-2026-05-01-bcafba])
- **Two valid venv invocation patterns:** (1) `source venv/bin/activate` — for interactive sessions where you want `python`/`pip` to resolve correctly without typing paths; (2) direct path invocation (`./venv/bin/python script.py`) — for scripts, automation, cron jobs, where you don't want to source an activation script into a parent shell. Direct path invocation is the more robust pattern for `sync-universal.sh` or GitHub Actions calling pipelines programmatically. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

- **KV cache forking status (2026-06-25, msgs 213-214):** Arbitrary-point KV cache forking is not solved at the API level as of 2026-06. llama.cpp has slot save/restore (closest to true forking); prefix caching (available via Anthropic API) is real and functional but is not arbitrary-point forking — it only caches fixed prefixes. The gap matters for multi-agent orchestration: T-25 (KV cache branching) and the FBC verification gap both require the ability to fork context at an arbitrary point mid-generation, which prefix caching cannot provide. This connects to the FBC verification gap and explains why harness-based parallel subagent branching is the current workaround. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

## Entities & Concepts

[[wiki-master-skill]], [[frame-before-commit]], [[extraction-pipeline]], [[skills-system]], [[design-execution-split]], [[harness-creator]], [[skill-evolution-framework]]

## Conflicts

None — new content is additive to the initial session work. The harness-creator skill was updated multiple times in the same session; the subagent finding about "subagents cannot spawn other subagents" was corrected by Jon (file-mediated coordination routes around the constraint) and the harness skill updated accordingly.

## Delta Update — 2026-07-21 SU (from full re-export, UUID bcafba)

The 2026-07-19 export (`chat-2026-07-19-bcafba-skills-master.md`, 353K) is a **fuller-fidelity native-JSON re-export of this same conversation** (thinking blocks preserved), not a large continuation — the size is mostly preserved thinking, not new turns. Verified delta = a single new exchange after a 2+ month gap (turn 107, "over a month since our last chat"):

- **True arbitrary-point KV-cache forking is NOT solved at any hosted-API level** (Anthropic/OpenAI expose no KV state). What is production-deployed is **prefix-based KV-cache reuse** (Anthropic, vLLM, SGLang) — not forking. `llama.cpp` exposes a per-slot `/slot/save` save/restore (local-inference only); **Ollama does not expose it** in its high-level API. Memory is the hard blocker (a 128K context on a 70B model ≈ 40GB HBM for KV; six true forks ≈ 240GB — "a physics problem"). Named active research: KVShare, LRAgent, TokenDance, TokenCake (none user-facing).
- **Ruling:** the reconstruction-package approach already designed for the FBC harness ([[harness-creator]]) is the correct practical workaround; the harness step should be built **swappable** for KV-level forking once `llama.cpp` slot save/restore stabilizes and Ollama exposes it. Reinforces (does not conflict with) existing harness content.
- Also (borderline-prior venv turns): Jon should **not enforce venv** as a default on his solo/Windows/AI-assisted setup — keep a per-project `requirements.txt` without enforced activation.
- **Note:** the temporal-context skill mis-stamped the 07-19 re-engagement as "2026-05-06 (estimated)" — a ~2.5-month error, live evidence the elapsed-time placeholder needs calibration.