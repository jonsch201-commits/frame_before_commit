---
title: Coordinator (role) — CFL multi-agent orchestration layer
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (fleet); sub: fleet 10 vs wiki 1 on authored labels"
type: concept
first_seen: conductor-execution-manager-crossvenue-intake-2026-07-18-78619b
source_count: 5
last_updated: 2026-07-23
---

## What This Is

The Coordinator is the foreground, interactive, top-tier CC session that sits above the PM (project-manager)
layer in the CFL fleet: it does not execute work itself, it coordinates PMs, may consult the fable-mirror
(claude.ai transcript corpus), and closes every run by coordinating a standard update. It descends from a
2026-07-18 design packet that separately proposed a **Conductor** (portfolio scheduler/router, propose-only,
never executes) and an **Execution-Manager** (single-work-packet orchestrator) — role names later folded
together (Conductor MERGE → Coordinator; EM KILL-now/concept-in-reserve) once the subagent architecture made
EM's schedule/run split redundant ([coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477]).

## What the Wiki Says

- Adopted via PR #50 (2026-07-19); eight executor agent defs adopted via PR #51 — the earlier "Conductor" design
  packet is its direct ancestor, not a competing role ([conductor-execution-manager-crossvenue-intake-2026-07-18-78619b]).
- Coordinator charter, ratified 2026-07-21 (Item 8 of the fable-mirror pipeline packet): foreground/interactive,
  runs nothing itself, membrane with exactly two ratified crossings (mirror corpus in, escalation packets out) —
  no third crossing without new ratification ([coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477]).
- **PM (project-manager) role exists in the org chart as the tracker-owning slot (per DS-8) but was, as of
  2026-07-21, undefined/unchartered** — the coordinator was found to be holding PM-grain work itself in the
  absence of a chartered PM, which Jon explicitly ruled out ("coordinator coordinates PMs; it holds no
  projects"). Two PM portfolios were structured that session: PM-1 (infrastructure suite) and PM-2 (journey
  suite / rest-of-phase-1 per the 78619b runbook) ([coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477]).
- **Reviewability Standard** (2026-07-22, supersedes an earlier same-session "one turn → one PR" rule that Jon
  found insufficient in practice): PRs must be decision-grain ("merge this if you agree that ___" in one
  clause), the review guide *is* the PR description (not a companion file), fresh-eyes self-contained, and
  every `TO: jon` message opens with an ACTIONS block above an FYI fold
  ([coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477]).
- **Addressing rule:** every coordinator/PM output must open with `TO:` (jon / triage / a PM / split sections);
  untagged output is a logged codex breach ([coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477]).
- As of origin/main HEAD 3cf476e (2026-07-22, verified by this ingest's git-log inspection), PRs #69–#76 —
  covering the mirror pipeline build, the PR re-cut, and the role-taxonomy decision (Coordinator KEEP /
  Conductor MERGE→Coordinator / EM KILL-now / PM KEEP) — are merged. The cold-review outcome for #76 and the
  precise text of Jon's final taxonomy ruling are not captured in any source page ingested so far — see
  `wiki/intake-triage/jon-turn3-review-standard-and-merge-plan-2026-07-22.md` (untracked as of this writing;
  not ingested by this pass — see this session's PR description for detail).
- **Taxonomy ratified 2026-07-22** ("Ratify as tabled," Jon): Coordinator KEEP; Conductor MERGE→Coordinator
  (graft register + override-rate calibration/demotion + cost-of-error model tiering); Execution-Manager
  KILL-now/concept-in-reserve **with one non-optional standing charter invariant** — the schedule/run
  separation EM existed to enforce must be written into the coordinator charter as an explicit fence ("a
  session that plans the portfolio does not execute work packets in the same context"); EM's death removes the
  role, not the invariant. Project-Manager KEEP. Net 4→2 standing roles. Full five-step provenance chain
  (recovered 78619b packet → PR #76 → independent cold review → wayfinder ballot → Jon ratification) recorded
  at `wiki/sources/infrastructure/role-taxonomy-ratification-2026-07-22.md`
  ([role-taxonomy-ratification-2026-07-22]). **Not yet verified by this ingest:** whether the EM-invariant
  sentence has actually landed in `exchange/coordination-charter-2026-07-21.md` — flagged as an open item on
  that source page, not resolved here.
- **BUILD→DEPLOY pivot, turn-5, ratified 2026-07-22:** turns 1–4b (charter, mirror pipeline, taxonomy,
  PM structure, Pocock incorporation, 78619b recovery) close out BUILD; turn-5 opens DEPLOY. Criterion,
  stated precisely: *"Jon's evenings become review-and-decide rather than build"* — bounded, scheduled,
  priced review-minutes, **not zero-Jon**. An earlier "evenings are his own" phrasing in the coordinator's
  own upward return was a strengthening-in-transit (coordinator overreach), corrected by the wayfinder;
  review-and-decide is the chartered bar. **Rider 1 (measure, don't vibe):** deployment success = Jon-minutes
  actuals vs. estimates per lane, reported in the gate-report. **Rider 2 (the clock never compresses the
  gates):** M-chain gates run at full depth toward 08-01 — the date yields, not the gate. Further
  infrastructure must clear the bar "does it save Jon-minutes before 08-01?"; default answer is no.
  ([deploy-phase-delegation-clause-2026-07-22-turn5])
- **Delegation clause (codex rule 4, turn-5), operating parameter:** within direction Jon has already
  ratified, the coordinator exercises delegated best-practice judgment on coordination *mechanics*
  (sequencing, packaging, routing, budgeting Jon's review-minutes) without per-item re-ratification. Reserved
  to Jon always: merges to `origin/main`, gates G1–G4 and successors, anything identity-adjacent, new
  ratifications (roles/charters/membrane crossings), agent registration, spend/plan changes, and anything the
  wayfinder itself flags as exceeding scope. Silence remains uninformative; every dispatch under this clause
  must cite it, and Jon can revoke or narrow it with a sentence.
  ([deploy-phase-delegation-clause-2026-07-22-turn5])
- **Review-budget protocol (turn-5, under the delegation clause), operating parameter:** Jon-asks arrive
  batched, priced, above the fold; the coordinator actively shapes the batch to target **≤15 Jon-minutes per
  batch**, highest-leverage first, with any deferral carrying a named cost. The gate-report's
  actuals-vs-estimates table is the feedback loop on whether the budgeting is working.
  ([deploy-phase-delegation-clause-2026-07-22-turn5])

## Conflicts

**Resolved 2026-07-22** (was open at last ingest): the role-taxonomy ⚠️ CONFLICT between the adopted
Coordinator and the proposed Conductor/Execution-Manager is now ratified — see
`wiki/sources/infrastructure/role-taxonomy-ratification-2026-07-22.md`. That page also carries forward, as a
genuinely still-open gap, whether the independent cold review of PR #76 is documented anywhere as a primary
artifact in its own right (the "concur, 4→2" outcome is attested only secondhand inside the ratifying packet,
not as a citable standalone report) — this is not a conflict between existing wiki claims, but a provenance
completeness gap worth a reader's caution.

## Related

[[extraction-pipeline]], [[frame-before-commit]], [[bgisolation-membrane]], [[fable-mirror]], [[transcript-corpus]],
[[design-execution-split]], [[loop-taxonomy]]
