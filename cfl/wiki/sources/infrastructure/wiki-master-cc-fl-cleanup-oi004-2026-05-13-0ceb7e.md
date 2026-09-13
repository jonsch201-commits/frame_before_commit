---
title: Wiki Master — FL Wiki Cleanup, Phase 1 Execution, OI-004, and T-006
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 6 vs skills 0 on authored labels"
source_file: raw/transcripts/claude-code/fl/code-2026-05-13-0ceb7e-fl-wiki-cleanup-execution.md
source_file_status: markdown-export (claude-code-session; turn numbers = message sequence)
project: Claude Foundational Layer
date_ingested: 2026-06-08
type: session
tags: fl, wiki-master, phase-1, oi-004, stylomantic, fbc, t-006, artifact-preservation, delta-origin
---

## Summary

Major FL wiki session (181K chars, resumed after compaction). Completed: 9 intake files filled, 8 FL + 3 Pro wiki source pages written, 4 concept pages updated (frame-before-commit, extraction-pipeline, skills-system, stylomantic), index/log updated, commit 01f289f. Phase 1 planning session inventoried all open items into 5 groups (A–E) and 7 phases. Key triage item T-006 flagged: unpredictable agent behavior (renaming artifact folder without provenance verification) — named as structural gap requiring design session with explicit artifact preservation defaults. New Anthropic export (30-day window) delivered but processing held pending T-003 window check.

## Key Claims

- FBC delta origin field introduced (v2): NATIVE / RECONSTRUCTED / MIXED — new classification for whether a branch's delta was generated fresh or reconstructed from summary. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e:T12])
- ASOP 56 maps to FBC's [META]+[DELTA] structure — actuarial standard of practice for model risk maps onto FBC protocol. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e:T14])
- CDP extraction as third path: retrieves project_uuid from live claude.ai API; project-map.json is the output. Conversations.json gap: export does NOT include project_uuid. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e:T11])
- Stylomantic POC v0.1 findings: OOB dominance (73.5%), label leakage, channel softmax cancellation, Bühlmann-Straub credibility collapse. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e:T15])
- T-006 — unpredictable choices: When skills are underspecified, agents gap-fill with local context → inconsistent behavior → requires design session with explicit artifact preservation defaults. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e:T23])
- Post-Compaction Resume protocol added to SKILL.md: read index.md, SCHEMA.md, relevant concept pages, log.md BEFORE writing anything after compaction. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e:T8])
- 30-day export caveat: new Anthropic export is rolling 30-day window, not complete history — T-003 conversations may not be covered if older than 30 days. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e:T24])
- Provenance / KV-hash integrity: source zip files must be traceable to wiki claims before folder restructuring. ([wiki-master-cc-fl-cleanup-oi004-2026-05-13-0ceb7e:T25])

## Entities & Concepts

[[frame-before-commit]], [[extraction-pipeline]], [[skills-system]], [[stylomantic]], [PERSONAL: jon]

## Conflicts

None.
