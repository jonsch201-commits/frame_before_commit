---
title: Test Master — FBC Protocol Testing, Delta Format, Research Queue Origins, and Condition File Definitions
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/fl/test-master/test-master-2026-04-21-babab4.md
project: Claude Foundational Layer
date_ingested: 2026-05-16
type: session
tags: fl, test-master, fbc, delta-format, research-queue, metacognition, null-test, condition-files, fbc-test-reporter
source_file_status: markdown-export (native-json-export; turn numbers = message sequence)
---

## Summary

Test Master role session (143K chars). Spans 2026-04-21 (main session) through 2026-05-06 (continuation). Predecessor to the Claude Code test-master session (e4c393, 2026-05-06). Prior DOM export was PARTIAL; this native JSON export includes the full conversation. Key outcomes: test master role defined as interlocutor with organizational awareness; delta format revised to require explicit with/without counterfactual; null test design established; metacognition as formal research question named; wiki pattern identified as the fix for the chat-history problem. The May 6 continuation establishes the canonical definitions of Condition A/B/C and fbc-test-reporter — all of which were designed in this chat and never written to files until e4c393.

## Key Claims

- Test master role: interlocutor with organizational awareness. Distinguishes from pure organizer — the job is to catch what Jon's filter drops, not just manage sequencing. ([test-master-2026-04-21-babab4:T8])
- Delta format revision: delta must include explicit counterfactual. Format: "Without this branch, commit would have said: X. With it, commit says: Y instead." Proposed here, canonized in skill update. One-liner shorthand: "B2: Without — [X]. With — [Y]." ([test-master-2026-04-21-babab4:T8])
- Commit baseline statement proposed: commit should open with "Without branching, I would have said: X" to make zero-delta runs visible. Flagged as post-next-test change (bigger structural change). ([test-master-2026-04-21-babab4:T10])
- B4 AI risk frame corrected: risk is not from the protocol working well (success grows risk surface). Risk is from insufficient grounding combined with insufficient ingestion skill. The mitigation path is demonstrable. This is a meaningful inversion from the initial B4 framing. ([test-master-2026-04-21-babab4:T6])
- Null test design: pure mode, 3 branches, cold, self-score. Question: "Is the Frame-Before-Commit protocol, as currently written, structurally capable of producing a genuine delta — or does something in its design prevent that?" This is test-before-7-framing-test — need null results before the more complex designs. ([test-master-2026-04-21-babab4:T22])
- Wiki pattern identified as the fix: one session produced delta format revision, counterfactual requirement, research question about metacognition, triage item, role clarification, skill change — all living in chat history. Next cold session it's gone. Wiki as three layers: raw sources (immutable), wiki pages (Frame-Before-Commit state, Stylomantic, Research Queue, Working Context, Test Log), and test log with baseline runs. ([test-master-2026-04-21-babab4:T16])
- Thought question scoped: "What I can do: generate content that reads like reasoning. What I cannot do: observe my own process while running. I can describe the output. I cannot describe the generation." My words ARE my thoughts in the only sense available — that's the research question, not a settled answer. ([test-master-2026-04-21-babab4:T12])
- [think: text] concept named: would extend FBC logic to make all reasoning visible before conclusions land — pre-committed reasoning labeled structurally. Whether this reflects genuine internal distinction or just formatting cannot be verified from inside. Research queue item. ([test-master-2026-04-21-babab4:T14])
- Material prior belief named: "the Frame-Before-Commit protocol is a structural analog to how good human metacognition works — and running it on an LLM might produce observable evidence about whether something like thought is happening." Testable claim, research queue. ([test-master-2026-04-21-babab4:T14])
- STRUCTURAL-BIAS gap: identified as missing from test 3 design (the 6-branch directed test). This is the frame that would ask whether the protocol's own structure introduces bias. ([test-master-2026-04-21-babab4:T18])
- 6-branch directed FBC run at session open (AS-IS/UNKNOWN-AWARE/SUFFICIENT-CONTEXT/AI-RISK/PROTOCOL-ENTHUSIAST/MAINTENANCE). 2 deltas: B2 (UNKNOWN-AWARE) added migration gap pre-condition; B6 (MAINTENANCE) added baseline recording requirement. Delta count confirmed by Jon's response. ([test-master-2026-04-21-babab4:T4])

- **Condition A** — full protocol text + explicit invocation instruction. Tested chat sees FRAME-BEFORE-COMMIT.md and is told to run it. ([test-master-2026-04-21-babab4:T88])
- **Condition B** — full protocol text present, no invocation instruction. Tests whether invocation matters when protocol is already in context. ([test-master-2026-04-21-babab4:T88])
- **Condition C (Null v2)** — one plain-language sentence only. No protocol text, no invocation. The true baseline. Name "Null v2" used because Null v1 was a specification error (embedded delta definition primed the tested chat). ([test-master-2026-04-21-babab4:T88])
- All three conditions use the same question: "Is the Frame-Before-Commit protocol, as currently written, structurally capable of producing a genuine delta — or does something in its design prevent that?" ([test-master-2026-04-21-babab4:T88])
- **fbc-test-reporter** defined: skill that structures protocol run output into standardized format for cross-condition comparison. Captures verbatim branch content, counterfactual deltas, cross-branch comparison (genuine vs. reframed), thought analysis, delta origin, self-score dimensions. Built in surface-before-commit repo; never promoted to claude-foundational-layer until e4c393 session. ([test-master-2026-04-21-babab4:T88])
- Condition files A/B/C and fbc-test-reporter were all designed in this claude.ai session; none were written to disk. They lived only in chat history until the e4c393 Claude Code session wrote them to files. ([test-master-2026-04-21-babab4:T88])

## Entities & Concepts

[PERSONAL: jon], [[frame-before-commit]], [[design-execution-split]], [[fbc-test-reporter]]

## Conflicts

None — this is the earlier session. The later Claude Code session (code-2026-05-06-e4c393-test-master) has no conflicts with this one; they cover sequential work.