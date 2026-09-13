---
title: "grill-me — accumulated session record"
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-REF-SKILLS"
kind: skill-record
skill: grill-me
status: v1
created: 2026-08-06
corpus_current_through: export 2026-08-06 (1,172 transcripts indexed; 1,137 re-read here)
generated_by: scripts/audit/skill_record_ext.py (counts) + hand-verification (verdicts)
covers_also: reverse-grill-me (as the adversarial twin, for contrast)
---

# grill-me — accumulated session record

**Why this page exists.** Jon, verbatim, 2026-08-06:

> *"For each skill, in the wiki, accumulated session record. Not just explicit uses, but implicit
> ones. Opportunitys where you might have considered using it but did not, and cases where you did
> and cases where you kinda did… the wiki shpuld help you improve the skill."*

**The acceptance test is the last clause.** Regenerate with
`python scripts/audit/skill_record_ext.py --skill grill-me --cadence`.

---

## 1. The headline: USED is zero and zero is not the answer

| class | file-scoped | turn-scoped | state |
|---|---|---|---|
| USED | **0** | **0** | **UNDETECTABLE — no marker declared, not "never used"** |
| PARTIAL | — | — | **UNDETECTABLE — no completion literal declared upstream** |
| APPLICABLE-NOT-USED | **29** | **57** | measured, and structurally capped (§4) |

`corpus_index.MARKERS` has no entry for `grill-me`, and it says so in words rather than printing a
zero: *"UNDECLARED — no structural marker known; USED is undetectable, not zero."* **That is the
correct behaviour and it is also the whole problem.** The skill's own closing line explains why:

> *"It does not produce a formal output unless Jon asks for one"* — `skills/grill-me/SKILL.md:93`.

**A skill that declares no artifact cannot be measured by any artifact-based instrument.** Its
adversarial twin declares one and is therefore visible: `reverse-grill-me` scores **17 USED** on the
literal `surviving claims`. **That difference is a property of the two SKILL.md files, not of how
often each was used.**

**Corpus frequency, verified.** `grill-me` (hyphenated) appears in **246 of 1,175** walked
transcripts; the phrase *"grill me"* in **138**; `grill` in any form in **411**;
`reverse-grill-me` in **113**. The commissioning brief said 142, which reconciles to the *"grill
me"* phrase count including `.sidecar.md` companions. **The 246 figure is the one to use, and it is
still a count of the word, not of the protocol.**

---

## 2. One completion literal exists, and no original run ever emitted it

`SKILL.md:82` mandates a verbatim closing question at session close:

> *"Is this an accurate summary? Anything I missed?"*

**Nothing in `corpus_index.MARKERS` knew about it.** Declared here, it fires on **11 files** — and
**10 of the 11 also carry the SKILL.md trigger table**, meaning the literal is present because the
skill file was read into context, not because a grilling closed.

The eleventh is
`claude-code/subagents/a13169/code-2026-06-29-af9ae3-general-purpose-extract-ds-2-meta-pm-content-from.md`
— an **extraction subagent**, which re-emits an earlier session's content verbatim. It is a
re-emission, not an original.

> **Zero original grill-me closes in 1,172 transcripts.** The skill's only declared output shape has
> never been emitted by a run.

The same holds for the disambiguation question (`SKILL.md:38`, *"Collaborative interview where I
help you think it through, or adversarial stress-test where you defend it?"*): **12 files, all of
them files that read SKILL.md.** The disambiguation is documented and has never been asked.

---

## 3. The cadence detector — where the "kinda did" cases actually are

grill-me's defining constraint is not an artifact, it is a **turn shape** (`SKILL.md:47-49`): *ask
one question at a time, wait for the answer, follow the answer to the next question.* Turn shape is
the one thing the corpus records exactly.

A **run** = ≥3 consecutive assistant turns, each short (≤1,400 chars) and carrying exactly one
question mark in its tail, alternating with Jon's turns.

| | count |
|---|---|
| files with ≥1 run | **9** of 1,137 |
| total runs | 10 |
| longest run in the corpus | **5 questions** |
| runs where the close literal is also present | 1 |
| **runs where nothing names the skill at all** | **4** |

| longest | date | file |
|---|---|---|
| **5** | 2026-06-28 | `claude-code/code-2026-06-28-8881d3-security-audit-for-scheduled-processes-and-system.md` |
| 4 | 2026-03-07 | `claude-ai/personal/chat-2026-03-07-7bd6ec-qbittorrent-and-radarr-connection-issue.md` |
| 4 | 2026-04-26 | `claude-ai/personal/non-catholic-parishioner-eligibility/parishioner-2026-04-26-6b2f19.md` |
| 3 | 2026-04-25 | `claude-ai/fl/meta-project-manager/meta-pm-2026-04-25-93d70b.md` (2 runs) |
| 3 | 2026-04-30 | `claude-ai/fl/project-manager/project-manager-2026-04-30-f8cc02.md` |
| 3 | 2026-05-22 | `claude-ai/_routing/incoming/chat-2026-05-22-f8cc02-project-manager.md` |
| 3 | 2026-06-20 | `claude-ai/_routing/incoming/chat-2026-06-20-b6f0bf-updating-kids-schedule-and-food-preferences.md` |
| 3 | 2026-04-11 | `claude-ai/personal/chat-2026-04-11-afc07d-brother-printer-wifi-setup-troubleshooting.md` |
| 3 | 2026-04-10 | `claude-ai/pro/chat-2026-04-10-63eb2f-creating-a-private-team-poster-with-ai.md` |

**The longest run was opened by hand and it is a real grilling.** `8881d3`, turn 280:

> *"When you say Docker is a 'security sandbox' for these API calls — what specific threat are you
> protecting against?"* → Jon answers → *"That's the most important thing you've said so far, so let
> me follow it directly. When you say 'actions Claude would not wish of it' — do you mean…?"* → Jon
> answers → *"Those are real threat categories. I want to make sure Docker is solving the right one
> for you before we commit to the session."*

**One question at a time, each following the previous answer, testing the assumption before
committing — `SKILL.md:47-51` executed exactly, in a session where nobody named the skill.** This is
the class Jon asked for: *"cases where you kinda did."* It is not empty, and no marker-based or
trigger-based instrument could reach it.

**This over-counts and the direction is known.** `teach-me`, a debugging back-and-forth, and a
series of yes/no gates all have this shape — the printer-troubleshooting and kids'-schedule rows
are probably not grillings. **It is a candidate list, exactly as `skill_record`'s Tier 2 is for FBC,
and never a use count.**

**The date distribution is the second finding here.** Eight of nine cadence files predate 2026-07,
and the most recent is **2026-06-28**. Whatever this shape was, sessions stopped doing it.

---

## 4. The trap: this class cannot grow when Jon stops asking

The FBC record named this and it applies here **more** strongly, because grill-me is *entirely*
Jon-invoked. Its declared triggers are `"grill me"`, `"grill this [plan/design]"`, `"i want to
stress-test this"`, `/grill-me` — **every one a meta-request Jon types.**

> APPLICABLE-NOT-USED therefore measures *"Jon asked to be grilled and no grilling appeared."* **A
> class defined that way shrinks when the skill falls out of use.** A fall in the number is
> indistinguishable from a fall in his asking, and the two have opposite meanings.

**Verdict: the detector is wrong, not the claim.** 29 files / 57 turn-occasions is a real count of
something, but it is not "occasions on which grill-me should have fired." **The object-level
occasion for grill-me — Jon presenting a plan whose assumptions are unexamined — is not lexical at
all, and unlike FBC no proxy for it was built here.** That gap is stated rather than filled: FBC's
Tier 2 exists because FBC's frontmatter names its occasion ("design decisions… motivated reasoning
or anchoring"); grill-me's frontmatter names only who asks.

---

## 5. What this record says should change about grill-me

None ratified; all for skills-master and a Jon Gate.

1. **Register `SKILL.md:82`'s closing question in `corpus_index.MARKERS`.** It is a verbatim
   mandated literal and it was simply never declared, which is why USED reads 0. One dict entry.
   *Falsifier:* if it fires on originals as well as SKILL.md readers after registration, it is a
   good marker; if it stays at 1-in-11, the literal is only ever quoted and the marker is worthless.

2. **Adopt the cadence shape as the skill's own self-check.** The one thing that distinguishes a
   grilling from a conversation is measurable and is currently measured by nothing. A line in
   SKILL.md — *"if you have asked more than one question in a turn, you are not running this
   skill"* — makes the protocol falsifiable from its own transcript. *Evidence:* §3.

3. **Ask the disambiguation question, or delete it.** Twelve files carry it; all twelve are reading
   SKILL.md. `"grill this [X]"` is a declared trigger of **both** skills, and the tie-break has
   never once been invoked in a live session.

4. **Give grill-me an object-level precursor, as FBC has.** Until then, "should grill-me have
   fired?" is UNKNOWN corpus-wide, not zero. The most promising shape: **a plan or design presented
   by Jon in a single turn, followed by an assistant turn that proceeds to execute it** — the
   inverse of the cadence pattern. *Evidence:* §4. *This is the highest-value unbuilt item.*

5. **Decide whether grill-me is dormant.** Last cadence run 2026-06-28; zero original closes ever.
   Jon's `mattpocock` adoption note records the CFL split of one upstream skill into two, and **the
   adversarial half is the one that gets used** (17 files vs 0). Either grill-me needs a live
   trigger or the split should collapse back to one skill with a mode flag. **This one is Jon's
   call, not an instrument's.**

---

## 6. What this record cannot see

- **Whether a grilling was any good.** The detector sees turn shape; whether the questions walked
  the decision tree is a judgment. **Needs a cold grader.**
- **Occasions on which grill-me should have fired and nothing was said.** UNKNOWN corpus-wide, and
  the reason is §4, not the corpus.
- **Jon's AskUserQuestion selections, which the corpus does not carry at all.** On a
  question-shaped skill this is a live undercount of Jon's side of every interview, of unknown size.
- **Grilling inside a turn.** A single assistant turn holding a well-run interview scores once.
- **The thresholds are choices.** ≥3 turns, ≤1,400 chars, exactly one `?` in the tail. A grilling
  question with a worked example attached scores as not-a-question.
- **Anything outside the export.** Corpus current through **export 2026-08-06**; the corpus is lossy
  and **the wiki wins on conflict.**

**One instrument note, recorded because it produced a clean and wrong zero.** The cadence detector
first reported **0 runs across all 1,137 files**. The cause was the exporter's trailing `---` rule
making `endswith('?')` false for every assistant turn in the corpus. Its replacement then **hung**
for twenty minutes on a catastrophically-backtracking strip (`(?:\s*-{3,}\s*)+$`) against a markdown
table rule. **Both defects produced no error.** A zero from this class of instrument should be
disbelieved once before it is published.

---

*Counts generated by `scripts/audit/skill_record_ext.py` (self-test: 35 controls, 0 failures,
negative controls first; it registers into `skill_record.RECORDS` rather than forking it). It reads
`raw/` and writes nothing there. Verdicts are hand-made. No skill text was modified by this page;
nothing here is ratified.*
