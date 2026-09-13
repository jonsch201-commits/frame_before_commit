---
format: cfl-page/v1
kind: entity
slug: switchboard
title: Switchboard
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: system
retrieval_key: switchboard launcher relay herald ps1
aliases: [Switchboard, Switchboard.ps1, Switchboard.cmd]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: infrastructure component; live status not re-verified by this lane
probe_sealed: "What 2026-08-17 finding does feedback_guarded-door-is-not-the-front-door.md document about Switchboard? => That the root double-click Switchboard.cmd still started a retired v0 relay while a guard sat four levels down in another seat's tree, and that guard failed open. TRUSTED"
---

## What it is

Switchboard is an infrastructure launcher/relay component (`Switchboard.ps1`, described in the
corpus as "Herald's launcher") used to start or route agent sessions. Jon's own memory record
`feedback_guarded-door-is-not-the-front-door.md` documents a 2026-08-17 finding about it: a fix's
stated cause named a class ("any seat can reach this launcher"), but enumerating the class found
the root double-click `Switchboard.cmd` still starting a retired v0 relay while a guard sat four
levels down in another seat's tree — and that guard failed open. The corpus also references a
"switchboard, built for exactly this" role in coordinator-facing dispatch.

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Switchboard' AND trunk != 'XC-Exchequer';
```
Result: **1860** matching rows (federated index, chunk-level).

Dream-sweep candidate count: **227 files**. Differs by far more than 20% — flagged, same
unit-mismatch caveat as [[herald]].

## Links

- [[DECISIONS]] — wiki/DECISIONS.md references Switchboard
- [[jon-control-surface]] — wiki/references/jon-control-surface.md references Switchboard

## Not recorded here

No current live/armed status for Switchboard — that must be checked against the running
infrastructure, not asserted from this synthesis pass. No family-member names, no financial
figures.
