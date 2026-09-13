---
title: Stale index.lock recovery
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: sub-branch too close to call: wiki 3 vs corpus 3 (margin < 1)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_stale-index-lock-recovery.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, git-hygiene, worktree]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: stale-index-lock-recovery
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Stale index.lock recovery

*Source description:* Worktree-heavy work on the Drive repo can hit a stale git index.lock → a commit against the emptied index stages mass deletions; recover with reset --mixed

During the 2026-07-15 autonomous run (6 per-phase worktrees on the Google-Drive repo), a git commit failed with `Unable to create index.lock: File exists`. Removing the stale lock and re-running `git add` + commit produced a **corrupted commit that staged deletion of all 462 tracked files** and kept only the 2 new files — because the index had been emptied, so git recorded a tree containing only the adds.

**Why:** Drive sync and/or a crashed prior git op left a stale `.git/worktrees/<wt>/index.lock`; after clearing it the index was in a reset/empty state relative to HEAD, so `git add <newfiles>` built a tree missing everything else.

**How to apply:**
1. The working tree is NOT damaged — files still exist on disk; only the index/commit is wrong. Verify with `ls` before any destructive fix.
2. Recover: `git reset --mixed origin/main` (rebuilds the index from origin/main; working tree untouched) → `git add <only your intended files>` → verify `git diff --name-status origin/main HEAD` shows ONLY your intended adds → commit → `git push --force-with-lease` (safe on a draft feature branch you own; never main).
3. Prevention: before each worktree commit, proactively `rm -f .git/worktrees/<wt>/index.lock` if present, and always sanity-check `git status --porcelain` shows only expected changes (unexpected `D` lines = corrupted index, stop).

**Second variant, 2026-07-26 — it fires at worktree CREATION, not only at commit.** `git worktree add` finished and reported `HEAD is now at 179d666`, but the index was never written: the directory held `index.lock` (106 KB — the index content, under the lock name) and **no `index` file at all**. `git status --porcelain` then reported a staged `D` for every one of the 804 tracked files. Committing there would have recorded a tree containing only the two new files, exactly as in the 2026-07-15 case.

- **The tell, before you trust any `git status` in a fresh worktree: `git ls-files | wc -l`.** Zero means the index is empty and every `D` line is an artifact, not a real deletion. Files on disk (`find . -type f | wc -l` = 806) confirm the working tree is intact.
- **Recovery here: `rm .git/worktrees/<wt>/index.lock` then `git reset --mixed HEAD`** — rebuild from the worktree's own HEAD, not from `origin/main`, when HEAD is already the intended base. Restored all 804 entries; porcelain then showed exactly the two intended changes. Back up the lock file first rather than renaming it to `index` — a partially-written index adopted wholesale is worse than a clean rebuild.
- **Because 39 stale worktrees had accumulated on this machine**, this is not rare-path: worktree churn is when it happens. Remove worktrees whose branches are merged (`git merge-base --is-ancestor refs/heads/<b> origin/main`) rather than letting them pile up.

Relates to [[drive-worktree-mirror-poisoning]] — both are Drive-filesystem-vs-git hazards. propose-never-merge + draft branches contained the blast radius; origin/main was never at risk.
