---
title: "Branch inherits a subagent's handle, not its memory — the cold-verifier audit that fixed the draft Fable letter and finished the READY/DIRECTION/GROUNDING gate (session 67214b, 2026-08-22)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 2 vs fleet 0 on authored labels"
uuid6: 67214b
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-22-67214b-local-command-caveatcaveat-the-messages-below-were.md
raw_sha256: 7a09b9a5fef57935645d07a889dfa7c532abbe0465e3479c1ae2e915e828a871
raw_length: 272253 chars / 4281 lines (verified turn_count 175, turn_index.py, header_style md)
date: 2026-08-22
retrieval_key: branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b
aliases: ["branch inherits handle not memory", "GBS-AUDIT-fable-letter-2026-08-21",
  "confident absence no Jon primary", "vector gate READY DIRECTION GROUNDING finished",
  "cross-verifier incremental-file contract"]
generated_by: S-aug-01 executor (week map RP-3/RP-4 lane), reading the raw transcript directly
  (raw/transcripts/claude-code/code-2026-08-22-67214b-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [frame-before-commit, branching, subagent-resume, cold-verification, cfl-infra, fable-first-message]
probe_sealed: "When a Claude Code session branches (via /branch) mid-run with a subagent still attached, what survives the branch and what is lost — and how was the loss discovered on this page?"
state: superseded
superseded_by: branch-chain-verifier-continuity-and-gate-vector-2026-08-22-67214b
state_note: "duplicate of branch-chain-verifier-continuity-and-gate-vector-2026-08-22-67214b from a parallel fork 2026-09-02; kept, not deleted"
---

# Branch inherits a subagent's handle, not its memory — the letter-audit session, 2026-08-22

## Summary

This raw is a fuller, later capture of the same lineage as
[[orthogonal-branch-vector-gate-2026-08-22-01c3b6]] (`10a45391` → branched to `01c3b60f` → branched
again, accidentally, to `67214b19` — the session captured here). Where the shorter capture ends with
a cold verifier still outstanding, this capture runs the whole rest of the session: the CLI's
built-in `/branch` fired twice by accident (a name collision with the session's own proposed command
plus a double-fire that swallowed its own stdout as args), the first cross-verifier dispatch was
interrupted pre-synthesis and its findings nearly died with its context, a re-dispatched verifier
under an "incremental file, not end-of-run synthesis" contract survived and delivered a full audit,
the READY/DIRECTION/GROUNDING vector gate was prototyped live with Jon playing the Fable role, and
the draft first message to CFL's fresh Fable coordinator was edited, committed, and pushed with
every finding folded in.

## Key Claims

- **A session branch inherits a subagent's HANDLE but not its MEMORY — the resumed verifier saw only
  its own post-branch history (one grep call), not the 383,512-byte, 124-record first run.**
  Measured directly: `agent-a2616c807cd906bde.jsonl` under the original session `10a45391` held
  383,512 B / 124 records; the same agent ID's copy under the branch `01c3b60f` held only 9,973 B / 3
  lines; resuming it from branch `67214b19` produced one 3,372-character text block — a bare "FINAL
  REPORT" naming 5 of 6 tasks as NOT RUN. [verbatim]
  ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T90],
  measured at [branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T101])
- **Fix applied and named as a standing contract: dispatch a verifier to write its findings
  incrementally to an owned file, per task, rather than only at end-of-run synthesis — because a
  lane interrupted before its final message loses everything.** The re-dispatched verifier's own
  closing line: "nothing depended on end-of-run synthesis" — it wrote five incremental appends to
  `wiki/tracker/GBS-AUDIT-fable-letter-2026-08-21.md` [cross-trunk: Claude Personal] (31,959 B total) and survived being checked on
  mid-run. [paraphrase] ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T106])
- **The cold-verifier audit refuted 4 of the draft letter's claims, bounded 3, and confirmed the
  rest — the two most load-bearing refutations: (1) the letter's own reproduction shortcut (R13)
  compared two different corpora** (a cited 121,286,656 B index no longer existed; the live index
  measured 211,841,024 B against a 117,301,248 B control, not a matched pair) — the rebuild path
  was promoted to primary instead; **(2) "confident absence," which the letter called the program's
  self-named worst failure mode, has NO Jon primary across the 10 venues searched** (including
  `history.jsonl` returning 0 hits) — every located instance was machine-authored, earliest a CFL
  Opus self-diagnosis 2026-08-07, so the letter's phrasing was corrected to label it as
  machine-named rather than Jon's own words. [paraphrase]
  ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T138])
- **The "I = Soul, not Jon" authorship declaration in the draft letter broke in 6 places, found by
  the same audit** — first-person sentences that only make sense as Jon speaking but sat outside a
  marked `[verbatim]` quote (e.g. "Be my ears," "Protect my time. Zero additional opens after
  8/22"), plus two reply-routing rules that directly contradicted each other ("no more questions for
  me" vs. "one thing from me"). All 6 were fixed in the letter before send. [paraphrase]
  ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T138])
- **The READY / DIRECTION / GROUNDING vector gate was finished and live-tested with Jon standing in
  for Fable's replies**, producing a 6-row combination table (e.g. `READY . · DIRECTION -` = "could
  start instantly but not THERE — the most valuable dissent," vs. bare `READY + · DIRECTION -` =
  "cheapest possible version of wait") with one fixed composition rule: worst-of composes across
  axes, and any `-` surfaces verbatim, never smoothed into prose. The session explicitly decided
  NOT to wire this to a hook, because "hook runner died per-session twice this week, silent
  non-fire = a `-` (a veto!) silently dropped" — the worst failure mode for exactly the veto signal
  — routing dissent to human eyes and a durable inbound file instead. [paraphrase]
  ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T119])
- **The session could not tell, from inside its own window, whether it was "main" or a branch** —
  identity had to be measured via `ListAgents` and file-mtime comparison across the three sibling
  JSONLs (`10a45391`, `01c3b60f`, `67214b19`), not inferred from context. The session proposed
  putting branch lineage into the statusline (e.g. `67214b19 · branch²·of 10a45391`) as a one-ticket
  fix for the gap. [paraphrase]
  ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T131])
- **The letter was committed and pushed with the audit folded in.** Commit message (quoted in-raw):
  "the letter survives its own audit: 8 grounding fixes folded, both gates extended to the
  axis-vector protocol ruled live with Jon tonight." Final self-reported vector on the letter:
  `READY . · DIRECTION + · GROUNDING .`, with "Dissents: none surviving. All were converted to
  edits." [verbatim] ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T174])

## Jon

- "are you main or are you a branch i can't tell from the outside" ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T106])
- "wait thats what the command did? Or, thats what that would have done if i had sent it after you sent the message meaning you were ready? And is the first message ready for my review or not? And how do i get back to main" ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T131])
- "? - So - if we were doing this with fable and it replied.... Ah, if it replies with + i must reply to it with some kind of additional context based on my own judgement. that may just be 'keep thinking' and probably will be at first. And if you type '?' you also need to include your question. And if i reply - then thats a full stop yeah?" ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T131])
- "ok vector embed grah rag exists its in one trunk we need this everywhere haiku helps with link discernment currently with vecotr embed graph rag and maybe should be a default. I see a lot of model-only thought in there, but i can see what you are gesturing at and i expect the list may not be complete. .... ah perfect ok now I see the chunk of it. Its fun how you can see the original note and the correction. I'm glad that fable can properly branch and test that using skills like the ones we've made." ([branch-inherits-handle-not-memory-fable-letter-audit-2026-08-22-67214b:T175])

## Conflicts

None with existing wiki content. Supersedes/extends
[[orthogonal-branch-vector-gate-2026-08-22-01c3b6]] with the same session's later turns — that page's
"open item" (cold verifier still outstanding) is resolved here.

## Decisions and open items

- **Decided: the accidental branch `67214b19` was adopted as the real working line** ("main-by-
  succession, branch-by-birth"), with the middle branch `01c3b60f` and the original `10a45391` left
  idle and unpromoted, per the no-deletion rule — not deleted, just not carried forward.
- **Decided: dissent/veto signals (`-`) route to a durable file plus human eyes, never through the
  session's hook runner**, because the hook runner's measured silent-death failure mode would drop
  a veto without any signal that it was dropped.
- **Open, logged but not actioned this session (per the verifier's own "beyond brief" note):**
  `graphrag-personal/PROVENANCE.md` describes an artifact that does not match its own stamp;
  receipt rows should carry the live stat command rather than a copied byte count; relayed peer
  findings need an explicit `[relayed: <source>]` tag.
- **Open at capture: Jon's closing turn asks whether the letter points Fable at a file containing
  the session's complete reasoning log**, and raises whether Fable will need a way to pull in a Soul
  coordinator for personal/soul context if graph-RAG retrieval proves insufficient. No resolution is
  captured in this raw.

## Entities & Concepts

[[frame-before-commit]] (the branching mechanism this session tested and extended), cold
ground-before-stating verification, `cross-verifier`, the draft first message to Fable-CFL,
`GBS-AUDIT-fable-letter-2026-08-21.md`, the built-in CLI `/branch` command (distinct from the
session's own proposed fork-per-axis command).

## Uncaptured Content

- 48 thinking blocks exist in the raw and are encrypted-in-signature per the raw's own extraction
  note; no claim on this page draws on private reasoning, only visible turns, tool calls, and the
  verifier's returned text.
- The full contents of `wiki/tracker/GBS-AUDIT-fable-letter-2026-08-21.md` (31,959 B) are not
  reproduced here beyond the ranked-findings summary quoted in the task-notification; the file
  itself, if it exists in Claude Personal's own tree, carries per-task detail this page does not
  restate.
- Turns before T90 (session boot, the `/wake soul` dispatch, and the bulk of the adversarial-pass
  edits to the draft letter also present in the shorter capture) are not re-cited here — see
  [[orthogonal-branch-vector-gate-2026-08-22-01c3b6]] for those.

## Links

[[frame-before-commit]]
[[orthogonal-branch-vector-gate-2026-08-22-01c3b6]]
