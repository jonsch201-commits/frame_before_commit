---
title: Nightly-lane Leg 2 truncated prompt
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-AGENTMEM; sub: fleet 3 vs wiki 0 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_nightly-lane-leg2-truncated-prompt.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, nightly-lane, cmd-mangling]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: nightly-lane-leg2-truncated-prompt
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Nightly-lane Leg 2 truncated prompt

*Source description:* Nightly corpus-delta lane Leg 2 prompt arrived truncated (first line only) on 2026-07-19; delta is deterministically recoverable from the un-advanced snapshot

On the 2026-07-19 run of the Stage 1 nightly corpus-delta lane, the Leg 2 headless prompt arrived cut off after its first line ("The nightly pure-Python scan found this corpus delta:") — no delta report, no task body. Recovery that worked: re-run Leg 1's diff (`extract_claude_code_sessions.py --list` parsed with the runner's LINE_RE, diffed against `%LOCALAPPDATA%\cfl-lanes\nightly-corpus-delta\snapshot.json`) — valid because the runner advances the snapshot only after Leg 2 succeeds. Task body lives in `build_prompt()` in `scripts/lanes/nightly_corpus_delta.py`. Result: draft PR #59. Root cause of the truncation not yet diagnosed — check how the runner passes `-p` on Windows (quoting/newlines in the argument) before the next scheduled night. Also surfaced: `raw/` is gitignored while the lane spec requires raw/ markdown in the PR (force-add used, tension flagged in PR #59); and bare `--update` would sweep 16 ratio-floor false-REFRESHes ([[md-not-uncaptured-authoritative-disposition]]) — scope conversion to the delta via the canonical converter.
