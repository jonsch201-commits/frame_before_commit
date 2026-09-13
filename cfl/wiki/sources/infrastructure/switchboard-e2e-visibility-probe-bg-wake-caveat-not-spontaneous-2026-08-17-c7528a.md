---
title: "Switchboard end-to-end visibility probe proves the --bg wake write path, with its own caveat that it does not prove spontaneous self-waking, 2026-08-17"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-code/code-2026-08-17-c7528a-switchboard-end-to-end-visibility-probe-do-exactly.md
source_kind: session
date: 2026-08-17
retrieval_key: switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a
aliases: [sb-probe-e2e-1745, bg wake visibility probe, RECAPS-ALL-TRUNKS append-only probe, not spontaneous self-waking caveat]
generated_by: coverage lane 8 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion
raw_sha256: 04c579572426fd9e72a6bf5e5f9a87fb3a783cd3c9280d4d978cc4a21e417114
raw_length: 5054 bytes / 112 lines
uncaptured_assessed: populated
fidelity: verbatim
tags: [claude-code, switchboard, probe, background-agent, unattended-wake, infrastructure]
---

# Switchboard end-to-end visibility probe, with its own scope caveat, 2026-08-17

## Summary

A second Personal-trunk background-agent probe (`sb-probe-e2e-1745`), dispatched the same day as
the companion probe `0ac216`, runs a near-identical append-and-readback drill against
`RECAPS-ALL-TRUNKS.md` — but this one's stated purpose is narrower: proving the agent runs as a
*named* background agent visible in the Claude agents list, not merely that shell work can run
unattended. The session completes the drill and then adds a self-scoping note the companion probe
lacks: the session was launched with a task prompt, so it demonstrates the `--bg` execution and
write path end-to-end, but explicitly does NOT demonstrate spontaneous self-waking. This caveat is
the page's most load-bearing content — it draws the exact boundary of what this class of probe can
and cannot claim to have proven.

## Key Claims

- **The probe instruction narrows the claim under test to named-agent visibility, not just
  unattended execution** — "Switchboard end-to-end visibility probe. Do exactly this, then stop:
  append ONE block to G:\My Drive\Claude\RECAPS-ALL-TRUNKS.md using append-only (python
  open(path,'a') or >>), format: '## Personal - <date time CDT> - background agent
  sb-probe-e2e-1745' then 'recap: proved the --bg wake path - this turn ran as a named background
  agent visible in claude agents, and wrote this line without any human present' then
  'awaiting-jon: NONE'. Verify by reading back the last 5 lines. Then stop." [verbatim]
  ([switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a:T1]).
- **The agent runs the drill in two tool calls** (`date "+%Y-%m-%d %H:%M"` → `2026-08-17 17:37`,
  then a heredoc `cat >> ... << 'EOF'` append immediately followed by `tail -n 5` in the same
  command) rather than three separate calls, and the readback confirms the block landed directly
  after the prior trunk's `awaiting-jon: NONE` line. [verbatim, from the tool_use/tool_result pairs]
  ([switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a:T2],
  [switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a:T3],
  [switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a:T4],
  [switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a:T5]).
- **The closing turn states the probe's scope limit explicitly, unprompted** — "One note for the
  probe's own record, since it bears on what the probe proves: this session was launched with a
  task prompt, so it demonstrates the `--bg` execution and write path end-to-end, not spontaneous
  self-waking. Stopping here as instructed — no wiki-ingest dispatch, no commit." [verbatim]
  ([switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a:T6]).
- **The readback tool-result also surfaces an unrelated, incidentally-captured status line** —
  the prior line above the new block lists five open cross-trunk items with named owners and
  dates (GraphRAG v0, census/ledger join, operator code items, CLAUDE.md shrink, D17-D21), visible
  only because the probe's own readback window happened to include it — not something this session
  was asked to check. [paraphrase]
  ([switchboard-e2e-visibility-probe-bg-wake-caveat-not-spontaneous-2026-08-17-c7528a:T4]).

## Jon said

No Jon turn appears in this raw — the dispatching instruction (T1) is the switchboard-operator's
scripted probe order, not a live Jon utterance, and carries no `[origin: human]` tag.

## Conflicts

None found against existing wiki pages. id `c7528a` absent from `wiki/sources/**` before this page.
Read together with the companion probe page
([[switchboard-probe-unattended-bg-wake-shell-round-trip-2026-08-17-0ac216]] if that slug resolves,
else the sibling source page for id `0ac216`, same date), the two probes are complementary, not
duplicative: `0ac216` demonstrates unattended shell execution; this one demonstrates named-agent
visibility, and only this one states the spontaneous-self-waking caveat. The raw carries
`capture_state: LIVE-SNAPSHOT` (`captured_through_record: 36`) — absence of further turns is not
evidence the session ended at T6.

## Cross-Wiki

None — this is CFL infrastructure content (switchboard-operator probe design and its own stated
scope limits), not personal/home/pro domain material.
