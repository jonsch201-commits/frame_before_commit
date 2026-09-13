---
title: Wiki Ingest Methodology — Routing, Thresholds, Negative Citation, and Update Protocol
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (wiki); sub: wiki 9 vs skills 1 on authored labels"
type: concept
first_seen: wiki-master-ingest-planning-2026-05-09-949f16
source_count: 6
last_updated: 2026-06-04
---

## What This Is

The policy and judgment layer for wiki ingest — distinct from the technical extraction pipeline. Covers routing decisions (which wiki a session goes to), ingest thresholds (what warrants a source page), Negative Citation (the standard for handling uncaptured content), the SKIP criteria (what invalidates a skip decision), and the op_update protocol for handling source changes after initial ingest.

See [[extraction-pipeline]] for the technical pipeline (scripts, fidelity, extraction paths).

## What the Wiki Says

### Routing Rules

Primary routing signal is claude.ai project assignment. Secondary signals: session content and domain.

| Source type | Destination |
|-------------|-------------|
| FL research, infrastructure, protocol work | FL wiki (`wiki/sources/[domain]/`) |
| Personal life, reflection, reference | Personal wiki (`wiki/personal/sources/`) |
| Professional work (actuarial, domain) | Pro wiki (`wiki/pro/sources/`) |
| Home tech, hardware, config | Home wiki (`wiki/home/sources/`) |
| Session with FL cross-reference in personal context | Write to personal wiki; add cross-reference in FL concept page |

Unassigned conversations (those without a claude.ai project assignment) require manual screening before routing — not automatically personal. ([wiki-master-ingest-planning-2026-05-09-949f16])

### Ingest Thresholds by Wiki

**FL wiki:** Standard — any FL research, infrastructure, or protocol session.

**Personal wiki:** Higher bar — session merits a source page if it contains a named research idea, FL concept invocation, recurring reference value, or shows reasoning that explains an FL decision. Do NOT ingest: logistics, hotel search, tech support.

**Home wiki:** Lower threshold for operational sessions — ingest any session containing hardware specs, device config, warranty status, wiring/network config, open service tickets, or completed repairs. Do NOT ingest: one-time travel logistics, UI procedures that change with software updates, unresolved troubleshooting with no durable specs.

([wiki-master-ingest-planning-2026-05-09-949f16], SCHEMA.md)

### Valid and Invalid SKIP Reasons

**"Operational" was retroactively invalidated** as a SKIP reason in skills-master-intake-grill-2026-05-27-e52ed2. Five health/family/life sessions had been incorrectly skipped for months under this justification.

**Valid SKIP reasons** (use sparingly):
- Truly trivial: 2-3 messages, zero durable information, complete in a single exchange
- Exact duplicate: content already captured in an existing source page with better coverage
- Pure UI procedure: step-by-step instructions for a product feature that changes with updates

**Invalid SKIP reasons**:
- "Operational" — if session contains a decision, fact, reference, or pattern useful later, ingest it
- "No FL cross-reference" — personal/home sources don't need FL connections
- "Too short" — short sessions can contain high-value reference data
- "Content seems minor" — wiki-master cannot judge lifetime value at ingest time

When in doubt: ingest and find a category. A source page with a thin summary is better than a missed record. ([skills-master-intake-grill-2026-05-27-e52ed2])

### Negative Citation Standard

Established in skills-master-intake-grill-2026-05-27-e52ed2 (T24). Official term: **Negative Citation**. Two types:

- **Type 1 (Inward Gap)** — source content not represented in any Key Claim. Addressed by the `## Uncaptured Content` section using the four-category taxonomy:
  - (a) Unfollowed threads
  - (b) Dissolved tensions
  - (c) Absent technical details
  - (d) Epistemic gaps
  
  Omit the section only if all four are genuinely empty. Never write N/A.

- **Type 2 (Outward Gap)** — a Key Claim with no outward cross-link to any concept, entity, or analysis page. Orphaned claim. Made visible at ingest via the orphaned claims check (step 4e in SKILL.md). Not all orphans require concept pages — the check makes the gap visible.

All new ingests must run the full Type 1 taxonomy. No shortcuts, even for short sessions. ([skills-master-intake-grill-2026-05-27-e52ed2])

### Citation Quality Vocabulary (optional)

When annotation granularity is needed, Key Claims may include a quality tag:

| Tag | Meaning |
|-----|---------|
| verbatim | Direct quote or near-verbatim |
| paraphrase | Faithful, semantics preserved, wording changed |
| reconstructed | Logical inference from what was said, not directly stated |
| contextual | Derived from surrounding context, not a single attributable message |

Format: `- **Claim text** [quality, timestamp]`. Currently optional — Jon to decide if required. ([wiki-master SKILL.md update 2026-06-04])

### Source Page Schema Standards

Confirmed 2026-05-27 (e52ed2 triage):

| Section | Status | Rule |
|---------|--------|------|
| `## Summary` | Required | Always present |
| `## Key Claims` | Required | Always present |
| `## Conflicts` | Required | Always present; write "None" explicitly if none |
| `## Entities & Concepts` | Conditional | Include when 2+ named entities/concepts appear |
| `## Cross-Wiki` | Conditional | Include when source connects to a different wiki |
| `## Uncaptured Content` | Conditional | Include when material content was excluded |

Conditional sections are omitted when conditions not met. Never written as placeholders or N/A.

`source_file_status` three-state field: OK (path given and resolves), BROKEN (path given but doesn't resolve), UNRECOVERABLE (source verifiably absent). ([skills-master-intake-grill-2026-05-27-e52ed2])

### op_update — Diff-as-Ingest Protocol

Proposed by wiki-master in wiki-master-cc-t24-diff-ingest-2026-05-09-b60686 (T10). When a raw source is modified after initial ingest:

1. Receive the diff, not the full file (re-ingesting full file risks overwriting valid synthesis)
2. Identify affected pages by citation slug lookup (`grep -r "source-slug" wiki/`)
3. Log the event: `update | [source-slug] — diff received / Changed: [...] / Affected pages: [...] / Status: flagged for review`
4. Mark affected pages: `⚠️ STALE-CHECK: source [source-slug] updated [date]. Review citations.`
5. Auto-rewrite of affected pages explicitly rejected — flagging and logging preserves ability to assess before acting

Multiple diffs before review: accumulate per-event log entries; staleness flag notes most recent update date. pipeline.py detects whether file has prior ingest record and branches: new file = op_ingest, changed file = op_update. ([wiki-master-cc-t24-diff-ingest-2026-05-09-b60686])

### Intake-Review Gating Operation

intake-review is a mandatory gating operation — approval and ingest are always separate explicit steps. Files deposited to `raw/intake/` are never auto-ingested. Wiki-master: lists all files, reads each, checks compliance against raw-file-standards.md, states APPROVE/NEEDS-FIX/DENY per file, presents results, waits for Jon's direction. ([skills-master-cc-restore-2026-05-08-f9cdf4])

### Phase-Based Ingest Strategy

R1-R5 and R6 were the ingest phases for the multi-master wiki improvement operation (2026-05-31/06-01). R6 specifically addressed citation annotation (adding T-tags to source pages with non-standard-format exemptions). The phased approach: extract sessions by domain, write source pages, update concept pages, annotate citations. ([wiki-master-phase3-subagent-log-2026-06-01-ad8e70])

## Conflicts

⚠️ POTENTIAL CONFLICT: SCHEMA.md says "page creation threshold: central to this source OR appears in 2+ sources" while SKILL.md implies higher scrutiny. No active contradiction — SCHEMA.md threshold applies to entity/concept pages, not source pages.

## Related

[[extraction-pipeline]], [[wiki-master-origin]], [[skills-system]], [[multi-agent-orchestration]]
