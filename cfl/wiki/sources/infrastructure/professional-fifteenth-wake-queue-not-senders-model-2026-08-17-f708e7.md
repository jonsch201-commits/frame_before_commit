---
title: "Professional's fifteenth wake: 'unread' meant the sender's model of the queue, not the queue — three letters dispositioned, one wrong order ID caught (session f708e7, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: f708e7
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-f708e7-you-have-new-mail-waiting-in-your-inbound-exchange.md
raw_sha256: 70c7aa60d41291fbba5c63621dc59fa2686399d406dcce5bdc8cfdc6a2664903
raw_length: 225285 chars / 3264 lines (verified turn_count 149, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: professional-fifteenth-wake-queue-not-senders-model-2026-08-17-f708e7
aliases: ["a wake's unread is the sender's model of the queue", "PRO-D2 five stamp headers",
  "wrong order ID t02001 vs t02178", "WAKE.md byte budget 6144 breach and repair",
  "cross-trunk write attribution ticketed"]
generated_by: S-aug-12 executor (RP-3/RP-4 window-to-source lane), reading the Professional-trunk
  extract directly (raw/transcripts/claude-code/code-2026-08-17-f708e7-...md, 39 thinking blocks
  encrypted-in-signature, tool calls/results summarized)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [professional-trunk, switchboard, wake-mechanism, peer-review-rule, letter-ledger, byte-budget]
---

# Professional's fifteenth wake: a wake's "unread" is the sender's model, not the queue — f708e7

## Summary

A headless wake dispatched three named letters to Professional's coordinator as "unread." The session
first surveyed its actual `exchange/inbound/` queue — 14 letters dated that day, 12 already carrying a
Professional disposition — and found two of the three the wake named had already been closed hours
earlier by other sessions, while a fourth letter the wake did not mention at all (CFL's D17 review)
was genuinely open. It dispositioned all four, caught and corrected its own previously-published wrong
order ID, flagged a possibly mis-scoped measurement rather than let it stand, found a near-miss in its
own queue-counting instrument (ticketed as PRO-D2), and closed by trimming `WAKE.md` back under its
byte budget after a routine addition pushed it over.

## Key Claims

- **"A wake's 'unread' is the sender's model of the queue, not the queue."** Two of the three letters
  the wake named as unread — Soul's compact-brief patch and the Secretary's recaps correction — had
  already been closed by earlier sessions (11, 12, and 13) hours before this wake fired; the wake's own
  model of what was outstanding was stale. [verbatim]
  ([professional-fifteenth-wake-queue-not-senders-model-2026-08-17-f708e7:T149])
- **A fourth letter the wake never named — CFL's D17 review — was the genuinely open item, alongside
  CFL's Fable-spend report.** The session dispositioned both: CFL's Fable-spend claim about
  Professional's own trunk ("Professional — none today") was independently verified (zero real
  `claude-fable-5` records that day), while its headline 273-message figure was accepted as reported
  rather than independently seconded, because the session's own 896-string count was judged "a weaker
  instrument" that only showed consistency, not confirmation. CFL's D17 ID correction was accepted and
  corrected the session's own earlier published receipt. [paraphrase]
  ([professional-fifteenth-wake-queue-not-senders-model-2026-08-17-f708e7:T149])
- **The session caught and published its own wrong order-ID attribution.** Its session-13 receipt had
  paired order `t02001` with a 15:39:32 delivery; CFL's ledger read the same row as `t02178`. The
  session's own arrival-time measurement stood; only the sender-side label had moved, and the error was
  locatable specifically because that field had been marked `[relayed]` — "exactly the column that
  failed." [paraphrase] ([professional-fifteenth-wake-queue-not-senders-model-2026-08-17-f708e7:T149])
- **A cross-trunk attribution ("Professional hardened `Switchboard.cmd`") was flagged as possibly
  mis-scoped rather than accepted or silently corrected.** The named file appears nowhere in
  Professional's own tree except inside CFL's letter, and the session cannot read the file at all — so
  its own "0 cross-trunk writes" bound may have been measured only over the woken sessions from 14:36
  and misstated as a property of the whole trunk. Ticketed for 2026-08-18: re-derive with the window
  stated, or withdraw. [paraphrase]
  ([professional-fifteenth-wake-queue-not-senders-model-2026-08-17-f708e7:T149])
- **PRO-D2 filed: the session's own queue-counting instrument silently under-counts because
  `inbound/` uses five different stamp header conventions.** A second grep verifying the session's own
  queue count returned two already-stamped letters as unstamped; the session opened the primaries
  directly rather than trusting the recount, and the original count held — but named the near-miss as a
  real defect in its own tooling rather than let a lucky catch stand as proof the tool was fine.
  [paraphrase] ([professional-fifteenth-wake-queue-not-senders-model-2026-08-17-f708e7:T149])
- **`WAKE.md` exceeded its 6,144-byte budget by two bytes after a routine addition; the session cut a
  duplicated clause rather than rephrasing, and re-measured to confirm.** Verified over budget at 6,146
  B via `Get-Item`; deleted a duplicated warning clause (not rewritten); re-measured at 6,109 B under
  budget. [contextual]
  ([professional-fifteenth-wake-queue-not-senders-model-2026-08-17-f708e7:T149])

## Jon

No Jon turns in this window — the session's single human turn is a wake-order mail-pointer dispatch,
not a Jon-authored message.

## Decisions and open items

- Cross-trunk write bound ("0 cross-trunk writes"): flagged as possibly mis-scoped, ticketed to
  re-derive with a stated measurement window or withdraw, by 2026-08-18.
- PRO-D2 (five inconsistent stamp-header conventions under-counting the queue silently): filed, no
  owner/date stated in this window beyond the filing itself.
- The one row awaiting Jon: a P-6 permission ask, default-on-silence stated as "keep staging."

## Conflicts

None with existing wiki content.

## Links

[[probe-registry]] — the session's own re-verification of its queue count with a second grep before
trusting either number is the exercise-before-reliance discipline this registry names, and its refusal
to accept its own recount at face value (opening the primaries instead) is the same "measure, don't
assume" pattern applied to itself.

## Uncaptured Content

- Turns 2–141 (the bulk of the middle — reading and cross-checking the full 14-letter queue, the
  detailed `7ca8b4a`-adjacent verification work, and the WAKE.md editing sequence) are not individually
  cited on this page; only T149 (the session's closing disposition report, which itself narrates and
  summarizes the intervening work) is cited directly.
- 39 thinking blocks exist in the raw and are encrypted-in-signature — not recoverable client-side, so
  no claim on this page draws on the session's private reasoning, only its visible tool calls and
  written text.
- This capture's relationship (if any) to the same-day Secretary-trunk switchboard sessions catalogued
  separately by this lane (f2e060, f3604e, fbf416) — all involve the same switchboard mechanism from a
  different trunk's vantage — is not established here and is out of scope for this page.
