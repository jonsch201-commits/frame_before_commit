---
name: oath-pairing-check
description: Verifies every PreCompact receipt after a given epoch has a matching barrier record within 60 minutes, the mechanical check behind OATH breach condition (b) (wiki/tracker/OATH-cfl-second-ideal-2026-08-29.md). Federated — pass any trunk's own --receipts and --records directories; nothing here is CFL-specific. Run it at every wake and at every compact/close boundary, before other work resumes; a nonzero exit is a blocking finding to record, not to silently retry past.
---

# oath-pairing-check

Mechanical check for CFL's second-ideal oath, breach condition (b) as re-cut in
`wiki/tracker/OATH-cfl-second-ideal-2026-08-29.md`:

> the oath is broken when a PreCompact receipt exists whose session has NO barrier record
> written at that same boundary (record `as-of` within the boundary window preceding the
> receipt, same session id) — pairing semantics, not raw timestamp order.

This skill is a **federated instrument**: it takes its two directories as arguments and hardcodes
no CFL path. Any trunk — this one or a stranger — can run it against its own receipts/records
directories (LAZY-2: a stranger runs it without us).

## When to invoke

At every wake, and at every compact or close boundary, before other work resumes. It is the
oracle for the OATH's condition (b) row and for T-10 row-5. A nonzero exit is a finding to
record (a new unpaired post-epoch receipt), not a thing to re-run until it goes away.

## What it checks

A **PreCompact receipt** — filename `YYYYMMDDTHHMMSS-<sess8>.md` — is **PAIRED** iff a
**barrier record** — filename `compact-<sess8>-YYYYMMDDTHHMMSS<tz>.md` (the same 8-hex-char
session prefix) — exists whose timestamp is **no later than** the receipt's own timestamp and
**no more than 60 minutes earlier**. Only `compact-`-prefixed record files count as barrier
records for this check; `close-`, `fold-in-`, and `branch-dispatch-` records are a different
instrument's concern.

A receipt dated before `--epoch YYYY-MM-DD` (date-only comparison — the day itself is **not**
before the epoch) is reported **PRE-EPOCH**: counted in the summary, never graded PAIRED or
UNPAIRED. This is the "Yeah no deletion" epoch pattern — old receipts are not silently dropped,
they are named and set aside.

A receipt named by `--known-breach <basename>` (repeatable) prints **KNOWN-BREACH** instead of
being graded fresh — it is already dispositioned (see BREACH №1 in the OATH file) and does not
re-fire the exit code.

## Usage

```
python scripts/pairing_check.py --receipts <dir> --records <dir> [--epoch YYYY-MM-DD] \
    [--known-breach <receipt-basename>]...
```

Exit codes:

- `0` — no NEW unpaired post-epoch receipt (PRE-EPOCH and KNOWN-BREACH do not count).
- `1` — at least one NEW unpaired post-epoch receipt.
- `2` — a supplied directory could not be read. **UNKNOWN dominates a PASS** — this never
  collapses to exit 0.

## Self-test

```
python scripts/pairing_check.py --selftest
```

Builds a temp directory (removed on exit) and exercises both controls per P29's rule — both a
positive and a negative case must be demonstrated before a check binds:

- a paired receipt prints `PAIRED` and the run exits 0,
- an unpaired receipt exits 1,
- a pre-epoch receipt is excluded from grading even though it would otherwise be unpaired,
- a known-breach receipt prints `KNOWN-BREACH` and does not push the exit code to 1,
- an unreadable directory exits 2.

Prints `PASS`/`FAIL` per control and exits 0 only if every control passed.

## CFL's own real invocation (example, not a hardcoded default)

```
python skills/oath-pairing-check/scripts/pairing_check.py \
    --receipts exchange/su-close/precompact \
    --records exchange/memory-core-v0/instances \
    --epoch 2026-08-29 \
    --known-breach 20260830T020943-9041f3b0.md
```

See `wiki/intake-triage/LANE-oath-pairing-skill-2026-08-30.md` for the first real run's output
and a finding on the date-only `--epoch` boundary.
