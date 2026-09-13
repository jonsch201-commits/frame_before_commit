---
title: "wayfinder — accumulated session record"
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-REF-SKILLS"
kind: skill-record
skill: wayfinder
status: v1
created: 2026-08-06
corpus_current_through: export 2026-08-06 (1,172 transcripts indexed; 1,137 re-read here)
generated_by: scripts/audit/skill_record_ext.py (counts) + hand-verification (verdicts)
---

# wayfinder — accumulated session record

**Why this page exists.** Jon, verbatim, 2026-08-06:

> *"For each skill, in the wiki, accumulated session record. Not just explicit uses, but implicit
> ones. Opportunitys where you might have considered using it but did not, and cases where you did
> and cases where you kinda did… the wiki shpuld help you improve the skill."*

**The acceptance test is the last clause.** This page is organised around what should change about
wayfinder. Regenerate the counts with
`python scripts/audit/skill_record_ext.py --skill wayfinder --senses`.

---

## 0. Read this before any number below

**The word `wayfinder` names three different things in this corpus, and only one of them is the
skill.** `wiki/references/vocabulary.md:56-58` records the first correction:

> *"The wayfinder's nine tickets B-1…B-9 … these are **work tickets** (workstream-status tags:
> `prototype`, `task`, `grilling HITL`), **not a content taxonomy**. `cfl-branch-registry.md` §1.1
> corrected exactly this conflation on 2026-08-06."*

To that add a third sense visible in Jon's own turns: **wayfinder as an addressed party** — *"You
are the FL wayfinder — meta-coordinator, claude.ai side"*, *"TO: wayfinder, FROM: Jon"*, *"relayed
via CFL wayfinder"*, *"**From**: Triage/Wayfinder"*.

**Every trigger-based count for this skill is a count over all three senses.** The split is §3.

---

## 1. The headline classes, both units

`corpus_index.py --query-skill wayfinder` and `--query-skill-turns wayfinder`, over **1,172 indexed
transcripts / 97,927 turns**:

| class | file-scoped | turn-scoped | what it tests |
|---|---|---|---|
| USED | **53** | **6** | `## Decisions So Far` present |
| PARTIAL | **2** | **0** | marker present, no `## Out of Scope` |
| APPLICABLE-NOT-USED | **15** | **140** | the word in **Jon's** turns, no marker inside the window |

Turn-scoped occasions: **146, in 23 files.** Window **58 turns**, the measured p90 of
invocation→marker distance, with a **hard reset at compaction boundaries** (26 indexed files carry
one).

**`PARTIAL` is a subset of `USED` — overlap 2 of 2, measured.** It is not a ratio between classes.

**The file→turn collapse from 53 to 6 is the instrument getting better, not worse.** File-scoped,
one `## Decisions So Far` anywhere in a 1,838-turn session answers every mention of the word in it.

### Disjointly, after deflation

| | files |
|---|---|
| carry `## Decisions So Far` | 53 |
| …template/documentation only (heading present, body is SKILL.md's placeholder) | **2** |
| **genuine map bodies** | **51** |
| …reaching `## Out of Scope` | 49 |
| …**not** reaching it — "kinda did" | 2 |
| carry CFL map *shape* (`wayfinder:map`, `## Destination`, `wayfinder-cfl`) | 172 |

**Corpus frequency, verified.** The word appears in **481 of 1,175** walked transcripts (11,427
occurrences). The commissioning brief said 509; a sidecar-inclusive `grep` gives 514. The three
numbers differ only by whether `.sidecar.md` companions are counted. **Nothing turns on this and it
is recorded so the next reader does not re-derive it.**

---

## 2. The finding that matters most: the map is read far more than it is charted

Of the **51 genuine map bodies, 42 are subagent transcripts** and 44 are dated 2026-08.

| | count |
|---|---|
| genuine map bodies in **subagent** transcripts | **42** |
| genuine map bodies in main **conversation** transcripts | 9 |
| of the 51, also carrying `wayfinder-cfl` / `wayfinder:map` / `## Destination` | 50 |

**A subagent does not chart a map. It is handed one.** So the dominant recorded use of this skill in
CFL is not the wayfinding protocol at all — it is **the map functioning as a briefing artifact
pasted into fresh agent context.** That is a real and valuable use, and it is not the use SKILL.md
describes.

**The maps that were actually charted are countable, and there are five:**

| map | 5 mandated headings present? |
|---|---|
| `exchange/wayfinder-map-2026-07-19.md` | yes (Destination · Notes · Decisions so far · Not yet specified · Out of scope) |
| `wiki/intake-triage/WAYFINDER-MAP-mirror-continuity-and-su-2026-08-05.md` | yes |
| `wiki/intake-triage/WAYFINDER-MAP-cfl-no-memory-files-2026-08-06.md` | yes |
| `wiki/intake-triage/WAYFINDER-MAP-cfl-no-memory-files-2026-08-06-v2.md` | **no — none of the five** |
| `wiki/tracker/wayfinder-cfl.md` | yes |

**4 of 5 conform. The one that does not is a `-v2` revision of a map that did.** A revision that
drops the format is the failure mode a map-shaped skill has, and no instrument in the program was
watching for it before this page.

`wiki/tracker/wayfinder-cfl.md` carries **10 commits, every one dated 2026-08-06.** The live CFL map
is one day old. Every count above that reads as "wayfinder is heavily used" is measuring a corpus in
which the map has existed for one day and been pasted into forty-two agent briefs.

---

## 3. The equivocality split — the number the APPLICABLE-NOT-USED headline depends on

Every occurrence of `wayfinder` **in Jon's own turns**, classified from a ±260-character window
(occurrences closer than 120 chars merged, reusing `gbs_record`'s rule):

| sense | occurrences | share |
|---|---|---|
| **SKILL** — the protocol, invoked or named as a protocol | **24** | 9.0% |
| **MAP** — the map file, its tickets, its rows | 60 | 22.6% |
| **PARTY** — wayfinder as an addressed role or interlocutor | 23 | 8.6% |
| **UNCLASSIFIED** | **159** | **59.8%** |
| total | 266 | |

**Only the SKILL row is an invocation occasion.** The published APPLICABLE-NOT-USED figures — 15
files, 140 turn-occasions — are computed over all four rows. **At most 9% of them can be occasions
on which the skill was applicable and not used**, and that is an upper bound, not an estimate.

**UNCLASSIFIED at 59.8% is the honest state of this classifier and it is printed, not hidden.** It
was 68.8% before the PARTY pattern was widened by hand-reading 22 windows; the widening moved 20
occurrences and left the residue. **A classifier that resolves 40% of its input is a partial
instrument and the page says so rather than reporting the resolved 40% as if it were the whole.**

Per-file, the split is uneven in an informative way:

| file | S | M | P | U |
|---|---|---|---|---|
| `code-2026-08-05-a69f31-fix-claude-code-settings-hook-configuration` | 3 | 21 | 0 | 29 |
| `code-2026-08-03-9e21da-cfl-coordinator-check-in-with-fabel-mirror` | 2 | 0 | 0 | 38 |
| `code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates` | 0 | 16 | 1 | 17 |
| `code-2026-07-29-627c1e-pr-review-merge-blockers` | 5 | 8 | 0 | 14 |
| `code-2026-07-06-da51cc-cc-handoff-packet-review` | 7 | 2 | 3 | 4 |

`da51cc` is the only file where the SKILL sense dominates. It is also the earliest genuine map body
in the corpus (2026-07-06).

---

## 4. Where the detector was wrong, and how it was caught

Two corrections were applied while building this page. Both are recorded because both produced
*plausible* numbers.

**(a) The template deflator scored 37 of 53 marker files as documentation.** The test was presence
of the string `skills/wayfinder/SKILL.md`. **But a session that runs wayfinder reads SKILL.md
first**, so the deflator was deleting exactly the files it existed to count. Genuine map bodies read
**16**. Replaced with a positional test — is the body under `## Decisions So Far` the SKILL.md
placeholder, or a real closed-ticket line — and the true figure is **51**.

*This is the same failure the FBC record found in its own first pass, in a different skin: presence
of the template is evidence the skill was consulted, not evidence it was not run.*

**(b) The PARTY sense was 3 occurrences and should have been 23.** The first pattern tested only
*"wayfinder said"* and *"from wayfinder"*. Hand-reading 22 UNCLASSIFIED windows found the dominant
missing shape immediately: wayfinder as an **addressed role**. An address is not an invocation, and
folding those into UNCLASSIFIED made the residue look like noise when a fifth of it had a name.

---

## 5. What this record says should change about wayfinder

None ratified; all for skills-master and a Jon Gate.

1. **Declare the marker against the ARTIFACT, not the heading.** The skill's product is a map
   **file**; `corpus_index` can only see the heading when a transcript pastes it, which is why 42 of
   51 "uses" are subagents holding a paste. A file-existence check over the five known maps is a
   stronger instrument than any string test and costs one glob. *Falsifier:* if the file check and
   the heading check agree on more than 80% of sessions, the heading test was adequate and this is
   not worth building.

2. **Fix the term before fixing anything else.** 9% of Jon's uses of the word are the skill. Jon's
   own standing note — *"undefined terms are upstream of sprawl"* — applies to a term this program
   defined itself. Either the connector-side role gets a different name or the skill does.
   *Evidence:* §3. *Falsifier:* if a reader can reliably tell the three senses apart from context
   alone, the classifier's 59.8% UNCLASSIFIED is an instrument defect and not a vocabulary one.

3. **Make the five headings a checked shape, not a convention.** One of five charted maps
   (`…-2026-08-06-v2.md`) carries none of them, and it is a *revision* of a map that did. A
   three-line lint over `WAYFINDER-MAP-*` and `wiki/tracker/wayfinder-*` closes it. *Evidence:* §2.

4. **Record the reachability fix as part of the skill, not only in `CLAUDE.md`.** Until 2026-08-06
   the resume rule lived inside `wiki/tracker/wayfinder-cfl.md` and nothing anywhere told a session
   to open that file — *"the instruction and the thing it governs must be reachable from the same
   starting point, or the instruction is decoration"* (`CLAUDE.md`, cold-session block). SKILL.md
   still does not say where CFL's map lives or that a session must open it. *This is the single
   cheapest change on the list.*

5. **Close the two PARTIAL map bodies or state why they stop.** Two genuine maps never reach
   `## Out of Scope`. SKILL.md treats out-of-scope as a closed class that never graduates; a map
   without it has no way to record what was ruled out.

---

## 6. What this record cannot see

- **A map advanced without the headings entering the transcript.** The live map is a wiki file; a
  session that edited it without pasting it is invisible to every count here.
- **Whether a ticket was a *decision* ticket.** SKILL.md's whole distinction is decision-tickets vs
  build-slices, and that is a judgment about content, not a string.
- **The 59.8% UNCLASSIFIED senses.** Reported as their own row. Any reading that folds them into
  MAP or SKILL has done the thing this page refuses.
- **The nine B-1…B-9 items as anything other than work tickets** (`vocabulary.md:56-58`;
  `cfl-branch-registry.md` §1.1). Any count here read as a taxonomy is misread.
- **Anything outside the export.** Corpus current through **export 2026-08-06**; the corpus is lossy
  and **the wiki wins on conflict.**

**Two instrument caveats for the next reader.** (1) The sense classifier reads a ±260-character
window, and a window is not a document. (2) Dates come from filenames, so a re-quote carries the
*quoting* file's date; the month histogram is over genuine map bodies only and still over-reports
2026-08.

---

*Counts generated by `scripts/audit/skill_record_ext.py` (self-test: 35 controls, 0 failures,
negative controls first; it registers into `skill_record.RECORDS` rather than forking it). It reads
`raw/` and writes nothing there. Verdicts are hand-made. No skill text was modified by this page;
nothing here is ratified.*
