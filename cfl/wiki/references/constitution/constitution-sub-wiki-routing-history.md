---
kind: reference
slug: constitution-sub-wiki-routing-history
status: LIVE
moved_from: CLAUDE.md
moved_on: 2026-09-12
moved_by: CFL coordinator, on Jon's instruction
---

# Sub-wiki routing — why the table names its repo

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

**Where the live instruction now lives:** `CLAUDE.md` → *Sub-wiki routing*.

---

⛔ **EVERY PATH BELOW IS IN THE `claude-foundational-layer` REPO, and until 2026-08-10 this table did
not say so.** This file syncs to `~/.claude/CLAUDE.md`, so it is read by sessions in EVERY trunk —
and `[measured 2026-08-10]` **`wiki/personal`, `wiki/home` and `wiki/pro` do NOT EXIST in the Claude
Personal trunk.** A session there follows this table, finds no directory, and **reads
absence-of-directory as absence-of-knowledge.** ⭐ Herald raised it; the routing was pointing every
trunk at one trunk's layout.

---

## ⛔ ONE CLAUSE IN THE BLOCK ABOVE IS NOW FALSE, and it is kept because it is history

The extract says *"This file syncs to `~/.claude/CLAUDE.md`."* **It no longer does.** The 2026-08-17
split ended that: `sync-universal.sh` copies **`CLAUDE-UNIVERSAL.md`** to `~/.claude/CLAUDE.md`, and
its own comment says so — *"CLAUDE.md stays in this repo and stays CFL's own; it loads for CFL
sessions as the project file."* `[verified 2026-09-12 21:2x by reading sync-universal.sh lines 37-47.]`

⭐ **The clause's REASONING survives its own falsification and is why the paragraph was written:** a
table naming one trunk's layout routed every trunk. The sync no longer carries CFL's constitution
outward, so the fence now is the one in the live text — **ask the trunk you are in what it has.**

---

## The reworded line, kept in its original bytes

⚠️ **This paragraph was not moved — it was REWORDED in place on 2026-09-12, because its second
sentence now duplicated the fence hoisted to the top of the section.** The live text keeps the
household fact and drops the repeat. `constitution_extract_receipt.py` flagged these three lines as
UNACCOUNTED, which is exactly what it is for: **a rewrite and a deletion look identical to it, so it
reports both and lets a reader dispose of them.** The original bytes, so `grep -F` still resolves:

⚠️ **In the Claude Personal trunk the layout is its own** — household material lives at
`wiki/household/`, not `wiki/personal/`. `[measured]` **Ask the trunk you are in what it has; do not
infer it from this table.**
