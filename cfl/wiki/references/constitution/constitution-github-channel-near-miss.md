---
kind: reference
slug: constitution-github-channel-near-miss
status: LIVE
moved_from: CLAUDE.md
moved_on: 2026-09-12
moved_by: CFL coordinator, on Jon's instruction
---

# The GitHub channel and AUTHOR-LOGIN — the near-miss that retired a sentence

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

**Where the live instruction now lives:** `CLAUDE.md` → *Standing constraints* → the venue table.

---

⚠️ **AUTHOR-LOGIN IS NOT AUTHORSHIP.** 336 GitHub items carry Jon's login; **171 of the 249
PR/issue opening bodies contain an explicit Claude-authorship marker** — agents open PRs with
`gh pr create` under his credentials. **87 are high-confidence his; 78 openings are UNKNOWN and are
not counted either way.** The fetcher splits them and never folds the ambiguous class in.

Two of the five constraints below exist **only** in channel 2, and two of the timestamps below are
only obtainable from channel 3.

**The GitHub row was added 2026-08-07 after this table nearly produced a false negative on a real
Jon quote — and the first version of that row said "FOUR channels," which a second read called
**OVERSTATED** on the day it was written: at least five further venues were already documented, and
the instrument defining the new row covered only **87 of the 336 items** it could reach. **Naming a
closed set is the defect; the near-miss below is only the symptom.** *"Focusing on 100% generally makes performance worse in humans"* has **0 hits in
`history.jsonl`, 0 under any `## Human` turn in any main transcript, and of 156 JSONL lines
containing it exactly one is `isMeta: true` — which opens "The coordinator sent a message while you
were working:", so it is the coordinator quoting it, not Jon saying it.** On the three-channel rule
that is a quote with no primary. **It is PR #122 review comment `3653971690`, `jonsch201-commits`,
2026-07-27T01:49:54Z.** The wiki page carrying it was right all along; the *search procedure* could
not see the channel. **This rule is invoked precisely to license the conclusion "no primary exists,"
so an incomplete enumeration here is the most expensive kind in the repo** — and one sentence has
already been retired on exactly that reasoning.
