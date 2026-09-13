---
format: cfl-page/v1
kind: entity
slug: duncan
title: Duncan (consent-file protocol concept)
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: system
retrieval_key: duncan idaho consent file protocol metaphor identity coercion
aliases: [Duncan, Duncan Idaho, Duncan consent file, Duncan Idaho constraint]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: metaphor-named protocol concept, not a person; checked against the record per this lane's negative-control instruction
probe_sealed: "Is Duncan, as used in this corpus, a real person? => No — it is a protocol/consent-record concept used two non-personal ways: a Duncan Idaho (Dune) failure-mode metaphor, and the named 'Duncan consent file' artifact; no occurrence names a real individual. TRUSTED"
---

## What it is

"Duncan" in this corpus is a protocol/consent-record concept, not a person. **Checked against the
record**, per this lane's instruction: the federated index shows the term used two ways, both
non-personal —

1. **"Duncan Idaho [failure mode/constraint]"** — a metaphor drawn from the Duncan Idaho
   character in Frank Herbert's *Dune* (a repeatedly-recreated identity/ghola), used in
   Antigravity-trunk protocol discussion to name a failure mode of "unearned identity coercion"
   and a design constraint ("prioritizing verifiable records over assumed identities").
2. **"Duncan consent file"** — a named artifact/mechanism: a consent record described as living
   "OUTSIDE the container, mirrored read-only inside," with named writers, referenced in a launch
   manifest/spec context (`wiki/intake-triage/agent-end/643640/code-2026-08-08-a267e8-explore-find-duncan-consent-file.i1.md`).
   A related CFL memory note records that a "Duncan consent file" primary was found sitting in a
   live Personal-trunk session JSONL after a search had concluded "no primary exists" — the point
   of that note is about search-completeness across sibling trunks, not about any person.

No occurrence found in this lane's bounded reads uses "Duncan" as a family member's or any real
individual's given name.

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Duncan' AND trunk != 'XC-Exchequer';
```
Result: **543** matching rows (federated index, chunk-level).

The dream-sweep candidate list gave **35 files**. Differs by far more than 20% — flagged, same
unit-mismatch caveat as [[herald]].

## Links

- [[CENSUS-resident-artifacts-21-addressed-2026-08-24]] — census page referencing Duncan
- [[INBOX-DRAIN-disposition-2026-08-24]] — references `DUNCAN-CONSENT.md` as the primary record for a re-instantiation ruling

Also cited by path (not wikilinked — this file lives under `agent-end/`, a raw subagent-transcript
archive, not a page this wiki treats as link-target-eligible):
`wiki/intake-triage/agent-end/643640/code-2026-08-08-a267e8-explore-find-duncan-consent-file.i1.md`

## Not recorded here

No claim that "Duncan" names any real person, including any family member. No family-member
names generally, no financial figures, no PII.
