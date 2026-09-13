---
title: Agent-memory drain — index and admission criterion
aliases: ["the brain drain", "poor memory", "memory files"]
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: sub-branch too close to call: wiki 3 vs fleet 3 (margin < 1)"
source_kind: reference
maintained_by: wiki-master skill (pilot: 2026-08-06 T-02; continuation: 2026-08-06 same-day, "poor
  memory" destination ticket)
status: DRAIN COMPLETE — 50 of 50 CFL agent-memory files drained. 46 in the original main pass;
  the remaining 4 were adjudicated by fable-mirror under Jon's 2026-08-06 D12 grant ("treat
  mirror as authorization, period") and drained 2026-08-06 — 2 to this published surface, 2 into
  `wiki/personal/` (in the wiki, off the connector). See the "Final 4" section below; full ruling
  at `wiki/intake-triage/MIRROR-RULING-conservatism-vs-canonical-exclusion-2026-08-06.md`. Source
  store still has 50 files on disk, untouched (NO DESTRUCTIVE ACTS).
ratification: Jon, 2026-08-02, `wiki/intake-triage/jon-ruling-memory-drain-and-personal-reunion-2026-08-02.md:12-17` —
  "We need to enact a brain drain that we've planned for. All memories get into the wiki as reference
  material related to conversations. ... They would be untraced files as they are static. You planned
  this, personal project implemented this out of necesity."
ticket: exchange/RATIFIED-BUT-UNAPPLIED-2026-08-05.md, T-02
destination: Jon, 2026-08-05 23:09:13 CDT — "make it so no memory files are actually needed because
  everything makes it into the wiki"
continuation_note: Jon, 2026-08-06 — "You have such poor memory. Fixing that is required to assist
  me." Approved wholesale, build-not-plan. This pass finished the drain the pilot deferred, built the
  citation-coverage exclusion class the pilot named and skipped, and built the retrieval-side checks
  (reachability chain, unapplied-ruling finder, index-store parity) the pilot didn't attempt at all.
---

# Agent-memory drain — index and admission criterion

## What this is

CFL's Claude Code agent keeps a per-project memory store outside git — one markdown file per
learned fact, at `C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\`.
That store is real, current, and untracked: it cannot be cited, cannot be read by another agent or
by Jon without opening a local path, and does not survive a memory-store reset or a launch from the
wrong directory (see [[cfl-memory-store-split-by-cwd]] on that last point specifically).

Jon's destination is to make the memory store **redundant** — every fact worth keeping lives in
`wiki/` instead, where it is citable, git-tracked, and readable by anyone with repo access. This
directory is the landing zone for that content. **This page and its ten siblings are the first
pilot batch, not the completed drain.**

## Admission criterion — what stays out, and why

A memory file is **excluded** from the drain if it fails **any** of the three tests below. All three
are needed because they catch different failure shapes; passing two out of three is not enough.

**1. Identity test.** Exclude if the item's subject is the agent's own self-model, the `self/`
directory, 02-CF consciousness-framework internals, or a topic the wayfinder map has explicitly
fenced as identity-adjacent — matching `feedback_identity-fence-purpose-based` in the source store,
itself a description of that fence and therefore self-referential to it. `wiki/` republishes to the
`canonical` branch (see below); identity content needs a decision only Jon can safely make, on a
surface he controls directly, before it is exposed there. **When in doubt, exclude and route to
Jon rather than judge it yourself** — this test is conservative by design.

**2. Project-vs-tooling test.** Include only if the item's substance is a fact, decision, or lesson
**about a CFL/FL project artifact, process, or Jon ruling** — not a generic operational note about
how the Claude Code harness or shell environment behaves in the abstract, detached from any project
consequence. A tooling fact with a project consequence still passes (e.g. "CC session retention
deletes JSONLs after `cleanupPeriodDays`" is a Claude Code setting, but its consequence is *CFL's own
corpus* — include). A tooling fact with no traceable project decision or loss attached to it does
not (e.g. a bare PowerShell here-string syntax note with no incident behind it — exclude, it belongs
in a skill or a script comment, not the project record).

**3. Publication-safety test.** Nothing that would be inappropriate on a page replicated to the
`canonical` branch. `wiki/` — **`wiki/intake-triage/` included** — is republished there
(`CLAUDE.md`, "Repo Hygiene" section), so anything landing in `wiki/references/` is public-facing
within Jon's own systems the moment it merges. Exclude anything naming family members, health,
finances, or any content Jon has marked identity-only, even if the framing looks anodyne. This is a
harder bar than "would embarrass no one" — it is "would Jon be surprised to find this on a surface
he didn't personally gate."

**The citation-coverage exclusion class — built 2026-08-06, this pass.** Every page drained by this
program declares `coverage_class: untraced-by-design` plus a required `coverage_class_reason:` in
its own frontmatter. `scripts/lint_citation_coverage.py` reads that field at scan time and drops the
page's claims from M1-M5 entirely — not "excused," genuinely never counted, so a 49-page drain can
never inflate or deflate the E2 coverage numbers. The exclusion is **frontmatter-driven, not
path-driven**: a page's directory grants it nothing; only the declared field does, so a real
session/reference/analysis page landing in this directory by mistake would not silently inherit the
exemption. Self-tested (`--selftest`, group 11: builds a throwaway fixture tree, proves an exempt
page is dropped from `scan()` and from `M1`'s denominator). A page excluded from the drain (see
"Excluded" table below) still needs its own reason on record — that rule applies to lint exemptions
too, not only to admission exclusions, and this script now warns if an exempt page has an empty
`coverage_class_reason`.

## What was moved — main pass (46 of 50)

| Memory file | Wiki page |
|---|---|
| `feedback_architecture-changes-require-permission.md` | [[architecture-changes-require-permission]] |
| `project_askuserquestion-answers-not-captured.md` | [[askuserquestion-answers-not-captured]] |
| `reference_cc-jsonl-thinking-signature-only.md` | [[cc-jsonl-thinking-signature-only]] |
| `project_cc-retention-cleanupperioddays.md` | [[cc-retention-cleanupperioddays]] |
| `project_cfl-launcher-git-pull-collision.md` | [[cfl-launcher-git-pull-collision]] |
| `project_cfl-memory-store-split-by-cwd.md` | [[cfl-memory-store-split-by-cwd]] |
| `feedback_checkpoint-model.md` | [[checkpoint-model]] |
| `feedback_coordinator-dispatches-never-adopts.md` | [[coordinator-dispatches-never-adopts]] |
| `project_corpus-path-divergence.md` | [[corpus-path-divergence]] |
| `feedback_decision-grain-one-clause-per-pr.md` | [[decision-grain-one-clause-per-pr]] |
| `feedback_decision-scope-calibration.md` | [[decision-scope-calibration]] |
| `feedback_deploy-phase-operating-protocol.md` | [[deploy-phase-operating-protocol]] |
| `feedback_derive-dont-record.md` | [[derive-dont-record]] |
| `project_docker-two-mode-architecture.md` | [[docker-two-mode-architecture]] |
| `feedback_drive-lag-stale-read-hazard.md` | [[drive-lag-stale-read-hazard]] |
| `reference_drive-worktree-mirror-poisoning.md` | [[drive-worktree-mirror-poisoning]] |
| `feedback_dual-relevance-wiki-routing.md` | [[dual-relevance-wiki-routing]] |
| `feedback_fbc-format-gap.md` | [[fbc-format-gap]] |
| `feedback_flagged-unknowns-are-work.md` | [[flagged-unknowns-are-work]] |
| `feedback_gmail-messaging-standards.md` | [[gmail-messaging-standards]] |
| `feedback_hedge-flattening-and-invented-rulings.md` | [[hedge-flattening-and-invented-rulings]] |
| `feedback_live-session-liveness-and-untracked-state.md` | [[live-session-liveness-and-untracked-state]] |
| `project_loop-taxonomy.md` | [[loop-taxonomy]] |
| `feedback_max-plan-fl-budget.md` | [[max-plan-fl-budget]] |
| `feedback_md-not-uncaptured-authoritative-disposition.md` | [[md-not-uncaptured-authoritative-disposition]] |
| `feedback_memory-collection-acknowledgment.md` | [[memory-collection-acknowledgment]] |
| `feedback_migrations-blind-instruments.md` | [[migrations-blind-instruments]] |
| `feedback_mirror-before-jon.md` | [[mirror-before-jon]] |
| `feedback_mirror-stateless-dispatch-only.md` | [[mirror-stateless-dispatch-only]] |
| `project_nightly-lane-leg2-truncated-prompt.md` | [[nightly-lane-leg2-truncated-prompt]] |
| `feedback_no-public-clone-inside-private-tree.md` | [[no-public-clone-inside-private-tree]] |
| `project_open-architecture-questions.md` | [[open-architecture-questions]] |
| `project_planned-path-g1-g2-gate-order.md` | [[planned-path-g1-g2-gate-order]] |
| `project_pm-herald-skill-state.md` | [[pm-herald-skill-state]] |
| `feedback_questions-are-guidance-not-gaps.md` | [[questions-are-guidance-not-gaps]] |
| `project_session-close-2026-07-07-backlog-plan.md` | [[session-close-2026-07-07-backlog-plan]] |
| `project_skill-frontmatter-silent-autoinvoke-failure.md` | [[skill-frontmatter-silent-autoinvoke-failure]] |
| `feedback_stale-index-lock-recovery.md` | [[stale-index-lock-recovery]] |
| `feedback_subagent-stays-open-only-with-work.md` | [[subagent-stays-open-only-with-work]] |
| `project_t44-apollo-artemis-complete.md` | [[t44-apollo-artemis-complete]] |
| `feedback_ti-b-decision.md` | [[ti-b-decision]] |
| `feedback_unshipped-fix-updates-its-own-docs.md` | [[unshipped-fix-updates-its-own-docs]] |
| `feedback_verify-conditional-claim-resolution.md` | [[verify-conditional-claim-resolution]] |
| `feedback_verify-controls-before-declaring-loss.md` | [[verify-controls-before-declaring-loss]] |
| `feedback_wiki-master-concurrency-gap.md` | [[wiki-master-concurrency-gap]] |
| `feedback_windows-maxpath-worktree.md` | [[windows-maxpath-worktree]] |

**Source files are untouched.** No destructive act — per Jon's standing instruction, this program
proves and completes the route and removes nothing from
`C:\Users\JonSc\.claude\projects\...\memory\`. All 50 source `.md` files (plus `MEMORY.md`) remain
on disk exactly as before this pass.

## Final 4 — adjudicated and drained, 2026-08-06 (0 remain excluded)

The main pass above excluded 4 files pending judgment. **All 4 have since been drained.**
Fable-mirror adjudicated the set under Jon's D12 grant ("treat mirror as authorization, period")
— full ruling at `wiki/intake-triage/MIRROR-RULING-conservatism-vs-canonical-exclusion-2026-08-06.md`.
**Describing these four by category and filename only below — never by particulars** (see the
leak note further down for why that rule exists on this exact page).

| Memory file | Landing path | Category (never restate particulars) |
|---|---|---|
| `feedback_identity-fence-purpose-based.md` | **This surface** — [[identity-fence-purpose-based]] | Record of a Jon ruling, written as guidance to agents. Mirror ruled its purpose is not self-directed, so the identity fence it describes does not cover it. |
| `project_active-work-state.md` | **This surface** — [[active-work-state]] | Coordinator session-status log. Mirror ruled it fails no safety test and effort-to-transfer is not an accepted exclusion ground; drained verbatim. |
| `feedback_empower-out-of-jon-court.md` | **`wiki/personal/`** (non-published trunk) — [[empower-out-of-jon-court]] | Family + financial-institution content — Ruling-B class. |
| `project_backup-desktop-reorg.md` | **`wiki/personal/`** (non-published trunk) — [[backup-desktop-reorg]] | Personal financial/estate archive content including a credential-exposure finding — Ruling-B class, strongest member. |

**Net: 50 of 50 source files now drained. 0 permanently withheld.** 48 land on this
published surface; 2 land in `wiki/personal/` — in the wiki, off the `canonical` connector. The
mirror's governing rule: *"withholding-from-wiki and publishing-to-connector are both errors; the
trunk structure exists so that neither is ever necessary."*

> **⚠️ Leak note, kept for the record — these two cells leaked once, 2026-08-06.**
> Before this rewrite, the reason column for the two `wiki/personal/`-routed files described the
> withheld material with enough specificity — a family member's given name, a named financial
> institution, the nature and location of a credential finding — that **this page, which is
> published to `canonical`, partially republished the very categories the exclusion existed to
> keep off it.** **The note protecting the content leaked the content.** Caught by `fable-mirror`
> on adjudication, not by the author. **A reason column is on the same surface as everything else
> on the page** — describe the category, never the particulars. The table above and this note
> have been rewritten to hold to that rule.

## S3 anchor — resolved (partially) by this batch

`wiki/intake-triage/SEED-REGISTER-2026-08-03.md`, seed **S3** — "Memory-split by working directory is
the same defect class as the `wiki/` path deixis" — named a falsifier that remains untested by this
pass (*"Show Claude Code keys project memory by something other than the launch cwd"* — nobody has
shown this). What this pass **did** do: re-measured S3's underlying numbers fresh, 4 days after the
original 2026-08-02 measurement, and they hold —

```
$ ls .../projects/G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer/memory/*.md | wc -l
49  (48 memory pages + MEMORY.md; up from 47 recorded 2026-08-02 — 2 new pages added since)
$ ls .../projects/G--My-Drive-Claude-Claude-Foundational-Layer/memory/*.md | wc -l
20  (unchanged, stale, confirmed a distinct file set — not merged, per standing instruction)
$ ls .../projects/G--My-Drive-Claude-Claude-Personal/memory/*.md
(no files — confirmed empty, 2026-08-06)
```

**This is corroboration of the measurement, not a test of the falsifier**, and per the seed
register's own guard rule ("a falsifier may not be judged by its author") this pass does not
upgrade S3's status. See the seed register itself for the recorded update.

## What this pass proved, and what is deliberately NOT claimed

**Proved:** the route closes end-to-end at full scale, not just on a 10-file pilot. 46 of 50 memory
files, each individually judged against the 3-part admission criterion, land as citable
`wiki/references/` pages with their content intact, their sources named, nothing deleted from the
source store, and the citation-coverage instrument correctly exempting every one of them (46/46
carry `coverage_class: untraced-by-design` with a non-empty reason; `lint_citation_coverage.py`'s
own selftest proves the exemption is enforced, not just declared).

**What this does NOT claim:**
- It does not claim the drain makes the memory store itself unnecessary today — see the reachability
  and unapplied-ruling checks below, which test whether anything actually *reads* this material, not
  just whether it was written down. A fact drained into the wiki that nothing re-reads is the same
  failure this whole program exists to fix, one level up.
- It does not claim the 4 exclusions are permanent or beyond dispute — 3 are clean criterion
  failures (identity, publication-safety ×2); the 4th (`active-work-state`) is a recorded judgment
  call, not a test failure, and is flagged as revisitable.
- It does not claim page DEPTH matches the 10-page pilot batch. The pilot wrote long, heavily
  cross-referenced essay-style pages; this continuation's 36 pages are a closer-to-verbatim transform
  of the source memory (frontmatter added, prose otherwise preserved) to fit the time budget of a
  same-day completion. The source prose was already dense and well-cited in most cases — this is a
  legitimate scope tradeoff, not a quality claim that all 46 pages read identically.
