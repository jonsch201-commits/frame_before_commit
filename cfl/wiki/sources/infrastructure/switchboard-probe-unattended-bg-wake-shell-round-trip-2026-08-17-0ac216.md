---
title: "Switchboard probe verifies an unattended --bg wake completes a full shell round-trip with no human prompt answered, 2026-08-17"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-code/code-2026-08-17-0ac216-switchboard-probe-do-exactly-this-then-stop-run-da.md
source_kind: session
date: 2026-08-17
retrieval_key: switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216
aliases: [sb-probe-order-1756, bg wake unattended shell round-trip, switchboard end-to-end probe, RECAPS-ALL-TRUNKS append probe]
generated_by: coverage lane 8 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion
raw_sha256: c49de2142dcf3bd0895ae857bb271baa9de214402f8cf5302d2d12e549a45830
raw_length: 4982 bytes / 137 lines
uncaptured_assessed: populated
fidelity: verbatim
tags: [claude-code, switchboard, probe, background-agent, unattended-wake, infrastructure]
---

# Switchboard probe verifies an unattended --bg wake round-trip, 2026-08-17

## Summary

A dispatched Personal-trunk background agent (`sb-probe-order-1756`) receives a tightly-scripted
switchboard probe instruction — run `date`, append one fixed recap block to the shared
`RECAPS-ALL-TRUNKS.md` file via bash `>>`, read back the last four lines, then stop — and executes
it end to end with three tool calls and no clarifying question. The session closes with the
assistant's own receipt confirming the block landed intact and noting explicitly that no prompts
fired and no human input was required, and that it deliberately left the SessionStart hook's
"19-JSONL" signal untouched per the instruction's "nothing else." This is an existence proof for
one class of switchboard-operator dispatch: a `--bg` wake can run real shell work unattended and
report a verifiable receipt, not just a status line.

## Key Claims

- **The probe instruction is a fully scripted, single-purpose dispatch** — "Switchboard probe. Do
  exactly this then stop: run 'date' in bash; append one block to
  G:/My Drive/Claude/RECAPS-ALL-TRUNKS.md via bash (>>): '## Personal - <the date you read> -
  background agent sb-probe-order-1756', 'recap: a --bg wake ran shell work unattended end to end,
  no human answered any prompt', 'awaiting-jon: NONE'; read back the last 4 lines. Nothing else."
  [verbatim]
  ([switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T1]).
- **The agent executes the three required steps as three separate Bash tool calls with no
  deviation** — `date` returns `Mon Aug 17 17:51:27 CDT 2026`; the recap block is appended via
  `printf ... >> "G:/My Drive/Claude/RECAPS-ALL-TRUNKS.md"`; `tail -n 4` reads the file back.
  [verbatim, from the tool_use/tool_result pairs]
  ([switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T2],
  [switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T3],
  [switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T4],
  [switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T5],
  [switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T6],
  [switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T7]).
- **The readback confirms the appended block landed intact immediately after a prior recap row**,
  and the session's own closing receipt states the result plainly: "Probe complete, end to end,
  unattended... No prompts fired, no human input required. Nothing else done — no commits, no
  wiki ingest (the SessionStart hook's 19-JSONL signal was left untouched per 'nothing else')."
  [verbatim]
  ([switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T8]).
- **The session is a Personal-trunk background agent, not CFL** — the recap block it appends is
  self-labeled `## Personal - ... - background agent sb-probe-order-1756`, and this same recap
  line is independently visible from the CFL side in a companion session's read of
  `RECAPS-ALL-TRUNKS.md` (`raw/transcripts/claude-code/code-2026-08-18-f4cfd0-...md`, tool-result
  block listing "Personal - 2026-08-17 17:51:27 CDT 2026 - background agent sb-probe-order-1756"
  among the cross-trunk recap tail) — cross-referenced here as corroboration of a claim already
  verbatim in this page's own raw, not as a citation into that other page.
  [paraphrase, cross-checked]
  ([switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216:T8]).

## Jon said

No Jon turn appears in this raw — the dispatching instruction (T1) is the switchboard-operator's
scripted probe order, not a live Jon utterance, and carries no `[origin: human]` tag.

## Conflicts

None found against existing wiki pages. id `0ac216` absent from `wiki/sources/**` before this page.
The raw carries `capture_state: LIVE-SNAPSHOT` (`captured_through_record: 38`,
`captured_at: 2026-08-20T01:30:39Z`) — the session may have continued past this capture; absence of
further turns below T8 is not evidence the session ended there, only that nothing further had been
read into the corpus as of the capture watermark.

## Cross-Wiki

None — this is CFL infrastructure content (switchboard-operator dispatch mechanics, background-agent
verification), not personal/home/pro domain material. See [[wiki-query]] for the retrieval layer
this probe's cross-trunk RECAPS visibility feeds.
