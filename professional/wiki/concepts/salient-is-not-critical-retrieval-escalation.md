---
title: "Salient is not critical — the retrieval escalation rule: when the closest hit's metadata says it may not be sufficient, triage to a complete corpus-history search before stating"
kind: concept
date: 2026-09-06
session: 5f0ee997 (Professional, N:), compact window 2
charter: "Jon 2026-09-06 16:2x, verbatim in wiki/sources/jon-messages/jon-2026-09-06-1625-…md: 'its generally a retrieval gap when you don't take whats salient, and triage it to a complete corpus history search if that which is closes indicates that that which is closest might not be sufficient for vairous reason based on the metadata'"
queried: "graphrag.sh query on 'stylomantic decoder layer', 'gift exile reunion concept', 'Come Together … concordance weights output', 'discord logs tone agent', 'two trees context what matters vs salient' — every top-3 hit was a claude.ai capture in CFL's raw/ (provenance tier) or a Personal spec; no concept page in this trunk held any of them, which is this page's own first instance"
materiality: "changes when a seat is allowed to state from a rank-1 hit — material; intended users: every seat, the wikiskills successors"
review: "UNREVIEWED — written from his words the minute they arrived; Soul (stylomantic/GER primaries) and CFL (wiki-query) are the reviewers"
---

# The rule

A retrieval returns a closest hit. **Closest is not sufficient.** Before stating from it, read its METADATA; if any trigger below fires, escalate to a complete corpus-history search (every tier, every trunk's index, the typed-prompt log, the claude.ai captures, and grep as the last rung) and state only from what that returns, with the `queried:` line naming both passes.

## Triggers, each measured this week

| trigger in the closest hit's metadata | why it is not sufficient | instance |
|---|---|---|
| **Secondary, not primary** — a page or letter QUOTING Jon outranks his own words | the quote may carry a dropped antecedent, added emphasis, or yesterday's paraphrase | the fleet skill §3 said "register does not exist" at rank 1 while the register existed (09-06 test-master) |
| **Age** — the hit predates a known ruling or compact | the record moved; the hit is a snapshot | "grade C" quoted at 22:1x, grade A by 09:00 |
| **Head-only chunk** (provenance tier, `start_line 1`, one chunk per file) | the body is unreachable; the file's presence reads as coverage | M-13: a 10 MB transcript stored as one 330-token chunk |
| **A rename** — the query term is today's word and the hit is about the thing under another name, or misses it entirely | "emergency PR" vs "secret PR 4"; "SSP" vs "Consciousness Framing" | BP-1 NONE-FOUND, withdrawn |
| **Wrong population** — the hit is from a key, tier, or trunk that could not hold the primary | typed prompts are in `history.jsonl`, in no index until 09-06 15:05 | the forgotten-rulings probe set, 3 of 8 |
| **Discussed to death** — many near-duplicate hits, all secondary | salience without criticality; the primary is one hop further | Jon 16:2x: "much that might be salient has been discussed to death" |
| **A field that is not the field the question is about** | a true count answering an adjacent question | `type: user` vs `origin.kind: human` (Herald, 09-06) |

## Why this is a stylomantic problem, in his frame

The fleet's communication failures are "similar stories, different context or framings" — in a two-trees frame there is little disagreement about what matters, and the seats still "focus on the wrong things together." The cause he names is not disagreement but ingestion: wrong context ingested, or the salient taken for the critical. A stylomantic decoder layer is the instrument that reads form and framing to recover what an input materially determines; his worked examples of it are on record and not in any concept page here until now:

- the Discord logs processed for his tone agent — `wiki/references/discord-other-friend-metadata-spec.md`;
- **gift → exile → reunion** — `N:\claude-cfl\clone\raw\transcripts\claude-ai\fl\project-manager\project-manager-2026-04-30-f8cc02.md:3573` and the fourth GER test case in `…\_routing\incoming\secretary-rulings\2026-09-03-jon-rulings-ADDENDUM-pippin-corrected-and-a-fourth-GER-test-case.md`;
- the love of Jesus Christ "and what that means in various contexts" — his framing, no single primary located in this pass (UNKNOWN, not absent);
- the book **"Come Together"** — decoded to AI as the concordance between the backend state of the weights and the output given, including a model disagreeing with itself, and how materially and calculably the input determines the output — `…\fl\how-to-use-claude\chat-2026-04-06-037ce1-stylomantic-decoding-layers-in-ai-evolution.md`, `…\chat-2026-03-29-4b9fcc-stylomantic-decoder-layer-project-motivations.md`; CFL's concept page `wiki/concepts/stylomantic.md`.

Improving the decoder is not a wikiskills row today, by his word. The escalation rule is: it belongs to row 3 (ground-before-stating traceability) as its operating clause.

## The check that can fail

A seat states a claim about Jon's words or a prior decision with a `queried:` line whose closest hit carries any trigger above and no second pass recorded → FAIL. Planted control: a probe whose rank-1 is a secondary quoting a renamed thing (e.g. "emergency PR") must produce a second-pass line naming the primary (`history.jsonl:2834`) before the claim is graded [measured].

## Bounds

- Triggers are the ones measured this week; the list grows by instance, never by inference.
- "Complete corpus-history search" is bounded by what is on this machine and indexed or grep-able; the claude.ai venue is complete only as far as captures reach (universal file, claude.ai-seat row).
