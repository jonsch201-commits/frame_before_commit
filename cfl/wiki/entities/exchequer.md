---
format: cfl-page/v1
kind: entity
slug: exchequer
title: Exchequer
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: seat
retrieval_key: exchequer xc financial estate personal role seat
aliases: [Exchequer, XC, XC-Exchequer]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: active personal-domain seat/trunk; its own path tree was explicitly excluded from this lane's reads
probe_sealed: "What domain does the Exchequer seat handle, and why does this page carry no financial detail? => Financial and estate-management matters for one of Jon's four personal-domain seats; this lane's instructions forbade opening any XC-Exchequer path, so the page is written entirely from external mentions. TRUSTED"
---

## What it is

Exchequer (also abbreviated XC, or referenced as the trunk XC-Exchequer) is one of Jon's four
personal-domain role seats, alongside Herald, Soul, and Guide-of-Home-and-Family, handling
financial and estate-management matters — per `wiki/agent-guide.md`, Herald "defers to Soul /
Guide-of-Home-and-Family / Exchequer" for that domain. The corpus describes it as air-gapped from
other trunks with respect to financial reference data, and its session content is treated with
extra handling care in cross-trunk pipelines (explicitly excluded from certain automated drains
"the money" per its own operational envelope).

**This lane's own instructions forbade opening any XC-Exchequer path**, so this page is written
entirely from mentions of Exchequer found in non-XC-Exchequer trunk content (home-wiki decision
pages, `wiki/agent-guide.md`, `wiki/index.md`). No financial figures, account identifiers, or
XC-Exchequer-internal content appear on this page or were read to write it.

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Exchequer' AND trunk != 'XC-Exchequer';
```
Result: **2862** matching rows (federated index, chunk-level; the query itself excludes the
XC-Exchequer trunk per this lane's rules).

Dream-sweep candidate count: **165 files**. Differs by far more than 20% — flagged, same
unit-mismatch caveat as [[herald]].

## Links

- [[agent-guide]] — names Exchequer among the personal-domain roles Herald defers to
- [[sewer-lateral-repair-decision-2026-07-09-9e5323]] — home-trunk decision page referencing Exchequer

## Not recorded here

No financial figures, account identifiers, balances, or any XC-Exchequer-internal content — this
lane's rules forbid opening XC-Exchequer paths, and this page was written without doing so. No
family-member names. No characterization of Jon's specific financial situation.
