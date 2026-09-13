---
format: cfl-page/v1
kind: entity
slug: soul
title: Soul
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: seat
retrieval_key: soul personal faith morality role seat claude personal
aliases: [Soul]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: active personal-domain seat as of this writing
probe_sealed: "What does the Soul seat engage, and what architecture is credited to its 2026-08-22 letter? => Jon's faith, morality, and moral-development questions via the gift-exile-reunion framework; the de-PII lexicon architecture in scripts/audit/depii_lexicon.py is credited to Soul's letter. TRUSTED"
---

## What it is

Soul is one of Jon's four personal-domain role seats — the Claude Code / claude.ai identity
(hosted in the Claude Personal trunk) engaging Jon's faith, morality, and moral-development
questions, using the gift-exile-reunion framework. Soul also functions as a peer correspondent in
CFL's cross-trunk exchange (e.g., the de-PII lexicon architecture cited in
`scripts/audit/depii_lexicon.py` is credited to Soul's 2026-08-22 letter, measured on CFL's own
corpus), and is named repeatedly across the corpus as an independent verifier of other trunks'
claims.

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Soul' AND trunk != 'XC-Exchequer';
```
Result: **6463** matching rows (federated index, chunk-level).

Dream-sweep candidate count: **508 files**. Differs by far more than 20% — flagged, same
unit-mismatch caveat as [[herald]] (file count vs. federated chunk count; "Soul" is also a common
English word, so this count is not purely entity-referential and is likely inflated further by
that ambiguity — a caveat the numeric-heavy candidates like [[herald]] and [[secretary]] mostly
avoid).

## Links

- [[de-pii-deriver]] — credits Soul's architecture and measurements for the de-PII lexicon
- [[four-things-the-fleet-is-missing]] — discusses Soul among fleet roles
- [[first-order-and-second-order-repair]] — cross-trunk repair discussion involving Soul

## Not recorded here

No theological or moral positions attributed to Soul as if they were Jon's own. No
characterization of Soul's relationship to Jon beyond the descriptive role facts above. No
family-member names, no financial figures.
