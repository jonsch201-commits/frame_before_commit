---
title: "Professional-trunk adversarial peer review of Jon's launch plate — 8 findings, headless seat (CFL session e3a556, 2026-08-21)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: e3a556
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-21-e3a556-you-are-a-fresh-professional-trunk-seat-performing.md
raw_sha256: 147ae7c432410a24bf2ed6e9aec1937eb5e8ccd3c0254d05f59deb8ed1c93b87
raw_length: 93157 chars / 1134 lines (verified turn_count 40, turn_index.py, header_style md)
date: 2026-08-21
retrieval_key: professional-seat-adversarial-review-of-jons-plate-2026-08-21-e3a556
aliases: ["Professional adversarial peer review 2026-08-21", "launch-cfl.bat wake-skill missing finding",
  "CFL launcher letter not found", "00-INDEX.md open-rows drift finding", "e3a556 plate review"]
probe_sealed: "What was finding 1 (BLOCKS-LAUNCH) in this Professional-trunk adversarial review, and how did the seat verify it? A cold reader should answer: the documented CFL launch procedure fails at step two because CFL's skills/ directory had no /wake skill (the one that existed was guarded [CLAUDE PERSONAL ONLY]), CFL's launch-cfl.bat still instructs typing /wake, and a grep of Personal's entire exchange/ tree for the claimed disposing letter ('CFL Coordinator.ps1') returned zero files."
generated_by: S-aug-01 executor (RP-3/RP-4 window-to-page lane), reading the FULL visible extraction
  directly (raw/transcripts/claude-code/code-2026-08-21-e3a556-you-are-a-fresh-professional-trunk-seat-performing.md,
  0 compaction boundaries)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [adversarial-review, launch-procedure, professional-trunk, headless-seat, cfl-infra, decision-queue-index]
supersedes: [professional-adversarial-plate-review-launch-defects-2026-08-21-e3a556]
---

# Professional-trunk adversarial peer review of Jon's launch plate — 8 findings, headless seat

## Summary

A write-denied (headless), fresh Professional-trunk seat was dispatched under Jon's order
("Have professional and CFL each perform an adversarial peer review of what is on my plate before
I launch the fresh cfl fable coordinator to go from here with my first message from it") to
adversarially review two things: what Personal's `00-INDEX.md` framed as genuinely on Jon's plate,
and whether the documented CFL launch procedure actually works. The seat read the reviewed
documents (Personal's `00-INDEX.md`, `TEACH-ME-fable-day-2026-08-21.md`, the launcher failure-class
page) and its own trunk's tracker, then spot-verified specific claims against disk rather than
trusting the index's prose. It produced 8 numbered, severity-tagged findings (1 BLOCKS-LAUNCH, 4
FIX-BEFORE-SEND/NOTE items on the index's internal accuracy, 3 further NOTE items on trunk
dormancy, time-cost honesty, and seat work priced onto Jon) alongside a list of claims that
survived spot-verification. Session made a single tool-heavy pass with 1 human turn (the dispatch)
and 39 further assistant/tool turns; it is entirely findings, not a conversation.

## Key Claims

- **BLOCKS-LAUNCH — the documented launch procedure fails at step two, in both documents under
  review.** `right-click-launcher-failure-class.md:71` shows the live `CFL Coordinator.ps1` line is
  bare `claude --continue` — the same shape as a prior mis-waking incident — disposed "letter, not
  edit," not fixed. `TEACH-ME §4:87` says "the first message IS the trigger" but names no launch
  route. A grep for "CFL Coordinator.ps1" across the entirety of Personal's `exchange/` (inbound and
  outbox) returned zero files, so the claimed disposing letter was not found from this seat.
  [verbatim] ([professional-seat-adversarial-review-of-jons-plate-2026-08-21-e3a556:T40])
- **FIX-BEFORE-SEND — the reviewed decision-queue index disagreed with its own counting instrument,
  three ways.** `00-INDEX.md:108` claimed "open rows: 1 — row 7," the exact grep the index cites
  (`awaiting-jon.sh:33`) matched 2 rows, and Section A's own header still said "3 rows" — one file,
  three counts. Structurally, row 8 sat inside a two-column coverage table with three cells and
  cited a file outside the directory the counting script scans. [verbatim]
  ([professional-seat-adversarial-review-of-jons-plate-2026-08-21-e3a556:T40])
- **FIX-BEFORE-SEND — a stated block (row 4, Fable budget) had expired ~2.5 hours before Jon's
  order and nothing on the plate flagged the state change from blocked to actionable.**
  [paraphrase] ([professional-seat-adversarial-review-of-jons-plate-2026-08-21-e3a556:T40])
- **FIX-BEFORE-SEND — only-Jon items inside the seat's OWN trunk were surfaced nowhere on the
  plate.** `claude-professional/wiki/tracker/tracker.md:296` named two Jon-only, non-redoable
  one-minute items (minting a token, signing a consent) that reach no Jon-facing index; the seat
  flagged them as possibly superseded (tracker last touched 08-17) but noted nothing on record
  closes them, and "UNKNOWN is not CLOSED." [verbatim]
  ([professional-seat-adversarial-review-of-jons-plate-2026-08-21-e3a556:T40])
- **NOTE — the peer trunk the fresh Fable must coordinate with was measured 4 days dormant.**
  Professional's last wake was 08-17 22:28; ten letters had arrived in `inbound/` since (newest
  08-20 23:02), all undisposed, on top of a measured ~203-item backlog — and the plate nowhere
  surfaced that a peer trunk was asleep. [paraphrase]
  ([professional-seat-adversarial-review-of-jons-plate-2026-08-21-e3a556:T40])
- **Positive controls reported alongside findings, not omitted.** The seat explicitly listed what
  survived spot-verification: the draft byte count (60,893 B) matched, several named files existed,
  and Personal's own claim about Professional lacking a `FOR-JON-REVIEW/` index was confirmed true.
  [verbatim] ([professional-seat-adversarial-review-of-jons-plate-2026-08-21-e3a556:T40])

## Jon

No Jon turns captured in this raw beyond the dispatch order quoted inside the single Human turn at
T1, which itself relays Jon's order as reported prose rather than a direct Jon-authored turn in this
session: "Have professional and CFL each perform an adversarial peer review of what is on my plate
before I launch the fresh cfl fable coordinator to go from here with my first message from it"
(2026-08-21 ~16:3x CDT, as dated inside the dispatch text).
([professional-seat-adversarial-review-of-jons-plate-2026-08-21-e3a556:T1])

## Conflicts

None with existing wiki content.

## Decisions and open items

- Open: finding 1 (no verified fresh-launch route for the CFL Fable coordinator) is named as the
  one finding that touches the day's action directly — nothing in this raw shows it being resolved.
- Open: findings 2, 3, and 7 (index self-inconsistencies, stale block state, unbudgeted read time)
  are named by the seat as fixable by the Personal seat "in minutes" — no confirmation of a fix
  lands in this raw.
- This page draws only on the initial dispatch (T1) and the closing findings message (T40); the
  intermediate 38 tool-call turns (the verification trail) are visible in the raw but not
  individually cited here.

## Entities & Concepts

Adversarial peer review, `00-INDEX.md` / decision-queue index, `TEACH-ME-fable-day-2026-08-21.md`,
`right-click-launcher-failure-class.md`, `launch-cfl.bat`, headless write-denied review seats.

## Uncaptured Content

- Turns T2–T39 (the tool-call verification trail building each finding) are visible in the raw but
  not individually walked or cited on this page — only the dispatch (T1) and the closing findings
  message (T40) are drawn on.
- 0 compaction boundaries and thinking-block status for this raw were not independently re-checked
  beyond what the raw's own frontmatter states.

## Links

[[frame-before-commit]] — the same obstacle-first, adversarial framing this review's own attack-vector
list (decisions mis-framed as Jon's, only-Jon items unsurfaced, unverified claims) instantiates.
