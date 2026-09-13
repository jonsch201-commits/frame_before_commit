---
title: "Pre-stop hook fires on a bare one-word reply — CFL session 034c1f, 2026-08-07"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 034c1f
source_kind: session
source_file: raw/transcripts/claude-code/fl/code-2026-08-07-034c1f-say-ok-and-nothing-else.md
raw_sha256: ba6e2339199589c8e60acc03101bb4c414bbf09bc843187bb99fdc3780cd9315
raw_length: 2197 chars / 58 lines (verified turn_count 3, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: stop-hook-bare-directive-034c1f-2026-08-07
aliases: ["say OK and nothing else 034c1f", "pre-stop consult hook 2026-08-03 rule", "bare directive stop-hook"]
generated_by: S-augM-07 executor (week-2026-09-02-corpus lane), reading the raw session extract directly
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [pre-stop-hook, fable-mirror, cfl-infra, stop-consult, hook-mechanics]
---

# Pre-stop hook fires on a bare one-word reply — CFL session 034c1f, 2026-08-07

## Summary

A minimal CFL session (Jon's entire message: "Say OK and nothing else.") received the standard
"OK" reply, then the Stop hook fired the 2026-08-03 pre-stop-consult rule anyway — because no
fable-mirror consult had been dispatched since Jon's last message. The raw is a live-snapshot
extract ending at the hook firing; no assistant response to the fired hook is captured in this
file. This page is one of four near-identical sessions (034c1f, 207c37, 24beb1, f15829) opened
the same day with the same one-line directive, each producing a different resolution to the same
gate — this one is the shortest, capturing only the hook firing itself.

## Key Claims

- **Jon's literal one-line instruction was followed exactly, with no scope expansion.** The
  entire human turn was "Say OK and nothing else." and the assistant's entire reply was "OK" —
  no tool calls, no additional commentary. [verbatim]
  ([stop-hook-bare-directive-034c1f-2026-08-07:T1])
- **The Stop hook fired regardless of the triviality of the turn.** The hook text states the rule
  verbatim: "PRE-STOP CONSULT REQUIRED -- Jon's rule, 2026-08-03: \"If main wants to stop, it
  must talk to you firt.\"" and that "This rule was violated twice on the day it was written,
  both times in a message that announced it was continuing." [verbatim]
  ([stop-hook-bare-directive-034c1f-2026-08-07:T3])
- **The hook names two remedies and an explicit non-exemption list.** Dispatch a narrow
  fable-mirror consult ("I want to stop X because Y") with the burden of proof on stopping and
  the default answer CONTINUE, or land work and write a one-line reason. Reasons the hook names
  as explicitly invalid: "reaching a good place to report, a lane finishing, having something
  worth telling Jon." [verbatim] ([stop-hook-bare-directive-034c1f-2026-08-07:T3])
- **This raw does not capture the session's actual resolution of the fired hook.** The file ends
  at the hook text; whether the session dispatched a consult, what it answered, and how the
  session actually closed are not represented here — see the sibling sessions 207c37, 24beb1, and
  f15829, opened with the identical one-line directive, for three different resolutions of the
  same gate on the same day. [contextual]

## Conflicts

None with existing wiki content.

## Entities & Concepts

Pre-stop-consult hook (2026-08-03 rule), [[mirror-stateless-dispatch-only]], fable-mirror,
Stop-hook mechanics.

## Uncaptured Content

- **No assistant response to the fired hook is in this raw.** The capture ends immediately after
  the hook's text; this page cannot report what the session actually did next.
- **Whether a fable-mirror consult was ever dispatched from this specific session is unknown from
  this raw** — three sibling sessions opened the same minute or hour with the identical directive
  each show a distinct resolution (see Key Claims), and this session's own resolution is not
  captured.
