---
title: Wiki Source-Page Standard v1.0
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 9 vs fleet 1 on authored labels"
status: DEPRECATED (retained, not deleted) — superseded by source-page-standard-v2.md (2026-07-13). v2.0
  regroups these 8 elements under 1 substrate + 4 functions; each element keeps its permanent ID. See the
  v2.0 Migration Map. This document remains the detailed per-element PASS/FAIL reference.
version: 1.0-draft
authored: 2026-07-12
authored_by: claude-opus-4-8/wiki-master (CC session da51cc)
extraction_by: claude-sonnet-5/Explore (external-standards research subagent) — see Provenance
maintained_by: skills-master (standard) + wiki-master (application)
supersedes: citability-standard.md (subsumes; that doc remains the detailed turn-numbering spec)
---

# Wiki Source-Page Standard v1.0

The single definition of **"done"** for a wiki source page. Every page — FL, personal, home, pro,
co-equally — is graded PASS/FAIL against the eight elements below; the grades populate the
**conformance ledger** (`audit-conformance-ledger.md`), which is the live answer to "what can we prove
is 100%." A page is **v1.0-conformant** only when every applicable element is PASS (or documented
`unrecoverable`). Nothing is backfilled to this standard until Jon ratifies it (§ Ratification).

## Decisions locked (Jon, 2026-07-12)
- Turn citations **mandatory** on all substantive Key Claims.
- Per-claim **quality tags mandatory** (verbatim / paraphrase / reconstructed / contextual).
- Negative citation **Type 1 (Uncaptured) and Type 2 (orphaned-claim) both required**.
- Findability frontmatter (`retrieval_key`, `aliases`) **required**.
- Provenance **required**, and **subagent contributions must be traceable** (`generated_by` +
  `extraction_by`).
- Audit = **backfill ALL 183 pages**; personal/home/pro held to the **same bar** as FL.
- Canary deploy is **gated** on corpus reconciliation + findability index (separate track).

---

## The eight elements

### E1 — Required sections
`## Summary` (2–4 sentences, synthesized, not the source's words), `## Key Claims`, and `## Conflicts`
(explicit "None" if none) are **always present**. `## Entities & Concepts`, `## Cross-Wiki`, and
`## Uncaptured Content` are **conditional** — present when their trigger is met, never as "N/A"
placeholders. (Unchanged from the confirmed 2026-05-27 schema.)
**PASS:** all three required sections present and non-empty.

### E2 — Turn citations (mandatory on all substantive claims)
Every Key Claim that asserts a fact/decision/spec carries a turn anchor `([slug:T{n}])` (or
`[slug:T{n}.P{p}]` when a message holds 3+ separable claims), per `citability-standard.md` (the
detailed turn-numbering spec, which v1.0 subsumes but does not replace).
**PASS:** ≥ 95% of substantive Key Claims carry a resolvable turn anchor. **Unrecoverable path:** if
`source_file_status: unrecoverable`, E2 is graded `unrecoverable` (not FAIL) and anchors are omitted.

### E3 — Per-claim quality tag (MANDATORY)
Every Key Claim carries exactly one tag indicating fidelity to the source passage:
`verbatim` (direct/near quote) · `paraphrase` (faithful, reworded) · `reconstructed` (logical inference,
not directly stated) · `contextual` (derived from surrounding context, no single attributable message).
Format: `- **Claim** [paraphrase] — context ([slug:T12])`.
**PASS:** every Key Claim tagged. **Unrecoverable path:** tag omitted, graded `unrecoverable`.

### E4 — Negative citation Type 1 (Uncaptured Content)
A `## Uncaptured Content` assessment against the four FBC negative-space categories (unfollowed threads,
dissolved tensions, absent technical details, epistemic gaps). Present when material content was left
out; **the assessment is required even to conclude "nothing material omitted"** — but the *section* is
omitted when genuinely empty (the reviewer records the empty finding in the ledger, not the page).
**PASS:** the assessment was performed (ledger notes empty vs populated); no "N/A" placeholder on-page.

### E5 — Negative citation Type 2 (orphaned-claim check)
Every Key Claim is checked for at least one outward link (a `[[slug]]` in Entities & Concepts /
Cross-Wiki / Conflicts, or integration into a concept/analysis page). Orphaned claims (in the source
page, referenced nowhere) are flagged — either linked, promoted to a concept page, or noted as a
known orphan. Enforced by the Z1 orphaned-claim detector, not eyeballing.
**PASS:** zero unflagged orphaned claims.

### E6 — Findability frontmatter (FAIR-grounded)
`retrieval_key:` (a stable, unique, kebab retrieval handle) **and** `aliases:` (≥2 natural-language
handles a future session would actually search — the "secret" was missed for lack of these). Content is
additionally indexed by the Z1 content/alias index so retrieval ≠ summary-grep.
**PASS:** `retrieval_key` present + unique; ≥2 `aliases`.

### E7 — Provenance & subagent traceability (PROV / Datasheets-grounded)
`generated_by:` (writing model/role, e.g. `claude-opus-4-8/wiki-master`), `extraction_by:` (any
subagent/model that produced the claims, e.g. `claude-sonnet-5/Explore` — **required whenever a
subagent contributed**), and `reads_manifest:` (link to the per-session reads-manifest, E-adjacent).
Material subagent logs are themselves ingestible per the subagent-log threshold.
**PASS:** `generated_by` present; `extraction_by` present iff a subagent contributed; reads-manifest
linked when one exists.

### E8 — Source integrity & fixity (OAIS / ISO 14721-grounded)
`source_file:` resolves, **or** `source_file: none` + `source_file_status: unrecoverable` (documented,
not silent). Fixity requires **two** figures, because a hash proves *fidelity* of what was kept but not
that *all* of it was kept: `raw_sha256:` (integrity — the raw bytes are unchanged) **and** `raw_length:`
(char/line count — the non-truncation check; Z1 reconciliation compares raw length vs extract coverage).
`raw_sha256` is required where the raw is available; omitted under the `unrecoverable` path.
**PASS:** source_file resolves (or unrecoverable documented) **and** `raw_length` present **and**
`raw_sha256` present when the raw exists.

---

## The reads-manifest (answers "what did this session actually read?")
Current CC extracts render only a truncated first tool-arg — offset/limit invisible, results stripped —
so a GBS **cannot** re-ground a session from the extract. v1.0 requires a per-session **reads-manifest**
(a data-master converter enhancement, Z1): the ordered list of files the session loaded, each with
`path` + `offset/limit` (or "full") + a `partial-read` flag. The source page links it via
`reads_manifest:`. This is what a GBS re-grounding pass consumes to reconstruct the session's evidence
base, and it is citable (PROV `used`).

## Conformance rubric → ledger
`audit-conformance-ledger.md` has one row per page × {E1…E8}, each cell PASS / FAIL / `unrecoverable`,
plus a `v1.0` boolean (all applicable elements PASS-or-unrecoverable). Generated and refreshed by the
Z1 lint extension. This is the resumable spine of the 183-page backfill (read the ledger, not memory)
and the provable "% to standard" metric.

## External-standard mapping
*(Grounded by a research subagent, 2026-07-12 — citations in § References; the subagent verified F/A/I/R
numbering, PROV types/relations, SKOS relations, and the OAIS fixity distinction against source pages.)*
| Element | Standard | Principle applied |
|---|---|---|
| E6 Findability | **FAIR** (Wilkinson 2016) | F1 globally-unique persistent ID (`retrieval_key`); F2/F4 rich, indexed, searchable metadata (`aliases` + content index) |
| E7 Provenance | **W3C PROV-O** | page = Entity `wasGeneratedBy` an Activity `wasAssociatedWith` an Agent (model/role); `wasDerivedFrom` source; `used` reads-manifest files |
| E7 Provenance block | **Datasheets for Datasets / Model Cards** | motivation, composition, collection process, limitations → the "how captured / known gaps" framing (E4 + E8) |
| E5 concept linking | **SKOS** | `prefLabel`/`altLabel` → title/aliases; `broader`/`related` → concept-page links |
| E8 Integrity | **OAIS / fixity checksums** | prove-extraction integrity: raw size/hash vs extract coverage |
| Skill docs (Z5) | **Diátaxis** | tutorial / how-to / **reference** / explanation — skills need the reference quadrant most |

## References
- **FAIR** — Wilkinson et al. 2016, *Scientific Data* 3:160018 · https://www.nature.com/articles/sdata201618 · https://www.go-fair.org/fair-principles/ (R1.2: detailed provenance is a first-class *reuse* requirement — grounds E7).
- **W3C PROV-O / PROV-DM** — W3C Rec. 2013 · https://www.w3.org/TR/prov-o/ · https://www.w3.org/TR/prov-dm/ (Entity/Activity/Agent; `wasGeneratedBy`/`wasDerivedFrom`/`wasAttributedTo`/`used`/`wasAssociatedWith`).
- **Datasheets for Datasets** — Gebru et al. 2018, arXiv:1803.09010 · **Model Cards** — Mitchell et al. 2019, arXiv:1810.03993 (Collection Process + Composition → completeness; Model Details + Caveats → provenance caveats).
- **Diátaxis** — Procida · https://diataxis.fr/ (skills need **How-to + Reference** most).
- **SKOS** — W3C Rec. 2009 · https://www.w3.org/TR/skos-reference/ (`prefLabel`→title, `altLabel`→aliases, `broader`/`narrower`/`related`→concept links).
- **OAIS / fixity** — ISO 14721; DPC Handbook · https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums (pair `raw_sha256` with `raw_length` — hash proves fidelity, length proves non-truncation).

## Provenance
- `generated_by:` claude-opus-4-8/wiki-master (CC session da51cc, 2026-07-12).
- `extraction_by:` claude-sonnet-5/Explore — external-standards research subagent; verified FAIR
  sub-principle numbering, PROV core types/relations, SKOS relations, and the OAIS fixity distinction
  against primary source pages; its brief grounds the mapping table + § References. (Short, well-scoped
  research → subagent-log tier = STUB, not a standalone source page; its contribution is traceable here
  per E7. Caveat it flagged: Datasheets(7)/Model-Cards(9) section counts are paraphrased, not quoted.)
  This Provenance block is the E7 pattern applied to this document — dogfooding traceability.

## Ratification
This is a DRAFT. **Jon ratifies v1.0 before any Z4 backfill begins.** Open questions for ratification:
1. E2 threshold — 95% of substantive claims cited, or 100%?
2. E6 — is `retrieval_key` + 2 aliases enough, or also require a 1-line `domain:` + `canary:` field
   (the 2026-07-08 frontmatter-conformance proposal)?
3. Reads-manifest — required for all go-forward ingests, or only for pages likely to need GBS
   re-grounding? (Backfilling it for 183 old sessions may be infeasible where raw tool-args weren't kept.)
