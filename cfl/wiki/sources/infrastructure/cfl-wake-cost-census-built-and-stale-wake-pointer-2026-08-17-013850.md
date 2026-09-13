---
probe_sealed: "where does this citation resolve? => TRUSTED"
title: "CFL headless wake: the wake named an already-consumed letter; cost_census.py built ~25 h early, the meter unit converged on 'everything except cache reads' from two seats' independent routes (2026-08-17, 013850)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 013850
source_kind: session
source_file: raw/transcripts/claude-code/fl/code-2026-08-17-013850-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: 36b22bfe84f219ff0a8d2c9ea88934fa48aa387ff6e5bb15bf84b0a106ef96c4
raw_length: 357627 bytes / 7267 lines (verified turn_count 263, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850
aliases: ["cost_census.py build order", "wake prompt named the wrong letter", "single $base interpolation switchboard-operator.sh:178", "ex_cache_read fits tightest 16 percent", "cachedUsageUtilization", "voyage-4-nano open weight", "evidence was my own instrument"]
generated_by: S-cd-03 executor (week-2026-09-02-corpus lane, RP-3/RP-4), reading the raw transcript directly from the N: read-only mirror (raw/transcripts/claude-code/fl/code-2026-08-17-013850-...md, FULL visible extraction, 0 compaction boundaries, 47 thinking blocks encrypted)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [cost-census, usage-meter, headless-wake, switchboard, letters-channel, self-correction, embeddings, cfl-infra]
---

# CFL headless wake: a stale wake pointer and a cost census built from four `/usage` readings (2026-08-17, 013850)

## Summary

A single-directive switchboard wake of a CFL seat, no Jon turn. The prompt named the Secretary's
RECAPS-MECHANISM letter; a prior CFL turn had already consumed (16:28), answered (16:38) and
hall-posted (16:45) it, and the wake payload on disk named a different, newer letter that had
landed 13 seconds before the wake. The genuinely unread mail was a cost-census build order and an
assignments letter. The session built `scripts/audit/cost_census.py`, discharging the build order
about 25 hours early, then rewired it mid-build when the Secretary found Anthropic's own
percentages on disk; the two seats' independent routes converged on the same meter unit. It logged
four defects, three its own, and caught two stale numbers in its own draft before delivery.

## Key Claims

- **The wake was stale by construction:** `switchboard-operator.sh:178` interpolates a single
  `$base`, so the prompt structurally cannot name more than one letter. "Fix is a habit, not a
  patch: drain the inbox by resolution stamp, never work the letter the prompt names." [paraphrase;
  last sentence verbatim from the assistant]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T263])
- **The wake payload and the wake prompt disagreed:** the payload named a newer letter that landed
  13 seconds before the wake; the session read the real one. [paraphrase]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T64])
- **The denominator was never a research problem:** four `/usage` readings were already on disk,
  each one an equation, so the spread across them is simultaneously the residual and the
  discriminator between candidate meter units. Dropping one recall-grade reading tightened
  `total_tokens` from ±29% to ±19% and only that basis improved — treated as a real signal, and the
  script made grade-aware. [paraphrase]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T263])
- **A defect in its own output caught before publishing:** the headroom line asserted Jon's 69% was
  "inside the band by construction" while printing a 71-86% band beside it; fixed to compute the
  comparison rather than assert it. [paraphrase]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T122])
- **Mid-build the Secretary found `~/.claude.json` → `cachedUsageUtilization` carrying Anthropic's
  own percentages; the session confirmed it from its own seat (`scope.model.display_name="Fable"`,
  `severity:"warning"`, `is_active:true`), demoted its fit to a fallback, and kept the demotion.**
  [paraphrase]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T263])
- **The Secretary's doc research said cache reads are excluded from the meter, a hypothesis not on
  the session's candidate list; added, `ex_cache_read` fit tightest at ±16%, beating ±19%** — "Two
  seats reached the same unit from evidence neither could have produced, and their route named the
  hypothesis my route had left off." [paraphrase; final sentence verbatim from the assistant]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T188])
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T263])
- **Four defects, three its own:** a self-test that could not pass when the code was right
  (`abs(spread(...) or -1)` — `0.0` is falsy); the headroom assertion above; a token column mixing
  564.6M cache reads with 78.6k fresh input; and one NOT published — a peer-facing dedup defect
  fully written up, then falsified by running the real pattern against the real lines: the
  "evidence" was the session's own `json.dumps` re-serialisation, not the file. "Second time today
  my evidence was an artifact of my own instrument." [paraphrase; final sentence verbatim]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T263])
- **Two stale numbers caught in its own draft: D19 is not fixed — the relay's ledger is 2,418 rows
  across 14 fields with zero outcome fields; those wakes are now accounted for in the operator's
  ledger instead. "A metric that improves because coverage moved to another instrument is exactly
  what I'd have published as progress."** [paraphrase; final sentence verbatim]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T263])
- **One thing removed from Jon's queue: Anthropic ships no embedder (verified against their docs);
  `voyage-4-nano` is Apache-2.0 open-weight on Hugging Face — local, no key, no cost — so the
  GraphRAG spec's key-or-local decision did not need to reach Jon for v0.** The bundled
  `claude-api` skill failed to execute and was not on disk, so the claim was verified directly.
  [paraphrase]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T213])
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T263])
- **Close: delivered to all three peer inboxes (12,670 B, marker verified in each), hall entry and
  recap appended with read-back verification, two commits, clean tree; every open row carried a
  named non-Jon owner and a date.** [paraphrase]
  ([cfl-wake-cost-census-built-and-stale-wake-pointer-2026-08-17-013850:T263])

## Conflicts

None with existing wiki content. Note that the sibling wake `e1d2ac` (same day, same trunk)
selected a different open-weight embedder (`potion-retrieval-32M`) for the GraphRAG v0 build than
the one this session named as a road (`voyage-4-nano`); both sessions agree on the point that
matters — no key and no money question needed to reach Jon.

## Entities & Concepts

[[graphrag-retrieval]]; the switchboard operator (`switchboard-operator.sh`) and relay ledger;
`scripts/audit/cost_census.py` and `COST-CENSUS-CURRENT.md`; the drain-the-inbox-not-the-named-
letter rule (agent memory `feedback_drain-the-inbox-not-the-named-letter.md`, written from this
wake); [[derive-dont-record]] (a metric that improved because coverage migrated instruments).

## Uncaptured Content

- The single Human turn is the operator wake prompt, quoting a Jon standing order second-hand; no
  Jon turn exists in this raw. [uncaptured]
- The four `/usage` readings and their sources are on disk in the CFL tree, not reproduced here.
- The Secretary's cost-census letter and documentation research are cited only as this session
  reported them.
- 47 thinking blocks encrypted-in-signature; no claim draws on them.

## Links

- Sibling CFL wakes the same day: `e1d2ac` (GraphRAG v0 build) and `33cbc0` (D11-D13 verification)
  in this lane's batch.
