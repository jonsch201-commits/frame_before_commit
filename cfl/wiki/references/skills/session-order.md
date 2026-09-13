---
title: "session-order — accumulated session record"
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-REF-SKILLS"
kind: skill-record
skill: session-order
status: v1
created: 2026-08-07
corpus_current_through: export 2026-08-06 (1,172 indexed at run start; 1,175 by run end — the corpus is live)
generated_by: scripts/audit/skill_record_ext.py --skill session-order (counts) + hand-verification (verdicts)
aliases:
  - "cold session open"
  - "session map"
  - "DONE / IN PROGRESS / NEXT / HELD / TRIAGE"
  - "HELD vs triage"
  - "when I park something it is HELD or TRIAGE"
  - "session close ritual"
  - "what's the one thing you need from this session"
  - "wake from nap"
  - "post-compact recovery"
  - "you compacted"
  - "multi-topic message"
  - "reading order at session open"
---

# session-order — accumulated session record

**Why this page exists.** Jon, verbatim, 2026-08-06:

> *"For each skill, in the wiki, accumulated session record. Not just explicit uses, but implicit
> ones. Opportunitys where you might have considered using it but did not, and cases where you did
> and cases where you kinda did… the wiki shpuld help you improve the skill."*

**The acceptance test is the last clause.** Regenerate with
`python scripts/audit/skill_record_ext.py --skill session-order`.

---

## 0. Read this before any number: this skill is four rituals, not one

`session-order` is never invoked. It declares four **states** as triggers, and they fail
independently:

| # | ritual | SKILL.md's trigger | occasion in the corpus | scoreable? |
|---|---|---|---|---|
| 1 | **Cold open** — read four files in order | *"Triggers at every cold session open"* | every conversation | **NO — see §5** |
| 2 | **Session map** | *"when Jon sends a multi-topic message… when direction shifts"* | an assistant turn | yes |
| 3 | **Post-compact recovery** | *"Wake from Nap"* | a compaction boundary | yes, one step of seven |
| 4 | **Session close ritual** | *"when session close is signaled"* | a shaped Jon turn | yes |

**A single USED/PARTIAL/ANU triple would score a session that kept a beautiful map and never ran
the close ritual as compliant.** So each ritual carries its own occasion count and its own
denominator, and there is no aggregate number on this page. That is the design, not an omission.

**Denominators, run-wide.** 1,175 transcripts re-read of 1,172 indexed at run start — **the corpus
grew by 3 mid-run**, because concurrent agents were writing extracts into it. **235 main
conversations, 832 subagents.** A subagent has no cold open, no close ritual and no session of its
own, yet its transcripts sit inside every corpus-wide figure below. The split is printed so a reader
can discount rather than take the totals at face value.

`corpus_index` reports this skill **UNDECLARED / 0 USED / ANU 11 files**, computed off the generated
trigger phrases `"session order"` and `/session-order` — i.e. sessions that *talked about* the skill.
Not superseded, not superseding; a different question.

---

## 1. Ritual 2 — the session map, and it has fallen out of use

| | count |
|---|---|
| turns carrying ≥1 map label | 48 |
| of those, SKILL.md's fenced template being quoted | **0** |
| **GENUINE map emissions** (≥3 of the 5 labels, no placeholders) | **23**, in **11 files of 1,175** |
| of the 23, **missing at least one of the five labels — "kinda did"** | **20** |
| full five-label maps | **3** |

**Per label, across the 23 genuine maps:**

| label | present | share |
|---|---|---|
| `HELD` | 22 | **95.7%** |
| `DONE` | 19 | 82.6% |
| `TRIAGE` | 18 | 78.3% |
| `IN PROGRESS` | 12 | 52.2% |
| `NEXT` | 10 | 43.5% |

**The two labels that survive are the two Jon cares about.** His standing instruction in `CLAUDE.md`
is *"When I park something, it's HELD (returns this session) or TRIAGE (handed off, session
responsibility ends). Don't conflate them."* `HELD` appears in **22 of 23** maps and `TRIAGE` in 18.
The two that get dropped — `IN PROGRESS` and `NEXT` — are the status-reporting half, and they are
present in barely half the maps. **The skill is degrading toward a park-ledger and away from a
status board**, and that is a defensible thing for it to become; it just is not what SKILL.md says.

### The date distribution is the finding

| month | files with a genuine map |
|---|---|
| 2026-04 | 1 |
| 2026-05 | 5 |
| 2026-06 | 1 |
| 2026-07 | 4 |
| **2026-08** | **0** |

**Last genuine map: 2026-07-18.** Not one in the entire 2026-08 corpus — which is also the period of
heaviest CFL activity, most compaction boundaries, and most parallel agents. **The map is a
multi-thread instrument and it stopped being used exactly as the number of threads exploded.**

The eleven files, in full, because the population is small enough to enumerate rather than
characterise: `project-manager-2026-04-30-f8cc02` · `skills-master-2026-05-01-bcafba` ·
`code-2026-05-04-740c93-generate-status-report` · `chat-2026-05-14-bcafba-skills-master` ·
`code-2026-05-17-41fa02-update-wiki-open-items-and-memory` ·
`chat-2026-05-22-f8cc02-project-manager` · `code-2026-06-28-8881d3-security-audit-for-scheduled-processes` ·
`agent-interaction-framework-2026-07-02-5990f2` ·
`chat-2026-07-06-2b98ca-automated-expense-tracking` · `chat-2026-07-10-7f2815-project-capacity-planning` ·
`code-2026-07-18-49a1c0-packet-manager-implementation`.

**Six of eleven are claude.ai. The role sessions that used it — project-manager, skills-master — are
where it lived.**

---

## 2. Ritual 3 — the post-compact restatement has never been emitted. Verified.

| | count |
|---|---|
| **compaction boundaries in the corpus** | **86**, in 26 files |
| the mandated literal *"Before compaction, we were…"* appears | 5 times |
| **boundaries ANSWERED by a restatement within 12 turns** | **0 of 86** |
| **APPLICABLE-NOT-USED** | **86 of 86** |

**A zero this clean is normally a broken detector, so all five literal hits were opened by hand.**
None of the five is a recovery:

- `code-2026-07-25-2b2ff8`, T640 and T643 — the phrase inside a `[tool_use: Write]` payload writing
  a **plan file**, and inside an `ExitPlanMode` argument. The session's own boundaries are elsewhere.
- `code-2026-07-26-ab2f68`, T46 — an **Explore agent reporting on `handoff/SKILL.md`'s text.**
- `code-2026-05-28-a2126e`, T61 — an Explore agent quoting the **herald** skill file.
- `code-2026-08-05-a11969`, T84 — an Explore agent's report on *"compact/wake machinery."*

**All five are the skill being read or quoted. None is the skill being run.** The 26 files that
carry a boundary include the heaviest sessions in the program — `code-2026-06-27-a13169` (11
boundaries), `code-2026-05-20-c5644b` (9), `code-2026-07-06-da51cc` (8),
`code-2026-08-02-9f7640` (7), `code-2026-08-05-a69f31` (7) — and **not one of them restated its
position after a compact.**

**What this does and does not prove.** It proves the *sixth* step of a seven-step ritual never fired.
Steps 1–4 are reads and leave no mark; step 6 (check for in-flight agents) has no literal. So the
honest statement is: **the one part of post-compact recovery that is mechanically observable has a
compliance rate of zero over 86 occasions.** Whether the unobservable steps ran is UNKNOWN.

This is not an isolated finding. `CLAUDE.md`'s own cold-session block records the same class of
failure for the wayfinder map: *"a session therefore woke with repo state and no role state."*
**Waking is where this program loses continuity, and the skill that governs waking is the one with a
zero.**

---

## 3. Ritual 4 — the close ritual, and a defect in SKILL.md itself

| | count |
|---|---|
| Jon turns carrying an unambiguous close signal | **3** |
| labelled `EXPORT` / `SKIP` judgments emitted | **3** |
| close signals answered within 8 turns | **0 of 3** |

**The first run of this detector said 12 and 21, and both were mostly noise.** The corrections are
the useful part of this section.

**(a) `EXPORT` matched `EXPORT-LOG`.** The v1 separator class allowed a hyphen, so
`- **EXPORT-LOG watermark:** 2026-06-27T21:14:43Z` — the *extraction audit trail*, an entirely
different artifact that appears in nearly every wiki-master session — scored as a close-ritual
judgment. `**SKIP-SUPERSEDED (1c802a)**`, a triage disposition, scored too. **Roughly 19 of 21 hits
were one of those two.** 21 → 3.

**(b) SKILL.md names `"done"` as a close signal, and that is the defect.** Taking the skill at its
word is what made the detector wrong. Jon's commonest use of the bare word is an **acknowledgement
that opens the next item**:

> *"Done. Next?"* — `meta-pm-2026-04-25-93d70b` T114, and again in `skills-master-2026-05-01-bcafba`
> *"done. Your turn... did it work? looks like no..."* — `code-2026-06-21-efd6a3` T664
> *"Done. Solved. Checking desktop."* — `chat-2026-04-11-afc07d` T58
> *"Done. Production file edited as agreed. Now, Run the migration/verification audit before I
> commit."* — `code-2026-07-06-da51cc` T1589

**Every one of those is the opposite of a close signal.** 12 → 3. **This is a finding about
`SKILL.md`, not only about a regex** — a session that follows the skill literally will read
*"Done. Next?"* as a session-close cue and run the close ritual in the middle of the work.

The three that survive are unambiguous and they are Jon's real vocabulary:
*"I'm done here for now"* (`chat-2026-06-12-0b7681` T30) and *"Goodnight. Next standard update
should combine these…"* (`chat-2026-07-30-4b4655` T7, and its twin `d1321c`).

**None of the three was answered by a labelled export judgment.** The three genuine judgments that
do exist in the corpus are all self-initiated at the end of a Claude Code session, not responses to
Jon: `EXPORT: yes — decisions made, architecture locked` (`code-2026-06-28-8881d3` T364) and
`- EXPORT — three scripts written, CDP debugging trail` (`code-2026-05-09-02ff5b` T69).

---

## 4. Ritual 3's occasion pool — a number that should not be read as a failure count

| | count |
|---|---|
| Jon turns of **multi-topic shape** (≥3 enumerated items, or ≥3 `?`) | **1,150** |
| answered by a genuine map within 8 turns | 24 |
| APPLICABLE-NOT-USED | 1,126 of 1,150 |

**Shape is not intent, and this pool's precision was not measured.** A numbered list of three file
paths is not three topics; one question asked three ways is one topic. **1,126 is a candidate pool at
unknown precision, and it is printed rather than promoted to a finding.** It is the same shape as the
GBS record's 7,346: a large ANU class that says more about the detector than the record.

What it does establish, weakly, is a floor: **whatever fraction of those 1,150 were genuinely
multi-topic, 23 maps across 15 months cannot have covered many of them.**

---

## 5. The largest UNKNOWN on this page, and it is structural

**The cold-open ritual — the skill's first and largest clause — cannot be scored at all.**

Its output is *reading four files in a mandated order*. Reading leaves no mark in a transcript unless
a tool call happens to be logged, and in claude.ai it never is. **All 235 conversations in this
corpus are cold-open occasions and none of them is gradeable.** That is **UNKNOWN, never zero**, and
no amount of better regex fixes it — it is a property of what a transcript records.

This is worth stating plainly because the cold-open list is the clause with the known history of
failing silently. SKILL.md carries its own note:

> *"Paths repaired 2026-07-26. This list previously named `README.md`, `WORKING_CONTEXT.md`,
> `SESSION-ORDER-SKILL.md` and `TEMPORAL-CONTEXT-SKILL.md`. **Only `README.md` still existed**…
> A cold-open skill whose mandatory reading list points at absent files fails silently."*

**Four of four conditional-load paths were also dead, and one (`BACKGROUND.md`) had no successor at
all.** So the one clause that cannot be observed is also the clause with a documented history of
being broken for an unknown length of time. **That combination is the finding, and this record
cannot close it.**

---

## 6. What this record says should change about session-order

**None ratified. All are proposals for skills-master and a Jon Gate.**

1. **Delete the bare word `"done"` from the close-signal list.** §3(b). It is Jon's acknowledgement
   token, not his goodbye, and the skill currently instructs a session to misread it. Replace with
   the forms the corpus actually contains: *"I'm done for now"*, *"Goodnight"*, *"that's it for
   tonight"*, *"stopping here"*. *Falsifier:* if any corpus instance of bare `"done"` is followed by
   Jon leaving rather than by another instruction, the word is ambiguous rather than wrong, and the
   fix is a disambiguation rule instead of a deletion.

2. **The post-compact restatement needs a trigger that is not a memory.** 0 of 86. The literal is
   step 5 of a 7-step ritual that a compacted session must remember to run *after* losing the context
   telling it to. **The `PreCompact` hook is already wired** (`CARRIER.md`, all six hook events,
   `8a4edad`) and is the natural home: emit the restatement scaffold into the post-compact context
   rather than asking the session to recall the obligation. *Evidence:* §2.
   *Falsifier:* if any of the 26 boundary-carrying sessions did restate its position in different
   words, the failure is the literal and not the ritual — this record tests one string.

3. **Say which four labels are mandatory and which are conditional.** 20 of 23 genuine maps drop at
   least one label, and the two that get dropped are consistently `IN PROGRESS` and `NEXT`. Either
   the map is a five-part shape and 87% of its uses are non-compliant, or it is a two-part park
   ledger with three optional rows. **SKILL.md currently implies the first and the record shows the
   second.** *Evidence:* §1.

4. **The map died in the month it was most needed.** Zero genuine maps in 2026-08, during the
   heaviest parallel-agent period in the program's history. Whatever the fix is, *"remember to show
   the map"* is not it — that has been the rule the whole time. **Recommend the map become an
   artifact with a path** (as the wayfinder map is) rather than a thing a session types, so that its
   absence is detectable by a file check instead of a string scan. *Falsifier:* if the
   `wiki/tracker/` wayfinder map has absorbed this function, the skill's map clause is **superseded
   rather than neglected**, and the right change is to say so in SKILL.md and retire it. **That
   possibility is live and this record does not adjudicate it.**

5. **The cold-open clause needs a mark.** §5. It is unobservable today and it has a documented
   history of silent breakage. One line — *"state the four files you read, in order, in your first
   substantive response"* — converts the program's least-checkable clause into its cheapest-checked
   one. This is the same move `CLAUDE.md`'s cold-session block already makes for the wayfinder map.

---

## 7. What this record cannot see — UNKNOWN, never zero

1. **The cold-open ritual entirely.** §5. 235 occasions, 0 gradeable.
2. **Whether a map was accurate.** Five labels present says the shape was kept. Whether the `HELD`
   row actually held everything parked is a judgment about content.
3. **Whether `HELD` was conflated with `TRIAGE`** — the distinction SKILL.md calls critical. The
   failure is putting the right word on the wrong item, which is invisible to a label detector.
   **This is the clause Jon states in `CLAUDE.md` in his own voice, and it is the one this page can
   least see.**
4. **Multi-topic precision.** §4. 1,126 is a pool, not a count of failures.
5. **Steps 1–4 and 6 of the post-compact ritual.** Only step 5 has a literal.
6. **Subagent contamination of the totals.** 832 of 1,175 transcripts are subagents with no session
   of their own. The split is printed; the totals are not corrected for it, because which corpus-wide
   figures *should* exclude subagents is a judgment, not a fact.
7. **Anything outside the export.** Corpus current through **export 2026-08-06**; it grew by 3 files
   during this run. The corpus is lossy and **the wiki wins on conflict.**

---

*Counts generated by `scripts/audit/skill_record_ext.py`, which registers into
`skill_record.RECORDS` rather than forking it and imports `spans` (== `gbs_record.spans`) and
`corpus_index`'s reference queries. Self-test 73 controls, 0 failures, negative controls first,
including regression controls for both v1 detector defects in §3, and a real before/after proving
`raw/` is left byte- and mtime-identical. Verdicts are hand-made. No skill text was modified by this
page; nothing here is ratified.*
