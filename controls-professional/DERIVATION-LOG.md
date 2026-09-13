## SCOPE

Run F 2026-09-13 00:5x: T7 remedies -- spec adds wiki/index.md and .claude/skills/oath-checks/; deriver CFL HEAD; same source root N:\claude-professional (fs mode) and exclusion set as run E.

---

# DERIVATION-LOG -- public-safe derived tree

Produced by `scripts/audit/derive_public_tree.py` (lane PUB-1).

Source: fs N:/claude-professional

**Two dispositions only: INCLUDE byte-identical, or EXCLUDE whole-file. No file's content was rewritten, and nothing in the source tree was modified.**

## Exclusion set

- Read from `scripts/audit/public_exclusions.txt` (sha256 `ea426a8a552d5b8032322bb8e4938e08a4868a0f324d82f624516130fb7318c0`), never inferred from repo prose.
- DIR_NAME entries: XC-Exchequer | CONTENT_CLASS entries: 5 | PATH_PREFIX entries: 16

## Gazetteer arming

- ARMED: 4 gazetteer entries loaded (entries themselves are never printed).

## Counts

| quantity | n |
|---|---|
| paths at source | 4993 |
| not in the include spec (never considered) | 4662 |
| considered | 331 |
| INCLUDED | 330 |
| EXCLUDED (distinct files) | 12 |
| exclusion hits (a file may carry several) | 12 |

## Exclusions by class

| class | files |
|---|---|
| CONTENT-XC-EXCHEQUER-PATH | 1 |
| PATH-DENY-EXACT | 11 |

## Every exclusion (path, class, line, detail)

| path | class | line | detail |
|---|---|---|---|
| `scripts/audit/retrievable_check.py` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/concepts/no-names-in-public-artifacts-without-consent.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/concepts/resident-corpus-clean-by-construction.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/concepts/synthesis-summaries-pii-free-by-default.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/references/cross-trunk-wiki-peer-review-2026-08-23.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/references/professional-wiki-first-principles-2026-08-09.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/sources/jon-frustration-register-2026-08-23.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/sources/jon-outstanding-asks-register-2026-08-24.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/sources/jon-typed-prompts/history-2026-05.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/sources/jon-typed-prompts/history-2026-06.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/sources/jon-typed-prompts/history-2026-07.md` | PATH-DENY-EXACT | 0 | FAMILY-CONSENT-PENDING |
| `wiki/sources/jon-typed-prompts/history-2026-08.md` | CONTENT-XC-EXCHEQUER-PATH | 221 | XC-Exchequer\exchange\questions-for-triage.md, |

## REPORT-ONLY (nothing was withheld for these)

**1 row(s).** These classes are REPORTED and never cut. `FM-HELD-PROSE` exists because T5 (Professional, 2026-09-13) found `HELD_VAL_RX` matching `held` inside a value's PROSE and withholding a LIVE page for a sentence about being held to a standard. `FM_HELD_KEY` includes `visibility` and `FM_HELD_VALUE` includes `held`/`personal`/`private`, all ordinary English, so any narrative value under a common key tripped it. **A page is withheld for a DECLARATION, not for a sentence** -- and the match was not loosened, because failing open is the dangerous direction on a public surface.

| path | class | line | detail |
|---|---|---|---|
| `wiki/concepts/leading-from-the-rigor-seat.md` | FM-STATUS-HELD-PROSE | 0 | status: LIVE — positions held by this seat; each states what would change its mind  [REPORT ONLY -- 'held' appears in a 14-token status whose declared value ... |

## REFERENCE-SURVIVORS

**REFERENCE-SURVIVORS: 8 of 12 excluded files have >= 1 inbound reference by name in an INCLUDED file (10 refs total); PATH_EXACT rows: 7 of 11 have survivors**

A whole-file EXCLUDE removes the body; the NAME survives wherever an INCLUDED file referred to it. Nothing below was rewritten -- a reference by name is disclosed here as a name only. Forms: FULL (repo-relative path), SUFFIX (parent-dir/basename), FILENAME, WIKILINK (`[[stem]]`), STEM (bare basename). FILENAME is armed only when no other file at source shares the basename; WIKILINK and STEM only when no other path shares the stem, and STEM additionally only for slug-shaped stems (a hyphen, underscore or digit) -- a shared name or a plain word is not a reference to THIS file, and the `forms dropped` column says so per file. One row per (referring file, line, excluded file), most specific form wins. `--fail-on-survivors` exits 4 when any PATH_EXACT row has >= 1 survivor.

| excluded file | exclusion | inbound refs | forms dropped |
|---|---|---|---|
| `scripts/audit/retrievable_check.py` | PATH_EXACT | 1 | none |
| `wiki/concepts/no-names-in-public-artifacts-without-consent.md` | PATH_EXACT | 0 | FILENAME (2 files at source named no-names-in-public-artifacts-without-consent.md); WIKILINK+STEM (2 paths at source share stem no-names-in-public-artifacts-without-consent) |
| `wiki/concepts/resident-corpus-clean-by-construction.md` | PATH_EXACT | 0 | FILENAME (2 files at source named resident-corpus-clean-by-construction.md); WIKILINK+STEM (2 paths at source share stem resident-corpus-clean-by-construction) |
| `wiki/concepts/synthesis-summaries-pii-free-by-default.md` | PATH_EXACT | 0 | FILENAME (2 files at source named synthesis-summaries-pii-free-by-default.md); WIKILINK+STEM (2 paths at source share stem synthesis-summaries-pii-free-by-default) |
| `wiki/references/cross-trunk-wiki-peer-review-2026-08-23.md` | PATH_EXACT | 1 | FILENAME (2 files at source named cross-trunk-wiki-peer-review-2026-08-23.md); WIKILINK+STEM (2 paths at source share stem cross-trunk-wiki-peer-review-2026-08-23) |
| `wiki/references/professional-wiki-first-principles-2026-08-09.md` | PATH_EXACT | 1 | FILENAME (2 files at source named professional-wiki-first-principles-2026-08-09.md); WIKILINK+STEM (2 paths at source share stem professional-wiki-first-principles-2026-08-09) |
| `wiki/sources/jon-frustration-register-2026-08-23.md` | PATH_EXACT | 2 | FILENAME (2 files at source named jon-frustration-register-2026-08-23.md); WIKILINK+STEM (2 paths at source share stem jon-frustration-register-2026-08-23) |
| `wiki/sources/jon-outstanding-asks-register-2026-08-24.md` | PATH_EXACT | 0 | FILENAME (2 files at source named jon-outstanding-asks-register-2026-08-24.md); WIKILINK+STEM (2 paths at source share stem jon-outstanding-asks-register-2026-08-24) |
| `wiki/sources/jon-typed-prompts/history-2026-05.md` | PATH_EXACT | 1 | none |
| `wiki/sources/jon-typed-prompts/history-2026-06.md` | PATH_EXACT | 1 | none |
| `wiki/sources/jon-typed-prompts/history-2026-07.md` | PATH_EXACT | 1 | none |
| `wiki/sources/jon-typed-prompts/history-2026-08.md` | SCAN | 2 | none |

### `scripts/audit/retrievable_check.py` (PATH_EXACT) -- 1 inbound ref(s)

- `.claude/skills/oath-checks/oath_checks.sh:1472` FULL `scripts/audit/retrievable_check.py`

### `wiki/references/cross-trunk-wiki-peer-review-2026-08-23.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/index.md:95` FULL `wiki/references/cross-trunk-wiki-peer-review-2026-08-23.md`

### `wiki/references/professional-wiki-first-principles-2026-08-09.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/index.md:92` FULL `wiki/references/professional-wiki-first-principles-2026-08-09.md`

### `wiki/sources/jon-frustration-register-2026-08-23.md` (PATH_EXACT) -- 2 inbound ref(s)

- `wiki/concepts/injection-is-not-authorship.md:33` FULL `wiki/sources/jon-frustration-register-2026-08-23.md`
- `wiki/index.md:114` FULL `wiki/sources/jon-frustration-register-2026-08-23.md`

### `wiki/sources/jon-typed-prompts/history-2026-05.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/sources/jon-typed-prompts/INDEX.md:17` FILENAME `history-2026-05.md`

### `wiki/sources/jon-typed-prompts/history-2026-06.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/sources/jon-typed-prompts/INDEX.md:18` FILENAME `history-2026-06.md`

### `wiki/sources/jon-typed-prompts/history-2026-07.md` (PATH_EXACT) -- 1 inbound ref(s)

- `wiki/sources/jon-typed-prompts/INDEX.md:19` FILENAME `history-2026-07.md`

### `wiki/sources/jon-typed-prompts/history-2026-08.md` (SCAN) -- 2 inbound ref(s)

- `wiki/references/probe-set-forgotten-rulings-2026-09-06.md:68` FILENAME `history-2026-08.md`
- `wiki/sources/jon-typed-prompts/INDEX.md:20` FILENAME `history-2026-08.md`

## VALUE-WALK

**VALUE-WALK: 1 literal(s) walked over 330 INCLUDED files; 0 literal(s) found, 0 hit(s) total**

Each `VALUE_WALK` literal from `public_exclusions.txt` is walked fixed-string and case-sensitive over every INCLUDED file. Withholding the file that introduced an identifier does not withhold the identifier. The literal is never printed here -- a row carries an opaque ordinal id, sha256[:8] of (per-run random salt + literal) with the salt printed nowhere (an unsalted digest of a low-entropy literal is an oracle), and its class -- so this log cannot leak what it guards. Nothing was rewritten. `--fail-on-value-hits` exits 5 when any hit exists.

| id | salted digest[:8] | class | hits |
|---|---|---|---|
| VW-01 | `beda2591` | CREDENTIAL-SHAPED Drive folder id | 0 |

## SHAPE-SCAN

**SHAPE-SCAN: 2 shape(s) scanned over 330 INCLUDED files; 0 token hit(s) (detector only, no exit code)**

Each `SHAPE_SCAN <name> <regex>` row is scanned, bounded by non-token characters, over every INCLUDED file, after dropping hex-only strings, tokens lacking mixed case plus a digit, tokens carrying a date, and hyphenated slugs. A hit names the shape and the token's LENGTH only, never the token. This is a detector feeding a human decision; it sets no exit code. Nothing was rewritten.

Second column (lane PUB-2e, 2026-09-02; never a filter -- no row is removed): each hit also carries `likely_slug`, `separators` (count of `-` and `_` in the token) and `longest_alpha_segment` (length of the longest separator-delimited all-letter segment, 0 if none). Rule: `likely_slug = separators >= 2 OR any separator-delimited segment all-alphabetic and >= 5 chars`. Rule tuned on seven tokens, three of them real: a sample, not a validation (Professional, 2026-09-02). Rows are ordered likely_slug=no first, so the tokens most worth a human read come first.

| shape | hits | likely_slug=no | likely_slug=yes |
|---|---|---|---|
| GOOGLE-DRIVE-ID | 0 | 0 | 0 |
| GOOGLE-FILE-ID | 0 | 0 | 0 |
