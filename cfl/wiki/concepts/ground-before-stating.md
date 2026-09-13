---
title: Ground-Before-Stating (GBS)
trunk: fl
branch: [gbs]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; branch from title/slug keyword (gbs); sub: branch `gbs` has no registered sub-branches"
type: concept
first_seen: agent-interaction-framework-2026-07-02-5990f2
source_count: 2
last_updated: 2026-07-07
---

## What This Is

Ground-Before-Stating (GBS) is the **claim-grounding discipline** of the foundational layer's
epistemic layer — the per-agent rule that a committed claim must carry its provenance and a fidelity
label rather than being asserted bare. Where [[frame-before-commit]] governs *divergence before
commitment* (generating frames before settling), GBS governs *grounding at commitment* (labeling what
a claim rests on when it becomes load-bearing). The two are the paired disciplines of the epistemic
layer in the [[multi-agent-orchestration]] three-layer model; both are per-agent, not orchestration
mechanics. ([agent-interaction-framework-2026-07-02-5990f2])

## What the Wiki Says

### Position in the node/loop model

GBS is the **ears→voice gate** in the Ears/Voice/Thoughts node taxonomy: source labels attach *at the
ear* (everything entering context is untrusted-by-default and labelable on entry), and GBS enforces
that what crosses into *voice* (committed output) carries its grounding. In the loop taxonomy it is
**L2, the grounding loop** ("ear→voice gate, built v1"). Mechanical enforcement lives only at the voice
boundary — a hook can lint GBS labels on output; nothing can gate thoughts. ([agent-interaction-framework-2026-07-02-5990f2])

### The paired-discipline split (with FBC)

- **FBC** = the thoughts→voice gate (divergence discipline).
- **GBS** = the ears→voice gate (grounding discipline).
- **Hooks** = mechanical enforcement at the voice boundary.

FBC branches are **exempt** from GBS; **COMMIT and META apply GBS**. See [[frame-before-commit]] for
the full rule and its architectural rationale (branches must not hedge internally). ([session-open-gbs-fbc-alignment-2026-07-07-883667])

### Point-of-commitment refinement (2026-07-07)

**GBS attaches at the point of commitment, not the point of origin.** A branch-originated claim that
survives into COMMIT is grounded *there*, when it becomes load-bearing — closing the path by which an
unlabeled, possibly false branch attribution could be laundered into a [DELTA] through the FBC
exemption. Confirmed by Jon ("100% agree, brilliant"). ([session-open-gbs-fbc-alignment-2026-07-07-883667])

### Relationship to the wiki citation standards

GBS is the behavioral discipline whose written-artifact analogs already live in the wiki: the
[[citability-standard]] (turn-level citation format), the Citation Quality vocabulary
(verbatim / paraphrase / reconstructed / contextual), and the wiki-master computed-claim provenance
rule (any computed value carries `[source: <script> @ <hash>]`). GBS is the general principle; those
are its wiki-master instantiations. When a claim is post-hoc reconstruction rather than a causal trace
(e.g., decomposing a no-FBC output into implicit branches), GBS requires the `[reconstructed — not
causal]` tag — the CoT-faithfulness caveat. ([agent-interaction-framework-2026-07-02-5990f2])

### Grounding as self-correction (observed)

GBS is load-bearing precisely on self-referential claims: in the 883667 session it caught a
memory-sourced "T-09 = professional governance, acute" assertion that contradicted the wiki record
(T-009 = Stylomantic→02-CF bridge) — the wiki-first check is GBS applied to the agent's own memory.
In the 5990f2 session the same discipline drove the refusal to manufacture a "found" secret
("zebra7431" was the agent's own example, not a planted value) rather than laundering a plausible
answer as success. ([session-open-gbs-fbc-alignment-2026-07-07-883667])

## Conflicts

None.

## Related

[[frame-before-commit]], [[multi-agent-orchestration]], [[citability-standard]], [[loop-taxonomy]], [[wiki-ingest-methodology]]
