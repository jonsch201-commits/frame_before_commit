---
title: project-map.json Audit — Triage Note
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 2 vs skills 0 on authored labels"
slug: project-map-audit-triage-2026-05-26
date: 2026-05-26
type: triage
status: OPEN — awaiting human review session
tags: project-map, citation-integrity, human-review-required
---

## What This Is

`raw/exports/project-map.json` maps conversation UUIDs to project names and conversation titles.
It was built from the Anthropic native data export (GDPR request). It is used by the citation audit
script to populate `project:` fields on all 102 wiki source pages.

**Current state:** 105 UUID entries. Used to set project: on 102 pages in the 2026-05-26 citation audit.

---

## Why It Needs Auditing

The map was built automatically from the Anthropic export without human verification of every entry.
Known issue surfaced in the 2026-05-26 audit:

- **1fe119** (Joseph/Elsa/Gift-Exile-Reunion framework) maps to "Claude Foundational Layer" despite
  the content being personal/creative analysis. This is technically correct — the session used 6 FBC
  runs and was held while in the CFL project — but it illustrates that project attribution reflects
  where the conversation was HELD, not what it was ABOUT.

Potential systematic issues:
1. Conversations held in the wrong project at time of chat (misrouted)
2. Non-project conversations attributed to a project (or vice versa)
3. The 5 "non-project" entries — do they need a project or is non-project correct?
4. The 1 "Claude Code session (Claude Foundational Layer)" entry vs. the 48 "Claude Foundational Layer"
   entries — is the distinction meaningful?

---

## What Human Review Looks Like

Jon scans the 105 entries in project-map.json for surprising attributions.
Specifically look for:
- Personal content in "Claude Foundational Layer" project (correct project?)
- Professional content in "Personal Life Questions" project (misrouted?)
- Conversations marked non-project that should be in a project
- Title and UUID pairs that don't match what you remember

Any corrections go back into project-map.json, and then the citation audit script must be re-run
to propagate corrections to wiki source pages.

---

## Priority

Low — the map is good enough for current use. Errors affect only the `project:` metadata field
on wiki pages, not the content of source pages. Run this when Jon has a quiet review session.

**Prerequisite:** project-map.json is at `raw/exports/project-map.json` (105 entries).
**Who does it:** Jon reviews, wiki-master re-runs citation audit if corrections are made.
