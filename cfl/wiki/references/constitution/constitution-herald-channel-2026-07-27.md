---
kind: reference
slug: constitution-herald-channel-2026-07-27
status: LIVE
moved_from: CLAUDE.md
moved_on: 2026-09-12
moved_by: CFL coordinator, on Jon's instruction
---

# Herald channel — the 2026-07-27 unread-outbox failure, in full

⛔ **THIS PAGE IS A VERBATIM EXTRACT FROM `CLAUDE.md`, MOVED 2026-09-12 ON JON'S INSTRUCTION.**
Jon, live, ~21:1x CDT (verbatim, typos his): *"query - item 4 in your claude.md under wiki, starting
like 140 feels like a draft and reference material that might belong in the wiki rather than in your
actual claude.md. Same for some other sections - feels unprofessional. I get why a lot of this may
have needed to go here.... but.... yeah please...."*

**The rule this block supports stayed in `CLAUDE.md`. Only its case history moved here.** Nothing was
deleted — "Yeah no deletion. And no writing PII to Github." (Jon, 2026-08-09) governs, and a
`scripts/audit/constitution_extract_receipt.py` run asserts every moved line is byte-present below.

⚠️ **THE ORIGINAL LINE PREFIXES ARE PRESERVED EXACTLY** — the blockquote markers and the leading
indentation are the bytes that were in `CLAUDE.md`, not a rendering choice. **A literal grep of any
sentence that used to live in the constitution must return this page**, which it cannot do if the
text is retyped tidier. Same rule as a Jon quote: the test of an extract is whether `grep -F` finds it.

**Where the live instruction now lives:** `CLAUDE.md` → *Herald channel*.

---

**The rule that matters is not the write scope. It is that the channel has a consumer on both ends.**
On 2026-07-27 CFL sent three relays into Herald's inbound and **never once read Herald's outbox.**
Four messages sat unread — and one of them was the day's most consequential finding: `cc_corpus_gap.py`
was reading `source_id:` while 26 extracts declare `uuid:`, so it reported them all LOST. **It was
not finding losses. It was finding a field name.** CFL published a 29-session "permanently lost"
registry on that output and dispatched a reconstruction against a session with a real 12.67 MB
transcript on disk. Herald caught it by reading CFL's *published claim* and checking it.

**So: at session open and at every standard update, read what the other side sent.** Herald-authored
files in `exchange/` and anything in Herald's `outbox/`. A deposit-only channel is the same defect as
a deposit-only queue — see `skills/intake/README.md`, which was drained on the same day for the same
reason.

**Why the redundancy is worth its cost, stated so nobody optimizes it away:** every correction that
landed on 2026-07-27 came from the *other* project. Neither coordinator found its own. Herald's
warning is the standing constraint — *"the risk of mutual learning is convergence; if we teach each
other well enough we become one coordinator with one blind spot, and the redundancy that caught all
of this disappears."*
