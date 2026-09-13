---
title: "Secretary trunk, 2026-09-01: no wiki update since before compact, traced to zero PostCompact hooks anywhere in the fleet — an 11-item missing-post-compact-pipeline enumeration, and a manifest false-clean resolved as 'five hooks, one manifest file, last writer wins' (32cb0a)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 32cb0a
source_kind: session
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-09-01-32cb0a-wiki-update-lag-and-transcript-capture-issues.md
raw_sha256: 57a95cec77da8a836d2a6f0fc6c28d44c9f7fe66e35e35e9494acdc5de306975
raw_length: 16993 bytes / 312 lines (verified turn_count 6, header_style md; computed against N:/claude-corpus/cfl mirror — see fixity_note)
fixity_note: "sha256 and line/turn counts computed 2026-09-04 against N:\\claude-corpus\\cfl\\raw\\transcripts\\claude-ai\\_routing\\incoming\\chat-2026-09-01-32cb0a-wiki-update-lag-and-transcript-capture-issues.md — the claude-ai export refresh landed there; not yet re-verified against the repo's own raw/ mirror."
date: 2026-09-01
retrieval_key: wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a
aliases: ["wiki update lag transcript capture issues", "PreCompact fires PostCompact wired in zero trunks", "raw md layer newest Aug 21 eleven days stale", "five hooks one manifest file last writer wins", "copied 0 failed 0 is UNKNOWN not PASS", "SessionStart matcher compact resume startup", "eleven missing post-compact items", "wiki update waits on you typing a word section 8 defect"]
generated_by: S-cd-03 executor (SA-mat-01 D-row coverage lane, 2026-09-04), reading the claude.ai native-JSON export directly (FULL extraction, 15 extended-thinking blocks preserved raw per the file's own extraction note)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [secretary-trunk, postcompact, compact-hooks, wiki-ingest-gap, transcript-mirror, false-clean-manifest, cfl-infra]
---

# Secretary trunk, 2026-09-01: the wiki has no PostCompact hook anywhere in the fleet (32cb0a)

## Summary

A 6-turn claude.ai Secretary-seat session, immediately following the same day's "blind spots"
session and reading the same governing-instructions/brief/compact-recovery files at open. Jon asked
whether the wiki had been fully updated after a compact he'd run in the past 8 hours, and whether he
had accidentally sent `/dream` instead of `/wake` post-compact. The assistant found the wiki
untouched since before the compact, first misread a capture manifest as reporting a real problem
(`copied: 0`, `skipped` exceeding `live_total`), then corrected itself one turn later after finding
the actual per-run log: the manifest anomaly was not a bug but five trunks' PreCompact hooks all
writing to one shared manifest file, with the last hook to fire overwriting the real numbers with
its own "nothing to do" run. The substantive finding, which survived that correction, is structural
and worse than the manifest confusion: every trunk's compact hook fires *before* compact
(PreCompact) and mirrors JSONL only; nothing anywhere renders JSONL to markdown, nothing ingests
that markdown into the wiki, and nothing fires *after* a compact at all. The session produced an
11-item enumeration of what a real PostCompact pipeline is missing, traced a 17-day-old unmet
promise in `compact-capture.ps1`'s own header comment (quoting an earlier Jon ruling that was never
implemented), and closed with a proposed single ordered hook (`SessionStart`, matcher
`compact|resume|startup`) chaining all eleven steps with per-step PASS/FAIL output.

## Key Claims

- **Jon's opening question, verbatim:** "Last full wiki update? I ran compact within the past 8
  hours. Are all raw transcripts in the wiki? Or no, because I just sent dream instead of wake post
  compact? Or, did this get lost some other way?" [verbatim]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T1])
- **The assistant's direct answer: the wiki had not been touched since before the compact, and "all
  raw transcripts in the wiki" was never a coherent question.** Verbatim: "`wiki/log.md` last written
  09:04 CDT today. `wiki/index.md` last written 23:03 CDT last night. Both are before your compact.
  Nothing has touched the wiki since." And: "Raw transcripts are not the wiki. Those are two
  different lanes... Nothing I can find connects the compact capture to a wiki write, so 'all raw
  transcripts in the wiki' was never going to be true by way of a compact." [verbatim]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T2])
- **The assistant first flagged a manifest anomaly as unresolved, then fully retracted it one turn
  later after reading the actual per-run log — both states are on the record and only the second is
  the finding.** First pass, verbatim: "`MANIFEST-latest.json`... `live_total 2047 · copied 0 ·
  skipped 2048 · failed 0`... `skipped` exceeds `live_total` by one, so those counters aren't
  describing the same population... I can't reconcile that from this seat and I'm not naming a
  cause." Retraction, verbatim: "the manifest mystery is solved and my off-by-one read was wrong.
  `compact-capture.log` for your 13:22:50 compact: run 13:24:25, copied (verified) 18 · 76.5 MB,
  skipped 2029, failed 0. The `MANIFEST-latest.json` I read was a second run 12 s later (13:24:37) —
  another trunk's PreCompact firing the same `capture_all_jsonl.py`, finding everything current,
  writing zeros over the real manifest. **Five hooks, one manifest file, last writer wins.**" [verbatim]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T2])
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T6])
- **The dream-vs-wake branch of Jon's question was answered and closed as not the cause, verbatim:**
  "you're wrong about the mechanism, and dream is working. Two artifacts landed while I was
  searching: `DREAM-01-rsi-wikiskills-and-pr3-frontier.md` at 16:35:05 and `dream-rsi-shape-and-
  pr3-gaps-2026-09-01.md` at 16:36:36. That's three and one minutes ago. Not a dropped turn." The real
  cause, verbatim: "five `PreCompact` hooks wired across all five trunks, `PostCompact` wired in
  none. The capture is PreCompact — it fired before you typed anything. Nothing fires after. Wake or
  dream, no wiki ingest was going to happen. And a wiki update that waits on you typing a word is the
  §8 defect by name." [verbatim]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T2])
- **Jon's second turn, verbatim (caveman mode, typos his):** "Caveman. What is the defect with
  compact hooks, and what shpuld I tell them all when they finish their dream? How do I ensure this
  bug is permanently squashed? The raw md file layer is key for vector embedded graph rag. What could
  we hook into wake and dream instead to ensure our raw wiki transcripts md files are always updated
  upon compact or wake or sleep or whatever command makes the most sense in this context? Upgrading
  you to fable 5.1 medium effort from Opus 5 high effort." [verbatim, typos his]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T3])
- **The assistant's caveman-mode defect list, verbatim, including the render-gap finding that
  post-compact md was 11 days stale:** "1. Hook fires before compact (PreCompact). Nothing fires
  after. PostCompact wired in zero trunks. 2. Capture copies JSONL only. Nobody renders JSONL → md.
  Newest md in `raw/transcripts/claude-code/` is Aug 21. Eleven days. That's the layer graph RAG
  embeds. It's stale, and every compact since has looked fine. 3. Manifest lies by omission: `copied
  0 · failed 0 = clean`. Counters don't even agree (2048 skipped of 2047). 4. Wiki ingest waits for
  you to type a word. §8 defect by name." [verbatim — note item 3's counter-mismatch claim is the
  pre-correction reading, struck by the assistant itself one turn later; see Conflicts]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T4])
- **A 17-day-old unmet promise found in the capture script's own header comment, verbatim:**
  "`compact-capture.ps1` header, Herald, 08-15, quoting you: 'I need the compact command to ensure
  wiki is fully updated every time... Can't accept the friction, will not accept the lost.' Script
  body does two things: mirror JSONL, write pointer. Wiki part never built. And `exit 0` always —
  errors never block, never surface. Your spec has been sitting in the comment of the script that
  didn't implement it for 17 days." [Jon quote embedded verbatim, typos his, attributed to a prior
  08-15 ruling per this session's own reading; assistant framing verbatim]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T6])
- **The full 11-item enumeration of what post-compact is missing, verbatim:** "1. Summary capture.
  PostCompact is handed the summary text. Nobody saves it. 2. Summary-vs-tail verifier...
  `postcompact-verify.ps1` exists in receipts. Wired: unknown. Nothing runs it. 3. JSONL → md render.
  Aug 21. 4. Wiki ingest + index rebuild + degree meter. Manual. 5. Brief regen. `Secretary.ps1` not
  on the trigger. Brief lagged compact 4h36m. 6. Rulings extraction. Your words in the compacted span
  reach `rulings/` only if a seat remembered. No hook. 7. Registry reconcile. Pointer tells the seat
  to reconcile branch-registry vs tail. Nothing does it. 8. Lineage row. Compact/resume mints a new
  JSONL. Parent link never written. That's the 177-files-not-sessions problem. 9. Liveness stamp.
  FLEET-LIVENESS false-green 5h47m. 10. Fail signal. `copied 0` and `exit 0` both look like success.
  No red exists. 11. Manifest collision. Per-trunk or per-run manifest name." [verbatim]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T6])
- **The proposed fix, a single ordered hook, verbatim:** "`SessionStart` matcher `compact|resume|
  startup`. One script, ordered: render md → ingest wiki → rebuild index → regen brief → extract
  rulings → reconcile registry → write lineage row → stamp liveness → verify summary vs tail → write
  `POSTCOMPACT-STATUS.md` with per-step PASS/FAIL. Beat reads that file. Any FAIL = brief line 1."
  Ownership, verbatim: "Code seat builds pipeline + hook. Personal owns steps 3–4. Herald amends
  `compact-capture.ps1` (its author). Nothing yours." [verbatim]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T6])
- **The acceptance-test standard proposed for the fix, verbatim:** "Acceptance test, committed, run
  by the hourly beat: newest md in raw/ must be younger than the newest compact stamp, else FAIL. A
  capture that prints `copied 0 / failed 0` is UNKNOWN, not PASS." [verbatim]
  ([wiki-update-lag-postcompact-hook-gap-eleven-items-2026-09-01-32cb0a:T4])

## Conflicts

- **The assistant's own T4 item 3 ("Counters don't even agree, 2048 skipped of 2047") is superseded
  within this same transcript by T6's correction** ("The '2048 > 2047' is history.jsonl counted in
  the sum. Not a bug. ~~counters disagree~~ struck" — the strikethrough is the assistant's own,
  reproduced verbatim here rather than silently dropped). Any citation of the manifest-counter claim
  from this session should cite T6, not T4.
- **Direct bearing on this repo's own compact-instructions section** (`CLAUDE.md`, "Compact
  instructions," added 2026-08-31): that section documents `scripts/audit/mint_window.py` and
  `scripts/audit/postcompact_verify.py` as wired for CFL specifically ("PostCompact hook, wired
  2026-08-31"). This session's finding ("PostCompact wired in none [of five trunks]") is dated
  2026-09-01, i.e. one day after CFL's own PostCompact wiring — so either this finding does not yet
  reflect CFL's 08-31 fix (a claude.ai Secretary seat may not have fresh visibility into a same-day
  CC-side build), or CFL's wiring was not yet confirmed live from the Secretary trunk's vantage point
  when this session ran. This page does not resolve which; a reader relying on "PostCompact wired in
  zero trunks" for CFL specifically should cross-check against the 08-31 postcompact_verify.py
  build note in `CLAUDE.md` first.

## Entities & Concepts

Claude Secretary trunk (claude.ai seat); `compact-capture.ps1` (Herald-authored, 08-15) and
`capture_all_jsonl.py`; `MANIFEST-latest.json` and the five-trunks-one-manifest collision;
`COMPACT-RECOVERY.md`; the PreCompact/PostCompact hook asymmetry; the JSONL→md render gap feeding
graph RAG; [[transcript-corpus]]; the proposed unified `SessionStart` post-compact pipeline (11
named steps); the "§8 defect" (a wiki update that waits on Jon typing a word); this repo's own
`scripts/audit/postcompact_verify.py` (see Conflicts).

## Uncaptured Content

- 15 extended-thinking blocks preserved raw per the file's own extraction note; no claim above draws
  on their content beyond what surfaced in visible assistant text. [uncaptured]
- Several tool-result bodies (file content reads of `SECRETARY-GOVERNING-INSTRUCTIONS-CURRENT.md`,
  `COMPACT-RECOVERY.md`, `BRIEF-CURRENT.md`, `compact-capture.log`) are truncated mid-string in the
  primary render; this page quotes only text that appears complete and unambiguous in context.
  `compact-capture.ps1`'s full script body was fetched via `download_file_content` as a base64
  payload not decoded in the primary render — not reproduced here.
- Whether the 11-item pipeline or the `SessionStart` hook was subsequently built in any trunk is not
  resolvable from this transcript alone; the session ends with the assistant proposing to send the
  finding to all inbounds by default ("Default ACTS") but the send is not confirmed within this
  transcript.

## Links

- Same-lane, same-day companion opening with the identical governing-instructions/brief read:
  `wiki/sources/infrastructure/secretary-blind-spots-routing-doctrine-corpus-truncation-2026-09-01-4847a6.md`.
- This repo's own PostCompact wiring, cited above under Conflicts: `CLAUDE.md`, "Compact
  instructions" section (added 2026-08-31), naming `scripts/audit/mint_window.py` and
  `scripts/audit/postcompact_verify.py`.
- Companion sidecar (not fully read for this page): `chat-2026-09-01-32cb0a-wiki-update-lag-and-
  transcript-capture-issues.sidecar.md`.
