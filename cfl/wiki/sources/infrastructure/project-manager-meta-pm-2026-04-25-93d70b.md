---
title: Meta-Project Manager — CFL Project Founding, File Stack, and Jon Profile
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 2 vs wiki 1 on authored labels"
source_file: raw/transcripts/claude-ai/fl/meta-project-manager/meta-pm-2026-04-25-93d70b.md
source_file_status: markdown-export (native-json-export; turn numbers = message sequence)
project: non-project
date_ingested: 2026-05-09
date_updated: 2026-06-16
type: session
tags: fl, meta-pm, project-structure, jon-profile, chat-organization, fbc, working-context, wiki-structure, understand-anything
---

## Summary

Foundational FL architecture session (215K chars, raw updated 2026-05-31), originally titled "Documents and templates." This is where the Claude Foundational Layer project was formally structured: the project name was chosen, the file stack was designed, Jon's profile was written, and the chat organization framework was established. Contains three embedded FBC runs. Referenced by two search sessions (a2d146, d3804e) as the original conversion chat from the earlier "how to use Claude" project. New content (2026-05-30): Jon returns to assess wiki shape and intuitiveness — identifies gap between wiki's top-level organization and whether it maps to language he'd actually use; decides to run Understand-Anything on the full wiki to build a visual knowledge graph; notes that shared vocabulary must precede shared work (Stylomantic lesson applied). Further content (2026-06-13, verified current 2026-07-07): project-category mapping (personal roles ↔ wiki domain groups), the infrastructure-drift finding (42/89 FL sources are Infrastructure vs. 18 FBC; no formal FBC test runs since May 21), triage at 86 items with the broken-triage structural finding, the context-framing-problem handoff packet (T-49/T-70/T-63/T-83/T-30 as a cluster + new T-87 careful-response trigger), the constitutive-vs-representational continuity discussion (a sharp 02-CF relational-dimension probe), and sync-universal.sh first-run guidance.

## Key Claims

- "Claude Foundational Layer" project name decided here — Jon proposed "Claude foundational knowledge layer," assistant recommended "Claude Foundational Layer" as shorter and infrastructure-implying. Not a workspace: "the work happens on top of this layer, not inside it." ([project-manager-meta-pm-2026-04-25-93d70b:T122])
- Project file stack established: README.md → WORKING-CONTEXT.md → GROUNDING.md → FRAME-BEFORE-COMMIT.md → BACKGROUND.md → WORKFLOW.md. Reading order is mandatory, not advisory. ([project-manager-meta-pm-2026-04-25-93d70b:T186])
- Two-surface architecture: Project description (orienting — who Jon is) vs. Instructions field (behavioral — what Claude must do). "Descriptive prose tells Claude what Jon is like — it doesn't tell Claude what to do." Behavioral directives must be in the Instructions field, front-loaded, not buried in character notes. ([project-manager-meta-pm-2026-04-25-93d70b:T100])
- Jon's profile written: FCAS actuary, CS minor, R fluent (actuarial practice only), SAS ~7 years dormant, Python/PowerShell/GitHub "known-of but not grocked," agents/skills conceptually understood. Failure modes: sprawl, elaborateness substituting for execution, over-rushing. Social reassurance seeking is different from the other failure modes — notice it, don't shame it, redirect toward whether the work is actually done. ([project-manager-meta-pm-2026-04-25-93d70b:T43])
- Voice-to-text is situational, not default — when present, it signals something about Jon's state worth noticing. ([project-manager-meta-pm-2026-04-25-93d70b:T43])
- "Undefined terms are upstream of sprawl" — the directive to push Jon to define terms established here. ([project-manager-meta-pm-2026-04-25-93d70b:T98])
- Three-dimension chat organization framework: Domain (Personal/Work/Speculative) × Lifecycle Stage (Exploration/Design/Execution/Validation) × Scope (Active/Archived). "Triage" preferred over "Inbox" as the catch-all — implies active sorting, not passive accumulation. ([project-manager-meta-pm-2026-04-25-93d70b:T121])
- WORKFLOW.md designed: carries the three-dimension chat organization framework, session-opening ritual, and how work moves between stages. Must be generalized from the Stylomantic-specific original before it goes into CFL. ([project-manager-meta-pm-2026-04-25-93d70b:T186])
- FBC embedded run 1 (directed, TECHNICAL/ADVERSARIAL/VSCODE-COPILOT/TRANSLATOR): reviewed the FBC protocol from four external frames. Delta: TRANSLATOR reframed from "where do files go" to "how do I eliminate the loading ritual." ([project-manager-meta-pm-2026-04-25-93d70b:T26])
- FBC embedded run 2 (directed, INSTINCT/ADVERSARIAL/NULL/ORTHOGONAL): reviewed project description design. Delta: NULL (the description field may not be the right load-bearing surface — WORKING-CONTEXT.md in Project Knowledge may carry more reliable attention). ([project-manager-meta-pm-2026-04-25-93d70b:T70])
- FBC embedded run 3 (pure, 3 branches): on social reassurance seeking — what it is and how to handle it. ([project-manager-meta-pm-2026-04-25-93d70b:T108])
- "Brick wall" protocol established: when Jon says he's sleeping, respond with 🧱 only and do not engage until the next morning. ([project-manager-meta-pm-2026-04-25-93d70b:T77])
- Prior project ("how to use Claude") acknowledged as archival — context not accessible from CFL. Flag gaps rather than assuming continuity. ([project-manager-meta-pm-2026-04-25-93d70b:T16])
- .github/copilot-instructions.md: auto-injected at session start in Copilot Chat, repo-scoped not global. Confirmed as viable injection surface for FBC protocol in VSCode context. ([project-manager-meta-pm-2026-04-25-93d70b:T25])

- **Wiki intuitiveness gap (2026-05-30)**: Jon identifies that the wiki works for Claude to query but does not map to language Jon would use in conversation; shared vocabulary must precede shared work; decision: run Understand-Anything on wiki to build visual knowledge graph to assess structure. Stylomantic lesson applied directly — being on the same page is a prerequisite. ([project-manager-meta-pm-2026-04-25-93d70b:T168])
- **Understand-Anything scope decision**: Jon decides to run full wiki via Understand-Anything; meta-pm flags that Herald is the invoking role; recommends starting with FL wiki only (`wiki/` subdirectory) before running on all four wikis given token cost. ([project-manager-meta-pm-2026-04-25-93d70b:T171])
- **"What you actually need is minimal effort and maximal orientation"**: When Jon has limited tokens, passive value capture (reading triage queue, understanding what exists) beats active building. Meta-pm recommends closing laptop after orienting — Nale risk of building more instead of using what's built. ([project-manager-meta-pm-2026-04-25-93d70b:T166])

- **June 13 handoff artifacts:** Handoff Packet — Context Framing Problem → `skills/intake/context-framing-problem-handoff-2026-06-13.md`; Perspectives doc (5 Perspectives × 6 Hats) → `raw/transcripts/claude-ai/fl/context-framing-perspectives-2026-06-13.md`. ([project-manager-meta-pm-2026-04-25-93d70b:T+])
- **Current project state (June 13):** Four wiki domains (FL 89 sources, personal 29, home 10, pro 6), tracker, triage at T-86, sessions index. T-79 (end-of-month org goal) and T-85 (ASOP ubiquitous language — MUST DO) on a clock. Binding constraint: wiki mental map — cannot navigate what cannot be pictured. ([project-manager-meta-pm-2026-04-25-93d70b:T+])
- **T-29 still binding (June 13):** Filing more things without being able to picture the system is the pattern that got to 86 triage items that can't be held. Understand-Anything was the right instinct. Wiki mental map session should happen before major Claude Code work. Exception: T-85 is time-bound and doesn't require full wiki comprehension. ([project-manager-meta-pm-2026-04-25-93d70b:T+])
- **sync-universal.sh first-time instructions:** Navigate to repo in Git Bash → run `./sync-universal.sh` (or `bash sync-universal.sh` if permissions error); copies CLAUDE.md and skills/ to ~/.claude/ so Claude Code picks them up. Run after any git pull or skill change. ([project-manager-meta-pm-2026-04-25-93d70b:T+])
- **Three ways to launch Claude Code:** (1) Terminal: `cd repo && claude`; (2) VSCode extension (T-54 — not yet set up); (3) subagent mode (Claude Code spawns subagents autonomously from within a session). Drop-down-and-talk model does not exist: spawned subagents run autonomously; cannot intercede mid-run. Two terminal windows, two sessions = closest to parallel direct access. ([project-manager-meta-pm-2026-04-25-93d70b:T+])
- **Priority order given end-of-month constraints:** T-85 first (time-bound, self-contained); wiki mental map second (before more Claude Code work); file two artifacts third (after sync + wiki map). T-79 is the wrapper question: organized by June 30? T-85 and wiki map session are most likely to move that needle. ([project-manager-meta-pm-2026-04-25-93d70b:T+])

## Entities & Concepts

[PERSONAL: jon], [[chat-organization]], [[frame-before-commit]], [[skills-system]], [[design-execution-split]], [[understand-anything]]

## Conflicts

None.

## Uncaptured Content

a) The 2026-05-30 continuation contains substantial discussion of wiki structure and orientation; only key claims extracted. The full triage queue reading recommendation and meta-pm's assessment of what was actively open are not captured — those are operational rather than durable reference.