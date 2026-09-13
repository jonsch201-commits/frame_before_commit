---
title: Migrations blind instruments
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_migrations-blind-instruments.md
as_of: 2026-07-29 (memory `modified` timestamp)
fidelity: [verbatim] for quoted spans
tags: [path-migration, blocking-gate, silent-failure, memory-drain, T-02]
generated_by: wiki-master pilot drain pass, T-02, 2026-08-06
retrieval_key: migrations-blind-instruments
aliases: [instrument denominator check, resolves-vs-exits-0, empty-population pass]
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page (T-02 pilot batch) — an operational/process record
  from the CC memory store, not a corpus-derived claim about a conversation. Exempted per
  wiki/references/agent-memory/README.md admission criterion; field added retroactively 2026-08-06
  when the exclusion-class prerequisite the pilot named as unbuilt was built."
---

# Migrations blind instruments

## The finding

2026-07-29: the L1 corpus move (`raw/sessions/` → `raw/transcripts/`) ran on disk while its git
shadow sat in an unmerged PR. Three instruments broke silently:

- `lint_skills.py` — 3 skills with dead `raw/sessions/` pointers (the sweep covered `wiki/` and 5
  scripts, never `skills/`). This one at least *failed loudly*.
- `lint_citation_coverage.py:361` — globs `raw/sessions/**`, now empty. Reported citation coverage
  as **0.4%**. True value ~55%. It was measuring the move, not the wiki, and was two steps from
  becoming the baseline number in Jon's evening brief.
- `verify_quotes.py` — **a BLOCKING gate for the FL trunk.** Returned `0 UNSUPPORTED` *and*
  `0 SUPPORTED`. It resolved nothing, so it could fail nothing.

## Why

An instrument that resolves a claim against a path reports "clean" and "can't see" identically
unless the *denominator* is checked. `0 UNSUPPORTED` out of 0 resolvable is not a pass. This is
`RATIO_FLOOR` inverted — see [[derive-dont-record]] for the alarm calibrated so it always fires; this
is the alarm that can never fire.

## How to apply

- After ANY path migration, run every instrument and check that its *resolvable population* is
  non-zero and roughly what it was before. Compare denominators, not verdicts.
- A migration's sweep must be a **committed, idempotent script**, never a hand-edit — otherwise it
  cannot be re-run after the next merge adds new stale citations, and its scope is undiscoverable.
  Scope must include `skills/`, not just `wiki/`.
- Land the mechanical sweep **last** in a merge train and regenerate it, rather than rebasing
  judgment PRs onto a 300-file diff.

## Related

Same-batch drain sibling: [[derive-dont-record]], [[hedge-flattening-and-invented-rulings]] (which
this memory is itself cited from, on the exact-field-name failure mode). Not-yet-drained:
`md-not-uncaptured-authoritative-disposition`, `unshipped-fix-updates-its-own-docs`.
