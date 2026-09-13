---
title: "Records map — what gets written WHEN, by WHAT, verified HOW"
kind: reference
status: LIVE
born: 2026-08-29
session: "post-compact lane of 9041f3b0"
model: sonnet
ticket: "sitting docket row 9, due 2026-09-03"
directive: >
  Jon, verbatim: "How does this not link to wiki concepts or skills and more and how does this
  not link to like our data definitions and standards and more? Like WHAT records get written
  WHEN? … the *foundation* glossery on these skills which are the only ways I directly update
  the wiki anymore - their criticality - is not clear from here."
seeds:
  - wiki/tracker/wayfinder-do-better-2026-08-29.md (DB-1 ticket)
  - wiki/intake-triage/RESEARCH-DB-1-discipline-census-2026-08-29.md (26-row census, 2026-08-29)
  - skills/memory-core/references/SPEC.md
  - .claude/hooks/
  - skills/ (/su, /su-compact, /wake definitions)
  - exchange/su-close/, exchange/memory-core-v0/
links: "[[memory-core]] [[unsaid-ledger]] [[probe-registry]] [[repo-hygiene]] [[ai-mechanics]]"
---

# Records map — what gets written WHEN, by WHAT, verified HOW

## Why this page exists

Jon's complaint on the standard-update glossary entry, verbatim (quoted in frontmatter): the
skills that write the wiki are "the only ways I directly update the wiki anymore" and their
**criticality is not clear** — the glossary named the skills without saying what record each
one produces, when it fires, or whether a wiki concept page even documents the record type.
This page is the table he asked for. It does not invent new discipline; it inherits DB-1's
26-row census (`wiki/intake-triage/RESEARCH-DB-1-discipline-census-2026-08-29.md`,
2026-08-29) verbatim for source/trigger/enforcement, and adds one column DB-1 did not carry:
**does a wiki concept page link to this record type — YES with path, or NO.**

**The NO column is Jon's exact complaint, made checkable.** Of 26 record types, **19 have no
wiki-concept link** — see Counts below.

**Method for the new column:** `grep -ril` against `wiki/index.md` and `wiki/concepts/*.md`
for the record's file path, script name, or the discipline's own vocabulary (e.g. "unsaid
ledger", "TERMINAL", "positional"). A hit that only lists a script name in passing (no
paragraph explaining the discipline) is marked YES-thin and flagged. Commands are listed at
the bottom, same discipline as DB-1's own Methods section.

## Table

| # | Record type | Written WHEN (barrier/ritual) | Written BY (skill/script/hook) | Verified HOW (what proves it happened) | Wiki concept link |
|---|---|---|---|---|---|
| 1 | WWJA pass record | before anything Jon-facing ships | `skills/probe-registry/references/WWJA.md`; logged as a row in `exchange/WORK-CLAIMS.md` | heartbeat-check: `heartbeat_battery.py` `check_wwja` (check 1) | **NO** — no `wiki/concepts/*.md` or `wiki/index.md` hit for "WWJA" |
| 2 | Seal file (expectations, written before a test runs) | every sealed test, before execution | `skills/probe-registry/SKILL.md` ("write a seal file first"); files under `wiki/tracker/SEAL-*.md` | prose-only — nothing checks a seal predates its run | YES — `wiki/concepts/probe-registry.md` |
| 3 | Probe registry row (append-only, failures kept) | every probe run | `skills/probe-registry/SKILL.md`; `wiki/tracker/PROBE-REGISTRY.md` | heartbeat-check: `check_probe_regressions` (check 6) | YES — `wiki/concepts/probe-registry.md` |
| 4 | Barrier memory instance — compact | compact | `skills/memory-core/references/SPEC.md`; `write_barrier_memory.py`; lands in `exchange/memory-core-v0/instances/` | tool-refuses: `write_barrier_memory.py --verify` + heartbeat-check `check_barrier_coverage` (check 9) | YES — `wiki/concepts/memory-core.md` |
| 5 | Barrier memory instance — close | close | same script/spec | same | YES — `wiki/concepts/memory-core.md` |
| 6 | Barrier memory instance — branch-dispatch | dispatch (forking a lane) | same script/spec, requires `expects{deliverable, verify_by, reunion}` | same | YES — `wiki/concepts/memory-core.md` |
| 7 | Barrier memory instance — fold-in | a lane's return | same script/spec, requires `snapshot_ref` | same | YES — `wiki/concepts/memory-core.md` |
| 8 | Unsaid ledger row (filled, real deficiency row) | compact / close (boundary barriers, `strict=True`) | `write_barrier_memory.py` `unsaid_ledger_failures()` | tool-refuses: `verify_instance(strict=True)` | YES — `wiki/concepts/unsaid-ledger.md` |
| 9 | Consolidation pass record (near-duplicate memory merge) | every close | `skills/memory-core/references/SPEC.md`; `consolidate_memory.py` | prose-only — no check verifies the consolidation script actually ran, only that a record exists | YES — `wiki/concepts/memory-core.md` (mentions consolidation) |
| 10 | Template-eval log row | new instance of a template | `skills/memory-core/references/SPEC.md`; `skills/memory-core/references/template-eval-log.md` | prose-only — nothing forces a row per instance | **NO** |
| 11 | Tier-0 index row | every barrier | `skills/memory-core/references/SPEC.md`; `exchange/memory-core-v0/INDEX-tier0.md` | prose-only — no heartbeat check reads this file's freshness against the instances directory | **NO** |
| 12 | Read-receipt stamp on peer letters | every letter, both directions | `exchange/personal-channel-log-2026-08-03.md` convention | prose-only — no script checks the ledger is fed; stopped being fed 2026-08-06 | **NO** |
| 13 | Exchange-read confirmation at session open | session open | `.claude/commands/wake.md` ("Peer mail, BOTH directions") | heartbeat-check: `check_inbox_new` (check 5) | **NO** — general "session open" concept pages exist but none documents this specific rule |
| 14 | WORK-CLAIMS TAKE/DONE row | dispatch (TAKE) / completion (DONE) | `exchange/WORK-CLAIMS.md` convention | heartbeat-check: `check_open_takes` (check 4) | YES — `wiki/concepts/memory-core.md` |
| 15 | WORK-CLAIMS append-only guarantee | every row write | same file, `>>` convention | prose-only — no script diffs the file against git history to detect a rewritten row | YES-thin — same page as #14, append-only rule itself not separately explained |
| 16 | ROUTING-LEDGER TERMINAL gate | agent standing down (self-routed at return) | `exchange/ROUTING-LEDGER.md`; `scripts/audit/route_agent_return.py` | tool-refuses: `TERMINAL_TOKEN` check, refuses further rows for that id6 | YES — `wiki/concepts/ai-mechanics.md` |
| 17 | ROUTING-LEDGER no-positional-reference rule | every row write | `exchange/ROUTING-LEDGER.md` convention (name antecedent by id6 + closed_utc) | prose-only — measured once by a one-off audit (`wiki/references/ledger-positional-defects-2026-08-06.md`), no standing re-check | **NO** — pages that mention ROUTING-LEDGER (`de-pii-deriver.md`, `disposition-rate.md`) do not cover the positional-reference rule itself |
| 18 | Canonical branch regeneration | every standard update | `CLAUDE.md`; `scripts/lanes/regenerate_canonical.sh` | mixed: tool-refuses for the excluded-path safety gate (exit 3/4 fail-closed); prose-only for whether an SU invoked the script at all — no check compares canonical's age to main HEAD | YES — `wiki/concepts/repo-hygiene.md` (covers the gate; does not cover the missing age-check) |
| 19 | PreCompact hook record (SU state + session-store reconcile) | compact (manual or auto) | `.claude/settings.json` `PreCompact` block → `pre-compact-su.sh` → `session_store_capture.py --reconcile` | heartbeat-check: `check_hook_liveness` (check 3), WARNs if 0 hookEvent records this session | **NO** |
| 20 | M-14 look-before-building check output | dispatch, before TAKE | `scripts/audit/check_before_dispatch.py` | prose-only — script exists and answers the question, but nothing forces it to run before a TAKE row lands | **NO** |
| 21 | Reachability-chain check output | session open | `.claude/commands/wake.md`; `check_reachability_chain.py` | prose-only — confirmed NOT wired into `heartbeat_battery.py` | **NO** |
| 22 | Mid-turn message scan output | session open | `.claude/commands/wake.md`; `scan_midturn_messages.py` | prose-only — confirmed NOT wired into `heartbeat_battery.py` | YES-thin — `wiki/concepts/mirror-consult-economics.md` lists the script name in a tool inventory, does not explain the discipline |
| 23 | Frozen-branch discipline record | close / any barrier check run | `scripts/audit/heartbeat_battery.py` `check_frozen_branch` (check 8) | heartbeat-check | **NO** |
| 24 | Tree-dirty discipline record | close | `scripts/audit/heartbeat_battery.py` `check_tree_dirty` (check 7) | heartbeat-check | **NO** |
| 25 | Corpus watermark record | close | `scripts/audit/heartbeat_battery.py` `check_corpus_watermark` (check 12), WARN ≥7 days stale | heartbeat-check | **NO** |
| 26 | CRLF boot-surface scan record | before ship (Docker build) | `scripts/audit/heartbeat_battery.py` `check_crlf_boot_surface` (check 11) | heartbeat-check | **NO** |

## Counts

- **26 record types mapped** (inherited 1:1 from DB-1's census rows — this page adds only the
  wiki-concept-link column; it does not re-derive source/trigger/enforcement).
- **Wiki-concept link: YES (substantive) — 11** rows: 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 18.
- **Wiki-concept link: YES-thin (name-only mention, no explanation of the discipline) — 2**
  rows: 15, 22.
- **Wiki-concept link: NO — 13** rows: 1, 10, 11, 12, 13, 17, 19, 20, 21, 23, 24, 25, 26.

  Check: 11 + 2 + 13 = 26. ✓

  **This is Jon's exact complaint, made checkable.** Folding YES-thin into NO (a bare
  script-name mention inside another page's tool inventory does not tell a reader the
  discipline exists or why it matters — Jon's own words, "their criticality is not clear from
  here") gives **15 of 26 record types with no real wiki-concept coverage.** Strict-NO alone
  is 13.

- **By enforcement class, among the 15 NO-or-thin rows:**
  - **Enforced (heartbeat-check) but wiki-silent** — the mechanism runs and would WARN, but
    no concept page tells a reader it exists: rows 1, 13, 19, 23, 24, 25, 26 (**7 rows**).
  - **Prose-only AND wiki-silent — the worst compounding, no check and no documentation:**
    rows 10, 11, 12, 15 (thin), 17, 20, 21, 22 (thin) (**8 rows**).
  - 7 + 8 = 15. ✓

## The single most critical unlinked record: WWJA (row 1)

**WWJA — "Working With Jon's Approval"/pre-Jon-facing-ship pass — is the single most critical
unlinked record type**, for three compounding reasons, not one:

1. **It is enforced** (heartbeat-check, `check_wwja`) — this is not a dead rule; the mechanism
   is live and was the exact rule that caught real defects late on PR-252 (295→297, missing
   3-PR scope line) per `wiki/tracker/wayfinder-do-better-2026-08-29.md` item 1, on 2026-08-29.
2. **It gates every artifact that reaches Jon** — by the rule's own text ("before anything
   ships to Jon"), it is the widest-scope gate in this census: every PR body, every letter,
   every sitting page that is Jon-facing.
3. **It has zero wiki-concept presence.** `grep -ril "WWJA" wiki/index.md wiki/concepts/*.md`
   returns nothing. A reader of the wiki — including Jon, reading his own glossary — cannot
   discover that this gate exists, what it checks, or that it was the mechanism that caught
   the PR-252 defects, anywhere in the concept layer. The only place WWJA is documented is
   `skills/probe-registry/references/WWJA.md` itself and this DB-1/records-map pairing.

**Recommended next step (not executed by this lane — DB-2/skills-master scope):** a
`wiki/concepts/wwja.md` page, minimum viable: what it checks, when it fires, the PR-252
catch as worked evidence, and a link back to `skills/probe-registry/references/WWJA.md`.

## What this page does NOT do

- Does not re-verify DB-1's enforcement-class claims — inherited verbatim, with DB-1's own
  honest bounds (it did not run the heartbeat battery live; several "last verifiably ran"
  cells are UNKNOWN) carried forward unchanged.
- Does not propose which lever (tool-refuses / heartbeat-check / demotion) each prose-only row
  should get — that is DB-2's charter, not this page's.
- Does not write the missing concept pages — flagged as a forward commitment below, not done
  here.

## Forward commitments

| item | oracle | owner | date |
|---|---|---|---|
| Write `wiki/concepts/wwja.md` (the single most critical unlinked record) | this page's own Table + Counts section, re-grepped for "WWJA" returning a hit | wiki-master (skills-master co-sign on WWJA.md content accuracy) | 2026-09-03 (docket due date) |
| Resolve the remaining 12 NO/thin rows (2, 10, 11, 12, 13, 15, 17, 19, 20, 21, 23–26) into either a concept-page stub or an explicit "not concept-worthy, tracked in skill/script docs only" disposition | this page's Table, re-walked row by row | wiki-master | with DB-2 (no fixed date set by this lane) |
| Re-verify this page's own counts against a fresh `grep -ril` pass (the Counts section corrected one arithmetic slip in-line; a second independent count would confirm 9 YES / 2 YES-thin / 13 NO / 2 thin = 26) | `grep -ril` commands below, re-run | any lane, cold | before this page is cited as authoritative in a Jon-facing artifact |

## Methods (commands run)

```
grep -rl "WWJA" wiki/index.md wiki/concepts/*.md
grep -ril "unsaid.ledger" wiki/index.md wiki/concepts/*.md
grep -ril "read.receipt" wiki/index.md wiki/concepts/*.md
grep -ril "canonical branch\|regenerate_canonical" wiki/index.md wiki/concepts/*.md
grep -ril "heartbeat_battery\|heartbeat battery" wiki/index.md wiki/concepts/*.md
grep -ril "PreCompact\|pre-compact-su" wiki/index.md wiki/concepts/*.md
grep -ril "TERMINAL" wiki/index.md wiki/concepts/*.md
grep -il "consolidat" wiki/concepts/memory-core.md
grep -il "tier.0" wiki/concepts/*.md wiki/index.md
grep -n "positional" wiki/concepts/de-pii-deriver.md wiki/concepts/disposition-rate.md wiki/concepts/ai-mechanics.md
grep -rl "M-14" wiki/concepts/*.md wiki/index.md
grep -n "scan_midturn\|mid-turn" wiki/concepts/mirror-consult-economics.md
ls wiki/concepts/
```
