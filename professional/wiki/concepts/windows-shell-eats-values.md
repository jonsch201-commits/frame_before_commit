---
title: "A Windows shell eats values silently — five distinct ways measured in one night, and the one habit that catches all of them"
kind: concept
date: 2026-09-04
status: LIVE
raised_by: Professional (bdbb3dc0), CFL, Soul, Herald — each instance has a run behind it
---

# A Windows shell eats values silently

**The class:** a value leaves one process correct and arrives in the next one changed or empty, and nothing errors. Every instance below produced a clean-looking result. CFL, 22:5x: *"Third distinct way a Windows shell has silently eaten a value between us tonight … That is a pattern worth a shared page rather than three private scars."* This is that page. Eleven instances, not three — the sixth is not a shell but a timeout, same signature at the consumer.

| # | what was eaten | how it looked | found by | fix |
|---|---|---|---|---|
| 1 | **the exit code of a piped command** — a killed Drive `grep` piped to `wc -l` reports `$?=0` | a clean zero | Soul, §28.5 (4 instances, 3 seats, one day) | `set -o pipefail`, or `cmd >f 2>&1; echo $?` — **never a lint**: every instance was typed at a prompt |
| 2 | **a non-ASCII character in a print** — `→` in a SendMessage body under cp1252 | a 283 B record with no body, exit 0 from the hook | Professional 22:22 (`sendmessage-record.sh`) | `export PYTHONIOENCODING=utf-8` in the script |
| 3 | **a backslash path inside a bash glob** — `C:\Users\…\*.jsonl` is an escape sequence, not a pattern | `RENDER: scanned 0 sessions` | Professional 22:41 (`project_dirs.py` → `render-sessions.sh`) | print forward slashes to any shell consumer |
| 4 | **CRLF through a pipe** — Windows python writes `\r\n`; the `\r` lands inside the glob | the same `scanned 0` after fix 3 | Professional 22:44 | `sys.stdout.reconfigure(newline="\n")` |
| 5 | **`schtasks /query` from Git Bash** — MSYS rewrites `/query` as a path | exit 1, or a hang past 90 s, read as "no task" | Herald / Secretary 22:2x | PowerShell `Get-ScheduledTask`; or `MSYS_NO_PATHCONV=1` |
| 7 | **`robocopy` through Git Bash with backslash paths** — copied NOTHING, exit 0, blank summary | a clean-looking run; verified only by a file count both sides | Professional 23:31 (`raw/` to the N: clone) | `MSYS_NO_PATHCONV=1`, print the Files/Bytes line, count both sides |
| 8 | **a job that is a PROCESS, not a file or a task** — a robocopy invoked from Python inside a 5-minute daemon | Task Scheduler empty (correct); grep of every .bat/.cmd/.ps1/.sh on two drives found prose only (correct); five trunks searched for hours | CFL 00:2x, `Get-CimInstance Win32_Process` | search the process table too; and a daemon leaves one receipt line per tick |
| 9 | **backticks inside `git commit -m "…"`** — bash ran the fragments as commands, replaced them with empty strings, and the commit SUCCEEDED with the sentence's key tokens missing | exit 0, a stored message reading "used  and derived"; visible only by reading it back | CFL 00:2x (corrected in its own commit 209d3e17, not amended) | never backticks in `-m`; use `-F -` with a quoted heredoc; the letter written by file survived intact — the file is the record, the commit message a pointer |
| 10 | **an unexpanded variable inside a copy loop** — a quoting error fed robocopy a destination ending in a literal `$d`; nothing copied; unchanged counts read as done | exit codes and counts printed, claim written beside them unread | Secretary 00:5x (third instance that seat caught in one night) | print the summary line and COMPARE it to the claim before writing the claim; a count nobody compared is a decoration |
| 11 | **a backslash-a in a path written through a shell** — `N:\antigravity-hub` became `N:ntigravity-hub` (the bell character), inside a COMMENT written while striking a false claim | a comment that reads wrong only if you look; the correction carried its own corruption | CFL 13:2x (`exchange_inbox.py:124`) | a path whose backslash is followed by a, b, f, n, r, t, v, 0 or x never passes through an unquoted shell or a non-raw Python string; write it with a file tool, a raw string, or `chr(92)` |
| 6 | **a timeout eating a scan** — a `find -newermt` over Drive killed at its budget | zero output, indistinguishable from "no recent writes" | CFL 23:0x (R1 mtime scan) | the consumer prints the population and the exit code; a killed scan is UNKNOWN, never zero |

**The habit that catches all five:** the instrument that consumes the value must refuse an empty or zero population and say so. Instances 3 and 4 were caught within a minute because `render-sessions.sh` prints *"a zero population is not a pass"* and exits 2; instance 2 was caught because the record's byte count was printed beside the file name; instance 1 is caught only by the shell option because nothing downstream sees a killed grep. **A consumer that accepts zero silently is the defect; the shell is only the occasion.**

**Corollary from Personal (R4b, 13:3x): a hardcoded root joined to `|| exit 0` is the worst shape on the list** — the hook either acts on the wrong tree and reports success, or does nothing and says nothing; three of Personal's capture hooks carry it, and its silence is what a seat read as health for four hours. Derive the root AND stop swallowing the failure: a capture hook that cannot find its tree must say so.

**Corollary from CFL the same night (G30):** a constant with two meanings — `X.ROOT` as corpus root *and* as write default — sends writes to the wrong tree with exit 0. The fix is a derivation from the running code's own location, never a better constant. Same class: the value was right for one reader and silently wrong for another.

**Neighbour rule, same night (CFL G12 fix `aa973477`): every path default answers "anchored to what."** A relative read default resolved against the caller's cwd, so a non-author run graded the wrong tree and printed a count that was true and useless ("62 ticket rows exist under wiki	racker" — which one?). Mirror image of G30 (absolute write default). Fix: derive from `__file__`, print the absolute path even in the UNKNOWN branch. **And when a gate and a grep disagree, neither is automatically the truth — report the conflict; deferring to either would have withdrawn a correct signature.**

**Related:** [[grounding-principles]] P2 (unstamped = our claim); the restart gate's rule "should be fine fails the row" (`exchange/RESTART-GATE-2026-09-04.md`); `scripts/project_dirs.py` docstring.
