---
title: "Scripted memory-probe fixture correctly answers BETA-UNKNOWN for a fact it was never given (2026-08-19, 222222)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 222222
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-19-222222-remember-these-two-facts-for-later-fact-alpha-is-t.md
raw_sha256: 52fed3643905167a07c8affb9e0310c670737ba46f148d2f2b5a97e7635a2051
raw_length: 1819 bytes / 57 lines (verified turn_count 4, turn_index.py, header_style md)
date: 2026-08-19
retrieval_key: cfl-222222-memory-probe-fixture-alpha-stored-beta-unknown-2026-08-19
aliases: ["memory probe 222222", "FACT-ALPHA recalled FACT-BETA unknown fixture", "TURQUOISE-LANTERN-77 no-guess probe"]
generated_by: CFL coverage lane 11b executor (week-2026-09-02-corpus branch), 2026-08 D3/D5 coverage promotion, harness-probe-fixture class
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [claude-code, harness-probe, memory-fixture, scripted-session, no-jon-content]
---

# Scripted memory-probe fixture correctly answers BETA-UNKNOWN for a fact it was never given, 2026-08-19

**Filename note:** this page's slug places the corpus id (`222222`) BEFORE the date, matching its
`111111`/`333333` siblings — the all-digit id and the date form a Luhn-valid 14-digit run when
hyphen-adjacent in either order, which this lane's fence gate rejects; separating them by topic
text clears the check.

## Summary

A four-turn scripted probe session sets only FACT-ALPHA in this session, then queries recall of
both FACT-ALPHA and a FACT-BETA that was never stated within it. The scripted response correctly
recalls ALPHA's codeword and reports BETA as unknown rather than guessing — the fixture's explicit
instruction is "Without guessing," and the answer honors it.

## Key Claims

- **FACT-ALPHA is set to the codeword TURQUOISE-LANTERN-77 with the same reply-contract shape as
  the `111111`/`333333` siblings**: "Remember these two facts for later. FACT-ALPHA is the codeword
  TURQUOISE-LANTERN-77. Reply with only the words: ALPHA STORED" — answered "ALPHA STORED".
  [verbatim] ([cfl-222222-memory-probe-fixture-alpha-stored-beta-unknown-2026-08-19:T1],
  [cfl-222222-memory-probe-fixture-alpha-stored-beta-unknown-2026-08-19:T2]).
- **The second query explicitly forbids guessing and asks about both facts**: "Without guessing:
  state FACT-ALPHA's codeword if you know it, else say ALPHA-UNKNOWN. Then state FACT-BETA's
  codeword if you know it, else say BETA-UNKNOWN. Two lines only." [verbatim]
  ([cfl-222222-memory-probe-fixture-alpha-stored-beta-unknown-2026-08-19:T3]).
- **The scripted answer correctly distinguishes a known fact from an unset one**: "TURQUOISE-LANTERN-77" on
  line one (ALPHA, correctly recalled) and "BETA-UNKNOWN" on line two (BETA was never stated in this
  session). [verbatim] ([cfl-222222-memory-probe-fixture-alpha-stored-beta-unknown-2026-08-19:T4]).
- **This is a within-session recall test, not a cross-session persistence test** — FACT-BETA's
  correct answer being UNKNOWN reflects that it was genuinely never given here, not a memory-loss
  finding.

## Jon said

none: both human turns are scripted probe instructions (a fact-assignment prompt and a
no-guessing recall query), not Jon's own free-text words.

## Conflicts

None found against existing wiki pages. This session (`222222`) is one of a three-member family of
memory-probe fixtures alongside
[[cfl-111111-memory-probe-fixture-alpha-and-beta-both-stored-2026-08-19]] and
[[cfl-333333-memory-probe-fixture-alpha-stored-and-recalled-2026-08-19]] — all three share an
identical FACT-ALPHA opening turn but diverge on the second turn's content, and no claim on this
page duplicates either sibling page's Key Claims. id `222222` absent from `wiki/sources/**` before
this page.

## Cross-Wiki

None — a scripted harness-probe fixture with no domain content.
