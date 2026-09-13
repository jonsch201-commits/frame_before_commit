---
title: Wiki Source-Page Standard v4.0
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 8 vs skills 0 on authored labels"
status: RATIFIED AND COMMITTED — operative standard. Jon ratified G1 analysis-kind + G2 fidelity
  extension 2026-07-13. Committed `4253fdc` 2026-07-13; refined `3dcef44` → `e93155e` 2026-07-27
  (PR #156, #158). Working tree clean as of 2026-08-01.
  STATUS CORRECTED 2026-08-01 — this field read "DRAFT — written, not committed" for
  nineteen days after the file was committed and four subsequent commits had landed on it. It was
  read as evidence the standard was not yet in force, which is the opposite of true. v1.0 and v2.0
  carry accurate lifecycle statuses (DEPRECATED / SUPERSEDED pre-commit); this one did not.
version: 4.0
epistemic_status: provisional-strong. v4.0 = v3.0 + the `analysis` source-kind (G1, ratified) + the
  fidelity-confidence vocabulary extension (G2-now, ratified). The truth-confidence axis C1 remains
  ASOP-gated (G2). This field is C1-fidelity applied to the standard.
authored: 2026-07-13
authored_by: claude-opus-4-8/wiki-master (CC session da51cc)
supersedes: source-page-standard-v3.md (deprecated-retained). v1.0/v2.0 retained for lineage.
governance: SemVer — MAJOR = function change = Jon sign-off; MINOR = additive check = batched; PATCH = auto
---

# Wiki Source-Page Standard v4.0

The single definition of **"done"** for a wiki source page — FL, personal, home, pro, co-equally.

**Lineage.** v1 flat-8 → v2 (1 substrate + 4 functions) → v3 (per-kind FORM: session|reference) → **v4
adds the `analysis` kind (G1) and extends fidelity vocabulary for certainty-disclosure (G2)**. Both
ratified by Jon 2026-07-13 on the strength of the calibration (90% error rate; finding F4 = the pipeline
inflates certainty). Permanent-ID lint-leaves and the migration map carry forward unchanged.

## The substrate + four functions
A page is **v4.0-conformant** when every check applicable to its `source_kind` is PASS / `unrecoverable` /
`N/A-by-kind` / `N/A-blocked`.

### FORM (substrate) — the page has the required shape for its `source_kind`
Every page declares **`source_kind:`** (machine-readable). Three kinds:
- **`session`** — a conversation extraction. Required: `## Summary`, `## Key Claims`, `## Conflicts`;
  conditional Entities/Cross-Wiki/Uncaptured. Has a raw; fixity applies.
- **`reference`** — a curated standing artifact (device/warranty/spec). Required: identity heading +
  domain sections. No Summary/KC/Conflicts. Verify against cited sources (ticket/URL/photo), not turns.
- **`analysis`** *(new, G1)* — a synthesis (`concepts/`, `analyses/`, `overview`). Required: thesis +
  synthesized claims + links. Summary/KC/Conflicts not required; `source_file: none` expected (no single
  raw). See VERIFY(analysis) below.
**Cascade:** FORM-fail for a session page (no `## Key Claims`) → VERIFY/RETRIEVE-of-claims grade
`N/A-blocked`, not FAIL.

### VERIFY — every substantive claim can be checked
- **E2 anchor.** *session:* `([slug:Tn])`, **resolved against `scripts/audit/turn_index.py`** (deterministic
  T-map; an anchor > verified turn-count is a lint FAIL). *reference:* source-citation; turn-anchor
  `N/A-by-kind`. *analysis (G1):* each synthesized claim **anchors to another wiki page** it rests on
  (`[[slug]]` / `[[slug:Tn]]` transitively) **or** carries **`[inferred]`** (the analysis's own synthesis).
  Plus a **staleness pin** `cited-page@audit_state` so a synthesis is flagged for re-check when a
  foundation page changes or re-verifies.
- **E2 population + threshold *(closes the E2-threshold open item; ratified 2026-07-26)*.**
  **Unit = the claim**, not the anchor: a top-level bullet under `## Key Claims`, with its nested
  sub-bullets folded into it. A claim is covered if **at least one** of its anchors satisfies its
  kind's form above. **No "substantive" filter — every top-level Key Claim counts.**
  **Threshold = 100%, per page** — not pooled across the corpus. Coverage is satisfied by a
  resolvable anchor **or** an explicit `unrecoverable` / `inferred` / `uncaptured` disclosure
  (option 3, Jon 2026-07-25), so 100% is reachable **without deleting a claim that cannot be
  sourced** — an unsourceable claim gets marked, not dropped. **This 100% is the eventual shape,
  not this cycle's operative number** — E2 is one axis the standing **interim-goalpost ratchet**
  (see below, added 2026-07-26) can sit on; when it does, the ratchet's currently-set value governs
  what's actually gated at a given standard update, and this clause's 100% remains the destination
  it ratchets toward. E2 itself is unchanged by the ratchet's existence — only which number is
  *operative this cycle* is a ratchet question, not an E2 question.
  - *Why no "substantive" filter.* The writer of a page would otherwise decide which of its own
    claims are substantive enough to need a citation, so the threshold is always met by shrinking
    its own denominator. That is `RATIO_FLOOR` inverted: a floor set unreachably low fires always
    and gets ignored; a threshold you can define your way past fires never. "Substantive" is also
    not Jon's word — his are *"Do all wiki articles now cite everything?"* and *"cite it de
    minimus"* (2026-05-26).
  - *Why per-page, not pooled.* Pooled coverage lets strong pages mask weak ones, and trust is
    extended to the page in front of the reader, not to a corpus average. Measured 2026-07-25 on
    one corpus: pooled 57.1% vs. per-page 48.9% — an 8-point gap that is entirely masking.
  - *Measured by* `scripts/lint_citation_coverage.py`, `method_version` `e2-methods/1.0.0`. Five
    methods, each reporting an option-3 and a strict number. **The gating method is per-page
    strict; the other four stay computed** so a future redefinition re-reads history rather than
    orphaning it (see Governance).
  - *The miss that motivated it* (admission gate): E2 as written carried no population and no
    threshold. Three implementations measured three different populations and none applied a
    threshold to E2's stated one. Sampled adjudication (n=40, two independent raters, 87.8% exact
    agreement, planted control caught by both) put genuine anchor support at **~40%** while the
    mechanical check read **96.7%**.
  - *Run cost* (admission gate): ~40 s over 218 source + 39 concept pages. Read-only; verified to
    mutate nothing across a full run plus a sample draw.
  - **Everything fails today under this axis specifically: per-page strict is 48.9%. The 100% above
    is a destination, not a description**, and ratifying it does not authorize a sweep to close the
    gap — that is separate work with a separate ask (per Jon's Q2, every phase merges on its own
    gate).
- **E3 fidelity + confidence *(extended, G2-now)*.** Every Key Claim carries one fidelity tag:
  `verbatim` · `paraphrase` · `reconstructed` · `contextual` · **`inferred`** (reconstruction/synthesis,
  not stated) · **`uncaptured`** (a known gap). A **certainty-inflation lint** flags the F4 patterns for
  human check: a recommendation verb attributed to Jon as a decision; a hedge-word ("presumably")
  promoted to a bare assertion; a tracker item marked done/"flagged" without a confirming anchor.
- **Recovery — resurfaced-branch** (key CC claims only): resume at exact context, log as disclosed
  `reconstructed` reconstruction; FBC the resurfacing. ASOP-41 discipline.

### RETRIEVE — every page/claim is findable and connected
- **E5 linkage** — every session Key Claim has ≥1 outward `[[link]]`; orphans flagged. reference/analysis:
  page indexed / claims link to foundations.
- **E6 findability** — `retrieval_key` (unique) + `aliases` (≥2). FAIR-grounded.

### TRACE — the page declares what made it and what it read
- **E7 provenance + reads-manifest** — `generated_by`; `extraction_by` iff a subagent contributed;
  `reads_manifest` when one exists. PROV/Datasheets-grounded.

### PRESERVE — nothing silently dropped
- **E4 uncaptured** — `## Uncaptured Content` assessment + **`uncaptured_assessed: empty|populated`** marker.
- **E8 fixity** — `source_file` resolves (or `unrecoverable` documented) + `raw_sha256` + `raw_length`.

## Confidence axis (C1) — split (G2, ratified)
- **Fidelity-confidence proceeds NOW** (above): the `inferred`/`uncaptured` tags + the inflation-lint are
  live presence checks — the wiki begins to wear its uncertainty at the *fidelity* level.
- **Truth-confidence C1 stays ASOP-gated.** How-sure-is-this-true (high/med/low) is the ASOP-41/23/1
  disclosure construct; it lands only after the Tier-1 ASOP ingest (a6314b→100%, T-85 modal-language
  first — **prioritized** per Jon 2026-07-13; grounded partly by a Jon grilling). Words-reify: don't
  reify instinct as the canon of a framework Jon holds professionally.

## audit_state & authority (G3, ratified)
`unaudited` → `linted` → `verified@{standard-ver, date, source-hash}`. Any page not `verified@current` has
demoted authority — surfaced as UNVERIFIED, not built upon. `linted`/anchored never displays as `verified`.
See `audit-state-and-authority.md`.

## Governance (interim), Migration Map, tooling
SemVer + deprecate-never-delete + provisional-entry + presence-expressibility admission gate (new checks
cite the miss that motivated them + a run-cost note). Migration map (permanent IDs) carries forward; add:
`FORM.kind` covers `analysis`; `VERIFY.anchor` parameterized per kind; E3 vocab extended (same ID).
Deterministic tooling: `census.py`, `turn_index.py` (3 header styles), `lint.py` → conformance ledger.

**Measurement versioning *(added 2026-07-26)*.** Any change to what a reported number *means* bumps
`METHOD_VERSION` in the measuring script; the old series stays labelled rather than being overwritten.
All methods stay computed even when only one gates, and nothing is cached — a number is re-derived at
every SU (Q3). This holds because the wiki's history is in git and the instrument is a pure function of
a tree: a redefinition **re-reads** history rather than orphaning it. Verified 2026-07-26 by recomputing
the 2026-07-14 tree (`7c9fa52`) under the current method. Caveat: `raw/` is gitignored, so a historical
worktree has no transcripts — anchor-correctness is only recomputable against the corpus as it currently
stands, and the measuring script's `--raw-root` exists to make that decoupling explicit rather than
silent.

## Interim goalposts — the ratchet *(added 2026-07-26, program-level, not an E2 check)*

**This is a standing mechanism, not a metric.** It does not belong to E2, or to any single check —
it is how *any* check in this standard that isn't yet ready to gate at its eventual shape moves
toward that shape over time. Naming it as "E2's threshold, now ratcheting" would make E2 mean two
different measured quantities at once (a per-page claim-anchor ratio, and whatever a future cycle
picks); that is exactly the kind of undefined-term sprawl this document exists to prevent, so the
ratchet gets its own name and its own section instead.

Jon rejected a fixed number on PR #122 review, in terms that describe a mechanism, not a metric:

> `:345` — "Its deliberately not exhaustive, its self improvement we don't know the end, we can see
> some goalposts along the way. Focusing on 100% generally makes performance worse in humans."

> `:330` — "The number is mine, the number requires you be able to explain everything in it in a
> clean concise way that, based on what I've said, you expect hits that definition."

**Definition, axis-agnostic.** Each cycle (standard update) that uses the ratchet:
1. Names **which axis** this cycle's goalpost sits on (a specific check, or a specific instrument
   reading — E2's per-page claim-anchor ratio is one possible axis, corpus conversation-coverage is
   another; different cycles may sit on different axes, which is what "some goalposts along the
   way," plural, describes).
2. Names **the instrument** that measures that axis.
3. **Measures**, then sets the **next** goalpost from the number actually observed — not from a
   number chosen in advance of measuring it.
4. Carries **the value Jon sets** — his to set, each cycle, not the standard's default and not the
   measuring agent's extrapolation. Every reported figure ships with a concise explanation of what's
   inside it (population, exclusions, method version) as his stated condition for setting it, not as
   a courtesy gloss.

**The goalpost is monotonic non-decreasing: it may rise or hold from one cycle to the next, but it
may never be lowered to accommodate a bad month.** A cycle that measures worse than the standing
goalpost is a miss against that goalpost, not grounds to move the goalpost down to meet it.

**This governs pace, not shape.** Wherever the ratchet sits on a check whose eventual shape is
already ratified (E2's 100%, per turn 7), that shape is untouched — the ratchet only sets what's
operative *this cycle*, never what the check ultimately means.

**Cycle 1 — axis, instrument, value.**
- **Axis: the UNEXAMINED count** — not "uncovered" loosely. `scripts/audit/coverage_gap.py` splits
  every corpus conversation without a wiki page into two registers that are opposite *decisions*,
  plus a third bucket that is genuinely undecided:
  - **STUBBED** — deliberately stubbed in `wiki/sources/session-stubs.md`: examined, judged no page
    is owed. A decision.
  - **QUEUED** — listed in `wiki/references/ingest-queue.md`: examined, judged a page IS owed, not
    yet written. Also a decision — the opposite one.
  - **UNCOVERED / unexamined** — in neither register: nobody has looked, and the wiki cannot
    currently tell that apart from "looked and judged not worth it." **This third bucket is cycle
    1's axis.** STUBBED and QUEUED are both dispositioned; conflating either into the axis would
    goalpost a number that silently includes committed-but-unwritten work, or work deliberately
    declined — measuring two different things and calling them one, the same conflation this branch
    already caught once between E2 and conversation-coverage generally, one level down.
  Chosen over citation-density for cycle 1, basis ratified 2026-07-26: the coordinator recommended
  it because **"a missing page costs more than a weakly-anchored one"** — and it is specifically the
  *unexamined* conversation this is aimed at: a page that doesn't exist yet and has never even been
  looked at fails every check in this standard at once with nothing on record, where a
  weakly-anchored page fails only E2 and a queued-but-unwritten page at least has a decision behind
  it. Jon: *"That sounds great."* This choice is cycle 1's, recorded so cycle 2's axis choice is
  legible against it, not a redefinition of E2 or a claim that conversation-coverage replaces it.
- **Instrument:** `scripts/audit/coverage_gap.py`. As of 2026-07-26 it reads both registers (fixed
  by PR #158 — it had previously known only `session-stubs.md` and read `ingest-queue.md` as if it
  didn't exist, which misreported every queued-but-unwritten conversation as unexamined).
- **Measured basis, all four counts** (244 distinct corpus conversations):
  - covered by a wiki page — **172 (70%)**
  - deliberately stubbed, no page owed — **27**
  - queued for ingest, a page is owed and unwritten — **8**
  - **UNCOVERED / unexamined — 37 (15%)** — this is cycle 1's number.
  **Computed directly against the tracked repo checkout, where `raw/` is present** — not carried
  from a brief and not recomputed in an off-Drive worktree missing `raw/`. That is a stronger
  provenance claim than this section originally carried (its first draft used 172/241, 42
  uncovered — figures that predate the register fix and conflated QUEUED into UNCOVERED; corrected
  here rather than left standing).
- **Value: `[JON — first goalpost value]`.** The axis is ratified; the number is not set here.
  Writing one in would repeat the exact defect this program exists to catch — Jon's provisional
  words recorded as a decision, confirmed twice this cycle already.

**Consequence — corrected 2026-07-27, because the first version of this sentence was over-broad.**
It said all seven of the wayfinder-gate acceptance criteria "become goalposts under this same
ratchet." **Only three do.** A monotonic ratchet has nothing to say about a binary: C2 (claim
traceability), C3 (anchor correctness) and C4 (Jon's words cited) are proportions with distance left
to travel and can carry a goalpost; **C1 (zero canonical leaks), C6 (both lints exit 0) and C7
(reasoning visible) are zero-gates** — "better than last month" is not a gate. C5 is neither: it is
**not currently evaluable at all**, because `audit_state`'s hash covers the raw source rather than
the page, so a page marked `verified` can have every claim rewritten and still read verified. Those
corrections live in the gate file itself; that file is untouched by this edit.

## Ratification
DRAFT — written, not committed. Jon ratified the *content decisions* (G1 analysis kind; G2 fidelity
extension + C1-gated) 2026-07-13; this document operationalizes them. Open: C1 placement (post-ASOP),
governance-tier finalization, reads-manifest scope.
