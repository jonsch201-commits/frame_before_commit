---
kind: reference
slug: constitution-where-jons-words-live
status: LIVE
moved_from: CLAUDE.md
moved_on: 2026-09-12
moved_by: CFL coordinator, on Jon's instruction
---

# Where Jon's words live - the venue catalogue, and it is KNOWN-INCOMPLETE

**THIS IS THE OPERATIVE PAGE, not an archive.** Read it before writing "no primary exists" - that is
the only sentence this catalogue exists to license, which makes an incomplete enumeration here the
most expensive kind in the repo. `CLAUDE.md` carries the rule; the rows are here.

**THE CLOSURE TEST:** a venue belongs on this page once any Jon utterance is found in it. **Add the
row when you find it; never conclude absence from this table.** Searching every row and finding
nothing licenses *"not in the rows I searched"* and nothing stronger.

**Moved out of `CLAUDE.md` 2026-09-12.** Jon had just asked whether the file I had spent the evening
trimming was actually good, and it was not: ten of these cells are 200-word case studies, which is
reference material by definition. The counts that were baked into the rows are deliberately NOT
carried forward as counts - see the note at the foot of this page.

**ORIGINAL LINE PREFIXES PRESERVED BYTE-FOR-BYTE** so `grep -F` of anything that used to be in the
constitution resolves here. Verified by `scripts/audit/constitution_extract_receipt.py`.

---

**`exchange/CARRIER.md` says "Authoritative wording lives in `CLAUDE.md`." Until 2026-08-07 it did
not — CARRIER quoted three standing constraints and `CLAUDE.md` held none of them.** A pointer to a
file that does not hold the thing is the same defect as the cold-open read-chain above. Resurrected
2026-08-07 and landed here so the pointer is true.

**Jon's words land in MANY venues and the list below is KNOWN-INCOMPLETE. Searching every row and
finding nothing does NOT license "this quote has no primary" — it licenses "not in the rows I
searched."**

**The closure test, because a list without one drifts back into being treated as complete:** a
venue belongs here once any Jon utterance is found in it. **Add the row when you find it; never
conclude absence from this table.**

| Channel | What it holds | Why it gets missed |
|---|---|---|
| `raw/transcripts/**` (2,206 files) | `## Human` turns | the only one anybody queries |
| `~/.claude/projects/**/subagents/agent-*.jsonl` | `type: user` + `isMeta: true` — messages he sends **mid-turn to a subagent** | **never appear in any main transcript** |
| `~/.claude/history.jsonl` (1,742 entries) | **every typed prompt**, with a wall-clock ms timestamp | survives the JSONL retention sweep; almost never read |
| **SIBLING TRUNKS' MAIN session JSONLs** — `~/.claude/projects/<OTHER-trunk>/*.jsonl`, `type: user` / `origin.kind: human` | **dispatches he types to Personal, Professional, Herald or SSP.** Row 2 covers *subagent* JSONLs **in this project**; this is a different file in a **different project directory** | **CFL's instruments search CFL's roots.** `find_answer.py` covers 9 tracked roots and **none of them is another trunk.** Added 2026-08-08 after a Jon ruling sat unreachable for 20 minutes in a live sibling session on this same disk |
| **`raw/github-comments/` — 87 high-confidence Jon-typed of 336 under his login** | **GitHub: issue comments, inline PR-review comments, review bodies** — `scripts/audit/fetch_jon_github_comments.py`, read-only | **this table said "three" until 2026-08-07 and NOTHING in `scripts/` had ever read them** |
| **`raw/Anthropic_zips/*.zip`** | Jon's claude.ai **message attachments** and full conversation bodies, inside archives — export zips this repo already stores. | **Every instrument here walks the filesystem; a zip member is not a file.** `[measured 2026-08-08]` `extracted-*` directories existed up to `extracted-1785689196` (the 08-02 export) when this row was proposed — the 08-05 and 08-08 exports had none, so both were unreadable to every search run against them. **This is the row that nearly cost the launch's most expensive question**: a peer lane searched six ways — FRAME content/filenames across three repos plus the SSP trunk, a target phrase across the 2,206-file corpus, every `*.jsonl` under `~/.claude/projects` (279 Personal, 489 CFL, 33 Professional, 146 XC, plus worktrees and `subagents/`) — and wrote *"Unsearchable by any tool here."* The FRAME bodies were sitting in an unextracted zip in this repo's own `raw/`, and Jon had already said where: *"Frame boddies are in anthropic zip."* **By the time this row was landed, a concurrent corpus-parser lane had already extracted both gaps** (`extracted-1785905488`, `extracted-1786190809` — 29 `extracted-*` dirs total, re-measured 2026-08-08 07:5x) — so the specific gap that motivated this row closed within the hour, but the *class* of gap (zip members invisible to filesystem-walking search) is what the row exists to name. |
| **Secretary's `rulings/` captures of claude.ai conversations** — e.g. `rulings/2026-09-01-jon-rulings-questions-should-open-resident-labeling.md` | Jon verbatim from **claude.ai-seat conversations** — a venue `history.jsonl` STRUCTURALLY never captures (it logs typed CC prompts only). Found 2026-09-01: Soul ran a clean 0-of-19 grep over 3,500 typed prompts for a sentence Jon really said — the search was true and the venue was wrong; the primary sat in Secretary's capture. Fourth same-day instance of primary-in-an-unreachable-venue (zip members, JSONL heredoc bodies, container-volume JSONLs, now this). | claude.ai conversations feel like "the same Jon" but land in NO instrument's roots; only the seat that had the conversation holds the capture |
| **`type: attachment` / `attachment.type: queued_command` entries in the MAIN session JSONL** — Jon's messages typed WHILE a turn runs, held in the queue; the verbatim text is in the entry's `prompt` field. | Mid-turn dispatches to the main session. Found 2026-09-01 ~22:5x: his four 09-01 mid-turn messages ("you did not sufficiently groun into the wiki…", "Ya failed to recheck things upon wake…", "I bet we don't even have the full knowledge base…", the `/wake and fix issues` order) exist ONLY in this class (9041f3b0 JSONL lines 10493/10993/11508/11509) plus `history.jsonl`; a compact consumed the queue before any became a `type: user` turn. | Every window renderer reads `type: user`; the compact summary then carries the text as machine paraphrase, and a searcher of windows concludes the primary is lost. It is not — the bytes are on disk under a type nobody reads. Row 2 covers the SUBAGENT isMeta class; this is the main-session queue class. |
| **`~/.claude/paste-cache/`** | Content Jon pastes into a session that the harness caches separately from the transcript. | Not a project directory, not JSONL, not walked by any tracked-root instrument. `[measured 2026-08-08]` **71 files, 359,311 B** — proposed overnight at 68 files / 352,392 B; re-measured here and the count differs (grew), so the larger number is published and flagged as the fresher one, not the original. |

**THE ZIP ROW IS SPLIT IN TWO, AND JON CORRECTED IT HIMSELF** (2026-08-17, verbatim):
*"Right. And anthropic zips don't include attachments. Hence me putting the full test into a message
here."* `[measured 2026-08-17 against the 08-16 export: **46** `attachments[]` DO carry
`extracted_content`; **250** `files[]` carry `file_uuid` and `file_name` and **no content field at
all**.]` **So read the row as "46 attachments' extracted text, plus 250 filenames with nothing
behind them" — a search of the export finds the NAME and concludes the file is present.**

**Venues covered by NO row above, so the table is a starting point and never a boundary:**
`AskUserQuestion` selections · Google Docs Jon authors or annotates · claude.ai project instructions
he edits directly · Jon-authored merge-commit messages · message attachments.

**Before concluding a Jon utterance has no primary, grep the OTHER trunks' `~/.claude/projects/`
directories.** With several coordinators running his dispatches fan out to several project
directories, and **each trunk's instruments search only its own** — `find_answer.py`'s nine roots
contain **zero** sibling trunks. *"Not in the tracked roots"* is a statement about a fraction of the
machine, not about the record.

**Case history — the 2026-08-08 find that produced the closure test, and the loss class no
filesystem walk can see (a zip member is not a file):** `wiki/references/constitution/constitution-jon-utterance-venue-history.md`.

**AUTHOR-LOGIN IS NOT AUTHORSHIP.** 336 GitHub items carry Jon's login; **171 of the 249
PR/issue opening bodies contain an explicit Claude-authorship marker** — agents open PRs with
`gh pr create` under his credentials. **87 are high-confidence his; 78 openings are UNKNOWN and are
counted neither way.** The fetcher splits them and never folds the ambiguous class in.

Two of the five constraints below exist **only** in channel 2, and two of the timestamps below are
only obtainable from channel 3.

**This table is invoked precisely to license the conclusion "no primary exists," so an incomplete
enumeration here is the most expensive kind in the repo** — and one sentence has already been retired
on exactly that reasoning. **Case history — the 2026-08-07 near-miss on a real Jon quote, and why the
row's own first draft said "FOUR channels" and was overstated the day it was written:**
`wiki/references/constitution/constitution-github-channel-near-miss.md`.

---

## The counts in the rows above are STALE BY DESIGN, and that is the lesson this page carries

`[measured 2026-09-12 21:5x CDT]` The rows say `raw/transcripts/**` holds **2,206 files** and
`~/.claude/history.jsonl` holds **1,742 entries**. On disk right now: **6,423** and **5,021**.
`wiki/log.md` is cited in `CLAUDE.md` at 409,585 B and is **577,102 B**.

So a constitution whose entire subject is measure-before-you-state was carrying four stale
measurements, and every one of them had a date stamp that made it look checked. **A dated number is
not a current number; it is a claim about one past moment.** The rows are kept with their original
figures because re-typing today's numbers would re-break this page on a fresher date - which is
exactly [[derive-dont-record]].

**Read the rows for the VENUE and the FAILURE MODE. Never for the count. If you need a count, count.**


---

## The section heading, in its original bytes

The `CLAUDE.md` section this page was lifted out of was headed, verbatim:

## Standing constraints — Jon's words, with their primaries

It still is. The heading stayed; the ten-row catalogue under it came here.
