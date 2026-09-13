---
title: "Supersession — Old Rules Outranking Their Amendments"
aliases: ["supersession", "supersedes edges", "old rules outranking amendments", "version confusion", "version-confusion defect", "P16", "the PII ranking regression"]
kind: concept
trunk: fl
branch: [cfl]
sub_branch: [retrieval]
branch_reason: "R-CONCEPTS; promoted 2026-08-23 from 16 days of frozen tracker material per Jon's 'forcing a wiki update' directive"
type: concept
first_seen: wiki/tracker/PROBE-REGISTRY.md P4/P16
source_count: 2
last_updated: 2026-08-23
maintained_by: wiki-master (proposal, this promotion pass — unratified)
---

# Supersession — the live, unfixed defect

**The failure mode:** a retrieval index has no innate notion that a later ruling replaces an
earlier one on the same question. Left alone, an older, more heavily-cited or more verbose chunk
can outrank the amendment that governs it — a retriever that is *confidently wrong in the
authoritative direction*.

## Status as of 2026-08-23: LIVE AND UNFIXED, and it governs the PII rule specifically

Probe P4/P16 in [[probe-registry]] tests exactly this: the query `no writing PII to github` must
surface the 2026-08-19 AMENDED block (CFL-D-009, the reachability qualifier) above the older
2026-08-09 wording (CFL-D-003) it amends.

- **Run 1:** TRUSTED but degraded — amendment at rank 6, three 08-09-only chunks at ranks 3–5
  *above* it.
- **Run 2:** RECOVERED via an `ARCHIVE_PENALTY` heuristic (L1).
- **Run 3 / Run 5 (full-corpus rebuild):** **REGRESSED AGAIN** — the 08-09-only wording leads by
  2.2%–2.55%, depending on the rebuild.

## The structural fix that was built, and why it does not close this case

P2-3 (2026-08-23) added typed `kind='supersedes'` edges from frontmatter and made `retrieve.py`
demote a superseded destination's score by 0.6. **This works** — proven on the real
source-page-standard v4→v3→v2→v1 lineage: the superseded v1 fell from rank 1 to rank 3 and v2/v3
left the top 8 (`wiki/tracker/wayfinder-pr2-2026-08-23.md:267-273`).

**But it cannot touch the PII case**, verified by the coordinator's own retrieval run:
`CLAUDE.md:248-261` (the superseded 08-09 wording) scores **0.02333**, beating its own amendment at
`:266-287` — **0.02275**, by 2.5% the wrong way. The two chunks live in the **same file**, and
supersession edges in this system are **file→file**. A file cannot demote a passage against
itself. The 1.2% margin the registry itself had already flagged as fragile simply flipped
direction on a full rebuild.

Two other defects were caught building the fix:

- **The parser hazard:** the first edge-extraction pass produced 30 "edges," 17 of them prose —
  targets like `the`, `any`, `two`, `CFL`, `374127` — each headed for a basename-stem lookup that
  could have silently demoted an unrelated file by name collision. A guard and 8 parser test cases
  were added to `--selftest`.
- **Scope creep, caught and split out rather than bundled:** P2-3 as originally scoped conflated
  three different defects. P15 (an unsourced verbatim quote outranking its cited primary inside an
  instrument's own test fixture) is **provenance, not supersession** — it needs a fixture
  classifier and is now PR-3 scope, explicitly **not to be promised in PR-2**. And rolling
  `maintained_by:` frontmatter onto 25 tracker files (M-22) was found to add a field "written by
  six scripts and read by none" — not itself the supersession fix.

## Why this matters beyond one probe

This is the general form of a hazard named in `wiki/DECISIONS.md`'s own era note: *"the OLDEST
decisions are frequently the MOST binding... naive recency inverts authority."* A retrieval system
built to surface "the latest thing" is exactly wrong when the latest thing is a provisional
resolution and the oldest thing is a still-binding constitution. The `supersedes` edge type is the
first mechanical attempt to encode *which* direction of recency actually governs — an author's
explicit frontmatter declaration, not a regex guessing from prose that merely discusses
supersession (the old L2 heuristic's failure: it fired on any page that *discussed* the topic and
stayed silent on pages that never announce their own obsolescence).

## PR-2 constraint

Per `exchange/COMPACT-HANDOFF-2026-08-23-1520.md:47-48`: **PR-2 must not claim this is fixed.**
Promise 7 of PR-1's retrospective was downgraded to PARTIAL specifically because of this
regression (see [[disposition-and-delivered-is-not-received]] for the retrospective's full score
history).

## See also

- [[probe-registry]] — P3, P4, P16, P17 are the probes tracking this defect by id.
- [[graphrag-retrieval]] — the ranker this defect lives inside.
- [[disposition-and-delivered-is-not-received]] — the retrospective-score pattern this regression
  is one instance of (a promise graded VERIFIED, later found PARTIAL on closer measurement).
