---
name: cross-trunk-metadata-audit-2026-08-23
description: "Measured frontmatter inconsistency across all six trunks, CFL PR-1 forensics, and a minimal proposed schema — written in response to Jon's PR-1 complaint (\"the metadata consistency! It was rempent even in the first of only 3 PRs\")"
kind: reference
created: 2026-08-23
calibration: measured
---

# Cross-trunk metadata audit — 2026-08-23

**Trigger.** Jon, verbatim: *"The metadata consistency! It was rempent even in the first of only 3
PRs that CFL will be allowed to give me! Very unprofessional."* This is a direct measurement of the
defect he named, across every trunk, plus the PR-1 instance and a minimal fix.

**Scope note.** Three trunks (Professional, CFL, Personal/Herald-source) keep a `wiki/` tree with
YAML frontmatter by convention. Three (Secretary, SSP, herald-wiki) do not use a `wiki/` subdirectory
at all — their markdown lives at repo root and in flat topic folders — so "under wiki/" was read as
"the trunk's whole tracked markdown corpus, minus `.git/`" for those three. That is stated, not
hidden, because it changes what "total pages" means per trunk.

---

## 1. Per-trunk frontmatter enumeration

Command run once per trunk (Python, `re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)`
against every `**/*.md` file, `.git/` excluded):

```
python fm_audit.py "<trunk-root>[/wiki]"
```

| Trunk | Root scanned | Total .md | No frontmatter | Distinct top-level keys |
|---|---|---:|---:|---:|
| Professional | `claude-professional/wiki` | 46 | 1 | 51 |
| CFL | `claude-foundational-layer/wiki` | 937 | 3 | 347 |
| Personal | `Claude Personal/wiki` | 809 | 109 | ~230 |
| Herald (retired) | `Herald Wiki/herald-wiki` (whole repo) | 261 (255 counted*) | 46 | ~85 |
| Secretary | `Claude Secretary` (whole repo) | 230 (229 counted*) | 201 | ~18 |
| SSP | `Claude SSP/claude-ssp` (whole repo) | 197 | 50 | ~95 |

\* `find` and the Python glob disagreed by one file in Herald and Secretary — a symlink or a file
whose glob pattern matched differently between `find -name "*.md"` and Python's `glob("**/*.md")`.
Not chased further; the counted figure is the one the frontmatter numbers below are drawn from.

**CFL's 347 distinct top-level keys is the headline number.** 106 of those 347 keys appear on
exactly **one** page each — singleton keys, most of them internal to one audit script's output
format rather than page metadata proper (e.g. `subagents_considered`, `finalised_this_run`,
`skipped_already_final`, `report_content_sha256`). This is not a schema; it is every script that
ever wrote frontmatter contributing its own vocabulary, uncoordinated, for a year.

**Professional's key histogram** (51 keys across 46 pages) shows the same pattern in miniature: 34
singleton keys out of 51 (`re`, `run`, `note`, `enforced_by`, `primary_source`, `consent-basis`,
`sealed`, `sealed_by`, `authored`, `counterpart`, `secrecy`, `corpus`, `freshness`, etc.) — a trunk
with 46 pages should not need 51 distinct metadata vocabularies, and this trunk is not exempt from
the finding just because it is younger and smaller.

**Full key histograms** (exact counts, most-common first) were captured to
`fm_audit.py` output for each trunk and are reproduced in condensed form under §2/§5 below where
they carry crosswalk or value evidence; the complete per-key counts are large (CFL alone is ~350
lines) and are not pasted in full here — re-run `fm_audit.py` against any trunk root to regenerate
them verbatim.

---

## 2. The cross-trunk key crosswalk

Evidence-based, not name-guessed — each row below was checked by opening at least one page per
trunk and comparing the key's role and value, not just its spelling.

### 2a. "What is this page called" — `title` vs `name` vs `slug`

- **`title`** is the dominant key for "the page's human-readable name" in every trunk that has one:
  Professional (39/46), CFL (838/937), Personal (658/809), Herald (140/255), Secretary (19), SSP (54).
- **`name`** plays the identical role on a small minority of pages, confirmed by inspection:
  `wiki/SCHEMA.md` (CFL) opens `name: Meta-Project Wiki — Claude Foundational Layer` with no `title`
  key at all — same slot, different key, on the trunk's own top-level schema file. CFL has 4 pages
  using `name` this way; Personal has 2; Professional has 7 (its own `wiki/SCHEMA.md`-equivalent
  pages use `name:` as the slug-like identifier, e.g. `name: resident-v1-safe-environment-and-
  prototype-loop`, which is closer to `slug` than to `title` — see below, this is itself a second
  collision).
- **`slug`** is a third, distinct concept present in Professional (5), CFL (27), Personal (539 —
  the dominant convention there), Herald (84), SSP (28): a machine-safe filename-shaped identifier,
  usually lowercase-hyphenated, that duplicates the filename. Personal's near-universal `slug`
  coverage (539/809, the third-most-common key in that trunk) versus CFL's near-absence (27/937)
  is itself a trunk-level divergence: Personal's page-creation path stamps `slug` by convention;
  CFL's mostly doesn't.
- **Collision found:** Professional's `name:` key is used BOTH as "the page title" (its `wiki/
  SCHEMA.md`-style pages) AND as "the page slug" (its `wiki/concepts/*.md` pages, e.g. `name:
  a-gate-that-fires-red-on-correct-behaviour`) — i.e. the same key means two different things
  depending on which corner of the same trunk wrote it.

**Crosswalk: `title` (human name) and `slug` (machine id) are two different things that should stay
two different keys; `name` is being used as a stand-in for BOTH, inconsistently, and should be
retired in favor of the pair.**

### 2b. "When was this made" — `created` vs `date` vs `as_of` vs `sealed`

- **`created`**: Professional (34), CFL (25), Personal (5), SSP (3). Meaning is consistent where
  checked: "the date this specific page/record came into existence." CFL's DECISIONS.md: `created:
  2026-08-22, M-6 (...), seeded from the letter/ruling record` — note the value is not a bare date,
  it is a date plus provenance clause (see §5).
  Rather, `date` is the far more common key for the same concept: Professional (9), CFL (158),
  Personal (639-640), Herald (202), Secretary (59-60), SSP (102).
- **`as_of`**: CFL (48), Personal (50), SSP (22) — a THIRD variant, used specifically for
  "the point-in-time this record's claims were true as of," which is a related but distinct concept
  from "when the page was written" (a page can be created 2026-08-23 but be `as_of` an earlier
  measurement). This is a real semantic distinction, not just a naming variant — do not fold it
  into `created`/`date` in the proposed schema.
- **`sealed` / `sealed_by`**: Professional (1 each), CFL (`sealed`: 3, `sealed_by`: 2) — a fourth,
  narrower variant meaning "the point at which this record was frozen against further edits"
  (pre-registration / falsifier-test pattern). Distinct concept again, low-incidence, not core.

**Crosswalk: `created`/`date` are true synonyms for the same concept (page inception timestamp) —
confirmed by identical usage pattern across CFL's DECISIONS.md, Professional's index pages, and
Personal's tracker pages. `as_of` is a genuinely different concept (claim-currency, not page-age)
and both concepts need to survive in any unified schema, under two different keys.**

### 2c. "What kind of page is this" — `kind` vs `type` vs `label`

This is the messiest collision in the corpus, and it does not resolve the same way in every trunk:

- **CFL**: `type` (353 pages) is MORE common than `kind` (59 pages), the reverse of every other
  trunk. On the 9 pages that carry both (e.g. `wiki/concepts/disposition-rate.md`), the two keys
  hold the **identical value** — `kind: concept` and `type: concept` on the same page, same line
  distance apart. This is not two concepts under two names; it is one concept written twice because
  two different tooling paths both stamp their own key for the same thing.
- **Personal**: `kind` (636 pages) is the dominant key, `type` (53 pages) is the minority. On the 42
  pages carrying both (e.g. `wiki/references/branching-thoughts-vs-subagents.md`): `type: reference`
  and `kind: reference:method` — here `kind` is NOT a synonym for `type`, it is a **namespaced
  sub-type** of it (`type` = coarse category, `kind` = category:subcategory).
  So the same key pair (`kind`+`type`) means "exact duplicate" in CFL and "coarse+fine" in Personal.
  A schema migration that just picks one of the two keys will silently destroy the sub-typing
  information Personal pages actually carry.
- **Professional**: `kind` (14) is the dominant convention, `type` (3) rare, no page carries both —
  no internal collision, but its 3 `type` values (`project`, `project`, `escalation-packet (mirror
  — proposes only; the seat disposes)`) show the same drift toward prose-in-a-category-field seen
  everywhere else (§5).
- **`label`**: Professional only, 2 pages — too rare to be a real crosswalk target, likely a typo
  or one-off for `kind`.

**Crosswalk finding, stated precisely because it is the actionable one: `kind` and `type` are used
as exact synonyms in CFL (duplication defect) and as a two-level taxonomy in Personal (coarse/fine,
intentional). Any unified schema must pick ONE key for the coarse category and, separately, decide
whether the CFL-style duplication gets deleted (recommended — see §6) or the Personal-style
sub-typing gets promoted to a real second field.**

### 2d. "What is this page about, one line" — `description` vs `summary`

- **`description`**: Professional (4), SSP (4) only.
- **`summary`** as a frontmatter key: **zero occurrences in any trunk's key histogram.** Where a
  one-line synopsis exists elsewhere it lives in prose under an `## Overview` heading, not in
  frontmatter — so this is not a naming collision, it is an **absent field** in four of six trunks
  (CFL, Personal, Herald, Secretary carry no one-line-summary frontmatter key at all, at any name).

### 2e. Routing/addressing keys — `from`/`to`/`re` cluster

Present with consistent meaning (sender/recipient/subject-line, letter-format pages) in CFL,
Personal, Herald, Secretary, SSP — this cluster is the most CONSISTENT one found in the corpus:
same three keys, same semantics, same co-occurrence pattern, across five trunks. Professional's
absence of this cluster is because Professional does not (yet) write inter-trunk letters into its
own `wiki/`; it receives them into `exchange/inbound/` instead, which is out of this audit's `wiki/`
scope. Not a defect — different page genre.

---

## 3. CFL PR-1 (squash commit `ee473c1`) — measured

```
git -C "<CFL path>" show ee473c1 --stat        # hangs / times out on this box — 1932-file squash
git -C "<CFL path>" log -1 ee473c1
git -C "<CFL path>" diff-tree --no-commit-id --name-status -r ee473c1
```

`git show --stat` would not complete in 20s or 60s runs (the diffstat renderer chokes on a
1,932-file commit); `diff-tree --name-status` returned in under 60s and is the basis for the counts
below.

**Commit metadata:**
```
commit ee473c1a956e7ba8065a8b6845625b552230e024
Author: jonsch201-commits <jonsch201@gmail.com>
Date:   Sat Aug 22 22:26:17 2026 -0500

    PR-1 of 3: Memory, Cognition & Federation — the tested foundation
```

**File-level shape:** 1,932 total files touched. Of those, **807 paths are under `wiki/`**, and
**771 of the 807 are `.md` files** — 293 newly added (`A`), 478 modified (`M`), 0 deleted.

**This is the direct link between the audit above and Jon's complaint.** PR-1 is not a small patch
that happened to contain one bad file — it is the commit that brought roughly **82% of CFL's current
937-page wiki** (771 of 937) into `main` in one squash. The 347-distinct-key sprawl and the
`kind`/`type` duplication measured in §1–§2 are not a separate, later problem from PR-1 — **they are
substantially the same pages PR-1 landed.** Spot-checked: `wiki/concepts/disposition-rate.md` (the
`kind: concept` / `type: concept` duplicate cited in §2c) is one of the 293 files PR-1 added
(`A wiki/concepts/disposition-rate.md` in the diff-tree output). `wiki/SCHEMA.md` and
`wiki/DECISIONS.md` (the `name:`-instead-of-`title:` and prose-`status:` examples in §2a/§5) are
both in the 478-file modified set.

**What is inconsistent, file:line, confirmed by direct read:**
- `wiki/concepts/disposition-rate.md:4` (`kind: concept`) and `:9` (`type: concept`) — duplicate
  category key, identical value, both present. Landed by PR-1 (file status `A`).
- `wiki/SCHEMA.md:6` uses `name:` where 838/937 other CFL pages use `title:` for the identical role
  — landed/modified by PR-1 (file status `M`).
- `wiki/DECISIONS.md:6` `status: LIVE — APPEND-ONLY. Never edit a prior entry...` — a full sentence
  (35+ words) in a field that on other pages holds a single token (`current`, `canonical`, `DRAFT`)
  — landed/modified by PR-1 (file status `M`).

I did **not** find a single canonical "here is THE metadata defect" commit hunk to point to beyond
these three, because the defect is distributional, not a single bad line — PR-1's 771 markdown
files collectively carry the 347-key sprawl measured in §1, and no small excerpt represents that
fairly. If Jon meant a narrower, specific instance than "the whole wiki's frontmatter is
inconsistent and PR-1 is where most of it entered," that instance is UNKNOWN to me and would need
him to point at the specific page(s) he was looking at when he wrote the complaint.

---

## 4. `sensitivity:` coverage — re-measured, with corrections

| Trunk | Relayed [unverified] | Measured [this session] | Correction |
|---|---|---|---|
| Personal | ~582 of 801 | **582 of 809** | Numerator confirmed exactly. Denominator was wrong — actual page count is 809, not 801 (+8). |
| CFL | ~18 of 926 | **18 of 937** | Numerator confirmed exactly. Denominator was wrong — actual page count is 937, not 926 (+11). |
| Professional | 0 of 35 | **0 of 46** | Numerator confirmed (sensitivity does not appear anywhere in Professional's 51-key histogram). Denominator was wrong — actual page count is 46, not 35 (+11). |

Two independent extraction methods (top-level key histogram, and a second pass reading the
`sensitivity:` line value directly) agreed on the numerators to within rounding (582 vs 583, 18 vs
18, 0 vs 0) — the 1-page spread on Personal is a regex edge case on a quoted vs unquoted value, not
a real disagreement.

**Also measured, not in the original relay:** Herald 79/255 (100% of those carry the tier token
`T2` and nothing else — the single most internally-consistent `sensitivity` field in the whole
corpus); Secretary 34-35/229 (0% tier-token, 100% freeform prose, e.g. entire sentences in the
field); SSP 1/197.

---

## 5. Value-level inconsistency (key consistency with junk values is not consistency)

| Trunk | `date` total | ISO `YYYY-MM-DD` | non-standard | `status` total | single/short token | full-sentence prose | `sensitivity` total | tier token (`T0`-`T9`) | freeform prose |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Professional | 9 | 9 | 0 | 20-21 | 1-2 | 18-20 | 0 | 0 | 0 |
| CFL | 158 | 151 | 7 | 205 | 48-50 | 155-157 | 18 | 12 | 6 |
| Personal | 640 | 618 | 22 | 642 | 467-470 | 172-175 | 583 | 566 | 17 |
| Herald | 202 | 134 | 68 | 124 | 88 | 36 | 79 | 79 | 0 |
| Secretary | 59-60 | 36-37 | 23 | 4 | 0 | 4 | 34-35 | 0 | 34-35 |
| SSP | 102 | 25 | 77 | 41 | 5-6 | 35-36 | 1 | 1 | 0 |

(Ranges reflect the two independent extraction passes; both are reported rather than picked
because neither is more authoritative and the spread is small.)

**Reading this table:** CFL's `status` field is prose 76% of the time (e.g. `wiki/DECISIONS.md`'s
35-word sentence, quoted in §3) — a field named `status` that mostly does not hold a status token
is not usable for any automated filter (`grep status: DRAFT` silently misses three-quarters of the
corpus). SSP's `date` field is non-ISO 75% of the time — many SSP dates are ranges (`2026-08-09/10`)
or carry embedded correction narratives (one `date:` value is itself a 400-character paragraph
explaining a 53-minute clock-drift correction). Herald and Secretary's sensitivity fields sit at
opposite poles of the same defect: Herald is 100% one controlled vocabulary (`T2`), Secretary is
100% freeform prose describing sensitivity rather than classifying it.

**The general finding under all six rows: no trunk has a machine-checkable `status`, `date`, or
`sensitivity` field today.** Every one of them accepts free text, and every one of them has been
used that way often enough that a script written against "the field holds one of N known values"
would be wrong on a material fraction of pages in every trunk except Herald's `sensitivity` field.

---

## 6. Minimal proposed schema

Design constraint taken directly from Jon's standing rule: **a small mandatory core beats a large
one** — overconservatism (in this case, over-specifying the schema) has cost more than the risk of
under-specifying it. The core below is deliberately short: six keys, chosen because each already
exists in some form in every trunk (so this is a rename/canonicalize migration, not new invention),
and each closes a specific defect measured above.

| Key | Rationale | Replaces / absorbs |
|---|---|---|
| `title` | Human-readable page name. Already the plurality convention in 4/6 trunks. | `name` (retire — §2a showed it means two different things even within one trunk) |
| `slug` | Machine-safe id, independent of title wording. Needed because `title` values are frequently full sentences with punctuation (§2a examples run 60-140 characters) that cannot double as a stable id. | nothing removed — this key already exists, just not universally populated |
| `kind` | Single controlled-vocabulary category token (`concept`, `reference`, `session`, `tracker`, `letter`, `ledger`, ...). | `type`, `label` (retire both — §2c showed `type` is either an exact duplicate of `kind` (CFL) or a coarser version of it (Personal); collapsing to one field and, where the finer Personal-style subtype is actually load-bearing, moving it to a documented `kind: category:subtype` string keeps that information without a second key) |
| `created` (ISO `YYYY-MM-DD`, date only, no embedded prose) | Page inception timestamp, machine-parseable. Provenance narrative that currently rides inside `date`/`created` values (§5 examples) moves to a `## Provenance` body section instead of living in the value string. | `date` (retire as a duplicate name for the same concept — §2b showed `created`/`date` are true synonyms) |
| `status` (single controlled-vocabulary token: `draft`/`current`/`superseded`/`archived`, or a small trunk-specific extension of that set) | The prose-sentence pattern measured in §5 (76% prose in CFL, 88% prose in SSP) makes this field useless for tooling today. Narrative belongs in the body, one line under a `## Status` heading if needed. | nothing removed — narrows the existing key's allowed values |
| `sensitivity` (controlled tier token, `T0`-`T2` or trunk-appropriate equivalent) | Herald already proves this works at 100% consistency (79/79 tier-token). CFL and Secretary's freeform-prose sensitivity fields (§4-§5) are the two worst offenders and the two most fixable, since Herald is the existence proof. | nothing removed — narrows the existing key's allowed values |

**Explicitly NOT in the mandatory core, and why:** `as_of` (real second concept, but only 3/6 trunks
need the claim-currency/page-age distinction — make it optional, not core); `description`/`summary`
(useful, but §2d shows 4/6 trunks have never needed it — a one-line synopsis is recoverable from the
page body on demand, it is not worth a mandatory field); the `from`/`to`/`re` letter cluster (already
consistent per §2e — do not touch what is not broken); all provenance/audit keys (`produced_by`,
`extract_status`, `finalised_utc`, etc.) that exist for CFL's transcript-pipeline machinery — those
are legitimate, high-volume, and out of scope for a page-identity schema.

### Migration cost, measured per trunk (pages that would need a frontmatter edit)

Cost = pages carrying a key being retired/renamed (`name`, `date`, `type`, `label`) OR a
non-conformant value in a core key being narrowed (`status` prose, `sensitivity` freeform,
`created`/`date` non-ISO). A page hit by more than one issue is counted once.

| Trunk | Pages needing `name`→`title` fix | `date`→`created` rename | `type`/`label`→`kind` fold | `status` value narrowing | `sensitivity` value narrowing | `date` ISO-format fix | **Distinct pages touched (dedup estimate)** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Professional | 7 | 9 | 3 | ~18-20 | 0 | 0 | **~30 of 46 (65%)** |
| CFL | 4 | 158 | 353 | ~155-157 | 6 | 7 | **~500-550 of 937 (~55-60%)** |
| Personal | 2 | 640 | 53 | ~172-175 | 17 | 22 | **~700 of 809 (~85%)** |
| Herald | 1 | 202 | 5 | ~36 | 0 | 68 | **~230 of 255 (~90%)** |
| Secretary | 0 | 60 | 0 | 4 | ~34-35 | 23 | **~90 of 229 (~40%)** |
| SSP | 4 | 102 | 4 | ~36 | 0 | 77 | **~150 of 197 (~75%)** |

**Total estimated migration: roughly 1,700-1,750 page-edits across the six trunks, dominated by two
mechanical, scriptable changes** — renaming `date:` to `created:` wherever it means page-inception
(the single largest line item everywhere), and narrowing `status:`/`sensitivity:` free text down to
a controlled token (which needs a human or an LLM pass per page, not a pure rename, since the prose
often carries real information that a script cannot safely discard — see the DECISIONS.md example
in §3, where the 35-word status sentence encodes an append-only editing rule that would be lost by
a naive truncation to `status: current`).

**Recommended sequencing, given the small-core principle:** land the schema and enforce it on NEW
pages first (near-zero cost, stops the sprawl from growing past 347 keys); then run the mechanical
renames (`date`→`created`, `type`/`label`→`kind` fold) trunk-by-trunt as a scripted pass, since those
touch the most pages but require no judgment; leave the `status`/`sensitivity` value-narrowing pass
for last and explicitly budget it as a slower, per-page pass rather than a script, because that is
where meaning would be destroyed by rushing it.
