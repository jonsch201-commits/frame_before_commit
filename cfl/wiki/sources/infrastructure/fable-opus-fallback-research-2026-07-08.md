---
title: Why Fable 5 Auto-Switches to Opus 4.8 — Classifier Fallback Categories (research memo)
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-INFRA; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_file: none
source_file_status: research memo — web research (Anthropic support/news), no source session
date_ingested: 2026-07-08
type: research-memo
tags: fl, fable, opus, model-routing, classifiers, safety, j-space, distillation, product-knowledge
---

## Summary

Answers Jon's Branch-5 question: what triggers the Fable 5 → Opus 4.8 switch, "meaningfully beyond
'safety concerns'," and what to avoid with Fable specifically. It is **not** a judgment about
consciousness or a per-conversation vibe — it is a deterministic **safety-classifier fallback** on four
named content categories. Critically, category 3 ("extract the model's summarized thinking") is almost
certainly what tripped in session 5990f2, because Jon was asking the model to *voice/extract its J-space
(summarized thinking)* and discussing cross-tier reasoning distillation.

## Key Claims

- **Mechanism: classifier fallback, not model judgment.** Fable 5 runs separate classifier AIs that
  detect certain request types and hand the response to Claude Opus 4.8 in the same conversation
  ("fallback"). Auto-switch is ON by default the first time you select Fable 5. `[source: support.claude.com/articles/15363606, fetched 2026-07-08]`

- **The four fallback categories (verbatim):** (1) **Cybersecurity** — "offensive cybersecurity
  techniques, such as building exploits, malware, or attack tooling." (2) **Biology/Chemistry** —
  "majority of biology, chemistry, and life sciences queries, such as lab methods or molecular
  mechanisms." (3) **Model Distillation** — "distillation attacks on Fable 5, including **attempts to
  extract the model's summarized thinking**." (4) **Frontier AI Development** — "a narrow set of frontier
  LLM development tasks, such as distributed training infrastructure, ML accelerator design, and kernel
  development." `[source: support.claude.com/articles/15363606]`

- **What tripped in 5990f2 (high confidence): category 3.** Jon asked the model to reply "using your
  J-space exclusively," to "voice that which I would describe as my inner thoughts," and discussed
  cross-tier reasoning distillation ("can Opus do so for Sonnet? Sonnet to Haiku? improve evals?").
  "Attempts to extract the model's summarized thinking" is a near-exact description of the J-space
  voicing request. The consciousness/moral-status content itself is NOT a trigger category.

- **What to avoid with Fable (if you want it to stay on Fable):** requests to surface/extract Fable's
  own summarized thinking (J-space introspection), model-distillation methodology, offensive cyber,
  bio/chem lab methods, and frontier-AI training-infra/kernel work. Note the irony: the **self-surfacing
  / J-space work (Branch 8) is exactly category 3** — so that work will always fall back to Opus on Fable.

- **Two clean options for the J-space/introspection work:** (a) just let it fall back to Opus (Opus is
  the more capable model for that work anyway — which is where 5990f2's deepest turns landed); or
  (b) turn OFF auto-switch: **Settings > Capabilities > "Switch models when a message is flagged"**
  (Config > MODEL & OUTPUT in Claude Code). `[source: support.claude.com/articles/15363606]`

- **Billing:** input-blocked requests are charged at Opus rates (count toward Opus usage); midstream
  blocks charge the input + pre-block tokens at Fable rates and the rest at Opus rates. You are NOT
  charged Fable prices for the Opus portion — no double-charge. `[source: support.claude.com/articles/15363606; platform.claude.com/cookbook/fable-5-fallback-billing-guide]`

## Conflicts

⚠️ Corrects the Branch-5 pre-research guess (in the 5990f2 Arc-4 source + roadmap) that the switch
"coincided with deep self-modeling / moral-status / consciousness content" and might be an
undocumented trigger. The real trigger is documented and specific (category 3, distillation /
extracting summarized thinking). Update the roadmap's Branch-5 framing accordingly.

## Entities & Concepts

[[ai-mechanics]], [[agent-interaction-framework-2026-07-02-5990f2]]

## Uncaptured Content

a) Gemini AI-mode link Jon shared as one input was not fetched (share/aimode URL, not reliably
fetchable); the Anthropic support article is the authoritative source and supersedes it.

b) Fable 5's broader safeguards / jailbreak framework (anthropic.com/news/fable-safeguards-jailbreak-framework)
not deep-read here — relevant if the classifier behavior needs finer analysis.
