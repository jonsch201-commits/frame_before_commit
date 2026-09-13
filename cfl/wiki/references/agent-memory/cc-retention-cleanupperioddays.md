---
title: CC session retention kills JSONLs (cleanupPeriodDays)
trunk: fl
branch: [cfl]
sub_branch: [corpus]
branch_reason: "R-AGENTMEM; sub: corpus 7 vs wiki 0 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_cc-retention-cleanupperioddays.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, retention, corpus-loss]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: cc-retention-cleanupperioddays
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# CC session retention kills JSONLs (cleanupPeriodDays)

*Source description:* Claude Code's cleanupPeriodDays (default 30) permanently deleted 28-29 CC sessions from 2026-05-01 to 06-16; history.jsonl survives the sweep and is the primary recovery source

**The mechanism.** `cleanupPeriodDays` — official Claude Code setting, **default 30 days**, minimum 1. Deletes session `.jsonl`, plus `subagents/`, `tool-results/`, `tasks/`, `shell-snapshots/`, `backups/` — **at startup**. Docs: `https://code.claude.com/docs/en/settings`. Documented only in the full settings reference; absent from all getting-started material.

**The loss.** Clean cutoff, zero scatter: every CC session **2026-05-01 → 2026-06-16 is gone (29)**; every session **2026-06-21 → 2026-07-21 survives**. Permanent — programmatic delete bypasses the Recycle Bin (verified: 5 items, zero `.jsonl`), no Anthropic export/recovery path (GH #64721), the only VSS shadow copy postdates the deletions. Set to `3650` in `C:\Users\JonSc\.claude\settings.json` on 2026-07-25; verified valid JSON, CC v2.1.220, launcher passes no `--setting-sources`.

**Do not trust the setting alone** — open bugs where cleanup ignores it: GH #62272 (after updates/restarts), #18881, #45903 (`--setting-sources local`). NOT established despite being widely repeated: that the clock keys on `mtime` (GH #15935 was closed as not-planned and never demonstrates it).

**What survives and matters most:**
- **`C:\Users\JonSc\.claude\history.jsonl`** — survives the sweep. 1,229 entries / 51 sessions / 2026-03-10→07-24, every typed prompt with `sessionId` + timestamp. It made 25 of 29 dead sessions *measurable*. It is a floor, not complete: omits headless `-p` runs, job sessions, and `1e609faf` entirely.
- **`memory/` dirs** survive. Three projects (`D--Decoding-Layer-POC`, `T--DCI`, `D--Claude-Projects-Video-Game-test-checks`) have populated `memory/` and zero JSONL / zero `.md` / zero history rows — possibly the only trace those projects existed.
- **git history recovers the action layer**: 25 of 29 dead `.md` were rendered by a legacy converter with zero tool markers, so what was *done* is absent from them — but commits from each session's window record it at full fidelity.

**Related archive defects:** `tool_result` capped at 300 chars and `tool_use` keeps only the first input key/80 chars (~12% of tool data retained; a `Write`'s content is never captured). 218 subagent JSONLs (84 MB, 38.8% of all CC bytes, 2,606 thinking blocks) have **never** been extracted — `extract_claude_code_sessions.py:89` globs top-level only. Thinking is readable in only 166 of 5,945 blocks. See [[flagged-unknowns-are-work]].
