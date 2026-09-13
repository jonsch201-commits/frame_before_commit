---
format: cfl-page/v1
kind: entity
slug: deco
title: TP-Link Deco (mesh network)
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: vendor
retrieval_key: deco tp-link mesh router home network
aliases: [Deco, TP-Link Deco, Deco mesh, Deco router]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: home-infrastructure hardware; model corrected in the record to XE200 (was X60)
probe_sealed: "What device is Deco, and what correction does the home wiki record about it? => A TP-Link Deco mesh Wi-Fi router in Jon's home network; the record corrects the model from X60 to XE200, admin URL 192.168.0.1. TRUSTED"
---

## What it is

Deco is a TP-Link Deco mesh Wi-Fi router/system used in Jon's home network (Trunk 3 / Home
domain), covered by `wiki/home/sources/network-tplink-deco-mesh-expansion-2026-06-13-869da8.md`
and `wiki/home/sources/network-deco-placement-floor-plan-2026-06-28-50749a.md`. The home wiki
records a correction: the model is XE200, not X60 as first recorded, and the admin URL is
`192.168.0.1` (the "Advanced" tab is not present on this unit). Home-security notes track Deco's
port-forwarding configuration status as part of the broader home-network security audit.

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Deco' AND trunk != 'XC-Exchequer';
```
Result: **670** matching rows (federated index, chunk-level).

Dream-sweep candidate count: **39 files**. Differs by far more than 20% — flagged, same
unit-mismatch caveat as [[herald]] (this is nonetheless the smallest of the eleven candidates by
both measures, consistent with it being a narrowly-scoped home-infrastructure term rather than a
seat name repeated across the whole fleet's correspondence).

## Links

- [[network-tplink-deco-mesh-expansion-2026-06-13-869da8]] — mesh expansion diagnostics and upgrade tiers
- [[network-deco-placement-floor-plan-2026-06-28-50749a]] — placement/floor-plan synthesis

## Not recorded here

No current admin credentials, no live IP configuration beyond the corrected admin URL already on
record, no network topology detail beyond what the linked source pages already carry. No
family-member names, no financial figures.
