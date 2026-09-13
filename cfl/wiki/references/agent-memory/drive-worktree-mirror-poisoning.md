---
title: Drive-worktree mirror poisoning
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-AGENTMEM; sub: fleet 3 vs wiki 0 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\reference_drive-worktree-mirror-poisoning.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, drive-sync, worktree]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: drive-worktree-mirror-poisoning
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Drive-worktree mirror poisoning

*Source description:* Repo lives ON Google Drive → every worktree is a divergent cold-read mirror; main checkout parked on a stale branch poisons claude.ai Drive reads

The CFL repo lives *on* Google Drive (`G:\…\claude-foundational-layer`). Google Drive syncs the raw filesystem — **every worktree's working tree, on whatever branch it's on, plus untracked files** — and the filesystem has no concept of a canonical branch. So the claude.ai Drive connector cold-reads "whatever branch each copy is parked on," NOT `origin/main`.

Consequences found in the P1 canonical-copy reconciliation (2026-07-15, autonomous run):
- `.claude/worktrees/` is NOT excluded from Drive sync → a Drive search for any slug returns N divergent copies (one per worktree). E.g. a remediated page reads *fixed* in the PR-branch worktree copy and *pre-fix* in every other copy — the connector can return either.
- The main checkout was parked on a stale feature branch **10 commits behind origin/main** → the primary cold-read surface was 10 merges stale, plus untracked intake files inside `wiki/`.

Proposed enforcement (Jon-gated, in PR #26): **E2 relocate `.claude/worktrees/` off Drive** (highest leverage); **E1** one canonical read copy held on `main` + auto `pull --ff-only` after merges as the sole Drive-connector target; **E3** untracked-in-wiki lint. Safe immediate fix: `git checkout main && git pull --ff-only` in the main checkout.

Deeper version of [[drive-lag-stale-read-hazard]] — that one is "git-clean but stale working file"; this is "the whole read-surface has no branch awareness." Always read consequential state via `git show origin/main:<path>`, never a worktree path.
