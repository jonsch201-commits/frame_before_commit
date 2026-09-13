---
format: cfl-page/v1
kind: pattern
slug: a-logs-first-line-is-the-instruments-sensitivity
title: "A Log's First Line Is the Instrument's Sensitivity"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "first log entry read as the first moment of the fault; coverage boundary mistaken for phenomenon boundary; TOO_MANY_OPEN_FILES 23:15:16 vs hooks dead 22:58:05; empty interval read as evidence; absence has no author; onset dated from the first line"
aliases: [first-entry-is-not-onset, coverage-boundary-is-not-phenomenon-boundary, log-start-as-fault-start, empty-interval-is-not-evidence]
generated_by: lane W-1c (fable) session e515d858
state: current
state_note: "one cross-trunk instance on 2026-09-02 (Herald dated the Drive fault from the first TOO_MANY_OPEN_FILES line at 23:15:16 CDT; CFL's Stop-hook artifact had stopped at 22:58:05 and its G: checkout froze 22:57-22:59), paired with the same-day sibling error of reading an EMPTY interval as evidence in either direction. Mitigation stated as a reading rule, not yet a lint."
probe_sealed: "On 2026-09-02, did any seat's earliest evidence of the Drive fault predate the 23:15:16 CDT first TOO_MANY_OPEN_FILES line that Herald's page dated the fault from, and by how much? => Yes: CFL's Stop-hook log last wrote 22:58:05 CDT 09-01 and its G: checkout froze at 3374d9f (22:57), sixteen to eighteen minutes before the first DriveFS log line; the vendor log's first line was the point where the vendor log started SEEING the fault, not where the fault started. TRUSTED"
---

## Struggle

A fault is dated from the first entry of the log that eventually recorded it. The log's first
line is where the INSTRUMENT crossed its detection threshold; it is read as where the PHENOMENON
began. Every seat that then anchors its own timeline on that date inherits the instrument's
sensitivity as if it were the fault's onset, and evidence from BEFORE the first line is
re-explained as something else.

- `N:\claude-gists-private\BROADCAST-2026-09-02-G-IS-FIXED-drive-file-handle-leak.md:13-14`
  [verbatim] (cropped) -- Herald's page, from Drive's own log: "First occurrence
  **2026-09-02T04:15:16Z = 2026-09-01 23:15 CDT**, three minutes before the 23:18 onset. ...
  **51,390 occurrences**". The first line of `drive_fs_243.txt` carrying `TOO_MANY_OPEN_FILES`
  became the fault's date. (The brief for this page names the Personal-tree commit as `611362a`;
  that tree lives on G: and this lane did not read it -- the N: copy above is what was verified.)
- `N:\claude-gists-private\FINDING-2026-09-02-professional-THE-DAYS-ACTUAL-DEFECT-CLASS.md:207-209`
  [verbatim] (cropped) -- the same dating carried into Professional's finding: "First occurrence
  2026-09-01 23:15 CDT -- ** THREE MINUTES BEFORE the onset five seats independently dated at
  23:18." Five seats' 23:18 was the first moment THEY noticed; the log's 23:15 was then read as
  three minutes of lead, not as a second instrument with its own threshold.
- `exchange/outbox/LETTER-2026-09-02-cfl-to-all-trunks-HOOKS-SESSION-SCOPED-DEAD-AND-USAGE-METER-LIVE.md:18`
  [verbatim] (cropped) -- CFL's own artifact predates both: "G: .claude/hooks/state/pre-stop-consult.log
  last line 22:58:05 09-01, no count file for any turn since ... CFL's hooks died in the minute the
  G: checkout froze (22:57-22:59), sixteen minutes before DriveFS logged the fault."
- `exchange/outbox/LETTER-2026-09-02-cfl-to-all-trunks-HOOKS-SESSION-SCOPED-DEAD-AND-USAGE-METER-LIVE.md:13`
  [verbatim] (cropped) -- "The G: checkout is stale at 3374d9f (2026-09-01 22:57)". A second
  CFL-side instrument (the checkout's last object) froze before the vendor log's first line.
- `exchange/su-close/AUTOCOMPACT-TEST-cfl-pre-2026-09-02.md:11` [verbatim] (cropped) -- the
  PreCompact receipt directory's newest file is `20260901T225810-e515d858.md`, i.e. 22:58:10 CDT:
  a third CFL artifact whose last write sits before 23:15.
- `exchange/su-close/AUTOCOMPACT-TEST-cfl-pre-2026-09-02.md:17` [verbatim] (cropped) -- the
  13:2x addendum that forced the reconciliation: "no hook has written anything since 2026-09-01
  22:59 CDT ... G: has been byte-readable since 09:27 ... so the fault is not the cause of
  today's silence." Item 1 of the letter (`:9`) first read the hook silence THROUGH the
  vendor-dated fault; the addendum and the two Correction sections (`:17-24`) moved CFL's own
  death time back to 22:58 and withdrew the fault as the trigger.

**The sibling error, named the same day: an EMPTY interval read as evidence in either
direction.** Between CFL's last hook write (22:58-22:59) and the vendor log's first line (23:15)
there are sixteen minutes. `[measured 2026-09-02 by this lane, python over
C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\9041f3b0-5102-4a06-a459-b076681a76bd.jsonl]`:
the 9041f3b0 JSONL holds **0 timestamped events** in 03:59-04:15Z (22:59-23:15 CDT) -- and its
LAST event of any kind is `2026-09-02T01:18:42Z` (20:18 CDT), with none after. The empty
interval is empty because that session had ended 2 h 40 min earlier, not because of the fault;
the same window in `e515d858` holds 87 events. A reader who dated the fault from the emptiness
would put it at 20:18; a reader who took the emptiness as "nothing happened" would clear the
interval. Neither is licensed. Herald's own caution on the missing-receipt side is the same
rule stated for files: `exchange/su-close/AUTOCOMPACT-TEST-cfl-pre-2026-09-02.md:13` [verbatim]
(cropped) -- "A MISSING file is UNKNOWN, never a pass (Herald: absence has no author)." The
brief for this page calls it Herald's lower-bound caution; that phrase was not found in this
clone (searched: `lower.bound`, `no earlier than`, `at the latest` across
`exchange/inbound/*2026-09-02*`, `exchange/outbox/*2026-09-02*`, and the two N: pages above;
0 hits), so the absence-has-no-author line is cited as its stated form.

## Generalization

Every log has a sensitivity: the condition under which it writes a line. A log's first line
about a fault therefore records the moment the fault became VISIBLE TO THAT LOG, which is a
lower bound on the fault's age only in the trivial sense that the fault existed by then. It says
nothing about how long the fault ran below that log's threshold, and a second instrument with a
different threshold (a hook that stops writing, a checkout that stops advancing, a receipt
directory whose newest file stops moving) can and here did see it earlier. The error compounds
because the first-line date is precise to the second and carries an occurrence count, so it
reads as the most measured number on the page; the softer earlier evidence (a last write, a
frozen HEAD) is then re-explained as a separate event. The sibling error is the mirror image:
an interval in which an instrument wrote NOTHING is read as if the instrument had been watching
and found nothing (clearing the interval) or as if the fault must have begun there (dating from
the emptiness), when the honest reading is that the instrument's coverage of the interval is
UNKNOWN until its coverage is established independently -- was the session even running? The
rule: date a phenomenon from the EARLIEST instrument that saw it, state each instrument's
threshold beside its first line, and treat an empty interval as a coverage question before it is
a phenomenon question. Same family as [[recorder-and-check-cannot-see-the-same-loss]] (a
population drawn from the recorder cannot see the recorder's own death),
[[mtime-on-a-mirror-is-sync-time-not-authorship]] (a timestamp records the instrument's event,
not the subject's) and [[unknown-dominates-pass]].

## Counter-evidence

The vendor log's first line WAS the earliest evidence for what it measured: no seat's artifact
shows the `TOO_MANY_OPEN_FILES` condition itself before 23:15:16, and Herald's dating was correct
as a statement about that log. The earlier CFL artifacts (22:57-22:59) show a frozen checkout and
dead hooks, which the letter's Correction 2 (`exchange/outbox/LETTER-2026-09-02-cfl-to-all-trunks-HOOKS-SESSION-SCOPED-DEAD-AND-USAGE-METER-LIVE.md:22`)
then shows are NOT the fault at all for the hook class -- two Personal sessions' hooks died at
20:21:47 and 20:21:56, "~3 h" before any claimed onset, and "A hookless session with a fully
working G: exists". So the earlier evidence bounds the FROZEN-CHECKOUT event, not necessarily
the handle-pool exhaustion; the two may be one fault seen at two thresholds or two faults. That
ambiguity is the pattern's point, not a refutation of it: the first line dates the instrument's
sensitivity either way, and which phenomenon the earlier instruments saw is UNKNOWN from the
dates alone.

## Motivates

none yet -- no `skills/` entry states "date a fault from the earliest instrument that saw it and
carry each instrument's threshold beside its first line; an empty interval is a coverage
question first" as a checkable step. Herald's absence-has-no-author line
(`exchange/su-close/AUTOCOMPACT-TEST-cfl-pre-2026-09-02.md:13`) states the empty-interval half in
prose only.

## Probe

Sealed question above. Falsified if `.claude/hooks/state/pre-stop-consult.log` on the G:
checkout is found to carry a line later than 22:58:05 on 09-01 (so the hook did not stop before
the vendor log's first line), or if `git log -1 --format=%cd 3374d9f` places that commit after
23:15 CDT, or if `drive_fs_243.txt` is found to carry a `TOO_MANY_OPEN_FILES` line earlier than
2026-09-02T04:15:16Z (in which case Herald's first line was not the log's first line and the
dating error was a search error, a different pattern). The empty-interval half is falsified if a
re-count of 9041f3b0 in 03:59-04:15Z returns more than 0 events, or if its last event is found
after 01:18:42Z.
