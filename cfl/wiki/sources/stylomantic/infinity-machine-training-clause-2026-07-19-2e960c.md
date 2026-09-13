---
title: "Training restrictions and corpus usage — The Infinity Machine license clause"
trunk: fl
branch: [stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-STYLO; sub: branch `stylomantic` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-19-2e960c-training-restrictions-and-corpus-usage-guidelines.md
date_ingested: 2026-07-19
type: session
tags: stylomantic, licensing, legal, corpus-policy
---

## Summary

Jon asks whether working with Claude on a Stylomantic-style decoder layer modeling "The Infinity Machine"
(a book) would count as "training" under a "may not be used for training" license clause, and what that
implies for corpus use. Claude distinguishes technical "training" (gradient updates to weights — not what
happens in-context) from the clause's likely purpose (preventing wholesale reproduction or style-cloning),
concludes the decoder use is a defensible-but-judgment-call middle case, and flags the largest actual
training-exposure risk as the claude.ai conversation channel itself (data may feed Anthropic's training
pipeline depending on data-sharing settings) rather than Jon's decoder. Jon then adds a durable constraint:
no full raw audiobook/text extraction into the CFL without his direct approval.

## Key Claims

- **"Used for training" (technical) ≠ what the clause is protecting against (purpose)** — an in-context
  decoder that never updates weights is not technical training, but if used *generatively* to produce text
  in the author's voice, that is "the clause's beating heart" regardless of the technical framing
  ([2e960c:T2]).
- **Claude's disclosed conflict of interest**: the largest actual training exposure isn't Jon's decoder, it's
  this channel — claude.ai conversations can feed Anthropic's training pipeline depending on data-sharing
  settings, so Claude has a stake in downplaying the training question ([2e960c:T2]).
- **Descending safety ordering for corpus handling** (Claude's proposal): discuss/analyze locally via Ollama
  (clean) → fit decoder locally, private, non-generative (defensible judgment call) → paste corpus text into
  claude.ai (check data settings first) → use decoder to generate in-style text (advised against — this is
  the clause's core target regardless of whether "training" technically occurred) ([2e960c:T2]).
- **Durable constraint registered via memory edit**: "Do NOT extract or ingest the full raw audiobook/text of
  'The Infinity Machine' (Sebastian Mallaby, 2026) into the CFL wiki or any agent-readable surface without
  Jon's direct approval" ([2e960c:T3]) — Jon-ratified, not a Claude proposal.
- **Book identification, verified via search**: *The Infinity Machine: Demis Hassabis, DeepMind, and the
  Quest for Superintelligence* by Sebastian Mallaby, published 2026-03-31, ~15 hours audio, narrated by
  Vidish Athavale [grounded, via search] — publication postdates Claude's training cutoff, so the book's
  actual text is not in Claude's weights; Claude knows *of* it, not *its content* ([2e960c:T3]).
- **[UNGROUNDED] flagged**: whether the license clause even binds Jon contractually (copyright-page assertion
  vs. an assented license differ) — left unresolved, with the author's intent treated as unambiguous
  regardless of enforceability ([2e960c:T2]).

## Entities & Concepts

[[stylomantic]]

## Conflicts

None.
