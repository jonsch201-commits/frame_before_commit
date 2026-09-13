---
title: "Corpus-Remediation Audit Program — the Design Advisory that da51cc Executed (born-at-standard, the loop, the fleet, Max-plan budget)"
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: sub-branch too close to call: fleet 3 vs corpus 3 (margin < 1)"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-13-ca3309-wiki-index-staleness-and-fbc-planning-forks.md
date: 2026-07-13
date_updated: 2026-07-13
date_ingested: 2026-07-18
type: session
source_kind: session
uuid: ca3309
domain: infrastructure
tags: [wiki-master, corpus-remediation, audit-program, born-at-standard, conformance-ledger, model-fleet, source-kind, verify, fbc, ssp, max-plan, budget, gated-decisions]
generated_by: claude-fable-5/claude-ai
continues: none
---

## Summary

The 2026-07-13 claude.ai (Fable 5) advisory session that answered a six-part design question about the wiki audit program and produced the verbatim **CC packet + amendment** pasted back into the Opus 4.8 CC session `da51cc` to execute. Its load-bearing move is a **reframe**: the pilot's error findings make this **corpus-correctness remediation with an unknown error base rate**, not metadata backfill — "an agent reading confidently-wrong pages doesn't have continuity, it has false memory with good retrieval." Nearly all of the architecture here is Claude's *recommendation* (provisional, binds at next ratification); only Q1/Q2/Q3 and the budget frame are Jon-ratified. The design counterpart to the execution page [[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont]].

## Key Claims

### Jon-ratified decisions (the F4 line — everything else here is recommendation)

- **Q1 — born-at-standard, effective immediately: RATIFIED "Yes."** New pages verify at creation (nearly free — source is in context); interim inline anchoring by the workhorse until the claims-parser lands ([ca3309:T4]).
- **Q2 — personal/ trunk: READ approved** for census/calibration/audits; **automated WRITES/repairs HELD** pending wiki-master personal-trunk conventions → new gated item **G4**. Jon's words: *"May read, should consider wiki master improvements related to reading and editing personal trunk"* ([ca3309:T4]).
- **Q3 — calibration batch APPROVED**, and the resource frame changed: *"I now have Max plan, and I expect you to plan to use roughly 80% of the monthly budget on this project, with discussion at each material decision point"* ([ca3309:T4]). Claude read this as compute allocation, not attention — *"80% of budget is compute allocation, not your time"* ([ca3309:T5]).
- **Material decision points enumerated** (Jon discussion required): anything GATED (G1–G4), calibration return + cadence setting, any workstream reallocation >~15% of the monthly envelope (provisional threshold), any semver-major, any expansion of personal/ automation ([ca3309:T5], the pasted packet amendment's "MATERIAL DECISION POINTS" block).

### Claude's recommended architecture (PROVISIONAL — binds at next ratification unless marked GATED)

- **The reframe (adopt):** corpus-correctness remediation with unknown error base rate; the conformance standard is the instrument; the pilot's error rate is n=1 → calibrate before pricing cadence ([ca3309:T1], "## The reframe the pilot forces").
- **The loop:** census → calibration (10–12 stratified pages) → **three concurrent triggers** — read-triggered repair (frequency), scheduled tail sweep (severity tail), event-triggered escalation (an error is evidence about a process, flag sibling pages of the same vintage) ([ca3309:T1], "## 1. The loop").
- **Resumability = honesty:** the conformance ledger is the checkpoint; one page = one row = one commit; front-matter `audit_state: unaudited → linted → verified@{standard-ver, date, source-hash}`; **lint must never display as verified** ([ca3309:T1], "## 1. The loop", "Resumability and honesty are the same mechanism" paragraph).
- **Orchestration — code before models:** deterministic work (fixity, link graphs, ledger writes, manifest conversion) spends zero tokens. Fleet: cheap tier (census/pre-staging/housekeeping), workhorse (extraction, turn-alignment, fidelity tags, discrepancy reports — **flags, never rules**), deep-judgment adjudicator (flagged deltas + omission calls only), narrative-tuned (uncaptured prose + rewrites, **round-tripped** because fluency is the fidelity threat). **Generator ≠ grader at task level; Jon = acceptance sampling** with a decaying inspection rate ([ca3309:T1], "## 2. Orchestration").
- **Context packets per task** = the check definitions graded + pinned artifacts + output schema + an escalation slot; exclude the governance doc/history; every task emits a reads-manifest ([ca3309:T1], "## 2. Orchestration", final paragraph).
- **Tooling build order:** linter harness (the real product) → fixity computer → conformance-ledger generator → source_kind classifier (conversation-extract / curated-reference / CANDIDATE-ANALYSIS) → claims-parser (the long pole, start day one, VERIFY runs provisional until it lands) → manifest converter last ([ca3309:T1], "## 3. Tooling sequence").
- **GATED G1 — "analysis" as a third source_kind parameterizes VERIFY itself** (claims anchor to wiki pages or declared inference, not source turns; needs a cited-page@version staleness check) — a function-meaning change = **major version, Jon sign-off**; reuse the provenance-bracket vocabulary ([ca3309:T1], "## 5. Taxonomy").
- **GATED G2 — decompose claim-confidence:** ship **fidelity-confidence** now (verbatim/paraphrase/inferred/uncaptured, lintable-as-presence); **hold truth-confidence** on the professional-standards (ASOP) ingest so the vocabulary is born compatible and avoids a 183-page migration ([ca3309:T1], "## 6. Claim-confidence").
- **Admission-gate additions (provisional):** a new check must cite the postmortem miss that motivated it (postmortem-born, not brainstorm-born) and carry a run-cost note — the structural counter to "check proliferation," named as Jon's elaborateness-substituting-for-execution failure mode ([ca3309:T1], "## 4. Self-improvement without you as bottleneck").

### Routing and a staleness flag

- The packet addresses da51cc as **orchestrator and adjudicator, not sole executor** — mechanical build delegates down to workhorse/cheap tiers; if that CC session had closed, both fenced blocks work in a fresh repo CC session that reads the standard doc from disk ("do not re-derive" = read, not reconstruct) ([ca3309:T3], packet preamble, "You hold the standard doc, pilot findings, and repo — do not re-derive them").
- **Index-staleness flag:** the claude.ai FL project's injected FBC skill copy lags the 2026-07-07 GBS×FBC point-of-commitment refinements — refresh project files ([ca3309:T1], orientation line before "Topic is clear").

## Entities & Concepts

[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont]], [[wiki-ingest-methodology]], [[multi-agent-orchestration]], [[actuarial-epistemology]], [[ground-before-stating]], [[frame-before-commit]], [[citability-standard]] — plus: audit_state, source_kind, VERIFY, conformance ledger, born-at-standard, acceptance sampling, generator≠grader, G1–G4 gated items

## Conflicts

None as contradiction — this is the DESIGN origin; da51cc is the EXECUTION. Note that G1 (analysis-VERIFY) and G2 (truth-confidence) remain **unratified/gated** here, consistent with the da51cc page's Conflict #7 (the v4.0 standard materially amends the wiki-master 7-phase SKILL.md; resolution is Jon's, skills-master owns the edit).

## Cross-Wiki

- [PERSONAL] Q2 opens automated **read** access to `wiki/personal/` for audits, with writes gated (G4) and privacy rules (reference-by-ID, personal content never quoted verbatim in shared queues/logs). A material governance change for the personal wiki.

## Uncaptured Content

a) The two fenced packets (the advisor return + the amendment) are reproduced in the raw and were the session's actual deliverable; only their structure is summarized here.
b) **Unfollowed threads:** the "standing commitment to raise the moral hierarchy in week-4 planning" was explicitly deferred as off-topic ([ca3309:T1]); the specific eight check IDs and fidelity-tag taxonomy were requested-back from CC, not supplied in-session ([ca3309:T1], closing paragraph).
c) **Absent technical detail:** the exact calibration stratification, the sweep cadence math (priced off measured minutes/page), and the budget burn-proxy metrics (sessions/hours/pages) were left to calibration return.
d) **Turn T2 (Human) and T6/T7 (the session's tail)** are not drawn on above: T2 is Jon's own clarifying meta-question ("I cannot fully opine due to limited attention capacity...") which reroutes T3 into a condensed CC-facing packet rather than adding new design content; T6/T7 are Jon confirming the amendment was addressed to the Opus 4.8 CC session and Claude's brief confirmation — administrative, not substantive.
