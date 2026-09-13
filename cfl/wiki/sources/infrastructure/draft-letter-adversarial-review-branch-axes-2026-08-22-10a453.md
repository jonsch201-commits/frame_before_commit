---
title: "Adversarial review of the draft first message to Fable-CFL, plus the axis-vector design for self-branching (Personal Soul seat, 2026-08-22, 10a453)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 10a453
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-22-10a453-cfl-session-review-and-reset.md
raw_sha256: 7b4d9b7057326e23f0350b308fc85bd434003b5fb0b19ce1a25c2cd113fa0036
raw_length: 205336 chars / 3046 lines (verified turn_count 80, turn_index.py, header_style md)
date: 2026-08-22
retrieval_key: draft-letter-adversarial-review-branch-axes-2026-08-22-10a453
aliases: ["adversarial review draft first message to fable 2026-08-22", "branch-axis vector design",
  "READY DIRECTION GROUNDING vector", "T35 thinking-blocks-empty-string finding", "/branch command design"]
generated_by: S-aug-01 executor (week map RP-3/RP-4 lane), reading the raw session extract directly
  (raw/transcripts/claude-code/code-2026-08-22-10a453-...md, live human/assistant turns only, no
  thinking blocks recoverable)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [frame-before-commit, branch-session, probe-registry, adversarial-review, cfl-infra, fable-launch]
probe_sealed: "What four-character gate vocabulary did this session propose replacing the three-character '.'/'+'/'?' ready-gate with, and why was a fourth character needed? Expected: TRUSTED — the page states it directly (READY/DIRECTION/GROUNDING vector, plus the earlier three-character-to-four-character '-' dissent addition)."
supersedes: [cfl-session-review-and-reset-2026-08-22-10a453]
---

# Adversarial review of the draft first message to Fable-CFL, plus the axis-vector design for self-branching

## Summary

A Personal-trunk Soul seat (session `10a453`, woken fresh after a compact) was directed by Jon to
be adversarial toward its own in-progress draft of the first message to a fresh CFL Fable
coordinator, and to confirm session-boundary procedure had been followed after the compact. The
session ran a self-adversarial edit pass on `DRAFT-first-message-to-fable-cfl-2026-08-19.md`
(authorship disclosure, a correction about thinking-block recoverability, a reset-timing update),
dispatched a cold ground-before-stating verifier at the letter itself, and — while the verifier ran
— worked out with Jon, turn by turn, a design for self-branching as an axis-vector rather than a
single readiness scalar: a `.`/`+`/`?` gate is readiness-only and cannot express dissent, so a
fourth character (`-`, "I dissent from the destination") was added, and the eventual reply-to-Jon
shape was redesigned as three independent axes — READY, DIRECTION, GROUNDING — each owned by a
different dispatched lane so that agreement across axes is real confirmation and agreement within
one axis is not. The session closed mid-design, discussing whether a `/branch` slash command
(Personal-owned, not CFL-owned) should formalize the pattern, with the cold verifier still
outstanding.

## Key Claims

- **The draft letter was edited three times in this session for honesty/correctness, not content
  additions.** Edits added: an authorship-disclosure block ("I" in the letter is Soul except inside
  `[verbatim]` quotes, sent by Jon's hand); a note that the reset condition for sending was now
  satisfied and Jon had directly ordered a truly-fresh CFL window, not a resumed one; and a struck
  claim ("a branch of your session carries your gradient") replaced with a correction citing a
  measured finding (T35, Personal commit `8238f9c`) that 791 of 791 thinking blocks in a measured
  session were stored as empty strings — destroyed at write time, not at compaction — so a branch
  carries visible turns and conclusions only, never the reasoning between them unless it was
  verbalized before the cut. [paraphrase]
  ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T52])
- **Jon ordered truly-fresh over resumed for the CFL window, and the session agreed with a named
  reason.** The draft's own header already ruled it: an 11-day seat "would be planning from its own
  scrollback," which the session called "the exact contamination the test can't survive."
  [paraphrase] ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T52])
- **A three-character readiness gate (`.` ready / `+` still thinking / `?` one question) was found
  to have no way to express disagreement, and a fourth character was proposed to fix it.** All
  three original characters measure only speed toward the same destination; none can signal that a
  reader thinks the destination itself is wrong. The proposed fix: add `-` meaning "I've read it,
  I'm not blocked, and I dissent," with reasons written to a named file rather than folded into
  prose. [paraphrase] ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T69])
- **The eventual reply-to-Jon was redesigned as a three-axis vector, not a scalar: READY /
  DIRECTION / GROUNDING**, each answered by a different independently-dispatched lane (readiness is
  the session's own; direction is the adversarial pass; grounding is the cold verifier, "and only
  it may answer it, because it read what I didn't write"), composed with an explicit rule: worst-of
  on grounding, and any `-` on any axis surfaces verbatim rather than being averaged into a summary.
  [paraphrase] ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T71])
- **Two working self-branching mechanisms were inventoried, and neither is a hook.** (1) `Agent`
  tool with `subagent_type: fork` — ready now, no skill or hook needed, but bound by the T35 finding
  (fork carries visible turns only, thinking blocks are empty strings); a prior seat had mentioned
  forking 11 times and invoked it 0 times. (2) `scripts/branch_session.py` — built and tested
  2026-08-19, negative control and cross-trunk both passed, but wired only as step 3c of the
  `/su-compact` ritual, no standalone skill, and no hook (the hook runner was measured dead this
  session, "silent non-fire"). [paraphrase]
  ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T78])
- **A new `/branch` slash command was proposed, scoped deliberately to Personal, not CFL.** Reason
  given: CFL-owned skill files sync-overwrite, so a Personal-owned command
  (`.claude/commands/branch.md`, in that repo) survives; the shape sketched: read Jon's words for
  axes, pick 2-4 roughly orthogonal ones, fork per axis, compose the READY/DIRECTION/GROUNDING
  vector plus one receipt file per axis, with the T35 discipline (verbalize before the barrier)
  built in. Any change to the existing `frame-before-commit` skill itself would instead need to go
  through CFL's own proposal channel (`exchange/outbox/`). [paraphrase]
  ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T80])
- **The session closed with the cold ground-before-stating verifier still outstanding** — findings
  were to be folded into the letter and the gate extensions only once it returned; this page does
  not capture that return. [contextual]
  ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T80])

## Jon

- **The wake order that framed the whole session, typos his:** "soul ok need to be adversarial with
  your current draft message to CFL fable. And I need to ensure all session boundry procedures have
  been followed, you are a new json and so you have not read what the json whihc sent me to you
  would necesarily read upon compact barrior."
  ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T4])
- **On resuming vs. fresh, typos his:** "i still have a window open with the cfl session - are you
  telling me i should not resume that session? What would be more wise in your opinion, resuming or
  truely fresh? Truely fresh right? Yeah that makes sense sorry i'mup to speed."
  ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T52])
- **On the branching goal, typos his:** "and you will use this to branch your thoughts with what
  goal, precisely"
  ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T72])
- **On self-branching mechanism status, typos his:** "you self branch yes? Is skill or hook is
  ready?" ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T77])
- **On reflex vs. tool, typos his:** "should be ready as reflect when i envoke the meta skill? What
  is? What good slash command in this context"
  ([draft-letter-adversarial-review-branch-axes-2026-08-22-10a453:T79])

## Conflicts

None with existing wiki content.

## Decisions and open items

- **Decided this session:** truly-fresh CFL window over resumed (Jon's direct order); the draft
  letter's three edits (authorship disclosure, reset-timing update, T35 correction) were applied.
- **Open at session close:** the cold ground-before-stating verifier's result was not yet in; the
  gate-vocabulary extension (three characters to four, then to the axis-vector form) was designed
  but not yet applied to the letter; whether to build `/branch` as a new Personal-owned slash
  command was raised by Jon and not yet answered by the session ("Build `/branch` now... Say
  word.").
- **Named but not resolved on this page:** an "F5 finding from the adversarial pass" is referenced
  as already existing (about branches being scored wrong when they agree) — its origin is earlier
  in this same session (before line 2691) and is not surveyed here; see Uncaptured Content.

## Entities & Concepts

[[frame-before-commit]] (the existing skill this session's axis-vector design proposes upgrading
from prose-branches to real forks), [[probe-registry]] (the same seal-before-run discipline this
session's pre-designed composition rule follows), `branch_session.py`, `DRAFT-first-message-to-
fable-cfl-2026-08-19.md`, T35 (thinking-blocks-empty-string finding).

## Links

[[frame-before-commit]], [[probe-registry]]

## Uncaptured Content

- **Lines 62-2690 of this 3,046-line raw (turns T5-T51) are not individually surveyed on this
  page.** That span holds an earlier adversarial-pass lane (including the "F5" finding referenced
  above) and substantial tool-call/edit activity between the wake order and the T52 "should I
  resume" exchange this page draws its Key Claims from. A full pass covering that span is out of
  scope here.
- **The cold ground-before-stating verifier's actual findings are not in this raw.** The session
  ends with the verifier still running; whatever it found, and how the letter's gates were finally
  worded, is not captured.
- **Thinking blocks are not recoverable for this session** — consistent with the T35 finding this
  session itself cites, no claim on this page draws on private reasoning, only visible turns.
