---
title: "Long-term FBC enhancement horizon — stage-boundary commits, summary-only branch arm, tailored thinking (claude.ai session 1cb2c3, 2026-08-08)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-FBC; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 1cb2c3
source_kind: session
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-08-1cb2c3-long-term-enhancement-strategy.md
raw_sha256: aa7d9f26f3a31d2f14434bc68b3ad26b5024d10680b6d519b51b73a521008e41
raw_length: 3749 chars / 59 lines (verified turn_count 2, turn_index.py, header_style md)
date: 2026-08-08
retrieval_key: fbc-stage-boundary-branching-horizon-2026-08-08-1cb2c3
aliases: ["long term enhancement strategy 2026-08-08", "FBC stage-boundary commits", "summary-only
  branch arm", "tailored thinking branch"]
generated_by: S-augM-02 synthesis lane (week-2026-09-02 corpus lane), reading the claude.ai native
  export extract directly (raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-08-1cb2c3-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [fbc, horizon-item, branching, thinking-tokens, effort-mode, held-2026-07-20-a]
---

# Long-term FBC enhancement horizon — stage-boundary commits, summary-only branch, tailored thinking

## Summary

A short claude.ai session (2 turns) in which Jon deposited a compressed, deliberately-"not ready"
horizon note extending Frame-Before-Commit (FBC) beyond its current input-side discipline: branch
at the end-of-thinking commit point and again at the output commit point, run a summary-only
branch as a measurement arm against same-model summarization erasing dead ends, tailor thinking
style per branch, and treat effort mode as a variable rather than a fixed setting. The assistant
read the note as a horizon deposit (branches and connections only, no execution), surfaced a
feasibility flag (API-signed thinking blocks are not trivially replayable via prefill), and offered
to capture it as an intake-triage horizon item — that offer's answer is not in this raw.

## Key Claims

- **Jon's compressed horizon note extends FBC to two new commit points: end-of-thinking and
  output.** "On critical messages, branch. Commit on thinking tokens done, separate branch just
  considers thinking summaries. Same for output." [verbatim]
  ([fbc-stage-boundary-branching-horizon-2026-08-08-1cb2c3:T1])
- **The assistant's four numbered branch ideas (B1-B4) are its own extension of Jon's note, not
  independently Jon-sourced.** B1 (stage-boundary commits) is framed "grounded in your FBC corpus;
  extension is my read"; B2 (summary-only branch as a measurement arm, tied to
  HELD-2026-07-20-A/BHM resampling) is tagged `[MEM]`; B3 (tailored thinking per branch) is tagged
  `[instinct]`; B4 (effort as a variable) is tagged `[ASSUMED]`. [paraphrase]
  ([fbc-stage-boundary-branching-horizon-2026-08-08-1cb2c3:T2])
- **A feasibility flag was raised against the "commit thinking, then branch outputs from fixed
  thinking" scheme: API thinking blocks are signed and not trivially replayable via prefill** —
  workable inside tool-use continuations, not for arbitrary resampling — tagged `[training,
  uncertain]`, referencing the drain corpus's own `cc-jsonl-thinking-signature-only.md`.
  [paraphrase] ([fbc-stage-boundary-branching-horizon-2026-08-08-1cb2c3:T2])
- **The assistant flagged its own missing grounding at session open**: temporal-context,
  session-order, `GROUNDING_UPDATED.md`, and `FRAME-BEFORE-COMMIT.md` were not visible in this
  project's injected context, so it proceeded on corpus knowledge of FBC rather than the live skill
  files, and named that gap rather than silently smoothing over it. [paraphrase]
  ([fbc-stage-boundary-branching-horizon-2026-08-08-1cb2c3:T2])
- **The session ends on an open question, not a decision**: the assistant asked whether Jon wanted
  a verbatim capture block for intake-triage as a horizon item or to leave it in-session. This raw
  contains no reply. [uncaptured] ([fbc-stage-boundary-branching-horizon-2026-08-08-1cb2c3:T2])

## Jon

> "Long term enhancement. Since earliest roots of FBC. On critical messages, branch. Commit on
> thinking tokens done, separate branch just considers thinking summaries. Same for output. Tailor
> thinking, branch thoughts. Effort mode matters here and more. Not ready."
> — [fbc-stage-boundary-branching-horizon-2026-08-08-1cb2c3:T1] (Jon's sole turn in this raw;
> verbatim)

## Decisions and open items

- No decision was made in this raw. Jon's note is explicitly framed by him as "Not ready" — a
  parked horizon item, not a ruling to act on.
- Open: whether this note was ever captured as an intake-triage horizon item per the assistant's
  closing offer — not resolvable from this raw alone.
- Open: whether B1-B4 map onto (or duplicate) HELD-2026-07-20-A (BHM resampling at branch-points)
  as a sibling experiment or an arm of the same one — the assistant flagged the adjacency but did
  not resolve it.

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[frame-before-commit]] (the protocol this note proposes extending to stage-boundary commit
points), thinking-token signing/replayability, effort-mode-as-variable, HELD-2026-07-20-A.

## Uncaptured Content

- **The assistant's closing question ("verbatim capture block... or leave it in-session?") has no
  answer in this raw** — the session log ends there; whether Jon replied in a later turn or a
  different venue is not known from this file.
- **Google Drive tool-call/result payloads (index.md search) are summarized, not reproduced in
  full** — file IDs and a truncated `fileSize` field are visible but the full search-result JSON is
  not walked here.
