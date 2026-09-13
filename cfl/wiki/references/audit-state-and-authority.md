---
title: Audit State & Authority Demotion (G3 — ratified 2026-07-13)
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-REF; sub: no sub-branch evidence above the floor (best wiki 1 < 2; a lone corroborating tag does not decide)"
status: RATIFIED (Jon 2026-07-13). Belongs in repo CLAUDE.md audit-program section.
authored_by: claude-opus-4-8/wiki-master (CC session da51cc)
---

# Audit State & Authority Demotion (G3)

Ratified after v3.0 calibration found a ~86% error rate and that **anchored ≠ verified** (finding F3:
pages that already carried turn anchors had the *worst* citation integrity). A cold session must not
treat an unverified wiki claim as established fact. Every source page carries an `audit_state`, and its
authority is a function of that state.

## The three states (frontmatter `audit_state:`)
- **`unaudited`** — no program checks have run. Content is raw extraction; may contain factual errors,
  wrong/estimated anchors, dropped items, or config bleed-through. **Authority: provisional.**
- **`linted`** — structural/presence checks pass (sections, findability, fixity, `source_kind`, anchors
  *present*) but claims have **not** been verified against the source. **Anchored does not mean correct.**
  **Authority: structural only — claims still provisional.**
- **`verified@{standard-ver, date, source-hash}`** — every Key Claim was checked against the pinned raw
  (`source-hash`) at the named standard version and either confirmed or corrected; anchors resolved via
  the canonical turn-index. **Authority: full, as of that standard version + source hash.**

## Authority demotion rule (G3)
A page that is not `verified@{current}` has **demoted authority**:
- A session may *surface* its claims but must mark them **UNVERIFIED** — e.g. "the wiki records X
  (unverified — audit_state: linted)". It must **not** present them as established fact, and must not
  build a downstream decision on them without re-checking the source.
- `verified@{...}` claims may be cited normally, with the standard version + source hash as warrant.
- Re-verification is required when the standard bumps a VERIFY function (MAJOR) or the source hash changes.

Rationale: calibration proved ~5 of 6 audited pages carried material errors and that the "47% anchored"
cohort was the *least* trustworthy on citations. Treating anchored-but-unverified pages as reliable is
exactly the failure this program exists to remove.

## Canonical anchoring (paired requirement)
Turn anchors MUST be assigned/verified against `scripts/audit/turn_index.py` (deterministic header
enumeration → verified T-map + count), never estimated. This tool resolved the calibration's turn-count
disagreements and every workhorse's hand-built index exactly. An anchor that does not resolve in the
turn-index is a lint failure.

## Display / ledger
The conformance ledger records each page's `audit_state`; dashboards and retrieval surfaces show it, so a
reader always sees whether a claim is verified. `linted`/anchored never renders as `verified`.
