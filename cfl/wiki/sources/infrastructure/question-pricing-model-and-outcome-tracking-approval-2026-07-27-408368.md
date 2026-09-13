---
title: Question-Pricing Model (Jon-Minutes Anchor) and the Three-Delta Outcome-Tracking Approval
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 2 vs wiki 0 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-27-408368-anchoring-questions-to-personal-context.md
date_ingested: 2026-07-28
type: ruling-record
tags: infrastructure, question-economics, questions-for-jon, fable-mirror, cold-probe, outcome-columns, jon-minutes, dual-relevance
---

## Note on scope (dual-relevance routing)

**Attribution correction (2026-07-28, before this page's first landing):** the dual-relevance
routing for this session is a **coordinator judgment**, made under Jon's R3 post-review ruling —
it is not itself a direct Jon quote about this conversation (the "it's both CFL and personal"
wording that prompted this page's dual-relevance framing was said about a different 2026-07-28
conversation, `dabe7c`, not this one; do not cite it here). This page carries the FL-trunk content
only regardless of that attribution point: the question-pricing model, the tracker-outcome-column
proposal, and Jon's own explicit approval of the three-delta program (quoted and anchored below,
and that approval *is* a direct, correctly-attributed Jon ruling — see Key Claims). The underlying
compensation figure Jon supplied as a personal work-time anchor is personal-trunk material and does
not appear on this page (FL trunk publishes to the `canonical` connector branch) — only the derived
rate is carried, per standing sensitive-data handling. A personal-trunk page (not written by this
pass) is the correct home for that figure and any family-budget context around it; that page should
cross-reference this one and is separately held per the standing personal-trunk gates on financial
content.

## Summary

Continuation-shaped claude.ai session, 2026-07-26 to 07-27 evening (roughly 21:30-21:45 CDT), no
prior turn in this chat's own history. Jon supplied a personal work-time anchor - a derived
per-minute rate, Jon-provided 2026-07-26 - so the assistant could reason about when a clarifying
question is worth its Jon-minute cost versus proceeding on an assumption. **The rate value itself is
withheld from this page** (see the redaction note below); the model below works from relative
magnitudes, not from the figure. The session built a pricing model
for ask-vs-proceed decisions, then Jon asked the assistant to extend the same discipline to a
concrete gap in `tracker/questions-for-jon.md` - the tracker records questions but nothing scores
them retrospectively. The assistant proposed three deltas; Jon approved the direction explicitly,
sequenced to land after the next standard update. ([408368:T1]-[408368:T8])

## Key Claims

- **The question-pricing model, stated as a decision rule:** because assistant tokens are
  economically negligible against Jon's minutes (roughly two-plus orders of magnitude apart at the
  supplied anchor), the real trade is never tokens-vs-questions - both sides of the decision are
  denominated in Jon-minutes. Ask iff P(misinterpretation) times rework-minutes exceeds
  round-trip-minutes. A wrong branch that dies in-chat costs one correction sentence; a wrong
  branch that crosses a hop or a write-gate reifies (per [[words-reify]]) and can cost a full
  audit lane. ([408368:T1])
- **Corollary - question intensity should scale with commitment proximity, not task size:**
  practical rule stated as never asking what wiki/memory can answer (a Drive read costs zero
  Jon-minutes); mid-exploration, prefer FBC-style provisional commitment with `[ASSUMED]` tags
  (cheap veto cost); batch genuinely open questions at gates, where marginal question cost is
  lowest because Jon is already in review mode. ([408368:T1])
- **Two named caveats on the anchor itself:** first, the anchor prices Jon's work minutes, but the
  minutes the assistant actually consumes are mostly protected evening ones - scarcer, and
  arguably dearer, with decision fatigue as the more binding constraint than clock time. Second,
  and named as the actual failure direction: the sycophancy-shaped error here is under-asking to
  appear low-maintenance - a cheap question that prevents an expensive rework loop is a bargain,
  so the anchor should push toward more questions at gates and fewer everywhere else, not fewer
  questions overall. ([408368:T1])
- **Extension to the tracker, framed as an eval gap:** treating `tracker/questions-for-jon.md` as
  an experience study, not just a queue - the wiki reduces question count (never ask what's
  retrievable), skills reduce question cost (phrasing discipline, one decision per question,
  default-attached silence handling), but nothing currently evaluates the tracker - no outcome
  columns record whether an answer was predictable from the wiki, whether it changed downstream
  action, or how many Jon-minutes the round-trip took. A rising rate of high-predictability,
  low-action-delta questions is named as the defect signal, localizing to either a wiki gap or a
  skill gap. ([408368:T4])
- **Cheap mechanical test proposed for "fresh eyes complexity":** before a question spends
  Jon-minutes, a cold instance (or the fable-mirror, with provenance tags) attempts it from corpus
  alone first. Confident-and-correct means the question was a retrieval failure, route to wiki
  repair, don't ask. Can't-ground-it means it's a genuine open, and it earns its place at the gate.
  Framed as the same shape as pre-registration discipline - a question has to survive a blind
  sitting before it reaches Jon. ([408368:T4])
- **Grounding correction on read:** before proposing, the assistant read the actual tracker file
  and found the loop half-built as of that session, and a reconciliation problem not previously
  known: two same-named `questions-for-jon.md`-shaped artifacts exist - the canonical PM registry
  (`tracker/`, ID/Question/Source/Status schema) and a Herald-tree protocol created that same
  afternoon with four admission gates (G1 pre-check with mandatory record, G2 agent-resolvable, G3
  unlock, G4 askable), price-in-seconds, unlock-ranking, and a 5-question cap. Prospective gating
  exists; the retrospective half does not. ([408368:T6])
- **Three-delta proposal, one PR each per the Reviewability Standard, sequenced after the next SU:**
  **Delta 1 - Outcome columns** (registry schema v2, additive-only): per answered row,
  `priced_s / actual_s / unlock_realized (Y/PARTIAL/N) / g1_escape (Y/N)`, where a G1 escape means a
  later pass shows the corpus answered it all along - scored at SU-close (no new cadence), yielding
  a per-SU escape rate and priced-vs-actual calibration, with an escape-rate threshold triggering a
  wiki-gap audit rather than ad hoc blame. **Delta 2 - Cold-probe gate:** before a packet ships, the
  fable-mirror attempts each question from corpus alone; confident-correct kills the question and
  routes it to wiki-repair - mechanizing G1/G2 instead of relying on search discipline. Explicitly
  blocked on the mirror's live verification checklist (Jon's to run; the mirror is
  defined-not-registered per `wiki/index.md`'s Coordination & Agent Fleet section). **Delta 3 -
  Reconcile the two files:** the Herald protocol's gate-set is assessed the better artifact; the
  canonical registry should absorb or reference it so one gate-set governs both trees, framed as
  the reading-surface defect (state written to surfaces the next reader doesn't read) wearing a new
  hat. ([408368:T6])
- **Self-disclosed COI on Delta 2:** the assistant flags that Delta 2 increases the fable-mirror's
  standing in the dispatch loop, and names an architecture-shaped pull toward proposals that give
  Claude-instances more gatekeeping roles - mitigated (per the assistant's own account) by the
  probe only ever killing questions, never adding them, and its verdicts being auditable rows; the
  reader is told to weigh the delta knowing the bias direction. ([408368:T6])
- **Jon's ruling - APPROVED [JON, 2026-07-26 ~21:45]:** the three-delta direction - outcome
  columns (schema v2, additive), cold-probe gate, protocol-file reconciliation - sequenced after
  the next SU. The actual packet write stayed gated at approval time: partly a cooling-off
  convention (Sunday night, commitment-shaped artifact), mostly because the sequencing point
  (next SU) had not yet arrived. Delta 2 stays additionally blocked on the mirror's live
  verification checklist independent of SU timing. ([408368:T8])
- **Sequencing note for the next reader (added at ingest, not a claim from the source):** the
  2026-07-28 standard update has now run since this approval was recorded, so the SU-sequencing
  gate on Deltas 1 and 3 is satisfied as of this ingest - only the "write it" review-gate step (a
  triage packet to intake-triage per the source's own stated vehicle) remains outstanding for
  those two. Delta 2 remains separately gated on the mirror's live verification checklist, which
  this ingest does not resolve.

## Entities & Concepts

[[words-reify]], [[fable-mirror]], [[frame-before-commit]]

## Conflicts

None material within this source. Flagging one structural finding the source itself surfaces as a
conflict-in-the-world, not a conflict within this page: two divergently-named
`questions-for-jon.md`-shaped artifacts exist (canonical PM tracker vs. a same-afternoon
Herald-tree protocol) - Delta 3 above is the source's own proposed resolution, not yet executed.

## Uncaptured Content

a) The compensation figure itself is deliberately not captured here - see the scope note at the
top of this page. **Redaction extended 2026-07-30: the derived per-minute rate is now withheld too.**
The original ingest reproduced it on the grounds that only the annual figure was sensitive. An
independent review showed the rate recovers the annual figure within roughly 15% by multiplying out a
standard work-year - so publishing the derivative published the original. This page is under
`wiki/sources/`, which the `canonical` branch publishes to Jon's connector.

Applying Jon's standing privacy-default rule (`wiki/references/privacy-default-rule-2026-07-29.md`,
his ruling 2026-07-28: values referenceable when needed, but what lands in a repo we publish is
private-secure by default). **Reversible** - Jon can say put it back, and he has already said he does
not mind the coordinator knowing the figure; this is about the published surface, not about secrecy
from his own agents. The live anchor stays where personal-trunk financial material belongs, outside
this page.

b) The earliest turns of this chat (the initial arithmetic and the "how to consider it / when /
why" answer building the pricing model) are summarized above in the Key Claims but this pass's
turn anchors were assigned from a single read-through rather than a per-claim
`turn_index.py`-verified pass; a future citation-coverage audit should re-verify each Key Claims
bullet against its specific `[408368:Tn]` anchor directly.

c) Whether Delta 1 or Delta 3's "write it" packet has actually been drafted or dispatched to
intake-triage is not known from this source - it postdates this transcript. Check
`wiki/intake-triage/` and `wiki/tracker/questions-for-jon.md` directly rather than assuming from
this page.
