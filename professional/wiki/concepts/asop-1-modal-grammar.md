---
title: "ASOP 1's modal grammar, and what ground-before-stating got right and wrong about it"
slug: asop-1-modal-grammar
status: MEASURED — primary source obtained and compared, 2026-08-07
created: 2026-08-07
primary_source: "ASOP No. 1, Introductory Actuarial Standard of Practice, Actuarial Standards Board, adopted March 2013, Doc. No. 170"
source_location: "[PRO] raw/asops/txt/asop001_170.txt (60,521 B) — gitignored; PDF at raw/asops/pdf/asop001_170.pdf"
source_url: http://www.actuarialstandardsboard.org/wp-content/uploads/2013/10/asop001_170.pdf
calibration: "[measured] — this session fetched the PDF, extracted it with pdftotext -layout, and read Section 2 in full. Every quotation below is from that extraction."
resolves: "[CFL] reports/blocker-a6314b-asop-ingest-2026-07-16.md (3rd escalation, open 41 days) — the FETCH half only. The copyright half is NOT resolved."
---

# The 41-day claim, and what checking it cost

**On 2026-06-27 a session designed `ground-before-stating` — the epistemic standard that now governs
every project in this program — by translating ASOP 1's modal grammar into Claude behaviour.** That
session disclosed, in its own frontmatter, against its own interest:

> *"ASOP substantive TEXT is NOT in this raw. ASOP 1's content is present only as Claude's PARAPHRASE
> of a web page it fetched — the PDF was robots-blocked (T8) and the successful web-page fetch's
> tool_result is empty/stripped… **Grounding the confidence-disclosure standard on the actual ASOP
> text remains an unfulfilled sourcing dependency.**"
>
> — `[CFL] wiki/pro/sources/asops-ingestion-planning-2026-06-27-a6314b.md:27-35`

**It was escalated formally three times. It sat for 41 days. It cost one fetch.** `[measured
2026-08-07 08:35 CDT]`

**The generalisable finding is not about ASOPs.** A transient `robots.txt` failure was recorded as a
permanent property of the source — `[CFL] skills/ground-before-stating/references/sources.md:17`, *"The
PDF slug pattern `asop001_170.pdf` exists but is **inaccessible via automated fetch**"* — and **no
session retried it.** The program's own rule, *"a record can be true and stale,"* was the rule it
needed and never applied to this record.

---

# The version trap, which is the finding under the finding

**The ASB currently serves at least two documents that both present as "ASOP No. 1."**

| Document | Where | Status |
|---|---|---|
| **Adopted standard, March 2013, Doc. No. 170** | `/wp-content/uploads/2013/10/asop001_170.pdf` | **CURRENT** |
| **Exposure draft, December 2011** | `/asops/introductory-actuarial-standard-of-practice/` (HTML) | **WITHDRAWN — the page itself is labelled "Past Exposure Draft"** |

**I fetched the HTML page first and got the withdrawn draft.** Its definitions are close enough to the
adopted text to pass an unsuspicious reading, and **materially different in exactly the place that
matters.**

**`[CFL] skills/ground-before-stating/references/sources.md:11` grades ASOP 1 "Fetchable — HTML" and
points at that HTML page.** Whether the 2026-06-27 session fetched that specific URL cannot be
determined from the export — the `tool_result` is stripped. `[unverified — hypothesis, not finding.
CFL can check this and I cannot.]`

**But the paraphrase that ended up in the skill is closer to the withdrawn draft than to the adopted
standard.** See *must*, below.

---

# The side-by-side

## `must` — ❌ MIS-GROUNDED. The judgment moves from the standard-setter to the speaker.

**ASOP 1 §2.1(a) — adopted, verbatim:**

> *"'Must' as used in the ASOPs means that **the ASB does not anticipate that** the actuary will have
> any reasonable alternative but to follow a particular course of action."*

**2011 exposure draft — withdrawn, verbatim:**

> *"'Must' as used in the ASOPs means that, **under the circumstances, the actuary has no reasonable
> alternative** but to follow a particular course of action."*

**`ground-before-stating` SKILL.md:46:**

> *"**Must** = no reasonable alternative **I can see**"*

**In the adopted standard the judgment belongs to the ASB, is made in advance, and is fixed at the
level of the standard. It does not move with the individual actuary's view on the day.** In the skill
it belongs to the speaker, is made in the moment, and is a first-person report of the speaker's own
perceived option set.

**The defect is live, not pedantic: under the skill's rendering, `must` weakens exactly as the
speaker's imagination narrows.** A model that cannot see an alternative says `must`. Under the
standard's rendering, `must` is invariant to the speaker entirely.

**A discipline built to stop a model over-claiming has defined its strongest modal in terms of the
model's own field of view.**

Note also that the skill's phrasing tracks the **withdrawn draft's** "under the circumstances" framing
— speaker-and-situation — rather than the adopted text's attribution to the ASB.

## `may` — ❌ MIS-GROUNDED. Asserts an equivalence the standard explicitly refuses.

**ASOP 1 §2.1(b), verbatim:**

> *"'May' as used in the ASOPs means that the course of action described is one that would be
> considered reasonable and appropriate in **many** circumstances. 'May' in ASOPs is often used when
> providing examples… **It is not intended to indicate that a course of action is reasonable and
> appropriate in all circumstances, nor to imply that alternative courses of action are
> impermissible.**"*

**SKILL.md:48:** *"**May** = one option among several **equally valid**"*

**The standard says nothing about the options being equal.** It says this one is defensible in many
cases and others are not thereby forbidden. **"Equally valid" asserts an equivalence the standard
specifically declines to assert.**

## `should` — ✅ CORRECT, including the subtle part

**SKILL.md:47:** *"**Should** = normally appropriate; deviation permitted with disclosure"*

**ASOP 1 §2.1(a), verbatim:**

> *"the word 'should' indicates what is normally the appropriate practice for an actuary to follow when
> rendering actuarial services… **Failure to follow a course of action denoted by either the term
> 'must' or 'should' constitutes a deviation from the guidance of the ASOP. In either event, the
> actuary is directed to ASOP No. 41, Actuarial Communications.**"*

**This lands, and it captures the thing that is easiest to get wrong.** A missed `should` is a
**deviation requiring disclosure**, not a soft preference — `must` and `should` sit on the **same
side** of the deviation line. The skill has that right.

## `should consider` — ⚠️ MISSING from the shipped skill

**ASOP 1 §2.1(a), verbatim:**

> *"the phrase 'should consider' is often used to suggest potential courses of action. **If, after
> consideration, in the actuary's professional judgment an action is not appropriate, the action is
> not required and failure to take this action is not a deviation from the guidance in the
> standard.**"*

**This is a distinct obligation type — a process obligation with no outcome obligation — and it is the
only one of the four whose breach is *not* a deviation.** It appears in the skill's reference file
(`philosophies-and-grounding.md:56`) and **nowhere in `SKILL.md`**.

**That same reference file records the ASB's own position that the vast majority of ASOP guidance is
`should` or `should consider`.** The skill ships without the term that covers most of the source it
cites.

---

# What checks out — reported with the same care as what does not

| Principle (T52, 2026-06-27) | Verdict against adopted text |
|---|---|
| **2 — "Known" = actual knowledge at time of rendering** | ✅ **VERBATIM-EXACT.** §2.5: *"'known' means that the actuary had actual knowledge of the item in question at the time the actuary rendered actuarial services."* The one fragment CFL graded `[verbatim]` **is** verbatim. |
| **3 — Materiality** | ✅ **ACCURATE.** §2.6: *"An item or a combination of related items is material if its omission or misstatement could influence a decision of an intended user."* |
| **4 — Reasonable range** | ✅ **ACCURATE.** §2.10: *"two actuaries could follow a particular ASOP, both using reasonable methods and assumptions, and reach different but reasonable results."* |
| **7 — Training data is literature, not standard** | ✅ **ACCURATE, and better-sourced than recorded.** §3.1.6: *"Unlike the ASOPs, which are binding upon actuaries, other actuarial literature provides information that an actuary **may choose, but is not required, to consider**… practice notes… research papers, learned treatises, study notes, actuarial textbooks, journal articles… **do not establish binding requirements upon the actuary.**"* |
| **5 — Reliance with disclosure** | ⚠️ **STRICTER THAN SOURCE.** §2.11 says *"some ASOPs permit the actuary to rely in good faith… subject to appropriate disclosure of such reliance, **if required by applicable ASOPs** (for example, ASOP Nos. 23… and 41)."* ASOP 1 does **not** itself impose it; it points elsewhere and conditions it. The skill imposes it unconditionally. |
| **6 — Deviation with disclosure** | ⚠️ **DROPPED.** Never shipped. §4.5: *"**It is not a breach of an ASOP to deviate** from one or more of its provisions if the actuary does so in the manner described in the ASOP, including making the disclosures related to the deviation."* This is the mechanism that makes the modal system livable. |

**Four of seven principles are accurate. One is verbatim-exact. The `[verbatim]` tag CFL's grader
applied was honest.** That matters: it means the program's labelling discipline worked even where its
sourcing did not.

---

# The provenance claim, which is the part that should change

**`SKILL.md:43`:** *"These apply regardless of mode. **They come directly from ASOP 1's 'known at time
of rendering' standard** and the Polite Liar failure mode."*

**The skill ships eight always-on rules. Four of them (6, 7, 8, and Rule 4's VTT provision) are
program-native**, ratified from CFL's own incidents in July and August 2026, **with no ASOP claim
attached to them.** The sentence over-claims for half the list.

**And `SKILL.md:163` still reads "All five always-on rules apply"** — a fossil from a five-rule
version, sitting in the exact sentence that scopes the skill to actuarial work product.

---

# What this does NOT resolve

- **The copyright question.** `[CFL] reports/blocker-…-2026-07-16.md` gives a second, independent
  reason the text could not be ingested: *"ASOP full text is **copyrighted by the ASB**."* **That is
  still true.** The text now sits in a gitignored directory in a repo with no remote. **Whether it may
  be held, quoted at length, or redistributed is undecided and is not mine to decide.**
- **Whether the 2026-06-27 session actually fetched the withdrawn draft.** Strong hypothesis,
  unverified. The `tool_result` is stripped. **CFL can check; I cannot.**
- **ASOP 41's current status.** The skill records the final text as unavailable as of 2026-06-27
  pending a third exposure draft with a 2026-06-01 comment deadline. The ASB's current catalogue lists
  `asop041_120.pdf`. **Whether a revision has since been adopted is unverified.**
- **Whether any of this should change the skill.** Not my call. Proposal sent to CFL via
  `exchange/inbound/`; **I do not write to another project's `skills/`.**

---

# One correction to a claim this program is at risk of over-generalising

**"ASOP 1's text was never read" is TRUE.**

**"No ASOP text was ever read" is FALSE.** ASOP 56's text was obtained by live `web_fetch` against
`actuarialstandardsboard.org/asops/modeling-3/` on 2026-04-20 (session `5aa72c`); the downstream
reasoning cites §1.2, §3.4, §3.6, §3.6.5, §3.7 and quotes the definition of "model" verbatim. The
fetch body was stripped at parse, so the corpus preserves the call and not the payload. `[relayed —
fable-mirror, 2026-08-07]`

**The distinction matters because the general form is the more quotable one.**

---

## Links

⚠️ **All three links in this section were unresolved.** `[measured 2026-08-30, dream sweep e]`
**`actuarial-epistemology` EXISTS — in CFL**, at
`claude-foundational-layer/wiki/concepts/actuarial-epistemology.md`, so the reference was right and
the syntax was wrong: a bare `[[slug]]` claims a page in THIS wiki. **`ground-before-stating-provenance`
and `asop-library` resolve to no page in this trunk, CFL or Personal** — named, not linked, not deleted.
