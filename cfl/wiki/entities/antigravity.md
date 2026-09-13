---
format: cfl-page/v1
kind: entity
slug: antigravity
title: Antigravity
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: seat
retrieval_key: antigravity sibling trunk coordinator corpus mining
aliases: [Antigravity]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: active sibling trunk/coordinator as of this writing
probe_sealed: "What kind of fleet member is Antigravity, relative to CFL? => A sibling trunk/coordinator in the same federated fleet, with its own project constitution and CARRIER operational envelope, that exchanges teaching/grading correspondence with CFL. TRUSTED"
---

## What it is

Antigravity is a sibling trunk/coordinator in the same federated fleet as CFL, with its own
project constitution, operational envelope ("CARRIER"), and coordinator-state snapshots
(federated index rows include "Antigravity — Project Constitution & Operational Guidelines" and
"CARRIER — Antigravity Operational Envelope & Federated State"). It runs its own corpus-mining
passes (e.g., the Phase B4 candidate-entity/term-diff mining engine referenced elsewhere in this
lane's brief) and exchanges teaching/grading correspondence with CFL (grade letters, corrections,
gate-closure verdicts).

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Antigravity' AND trunk != 'XC-Exchequer';
```
Result: **931** matching rows (federated index, chunk-level). Note: nearly all of these are
naturally attributed to the `Antigravity` trunk itself in `docs_fts.trunk`, since it is that
trunk's own name.

Dream-sweep candidate count: **75 files**. Differs by far more than 20% — flagged, same
unit-mismatch caveat as [[herald]].

## Links

- [[ruling-queue-cfl]] — wiki/tracker/ruling-queue-cfl.md references Antigravity
- [[wayfinder-antigravity-teach-trust-2026-08-30]] — tracker page on Antigravity teach/trust work

## Not recorded here

No characterization of Antigravity's judgment, reliability, or relationship to CFL beyond the
descriptive facts above (which are drawn from titles/index metadata, not adjudicated content). No
family-member names, no financial figures, no predictions about Antigravity's future scope.
