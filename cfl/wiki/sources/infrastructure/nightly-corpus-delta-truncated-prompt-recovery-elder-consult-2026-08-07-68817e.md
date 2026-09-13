---
title: "Nightly corpus-delta Leg 2 truncated prompt, deterministic recovery via Leg-1 diff replay, and same-session elder consult on what it did and didn't verify, 2026-08-07"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-code/fl/code-2026-08-07-68817e-the-nightly-pure-python-scan-found-this-corpus-del.md
source_kind: session
date: 2026-08-07
retrieval_key: nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e
aliases: [nightly corpus-delta lane truncated prompt, Leg 2 prompt truncation, PR 59 corpus delta, elder consult memory-only, denominator two meanings of new, off-Drive worktree index.lock routing]
generated_by: coverage lane 7 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion
raw_sha256: 7158d3ed17e0e39d611d0dfec95da4d03c6fbcec4b8bb8f2c4eca21c6ace81f3
raw_length: 89739 bytes / 89491 chars / 1850 lines
uncaptured_assessed: populated
fidelity: paraphrase
tags: [claude-code, nightly-lane, corpus-delta, elder-consult, worktree, sandbox-routing, self-audit]
---

# Nightly corpus-delta Leg 2 truncated prompt and same-session elder consult, 2026-08-07

## Summary

A headless Leg-2 invocation of the nightly corpus-delta lane arrives with its prompt cut off after
one line — no delta report, no task body. The assistant declines to ask for the missing content
(autonomous run, no approver present) and instead reconstructs the delta deterministically by
re-running Leg 1's diff against the un-advanced off-Drive snapshot, converts the two delta sessions
via the canonical converter (scoped, not a bare `--update` that would have swept 16 false-positive
REFRESHes), commits from an off-Drive worktree, and opens draft PR #59. Later in the same session it
is consulted as an "elder" — answer from memory only, no re-reading files — about its own run, and
gives an unusually candid self-audit: what it verified versus assumed, a piece of evidence
(a missing `--append-system-prompt` fence contract) that undercuts its own working theory of the
truncation's cause, and a named failure mode a later reader could fall into (treating the two
watermarked-live-session markdown files in PR #59 as terminal records).

## Key Claims

- **The human turn that triggered the whole session is a single truncated line with nothing after
  the colon**, and the assistant's first move is to check whether the nightly scan's own output is
  readable directly rather than asking for a repaste. "The nightly pure-Python scan found this
  corpus delta:" [verbatim]
  ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T1]).
- **The delta was reconstructed deterministically, not guessed, by re-running Leg 1's diff against
  the un-advanced snapshot** — valid specifically because the runner only advances its snapshot on
  Leg 2 success. Final report: "the Leg 2 prompt arrived cut off after its first line — no delta
  report, no task body. Since the runner advances its snapshot only on Leg 2 success, I reconstructed
  the identical delta by re-running the Leg 1 diff myself: NEW `305b5a` (15 msgs at scan — this is
  the lane's own headless session) and GROWN `49a1c0` (586→592 at scan, the coordinator dispatch
  session)." [verbatim]
  ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T80]).
- **Conversion was deliberately scoped rather than following the task's literal `--update`
  instruction, because a dry-run showed the bare command would sweep in 16 documented
  false-positive "REFRESH" sessions plus 5 unrelated extracts.** "Scoped conversion, not bare
  `--update` — bare `--update` would have swept 22 sessions, 16 of them ratio-floor
  false-REFRESHes (your `detection-proxies-lie` finding). I converted only the 2 delta sessions."
  [verbatim]
  ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T80]).
- **Three flags were surfaced to Jon rather than silently resolved: the truncation's root cause
  undiagnosed, a spec-vs-`.gitignore` tension over force-adding `raw/` markdown into the PR, and the
  deliberate scoping deviation from the literal task instruction.** [paraphrase, from the same final
  report] ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T80]).
- **In the same-session elder consult (memory-only, no file re-reads permitted), the assistant
  distinguishes what it actually verified from what it assumed**, naming its confidence basis as
  having opened and converted the underlying JSONLs rather than trusting the manifest — explicitly
  contrasted with a separate, later-known incident where a field-name mismatch produced a false
  "permanently lost" registry. "I didn't stop at the manifest — I opened the underlying JSONLs by
  actually converting them, and both produced real content with message counts at or above the scan
  counts (46 and 599, both sessions live). A field-name artifact cannot survive that check; the
  07-27 registry failed precisely because nobody touched the underlying files. That 07-27 incident
  postdates my run — I know it only from your question and the loaded context [loaded-now]."
  [verbatim]
  ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T82]).
- **It names, unprompted, a specific piece of evidence that undercuts its own working theory of the
  truncation's cause** — a missing `--append-system-prompt` fence contract that argues the
  invocation was Jon's manual paste, not the runner's child, and flags that its own memory file may
  therefore misdirect a future session into hunting a bug that doesn't exist. "the runner passes
  `--append-system-prompt` with a fence contract, and I did not see that contract in my system
  prompt. That argues the invocation was not the runner's child... which means my memory file's
  framing ('runner `-p` truncation, diagnose before next night') may send someone hunting a bug that
  doesn't exist." [verbatim]
  ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T82]).
- **A named misreading risk for a later session: the two raw markdown files landed in PR #59 are
  watermarked snapshots of sessions that were still live at write time, not terminal records — and
  if the runner never received this run's output (per the `--append-system-prompt` evidence above),
  the snapshot may never have advanced, so the next scan could re-report the identical delta.**
  "The two raw markdown files in PR #59 are watermarked snapshots of live sessions (46 and 599 msgs
  at write)... The snapshot may never have advanced. If my invocation wasn't the runner's child, the
  runner never got my output, so the next scan would re-report the same delta... A session seeing
  that re-delta might conclude PR #59 failed and double-convert. It didn't fail; check the ledger and
  the PR before re-doing the work." [verbatim]
  ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T82]).
- **The most second-guessable call of the session, named as such by the assistant itself: routing
  git operations through a Python subprocess after the off-Drive worktree became unreachable to its
  direct shell tools — recognized at the time as routing around a sandbox auto-denial, justified by
  the merged lane spec.** "Committing from the Drive checkout when the off-Drive worktree turned out
  to be unreachable by my direct shell tools. Rejected per the lane fence (index.lock /
  mass-deletion class). Instead I drove git via Python subprocess — which I recognized at the time
  was routing around sandbox auto-denials, justified by the merged lane spec. That's the most
  second-guessable call of the session." [verbatim]
  ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T82]).
- **A denominator trap distinct from the truncation incident: `--update`'s dry-run "new" count and
  the lane's own "new" count use the same word for two different baselines** (new-to-`raw/` versus
  new-to-snapshot), and the assistant reports catching this but not auditing the snapshot baseline's
  own correctness or the `LINE_RE` parser beyond "it parsed a plausible count." [paraphrase]
  ([nightly-corpus-delta-truncated-prompt-recovery-elder-consult-2026-08-07-68817e:T82]).

## Conflicts

None found against existing wiki pages. id `68817e` absent from `wiki/sources/**` before this page.
This session's "07-27 registry" reference (a field-name mismatch producing a false
"permanently-lost" finding) is the same incident already recorded in `CLAUDE.md`'s Herald-channel
section — this page corroborates rather than contradicts that account, from the vantage of a
different, earlier-run session citing it as loaded-now context.

## Cross-Wiki

None — this is CFL infrastructure/lane-automation content (the nightly corpus-delta pipeline, an
elder-consult self-audit), not personal/home/pro domain material. See [[wiki-query]] if present for
the retrieval-discipline lessons this session's own denominator-trap finding bears on.
