---
title: "Wiki-Master Standard Update (capture-only, born-at-standard v4.0) — zero new sessions, the false-REFRESH finding"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 8 vs corpus 3 on authored labels"
date: 2026-07-13
date_updated: 2026-07-17
type: session
source_kind: session
uuid: 96e1c2
domain: infrastructure
tags: [wiki-master, standard-update, detection, false-refresh, count-gate, born-at-standard-v4, drive-lag, collision-check]
aliases:
  - "the 07-13 standard update"
  - "false-REFRESH finding"
  - "mtime is not a growth signal"
  - "the SU that was missed by its own count gate"
retrieval_key: wiki-master-su-capture-only-2026-07-13-96e1c2
source_file: raw/transcripts/claude-code/fl/code-2026-07-13-96e1c2-update-wiki-standard-to-v40-with-audit-metadata.md
generated_by: claude-opus-4-8/claude-code
liveness: CLOSED
coverage_through: 2026-07-13T17:40:00Z
audit_state: unaudited
---

# Wiki-Master Standard Update — capture-only (2026-07-13)

Scoped, capture-only standard update run on Opus against born-at-standard v4.0. Ingested on
**2026-07-17**, four days late — see Conflicts.

## Summary

A tightly-scoped SU whose ingest scope turned out to be **empty**: zero genuinely-new CC sessions, every
one of the 16 discovered sessions dispositioned against git-authoritative evidence. Its real deliverable
was a **tooling finding** — the `--update` mtime heuristic produces false REFRESH signals — established by
checking last-turn timestamps rather than trusting the flag. The session also caught a live collision
risk, correctly identified its own aborted Sonnet predecessor, and shipped draft PR #22. It is a good
example of an SU that produced value by proving there was nothing to do, and it is the strongest evidence
for two structural defects it did not itself recognize: it was **missed by its own count gate**, and it
**saw the misrouted intake pile and called it debris**.

## Key Claims

- Jon's brief scoped the run to capture-only on Opus, born-at-standard v4.0, with explicit exclusions:
  don't touch the 183-page audit backlog / conformance ledger / `wiki-audit-*` branches (a concurrent
  audit owns them); defer the Anthropic zip batch; **"da51cc is OPEN — do not extract it"**; work on branch
  `wiki-standard-update-nap-2026-07-13`, draft PR, do not merge ([96e1c2:T7]).
- **Zero genuinely-new CC sessions to ingest.** All 16 discovered sessions were dispositioned with verified
  evidence; the 07-12 SU (da51cc) had already swept the CC backlog ([96e1c2:T44]).
- **`md✓`/`md✗` is not a capture signal** — disposition was taken from git-authoritative wiki footprint
  instead, per the standing lesson ([96e1c2:T18]).
- **The `--update` mtime heuristic produces false REFRESH signals.** `5bfcff` and `efd6a3` looked grown but
  **had zero turns after 2026-07-12** — the mtime bump was a filesystem touch, not new content. The real
  check is the last-turn timestamp ([96e1c2:T38]).
- Ratio-based `[REFRESH]` flags are mostly false positives: **tool-heavy CC sessions legitimately compress**,
  so a low MD/JSONL size ratio is not evidence of truncation ([96e1c2:T34]).
- **Collision check performed and resolved:** `1c802a` was running the same brief verbatim, started 5
  minutes earlier, on the same branch. It was **this session's aborted predecessor** — ran on
  `claude-sonnet-5` though the brief demanded Opus, did setup only, made **zero writes and zero commits**,
  and died at 17:25:04 when Jon `/clear`'d and switched to Opus. Not the concurrent audit ([96e1c2:T30]).
- The count gate showed **N=10 pending claude.ai sessions** (the deferred zip batch) and a **new zip
  `1783821969`** past the watermark — both deferred-and-noted per the brief ([96e1c2:T34]).
- The count gate was **grounded, not trusted**: every capture page the previous SU's log claimed to exist
  was verified present in git ([96e1c2:T42]).
- The drive-lag hazard was actively honored: working-tree `log.md` was confirmed against git HEAD **before**
  appending ([96e1c2:T54]).
- Draft PR #22 opened; the finding was filed by **extending** the existing detection intake proposal and
  the existing memory rather than creating duplicates ([96e1c2:T58]).

## Conflicts

1. ⚠️ **CONFLICT — this SU was missed by its own count gate.** `96e1c2` ran the CC completeness check,
   correctly identified that only `1c802a` and **itself** had zero wiki footprint, wrote a skip row for
   `1c802a` — and then wrote no page, no stub, and no skip row **for itself**. It was ingested 4 days later
   by the 2026-07-17 SU. The gate enumerates sessions; the session running the gate is not in its own
   enumeration. *(Resolution: skills-master — the completeness gate must include the running session.)*

2. ⚠️ **CONFLICT — `wiki/intake-triage/` was seen here and classified as "debris."** This session recorded:
   *"Committing only my own files — the untracked `reports/`, `scripts/migrations/`, `wiki/intake-triage/`
   debris isn't mine to commit."* The role discipline was **correct** (an SU must not commit another
   agent's files). The defect is that it **classified without inspecting and did not escalate**: the
   directory held packets explicitly addressed `to: [wiki-master]` and marked `status: UNREVIEWED`. P1
   independently re-found it on 2026-07-15 ("8 untracked intake files sat inside `wiki/`, invisible to
   git"); by 2026-07-17 it held **12** files. Seen twice, left twice. *(See the 2026-07-17 SU log.)*

3. ⚠️ **CONFLICT — "da51cc is OPEN — do not extract it" (Jon's brief, [96e1c2:T7]) vs. the measured
   outcome.** The instruction was **reasonable on 07-13**: da51cc was live and actively being worked, and
   extracting a moving target mid-flight is a real hazard. The defect is that a sound one-day instruction
   became a **standing default** nobody revisited. Between 07-12 and 07-17 da51cc grew **+187%**, and
   **1,388 messages / ~980,000 chars (74% of its char mass)** accumulated in no wiki page. *(Resolution:
   `skills/intake/ready/live-session-liveness-policy-2026-07-17` — a live session is re-snapshotted on any
   delta at every SU, with a coverage watermark; "open" stops meaning "skip.")*

4. ⚠️ **CONFLICT — the branch this SU created still owns the main checkout.** The brief said to work on
   `wiki-standard-update-nap-2026-07-13`, which was created **in the main checkout** rather than a
   worktree, and never switched back. As of 2026-07-17 the main checkout is **still parked on that
   branch**, which is the mechanism poisoning claude.ai's cold reads off the Drive folder. The fix (B1,
   `git checkout main && git pull --ff-only`) is Jon's hand. *(See [[drive-worktree-mirror-poisoning]].)*

## Entities & Concepts

- [[md-not-uncaptured-authoritative-disposition]] — `md✗` is not a capture signal; `--update` mtime/size is not a growth signal
- [[drive-lag-stale-read-hazard]] — honored here: working tree confirmed against git HEAD before append
- [[drive-worktree-mirror-poisoning]] — the nap branch left on the main checkout is the live instance
- born-at-standard v4.0 — `source_kind`, turn anchors, fidelity tags, findability, fixity, `uncaptured_assessed`
- count gate — the exhaustive N-file disposition check; **does not include the running session**
- `scripts/audit/turn_index.py`, `lint.py` — the deterministic spine this brief mandated
- 1c802a — aborted Sonnet predecessor of this session; skip row written
- PR #22 — the draft PR this session shipped

## Uncaptured Content

**a) Unfollowed threads.** The new zip `1783821969` was noted-and-deferred per brief and **remained
un-ingested as of 2026-07-17** — the claude.ai sessions from 07-12 onward are in no export yet. The "N=10
pending" claude.ai sessions were labeled *pending* while all ten already had wiki pages; the SU deferred
them per brief rather than re-dispositioning, so the mislabel was carried forward into the log and
re-read as a backlog by the next SU.

**b) Dissolved tensions.** The collision scare with `1c802a` resolved cleanly to "aborted predecessor" and
was not developed into a general concurrency convention, though two same-brief sessions on one branch is
exactly the hazard [[wiki-master-concurrency-gap]] describes.

**c) Absent technical details.** The specific edits to the detection intake proposal and to memory are
referenced but not reproduced. PR #22's diff is not summarized here.

**d) Epistemic gaps.** This page was written from the extracted MD on 2026-07-17, not from the live
session. The MD's 26 thinking blocks are **encrypted-in-signature and unrecoverable**, so the reasoning
behind the false-REFRESH diagnosis survives only as its visible narration.
