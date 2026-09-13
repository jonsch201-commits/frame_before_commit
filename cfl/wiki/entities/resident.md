---
format: cfl-page/v1
kind: entity
slug: resident
title: Resident
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: system
retrieval_key: resident term for the ai instance in a project scope
aliases: [Resident, the resident]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: generic term, not a single named seat
probe_sealed: "What does the term 'the resident' refer to in this corpus? => The generic term for the Claude Code / claude.ai agent instance occupying a given project/trunk, distinct from any one named seat, grounding Jon's over-scrubbing-is-a-violation PII rule. TRUSTED"
---

## What it is

"The resident" is the corpus's generic term for the Claude Code / claude.ai agent instance
occupying a given project/trunk — distinct from any one named seat (Herald, Soul, Secretary,
etc.). It appears in Jon's own PII ruling: *"It's fine in any file the resident can read"*
(2026-08-11, quoted verbatim in Jon's global CLAUDE.md), which grounds the over-scrubbing-is-a-
violation rule — a redactor that reduces what the resident can read breaks a standing instruction
just as surely as a leak does. It also appears in continuity-contract and consciousness-framework
discussions as the entity whose registration/dispatch/measurement is being governed.

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Resident' AND trunk != 'XC-Exchequer';
```
Result: **4098** matching rows (federated index, chunk-level). Note: "resident" is also an
ordinary English word (e.g. "resident of," "non-resident"), so this count includes non-entity
usage.

Dream-sweep candidate count: **269 files**. Differs by far more than 20% — flagged, same
unit-mismatch and word-ambiguity caveats as [[professional]].

## Links

- [[fable-mirror]] — discusses the resident's read access relative to fable-mirror
- [[orders-and-oaths]] — discusses "the resident (and any agent here)" proposing actions
- [[graphrag-retrieval]] — discusses resident measurement/verification

## Not recorded here

No claim that "resident" names one specific seat — it is a role-neutral term. No
characterization of any individual resident's judgment. No family-member names, no financial
figures.
