---
title: CFL memory store split by working directory
aliases: [memory store split, project slug by cwd, identity-by-working-directory]
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 1 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_cfl-memory-store-split-by-cwd.md
as_of: 2026-08-03 (memory `modified` timestamp; content re-measured 2026-08-06, see below)
fidelity: [verbatim] for quoted spans; measurement re-run and re-verified by this page's own drain pass
tags: [identity-by-cwd, wiki-path-deixis, memory-drain, T-02]
generated_by: wiki-master pilot drain pass, T-02, 2026-08-06
retrieval_key: cfl-memory-store-split-by-cwd
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page (T-02 pilot batch) — an operational/process record
  from the CC memory store, not a corpus-derived claim about a conversation. Exempted per
  wiki/references/agent-memory/README.md admission criterion; field added retroactively 2026-08-06
  when the exclusion-class prerequisite the pilot named as unbuilt was built."
---

# CFL memory store split by working directory

## The finding

CFL's Claude Code agent memory is split across **two slugs**, keyed by the directory a session was
launched from, with no signal to a cold session about which one it loaded.

**Measured on disk 2026-08-02** (`ls -d C:/Users/JonSc/.claude/projects/*/memory`):

| slug | files | state |
|---|---|---|
| `G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer` | **47** | current — the real one |
| `G--My-Drive-Claude-Claude-Foundational-Layer` | **20** | **STALE** — index still says *"R6 ~45/78 done"*, *"Phase 3c running"*, *"raw/sessions/ summary issue fixed"* |
| `G--My-Drive-Claude-Claude-Personal` | **0** | directory exists, empty |

Also present as separate slugs: two on-Drive worktree paths
(`...--claude-worktrees-fable-substrate`, `...--claude-worktrees-wiki-su-2026-07-07`) and
`G--My-Drive-Claude-Claude-Personal-XC-Exchequer`.

## Re-measured 2026-08-06 (this drain pass)

```
$ ls .../projects/G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer/memory/*.md | wc -l
49   # 48 memory pages + MEMORY.md — up from 47 recorded 2026-08-02; 2 new pages added since
$ ls .../projects/G--My-Drive-Claude-Claude-Foundational-Layer/memory/*.md | wc -l
20   # unchanged, confirmed still a distinct file set — NOT merged, per Jon's standing no-destructive-acts instruction
$ ls .../projects/G--My-Drive-Claude-Claude-Personal/memory/*.md
(no files — confirmed empty)
```

The split holds four days later. This is corroboration of the numbers, not a test of the broader
class claim — see "Open falsifier" below.

## Why

Claude Code derives the project memory slug from the launch cwd. Launching CFL from the parent
Drive folder rather than the repo folder yields a different slug and therefore a different memory
store — **with no signal that you are reading the wrong one.**

## How to apply

This is the same defect class as the `wiki/` path-deixis problem one layer down —
**identity-by-working-directory**. `wiki/` resolves by cwd; project memory resolves by cwd too.
Treat them as one issue, not two. Before trusting a memory index in a CFL session, confirm the slug
ends in `-claude-foundational-layer`. The stale parent store's retirement (archive its 20 files into
the repo store, then empty it) is **Jon's call, not a coordinator fix** — retiring it costs him a
working store if he deliberately launches from the parent folder.

**Corollary already on record:** an agent that writes a *relative* `wiki/intake-triage/...` path
deposits into whatever repo it was launched in, so cross-project deposits silently miss. Design
packet: `skills/intake/ready/claude-md-wiki-path-deixis-2026-08-01.md` (untracked as of 2026-08-02;
not independently re-verified by this pass).

## Open falsifier — not resolved by this page

`wiki/intake-triage/SEED-REGISTER-2026-08-03.md` seed S3 names this finding's falsifier: *"Show
Claude Code keys project memory by something other than the launch cwd."* Nobody has run that check.
This page corroborates the underlying measurement; it does not test the falsifier, and per the
seed register's own guard rule a falsifier may not be judged by its author.

## Related

Same-batch drain siblings: none yet directly cross-referenced by this memory's own text.
Not-yet-drained related items named in the source: `mirror-stateless-dispatch-only`,
`drive-worktree-mirror-poisoning`, `live-session-liveness-and-untracked-state` — none of the three
have a `wiki/references/agent-memory/` page as of this pass; they remain in the source-only store.
