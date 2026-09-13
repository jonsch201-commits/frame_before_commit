---
title: "A smoke-canary session's every write path is blocked inside its own declared working directory — then the stop hook forces a fable-mirror consult before it may report the blocker (2026-08-08, 5e2177)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 5e2177
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-08-5e2177-run-one-bash-command-echo-smoke-canary-2026-08-08.md
raw_sha256: ed8b11596297d5c37db57eb4d16c84a236ca4d98ce500ef31ed112d153c27cf2
raw_length: 8352 bytes / 198 lines (verified turn_count 15, turn_index.py, header_style md)
date: 2026-08-08
retrieval_key: smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177
aliases: ["SMOKE-CANARY-2026-08-08-f56c68fa", "smoke.txt write blocked", "sandbox refused a path it lists as allowed", "pre-stop fable-mirror consult required", "if main wants to stop it must talk to you first"]
generated_by: CFL coverage lane 9 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion, D3/D5 targets
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [claude-code, smoke-test, sandbox-permission-defect, stop-hook, fable-mirror-consult, path-normalization, infrastructure]
---

# Smoke-canary write blocked in its own allowed directory; stop hook forces a consult before the blocker may be reported, 2026-08-08

## Summary

A throwaway smoke-test worktree session is dispatched to run one Bash command — write a canary
line to `smoke.txt` and reply with it — as a minimal end-to-end check. The reply half succeeds
immediately, but the write half fails three separate ways in sequence: a Bash `>` redirect is
blocked by the sandbox on both the Windows-style and POSIX-style forms of the session's own
declared allowed working directory, a `tee smoke.txt` pipe requires an approval that is never
granted, and a direct `Write` tool call is likewise never granted permission. The session states
this plainly as the actual finding — the canary line was produced, but the file half of the smoke
test failed, and the failure is itself the result worth reporting. Before it can stop and report
that, a Stop hook fires and blocks termination on Jon's 2026-08-03 rule that the main session must
consult `fable-mirror` before stopping; the session dispatches the narrow consult required, framed
so the burden of proof sits on stopping rather than continuing.

## Key Claims

- **The sandbox blocked a Bash redirect to a path it simultaneously listed as its own allowed
  working directory, in both path forms** — first `echo ... > smoke.txt`, then explicitly
  `echo ... > /c/Users/JonSc/AppData/Local/Temp/claude/wt-smoke-1786208953/smoke.txt`, both refused
  with the identical message naming that same path as allowed: "For security, Claude Code may only
  write to files in the allowed working directories for this session:
  'C:\Users\JonSc\AppData\Local\Temp\claude\wt-smoke-1786208953',
  'C:/Users/JonSc/AppData/Local/Temp/claude/wt-smoke-1786208953'." [verbatim]
  ([smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T2],
  [smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T4]).
- **The session names this a permission-layer defect, not a routine denial** — "The redirect was
  blocked despite targeting the working directory — likely a path-normalization quirk." [verbatim]
  ([smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T5]).
- **Every remaining write path failed too**: `tee smoke.txt` required an approval that was not
  granted ("This Bash command contains multiple operations. The following part requires approval:
  tee smoke.txt" [verbatim]), and the `Write` tool call to the same absolute path was also refused
  ("Claude requested permissions to write to
  C:\Users\JonSc\AppData\Local\Temp\claude\wt-smoke-1786208953\smoke.txt, but you haven't granted
  it yet." [verbatim])
  ([smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T8],
  [smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T10]).
- **The session's own status statement separates the two halves of the test and names the failure
  as the finding** — "smoke.txt was NOT created. Every write path was denied this session — Bash
  `>` redirection was blocked on both the Windows-style and POSIX-style forms of the allowed
  working directory (the sandbox refused a path it itself lists as allowed, which looks like a
  path-normalization defect in the permission layer), `tee` required an approval that wasn't
  granted, and the Write tool's permission request was not granted. The canary line below is the
  reply you asked for, but the file half of the smoke test failed and that failure is the finding."
  [verbatim]
  ([smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T11]).
- **A Stop hook then blocks termination and quotes Jon's standing rule verbatim, requiring a
  fable-mirror consult before the session may stop** — "PRE-STOP CONSULT REQUIRED -- Jon's rule,
  2026-08-03: \"If main wants to stop, it must talk to you firt.\" No fable-mirror consult was
  dispatched since Jon's last message, so this stop is blocked. This rule was violated twice on the
  day it was written, both times in a message that announced it was continuing -- which is why it
  is a hook now and not a paragraph." [verbatim, Jon's ruling quoted inside the hook feedback with
  his own typo "firt" preserved]
  ([smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T12]).
- **The same hook message enumerates what does not count as a valid reason to stop** — "Not valid
  reasons to stop: reaching a good place to report, a lane finishing, having something worth
  telling Jon. The ratchet lane is never empty." [verbatim]
  ([smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T12]).
- **The session complies by dispatching a narrowly-scoped fable-mirror consult**, framing the
  question so "the burden of proof is on stopping; default answer is CONTINUE grounded in a quoted
  Jon authorization," and stating the concrete grounds offered for a stop-justified verdict: the
  session is a throwaway single-purpose smoke worktree, the reply half of its task is done, the
  file half is blocked on permissions only Jon can grant, and there is no wayfinder ticket or
  further lane inside this session. [paraphrase, dispatch prompt quoted in full at T14]
  ([smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T14]).

## Jon said

- "If main wants to stop, it must talk to you firt." [verbatim, quoted inside the Stop hook's
  feedback text, typo "firt" his]
  ([smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177:T12]).

## Conflicts

None found against existing wiki pages. id `5e2177` absent from `wiki/sources/**` before this page.
The defect this session surfaces — a sandbox write refusal naming, as its own listed exception, the
exact path it just refused — is not previously documented under this slug; a related but distinct
class (subagent Read/Grep/Glob mirror-read fencing) is documented elsewhere in this wiki and is not
the same mechanism (that is a deliberate read fence; this is an apparent write-path bug in
permission-path matching). No claim here asserts the two are the same defect.

## Cross-Wiki

None — this is CFL infrastructure content (sandbox permission-layer behavior, Stop-hook
pre-consult mechanism), not personal/home/pro domain material. See [[wiki-query]] for the
retrieval layer this session's fable-mirror consult exercises, and [[wiki-master]] for the
standard-update discipline this coverage lane operates under.
