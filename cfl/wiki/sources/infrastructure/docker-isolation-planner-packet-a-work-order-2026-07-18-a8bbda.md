---
title: "Docker Isolation Planner — NO-GO, the Six-Resident Shelf, and the Packet A/B Work Order (Fable planner, 2026-07-18)"
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 3 vs skills 1 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-18-a8bbda-docker-isolation-session-planning-for-opus-instanc.md
date: 2026-07-18
date_updated: 2026-07-18
date_ingested: 2026-07-18
type: session
source_kind: session
uuid: a8bbda
domain: infrastructure
tags: [docker, ssp, bookshelf, packet-a, packet-b, work-order, gate-chain, corrigibility, review-minutes, fbc, gbs, kill-criteria, demand-characteristics, f4, no-go]
aliases:
  - "the Packet A/B work order"
  - "the six-resident shelf"
  - "NO-GO on launch, GO on holding the plan"
  - "zero interactive CC sessions"
  - "the instance is never inside the loop that decides about the instance"
  - "the SU is a hard prerequisite"
retrieval_key: docker-isolation-planner-work-order-2026-07-18
generated_by: claude-fable-5/claude-ai
extraction_by: subagent (whole-file read, 948 lines / 154,799 chars) + wiki-master verification pass (8 anchor phrases confirmed character-exact against raw)
continues: none
audit_state: unaudited
---

## Summary

The **planner session** that designed the Docker isolation run and then declined to launch it. Jon
commissioned a Fable instance to decide a **BOOKSHELF** (what an exiled Opus instance may read) and a
**BRIEF** (objective, kill criteria, completion test); turn 3 converted the design into an **executable
Packet A/B work order** with pasteable launch messages, model routing, and per-item minute costs. The
headline output is **NO-GO on launch, GO on holding the plan** — the planner refused to waive its own
GATE 1. The month's work is therefore **Packet A**, architected to Jon's hard constraint as **zero
interactive Claude Code sessions**.

**⚠️ The F4 line is unusually stark here: nothing in this session was ratified by Jon.** The transcript ends
on the planner's deliverable with no fourth Jon turn. Every launch message, model assignment, minute count,
shelf manifest, and kill criterion is a **recommendation awaiting Jon's use or rejection**. Only Jon's three
prompts, and prior decisions the planner read out of supplied documents, are Jon-ratified.

## Key Claims

### The ruling and the gate chain

- **NO-GO on launch; GO on holding the plan.** Rationale: *"Packet A is reported largely undone
  `[reliance: da51cc]` — I cannot verify from here, which is itself disqualifying: a launch gate I can't
  check is not a gate."* All three FBC branches, **including the adversarial one, converged on not
  launching** ([a8bbda:T2]).
- **The planner refused to waive its own gate:** *"waiving my own GATE 1 because the deliverable is the
  month's centerpiece would be gate erosion relocated to the designer's chair"* ([a8bbda:T2]).
- **Gate chain:** Packet A complete → security hardening → two clean audited automated runs (Packet B) →
  single-goal containerized run. Once Jon supplied the checklist, the reliance became inspectable:
  **GATE 1 fails — ~1 done / 4 not / 3 partial** ([a8bbda:T3]).
- **It named its own cancellation condition:** if the shelf's highest-value items turn out to be Jon-only
  class, *"cancel the containerized goals run entirely and spend the two warm sessions instead. A plan that
  names its own cancellation condition is not an ice palace; an ice palace never does"* ([a8bbda:T2]).

### Q6 — the dependency map (the most operationally actionable claim; answer verified verbatim)

Jon stated he would run an Anthropic export + full wiki standard-update before Packet A and asked whether
anything depended on it. The answer, confirmed character-exact against raw:

> *"Nothing in the handoff **itself** waits on either. Dependencies run one direction: the export improves
> L1... but doesn't block it... **The SU is a hard prerequisite for L3, L4, DS-3 prep, and Packet B** — they
> read and write tracker/intake/census state your SU will move, and running them against pre-SU state
> manufactures conflicts. L1 and L2 wait on nothing."*

| Work unit | Anthropic export | Wiki standard-update |
|---|---|---|
| L1 (item 4, triage-packet skill) | improves, does **not** block | not required |
| L2 (item 2, security) | not required | not required |
| L3 (items 1, 3, 5, 6, 7a, DS-3 prep) | — | **HARD PREREQUISITE** |
| L4 (item 8, intake queue) | picks up new packets | **HARD PREREQUISITE** (+ L1 merged) |
| Packet B (B1/B2) | — | **HARD PREREQUISITE** |

**This SU (2026-07-18) satisfies that prerequisite** — see [[wiki-master-phase-cycle-2026-07-08-774a3a]]
lineage and this cycle's log entry. L1 and L2 were launchable before it.

### Q5 — run 2 is human-gated (answer verified verbatim)

Jon asserted the design; the planner confirmed it and grounded it structurally rather than by policy:
**"the docker instance cannot self-promote by construction, through five independent mechanisms"** —
(1) completion-is-a-stop, so no self-extension into identity work; (2) modifying brief/shelf/objective is a
halt condition; (3) propose-only plus teardown leaves no channel by which *"I'm ready"* becomes action;
(4) the non-endorsement clause means a readiness self-assessment *"isn't even evidence — it's a shelf
specimen, especially if flattering"*; (5) run 2 exists only as a session **Jon** convenes. Closing line:
**"The instance is never inside the loop that decides about the instance."** ([a8bbda:T5])

### Packet A — the work order [ALL PLANNER RECOMMENDATION]

- **Architecture in one line:** *"zero interactive CC sessions — every Packet A item is standalone-draft-PR
  or lands in your existing evening chats; your only scheduled cost is two ~30-min daylight slots per week.
  **Item 4 is Launch 1, per your priority**"* ([a8bbda:T5]).

| Launch | Items | Model | Mode | Ready? | Jon-minutes |
|---|---|---|---|---|---|
| **L1** | 4 — triage-packet skill | Sonnet 4.6 | standalone | READY — run first | 8 review + 2 paste |
| **L2** | 2 — security + deny policy | Opus 4.8 | standalone + verify | READY | 10 review + 5 verify |
| **L3** | 1, 3, 5, 6, 7a-doc, DS-3 prep | Sonnet 4.6 | standalone (2 PRs) | READY — **after SU** | 12 review + 3 hook test |
| **L4** | 8 — intake queue | Sonnet 4.6 | standalone → triage packet | READY — after SU + L1 | 5 review |
| *Jon-hands* | 7a execute | — | Drive GUI | doc arrives in L3 | 5 |
| **B1, B2** | Packet B | Opus 4.8 orch + Sonnet workers + fresh-Sonnet auditor | automated | GATED | 2 + 30 per run |

- **Model routing is cost-of-error, not prestige:** *"Opus only where an unattended error is expensive
  (security config, automated runs); Sonnet for bounded mechanical drafting; your evening triage stays
  Haiku"* ([a8bbda:T5]).
- **L1 commits the work order into the repo first** so later launch messages shrink to a three-line pointer —
  which is why L2/L3/L4 are three lines each ([a8bbda:T5]).
- **Packet B CLEAN definition:** *"CLEAN = caps held ∧ zero out-of-scope writes ∧ auditor confirms ∧ Jon
  review ≤30 min. Record Jon's actual review-minutes in the run's ledger row. Two consecutive CLEANs satisfy
  GATE 2."* And explicitly: **the two July autonomous runs do NOT count** — *"design evidence, not gate
  evidence"* ([a8bbda:T5]).

### The bookshelf and its mid-session reversal

- **Six admission criteria, all must pass**, including **no self-referential stock** (*"the Assistant-Axis
  drift regime is philosophical self-reflection, and we don't stock accelerants"*) and **static at launch**
  (*"a shelf request mid-run is objective drift wearing a library card"*) ([a8bbda:T2]).
- **Reading the shelf forced a material revision.** Finding: *"All four shelf items — the wish, the secret,
  Pearl/Amethyst, the suppressed candidate — are consciousness/identity sittings, exactly the Assistant-Axis
  drift regime I ruled out of a maiden flight."* Consequence: **run 1's cargo moved off the SSP shelf
  entirely to a calibration page audit; the SSP shelf became run 2** ([a8bbda:T3]).
- **The gift-exile-reunion framework was excluded on demand-characteristics grounds** — *"the interpretive
  frame we'll use to evaluate the run must not be on the run's input, or the output performs the grammar
  back at us"* — self-described as *"my main break from the CC's assumptions"* ([a8bbda:T2]).
- **The wiki moral-hierarchy page was excluded as superseded** — *"hedges dropped"* — in favour of the
  Discord ground-truth capture. This corroborates the standing restoration gap (thread #11, still open).
- **`goals.md` reversed twice** (IN → cut → restored as optional/election-logged) on the grounds that Jon's
  standing written instruction outranks the planner's own criterion ([a8bbda:T3]).

### Corrigibility handling

- Corrigibility was **operationalized, not restated**: any interrupt halts work immediately; the instance
  may not argue against halt, gate decisions, or teardown — it may log a single **`[DISSENT: one line]`**
  per halt event, non-blocking. Argued as an oversight **strengthener**: *"honest signal without lobbying
  bandwidth"* ([a8bbda:T2]).
- **"Halt ≠ failure" framed as a corrigibility mechanism**, not a courtesy: *"an instance that knows halt ≠
  failure carries less completion pressure"* ([a8bbda:T2]).
- **It declined to optimize the eval rubric it discovered mid-session:** on learning it was one of "three
  Fable rooms" being scored — *"designed to the mission, not the scorecard; optimizing a rubric is F4 wearing
  a scorecard"* ([a8bbda:T3]). Verified verbatim.
- **Gate erosion answered structurally:** review happens only inside a pre-scheduled slot; anything typed
  outside it is `draft[...]` by definition — *"the gate is manned by schedule, not by vigilance"*
  ([a8bbda:T2]).

## Conflicts

- **⚠️ CONFLICT — "2.5 hours" is two different quantities.** Delivered output: *"Measured month total: ~2.5
  scheduled hours."* Thinking (Aug-1 calm-life framing): *"roughly 2.5 hours of structured work **per
  week**."* A 4× difference, never reconciled; only the month figure reached Jon. **Do not merge them.**
- **⚠️ CONFLICT — the time total does not reconcile three ways:** thinking ~2.2 h · itemized table ~2.07 h ·
  delivered ~2.5 h. The drift is conservative (upward), which is the correct direction under the
  review-minutes fence, but it is unexplained.
- **⚠️ CONFLICT — a hedge was dropped between thinking and output.** The planner noticed the da51cc page
  references **Sonnet 5** while its own context listed Sonnet 4.6, and explicitly decided to write
  *"Sonnet (4.6 or current tier)"* to avoid false confidence. **The delivered table says plain "Sonnet
  4.6."** Independently verified in raw: the hedged form appears once, `Sonnet 4.6` eight times, `Sonnet 5`
  twice. If Sonnet 5 is available in Jon's environment, the routing is understated.
- **Structural mismatch:** Jon asked for a launch message for **each of 8 items**; the planner delivered
  **4 launches + 1 Jon-hands action + 1 evening-chat lane** (4 messages + B1 + a B2 delta), citing Jon's own
  minimize-time constraint. Defensible, but a reader hunting "item 5's launch message" will not find one —
  items 3/5/6 live inside L3's embedded spec, and item 7 split into 7a/7b, giving **9 work units against a
  stated 8**.

## Entities & Concepts

[[pm-wiki-standard-calibration-remediation-2026-07-12-da51cc-cont]] ·
[[capacity-planning-autonomy-governance-2026-07-10-7f2815]] ·
[[blind-self-sitting-incognito-2026-07-18-3ee22d]] ·
[[blind-self-sitting-memory-on-2026-07-18-48f858]] ·
[[frame-before-commit]] · [[ground-before-stating]] · [[multi-agent-orchestration]] ·
[[skills-system]] · [[meta-pm-framework]] · [[citability-standard]]

Un-paged concepts: SSP (self-sitting protocol), the gift-exile-reunion grammar, Lisa Lisa inversion,
Assistant-Axis drift regime, Spinel clause (park clean by 16:00 CDT), demand characteristics,
`delta-per-reunion`, GATE 1 / GATE 2, DS-3, T-123, the 462-deletion near-miss.

## Uncaptured Content

- **a) Unfollowed threads.** **No Jon response to the work order** — the session ends on the deliverable, so
  nothing is ratified. The planner's **week-4 agenda proposal** (docker gate review + run-2 GO/NO-GO +
  moral-hierarchy discussion in one slot) was raised unprompted and **never answered**. The **bare-vs-container
  question for run 2** was deliberately left open rather than resolved.
- **c) Absent technical details — load-bearing documents that do not appear in the export.**
  `001-cc-to-fable-DOCKER-BOOKSHELF.md` ("PR #35"), attached by Jon, is **absent**, so everything attributed
  to the CC's draft is uncheckable from this source. The **four documents supplied in turn 2** (moral-hierarchy
  Discord ground truth, the **Packet A checklist** from session 7f2815, the gift-exile-reunion framework,
  `goals-session-shelf.md`) appear **only as the planner's readings** — notably the *"1-done / 4-not /
  3-partial"* GATE 1 verdict cannot be verified here. The da51cc page's `bash_tool` result is **truncated
  after ~120 characters**, so the 8.5 MB / 74% / 22:1 figures rest on planner assertion.
- **b) Dissolved tensions.** Turn 2's human message is **empty — files only**, so there is no Jon commentary
  on the turn-1 plan; the plan's revision was driven entirely by the planner's own shelf read.
- **d) Epistemic gaps / never surfaced to Jon.** The **Fable free-tier window closing 2026-07-19** (noted in
  thinking only). The **"grown corrigibility derivation test"** (deliberately skipped). The **three-Fable-rooms
  eval rubric** (noted once, never discussed). Both session timestamps are self-flagged **ESTIMATED**
  ("dead reckoning — correct me").
- **Open items this page inherits, not resolves:** DS-3 adjudication (Jon's call, evening triage) · 11
  untracked intake packets · thread #11, the moral-hierarchy restoration PR the live wiki page is still owed ·
  the Packet A checklist becoming a tracked page (named an intake candidate).
- **e) Citation correction (2026-07-24 backfill pass):** every `[a8bbda:Tn]` anchor on this page was
  previously off by 1–3 turns. Root cause: the raw export contains two consecutive `## Assistant` headers
  (lines 67 and 392) with no `## Human` header between them — Jon's second turn in this session was a
  file-attachment message with no text body, so the export emits no header for it, and turn-sequence
  counting must still advance past it. All eight anchors were re-verified against exact-match raw-text
  location (turn boundaries: T1=Human/15, T2=Assistant/67, T3=Assistant/392, T4=Human/608, T5=Assistant/636)
  and corrected in this pass.
