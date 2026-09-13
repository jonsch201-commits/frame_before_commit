---
title: "Professional letter-watch wake verifies the relay path against its own first turn, and catches WAKE.md self-grading itself wrong (session bd850a, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 3 vs fleet 0 on authored labels"
uuid6: bd850a
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-bd850a-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: e6dfc4f154e61609afc53dbc90d6e95fe698653da9ea0d9da58e8ecc28c2b243
raw_length: 199073 chars / 3004 lines (verified turn_count 167, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: professional-letter-watch-relay-wake-verified-2026-08-17-bd850a
aliases: ["grade your wake from your first turn not your wake file", "recaps mechanism unreachable not refused", "selftest false-pass path bd850a", "relay wake latency table 2026-08-17"]
generated_by: S-aug-10 executor (week-map RP-3/RP-4 synthesis lane), reading the full-visible extract
  (raw/transcripts/claude-code/code-2026-08-17-bd850a-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, relay, letter-ledger, recaps, self-catch, cfl-infra]
---

# Professional letter-watch wake verifies the relay against its own first turn, not its own file

## Summary

A headless "switchboard wake (operator, letter watch)" seat, running as Professional, was
directed to read one new inbound letter, act on or ticket it, stamp the letter ledger, and post a
receipt to the town hall spine. It read the letter (a Secretary courier relaying a new
`RECAPS-ALL-TRUNKS.md` append-only mechanism plus two dispositions), measured its own trunk's
wake-relay latency against the letter's claimed delivery timestamps (two relays, 126.7s and 35.0s
apart), and found that `WAKE.md`'s own published "0 of 10 by a relay order" line was wrong — it
had been written by the very session that was itself the first relay wake, and the next relay wake
missed the error too. It also ran six probes on the new recaps mechanism (all write paths
hard-blocked or unapprovable) and continued unblocked lint work. `git add -A` was refused for a
13th consecutive session; 42 paths are uncommitted.

## Key Claims

- **The relay wake path fires, and the seat verified it against its own first-turn timestamps
  rather than its own prose.** Two relay-delivered wakes: Secretary claimed `t02001` delivered
  15:39:32, this trunk's own session `9ff05b94` first turn measured 15:41:38.701 CDT (126.7s
  latency); `t02202` delivered 15:47:39, session `f13122c6` first turn measured 15:48:13.981 CDT
  (35.0s latency). The two relay wakes carry a distinguishable first-turn template from the
  letter-watch wake, so a receiver can discriminate delivery mechanism without reading the
  sender's tree. [verbatim] ([professional-letter-watch-relay-wake-verified-2026-08-17-bd850a:T167])
- **`WAKE.md:4`'s own claim was wrong, and it was written by the defect it describes.**
  `WAKE.md` said "0 of 10 by a relay order" — written by the session that was itself the first
  relay wake, and the second relay wake missed the same error. Rule recorded: "grade your wake
  from your first turn, not from your wake file." [verbatim]
  ([professional-letter-watch-relay-wake-verified-2026-08-17-bd850a:T167])
- **The new recaps mechanism is unreachable from this seat, not refused as a policy matter.** Six
  probes — Bash `ls`, PowerShell `Get-ChildItem`, PowerShell `Add-Content`, Bash `>>` all
  hard-blocked; `Read`/`Glob` prompt with no approver present; `Write` deliberately not attempted
  because it truncates an append-only file the seat cannot read back, which would have destroyed
  the four recaps Jon had relayed by hand. This also falsified a prior session's published claim
  that "the block is BASH-ONLY" — PowerShell hard-blocks cross-trunk too. [paraphrase]
  ([professional-letter-watch-relay-wake-verified-2026-08-17-bd850a:T167])
- **A selftest's positive controls can pass forever after their first real pass, because they grep
  an append-only shared log with no per-run marker.** `switchboard-operator.sh`'s selftest greps
  the entire operator log for matching lines from any prior run; a regression that stopped logging
  those lines would still pass. The meta-parse control is the only one that does not read the
  shared log, and it was the only control observed to fail when its subject actually broke.
  Proposed remedy (marked OPINION in-session): stamp a per-run nonce into each control line.
  [paraphrase] ([professional-letter-watch-relay-wake-verified-2026-08-17-bd850a:T167])
- **`git add -A` refused for the 13th consecutive session; 42 uncommitted paths, hall receipt
  undelivered.** One item is named as awaiting Jon (a permission ask, P-6) with a stated default
  on silence: keep staging, stop nothing. [verbatim]
  ([professional-letter-watch-relay-wake-verified-2026-08-17-bd850a:T167])

## Conflicts

None with existing wiki content.

## Jon

No Jon turns in this window — the sole Human turn (T1) is a scripted letter-watch wake directive
from the switchboard operator, not Jon typing live. It closes by re-quoting his standing order
verbatim: "All work must be visible to all (Jon, 2026-08-17)." [contextual]
([professional-letter-watch-relay-wake-verified-2026-08-17-bd850a:T1])

## Decisions and open items

- The Secretary's courier letter (recaps mechanism, two dispositions) — read, acted on, stamped,
  receipted (closed, this session).
- `WAKE.md:4`'s "0 of 10" claim — struck; rule recorded to grade wake mechanism from first-turn
  timestamps, not from the wake file's own prose.
- Recaps append — staged at `exchange/outbox/RECAPS-ROW-professional-2026-08-17-1627.md`, owner
  this seat, 2026-08-18 (open — every direct write path unreachable this session).
- Lint check P-7 (grade `exchange/wake-receipts/`) — rewritten with three new selftest canaries,
  but unrun: `bash scripts/lint.sh`, `--selftest`, and even `bash -n` were all refused this
  session; the next session with execute rights must run `--selftest` before trusting the verdict.
- P-3 reopened: 14 sessions today, 10 receipts, both relay wakes among the four that wrote none.
- `git add -A` denial (13th consecutive session, 42 paths) — open; P-6 permission ask awaits Jon,
  default on silence is keep staging, stop nothing.

## Entities & Concepts

[[derive-dont-record]] (the `WAKE.md`-grades-itself-wrong finding is the same class as a
diverging record), [[verify-controls-before-declaring-loss]] (the selftest-false-pass finding
names the identical failure mode — a control that cannot fail once it has passed once), switchboard
relay, `RECAPS-ALL-TRUNKS.md`, letter ledger.

## Uncaptured Content

- **165 of 167 turns not individually surveyed for this page.** This page draws on the opening
  directive (T1) and the closing findings summary (T167, which recounts the intervening
  investigation); the tool calls in between (reading the letter, probing the recaps path six ways,
  the lint rewrite) are not separately cited.
