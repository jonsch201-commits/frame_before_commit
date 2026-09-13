---
title: Ratification Packets — G1 (analysis kind), G2 (confidence axis), G4 (personal-trunk)
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-REF; sub: sub-branch too close to call: wiki 3 vs fleet 3 (margin < 1)"
status: AWAITING JON — gated items; packets prepared, not implemented (per advisor packet governance)
authored_by: claude-opus-4-8/wiki-master (CC session da51cc, 2026-07-13)
---

# Ratification Packets — G1 / G2 / G4

Each is a MATERIAL DECISION POINT reserved for Jon. G3 is already ratified. Below: what, why (grounded in
calibration), the exact proposed rule, version impact, and the decision.

---

## G1 — `analysis` as a third `source_kind`  (MAJOR → Standard v4.0)

**Why.** The census found **~36 pages (20% of the corpus)** are *syntheses* — `concepts/`, `analyses/`,
`overview` — not conversation extractions. Calibration confirmed (`actuarial-epistemology`): they have no
single raw, their claims cite *other wiki pages*, and the session/reference rubrics can't grade them. They
are currently ungradeable and stuck at `unaudited`.

**Proposed rule.**
- Add `source_kind: analysis`.
- **FORM (analysis):** a synthesis structure (thesis + synthesized claims + links); Summary/Key-Claims/
  Conflicts not required; `source_file: none` is expected (no single raw).
- **VERIFY (analysis) — parameterized:** every synthesized claim either (a) **anchors to another wiki
  page** it rests on — `[[slug]]` or, when it leans on a specific claim, `[[slug#claim]]` / `[[slug:Tn]]`
  transitively — **or** (b) carries an **`[inferred]`** tag marking it as the analysis's own synthesis not
  traceable to one source. (Reuses the fidelity-bracket vocabulary.)
- **Staleness check:** an analysis claim citing a source page pins `cited-page@audit_state` (or @version),
  so when the underlying page is re-verified or changed, the analysis is flagged for re-check. This is how
  syntheses stay honest as their foundations move.
- Migration: the ~36 candidate-analysis pages get `source_kind: analysis` + graded under this rubric.

**Version.** MAJOR (new function parameterization) → **v4.0**, Jon sign-off.
**DECISION:** ratify `analysis` kind + its VERIFY/staleness rule as above? (ratify / modify / defer)

---

## G2 — confidence axis  (split: fidelity-confidence NOW; truth-confidence ASOP-gated)

**Why.** Calibration **finding F4**: the pipeline systematically **inflates certainty** — Claude's
recommendations recorded as Jon's decisions, hedges ("presumably") as settled facts, unconfirmed proposals
as actioned. The errors are *directional*, not random: the wiki erases uncertainty. This is exactly the
ASOP-41 disclosure-under-uncertainty gap.

**Proposed rule (two parts).**
- **NOW (proceeds as a presence check, no gate):** extend E3 fidelity vocabulary to include **`inferred`**
  (claim is reconstruction/synthesis, not stated) and **`uncaptured`** (a known gap) alongside verbatim/
  paraphrase/reconstructed/contextual. The linter already accepts these; this makes them standard. A
  companion lint heuristic flags **certainty-inflation patterns** for human check (a recommendation verb
  attributed to Jon; a hedge-word promoted to a bare assertion; a tracker item marked done without a
  confirmation anchor).
- **GATED (stays held on the Tier-1 ASOP ingest):** the **truth-confidence axis C1** — *how sure are we
  this is true* (high/med/low), distinct from fidelity — remains gated because confidence-disclosure IS
  the ASOP-41/23/1 construct and must be grounded in it, not in instinct (words-reify). **F4 is strong
  evidence to PRIORITIZE the ASOP ingest** (a6314b→100%, T-85 modal-language first) so C1 can land.

**DECISION:** (a) confirm fidelity-confidence tags + the inflation-lint proceed now; (b) confirm C1 stays
ASOP-gated **and** approve prioritizing the Tier-1 ASOP ingest so C1 can be unblocked. (yes-both / modify)

---

## G4 — personal-trunk read/edit conventions  (unblocks personal remediation)

**Why.** Personal pages hold sensitive family/financial/health content. Q2 approved READ (census,
calibration, audit — done, under G4-preview discipline); automated WRITES are HELD until these conventions
ratify. The 3 personal calibration pages are audited and waiting.

**Proposed conventions** (the calibration audits already followed these as a preview):
- **Least-context:** any task touching `personal/` receives only the page under test + its raw — no
  cross-trunk context.
- **Reference-by-ID / no verbatim personal content in shared surfaces:** discrepancy reports, the shared
  conformance ledger, logs, escalation files carry grades + abstracted error-types + turn anchors —
  **never** verbatim personal specifics (names, dollar figures, accounts, health, addresses). Commit
  messages and PR text for personal remediations are likewise abstracted.
- **Grades-only ledger rows** for personal pages (audit_state + PASS/FAIL, no claim text).
- **Write protocol:** automated remediation may write to `personal/` **only after this ratifies**; each
  personal page = its own commit; content abstracted in all shared metadata.
- **Escalation-in-scope:** anything needing Jon on a personal page is surfaced as an *abstracted* flag;
  full detail on request through a private channel, not the shared PR.

**DECISION:** ratify these conventions (then personal remediation proceeds under them)? (ratify / modify)

---

## If ratified
- G1 → write Standard v4.0 (analysis kind) + migrate ~36 pages into the audit queue.
- G2 → fold fidelity-confidence + inflation-lint into the linter now; sequence the ASOP ingest to unblock C1.
- G4 → remediate the 3 audited personal pages under the conventions; open personal/ to the sweep.
