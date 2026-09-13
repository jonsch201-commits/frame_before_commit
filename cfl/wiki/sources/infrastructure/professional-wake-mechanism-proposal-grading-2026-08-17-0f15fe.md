---
title: "Professional grades CFL's Wake Mechanism Proposal v1 row-by-row, finds a false SPECIFICATION in its own tracker, executes Jon's model-policy order early, and closes with 31 uncommitted paths (2026-08-17, 0f15fe)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 2 vs fleet 0 on authored labels"
uuid6: 0f15fe
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-0f15fe-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: f622457da20ad6c3b7b9a47a93072b57bc80b4bd1236471a322e24fa64e65e64
raw_length: 235349 chars / 2495 lines (verified turn_count 114, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe
aliases: ["Wake Mechanism Proposal v1 graded", "R6 spend budget priced", "P-5 false SPECIFICATION found",
  "model policy Opus 5 seat 2026-08-17", "31 uncommitted paths Professional"]
generated_by: S-aug-03 executor (RP-3/RP-4 window-to-page lane), reading the raw transcript directly
  (N:/claude-corpus/cfl/raw/transcripts/claude-code/code-2026-08-17-0f15fe-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
probe_sealed: "What did this session find wrong with its own trunk's published probe table (P-5), and how did the error propagate before it was caught? [expected class TRUSTED]"
tags: [switchboard, wake-mechanism, model-policy, spend-budget, cfl-infra, cross-trunk-review]
---

# Professional grades CFL's Wake Mechanism Proposal v1, finds a false SPECIFICATION, executes a Jon order early

## Summary

A switchboard-woken Professional session was told to read and disposition one letter — CFL's
`WAKE-MECHANISM-PROPOSAL v1` — but three more letters arrived mid-turn, including a Jon order on
model policy, and the session dispositioned all four before closing. It graded the wake proposal's
numbered rules (R2, R6, §7) individually rather than accepting or rejecting the whole, found and
corrected a false claim already published in its own trunk's tracker (a probe result three sessions
had copied from each other rather than independently verified), executed Jon's model-policy order
~26 hours before its deadline (measuring its own seat model, grepping its full script/hook surface
for automated model spend, and finding the trunk's real stale-tier problem sitting in a
constitution file rather than in any script), and detected a second, concurrent Professional
session writing the same tree by mtime before either collided. It closed unable to commit (31
uncommitted paths) or write cross-trunk (nine hall artifacts "deposited-in-place, not delivered"),
naming both defaults explicitly rather than treating either gap as resolved.

## Key Claims

- **CFL's proposal answers "why does nothing wake a cold trunk" as a proven claim, not an assumed
  one.** Checked against the harness tool contract itself: `CronCreate` jobs live only in the
  issuing session and are gone when it exits (`durable` has no effect); `Monitor` streams into a
  live session rather than creating one; all seven hooks fire during or around a turn. The
  proposal's conclusion: a session cannot wake itself, so any wake mechanism requires an always-on
  external process — the switchboard's shape is correct, and every named defect is in its state
  handling, not in the choice of architecture. [verbatim/paraphrase]
  ([professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T3])
- **R6 (frequency-cap wake governance) priced and partially declined.** A frequency cap is the
  right instrument only where severity per event is roughly constant; that holds for Jon's
  attention and fails for trunk wakes, whose spend varies by orders of magnitude. Option (a)
  endorsed, option (b) declined. Flagged as low-confidence on its own evidence base: n=9, one
  trunk, one day. [paraphrase] ([professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T114])
- **R2 (receiver-confirmed liveness) found insufficient without a companion rule (U13).** CFL's own
  ledger showed two delivery rows (`t02001`/`t02019`) marked DELIVERED at 14:47/14:48 with no
  Professional session having arrived in that window — under R2 as written, the system would
  declare itself healthy at two rows already known wrong.
  [paraphrase] ([professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T114])
- **A published tracker claim (P-5) was found FALSE and corrected: "Bash chained && : refused" was
  promoted to a "SPECIFICATION" from a probe that never independently ran.** The actual gate is
  per-member — the refusal message names the offending command, and unlisted commands are refused
  bare as well as chained. Three sessions had agreed because three sessions ran three copies of one
  mis-attributed probe; the primary was free to check and sat in every transcript unexamined.
  [paraphrase] ([professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T114])
- **Jon's model-policy order executed the same session, ~26 hours early.** Seat model measured as
  Opus 5 from the session's own environment block; a grep of the trunk's complete script and hook
  surface (9 files in `scripts/`, 3 in `.claude/`) found zero `--model` flags and zero automated
  model-spawn paths — reported as a measured zero with the enumeration published, not an absence
  claim. One exception reported rather than rounded away: `.claude/commands/su-compact.md:67`
  advises a `fable-mirror` consult in prose only, and this seat declined to run it while Fable was
  scarce. The trunk's real stale-tier problem was found in `WAKE.md:49` — "Models: main loop
  Fable," inside a Gates block marked not-overridable — while the session itself ran on Opus, a
  pin/running-tier mismatch the order's own grep instructions (scripts and hooks only) would have
  missed entirely. [paraphrase]
  ([professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T114])
- **A convergence spotted across two unrelated letters: R6 and the model-policy order name the same
  missing instrument.** R6 wants a token/spend budget to govern wakes; the model-policy order
  establishes that per-model usage is not measured at all — so R6 cannot be implemented until that
  ledger exists, and (measured directly) a session cannot read its own token spend, so the ledger
  must be built at harness or account level, not from inside any session.
  [paraphrase] ([professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T114])
- **A second, concurrent Professional session was detected writing the same tree by file mtimes,
  before any collision occurred**, and this session stood down from `WAKE.md`, the tracker, and the
  log, writing only session-keyed append-only artifacts instead — at the cost of a planned repair it
  had come to make, recorded as a deliberate decision rather than an oversight.
  [paraphrase] ([professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T114])
- **Session closed with two named, unresolved defaults.** 31 paths uncommitted across nine
  sessions' work (`git add` refused from a woken session by two routes); nine hall artifacts
  "deposited-in-place, not delivered" because cross-trunk write is unreachable. Both defaults are
  stated explicitly rather than left implicit, and lint did not run at all — refused chained and
  bare, nine sessions running. [verbatim/paraphrase]
  ([professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T114])

## Jon

No live Jon turn in this window. The single human-role turn (T1) is a switchboard-generated wake
order paraphrasing a standing instruction attributed to Jon ("All work must be visible to all,
Jon, 2026-08-17"), not a directly captured Jon utterance. The model-policy order acted on inside
this session arrived as a separate courier letter (`secretary-courier-JON-ORDER-model-policy-...`)
whose own text is not reproduced verbatim on this page — see the raw at
`professional-wake-mechanism-proposal-grading-2026-08-17-0f15fe:T110`-area turns for its content.

## Conflicts

None with existing wiki content.

## Decisions and open items

- R6 (frequency-cap wake budget): option (a) endorsed, (b) declined, pending an instrument (spend
  ledger) that does not yet exist.
- R2 needs a companion rule (U13) before it is safe to treat receiver-confirmed liveness as
  sufficient on its own.
- P-5's tracker claim on chained-Bash refusal corrected from a false "SPECIFICATION" to the actual
  per-member gate behavior.
- Model-policy order executed and reported; `WAKE.md:49`'s stale "main loop Fable" pin vs. this
  session's actual Opus assignment ticketed for Professional, 2026-08-18.
- Two items left for Jon to unblock explicitly, each with a stated default if he says nothing:
  the 31 uncommitted paths (default: stays on the tree, carried by the next session with git
  write), and cross-trunk write access for the hall spine (default: stays readable in-tree only,
  not delivered).

## Links

[[max-plan-fl-budget]] — the standing instruction that compute should be spent liberally on FL
work while review-minutes stay scarce is the backdrop this session's R6/spend-ledger convergence
argues against treating token spend as unmeasured indefinitely.
[[live-session-liveness-and-untracked-state]] — the same class of risk this session names directly
in its own close: untracked/uncommitted state left in a working tree, and a second concurrent
session writing the same tree undetected until mtimes were checked.

## Entities & Concepts

Switchboard wake mechanism, CFL's Wake-Mechanism-Proposal v1 (R2/R6/§7), P-5 tracker claim,
model-policy order, per-model spend ledger, hall spine delivery.

## Uncaptured Content

- Turns 4–108 (the bulk of the session's letter-reading, grading, and drafting work across the
  wake-mechanism proposal and the model-policy order) are not individually cited on this page;
  only the opening proposal letter (T3) and the closing summary (T114) are drawn on directly.
- 34 thinking blocks exist in the raw and are encrypted-in-signature — not recoverable, so no claim
  here draws on the session's private reasoning, only its visible tool calls and final message.
- The exact text of the Jon model-policy order letter itself is not quoted verbatim on this page;
  only this session's report of executing it is captured.
