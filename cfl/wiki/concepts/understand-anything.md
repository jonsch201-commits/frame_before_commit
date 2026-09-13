---
title: Understand-Anything Plugin
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (skills); sub: skills 2 vs wiki 1 on authored labels"
type: concept
first_seen: wiki-multi-master-audit-2026-06-02-dba2c0b
source_count: 3
last_updated: 2026-06-04
---

## What This Is

Lum1104/Understand-Anything v2.7.5 is a Claude Code plugin that builds a structured knowledge graph over a codebase or wiki. For the CFL project, it was installed and configured to traverse the FL wiki, producing a 329-node graph as a traversal interface over wiki content. `parse-knowledge-base.py` was patched to handle Jon's table-format wiki index. The plugin gives Claude a structured graph navigation layer over the wiki in addition to direct file reads.

The artifact lives at `wiki/.understand-anything/`. The primary FL source is wiki-multi-master-audit-2026-06-02-dba2c0b; a personal wiki source ([PERSONAL: herald-excel-understand-anything-2026-05-29-ced2a6]) adds Herald integration context.

## What the Wiki Says

### Installation and Graph State

Installed during the multi-master wiki improvement session (dba2c0b) as part of the early Herald/Understand-Anything integration phase (T1–T80 of that session). Plugin: Lum1104/Understand-Anything v2.7.5.

Graph state after initial setup:
- **329 nodes total**: 154 articles, 130 entities, 34 claims, 11 topics
- **597 edges**
- Built over the FL wiki content

([wiki-multi-master-audit-2026-06-02-dba2c0b:T82])

**Updated graph state after 2026-06-04 rebuild (commit d28e66d):**
- **863 nodes total**: 170 articles, 11 topics, 124 entities, 558 claims
- **1100 edges**
- Increase from 329 → 863 nodes reflects Key Claims extraction (item 13A) as first deterministic claim graph
- ⚠️ `categorized_under = 0` still present — parse-knowledge-base.py does not handle Jon's backtick table-format index; fix pending

([wiki-session-conflict-resolution-crosslinks-2026-06-04])

### parse-knowledge-base.py Patch

The default `parse-knowledge-base.py` script did not handle Jon's table-format wiki index. A patch was applied during the setup session to correctly parse the index format. Without this patch, the plugin would misread the FL wiki's index structure and build an incomplete or malformed graph. ([wiki-multi-master-audit-2026-06-02-dba2c0b:T82])

### Operational State

As of 2026-06-04, the plugin is installed and working. The knowledge graph is live at `wiki/.understand-anything/`. The plugin is tracked in `project_wiki_state.md` in memory.

**Article-analyzer dispatch note:** The article-analyzer runs as a Claude Code subagent via the Agent tool — it does NOT require an external API key or `.env` credentials. If a rebuild agent reports "API authentication failure" or falls back to inline analysis, the diagnosis is wrong. The correct action is to re-run with explicit Agent tool dispatch. Silent fallback to inline-only analysis skips entity extraction and produces 0 entity nodes in the graph. This failure mode occurred in the 2026-06-04 first rebuild attempt before Jon's second rebuild succeeded. ([wiki-session-conflict-resolution-crosslinks-2026-06-04])

### Herald Integration Context

In the Herald session [PERSONAL: herald-excel-understand-anything-2026-05-29-ced2a6], Jon asked whether the Understand-Anything skill could be applied to raw conversation logs — treating them as "code" for the plugin's purposes, with meta-knowledge sitting on top. The answer was left open pending skills-master clarification of the skill's definition of "code." This use case (applying the graph-traversal interface to session logs rather than wiki articles) is not yet implemented or scoped.

### Relationship to Wiki Navigation

The plugin provides a complementary navigation layer to direct file reads. The recommended cold-session workflow — read `wiki/index.md` first, then relevant concept pages — remains primary. The graph interface is most useful for traversal and relationship discovery across the 329 nodes, not for targeted claim lookup.

### Caveman Skill Reference

The multi-master session that installed Understand-Anything also produced the Caveman skill (ultra-compressed communication mode). Both were created in the same session arc, though they are unrelated capabilities. ([wiki-multi-master-audit-2026-06-02-dba2c0b:T212])

## Conflicts

None.

## Related

[[wiki-ingest-methodology]], [[herald-of-home-and-life]]
