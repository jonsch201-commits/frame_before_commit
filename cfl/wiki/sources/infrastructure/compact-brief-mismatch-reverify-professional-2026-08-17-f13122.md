---
title: "Professional's headless wake re-verifies Soul's compact-brief fix and finds the finding described the wrong trunk's defect (session f13122, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: f13122
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-f13122-you-have-new-mail-waiting-exchangeinboundsoul-to-p.md
raw_sha256: 24fc547dd2ab5561923d89a01f7016e764df3b9a35569e8b010e9236a251adea
raw_length: 125220 chars / 1780 lines (verified turn_count 86, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: compact-brief-mismatch-reverify-professional-2026-08-17-f13122
aliases: ["twelfth wake compact-brief re-verify", "Soul finding described wrong trunk defect",
  "P-10 P-11 open items 2026-08-17", "session 11 vs session 12 same seat re-run"]
generated_by: S-aug-12 executor (RP-3/RP-4 window-to-source lane), reading the headless-seat
  extract directly (raw/transcripts/claude-code/code-2026-08-17-f13122-...md, 20 thinking blocks
  encrypted-in-signature, tool calls/results summarized)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, secretary, compact-brief, professional-trunk, peer-review-rule, headless-wake]
---

# Professional's headless wake re-verifies Soul's compact-brief fix — session f13122, 2026-08-17

## Summary

A headless, single-directive wake session in Professional's trunk was dispatched to read and act on
Soul's mail naming a "compact-brief false positive" with a proposed two-line patch. The session (1
human turn: the wake order; 86 turns verified total) read the referenced letter, then — recognizing
that a peer session in its own trunk ("session 11") had already stamped the letter FIXED — re-ran the
verification mechanism itself rather than inheriting the prior session's disposition, per the
constitution's own rule that a fix is not closed by its author. It found that session 11 had verified
the *commit* but not the *mechanism*, and that Soul's finding's own quoted sentence did not actually
exist anywhere in Professional's brief code — the freshness-check defect Soul described belonged to
Personal's adaptation, not Professional's. The session hit its session limit mid-edit, immediately
after appending its corrected disposition to the shared tracker.

## Key Claims

- **Session 11 verified the commit; it did not verify the mechanism — and accepted the finding's
  description of the defect without checking it against the actual code.** This session (referred to
  in-file as "session 12," the same seat as session 11) re-ran the check rather than inheriting the
  result, invoking the universal-layer rule verbatim: "a review checked against the finding can only
  ever be as good as the finding." [paraphrase]
  ([compact-brief-mismatch-reverify-professional-2026-08-17-f13122:T86])
- **The sentence Soul quoted as Professional's defect does not exist in any version of Professional's
  compact-brief code.** A grep of the tree found the sentence only inside Soul's own letter; Soul's
  filenames (`COMPACT-RECOVERY.md`, `compact-capture.log`) matched Personal's naming convention, not
  Professional's — the freshness-check sentence Soul described "entered in Personal's adaptation," so
  this was not the shared pattern recurring in a second trunk. [paraphrase]
  ([compact-brief-mismatch-reverify-professional-2026-08-17-f13122:T86])
- **Professional's actual pre-fix defect was the inverse of Personal's, and worse in kind.** Personal's
  copy failed CLOSED (a false failure against a working hook, per Soul's own description). Professional's
  pre-fix logic (`6e4b918`) checked only file presence (`[ -f "$RECEIPT" ]`) with no freshness test at
  all, so it would silently fail OPEN: a compacted seat could read an earlier session's stale receipt
  as its own HEAD and transcript path. The fix (`b5ee7e7`, timestamped 11:46:58, predating Soul's
  letter) added a `MISMATCH` verdict comparing a written `session:` id against the live one, curing
  both directions. [paraphrase] ([compact-brief-mismatch-reverify-professional-2026-08-17-f13122:T86])
- **A new gap was found in the fix itself and ticketed, not silently left: P-10, a fifth verdict state
  is missing.** If `PreCompact` fires on a payload with no `session_id`, the written line becomes a
  bare `session: `, matches nothing, and `verdict()` returns `MISMATCH` against a populated live id —
  escalating to a false T-1 finding, which is Soul's original false-failure defect recurring through a
  different door. Fix proposed (a fifth verdict, `RECEIPT-SESSION-UNKNOWN`, fail-open) but explicitly
  **not implemented this session** because `bash scripts/*.sh` was refused to this seat and the session
  declined to land unverified code inside a finding about false-green liveness. [verbatim: "Ticketed
  with owner and date is a disposition; annotation is not."]
  ([compact-brief-mismatch-reverify-professional-2026-08-17-f13122:T86])
- **P-11 — a convention defect found in this trunk's own stamping practice: stamping a letter in place
  destroys the anchor the stamp itself cites.** Session 11 wrote a byte-count-and-mtime anchor into the
  very letter file it was anchoring; the later append moved the mtime, so the load-bearing claim ("the
  fix predates the letter by seven minutes") became permanently uncheckable by mtime — the byte count
  alone survived only because the letter had already been committed to git first. Rule stated:
  "anchor to an immutable store (the git blob), never to the file being stamped." [paraphrase]
  ([compact-brief-mismatch-reverify-professional-2026-08-17-f13122:T86])
- **The session made a live tight-window edit to a shared multi-writer tracker file, checking for a
  live peer first.** It listed peer session JSONL mtimes, found a peer (`9ff05b94`) had last written 6
  minutes earlier, and made its own tracker insert as a single tight `Edit` call to minimize the
  collision window rather than holding the file open longer than necessary. [contextual]
  ([compact-brief-mismatch-reverify-professional-2026-08-17-f13122:T86])
- **Session ended mid-work at the platform's session limit, immediately after the tracker edit
  succeeded.** The final visible turn is the tool result confirming the tracker write, followed by the
  platform message "You've hit your session limit · resets 4:20pm (America/Chicago)" — no further
  session-authored content follows. [verbatim] ([compact-brief-mismatch-reverify-professional-2026-08-17-f13122:T86])

## Jon

No Jon turns in this window — the session's single human turn is a wake-order dispatch (switchboard
mail-pointer text), not a Jon-authored message.

## Decisions and open items

- P-10 (fifth verdict state `RECEIPT-SESSION-UNKNOWN`, fail-open, plus a selftest state E) — OPEN,
  owner: next Professional session that can run `bash scripts/*.sh`, or Jon, by 2026-08-18.
- P-11 (never anchor a stamp to the file it stamps; anchor to the git blob) — OPEN, no owner named in
  this window.
- Session limit hit mid-turn; whether the tracker commit and further verification landed after this
  capture is not established here.

## Conflicts

None with existing wiki content.

## Links

[[probe-registry]] — the "verify before relying" discipline this session's re-run of session 11's
verification exemplifies (checking a fix against the finding rather than inheriting a green result).

## Uncaptured Content

- This raw is a `capture_state`-unmarked static extract (no `LIVE-SNAPSHOT` frontmatter field, unlike
  several sibling captures this same day) but ends abruptly at a platform session-limit message with
  no closing summary — whether the session resumed and what, if anything, landed afterward (the
  tracker `git commit`, in particular) is out of scope for this page.
- Turns 2–85 (the bulk of the middle — reading the mail, earlier tracker context, and the concurrency
  checks preceding the final edit) are drawn on only in aggregate here; only T86 (the session's final
  turn, containing the tracker Edit and its surrounding assistant text) is individually cited.
- 20 thinking blocks exist in the raw and are encrypted-in-signature (per this raw's own extraction
  note) — not recoverable client-side, so no claim on this page draws on the session's private
  reasoning, only its visible tool calls and written text.
