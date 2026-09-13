---
title: Project Manager — Repo Naming, Architecture Decisions, Skill Loading, and Voice Notes Pipeline
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: sub-branch too close to call: skills 3 vs fleet 3 (margin < 1)"
source_file: raw/transcripts/claude-ai/fl/project-manager/project-manager-2026-04-30-f8cc02.md
source_file_status: markdown-export (native-json-export; turn numbers = message sequence)
project: Claude Foundational Layer
date_ingested: 2026-05-16
date_updated: 2026-06-15
type: session
tags: fl, project-manager, repo-naming, surface-before-commit, architecture, skills, fbc, obsidian, voice-notes
---

## Summary

Project Manager role session (146K chars). Date range: 2026-04-30 through 2026-05-09 continuation. Key outcome: "surface-before-commit" chosen as the repo name via FBC run. Three FBC runs embedded. Architecture decisions: one repo, wiki first; three-layer clarity (claude.ai project vs. skills repo vs. wiki repo); skill loading tier design (critical in project files, reference in repo). SESSION-ORDER-SKILL.md canonized as the guaranteed loading chain. "Branches as thoughts" insight and Calvin and Hobbes meme as FBC failure mode exemplar. Continuation adds Obsidian/voice notes sync design via GitHub.

## Key Claims

- "surface-before-commit" chosen as repo name — "surface" names the goal (making pre-commit content visible before it hardens) rather than the mechanism (branching), making it extensible to methods other than FBC; ML resonance: surfacing latent structure before committing to a representation. Jon proposed; assistant confirmed stronger than all its own candidates. ([project-manager-architecture-2026-04-30-f8cc02:T12])
- One-repo decision: wiki first, no feature creep, nothing else until wiki is running and 3-4 real ingests complete. ([project-manager-architecture-2026-04-30-f8cc02:T1])
- Three-layer clarification: (1) Claude.ai project — FBC protocol docs, working context, grounding; (2) skills repo — raw skill files, operational tooling, pipeline; (3) wiki repo (surface-before-commit) — compounding knowledge artifact. Skills Master owns the skills repo; Project Manager owns sequencing. ([project-manager-architecture-2026-04-30-f8cc02:T107])
- "Branches as thoughts" parallel established: each branch is akin to a thought; the protocol gives the ability to direct what might be described as the model's thoughts before they harden into language. The repo is infrastructure for making thinking visible and persistent — not just conclusions. ([project-manager-architecture-2026-04-30-f8cc02:T10])
- Skill loading tier architecture: critical skills (guaranteed every session) → must be in project files, referenced from SESSION-ORDER-SKILL; reference skills (available on demand) → repo is sufficient. Memory cannot hold skill files — it's a short lossy summary. ([project-manager-architecture-2026-04-30-f8cc02:T99])
- SESSION-ORDER-SKILL.md loading chain: Instructions → README → SESSION-ORDER-SKILL → conditional/reference files. Adding one line to SESSION-ORDER-SKILL makes a repo skill effectively guaranteed-available. ([project-manager-architecture-2026-04-30-f8cc02:T68])
- Calvin and Hobbes meme analysis: identified as exact opposite of Jon's trained thinking and as an FBC failure mode exemplar — premature closure via simple taxonomy; System 1 wearing System 2 costume; branches and immediately commits with no META, no NULL branch questioning whether the two-bucket premise is malformed. ([project-manager-architecture-2026-04-30-f8cc02:T19])
- Project Manager role boundary: project structure, sequencing, communications, feature creep prevention, context hygiene. Does NOT own skills (Skills Master lane). ([project-manager-architecture-2026-04-30-f8cc02:T16])
- Three FBC runs: directed (FUNCTIONAL/IDENTITY/ADVERSARIAL/NULL — first naming pass), pure (ACCUMULATION/INFRASTRUCTURE/DOUBLE-MEANING/COMMITTED-LAYER — second naming pass with repo context), directed (PRECISION/POETIC/FUNCTIONAL/NULL — on `thought-direction-layer` vs. other candidates). ([project-manager-architecture-2026-04-30-f8cc02:T2])

- Voice notes pipeline design (continuation): Voicenotes app (phone) → Voicenotes Sync plugin (Obsidian desktop) → git push to GitHub → Obsidian mobile pulls from GitHub via GitHub app. Each step either already working or one install away. Recommendation: same repo as wiki (raw/personal/ or raw/voice/), not separate vault. Obsidian-git plugin identified as the sync mechanism. ([project-manager-architecture-2026-04-30-f8cc02:T115])

- **Austin Starks video analysis — Packet E (June 11 continuation):** Four-project video assessed against CFL. Verdict per project:
  - Board of Advisors (role structure): Jon already done better (Soul, Guide, Exchequer, Herald with explicit contracts). Two genuine gaps: (1) **content ingestion for roles** — Jon's roles are contract-defined from first principles; Austin's are content-trained from real people; ingesting thinkers Jon trusts into roles could meaningfully improve outputs; (2) **`/ask the board` unified multi-role query skill** — Jon's roles are separate chats, not a single skill that loops through all simultaneously. Board of advisors pattern reframed: perspective sourcing for deep FBC runs using real-world frames with actual content behind them.
  - Niched Command Center: personal domain gap; Exchequer is the natural home for personal finance tracker; gated behind Judge of Finance Philosophy (Packet C prerequisite). Maps to OI-014.
  - AI-Optimized Personal Website: Not needed. Skip.
  - Internal Operating System: Jon is ahead structurally. Two specific gaps: (1) **`/improve system` slash command** — after good output, captures what changed and updates relevant skill file automatically; formalizes the correction-to-skill-update loop that currently exists only informally; (2) ingest resource skill UX (minor improvement to wiki-master).
- **Packet E created:** Skills Master packet covering three additions: content ingestion pattern for role training; `/ask the board` equivalent (unified multi-role query skill); `/improve system` as formalized slash command. File: `PACKET-E-skills-master-austin-video-additions.md` (created in session output).
- **Nehemiah framing (Jon, June 11):** "We must not build for you a tower of Babel, but a framework that can use true external feedback and can identify sources of good judgment." Nehemiah metaphor: build the wall section by section, each person working their own gate — infrastructure, not a monument. Applied to board of advisors: add content behind the roles rather than scaling the structure. ([project-manager-architecture-2026-04-30-f8cc02])

## Entities & Concepts

[PERSONAL: jon], [[frame-before-commit]], [[design-execution-split]], [[skills-system]], [[surface-before-commit-repo]]

## Conflicts

None.