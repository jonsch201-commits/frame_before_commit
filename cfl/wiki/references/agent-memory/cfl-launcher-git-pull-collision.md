---
title: CFL launcher git-pull collision
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_cfl-launcher-git-pull-collision.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, launcher, git]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: cfl-launcher-git-pull-collision
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# CFL launcher git-pull collision

*Source description:* The CFL launcher .ps1 crashed on every run because `git pull --ff-only` aborts on identical-content untracked collisions — a structural consequence of how agents drop files into exchange/ and wiki/intake-triage/

Fixed 2026-07-24. `CFL - including git pull and skill sync.ps1` (in `G:\My Drive\Claude\Claude Foundational Layer\`) died on essentially every launch. Two causes:

1. **Structural, and it will recur in spirit:** agents routinely write files into `exchange/` and `wiki/intake-triage/` in the working tree; those same paths later land on `origin/main` via PR. `git pull --ff-only` then refuses with *"untracked working tree files would be overwritten by merge"* — **even when the content is byte-identical**. The old script treated any dirty tree as a hard abort, so the repo's own normal workflow guaranteed the crash. Fix: on that specific failure, compare each blocking file's `git hash-object` against `origin/main:<path>`; if identical, `git add` it (staging only, never touches content) and retry once. Genuinely differing files still abort with a list — nothing force-added or discarded.
2. **PS 5.1 stderr:** `2>` / `2>&1` on a native exe wraps stderr lines in `NativeCommandError` and corrupts captured text even on exit 0. Route git output through `cmd /c "... 1> f 2> f"` instead. Also: a mojibake em-dash introduced by an editing pass was a genuine parse error — verify with `[System.Management.Automation.Language.Parser]::ParseFile` after editing, and keep the file pure ASCII.

**Why:** the crash looked like a git problem but was a workflow-shape problem; treating "dirty tree" as fatal is wrong for this repo specifically.

**How to apply:** never "fix" this by `reset --hard` or `clean -fd` — untracked files in `exchange/`/`wiki/intake-triage/` are live work products. Relates to [[drive-lag-stale-read-hazard]], [[stale-index-lock-recovery]], [[live-session-liveness-and-untracked-state]].
