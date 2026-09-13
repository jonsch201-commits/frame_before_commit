---
title: How a machine's Claude record reaches G, and why the laptop's does not
created: 2026-08-23
kind: reference
owner: professional
re: SEC-104 (Secretary, due 2026-08-24)
---

# The mechanism exists, it is healthy, and it is bound to one machine

## 1. What actually runs

`[measured 2026-08-23 15:2x CDT, this seat]`

| | |
|---|---|
| task | Windows Scheduled Task **`ClaudeAccumulateArchive`**, State `Ready` |
| action | `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\Users\JonSc\.claude\hooks\archive-claude-accumulate.ps1" -Quiet` |
| cadence | daily **12:30**; `LastRun 2026-08-23 12:30:01`, `LastTaskResult 0`, `NextRun 2026-08-24 12:30` |
| but also | `LAST-RUN.txt` stamps **13:52:54** and files landed **13:54** — so it is **also** fired outside the schedule, from the same `hooks/` directory it lives in |
| source | **`C:\Users\JonSc\.claude`** — one root, this desktop |
| destinations | `D:\Bkp\cfl-corpus\archive` **and** `G:\My Drive\Claude\.claude-projects-backup` |
| health | `STATUS OK-BUSY` · 9,498 files live · 1,003 superseded versions · **14 copied, 14 hash-verified, 0 failed**, 9 busy and retried next run |

⭐ **It is ACCUMULATE, not mirror — its own log says so: *"Files deleted at the source remain here."*
That is Jon's no-deletion ruling implemented in a scheduled task**, and it is the reason a
`cleanupPeriodDays` sweep at the source no longer destroys the record.

## 2. Why the laptop's record is absent, stated as a cause and not a symptom

⛔ **`-SourceRoot` defaults to `$env:USERPROFILE\.claude` and the task exists on THIS machine only.**
Nothing about the design excludes a second machine; **no second machine has ever been enrolled.**

**Confirming measurements:** `.claude-projects-backup/live/projects/` holds **35** directories;
`C:\Users\JonSc\.claude\projects\` holds **35**. Same count, same names. **The archive is a faithful
copy of one machine, and that machine is not the laptop.**

⚠️ **What this is NOT:** it is not a broken component. A prior report read
`live/projects/`'s **directory mtime** (Aug 22 20:05) as its contents' freshness and concluded the
transcript half had stalled. **A directory's mtime moves when entries are added or removed, not when
their contents change.** Its children were written **Aug 23 13:53**, including the live session's own
JSONL. **Nothing was stale. A proxy was measured instead of the thing.**

## 3. ⛔ Do not simply point the laptop at the same destination

`sessions/*.json` are named by **PID** (`33828.json`, `33404.json`) and the file content carries
`pid`, `sessionId`, `cwd`, `version` — **no hostname, no machine identifier anywhere.** Two machines
writing one destination root **collide on relative path**:

- `sessions/<pid>.json` — PIDs are small integers and recur across machines within days;
- `history.jsonl` — **one file, both machines' typed prompts**, each run superseding the other;
- `CLAUDE.md`, `settings.json` — same.

⚠️ **Accumulate mode makes this recoverable and not obvious.** The loser is not destroyed, it is
filed under `versions/` as a superseded blob — **so the corruption is silent, and after the fact
nothing in the path says which machine wrote which side.** ⭐ **Recoverable-but-unattributable is the
worse failure here, because Jon's stated interest is *"atribution and tracing to when things ahve
been better or worse."***

## 4. The fix, and it needs no code change

**The script is already parameterised** (`param($SourceRoot, $Destinations, …)`). Enrol the laptop
with a **machine-scoped destination root**:

```powershell
# ON THE LAPTOP, once. Creates the task; nothing else changes.
$dest = "G:\My Drive\Claude\.claude-projects-backup\machines\$env:COMPUTERNAME"
```

…passed as `-Destinations $dest`, with the same daily trigger. **Every collision in §3 disappears
because no relative path is shared**, and the machine name is recoverable from the path itself,
which is the attribution property that does not exist today.

⛔ **NOT DONE HERE, and deliberately:** the script lives under `~\.claude\`, which this trunk is
constitutionally forbidden to edit, and the laptop is not this machine. **This is a spec plus one
command, not an applied change.** The one improvement worth proposing to whoever owns the script:
**default the destination to a `machines\$env:COMPUTERNAME` segment** so enrolment cannot be done
wrong, rather than relying on whoever runs it to remember.

## 5. What this still does not cover

1. **The gap between runs.** `[m]` at 15:1x the archive held **275,180 B** of the live session
   against **958,360 B** on disk — roughly a third. **A session that ends between copies loses its
   tail**, and the busy-file retry (`BUSY THIS RUN: 9 (live transcripts)`) is exactly the class of
   file most likely to be mid-write at close.
2. ⛔ **The compact boundary is a separate failure surface and must be tested separately.** Jon drove
   the laptop through ten heartbeats, a wayfinder run, and **a compact** — and this program has
   already measured a compact reporting green while producing no durable artifact. **Enrolling the
   laptop protects the transcript; it does not prove the compact wrote anything to protect.**
