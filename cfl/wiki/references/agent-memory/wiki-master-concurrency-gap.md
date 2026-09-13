---
title: Wiki-master concurrency gap
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-AGENTMEM; sub: wiki 8 vs skills 0 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_wiki-master-concurrency-gap.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, concurrency, wiki-master]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: wiki-master-concurrency-gap
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Wiki-master concurrency gap

*Source description:* Live discovery 2026-07-03 that wiki-master has no protocol for concurrent/background operation — 3 intake packets filed, awaiting an interactive skills-master session

Wiki-master (and skill ecosystem generally) currently has no defined protocol for two or more
processes writing to `wiki/` concurrently, and no distinction between a narrow "ingest just this
session" trigger and a broad "sweep the whole backlog" operation. Both gaps were caught live on
2026-07-03: this session ran its own wiki-master detection pass while a second, Jon-directed
process (his own separate PM session, plus at least one other concurrent wiki-master-equivalent
run) wrote to the same files uncommitted, with no coordination signal between them.

**Why this matters:** Jon flagged (independently, same evening) that he's "been lazy with my
GitHub" and wants branching/merging discipline for wiki updates researched properly — this
concurrency event is direct, concrete evidence for that concern, not a hypothetical.

**Three packets now sit in `skills/intake/`, meant to be worked as one interactive skills-master
session (Jon present, not autonomous):**
- `human-required-skills-master-wiki-git-workflow-2026-07-03.md` — branching/merging discipline
- `session-close-wiki-update-mandate-2026-07-03.md` — filed by the *other* concurrent process; proposes mandatory wiki update at every session close
- `human-required-skills-master-wiki-update-triggers-2026-07-03.md` — this session's correction/extension: the mandate packet's stated scope ("current conversation only") didn't match its own actual behavior (it also swept in unrelated backlog); proposes splitting into a narrow mandatory job vs. a broad optional one, plus a possible new "session map" artifact (distinct from `handoff` output and from memory) to brief a background wiki-ingest subagent cheaply.

## How to apply

Do not resolve any of these three autonomously — Jon explicitly wants to clarify intent and best
practices together in that session. When a skills-master session next runs, brief it with all
three packets together, since they're facets of one problem. See [[backup-desktop-reorg]] for the
unrelated task that surfaced this during the same session.
