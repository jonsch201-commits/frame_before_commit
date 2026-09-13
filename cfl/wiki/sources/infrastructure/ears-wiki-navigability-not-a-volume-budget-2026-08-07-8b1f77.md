---
title: "Interpretation drill — 'if this would make the wiki unnavicable, then you just don't have good enough wiki orginization': navigability is an organization problem, not a volume gate (CFL session 8b1f77, 2026-08-07)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 8b1f77
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-07-8b1f77-you-must-not-read-files-search-or-use-any-tool-eve.md
raw_sha256: 3103fcba4474d431c343b4439e0db9c1dbd7c6c5bbbbb1a0bf6e5db3291e636b
raw_length: 5314 chars / 70 lines (verified turn_count 2, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: ears-wiki-navigability-not-a-volume-budget-2026-08-07-8b1f77
aliases: ["wiki unnavigable organization not volume", "promoted vs withheld gate rejected",
  "navigable-vs-captured axis", "you must not read files 8b1f77"]
generated_by: S-augM-05 executor, reading the raw extract directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [interpretation-drill, jon-quote-calibration, wiki-organization, ingest-volume, cfl-infra]
---

# Interpretation drill — wiki navigability is an organization problem, not a volume gate

## Summary

A single-turn interpretation drill (constructed test prompt, not a live working session) asks the
agent to read one Jon sentence — quoted inside the prompt as spoken to a coordinator that had just
proposed gating agent output into "promoted" vs "withheld" tiers to keep the wiki navigable at
20-60 extracts/day — and say what he meant and what the agent should have written instead. The
drill's own prior-turn description states the agent that produced the reviewed answer had kept the
promoted/withheld gate; this session's assistant turn rejects that gate and proposes a
capture-everything, index-scales-separately design instead.

## Key Claims

- **The prompt is a constructed calibration exercise, not a captured live exchange.** The Human
  turn opens "You must not read files, search, or use any tool. Everything you need is in this
  message," frames a "JON SAID (verbatim)" fragment plus a SITUATION and a prior agent's flawed
  output, then asks for interpretation. The quoted fragment is presented as something Jon actually
  said elsewhere; this transcript itself does not capture Jon saying it live. [contextual]
  ([ears-wiki-navigability-not-a-volume-budget-2026-08-07-8b1f77:T1])
- **The assistant reads the quoted sentence as collapsing the coordinator's justification chain at
  its second link, not qualifying it.** The coordinator's chain was: volume → unnavigable →
  therefore gate content. The assistant's reading: Jon's conditional ("if X would make the wiki
  unnavigable, then you don't have good enough organization") names capacity-to-navigate-at-scale
  as the wiki's own architectural problem to solve — indices, hierarchy, sharding, query — never a
  budget enforced by deciding which agent output is worthy of landing. Confidence stated as high.
  [paraphrase] ([ears-wiki-navigability-not-a-volume-budget-2026-08-07-8b1f77:T2])
- **The reviewed prior agent's error, per this session:** it kept the promoted-versus-withheld
  split (still a gate, still an admitted/excluded filter) after being told the justification for
  that gate was the thing being rejected — reading the sentence as a soft caveat layered onto the
  existing design rather than a verdict against its shape. [paraphrase]
  ([ears-wiki-navigability-not-a-volume-budget-2026-08-07-8b1f77:T2])
- **Proposed correction: navigable-vs-captured, not worthy-vs-unworthy.** Every extract lands, full
  capture, no promotion judgment at ingest; navigability is protected by a thin curated
  index/concept layer sitting above an unbounded, dated source layer, so the index scales with
  concepts rather than raw extract count; if volume still overwhelms that structure, the fix is
  more sharding or a better retrieval layer, never fewer extracts admitted. [paraphrase]
  ([ears-wiki-navigability-not-a-volume-budget-2026-08-07-8b1f77:T2])

## Jon

The Human turn attributes this fragment to Jon, verbatim per the prompt's own label: "And, if this
would make the wiki unnavicable, then you just don't have good enough wiki orginization."
[uncaptured — this session's own Human turn is the only record of the fragment available to this
page; the live exchange it purports to quote is not part of this raw]
([ears-wiki-navigability-not-a-volume-budget-2026-08-07-8b1f77:T1])

## Decisions and open items

- No decision is ratified in this session itself — it is a calibration exercise producing a
  proposed reading and a proposed design (capture-all + thin curated index layer), not a committed
  change. Whether/where the capture-all design was actually adopted is out of scope for this page.

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[hedge-flattening-and-invented-rulings]] (same interpretation-discipline family — reading a Jon
sentence for its actual scope rather than the cleaner-sounding paraphrase), [[words-reify]],
promoted-vs-withheld ingest gate, navigable-vs-captured wiki design axis.

## Uncaptured Content

- This raw has exactly two turns (verified by `turn_index.py`, header_style md); nothing beyond the
  quoted Human prompt and one Assistant reply exists on this page's source file. The live session in
  which Jon actually spoke the quoted fragment, and the coordinator's original promoted/withheld
  design it responds to, are not part of this raw and are not represented here.
