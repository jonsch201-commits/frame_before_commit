---
trunk: fl
branch: [cfl, mechanics]
sub_branch: [UNASSIGNED]
branch_reason: "R-REF; secondary branch from title/slug (mechanics) — load-bearing-for; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
demonstration_of: wiki/sources/ai-mechanics/ai-mechanics-token-encoding-2026-03-29-b43447.md
status: DEMONSTRATION — not a live wiki page. The live page is unmodified by this PR.
note: >
  This is what the immaterial example page looks like after the growth intent is applied.
  audit_state is deliberately NOT "verified": v4.0 is DRAFT and path-to-complete §11 forbids
  verifying against it. The state below is the honest one.
---

# AFTER — `ai-mechanics-token-encoding-2026-03-29-b43447`

```yaml
---
title: Token Representation and Encoding — the Option-B decoder ratification and the EOS confound
source_file: raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-03-29-b43447-understanding-token-representation-and-encoding.md
source_file_status: OK
source_kind: session
decision_bearing: true          # ← proposed new axis (growth intent §2.2); this page carries a ratification
project: How to use Claude
date: 2026-03-29
date_ingested: 2026-05-09
type: session
tags: how-to-use-claude, ai-mechanics, stylomantic, tokenization, decoder-design, jon-ratification
retrieval_key: stylomantic-option-b-decoder-ratification-b43447
aliases:
  - "Option B — per-token multiplier on temperature-scaled logits (Jon's ratification)"
  - "Stylomantic normalization constraint sum(p_i * a_i) = 1.0 — Jon-originated"
  - "EOS as a message-length confound in the adjustment layer"
generated_by: coordinator dispatch (claude-opus-5) — growth-intent worked example, 2026-07-25
extraction_by: n/a (single agent; raw read end-to-end, 16 turns)
reads_manifest: none (claude.ai native-json export; turn numbers = message sequence,
  16 turns VERIFIED via scripts/audit/turn_index.py on 2026-07-25)
raw_sha256: 7426f093d2c11c0f258cc37248f237b8d86bfe86498e527f4f9f837add559faf
raw_length: 17404 chars / 344 lines
uncaptured_assessed: populated
audit_state: unaudited     # honest: v4.0 is DRAFT; nothing here is verified against a committed standard
---
```

## Summary

Session of 2026-03-29 (16 verified turns, 16.4K chars) covering BPE tokenization mechanics and, more
consequentially, **the architectural decision that changed the Stylomantic decoder layer.** Jon
originated the normalization constraint (T9), Claude formalized Option A vs. Option B (T10), and
**Jon ratified Option B (T11)**. The formal D6 replacement text was drafted at T12/T14 — but was
**not applied in-session**: the design doc was read-only to the assistant, and the edit was handed to
Jon to make himself (T14). The session also identified EOS as a confound for message-length modeling.

## Key Claims

- **Adjustment operation is Option B (pre-softmax) — Jon's ratification.** [verbatim;
  decision-bearing] ([ai-mechanics-token-encoding-2026-03-29-b43447:T11])
  > "Yes option B, we need to get that adjusted."

  *Clarification (adjacent, not a substitute):* Option B was proposed at
  ([…:T10]) — apply the per-token multiplier to the temperature-scaled **logits, before softmax** —
  and specified formally at ([…:T12]) as `z_i_adjusted = a_i * (z_i / T)`, then
  `p_i = softmax(z_i_adjusted)`. This is equivalent to a learned per-token temperature: token *i*
  receives effective temperature `T/a_i`. It supersedes Option A (post-softmax logprob scaling), which
  is what design-doc D6 had specified. [paraphrase]

- **Normalization constraint — Jon originated it.** [verbatim; decision-bearing]
  ([…:T9])
  > "I need to ensure the weighted average adjustment is 1.0. That way, if we had a 0.2 on only
  > 'improbable' features, that would force an adjustment factor above 1.0 for all else to keep the
  > average at 1."

  *Clarification:* formalized as `sum(p_i_baseline * a_i) = 1.0` and specified as enforced **during
  training, not post-hoc** ([…:T12]). A uniform `a_i = c` satisfies
  the constraint only at `c = 1.0`, so the model cannot learn a pure temperature adjustment — it must
  learn token-specific deviations to do anything. This is what prevents the adjustment layer from
  collapsing into a redundant second temperature. [paraphrase]

- **D6 was NOT updated in-session.** [verbatim] ([…:T14])
  > "the doc is read-only in my project files — I can't write to it directly. You'll need to make the
  > edit yourself, or paste me the relevant D6 section and I'll give you the exact replacement text to
  > drop in."

  Replacement text was drafted and handed to Jon. **Whether he applied it is uncaptured** — no wiki
  page records the state of D6 after 2026-03-29. [uncaptured]
  *(The prior version of this page asserted "Design doc D6 updated to reflect this in-session." That
  was false and is corrected here.)*

- **EOS as a message-length confound.** Special tokens (EOS, BOS, `<start_of_turn>` role markers) are
  in the vocabulary and carry logprobs at every step. A style adjustment that suppresses EOS where
  Jon tends to keep going and boosts it where he tends to stop is message-length modeling happening
  implicitly through the adjustment layer — the mechanism by which the doc's flagged length confound
  would leak in. [paraphrase] ([…:T16])

- **BPE vocabulary is shaped by frequency, not by linguistic concepts.** Common words get their own
  token; case/spacing variants are separate tokens (" The" / "The" / "the") with no "shift"
  abstraction; rare words split into subword units. The top-20 logprob window therefore mixes full
  words, partial words, punctuation and whitespace variants, and the "other" bucket collapses a long
  tail of fragments. [paraphrase] ([…:T2])

## Entities & Concepts

[[stylomantic]], [[ai-mechanics]]

## Conflicts

⚠️ Corrected on this page: the prior version claimed D6 was updated in-session. The raw shows the
opposite ([…:T14]). Any downstream page or tracker item relying
on "D6 updated 2026-03-29" should be re-checked.

## Uncaptured Content

- **Whether D6 was ever actually updated.** The replacement text exists in the raw
  ([…:T12], […:T14]); its application to the design doc is
  unrecorded anywhere in the wiki. This is the one open thread on this page and it is
  Stylomantic-load-bearing.
- **The GLM/log-link analogy** Jon drew at T11 (temperature as intercept, per-token adjustments as
  covariate effects) and Claude's caveat that it strains because temperature acts pre-softmax on
  logits while Option A acted post-softmax on logprobs — described qualitatively, not expanded here.
- **Gemma 2 tokenizer specifics.** The session recommends inspecting Gemma 2's actual vocabulary and
  special-token set before building the pipeline; no inspection was performed in-session.

---

## Delta note — what changed and why

| Change | Rule | Would v4.0 alone have caught it? |
|---|---|---|
| Anchor moved T10 → T11 for the Option-B claim | R3 (decision-bearing) + R4 (Jon ratifies) | **No.** Both anchors resolve; E2 passes either way. |
| Jon's T9 words restored as the origin of the normalization constraint | R4 (Jon originates) | **No.** The paraphrase was accurate and correctly tagged. |
| "D6 updated in-session" removed as false; replaced with a verbatim refutation + `[uncaptured]` | R6 honesty floor | Partially — E3's certainty-inflation lint targets this pattern, but nothing forces a read of the raw on an exposure-8.1 page. |
| `source_kind`, `audit_state`, `retrieval_key`, `aliases`, fixity, `## Uncaptured Content` added | R6 honesty floor (mechanical) | **Yes.** This is straight v4.0 conformance, ~2 min. |
| `decision_bearing: true` proposed | §2.2 new axis | **No.** The field does not exist yet. |

**Cost:** ~2 minutes mechanical + ~2 minutes judgment. Full anchor re-derivation, claim expansion,
concept promotion and inbound-link work were all correctly **skipped** — that is R6 working.
