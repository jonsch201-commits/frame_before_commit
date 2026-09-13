---
title: Session-close 2026-07-07 backlog plan
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-AGENTMEM; sub: wiki 4 vs skills 0 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_session-close-2026-07-07-backlog-plan.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, backlog, triage]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: session-close-2026-07-07-backlog-plan
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Session-close 2026-07-07 backlog plan

*Source description:* Approved 2026-07-07 plan — backlog org scheme + Matt Pocock update protocol + next-session sequence; 3 Jon-confirmed decisions

2026-07-07 session close (background PM session). Approved plan lives at `C:\Users\JonSc\.claude\plans\ok-i-took-a-shimmering-heron.md`. Extends `HANDOFF-2026-07-08.md`.

**Jon-confirmed decisions this session:**
- **Matt Pocock upstream adoption** = a new `adopt-upstream` operation on the **skills-master** skill + a `skills/UPSTREAM.md` registry + provenance frontmatter (`upstream_repo/commit/pulled_date/local_changes`). NOT a standalone skill. The 4 vendored skills (grill-me, handoff, teach-me, reverse-grill-me) currently carry zero provenance and there is no fetch/diff/adopt mechanism.
- **Backlog organization** = BOTH a central PM registry (`wiki/tracker/backlog.md`) AND physical status subfolders under `skills/intake/` (`ready/`, `needs-design/`, `routed/`, `archive/`).
- **Sequencing** = a dedicated backlog-triage/archive session FIRST, then the handoff's skills-master formalization, then the Pocock protocol.

**Backlog reality:** `skills/intake/` holds ~71 packets, not "~4" — ~23 already-done (→archive), ~5 verify-then-archive, ~3 partial (keep), ~30 need Jon design, ~13 agent-ready. Dominant owners: wiki-master (~20), skills-master (~18).

**Immediate open:** PR #2 (DS-3 review sheet + PM ratification, branch `ds3-review`) — Jon approved, marked ready+mergeable, awaiting Jon's merge. Then Option A on `references/`: move `partial-sessions-registry.md` + `raw-file-standards.md` (recommend → `wiki/sources/infrastructure/`), delete `wiki/references/` and the DS-3 `wiki/archive/` dupes.

Related: [[active-work-state]] [[drive-lag-stale-read-hazard]] [[decision-scope-calibration]].
