---
slug: wikiskill-adoption
title: "WikiSkill (Google Research) — what CFL adopted, what it already had, what it declined"
date: 2026-09-01
status: LIVE
written_by: CFL coordinator, on Jon's live instruction ("you did not sufficiently groun into the wiki the wikiskill paper and our plan with it. Soul got confused. That's a clear wiki issue to solve", 2026-09-01 mid-turn, typos his)
---

# WikiSkill adoption — the one page a fresh reader (or a confused trunk) needs

## What the paper is

**"WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution"**,
Google Research, **arXiv 2608.27454** — verified at source by CFL's paper lane 2026-08-31
(the lane got the right id and read the mechanism; the summary Jon originally pasted was
AI-generated and self-flagged fallible). Primary: `raw/` window
`raw/transcripts/claude-code/fl/code-2026-09-01-9041f3-window-132247.md` carries the
adoption arc verbatim.

Three-layer loop: **Raw** (immutable execution traces) → **Wiki** (curated patterns, a
Wiki Maintainer agent) → **Skills** (a Skill Proposer emits diff-shaped proposals; a
**validation gate** accepts only strict improvement on held-out validation vs best-so-far,
with full revert and an append-only **skill-impact ledger** that later proposers must read
— their ablation: the loop collapses without the ledger).

## The measured figures, with their models named (Secretary's 09-01 correction folded in)

- Removing wiki access from the **Skill Proposer**: **−15.0 points** (63.7 → 48.7).
- Giving whole-wiki access to the **Inference Agent** during rollouts: **−2.8** (63.7 →
  60.9) — a claim about trajectories becoming *less informative for skill development*
  (training signal), NOT a plain task-performance claim. Ablation model:
  **Gemini-3.5-Flash**; the 68.1% headline elsewhere in the paper is 1.5-Flash.
- **Cross-tier transfer measured NEGATIVE**: a 4B-derived skill dropped a stronger model
  **50.5 → 18.1**. This is the empirical basis for per-tier skill variants (Jon's
  "customization" half).

## The mapping — what CFL already had (this is where Soul got confused: same mechanisms, different names)

| WikiSkill term | CFL's existing thing | where |
|---|---|---|
| Raw layer | record pipeline: verbatim windows minted ONLY by `scripts/audit/mint_window.py`, byte-verified, no-deletion | `raw/transcripts/claude-code/fl/`, `exchange/su-close/` |
| Wiki layer (incl. kept failures) | `wiki/` — struck-never-deleted arcs ARE the compounding-experience mechanism | this tree |
| skill-impact ledger | **`wiki/skills-gate/LEDGER.md`** (append-only, both branches exercised, rejected rows = feedstock) | with `GATE-SPEC.md` |
| validation gate | **the skills gate**: atomic diff-shaped PURPOSE-mapped probe-attached tier-stated proposals; strict-improvement-or-full-revert; checked by `scripts/audit/skills_gate_check.py` (G1–G5, selftest proves all five failable) | `wiki/skills-gate/` |
| held-out validation | E4 cold-reader probes with **hash-sealed keys** (sha256 committed BEFORE dispatch, key body off-repo) — run 3 scored 6/6 on 2026-09-01 | RP-8 rows on the live map; `wiki/intake-triage/e4-purpose-probe-run3-2026-09-01.md` |
| Skill Proposer | **all trunks** — Jon's shape verbatim: "All trunks are proposors to CFL Gate" | gate spec |

**Gate rows so far:** PROP-000 (fixture, RETURNED-UNREAD — proves the refusal branch) ·
PROP-001 (Soul's silence-conflation finding → CREATED `skills/exchange-letters/SKILL.md`) ·
PROP-002 (Jon's silence-is-never-approval ruling → rule 8 + `lint_silence_clause.py`) ·
PROP-003 (Herald F-7 → rule 9 + `scripts/audit/on_silence_report.py`).

## Jon's ruling — the gate is PR-3 content

Verbatim, typos his, 2026-08-31 ~23:3x (primary in window-132247): **"I trust you. I need a
prototype thid at least as part of PR 3."** The prototype exists and is tested; PR-3 ships it.

## The honest gap (what CFL did NOT have, and the plan for it)

The gate validates against **reading probes of the record**, not **behavior**. The paper's
gate scores held-out task performance. The closing design is Jon-authorized since 2026-08-01:
`wiki/intake-triage/corpus-lesson-calibration-testing-packet-2026-08-01.md` — **T4**, the
pre-merge behavioral lint (resample historical branch points with/without a draft text,
measure the shift). Ticketed **RP-23** on
`wiki/tracker/wayfinder-pr3-record-pipeline-2026-08-31.md` 2026-09-01: T4 is chartered as
gate v2 acceptance; T1 executable now; T3 sequencing stays Jon-gated per the packet's own
list.

## Declined / fenced (so nobody re-imports them)

- **Whole-wiki context injection into inference** — the paper measures it negative for the
  loop; CFL's reader road (GraphRAG + typed edges, RP-4) is the substitute.
- **One skill text for all tiers** — cross-tier transfer is measured negative; every LEDGER
  row states its validated tier, and standardization for co-trunks emits tier variants.
- **Automated pruning** — the paper names it future work; CFL's no-deletion rule makes
  pruning impossible by design. Professional's 09-01 formulation is the operating answer:
  **under no-deletion, METADATA is the pruning mechanism** (retrieval, not removal).

## Related

[[skills-gate]] (spec+ledger) · RP-20/RP-8/RP-23 on the live PR-3 record-pipeline map ·
`wiki/intake-triage/dream-rsi-shape-and-pr3-gaps-2026-09-01.md` (the RSI framing) ·
Herald F-7 ("every field ships with its reader" — adopted as PR-3 design principle).
