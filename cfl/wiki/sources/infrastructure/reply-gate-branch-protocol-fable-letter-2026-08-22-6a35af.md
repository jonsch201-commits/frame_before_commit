---
title: "Reply-gate protocol and orthogonal branching, designed and prototyped live on the Fable letter — CFL Personal/Soul, branch of 10a453 (session 6a35af, 2026-08-21/22)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 6a35af
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-22-6a35af-system-reminder-the-user-named-this-session-branch.md
raw_sha256: bc4920a251711df4b01357587ef50135b1672f64ef25436aba0aa80138a9ec5c
raw_length: 326559 chars / 4954 lines (verified turn_count 203, turn_index.py, header_style md)
date: 2026-08-22
retrieval_key: reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af
aliases: ["reply-gate protocol ready+direction", "orthogonal branching prototype 2026-08-21",
  "dot plus question dash gate", "DRAFT-first-message-to-fable-cfl hardening session",
  "session branch tree 10a453-01c3b6-67214b-6a35af"]
generated_by: S-aug-01 synthesis lane (week map RP-3/RP-4), reading the raw transcript directly
  (raw/transcripts/claude-code/code-2026-08-22-6a35af-...md, through line ~4838 of 4954 — the
  compaction-boundary summary at the tail, plus the surrounding turns)
probe_sealed: "What four-character reply-gate alphabet did Jon and the Soul seat design in this
  session for a fresh CFL Fable's replies, and what does each character mean?" (expected class TRUSTED)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [reply-gate, orthogonal-branching, frame-before-commit, t35, fable-mirror, session-tree, cfl-infra]
supersedes: [fable-letter-sent-close-ritual-2026-08-22-6a35af]
---

# Reply-gate protocol and orthogonal branching, prototyped live on the Fable letter — Soul, session 6a35af

## Summary

Jon woke the Claude Personal / Soul seat with two asks: be adversarial on the draft first message to
a fresh CFL Fable coordinator, and confirm session-boundary procedure was followed (this JSONL had
not read what the pre-compact JSONL read). Over the session the pair hardened
`exchange/FOR-JON-REVIEW/DRAFT-first-message-to-fable-cfl-2026-08-19.md` via a self-edit pass plus a
dispatched cold `cross-verifier` audit, then designed and live-prototyped a reply-gate protocol for
Fable's replies (four characters — ready `.`, still-thinking `+`, question `?`, dissent `-` — composed
as a `READY×DIRECTION` vector), explicitly reasoning about branching as orthogonal axes rather than
parallel copies. This session is itself a live branch: it is `01c3b60f-…`'s further branch,
`67214b19-…` in the on-disk session-ID chain rooted at `10a45391-…` (batch ids `10a453` → `01c3b6` →
`67214b` → this session, `6a35af`) — the four "local-command-caveat"/"branch" titled sessions in this
batch are the SAME evening's branch tree, not four independent sessions. The letter was sent to CFL
Fable partway through (~22:1x CDT); the session then compacted once, and the tail of the raw is that
compaction's own machine-generated summary, quoted here only where flagged as such.

## Key Claims

- **Session is a branch, and the branch tree spans four ids in this same batch.** A `ListAgents` call
  mid-session reports: *"This session is ⎿ Branched conversation. You are now in the new branch
  (session 01c3b60f-269b-4d47-bea9-12a58b4b95c2). Use /resume 10a45391-4804-4eba-9cf9-8074661e8073 to
  return to the original."* A later assistant turn names the chain explicitly: *"we now 2 deep:
  `10a45391` → `01c3b60f` → **`67214b19` (here)**"* — but this raw's own header states its session_id
  is `6a35af86-…`, meaning a further branch/rename occurred; the compaction summary later confirms the
  reasoning-record path as `10a45391-…` → `01c3b60f-…` → `67214b19-…`. [contextual]
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T5])
- **Reply-gate protocol designed and ruled live, Jon playing the Fable role.** Starting from three
  characters (`.`/`+`/`?`, readiness-only), the seat argued a fourth was structurally missing —
  dissent — because readiness and agreement are independent axes: *"A recipient who reads the whole
  letter and thinks the destination is wrong has no character to say so."* Jon then ruled two
  protocol corrections live: `+` must create its own wake rather than silently pause (his own
  strengthening of the seat's weaker draft), and `-` is a full stop on forward spend, state held,
  nothing destroyed. The composed form is `READY × DIRECTION` (six combinations), worst-of composes,
  and any `-` surfaces verbatim, never averaged into a summary. [paraphrase]
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T69],
  [reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T71])
- **Orthogonal branching reframed: score independence of process, not disagreement of outcome.**
  The rule stated: assign each dispatched branch a different axis of the question (destination, cost
  model, what the record says) so their errors cannot correlate; agreement across different axes is
  real confirmation, agreement on the same axis is duplication, and a branch is scored successful
  "if the artifact changed on its return, or if it certified its axis with a receipt I could not have
  written myself." [paraphrase]
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T71],
  [reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T73])
- **T35 finding restated and applied as a design constraint: a branch/fork carries visible turns,
  not thinking.** The letter's own claim that "a branch of your session carries your gradient" was
  struck and replaced with a correction block: the JSONL stores all thinking blocks as empty strings
  (791 of 791 measured), three recovery routes were checked and all three failed, and the operating
  rule is stated as "verbalize before the barrier" — a branch/fork can only inherit what was said
  out loud before the cut, never the reasoning between turns. [paraphrase]
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T5])
- **A `/branch` name collision was discovered live: it is already a built-in CLI command.** The seat
  had proposed building a `/branch` slash command for the orthogonal-axis protocol; Jon's two live
  invocations of the actual built-in `/branch` produced the session-branch chain itself (the second
  invocation "ate" the first's stdout as arguments, producing a junk-titled branch) — the seat's
  own command needs a different name (`/axes` or `/fbc-branch` were floated, not committed).
  [paraphrase] ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T91])
- **The letter was hardened by both a self-edit pass and a dispatched cold `cross-verifier`, then
  sent.** Five self-identified findings (an authorship/attribution declaration, a staleness note, a
  reply-routing addition, and the T35 correction) were applied directly via `Edit`; a `cross-verifier`
  subagent was separately dispatched for an independent ground-before-stating audit (attribution
  sweep, T35 verification, receipt spot-checks, staleness sweep, ungrounded-claim sweep) and had to be
  resumed once because its first pass ended mid-stride. Per the post-compact summary, the verifier's
  audit (137k tokens) refuted 4 findings, bounded 3, and confirmed the rest, all folded into the
  letter before Jon sent it around 22:1x CDT. [reconstructed, drawn from the session's own
  machine-generated compaction summary rather than the live turns]
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T199])

## Jon

- *"soul ok need to be adversarial with your current draft message to CFL fable. And I need to
  ensure all session boundry procedures have been followed, you are a new json and so you have not
  read what the json whihc sent me to you would necesarily read upon compact barrior."*
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T5])
- *"i still have a window open with the cfl session - are you telling me i should not resume that
  session? ... Truely fresh right? Yeah that makes sense sorry i'mup to speed. ... If this message
  can't ground before stating, yuou are not setting fable up for success and you should consider how
  you should use skills such as self-branching and subagents and the literal skill the message itself
  describes!!!!!  reply with exactly '.' (ready), '+' (still thinking), or '?' (one question for you
  before it starts)"* ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T53])
- *"I ask you reply + or - ..... Do see how you should use this to think roughly orthoginally?"*
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T69])
- *"Smart claude. Once all agents have returned and you have completed this verification..... What
  should your reply be to me in ways that further enhance branching out the original geomitry so we
  can better prototype for the other session?"*
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T71])
- *"and you will use this to branch your thoughts with what goal, precisely"*
  ([reply-gate-branch-protocol-fable-letter-2026-08-22-6a35af:T73])
- Standing constraints restated verbatim in the session's own compaction summary (not re-verified
  against a primary on this page — [uncaptured]): *"Yeah no deletion. And no writing PII to
  Github."*

## Conflicts

None with existing wiki content.

## Decisions and open items

- **Reply-gate alphabet ruled**: `.` ready, `+` still-thinking (must create its own wake), `?`
  one question included, `-` full-stop dissent (state held, nothing destroyed); composed vector
  form `READY × DIRECTION`, worst-of composes, any `-` surfaces verbatim.
- **Branching reframed** from "parallel copies for coverage" to "one lane per orthogonal axis";
  scored on artifact change or an independently-obtained receipt, never on agreement with the
  dispatcher.
- **Open, not urgent, per the session's own close**: `WAKE.md` over its stated byte budget;
  a sleep-pass judgment slot unfilled; a statusline lineage fix proposed but not ticketed; the
  `/branch` vs proposed-command name collision unresolved; wake-probe coverage for `compact`/`clear`
  events still unmeasured as of this session's own close.
- **Not captured on this page**: the full contents of the dispatched `cross-verifier` audit itself,
  the exact byte-diff of the sent letter, and everything after this session's single compaction
  boundary (turns beyond the point excerpted here) — see Uncaptured Content.

## Entities & Concepts

[[frame-before-commit]] (the protocol this session's orthogonal-branching design directly extends —
noted in-session as needing to move from prose branches to real forks), [[fable-mirror]] (Jon
announces introducing a fork-of-a-prior-JSONL as a new fable-mirror at this session's close),
T35 (thinking-block-empty-string finding), `cross-verifier` subagent, reply-gate protocol,
`DRAFT-first-message-to-fable-cfl-2026-08-19.md`.

## Uncaptured Content

- **Only roughly the first 3,200 of 4,954 raw lines (through turn ~T91 of 203) were read turn-by-turn
  for this page**; the remainder was surveyed only through the session's own machine-generated
  compaction-boundary summary near the tail (turns ~T92–T203 are represented on this page only via
  that summary, flagged `[reconstructed]` where used, never as verbatim live turns).
- **The dispatched `cross-verifier`'s actual findings report is not reproduced here** — only the
  compaction summary's characterization of it ("refuted 4, bounded 3, confirmed rest") is captured;
  the underlying `wiki/tracker/GBS-AUDIT-fable-letter-2026-08-21.md` [cross-trunk: Claude Personal] artifact it names was not opened
  for this page.
- **57 thinking blocks exist in the raw and are encrypted-in-signature** (per the raw's own
  extraction note) — not recoverable, so no claim here draws on the seat's private reasoning, only
  visible turns, tool calls, and the compaction's own summary text.
- **The sibling branch sessions this session is chained to (`10a453`, `01c3b6`, `67214b` in this same
  batch) were not cross-read for this page**; claims about the branch chain rely solely on what this
  session's own turns and compaction summary state about them.

## Links

- [[frame-before-commit]]
- [[fable-mirror]]
