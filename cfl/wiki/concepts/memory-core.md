---
title: "Memory-Core — the Barrier-Write Discipline (Core Memory v0)"
aliases: ["memory core", "core memory", "barrier memory", "barrier-write discipline", "write_barrier_memory", "unsaid ledger mechanism", "the memory system", "session memory system", "core memory v0"]
kind: concept
trunk: fl
branch: [cfl]
sub_branch: [memory]
branch_reason: "R-CONCEPTS; promoted 2026-08-23 from 16 days of frozen tracker material per Jon's 'forcing a wiki update' directive"
type: concept
first_seen: skills/memory-core/references/SPEC.md (2026-08-22 reconcile)
source_count: 3
last_updated: 2026-08-23
maintained_by: wiki-master (proposal, this promotion pass — unratified)
---

# Memory-Core (Core Memory v0)

**What it is.** A barrier-write discipline that gives Jon's sessions state across the four
moments they otherwise lose it — **compact, close, branch-dispatch, and fold-in**. It answers his
stated problem: sessions "lose state at every barrier" and today's substitute is "fragmented: a
memory dir of flat lessons, handoff docs written only when someone remembers, WORK-CLAIMS rows
that record verbs but not conditioning" (`skills/memory-core/references/SPEC.md:29-32`).

Jon's own foundation, verbatim, ancestor msg 0, 2026-08-11 (`skills/memory-core/references/SPEC.md:35-39`):

> *"Json section, MD section, summary section. This is the foundation. Assume 0 compacts
> allowed."*

A memory instance is **resumable-from-a-point** — that is Jon's own definition of remembering:
it "could summarize itself and a fresh session could summarize it," and "You could resume it as a
subagent any time, and always from the same point if needed." JSONs are "purely addative" and
rollback-able to any message boundary.

## Where it lives

- **Spec (official, normative):** `skills/memory-core/references/SPEC.md` — 603 lines, reconciled
  to the shipped code 2026-08-22. Supersedes `exchange/memory-core-v0/SPEC.md`, which is frozen in
  place with a `POINTER.md`. **The location itself was a finding**: Jon, verbatim, at the reconcile
  — *"this is a message in the exchange that can't be where something as important as final specs
  should be... I dont see enough cited in it... poor final location regardless for a PR."*
- **Code:** `skills/memory-core/scripts/{write_barrier_memory.py,consolidate_memory.py,adopt_memory_core.py}`
- **Runtime store (CFL v0-transitional binding):** `exchange/memory-core-v0/instances/`
- **Operating discipline:** `skills/memory-core/SKILL.md`

## The schema, in brief

Each instance carries: `id` (`MEM-<YYYY-MM-DD>-<session8>-<suffix>`, suffix ∈
`{compact,close,branch-<lane>,foldin-<lane>}`), `barrier` (enum: `compact|close|branch-dispatch|fold-in`,
must equal the filename suffix class), `as-of` (full ISO-8601, never self-clocked), `git-head`
(40-hex or an explicit `UNKNOWN` string), and a `STATUS: SKELETON` body stamp that is **required**
whenever any `<placeholder>` remains — removed only by hand, once every prompt is filled
(`skills/memory-core/references/SPEC.md:152-162`).

## The verify gate — real, and for 16 days it was not wired

`write_barrier_memory.py` has always defined `verify_instance()`, a real validator with a
`required_sections` list per barrier. **Until 2026-08-23 it was called only from `--selftest`.** A
real write ran `instantiate()`, emitted a template full of `<placeholders>`, printed *"NEXT: fill
the template prompt sections in that file,"* and never returned to check anyone did
(`wiki/tracker/SEAL-unsaid-ledger-mechanism-2026-08-23.md:17-22`).

That produced the specific failure PR-1's promise 12 (every boundary writes an unsaid ledger)
graded VERIFIED against, on a file count: **counted across the store, 27 matched instances, 11
filled, 16 unfilled skeletons — including all three `close` instances and 3 of 4 `compact`**
(`wiki/tracker/SEAL-unsaid-ledger-mechanism-2026-08-23.md:95-101`). The unsaid ledger — a section
of the record meant to hold what a boundary self-critique found unsaid — **had produced zero
artifacts across all 28 barrier instances, at any point, ever**, because the records that would
carry it were never filled.

**The fix, sealed and graded 2026-08-23** (`wiki/tracker/SEAL-unsaid-ledger-mechanism-2026-08-23.md`):
`--verify` now checks a real instance and FAILS a skeleton, FAILS a heading-with-placeholder-content
(the standing lesson: "write criteria against the bytes the consumer receives" — a heading-only
check would have been satisfied by the empty template itself), and PASSES a genuinely filled
record. It applies to `compact` and `close` only (branch-dispatch/fold-in are lane artifacts, not
boundary self-critique). **It is a script gate the ritual invokes explicitly, not a hook** — Jon's
promise 9 ("nothing is automatic until PR-3") stays intact; "a tool refusing to certify its own
incomplete output is not automation; it is the tool being correct."

A second defect surfaced by the same seal: two template directories exist
(`exchange/memory-core-v0/TEMPLATES/`, the legacy copy, vs. the official
`skills/memory-core/TEMPLATES/` rehomed 2026-08-22) and had **silently diverged**; a `--root`-less
run resolves to neither and falls through to the script-relative fallback, contradicting the
resolver's own comment. Not fixed — flagged as a live federation-portability surface deserving its
own probe; both copies were patched identically in the meantime so they cannot diverge further.

## Where this sits in PR-1's retrospective

Promise 5 ("every barrier writes its record") was **downgraded from VERIFIED to PARTIAL** once a
lane built the thing that actually reads the records, rather than counting files
(`wiki/tracker/wayfinder-pr2-2026-08-23.md:229-236`). See [[disposition-and-delivered-is-not-received]]
for the general pattern this is one instance of.

## Not yet built

- No hook wiring (deliberate, per promise 9 — PR-3 territory).
- No consolidation enforcement — `consolidate_memory.py` exists but consolidation is described as
  "ritual text, not enforced mechanism" as of the 2026-08-23 retrospective.
- The template-resolution defect above (root-derived candidates never reach template lookup).

## See also

- [[probe-registry]] — the mechanism that keeps this page from going stale the way `wiki/concepts`
  itself did for 16 days.
- [[disposition-and-delivered-is-not-received]] — the parent defect class this promise-5 downgrade
  is one instance of.
