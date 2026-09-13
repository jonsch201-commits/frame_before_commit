---
kind: reference
slug: constitution-wayfinder-map-derivation-history
status: LIVE
moved_from: CLAUDE.md
moved_on: 2026-09-12
moved_by: CFL coordinator, on Jon's instruction
---

# Wayfinder-map derivation — the case history behind CLAUDE.md's read-at-open item 4

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

**Where the live instruction now lives:** `CLAUDE.md` → *Read at session open* → item 4.

---

   > ⛔ **CORRECTED 2026-08-24 BY A `/dream` SWEEP, and this line had been false for SEVEN DAYS.**
   > This item read **`wiki/tracker/wayfinder-cfl.md` — the live wayfinder map**, full stop.
   > `[measured 2026-08-24 ~21:3x, this session, by opening both files]`
   >
   > | | `wayfinder-cfl.md` | `wayfinder-pr2-2026-08-23.md` |
   > |---|---|---|
   > | its own frontmatter says | ⛔ **`canonical: true`** | ⭐ **`status: "LIVE"`** |
   > | last commit touching it | ⛔ **2026-08-17** (`f36f2a1`) | **2026-08-23** (`60ff061`) |
   > | names the other file | ⛔ **0 times** | — |
   >
   > ⛔ **So a cold session obeying this list landed on a map SEVEN DAYS STALE that asserts its own
   > canonicity, and resumed at `M-3` while the live charter's first unclosed ticket was `P2-14`.**
   > ⚠️ **NOTHING ERRORED. The stale map opens, parses, and reads as authoritative** — an existence
   > check passes on a file whose CONTENT is superseded.
   >
   > ⭐ **AND THE PARAGRAPH DIRECTLY BELOW THIS ONE IS ABOUT THIS EXACT DEFECT.** It explains that the
   > read-chain exists because *"the instruction and the thing it governs must be reachable from the
   > same starting point, or the instruction is decoration."* ⛔ **The chain was reachable and pointed
   > somewhere stale, which that sentence does not cover — REACHABLE IS NOT CURRENT.**
   >
   > ⛔ **THE FIX IS A DERIVATION, NOT A NEW FILENAME. Swapping in `wayfinder-pr2-…` would re-break
   > this file the hour PR-3 is chartered** — the same defect with a fresher date, which is CFL's own
   > named characteristic failure ([[derive-dont-record]]). **So:**
   >
   > ⭐ **DERIVE THE LIVE SET: the `kind: wayfinder:map` files in `wiki/tracker/` whose frontmatter
   > says `status: LIVE`. ENUMERATE THEM ALL AND REPORT THEM ALL.**
   > ⚠️ **`canonical: true` is NOT the field to derive on** — the superseded map carries it and every
   > live map does not.
   >
   > ⛔ **THE RULE WAS EXERCISED THE MINUTE IT WAS WRITTEN, AND ITS FIRST RUN CORRECTED THE RULE.**
   > `[measured 2026-08-24 ~21:4x: 6 `wayfinder:map` files; **1 SUPERSEDED, 3 LIVE, 2 carry no
   > `status:` field at all**.]` **The first draft of this item said "if exactly one is LIVE that is
   > the map."** ⛔ **Exactly one never was. CFL RUNS THREE CONCURRENT MAPS** —
   > `wayfinder-pr2-2026-08-23.md` (the sitting's charter), `wayfinder-exchange-reorg.md` (T-10) and
   > `wayfinder-memory-cognition-federation.md` — **and they are all genuinely live, on different
   > scopes. Multiplicity is not the defect; ASSUMING SINGULARITY WAS.**
   >
   > ⭐ **SO THE RESUME RULE IS:** report every LIVE map with its first unclosed ticket, then resume
   > on the one whose SCOPE matches the directive you woke to. ⛔ **If no directive selects one, say
   > so and ask — never pick by mtime, which is precisely how a stale map wins.**
   > ⚠️ **The 2 maps with NO `status:` field are UNKNOWN, not live and not dead. UNKNOWN dominates.**
   >
   > ⛔ **THE RULE STANDS; ITS ILLUSTRATIVE COUNT HAS EXPIRED, AND THE NUMBERS ABOVE ARE KEPT AS
   > HISTORY, NOT AS STATE.** `[re-measured 2026-09-05 ~14:4x CDT: **22** `wayfinder:map` files in
   > `wiki/tracker/`, of which **17 declare `status: LIVE`**.]` ⛔ **The sentence "CFL RUNS THREE
   > CONCURRENT MAPS" and the three filenames beside it are TWELVE DAYS OLD and off by roughly
   > 6×.** ⚠️ **A seat that reads them as current expects three and meets seventeen** — and the two
   > worst failures are opposite: hunting for a fourth that "should not exist," or picking by mtime,
   > which this very item forbids.
   >
   > ⭐ **This is [[derive-dont-record]] firing on the paragraph that teaches derive-don't-record.**
   > **The instruction was right and its example rotted** — which is why the DERIVATION, never the
   > filenames, is the operative half. ⛔ **Do not update the three names to seventeen names; that
   > re-breaks this file on a fresher date, which is the exact error the item already names.**
   > ✅ **Run the derivation. `scripts/audit/ticket_queried.py` prints every LIVE map with its open
   > tickets, and grades each ticket's `queried:` field** (built 2026-09-05, selftest 9/9 —
   > and **its own first run mis-reported 11 of 16 maps as ticketless because its parser matched one
   > heading convention**, which is the same class one layer down).
   >
   > ⭐ **Note what the derivation did on its first run, because it is the inversion this trunk keeps
   > failing the other way: it refused to return an answer and returned a QUESTION instead — and the
   > question was true.** ⛔ **The hardcoded pointer it replaced returned a confident answer that had
   > been wrong for seven days.**


---

## The item's own heading, before it was cut to eight lines

The live instruction was rewritten again on 2026-09-12 21:4x after Jon read the first pass:
*"I don't get why their are so many emojis, or why we need that much about the wayfinder map details
in there."* Item 4 went 67 lines -> 18 -> **8**, and the marker glyphs came out of the whole
constitution. The two heading lines below are the pre-cut bytes, kept so `grep -F` still resolves:

4. ⛔ **THE LIVE WAYFINDER MAP — AND IT IS NOT ALWAYS `wayfinder-cfl.md`. DERIVE IT, NEVER
   HARDCODE IT.** **Resume at the first unclosed ticket OF THE MAP YOU DERIVED.**
