---
title: Design/Execution Split
trunk: fl
branch: [UNASSIGNED]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; no registered branch keyword in title, slug, tags or headings"
type: concept
first_seen: skills-master-wiki-pipeline-2026-05-01-bcafba
source_count: 1
last_updated: 2026-05-09
---

## What This Is

The architectural principle governing how work is distributed across claude.ai and Claude Code. Design — working out what to build, iterating on protocol, writing [[skills-system]] specifications — happens in claude.ai. Execution — filesystem operations, git, running tests, wiki writes, API calls — happens in Claude Code. Not a compromise or interim arrangement: each environment does one thing and does it well.

## What the Wiki Says

### The Three Layers

Established via two FBC runs in skills-master-wiki-pipeline-2026-05-01-bcafba:

1. **claude.ai** — relational and orienting layer. Working context, who Jon is, how to work with him, philosophical framework. Ambient context that shapes interactions. Also the design environment: where skills are iterated, protocols worked out, and specifications written.

2. **Wiki (GitHub repo)** — compounding operational knowledge layer (see [[wiki-master-origin]]). Test theory, findings, protocol state, analyses, session sources. Owned by Jon, not locked in a chat. Grows over time. When Claude Code reads the wiki before operating, it inherits accumulated synthesis — qualitatively different from session memory.

3. **Claude Code** — execution hands. Reads wiki and skill files, runs tests, writes outputs back, commits. Operates programmatically without conversational overhead.

([skills-master-wiki-pipeline-2026-05-01-bcafba])

### What Each Layer Is NOT

- claude.ai is not an execution environment. It cannot write files, call APIs programmatically, capture outputs, or commit. Tests run here are theater.
- Claude Code is not the design environment. It executes better than it designs. Skill design in CLAUDE.md without a prior design conversation produces unbounded execution.
- The wiki is not memory. It's a durable artifact. Its value is ownership and compounding, not session injection.

([skills-master-wiki-pipeline-2026-05-01-bcafba])

### What Migrates and What Stays

**Migrates to wiki/Claude Code:** Operational knowledge — test master content, protocol theory, test designs, session findings, analyses. Anything that should survive and compound.

**Stays in claude.ai:** Working context, relational layer, session memory. Anything that shapes interactions rather than accumulates in an artifact.

The migration question is smaller than it appears once the split is clear. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

### CLAUDE.md as Bridge

The injection mechanism that makes Claude Code feel like a persistent relationship rather than a cold tool. CLAUDE.md is the full working context as a file — read automatically every session, no lossy summarization. The relational layer can live in Claude Code if CLAUDE.md is written well. This dissolves the argument that "the relational layer has to stay in claude.ai." ([skills-master-wiki-pipeline-2026-05-01-bcafba])

## Conflicts

None.

## Related

[[skills-system]], [[frame-before-commit]]
