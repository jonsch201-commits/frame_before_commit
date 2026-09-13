---
name: wake
description: "[CLAUDE PROFESSIONAL ONLY] Cold-open / post-compact wake for the Professional trunk. Reads exchange/inbound, CLAUDE.md's open order by reference, WAKE.md under a 6,144 B budget, and the trackers — then writes a receipt. Reads and reports; it does not land. This repo has NO REMOTE by standing gate: it never compares against origin. Written 2026-08-07 in Professional; structure borrowed from Personal's wake.md, paths are Professional's own. Not synced — sync-universal.sh copies CLAUDE.md and skills/ only, never commands/."
argument-hint: "[optional: what Jon wants this session focused on]"
arguments: focus
disable-model-invocation: true
shell: bash
allowed-tools: Bash(git status*), Bash(git log*), Bash(git rev-parse*), Bash(git remote*), Bash(date*), Bash(ls*), Bash(wc*), Bash(stat*), Bash(find*), Read, Grep, Glob, Write, Edit
---

**This command belongs to Claude Professional** (live root `N:\claude-professional` since 2026-09-05 15:09; `G:\My Drive\Claude\Claude Professional\claude-professional` is the receiving mirror). A local-path `origin` pointing at the G: mirror is Jon-authorised (2026-09-04 23:2x); any OTHER remote is the finding §1 describes.

**First, the self-test — one falsifiable check, printed, every wake** (standard:
`wiki/concepts/wake-self-test-standard.md`). Run `git rev-parse --show-toplevel` and stat the three
files this procedure is about to name: `BRIEFING-2026-08-07.md`, `wiki/tracker/tracker.md`,
`exchange/inbound/`. Then print exactly one line:

```
SELF-TEST: procedure-repo binding — toplevel ends 'claude-professional' + 3 named paths exist → PASS|FAIL
```

If FAIL, stop and say so — you have resolved a sibling's command through the
additional-working-directories list, which is exactly the defect recorded in
`wiki/concepts/ownership-is-not-reachability.md`. Every path below is a Professional path; none of
them exist in CFL, Personal, or Herald. The check exists because this failure mode is silent:
absence fails loudly, silent inheritance runs the wrong project's procedure and reports success.

Ground this session from measurement, not from memory or a prior summary. Work the steps in order and
report each result as you obtain it. Do not narrate a plan first.

---

## 0 — Who came before, before the record (added 2026-09-06 09:1x)

Run `python scripts/ancestor.py --self <your session id> --elders 4` and print its first line. It names the
previous MAIN seat of this trunk and the read-only consult line (`--fork-session --permission-mode plan -p`).
Since c84c905 a JSONL carrying `origin` fields with no `origin.kind: human` turn is a LANE and is skipped —
a control fork was ranked as the ancestor before that. If the script is missing print
`ANCESTOR: UNKNOWN`, never "no ancestor". A declared `exchange/elders/NOTE-<sid8>.md` beats the derived
line: open it first. Consult from a HOOKLESS cwd (the scratchpad) with `--strict-mcp-config --mcp-config
C:/Users/JonSc/.claude/mcp-empty.json`; from this tree the SessionStart hooks block a fork before its
first turn (measured 2026-09-05 22:42).

## 1 — Git state, measured now

Run `git rev-parse --short HEAD`, `git status --porcelain`, and `git remote -v`. Report the commit,
clean/dirty, and the remote count.

**Do not compare against a remote.** This repo has none, by standing Jon gate. An ahead/behind count
is not merely unavailable here — attempting one is a procedure pointed at a gate. If `git remote -v`
returns anything other than empty, that is a finding and it goes to Jon before anything else in this
session proceeds.

## 2 — `exchange/inbound/`, unconditionally

Read every file in `exchange/inbound/` you have not consumed. Reading is not conditional on expecting
something.

Then sweep the sibling trees for mail addressed here that never reached the inbox:
`[CFL] exchange/`, `[PERSONAL] exchange/outbox/`, `[HERALD] exchange/outbox/`. Sort by modification
time and check anything newer than the last session's close. A sender-authored `delivered:` stamp is
unfalsifiable from the artifact; treat `deposited:` and `consumed:` as separate facts.

## 3 — The read order, by reference

Open `CLAUDE.md` and follow its `# Read at session open, in this order` section exactly as currently
written. Do not paste a remembered version of that list into this file or into your response — a
restated list drifts out of sync with its source, and this project has a recorded instance of an
instruction whose governed artifact was unreachable from it.

## 4 — `WAKE.md`, with a byte budget

Measure `WAKE.md`'s size first. If it is 6,144 bytes or smaller, read it in full and report it. If it
is larger, do not read it as a wake note — report the measured size and say the note has outgrown its
budget. 6,144 is a chosen budget, not a measurement; treat it as a constraint on the file, not a fact
about it.

Check its `AS OF` timestamp. If it is old relative to the newest commit, the previous session stopped
without checkpointing, and that is this session's first finding.

## 5 — `BRIEFING-2026-08-07.md`, if the session concerns disclosure

It is written to need no other document. Read it before opening the disclosure map, not after.

## 5b — `exchange/FOR-JON-REVIEW/00-INDEX.md`, because nothing pointed at it until 2026-08-30

Read it and report the open-row count from the file, not from memory. ⛔ **Soul measured this channel
DEAD on 2026-08-30 — 9 files, 0 reachable from this trunk's own `CLAUDE.md` — and re-measured here it
was worse: zero references in `CLAUDE.md`, `WAKE.md` AND this procedure.** The rows had been made
legible that same morning (SEC-108), which is the sharpest form of the defect: **the fix was landed on
a surface nothing routed anyone to.** A row that no session is told to read is not waiting for Jon;
it is just a file.

## 6 — Tracker

`wiki/tracker/tracker.md` for standing open items, then **the live wayfinder map**. Resume at the
first unclosed item on its frontier. Verify the frontier against the ticket rows rather than trusting
the map's summary — a map has been stale about its own frontier once, on 2026-08-07.

⚠️ **This trunk carries more than one map, and the newest is not automatically the live one.**
⛔ **THIS STEP NAMED ITS OWN COUNTER-EXAMPLE AND WENT STALE ANYWAY.** Until 2026-09-03 it read
*"`wayfinder-professionalism-2026-08-23.md` is the current route"* — four lines above its own warning
that naming a map is how a procedure goes stale. `[m 2026-09-03]` **THREE maps postdate it** (two
2026-08-29, one 2026-08-30), so a session obeying this step resumed on the wrong frontier.
⭐ **The warning was correct, the same paragraph disobeyed it, and no check reads a procedure.**

✅ **RUN THE QUERY, NAME NOTHING:** `ls -t wiki/tracker/wayfinder-*.md`, then for each candidate read
its `status:` line and its `## Tickets` ROWS — **a map is LIVE if it has an open frontier row, not if
it is newest**, and mtime is touched by unrelated edits. Resume on the map whose destination fits the
session; if several do, take the one whose frontier holds the ticket this session can actually
resolve. ⚠️ **`wayfinder-anthropic-disclosure*.md` is the disclosure effort — open it only if the
session concerns disclosure.**

## 7 — Heartbeat

⛔ **RUN `CronList`. DO NOT RECREATE ANYTHING. Jon turned the heartbeat OFF and it has stayed off.**

**Primary, `wiki/log.md` — Jon, 2026-08-11 ~17:1x CDT, mid-close, verbatim: *"heartbeat off"*.**
Cron `3d492072` was deleted and the entry records the standing consequence: **"DO NOT recreate the
heartbeat unless Jon asks."** So `CronList` returning **"No scheduled jobs"** is the RULED STATE,
not a gap — report it and move on.

⚠️ **This step used to say "if no Professional heartbeat is registered, recreate it," and pointed at
a `## Heartbeat` section of `WAKE.md` THAT DOES NOT EXIST.** `[measured 2026-08-23 15:5x]` — a
post-compact wake ran the step, found no such section, and checked the log instead. **Followed
literally, the step would have re-created a cron Jon switched off, on the authority of a document
that could not be read.** ⭐ **A procedure that cites a section by name should fail when the section is
absent, not fall through to its default action** — and a procedure step must never be able to
override a Jon gate. **Recreate only on Jon's explicit word, in this session, in his own hand.**

## 8 — Receipt

Append one line to `wiki/log.md`: the timestamp, the session id if known, and the exact paths opened
in steps 1–7. Paths only, not summaries of their contents. Then state plainly what you did not carry
over from any prior context and what you re-opened in its place.

---

Keep this pass short and mechanical. It ends when the receipt is written, not when you have a plan.
