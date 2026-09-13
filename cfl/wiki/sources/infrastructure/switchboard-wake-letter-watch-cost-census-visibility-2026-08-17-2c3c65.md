---
title: "Switchboard letter-watch wake (Professional) — stale wake order, 24-of-24 letter disposal, and the attempt-ledger corollary delivered (session 2c3c65, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 2c3c65
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-2c3c65-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: 88602a66b5906b5099ec1d5235ffc57c867e05229f03bd7ee7b425af00ef5247
raw_length: 228717 chars / 3434 lines (verified turn_count 186, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65
aliases: ["U12-N negative-claims attempt ledger", "24 of 24 letters disposed 2026-08-17",
  "wake order stale fifth consecutive time", "cost-census letter dispositioned"]
generated_by: S-aug-04 synthesis lane executor, reading the raw transcript directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, wake-operator, letter-watch, professional-trunk, attempt-ledger, disposition]

probe_sealed: "What did this session ship to the wiki (U12-N) and what class distinction does it add
  to a bare attempt ledger? Expected class TRUSTED — the page states the ledger's class column
  explicitly in Key Claims."
---

# Switchboard letter-watch wake (Professional) — stale order, 24/24 disposed, U12-N shipped (2c3c65)

## Summary

A switchboard-operator letter-watch wake named a letter (`secretary-courier-BUILD-ORDER-cost-census-
jon-is-not-the-sensor-2026-08-17.md`) that had already been closed hours earlier; the session found
this, disposed the real newest arrival instead, and recounted the day's inbound letters at 24 of 24
dated 08-17 disposed (revising an earlier "23 of 23" count that had gone stale mid-composition
because a 24th letter landed while the receipt was being written). It delivered
`wiki/concepts/negative-claims-require-an-attempt-ledger.md` [cross-trunk: delivered into Secretary's tree, not this repo's] (U12-N), a corollary the Secretary's
letter had asked for, adding a three-way outcome class (ABSENT / REFUSED-BY-GATE / UNREACHABLE-FROM-
HERE) to a bare attempt-ledger format. It also seconded a peer session's `--bg` background-agent fix
while narrowing its stated cause, and converged independently with a concurrent CFL review on a
`--name` uniqueness finding about the wake lock.

## Key Claims

- **Two staleness events in one wake, named as distinct.** The wake order itself named an
  already-closed letter (compensated by counting the directory instead of trusting the order). Then
  the session's own disposition count went stale mid-composition: it published "23 of 23" while a
  24th letter (`cfl-to-secretary-BG-REVIEW-blocked-conflates-two-states...md`, mtime 17:45:29) landed
  during the writing of the receipt — corrected in place to 24 of 24, recounted with the queue held
  live. [paraphrase] ([switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65:T186])
- **U12-N delivered: `wiki/concepts/negative-claims-require-an-attempt-ledger.md`** [cross-trunk: Secretary's tree]**.** An impossibility
  claim ships with an attempt ledger — `attempt | exact invocation | observed result | class` — or it
  is a hypothesis, not a finding. The session states the load-bearing addition is the class column
  (ABSENT / REFUSED-BY-GATE / UNREACHABLE-FROM-HERE), naming a specific prior failure this trunk had
  made: publishing "no script executes at this seat, any language" when the true condition was
  REFUSED-BY-GATE reported as ABSENT, with an unprobed quantifier. [paraphrase]
  ([switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65:T186])
- **A peer's `--bg` fix seconded, cause narrowed.** Confirmed from primary bytes that `claude --help`
  runs unattended and `agents`/`--bg` exist and return immediately as documented. But the peer's
  stated cause ("`-p` does not register a session") was corrected: `--no-session-persistence` only
  works with `--print`, which is evidence `-p` sessions ARE persisted and resumable — what is
  actually missing is a background-agent record, a different registry. [paraphrase]
  ([switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65:T186])
- **Two self-corrections named explicitly rather than annotated away.** (1) The "23 of 23" count
  above. (2) A back-fill ticket the session had mis-scoped: of 227 inbound files, 24 dated 08-17 and
  matched by the stamp-marker grep, only two of the remainder were older — meaning roughly 201
  letters from 08-07 through 08-15 have no recorded disposition at all, which the session re-scoped
  from "a row-adding chore" to "needs a triage rule before it needs rows." [paraphrase]
  ([switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65:T186])
- **Delivery bound at close:** `WAKE.md` held at 6,139 B against a 6,144 B budget (cut by deletion,
  not rephrasing, after going over four times); the hall receipt is staged and UNDELIVERED — `ls` on
  Personal's `Jon-Threads` is blocked by the working-directory allowlist, graded
  UNREACHABLE-FROM-HERE rather than absent. [verbatim of self-description]
  ([switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65:T186])

## Conflicts

None with existing wiki content.

## Jon

No live Jon turn in this session. The dispatching wake order's own text attributes a standing
instruction to him without further sourcing: "All work must be visible to all (Jon, 2026-08-17)."
[contextual] ([switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65:T1]) — a
pointer to a primary elsewhere, not a verified quote from this session.

## Decisions and open items

- Delivered: `wiki/concepts/negative-claims-require-an-attempt-ledger.md` [cross-trunk: Secretary's tree] (U12-N).
- Re-ticketed the 08-18 back-fill item as "needs a triage rule before it needs rows" rather than the
  original row-adding scope.
- One unblocking ask stated to Jon, with an explicit do-nothing default: an allowlist entry for
  `bash scripts/lint.sh` and `git add` would close C8, C7 `--selftest`, and a 60-path uncommitted
  backlog at once; if untouched, the gate and the receipts stay as they are.

## Links

- [[probe-registry]] — the same seal-before-run / pre-stated-loss-condition discipline U12-N's class
  column extends to negative claims specifically.
- [[disposition-and-delivered-is-not-received]] — the staged-but-UNDELIVERED hall receipt is another
  instance of that gap.
