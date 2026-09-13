---
title: "Secretary trunk: five compounding switchboard defects found in ten minutes after Jon's 'Soul never read anything' complaint (session f3604e, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: f3604e
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-f3604e-run-reading-beat-and-write-brief.md
raw_sha256: 437c08ce7220ac0ddaf703e4bb0af50870bef92bd8b4de95779496ab1c66a3ee
raw_length: 103596 chars / 1355 lines (verified turn_count 49, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: switchboard-relay-single-target-defect-secretary-2026-08-17-f3604e
aliases: ["Soul never read anything except at my word", "relay allowMultiTarget false single target",
  "operator v2 five defects switchboard", "checkpoint critic branch fork 14:2x"]
generated_by: S-aug-12 executor (RP-3/RP-4 window-to-source lane), reading the Secretary-trunk
  extract directly (raw/transcripts/claude-code/code-2026-08-17-f3604e-...md, 17 thinking blocks
  encrypted-in-signature, 1 compaction boundary, tool calls/results summarized)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, secretary, relay, operator, wake-mechanism, checkpoint-critic]
---

# Secretary trunk: five compounding switchboard defects found in ten minutes — session f3604e

## Summary

This is one of at least three separately-captured continuations of the Secretary trunk's long
2026-08-17 "switchboard" session, sharing an identical machine-written compaction summary of the
session's earlier hours with sibling captures catalogued separately by this same lane (f2e060,
fbf416) — the relationship among them is not established by this page (see Uncaptured Content).
This capture's own new material begins right after a `/compact`: Jon opened with "Switchboard is not
working as intended. Soul never read anything except at my word. I bet if I asked the others, they
would say the same thing." The session investigated rather than assumed, and within roughly ten
minutes found and fixed five compounding defects — the relay watching only one trunk by
configuration, an operator that discarded a wake's real letter pointers because the wake's header
looked like known noise, a startup catch-up gap, a drifted relay process still running, and a
restart path that relaunched the drifted version. The capture ends with a Stop-hook "checkpoint
critic branch" fork raising three findings against the fix.

## Key Claims

- **The relay was configured to watch only Personal — CFL, Professional, and XC were never in scope,
  confirming Jon's suspicion as a structural fact rather than a guess.** `config.json` had
  `allowMultiTarget: false` with one target; the ledger showed 1,967 ticks, all against Personal, zero
  against CFL or Professional. The session's own framing: "Your 'I bet the others would say the same'
  isn't a bet — it's structural." [verbatim]
  ([switchboard-relay-single-target-defect-secretary-2026-08-17-f3604e:T49])
- **The operator judged a wake's noise-header and discarded two real letters riding inside it.** The
  one wake that had fired after operator launch (t01938, 13:38) carried a known-noise `quest_stall`
  header, so it was free-HELD — but its `pending_pointers` held two real letters for Soul (an EARS
  review and a herald-coordinates-XC ruling courier), which is why "Soul read nothing except at your
  word." [paraphrase]
  ([switchboard-relay-single-target-defect-secretary-2026-08-17-f3604e:T49])
- **Three further compounding defects, named together as the full causal chain.** Wakes from before
  the operator's 13:31 start were never re-considered at startup, including a 12:18 NEW_MAIL wake for
  Jon's own ruling courier; the actually-running relay process was a drifted v0 build (confirmed by
  argv matching pid 27620, matching a separate finding attributed to "Herald"); and the session's own
  restart path had been relaunching that same drifted v0, making the drift self-perpetuating.
  [paraphrase] ([switchboard-relay-single-target-defect-secretary-2026-08-17-f3604e:T49])
- **Operator v2 was built and selftested with a positive control per defect, but final launch required
  a Jon-run command the session could not execute itself.** Fixes: noise-hold now requires zero
  pending pointers; a startup catch-up pass re-judges recent wakes; the watch list explicitly includes
  CFL and Professional `exchange/inbound/`; an idle trunk gets a deterministic continuation wake (max 1
  per 3h, zero judgment tokens); relay3 pinned everywhere. The classifier blocked the session from
  killing the old processes itself, so it handed Jon one literal command
  (`! bash ".../relaunch-switchboard-v2.sh"`) to run. [paraphrase]
  ([switchboard-relay-single-target-defect-secretary-2026-08-17-f3604e:T49])
- **A Stop-hook "checkpoint critic branch" fork raised three findings against the fix, each required
  to cite a checkable receipt.** F1: the closing claim that the catch-up pass "will judge-and-deliver
  Soul's held mail within seconds" relies on a DELIVER path that had never fired end-to-end (zero
  "DELIVER ->" lines in the operator log at fork time) — an estimate resting on an unexercised
  instrument. F2: the catch-up fix's own `-mmin -90` window silently drops wakes older than 90
  minutes at launch time, with at least three named wakes falling outside it and no record of what
  they pointed at being dropped. F3: the letter-watch loop's `find -newer marker` then `touch marker`
  ordering can miss a letter whose mtime lands in between the two calls — the same race class the
  session had just fixed elsewhere under its own rule "a visible duplicate beats a silent loss."
  [verbatim, three findings quoted with their own receipts]
  ([switchboard-relay-single-target-defect-secretary-2026-08-17-f3604e:T49])

## Jon

- `[switchboard-relay-single-target-defect-secretary-2026-08-17-f3604e:T6]` — "Switchboard is not
  working as intended. Soul never read anything except at my word. I bet if I asked the others, they
  would say the same thing." (verbatim)

## Decisions and open items

- F1 (unexercised DELIVER path claimed as imminent) — critic finding, no disposition recorded within
  this capture's visible window.
- F2 (90-minute catch-up window silently drops older wakes; named wakes' contents unrecovered) — OPEN,
  no owner named in this window.
- F3 (find-then-touch race in the letter-watch loop) — OPEN, no owner named in this window.
- The one Jon-only item: run `relaunch-switchboard-v2.sh` to kill the drifted v0 processes and launch
  relay3 + operator v2 — status after this capture's window not established here.

## Conflicts

None with existing wiki content.

## Links

[[probe-registry]] — "exercise-before-reliance" and the pre-stated positive-control discipline this
session names explicitly for operator v2's selftest, and which F1 finds was skipped for the
end-to-end DELIVER claim.

## Uncaptured Content

- **This capture shares an identical machine-written compaction summary with at least two sibling
  captures dated the same day** (catalogued separately by this same lane, f2e060 and fbf416), each
  ending in its own distinct "checkpoint critic branch" Stop-hook fork at a different timestamp (this
  one ~14:2x). Whether these are literal forks of one underlying session, independent resumes sharing
  inherited context, or some other relationship is not established from this raw alone.
- Turns 1–5 (the pre-compaction summary itself and the immediate post-compaction acknowledgment) are
  not individually cited on this page; only the post-"Switchboard is not working" exchange (T6
  onward) is drawn on.
- 17 thinking blocks exist in the raw and are encrypted-in-signature — not recoverable client-side, so
  no claim on this page draws on the session's private reasoning, only its visible tool calls and
  written text.
