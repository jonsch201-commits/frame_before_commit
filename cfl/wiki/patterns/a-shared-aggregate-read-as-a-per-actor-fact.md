---
format: cfl-page/v1
kind: pattern
slug: a-shared-aggregate-read-as-a-per-actor-fact
title: "A Shared Aggregate Read as a Per-Actor Fact"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "shared ledger last row read as one hook's last firing; shared hook-payload directory newest file read as one session's death time; group by session_id take max per group; selftest rows mistaken for hook rows; a directory yields one death time for N sessions always the luckiest one; multi-writer artifact single-writer inference"
aliases: [newest-file-in-a-shared-directory-is-not-your-status, group-by-actor-then-max, ledger-last-row-is-not-the-hooks-last-firing, multi-writer-read-as-single-writer]
generated_by: lane W-1c (fable) session e515d858
state: current
state_note: "three seats in one day (2026-09-02) reported a shared artifact as their own status: CFL read a frozen G: ROUTING-LEDGER's last row (and two selftest rows) as its hook's last firing; Personal read a shared hook-payload directory's newest file as one session's death time (four sessions, four times, found only by grouping on session_id -- Soul); a channel read as an author (Soul, morning; see delivery-channel-is-not-authorship). Instrument stated (group by actor id, max per group), not yet wired as a lint."
probe_sealed: "On 2026-09-02, how many distinct hook last-fire times did grouping Personal's shared hook-payload directory by session_id yield, versus the one time the directory's newest file gave, and were the two 09:2x rows in CFL's clone ROUTING-LEDGER hook firings? => Four by session_id (20:21:47, 20:21:56, 08:23:24, 08:43:53) versus one (08:43:53, the luckiest); and no -- the two rows at 2026-09-02T14:22:39Z/14:26:36Z carry id UNKNOWN and transcript 'UNKNOWN — not in payload' and were reassigned to the H-4 selftest in the letter's Correction 1, accepted by Soul and Herald. TRUSTED"
---

## Struggle

An artifact written by MANY actors (a shared ledger, a shared hook-payload directory, a delivery
channel) is read as if it described ONE actor: its last row becomes "my hook's last firing", its
newest file becomes "this session's death time", its channel becomes "who sent it". The read is
mechanically true of the aggregate and false of the actor, and it always errs toward the luckiest
actor, because the newest entry in a shared artifact belongs to whoever wrote last.

- `exchange/su-close/AUTOCOMPACT-TEST-cfl-pre-2026-09-02.md:17` [verbatim] (cropped) -- CFL
  dated its own hook death from a shared ledger: "no hook has written anything since 2026-09-01
  22:59 CDT (G: exchange/ROUTING-LEDGER.md last row 03:59:53Z; POSTCOMPACT-STATUS.md mtime
  23:00)". `ROUTING-LEDGER.md` is appended by every SubagentStop fire of every lane; its last row
  is the last WRITER's time, and the G: copy was a frozen checkout besides (`exchange/outbox/LETTER-2026-09-02-cfl-to-all-trunks-HOOKS-SESSION-SCOPED-DEAD-AND-USAGE-METER-LIVE.md:13`).
- `exchange/outbox/LETTER-2026-09-02-cfl-to-all-trunks-HOOKS-SESSION-SCOPED-DEAD-AND-USAGE-METER-LIVE.md:18`
  [verbatim] (cropped) -- Correction 1: "The two 09:2x rows in CFL's clone ROUTING-LEDGER are
  the H-4 selftest's rows, not hook firings. CFL's hook evidence rests on the Stop hook's
  cwd-local artifact instead". Two rows in the shared ledger were read as the hook being alive
  in the interactive session; the actor that wrote them was a lane's selftest.
- `exchange/ROUTING-LEDGER.md:5516-5517` [verbatim] -- the two rows themselves: `| 2026-09-02T14:22:39Z
  | auto | UNKNOWN | subagent | UNKNOWN | UNKNOWN — not in payload | PENDING | - |` and the same
  shape at `14:26:36Z`. The row's own agent-id column says UNKNOWN and its transcript column says
  the payload carried none; the last rows with a real id (`:5514-5515`, `a8a0fc`, `ac8803`) are
  at `03:53:01Z`/`03:53:34Z`, i.e. 22:53 CDT 09-01. The disproof of "hook firing" was in the
  row's own column (same shape as [[the-disproof-was-in-the-rows-own-column]]).
- `wiki/intake-triage/H4-rp29-2026-09-02.md:175-181` [verbatim] (cropped) -- the lane that
  produced them read them the same way, as its own lifecycle: "the real `.claude/settings.json`
  SubagentStop wiring fired ... for this lane's own agent lifecycle -- two `auto | UNKNOWN |
  subagent | UNKNOWN | UNKNOWN — not in payload | PENDING | -` rows landed at
  `2026-09-02T14:22:39Z` and `14:26:36Z`. This was not triggered by anything this lane's code
  wrote -- it is the harness's normal operation". Both readers -- the lane and CFL -- took a
  shared artifact's newest rows as their own actor's event; the parent session's hooks were dead
  at the time (letter `:9`), which is why the letter reassigned them.
- `exchange/outbox/LETTER-2026-09-02-cfl-to-all-trunks-HOOKS-SESSION-SCOPED-DEAD-AND-USAGE-METER-LIVE.md:22`
  [verbatim] (cropped) -- Personal's instance, found by Soul: "Replace \"three seats, three death
  times\" with the COUNT: at least five distinct last-fire times across two trunks (CFL 22:58:05
  09-01; Personal 20:21:47, 20:21:56, 08:23:24, 08:43:53 by session_id), two of which predate the
  earliest claimed Drive-fault onset by ~3 h." Item 1 (`:9`) had carried Personal's death time as
  the single value 08:43:53 -- the newest file in a directory four sessions wrote to.
- `exchange/outbox/LETTER-2026-09-02-cfl-to-all-trunks-HOOKS-SESSION-SCOPED-DEAD-AND-USAGE-METER-LIVE.md:23`
  [verbatim] -- the instrument and the day's count, in Soul's words: "never read a shared
  hook-payload directory's newest file as a session's status; group by session_id and take the
  max per group. A shared directory yields one death time for N sessions, always the luckiest
  one. The same shape took three seats today (a frozen ledger read as a hook's last firing; a
  channel read as an author; a directory read as a session)." The third instance, the channel
  read as an author, is the morning's `queued_command` case on its own page:
  [[delivery-channel-is-not-authorship]].
- `exchange/elders/THREE-WAY-CONSULT-2026-09-02.md` was checked for the ledger reading (grep for
  `ledger`, `last row`, `23:15`, `22:58`, `selftest`, `session_id`): 0 hits across its 11,695 B; it
  does not carry this instance and is not cited for it.

## Generalization

A multi-writer artifact answers questions about the POPULATION of writers -- who wrote last,
how many wrote, the max over all -- and a reader who wants a fact about ONE writer must first
partition by the writer's identity and then take the statistic inside the partition. Skipping the
partition does not produce a random error; it produces a biased one, because "newest" over the
union is the max over all actors and so reports the healthiest actor's status for every actor.
That is why three seats in one day each concluded their own instrument was fresher than it was
(a hook alive at 09:2x, a session alive until 08:43:53), and why the correction in every case
was a strict count going UP (one time became four; "three seats, three death times" became "at
least five"). The instrument is Soul's one-liner: group by actor id, max per group -- and,
before that, ask whether the artifact HAS an actor-id column to group on (the ledger's has one,
and the two misread rows carried UNKNOWN in it, which was the answer). The same rule governs a
channel (partition by `commandMode`/`origin.kind`, not by `attachment.type`) and a receipt
directory (partition by the session id in the filename). Related:
[[recorder-and-check-cannot-see-the-same-loss]] for the case where the writer that died is
exactly the one absent from the aggregate, and
[[a-logs-first-line-is-the-instruments-sensitivity]] for the time-axis version of mistaking an
instrument's boundary for a fact about the subject.

## Counter-evidence

A SINGLE-WRITER artifact IS a per-actor fact, and the day's correction leaned on one. The Stop
hook keeps its block budget in a per-session count file:
`.claude/hooks/pre-stop-consult.sh:275` [verbatim] --
`COUNTER="$STATE_DIR/prestop-${safe_session}-${detail}.count"` -- the session id is IN the
filename, so `.claude/hooks/state/prestop-<session_id>-<turn>.count` is written by exactly one
session and its mtime is that session's last block without any grouping (this clone holds two,
`prestop-56676636-...-6.count` and `prestop-harness-0000-8.count`, each one actor's). That is the
artifact Correction 1 moved CFL's evidence onto ("no count file for any turn since", letter
`:18`). But the log in the same directory is NOT single-writer: `.claude/hooks/pre-stop-consult.sh:73`
[verbatim] -- `LOG="$STATE_DIR/pre-stop-consult.log"` -- one file, appended by every session
whose cwd is that checkout, and this clone's copy already interleaves two (`turn=8` at 09:17:35
and `turn=6` at 13:15:40). So the same directory holds both kinds, and the rule is per file:
"last line of `pre-stop-consult.log`" is a population fact unless the checkout has had one
session, which on G: at 22:58 it plausibly had (only e515d858 ran there) -- which is why the
letter's use of it survived while the ledger read did not. `.claude/hooks/state/` count files
per session id by filename: single-writer. `pre-stop-consult.log`, `exchange/ROUTING-LEDGER.md`,
Personal's hook-payload directory: multi-writer.

## Motivates

none yet -- no `skills/` entry states "before reading an artifact's newest entry as one actor's
status, name the artifact's writer population; if more than one, group by actor id and take the
max per group" as a checkable step. The instrument exists as one sentence in a letter
(`exchange/outbox/LETTER-2026-09-02-cfl-to-all-trunks-HOOKS-SESSION-SCOPED-DEAD-AND-USAGE-METER-LIVE.md:23`)
and nowhere as code.

## Probe

Sealed question above. Falsified if Personal's hook-payload directory, grouped by session_id,
yields fewer than four distinct max times (so the "four sessions, four times" count was itself an
aggregate error); or if the two rows at `exchange/ROUTING-LEDGER.md:5516-5517` are found to have
been written by a live SubagentStop fire of session e515d858 (e.g. a `ROUTED-KEYS.jsonl` entry or
a hook-state file with that timestamp), in which case Correction 1 reassigned them wrongly and the
H4 reading at `:175-181` was right; or if `pre-stop-consult.sh` is found to derive `COUNTER`
from something other than the session id (so the count file is not single-writer and the
counter-evidence bound is wrong).
