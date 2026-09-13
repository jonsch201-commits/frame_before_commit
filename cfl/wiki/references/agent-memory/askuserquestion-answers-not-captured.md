---
title: AskUserQuestion answers are not captured
trunk: fl
branch: [cfl]
sub_branch: [corpus]
branch_reason: "R-AGENTMEM; sub: corpus 5 vs wiki 0 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_askuserquestion-answers-not-captured.md
as_of: 2026-07-26 (memory `modified` timestamp)
fidelity: [verbatim] for quoted spans
tags: [corpus-gap, askuserquestion, parser-defect, memory-drain, T-02]
generated_by: wiki-master pilot drain pass, T-02, 2026-08-06
retrieval_key: askuserquestion-answers-not-captured
aliases: [dropped selection, corpus silent question, multiple-choice answer loss]
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page (T-02 pilot batch) — an operational/process record
  from the CC memory store, not a corpus-derived claim about a conversation. Exempted per
  wiki/references/agent-memory/README.md admission criterion; field added retroactively 2026-08-06
  when the exclusion-class prerequisite the pilot named as unbuilt was built."
---

# AskUserQuestion answers are not captured

## The finding

Found 2026-07-26 via a fable-mirror records query. The corpus shows the assistant asking Jon,
verbatim, *"E2 citation threshold — 95% of substantive claims, or a hard 100%?"* — and **his
selection went through an `AskUserQuestion` tool whose chosen option is not preserved in the
transcript.** Only the assistant's later restatement survives
(`code-2026-07-06-da51cc-cc-handoff-packet-review.md:8364` vs `:8370`).

**He answered. The record did not keep it.**

## Why this matters beyond one question

It is the same defect family as the dropped `tool_result` records (fixed 2026-07-25) and the
subagent glob (fixed 2026-07-25) — a whole record class silently absent from the corpus. It means an
unknown number of Jon's rulings given through that UI are invisible to the mirror, and it degrades
every "CORPUS SILENT" finding: silence was already uninformative, but this makes it *actively
misleading* for any question that was ever put to him as a multiple-choice.

## How to apply

- When a mirror query returns CORPUS SILENT on something that looks like it *would* have been asked
  as a choice, say so — "silent, and this is a question-shaped topic where the capture defect
  applies." Do not upgrade silence to "he never ruled."
- Before asserting Jon never decided something, check whether the surrounding transcript shows an
  assistant question immediately followed by an assistant restatement with no Jon turn between —
  that pattern IS the dropped selection.
- The fix belongs to the parser (`convert-claude-code.py` / the extractor), not to whatever project
  trips over it. **Not yet built as of 2026-07-26 — not independently re-verified by this pass; treat
  as still-open unless checked fresh.**
- Corroborates [[derive-dont-record]]: the assistant's restatement of Jon's answer is a *recorded*
  fact with nothing able to notice when it misstates the original.

## Related

Same-batch drain sibling: [[mirror-before-jon]]. Not-yet-drained: `cc-retention-cleanupperioddays`
(a different permanent-loss channel), `md-not-uncaptured-authoritative-disposition`.
