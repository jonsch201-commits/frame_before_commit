---
format: cfl-page/v1
kind: concept
slug: wiki-t24-diff-ingest-2026-05-09-b60686
date: 2026-09-02
title: "T-24 Diff-as-Ingest (claimed INGESTED 2026-05-13, never actually landed)"
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "T-24 diff as ingest design b60686b6 claimed ingested never landed triage resolution"
aliases: [wiki-t24-diff-ingest-2026-05-09-b60686.md, T-24, diff-as-ingest]
generated_by: lane S-4 (sonnet) session e515d858
state: superseded
state_note: "duplicate of wiki-master-cc-t24-diff-ingest-2026-05-09-b60686 from a parallel fork 2026-09-02; kept, not deleted"
probe_sealed: "Does wiki/sources/wiki-t24-diff-ingest-2026-05-09-b60686.md, or its content under another name, exist anywhere in this clone's git history? => No file at this path was found by search; wiki/tracker/triage.md's own 2026-05-13 resolution entry is the only record of it, and it records a claim of ingestion rather than the ingested content itself. TRUSTED"
superseded_by: wiki-master-cc-t24-diff-ingest-2026-05-09-b60686
---

## Definition

[verbatim, cropped] `wiki/tracker/triage.md`'s 2026-05-13 resolution entry states, for conversation
`b60686b6`: "→ **INGESTED** as `wiki/sources/wiki-t24-diff-ingest-2026-05-09-b60686.md` (T-24
diff-as-ingest design)." [paraphrase] The entry sits alongside a matching claim for a sibling
conversation (`b04c8b74` → `wiki/sources/forward-pass-mechanics-2026-05-07-b04c8b.md`), which this
audit's own table (row 61) separately confirms DID land, under a slightly different real path
(`wiki/sources/fbc/fbc-forward-pass-mechanics-2026-05-07-b04c8b.md`) — i.e. the sibling claim was
approximately true (content real, path drifted), while this row's claim (T-24, "diff-as-ingest
design") has no matching content anywhere in this clone under any name. The underlying subject,
T-24, is a design for treating a diff against prior wiki content as itself a form of ingest.

## Origin

- `wiki/tracker/triage.md:59` — the sole CFL-wiki citer, in the T-003/T-24 export-recovery
  resolution block.

## Evidence

- [[wiki-ingest-methodology]] (`wiki/concepts/wiki-ingest-methodology.md`) — the CFL page most
  directly on point for ingest methodology generally; it does not describe a diff-as-ingest design
  specifically, so it should not be read as having absorbed T-24's content.
- [[hypothesis-loop]] — the standing research-loop page; a "diff-as-ingest design" would, if it
  existed, likely interact with this loop's validation/measurement steps, but no such interaction
  is documented anywhere reachable from this clone.

## Not established

The actual T-24 "diff-as-ingest design" content — what it proposed, whether it was ever
implemented, and why the 2026-05-13 triage resolution claimed ingestion when no such file exists —
is not established by any primary reachable from this clone. This page documents the false-positive
claim itself (a `derive-dont-record`-shaped instance: a triage tracker recorded "INGESTED" once and
nothing since re-checked it against the actual `wiki/sources/` tree); it does not reconstruct the
design T-24 was supposed to describe.
