---
title: Stochastic Retrieval — Directed Randomness as Wiki Source Selection
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (wiki); sub: wiki 6 vs skills 0 on authored labels"
type: concept
moved_from: wiki/analyses/stochastic-retrieval-research-concept-2026-06-04.md
moved_date: 2026-07-03
source_file: raw/intake/stochastic-retrieval-research-concept-2026-06-04.md
source_file_status: OK
project: Claude Foundational Layer
date_created: 2026-06-27
date: 2026-06-04
tags: fl, research-concept, stochastic-retrieval, wiki, rag, stylomantic, fbc, test-master
---

## Summary

Research concept raised by Jon during a voice/graph walkthrough session (2026-06-04). Proposes replacing pure relevance maximization in wiki source selection with directed randomness — a relevance-band sampling approach. Jon explicitly flagged structural parallels to Stylomantic. Filed as a test-master/research thread candidate; requires design pass before empirical testing.

## The Concept

**What Jon described:** A wiki source selection system where Claude reads a random sample from within a relevance band rather than the highest-scoring retrieval. Key properties:

- Selects "versions" or "pieces" of sources rather than everything
- "Directed signal with ambiguity built in" — correlated with the frame but not highest-similarity retrieval
- Claude has the option to "recall" alternative options (what else could have been selected)
- Does not affect the context window content itself — intervenes at selection, not at substance

Jon's exact words (reconstructed): *"random number generator select 'versions' or 'pieces' of sources for you to read (not everything, directed signal with ambiguity built in, with you having the option to 'recall' other options)... does not actually affect your context window. It just meaningfully lets you 'hook' directedly random thoughts that you could know are meaningfully corrilated with a given frame, or might alternatively reflect random noise (both may be helpful in context)"*

## Why This Is Different From RAG

RAG: maximize relevance score → retrieve top-K.

Stochastic retrieval: sample within a relevance band → introduce productive noise → enable alternative recall.

The hypothesis: highest-relevance retrieval may create a **"retrieval colonization" effect** analogous to FBC's single-frame problem. A dominant retrieval crowds out adjacent-but-different signal. Directed randomness may improve performance on tasks where the correct framing is uncertain.

## Structural Analogy to Stylomantic

Jon flagged this explicitly: *"meaningfully similar to stylomantic in that it does not actually affect your context window."*

- **Stylomantic:** intervenes at the output probability distribution (token-level logprob manipulation; no weight changes)
- **Stochastic retrieval:** intervenes at the input selection layer (retrieval-level sampling; no context-content changes)

Both share the pattern: **intervention at the interface, not the substance.**

The "recall alternatives" feature mirrors Stylomantic's beam search alternative paths — you could surface what other retrievals were available and what they would have injected.

## Open Design Questions

1. What is the relevance band? (cosine similarity threshold? top-N×2 pool sampled to top-N?)
2. How does "recall" surface alternatives? (on-demand? always logged?)
3. Is the randomness seeded (reproducible) or truly random?
4. What's the success metric? (task outcome quality? FBC branch independence? subjective usefulness?)
5. Does this require changes to existing wiki infrastructure or can it be implemented as a skill?

## Routing

- Design/formalization pass needed before testing (relevance band definition, recall mechanics)
- Empirical testing (does stochastic retrieval outperform pure-relevance on real tasks?) → **test-master**
- Possible skill implementation if design is self-contained

## Related Concepts

[[stylomantic]], [[frame-before-commit]], [[extraction-pipeline]]
