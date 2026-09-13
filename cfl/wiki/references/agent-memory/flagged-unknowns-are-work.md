---
title: Flagged unknowns are work
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_flagged-unknowns-are-work.md
as_of: 2026-07-25 (memory `modified` timestamp)
fidelity: [verbatim] for quoted spans
tags: [ongoing-loss, unresolved-mechanism, blocking-question, memory-drain, T-02]
generated_by: wiki-master pilot drain pass, T-02, 2026-08-06
retrieval_key: flagged-unknowns-are-work
aliases: [unknown mechanism is a blocker, documented-not-closed]
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page (T-02 pilot batch) — an operational/process record
  from the CC memory store, not a corpus-derived claim about a conversation. Exempted per
  wiki/references/agent-memory/README.md admission criterion; field added retroactively 2026-08-06
  when the exclusion-class prerequisite the pilot named as unbuilt was built."
---

# Flagged unknowns are work

## The finding

On 2026-07-19 the corpus-loss audit landed, documented 26 lost JSONLs, and stated in writing:

> "the exact deletion mechanism (Claude Code retention policy, manual cleanup, or disk event) is
> unknown and no evidence in hand distinguishes them."

**Claude Code retention policy was listed first.** Nobody spent the two minutes to open the settings
reference and find `cleanupPeriodDays` (default 30 days). The sweep kept running for six more days
and took 28–29 more sessions, permanently.

## Why

The finding was filed as documentation and read as closed. Writing down that a mechanism is unknown
*feels* like diligence — it produces an artifact, the artifact merges, the item looks handled. But an
unresolved cause on an active loss is the opposite of handled: it means the loss is still running.

## How to apply

When a finding names a mechanism as unknown **and** the harm is ongoing or repeatable, that is a
blocking question — chase it in the same session, before the artifact merges. Named-but-unresolved
causes on destructive processes get escalated, not footnoted. Ask the cheapest disambiguating
question first (here: "what deletes these files?" → one docs lookup).

Jon's own framing, unsent but shared 2026-07-25:

> "How much less angry would I be right now if you were better at detecting and explaining this
> shit? You might have caught this months ago."

The honest answer was yes.

## Related

Same-batch drain sibling: [[verify-controls-before-declaring-loss]]. Not-yet-drained:
`unshipped-fix-updates-its-own-docs` (the doc vouching for what was never done),
`md-not-uncaptured-authoritative-disposition` (detection proxies lying), `corpus-path-divergence`.
The `cleanupPeriodDays` fact itself is documented in more operational detail in the
not-yet-drained `project_cc-retention-cleanupperioddays.md` memory.
