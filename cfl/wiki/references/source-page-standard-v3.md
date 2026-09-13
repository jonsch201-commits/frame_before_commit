---
title: Wiki Source-Page Standard v3.0
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 8 vs skills 0 on authored labels"
status: DEPRECATED-retained — superseded by source-page-standard-v4.md (2026-07-13, adds analysis kind + fidelity-confidence extension). v3.0 was the ratified session|reference standard; retained for lineage.
version: 3.0-draft
epistemic_status: provisional-strong — the 1-substrate+4-function architecture converged across two
  models (meta-FBC, 2026-07-13) AND survived a migration/verification audit against real pages. v3.0 is
  what the audit forced: FORM is per-source-kind, not universal. The confidence axis (C1) that would let
  this document state its own status precisely is itself PROVISIONAL and ASOP-gated. This field IS C1
  applied to the standard — dogfooding.
authored: 2026-07-13
authored_by: claude-opus-4-8/wiki-master (CC session da51cc)
supersedes: source-page-standard-v2.md (v2.0 superseded pre-commit — never ratified; retained for the
  design lineage of this session). v1.0 remains deprecated-retained as the per-element PASS/FAIL reference.
maintained_by: skills-master (standard) + wiki-master (application)
governance: SemVer — MAJOR change = Jon sign-off; MINOR (additive lint check) = batched; PATCH = auto
---

# Wiki Source-Page Standard v3.0

The single definition of **"done"** for a wiki source page — FL, personal, home, pro, co-equally.

**Lineage.** v1.0 = flat checklist of 8 elements. **v2.0** (meta-FBC, 2026-07-13) regrouped the 8 as
lint-leaves under **1 substrate + 4 epistemic functions**. **v3.0** = what the 2026-07-13 migration audit
forced on contact with real pages: **FORM is parameterized by source-kind, not universal** — a device-
warranty reference artifact and a session-claims extraction have legitimately different required shapes;
forcing one schema on both is a category error. v3.0 also closes the two expressibility gaps the audit's
admission gate flagged (E4 ledger-dependency; the FORM-fail cascade).

Nothing is backfilled to this standard until Jon **signs off on this written draft** (§ Ratification).

## Decisions locked
**Jon, 2026-07-12:** turn citations mandatory on substantive Key Claims · per-claim fidelity tags
mandatory · neg-cite Type 1 + Type 2 both required · findability frontmatter required · provenance
required (+ subagent traceability) · backfill ALL 183 pages, personal/home/pro = FL bar · canary gated.

**Jon, 2026-07-13:**
- **Restructure (v2.0):** 1 substrate + 4 functions; 8 elements → permanent-ID lint-leaves.
- **Confidence axis (C1) = PROVISIONAL, ASOP-gated** (§ The confidence axis).
- **Governance = interim** ("TBD, fine for now").
- **Source-kind grading = uniform bar** + `unrecoverable` path + **resurfaced-branch** for key CC claims.
- **Per-kind FORM (v3.0):** "uniform bar" = **domain-parity** (personal/pro held to FL rigor); it does
  NOT mean forcing a warranty record into a claims schema. FORM is per-source-kind; rigor is uniform,
  shape is kind-appropriate. *(Jon chose "A" over "scope v2.0 to session-kind only," 2026-07-13.)*

---

## The substrate + four functions

A page is **v3.0-conformant** when every check **applicable to its `source_kind`** is PASS or documented
`unrecoverable`/`N/A-by-kind`.

### FORM (substrate) — *the page has the required shape for its source-kind*
Every source page declares **`source_kind:`** in frontmatter (machine-readable → the per-kind FORM check
is presence-expressible). FORM.sections is parameterized:

- **`source_kind: session`** — extracted from a conversation (claude.ai or CC). **Required:** `## Summary`
  (2–4 synthesized sentences), `## Key Claims`, `## Conflicts` ("None" explicit if none). **Conditional:**
  `## Entities & Concepts`, `## Cross-Wiki`, `## Uncaptured Content` — present only when triggered, never
  "N/A".
- **`source_kind: reference`** — a curated standing artifact (device/warranty records, spec sheets,
  registries) that is not a single conversation's claims. **Required:** an identity heading + the
  artifact's domain-appropriate sections (e.g. Product / Issue / Warranty / Ticket / Action Items).
  Summary/Key Claims/Conflicts are **not** required. Its verification anchors to cited sources (ticket #,
  URL, photo), not conversation turns.

New kinds are **additive (MINOR)** — the taxonomy is extensible under `refine > group > expand`.
**PASS:** `source_kind` present; the kind's required sections present and non-empty; no "N/A" placeholders.

**Cascade (ledger rule — closes v2.0 gap #2).** FORM is the substrate the other functions stand on. When
FORM.sections FAILs for a `session` page (e.g. no `## Key Claims`), the claim-operating checks
(VERIFY.anchor, VERIFY.fidelity, RETRIEVE.linkage) grade **`N/A-blocked`, not FAIL** — the page shows one
root FORM failure, not four derived ones.

### VERIFY — *every substantive claim can be checked against the source*
- **E2 — Anchor.** *session-kind:* every Key Claim asserting a fact/decision/spec carries `([slug:T{n}])`
  (or `[slug:T{n}.P{p}]` for 3+ separable claims). *reference-kind:* the analog is a **source-citation**
  (ticket/URL/photo); turn-anchor grades **`N/A-by-kind`**.
  **PASS (session):** ≥95% of substantive Key Claims carry a resolvable anchor. **Unrecoverable:** if
  `source_file_status: unrecoverable`, grades `unrecoverable`. **Expressibility:** anchor *presence* is
  greppable; the ≥95% *grade* requires the Key-Claims parser (§ Linter dependencies).
- **E3 — Fidelity.** Every Key Claim carries exactly one tag: `verbatim` · `paraphrase` · `reconstructed`
  · `contextual`. Format: `- **Claim** [paraphrase] — context ([slug:T12])`.
  **PASS:** every Key Claim tagged. **Expressibility:** tag presence greppable; "every claim tagged" needs
  the parser.

**Recovery provision — resurfaced-branch (key claims only, materiality-gated).** For a **key** claim on a
CC session with a thin anchor/fidelity trail, the session may be **resumed at exact context** and the
model output captured — logged as a **disclosed reconstruction**, never original: tag `reconstructed`,
provenance `resurfaced @ T{n}`, one-line "a branch of the conversation that could have occurred." **FBC
the resurfacing itself** — run the exact context through multiple frames, log the branch-*set*, so it
carries its own uncertainty. ASOP 41 discipline: disclosed reliance, stakes-scaled. Key messages only.

### RETRIEVE — *every page and claim can be found and is connected*
- **E5 — Linkage (orphaned-claim / neg-cite Type 2).** *session-kind:* every Key Claim has ≥1 outward
  link (`[[slug]]` in Entities & Concepts / Cross-Wiki / Conflicts, or concept-page integration); orphans
  flagged. *reference-kind:* the page itself is linked from its domain index. Enforced by the Z1 detector.
  **PASS:** zero unflagged orphaned claims (session) / page indexed (reference). **Expressibility:** link
  presence greppable; per-claim orphan grade needs the parser.
- **E6 — Findability (FAIR-grounded).** `retrieval_key:` (stable, unique, kebab) **and** `aliases:` (≥2
  natural-language handles a future session would search). Content indexed by the Z1 content/alias index.
  **PASS:** `retrieval_key` present + unique; ≥2 `aliases`. **Expressibility:** fully greppable.

### TRACE — *the page declares what made it and what it read*
- **E7 — Provenance + reads-manifest (PROV / Datasheets-grounded).** `generated_by:` (writing
  model/role), `extraction_by:` (any subagent/model that produced claims — required whenever a subagent
  contributed; declare a subagent-contribution flag so the IFF is page-detectable), `reads_manifest:`
  (link to the per-session reads-manifest).
  **PASS:** `generated_by` present; `extraction_by` present iff a subagent contributed; reads-manifest
  linked when one exists. **Expressibility:** fully greppable.

### PRESERVE — *nothing was silently dropped or truncated*
- **E4 — Uncaptured content (neg-cite Type 1).** A `## Uncaptured Content` assessment against the four
  FBC negative-space categories (unfollowed threads, dissolved tensions, absent technical details,
  epistemic gaps). **Frontmatter marker `uncaptured_assessed: empty | populated` (required on
  session-kind) — closes v2.0 gap #1:** `populated` ⇒ the section is present; `empty` ⇒ section omitted,
  marker proves the assessment ran. This makes E4 **page-presence-expressible** instead of ledger-only.
  **PASS:** `uncaptured_assessed` present; if `populated`, section present; no "N/A" placeholder.
- **E8 — Integrity & fixity (OAIS-grounded).** `source_file:` resolves, **or** `source_file: none` +
  `source_file_status: unrecoverable`. Fixity: `raw_sha256:` (bytes unchanged) **and** `raw_length:`
  (non-truncation).
  **PASS:** source_file resolves (or unrecoverable documented) **and** `raw_length` present **and**
  `raw_sha256` present when the raw exists. **Expressibility:** fully greppable.

---

## The confidence axis (C1) — PROVISIONAL, ASOP-gated
Distinct from fidelity (E3, how faithfully captured), **confidence** is *how sure we are the claim is
right*. Jon's intent: the wiki "wears its confidence on its sleeve" — claim, synthesized page, and the
standard's own level. **Status: PROVISIONAL** — ships now as a per-claim tag-value
(`confidence: high/med/low`), lintable via provisional-entry, binding on batch ratification.
**Placement is deferred by design** (per-claim tag vs cross-function invariant) — gated on **Tier-1 ASOP
ingestion** (a6314b→100%; T-85 modal-language first), because confidence-disclosure IS the ASOP construct
(**41** stakes-scaling · **23** limitation-surfacing · **1** base obligation). Drafting it from instinct
before ASOP would reify instinct as the canon of a framework Jon already holds professionally. **Promotion:**
ingest ASOP → FBC the placement grounded in 41/23/1 → MINOR/MAJOR per outcome → PROVISIONAL → ratified.

## Governance *(interim — Jon: "TBD, fine with your recommendations for now")*
- **SemVer.** MAJOR (a function's meaning changes, incl. a new source-kind's FORM) → **Jon sign-off.**
  MINOR (additive lintable check) → **batched** (auto-lands PROVISIONAL, binding next batch). PATCH → auto.
- **Deprecate, never delete; permanent IDs.** Retired checks marked `deprecated`; IDs (E1…E8, C1, …)
  never reused. Enforcement shrinks; the record grows monotonically — this keeps the Migration Map valid.
- **Provisional entry (owner-bottleneck fix).** A check whose linter exists auto-lands PROVISIONAL,
  enforced-but-non-binding until the next ratification batch. C1 is the first live test.
- **Admission gate (softened).** A new check must be **presence-expressible** (detect *whether* it was
  done) — not correctness-expressible (whether *well* stays judgment). *The 2026-07-13 audit is this gate
  working:* it flagged E4 (was ledger-only → fixed with the marker) and E2/E3/E5 (need the Key-Claims
  parser → § Linter dependencies), rather than papering over them.
- **Change ordering: refine > group > expand.** Sharpen, then regroup, before adding — resist sprawl.
- **Source-kind overlay.** Uniform *rigor* across kinds; *shape* per kind (FORM profiles). Structurally
  impossible checks grade `unrecoverable` (documented) or `N/A-by-kind` — never a silent waiver — except
  the key-claim resurfaced-branch recovery.

## Migration Map (E-number → function.check) — REQUIRED for historical continuity
| v1.0 element | v3.0 function.check | Permanent ID | Δ since v2.0 |
|---|---|---|---|
| E1 Required sections | `FORM.sections` (per `source_kind`) | E1 | **parameterized by kind (MAJOR → v3.0)** |
| — | `FORM.kind` (`source_kind` present) | E1k | new (MINOR, part of the v3.0 MAJOR) |
| E2 Turn citations | `VERIFY.anchor` (session) / source-cite (reference) | E2 | kind-adapted |
| E3 Quality tag | `VERIFY.fidelity` | E3 | — |
| E4 Uncaptured content | `PRESERVE.uncaptured` (+ `uncaptured_assessed` marker) | E4 | **marker added (MINOR)** |
| E5 Orphaned-claim | `RETRIEVE.linkage` | E5 | — |
| E6 Findability | `RETRIEVE.findability` | E6 | — |
| E7 Provenance | `TRACE.provenance` | E7 | — |
| reads-manifest | `TRACE.reads-manifest` | E7m | — |
| E8 Integrity & fixity | `PRESERVE.fixity` | E8 | — |
| Confidence | `C1` (placement TBD) | C1 | PROVISIONAL |
| Resurfaced-branch | `VERIFY.resurfaced` (recovery) | E2r | — |

**Grades do not break:** checks are identical values keyed by permanent ID; regrouping + kind-scoping is a
ledger header/column change, not a re-grade (verified against 6 real pages, 2026-07-13). The audit found
0/6 findability, 0/6 fixity, 1/6 provenance, 1/6 anchored — the flat-8 grades and the v3.0 grades agree.

## Linter dependencies (what the admission gate surfaced, 2026-07-13)
- **Fully presence-expressible today (grep frontmatter/headers):** E1k, E6, E7, E7m, E8, E4-marker.
- **Presence-expressible; *grade* needs a Key-Claims parser:** E2, E3, E5 (count claims, match
  anchors/tags/links per claim). This parser is the Z1 lint prerequisite for a binding grade — until it
  exists, E2/E3/E5 grade at the coarse "any present" level and are flagged PROVISIONAL.

## The reads-manifest
Current CC extracts render only a truncated first tool-arg — offset/limit invisible, results stripped — so
a GBS cannot re-ground from the extract. v3.0 requires a per-session **reads-manifest** (data-master
converter enhancement, Z1): ordered files loaded, each `path` + `offset/limit` (or "full") + `partial-read`
flag. Linked via `reads_manifest:`; citable (PROV `used`).

## Conformance ledger
`audit-conformance-ledger.md`: one row per page × each applicable check (PASS / FAIL / `unrecoverable` /
`N/A-by-kind` / `N/A-blocked`), plus a `v3.0` boolean and the page's `source_kind`. Generated by the Z1
lint extension; the resumable spine of the 183-page backfill (read the ledger, not memory).

## External-standard mapping
| Function.check | Standard | Principle |
|---|---|---|
| RETRIEVE.findability (E6) | **FAIR** (Wilkinson 2016) | F1 unique persistent ID; F2/F4 rich indexed metadata |
| TRACE.provenance (E7) | **W3C PROV-O** | Entity `wasGeneratedBy` Activity `wasAssociatedWith` Agent; `used` reads-manifest |
| TRACE.provenance block | **Datasheets / Model Cards** | collection process + composition → completeness |
| RETRIEVE.linkage (E5) | **SKOS** | `prefLabel`/`altLabel` → title/aliases; `broader`/`related` → concept links |
| PRESERVE.fixity (E8) | **OAIS / fixity** | hash proves fidelity, length proves non-truncation |
| C1 confidence | **ASOP 41 / 23 / 1** | disclosure scales with stakes *(gating C1's placement)* |
| FORM per source-kind | **Datasheets "Composition"** | different artifact types warrant different descriptive schemas |
| Skill docs (Z5) | **Diátaxis** | tutorial / how-to / reference / explanation |

## References
- **FAIR** — Wilkinson et al. 2016, *Scientific Data* 3:160018 · https://www.go-fair.org/fair-principles/
- **W3C PROV-O** — W3C Rec. 2013 · https://www.w3.org/TR/prov-o/
- **Datasheets for Datasets** — Gebru et al. 2018, arXiv:1803.09010 · **Model Cards** — Mitchell et al. 2019, arXiv:1810.03993
- **Diátaxis** — Procida · https://diataxis.fr/
- **SKOS** — W3C Rec. 2009 · https://www.w3.org/TR/skos-reference/
- **OAIS / fixity** — ISO 14721; DPC Handbook · https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums
- **ASOP 1 / 23 / 41** — Actuarial Standards Board *(Tier-1 substantive ingestion PENDING — a6314b ~25% partial; grounds C1)*.

## Provenance
- `generated_by:` claude-opus-4-8/wiki-master (CC session da51cc, 2026-07-13).
- `restructure_basis:` 6-frame + 2-synthesis meta-FBC (6 cold Opus frames + cold Opus synthesizer + CC
  Fable-at-max cross-check), 2026-07-13 — 1-substrate+4-function converged across two models.
- `v3.0_basis:` migration/verification audit of 6 real pages (3 newest FL + worst-cited personal/home/pro),
  2026-07-13 — found FORM was not universal (home reference + PM narrative pages), forcing per-kind FORM;
  confirmed the migration map holds and E1k/E6/E7/E7m/E8 are presence-expressible. Full audit in the
  da51cc transcript (test-master data).
- `extraction_by:` claude-sonnet-5/Explore — external-standards research (v1.0 carryover).
- This Provenance block + `epistemic_status:` are TRACE and C1 applied to this document — dogfooding.

## Ratification
DRAFT — **written, not committed.** Jon signs off on this written draft before any commit, and before any
docker session. Open questions carried:
1. **C1 placement** — deferred to post-ASOP FBC (by design).
2. **Governance tiers** — interim; Jon finalizes.
3. **E2 threshold** — 95% or 100% of substantive claims?
4. **reads-manifest scope** — all go-forward, or only GBS-likely pages?
5. **source_kind taxonomy** — session + reference cover the current corpus; add kinds (analysis? tool-run?)
   additively as they appear.
