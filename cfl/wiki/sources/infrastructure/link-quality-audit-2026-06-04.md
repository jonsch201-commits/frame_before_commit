---
title: Link Quality Audit — extraction-pipeline, skills-system, wiki-master-origin (2026-06-04)
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: sub-branch too close to call: wiki 6 vs corpus 6 (margin < 1)"
type: audit-log
date: 2026-06-04
purpose: Remove operational-footnote wikilinks from concept and source pages to reduce hub inflation on three over-connected concept nodes.
standard: Zettelkasten / Matuschak / Wikipedia navigation policy. Keep: conceptual, evidential, build-chain. Remove: operational/footnote ("I used B here").
---

# Link Quality Audit 2026-06-04

## Removals Log

### Sub-task A: [[extraction-pipeline]] removals

**Concept pages:**

- frame-before-commit → [[extraction-pipeline]] removed — operational/footnote: FBC is a reasoning protocol; no conceptual dependency on extraction-pipeline; mentioned in Related without explanation of why FBC requires understanding the pipeline
- skills-system → [[extraction-pipeline]] removed — operational/footnote: skills-system covers injection mechanisms, not extraction; link was a passing footnote
- stylomantic → [[extraction-pipeline]] removed — operational/footnote: Stylomantic is about logprob reweighting; no conceptual dependency on extraction-pipeline
- design-execution-split → [[extraction-pipeline]] removed — operational/footnote: design-execution-split covers claude.ai vs Claude Code split; extraction-pipeline not conceptually required to understand this
- loop-taxonomy → [[extraction-pipeline]] removed — operational/footnote: loop-taxonomy covers research loops; no conceptual link to extraction
- multi-agent-orchestration → [[extraction-pipeline]] removed — operational/footnote: multi-agent coordination patterns do not require extraction-pipeline to be understood
- understand-anything → [[extraction-pipeline]] removed — operational/footnote: the graph plugin concept has no conceptual dependency on extraction-pipeline

**Source pages:**

- llm-wiki-origin-2026-04-15 → [[extraction-pipeline]] removed — operational/footnote: LLM wiki origin doc is about three-layer architecture concept, not about the extraction mechanism
- wiki-master-cc-fl-wiki-completion-2026-05-09 → [[extraction-pipeline]] removed — operational/footnote: session is about wiki completion and export format discovery; extraction-pipeline not central
- UNCERTAIN-cfl-early-setup-2026-05-01-000a36 → [[extraction-pipeline]] removed — operational/footnote: session is about wiki infrastructure initialization; extraction not central
- skills-master-cc-restore-2026-05-08-f9cdf4 → [[extraction-pipeline]] removed — operational/footnote: role boundary fix and intake organization session; extraction not central
- skills-master-cc-intake-org-2026-05-07 → [[extraction-pipeline]] removed — operational/footnote: intake organization and role boundary session; extraction not central
- skills-master-role-architecture-2026-05-15-2e2c62 → [[extraction-pipeline]] removed — operational/footnote: role architecture session; extraction not central
- fbc-protocol-v2-2026-04-20-3ff2d9 → [[extraction-pipeline]] removed — operational/footnote: FBC protocol session; extraction mentioned in passing project-state discussion
- ai-mechanics-thinking-2026-03-23-a53ccf → [[extraction-pipeline]] removed — operational/footnote: thinking mechanics / temperature session; extraction-pipeline not mentioned or relevant
- discord-export-stylomantic-2026-03-22-57c322 → [[extraction-pipeline]] removed — operational/footnote: Discord data export for Stylomantic training data; unrelated to the CFL conversation→wiki extraction pipeline

---

### Sub-task B: [[skills-system]] removals

**Concept pages:**

- frame-before-commit → [[skills-system]] removed — operational/footnote: FBC is a reasoning protocol; understanding FBC does not require understanding skills-system

**Source pages:**

- llm-wiki-origin-2026-04-15 → [[skills-system]] removed — operational/footnote: LLM wiki origin is about the wiki pattern concept; skills-system is not central to that document
- wiki-master-m365-onedrive-2026-05-02-1371bc → [[skills-system]] removed — operational/footnote: M365/OneDrive wiki integration session; skills-system mentioned only in the context of "wiki concept applied to M365"
- wiki-master-cc-fl-wiki-completion-2026-05-09 → [[skills-system]] removed — operational/footnote: wiki completion session; skills-system not central
- triage-master-open-items-2026-04-28-090a56 → [[skills-system]] removed — operational/footnote: triage session covering open items and FBC thought-layer research; skills-system not central to session content
- fbc-protocol-v2-2026-04-20-3ff2d9 → [[skills-system]] removed — operational/footnote: FBC protocol session; skills-system mentioned in passing
- ai-mechanics-skills-clarity-2026-05-02-2d91af → [[skills-system]] removed — operational/footnote: brief reference session on AI skill stacks for clarity; no substantive skills-system content

---

### Sub-task C: [[wiki-master-origin]] removals

**Concept pages:**

- understand-anything → [[wiki-master-origin]] removed — operational/footnote: graph plugin concept has no conceptual dependency on wiki-master-origin
- citability-standard → [[wiki-master-origin]] removed — operational/footnote: citation format standard does not require wiki-master-origin to be understood
- loop-taxonomy → [[wiki-master-origin]] removed — operational/footnote: loop taxonomy covers research loops; no conceptual link to wiki-master-origin

**Source pages:**

- wiki-multi-master-audit-2026-06-02-dba2c0b → [[wiki-master-origin]] removed — operational/footnote: R1-R6 wiki improvements session; wiki-master-origin is the distant background motivation, not a central topic of this session

---

## Kept (representative — not exhaustive)

- claude-architecture → [[extraction-pipeline]]: KEPT — explicitly states "directly relevant to why the extraction-pipeline... pattern exists"
- ai-mechanics → [[extraction-pipeline]]: KEPT — context overhead modeling uses this concept
- wiki-master-origin → [[extraction-pipeline]]: KEPT — "the extraction-pipeline is the operational mechanism that feeds raw content into this pattern"
- wiki-ingest-methodology → [[extraction-pipeline]]: KEPT — explicitly cross-references extraction-pipeline for technical detail
- citability-standard → [[extraction-pipeline]]: KEPT — framing conflict between two pages was resolved here; citation format relates to pipeline output
- wiki-master-cc-t24-diff-ingest → [[extraction-pipeline]]: KEPT — diff-as-ingest directly about extraction/ingest pipeline
- data-master-pipeline-extraction → [[extraction-pipeline]]: KEPT — session IS about extraction pipeline
- loop-taxonomy → [[skills-system]]: KEPT — explicitly states "all skills-system updates after 2026-05-22 should use these canonical names"
- wiki-master-origin → [[skills-system]]: KEPT — wiki-master is part of skills-system; wiki-master-origin is the conceptual origin of that role
- extraction-pipeline → [[wiki-master-origin]]: KEPT — explicitly cross-references wiki-master-origin for the broader LLM wiki pattern
- claude-architecture → [[wiki-master-origin]]: KEPT — stateless architecture is the root constraint that motivated the wiki-master-origin pattern
- llm-wiki-origin-2026-04-15 → [[wiki-master-origin]]: KEPT — this IS the wiki-master-origin source document

---

## Post-Audit Verification (2026-06-08)

**Context:** Test-master retroactive grep (2026-06-08) confirmed 4 removals logged above were never executed. Wiki-master executed all 4 missed removals and ran full post-audit grep verification.

### Missed Removals Executed (2026-06-08)

| File | Link removed | Audit sub-task |
|------|-------------|----------------|
| `wiki/sources/infrastructure/wiki-master-cc-fl-wiki-completion-2026-05-09.md` | `[[wiki-master-origin]]` | Sub-task C |
| `wiki/sources/infrastructure/wiki-master-m365-onedrive-2026-05-02-1371bc.md` | `[[wiki-master-origin]]` | Sub-task C |
| `wiki/sources/infrastructure/skills-master-cc-restore-2026-05-08-f9cdf4.md` | `[[skills-system]]` | Sub-task B |
| `wiki/sources/infrastructure/UNCERTAIN-cfl-early-setup-2026-05-01-000a36.md` | `[[skills-system]]` | Sub-task B |

### Post-Audit Grep Results (2026-06-08)

Grep scope: `wiki/` directory, `.md` files only, excluding `link-quality-audit-2026-06-04.md` (this file), `log.md`, and `.understand-anything/` (JSON graph artifacts).

| Slug | Files with live links (post-remediation) | Notes |
|------|------------------------------------------|-------|
| `[[extraction-pipeline]]` | 24 files | Remaining links are all KEPT per audit log or post-audit source pages |
| `[[skills-system]]` | 27 files | Remaining links are all KEPT per audit log or post-audit source pages |
| `[[wiki-master-origin]]` | 9 files | Remaining links are all KEPT per audit log or post-audit source pages |

**Confirmation:** None of the 4 target files (`wiki-master-cc-fl-wiki-completion-2026-05-09`, `wiki-master-m365-onedrive-2026-05-02-1371bc`, `skills-master-cc-restore-2026-05-08-f9cdf4`, `UNCERTAIN-cfl-early-setup-2026-05-01-000a36`) appear in the post-remediation grep output for their respective removed slugs. All 4 removals verified complete.

Note: Pre-audit counts are not recorded in this audit log, so a precise delta comparison is not possible. The above counts reflect the current state after all intended removals (including the 4 missed ones) have been executed.
