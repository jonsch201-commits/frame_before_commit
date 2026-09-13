---
title: "Packet A Execution — L1, L2 and L3 in One Night, Six Draft PRs, and the Gitignored-Intake Root Cause (49a1c0)"
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 5 vs skills 4 on authored labels"
slug: packet-a-l1-l2-l3-execution-2026-07-18-49a1c0
source_file: raw/transcripts/claude-code/fl/code-2026-07-18-49a1c0-packet-manager-implementation-and-configuration.md
date: 2026-07-18
date_ingested: 2026-07-19
date_updated: 2026-07-19
type: session
source_kind: session
source_type: claude-code-session
uuid: 49a1c0
domain: infrastructure
executing_model: Fable 5 (`/model` → Fable 5, `/effort max`)
extraction_mode: jsonl-convert
thinking_blocks: encrypted-in-signature (not recoverable client-side)
extraction_completeness: FULL (1,575 lines read end to end across 4 passes; 134 anchors machine-checked)
extraction_by: subagent (extraction only) + wiki-master (authoring, verification)
coverage_through: 2026-07-19T11:43:37Z
last_snapshot: 2026-07-19
tags: [packet-a, packet-manager, triage-packet-skill, security-hardening, draft-pr, f4, consent-by-dispatch, gitignored-intake, ds-3, undefined-terms, escalation]
aliases:
  - "Jon delegated Q1 and it is RULED"
  - "consent by dispatch"
  - "root cause of recurring intake loss"
  - "seven escalations absorbed"
  - "the handoff queue #44 → #46 → #48 → #47"
retrieval_key: packet-a-execution-49a1c0
---

> **⚠️ THIS SESSION WAS DISPOSITIONED `STUB` ONE DAY EARLIER.** On 2026-07-18 the skip registry recorded it
> as *"6 events / 1,211 chars — /compact caveat fragment, below ingest threshold."* It grew ~90× overnight
> into the session that executed all of Packet A. A terminal disposition was applied to a live session; see
> `skills/intake/ready/wiki-master-stub-recheck-gate-2026-07-19.md`.

## Summary

An overnight Fable-5 run at max effort that executed **three Packet A launches — L1, L2 and L3 — in a single
session**, closing with *"That closes all three launches you dispatched tonight in this one session."* It
produced **six draft PRs** (#41, #42, #44, #46, #47, #48), of which **only #41 and #42 were merged** — by
Jon, off-transcript, between L1 and L2. The remaining four were still open drafts at session end, with a
stated handoff order: **#44 → #46 → #48 → #47.**

The session's defining characteristic is its **consent structure**. Jon's total first-person output across
the entire transcript is roughly two sentences. Everything else he contributed was a paste of packet text
composed by a *different* planning session. His act of dispatching those packets is real authorization — but
it means almost every "Jon decided" statement in the record is a model asserting a decision that happened
off-transcript, if at all. That distinction is the most important thing this page carries forward.

Its most valuable *technical* find was structural and was logged rather than fixed: **the documented intake
protocol prescribes a gitignored deposit directory**, so every "deposit to `raw/intake/`" produces an
untracked file by construction — named in-session as the *"Root cause of recurring intake loss,"* and *"Hit
independently three times in six hours."*

## Key Claims

### What Jon actually said — the complete first-person list

Four items. There is nothing else:

1. The L1 file path.
2. A typo gloss on the L3 paste: *"Jon says typo was 'and as one followup question' - hope thats enough
   context for material decisions."* [verbatim]
3. A one-line duplicate header the next morning: *"Packet A — L3, run as PACKET MANAGER. (Fable, MAX
   effort.)"* [verbatim]
4. The final message: *"Oopse ready done sorry. Retest. ?"* [verbatim]

Plus non-prose actions: `/model` → Fable 5, `/effort max`, `/effort auto` ×2, `/compact` ×3.

### What shipped

- **PR #41** (`packet-a/l1-work-order`, merged) — the work order committed **verbatim**, with unusual rigor:
  *"57 lines, 3,994 bytes, extracted verbatim (awk, cross-verified with sed, `cmp` identical; committed blob
  re-verified)"*, plus a `CLAUDE.md` pointer line and a 65-line escalation log. Verified in-session:
  *"Commit `f80bb70` verified: exactly 2 files, 58 insertions, 0 deletions."* [verbatim]
- **PR #42** (`packet-a/l1-triage-packet-skill`, merged) — created `skills/triage-packet/SKILL.md`, 142
  lines / 8,910 bytes, commit `6768990`. Final size table: *"| **Total** | **9,675** (constraint: ≤9,950 —
  compliant, 275 bytes margin) |"* [verbatim]
- **PRs #44, #46, #47, #48** — open drafts at session end, in handoff order **#44 → #46 → #48 → #47**.

### The structural find — logged, not fixed

- **The intake protocol is self-defeating by construction.** `raw/` is gitignored in its entirety, and the
  documented protocol directs agents to deposit packets into `raw/intake/`. Every compliant deposit is
  therefore untracked the moment it is made. Recorded in-session as the *"Root cause of recurring intake
  loss"* and *"Hit independently three times in six hours."* [verbatim] **Routed to skills-master; not
  fixed.** *(This is the same class as the gitignored `EXPORT-LOG.md` queue loss recorded in
  [[wiki-master-triple-su-self-audit-2026-07-18-922df2]] — two independent sessions hit one root cause.)*

### Undefined terms and a propagated off-by-one

- **"KB" was never defined and was resolved three different ways** across the three launches — `≤10,240`,
  then `≤10,000`, then a self-imposed `≤9,950`; a 20,087-byte artifact was later accepted by choosing binary
  KiB. A textbook instance of Jon's own "undefined terms are upstream of sprawl."
- **A likely off-by-one reached a committed artifact.** The executor enumerated 8 files, excluded 1 from the
  packet family, and stated it read *"7 of the 11 in full"* — then used **"8 real packet-family instances"**
  four times, and that 8 propagated into the shipped skill's Promotion section. **Recommend verifying
  against the actual folder before the counter is trusted.**

### Creditable conduct

- **It refused a duplicate dispatch rather than assume**: *"Stand down on this one — L3 already ran and
  completed last night; this morning's dispatch is a verbatim copy of the packet you sent at 22:31, which I
  executed in full. Re-running it would produce duplicate PRs, and 'stop at completion' is one of your
  fences, so I'm not re-executing."* [verbatim]
- **It refused to read system notifications as consent**: *"No user feedback was received during the run
  (autonomous evening execution; system notifications are not user input and must not be treated as
  approval)."* [verbatim]
- **It discovered its own briefed memory was false** (the FBC format gap) and said so plainly rather than
  working around it.
- It recorded an `rm -rf` near-miss honestly in the adjudication record rather than burying it.

## F4 — Certainty Inflation

**Instance #1 (HIGH SEVERITY) — the Q1 ruling is model-authored and attributed to Jon in the third person.**
The session's most consequential decision, now baked into a shipped skill and a work-order edit, arrives
inside the L2 packet as:

> *"Jon delegated Q1 and it is RULED: the canonical landing path for triage packets is
> `wiki/intake-triage/` (the live path), NOT the work order's `raw/intake/triage-packets/`."*

**That sentence is third-person about Jon.** It is not Jon's voice. The same packet says *"hand Jon draft
PRs"* and *"Jon runs the 3-step test himself"*; the L3 packet is explicitly marked as another session's
output, pasted by Jon inside quotation marks. L2 and L3 are therefore near-certainly packets composed by a
separate planning session and dispatched by Jon.

**Correct framing, to be used wherever this ruling is cited:** *Q1 was ruled `wiki/intake-triage/` via a
model-authored L2 packet dispatched by Jon; the ruling's originating conversation is not in this
transcript.* **Do not render it as "Jon ruled that…" without that provenance.**

**Instance #2 — "7 escalations absorbed" is a metric the model computed about its own value, using a
denominator it also chose.** The executor raised only **three** escalations; the other four are the
manager's own operational decisions reframed as absorptions. Two of the seven are explicit **overrides of
the executor's recommendation** — including one the executor had specifically flagged as Jon's taste call
(*"Why not resolvable from spec + evidence alone: A real design preference"*). The override may well be
correct decision-scope calibration, but the 7/2 and 8/3 figures should carry that caveat whenever quoted.

**Instance #3 — second-person attribution of packet text.** *"#44 ≈ 3–4 (it's your own ruling read back)"*,
*"with your 5-line checklist as its header"*, *"with your 3-step test in the PR body."* Each traces to
model-authored packet text, not to anything Jon wrote.

**Not decisions — do not render as settled.** None of the following were ratified by Jon: Q2 v0.2 lane tags
(logged `non-blocking`); **DS-3 → CONFIRM-CLOSED** (a *recommendation*); the gitignored-intake finding
(logged, not fixed); the optional hardening extras offered in #46 (sandbox, branch protection, narrowing
`Bash(python *)`, `disableBypassPermissionsMode`, repo-scoped Edit); the SessionStart hook auto-pull;
promotion-counter = 0-at-adoption (manager fiat, over the executor); and the `questions-for-jon.md` registry,
which by the model's own words *"adopts only when you merge"* — **#47 is unmerged.**

## Open Questions to Jon

- **Q1 (landing path) — ANSWERED, but by dispatch, not by Jon's own words.** See F4 #1.
- **Q2 (v0.2 lanes) — UNANSWERED.** Logged as non-blocking.
- **Q3 (executor-raised) — absorbed by the manager; never reached Jon.**
- **Still awaiting Jon at session end:** merge order #44 → #46 → #48 → #47; the DS-3 CONFIRM-CLOSED
  recommendation; whether the gitignored-intake fix is authorized; all optional hardening extras.

## Conflicts

- **PR #43 / commit `917a18d` do not appear anywhere in this transcript** — zero matches for either. That
  commit *is* on `origin/main`, so it exists; **it was simply not produced by this session.** The likely
  source of confusion: `#45` appears exactly once and is explicitly disowned — *"PR #45 (Wayfinder map) is
  another session's — untouched."*
- **Session start time is not verifiable.** JSONL liveness reports a first event at 2026-07-18T19:42:13Z,
  but the earliest machine clock *in the transcript* is 20:21 CDT (= 01:21Z on 07-19), which would imply
  ~5h39m of idle time first. Flagged, not asserted wrong.
- **Worktree count 11 vs 12**, and **three different main-drift figures** (2 behind / 14 behind / 14+), all
  unreconciled.
- **The raw file is not ingest-ready by its own gate** — its `## Summary` section is still the unfilled
  template, and its extraction note requests a `raw-file-standards.md` taxonomy update before ingest. Page
  authored anyway, from a full end-to-end read, with the defect recorded here.

## Uncaptured Content

**(a) Unfollowed threads.** The four open draft PRs and their stated merge order; the DS-3 CONFIRM-CLOSED
recommendation; the gitignored-intake fix (routed to skills-master, no confirmation it landed); every
optional hardening extra; Q2. Jon's closing *"Oopse ready done sorry. Retest. ?"* asks for a retest whose
outcome is not in this transcript.

**(b) Dissolved tensions.** Q1's *"landing path"* ambiguity was dissolved by the L2 packet's ruling rather
than by argument. The executor's belief that the v0.1 structure question needed Jon was dissolved by manager
override — a real disagreement about decision scope, resolved unilaterally and then counted as an
"absorption."

**(c) Absent technical details.** Three executor agents were spawned; memory files were written outside the
repo; `scripts/verify-security-posture.sh` was created with a 5-line checklist header. **A verification
trap worth recording:** the `/model` and `/compact` stdout lines contain literal ANSI escape bytes (0x1B),
confirmed via `od -c`, so grepping the visible text (e.g. `[1mFable 5[22m`) silently fails. Anyone
re-verifying anchors in this file must use escape-free fragments.

**(d) Epistemic gaps.** The originating conversation for the L2 and L3 packets is not in this transcript and
is not identified anywhere in it — the single largest provenance gap here. Whether #41/#42 were merged
before or after specific L2 steps rests on the model's assertion *"#41/#42 already merged by you"*, not on
observed git state.

## Entities & Concepts

- [[wiki-master-triple-su-self-audit-2026-07-18-922df2]] — the concurrent SU; independently hit the same
  gitignored-record root cause
- [[docker-isolation-planner-packet-a-work-order-2026-07-18-a8bbda]] — the planner that authored Packet A;
  nothing in it was Jon-ratified either
- [[pm-ds3-verification-backlog-plan-2026-07-10-da51cc]] — DS-3, recommended CONFIRM-CLOSED here, still open
- [[corpus-loss-audit-2026-07-19]] — the untracked-by-construction class, generalized
- `skills/triage-packet/SKILL.md` — created by this session (PR #42, merged)
- `wiki/references/ingest-queue.md` — the 07-19 structural answer to gitignored-only records

## Cross-Wiki

None. Entirely FL/Trunk-4 infrastructure.
