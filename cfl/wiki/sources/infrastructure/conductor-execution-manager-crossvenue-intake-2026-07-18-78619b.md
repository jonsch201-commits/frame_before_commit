---
title: Conductor role, Execution-Manager role, and cross-venue intake — design packet (PARTIAL)
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 8 vs skills 3 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-19-78619b-conductor-role-design-and-cross-venue-intake-packe.md
date_ingested: 2026-07-19
type: session
tags: infrastructure, coordination, multi-agent-orchestration, fbc, skills-system
source_file_status: partial-artifact-missing
---

## Summary

Jon dispatches a fresh claude.ai "planner" instance — deliberately not the 11-day da51cc session, to avoid
the same self-review conflict skills-master's own SKILL.md names — to design three things as one intake
packet: a **Conductor** role (portfolio-level scheduler/router across 28 skills, propose-only, never
executes), an **Execution-Manager** role (single-work-packet orchestrator, ruled its own thin role rather
than a Conductor mode), and a **cross-venue intake extension** letting claude.ai sessions formally deposit
into `skills/intake/`. Claude runs FBC first per Jon's method requirement, delivers the full packet plus a
paste-ready launch runbook as downloaded artifacts, then works through two follow-up turns on launch timing
and exact session/model/mode parameters for a four-step rollout (S1 draft, M2 da51cc flush, M3-A/B
acceptance tests).

## Key Claims

- **FBC finding: the Conductor gap is real but narrower than the invocation frames it.** Existence stands on
  skills-master's own SKILL.md pre-registration (predates da51cc, so isn't that session's framing artifact).
  Size does not stand on da51cc's observed workload — an 11-day session is itself a hygiene violation (the
  close ritual exists to prevent exactly this), so importing its accumulated scope into the role definition
  would institutionalize a protocol failure. Delta: define Conductor minimally and session-bounded, ship with
  an override-rate demotion path and an unconditional session registry regardless of which reading holds
  ([78619b:T2]).
- **Execution-Manager ruled its own role, not a Conductor mode** — the planner/executor separation is named
  as the one fence that must not erode; mode boundaries drift under load (the 11-day session *is* that
  drift), while role fences with a mutual-exclusion rule (a session wears Conductor or EM, never both) hold.
  Cost: one extra file, ~5 review-minutes ([78619b:T2]).
- **Conductor boundaries, explicit**: never writes to `skills/`, `wiki/`, or `wiki/tracker/`; drafts registry
  lines for PM to append (registry proposed at `wiki/tracker/sessions.md`, PM-owned); never spawns executor
  sub-sessions; never modifies its own SKILL.md; never auto-runs on session open (requires explicit
  invocation); proposes and routes only — merge/commit authority stays with Jon at every gate ([78619b:T2]).
- **Closing da51cc has a three-step precondition (M1→M2→M3)**: M1 = Jon ratifies + skills-master writes/pins
  paths; M2 = da51cc runs its close ritual and flushes state under a facts-not-recommendations rule (da51cc
  may not author or "correct" the new role definition — conflict of interest — but may list "practices I
  performed that the new definition excludes" as facts, not recommendations); M3 = a fresh cold session,
  given the definition alone, produces a plan Jon wouldn't reorder more than one of the top three items on —
  the operationalized success criterion ([78619b:T2]).
- **Budget amendment mid-session**: original ~55-minute one-time estimate missed a separate cost for M2 (an
  11-day session's state flush is not a normal close ritual); amended to **~80 min one-time, ≤6 min/week
  steady-state**, with a kill-check at 4 weeks (override-rate >40% demotes Conductor to a checklist; registry
  survives demotion) ([78619b:T8]).
- **Concrete rollout table delivered** (4 steps: S1 draft A+B(+C) / M2 flush / M3-A conductor test / M3-B EM
  test), each with model (Sonnet 4.6 throughout — content pre-drafted, errors diff-visible at Jon's gate, cost-
  of-error routing argues against paying Opus rates), mode (no plan mode anywhere — the packet's own §0 is
  the plan), and Jon-minutes per step ([78619b:T8]).
- **Session self-identifies its place in a larger sequence**: "MESSAGE 3 (the PLANNER)" in what Jon's prompt
  calls "the Fabel project skill/et al improvement plan," with "MESSAGE 4" described as a subsequent "blind
  sitting" (a bare Fable session without project context or memory) — Claude explicitly does not have the
  phase 1/phase 2 definitions in context and answers conditionally rather than guessing ([78619b:T6]).

## Entities & Concepts

[[frame-before-commit]], [[skills-system]], [[multi-agent-orchestration]]

## Conflicts

⚠️ CONFLICT — possible naming/scope overlap, not resolved by wiki-master: `wiki/index.md` records a
**"Coordinator role — ADOPTED"** via `exchange/coordination-plan-2026-07-19.md` (PR #50, merged 2026-07-19),
described as holding five standing duties (hold the map, dispatch AFK lanes, batch HITL, enforce the codex,
close loops and measure). This session (dated 2026-07-18, one day earlier) independently designed a
**"Conductor"** role via FBC with an overlapping shape (portfolio-level scheduler/router, propose-only,
session registry) — routed to `skills/intake/` for skills-master, not the same artifact that produced the
merged Coordinator plan. Whether "Conductor" (this packet) and "Coordinator" (the adopted plan) are the same
initiative under different names, one superseding the other, or genuinely parallel designs is **not
determinable from this session alone** and is flagged to the coordinator/Jon rather than resolved here.

## Uncaptured Content

a) **Delivered artifacts absent from export — PARTIAL, matching the precedent already logged for `3ee22d`**:
this session created and delivered two file artifacts — `conductor-em-crossvenue-intake-2026-07-18.md`
(the full intake packet: FBC run, proposed SKILL.md content for Conductor and Execution-Manager, cross-venue
intake template, V1–V7 arrival-verification checklist) and `launch-runbook-conductor-em-2026-07-18.md` (the
paste-ready runbook). Neither file was found anywhere in the repository at ingest time (checked `raw/`,
`skills/intake/`, full-text filename search). The Key Claims above are reconstructed from the chat's spoken
summary of the packet's contents, not read from the packet itself — recovery action open, same as `3ee22d`.
b) Unfollowed thread: Jon's tail line in the opening message ("merge #40 and #39... read the OpenWiki
packet... draft the Fable-max launch message") is explicitly read by Claude as Jon's own action item, not
this session's — no resolution tracked here.
c) Absent technical detail: the actual content of the proposed Conductor and EM SKILL.md files (structure,
YAML frontmatter, operations list) is described only in outline via the chat summary, not verified against
the source artifact per (a) above.
d) **Citation correction (2026-07-24 backfill pass):** the turn anchors on the seven Key Claims bullets above
were previously off by one or more turns (misattributed to T1/T2/T3 for content that verified reading of the
raw `## Human` / `## Assistant` sequence places at T2, T6, and T8). Corrected in this pass; every anchor was
re-verified against the raw file's turn boundaries before being applied.
