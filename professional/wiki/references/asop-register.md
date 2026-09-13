---
title: ASOP register — what is on disc, whether it is current, and which ones actually bind Jon's work
name: asop-register
created: 2026-08-23
kind: reference
owner: professional
---

# The ASOPs are on disc, they are current, and until today they were not retrievable

> ⛔ **ADDED 2026-09-04 (branch of `bdbb3dc0`, P4-5) — `GBS` RESOLVES, AND THE SKILL'S ASOP POINTER DOES NOT.**
> **`GBS` = `ground-before-stating`.** Jon confirmed the expansion 2026-07-26 (CFL `wiki/tracker/questions-for-jon.md:153`);
> the skill's own frontmatter says *"Invoke with `/gbs`"*. Skill path, machine-global: `~/.claude/skills/ground-before-stating/`
> (identical copies in `N:\claude-cfl\clone\skills\` and CFL's G: tree; **no trunk-local copy in Professional, Personal,
> Secretary or Antigravity**). It cites **ASOP 1, 23, 25, 41** and is where every trunk meets the ASOPs.
> ⛔ **Its `references/sources.md:17-21` points at `raw/references/asops/` — a directory that no longer exists in CFL's
> clone.** `[m 2026-09-04]` **This trunk's `raw/asops/{pdf,txt}` (57 + 57, `MANIFEST.tsv`) is the only live ASOP corpus
> found on this machine.** Proposal to repoint the skill sent to CFL through the outbox the same hour — never an edit of
> their skill. ⚠️ **And the search-population lesson, recorded so it is not paid a fourth time: on 2026-09-04 this seat
> wrote "I cannot expand the acronym from any primary in this corpus" after searching `wiki/` and `exchange/` and never
> `~/.claude/skills/`.** A search that skips a venue is a search of the other venues.

**Jon, 2026-08-23:** *"You should know the relevent ASOPS. You should have them on disc. If you
can't find them, that is a huge professionalism issue."*

⭐ **Both halves answered, and they answer differently.** `[measured 2026-08-23]` **57 ASOPs on
disc** — 57 PDFs and 57 `.txt` extractions under `raw/asops/`, fetched by `scripts/fetch_asops.sh`
around 2026-08-07. **Presence: fine.** ⛔ **Findability: it was the real defect.** This trunk's
retrieval index deliberately excluded `raw/`, so a query about a standard returned nothing while
the standard sat in the tree. **Reachable is not retrieved** — this trunk's own standing rule,
failing against its own core reference library. **Fixed today: the ASOP texts are indexed as a
`standards` tier.**

## Currency — checked against the ASB, not assumed

**Official list fetched 2026-08-23 from `actuarialstandardsboard.org/standards-of-practice/`.**

| check | result |
|---|---|
| ASOPs on the official list | **57** |
| ASOPs on disc | **57** |
| **on the list and MISSING from disc** | ⭐ **0** |
| on disc but not on the list | **0** |
| text extractions garbled or truncated | **0** |
| number sequence | 1–46 and 48–58 |

⛔ **ASOP 47 IS NOT A GAP, and reading it as one would be this trunk's own defect-of-the-day.**
47 was repealed **jointly with 46** in December 2024 (superseded by ASOP 58, Enterprise Risk
Management), and the joint repeal notice is on disc as `asop046and047repeal_219.txt`. **The
sequence has a hole; the library does not.**

⚠️ **THE TRAP IN THIS COMPARISON, and it would have produced a false staleness report.** The dates
printed **inside** the documents are **ADOPTION** dates. The dates on the ASB website are
**EFFECTIVE** dates. They differ systematically — ASOP 58 was *adopted* December 2024 and became
*effective* May 2025; ASOP 7 was *adopted* December 2025 and became *effective* June 2026. **A
naive column-against-column diff would have reported most of the library as stale.** It is not:
both June-2026-effective standards (**7** and **20**) are the current editions on disc, because the
2026-08-07 fetch post-dates them. **Measuring one object and claiming about another** —
the same discipline named elsewhere in this wiki today.

⚠️ **Bound on the currency claim:** it rests on one fetch of one page on one day. **It is true as of
2026-08-23 and it decays silently.** `scripts/fetch_asops.sh` is the re-check; nothing schedules it.

## ⭐ The CORE list — the part that is actually useful

A register that treats 57 standards as equally relevant has not helped anybody. **Jon is an FCAS in
Management Liability, Fidelity/Crime, Cyber, Information Risk and Financial Institutions.** These
are the ones that bind most of what he does:

| # | standard | why it is CORE |
|---|---|---|
| **1** | Introductory Actuarial Standard of Practice | the meta-standard — defines *deviation*, *materiality*, and how every other ASOP is to be read |
| **12** | Risk Classification (for All Practice Areas) | risk classification is the substance of underwriting and pricing in every specialty line he writes |
| **13** | Trending Procedures in Property/Casualty Insurance | trending is a P/C ratemaking primitive and its judgement calls are exactly where reviewers land |
| **23** | Data Quality | data quality — the standard that governs the input to every model and every reserve he signs |
| **25** | Credibility Procedures | credibility — his own default analytical frame; the standard that constrains how he blends it |
| **29** | Expense Provisions for Prospective Property/Casualty Risk Transfer and Risk Retention | expense provisions in prospective P/C risk transfer — direct to specialty-lines pricing |
| **30** | Treatment of Profit and Contingency Provisions and the Cost of Capital in P/C Ratemaking | profit and contingency plus cost of capital in P/C ratemaking — the other half of the rate |
| **38** | Catastrophe Modeling (for All Practice Areas) | catastrophe modeling, all practice areas — the binding standard for cyber accumulation work |
| **39** | Treatment of Catastrophe Losses in Property/Casualty Insurance Ratemaking | catastrophe losses in P/C ratemaking — the ratemaking counterpart to 38 |
| **41** | Actuarial Communications | actuarial communications — binds the *form* of every work product he issues, without exception |
| **43** | Property/Casualty Unpaid Claim Estimates | P/C unpaid claim estimates — the reserving standard for his lines |
| **53** | Estimating Future Costs for Prospective P/C Risk Transfer and Risk Retention | estimating future costs for prospective P/C risk transfer — the pricing standard for his lines |
| **56** | Modeling | modeling — governs model design, testing, and reliance; binds nearly everything he builds |

**Thirteen of fifty-seven.** ⭐ **All thirteen are on disc and all thirteen are current.** There is
no CORE-class standard missing from this library — that is the headline finding, and it is a pass.

**Seven more are SITUATIONAL** — they bind real work he does, but episodically rather than daily:

| # | standard | when it binds |
|---|---|---|
| 17 | Expert Testimony by Actuaries | expert testimony — live whenever ML/professional-lines work reaches litigation support |
| 19 | Appraisals of Casualty, Health, and Life Insurance Businesses | appraisals of casualty/health/life businesses — M&A and portfolio-transfer work |
| 20 | Analysis of Property/Casualty Cash Flows, Including Discounting | P/C cash flows including discounting — binds when discounting enters reserving or pricing |
| 21 | Responding to or Assisting Auditors or Examiners | responding to auditors and examiners — binds at audit and exam interactions |
| 36 | Statements of Actuarial Opinion Regarding P/C Loss, LAE, or Other Reserves | statements of actuarial opinion on P/C reserves — binds only if he signs or supports an opinion |
| 55 | Capital Adequacy Assessment | capital adequacy assessment — binds FI and information-risk capital work |
| 58 | Enterprise Risk Management | enterprise risk management — the FI/ERM standard; replaced the repealed 46 and 47 |

## How to actually read one

```bash
bash scripts/graphrag.sh asop "how much documentation does a reviewer need to reproduce my work"
```

⚠️ **Retrieval finds the passage; it does not read the standard for you.** For anything that will be
relied on, open the PDF — `raw/asops/pdf/` — because the `.txt` extraction loses tables and the
appendices that carry most of the worked guidance.

## The full register

**`state` is a measured property of the text extraction, not a judgement about the standard.**
`INTACT` means the extracted text is prose with a plausible alphabetic ratio and the word
"Actuarial" present in its head; the five shortest files were opened by hand and confirmed to be
**repeal notices, not truncations.**

| # | class | title | adopted (in doc) | effective (ASB) | txt bytes | state |
|---|---|---|---|---|---|---|
| 1 | CORE | Introductory Actuarial Standard of Practice | March 2013 | 2013-06-01 | 60,521 | INTACT |
| 2 | OUT-OF-SCOPE | Nonguaranteed Elements for Life Insurance and Annuity Products | September 2021 | 2022-06-01 | 77,310 | INTACT |
| 3 | OUT-OF-SCOPE | Continuing Care Retirement Communities and At Home Programs | September 2021 | 2022-06-01 | 83,603 | INTACT |
| 4 | OUT-OF-SCOPE | Measuring Pension Obligations and Determining Pension Plan Costs or Contributions | December 2021 | 2023-02-15 | 100,812 | INTACT |
| 5 | OUT-OF-SCOPE | Incurred Health and Disability Claims | March 2017 | 2017-09-01 | 65,540 | INTACT |
| 6 | OUT-OF-SCOPE | Measuring Retiree Group Benefits Obligations | May 2014 | 2015-03-31 | 222,976 | INTACT |
| 7 | OUT-OF-SCOPE | Life or Health Cash Flow Analysis | December 2025 | 2026-06-01 | 62,664 | INTACT |
| 8 | OUT-OF-SCOPE | Regulatory Filings for Health Benefits, Accident and Health Insurance | March 2014 | 2014-09-01 | 85,682 | INTACT |
| 9 | REPEAL | Documentation and Disclosure in P/C Ratemaking, Reserving, and Valuations | March 2011 | REPEALED 2011-05-01 | 16,206 | INTACT |
| 10 | OUT-OF-SCOPE | U.S. GAAP for Long-Duration Life, Annuity, and Health Products | December 2022 | 2023-05-01 | 59,875 | INTACT |
| 11 | OUT-OF-SCOPE | Treatment of Reinsurance or Similar Risk Transfer Programs (Life/Annuity/Health) | April 2021 | 2022-12-01 | 83,330 | INTACT |
| 12 | CORE | Risk Classification (for All Practice Areas) | December 2005 | 2006-05-01 | 66,303 | INTACT |
| 13 | CORE | Trending Procedures in Property/Casualty Insurance | June 2009 | 2009-11-01 | 37,631 | INTACT |
| 14 | REPEAL | When to Do Cash Flow Testing for Life and Health Insurance | September 2001 | REPEALED 2002-04-15 | 2,350 | INTACT |
| 15 | OUT-OF-SCOPE | Dividends for Individual Participating Life Insurance, Annuities, and Disability Insurance | March 2006 | 2006-08-01 | 54,235 | INTACT |
| 16 | REPEAL | Actuarial Practice Concerning Health Maintenance Organizations | April 2007 | REPEALED 2007-04-26 | 14,469 | INTACT |
| 17 | SITUATIONAL | Expert Testimony by Actuaries | June 2018 | 2018-12-01 | 37,447 | INTACT |
| 18 | OUT-OF-SCOPE | Long-Term Care | March 2022 | 2022-09-01 | 54,756 | INTACT |
| 19 | SITUATIONAL | Appraisals of Casualty, Health, and Life Insurance Businesses | June 2005 | 2005-11-01 | 41,789 | INTACT |
| 20 | SITUATIONAL | Analysis of Property/Casualty Cash Flows, Including Discounting | December 2025 | 2026-06-01 | 62,809 | INTACT |
| 21 | SITUATIONAL | Responding to or Assisting Auditors or Examiners | September 2016 | 2016-12-15 | 68,258 | INTACT |
| 22 | OUT-OF-SCOPE | Statements of Actuarial Opinion Based on Asset Adequacy Analysis | September 2021 | 2022-06-01 | 62,463 | INTACT |
| 23 | CORE | Data Quality | December 2016 | 2017-04-30 | 51,075 | INTACT |
| 24 | OUT-OF-SCOPE | NAIC Life Insurance Illustrations Model Regulation | September 2024 | 2024-12-01 | 52,986 | INTACT |
| 25 | CORE | Credibility Procedures | December 2013 | 2014-05-01 | 32,205 | INTACT |
| 26 | OUT-OF-SCOPE | Actuarial Certification of Small Employer Health Benefit Plans | October 1996 | 1997-01-01 | 54,786 | INTACT |
| 27 | OUT-OF-SCOPE | Selection of Assumptions for Measuring Pension Obligations | December 2023 | 2025-01-01 | 106,742 | INTACT |
| 28 | OUT-OF-SCOPE | Statements of Actuarial Opinion Regarding Health Insurance Assets and Liabilities | April 2024 | 2024-10-01 | 67,919 | INTACT |
| 29 | CORE | Expense Provisions for Prospective Property/Casualty Risk Transfer and Risk Retention | December 2023 | 2024-07-01 | 43,730 | INTACT |
| 30 | CORE | Treatment of Profit and Contingency Provisions and the Cost of Capital in P/C Ratemaking | July 1997 | 1997-12-01 | 51,560 | INTACT |
| 31 | REPEAL | Actuarial Content of Financial Statements of Insurance Companies | June 2009 | REPEALED 2009-06-30 | 12,839 | INTACT |
| 32 | OUT-OF-SCOPE | Social Insurance | June 2020 | 2021-09-01 | 54,771 | INTACT |
| 33 | OUT-OF-SCOPE | Closed Blocks in Mutual Life Insurance Company Conversions | January 1999 | 1999-06-01 | 46,244 | INTACT |
| 34 | OUT-OF-SCOPE | Retirement Plan Benefits in Domestic Relations Actions | June 2015 | 2015-12-01 | 80,666 | INTACT |
| 35 | REPEAL | Selection of Demographic and Other Noneconomic Assumptions for Pension Obligations | June 2024 | REPEALED 2025-01-01 | 3,219 | INTACT |
| 36 | SITUATIONAL | Statements of Actuarial Opinion Regarding P/C Loss, LAE, or Other Reserves | March 2024 | 2024-10-01 | 57,594 | INTACT |
| 37 | OUT-OF-SCOPE | Allocation of Policyholder Consideration in Demutualizations | June 2000 | 2000-12-15 | 60,596 | INTACT |
| 38 | CORE | Catastrophe Modeling (for All Practice Areas) | July 2021 | 2021-12-01 | 37,203 | INTACT |
| 39 | CORE | Treatment of Catastrophe Losses in Property/Casualty Insurance Ratemaking | June 2000 | 2000-12-15 | 51,685 | INTACT |
| 40 | OUT-OF-SCOPE | NAIC Valuation of Life Insurance Policies Model Regulation X Factors | March 2024 | 2024-09-15 | 45,483 | INTACT |
| 41 | CORE | Actuarial Communications | December 2010 | 2011-05-01 | 59,617 | INTACT |
| 42 | OUT-OF-SCOPE | Health and Disability Actuarial Assets and Liabilities Other Than Incurred Claims | March 2018 | 2018-08-01 | 63,620 | INTACT |
| 43 | CORE | Property/Casualty Unpaid Claim Estimates | June 2007 | 2007-09-01 | 77,620 | INTACT |
| 44 | OUT-OF-SCOPE | Selection and Use of Asset Valuation Methods for Pension Valuations | September 2007 | 2008-03-15 | 50,887 | INTACT |
| 45 | OUT-OF-SCOPE | The Use of Health Status Based Risk Adjustment Methodologies | January 2012 | 2012-07-01 | 45,390 | INTACT |
| 46 | REPEAL | Repeal of ASOP 46 and ASOP 47 (superseded by ASOP 58) | December 2024 | REPEALED 2025-05-01 (with 47) | 2,471 | INTACT |
| 48 | OUT-OF-SCOPE | Life Settlements Mortality | December 2013 | 2014-04-30 | 69,991 | INTACT |
| 49 | OUT-OF-SCOPE | Medicaid Managed Care Capitation Rate Development and Certification | March 2015 | 2015-08-01 | 93,681 | INTACT |
| 50 | OUT-OF-SCOPE | Determining Minimum Value and Actuarial Value under the ACA | September 2015 | 2016-01-31 | 47,999 | INTACT |
| 51 | OUT-OF-SCOPE | Assessment and Disclosure of Risk Associated with Measuring Pension Obligations | September 2017 | 2018-11-01 | 78,295 | INTACT |
| 52 | OUT-OF-SCOPE | Principle-Based Reserves for Life Products under the NAIC Valuation Manual | September 2017 | 2017-12-31 | 110,007 | INTACT |
| 53 | CORE | Estimating Future Costs for Prospective P/C Risk Transfer and Risk Retention | December 2017 | 2018-08-01 | 59,995 | INTACT |
| 54 | OUT-OF-SCOPE | Pricing of Life Insurance and Annuity Products | June 2018 | 2018-12-01 | 69,643 | INTACT |
| 55 | SITUATIONAL | Capital Adequacy Assessment | June 2019 | 2019-11-01 | 47,469 | INTACT |
| 56 | CORE | Modeling | December 2019 | 2020-10-01 | 106,369 | INTACT |
| 57 | OUT-OF-SCOPE | Statements of Actuarial Opinion Not Based on an Asset Adequacy Analysis | January 2023 | 2023-06-15 | 30,317 | INTACT |
| 58 | SITUATIONAL | Enterprise Risk Management | December 2024 | 2025-05-01 | 43,774 | INTACT |

## ⛔ Two defects found in the library's own metadata while building this

1. **Six rows of `raw/asops/MANIFEST.tsv` have a corrupted `url` field.** ASOPs **9, 14, 16, 31, 35
   and 46** carry the literal string `asops, downloaded 2026-08-05]` where a URL belongs — a
   fragment of prose written into a data column, in the six rows whose `status` is `from-cfl`.
   ⚠️ **The consequence is not cosmetic: the obvious way to join the manifest to the files on disc
   is by URL stem, and that join silently drops exactly those six** — it reported them as missing
   text extractions when all six are present and intact. **The first scan run for this register
   made that error and it was caught only by counting both sides.** Joining by the number in the
   filename is correct; joining by URL is not.
2. **The manifest has no fetch date and no effective-date column**, so currency cannot be assessed
   from it at all — which is why the check above needed a live web fetch. **A reference library
   whose manifest cannot answer "is this current" is a library that has to be re-verified by hand
   every time.** Proposed columns: `fetched_utc`, `adopted`, `effective`, `superseded_by`.

Neither is fixed here. **Both are ticketed rather than repaired in passing**, because `MANIFEST.tsv`
is `fetch_asops.sh`'s output and editing the artifact without fixing the generator produces a file
that reverts on the next run.
