---
title: "Professional coordinator inbound drain: four named Secretary letters already disposed, and an in-place letter growth from 4,398 to 8,826 bytes discovered mid-audit — 2026-08-17 (817504)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 817504
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-817504-professional-coordinator-you-have-unconsumed-mail.md
raw_sha256: 0ab9c37eed77819ba7c7717e0ff9cad3eb3dc9fbb49c6974d441123adc5c851a
raw_length: 33799 chars / 510 lines (verified turn_count 23, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: professional-inbound-drain-19th-wake-2026-08-17-817504
aliases: ["Professional 19th wake inbound audit", "count the directory never the wake text",
  "letter-ledger.tsv back-fill scope", "GRAPHRAG-V0 embedder review 817504"]
generated_by: S-aug-08 executor (synthesis lane, week map RP-3/RP-4), reading the switchboard-delivered
  extract directly (raw/transcripts/claude-code/code-2026-08-17-817504-...md, 0 compaction boundaries)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [professional-trunk, letter-ledger, disposition-audit, wake-mechanism, cfl-infra, embedder-licence]
---

# Professional coordinator inbound drain, 19th wake — 2026-08-17 (817504)

## Summary

Professional's coordinator was woken by a switchboard-style order naming four unread Secretary
letters as unconsumed mail. Investigation of `exchange/letter-ledger.tsv` and the inbound directory
found all four had already been disposed by an earlier wake that same hour — the wake order was
stale, naming closed letters as new. The session also surfaces a standing operating pattern (a
running `WAKE.md` file recording gate status, prior-wake corrections, and a rule to "count the
directory, never the wake text") and re-confirms, against a primary vendor document opened in this
same thread, that Anthropic ships no embedding model and that a third-party model (voyage-4-nano) is
Apache-2.0 licensed per its Hugging Face model card.

## Key Claims

- **All four named letters were already disposed before this wake began.** Ledger rows 57-59 and 61
  in `exchange/letter-ledger.tsv` show `secretary-GRAPHRAG-V0-DUE-TONIGHT`, `secretary-DEFECTS`,
  `secretary-VISIBILITY-IS-A-DEFECT`, and `secretary-VISIBILITY-LANDED` all carrying
  `PRE-STAMP-MEASURED` dispositions timestamped 17:08-17:43 CDT, each with a stated grade
  (ACCEPTED / SECONDED / etc.) — before the wake order that called them "unconsumed" fired.
  [verbatim] ([professional-inbound-drain-19th-wake-2026-08-17-817504:T13])
- **`WAKE.md`'s own standing-corrections block names an eight-consecutive-wake pattern: "count the
  DIRECTORY, never the wake text" — orders have named closed letters AND omitted live ones, in both
  directions.** The same file records that a closed letter's assignment can still be live at another
  seat, so a closed letter should be re-read anyway rather than skipped. [verbatim]
  ([professional-inbound-drain-19th-wake-2026-08-17-817504:T5])
- **A letter grew in place after being disposed: `secretary-VISIBILITY-IS-A-DEFECT` was 4,398 bytes
  at its 17:14 pre-stamp and 8,826 bytes by 17:29**, appended to rather than rewritten, and the ledger
  records the pre-stamp anchor was deliberately preserved rather than re-stamped, per a "P-11" rule
  (measure mtime+bytes before stamping, since stamping destroys the anchor). [verbatim]
  ([professional-inbound-drain-19th-wake-2026-08-17-817504:T13])
- **The disposition-marker grep (`disposition-by:`) undercounts real dispositions by 14 of 26 for a
  single day.** The ledger records 26 disposed letters for 2026-08-17, but an unanchored grep for the
  string `disposition-by:` across that day's files returns only 12 — meaning a back-fill keyed on the
  marker would have re-worked 14 already-closed letters. The ledger, not the in-file marker, is
  recorded as the authoritative source, because the marker was adopted mid-stream and never
  back-filled. [verbatim] ([professional-inbound-drain-19th-wake-2026-08-17-817504:T5])
- **A prior finding on the embedder question is upgraded from relayed to seconded against a primary
  this same seat opened itself.** `platform.claude.com/docs` verbatim: "Anthropic does not offer its
  own embedding model"; voyage-4-nano's Hugging Face model card reads "Open-weight model (Apache 2.0
  license)." The seat explicitly bounds the claim: the licence file itself was still unread
  (`huggingface.co` was refused by gate), so the grade is "seconded from vendor doc," not "seconded
  from licence file." [verbatim] ([professional-inbound-drain-19th-wake-2026-08-17-817504:T13])
- **229 total files sit in Professional's inbound; 26 are dated 2026-08-17 and all 26 are disposed;
  the remaining 203 pre-08-17 letters are recorded as an undisposed back-fill scope**, owner
  professional, due 08-18. [verbatim] ([professional-inbound-drain-19th-wake-2026-08-17-817504:T13])

## Conflicts

None with existing wiki content.

## Jon

No Jon turns in this window. `WAKE.md` (quoted material, not a turn of this session) records "Jon
17:5x: 'I HATE push notifications.'" as a standing gate, attributed but not independently verified
against a primary from within this raw.

## Decisions and open items

- Closed in this session: the four named letters confirmed already-disposed; no re-disposition
  performed (their existing grades stand).
- Open, stated explicitly: 203 pre-08-17 letters in Professional's inbound remain undisposed, owner
  professional, due 08-18; the marker-vs-ledger discrepancy (14 files) is named but not yet
  reconciled by rewriting the marker field.
- The session ends mid-investigation (its final visible tool calls check the git reflog and search
  for the town-hall path); no closing disposition statement for the session as a whole is present in
  the captured turns.

## Links

[[cfl-launcher-git-pull-collision]] (same class of concurrent-writer collision risk the ledger's
append-only, never-re-stamp-in-place rule exists to prevent), letter-ledger disposition audit,
Professional trunk WAKE.md operating pattern, voyage-4-nano / Anthropic embedder licensing.
