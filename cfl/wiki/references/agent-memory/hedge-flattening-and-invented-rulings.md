---
title: Hedge-flattening and invented rulings
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_hedge-flattening-and-invented-rulings.md
as_of: 2026-07-30 (memory `modified` timestamp; incidents 2026-07-29)
fidelity: [verbatim] for quoted spans
tags: [quote-fidelity, invented-ruling, hedge-flattening, memory-drain, T-02]
generated_by: wiki-master pilot drain pass, T-02, 2026-08-06
retrieval_key: hedge-flattening-and-invented-rulings
aliases: [invented Jon ruling, dropped hedge, trailing question mark]
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page (T-02 pilot batch) — an operational/process record
  from the CC memory store, not a corpus-derived claim about a conversation. Exempted per
  wiki/references/agent-memory/README.md admission criterion; field added retroactively 2026-08-06
  when the exclusion-class prerequisite the pilot named as unbuilt was built."
---

# Hedge-flattening and invented rulings

## The finding

2026-07-29, four instances in one day, three different agents, all on Jon-attributed text:

1. **Invented ruling.** `wiki/index.md` and `session-stubs.md` stated the `dabe7c` conversation was
   *"Jon-ruled directly ('it's both CFL and personal')."* **That string exists in no primary
   source** — zero occurrences across all of `raw/`, `wiki/`, `exchange/` except one agent-authored
   packet that cited the transcript for it. Circular: the packet was the only "evidence," and the
   index cited the packet as a Jon ruling.
2. **Hedge → answer.** Source: *"Likely more the former?"* (a question). Page: *"Jon's answer on
   mechanics: 'likely more the former'."* Question mark dropped, capital dropped, framed as a
   settled answer.
3. **Hedges dropped entirely.** The moral-hierarchy page read as assertion where Jon had written
   *"I feel as though this is incomplete, but in the right direction. Thoughts? Too vague?"* — a
   lossy paste flattened his doubt on a page about his own moral reasoning.
4. **Punctuation edits inside quotation marks, uncited:** em-dash → comma and capital → lowercase in
   his "categorical floor" statement; `its` for `it's` in a restored quote.

## Why it keeps happening

Paraphrase pressure. An agent embedding a quote in its own sentence wants the quote to fit
grammatically, so it lowercases, swaps punctuation, and drops the clause that makes it a question.
Each edit is individually tiny; together they convert a man thinking out loud into a man issuing
rulings.

## How to apply

- Never write "Jon ruled/approved/said" without a `file:line` quote actually grepped. If the grep
  returns nothing, the attribution is model-authored — say so.
- A trailing `?` is load-bearing. So is a capital letter mid-sentence. Compare punctuation, not just
  words, when verifying a quote.
- Check whether the *citing* source is itself an agent artifact. A quote whose only occurrence is in
  a packet written by an agent is not evidence.
- Provenance instruments key on EXACT field names and silently pass on variants — `source:` vs
  `source_file:` is why instance #1 above was never checked. See [[migrations-blind-instruments]].

This finding is `wiki/SCHEMA.md`'s own "How to quote Jon" rule, ratified 2026-07-28, stated at
instrument-failure granularity — four concrete instances of exactly the class that ratification
exists to prevent.

## Related

Same-batch drain sibling: [[migrations-blind-instruments]]. Not-yet-drained:
`project_corpus-path-divergence`.
