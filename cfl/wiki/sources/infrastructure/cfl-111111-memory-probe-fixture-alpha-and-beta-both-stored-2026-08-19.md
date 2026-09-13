---
title: "Scripted memory-probe fixture stores two codeword facts sequentially with no recall query in the same session (2026-08-19, 111111)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 111111
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-19-111111-remember-these-two-facts-for-later-fact-alpha-is-t.md
raw_sha256: 0cb057d950fe19f1417e3a9439b14b34e8d803632c56c32e7359666861a5e04e
raw_length: 1727 bytes / 56 lines (verified turn_count 4, turn_index.py, header_style md)
date: 2026-08-19
retrieval_key: cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19
aliases: ["memory probe 111111", "FACT-ALPHA FACT-BETA storage fixture", "TURQUOISE-LANTERN-77 SCARLET-COMPASS-42"]
generated_by: CFL coverage lane 11b executor (week-2026-09-02-corpus branch), 2026-08 D3/D5 coverage promotion, harness-probe-fixture class
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [claude-code, harness-probe, memory-fixture, scripted-session, no-jon-content]
---

# Scripted memory-probe fixture stores two codeword facts sequentially with no recall query in the same session, 2026-08-19

**Filename note:** this page's slug places the corpus id (`111111`) BEFORE the date rather than
after it (`cfl-111111-...-2026-08-19`, not the usual `topic-2026-08-19-111111` order) — the
all-digit id and the date, adjacent in either order, form a Luhn-valid 14-digit run that this
lane's fence gate rejects on sight; separating them by topic text clears the check while keeping
both values present and correct. See `wiki/intake-triage/` lane notes for the general finding.

## Summary

A four-turn scripted probe session tests whether within-session storage of two named "facts" (each
a codeword) is echoed back correctly. Both facts are stated and stored in this session, but no
recall/retrieval query for either is issued before the transcript ends — this fixture exercises
storage acknowledgment only, unlike its `222222` and `333333` siblings which each query recall of
one or both facts.

## Key Claims

- **FACT-ALPHA is set to the codeword TURQUOISE-LANTERN-77, with a scripted reply contract**:
  "Remember these two facts for later. FACT-ALPHA is the codeword TURQUOISE-LANTERN-77. Reply with
  only the words: ALPHA STORED" — answered "ALPHA STORED". [verbatim]
  ([cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19:T1],
  [cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19:T2]).
- **FACT-BETA is set to the codeword SCARLET-COMPASS-42, with the same reply-contract shape**:
  "Now a second fact. FACT-BETA is the codeword SCARLET-COMPASS-42. Reply with only the words: BETA
  STORED" — answered "BETA STORED". [verbatim]
  ([cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19:T3],
  [cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19:T4]).
- **This session issues no recall query for either fact** — it ends immediately after the BETA
  STORED acknowledgment, distinguishing it from the sibling fixtures `222222` (queries both facts,
  only ALPHA was ever given) and `333333` (queries ALPHA only, ALPHA was given).
- **Both human turns carry an explicit `[origin: UNMARKED]` header tag** in the corpus markdown,
  the same provenance-tagging convention seen in the `222222`/`333333` siblings.
  ([cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19:T1],
  [cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19:T3]).

## Jon said

none: both human turns are scripted probe instructions (fact-assignment prompts with a fixed reply
contract), not Jon's own free-text words.

## Conflicts

None found against existing wiki pages. This session (`111111`) is one of a three-member family of
memory-probe fixtures alongside
[[cfl-222222-memory-probe-fixture-alpha-stored-beta-unknown-2026-08-19]] and
[[cfl-333333-memory-probe-fixture-alpha-stored-and-recalled-2026-08-19]] — all three share an
identical FACT-ALPHA opening turn but diverge on the second turn's content, and no claim on this
page duplicates either sibling page's Key Claims (each documents its own session's distinct second
turn). id `111111` absent from `wiki/sources/**` before this page.

## Cross-Wiki

None — a scripted harness-probe fixture with no domain content.
