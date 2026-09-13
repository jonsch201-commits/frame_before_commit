---
title: "references/ genre split — admission rules (pre-migration)"
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-REF; sub: no sub-branch evidence above the floor (best wiki 1 < 2; a lone corroborating tag does not decide)"
source_kind: standard
maintained_by: coordinator
last_updated: 2026-07-28
authority: wiki/references/record-architecture-v1.md
status: PROSPECTIVE — the four directories named below do not exist yet; this file specifies the
  admission rule each will enforce once PR-D creates them and migrates `wiki/references/`'s current
  ~18 files into them. Single file for now because splitting into four README stubs would create
  four empty directories this PR is not scoped to create.
---

# references/ genre split — four coming subdirectories

`wiki/references/` is currently a flat catch-all — standing rules, dated audit records, live
registries, and four coexisting versions of the source-page standard, with no admission rule
distinguishing them (this friction is what the record-architecture project was ratified to fix — see
`record-architecture-v1.md` §"What this supersedes": *"the flat `wiki/references/` (→ four-genre
split)"*).

PR-D moves files into four genre subdirectories. Each genre has a one-sentence admission rule — the
test to apply before a file lands in it:

## `references/rules/`

**Admission rule: timeless, edited by ruling.** A rule doesn't have a publish date that matters —
it has a *current text*, amended in place when Jon rules again. No archive-by-date; the file's git
history is the archive. Example candidates from current `references/`: `efficiency-rules.md`,
conduct-rule material (R8/R10 per the 2026-07-28 train rulings).

## `references/records/`

**Admission rule: immutable, dated.** A record describes something that happened, on a date, and is
never edited after landing — corrections are new records that supersede, not silent rewrites.
Example candidates: `audit-census-2026-07-13.md`, `calibration-results-2026-07-13.md`,
`pilot-backfill-findings-2026-07-13.md`, `ratification-packets-g1-g2-g4-2026-07-13.md`.

## `references/registries/`

**Admission rule: live, `maintained_by:` required.** A registry is state that changes as the world
changes — it has an owner who keeps it current, not a publish date that freezes it. Every file in
this directory must declare `maintained_by:` in frontmatter (record-architecture-v1.md's L4 rule).
This PR seeds the first resident: `references/registries/trunks.md`. Other candidates:
`ingest-queue.md`, `lost-sessions-registry.md`, `partial-sessions-registry.md`,
`corpus-operations-taxonomy.md`.

## `references/standards/`

**Admission rule: one live version + archive.** A standard has exactly one current version at any
time; superseded versions move to an `archive/` subfolder rather than staying live alongside the
current one under a different version suffix. This directly fixes the "four coexisting standard
versions with no archive marker" friction that motivated the whole split
(`source-page-standard-v1.md` through `v4.md` currently all live in `wiki/references/` at once).
`record-architecture-v1.md` itself will land here once ratified into its final home
(`references/standards/record-architecture-v1.md` per its own frontmatter `status:` line).

---

## What this PR does NOT do

No files move in this PR. The four directories above do not exist on disk yet. This file exists so
the admission rule is decided and Jon-visible before the migration PR runs it — the migration PR's
job becomes mechanical sorting against these four sentences, not a second round of design.
