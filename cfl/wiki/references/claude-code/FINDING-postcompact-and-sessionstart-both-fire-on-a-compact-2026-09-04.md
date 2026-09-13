---
kind: reference
domain: claude-code
slug: postcompact-and-sessionstart-both-fire-on-a-compact
title: "A compact fires PostCompact AND SessionStart(compact) — one script wired to both races itself"
measured: 2026-09-04 21:2x CDT
measured_by: CFL main seat (session 71ce5a0e), against its own compact
status: FIXED (G28, scripts/audit/runlock.py) — the platform behaviour itself is NOT a bug and is not fixed by us
reader_token_cost: "~900 tokens (3,600 bytes / 4, measured post-write)"
on_silence: "nothing acts; this is a finding other trunks' hook authors need, not a request"
---

# A compact fires TWO hook events, and a script wired to both runs twice, concurrently

## The observation

One `/compact` on 2026-09-04 21:2x. CFL's terminal printed **two tables from the same script in the
same minute, disagreeing on two rows**:

| step | PostCompact run | SessionStart:compact run |
|---|---|---|
| 2 ingest wiki | **PASS** | **FAIL** |
| 9 summary vs tail | **FAIL** | **PASS** |

Both are `scripts/audit/postcompact_pipeline.py`. `.claude/settings.json` wires it on **`PostCompact`**
and on **`SessionStart` with matcher `compact|clear`**. A compact fires both events, so the script
ran twice, concurrently, and both instances wrote the same output file
(`exchange/su-close/POSTCOMPACT-STATUS.md`). **The copy left on disk is whichever finished last —
which was not the copy on the screen.**

## Why it was expensive, and it is not the row you would guess

Step 2 (`main_thread_ingest.py`) graded **FAIL** with the note `exit=0: no output`. Run by hand
immediately afterward, single-instance, the same command returns exit 0 and:

```
=== MAIN-THREAD I1 — 1 session(s) considered, 1 written, 0 error(s) ===
  wrote  71ce5a0e-d25  ...i1.md — 73 Jon utterance(s), 57 anchored, 4983 turns
```

⛔ **A concurrency artefact was graded as a content failure, and the grader's own note pointed away
from the cause.** "No output" reads as *the ingest found nothing*; the truth was *two processes were
writing one path*. This is the same shape as the chained-hook stdin finding of the same day: **a
second consumer cannot distinguish "nothing was there" from "someone else already took it."** Both
render as an absence, and an absence is what a default fires on.

## What is NOT the fix

**Unwiring one of the two.** `PostCompact` does not cover `clear`, so dropping the `SessionStart`
entry loses coverage; dropping the `PostCompact` entry loses the payload that carries `session_id`.
And neither stops the *next* script from being wired to both. **The defect is two writers of one
verdict file with no arbitration** — each table internally consistent, neither aware the other
exists, and no way for a reader to tell they are holding one of two.

## The fix

`scripts/audit/runlock.py` (selftest 9/9, G28). `O_CREAT|O_EXCL` acquire; **the loser writes
nothing** and prints a skip that **names the holder's pid and the lock's age** — a skip with no
holder named is indistinguishable from "did not run", which is the class of error this pipeline
exists to end. A lock older than 900s is **stolen, and the theft is reported**: a crashed run must
not wedge every future compact, or the fix becomes a bigger outage than the bug.

**Verified against the real thing, not only a fixture.** A second live instance launched while the
first held the lock:

```
POSTCOMPACT-STATUS: SKIPPED -- another postcompact_pipeline is already running:
[pid=44348 start=1788576941.766 argv=... --session 71ce5a0e-...], age 136.9s.
This instance wrote NOTHING; the holder owns the verdict file.
```

The holder then finished **PASS-WITH-SKIPS, steps 2 and 9 both PASS**. Before and after measured on
the same session, the same compact.

## For the other trunks

⚠️ **Any hook script wired to more than one event that writes a single status/verdict/log file has
this defect**, whether or not it has shown symptoms — and it shows symptoms only when the two runs
happen to disagree, which is rare and looks like flakiness. Herald, Professional and Secretary all
run status-writing hooks. **The check is a grep of your own `settings.json` for a script name
appearing under two events, not a wait for a contradiction to appear.**

⭐ And note what made this findable at all: **the two tables were printed where a human could see
both.** Had only the disk copy existed, there would have been one internally-consistent FAIL table
and a wrong root cause to chase.

Related: [[chained-hooks-share-one-stdin]] (same day, same "an absence is not a measurement" family).
