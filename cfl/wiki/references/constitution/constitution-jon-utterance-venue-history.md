---
kind: reference
slug: constitution-jon-utterance-venue-history
status: LIVE
moved_from: CLAUDE.md
moved_on: 2026-09-12
moved_by: CFL coordinator, on Jon's instruction
---

# Jon-utterance venues — the zip loss class, the fifth row, and the GitHub near-miss

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

⛔ **CORRECTED 2026-08-17 BY JON'S OWN WORDS, WHICH NO INSTRUMENT HERE COULD READ UNTIL THE ZIP WAS
PARSED THE SAME DAY.** The row above says the zips hold *"Jon's claude.ai message attachments."*
**Jon, `raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-17-becc33-brief-status-update-and-task-decisions.md`,
`## Human` turn 22, conversation updated `2026-08-17T01:59:34Z` (verbatim):**

> *"Right. And anthropic zips don't include attachments. Hence me putting the full test into a message here."*

**Measured against the 08-16 export the same day, and the truth is split — which is why the row was
able to mislead:**

| class | count | what the zip actually carries |
|---|---|---|
| `attachments[]` | **46** | **`extracted_content` IS present** — text pulled out at upload time and inlined into the conversation JSON. Readable. |
| `files[]` | **250** | **`file_uuid` and `file_name` ONLY. No content field exists at all.** |

**And the archive holds 10 members, every one of them `.json` — zero binary assets.**

⭐ **SO THERE IS A LOSS CLASS NOBODY HAD NAMED: 250 attachment references whose content the export
does NOT contain** — `.docx`, `.png`, screenshots, pasted-text files. Their `file_uuid`s are resolvable
only through claude.ai itself. **A search of the export for one of those filenames finds the NAME and
concludes the file is present.** ⚠️ **Jon's sentence is the operationally correct one: he pasted a full
test inline BECAUSE he could not rely on an attachment surviving.** Read the row as *"46 attachments'
extracted text, plus 250 filenames with nothing behind them."*

**Known venues NOT covered by any row above, each already documented somewhere in this wiki — so
treat this table as a starting point, not a boundary:** `AskUserQuestion` selections (never
captured anywhere — `wiki/references/agent-memory/askuserquestion-answers-not-captured.md`) ·
**Google Docs Jon authors or annotates** · **claude.ai project instructions he edits directly** ·
**Jon-authored merge-commit messages** in git history · message attachments.

⭐ **The fifth row was added 2026-08-08, and the way it was found is the reason the closure test above
is not decoration.** A CFL lane searched for the "Duncan consent file" Jon named in his overnight
directive, found nothing, and — correctly — wrote that its bound was *"not in the tracked roots"* and
that the primary *"may well exist in Jon's head, in a claude.ai session, or in a venue no instrument
here reads."* **All three of those guesses were wrong.** Jon had typed it **twenty minutes earlier**,
as a `type: user` / `origin.kind: human` entry at line 11 of a **live Personal SSP session JSONL on
this same disk** — `35c4e94e-…`, `2026-08-08T05:03:17.820Z`. It surfaced only because that sibling
coordinator **read CFL's file and wrote back**.

**The general form, and it is new: with four coordinators running, Jon's dispatches fan out to four
project directories, and each trunk's instruments search only its own.** A ruling typed to Personal
is invisible to CFL not because it is hidden but because **nobody's search path crosses a trunk
boundary.** *"Not in the tracked roots"* is now a statement about **one ninth of the machine**, and
`find_answer.py`'s nine roots contain **zero** sibling trunks. **Before concluding a Jon utterance
has no primary, grep the other trunks' `~/.claude/projects/` directories** — and note that the letters
channel found this one when no instrument could, which is the same lesson as 2026-07-27.

