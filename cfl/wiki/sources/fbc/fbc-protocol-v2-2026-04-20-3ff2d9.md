---
title: FBC Protocol v2 — Status Audit and Protocol Review
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: none
source_file_status: unrecoverable (Claude Code intake file deleted after wiki-master processing; stub only)
project: Claude Foundational Layer
date_ingested: 2026-05-11
type: session
tags: fbc, protocol, worktree, status-audit, v2
---

## Summary

Status audit session from the surface-before-commit worktree following handoff disorganization between claude.ai and Claude Code. Surfaced FBC protocol v2 updates (T-tag notation, counterfactual delta format, delta origin field NATIVE/RECONSTRUCTED/MIXED, ASOP 56 connection, test battery design) that existed in output files but had not been committed to the repo. Established baseline for v2 format and identified unresolved infrastructure gaps. This is the primary source for the delta origin field classification, which is not documented elsewhere.

## Key Claims

- **Delta origin field:** FBC deltas should be tagged NATIVE (emerged naturally during protocol run), RECONSTRUCTED (identified retrospectively after run completion), or MIXED (partially spontaneous, partially reconstructed) — this three-way classification distinguishes genuine protocol output from post-hoc narrative construction and is load-bearing for empirical validation
- **T-tag sub-thought notation confirmed:** B{n}T{k} format (B1T1, B1T2...) forces commit-before-continuing within a branch; introduced in skills-master-bcafba, validated in worktree context as producing thoughts that would not survive without forced separation
- **Counterfactual delta format:** "Without this branch, the commit would have said X; with it, the commit says Y" — provides auditable before/after rather than subjective "this branch was important"; adopted as the v2 standard format
- **ASOP 56 connection:** Actuarial Standard of Practice 56 (actuarial communication standards) requires explicit uncertainty quantification; FBC's [META] and [DELTA] serve an analogous function — identified as a disciplinary framework that validates FBC's core structure
- **Test battery design:** A formal battery of FBC test runs was scoped to evaluate protocol performance across invocation modes — pre-specified conditions, not post-hoc selection; basis for test-master sessions that followed
- **Project status finding:** Chat-to-code handoff had fragmented project state across multiple locations; no single source of truth existed for wiki state, raw files, and protocol document versions at time of session

## Entities & Concepts

[[frame-before-commit]]

## Conflicts

Delta origin field (NATIVE/RECONSTRUCTED/MIXED) is new — not previously documented in the wiki. T-tags and counterfactual delta format are already in [[frame-before-commit]] from skills-master-bcafba; this session confirms and extends, no conflict.

## Uncaptured Content

a) Verbatim session content not preserved — this was a Claude Code intake file deleted after wiki-master processing. A stub file now exists at `raw/intake/code-2026-04-20-3ff2d9-please-confirm-project-status-the-handoff-between.md`. Key Claims are the only surviving record of the session content.
b) N/A — original not available to identify dissolved tensions.
c) N/A — unfollowed threads cannot be identified without the verbatim session.