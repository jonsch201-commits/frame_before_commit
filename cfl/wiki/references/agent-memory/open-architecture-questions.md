---
title: Open architecture questions
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: sub-branch too close to call: wiki 2 vs skills 2 (margin < 1)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_open-architecture-questions.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, architecture, open-questions]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: open-architecture-questions
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Open architecture questions

*Source description:* Unresolved design questions about system architecture raised 2026-05-22. Require Jon input before acting.

Architecture questions Jon raised 2026-05-22 that are not yet resolved. Do not act on these without Jon's direction.

**Why:** These are configuration-level decisions, not skill-level decisions. Acting without Jon's input risks architectural inconsistency.

**How to apply:** At next relevant session, surface these to Jon. Do not implement independently.

---

## 1. Real Agents vs. Skills Stacked on Skills

Jon: "We also likely need to improve and formalize the skill improvement loop. And, maybe make actual official agents rather than just skills stacked upon skills."

Current state: test-master, wiki-master, skills-master are markdown skill files read by a single Claude instance. They don't have isolated context, their own CLAUDE.md files, or their own tool access.

What "real agents" might mean: actual Claude Code agent configurations with dedicated system prompts, separate CLAUDE.md files, defined tool access. Would require config changes.

Open question: which roles should become real agents? What would that require from Jon?

---

## 2. Wiki-Master as Session-Open Subagent

Jon: "You may need to literally reference the wiki for your own memories at times. This may require I update config settings and wiki master settings."

Current state: wiki-master is invoked manually when Jon or I ask. There's no standing mechanism to query it at session open.

What this would require: wiki-master launchable as a reliable subagent with its own context. Possibly a config setting that auto-invokes wiki-master at session start with a relevance query.

Open question: what config changes does Jon need to make? What's the right trigger for mid-session wiki queries?

---

## 3. Grill-Me Skill Location and Integration

Jon referenced a grill-me skill in passing (2026-05-22). He noted "grill-me is existing skill" in 02-CF methodology session (LOG.md 2026-05-20). The URL he referenced (github.com/mattpocock/skills) was an external reference.

Open question: where does the grill-me skill live in this project? Should it be a formal step in the Hypothesis Loop or Skill Improvement Loop?
