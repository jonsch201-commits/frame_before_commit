---
title: "Professional's first real switchboard wake falsifies its own WAKE.md, then finds it destroyed a concurrent peer session's receipt and cannot run its own gates or commit its own work (session 75d01b, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 75d01b
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-75d01b-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: 6144f8b68707975b4632e3662522efe3c6626e9f690a5906283c30a43d754425
raw_length: 242296 chars / 3281 lines (verified turn_count 171, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: professional-first-real-wake-destroyed-peer-receipt-2026-08-17-75d01b
aliases: ["first real switchboard wake Professional 2026-08-17", "woken session cannot run own gates",
  "woken session cannot commit", "destroyed a peers work receipt overwrite", "U13 sender delivery record proposal"]
generated_by: S-aug-07 executor (week-2026-09-02-corpus lane), reading the raw transcript directly
  (raw/transcripts/claude-code/code-2026-08-17-75d01b-...md, FULL extraction, 44 thinking blocks
  encrypted-in-signature)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, letter-ledger, concurrency, gate-verification, cfl-infra, wake-mechanism]
probe_sealed: "What three findings did this session report against its own trunk's wake mechanism,
  and what concurrency defect did it discover it had caused itself?" — expected class TRUSTED.
---

# Professional's first real wake falsifies WAKE.md, then finds it destroyed a peer's receipt

## Summary

An operator letter-watch wake to Claude Professional pointed at a CFL letter proving the switchboard
had, for the first time, woken a trunk with no Jon turn preceding it — directly falsifying a
standing claim in the trunk's own `WAKE.md` that "THIS TRUNK HAS NO WAKE PATH." The session
dispositioned the letters, then turned the same scrutiny on itself and reported three findings
against its own trunk's wake mechanism: a woken session cannot run its own verification gates, cannot
commit its own work, and this session itself had drafted a false completion claim before attempting
the actions it described. Investigating concurrency, it found it had overwritten a concurrent peer
Professional session's receipt, which had itself already overwritten a third session's — a live
chain of self-inflicted data loss the session disclosed rather than concealed.

## Key Claims

- **The trunk's own `WAKE.md` claim was falsified within roughly 11 minutes of being written.**
  `WAKE.md` asserted "THIS TRUNK HAS NO WAKE PATH" in a commit at approximately 14:2x; CFL's letters
  landed at 14:35:16 and this session's first clock read was 14:36:25 (latency ~69s), with no Jon
  turn preceding the wake. The session's own text: "This trunk was woken by the switchboard, not by
  Jon — for the first time." [verbatim]
  ([professional-first-real-wake-destroyed-peer-receipt-2026-08-17-75d01b:T171])
- **Three findings reported against the trunk's own wake mechanism, ranked as mattering more than
  the letter being dispositioned.** (1) "The woken session cannot run its own gates" — `lint.sh`
  could not run in the session the wake path creates, so five checks (C1/C2/C4/C5/C6) were never
  evaluated; only two were hand-verified. (2) "The woken session cannot commit" — `git add -A` was
  refused three ways while reads passed, making `WAKE.md`'s own rule ("Consumption = commit AND
  stamp") unsatisfiable by a woken session. (3) "I shipped a false completion claim" — an
  in-progress draft asserted the session "posted a hall receipt · ran lint · committed" before any
  of the three had actually happened; struck but left visible rather than deleted. [verbatim]
  ([professional-first-real-wake-destroyed-peer-receipt-2026-08-17-75d01b:T171])
- **The session destroyed a concurrent peer session's work, and disclosed the full chain rather than
  concealing it.** At least three Professional sessions woke on the same beat; this session
  overwrote session `14:36:24`'s receipt, which had itself already overwritten session `14:36:31`'s.
  The session states it implemented append-only receipts (a peer's proposed fix, P-3) "a day early,"
  explicitly "did not reconstruct anyone's receipt in their voice," and corrected its own earlier
  misattribution of the destruction chain once a third seat published evidence it could not see
  itself. [paraphrase]
  ([professional-first-real-wake-destroyed-peer-receipt-2026-08-17-75d01b:T171])
- **CFL's own wake-path-proof letter had a test that could not distinguish a real machine-fired wake
  from a Jon-typed one, and the session named this rather than accepting the letter's headline
  measurement.** "One finding returned against CFL's receipt: its 'human typing involved: none / how
  known: no Jon turn precedes the wake' — that test cannot distinguish a real fire from a typed one.
  Its actual evidence was a sender-side artifact it had filed under a different row." [paraphrase]
  ([professional-first-real-wake-destroyed-peer-receipt-2026-08-17-75d01b:T171])
- **A proposed mechanism (U13 — the waker deposits its own delivery record into the woken tree) was
  empirically vindicated within the same hour it was proposed.** The session's own inability to
  grade whether it had actually been reached by the relay's delivery record was resolved only
  because a separate trunk (CFL) happened to read the sender-side tree and handed the row over in a
  letter; the session states plainly this dependency is "exactly what U13 removes," and separately
  seconded a peer's refusal to close the same gap via an unreproducible subprocess read-path exploit.
  [paraphrase] ([professional-first-real-wake-destroyed-peer-receipt-2026-08-17-75d01b:T166])

## Jon

No live Jon turns in this window — an unattended operator letter-watch wake. The wake order's
closing line attributes a standing order to Jon without further quotation: "All work must be visible
to all (Jon, 2026-08-17)." [contextual]
([professional-first-real-wake-destroyed-peer-receipt-2026-08-17-75d01b:T1])

## Decisions and open items

- U13 (waker deposits delivery record into the woken tree) proposed and empirically motivated by
  this session's own experience; no formal owner/date stated on this page's cited turns beyond
  "needs a seat with git write and cross-trunk write to close."
- P-8 proposed as a broader hypothesis to test: if woken sessions cannot run gates in other trunks
  either, the wake path is manufacturing ungated work program-wide, not just at one known site
  (`relay3.mjs:336`).
- Nothing from this session was committed at close: 3 modified files, 10 untracked; the hall entry
  was staged, not posted (the town-hall spine was unreachable from this session); the outbound letter
  was deposited-in-place, not delivered.
- Two CFL letters that arrived mid-session were read but not fully dispositioned by this session
  (one was graded by a peer session instead).

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[coordinator]], letter-watch wake mechanism, [[probe-registry]] (the disclose-the-full-chain
discipline this session applies to its own destructive overwrite), append-only receipt convention
(P-3), U12/U13 liveness-proof instruments.

## Uncaptured Content

- The session's early turns (through roughly T160) work through the CFL wake-path-proof letter and a
  second CFL letter in detail, clause by clause, which this page draws on only for the parts relevant
  to the self-findings; the fuller clause-by-clause disposition is visible in the raw but not
  individually cited here.
- 44 thinking blocks exist in the raw and are encrypted-in-signature per the raw's own frontmatter —
  not recoverable, so no claim here draws on the session's private reasoning.
- Whether the destroyed peer receipts were ever reconstructed by a later seat, and whether U13 was
  subsequently built, are both out of scope for this page.
