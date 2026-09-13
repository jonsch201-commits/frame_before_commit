---
title: Windows MAX_PATH x git worktree
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_windows-maxpath-worktree.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, worktree, windows]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: windows-maxpath-worktree
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Windows MAX_PATH x git worktree

*Source description:* Windows MAX_PATH breaks worktree checkouts at long base paths — use a short off-Drive base + per-invocation core.longpaths; a partial checkout is the mass-deletion hazard state. Also covers a distinct gotcha — isolated worktrees never inherit untracked files from the main checkout.

# Windows MAX_PATH × git worktree (observed 2026-07-18)

`git worktree add` into the session scratchpad failed: the scratchpad base is ~150 chars, the repo's wiki source filenames run ~95 chars repo-relative, and git-for-Windows refuses paths past 260 without `core.longpaths`. ~20 files errored "Filename too long" and the worktree ended PARTIALLY checked out with `fatal: Could not reset index file to revision 'HEAD'`.

**Why:** A partially-checked-out worktree is the same hazard state as [[stale-index-lock-recovery]] — committing from it can stage the missing files as deletions (mass-deletion commit). The main checkout on `G:\My Drive\...` (~60-char base) is fine; only extra-long bases break.

**How to apply:**
- Create worktrees at a SHORT off-Drive base, e.g. `C:\Users\JonSc\AppData\Local\Temp\claude\wt-<slug>` (~45 chars) — satisfies [[drive-worktree-mirror-poisoning]] (off-Drive) and MAX_PATH at once.
- Add `-c core.longpaths=true` per-invocation for margin; do not set persistent repo config without Jon.
- After ANY worktree create: verify `git -C <wt> status --porcelain` is EMPTY before writing into it. Non-empty or checkout errors = do not commit; remove (`git worktree remove --force` → if "not a working tree", `rm -rf` + `git worktree prune`), delete the branch, recreate short.

## Distinct gotcha: isolated worktrees don't inherit untracked files (2026-07-20, session 49a1c0)

A skills-executor dispatched into `wt-packet8-fixes` stalled mid-task on an item needing untracked files (`exchange/lanes/ledger/*.tsv`, `reports/*.html`, `scripts/migrations/*.py`, a stray `wiki/*.md` duplicate) — they exist in the main Drive checkout's working tree but were never committed, so `git worktree add` never brings them along. `git worktree` only replicates tracked/committed state; untracked files are checkout-local. The task-notification result was a mid-sentence fragment ("Let me check the originals first") — same truncation signature as the earlier false-completion case, but this time the underlying cause was real and structural, not a reporting glitch.

**Fix applied:** coordinator copies the specific untracked files from the main checkout into the agent's worktree by hand, then resumes the agent via `SendMessage` with the files' exact paths. Worked cleanly on retry (PR #67).

**How to apply:** Before dispatching any subagent brief whose scope includes "decide disposition of untracked files" or similar, either (a) pre-copy those files into the target worktree before dispatch, or (b) flag in the brief that the agent should report back rather than stall if it hits untracked-file-dependent items, so the coordinator can intervene without burning a full dispatch cycle on a mid-sentence cutoff.

## Distinct gotcha: `git worktree add` fails via the Bash tool under Temp, works via PowerShell (2026-07-22)

A skills-executor's `git worktree add` into `C:\Users\JonSc\AppData\Local\Temp\claude\wt-*` consistently failed **through the Bash tool** with `fatal: could not create leading directories of '.../.git'` (confirmed via GIT_TRACE + retries + shallower paths; native `git.exe` succeeded at `C:\` root via Bash). It was NOT a permissions/MAX_PATH gap — Bash-tool `mkdir`/`echo` into the same Temp path worked; the failure was specific to native `git.exe` **worktree-add writes** into that Temp path through the Bash tool. Ran immediately via the **PowerShell tool** at the exact same path. Cost real time; recurs per agent hitting the Bash/Temp interaction.

**How to apply:** In executor briefs that create an off-Drive Temp worktree, tell the agent to create the worktree via the **PowerShell tool** (or fall back to it immediately on the Bash `could not create leading directories` error), not to burn retries on Bash. Off-Drive Temp base is still correct ([[drive-worktree-mirror-poisoning]] + MAX_PATH); only the *tool* used for the `worktree add` matters.
