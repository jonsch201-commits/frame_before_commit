---
name: memory-core
description: >-
  The barrier-write discipline for Core Memory v0 (spec skills/memory-core/references/SPEC.md;
  store exchange/memory-core-v0/instances/). Use at every
  session barrier: compact (PreCompact), close, branch-dispatch (forking a lane), and fold-in (a
  lane's return). Trigger phrases: "write a memory", "barrier", "fold in", "branch snapshot",
  plus any compact or session-close event. Covers write_barrier_memory.py invocation, the
  CLAIMED/VERIFIED/CHANGED fold-in discipline, consolidation status, and the
  verbalize-before-the-barrier rule (a dispatched lane carries its snapshot WITH it, not
  separately).
---

# memory-core

A tool skill wrapping Core Memory v0. It writes durable, addressable, resumable records at the
four points where session state would otherwise be lost: compact, close, branch-dispatch,
fold-in. Read `exchange/memory-core-v0/README.md` (one screen, the pack's cold-start entry)
before first use, then `skills/memory-core/references/SPEC.md` for the normative schema and error semantics — this
file is the operating discipline, not a restatement of the spec.

## Role boundary

⛔ **Official locations (rehomed 2026-08-22 on Jon's finding that a final spec cannot live in a
message channel).** Spec and reference docs: `skills/memory-core/references/` — **`SPEC.md` there
is the normative one**, reconciled to as-built; the `exchange/memory-core-v0/SPEC.md` copy is
frozen with a POINTER and will drift. Scripts: `skills/memory-core/scripts/`. Templates:
`skills/memory-core/templates/`. **The store does NOT live in the skill** — runtime data is not
skill content; its official home is the `MEMORY_ROOT` parameter
(`skills/memory-core/references/PORTABILITY-DECISION.md`), and CFL's `exchange/memory-core-v0/instances/` is the
**v0-transitional** binding of it, which is still both scripts' default.

- Writes only under the bound store (`exchange/memory-core-v0/instances/` today) — append-only,
  never overwrites; a colliding filename gets a `-2` disambiguator.
- Touches no harness config. **Hook status, the one formula to use everywhere: `script COMPLETE,
  wiring PROPOSAL-ONLY (never applied)`** (`skills/memory-core/scripts/WIRING-PROPOSAL.md`). It goes live when PR-3
  merges — one gate, not two.
- Does not hand-edit a JSON section after it is written (append-only; corrections are new
  `events` entries, never edits to prior fields) and never hand-edits an MD/Summary section
  (both are generated from JSON — regenerate, don't patch).

## The four barriers

| Barrier | Fires at | What gets written | Template |
|---|---|---|---|
| **compact** | PreCompact | live state, open claims, resume anchor — what "0 compacts allowed" was protecting | `skills/memory-core/templates/compact-memory.md` |
| **close** | session end | full memory + consolidation pass + index row | `skills/memory-core/templates/close-memory.md` |
| **branch-dispatch** | dispatching a fork/Agent | conditioning snapshot carried OUT **inside** the fork prompt | `skills/memory-core/templates/branch-dispatch-snapshot.md` |
| **fold-in** | a lane's return, after grading | CLAIMED/VERIFIED/CHANGED reunion record | `skills/memory-core/templates/fold-in-reunion.md` |

compact and close are the only two that are harness hook events; branch-dispatch and fold-in have
**no hook event at all** — nothing fires automatically at "the coordinator dispatched a lane" or
"a return folded in." Those two wire at the **coordinator's own call site**, as procedure, not
config (`skills/memory-core/scripts/WIRING-PROPOSAL.md` §2).

## Invoking the writer

```bash
python skills/memory-core/scripts/write_barrier_memory.py \
  --barrier compact|close|branch-dispatch|fold-in \
  --session <uuid> --as-of <full ISO8601> [--lane <name>] [--seat <seat>/<model>]

# sanity-check before relying on it
python skills/memory-core/scripts/write_barrier_memory.py --selftest --as-of "$(date -Iseconds)"
```

**`--session` is the WRITING session's OWN uuid — never the example value from a template's
worked example (that one belongs to the originating session).** Find your own id with
`echo $CLAUDE_CODE_SESSION_ID` (verified present) or, as fallback,
`ls -t ~/.claude/projects/<this-project-slug>/*.jsonl | head -1` (mtime ordering — confounded by
a concurrent live session in the same project; prefer the env var). A `--session` that does not
resolve to a JSONL is **refused, exit 2**, with a teaching message — never written with a silent
UNKNOWN resume anchor (Soul Trial-B finding F1: a bogus session used to succeed quietly, which is
worse than failing loudly, since the anchor is the one thing the artifact exists to carry).

`--as-of` is **always required, never defaulted** — a self-clocked timestamp is an unverifiable
one, repo convention. Inside a hook, pass the measured wall clock at fire time
(`$(date -Iseconds)`); that is a measured argument, not a banned default.

Output lands in `instances/`, one file per write:
`<barrier>-<session8>-<timestamp>.md`. An instance still carrying template placeholders
self-declares `STATUS: SKELETON` in its header — treat a skeleton as **a barrier reached but not
yet graded**, never as recorded state.

## The fold-in reunion discipline

A return that is merely pasted in is swallowed, not remembered. The reunion record — three
columns, always — is what makes a lane's work part of the parent's memory instead of an
unverified quote:

- **CLAIMED** — verbatim from the return. The author never scores their own claim.
- **VERIFIED** — a **parent-side** check with its own evidence pointer: re-run, grep, diff,
  count. "The lane said so" is not verification.
- **CHANGED** — deltas found on receipt: corrections, surprises, side effects, new tickets. An
  **empty CHANGED column on a nontrivial return is suspicious, not clean** — it usually means the
  parent didn't look hard enough.

**Reunion only counts if you change something on receipt.** A fold-in that copies CLAIMED into
VERIFIED with no independent check, and leaves CHANGED empty, has not folded anything in — it has
relayed. Close the loop the same way any shared registry closes: append DONE (or NOTE) to
`exchange/WORK-CLAIMS.md`, then **grep your own marker back** — a write is not a delivery
(the same discipline WORK-CLAIMS itself runs on).

Worked example (real fold-in, session `643640a7`, 2026-08-21): a lane claimed "3 ranker defects
fixed, lex reaches top-k"; the parent independently re-read the diff and re-ran the selftest
before verifying it; and the CHANGED column caught something the CLAIMED column never mentioned —
the same return had been ingested 4× by the agent-end hook, turn count drifting 18→21 — which
became its own new ticket. See `skills/memory-core/templates/fold-in-reunion.md` (worked
example below the double rule).

## Verbalize-before-the-barrier

At dispatch, the snapshot is not written and left behind — it travels **inside** the fork prompt
itself: run the branch-dispatch write first, then include the resulting instance's content (or
its path, for a lane that can read files) as the conditioning the lane starts with. A lane that
starts from a bare task line has lost everything the parent knew going in; a lane that starts
from the snapshot starts with the parent's conditioning. This is what "verbalize before the
barrier" means mechanized — say the state out loud (write it) before the branch point, not after.

## Consolidation status

`skills/memory-core/scripts/consolidate_memory.py` builds `INDEX-tier0.md` (tier-0, ≤200 lines / ≤25 KB hard cap) and
runs merge/decay/promote as append-only consolidation events. **Status: LIVE. First live pass run
2026-08-22 (D-1 receipt) — `INDEX-tier0.md` exists, 39 lines / 3,300 B, all 22 instances then on
disk seeded; re-run twice more the same day with zero record inflation.** ⚠️ This paragraph said
*"NOT YET LIVE — it has not been run against the live store"* until the reconcile; that was true
when written and false by 16:0x the same day (SPEC.md changelog C-23). **Consolidation runs by
RITUAL, not by gate** (SPEC.md § Gates G-1). For any pack the script has NOT been run against, no
index exists and the `instances/` listing is the working index (`ls -t instances/` for
newest-first — a plain listing groups by barrier prefix, not time).

**The bootstrap gap is open and you should expect it:** nothing at any barrier writes citations
between records, so PROMOTE can never fire. The D-2 exhibits ran the pass forward +30d and +90d:
**22/22 decayed, 0 promoted, both times.** Decay is the only move that fires in steady state.

`--pack` is required with no default, and a pack inside a git working tree is refused unless
`--pack-tracked-ok` is explicitly passed (SPEC.md § Gates G-4 respecifies this as a ONE-TIME
per-pack acknowledgment — not yet built; today it is needed on every run) — consolidation MERGE copies source bodies verbatim into
the pack, and a tracked pack is GitHub-bound (No-PII-to-GitHub, CFL-D-003/CFL-D-009 apply).

## Hook liveness — check before trusting any boundary artifact

A hook runner can die inside one live session while `.claude/settings.json` stays valid and
sibling seats keep firing the identical config — measured 2026-08-20, one session's hooks went
silent for 1,312 further transcript lines across two compact boundaries while a sibling session
kept firing. **Wiring is a property of a file; firing is an event, and only the transcript
records it.** Run the three-line check in `skills/memory-core/scripts/LIVENESS.md` at every
wake and before trusting that a PreCompact/Stop artifact exists. On DEAD, do not edit
`settings.json` — assume dead for the rest of that session and run every barrier write by hand
(LIVENESS.md has the exact commands).

## What this skill does NOT do

- Does not wire hooks into the harness: `script COMPLETE, wiring PROPOSAL-ONLY (never applied)`.
- Does not run consolidation automatically — `consolidate_memory.py` is a separate, explicit
  invocation, and its live status is above (it HAS run; it is not automatic).
- Does not resolve the intuitive-vs-queryable fork (MD+Summary as the human surface vs
  JSON+index as the query surface) — that question is reserved for Jon at gate G-2
  (`skills/memory-core/references/SPEC.md`, Out of Scope). Write both surfaces; privilege neither.
- Does not delete or truncate. Rollback is by parent chain, never by line-truncation.

## Keywords

write a memory, barrier, compact memory, close memory, fold in, branch snapshot,
verbalize-before-the-barrier, write_barrier_memory.py, consolidate_memory.py, CLAIMED VERIFIED
CHANGED, reunion table, hook liveness, resume anchor, core memory v0, INDEX-tier0.
