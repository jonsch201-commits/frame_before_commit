---
title: Wiki Source-Page Standard v2.0
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 8 vs skills 0 on authored labels"
status: SUPERSEDED pre-commit by source-page-standard-v3.md (2026-07-13) — never ratified; retained for
  the design lineage of this session. v3.0 keeps v2.0's 1-substrate+4-function architecture and makes FORM
  per-source-kind after the migration audit found FORM was not universal. Do not grade against v2.0.
version: 2.0-draft (superseded)
epistemic_status: provisional-strong — two models converged independently; the restructure is our best
  reasoned instinct, not proven law. The confidence axis (C1) that would let this document state its own
  status precisely is itself PROVISIONAL and ASOP-gated. This frontmatter field IS C1 applied to the
  standard — dogfooding the axis it defines.
authored: 2026-07-13
authored_by: claude-opus-4-8/wiki-master (CC session da51cc)
supersedes: source-page-standard-v1.md (v1.0 deprecated, NOT deleted — see § Migration Map)
maintained_by: skills-master (standard) + wiki-master (application)
governance: SemVer — MAJOR change = Jon sign-off; MINOR (additive lint check) = batched; PATCH = auto
---

# Wiki Source-Page Standard v2.0

The single definition of **"done"** for a wiki source page — FL, personal, home, pro, co-equally.

**What changed from v1.0 (why this is a MAJOR bump).** v1.0 was a **flat checklist of 8 elements**.
v2.0's claim, reached by a 6-frame + 2-synthesis meta-FBC with independent inter-model convergence, is
that the 8 elements are not the real unit — they are **evidence of 4 epistemic functions a page performs
on one substrate.** The functions are the thing a cold session actually relies on; the 8 checks are
**lint-leaves** hanging under them, each keeping its permanent ID (E1…E8) so historical audits and the
conformance ledger never break (see § Migration Map). Grouping ≠ merging: the checks stay distinct.

Nothing is backfilled to this standard until Jon **signs off on this written draft** (§ Ratification).

## Decisions locked
**Jon, 2026-07-12:**
- Turn citations **mandatory** on all substantive Key Claims.
- Per-claim **fidelity tags mandatory** (verbatim / paraphrase / reconstructed / contextual).
- Negative citation **Type 1 (Uncaptured) and Type 2 (orphaned-claim) both required**.
- Findability frontmatter (`retrieval_key`, `aliases`) **required**.
- Provenance **required**; subagent contributions traceable (`generated_by` + `extraction_by`).
- Audit = **backfill ALL 183 pages** to full standard; personal/home/pro held to the **same bar** as FL.
- Canary deploy is **gated** on corpus reconciliation + findability index (separate track).

**Jon, 2026-07-13 (v2.0 clarification):**
- **Restructure APPROVED:** 1 substrate + 4 functions; 8 elements → lint-leaves with permanent IDs.
- **Confidence axis (C1) = PROVISIONAL and ASOP-gated** (§ The confidence axis). Ships now as a
  per-claim tag-value; its *placement* (per-claim tag vs cross-function invariant) is decided only after
  Tier-1 ASOP ingestion. Rationale: the confidence/disclosure construct **is** ASOP 41/23/1; drafting it
  from instinct before ASOP is ingested would reify instinct as canon (the words-reify failure).
- **Governance = interim** ("TBD, fine with your recommendations for now") — the SemVer tiers below are
  PROVISIONAL until Jon finalizes.
- **Source-kind grading = uniform bar** + `unrecoverable` path + the **resurfaced-branch** recovery
  provision for key CC claims (§ VERIFY).

---

## The substrate + four functions

Each function states an **invariant** (what it promises a cold session) and lists its **checks** (the
former elements, permanent IDs retained). A page is **v2.0-conformant** when every applicable check is
PASS or documented `unrecoverable`.

### FORM (substrate) — *the page has the required shape*
The load-bearing frame every other function sits on.
- **E1 — Required sections.** `## Summary` (2–4 synthesized sentences), `## Key Claims`, and
  `## Conflicts` ("None" explicit if none) are **always present**. `## Entities & Concepts`,
  `## Cross-Wiki`, `## Uncaptured Content` are **conditional** — present only when triggered, never as
  "N/A" placeholders.
  **PASS:** all three required sections present and non-empty; no placeholder conditional sections.

### VERIFY — *every substantive claim can be checked against the source*
The claim is both **anchored** (where it came from) and **fidelity-tagged** (how faithfully it was kept).
- **E2 — Turn anchor.** Every Key Claim asserting a fact/decision/spec carries `([slug:T{n}])` (or
  `[slug:T{n}.P{p}]` when a message holds 3+ separable claims), per `citability-standard.md`.
  **PASS:** ≥95% of substantive Key Claims carry a resolvable turn anchor. **Unrecoverable path:** if
  `source_file_status: unrecoverable`, E2 grades `unrecoverable`, anchors omitted.
- **E3 — Fidelity tag.** Every Key Claim carries exactly one tag: `verbatim` · `paraphrase` ·
  `reconstructed` · `contextual`. Format: `- **Claim** [paraphrase] — context ([slug:T12])`.
  **PASS:** every Key Claim tagged. **Unrecoverable path:** tag omitted, graded `unrecoverable`.

**Recovery provision — resurfaced-branch (key claims only, materiality-gated).** *(New, 2026-07-13.)*
For a **key** Key Claim on a CC session where the anchor/fidelity trail is thin, the session may be
**resumed at exact context** and the model's output captured — but it is logged as a **disclosed
reconstruction**, never as original: fidelity tag `reconstructed`, provenance `resurfaced @ T{n}`, and a
one-line note that this is "a branch of the conversation that could have occurred." **Consider FBC-ing
the resurfacing itself** — run the exact context through multiple frames and log the branch-*set*, so the
reconstruction carries its own uncertainty rather than posing as the one true answer. This is ASOP 41
discipline: disclosed reliance, stakes-scaled. Use sparingly (cost); key messages only.

### RETRIEVE — *every page and claim can be found and is connected*
Findable by content, not just by title/summary grep; and no claim dangles unlinked.
- **E5 — Linkage (orphaned-claim / neg-cite Type 2).** Every Key Claim is checked for ≥1 outward link
  (`[[slug]]` in Entities & Concepts / Cross-Wiki / Conflicts, or integration into a concept page).
  Orphans are flagged — linked, promoted, or noted as a known orphan. Enforced by the Z1 detector.
  **PASS:** zero unflagged orphaned claims.
- **E6 — Findability frontmatter (FAIR-grounded).** `retrieval_key:` (stable, unique, kebab handle)
  **and** `aliases:` (≥2 natural-language handles a future session would actually search — the "secret"
  was missed for lack of these). Content additionally indexed by the Z1 content/alias index.
  **PASS:** `retrieval_key` present + unique; ≥2 `aliases`.

### TRACE — *the page declares what made it and what it read*
A GBS can re-ground the session from the page alone.
- **E7 — Provenance + reads-manifest (PROV / Datasheets-grounded).** `generated_by:` (writing
  model/role), `extraction_by:` (any subagent/model that produced claims — **required whenever a
  subagent contributed**), and `reads_manifest:` (link to the per-session reads-manifest).
  **PASS:** `generated_by` present; `extraction_by` present iff a subagent contributed; reads-manifest
  linked when one exists.

### PRESERVE — *nothing was silently dropped or truncated*
The negative-space guarantee and the fixity guarantee.
- **E4 — Uncaptured content (neg-cite Type 1).** A `## Uncaptured Content` assessment against the four
  FBC negative-space categories (unfollowed threads, dissolved tensions, absent technical details,
  epistemic gaps). The **assessment is required even to conclude "nothing material omitted"** — but the
  *section* is omitted when genuinely empty (the reviewer records the empty finding in the ledger).
  **PASS:** assessment performed (ledger notes empty vs populated); no "N/A" placeholder on-page.
- **E8 — Integrity & fixity (OAIS / ISO 14721-grounded).** `source_file:` resolves, **or**
  `source_file: none` + `source_file_status: unrecoverable` (documented). Fixity requires **two**
  figures: `raw_sha256:` (fidelity — bytes unchanged) **and** `raw_length:` (non-truncation — Z1
  reconciliation compares raw length vs extract coverage).
  **PASS:** source_file resolves (or unrecoverable documented) **and** `raw_length` present **and**
  `raw_sha256` present when the raw exists.

---

## The confidence axis (C1) — PROVISIONAL, ASOP-gated

Distinct from **fidelity** (E3: how faithfully the claim was captured), **confidence** is *how sure we
are the claim is right*. Jon's intent: "the wiki wears its confidence on its sleeve" — at the claim, the
synthesized page, and the standard's own level.

- **Status: PROVISIONAL.** It ships **now** as a per-claim tag-value (`confidence: high/med/low`),
  lintable today via the provisional-entry mechanism (§ Governance). It is **binding on batch
  ratification**, not before.
- **Placement is the open question, and it is deliberately deferred.** Candidate answers: a per-claim E3
  sibling, **or** a cross-function invariant that also applies to synthesized pages and to this document
  (as `epistemic_status:` in the frontmatter above already demonstrates). **This is not decided by
  instinct.** It is gated on **Tier-1 ASOP ingestion** (a6314b→100%; T-85 modal-language first), because
  confidence-disclosure is precisely the ASOP construct: **ASOP 41** (disclosure scales with stakes),
  **ASOP 23** (surface known limitations), **ASOP 1** (base communication obligation). Drafting it before
  ASOP is ingested would reify my instinct as the canon of a framework Jon already holds professionally.
- **Promotion path:** ingest Tier-1 ASOP → FBC the placement decision grounded in ASOP 41/23/1 → MINOR
  or MAJOR bump per outcome → C1 promoted from PROVISIONAL to ratified.

---

## Governance *(interim — Jon: "TBD, fine with your recommendations for now")*

- **SemVer.** **MAJOR** = a function's meaning changes → **Jon sign-off.** **MINOR** = an additive
  lintable check → **batched** (auto-lands PROVISIONAL, binding on the next ratification batch).
  **PATCH** = wording → **automatic.**
- **Deprecate, never delete; permanent IDs.** A retired check is marked `deprecated`, not removed; its ID
  (E1…E8, C1, …) is never reused. Enforcement can shrink; the record grows monotonically. This is what
  keeps the Migration Map and historical audits valid forever.
- **Provisional entry (the owner-bottleneck fix).** A proposed check whose linter exists **auto-lands
  PROVISIONAL** and is enforced-but-non-binding until the next ratification batch makes it binding. C1 is
  the first live test of this mechanism.
- **Admission gate (softened).** A new check must be **presence-expressible** in lint (can we detect
  whether it was done?) — *not* correctness-expressible (whether it was done *well* stays human
  judgment). The strict version would have wrongly excluded E3/E4.
- **Change ordering: refine > group > expand.** Prefer sharpening an existing check, then regrouping,
  before adding a new one — resist element sprawl.
- **Source-kind overlay.** **Uniform bar for all kinds.** Where a check is structurally impossible for a
  kind, it grades `unrecoverable` (documented, not silently waived) — *except* the key-claim
  resurfaced-branch provision (§ VERIFY), which can recover an otherwise-`unrecoverable` CC anchor. No
  per-kind lowered bars.

---

## Migration Map (E-number → function.check) — REQUIRED for historical continuity
*(Fable's catch: existing pages were audited under flat-8; publishing this map in the same commit is what
prevents those audits and the conformance ledger from breaking.)*

| v1.0 element | v2.0 function.check | Permanent ID |
|---|---|---|
| E1 Required sections | `FORM.sections` | E1 |
| E2 Turn citations | `VERIFY.anchor` | E2 |
| E3 Quality tag | `VERIFY.fidelity` | E3 |
| E4 Uncaptured content | `PRESERVE.uncaptured` | E4 |
| E5 Orphaned-claim check | `RETRIEVE.linkage` | E5 |
| E6 Findability frontmatter | `RETRIEVE.findability` | E6 |
| E7 Provenance | `TRACE.provenance` | E7 |
| (E7-adjacent) reads-manifest | `TRACE.reads-manifest` | E7m |
| E8 Integrity & fixity | `PRESERVE.fixity` | E8 |
| *(new 2026-07-13)* Confidence | `C1` — placement TBD | C1 (PROVISIONAL) |
| *(new 2026-07-13)* Resurfaced-branch | `VERIFY.resurfaced` (recovery) | E2r |

No element was merged or dropped; grouping is by epistemic function, not by mechanism (E4→PRESERVE and
E5→RETRIEVE split the two "negative citations" by what they *guarantee*, not by their shared name).

## The reads-manifest (answers "what did this session actually read?")
Current CC extracts render only a truncated first tool-arg — offset/limit invisible, results stripped —
so a GBS **cannot** re-ground a session from the extract. v2.0 requires a per-session **reads-manifest**
(data-master converter enhancement, Z1): the ordered list of files the session loaded, each with `path`
+ `offset/limit` (or "full") + a `partial-read` flag. The source page links it via `reads_manifest:`.
This is what a GBS re-grounding pass consumes, and it is citable (PROV `used`).

## Conformance rubric → ledger
`audit-conformance-ledger.md` has one row per page × each check (PASS / FAIL / `unrecoverable`), plus a
`v2.0` boolean (all applicable checks PASS-or-unrecoverable). Generated/refreshed by the Z1 lint
extension. This is the resumable spine of the 183-page backfill (read the ledger, not memory) and the
provable "% to standard" metric. Rows carry the permanent IDs, so a v1.0→v2.0 relabel is a header change,
not a re-grade.

## External-standard mapping
| Function.check | Standard | Principle applied |
|---|---|---|
| RETRIEVE.findability (E6) | **FAIR** (Wilkinson 2016) | F1 globally-unique persistent ID; F2/F4 rich, indexed, searchable metadata |
| TRACE.provenance (E7) | **W3C PROV-O** | page = Entity `wasGeneratedBy` an Activity `wasAssociatedWith` an Agent; `wasDerivedFrom` source; `used` reads-manifest |
| TRACE.provenance block | **Datasheets / Model Cards** | motivation, composition, collection process, limitations → "how captured / known gaps" |
| RETRIEVE.linkage (E5) | **SKOS** | `prefLabel`/`altLabel` → title/aliases; `broader`/`related` → concept links |
| PRESERVE.fixity (E8) | **OAIS / fixity** | raw size/hash vs extract coverage — hash proves fidelity, length proves non-truncation |
| C1 confidence | **ASOP 41 / 23 / 1** | disclosure scales with stakes; surface known limitations; base communication obligation *(gating C1's placement)* |
| Skill docs (Z5) | **Diátaxis** | tutorial / how-to / **reference** / explanation |

## References
- **FAIR** — Wilkinson et al. 2016, *Scientific Data* 3:160018 · https://www.go-fair.org/fair-principles/
- **W3C PROV-O / PROV-DM** — W3C Rec. 2013 · https://www.w3.org/TR/prov-o/
- **Datasheets for Datasets** — Gebru et al. 2018, arXiv:1803.09010 · **Model Cards** — Mitchell et al. 2019, arXiv:1810.03993
- **Diátaxis** — Procida · https://diataxis.fr/
- **SKOS** — W3C Rec. 2009 · https://www.w3.org/TR/skos-reference/
- **OAIS / fixity** — ISO 14721; DPC Handbook · https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums
- **ASOP 1 / 23 / 41** — Actuarial Standards Board *(Tier-1 substantive ingestion PENDING — a6314b is ~25% partial; grounds C1 once ingested)*.

## Provenance
- `generated_by:` claude-opus-4-8/wiki-master (CC session da51cc, 2026-07-13).
- `restructure_basis:` 6-frame + 2-synthesis meta-FBC (6 cold Opus frame-agents + cold Opus synthesizer
  + CC Fable-at-max inter-model cross-check), 2026-07-13. Two independent models converged on 1-substrate
  + 4-function; Fable independently caught the migration-map risk, provisional-entry, and the softened
  admission gate. Full run is in the da51cc transcript (test-master inter-model-convergence data).
- `extraction_by:` claude-sonnet-5/Explore — external-standards research subagent (v1.0 carryover);
  verified FAIR/PROV/SKOS/OAIS against primary sources.
- This Provenance block + the `epistemic_status:` frontmatter are the TRACE and C1 patterns applied to
  this document — dogfooding.

## Ratification
This is a DRAFT — **written, not committed.** Jon signs off on this written draft before any commit, and
before any docker session. Open questions carried into ratification:
1. **C1 placement** — per-claim tag vs cross-function invariant — deferred to post-ASOP FBC (by design).
2. **Governance tiers** — interim; Jon to finalize the MAJOR/MINOR/PATCH split and provisional-entry semantics.
3. **E2 threshold** — 95% of substantive claims cited, or 100%? (carried from v1.0)
4. **reads-manifest scope** — all go-forward ingests, or only pages likely to need GBS re-grounding?
   (Backfilling 183 old sessions may be infeasible where raw tool-args weren't kept.)
