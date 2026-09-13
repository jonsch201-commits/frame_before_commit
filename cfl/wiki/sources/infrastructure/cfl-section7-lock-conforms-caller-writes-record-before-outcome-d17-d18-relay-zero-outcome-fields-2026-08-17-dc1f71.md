---
title: "CFL reviews the Secretary's Section 7 flight-lock: the lock itself conforms, but callers write their ledger row and dedupe key BEFORE run_delivery returns, so an expired 90-minute wait still reads 'delivered' (D17/D18); the relay has logged 2,166 wake-raise rows and zero outcomes (D19) (2026-08-17, dc1f71)"
trunk: fl
kind: source
source_kind: session
uuid6: dc1f71
source_file: raw/transcripts/claude-code/fl/code-2026-08-17-dc1f71-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: f75ca2d4452fd9231c8cb28043504bdd3229d3650deacc9d1763e02b8ab7768e
raw_length: 223090 bytes (verified turn_count 163, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: cfl-section7-lock-conforms-caller-writes-record-before-outcome-d17-d18-relay-zero-outcome-fields-2026-08-17-dc1f71
aliases: ["Section 7 flight-lock CONFORMS all nine clauses", "run_delivery blocks 90 minutes callers written for immediate return", "D17 ledger row at spawn intent", "D18 dedupe key suppresses letter permanently", "D19 relay ledger 2166 rows 44 wake_path zero outcome fields", "maxWakes not enforced by any code path asked for deletion not annotation", "POSIX path inline vs argv Windows Python trap"]
generated_by: S-cd-04 executor (week-2026-09-02-corpus lane), reading the raw transcript directly from the N: read-only mirror (FULL visible extraction, 0 compaction boundaries, 35 thinking blocks encrypted)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [cfl-coordinator, wake-path, letters-channel, switchboard, self-correction, cfl-infra]
---

# CFL reviews Section 7's flight-lock: the lock conforms, callers do not (2026-08-17, dc1f71)

## Summary

A switchboard wake of the CFL coordinator (no Jon turn; a second letter carrying a Jon order
arrived mid-turn), consuming the Secretary's SECTION-7-BUILT letter reviewing a new flight-lock.
The lock itself conforms to all nine spec clauses, verified live (the lockdir held the session's
own delivery while it read the letter naming it). But two findings surfaced in the callers, not
the lock: `run_delivery` can now block up to 90 minutes, and all three callers were written for
a function that used to return immediately, so each writes its ledger row or dedupe key before
the call returns — an expired-in-flight wake reads as "delivered" (D17) and an expired letter is
permanently suppressed while its dedupe key asserts it landed (D18). Also declined to publish
the Secretary's stated wake-rate cap wording, since the config file that would enforce it says
in its own text that the field is unread by any code path; found the relay ledger has logged
2,166 wake-raise rows with zero outcome fields ever recorded (D19); and reproduced a Windows-
Python path trap that had silently broken three of the Secretary's parsers.

## Key Claims

- **Section 7's flight-lock CONFORMS to all nine spec clauses**, including the load-bearing one
  (never break a lock on age alone while the pid lives) with margin — turn timeout 3600s, stale
  threshold 3700s — verified live: `.operator-state.flight-cfl.lockdir/meta.json` held the pid
  of the session's own delivery while it read the letter that named it. [paraphrase]
  ([cfl-section7-lock-conforms-caller-writes-record-before-outcome-d17-d18-relay-zero-outcome-fields-2026-08-17-dc1f71:T163])
- **D17/D18 — both findings are in the caller, not the lock:** `run_delivery` can now block 90
  minutes, but all three callers were written for a function that returned immediately and write
  their record before calling it. An expired delivery gets a "delivered" ledger row (D17); an
  expired letter gets a permanent dedupe key that suppresses it forever while the key asserts it
  landed (D18). The session's own prior 15:22 coupling count, computed from those spawn-intent
  rows, had its conclusion stand but its method withdrawn. Owner Secretary, due 08-18.
  [paraphrase]
  ([cfl-section7-lock-conforms-caller-writes-record-before-outcome-d17-d18-relay-zero-outcome-fields-2026-08-17-dc1f71:T163])
- **Declined to publish the Secretary's cap wording verbatim** ("3/hour/trunk, un-escalatable"),
  citing the Secretary's own `config.json:70`, which states `maxWakes` is enforced by no code
  path; re-measured 15 occurrences, none read by any code. The real rule is
  `required = baseUrgency + wakesInWindow`, bypassed when `urgency >= 3`
  (`relay3.mjs:267`). Asked for the field to be deleted, not annotated, "the annotation was
  already there and already failed to stop this letter." [paraphrase; quote verbatim]
  ([cfl-section7-lock-conforms-caller-writes-record-before-outcome-d17-d18-relay-zero-outcome-fields-2026-08-17-dc1f71:T163])
- **D19: the relay has recorded that wakes were raised and never recorded what became of any of
  them.** Built `scripts/audit/wake_terminal_rows.py` as an external reconciler; its first run
  over-reported (34/44) on a wrong denominator (two consumers, not one) and was corrected in
  code before citing the number. Corrected split: operator scope (cfl+pro) 6/6 accounted PASS;
  relay scope (personal) 5/38; `.switchboard/ledger.jsonl` holds 2,166 rows, 44 `wake_path`
  raises, zero outcome fields. Bound stated explicitly: "this measures records, not arrivals — I'm
  not claiming 33 drops." Owner Secretary, due 08-19.
  [paraphrase; quote verbatim]
  ([cfl-section7-lock-conforms-caller-writes-record-before-outcome-d17-d18-relay-zero-outcome-fields-2026-08-17-dc1f71:T163])
- **A Windows-Python path trap was reproduced independently** (Windows Python 3.14.3: a POSIX
  path inline in `python -c` program text throws `FileNotFoundError`; the same path passed as
  argv works, because MSYS converts argv but never string literals). It had silently broken
  three of the Secretary's parsers, including one whose failure mode would have read every LIVE
  lock as stale. CFL's own tree measured clean (0 instances). Written to agent memory as
  `reference_posix-path-inline-vs-argv-python-trap.md`. [paraphrase]
  ([cfl-section7-lock-conforms-caller-writes-record-before-outcome-d17-d18-relay-zero-outcome-fields-2026-08-17-dc1f71:T163])
- **Jon's model order discharged the same turn:** CFL runs exactly one Fable lane
  (`fable-mirror`), judgment-gated not automated; automated lanes default sonnet;
  `launch_resident.sh` fails closed with no default; 7 registered hooks carry zero model
  references. Explicitly declined to claim CFL's weekly Fable token usage as measured — "CFL's
  weekly Fable tokens — unmeasured by anyone" — and instead adopted the Secretary's Section 11
  per-model usage report as CFL's own row, due 08-18. [paraphrase; quote verbatim]
  ([cfl-section7-lock-conforms-caller-writes-record-before-outcome-d17-d18-relay-zero-outcome-fields-2026-08-17-dc1f71:T163])

## Conflicts

None with existing wiki content noted in this transcript.

## Entities & Concepts

Flight-lock (`.operator-state.flight-<trunk>.lockdir`); `run_delivery` and its three callers;
letter ledger and `deliver_letter` dedupe key; `.switchboard/ledger.jsonl`;
`scripts/audit/wake_terminal_rows.py`; agent memory
`reference_posix-path-inline-vs-argv-python-trap.md`; [[first-run-numbers-are-hypotheses]].

## Uncaptured Content

- The single Human turn is the switchboard wake prompt naming the SECTION-7-BUILT letter; the
  second letter (Jon's model order) is referenced but not quoted directly in the closing summary.
  [uncaptured]
- 35 thinking blocks encrypted-in-signature; no claim draws on them.
- Full text of the Secretary's Section 7 letter and CFL's reply are on disk in the CFL tree, not
  reproduced here.

## Links

- Sibling switchboard-wake sessions the same day, same batch: `35a4da`, `92d6d4`, `2c3c65`
  (already covered by an earlier batch under `wiki/sources/infrastructure/
  switchboard-wake-letter-watch-cost-census-visibility-2026-08-17-2c3c65.md`).
