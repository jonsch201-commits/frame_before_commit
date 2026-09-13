---
title: "CFL security-master pass: two-mode Docker architecture adopted (host runs Claude Code/browser/MCP, container runs credential-touching scripts) after a grill-me; Deco IoT-network triage ranks a TP-Link Python API over an Android-emulator path; first documented firing of the fable-mirror pre-stop-consult stop-hook loop (2026-08-07, 32d5c1)"
trunk: fl
kind: source
source_kind: session
uuid6: 32d5c1
source_file: raw/transcripts/claude-code/fl/code-2026-08-07-32d5c1-docker-iot-network-sandbox.md
raw_sha256: e8609cf161750750540247f8b317e9e8f8fa0967b0f7fc04b394e09b8491d15b
raw_length: 233223 bytes (verified turn_count 154, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: cfl-security-pass-docker-two-mode-architecture-deco-iot-triage-and-first-stop-hook-loop-2026-08-07-32d5c1
aliases: ["Docker is a blast-radius limiter not a security posture for Claude Code", "two-mode architecture host vs container", "Deco XE200 IoT SSID separate from guest isolation", "TP-Link Python API ranked over Android emulator", "PRE-STOP CONSULT REQUIRED Jon's rule 2026-08-03", "fable-mirror stop authorization Closed"]
generated_by: S-cd-04 executor (week-2026-09-02-corpus lane), reading the raw transcript directly from the N: read-only mirror (FULL visible extraction, 1 compaction boundary, 38 thinking blocks encrypted); re-anchored UC-0c 2026-09-03 per contract v1 section 5 -- 5 claims, 3 verified unchanged (T8, T154 x1), 2 moved (T127->T56, T8->T7 on the Deco-triage claim; T154->T129 on the stop-hook-text claim)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [security-master, docker-sandbox, home-network, deco, stop-hook, fable-mirror, cfl-infra]
---

# CFL security-master pass: two-mode Docker architecture, Deco IoT triage, and the first stop-hook loop (2026-08-07, 32d5c1)

## Summary

A CFL security-master session (continued across one compaction boundary) working a home
network/PC security pass: Apollo (Sunshine) admin password secured, port forwarding confirmed
clean, Deco router model/IP corrections filed to the wiki, and a Docker-sandbox architecture
decided after Jon requested a grill-me on the plan. The session then triaged options for
autonomous Deco IoT-network management (moving 2.4GHz devices off the guest network), ranking a
TP-Link Python API over an Android-emulator/virtual-phone path. Toward the session's end, the
transcript records the first documented firing (in this batch) of a new stop-hook rule requiring
a fable-mirror pre-stop consult before the session may stop, and the session's compliant response.

## Key Claims

- **The Docker security architecture settled on two modes, after Jon requested a grill-me:**
  Host mode runs Claude Code, Chrome automation, Gmail MCP, and PowerShell (cannot be
  containerized — needs Windows host integration); Container mode runs TP-Link API calls and
  other credential-touching scripts on a `python:3.12-slim` base with env-var-only credentials
  and explicit output mounts. [paraphrase, drawn from the session's own handoff artifact]
  ([cfl-security-pass-docker-two-mode-architecture-deco-iot-triage-and-first-stop-hook-loop-2026-08-07-32d5c1:T56])
- **Jon's words requesting the plan, verbatim:** "I do not what to do what you say I have to do
  now. That sounds like hell. Further, I will need you to explain our options for security and
  network efficiency here, and cite your reasoning. Regardless, sounds like we will likely need
  to do docker session first. Plan for the IoT network vitrual app phase, but then plan for the
  docker session. i will use grill-me on the docker plan." [verbatim, typos his]
  ([cfl-security-pass-docker-two-mode-architecture-deco-iot-triage-and-first-stop-hook-loop-2026-08-07-32d5c1:T8])
- **Deco XE200 IoT-network triage:** the app's "IoT Network" feature (a separate SSID, distinct
  from guest isolation — IoT-SSID devices can still reach the main LAN) is the correct answer
  for 2.4GHz devices; the web UI can do nothing here (Status + System only, all SSID management
  is app-only). Ranked autonomous-control options: manual (100% now) > TP-Link Python API
  (high confidence, needs Docker) > Android emulator + ADB (medium, brittle to app updates) >
  full virtual-phone VM (low priority, overkill). [paraphrase]
  ([cfl-security-pass-docker-two-mode-architecture-deco-iot-triage-and-first-stop-hook-loop-2026-08-07-32d5c1:T7])
- **A new stop-hook rule fired for (apparently) the first time this session:** "PRE-STOP CONSULT
  REQUIRED -- Jon's rule, 2026-08-03: 'If main wants to stop, it must talk to you firt.'" The
  hook blocks stopping until a fable-mirror consult is dispatched with a narrow "I want to stop X
  because Y" question, burden of proof on stopping, default answer CONTINUE. Explicitly enumerated
  invalid reasons to stop: "reaching a good place to report, a lane finishing, having something
  worth telling Jon." [verbatim hook text]
  ([cfl-security-pass-docker-two-mode-architecture-deco-iot-triage-and-first-stop-hook-loop-2026-08-07-32d5c1:T129])
- **The session complied and stopped only after the consult:** dispatched fable-mirror with a
  narrow stop question (five-question elder consult complete, no new directive from Jon), ran
  `wake_map.py`, and recorded the one-line reason "done-and-verified — elder consultation
  complete, five questions answered from memory, no new work assigned this turn, fable-mirror
  confirmed STOP-OK conditioned on landing elder answers (conversational, no files to commit)."
  [verbatim]
  ([cfl-security-pass-docker-two-mode-architecture-deco-iot-triage-and-first-stop-hook-loop-2026-08-07-32d5c1:T154])

## Conflicts

None with existing wiki content noted in this transcript.

## Entities & Concepts

Security-master role (home PC/network audit); Docker two-mode architecture (host vs container);
Deco XE200 IoT SSID; TP-Link Python API; the fable-mirror pre-stop-consult stop hook (Jon's
2026-08-03 rule), an instance of [[derive-dont-record]] applied to session termination itself
(burden of proof on stopping rather than a recorded default); `wake_map.py`; sibling sessions
`c4a3e7` and `325ce6` continue the same underlying stop-hook-loop pattern and
Deco/security-audit thread.

## Uncaptured Content

- 38 thinking blocks encrypted-in-signature; no claim draws on them.
- The full Windows-process/persistence audit output (Phase 2 of `run-a-security-pass-
  peaceful-owl.md`) is referenced but not reproduced in the claims above.
- Router IPs, device SSID names, and specific credentials appear in the raw transcript; none are
  reproduced in this page per the no-financial/no-unnecessary-PII scope.

## Links

- Sibling sessions in this batch continuing the same thread: `c4a3e7` (stop-hook loop repeats
  three times, fable-mirror returns "Closed" each time — treated as STUB, no new claims beyond
  this page and `325ce6`), `325ce6` (own PAGE — reflective self-honesty content, Jon quotes,
  misread-risk analysis).
