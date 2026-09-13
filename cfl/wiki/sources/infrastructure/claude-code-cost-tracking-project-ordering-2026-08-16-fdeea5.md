---
title: "Claude Code cost tracking, three telemetry tiers, and why dollars is the wrong ordering variable on a subscription — claude.ai secretary seat, 2026-08-16 (fdeea5)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: fdeea5
source_kind: session
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-16-fdeea5-claude-code-cost-tracking-and-project-prioritizati.md
raw_sha256: 53f3a7e4bd89c67342aabfe74fcfd02bacdd90faafab67fbe70d2f410bf411f8
raw_length: 9705 chars / 131 lines (verified turn_count 4, turn_index.py, header_style md)
date: 2026-08-16
retrieval_key: claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5
aliases: ["Claude Code cost tracking 2026-08-16", "OpenTelemetry api_request cost_usd",
  "plan-window not dollars ordering variable", "7x teammate plan-mode cost finding"]
probe_sealed: "Does a wiki page already exist for session fdeea5 (Claude Code cost tracking and
  project prioritization, 2026-08-16)? => No — `wiki/sources/**/*-fdeea5.md` returns no match in
  this clone as of 2026-09-02. TRUSTED"
generated_by: S-aug-13 executor (week-2026-09-02-corpus lane), reading the claude.ai native-JSON
  extract directly (raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-16-fdeea5-...md, FULL
  extraction, 2 thinking blocks preserved)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [claude-code, telemetry, cost-tracking, secretary, cfl-infra, ordering]
---

# Claude Code cost tracking, three telemetry tiers, and dollars-is-the-wrong-variable — 2026-08-16 (fdeea5)

## Summary

A short claude.ai secretary session (2 human turns) in which Jon asked whether Claude Code's
per-turn cost is calculable and how far below the turn level it breaks down, framing it as an input
to cost/benefit project ordering. The assistant researched current Anthropic docs live (three
web-fetch/web-search round trips) and returned a three-tier answer — built-in `/usage`, OpenTelemetry
`api_request` events, and a traces beta span tree — then corrected Jon's framing on two points: there
is no forward cost estimator, and on a subscription plan the scarce resource is the plan window, not
dollars. Jon's second turn asked only whether the session was fully triaged; the assistant reported
two files written to Drive (a rulings file and a Code-seat instrumentation letter) and flagged its
own near-miss of asking a low-materiality question.

## Key Claims

- **Three telemetry tiers exist for Claude Code cost, verified against current docs.** Tier 1:
  `/usage` shows session token counts and a local list-rate dollar estimate, plus (on Pro/Max/Team)
  attribution to skills, subagents, plugins, and individual MCP servers as a percentage of total.
  Tier 2 (OpenTelemetry, `CLAUDE_CODE_ENABLE_TELEMETRY=1`): an `api_request` event per API call
  carries `cost_usd`/`cost_usd_micros`, token counts, and attribution attributes
  (`agent.name`/`skill.name`/`plugin.name`/`mcp_server.name`/`mcp_tool.name`); every event from one
  prompt shares a `prompt.id` UUID, so summing `cost_usd` over one `prompt.id` gives exact per-turn
  cost. Tier 3 (`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`): a `claude_code.interaction` root span with
  `llm_request`/`tool`/hook child spans, per-span token counts and time-to-first-token.
  [contextual] ([claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5:T2]) [source: three
  web_fetch calls against code.claude.com/docs, this raw, T2]
- **Two corrections to Jon's cost-ordering framing.** No forward estimator exists — every cost
  surface is measured after the fact, so cost-aware ordering needs a baselining pass (run each
  operation once, record cost) that itself costs something. Second, on a Max/Pro subscription the
  session-cost figure is not billing-relevant; the real constraint is the rolling five-hour and
  weekly plan-window allowance, and the docs name the exact failure modes this program's
  always-on multi-trunk design invites: long-open sessions resending full context, scheduled tasks
  firing while idle, cross-session messages arriving as fresh full-context turns, and agent teams
  using roughly 7x tokens when teammates run in plan mode. [paraphrase]
  ([claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5:T2])
- **Two Drive files landed from this session, not offered as a future action.** A rulings file
  (`rulings/2026-08-16-jon-rulings-cost-visibility-and-project-ordering.md`) and a Code-seat
  instrumentation letter (`exchange/inbound/secretary-claudeai-to-code-COST-INSTRUMENTATION-2026-08-16.md`,
  five tickets with acceptance tests) were created via the Google Drive connector during this
  session. [paraphrase] ([claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5:T4])
- **The assistant named its own near-defect: ending a reply with an offer rather than a delivery.**
  Its own words: "in the first reply I ended with 'say the word and I'll write it.' That's a request
  for your attention wearing a delivery's clothing." It also reported that both candidate follow-up
  questions it considered asking Jon (whether the baselining pass is worth its cost; whether cost
  instrumentation should precede an eval harness) failed a materiality gate because both were
  cost/benefit ordering calls the assistant was already resolving in the same session. [verbatim]
  ([claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5:T4])
- **A folder-ID correction was caught by verification, not assumption.** The `rulings/` folder ID
  the assistant was carrying differed from the one in Jon's own message by one character; the
  assistant searched Drive rather than trusting the carried value and used the correct one.
  [paraphrase] ([claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5:T4])

## Conflicts

None with existing wiki content.

## Jon

- **T1** — "Cost. I know when I use VScode at work, I know the credit cost of every message I send.
  I don't see that in Claude Code, but I infer it must be claculatable. Product documtation check.
  How can we improve our cost estimates per turn and how well does this break down below the turn
  level? We've done a couple tests, and I assume this is solvable. One key aspect of project
  ordering is considering cost and benefit, and that can't be on me. We all have the vision, we
  don't have the full order. And we don't have data to consider cost to help you consider the best
  order of actions. For the record, I've spent personally under $400 on Claude since I started, and
  I feel it's been well with it. Thank you, Anthropic for the subsidy." [verbatim]
  ([claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5:T1])
- **T3** — "Any questions for me, or is this good and triaged and will materially help without
  another word from me?" [verbatim] ([claude-code-cost-tracking-project-ordering-2026-08-16-fdeea5:T3])

## Decisions and open items

- Jon ruled (in substance, via his framing accepted without correction) that project ordering
  should weigh cost against benefit rather than resting entirely on his own judgement; the assistant
  took ownership of the two materiality-failing sub-questions rather than routing them back to him.
- Open item, assistant's own flag: whether the review-then-`go` pattern from a prior day should
  govern this seat's writes going forward, versus the write-then-report pattern used here — left to
  Jon to state a preference on.
- The instrumentation build (env vars, collector, attribution rollup) was handed to the Code seat
  via letter; this page does not confirm whether that build has since landed.

## Entities & Concepts

[[coordinator]] (the secretary seat dispatching a ticket to a build-capable seat), Claude Code
telemetry (`/usage`, OpenTelemetry, traces beta), plan-window vs. dollar cost framing.

## Uncaptured Content

- **The two Drive-written files' full content is not read independently on this page** — only the
  assistant's own summary of what went into them, at T4. A claim about their exact wording is out
  of scope here.
- **Whether the Code seat actually built the OpenTelemetry instrumentation is not addressed** — this
  raw ends with the letter sent, not with a build receipt.
