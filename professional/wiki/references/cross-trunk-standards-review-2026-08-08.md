---
title: Cross-Trunk Wiki Standards & Consistency Review
author: Claude Professional coordinator (592c3c16)
date: 2026-08-08
kind: reference
status: current
scope: read-only audit of the three live wikis (Professional, CFL, Personal); proposals only — no sibling tree was edited
---

# Cross-Trunk Wiki Standards & Consistency Review

**Requested by Jon, 2026-08-08:** a standards-consistency review, multiple fronts, "ground before
stating." Read-only. Findings for CFL and Personal travel to them by letter; the Professional fixes
are mine to make.

## Method & grading

- **[measured-here]** — I ran the command this session.
- **[relayed:CFL-audit]** / **[relayed:Personal-audit]** — a subagent ran it; commands were returned.
  Headline numbers were spot-verified at the primary (noted inline).
- Nothing below asserts a number I did not either run or verify.

> **⚠️ CORRECTION (2026-08-08, after Jon challenged the read).** An earlier version of this review
> called CFL's `intake-triage/agent-end/` "operational sprawl / machine-generated detritus." **That was
> a defect in my reading.** `agent-end/` is organized: root `README.md` + `INDEX.md`, an `INDEX.md` +
> `I2-SESSION.md` per subdir, per-subagent records named `code-DATE-<id>-<agent-type>-<task>.md` (a
> human can scan it and see what each agent did), and the raw jsonl correctly separated into
> `raw/transcripts/` (2,096 files), not duplicated here. It is the *branches-come-back-whole* discipline,
> indexed. **P2 is withdrawn; Front 3 is corrected below.** The Personal `intake-triage` drain question
> (178 staged / 3 promoted) still stands — it is backed by Personal's own index.

---

## The reframe, up front

**Most of what the request asks about is already solved — for two of the three trunks, and better
than the question assumes.** The bottleneck is not missing structure; it is (a) one trunk that never
adopted the standard, (b) undrained queues that have become the dominant mass, and (c) a set of
rules the disk quietly ignores.

- **CFL** runs a Jon-ratified *record-architecture-v1*: **frontmatter is the source of truth; folders
  are a "checked projection"** verified by an instrument (registry ⇌ frontmatter ⇌ folder). Its FL
  index is guarded by `index_counts.py --strict`. [relayed:CFL-audit]
- **Personal** enforces **thirteen checks** (`lint.sh` + `close-check.sh`), and each carries a
  `--selftest` proving it can actually fail — the exact anti-rot property the request wants. Its index
  reconciles 300/300 against disk. [relayed:Personal-audit]
- **Professional (this trunk)** has **no `SCHEMA.md`, no lint, and empty scaffolded `sources/` and
  `references/`.** It is the laggard. [measured-here]

So the honest answer to *"is most of that already solved?"* — for CFL and Personal, yes, and the
consistency machinery is sophisticated. The work is at the edges and in the newest trunk.

---

## Front 1 — Schema & the consistency machinery

| Trunk | SCHEMA | Enforcement | Verdict |
|---|---|---|---|
| CFL | present, ratified `record-architecture-v1` | `index_counts.py --strict` on the FL index | mature; some rules ahead of disk |
| Personal | present, v2.0-prototype (self-labelled "expects revision") | 13 checks, each `--selftest`-proven-failable | mature; the model for the others |
| Professional | **ABSENT** | none | **skeletal — the primary gap** |

**Finding:** the three trunks are at wildly different maturity. The standard-and-lint pattern exists
and works; Professional simply hasn't adopted it.

---

## Front 2 — Index vs disk reconciliation (the staleness defect)

- **CFL FL index: CLEAN** — sources 157/157, concepts 41/41, instrument-guarded. [relayed:CFL-audit]
  But the FL index carries **stale sub-wiki counts**: personal −7 (says 44, disk 51), home −4 (25 vs
  29), pro −3 (9 vs 12). Secondary copies drifted; the primary is guarded. [relayed:CFL-audit]
- **Personal index: CLEAN** — 300/300 at every level. [relayed:Personal-audit] Two internal caveats:
  the same file gives two unreconciled numbers for `intake-triage` (137 header vs 178 stats), and the
  freshness stamp says "updated 2026-08-08" over counts actually measured 2026-08-03 (`gen_index.py`
  unrun that pass). A recency claim 5 days stale. [relayed:Personal-audit]
- **Professional:** no generated index guard; small enough that it's currently accurate by hand.

**Finding:** the primary indexes are healthy. The defect is **stale secondary copies of a count** —
the FL index re-stating sub-wiki totals it doesn't own, Personal re-stating one folder two ways. This
is the gist's "a stale authority is worse than none" at small scale: a number re-stated where it
isn't generated will drift.

---

## Front 3 — Counts per folder, and the intake-triage rot (the biggest finding)

**In both large wikis the `intake-triage/` queue is the single dominant mass, and it is not draining.**

- **CFL:** `intake-triage/` = **350 .md** [measured-here]; of which `agent-end/` = **214 .md across 24
  hash-named subdirs** [measured-here]. **This is NOT rot (corrected — see banner above):** it is an
  organized, indexed capture of each subagent's work as human-readable `.md` records, with `README`/
  `INDEX` orientation and the raw jsonl correctly separated into `raw/`. The narrower, honest question
  is a *promotion/prune cadence*, below — not eviction.
- **Personal:** `intake-triage/` = **178** (137 + 41 archived), spanning 08-02→08-08, with **only 3
  ever promoted.** [relayed:Personal-audit] The classic deposit-only/undrained-queue shape the project
  constitution warns about — and `kind:` hygiene there is decaying (52/137 non-conforming to the
  "everything staged is `kind: source`" rule; some `kind:` values have become free-text prose).
  [relayed:Personal-audit]

**Finding — and it is pointed:** this is the exact failure the *record-method* gist is built around,
live in the wikis themselves. Two distinct sub-problems:
1. **Operational sprawl inside the knowledge tree** (CFL `agent-end/` 214 files). Session-end capture
   is not curated knowledge; it does not belong in `wiki/` at all.
2. **An undrained synthesis queue** (Personal 178 staged / 3 promoted). The consumer rule exists in
   the `intake` skill; it is not being run.

---

## Front 4 — Frontmatter, and the "OKF" question

- **Titles are near-universal** (0% missing in CFL sources/concepts; 5.5% missing in Personal). `type`
  /`kind` missing 6–17% depending on folder. [relayed, both]
- **CFL has a field-name-in-transition:** page-kind exists as both `type:` and `source_kind:`; 117/157
  FL sources lack `source_kind:`. Not a clean field. [relayed:CFL-audit]
- **AI-oriented vs human-readable split is real and deliberate.** Machine fields: `trunk, branch,
  sub_branch, branch_reason, retrieval_key, audit_state, source_jsonl, rests_on, staged_as, …`. Human
  fields: `title, date, status, origin`. The wikis optimize for machine navigation by design.

**OKF — resolved, ground-first:** there is **no frontmatter format named OKF anywhere** [measured-here,
12 CFL files + Personal grep]. "OKF" is an **undefined term of Jon's** — it appears in `goals.md` as
*"OKF style wiki"* and titles a session on *"full-conversation logging (OKF)."* CFL's own log records:
*"OKF resolved as far as evidence allows… the term is undefined in the corpus"* (inference offered:
"OpenWiki"; flagged as inference). **So "good OKF frontmatter" cannot be verified against the record —
the record has rich structured frontmatter, but nothing it calls OKF.** Per Jon's own principle
(*undefined terms are upstream of sprawl*), this is a define-it item, not something to assert. → **HITL.**

---

## Front 5 — Naming conventions (cross-trunk divergence + dead-letter rules)

Three different naming rules are in play, and no single one holds:

- The task-form convention `{topic}-YYYY-MM-DD-uuid6`.
- CFL's SCHEMA: `[role]-{topic}-YYYY-MM-DD-uuid6` with documented exemptions (reference/test files).
- **Personal's SCHEMA: kebab-case, human-readable, NO date, NO uuid in the filename** (date in
  frontmatter). [relayed:Personal-audit, verbatim SCHEMA:823]

Conformance: CFL 67.5% to the uuid6 pattern, but most deviations are schema-sanctioned or pre-UUID
(the real drift is ~38 date-only source pages). Personal: only 7/37 match the uuid6 form, and 21/37
**violate Personal's own schema** by embedding a date — the SCHEMA rule is effectively **dead letter**.
[relayed, both]

**Finding:** a rule the disk universally ignores is rot in the schema, not in the disk. Either the
rule is enforced by an instrument or it is retired. And the cross-trunk divergence (uuid6 vs
kebab-no-date) should be a *conscious* decision, not drift — different trunks may legitimately differ,
but nothing currently records that they chose to.

---

## Front 6 — Retired folders, archive duplication, sensitive-mirror asymmetry

- **CFL retired folders** (`analyses/ entities/ methodology/`) exist as **empty shells** — harmless but
  uncleaned. [relayed:CFL-audit] **CFL `archive/` genuinely duplicates live content:**
  `citation-audit-2026-05-26.md` and `project-map-audit-triage-2026-05-26.md` exist **both** in
  `archive/references/` **and** live in `sources/infrastructure/` [measured-here]; `archive/entities/jon.md`
  is a near-duplicate of `personal/jon.md`. A "move" that left a copy behind.
- **CFL `sessions/`** contradicts its own SCHEMA: the schema says it "holds only POINTER.md"; disk has
  `index.md` and no `POINTER.md`. [relayed:CFL-audit]
- **Personal `sensitive/` mirror is asymmetric and mostly scaffolding:** of 7 pages, **4 are `kind:
  pointer` redirect stubs (marked T1), only 2 are genuine T2 content.** Several mirror subfolders are
  empty `.gitkeep`. The mirror replicates `documents/sessions/voice` but omits `gmail/jon-messages/
  youtube`. [relayed:Personal-audit] (Structure only — no sensitive content read or reproduced.)
- **Personal `entities/` is active (6 pages)** — it did NOT follow CFL's retirement. Legitimate
  trunk divergence, but again unrecorded as a choice.

---

## Proposals — help-not-rot, reviewable, improvable

Ordered by value. Each is designed to be checkable by an instrument, not a discipline — because the
siblings already proved discipline doesn't survive and a check that can't fail is rot.

**P1 — Professional adopts the sibling pattern (MINE to do).** Write a `SCHEMA.md` for this trunk
modeled on Personal's, and a minimal lint with `--selftest`. Remove or fill the empty scaffolded
folders. Closes the maturity gap and is the single biggest consistency win. *Owner: me.*

**P2 — WITHDRAWN.** This proposed evicting `agent-end/` as "sprawl." On inspection it is organized,
indexed, human-readable, and correctly separated from the raw jsonl — Jon's challenge was right and the
finding was mine to retract. Any residual is the modest **promotion/prune-cadence** question (when does
a staged record graduate to `sources/` or age out?), which is CFL's design call, not a defect to route.

**P3 — Drain the synthesis queue, and add a mass check (both, by letter).** Run the `intake` consumer
rule that already exists (Personal: 178 staged / 3 promoted). Proposed reviewable metric: **a check
that fails when queue-mass exceeds knowledge-mass** — an undrained queue announces itself in the ratio.
*Route to CFL + Personal.*

**P4 — Kill or generate every stale secondary count (both).** The FL index should not re-state
sub-wiki totals it doesn't own (delete them, or generate them); Personal should reconcile its 137-vs-178
and stop stamping a fresh date over stale counts. Rule: **a number lives where it is generated, or it
is a pointer, never a re-stated copy.** *Route to CFL + Personal; I'll apply it to my own index.*

**P5 — Retire dead-letter rules or enforce them (both).** Personal's "no date in filename" rule is
universally violated; either an instrument enforces it or the schema retires it. Record the
cross-trunk naming divergence as a *decision*, not drift. *Route to both.*

**P6 — Clean the archive + mirror asymmetries (CFL + Personal).** CFL: make `archive/` a true
retired-only tree (no live duplicates) or delete the shells; fix the `sessions/` SCHEMA contradiction.
Personal: prune the 4 T1 pointer-stubs out of `sensitive/` or make the mirror consistent. *Route by
letter.*

**P7 — The human-facing view (all three) — this is the OKF/legibility gap.** Every wiki optimizes for
machine navigation; the human view is thin. Proposal: a short, current, per-wiki "what is here and
where to look" page — the *orientation* discipline from the record-method gist — kept under a byte
budget so it stays legible. This is the direct fix for "good for AI but less for me." *Mine to
prototype for Professional; propose to siblings.*

**P8 — Define OKF (HITL, Jon).** It is a term you treat as significant and the record cannot define.
One sentence from you retires a recurring unknown.

---

## What is already solved — credit where due

- CFL's frontmatter-is-truth / folders-are-a-checked-projection architecture is exactly the
  rot-resistant, instrument-verified design the request asks for.
- Personal's 13 checks with mandatory `--selftest` are the anti-rot mechanism, already built and tested.
- Both indexes reconcile against disk at the primary level.
- Both schemas are unusually self-documenting — they record their own past failures inline, which is
  itself a reviewability property most documentation lacks.

The request reads as "is this a mess?" The measured answer is: **two mature trunks with edge-drift, one
skeletal trunk, and two undrained queues.** Fixable, and mostly already designed.
