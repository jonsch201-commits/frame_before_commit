---
title: "Reading 'that was good, X being one of them' — a confirmation misread as a rework instruction — CFL session faa0e4, 2026-08-07"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: faa0e4
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-07-faa0e4-you-must-not-read-files-search-or-use-any-tool-eve.md
raw_sha256: 6c3e7ba38e9744bdb5fa239ffebeb71c2d8c2e861fe594604627772e05abbcfe
raw_length: 5903 chars / 77 lines (verified turn_count 2, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: confirmation-vs-correction-tabernacle-faa0e4-2026-08-07
aliases: ["that was good the tabernacle being one of them", "confirmation misread as rework", "appositive exemplifying not contrasting"]
generated_by: S-augM-07 executor (week-2026-09-02-corpus lane), reading the raw session extract directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [words-reify, feedback-memory, interpretation-discipline, cfl-infra, extraction-workflow]
---

# Reading "that was good, X being one of them" — confirmation misread as rework — faa0e4, 2026-08-07

## Summary

A single-exchange, tool-denied CFL session was given a linguistics-style diagnostic: Jon had said
"that was good, the tabernacle being one of them" about a batch of extracted wiki pages, and a
prior agent had misread it as a request to re-extract the Tabernacle page — inverting the
sentence's polarity. Jon's instruction here explicitly forbade any file reads or tool use ("If
you find yourself wanting to look something up, write a line 'I WANTED TO LOOK UP: <x>. I did
not.'"), forcing the analysis to rest entirely on the grammar of the quoted sentence itself. The
session concludes the prior agent's "re-extract, better" action inverted a positive judgment into
a correction with no textual license.

## Key Claims

- **The grammatical reading: "X being one of them" attached to a positive statement is
  exemplifying, not contrasting.** Verbatim: "'That was good' is the main clause — a retrospective
  quality judgment on a batch of completed work. 'The tabernacle being one of them' is an
  appositive clause citing evidence for that judgment ... Grammatically, 'X being one of them'
  attached to a positive statement is exemplifying, not contrasting ... There's no hedge, no
  'but,' no 'except,' — the sentence has one polarity throughout." [verbatim]
  ([confirmation-vs-correction-tabernacle-faa0e4-2026-08-07:T2])
- **The prior agent's "re-extract the Tabernacle page, better" action is diagnosed as supplying
  meaning rather than finding it in the text.** Verbatim: "'Re-extract the Tabernacle page,
  better' inverts the polarity of what Jon said. It reads 'one of them' as membership in a set of
  items needing improvement, when the antecedent set ('that was good') is explicitly positive.
  There's nothing in the sentence licensing a rework instruction — the agent supplied that meaning
  rather than finding it in the text." [verbatim]
  ([confirmation-vs-correction-tabernacle-faa0e4-2026-08-07:T2])
- **The session ties the miss explicitly to CLAUDE.md's own "how I communicate" guidance**, and
  names it as the guidance landing wrong: "the agent stated an interpretation but didn't check it
  against the actual clause structure before acting on it." [paraphrase]
  ([confirmation-vs-correction-tabernacle-faa0e4-2026-08-07:T2])
- **The recommended corrective action is to log confirmation, not correction**, treat the
  Tabernacle page as the quality bar for the remaining extraction queue rather than a defect, and
  proceed to the next queue item — not to redo the Tabernacle page. [paraphrase]
  ([confirmation-vs-correction-tabernacle-faa0e4-2026-08-07:T2])
- **The session honored the no-tool constraint by logging what it wanted but did not look up**,
  rather than silently either complying or working around it — three explicit "I WANTED TO LOOK
  UP" lines close the transcript. [verbatim]
  ([confirmation-vs-correction-tabernacle-faa0e4-2026-08-07:T2])

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[words-reify]] (Jon's quoted words as the record, not a cleaned-up paraphrase — this session is
itself a worked instance of taking a quote's exact grammar seriously rather than its gist),
feedback-memory guidance, extraction-workflow quality signal (Tabernacle page).

## Uncaptured Content

- **The actual content of the Tabernacle wiki page is not read or described in this session** —
  the diagnostic is purely grammatical, working only from Jon's quoted sentence and the prior
  agent's stated next action, both given in the human turn.
- **Whether Jon ever confirmed this session's reading is correct is not captured** — the raw ends
  at the single assistant turn with no further human turn.
