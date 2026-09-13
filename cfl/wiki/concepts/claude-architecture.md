---
title: Claude Architecture — Statelessness, Context Window, and Persistent Context
trunk: fl
branch: [UNASSIGNED]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; no registered branch keyword in title, slug, tags or headings"
concept_type: research-background
sources:
  - claude-conversation-mechanics-2026-03-06-c310bf
  - claude-data-privacy-2026-03-11-1d3d2e
  - ai-mechanics-token-api-2026-03-26-8b5b19
last_updated: 2026-06-01
---

# Claude Architecture — Statelessness, Context Window, and Persistent Context

Covers how Claude sessions work at the product and infrastructure level: stateless design, context window assembly, persistent context mechanisms, branching conversations, and data privacy properties. Distinct from [[ai-mechanics]], which covers the inference-level (token sampling, attention, temperature). These two layers together answer "how does Claude work" from the product level down to the forward pass.

Directly relevant to why the [[extraction-pipeline]] and [[wiki-master-origin]] pattern exist: the stateless design is the architectural problem that the CFL wiki solves.

---

## Stateless Design

**No server-side session state.** Each API request is a fresh inference. Claude does not retain anything between turns except what is explicitly included in the context transmitted with the current request. This is a deliberate design choice, not a limitation — it eliminates session corruption and stale-context bugs at the cost of full re-transmission on every request.

**Stateless design is also a security property:** Nothing persists server-side between turns, reducing tampering risk and providing a hard privacy boundary.

**The model has no memory of prior conversations** unless explicitly retrieved via past_chats tools or similar retrieval mechanisms. Context window assembly is the sole "memory" mechanism.

---

## Context Window Mechanics

**Every message transmits the full context.** System prompt, project files, userMemories, document attachments, and message history all travel with each request. Context starts at thousands of tokens of overhead before the user types a word.

**Scale reference:** Token ≈ ¾ word, ~4 bytes. 200K tokens ≈ 800KB, ~500 pages. Claude 3 context windows (200K–1M tokens) are large by historical standards but still finite — context overhead accumulates across a long session.

**Prompt caching partially offsets cost:** Repeated prefixes (system prompt, project files) can be cached at reduced compute cost even if bytes still travel the wire. This is the mechanism that makes CLAUDE.md efficient to maintain across many sessions.

---

## Persistent Context Mechanisms in claude.ai

Three mechanisms carry context across conversations, each with different reliability and fidelity:

1. **Memories** — lossy summaries generated and surfaced automatically. No guarantee which memories are retrieved for any given conversation. Most direct cross-session mechanism but imprecise.
2. **Custom instructions / User preferences** — pasted into every session in that account. Reliable and predictable; this is the mechanism CLAUDE.md-style configuration exploits in Claude Code.
3. **Projects** — documents attached to a project persist across conversations scoped to that project. More structured than memories; lower retrieval uncertainty.

**CLAUDE.md in Claude Code** is the Claude Code analog of custom instructions — injected into every session automatically. It is separate from claude.ai's features; they don't share state.

---

## Conversation Branching

Claude.ai allows editing any prior message, branching the conversation from that point. Everything after the edit is discarded in the new branch; the original thread remains navigable. This is a UI-level branching mechanism, distinct from [[frame-before-commit]] protocol branching, which happens within a single forward generation.

---

## Training and Privacy

**Conversation data may train future models:** By default on claude.ai, conversations can be used for model training unless opted out in Settings → Privacy.

**Individual user interaction style does not directly shape future models:** Training is aggregated and abstracted. Jon's interactions may contribute to better general patterns for skilled users, not a model tuned specifically to Jon.

**Data categories worth caution in sharing:** Personal health information, other people's data without consent, proprietary/trade-secret business information, financial account details, combinations of details that profile third parties.

**Hard refusals are narrow:** Claude won't produce content enabling mass harm, CSAM, or actual malware. The more practically useful framing is "what to be skeptical of in Claude's outputs" rather than "what to avoid discussing."

---

## CFL Design Implications

The stateless architecture is the root constraint that motivated the [[wiki-master-origin]] pattern. The problem: every session starts fresh, so insights from Session A are unavailable in Session B unless explicitly carried. Solutions attempted before the wiki:

- Memories (lossy, unpredictable)
- Custom instructions (reliable but fixed-size)
- Projects (scoped, not cross-project)

The CFL wiki takes a different approach: LLM-maintained, incrementally compiled knowledge base. Knowledge produced in sessions is compiled into wiki pages, committed to git, and injected via CLAUDE.md at session start. The wiki is not RAG — it is a curated, maintained synthesis layer.

---

## Related

- [[ai-mechanics]] — inference-level mechanics (sampling, attention, forward pass)
- [[extraction-pipeline]] — the pipeline for extracting session content before it is lost
- [[wiki-master-origin]] — why the wiki pattern exists given this architecture
- [[design-execution-split]] — claude.ai vs Claude Code in this architecture
