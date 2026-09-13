---
title: No public clone inside the private tree
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_no-public-clone-inside-private-tree.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, exfil-hazard, git-hygiene]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: no-public-clone-inside-private-tree
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# No public clone inside the private tree

*Source description:* Cloning a public repo INSIDE the private CFL working tree creates a real exfil hazard + trips the harness data-exfiltration scanner (false positive on unrelated git ops). Clone to an off-tree location, or immediately remove the public push-remote.

2026-07-22: I cloned `mattpocock/skills` (public) into `raw/upstream/mattpocock-skills/` — inside the private CFL working tree (gitignored, so untracked, seemed fine). Its `origin` carried a **public push-URL**. When a concurrent wiki-SU agent later did a legitimate `git push`/`gh pr create` to the PRIVATE CFL repo, the harness data-exfiltration scanner saw a public-repo push-remote in the environment and flagged the SU as possible exfiltration of private wiki content to `mattpocock/skills`.

**It was a FALSE POSITIVE** — verified: PR targeted `isCrossRepository:false` / private repo; `git ls-remote` on the public repo showed the branch never landed there; the SU worktree's own `origin` was the private repo. But the underlying hazard is REAL: a public push-target living inside the private tree is one stray `git -C`/cwd-slip away from actual exfiltration.

**Why:** the scanner's repoVisibility heuristic keys on public push-remotes *present in the environment*, not only on the exact command's target. A nested public clone poisons the whole tree's git-op safety surface — same family as [[drive-worktree-mirror-poisoning]].

**How to apply:**
- Clone third-party/public repos to an **off-tree** location (scratchpad, or a sibling dir outside the private repo root) — not under the private working tree, even in a gitignored path.
- If it must live in-tree, **immediately** `git -C <clone> remote remove origin` (or set push URL to `no_push`) right after cloning. Files + `git log -1` pinned HEAD survive the remote removal.
- When the harness fires an exfil/security warning, **verify before relaying** (per [[verify-conditional-claim-resolution]]): check the PR's `isCrossRepository`, the actual worktree `origin`, and `git ls-remote` the suspected public target for the branch. Report the resolved truth, not the raw alarm — but treat the tripwire as a signal to fix a real hazard, not noise to dismiss.
