---
kind: reference
slug: constitution-stale-lines-retired
status: LIVE
retired_from: CLAUDE.md
retired_on: 2026-09-12
---

# Lines retired from CLAUDE.md because they were stale, not because they were long

Everything above kept its words and changed its address. **These lines were RETIRED: they asserted
something that is no longer true, or they were structure that did not survive the reorganisation.**
They are recorded here rather than deleted - *"Yeah no deletion. And no writing PII to Github."*
(Jon, 2026-08-09) - and each carries what replaced it.

`[measured 2026-09-12 21:5x, in the order the receipt reported them]`

| retired line, verbatim | why | what replaced it |
|---|---|---|
| the four-item **Skills Loaded** list (`frame-before-commit`, `temporal-context`, `session-order`, `wiki-master`) | **45 skill directories on disk.** The list was written in 2026-07 and named 9% of them | a `## Skills` section that says run `ls skills/` and names no skills |
| *"`~/.claude/` is managed by `claude-foundational-layer` repo. Run `sync-universal.sh` after pulls (the SessionStart hook also runs it automatically)."* | true but incomplete: it says nothing about the receipts, or about the probe that reports a divergence the sync cannot fix | a References line naming both |
| *"Full working context: see foundational layer project in claude.ai"* | a pointer to a surface no CFL session can read | dropped; `wiki/index.md` is the pointer |
| *"Goals: `claude-foundational-layer/raw/references/goals.md`"* | the path is written from OUTSIDE the repo it is in - a leftover from when this file was the global layer | `raw/references/goals.md` |
| *"Packet A/B work order (2026-07-18): `exchange/packet-a-work-order-2026-07-18.md`"* | a single July work order sitting in the constitution as if it were current state | dropped; state is `wiki/index.md` |
| *"`wiki/log.md` … it is 409,585 B `[measured 2026-08-24]`"* | **577,102 B measured 2026-09-12.** A dated number that reads as checked | the same warning with no number, and an instruction to `wc -c` it |
| `### Cold session behavior` | an empty heading whose only content was the H1 below it | dropped |
| `# Read at session open, in this order` | **an H1 in the middle of the document**, nested under an H3, so every outline tool read the file as two documents | `### Read at session open, in this order` |
| `# Compact instructions` | the same defect, at the foot of the file | `## Compact instructions` |

## The pattern worth keeping

**Four of the nine were stale MEASUREMENTS, and all four carried a date stamp.** A date stamp makes a
number look verified when all it records is that someone looked once. The file's own subject is
measure-before-you-state, and it was the least accurate document in the trunk about itself.

**The fix that generalises is not "re-measure these four."** It is: a constitution states rules and
names the command; it does not cache the command's output. Where a count is genuinely load-bearing,
it belongs in an instrument that recomputes it.

---

## The retired lines, byte-for-byte, so `grep -F` resolves

    # Claude Personal Context — Jon
    ## Skills Loaded
    - `frame-before-commit` — divergent reasoning protocol
    - `temporal-context` — timestamp and session state
    - `session-order` — cold session open behavior
    - `wiki-master` — wiki ingest, query, lint
    - `~/.claude/` is managed by `claude-foundational-layer` repo. Run `sync-universal.sh` after pulls (the SessionStart hook also runs it automatically).
    - Full working context: see foundational layer project in claude.ai
    - Goals: `claude-foundational-layer/raw/references/goals.md`
    - Packet A/B work order (2026-07-18): `exchange/packet-a-work-order-2026-07-18.md`
    **Log:** `wiki/log.md` — all past operations; consult for session history. ⚠️ **NEWEST ENTRY FIRST — it is 409,585 B `[measured 2026-08-24]` and is the second-largest file in the tree. Never read it whole.** `[verified 2026-08-24: no CFL hook, skill or procedure reads it whole — this line is a guard against a reader doing it, not a report of one that does.]`
    ### Cold session behavior
    # Read at session open, in this order
    | ⭐ **SIBLING TRUNKS' MAIN session JSONLs** — `~/.claude/projects/<OTHER-trunk>/*.jsonl`, `type: user` / `origin.kind: human` | **dispatches he types to Personal, Professional, Herald or SSP.** Row 2 covers *subagent* JSONLs **in this project**; this is a different file in a **different project directory** | **CFL's instruments search CFL's roots.** `find_answer.py` covers 9 tracked roots and **none of them is another trunk.** Added 2026-08-08 after a Jon ruling sat unreachable for 20 minutes in a live sibling session on this same disk |
    | ⭐ **`raw/Anthropic_zips/*.zip`** | Jon's claude.ai **message attachments** and full conversation bodies, inside archives — export zips this repo already stores. | **Every instrument here walks the filesystem; a zip member is not a file.** `[measured 2026-08-08]` `extracted-*` directories existed up to `extracted-1785689196` (the 08-02 export) when this row was proposed — the 08-05 and 08-08 exports had none, so both were unreadable to every search run against them. **This is the row that nearly cost the launch's most expensive question**: a peer lane searched six ways — FRAME content/filenames across three repos plus the SSP trunk, a target phrase across the 2,206-file corpus, every `*.jsonl` under `~/.claude/projects` (279 Personal, 489 CFL, 33 Professional, 146 XC, plus worktrees and `subagents/`) — and wrote *"Unsearchable by any tool here."* The FRAME bodies were sitting in an unextracted zip in this repo's own `raw/`, and Jon had already said where: *"Frame boddies are in anthropic zip."* **By the time this row was landed, a concurrent corpus-parser lane had already extracted both gaps** (`extracted-1785905488`, `extracted-1786190809` — 29 `extracted-*` dirs total, re-measured 2026-08-08 07:5x) — so the specific gap that motivated this row closed within the hour, but the *class* of gap (zip members invisible to filesystem-walking search) is what the row exists to name. |
    | ⭐ **`type: attachment` / `attachment.type: queued_command` entries in the MAIN session JSONL** — Jon's messages typed WHILE a turn runs, held in the queue; the verbatim text is in the entry's `prompt` field. | Mid-turn dispatches to the main session. Found 2026-09-01 ~22:5x: his four 09-01 mid-turn messages ("you did not sufficiently groun into the wiki…", "Ya failed to recheck things upon wake…", "I bet we don't even have the full knowledge base…", the `/wake and fix issues` order) exist ONLY in this class (9041f3b0 JSONL lines 10493/10993/11508/11509) plus `history.jsonl`; a compact consumed the queue before any became a `type: user` turn. | Every window renderer reads `type: user`; the compact summary then carries the text as machine paraphrase, and a searcher of windows concludes the primary is lost. It is not — the bytes are on disk under a type nobody reads. Row 2 covers the SUBAGENT isMeta class; this is the main-session queue class. |
    - ⛔ **NO WRITING PII TO GITHUB — and this one binds every write path, not one record.**
      wider than, his standing *"Not in the github, yes on G."*** ⭐ **The soul lane flagged the
      keep json"* is an obligation and not a preference.** ⚠️ It lands against a known destroyer:
      > ⛔ **AND A RULING FROM BETWEEN THE TWO WAS MISSING FROM THIS FILE ENTIRELY UNTIL 2026-08-23.**
      > ⭐ **THIS RULING HAS A HALF NOBODY CARRIES: OVER-SCRUBBING IS A VIOLATION, NOT A SAFE DEFAULT.**
      > **earlier and more specific** (the consciousness-framing GitHub is named out). ⛔ **The reading
      > ⚠️ **And an approval was sitting unused inside the same day's mail:** 2026-08-11 ~16:3x, Jon
      > reading our own mail.** ⛔ **Read-and-summarized is not landed.**
      > ⚠️ **AMENDED BY JON 2026-08-19 (~20:34 CDT) — the fence is QUALIFIED BY REACHABILITY, not
      ⭐ **QUALIFIED BY JON HIMSELF, 2026-08-20 — and this qualifier was MISSING from both constitutions
      ⛔ **READ BOTH TOGETHER OR YOU GET THE RULE WRONG IN ONE OF TWO DIRECTIONS.** The 08-03 ruling is
      pace relaxes.** ⚠️ **Quoting the 08-03 line alone turns a situated complaint into a permanent
      ⭐ **AND THE LAST SENTENCE IS THE OPERATIVE ONE, because it says what earns the relaxation:**
      ⛔ **HOW THIS WAS FOUND, because the method matters more than the quote.** A drain lane verified
      this primary and still filed the row as **"UNDISPOSITIONED — NEEDS JON."** ⭐ **The evidence was in
      ⛔ ***"'this needs Jon' is the most comfortable sentence in this program. It ends a lane, it sounds
    A **foreground, interactive, top-tier session** that **runs nothing itself** — it coordinates project managers and the master fleet, **consults `fable-mirror` WHEN SUPPORT IS LIKELY TO HELP — a judgment, not a rule** (A1-v2, Jon 2026-08-09: *"You should consult when it is likely that support will be helpful. You were only doing it every time as training wheels."* ⛔ **SIGNAL = the answer lives in the corpus and you would otherwise guess, above all before writing *"no primary exists"*. NOTICE = anything CFL measured itself, build work, or a verbatim relay.** Both always and never are ways of not deciding, and CFL did both inside a week) (the four triggers are enumerated once, in charter clause A1 — *"fable mirror is required period."*, Jon, `exchange/mirror-consult-digest-2026-08-03.md:35`, ruled after being shown the mirror was 29% of spend), and **always closes a run with a coordinated standard update** (which now also regenerates the `canonical` branch). Charter: `exchange/coordination-charter-2026-07-21.md`. **The mirror stays "advisory" in AUTHORITY — it ratifies nothing, flips no status, and is never a substitute for a Jon Gate. It is NOT "advisory" in the sense of optional; that reading is retired** (charter A3). Dispatching ≠ executing; delegation is the whole job. It is a **session role, not** a `.claude/agents/` definition. BGIsolation is a **membrane with exactly two crossings** — mirror corpus in, escalation packets out; no third without a new ratification.
    # Compact instructions
