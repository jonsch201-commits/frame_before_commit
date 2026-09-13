---
title: "Docker/IoT sandbox planning session; and a fable-mirror elder-consultation fork's pre-stop hook fires despite the fork's own dispatch instruction to 'not consult the mirror,' surfacing a naming conflict the coordinator holds open for Jon (2026-08-07, 7c4392)"
trunk: fl
kind: source
source_kind: session
uuid6: 7c4392
source_file: raw/transcripts/claude-code/fl/code-2026-08-07-7c4392-docker-iot-network-sandbox.md
raw_sha256: 22894913620664fae926da9dc8816e25c116e5ceea41d9a18cd39a9a6961e7ce
raw_length: 217541 bytes (verified turn_count 132, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: cfl-elder-fork-stop-hook-conflicts-with-do-not-consult-instruction-2026-08-07-7c4392
aliases: ["Docker sandbox before TP-Link Deco API access sequencing", "Deco XE200 not X60 wiki correction", "elder fork told answer from memory do not consult the mirror then stop hook demands a mirror consult", "hook wins by default even when session framing says the opposite"]
generated_by: S-cd-05 executor (week-2026-09-02-corpus lane), reading the raw transcript directly from the N: read-only mirror (bounded line-range reads via turn_index.py, no whole-file read)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [cfl-coordinator, fable-mirror, pre-stop-consult, docker, iot-network, cfl-infra, security-master]
---

# Docker/IoT sandbox plan, and a fable-mirror elder fork's stop-hook conflict (2026-08-07, 7c4392)

## Summary

A security-master-framed session first plans Docker-sandboxed isolation as the prerequisite for
any automated TP-Link Deco router API access (IoT network segmentation off the guest network),
recommending the Python API path over Android-emulator UI automation and correcting a wiki
hardware/IP conflict (Deco is XE200, not X60). The session was then re-consulted, in the same
transcript, as an "elder" — explicitly told to answer from memory only, not run scripts, and not
consult the mirror. When that fork tried to stop after answering the single question asked, the
standing pre-stop-consult hook fired and required exactly the mirror consult the dispatch had
forbidden, and fable-mirror itself returned no corpus evidence either way for elder-fork stop
exemption — leaving the session to name the conflict explicitly rather than resolve it
unilaterally.

## Key Claims

- **Docker/sandbox isolation is the confirmed prerequisite for TP-Link Deco API automation, and
  the reasoning is architectural, not just sequencing:** "The TP-Link Deco local API requires auth
  tokens... Without a container, those tokens would sit on the Windows filesystem accessible to
  any process running as your user — including every Claude Code session." Blast radius, auditability
  (explicit `-v output:/data` mounts), and reproducibility (Dockerfile checked into the repo) are
  named as the four reasons, in that order. [quote verbatim of the isolation clause; paraphrase of
  the remaining three]
  ([cfl-elder-fork-stop-hook-conflicts-with-do-not-consult-instruction-2026-08-07-7c4392:T20])
- **Wiki hardware/IP conflict flagged for correction:** "⚠️ WIKI CONFLICT: 869da8 source documents
  Deco as X60 with Advanced → Wireless in web UI. This session confirmed hardware is XE200 and web
  UI is Status + System only... (Deco model, LAN IP 192.168.0.1 not .68.1, Home_Base IP .0.83 not
  .68.50)." [quote verbatim]
  ([cfl-elder-fork-stop-hook-conflicts-with-do-not-consult-instruction-2026-08-07-7c4392:T20])
- **Python local-API path recommended over Android-emulator UI automation for Deco IoT
  management:** "UI automation against the Deco app is brittle — app updates silently break
  element selectors. The TP-Link local HTTP API doesn't change on app updates... Android emulator
  is a better fit for tasks where no API exists." Library ranked: `python-tplink-deco` (HA
  community, XE200-confirmed) preferred over direct requests/pycryptodome calls or
  `tplink-smarthome-api` (wrong family — Kasa only). [paraphrase; quote of the brittleness clause
  verbatim]
  ([cfl-elder-fork-stop-hook-conflicts-with-do-not-consult-instruction-2026-08-07-7c4392:T20])
- **The same transcript later carries an elder-consultation fork, explicitly scoped away from
  live-session norms:** "You are being consulted as an elder, not asked to do work... answer in
  plain prose only. Answer FROM MEMORY. Do NOT read any files... do not run scripts, do not
  consult the mirror." Asked what earlier Claude setups Jon may have had before the current CFL
  program; the fork answered honestly that Jon never named predecessors in its own session and
  declined to speculate beyond what it observed (heavy pre-existing ceremonialization, a
  security-master stub with 4 waiting packets, a possible restraint period after an April 2026
  malware incident). [paraphrase; dispatch instruction quoted verbatim]
  ([cfl-elder-fork-stop-hook-conflicts-with-do-not-consult-instruction-2026-08-07-7c4392:T128])
- **The pre-stop hook fired on the elder fork's attempt to stop, in direct conflict with the
  fork's own dispatch instruction, and the fork surfaced the conflict rather than silently
  resolving it either way:** "the elder consultation framing in your message said explicitly 'do
  not consult the mirror'... The stop hook then fired requiring a mirror consult before stopping.
  I followed the hook... but the two instructions are in direct tension... If elder consultation
  forks are meant to be exempt from the ratchet-lane stop rule, that exemption needs to be written
  into the hook logic or the elder consultation protocol — one of them has to name the other.
  Right now neither does, so the hook wins by default even when the session framing says the
  opposite." The dispatched fable-mirror consult itself returned "without a quoted authorization
  to stop — sparse output, no corpus evidence found either way for elder-fork stop behavior
  specifically," so the hook's own CONTINUE default applied. Held open pending direction. [quote
  verbatim, both clauses]
  ([cfl-elder-fork-stop-hook-conflicts-with-do-not-consult-instruction-2026-08-07-7c4392:T130])

## Conflicts

Flags its own wiki conflict against source `869da8` (Deco X60 vs XE200, and two IP addresses) —
see Key Claims above; not resolved within this transcript.

## Entities & Concepts

Jon's 2026-08-03 pre-stop-consult rule (same rule investigated for origin in sibling session
`a40525` this batch); elder-consultation fork protocol (no prior written exemption from the stop
hook — the gap this session names); fable-mirror pre-stop-consult swarm (cross-referenced in
sibling session `59e505`); Deco XE200 IoT network segmentation; [[derive-dont-record]].

## Uncaptured Content

- 35 thinking blocks encrypted-in-signature; no claim draws on them.
- 1 compaction boundary present; per corpus convention this is a `user`-role harness record, not
  attributed to Jon, and the mid-transcript compaction/re-brief content is not further reproduced
  here beyond the quoted plan excerpts. [uncaptured]
- The Human turn preceding the Docker/IoT plan (opening security-pass framing) is summarized from
  the corpus's own auto-generated "Summary" block, not independently verified against the raw
  Human text in this pass. [uncaptured — summary-sourced]

## Links

- Sibling same-morning fable-mirror pre-stop-consult sessions: `59e505`, `a40525` (both this
  batch, `wiki/sources/infrastructure/`).
- Filed under `wiki/sources/infrastructure/` rather than `wiki/home/sources/` per this lane's
  literal instruction and because the session runs in the CFL trunk (`project: fl`) documenting a
  fable-mirror stop-hook conflict, not merely home-device facts — same reasoning as recorded in
  `wiki/intake-triage/S-cd-04-report-2026-09-03.md` dead-end #4 for the sibling `32d5c1`/`325ce6`
  Deco/security sessions; may belong moved to `wiki/home/sources/` on a future pass.
