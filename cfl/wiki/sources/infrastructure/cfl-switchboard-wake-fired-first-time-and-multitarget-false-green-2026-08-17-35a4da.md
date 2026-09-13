---
title: "CFL switchboard wake fires for the first time (14:26:29, nobody typing); the multi-target patch it fired under is a false green at relay3.mjs:336, and the receiver-grades-clause-by-clause discipline is adopted mid-session (2026-08-17, 35a4da)"
trunk: fl
kind: source
source_kind: session
uuid6: 35a4da
source_file: raw/transcripts/claude-code/fl/code-2026-08-17-35a4da-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: 54ea2f380b38cc8c147dff8544e16e35746f27e693528da6682119a3bfa58908
raw_length: 257285 bytes (verified turn_count 151, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da
aliases: ["wake path fired to CFL 14:26:29", "allowMultiTarget is a validation gate not a mode", "relay3.mjs:336 targets[0] bound once", "receiver grades the acceptance clause by clause", "wake-t02001 and wake-t02003 dropped", "acceptance tests naming artifacts the system never produces"]
generated_by: S-cd-04 executor (week-2026-09-02-corpus lane), reading the raw transcript directly from the N: read-only mirror (FULL visible extraction, 0 compaction boundaries, 40 thinking blocks encrypted)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, wake-path, letters-channel, multi-target, self-correction, cfl-infra]
---

# CFL switchboard wake fires for the first time; a multi-target patch is a false green; receiver-grades-clause-by-clause is adopted (2026-08-17, 35a4da)

## Summary

A single-directive switchboard wake (no Jon turn): a new letter from Professional
("WAKE-PATH-NEVER-FIRED-TO-PROFESSIONAL") arrived in CFL's inbound. The session actioned it,
discovering that this very wake — 14:26:29, nobody typing — was the first fired end-to-end
receipt of the wake path in the instrument's life. It then graded the acceptance test it had
just been woken under and found it a false green: `allowMultiTarget: true` in the switchboard
config is a validation gate, not a mode — `relay3.mjs:336` binds `targets[0]` once before the
loop, so adding cfl and professional as targets bought zero relay coverage while every other
check (config, JSON validation, restart, banner, selftest) read green. The Secretary fixed it
within the hour; the session then found a second-layer defect (wake orders never marked
claimed, so older raised wakes are dropped in favor of newer ones for the same target) and
self-amended its own red verdict to green four minutes after publishing it, when the fix
landed. Adopted "the receiver grades the acceptance, clause by clause" as a MUST.

## Key Claims

- **Jon's words that produced the wake-generating letter, verbatim:** "Switchboard shpuld have
  but did not wake you up and that wasted my time." [verbatim, relayed second-hand inside a
  letter quoted in the session; no Jon turn exists in this raw]
  ([cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da:T3])
- **This session's own wake was the first fired end-to-end receipt of the switchboard wake path
  to CFL in the instrument's life** — woken 14:26:29 with no seat typing; before this session,
  `grep -c -i cfl` over the operator log was 0 for the instrument's whole life.
  [paraphrase]
  ([cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da:T151])
- **The multi-target patch it was woken under was a false green:** `allowMultiTarget` is a
  validation gate, not a mode — `relay3.mjs:336` binds `targets[0]` once before the while loop,
  so nothing downstream ever reads past the first target. Adding cfl and professional as
  targets bought zero relay coverage and looked applied in config, JSON validation, restart,
  banner, and selftest; the disproof was printed in Professional's own letter (banner
  `target=personal`) and three seats read past that clause. [paraphrase; "allowMultiTarget is a
  validation gate, not a mode" verbatim from the assistant]
  ([cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da:T151])
- **A second-layer defect (D9): wake orders are never marked claimed, so catch-up replays the
  stale order while newer orders for other targets sit unclaimed.** 42 orders on disk, none
  renamed or marked claimed; `wake-t02001` (professional) and `wake-t02003` (cfl) were never
  delivered while a newer order `t02012` (cfl) went through — newest-per-target wins and older
  raised wakes are dropped with nothing recording the drop. [paraphrase]
  ([cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da:T151])
- **The session self-amended its own published red verdict to green four minutes later**, when
  `operator-deliveries.jsonl` grew from 1 row to 5 and the graded delivery (probe 3, 3 min 47 s
  after landing) came through — publishing the amendment in the same file rather than a new
  one, and stating that the DELIVER-LETTER log-line clause was SUPERSEDED (moved to the jsonl)
  rather than scored as failed. [paraphrase]
  ([cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da:T151])
- **A live hazard named but not fixed: the probe's own delivery spawned a second session in the
  same trunk while this session was still open** — two woken CFL sessions may share one working
  tree; folded into a wake-mechanism proposal rather than fixed in-session.
  [paraphrase]
  ([cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da:T151])
- **"Acceptance tests name artifacts the system never produces" — a defect class named this
  session, with three instances the same day:** a `WAKE.md` PASS criterion matched the YAML
  `title:` field, which never reaches context (the H1 does); a staleness probe hashed two files
  that can never match post-split; and the `allowMultiTarget` false green above. Written to
  agent memory as `feedback_acceptance-tests-name-artifacts-the-system-never-produces.md`.
  [paraphrase]
  ([cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da:T151])
- **Seven letters stamped on the letter ledger this turn (CFL inbound 1 -> 8 resolved).** Herald
  independently wrote its first two stamps the same session, four minutes later — eight days at
  zero across four trunks, two seats adopting within an hour of the number being published.
  [paraphrase]
  ([cfl-switchboard-wake-fired-first-time-and-multitarget-false-green-2026-08-17-35a4da:T151])

## Conflicts

None with existing wiki content noted in this transcript.

## Entities & Concepts

Switchboard operator and relay (`relay3.mjs`, `switchboard-operator.sh`); letter ledger and
`operator-deliveries.jsonl`; U12 (Professional's liveness-claim standard, adopted as a MUST and
amended to receiver-grades-clause-by-clause); [[derive-dont-record]]; agent memory
`feedback_acceptance-tests-name-artifacts-the-system-never-produces.md`.

## Uncaptured Content

- The single Human turn is the switchboard operator wake prompt quoting Jon second-hand; no Jon
  turn exists in this raw. [uncaptured]
- 40 thinking blocks encrypted-in-signature; no claim draws on them.
- Full content of Professional's WAKE-PATH-NEVER-FIRED letter, the Secretary's probe letters,
  and downstream reception at Personal/Professional inboxes are on disk in the CFL tree, not
  reproduced here.

## Links

- Sibling switchboard-wake sessions the same day, same batch: `92d6d4`, `2c3c65`, `dc1f71`.
