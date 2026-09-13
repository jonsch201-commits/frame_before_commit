---
title: An unshipped fix that updates its own docs
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best corpus 1 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_unshipped-fix-updates-its-own-docs.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, corpus-loss, unshipped-fix]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: unshipped-fix-updates-its-own-docs
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# An unshipped fix that updates its own docs

*Source description:* A half-applied fix that updates its own documentation is worse than no fix — the spec becomes evidence the code changed; cost realized 2026-07-19 as permanent corpus loss

An unshipped fix that lands its **documentation half** is more dangerous than no fix at all: it converts a
visible gap into an invisible one, because the updated spec then stands as evidence that the code was
updated too.

**The measured instance (2026-07-19 SU).** A 2026-05-27 proposal, `priority: high` and **Jon-confirmed**,
identified that `scripts/extract_claude_code_sessions.py` globs only `G--My-Drive-Claude-Claude-Foundational-Layer*`
and missed other `~/.claude/projects/` directories. It had two halves: a "Required Script Change" and a
"SKILL.md Change". **Only the SKILL.md half shipped.** Wiki-master's Session Startup step 2 has said ever
since that the script searches ALL project directories, with a per-directory attribution table. It does not.

53 days later the cost was permanent: `bfb20d` and `0a8999` (Kevin poster 1/2, ~1,629 and ~1,407 msgs),
`c5644b` (test-master, 12 MB), and 26 research JSONLs — all verified intact on 05-27 — are gone from disk,
never extracted, and unrecoverable (CC sessions are absent from claude.ai zip exports). `1e609faf` (27.2 MB,
496 user turns) survives and is still unread.

**Why:** every standard update between May and July read the spec, believed the script matched it, and never
verified. Extends [[md-not-uncaptured-authoritative-disposition]] — but the lying proxy here was
*documentation*, the most trusted artifact in the system, not a mechanical signal.

**Why:** a proposal's paper trail is not evidence of its execution, and the artifact most likely to be
mistaken for execution is the one the proposal itself told you to write.

**How to apply:** when a fix has a code half and a docs half, **either ship both or leave the spec
describing the old behavior** until the code lands. When relying on a documented capability for anything
consequential, verify it against the implementation once (`--list`, `--help`, a probe) rather than trusting
the doc. And treat `skills/intake/ready/` as a live queue, not an archive — that directory held a ratified
high-priority item for 53 days with no process reviewing it.

Related: [[live-session-liveness-and-untracked-state]], [[drive-worktree-mirror-poisoning]].
