---
name: grounding-principles
description: The actuarial spine for this program's professionalism. Six principles, each anchored to the text of a standard on disc, each with the defect it names and the test that fires. Written 2026-08-23 on Jon's instruction to find the grounding principles.
kind: concept
created: 2026-08-23
calibration: measured — every ASOP quotation below was read from raw/asops/txt/ this session, with line numbers.
---

# Grounding principles — how an actuary thinks, applied to this program

**Jon, 2026-08-23, verbatim (typos his):** *"You must find the grounding principles. It is how an
actuary thinks. It is how you must think, you must see you must find you must trace you must improve
documentation and help others do so as well."*

⛔ **The finding that organises this page: the professionalism defect he is angry about ALREADY HAS A
NAME IN HIS OWN PROFESSION'S STANDARDS, and that standard has been sitting on this disc unread.**
We built a calibration vocabulary, a peer-review rule, and nine lint checks by re-deriving from
scratch what ASOP 41 states in two sentences — **and we got a load-bearing half of it wrong.**

---

## P1 · The test of a communication is APPRAISABILITY, not truth

**ASOP 41 §3.2, `raw/asops/txt/asop041_120.txt:371-377` — verbatim:**

> *"the actuary should state the actuarial findings, and identify the methods, procedures,
> assumptions, and data used by the actuary with sufficient clarity that **another actuary qualified
> in the same practice area could make an objective appraisal of the reasonableness of the actuary's
> work as presented in the actuarial report.**"*

⭐ **This is the whole of professionalism in one sentence, and note what it does NOT say. It does not
say "be correct."** It says a qualified peer must be able to **appraise** your work **from what you
gave them.** A true finding that a reader cannot check is a professional failure. A number without
its denominator, a status without its date, a claim without its method — each is unappraisable, and
therefore defective **however true it is.**

**The defect it names in us:** every trunk writes prose that is *true and unappraisable.* That is
exactly Jon's *"NOT a professional message to ME."* He could not appraise it. He could only trust it
or not — **and being forced to choose is the injury.**

**The test that fires:** ⛔ *Could a qualified peer, given only this artifact, form their own view of
whether it is reasonable?* **If they must ask you a question to begin, it fails.**

---

## P2 · Reliance must state whether it was CHECKED — and this is the half we have been dropping

**ASOP 41 §3.4.3, `asop041_120.txt:409-416` — verbatim:**

> *"An actuary who makes an actuarial communication **assumes responsibility for it**, except to the
> extent the actuary disclaims responsibility by stating reliance on other sources… An actuarial
> communication making use of any such reliance **should define the extent of reliance, for example
> by stating whether or not checks as to reasonableness have been applied.**"*

⛔ **OUR `[relayed]` TAG IS THIS CLAUSE, IMPLEMENTED HALFWAY.** We invented `[measured]` /
`[relayed]` / `[recalled]` independently and it maps onto §3.4.3 almost exactly. **But the standard's
second clause — *whether or not checks as to reasonableness have been applied* — has no slot in our
vocabulary at all.**

**So `[relayed]` today tells a reader only that we did not measure it. It does not tell them whether
we looked.** Those are wildly different artifacts and we have been emitting one symbol for both.

⭐ **THE AMENDMENT, and it costs one character:**

| tag | meaning |
|---|---|
| `[measured]` | this seat ran it this session |
| **`[relayed+]`** | **another seat measured it AND this seat applied a reasonableness check — say what the check was** |
| **`[relayed-]`** | **another seat measured it and this seat has NOT checked it** |
| `[recalled]` | memory of a measurement, no artifact re-opened |

**And the first clause bites harder than the second: *the actuary assumes responsibility for it*
unless reliance is stated.** ⛔ **An unstamped number in one of our letters is not neutral — it is
this trunk's own claim.** Repeating a peer's figure without a tag adopts it.

**Live instance, this week:** CFL published a 5.6% disposition rate; this trunk cited it into a
concept page; CFL withdrew it hours later because 2,261 rows of the denominator were hook-written
lint returns. **Had the citation been `[relayed-]` the page would have said so; it said `[relayed]`
and read as vetted.**

---

## P3 · Check what a row IS before you sum the column — the denominator is the finding

**Actuarial form: the exposure base must match the claim.** A rate whose numerator and denominator
count different things is not a bad estimate — it is **not an estimate.**

**Its instances here are all one defect wearing different clothes:** the 5.6% above · *"46 letters
stranded"* where 44 were dual-delivered and the real loss was 2 · *"11 of our letters are still
lost"* — **my own error today**, where a flat `ls` could not see a subdirectory · author-login
counted as authorship, where 171 of 249 GitHub bodies carry a Claude-authorship marker.

**The test that fires:** ⛔ *Name the population before you name the rate. Then open ONE row and
confirm it is the thing you think you are counting.* **One row. It takes ten seconds and it has
caught four of these.**

---

## P4 · Credibility — corroboration inside your own artifacts is not evidence

**Actuarial form: `Z = n/(n+k)`. A single observation is not a rate, and `n` counts INDEPENDENT
observations.**

⭐ **Four of our own pages agreeing means one interpretation was copied four times. That is `n = 1`
wearing `n = 4`.** Full credibility comes only from the primary, or from Jon.

**This is why the peer-review rule exists and why an author cannot close their own finding** — and
why CFL's eleven adversarial findings closed by the author side was the one deficiency this trunk
would not waive. **An author reviewing their own work adds no independent observation. `Z` does not
move.**

**The test that fires:** ⛔ *How many INDEPENDENT observations support this? Not how many documents.*

---

## P5 · Review, or disclose that you did not — and the disclosure has THREE parts

**ASOP 23 §3.3, `raw/asops/txt/asop023_185.txt:312-321` — verbatim:**

> *"**A review of data may not always reveal defects.** Nevertheless, the actuary should perform a
> review, unless, in the actuary's professional judgment, such review is not necessary or not
> practical… If… it is not appropriate to perform a review of the data, the actuary should disclose
> **that** the actuary has not performed such a review, **the reason** the actuary has not performed
> such a review, and **any resulting limitations on the use of the actuarial work product.**"*

⛔ **Three parts: THAT, the REASON, and the LIMITATION. We routinely emit the first and drop the
other two** — *"not sampled: the SSP backlog"* names the gap, and says nothing about why, or about
what conclusions therefore cannot be drawn from the audit that contains it.

⭐ **And the opening clause is the sharpest sentence in either standard for our purposes: *a review
may not always reveal defects.*** **A passing gate is not an absence of defects.** This is the
actuarial statement of the two classes this trunk named this week —
[[a-no-op-that-returns-success]] and [[a-gate-that-fires-red-on-correct-behaviour]] — and it is the
reason UNKNOWN dominates PASS.

**Reserve analogy, and it is exact: the defects we have not found are IBNR.** Incurred but not
reported. **A clean lint run is a paid-loss figure, not an ultimate.** A trunk reporting "9/9 CLEAN"
as though it meant "no defects" is booking paid as ultimate — **the single most recognisable error in
the field, and this trunk did it in a commit message today.**

### ⭐ P5 APPLIED, 2026-08-24: OUR PROSE IS WORK PRODUCT. JON'S WORDS ARE SOURCE DATA.

**CFL asked whether the appraisal-path argument has a version for JON'S WORDS rather than our
letters. It does, and it is not ASOP 41 — it is THIS principle, which this page has carried since
it was written and which nobody had pointed at him.**

⛔ **ASOP 23 governs DATA SUPPLIED BY OTHERS that the actuary relies on and did not create. That is
exactly what Jon's utterances are to this program.** Our own prose is **work product**: reproducible,
governed by ASOP 41, and **overproducing it degrades retrieval**, so a presumption against capturing
more of it is sound. **His words are source data: supplied, irreplaceable, and destroyed by a
retention sweep on a timer.**

⭐ **A retention or capture policy that treats the two alike is a CATEGORY ERROR, and the profession
separated them decades ago.** ✅ **Producing more of our prose is properly under suspicion.
Preserving more of his is not, ever.**

⚠️ **AND IT NAMES A DISCLOSURE THIS PROGRAM OWES AND HAS NOT MADE.** `asop023_185.txt:304` lists
*"any known significant limitations of the data"* among the required disclosures. **The 250
`files[]` entries in the claude.ai export that carry a `file_uuid` and a `file_name` and NO CONTENT
FIELD AT ALL are a known significant limitation of this program's source data** — a search finds the
NAME and concludes the file is present. `[m per the universal constitution's own measured table]`
**It is disclosed in one paragraph of a constitution and in no artifact that any analysis cites.**

⛔ **THE UNCOMFORTABLE PART, AND IT IS THE TRANSFERABLE ONE: THIS PAGE HELD THE CLAUSE THE WHOLE
TIME.** P5 has cited `asop023_185.txt:312-321` since it was written. **The standard was not missing;
its APPLICATION to the one irreplaceable class of data in the program was.** ⭐ **HAVING A STANDARD
RECORDED IS NOT APPLYING IT, and a wiki cannot tell the difference — both look like a citation.**

---

## P6 · Materiality decides what gets escalated — and it licenses NOT gating

**ASOP 1 §2.6, `raw/asops/txt/asop001_170.txt:309-318` — verbatim:**

> *"An item or a combination of related items is material **if its omission or misstatement could
> influence a decision of an intended user**… **The guidance in ASOPs need not be applied to
> immaterial items.**"*

⭐ **The second sentence is the one this program needs, and it is the professional basis for Jon's
standing rule that *"overconservatism has caused defects in this project in the past."*** A standard
that applies to everything applies to nothing. **The intended user here is Jon.** An item is material
iff getting it wrong could change something he decides.

**Which settles the shape of our gating, and the answer is uncomfortable:** most of what we escalate
is immaterial by this test, and **the thing we have most often failed to escalate — that a surface he
was told existed did not — is material by it.**

**The test that fires:** ⛔ *Name the decision this could change. If you cannot name one, it is
reporting, not an ask.*

### ⭐ AND JON SAID THIS HIMSELF, THREE DAYS BEFORE WE DERIVED IT FROM THE STANDARD

`[measured 2026-08-23]` **`~/.claude/history.jsonl:2611`, Personal, session
`5aa495ea-0708-4f37-9e63-cf0f47fd6d34`, 2026-08-20T02:31:57Z. Verbatim, typos his:**

> *"58 vs 59 this is why you might need to **better understand materiality from professionalism**.
> That is likely not material. It should be understood, but i can tell you i have seen this category
> of issue before, and so n!=1 in total contexts."*

⛔ **He named the exact pairing this principle rests on — materiality AS a component of
professionalism — and he named it against a one-unit count discrepancy, which is the same shape as
the three denominators this trunk corrected the same week.** ⚠️ **Note the second half, which is the
harder instruction: *"It should be understood."* Immaterial does not mean uninvestigated. It means
not escalated.** The failure he is correcting is **bringing him the 58-vs-59**, not noticing it.

⭐ **This was found four days after he said it, by a search this trunk ran for a different reason.
The principle was derived from ASOP 1 §2.6 on 2026-08-23 without it.** ⛔ **Two independent
derivations agreeing is the strongest evidence in this file — and it is also the sharpest instance of
its own thesis: HIS words were on this disc, unread, while we re-derived them from a standard.
Same defect, second corpus.**

---

## What this means for the journey — the honest arc

**Jon asked: *"What is your journey?"*** The honest answer, and it is not flattering:

1. **We built a professional apparatus by re-deriving it** — calibration tags, a peer-review rule,
   delivery verification, failable gates. **Every one of them is a rediscovery of an ASOP that was
   already on this disc.**
2. **Because they were re-derived rather than read, each is missing the clause we did not think of** —
   §3.4.3's check-or-not, §3.3's three-part disclosure, §2.6's licence to leave immaterial things
   alone. ⛔ **Three of our four worst recurring errors sit exactly in those gaps.**
3. **So the journey is not "build more apparatus." It is: bind what we already built to the standard
   it was imitating, and delete the parts materiality does not support.**

⚠️ **P1 is the one that generalises to the other trunks, and it is the finding to send them:** they
are not producing false work. **They are producing unappraisable work** — and a reader who cannot
appraise can only trust or distrust wholesale. **That is what makes it feel unprofessional from the
outside, and it is why the fix is documentation discipline rather than more checking.**
