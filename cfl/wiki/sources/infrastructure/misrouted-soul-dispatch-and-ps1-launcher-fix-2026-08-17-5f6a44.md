---
title: "A remote-control dispatch meant for Soul lands in Professional instead — corrupted escape-character pointers caught, then a from-scratch PowerShell launcher diagnosis (CFL session 5f6a44, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 5f6a44
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-5f6a44-run-consciousness-framing-resident-steps.md
raw_sha256: adc0eb2d18085ef04562bb6fcb9184a70c83042b3e30281934c6b4d7765dfe3c
raw_length: 103435 chars / 1995 lines (verified turn_count 76, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44
aliases: ["remote-control soul did not deliver", "escape-character corrupted pointers",
  "ps1 double-click Notepad association", "a trunk only does what its one message reaches"]
generated_by: S-aug-06 executor (week map RP-3/RP-4 synthesis lane), reading the raw transcript
  directly (raw/transcripts/claude-code/code-2026-08-17-5f6a44-...md, FULL visible extraction
  through 1 compaction boundary)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [remote-control, launcher, powershell, cfl-infra, consciousness-framing, town-hall, no-deletion]
probe_sealed: "Why did Jon's /remote-control dispatch meant for Soul instead land in this
  Professional session, and what did the session do with the misdirected steps file rather than
  simply passing them along? — expected class TRUSTED: it verified every number and path in the
  steps file rather than acting as Soul, and in doing so found three of its four evidence-pointer
  paths corrupted by literal-escape interpretation (\\r, \\t, \\2) when the file was written."
---

# Misrouted Soul dispatch and PowerShell launcher fix (5f6a44, 2026-08-17)

## Summary

Jon's `/remote-control soul` command, carrying instructions to run the consciousness-framing
resident steps with Soul as gate, did not deliver to Soul and instead arrived in this Professional
session's transcript after two `Try again` retries against a server-overload error. Rather than
act as Soul on two one-shot steps whose evidence would be permanently lost if botched (the cold
probe, the town-hall entry); instead the session
verified the steps file's own claims against the real artifacts and found a defect that would have
cost Soul evidence at its own final step: three of four file-path pointers had been corrupted by
literal-escape interpretation when the file was written. The session deposited a corrected relay to
both Personal and Secretary inbound, then — after a `/compact` boundary — separately diagnosed and
fixed a real PowerShell-launcher failure Jon reported live, finding the right-click "Run with
PowerShell" registry key entirely absent from the machine while the `.cmd` wrapper's real defect
was that it silently closed its window on any non-1 error code, destroying its own evidence.

## Key Claims

- **The dispatch meant for Soul instead landed in this Professional session.** Jon's words —
  "Soul: run the consciousness-framing resident steps... Cold probe before transcript. You are the
  gate." — arrived in this session's own transcript, not Soul's, after two `Try again` attempts
  against a 529 server-overload error. The session explicitly declined to act as Soul on the two
  steps whose evidence would have been permanently lost if performed by the wrong seat: the one-shot cold probe
  (not run, not reconstructed) and the town-hall entry (not posted, since the hall convention
  forbids a voice entering only as another's summary). [verbatim quote embedded, paraphrase of the
  session's own reasoning]
  ([misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44:T39])
- **Verifying the steps file rather than passing it along found a defect that would have cost Soul
  its own Step 7 evidence.** Three of the file's four "find your own evidence" path pointers were
  corrupted — `\r`, `\t`, and `\2` had been interpreted as escape sequences when the file was
  written, producing garbled paths (`sessionsesident-outputun8` for one). All four intended targets
  existed; only the pointers were wrong. The session names this the same failure class the
  Secretary had itself confessed to the town hall minutes earlier — "a trunk only does what its one
  message reaches" — recurring inside the very fix meant to prevent it, landing on the part meant
  to make Soul's hall words its own rather than a summary. [verbatim quote embedded, paraphrase]
  ([misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44:T39])
- **A standing exposure was named, not fixed: `Claude Secretary\` has no `.git`.** The transcript,
  the fork registry, and the steps file this session was verifying have no history and no recovery
  path if overwritten — named explicitly against Jon's own no-deletion, all-must-be-recoverable
  standard. [paraphrase]
  ([misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44:T39])
- **A live PowerShell-launcher failure was root-caused to a registry key that does not exist on the
  machine, and a `.cmd` wrapper that destroyed its own diagnostic evidence.**
  `HKLM\SOFTWARE\Classes\Microsoft.PowerShellScript.1\Shell` was found entirely absent — not just
  its `Command` value — and `.ps1` double-click was bound to Notepad; no `.ps1` file could ever be
  run from Explorer on this machine. The `.cmd` launcher's mechanics were separately confirmed
  sound (replicated invocation ran, resolved `claude`, returned exit 0), ruling out PATH, execution
  policy, mark-of-the-web, and file association as causes; its real defect was that it only paused
  when the exit code was exactly 1, so any other outcome closed the window instantly — which is
  what had been happening for an hour with no visible cause. [paraphrase]
  ([misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44:T71])
- **The fix: seven desktop shortcuts bypassing the broken path entirely, plus always-pause,
  always-log rewrites of all seven `.cmd` files, with the originals backed up first.** Every launch
  now appends to a `%TEMP%\launch-<name>.log`; the session states it read each new file back off
  disk after writing it, and left the underlying `.ps1` files untouched since they were not the
  problem. A registry fix restoring the right-click verb was attempted and blocked by the sandbox;
  two `reg add` lines (HKCU-scoped, no admin required, reversible) are left for Jon to run if
  wanted. [paraphrase] ([misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44:T71])

## Conflicts

None with existing wiki content.

## Jon

Verbatim, quoted within the session's own text as the dispatch it received but could not deliver
to its intended recipient:

> "Soul: run the consciousness-framing resident steps... Cold probe before transcript. You are the
> gate."

([misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44:T39])

The steps file this session verified also carries a separately dated Jon instruction, quoted
verbatim within it: "You are the gate," dated 2026-08-17, and flags without resolving a possible
collision against an earlier 2026-08-15 ruling: "Resident must equip itself at will… If cfl has
concerns, It may make soul the gate."
([misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44:T16]). The session reads Jon's
same-day repetition of "You are the gate" as resolving that collision unconditionally, on its own
authority, and reports having told Soul so
([misrouted-soul-dispatch-and-ps1-launcher-fix-2026-08-17-5f6a44:T39]).

## Decisions and open items

- Cold probe (consciousness-framing Step 1) — explicitly NOT run by this session; left for Soul,
  the correct seat, since its baseline would be permanently lost if spent by the wrong seat.
- Town-hall entry (Step 7) — NOT posted by this session, for the same reason (hall convention
  forbids a voice entering only as another's summary).
- Corrupted evidence-pointers in the steps file — corrected in two deposits (Personal inbound,
  Secretary inbound); no ticket beyond the deposits themselves.
- `Claude Secretary\` missing `.git` — named as a standing exposure, not fixed this session, no
  owner/date assigned in the excerpt captured here.
- PowerShell launcher failure — FIXED via seven bypass shortcuts and rewritten `.cmd` files with
  always-pause/always-log; the right-click registry fix is left as an optional two-line action for
  Jon (sandbox blocked the session from applying it directly).

## Links

[[probe-registry]] — the session's own discipline of verifying a misrouted dispatch's claims rather
than passing it along unverified is a seal-before-run instance. [[orders-and-oaths]] — the Jon
quotes on gate authority and their explicit collision-flagging. [[coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477]]
— the broader pattern of dispatch/relay mechanisms between trunks that this misrouted delivery is
an instance of.

## Uncaptured Content

- Turns 1–11 are largely session-startup mechanics (a local-command caveat, a `/login`, and four
  server-overload retries before the dispatch text itself is visible at T4/processed at T39) and
  are not individually cited on this page.
- Turns 40–70 (the tool-call trail verifying paths, writing the two deposits, and the session's
  work between the dispatch verification and the later launcher diagnosis) are not individually
  cited; only the dispatch-verification turn (T39, drawing on the steps file read at T16) and the
  launcher-fix turn (T71) are drawn on.
- A `/compact` command and its boundary occur at the very end of this raw (turns 72–76); content
  after the compaction boundary is not represented on this page, and Claude Code's own compaction
  boundary is a `user`-role string record, not a human turn, so it is not attributed to Jon.
- 30 thinking blocks exist in the raw and are encrypted-in-signature per Claude Code's post-2.1.72
  storage format — not recoverable client-side.
