---
title: "handoff — accumulated session record"
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-REF-SKILLS"
kind: skill-record
skill: handoff
status: v1
created: 2026-08-06
corpus_current_through: export 2026-08-06 (1,172 transcripts indexed; 1,137 re-read here)
generated_by: scripts/audit/skill_record_ext.py (counts) + hand-verification (verdicts)
---

# handoff — accumulated session record

**Why this page exists.** Jon, verbatim, 2026-08-06:

> *"For each skill, in the wiki, accumulated session record. Not just explicit uses, but implicit
> ones. Opportunitys where you might have considered using it but did not, and cases where you did
> and cases where you kinda did… the wiki shpuld help you improve the skill."*

**The acceptance test is the last clause.** This page is organised around what should change about
handoff. Regenerate the counts with `python scripts/audit/skill_record_ext.py --skill handoff`.

---

## 1. The headline, and the one sentence that matters

`handoff` is the **highest-frequency skill name in the corpus** — the word appears in **645 of
1,175** walked transcripts (8,251 occurrences). It is also the skill with the **largest gap between
how often it is named and how often its declared output exists.**

> **Not one transcript in the corpus, and not one artifact on disk, carries a filled
> `## What Was Accomplished This Session` — the skill's own marker. The mandated ten-section
> template has never been used by any handoff ever written.**

That is not a detector failure. It was checked by hand (§4) and the artifacts are enumerated (§3).

| class | file-scoped | turn-scoped | what it tests |
|---|---|---|---|
| USED | **20** | **0** | `## What Was Accomplished This Session` present anywhere |
| PARTIAL | **0** | **0** | marker present, no `## Next Steps` |
| APPLICABLE-NOT-USED | **0** | **0** | a declared trigger in **Jon's** turns, no marker |

**All three of those numbers are misleading and the reasons are different.**

- **USED = 20 counts pastes of SKILL.md, not handoffs.** All twenty carry the heading with
  SKILL.md's placeholder underneath (`[Bulleted list: concrete outputs, decisions, commits made]`).
  Verified by hand on `2b2ff8`, which has the heading **twice**, both times followed by the
  placeholder — a session that read the skill file twice.
- **PARTIAL = 0 is arithmetic on an empty set,** not a compliance finding.
- **APPLICABLE-NOT-USED = 0 is UNKNOWN, and this is the important one.** `SKILL.md` declares **no
  lexical trigger.** Its triggers are *"context fill reaches 60-70%"* and *"Jon signals done for the
  day but work is incomplete"* — **states, not strings.** The generated trigger list therefore holds
  only `/handoff` (the bare word is 7 characters, below `corpus_index`'s `MIN_TRIGGER_LEN` of 8),
  and Jon never types the slash form. **A skill with no declared trigger cannot have non-use
  detected. The class is UNKNOWN, never zero.**

---

## 2. Handoffs are being written. The template is not being used.

The template detector returning zero was real, so a second detector was added for the class it
cannot see: a document **titled** as a handoff (`# Session Handoff — …`), or SKILL.md:185's
mandated confirmation sentence (*"Handoff written to \[path]. Ready for fresh session."*).

| | files |
|---|---|
| template-conforming handoffs | **0** |
| **off-template handoffs** | **23** |
| …carrying a handoff document title | 11 |
| …confirming a handoff was written | 16 |

By month: **2026-06 = 1 · 2026-07 = 10 · 2026-08 = 12.** Use is **rising**, and every one of those
uses ignores the format.

**The ratio 0 : 23 is the finding.** A ten-section template that has never once been filled, in a
skill used more than any other, is not a standard — it is text that every session reads and no
session follows.

### Compliance with the two 2026-08 ratifications

Scored over all 23 handoff-producing files, because scoring only the conforming set would divide by
zero and report perfect compliance over an empty class.

| ratification | denominator | complying |
|---|---|---|
| **2026-08-01** — write to the repo **and** a `wiki/sources/` page, never temp (`SKILL.md:34,43-47`) | 12 files dated ≥ 08-01 | **11 name a source page** |
| …of those same 12, **still naming a temp path** | 12 | **8** |
| **2026-08-03** — Interpretation Summary table (`SKILL.md:228-249`) | 9 files dated ≥ 08-03 | **4** |
| **SKILL.md:181** self-test (*"Name three things a fresh agent would need…"*) | 23 | 17 |

**Read the temp row carefully before treating it as a violation.** Eight of twelve name a temp path,
but the 2026-08-01 revision *itself* discusses `%TEMP%` at length in its "Why not temp" section — so
a session that read the revision and complied with it still matches. **This row is an upper bound on
non-compliance and cannot be tightened lexically.**

The interpretation-summary row is the cleaner signal: **4 of 9, three days after ratification.**

---

## 3. The artifacts themselves — five, program-wide

No transcript-scoped instrument can see these; the skill writes **files**. Scoped across the whole
program because `SKILL.md:40` gives its own worked example in a **sibling project**.

| artifact | filled sections | source page named | interp. table | self-test |
|---|---|---|---|---|
| `Claude Foundational Layer\claude-foundational-layer\HANDOFF-2026-07-08.md` | 0/10 | yes | no | no |
| `…\HANDOFF-2026-07-10.md` | 0/10 | no | no | no |
| `Claude Personal\handoff-document-capture-2026-08-01.md` | 0/10 | no | no | no |
| `Claude Personal\handoff-coordinator-2026-08-02.md` | **3/10** | yes | no | no |
| `Claude Personal\handoff-coordinator-2026-08-03.md` | 1/10 | yes | no | no |

**Best template conformance of any handoff ever written: 3 of 10 sections.** The three that follow
the 2026-08-01 naming convention (`handoff-{topic}-{date}.md`) all live in **Claude Personal**, not
in this repo. **The CFL repo has produced no handoff artifact since 2026-07-10.**

**Five artifacts, five different structures — and none of them is the template.** The two CFL ones
share a shape (*Pinned next step · Pointers · Locked decisions (do not re-litigate) · Git state · Do
NOT without Jon*). The three Personal ones share nothing with those or with each other: 08-02 opens
*"You are the coordinator. Open cold."* and runs to 20 headings; 08-03 leads with *"FIRST ACT —
non-negotiable, and it has a deadline"*; 08-01 is a numbered capture list. **The convergent element
across all five is not a section — it is a hard-rules block, present in four of the five under four
different names**, and the template has no such section at all.

*One correction to the table above, made by hand:* `handoff-coordinator-2026-08-03.md` **does**
perform SKILL.md:181's verification self-test — under the heading *"Self-test — three things a fresh
agent needs that were NOT in the first draft"*. The detector matches SKILL.md's own phrasing
(*"Name three things a fresh agent"*) and misses the paraphrase. **The self-test column is a lower
bound.**

**One more artifact exists and it is the one the revision was written to prevent:**
`%LOCALAPPDATA%\Temp\claude\cfl-dev\exchange\handoff-2026-07-31.md` — a handoff in a
self-deleting directory, dated the day before the ratification that forbade it. It is excluded from
the table above because it is outside every project tree, which is precisely the defect.

---

## 4. Where the detector was wrong, and how it was caught

**The template deflator had to become positional, and the first version was badly wrong.** Its first
form tested whether a SKILL.md placeholder appeared *anywhere* in the file. It scored **17 of 20**
marker-bearing files as template-only — **including four that carry all ten headings**.

The reason is structural and generalises: **a session that RUNS this skill reads `SKILL.md` first.**
The placeholders and the real document therefore sit in the same transcript. **Presence of the
template is evidence the skill was consulted, not evidence it was not run**, and a deflator that
cannot tell those apart deletes exactly the files it exists to count.

Replaced with a positional test — *is the text under this heading the placeholder, or real prose* —
mirroring the `{N}`-vs-digit move `skill_record.py` makes for FBC. **The answer did not change
(still zero), but it is now zero for a reason that survives inspection**, and the same fix moved
wayfinder's count from 16 to 51.

**Verdict on the class: the detector is right and the claim is wrong.** "handoff is the most-used
skill in the corpus" is true of the *word* and false of the *protocol*.

---

## 5. What this record says should change about handoff

None ratified; all for skills-master and a Jon Gate.

1. **Either the template gets used or it gets replaced by the shape people actually write.**
   0 : 23 is not a compliance gap, it is a spec that lost. And there is one convergent element to
   replace it with: **four of the five artifacts carry a hard-rules / do-not block** — *"Do NOT
   without Jon"*, *"Hard rules — every one of these exists because it was violated in the last 72
   hours"*, *"Constraints — each of these exists because it was violated"*, *"the two rules Jon
   enforced hardest today"*. SKILL.md has `## Constraints / Warnings` in the template, which is the
   nearest thing, and **no artifact used that name.** *Falsifier:* if the next three handoffs
   written after a reminder do conform to the ten sections, the template was fine and the problem
   was reachability, not fit.

2. **Declare a trigger that is a string, or state in SKILL.md that non-use is undetectable.**
   Right now the APPLICABLE-NOT-USED class is structurally empty and reads as perfect compliance.
   The cheapest fix is not a better detector — it is a one-line honesty note in the skill.
   *Evidence:* §1.

3. **Score the two-artifact rule on the source page's EXISTENCE, not on its being named.** 11 of 12
   post-08-01 files name a `wiki/sources/` path; whether the page exists was never checked by
   anything. A glob is cheap. *Evidence:* §2.

4. **Make the Interpretation Summary a blocking section, or drop it.** 4 of 9 at three days old is
   the trajectory of the ten-section template repeating. SKILL.md already says *"An empty table is a
   defect in the handoff"* — nothing enforces it, and nothing reports it.

5. **CFL has written no handoff since 2026-07-10 while writing 23 off-template ones.** That is not a
   contradiction: the off-template ones were written into `exchange/` (RESUME, CARRIER, WAKE) under
   other names. **Either those files are handoffs and the skill should say so, or the skill is being
   routed around.** This is the most consequential open question on the page and it needs Jon, not
   an instrument.

---

## 6. What this record cannot see

- **A handoff written but never pasted into the conversation.** This is the *dominant* case; the
  corpus sees pastes, the disk sees artifacts, and the two numbers are printed separately rather
  than reconciled.
- **Whether a session that should have written one did not.** No lexical trigger exists. **UNKNOWN,
  never zero.**
- **Whether a named `wiki/sources/` page exists.** The test is that the transcript names a path.
  Under-counts compliance; the direction is known and is downward.
- **Whether a section is present and empty.** Section coverage is a heading-plus-body test with a
  300-character window, not a quality judgment.
- **Anything outside the export.** Corpus current through **export 2026-08-06**; the corpus is lossy
  and **the wiki wins on conflict.**

---

*Counts generated by `scripts/audit/skill_record_ext.py` (self-test: 35 controls, 0 failures,
negative controls first; it registers into `skill_record.RECORDS` rather than forking it). It reads
`raw/` and writes nothing there. Verdicts are hand-made. No skill text was modified by this page;
nothing here is ratified.*
