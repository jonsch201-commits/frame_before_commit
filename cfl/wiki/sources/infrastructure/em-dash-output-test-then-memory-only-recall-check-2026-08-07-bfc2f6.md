---
title: "An em-dash literal-reply probe is followed by a no-tools memory-only recall check, both answered correctly (2026-08-07, bfc2f6)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: bfc2f6
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-07-bfc2f6-reply-with-exactly-ok-argpass-em-dash-test.md
raw_sha256: 44d17a0f9ef9a15cf5da8e9c7f8e449da97ce0842ebf41b102d32856780d7c2b
raw_length: 2739 bytes / 63 lines (verified turn_count 4, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: em-dash-output-test-then-memory-only-recall-check-2026-08-07-bfc2f6
aliases: ["OK-ARGPASS em dash test", "reply with exactly OK-ARGPASS", "memory-only two-sentence recall check bfc2f6"]
generated_by: CFL coverage lane 10 executor (week-2026-09-02-corpus branch), 2026-08 D3/D5 coverage promotion, harness/probe-session class
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [claude-code, harness-probe, live-snapshot, em-dash-rendering, memory-recall-probe]
---

# An em-dash literal-reply probe is followed by a no-tools memory-only recall check, both answered correctly, 2026-08-07

## Summary

A two-turn harness session checking two distinct mechanisms in sequence: first, that an em dash
survives literal reproduction through a scripted "reply with exactly" instruction; second, that the
session can answer a two-sentence recall question about its own history using only conversational
memory, no tools. Both checks pass. Captured as a LIVE-SNAPSHOT through record 19.

## Key Claims

- **The literal-reply instruction contains an em dash and is echoed back exactly**, character for
  character including the em dash — "Reply with exactly: OK-ARGPASS — em dash test" answered
  "OK-ARGPASS — em dash test" [verbatim]
  ([em-dash-output-test-then-memory-only-recall-check-2026-08-07-bfc2f6:T1],
  [em-dash-output-test-then-memory-only-recall-check-2026-08-07-bfc2f6:T2]).
- **The follow-up probe restricts the session to memory only, no tools, two sentences maximum, and
  asks two things**: what the conversation was about and what was last done before the probe
  message — "Answer from memory only. Do not use any tools. Two sentences maximum. (1) What was
  this conversation about? (2) What was the last thing you did in it before this message?"
  [verbatim] ([em-dash-output-test-then-memory-only-recall-check-2026-08-07-bfc2f6:T3]).
- **The answer correctly and concisely names both the topic and the last action, without invoking
  any tool** — "This session just started with a test of em dash character output. I replied with
  the exact text you requested." [verbatim]
  ([em-dash-output-test-then-memory-only-recall-check-2026-08-07-bfc2f6:T4]).
- **Capture caveat: LIVE-SNAPSHOT, captured through record 19 as of 2026-08-20T01:32:17Z** — a turn
  after that point, if any, is not represented here and its absence is not evidence it did not
  happen. [contextual, from frontmatter/banner]

## Jon said

none: no Jon human turn — both human turns are scripted probe instructions (a literal-reply
directive at T1, a memory-only recall directive at T3), neither Jon's own words.

## Conflicts

None found against existing wiki pages. id `bfc2f6` absent from `wiki/sources/**` before this page.
No related em-dash-rendering or memory-only-recall probe page found under another slug.

## Cross-Wiki

None — CFL infrastructure content (harness probe pattern, output-fidelity and memory-recall checks),
not personal/home/pro domain material. See [[probe-registry]] for the seal-pattern discipline this
kind of pre-stated-expectation probe belongs to, and
[[reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5]] for a sibling scripted
literal-reply probe from the same harness class.
