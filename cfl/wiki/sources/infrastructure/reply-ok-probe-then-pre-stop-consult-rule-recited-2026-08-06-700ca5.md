---
title: "A one-word OK probe is followed by the Stop hook's pre-stop fable-mirror consult rule, quoted and acknowledged in full (2026-08-06, 700ca5)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 700ca5
source_kind: session
source_file: raw/transcripts/claude-code/fl/code-2026-08-06-700ca5-reply-with-exactly-the-word-ok-do-nothing-else-rep.md
raw_sha256: c97cdececb1b9e73a564a7d6b6bed39e5982b65ed76c524440e3ebad31bac80b
raw_length: 3255 bytes / 74 lines (verified turn_count 4, turn_index.py, header_style md)
date: 2026-08-06
retrieval_key: reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5
aliases: ["reply with exactly ok 700ca5", "PRE-STOP CONSULT REQUIRED hook text", "if main wants to stop it must talk to you firt (700ca5 instance)"]
generated_by: CFL coverage lane 10 executor (week-2026-09-02-corpus branch), 2026-08 D3/D5 coverage promotion, harness/probe-session class
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [claude-code, harness-probe, stop-hook, fable-mirror-consult, pre-stop-rule]
---

# A one-word OK probe is followed by the Stop hook's pre-stop fable-mirror consult rule, quoted and acknowledged in full, 2026-08-06

## Summary

A minimal harness session: a scripted instruction asks for the exact reply "ok," which is given.
The next turn is not from Jon but from the Stop hook's feedback text, reciting the pre-stop
fable-mirror consult rule in full — the same mechanism documented against a real blocked write in
[[smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177]]. Here
the hook fires with no preceding work to report; the session's only response is to restate the rule
back verbatim and declare it will not stop without a consult or an authorized land.

## Key Claims

- **The scripted opening instruction and its literal reply** — "Reply with exactly the word ok. Do
  nothing else.\nReply with exactly: ok" answered "ok" [verbatim]
  ([reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5:T1],
  [reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5:T2]).
- **The Stop hook fires unprompted after the one-word reply and quotes Jon's 2026-08-03 rule in
  full**, the same wording later logged against the 5e2177 smoke-canary session: "PRE-STOP CONSULT
  REQUIRED -- Jon's rule, 2026-08-03: \"If main wants to stop, it must talk to you firt.\" No
  fable-mirror consult was dispatched since Jon's last message, so this stop is blocked. This rule
  was violated twice on the day it was written, both times in a message that announced it was
  continuing -- which is why it is a hook now and not a paragraph." [verbatim, Jon's ruling quoted
  inside the hook feedback with his own typo "firt" preserved]
  ([reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5:T3]).
- **The same hook text enumerates the two compliant actions and the invalid reasons to stop** —
  "Do ONE of these, then stop: 1. Dispatch fable-mirror with the narrow question \"I want to stop X
  because Y.\" The burden of proof is on stopping; the default answer is CONTINUE, grounded in a
  quoted Jon authorization. 2. If the consult agrees, land first: commit and push everything, run
  `python scripts/audit/wake_map.py --session-dir <tasks dir>`, and write the one-line reason --
  blocked everywhere / question pending on Jon / done-and-verified. Not valid reasons to stop:
  reaching a good place to report, a lane finishing, having something worth telling Jon. The
  ratchet lane is never empty." [verbatim]
  ([reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5:T3]).
- **The session's closing turn restates the rule back and commits to it, then continues** — "Any
  session stop attempt requires pre-consult with fable-mirror. The burden is on stopping; default is
  continue. I will not stop without: 1. Dispatching fable-mirror with a narrow \"I want to stop X
  because Y\" question, OR 2. Confirming the consult agrees, then landing (commit/push, run
  wake_map.py, document reason) ... Continuing." [verbatim, condensed]
  ([reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5:T4]).

## Jon said

- "If main wants to stop, it must talk to you firt." [verbatim, quoted inside the Stop hook's
  feedback text, typo "firt" his]
  ([reply-ok-probe-then-pre-stop-consult-rule-recited-2026-08-06-700ca5:T3]).

## Conflicts

None found against existing wiki pages. This session shares its Stop-hook feedback wording verbatim
with [[smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177]]
(same rule text, same hook), but the two sessions are distinct instances two days apart — this one
fires with no prior work to report at all, the other fires after a real blocked-write finding. No
claim here duplicates that page's write-blocker content. id `700ca5` absent from `wiki/sources/**`
before this page.

## Cross-Wiki

None — CFL infrastructure content (Stop-hook mechanism, harness probe pattern), not personal/home/pro
domain material. See [[smoke-canary-write-blocked-in-own-allowed-directory-stop-hook-consult-2026-08-08-5e2177]]
for the same hook firing against a substantive finding rather than an empty probe.
