---
title: Cosmere Intent mechanic as a frame for Docker containment scope
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: no sub-branch evidence above the floor (best skills 1 < 2; a lone corroborating tag does not decide)"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-19-266e2a-magic-system-for-intent-clarification.md
date_ingested: 2026-07-19
type: session
tags: infrastructure, docker, skill-improvement, containment, j-layer
---

## Summary

Jon asks how Claude should ingest and clarify his intent from the corpus to improve skills, then uses
Brandon Sanderson's Cosmere "Command + Intent" magic mechanic as a frame, and asks how much of a proposed
autonomous corpus-improvement loop should run inside Docker. Claude proposes a correction-ledger extraction
(every override/correction mapped to the skill it implicates) as the concentrated intent signal, then draws
a three-way containment partition: execution containment (Docker) bounds what a process can touch;
instruction-layer containment (the ratification/"write it" gate) is what actually guards self-modification
of the skill layer, which Docker does nothing against; contamination containment (BGIsolation) is orthogonal
to both.

## Key Claims

- **Proposed practical step: a "correction ledger"** — a single extraction pass over the corpus mapping
  every instance where Jon overrode, corrected, or narrowed a Claude output to the skill it implicates,
  framed as the highest-concentration intent signal available (rest of corpus is "mostly confirmation")
  ([266e2a:T1]).
- **Cosmere frame adopted as a durable interpretive lens**: Jon's compressed prompts are "Command," Claude's
  job is recovering "Intent" before acting, and enumerate-before-commit is explicitly framed as "not
  Awakening on an under-specified Command" ([266e2a:T2]).
- **Three distinct containment types, not substitutable for each other** [REASON]: execution containment
  (Docker — bounds filesystem/network/resource access), instruction-layer containment (ratification/"write
  it" gate — guards against memetic propagation of self-modifying skill diffs), and contamination
  containment (BGIsolation — who sees what) ([266e2a:T2]).
- **Docker scoped to "the autonomous middle of the loop, not the ends"**: extraction, generation, grounding,
  diff-drafting, and eval runs → Docker (wiki mounted read-only, staging dir the sole writable surface,
  eval-ledger/canary content excluded from the mount entirely to prevent contamination); delivery to
  intake-triage → fine from inside the container; ratification and application of ratified diffs →
  must stay outside, supervised ([266e2a:T2]).
- **Explicit rejection of "Dockerize everything"**: applying diffs from within an autonomous container would
  trade Jon's visibility for a wall that doesn't guard the relevant surface — named as degrading the
  audit-surface principle while feeling like more containment ([266e2a:T2]).
- **Governance framing**: the loop is licensed to draft "Commands"; durable change to any agent-readable
  surface requires Jon's "Intent" (ratification); an architecture where the container's approval replaced
  Jon's would be class (ii) drifting toward class (iii) without the closed-list consent structure
  ([266e2a:T2]).

## Entities & Concepts

[[frame-before-commit]]

## Conflicts

None.

## Uncaptured Content

c) Threads mentioned but not followed: Claude offers to draft the correction-ledger extraction as a CC
packet spec pending Jon's "write it" — not actioned within this session.
