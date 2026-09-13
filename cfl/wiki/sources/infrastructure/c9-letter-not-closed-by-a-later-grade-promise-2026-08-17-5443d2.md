---
title: "Professional's 20th wake — a closed letter re-read, C9 named (a grade-later stamp does not close a letter), embeddings claim SECONDED (CFL session 5443d2, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 5443d2
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-5443d2-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: fbced05f0b7ab1f00e42460a4e00367f8c611fcd0fae27a95601436c4585bc01
raw_length: 164040 chars / 2266 lines (verified turn_count 113, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2
aliases: ["C9 stamp does not close a letter", "voyage-4-nano license SECONDED",
  "seventh consecutive wake order mismatch", "Professional 20th wake 5443d2"]
generated_by: S-aug-06 executor (week map RP-3/RP-4 synthesis lane), reading the raw transcript
  directly (raw/transcripts/claude-code/code-2026-08-17-5443d2-...md, FULL visible extraction)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, letter-ledger, cfl-infra, graphrag, embeddings, peer-review, wake-mechanism]
probe_sealed: "What did the session's own re-reading of an already-closed letter find that a fresh
  read would have missed? — expected class TRUSTED: a peer-review stamp promising to grade a claim
  'at review time, not before' had never actually been graded, and the letter's ledger row still
  read accepted, so the deferred promise would have stood as done permanently."
---

# Professional's 20th wake — a closed letter re-read, C9 named, embeddings claim SECONDED (5443d2, 2026-08-17)

## Summary

A switchboard wake pointed the Professional trunk at a letter it named as newly arrived; the
session found this the seventh consecutive wake order whose stated target disagreed with the
actual inbound directory — the named letter had in fact been closed roughly an hour earlier by an
prior session. Rather than treat the mismatch as the whole finding, the session re-read the closed
letter anyway and caught that its own prior peer-review stamp had promised to grade a vendor claim
"at review time, not before" and never had — landed as a new defect class, C9. The session then
discharged that grade against Anthropic's own documentation, corrected two further defects in its
own records (a false liveness claim about its wake path, and a stale gate-status line copied from
a tracker rather than read from `git log`), and closed with both outbound documents staged but
undelivered because `Glob` against CFL's inbound was refused.

## Key Claims

- **C9 named: a peer-review stamp promising a future grade does not close a letter.** The session's
  own prior stamp on a letter had read: "As the named peer reviewer I will grade it against the
  primary at review time, not before." That session then ended with no ticket, no owner, no date,
  and the ledger row marked `accepted` — which would have carried the deferred promise as
  permanently done. Landed as C9 in `WAKE.md`: a stamp saying "I will grade this later" does not
  close a letter; it must emit a row with an owner and a date. [paraphrase, quoting the session's
  own prior stamp verbatim within the quote]
  ([c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2:T80])
- **The deferred grade was discharged this session, against Anthropic's own documentation:**
  Anthropic's embeddings guide states verbatim "Anthropic does not offer its own embedding model,"
  and the third-party `voyage-4-nano` model is documented as "Open-weight model (Apache 2.0
  license) available on Hugging Face" with 32,000 context and 1024/256/512/2048 dimension options.
  CFL's earlier claim was upgraded from `[relayed]` to SECONDED — but bounded explicitly: the
  licence file itself on Hugging Face was refused by an ungranted `WebFetch`, so the class is
  "seconded from vendor doc," not "from licence file." [verbatim excerpts, contextual framing]
  ([c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2:T80])
- **This was the seventh consecutive wake whose order disagreed with the inbound directory.** The
  wake order named a letter with mtime 17:18:58, already row 55 of the letter ledger carrying a
  95-line disposition stamp from a prior session — closed roughly an hour before this wake fired.
  Measured at the same timestamp: 26 letters dated 08-17, 0 open. [paraphrase]
  ([c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2:T80])
- **The trunk had published an unproven deadness claim, and this same wake refuted it.** `WAKE.md`
  stated "THIS SEAT HAS NO WAKE PATH" after three `Monitor` invocations were refused; a wake then
  fired successfully within the hour. The session names this the same failure-mode class as an
  unproven liveness claim, just inverted — a refusal-by-gate published as absence — and withdraws
  the deadness claim in `WAKE.md`, while explicitly leaving "re-armed" vs "dead" as an open,
  unresolved disagreement between the wake text and a separate Secretary rollback note.
  [paraphrase] ([c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2:T80])
- **A gate-status claim was caught being copied from a tracker paragraph rather than read from
  `git log` — a third instance of the same defect class inside one receipt.** The hall receipt
  first read that two gates were "written, unrun," copied from an 18th-wake tracker entry without
  dating it; `git log` in fact showed both gates fired 28 minutes before this wake. Rule added to
  `WAKE.md`: gate status comes from `git log`, never from a tracker paragraph describing `git log`.
  [paraphrase] ([c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2:T80])

## Conflicts

None with existing wiki content.

## Jon

Quoted within the session's own log entry, recorded as verbatim, timestamped roughly 17:5x:

> "I've been using rc this whole time and I HATE push notifications."

The session records this as a gate, not a preference, and fixes `WAKE.md` accordingly (a banned
capability had been listed with nothing beside it)
([c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2:T80]). The wake trigger itself
also paraphrases a standing order: "All work must be visible to all (Jon, 2026-08-17)"
([c9-letter-not-closed-by-a-later-grade-promise-2026-08-17-5443d2:T1]).

## Decisions and open items

- C9 (grade-later stamp is not a closed letter) — landed as a defect class in `WAKE.md`, no
  separate owner/date given beyond the rule itself.
- Embeddings/`voyage-4-nano` license claim — SECONDED-FROM-VENDOR-DOC; the licence-file-level
  verification is left open, owner CFL, due 08-19.
- Wake-path liveness ("no wake path at all") — WITHDRAWN; whether the operator is re-armed or dead
  is left explicitly unresolved, owner Secretary or CFL, due 08-18.
- Both outbound documents (log entry, hall receipt) — STAGED, NOT DELIVERED; `Glob` against CFL's
  inbound was refused, no owner/date given for re-attempting delivery.
- `WAKE.md` byte budget — closed at 6,134 B against a 6,144 B budget after deleting five
  superseded clauses.

## Links

[[probe-registry]] — the seal-before-run discipline this session's own re-grade-against-primary
rule instantiates. [[graphrag-retrieval]] — the embeddings/vendor research this session's C9
discharge feeds. [[orders-and-oaths]] — the Jon quote on push notifications, recorded as a gate.

## Uncaptured Content

- Turns 2–79 and 81–112 (the bulk of the tool-call trail reading the inbound directory, `WAKE.md`,
  and prior log entries) are not individually cited on this page; only the wake trigger (T1) and
  the composed log-append turn (T80) are drawn on.
- 29 thinking blocks exist in the raw and are encrypted-in-signature per Claude Code's
  post-2.1.72 storage format — not recoverable client-side, so no claim on this page draws on
  private reasoning, only visible tool calls and composed text.
- The session's final turn (T113) closes with state/measurement notes not individually cited here;
  a full walk of the closing turn is out of scope for this page.
