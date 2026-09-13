---
format: cfl-page/v1
kind: entity
slug: professional
title: Professional
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: seat
retrieval_key: professional trunk seat work fbc actuarial
aliases: [Professional]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: active trunk/seat as of this writing
probe_sealed: "What domain does the Professional seat handle, and what routes through it per Jon's PII amendment? => Jon's work-domain content (actuarial AI tooling, FBC at work, M365 strategy); anything genuinely outbound-publishable is meant to route through Professional per the 2026-08-19/20 PII ruling. TRUSTED"
---

## What it is

Professional is one of Jon's four life trunks (Personal/Family, Professional, Home,
Intellectual/Build) and also the name of the corresponding Claude Code / claude.ai seat that
handles Jon's work-domain content — actuarial AI tooling decisions, FBC (frame-before-commit) at
work, and M365 email strategy, per `wiki/agent-guide.md`. Anything genuinely outbound-publishable
is meant to route through Professional per Jon's 2026-08-19/20 PII amendment ("if we make
something cool that needs to be shared, then professionalism will deal with ensuring we have
something that can be externally published"). Professional also acts as an independent
cross-trunk verifier in the corpus (e.g., "Professional independently asked Secretary to falsify
their [claim]").

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH 'Professional' AND trunk != 'XC-Exchequer';
```
Result: **5998** matching rows (federated index, chunk-level). Note: "Professional" is also an
ordinary English adjective, so this count over-counts non-entity usage more than most of the
other candidates on this page's sibling entries.

Dream-sweep candidate count: **392 files**. Differs by far more than 20% — flagged, same
unit-mismatch and word-ambiguity caveats noted above.

## Links

- [[agent-guide]] — names Professional's domain scope (actuarial AI tooling, FBC at work)
- [[actuarial-epistemology]] — Professional-trunk concept content
- [[first-order-and-second-order-repair]] — cross-trunk repair discussion involving Professional

## Not recorded here

No characterization of Jon's employer, compensation, or specific work content. No family-member
names, no financial figures.
