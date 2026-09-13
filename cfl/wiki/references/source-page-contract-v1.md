---
title: "Source Page Contract v1 — the minimal frontmatter+body that clears scripts/audit/lint.py"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 1 vs fleet 0 on authored labels"
source_kind: reference
retrieval_key: source-page-contract-v1
aliases: [source page contract, minimal compliant session page, lint contract v1, E1-E8 field map]
date: 2026-09-02
generated_by: S-0 executor (week-2026-09-02-corpus lane), reading scripts/audit/lint.py + wiki/SCHEMA.md
  + skills/wiki-master/SKILL.md against two lint-clean wiki/sources/infrastructure/ pages
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
tags: [contract, lint, source-page, E8-fixity, citation-anchors, fidelity-tags]
---

# Source Page Contract v1

**Purpose.** This page states the SMALLEST frontmatter+body a `source_kind: session` wiki page
needs to clear every one of `scripts/audit/lint.py`'s ten checks (`E1k_kind … E8_fixity`) plus the
deterministic anchor-range check, for a session captured THIS WEEK (2026-09-02). It is derived
empirically — by grading two existing lint-clean pages
(`wiki/sources/infrastructure/jon-wayfinder-vision-2026-08-05-ab3ddc.md`,
`wiki/sources/infrastructure/j-layer-forward-pass-direction-2026-07-11-090a56-cont.md`) and one
lint-clean analysis page's summary companion
(`wiki/sources/infrastructure/session-9e21da-subagent-summaries-2026-08-03.md`) — not invented.
`scripts/audit/lint.py --explain <slug>` is the ground truth for every claim below; run it after
writing a page, never trust this contract alone.

## How to run the grader against a page whose raw lives off the tracked tree

`lint.py`'s default `--main-root` is a hardcoded `G:/...` path — **never point it there under this
lane's rules (G:\ is untouched).** Every invocation in this lane instead passes
`--main-root "N:/claude-corpus/cfl"`, because that is the read-only mirror whose
`raw/transcripts/claude-code/fl/...` tree holds the source files this page's two exemplars cite.
`lint.py` resolves `source_file:` as `os.path.join(main_root, source_file)` (`scripts/audit/lint.py:167`),
so a page's `source_file:` frontmatter value must be **repo-relative** (`raw/transcripts/...`, no
drive letter) for that join to land on the right byte — see the two exemplar pages for the working
form. `--explain <slug>` grades EVERY page under `wiki/**/sources/` on each call (there is no
single-file positional argument) and then prints only the rows whose slug contains the substring
you passed; it is the right invocation for grading one new page without waiting on a full-repo run.

## Field-by-field: which check each frontmatter key satisfies

| Frontmatter key | Check(s) it satisfies | Rule, read from `lint.py` |
|---|---|---|
| `source_kind: session` | **E1k_kind** | `PASS if fm.get("source_kind") else FAIL` (`lint.py:169`). Also feeds `kind_of()` so the page is graded as a session rather than falling through to the `candidate-analysis` default. |
| `source_file: raw/transcripts/claude-code/fl/<file>.md` | **E8_fixity** (gate), **E2_anchor** (session path uses turn anchors, not this field, but a present+resolving `source_file` is what makes E8 gradable at all rather than `N/A-kind`) | `has_raw = bool(sf) and sf.lower() not in ("none","n/a","")` (`lint.py:159`). Must be a path that resolves under `--main-root` or E8 grades `UNRECOVERABLE`, not PASS. |
| `raw_sha256: <64-hex>` (frontmatter) | **E8_fixity** | `lint.py` recomputes `hashlib.sha256(open(raw_path,"rb").read()).hexdigest()` and compares to the declared value stripped (`lint.py:151-156`). A stale, wrong, or invented hash FAILs — this is the one field in the whole contract that is independently VERIFIED, not just checked for presence. |
| `raw_length: <n> chars / <n> lines` (anywhere in body or frontmatter prose, literal string `raw_length:`) | **E8_fixity** (co-gate) | `declared and "raw_length:" in text` (`lint.py:150`) — both `raw_sha256:` AND the literal substring `raw_length:` must appear or E8 FAILs even with a correct hash. |
| `retrieval_key: <unique-slug-ish-string>` | **E6_find** (co-gate) | `"retrieval_key:" in text and text.count("aliases:") >= 1` (`lint.py:172`). |
| `aliases: [a, b, c]` (at least one entry) | **E6_find** (co-gate) | Same line — the literal substring `aliases:` must appear at least once; an empty `aliases: []` still satisfies the substring count but defeats the field's purpose, so write real aliases. |
| `generated_by: <agent/session identifying who wrote this page>` | **E7_prov** | `"generated_by:" in text` (`lint.py:173`) — presence-only; no cross-check. |
| `uncaptured_assessed: populated` (or `none`/whatever disposition) | **E4_uncap** | `PASS if "uncaptured_assessed:" in text else (NA_KIND if not has_raw else FAIL)` (`lint.py:170`) — required whenever `source_file` resolves (`has_raw` true), which a session page's `source_file` makes true by construction. |
| `extraction_by: <subagent/pipeline>` — **OMIT unless a subagent actually contributed** | **E7m_reads** | Conditional check: `if "extraction_by:" in text: e7m = PASS if "reads_manifest:" in text else FAIL else: e7m = NA_KIND` (`lint.py:175-178`). Writing `extraction_by:` without a matching `reads_manifest:` line TURNS AN AUTOMATIC PASS INTO A FAIL — the safest minimal-compliant choice is to omit both fields entirely when no subagent read the raw on this page's behalf, letting the check grade itself `N/A-kind`. |
| `reads_manifest: <path or "none (reason)">` | **E7m_reads** (co-gate) | Only required, and only checked, when `extraction_by:` is present (see above). |

**date** lives in frontmatter (`date: YYYY-MM-DD`), never the filename — SCHEMA's L1 rule
(`wiki/SCHEMA.md` "File Naming") and this repo's own convention (every exemplar and model page
below carries `date:` in frontmatter with a date-bearing slug for human readability only). The
slug's own `YYYY-MM-DD` is cosmetic; lint does not read it.

**uuid6, trunk/branch/sub_branch/branch_reason** — not independently checked by `lint.py` (no
`E*` check reads them), but required by `wiki/SCHEMA.md`'s three-coordinate rule (DOMAIN =
trunk→branch→sub_branch) and by the slug format `skills/wiki-master/SKILL.md` states:
`{topic}-YYYY-MM-DD-UUID6`. `branch_reason` follows this repo's existing convention (a short
`R-<code>; sub: <n> vs <n> on authored labels` string, copied verbatim in structure from every
model page's own `branch_reason:` field — the exact wording is free text, the FORM is what
repeats).

## Body rules — what `E1_form`, `E2_anchor`, `E3_fidelity`, `E5_link` actually require

- **`E1_form`** (session kind): `all(f"## {s}" in body for s in ("Summary", "Key Claims",
  "Conflicts"))` (`lint.py:105`) — all three headings, spelled exactly `## Summary`, `## Key
  Claims`, `## Conflicts`, must be present verbatim (case- and space-sensitive on the `## `
  prefix) or E1 FAILs. **This is also the cascade gate**: if `## Key Claims` is missing, `E2`,
  `E3`, and `E5` all downgrade from FAIL to `N/A-blocked` rather than independently failing
  (`lint.py:108-110`) — but the intent of this contract is a page that clears the cascade by
  having the section, not one that hides behind the blocked grade.
- **`E2_anchor`** (session kind): `has_turn_anchor = bool(re.search(r":T\d+", text))`
  (`lint.py:113`, applied via `claim_check`) — at least one citation of the literal form
  `:T<digits>` must appear anywhere in the page text. Format from
  `skills/wiki-master/SKILL.md` §"Citation anchors": `([slug:T{n}])` for a whole-turn citation,
  `([slug:T{n}.P{p}])` for a paragraph inside a long turn. `slug` is this page's own filename
  stem (no path, no extension) — a **self-referential** anchor, not a link to another page.
- **DETERMINISTIC anchor-range check** (separate from E2, computed in `main()`, `lint.py:214-224`):
  every `:T<n>` cited anywhere in the page is collected, `turn_index.py` is run against the
  resolved `source_file`, and any `n` greater than the raw's VERIFIED turn count is a broken
  anchor (FAILs the page's overall `conformant` boolean even though E2 itself still shows PASS).
  **Practical consequence:** run `python scripts/audit/turn_index.py <raw> --json` (or the
  plain summary form) against the actual raw BEFORE picking turn numbers to cite — do not
  estimate. See the two exemplar pages' turn-index output, pasted in the report
  (`wiki/intake-triage/S0-exemplars-2026-09-02.md`), for a worked example. Note also that
  `turn_index.py` only recognizes two header styles (`## Human`/`## Assistant`/... or
  `**Jon**`/`**Claude**`); a raw using a THIRD header convention (this lane found one — the
  `record-pipeline-window/v0.3` window-chunk files under `.../fl/`, whose turns read `## Human
  [HH:MM:SS.ffffffZ]` with a bracketed timestamp rather than the accepted `— [origin:...]`
  suffix) indexes as **0 verified turns**, which would FAIL every `:Tn` anchor cited against it
  as out-of-range. **Prefer a raw file that `turn_index.py` already parses non-zero** — check
  before committing to a source, not after.
- **`E3_fidelity`** (session kind): `bool(re.search(r"\[(verbatim|paraphrase|reconstructed|
  contextual|inferred|uncaptured)\]", text))` (`lint.py:120-121`) — at least one Key Claim
  bullet must carry one of these six exact bracketed tags. `skills/wiki-master/SKILL.md`
  requires EVERY Key Claim to carry one, not just one page-wide, though `lint.py` itself only
  checks for at least one occurrence.
- **`E5_link`** (session kind): `has_wikilink = bool(re.search(r"\[\[[^\]]+\]\]", text))`
  (`lint.py:114`, applied via `claim_check`) — at least one `[[slug]]` link to an EXISTING wiki
  page anywhere on the page. `wiki/SCHEMA.md` "Cross-Link Protocol" — link to the slug (filename
  stem), never a path.

## Jon-quote rules, restated for this contract (source: `wiki/SCHEMA.md` §"How to quote Jon")

- Words verbatim, including his own typos and disfluencies — never silently corrected.
- Case and punctuation are content, not styling.
- **No emphasis (`**bold**`, CAPS, italics) added INSIDE a quotation's own quotation marks** — the
  universal-layer amendment (2026-08-24) this lane's own instructions carry: emphasis inside a
  quote makes the quote unfindable by literal grep of the corpus that holds the primary. If a
  phrase must be emphasised, emphasise OUTSIDE the quote marks or restate it in your own sentence.
- `[sp]` marks a spelling correction, `[interp]` marks an interpretive best-guess — both keep the
  original alongside, never silently replace it.
- **Never attribute a paraphrase as a marked verbatim quote** — `record-architecture-v1.md`'s own
  correction (Jon's "educational material" line, downgraded from quote to paraphrase 2026-07-30)
  is the standing example of the failure this rule exists to prevent.

## What this contract deliberately leaves OPEN

- The `reconstructed` vs `inferred` fidelity-tag boundary — `skills/wiki-master/SKILL.md` states
  this is undrawn by the v4.0 standard and left to the writer's judgment, disclosed inline.
- `audit_state:` — read by `lint.py`'s `audit_state_of()` for the G3 ledger/authority display but
  NOT part of the `conformant` boolean; a freshly-authored page may reasonably omit it or set
  `unaudited` (the model pages disagree with each other on whether to set it at all).
- `sensitivity:` — appears on some model pages (`jon-wayfinder-vision-...`: `sensitivity: T1`) but
  is read by no `E*` check; include it if the page's own content warrants a stated tier, omit it
  otherwise.

## Verification

Both exemplar pages under `wiki/sources/infrastructure/` built from this contract graded
`CONFORMANT: True` with `E8_fixity: PASS` under `--main-root "N:/claude-corpus/cfl"` — full output
pasted in `wiki/intake-triage/S0-exemplars-2026-09-02.md`, alongside the negative control (hash
removed → `E8_fixity: FAIL`, everything else unchanged) that this contract predicts and the run
confirms.

## Cross-links

- [[probe-registry]] — same seal-before-run discipline this contract's own "Verification" section
  follows (state the expected grades, then run the check).
- `wiki/sources/infrastructure/jon-wayfinder-vision-2026-08-05-ab3ddc.md`,
  `wiki/sources/infrastructure/j-layer-forward-pass-direction-2026-07-11-090a56-cont.md` — the two
  pages this contract was read off of.

## Appended rule — probe applicability by kind (GATE-06, coordinator ruling 2026-09-02)

**The `:Tn` fresh-reader probe is NOT APPLICABLE to a page whose kind has no turns.** A page with
`source_file: none`/absent (the same `has_raw` rule `lint.py` uses to grade E2/E3/E4/E8 `N/A-kind`),
or whose declared raw `turn_index.py` finds zero turns in (a static reference such as
`raw/references/goals.md`), has nothing a turn probe can check. For those pages `ingest_gate.py`
skips step 3, records `PROBE: N/A-kind (no turns; E10_probe lint is the applicable check)` in the
ledger row, and the verdict is decided by LINT + FENCE (+ HASH) alone — `E10_probe` (a sealed
`probe_sealed: "<question> => <class>"` on any page dated 2026-09-02 or later) is the check that
applies. A no-turns page that nevertheless cites `:Tn` anchors is contradictory and stays on the
normal probe path (it is graded, never waved through). Background: GATE-05 recorded seven such
pages REJECTED-probe on a cold-grader UNKNOWN ("zero :Tn in range") while GATE-04 graded the same
shape TRUSTED as vacuous; both were grading a check that does not apply.
`wiki/intake-triage/GATE-06-2026-09-02.md` carries the re-runs.
