# Ground Before Stating — Sources

Maintained by skills-master. Read before extending GBS to new ASOP content or adding literature citations.

---

## Must Include — Foundational (v1)

| Source | Access | URL |
|---|---|---|
| ASOP 1, *Introductory Actuarial Standard of Practice* (ASB, 2013) | Fetchable — HTML | `actuarialstandardsboard.org/asops/introductoryactuarialstandardpractice/` |
| RFC 2119 (IETF, 1997) | Fetchable | `rfc-editor.org/info/rfc2119/` |
| "The Polite Liar: Epistemic Pathology in Language Models" | Fetchable | `arxiv.org/pdf/2511.07477` |
| Xu et al., "Confronting Verbalized Uncertainty," *IJHCS* (2025) | Fetchable | `doi.org/10.1016/j.ijhcs.2024.103363` |
| ASB article: "Must, Should, May: Small Words, Huge Implications" | Fetchable | `actuarialstandardsboard.org/profcounts/must-should-may-small-words-huge-implications/` |

**Note — CORRECTED 2026-08-07. Read the local copy; do not fetch.** ASOP PDFs are **on disk**:
`raw/references/asops/` — **57 ASOP PDFs + `MANIFEST.json`**, downloaded 2026-08-05 21:22–21:23
(`ls raw/references/asops/*.pdf | wc -l` → 58, of which 1 is
`Actuarial-Standards-Setting-Process.pdf`). Claude Professional holds an independent set of 57 at
`raw/asops/pdf/`. ASOP 1 is `raw/references/asops/asop001_170.pdf`.

The line this replaces read *"inaccessible via automated fetch"* and was true when written
(2026-06-27, PM session `a6314b` — the robots.txt block is the worked example in
`worked-examples.md:11`). **It stayed on the page for two days after the files landed.** A fetch
verdict is a fact about a moment; a skill that records one without a re-check turns a transient
blocker into a permanent one. **The remedy for "blocked by robots.txt" was never a different URL —
it was a copy on disk, and the copy existed.**

The HTML pages below remain valid and are still the right cite for a *published-location* claim.
The PDF slug pattern `asop001_170.pdf` is real; it is simply not reachable by automated fetch.

---

## Should Include — Supporting Evidence (v1)

| Source | Access | URL |
|---|---|---|
| Kent, "Words of Estimative Probability," *Studies in Intelligence* (1964) | Fetchable — declassified | `cia.gov/readingroom/docs/CIA-RDP86T00268R000700080006-2.pdf` |
| Kuhn et al., "Semantic Uncertainty," ICLR (2023) | Fetchable | `arxiv.org/abs/2302.09664` |
| Mielke et al., "Teaching Models to Express Uncertainty in Words," *TMLR* (2022) | Fetchable | `arxiv.org/abs/2205.14334` |
| ASB article: "ASOP No. 1 and Professional Judgment" | Fetchable | `actuarialstandardsboard.org/profcounts/asop-no-1-and-professional-judgment/` |

---

## Training Only — Cite in References; Do Not Fetch

These cannot be fetched in a session. They are cited in `philosophies-and-grounding.md` as literature context. Skills-master must not cite these as live references in SKILL.md or tell Jon to verify them via URL.

| Source | Phil. | Notes |
|---|---|---|
| Austin, *How to Do Things with Words* (1962) | P3 | Foundational speech act theory; constative vs. performative distinction |
| Grice, "Logic and Conversation," *Studies in the Way of Words* (1989) | P3 | Four maxims; Quality maxim = ancestor of reliance disclosure requirements |
| Hyland, *Hedging in Scientific Research Articles* (1998) | P3 | Corpus study; hedging in scientific writing as act-type signal, not confidence signal |
| Garner, *Legal Writing in Plain English* (2001) | P2 | ABC Rule: eliminate "shall"; cautionary tale for overloaded modal language |
| Tetlock & Gardner, *Superforecasting* (2015) | P1 | Calibrated verbal probability; the three-bin problem; superforecasters vs. pundits |

---

## Version Roadmap — Sources to Add

**v2 (ASOP 23 — data quality):**
- ASOP 23, *Data Quality* (ASB, revised 2017) — fetch HTML via `actuarialstandardsboard.org/asops/data-quality/`
- CAS Practice Note on Data Quality (most recent year)

**v3 (ASOP 25 — credibility):**
- ASOP 25, *Credibility Procedures* (ASB, effective 2014) — fetch HTML via `actuarialstandardsboard.org/asops/credibility-procedures/`

**v4 (ASOP 41 — communications):**
- ~~ASOP 41 final text — not yet available as of 2026-06-27 (third exposure draft, comment deadline June 1 2026, not yet finalized)~~ **struck 2026-09-06: the sentence was true of the REVISION and false of the STANDARD. ASOP No. 41 (December 2010) is in force and available at `N:/claude-professional/raw/asops/txt/asop041_120.txt` (59,617 B) — ingestable now.** (Herald 6c509f4d)
- ASOP No. 41 **revision** — third exposure draft, comment deadline June 1 2026; monitor `actuarialstandardsboard.org` for adoption; **do not ingest the exposure draft as final** (guard kept)
