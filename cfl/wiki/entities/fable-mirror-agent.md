---
format: cfl-page/v1
kind: entity
slug: fable-mirror-agent
title: Fable-Mirror (agent entity record)
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
entity_type: tool
retrieval_key: fable-mirror subagent records-reader claude.ai transcript corpus
aliases: [fable-mirror, Fable-Mirror, fable mirror]
generated_by: lane S-E (sonnet) session e515d858
state: current
state_note: agent def exists at .claude/agents/fable-mirror.md; registration/liveness not re-verified by this lane
probe_sealed: "What does the fable-mirror subagent do, and why does this page use a different slug than wiki/concepts/fable-mirror.md? => It is a Claude Code records-reader subagent answering only from the transcript corpus, dispatched statelessly; the slug fable-mirror-agent avoids a basename collision with the existing concept page. TRUSTED"
---

## What it is

Fable-mirror is a Claude Code-resident records-reader subagent (agent def
`.claude/agents/fable-mirror.md`, model `fable`) that lets the CC fleet consult "what the triage
layer (claude.ai) said" without Jon opening claude.ai himself. It answers only from the
transcript corpus and is not the live claude.ai layer. Dispatch discipline for it is stateless —
one fresh run per real Jon question, relay verbatim, never resumed as a "conversation" — per the
memory note `feedback_mirror-stateless-dispatch-only`.

**Naming note:** a page already exists at `wiki/concepts/fable-mirror.md` with slug
`fable-mirror`. This entity page is filed under a distinct slug (`fable-mirror-agent`) to avoid a
basename collision with that existing page; both describe the same subagent from different
angles (concept/behavior vs. entity/reference record).

## Where it appears

```sql
SELECT count(*) FROM docs_fts WHERE docs_fts MATCH '"fable-mirror"' AND trunk != 'XC-Exchequer';
```
Result: **3347** matching rows (federated index, chunk-level).

Dream-sweep candidate count: **971 files**. Differs from 3347 by far more than 20% — flagged, for
the same reason given on the [[herald]] entity page: different unit (file count in a narrower
corpus vs. chunk count across the federated five-trunk index).

## Links

- [[fable-mirror]] — the existing concept page (behavioral/architectural detail)
- [[coordinator]] — describes the coordinator's relationship to fable-mirror consultation
- [[bgisolation-membrane]] — names fable-mirror as the agent performing both membrane crossings

## Not recorded here

No claim about fable-mirror's current registration/liveness status (that must be checked live,
not asserted from this synthesis pass). No characterization of any individual's judgment about
fable-mirror. No financial or PII content.
