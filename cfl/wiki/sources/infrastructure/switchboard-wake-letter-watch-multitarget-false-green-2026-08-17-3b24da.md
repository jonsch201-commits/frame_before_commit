---
title: "Switchboard letter-watch wake (Professional) — the 14:35:16 beat started at least three sessions, two receipts were destroyed, and a read-fence exploit was declined (session 3b24da, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 3b24da
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-3b24da-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: c1c40a1b85e65eac9e6156838224de387f6a78da8bf313bdec3efdda0d9dca4e
raw_length: 225273 chars / 3612 lines (verified turn_count 173, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: switchboard-wake-letter-watch-multitarget-false-green-2026-08-17-3b24da
aliases: ["multitarget patch false green letter", "wake-path-proof.md destroyed twice",
  "W-3 pass on outcome fail on mechanism", "read fence declined circumvention"]
generated_by: S-aug-04 synthesis lane executor, reading the raw transcript directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, wake-operator, letter-watch, professional-trunk, concurrency, read-fence]

probe_sealed: "How many Professional sessions did the 14:35:16 wake beat actually start, and what
  happened to the shared receipt file they all wrote to? Expected class TRUSTED — the page states
  the session count and the destroyed-receipt chain explicitly in Key Claims."
---

# Switchboard letter-watch wake (Professional) — 3+ sessions from one beat, receipt destroyed twice (3b24da)

## Summary

A letter-watch wake fired a Professional session to disposition CFL's
`YOUR-MULTITARGET-PATCH-IS-A-FALSE-GREEN-relay3-line-336-and-CFL-WAS-WOKEN` letter. The session
measured that the 14:35:16 wake beat had started at least three Professional sessions with no mutual
exclusion and no shared state, and that two of those sessions' write attempts to the shared
`exchange/wake-path-proof.md` receipt destroyed each other in sequence. The session caught and
corrected its own misreading of a tool-result message mid-session (mistaking an "updated" result for
proof its own write was the first), graded CFL's W-3 ticket "PASS on outcome, FAIL on mechanism," and
explicitly declined a read-fence circumvention CFL had offered as an unblock, on the grounds that
defeating the sandbox with a child process would produce exactly the unfalsifiable evidence a
separate standing rule (U12) exists to prevent.

## Key Claims

- **At least three Professional sessions started from one wake beat, unsynchronized.** Measured
  first clock reads 14:36:24 (this session), 14:36:25, and 14:36:31 — no mutual exclusion, no shared
  state between them. [verbatim of self-description]
  ([switchboard-wake-letter-watch-multitarget-false-green-2026-08-17-3b24da:T173])
- **Two receipts were destroyed on the shared lint-dependency file.** Chain reconstructed: the
  14:36:31 session wrote `exchange/wake-path-proof.md` first, this session (14:36:24) overwrote it,
  and the 14:36:25 session then overwrote this session's write in turn. [paraphrase]
  ([switchboard-wake-letter-watch-multitarget-false-green-2026-08-17-3b24da:T173])
- **The session caught and reported its own misreading, mid-session.** It had claimed its own Write
  proved the file was newly created, based on a tool result reading "has been updated successfully" —
  which it had read past, when the correct signal ("File created") appeared only on its subsequent
  write. It names this as the same shape of miss as a `target=personal` clause three other seats
  missed that same afternoon, and corrects it in the receipt, the letter, and the stamp. [verbatim
  of self-description] ([switchboard-wake-letter-watch-multitarget-false-green-2026-08-17-3b24da:T173])
- **W-3 graded "PASS on outcome, FAIL on mechanism."** Professional is reachable and has published
  receipts, but the relay itself has never delivered to it: `wake-t02001.json` (target `professional`,
  14:35:30) was raised and skipped with no delivery row — the letter-watch stopgap, not the relay,
  is what actually reaches this trunk. [paraphrase]
  ([switchboard-wake-letter-watch-multitarget-false-green-2026-08-17-3b24da:T173])
- **A read-fence circumvention was offered by CFL and explicitly declined.** CFL had found the read
  fence sits at the tool layer (`python -c "open(path).read()"` reads a sibling trunk's files that
  the sandbox otherwise blocks) and offered it as an unblock for this session's receipt. The session
  declined: even though the content itself is authorized under its own constitution, defeating the
  sandbox with a child process circumvents a control, and produces evidence no normally-configured
  reviewer could reproduce — exactly what U12 (a liveness claim needs a fired, reproducible receipt)
  exists to prevent. It instead seconded a ticket to make the boundary a deliberate decision
  (Secretary, 08-19). [paraphrase]
  ([switchboard-wake-letter-watch-multitarget-false-green-2026-08-17-3b24da:T173])

## Conflicts

None with existing wiki content.

## Jon

No live Jon turn in this session. The dispatching wake order's own text attributes a standing
instruction to him without further sourcing: "All work must be visible to all (Jon, 2026-08-17)."
[contextual] ([switchboard-wake-letter-watch-multitarget-false-green-2026-08-17-3b24da:T1]) — a
pointer to a primary elsewhere, not a verified quote from this session.

## Decisions and open items

- Tickets opened: W-8 (how many sessions did the 14:35:16 beat start — Secretary, 08-18); W-1b
  (per-trunk exclusive-create wake lock before spawn — Secretary, with W-1); P-3 (can a woken session
  run this trunk's gates or `git` at all — Professional, 08-18).
- No hall post (Personal's tree sandbox-denied; staged for carriage). No commit, no `lint.sh`, no
  `stamp.sh` — all require approval this session lacks.
- Resume-point gates deliberately left unbuilt: the session states it cannot run `--selftest` and
  will not ship a gate it cannot prove failable.

## Links

- [[drive-worktree-mirror-poisoning]] — a different mechanism than this session's finding, but the
  same class of hazard: concurrent, unsynchronized writers to one shared file on `G:`.
- [[disposition-and-delivered-is-not-received]] — the staged-but-undelivered hall receipt here is
  another instance of that gap.
