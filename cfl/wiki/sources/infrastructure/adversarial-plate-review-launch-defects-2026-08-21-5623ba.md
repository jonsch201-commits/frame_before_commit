---
title: "Adversarial peer review of Jon's plate and the CFL launch procedure — headless CFL seat, 2026-08-21 (5623ba)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 9 vs fleet 5 on authored labels"
uuid6: 5623ba
source_kind: session
source_file: raw/transcripts/claude-code/fl/code-2026-08-21-5623ba-you-are-a-fresh-cfl-trunk-seat-performing-an-adver.md
raw_sha256: b94f3f42733ada0444ca04dc4d716b985464ca0726c8d758517dc3420b575fb9
raw_length: 109499 chars / 1873 lines (verified turn_count 58, turn_index.py, header_style md)
date: 2026-08-21
retrieval_key: adversarial-plate-review-launch-defects-2026-08-21-5623ba
aliases: ["adversarial peer review Jon's plate 2026-08-21", "launch-cfl.bat wake-skill missing",
  "CFL launcher adversarial review 5623ba", "graph-RAG one-trunk-wide finding"]
generated_by: S-0 executor (week-2026-09-02-corpus lane), reading the headless-seat extract directly
  (raw/transcripts/claude-code/fl/code-2026-08-21-5623ba-...md, 0 compaction boundaries, FULL visible
  extraction)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [adversarial-review, launch-procedure, graphrag, headless-seat, cfl-infra, wake-skill]
---

# Adversarial peer review of Jon's plate and the CFL launch procedure — headless seat, 2026-08-21

## Summary

A write-denied (headless), fresh CFL-trunk seat was dispatched to adversarially review two things
ahead of a fresh Fable coordinator's launch: what genuinely sits on Jon's plate (as framed by a
sibling trunk's index) and whether the documented CFL launch procedure actually works. The seat
first re-read a nested tool-result payload (the sibling trunk's own decision-queue index) that had
itself corrected two earlier mis-framings, then produced nine numbered, severity-tagged findings of
its own — the most severe being that following either documented launch path (the sibling's or
CFL's own) fails a fresh Fable at its first typed command. The session made no commits (write-denied
by design); its entire deliverable is the closing findings list.

## Key Claims

- **BLOCKS-LAUNCH — the documented launch procedure fails at step two, in both documents under
  review.** The sibling trunk's teaching package names only its own launcher
  (`Personal Coordinator Soul.cmd`) with no CFL launch step anywhere in the package; CFL's own real
  door, `launch-cfl.bat`, instructs the operator to type `/wake` next, but CFL's `skills/` directory
  contained no wake skill at all, and the one `/wake` skill that did exist was guarded
  `[CLAUDE PERSONAL ONLY]` and refused to run in the CFL repo. [verbatim]
  ([adversarial-plate-review-launch-defects-2026-08-21-5623ba:T58])
- **The vector-embedded graph-RAG index existed and worked, but was one trunk wide.** Measured:
  16,132 chunks across 819 files, 1,307 edges, real embedder (`potion-retrieval-32M`, 512
  dimensions), built in 68.8 seconds; 817 of the 819 indexed files were CFL's own `wiki/` — zero
  files from five other trunks, zero raw transcripts/conversations. A live probe for a specific
  Jon ruling on "heartbeats" returned nothing relevant in hybrid, dense, lexical, or graph mode
  because the token appeared in zero indexed files, the ruling living instead in an unindexed
  sibling trunk's own files. [contextual]
  ([adversarial-plate-review-launch-defects-2026-08-21-5623ba:T8]) [source: nested tool-result
  payload quoting `retrieve.py`/`build_index.py` output, this raw, T8]
- **"Confident absence" named as the worst failure mode of the retrieval index.** The reviewed
  index returns well-ranked, plausible-looking answers with no signal that entire trunks were never
  in the searched corpus — distinguished explicitly from an index that abstains or flags staleness,
  which the same review calls the more valuable (if less complete) behavior. [paraphrase]
  ([adversarial-plate-review-launch-defects-2026-08-21-5623ba:T8])
- **A cold reader scored 79% on questions the original doer wrote, 30% on questions it wrote for
  itself — and all five self-authored failures were orientation questions**, not content questions:
  who am I, what is live, what is unsaved, can the clock be trusted, does the tooling run. Quoted
  in-raw: "A record written by the doer is an excellent record of conclusions and a poor record of
  preconditions — because the preconditions were ambient in the context that is about to be
  destroyed. The evening survives; the seat does not." [verbatim]
  ([adversarial-plate-review-launch-defects-2026-08-21-5623ba:T8])
- **The reviewed decision-queue index's own generated open-row count had drifted from its prose
  count** (one file stated "open rows: 1" in one place and "3 rows" in another), traced to a
  4-cell decision row appended inside a 2-column coverage table outside the section the counting
  regex scans — "the exact defect this file exists to end," in the review's own words. [paraphrase]
  ([adversarial-plate-review-launch-defects-2026-08-21-5623ba:T58])
- **Positive controls were reported alongside the findings, not omitted.** The review explicitly
  verified and reported passing checks too — a named universal-constitution file matched its
  claimed byte count exactly, a claimed CLAUDE.md duplication was independently confirmed
  (the seat itself loaded the identical standing-constraints block twice), and a sibling document's
  citation-and-strike discipline held at every claim the seat probed. [paraphrase]
  ([adversarial-plate-review-launch-defects-2026-08-21-5623ba:T58])

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[frame-before-commit]] (the review's own obstacle-first, adversarial framing), graph-RAG,
`turn_index.py`, launch procedure / `launch-cfl.bat`, headless review seats.

## Uncaptured Content

- **The sibling trunk's own reviewed documents are quoted only as they appear inside this session's
  tool-result payloads** (the decision-queue index and a companion teaching package), not read
  independently against their own live state — a claim about whether those documents have since
  changed is out of scope here.
- **Turns 9–57 (the bulk of the middle of the session — repeated Read/Bash tool calls building the
  finding list) are not individually cited on this page.** Only the framing at T8 and the closing
  findings at T58 are drawn on; the intermediate tool-call trail that produced them is visible in
  the raw but not walked turn-by-turn here.
- **10 thinking blocks exist in the raw and are encrypted-in-signature** (per the raw's own
  frontmatter) — not recoverable client-side, so no claim on this page draws on the seat's private
  reasoning, only its visible tool calls and final message.
