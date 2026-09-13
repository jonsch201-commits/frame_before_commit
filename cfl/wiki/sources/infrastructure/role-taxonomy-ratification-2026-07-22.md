---
title: Role Taxonomy Ratification — 4→2 Standing Roles (Coordinator/Conductor/Execution-Manager/PM), Full Provenance Chain
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 8 vs wiki 5 on authored labels"
date_ingested: 2026-07-22
type: ruling-record
tags: coordinator, conductor, execution-manager, project-manager, role-taxonomy, ratification, T-117, PR-76
provenance_chain:
  - step: 1
    what: Recovered 78619b packet §§2–3 (proposed Conductor + Execution-Manager role designs, 2026-07-18)
    where: wiki/sources/infrastructure/conductor-execution-manager-crossvenue-intake-2026-07-18-78619b.md; full transcription wiki/intake-triage/conductor-em-crossvenue-intake-2026-07-18.md
  - step: 2
    what: Decision packet #76 — coordinator's self-authored keep/merge/kill recommendation (Coordinator KEEP, Conductor MERGE→Coordinator, EM KILL-now/reserve, PM KEEP); self-reference flagged, not ruled by the coordinator itself
    where: exchange/role-taxonomy-decision-packet-2026-07-21.md (merged as PR #76, commit 115d420)
  - step: 3
    what: Independent cold review — fresh session, primary docs only (adopted charter, recovered packet §§2-3, DS-8), wrote nothing of #76 — ordered specifically because "flagging is not independence"; result concur, 4→2
    where: ordered by jon-turn3-review-standard-and-merge-plan-2026-07-22.md ACTION 5; outcome referenced in jon-turn4-taxonomy-ratified-pm-unblock-2026-07-22.md provenance line (no independent cold-review report file located in the tracked repo as of this ingest — see Conflicts/Gaps below)
  - step: 4
    what: Wayfinder ballot — Jon's ruling relayed via the claude.ai FL wayfinder (Fable 5), turn 4
    where: wiki/intake-triage/jon-turn4-taxonomy-ratified-pm-unblock-2026-07-22.md (untracked at origin/main as of this ingest — Jon-authorized Drive write to intake-triage, "Write it", 2026-07-22)
  - step: 5
    what: 'Jon ratification: "Ratify as tabled" (2026-07-22), with one added non-optional invariant'
    where: wiki/intake-triage/jon-turn4-taxonomy-ratified-pm-unblock-2026-07-22.md, ACTION 1
---

## Summary

This page records the ratification of the CFL role taxonomy — the resolution of the ⚠️ CONFLICT
between the coordinator role (adopted PR #50, 2026-07-19) and the separately-proposed Conductor /
Execution-Manager roles (recovered 78619b packet, 2026-07-18). Net effect: **4 proposed/adopted
roles collapse to 2 standing roles** — Coordinator and Project-Manager — plus the existing executor
subagent fleet. This is the wiki's authoritative record of that ruling and its full five-step
provenance chain, per the coordinator's dispatch request (`jon-turn4-...` ACTION ①, "Wiki-master
records the ruling with full provenance... in ③'s dispatch").

## The Ruling, As Ratified (Jon, 2026-07-22, "Ratify as tabled")

| Role | Disposition | Detail |
|------|-------------|--------|
| **Coordinator** | **KEEP** | Ratified portfolio layer (charter: `exchange/coordination-charter-2026-07-21.md`, Item 8). Nothing to decide except what folds in below. |
| **Conductor** | **MERGE → Coordinator** | Same role under two names, arrived at independently on two dates. Graft into the coordinator charter: the **register** operation (session-registry drafting, `wiki/tracker/sessions.md`), the **override-rate calibration + demotion path** (gate-report kill-check: >40% override ⇒ demote to a session-order checklist), and **cost-of-error model tiering** (Sonnet-default for routine planning, escalate on gate conflicts). "Conductor" as a name is retired — no new role, a better-specified coordinator. |
| **Execution-Manager** | **KILL now, concept-in-reserve** — **with one non-optional standing charter invariant** | The subagent architecture already gives the schedule/run separation EM was designed to enforce (an executor runs in its own context; the coordinator dispatching it is not running the work). A standing EM *skill* would be taxonomy proliferation the recovered packet's own anti-taxonomy fence warns against (§3.1: "naming a recurring observed shape is documentation, not taxonomy... keep it to one page and create nothing else"). **However**, Jon's ratification adds what the #76 packet's KILL recommendation did not carry on its own: EM's death removes the *role*, not the *invariant* — the coordinator charter must carry an **explicit fence, non-optional**: *a session that plans the portfolio does not execute work packets in the same context.* Without this line written into the charter, the da51cc accumulation pattern (a layer quietly growing past what anyone tracks) has no fence once EM-as-a-role is gone. **This charter edit is not yet confirmed landed** — see Open Items below. |
| **Project-Manager** | **KEEP, unchanged** | Distinct axis from coordinator: PM *owns state* (tracks `wiki/tracker/`), coordinator *coordinates PMs* and holds no projects itself. No conflict; PM-1/PM-2 *instances* are a deployment structure evaluated separately, gated on this ruling. |

**Net: 4 proposed/adopted roles → 2 standing roles** (Coordinator, Project-Manager) + the existing
eight-agent executor fleet (`.claude/agents/*.md`).

## Full Provenance Chain (five steps)

1. **Recovered 78619b packet §§2–3** (`conductor-execution-manager-crossvenue-intake-2026-07-18-78619b`)
   — the original 2026-07-18 proposal, presented in-session but never landed in the repo until
   recovered as a Google Doc and transcribed 2026-07-21/22. Proposed Conductor (portfolio
   scheduler/router, propose-only, Sonnet-tier, demotion path) and Execution-Manager (single-work-
   packet orchestrator, mutual-exclusion with conductor) as two roles, both never adopted.
2. **Decision packet #76** (`exchange/role-taxonomy-decision-packet-2026-07-21.md`, merged commit
   `115d420` into PR #76) — the coordinator's own keep/merge/kill recommendation, laid out on
   primary documents with an explicit self-reference caveat: *"this is the coordinator instance
   reasoning about the layer it embodies... the ruling is Jon's; my job is to make it decidable on
   primary documents, not to settle it."* Recommended: Coordinator KEEP, Conductor MERGE→Coordinator
   (graft register + calibration + model-tiering), EM KILL-now/concept-in-reserve (counter-argument
   for KEEP stated fairly), PM KEEP.
3. **Independent cold review** — ordered by `jon-turn3-review-standard-and-merge-plan-2026-07-22.md`
   (ACTION ⑤) precisely because "your self-reference flag was honest; flagging is not
   independence." Specified as a fresh session, primary docs only (adopted charter, recovered
   packet §§2–3, the `project-manager` skill/DS-8), which wrote nothing of #76 itself. Its mandate:
   concur/dissent per role, with citations, report alongside the coordinator's own before Jon
   rules. **Outcome, per the turn-4 packet's own provenance line: "concur, 4→2."** ⚠️ **Gap**: no
   standalone cold-review report file was located in the tracked repo or in the untracked
   intake-triage files present at this ingest — the concurrence is attested only secondhand, inside
   the turn-4 packet's `provenance_inputs` field ("cold-review concurrence (4→2, per that
   read-out)"), not as a citable primary document in its own right. This gap is also flagged in
   `wiki/concepts/coordinator.md`'s existing Conflicts section ("whether the coordinator's cold
   review of PR #76... was actually run by an independent instance before Jon's final ratification
   — no source page yet confirms this happened") and is **not resolved by this ingest**.
4. **Wayfinder ballot** — Jon's ruling, relayed through the claude.ai FL wayfinder venue (model
   "Claude Fable 5," turn 4), captured in
   `wiki/intake-triage/jon-turn4-taxonomy-ratified-pm-unblock-2026-07-22.md`. This packet is the
   wayfinder ballot: it carries Jon's verbatim ruling quote and the provenance chain's own final
   line ("Ratification provenance chain for the wiki record: packet §§2–3 (recovered 78619b
   artifact) → #76 keep/merge/kill → independent cold review (concur, 4→2) → wayfinder ballot →
   Jon: 'Ratify as tabled.'"). Note: this file is **Jon-authorized to be written to
   `wiki/intake-triage/`** ("Write it", 2026-07-22) but was **not yet present at `origin/main` as of
   this ingest** — it exists on-disk in the working tree this ingest read from. It is the Triage
   inbound surface; wiki-master does not write to it, only reads it as primary evidence for this
   record.
5. **Jon ratification.** Verbatim, per the turn-4 packet: *"I approved 75 and merged it. Ratify as
   tabled. Write it."* — with the added EM-invariant condition spelled out above. This is the
   binding disposition; steps 1–4 are the record of how it was reached, not alternative rulings.

## What This Unblocks (per the ratifying packet, not yet independently verified by this ingest)

- **PM charter work proceeds**: `skills/project-manager/SKILL.md` (S1 contract), then PM-1
  (Infrastructure) and PM-2 (Journey) charters, per the turn-2 structure — with one correction:
  PM-2's inherited M3-B test (EM cold-start) is **obsolete as written** (EM is dead) and needs a
  replacement (candidates named in the packet: test the EM-invariant under load, or PM cold-start
  acceptance). Do not run M3-B as originally specced.
- **Coordinator charter edit**: the EM-invariant fence (schedule/run separation, non-optional) must
  be written into the coordinator's charter document. **Not verified landed as of this ingest** —
  flagged as an open item below.

## Open Items / Gaps (flagged, not resolved by this ingest)

- **Cold-review primary document not located.** See step 3 above. If a standalone cold-review
  report exists elsewhere (a session not yet exported, or a claude.ai-side artifact), it should be
  captured and cross-linked here; until then, "concur, 4→2" rests on the turn-4 packet's own
  attestation, one level removed from the review itself.
- **EM-invariant charter edit not verified landed.** This ingest did not find the sentence-level
  fence ("a session that plans the portfolio does not execute work packets in the same context")
  present in `exchange/coordination-charter-2026-07-21.md` at `origin/main` as read for this pass.
  This is a follow-up item, not something this wiki-master pass is scoped to write into the
  charter itself (charter edits are the coordinator's/PM's lane, not wiki-master's).
- **`jon-turn4-taxonomy-ratified-pm-unblock-2026-07-22.md` and its sibling turn-3 packet are
  untracked** at `origin/main` as of this ingest (present only in the local working tree). This
  page cites them as primary sources under the standing rule that `wiki/intake-triage/` is
  readable-not-writable by wiki-master; their eventual landing on `origin/main` (via whatever PR
  carries the Triage layer's own commits) is outside this pass's scope to force.

## Related

[[coordinator]], [[bgisolation-membrane]]
