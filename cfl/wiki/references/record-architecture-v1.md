---
title: "Record Architecture v1 — the L0–L4 map"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 5 vs fleet 2 on authored labels"
source_kind: standard
retrieval_key: record-architecture
status: RATIFIED — Jon, 2026-07-28 evening, session 0fb7ca ("I approve, pending review of full
  structure" → L0–L4 walked and approved layer by layer → "I approve"). This document is the
  full-structure artifact that approval names. Destination after the references/ genre split:
  references/standards/record-architecture-v1.md.
ratified_by: Jon, 2026-07-28, CC session 0fb7cad8
maintained_by: coordinator; amendments are decision-grain PRs
---

# Record Architecture v1

## Purpose

One system of record for everything Jon and Claude produce together, organized so that any file's
home is derivable from three questions and any claim's provenance is walkable by one key.

Jon, 2026-07-28 — **[PARAPHRASE — UNVERIFIED]**, relayed via Herald: *"There was a part of me that
knew that these challenges with your knowledge base would happen eventually… my hope is that this
will ultimately be great educational material."* ⚠️ **Attribution corrected 2026-07-30.** This was
rendered as a near-verbatim quote; the string has **zero occurrences anywhere in `raw/`** and its only
source is an agent-authored file (`exchange/herald-thoughts-on-memory-transcripts-2026-07-28.md:16-19`).
Under R1 a relayed paraphrase may not be presented as a marked quotation. **The substance of this
section is unchanged and still ratified** — only the provenance label is corrected. If Jon confirms he
said something to this effect, this becomes a capture gap to close rather than an attribution to drop.
**The record is a curriculum, not only a ledger** — it is kept for
future readers (Claude instances, Jon, eventually family) learning how this was built, including
honestly-kept failures AND the Feast Record of what worked.

## The three coordinates

Every artifact answers: **LAYER** (how digested), **DOMAIN** (whose life: trunk → branch →
sub-branch), **VENUE** (how captured — matters only at L0/L1, collapses to frontmatter above).
The **uuid6 is the join key across all layers.** Coordinates live IN the file (frontmatter);
folders are a checked projection; `references/registries/trunks.md` (formerly TRUNKS.md) is the
single vocabulary registry. An instrument verifies registry ⇌ frontmatter ⇌ folder.

## The five layers

| Layer | What | Where | Axis |
|---|---|---|---|
| **L0 originals** | immutable capture artifacts | `raw/originals/` | venue → mechanical only |
| **L1 transcripts** | verbatim extracts + sidecars | `raw/transcripts/` | venue → trunk → branch → [sub-branch] |
| **L2 summaries** | source pages (full / delta / stub) | `wiki/[{trunk}/]sources/` | domain → branch |
| **L3 synthesis** | concepts, rules, standards, records | `wiki/concepts/<kind>/`, `references/{rules,standards,records}/` | domain → genre/kind |
| **L4 state** | trackers, registries, queues | `wiki/tracker/`, `references/registries/`, intake lanes | domain; `maintained_by:` required |

Side rails (not layers): `exchange/` (correspondence, delivery-only, consumer rule both ends);
`skills/` + agent definitions (behavior, skills-master's domain).

## L0 rules

- Single root `raw/originals/`: `claude-ai/exports/`, `claude-code/{jsonl,history}/`, `audio/`,
  `documents/`, `external/`, `LEDGER.md` (append-only, hash/size/date/completeness per artifact).
- **Mechanical axes only** (venue, project-dir, year). Never semantic — L0 artifacts are
  containers, many-to-many with conversations; the join is the LEDGER, not the path.
- **L0 holds either the bytes or a dated claim about where the bytes live** — `external/` pointer
  records (URL/ISBN/location + retrieved-date + hash of any local capture) for YouTube, audiobooks,
  physical documents. Captures land in `audio/`/`documents/` beside their pointers.
- Append-only; partial/defective originals kept and marked (a defective original is still an
  original). SU standing step: refresh JSONL copies, snapshot `history.jsonl` dated, append ledger.

## L1 rules

- Tree: `raw/transcripts/{claude-ai,claude-code,external}/{fl,personal,pro,home}/<branch>/[<sub-branch>/]`
  plus `_routing/{incoming,ambiguous}/` per venue and shared `_superseded/`.
- Names: `chat|code|ext-<uuid6>-<slug>.md` — **date in frontmatter, never filename**; slugs
  correctable (uuid is the key). Sidecars adjacent, same basename.
- One file, one home (primary branch); multi-branch in frontmatter (`branch:` list, files under
  first). Dual-relevance is an L2 cross-link, never an L1 copy.
- `_routing/incoming` = parser-owned; `_routing/ambiguous` = judgment-pending with
  `routing_question:` in frontmatter; both drained every SU, >14 days flagged.
- Fences: never-shrink; read-only to all agents except the parser; honest per-block fidelity
  stamps (readable / summary-only / signature-only).

## Depth and growth rules (all layers)

- **Depth cap: venue/trunk/branch/sub-branch — four levels.** Finer detail rides frontmatter (`arc:`).
- **Branch genres, marked in the registry:** PROJECT (completable), STANDING SUBJECT (never done),
  META-BRANCH (the system tending that trunk — fl→cfl, personal→planning; one per trunk, max).
- **Depth-on-demand:** flat until ~30 files (growth-intent trigger), then split using registry
  names. The trigger is simultaneously the sub-branch trigger and the L2 split trigger.
- **Fold on the single-valued coordinate; frontmatter the multi-valued ones.** L1 folds by primary
  branch; concepts fold by `kind:` (protocols / models / doctrines / taxonomies / system — a
  registered five-word vocabulary), carrying `branch:` as a list.
- A conversation fitting no branch is a **seed**: `_routing/ambiguous` is the seedbed; registering
  a new branch is a registry-edit PR.

## Disposition taxonomy (L1→L2)

**INGEST** (full page) · **DELTA-NOTE** (growth on an existing page) · **STUB** (below threshold;
row in session-stubs) · **QUEUE** (material but large; ingest-queue row with size) ·
**INGESTED-VIA-PACKET** (content lives in a packet; stub points at it) · **HELD** (exposure-class
or awaiting a ruling; reported, not written). Per R11: subject matter alone is never HELD-grounds —
freeze is for exposure/externality/identity-self only.

## Doctrine adopted from Herald (2026-07-28 analysis, both trees)

- **Instruments detect and enqueue; sessions judge.** No linter renders a verdict that requires
  judgment; it files a signal. (Their pharma post-mortem lesson, adopted as shared doctrine.)
- **The wiki is already a graph — lint it as one:** every citation/link resolves; entity mentions
  backlink. First specimen caught cross-tree the same evening: a bookshelf-packet citation to a
  slug that never existed (wrong-edge), corrected same day.

## What this supersedes

`raw/sessions/` (→ `raw/transcripts/`), `raw/Anthropic_zips/` (→ `originals/claude-ai/exports/`),
`new-sessions/` (→ `claude-ai/_routing/incoming/`), the flat `wiki/references/` (→ four-genre
split), `sources/infrastructure/` (→ `sources/cfl/` + sub-branches). Historical prose references
to old paths stay unedited (no history rewrite); live `source_file:` pointers are swept
mechanically, gated on `lint.py` fixity + `verify_quotes.py` zero-broken.

## Registry seed notes (PR-A, 2026-07-28)

Added while seeding `wiki/references/registries/trunks.md` from disk (SCHEMA §"Disposition
taxonomy" / this document's DOMAIN coordinate). Per the PR-A brief: **disk wins for what exists, the
standard wins for names.** Full per-branch tables live on the registry page; this section is the
durable discrepancy record the brief asked for.

- **fl trunk folder-name variance (3 branches):** this document's fl seed list names
  `cf, mechanics, governance`; the actual `wiki/sources/` subdirectories on disk are
  `consciousness/`, `ai-mechanics/`, `ai-governance/`. Same branches, longer disk names. Not
  resolved here — flagged so a future move PR renaming these folders to match the standard's
  shorter names does so visibly, not silently.
- **pro trunk coverage gap:** `references/TRUNKS.md`'s "Specialty lines core work (always-on area)"
  — Jon's actual job — has **zero** `wiki/pro/sources/` files as of 2026-07-28. Registered as a
  branch with no sources rather than dropped; the gap is real, not a naming issue.
- **home trunk — two branches missing from the seed list entirely:** Solar/energy
  (`sunrun-solar-battery-evaluation-2026-07-11-b7e4c2`) and Sewer/structural repair
  (`sewer-lateral-repair-decision-2026-07-09-9e5323`) exist on disk with no corresponding row in
  `references/TRUNKS.md`, whose "Active branches" list was last updated 2026-06-28, before both
  sessions. Added as new branches in the registry; no standard name existed to defer to.
- **personal trunk — undifferentiated seed list:** `references/TRUNKS.md` groups "faith/OCIA,
  personal identity, finance/security, personal growth, self-care" as one list item under "What it
  contains." Disk (`wiki/personal/sources/`, 49 files) shows these as separately countable,
  independently active clusters (Faith/OCIA = 7 sources, Family Health = 6, etc.), so the registry
  splits them into distinct branch rows rather than preserving the single undifferentiated line.

None of these block PR-A (no file moves in this PR); they are the concrete input for whichever later
PR executes the `consciousness/`→`cf/`, `ai-mechanics/`→`mechanics/`, `ai-governance/`→`governance/`
renames, and for Jon's own eventual fill-in of the bracketed vision-statement placeholders this
document's registry carries forward verbatim from `references/TRUNKS.md`.
