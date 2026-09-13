---
title: "Jon Dispatch Addendum — Turn 9b: Memory-in-Zips Test Required, Memory-Capture Gap (2026-07-26)"
aliases: [memory-in-zips-test-2026-07-26, memory-snapshot-capture-procedure-2026-07-26]
trunk: fl
branch: [cfl]
sub_branch: [corpus]
branch_reason: "R-SRC-INFRA; sub: corpus 4 vs wiki 3 on authored labels"
source_kind: session
retrieval_key: jon-turn9b-memory-in-zips-test-2026-07-26
generated_by: wayfinder (claude.ai FL wayfinder), Jon-transmitted
origin: wiki/intake-triage/jon-turn9b-memory-in-zips-test-2026-07-26.md
audit_state: unaudited
status: ACTIVE — amends [[jon-turn9-growth-intent-commented-fold-and-revise-2026-07-26]] §5 standing items. Ten days unrouted before this ingest (deposited 2026-07-26, ingested 2026-08-05).
maintained_by: coordinator (deposit); wiki-master ingests
tags: [jon-ruling, memory-capture, standard-update, export-zip-test, mem-provenance]
---

# Ingest note (wiki-master, SU-close step 4, 2026-08-05)

Ingested verbatim from `wiki/intake-triage/jon-turn9b-memory-in-zips-test-2026-07-26.md`, content
unchanged below. **Jon's direct quote is preserved exactly:** *"require this be tested upon next standard
update."* That is a ruling in the imperative and is carried as such.

**Known non-conformance, flagged not silently fixed:** original file has no `retrieval_key`/`aliases`
block — added at ingest. **This ingest does not perform the required test.** The file itself specifies
the test ("search exhaustively for claude.ai memory content… report with QUOTES") and the wayfinder's own
pre-registered expectation (ABSENT) — this ingest pass carries that expectation as reported, not as
verified, and does not attempt to run the test against a current export zip. Whether the test has been
run on any Standard Update since 2026-07-26 is UNRESOLVED and not addressed by this wiki page; it is a
live operational question for the coordinator, separate from this ingest's job of getting the ruling on
record.

---

# Turn-9b — memory-in-zips test (Jon-required) + memory/project-knowledge capture gap

## Required test, next Standard Update (Jon: "require this be tested upon next standard update")

Against the NEWEST export zip on the machine: search exhaustively for claude.ai memory content — any per-project memory summaries, global memory profile, userMemories-like structures, or memory JSON alongside conversations.json/users.json/projects. Report with QUOTES: if memory content is found, quote a fragment proving presence and record where it lives; if absent, state "no memory structures present in export" as a tested claim, not an assumption.

Expected result (wayfinder pre-registered, from docs review 2026-07-26): ABSENT. Anthropic help center describes exports as conversation data + user data; multiple independent guides state memory is not exportable as a file and Projects are likewise excluded. Gemini's claim that memory "should be" included is contradicted by available documentation. But the zip is ground truth — test it.

## If absent (expected): standing capture procedure

Claude.ai memory summaries and project knowledge/instructions are then UNCAPTURED CORPUS SOURCES — model-authored profiles of Jon and project state that exist nowhere in raw/. Procedure:
1. Jon manually copies, on a cadence he sets (proposal: monthly, or before any major project change): the global memory profile + each project's memory summary (Settings → memory panel, per scope) + each project's instructions/knowledge file list.
2. These land in the standardized export landing folder (pending Jon's answer on location) and ingest as source_kind: memory-snapshot, provenance [MEM] — model-authored ABOUT Jon, never Jon-verbatim, never categorical-floor. They are evidence of what the system believed, not of what Jon said.
3. SU recency check extends to memory-snapshot age: if newest snapshot > 60 days, flag "memory capture requested from Jon" as a named line.

Rationale: the wayfinder's own project memory is substantial and load-bearing for session continuity; if the platform changed or an account issue occurred, it would be lost with no corpus trace. Same class as the export-ingestion defect — a silently uncaptured layer — caught before it cost.

Silence is never approval. — Jon
