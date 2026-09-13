---
title: Wiki T-24 — Diff-as-Ingest and Judgment Project
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 8 vs skills 0 on authored labels"
source_file: raw/transcripts/claude-ai/fl/chat-2026-05-09-b60686-wiki-structure-and-organization.md
project: Claude Foundational Layer
date_ingested: 2026-05-13
type: session
tags: wiki-infrastructure, t24, diff-ingest, op-update, judgment, wiki-improvement
source_file_status: OK
supersedes: [wiki-t24-diff-ingest-2026-05-09-b60686]
---

## Summary

Jon and wiki master work through T-24: treating git push diffs as primary raw sources for the wiki change log. Session produces a formal wiki master proposal for `op_update` (diff-based ingest), and frames "wiki improvement" as a category with "judgment" (surfacing model uncertainty and known failures) as a project within it.

## Key Claims

- **T-24 gap:** `pipeline.py` ingests full files only; no diff capture anywhere. When a raw source updates after initial ingest, wiki pages citing it become silently stale. This is a validity failure, not a logging gap. ([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686:T8])
- **op_update design (wiki master proposal):**
  - Receive the diff, not the full file — re-ingesting the full file risks overwriting valid synthesis
  - Identify affected pages by citation slug lookup (`grep -r "source-slug" wiki/`) — cheap and already implied by the citation format
  - Log event explicitly with format: `update | [source-slug] — diff received / Changed: [...] / Affected pages: [...] / Status: flagged for review`
  - Mark affected pages with `⚠️ STALE-CHECK: source [source-slug] updated [date]. Review citations.` — flag persists until wiki master explicitly clears it during review
  - Auto-rewrite of affected pages explicitly rejected: flagging and logging preserves ability to assess before acting
  ([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686:T10])
- **op_update vs op_ingest distinction:** New file = full ingest (op_ingest). Changed file = diff ingest (op_update). pipeline.py detects whether file has prior ingest record and branches. GitHub Action needs no changes. ([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686:T8])
- **Multiple diffs before review:** Accumulate per-event log entries; staleness flag notes most recent update date. Change history reconstructable from log. ([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686:T10])
- **Wiki improvement as category:** Named category in wiki structure for meta-level improvements to wiki operations and reliability. ([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686:T6])
- **Judgment project concept:** A project within wiki improvement. Goal: surface when model intuition is likely wrong, when misalignment is probable, when the answer is certain vs. uncertain. Three possible inputs: documented confident failures, domain reliability flags, real-time uncertainty self-reporting. Design questions left open for Jon: granularity of domain-reliability.md, who triggers known-failures.md writes, whether judgment gets its own lint pass. ([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686:T6])

## Entities & Concepts

[[wiki-master-origin]], [[extraction-pipeline]]

## Conflicts

None. T-24 gap confirmed: nothing in existing code handles diffs, staleness detection, or update vs. ingest branching.