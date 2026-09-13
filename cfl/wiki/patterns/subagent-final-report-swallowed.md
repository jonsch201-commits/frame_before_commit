---
format: cfl-page/v1
kind: pattern
slug: subagent-final-report-swallowed
title: "Subagent Final Report Swallowed (and the Loop That Re-Files Its Own Reply)"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "task notification carries hook echo largest assistant text block subagent JSONL SubagentStop re-fires PENDING row for the replying lane"
aliases: [notification-is-not-the-report, route_agent_return-refires, harvest-largest-block]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "the swallow half has a fix in the tree (two extraction scripts); the re-fire half (RP-29) is OPEN — measured this cycle at 100 tool uses on one lane before it was noticed."
probe_sealed: "This cycle's dream run measured how many tool uses the mirror lane and sweep (c) burned on the SubagentStop re-fire loop before it was caught. => mirror lane 100 tool uses, sweep (c) 40, with two lanes' final reports swallowed by the loop text itself. TRUSTED"
---

## Struggle

A subagent's completion notification is not its report — the notification can carry a one-word
hook echo while the actual report sits only in the subagent's own JSONL as the largest assistant
text block; and separately, the hook wired to notice a subagent stopping can re-fire on that same
subagent's own reply-to-being-routed, creating a PENDING row for the very agent that just
terminated and looping.

- `scripts/audit/harvest_subagent_report.py:2,51-52` [contextual] — file docstring: "Harvest the
  largest assistant text block from a subagent JSONL"; code: "Find the largest block" /
  `largest_block = max(blocks, key=len)` — the mechanism built specifically because the
  notification layer does not carry the report.
- `wiki/tracker/wayfinder-pr3-record-pipeline-2026-08-31.md:93` [verbatim] (cropped) — RP-29 row:
  "SubagentStop hook re-fires on a subagent's own terminal reply (`route_agent_return.py` -> new
  PENDING row for the replying lane -> lane replies to route it -> re-fire). Measured this cycle:
  mirror lane 100 tool uses, sweep (c) 40, two final reports swallowed by loop text."

## Generalization

Two related instances of the same root cause — the harness's control-plane signal (a completion
notification, a Stop-hook firing) is not the same channel as the content it is supposed to gate,
and code written to react to the SIGNAL rather than to the underlying STATE either loses content
(the notification carries no report) or manufactures spurious work (the hook treats "an agent just
replied" as indistinguishable from "an agent just started," and re-routes it). Both failures are
invisible to a coordinator that trusts the signal at face value — a clean "Done." notification and
a busy but productive-looking tool-use count both look healthy. Related:
[[later-instrument-blames-earlier]] (another harness-signal-vs-content-channel confusion).

## Counter-evidence

none found, searched: `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md` and the
DREAM packets for an instance where a subagent's completion notification WAS the full report
(rather than requiring JSONL extraction) or where a Stop/SubagentStop hook correctly deduped on
agent id without re-firing; none appears in this bounded set — every subagent-completion mention
found describes the swallow or the re-fire, not a clean case.

## Motivates

none yet directly named — `scripts/audit/harvest_subagent_report.py` and
`scripts/audit/extract_subagent_report.py` exist as the fix for the swallow half; RP-29's fix
("the hook must not create a PENDING row whose subject is the agent that just stopped, or must
dedupe on agent id + artifact path; selftest with a fixture lane") is proposed but, per the
wayfinder row's status, not yet built.

## Probe

Sealed question above. Falsified if `wiki/tracker/wayfinder-pr3-record-pipeline-2026-08-31.md`'s
RP-29 row is found CLOSED with a dedupe fix landed, or if a fresh six-lane dream-style fan-out is
run and every lane's completion notification is found to carry its full report without needing
`extract_subagent_report.py`.
