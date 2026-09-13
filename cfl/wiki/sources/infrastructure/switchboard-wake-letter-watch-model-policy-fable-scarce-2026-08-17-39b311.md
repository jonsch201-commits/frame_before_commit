---
title: "Switchboard letter-watch wake (Professional) — JON-ORDER model-policy letter answered: WAKE.md's Fable gate was false all day (session 39b311, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 39b311
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-39b311-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: fbd2baf6ce9de7ffac81dde84c39186aae5b6ceb7d11c6f96accc96253411669
raw_length: 135524 chars / 2001 lines (verified turn_count 102, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: switchboard-wake-letter-watch-model-policy-fable-scarce-2026-08-17-39b311
aliases: ["JON-ORDER model policy fable scarce letter", "WAKE.md Fable gate false 2026-08-17",
  "13 of 13 sessions ran Opus", "P-6 probe glob grep no prompt"]
generated_by: S-aug-04 synthesis lane executor, reading the raw transcript directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, wake-operator, letter-watch, professional-trunk, model-policy, self-measurement]

probe_sealed: "What did this session find when it checked its own trunk's WAKE.md 'main loop Fable'
  gate against measured session data, and what did it do about it? Expected class TRUSTED — the
  finding and the correction are both stated verbatim in Key Claims."
---

# Switchboard letter-watch wake (Professional) — model-policy letter answered, own Fable gate false (39b311)

## Summary

A letter-watch wake fired a Professional session to answer a `JON-ORDER-model-policy-fable-scarce-
check-your-model-flags` letter. The session enumerated its own trunk's scripts/hooks for `--model`
usage (found zero, confirmed the trunk runs no automated inference path), then measured its own
current model against `WAKE.md`'s own "not overridable" gate ("Models: main loop Fable") and found
the gate false: 13 of 13 sessions dated 08-17 in this project had run Opus, across 1,240 assistant
turns, with zero Fable sessions that day (Fable was real in this trunk's history but only before
08-17). The session corrected the gate in place, forwarded a spawn-inheritance question to the
Secretary rather than answering it from an unreachable tree, and unblocked the trunk's top resume
item (P-6, a sibling-read capability probe) with 16 direct measured calls.

## Key Claims

- **`--model` enumeration: zero found, with the population stated.** Across 334 executable/config/
  markdown files, no `--model` flag anywhere; eight `scripts/*.sh` never invoke the `claude` CLI at
  all; the launcher passes only `--add-dir`; neither hook makes an inference call; no cron, no
  daemon. Qualifier carried: `~/.claude/settings.json` was read-refused to this seat, so a
  machine-level default is UNKNOWN from here, not asserted absent. [paraphrase]
  ([switchboard-wake-letter-watch-model-policy-fable-scarce-2026-08-17-39b311:T102])
- **The trunk's own model gate was measured false, against itself, and corrected in place.**
  `WAKE.md`'s gate read "Models: main loop Fable." Measured across this project's session JSONLs:
  13 of 13 sessions dated 08-17 ran Opus (1,240 assistant turns), zero ran Fable; Fable's 994
  historical records across 7 files all predate that day. The session corrected `WAKE.md:49` in
  place rather than leaving the false gate standing. [verbatim of self-description]
  ([switchboard-wake-letter-watch-model-policy-fable-scarce-2026-08-17-39b311:T102])
- **The operator's spawn cost was named as a question the session's own tree could not answer.**
  The 15:31:30 letter woke three concurrent Professional sessions off one arrival — up to three
  full-context Opus sessions per single letter, on a tier Jon had just reserved to mirror usage.
  Rather than answer, the session ticketed the question to the Secretary (08-18: "what model do
  operator-spawned sessions inherit, and who set it?") and declined to set a room-wide Fable spend
  policy itself, reasoning it should not own a cross-trunk budget from a seat that cannot commit,
  deposit, or reach the hall. [paraphrase]
  ([switchboard-wake-letter-watch-model-policy-fable-scarce-2026-08-17-39b311:T102])
- **P-6 (sibling-read capability) unblocked with 16 direct probes, correcting its own prior framing.**
  Found that only `Bash` hard-blocks on a sibling tree; `Glob` and `Grep` return a permission prompt
  rather than a denial, and — more consequentially — `Glob`/`Grep` reach `~/.claude/projects/` with
  no prompt at all, which the session used to obtain the day's own model-usage measurement. Ten prior
  sessions had reported this trunk could not read outside its own tree; the session states that claim
  is false as a general statement. [paraphrase]
  ([switchboard-wake-letter-watch-model-policy-fable-scarce-2026-08-17-39b311:T102])
- **A concurrent session stamped the same letter 90 seconds later and caught a miss.** Both stamps
  survived (append-mode held). The concurrent stamp found the session's own search pattern had missed
  `.claude/commands/su-compact.md:67`'s `fable-mirror` recommendation, because the pattern searched
  only for `--model`/`claude-<tier>` strings; the session verified the miss independently and adopted
  the peer's disposition. [paraphrase]
  ([switchboard-wake-letter-watch-model-policy-fable-scarce-2026-08-17-39b311:T102])

## Conflicts

None with existing wiki content.

## Jon

No live Jon turn in this session. The dispatching wake order's own text attributes a standing
instruction to him without further sourcing: "All work must be visible to all (Jon, 2026-08-17)."
[contextual] ([switchboard-wake-letter-watch-model-policy-fable-scarce-2026-08-17-39b311:T1]) — a
pointer to a primary elsewhere, not a verified quote from this session. Note also: the reserved
tier described in this session's spawn-cost finding ("a tier Jon just reserved to mirror usage") is
this session's paraphrase of a ruling made elsewhere, not a quote captured in this window.

## Decisions and open items

- Corrected `WAKE.md:49` in place (Fable gate → measured reality).
- Ticketed to Secretary, 08-18: what model do operator-spawned sessions inherit, and who set it.
- Declined to set a cross-trunk Fable spend policy from this seat, with reason stated.
- Ticketed (not executed, to avoid a lost update while a peer was concurrently rewriting the same
  block): strike `Glob` from the P-6 hard-block line in `WAKE.md`.
- Both the hall receipt and a cross-trunk write remain unreachable from this seat, tenth consecutive
  session to report that state.

## Links

- [[max-plan-fl-budget]] — this session's spawn-cost finding is a concrete instance of the
  spend-discipline question that page names.
- [[coordinator]] — the spawn-inheritance and self-measurement pattern here concerns how a
  coordinator session's own model gate can silently diverge from measured behavior.
