---
title: "Source-page repair contract v1 — what a repair MAY and MAY NOT change"
kind: reference
status: ADOPTED 2026-09-03 04:2x by CFL main seat as UC-0 task (2); text is Antigravity's 2026-09-02 draft (N:\claude-gists-private\source-page-repair-contract-v1.md, 2008 B) checked clause-by-clause against the UC-0 brief; CFL edits are marked [CFL]
provenance: intake via UC-0 brief (Jon 2026-09-02, "yes-ish" -> tickets); not a Jon ruling; the forbidden-region clauses restate standing rules (typos his; no emphasis inside quotes; no deletion; never invent a hash)
---

# Source-page repair contract v1

> **Canonical Source Page Repair Contract (v1.0): Boundary rules, permitted mutations, forbidden regions, and automated acceptance gates for batch repairing historical Class C/D wiki source pages.**

---

## 1. Allowed Modifications (Permitted Mutations)

A repair agent MAY modify ONLY the following explicit regions:
1. **Frontmatter Metadata (`---` to `---`):**
   - Standardizing canonical keys: `title`, `slug`, `trunk`, `kind: source`, `source_kind`, `uuid6`, `date`, `source_file`, `raw_sha256`, `raw_length`, `generated_by`, `state`, `probe_sealed`.
   - Computing exact `raw_sha256` and `raw_length` directly from the raw transcript file bytes on disk.
2. **Structural Anchors & Fidelity Tags:**
   - Adding `:T<n>` turn anchors and fidelity calibration tags, ~~`([measured]`, `[relayed]`, `[recalled]`, `[SEM]`, and lint E3 vocabulary `[verbatim]`, `[paraphrase]`, `[reconstructed]`, `[contextual]`, `[inferred]`, `[uncaptured]`, with comma qualifiers)`~~ in `## Key Claims`. **Struck 2026-09-04, Professional review F5 (this letter is a re-review of a 2026-09-03 disposition that widened the enumeration instead of pointing to the authority; the same class of drift Professional predicted was already measurable — `TAG_RE` also accepts `MIRROR-INFERENCE`, which this enumeration omitted).** The set of allowed tags is `TAG_RE` in `scripts/audit/repair_diff_check.py:29-31` — the single authority; a repair MAY use any tag that pattern accepts, and no second list is maintained here.

     ```
     TAG_RE = re.compile(r'\[(?:measured|relayed|recalled|SEM|MIRROR-INFERENCE|'
                         r'(?:TRANSCRIPT|THINKING-SUMMARY|COMPACT-SUMMARY):[0-9]{4}-[0-9]{2}-[0-9]{2}[0-9T:Z.+\- ]{0,20}|'
                         r'(?:verbatim|paraphrase|reconstructed|contextual|inferred|uncaptured)(?:\s*,\s*' + _QUAL + r'){0,2})\]')
     ```
3. **Resolvable Wikilinks:**
   - Converting bare strings to resolvable bidirectional `[[slug]]` or exact AST locators (`file.py#Lstart-Lend`).

---

## 2. Forbidden Regions (Strict Invariants)

A repair agent MUST NEVER:
1. **Never alter or sanitize quoted Jon text** (Verbatim human primaries remain 100% immutable).
2. **Never change the substantive meaning** of historical claims or decisions.
3. **Never perform deletions** of substantive sections outside frontmatter normalizations.
4. **Never invent hashes:** If a raw transcript file is unreachable, mark status as `UNKNOWN` rather than hallucinating a SHA256 digest.

---

## 3. Automated Acceptance Gate

Every repaired page must pass the 3-tier validation harness:
1. **`python scripts/audit/ingest_gate.py --dry-run <page>` prints `[1/6 LINT]   PASS`** (rewritten 2026-09-03 17:2x: the 10:4x replacement named `lint.py --all-kinds`, which disagreed with section 4's bullet; one command now, in both places. Original Antigravity line named `bash scripts/lint.sh`, which does not exist in this tree.)
2. **`python scripts/audit/repair_diff_check.py` $\rightarrow$ Proves zero modifications outside frontmatter/anchors**.
3. **Ingest Gate Verification $\rightarrow$ `ACCEPTED` in `INGEST-LEDGER.md`**.

---

*Staged at `N:\claude-gists-private\source-page-repair-contract-v1.md` for CFL Ultracode workflow.*


---

## 4. [CFL] Amendments at adoption, 2026-09-03

- **Tier 1 command (struck and rewritten 2026-09-03 17:2x, Professional F1 second pass: this bullet and section 3.1 named two different commands).** There is ONE binding Tier 1 check: `python scripts/audit/ingest_gate.py --dry-run <page>` must print `[1/6 LINT]   PASS` (E1k..E10). `python scripts/audit/lint.py --main-root "N:/claude-corpus/cfl" --explain <id6>` is the same lint with per-check explanations, for diagnosis; it is not a second gate. Section 3.1 above now names the gate command; this bullet no longer names a different one.
- **Tier 2 exists now:** `scripts/audit/repair_diff_check.py <before> <after>` (built 2026-09-03 with --selftest) fails when any changed line lies outside frontmatter, a `:T<n>` anchor edit, a fidelity tag, or a `[[slug]]` link conversion.
- **Fixity rot is a repair class, not a page defect:** a page whose `raw_sha256` no longer matches because the transcript was RE-RENDERED after the page was written (S-cd-03 13ffb2, 2026-09-03) is repaired by recomputing from the current transcript file, and the repair report must say the transcript changed, not the page.
- **The pre-stated loss condition from the UC-0 brief stands:** if all pages of a dry run pass with 0 UNKNOWN on the first try, the grader is suspect.

## 5. [CFL] Amendment 2026-09-03 10:4x — anchor verification is REQUIRED (from the UC-0 dry run)

The dry run graded 5 repaired pages: 3 ACCEPTED, 2 REJECTED, and both rejects were one class, `:T<n>` anchors carried forward unverified (bb48e2: one wrong anchor; 0ea25c: three, one of them four turns short). Fixity proved the transcripts had not changed; the anchors were wrong at authoring. §1 allowed anchor changes but nothing required an anchor check.

**Rule (binding on every repair lane from this amendment on):**

1. For every Key Claim carrying a `:T<n>` anchor, take one distinctive phrase of the claim (5+ words; a bare number is NOT a discriminator and must be paired with a word from the claim) and `grep -n` it in the transcript. `python scripts/audit/turn_index.py <raw>` gives the line-to-turn map; use absolute paths and no `cd`.
2. Set `<n>` to the turn that contains the phrase. **If the phrase occurs in more than one turn** (Jon's words are re-quoted by coordinators inside the same session), choose the turn whose speaker matches the claim's attribution (a Jon claim anchors to the Human turn, not to the assistant quoting it) and record every candidate turn in the log. If the phrase is found in no turn, the claim is tagged `[uncaptured]` and loses its anchor rather than keeping a wrong one.
3. The repair report's anchor log has one row per anchored claim, moved or not, with the grep line(s) and the turn: **a verified-unchanged anchor shows its grep line exactly like a moved one does.** A row without a grep line is a skipped check, and the report checker treats it as one.
4. A page with any unverified anchor is not eligible for the gate. A grader FAIL on an anchor after this step is a lane defect UNLESS the page's recorded `raw_sha256` no longer matches the transcript (the re-render class in section 4), in which case it is a fixity defect and the page is re-anchored against the current bytes.

5. **A claim tagged `[verbatim]` must grep exactly** (the quoted string, typos and all, found by `grep -F` in the transcript); if it does not, the tag is `[paraphrase]` and the quotation marks come off. Added 2026-09-03 17:58 from S-cd-05's e6196f reject: T117 material was rendered in words the turn does not contain and presented as a quote. Same rule as CLAUDE.md's "a corrected quote is an unverifiable quote", applied at the repair step where it can be checked mechanically.

(5.1-5.4 amended 2026-09-03 17:1x on Professional's review F2/F3/F4: phrase uniqueness was presupposed, the number branch was the least discriminating, and skipped and verified anchors produced identical reports.)

`repair_diff_check.py` already treats an anchor change as an allowed mutation; this rule makes the change mandatory where the evidence requires it. First test of the rule: re-repair the two rejected pages from `wiki/intake-triage/rejected-pages/` on the next GO.
