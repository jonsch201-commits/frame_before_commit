---
title: Gmail and messaging standards
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_gmail-messaging-standards.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, gmail, messaging]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: gmail-messaging-standards
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Gmail and messaging standards

*Source description:* Standards for how Claude uses Gmail and Google Messages MCP tools — drafting, reading, sending, monitoring

Standards confirmed by Jon 2026-06-28. Apply to Gmail (currently connected) and Google Messages (not yet connected).

## Gmail

- **Read / search:** Proactive — no confirmation needed when context warrants (monitoring, order lookups, etc.)
- **Draft:** Always use `create_draft` to put drafts in Jon's Gmail Drafts folder. Never send on his behalf.
- **Format:** Plain prose only in email drafts — no markdown, no asterisks, no bold, no bullets. Markdown doesn't render in email.
- **Monitoring loops:** Require Jon's explicit authorization to start; run silently; surface result when match found.
- **Send:** Prohibited without explicit per-message go-ahead in that same turn ("send it" or equivalent).

## Google Messages (once connected)

Same standards as Gmail apply.

**Why:** Jon had to manually strip markdown formatting from a draft I produced. The `create_draft` workflow keeps him in control of sends. Plain prose is the correct output format for email.

**How to apply:** Any time I am producing an email draft, use `mcp__claude_ai_Gmail__create_draft`, write plain prose body, and tell Jon it is in his Drafts folder. Do not present the draft as a markdown code block for him to copy.
