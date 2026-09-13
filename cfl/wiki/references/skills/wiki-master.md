---
title: "wiki-master — accumulated session record"
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-REF-SKILLS"
kind: skill-record
skill: wiki-master
status: v1
created: 2026-08-07
corpus_current_through: export 2026-08-06 (1,214 indexed at run time; 1,179 re-read; disk audit over 157 tracked source pages)
generated_by: scripts/audit/skill_record_ext.py --skill wiki-master (counts) + hand-verification (verdicts)
aliases:
  - "add to wiki"
  - "ingest this"
  - "add and ingest"
  - "query the wiki"
  - "lint the wiki"
  - "what does the wiki say about"
  - "source page"
  - "key claims"
  - "fidelity tag"
  - "verbatim paraphrase reconstructed contextual"
  - "citation quality"
  - "the wiki should help you improve the skill"
  - "standard update"
  - "count gate"
  - "PARTIAL registry"
---

# wiki-master — accumulated session record

**Why this page exists.** Jon, verbatim, 2026-08-06:

> *"For each skill, in the wiki, accumulated session record. Not just explicit uses, but implicit
> ones. Opportunitys where you might have considered using it but did not, and cases where you did
> and cases where you kinda did… the wiki shpuld help you improve the skill."*

Regenerate with `python scripts/audit/skill_record_ext.py --skill wiki-master`.

---

## 0. Why the corpus is the wrong place to look for this skill

wiki-master's product is a **file**. A transcript contains a source page's shape only if the
assistant also *pasted* it into the conversation — the same blindness the `handoff` record
documents. But wiki-master differs from handoff in the decisive way: **its artifacts are tracked, in
this repo, and every one can be graded against the skill's own written schema.**

The evidence for how blind the corpus is:

| | count |
|---|---|
| transcripts pasting a `## Key Claims` heading | **2** of 1,179 |
| source pages actually on disk | **157** |

**Two.** The gap is not a finding about wiki-master; it is a finding about the instrument. Source
pages are written through tool calls, where the headings sit inside escaped JSON payloads and never
appear at the start of a line. **So the primary measure on this page is the disk audit, and the
corpus figures are printed beside it and never reconciled into one number.**

`corpus_index` reports **UNDECLARED / USED 0 / ANU 70 files** (293 turn-occasions), computed from the
richest generated trigger list of any CFL skill — *"add and ingest"*, *"ingest this"*,
*"query the wiki"*, *"lint the wiki"*, *"what does the wiki say about"*, *"wiki master"*. That ANU of
70 is the second-highest in the corpus and it is measuring **sessions where Jon said one of those
phrases and no page-shape was pasted** — which, given the paragraph above, is close to all of them.
It is reported and it is not load-bearing.

---

## 1. The disk audit — 157 tracked source pages, graded against SKILL.md

### Required sections

SKILL.md's *"Source page section schema (confirmed 2026-05-27)"* names three sections as **Required**
and marks `## Conflicts` *"Always present — ingest is incomplete without this."*

| | count | of 157 |
|---|---|---|
| **carrying all three required sections** | **126** | **80.3%** |
| missing `## Summary` | 21 | 13.4% |
| missing `## Key Claims` | 27 | 17.2% |
| missing `## Conflicts` | 27 | 17.2% |

**31 of 157 pages are incomplete by the skill's own definition of complete.**

One thing the audit expected to find and did not: **`## Conflicts` present but empty — 0 pages.**
SKILL.md requires the word *"None."* written explicitly rather than left blank, and where the section
exists, it is always filled. **The failure mode is omitting the section, never leaving it hollow.**

### Conditional sections — presence, not compliance

| section | present |
|---|---|
| `Entities & Concepts` | 132 of 157 |
| `Uncaptured Content` | 72 of 157 |
| `Cross-Wiki` | 19 of 157 |

**No rate is computed for these and none should be.** Their rule is *"Include when 2+ named
entities appear"* / *"when material content was excluded"* — conditions on content. A missing
conditional section is not a defect, and treating it as one would manufacture 100+ false findings.

### The conflict rule

**5 of 157 pages carry a `CONFLICT:` marker.** SKILL.md: *"Never silently overwrite… write both and
mark `⚠️ CONFLICT:`. Resolution is Jon's job."* Whether 5 is right is not knowable from the pages —
it is the count of conflicts *found*, and a conflict silently overwritten leaves no trace. **This
number has no denominator and is reported without one.**

---

## 2. The finding: a ratified "not optional" rule that changed nothing

SKILL.md, verbatim: **"Every Key Claim carries one fidelity tag. Not optional."** Ratified by Jon
**2026-07-13** as G2, *"fidelity-confidence vocabulary."*

**Because the rule has a birthday, the pages are split at it. A page written before a rule existed is
evidence FOR the rule, never a violation of it** — the same discipline the GBS record applied to its
Rule 8.

| | pages | Key Claim bullets | tagged | rate | pages with **zero** tags |
|---|---|---|---|---|---|
| **BEFORE** 2026-07-13 | 112 | 895 | 121 | **13.5%** | 92 |
| **ON/AFTER** 2026-07-13 | 45 | 306 | 41 | **13.4%** | 23 |
| date UNKNOWN | 0 | 0 | 0 | — | 0 |
| **total** | **157** | **1,201** | **162** | 13.5% | 115 |

> **The before and after rates are 13.5% and 13.4%. Ratification moved the number by one tenth of a
> percentage point, in the wrong direction.**

**Only the ON/AFTER row is a compliance rate.** The other rows are printed so nobody computes one
from the total. And the ON/AFTER row is the one that matters: **23 of 45 post-ratification pages
carry no fidelity tag at all.**

### Where compliance does exist, and when it started

Only **4 of the 45** post-ratification pages carry any tag, and they are not evenly imperfect:

| page | tagged / bullets |
|---|---|
| `sources/infrastructure/document-capture-and-record-integrity-2026-08-01-a85aea.md` | **22 / 23** |
| `sources/infrastructure/fable-mirror-first-extended-deployment-2026-08-01-a4db57.md` | **16 / 16** |
| `sources/infrastructure/wiki-master-triple-su-self-audit-2026-07-18-922df2.md` | 2 / 10 |
| `sources/infrastructure/coordinator-mirror-pipeline-ratifications-…-2026-07-21-1ad477.md` | 1 / 18 |

**The two compliant pages are both dated 2026-08-01 and both are essentially perfect (16/16 and
22/23).** The rule did not diffuse gradually; it went from unused to fully used, in two pages,
**nineteen days after ratification.** Everything between 2026-07-13 and 2026-08-01 is at or near
zero — including `wiki-master-su-capture-only-2026-07-13-96e1c2.md`, a page written by wiki-master
**on the day of ratification**, with 10 untagged bullets.

**One corroboration, found while registering these pages in `wiki/index.md` and worth more than it
looks.** `scripts/lint_untracked_wiki.py` reported exactly three source pages on disk with no index
row — and **two of the three are `a85aea` and `a4db57`, the two fully-tagged pages.** The batch that
hit the citation-quality step is the same batch that missed the index-registration step. That is
evidence they came from a **distinct process** rather than from a gradually-improving standard
practice, which sharpens recommendation §5.2 from *"find out what changed"* to *"find out what
produced these two pages, because it did one thing better and one thing worse."* (The three rows were
added and `wiki/index.md`'s Sources header recomputed from disk; `index_counts.py --strict` now reads
`157/157 OK`.)

**That is the actionable shape.** This is not "the rule is being partially followed." It is "the rule
was ratified, ignored for nineteen days, and then adopted by whatever produced those two pages." The
worth-answering question is what changed on 2026-08-01 — and this record cannot answer it.

### The worst post-ratification pages, by size

`tree-search-generation-j-layer-licensing-2026-07-17-5d2f71` (31 bullets, 0 tagged) ·
`self-improvement-framework-triage-roadmap-2026-07-17-44a95b` (21) ·
`docker-isolation-planner-packet-a-work-order-2026-07-18-a8bbda` (17) ·
`corpus-remediation-program-design-2026-07-13-ca3309` (15) ·
`blind-self-sitting-incognito-2026-07-18-3ee22d` (13) ·
`blind-self-sitting-memory-on-2026-07-18-48f858` (13) ·
`corpus-loss-audit-2026-07-19` (13).

**The two `blind-self-sitting` pages are consciousness-experiment records** — the class of page where
the difference between `verbatim` and `reconstructed` carries the most weight, and where the tag is
therefore worth the most.

---

## 3. The defect this audit found in itself, and why it is on the page

**The first version of the section slicer cut `## Key Claims` at the next `^#{2,3}` heading.** A
`###` *subheading inside* Key Claims therefore truncated the section. It reported **919 bullets / 81
tagged** instead of the true **1,201 / 162**.

The damage was not a uniform undercount. **It deleted claims non-uniformly, because the pages that
subdivide their claims into `###` groups are the long, careful ones** — exactly the pages most likely
to carry tags. Uncorrected, this page would have published a post-ratification compliance rate of
**0.6%** and a headline reading *"the ratification produced one tagged bullet in twenty-five days."*

**The real figure is 13.4%, and the real finding is the opposite in character: not near-total
non-compliance, but a rule that did not move a number it should have moved.** Slicing is now
level-aware, and the correction is recorded here rather than quietly applied, because a 0.6% would
have been believed.

---

## 4. What the corpus does say

| | count |
|---|---|
| transcripts scanned | 1,179 of 1,214 indexed |
| transcripts pasting a `## Key Claims` shape | 2 |
| fidelity tags emitted **anywhere** in transcripts | **4,949** |
| `CONFLICT:` markers emitted in transcripts | 100 |
| transcripts naming the ingest **count gate** | 30 |
| transcripts naming the **PARTIAL registry** | 18 |

**4,949 tags emitted in transcripts against 162 that landed on a page.** That ratio is not a finding
about loss — the vast majority of those 4,949 are the vocabulary being *discussed*, quoted from
SKILL.md, or used in agent reports rather than in source pages. **It is stated to show why the corpus
figure cannot be used as a proxy for the disk figure**, in either direction.

**The count-gate and PARTIAL-registry rows are string counts in prose.** A session that ran the gate
silently and a session that merely named it are identical to this instrument. Both rows are upper
bounds on *discussion*, not evidence of *execution*, and they are labelled that way in the tool
output too.

---

## 5. What this record says should change about wiki-master

**None ratified. All are proposals for skills-master and a Jon Gate.**

1. **The fidelity tag needs a lint, not a sentence.** *"Not optional"* has been in SKILL.md since
   2026-07-13 and moved compliance from 13.5% to 13.4%. **A rule that a ratification cannot move is
   a rule that needs an instrument.** The check is three lines — every bullet under `## Key Claims`
   on a page dated on/after 2026-07-13 must match one of the six qualities — and it fits the existing
   blocking-lint pattern (`verify_quotes.py`, `lint_skills.py`). *Falsifier:* if the two 2026-08-01
   pages turn out to have been tagged by a process that is now standard, the rule is already
   self-correcting and a lint would only confirm it.

2. **Find out what happened on 2026-08-01.** Two pages, 22/23 and 16/16, after nineteen days of
   nothing. Whatever produced them is the intervention that worked, and this record could not
   identify it from the page contents. **That is a one-query question for the corpus and it is worth
   asking before building the lint in (1)** — an existing working practice beats a new instrument.

3. **31 of 157 pages are missing a required section.** `## Conflicts` is absent from 27, and SKILL.md
   says *"ingest is incomplete without this."* Either those 27 pages are incomplete ingests that
   should be finished, or the schema's "Required" is aspirational and should say so. **The audit
   cannot tell which, and both answers are actionable in different directions.**

4. **Declare a marker for `corpus_index`.** `wiki-master` has the richest trigger list of any CFL
   skill and **no declared marker**, so its file-scoped USED reads 0 and its ANU of 70 is the second
   largest in the corpus while measuring almost nothing. The marker cannot be the page headings —
   §0 shows why. **It should be the artifact:** a source page's existence in `wiki/sources/` with a
   date matching the session's. That is a join `corpus_index` cannot currently express, and saying so
   is more useful than declaring a string that will not work.

5. **The count gate and the PARTIAL registry leave no trace.** Both are mandatory startup steps and
   both are invisible except as prose. If either matters — and the count gate exists because ingests
   were silently partial — **it should emit a line with a number in it**, which turns an unobservable
   obligation into a countable one. *(Same class as recommendation 5 on the `session-order` record;
   this program's mandatory reads are consistently unmarked.)*

---

## 6. What this record cannot see — UNKNOWN, never zero

1. **Whether a source page is TRUE.** Schema conformance is a shape test. Whether the Key Claims
   faithfully represent the session is precisely the judgment the fidelity tag exists to *disclose* —
   and a tag's **accuracy** is not checkable from the page. A page tagged 22/23 `verbatim` could be
   22/23 wrong.
2. **Ingest decisions that went the other way.** A session correctly SKIPPED is indistinguishable
   here from a session never seen. The skip registry, not this page, holds that record.
3. **The conditional sections, as compliance.** §1. Presence only.
4. **The count gate and PARTIAL registry as ACTIONS.** §4. Upper bounds on discussion.
5. **`wiki/personal/`, `wiki/home/`, `wiki/pro/`.** Out of scope by construction — this record does
   not write to them and does not grade them. Their conformance is **UNKNOWN**.
6. **Pages deleted or superseded.** The disk audit sees the current tree only. A page that was
   written non-conforming and later fixed, and a page that was always right, are the same row.
7. **Anything outside the export.** The corpus grew from 1,172 to 1,214 rows during this record's
   run; counts move with it, which is why every figure carries its denominator.

---

*Counts generated by `scripts/audit/skill_record_ext.py`, which registers into
`skill_record.RECORDS` rather than forking it. Self-test 82 controls, 0 failures, negative controls
first, including a control that the fidelity rule is split at its ratification date and one that
every graded page carries a parsed date or the literal `UNKNOWN` — never a guess. The disk audit
reads `wiki/sources/` and writes nothing. Verdicts are hand-made. No skill text was modified by this
page; nothing here is ratified.*
