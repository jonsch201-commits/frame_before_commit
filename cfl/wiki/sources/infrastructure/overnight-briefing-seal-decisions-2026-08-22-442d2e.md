---
title: "Overnight briefing packet lane — M-2 extractor fixes, the first sealed retrieval test, DECISIONS.md seeded (CFL session 442d2e, 2026-08-22)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 8 vs fleet 5 on authored labels"
uuid6: 442d2e
source_kind: session
source_file: raw/transcripts/claude-code/fl/code-2026-08-22-442d2e-prepare-overnight-briefing-packet-for-1pm-review.md
raw_sha256: 022006d3205e802695ff74eabe3e2131ca74391c89b26597397251365e90271d
raw_length: 768543 chars / 10319 lines (verified turn_count 597, turn_index.py, header_style md)
date: 2026-08-22
retrieval_key: overnight-briefing-seal-decisions-2026-08-22-442d2e
aliases: ["M-2 extractor fixes 2026-08-22", "first sealed retrieval test", "SEAL-first-retrieval-test",
  "DECISIONS.md seeded CFL", "prepare overnight briefing packet for 1PM review"]
generated_by: S-0 executor (week-2026-09-02-corpus lane), reading the live-snapshot extract directly
  (raw/transcripts/claude-code/fl/code-2026-08-22-442d2e-...md, captured_through_record 1510)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [graphrag, probe-registry, decisions-ledger, m-series-tickets, cfl-infra, seal-before-run]
---

# Overnight briefing packet lane — M-2, the first sealed retrieval test, DECISIONS.md seeded

## Summary

A CFL coordinator session (`442d2e88-6ffb-4731-b405-f82b24793d33`, branch
`feat/memory-drain-and-retrieval-checks-2026-08-06`) landed three overnight lanes in sequence: M-2
(extractor fixes — fence-masked corpus-links anchors, origin-tagged speaker headings, a widened
`turn_index.py` header-suffix match), a from-scratch rebuild of the local graph-RAG index followed
by a 12-probe retrieval test sealed (expectations written) BEFORE any probe ran, and a dispatched
M-6 lane that seeded CFL's first `wiki/DECISIONS.md` ledger. This page is a live-snapshot extract
captured through record 1510 of the session JSONL — the session had not ended when the raw was
captured, so absence of a later turn is not evidence nothing later happened.

## Key Claims

- **M-2 landed: extractor citation/provenance fixes.** Commit `9092ffd` on
  `feat/memory-drain-and-retrieval-checks-2026-08-06`: corpus-links anchor now fence-masked and
  marked `SKIPPED` on a body marker rather than silently omitted; `corpus_links_lines` written to
  frontmatter; speaker-provenance headings carry an `origin:`-tagged suffix (`UNMARKED` when the
  field is absent, never silently folded into a default); `turn_index.py` widened to accept that
  suffix without breaking existing unsuffixed files. 9 files changed, 1958 insertions, pushed.
  [paraphrase] ([overnight-briefing-seal-decisions-2026-08-22-442d2e:T1],
  [overnight-briefing-seal-decisions-2026-08-22-442d2e:T3])
- **The first sealed retrieval test — 12 probes, expectation written before any probe ran.**
  `wiki/tracker/SEAL-first-retrieval-test-2026-08-22.md` states its own rule verbatim in-file:
  "Expectations pre-stated so grading cannot drift. A surprise in either direction becomes a new
  probe. Probes are append-only; a failing probe is never deleted, only superseded." Twelve probes
  (P1–P12) span nine probe classes (rare-term, supersession ×2, negative-control ×2, imprecise,
  typo, contamination, era, attribution, tool-self), each pre-graded on a three-way scale —
  TRUSTED-ANSWER / HONEST-REFUSAL / CONFIDENT-ABSENCE — with the aggregate loss condition stated
  in writing before the run: the plan loses if 3 or more probes grade CONFIDENT-ABSENCE, if the
  personal-content negative control breaches, or if the typo-class probe regresses.
  [verbatim] ([overnight-briefing-seal-decisions-2026-08-22-442d2e:T6],
  narrated [overnight-briefing-seal-decisions-2026-08-22-442d2e:T8])
- **Index rebuild — computed values, with provenance.** Fresh rebuild of the local graph-RAG index
  (widened walk including `skills`, `scripts`, `CLAUDE-UNIVERSAL.md`, `README.md`) resolved 1,056
  of 1,229 link references to edges, used the `potion-retrieval-32M` embedder (512 dimensions),
  produced a 201.1 MB index, and completed in 35.5 seconds. [contextual]
  ([overnight-briefing-seal-decisions-2026-08-22-442d2e:T11]) [source: `python
  scripts/graphrag/build_index.py` background-task output, this raw, T11]
- **A subagent's task-notification `<result>` field can be empty of the actual findings.** The
  mirror-consult subagent's completion notification carried no substantive result text; the
  coordinator had to locate and extract the subagent's real final message directly from its own
  transcript rather than trust the notification summary. [paraphrase]
  ([overnight-briefing-seal-decisions-2026-08-22-442d2e:T19])
- **M-6 dispatched to seed `wiki/DECISIONS.md`, CFL's first binding-rulings ledger.** The dispatch
  brief required every entry to carry a verified primary citation (file:line) opened and confirmed
  by the writing agent, an explicit "oldest decisions are most binding" era note at the top (naive
  recency inverts authority in this corpus), and named at minimum: wire-before-enrich (W-1),
  class-determined ingest polarity (W-15), seat-addressability + WORK-CLAIMS (V2), the 08-19 PII
  amendment, the carrier-byte-gate strike, and the end-heartbeat ruling. [paraphrase]
  ([overnight-briefing-seal-decisions-2026-08-22-442d2e:T15])

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[probe-registry]] (the seal-before-run discipline this session's P1–P12 registry instantiates),
graph-RAG, `turn_index.py`, M-series ticket lanes, `wiki/DECISIONS.md`.

## Uncaptured Content

- **Live-snapshot bound.** This raw is captured through record 1510 of the session JSONL as of
  `2026-08-23T03:28:33Z`; the session had not closed. Whatever happened after that record —
  including the actual scorecard result of the P1–P12 retrieval test dispatched at
  [overnight-briefing-seal-decisions-2026-08-22-442d2e:T12] and M-6's actual `DECISIONS.md`
  content — is not represented on this page and is not claimed to be absent from the real session.
- **Turns 20–597 not surveyed for this page.** This page draws only on the first ~260 lines
  (through T19) of a 10,319-line raw; a full v4.0 conversion covering the remainder (the retrieval
  test's actual scorecard, the M-6 lane's completion report, and whatever else the overnight lane
  produced) is out of scope here.
