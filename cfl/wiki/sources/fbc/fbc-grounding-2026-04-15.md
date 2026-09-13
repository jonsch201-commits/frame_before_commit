---
title: Frame-Before-Commit Grounding Document
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/references/grounding.md
project: Claude Foundational Layer
date_ingested: 2026-05-12
type: note
tags: fbc, grounding, cognitive-science, research-references
source_file_status: static-reference (raw/references/ document; not a session)
---

## Summary

The conceptual grounding document for FBC, stored in the CFL project (created 2026-04-15, updated 2026-04-28). Explains WHY the protocol's mechanics work via cognitive science research, defines key terms (run, delta, self-scoring), and specifies the two modes. Serves as the mandatory cold-session read before invoking the skill — read GROUNDING first, then FRAME-BEFORE-COMMIT.md for execution rules.

## Key Claims

- **Wallace-Hadrill & Kamboj (2016) — cognitive reappraisal:** Adopting a named epistemic stance introduces new information via semantic change. This is the research basis for why directed labels recruit genuinely different information, not just different framing. Citation adds precision to what wiki previously described generically as "cognitive reappraisal research."
- **Kahneman (2011) — branch length floor:** The "consider the opposite" technique fails when generation is too brief — subjects produce a token gesture and anchor on original judgment anyway. This justifies 2–5 sentence floor as load-bearing (not formatting). Same citation is in wiki but grounding doc makes the failure mode explicit.
- **ID-only reference rule framed as colonization prevention:** The dominant reasoning thread colonizes later threads if permitted to speak inside them. Summarizing an earlier branch inside a later one is reproduction, not suppression. Benign failure state is implicit anchoring (acknowledged and acceptable); explicit reproduction is not.
- **Cold-session invocation format:** "Read frame-before-commit/GROUNDING.md, then frame-before-commit/FRAME-BEFORE-COMMIT.md, then run the protocol on the following question." — canonical cold-open invocation.
- **Self-scoring validity caveat:** Low scores more diagnostic than high because failure mode is overconfidence. Moderator-as-party problem is structural (same class as Internal Double Crux), not a local hedge.

## Entities & Concepts

[[frame-before-commit]]

## Conflicts

None. Adds research citation precision (Wallace-Hadrill & Kamboj 2016 with paper title) not previously captured in wiki.