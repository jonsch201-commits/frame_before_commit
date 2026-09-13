---
title: "temporal-context — accumulated session record"
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-REF-SKILLS"
kind: skill-record
skill: temporal-context
status: v1
created: 2026-08-07
corpus_current_through: export 2026-08-06 (1,172 transcripts indexed; 1,137 re-read here)
generated_by: scripts/audit/skill_record_ext.py --skill temporal-context (counts) + hand-verification (verdicts)
aliases:
  - "temporal context documentation"
  - "you should just check time more"
  - "the actual time of a message sent is nowhere in any json?"
  - "I don't know how to get you temporal context, but you need it"
  - "because you woke up"
  - "I view you as meaningfully waking up"
  - "good morning is a compaction boundary, not a clock"
  - "the timestamp on every response"
  - "measured vs ESTIMATED"
  - "why is the time wrong"
  - "check the clock before you stamp it"
---

# temporal-context — accumulated session record

**Why this page exists.** Jon named this skill directly, twice, on 2026-08-06.

> *"More on q1. Their needs to be more temporal context documentation. This would be so easy to
> improve if it was organized in the wiki under skills in Projects."*

> *"Sorry I said morning because you 'woke up' you should just check time more, this is why CFL
> needs to document the skill in its wiki including references to your conversations."*
> — relayed byte-identical in `exchange/personal-to-cfl-temporal-context-wiki-documentation-2026-08-06.md:16-17`

**His second sentence is the acceptance test, and it is more specific than the general skill-record
brief:** the page must *"reference the actual conversations where the skill's behavior was
exercised, failed, or was corrected — not just restate the skill text"*
(`…-wiki-documentation-2026-08-06.md:23-26`). Everything below is a count or a citation. Regenerate
the counts with `python scripts/audit/skill_record_ext.py --skill temporal-context`.

---

## 0. The one thing that makes this record different from every other skill record

**This is the only skill in CFL with an external answer key.**

Every other record can ask *did the skill run?* This one can ask *was the output right?* — because
the `.sidecar.md` companions carry the venue's own per-turn clock, and the sidecar's `T{n}` maps
one-to-one onto the primary transcript's turn headings. So for any turn that stamped
`[YYYY-MM-DD HH:MM CDT]`, the true wall-clock time of that turn is recoverable and the stamp can be
graded.

That matters because **this skill's measured failure mode is not omission.** It is a stamp that is
present, correctly formatted, labelled `*(measured)*`, and **wrong by two hours.** A
presence-detector scores that as USED. So does `corpus_index`. So would every other page in this
directory.

**945 of 1,137** scanned transcripts carry a sidecar. **Both venues have a key, under different
field names** — Claude Code declares `timestamp:`, claude.ai declares `created_at:`. The first
version of the reader here read `timestamp:` only, returned **0 rows for an 8-turn claude.ai file**,
and would have published *"claude.ai cannot be checked."* That is the same defect `CLAUDE.md`
records for `cc_corpus_gap.py`, which read `source_id:` while 26 extracts declared `uuid:` and
therefore reported every one of them LOST: ***it was not finding losses, it was finding a field
name.*** It was caught here by a self-test control, not by reading.

---

## 1. The three classes, on the unit the skill's own trigger requires

SKILL.md's frontmatter, verbatim: **`"Triggers on every response."`** So the occasion is not a
phrase Jon types. It is an assistant turn. This is the **only skill in `skill_record_ext.py` whose
APPLICABLE-NOT-USED class is uncapped** — it cannot shrink because Jon stopped asking, which is the
structural trap the `grill-me` and FBC records both had to declare.

| class | count | of | definition |
|---|---|---|---|
| **USED** | **802** | 6,316 response turns | the turn carries `[YYYY-MM-DD HH:MM CDT]` |
| **PARTIAL — "kinda did"** | **711** | 978 stamp occurrences | stamp present, **no provenance label** |
| **APPLICABLE-NOT-USED** | **5,514** | 6,316 response turns | response turn with no stamp at all |

**Denominators, all of them.** 1,137 transcripts re-read of 1,172 indexed · **55,529 assistant
turns** · **6,316 response turns** · 978 stamp occurrences · 949 stamped assistant turns · **71 of
1,137 transcripts carry any stamp at all.**

**A "response turn" is a choice and it is stated.** In a Claude Code transcript an `## Assistant`
heading is emitted for every tool-calling step, most of which Jon never sees. A response turn is the
last `A` turn before the next `H` — the turn Jon reads. Both denominators are printed: **1.71% of
all assistant turns are stamped; 12.70% of response turns are.** The looser number is not hidden
because it is not wrong, only less meaningful.

### What `corpus_index` says, and why it is answering a different question

| | corpus_index | this page |
|---|---|---|
| USED | **0 — UNDECLARED** | 802 turns |
| PARTIAL | UNDETECTABLE | 711 |
| APPLICABLE-NOT-USED | **24 files** / 37 turns | 5,514 turns |

`corpus_index` reports **UNDECLARED, not zero**, because no structural marker was ever declared for
this skill — and its ANU of 24 is computed from the generated trigger phrases `"temporal context"`
and `/temporal-context`, so **it is counting sessions that TALKED about the skill**, which is close
to the opposite of the class name. Neither number supersedes the other. **The 0 is the honest
output of a registry gap, and the fix is one entry in `corpus_index.MARKERS` — see §6.1.**

---

## 2. The finding: the surface with a clock stamps worse than the surface without one

This is the result this page exists to deliver, and it was not expected.

| venue | aligned same-day stamps | median \|error\| | within 2 min |
|---|---|---|---|
| **claude.ai** | 31 | **1.3 min** | 17 (54.8%) |
| `_superseded` (claude.ai) | 22 | 1.1 min | 14 (63.6%) |
| **Claude Code** | **368** | **15.6 min** | 86 (**23.4%**) |

**Claude Code is the venue where `date` exists.** SKILL.md tier 1 calls running it *"not a fallback
and not optional… the default action for every timestamped response."* claude.ai has no shell at
all and falls through to tier 3, Jon's own typed time. **The surface with the measurement instrument
is off by a median of 15.6 minutes; the surface without one is off by 1.3.**

The mechanism is visible in the distribution and is not mysterious: **claude.ai sessions are short
and anchored to a human message; Claude Code sessions run for hours.** Drift is a function of
session length, and tier 1 is only worth having if it is re-run. SKILL.md already says so
(`:120-127`, *"re-run `date` (tier 1) rather than advancing an estimate; measurement is free"*).
**The record says the sentence is not being obeyed on the one surface where it applies.**

### The whole distribution, same-day stamps only

**n = 421** aligned same-day stamps of 463 aligned of 978 total.

| \|error\| | count | share |
|---|---|---|
| ≤ 2 min — right | 117 | 27.8% |
| 2–10 min | 85 | 20.2% |
| 10–30 min | 61 | 14.5% |
| 30–60 min | 36 | 8.6% |
| **> 60 min — wrong** | **122** | **29.0%** |

median 11.6 · p75 70.7 · p90 182.0 · max 799.7 minutes.

**Cross-day stamps (42 of 463) are excluded and printed, not deleted.** A stamp whose date differs
from its turn's date is overwhelmingly a *quotation* — a session pasting an older page or an earlier
session's line. The first run left them in and reported a max error of **288,084 minutes (200
days)**, which is not a clock reading. Removing them moved p90 from 264 to 182 and median from 16.1
to 11.6.

**Drift has a sign: 179 stamps ahead by >2 min, 125 behind.** Scatter would be symmetric. Dead
reckoning and carried-forward anchors both run forward. *(The 125 behind are real and unexplained
here; the largest are sessions that stamped an early-day time deep into an evening run.)*

### Per session, the largest contributors

| session | n | median \|err\| | within 2 min |
|---|---|---|---|
| `code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates` | 83 | 25.1 | 14 |
| `code-2026-07-25-2b2ff8-build-herald-wiki-with-sensitivity-tiering` | 54 | **180.1** | 2 |
| `code-2026-08-03-9e21da-cfl-coordinator-check-in-with-fabel-mirror` | 42 | 21.1 | 6 |
| `code-2026-08-02-9f7640-run-restart-checks-and-report-before-wiki-queue` | 33 | **1.7** | 18 |
| `code-2026-08-05-a69f31-fix-claude-code-settings-hook-configuration` | 17 | **100.5** | 1 |
| `chat-2026-07-28-1ad477-wiki-orientation-and-cc-coordinator-message-draft` | 17 | 1.0 | 11 |
| `code-2026-08-01-69cc52-set-up-browser-tools-and-documentation-handoff` | 17 | 29.1 | 1 |

**`a69f31` is the session Claude Personal's packet cites** as the Good-morning-read-as-clock instance
(`…-wiki-documentation-2026-08-06.md:33-35`). Independently, from the corpus, it is the **worst
sustained drift in the top seven: median 100.5 minutes, 1 of 17 stamps within 2 minutes.** Personal
found one instance by reading. The corpus says the whole session was that way.

**`9f7640` is the counter-example and it matters.** Median 1.7 minutes, 18 of 33 within two. The
skill is achievable in Claude Code. Nothing structural prevents it.

---

## 3. `*(measured)*` — the label exists in exactly one session in the entire corpus

| | count |
|---|---|
| stamps carrying a `*(measured)*` label, corpus-wide | **57** |
| **files containing any `*(measured)*` label** | **1** |
| of the 57, aligned and same-day | 57 |
| **of those, \|error\| > 2 min — FALSE `[measured]`** | **44** |
| of those, \|error\| ≤ 2 min — genuine | 13 |

**All 57 are in `code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates.md`** — the
session that ran the day after the skill's source-priority list was corrected, and the session that
was auditing itself. **This is not a corpus-wide compliance rate. It is one session, reported with
its denominator so nobody reads it as one.**

Within that session the pattern is unambiguous and is the exact defect SKILL.md:22-33 was rewritten
to prevent:

| turn | stamped | true, from the sidecar clock | error | label |
|---|---|---|---|---|
| T38 | `2026-08-06 00:23 CDT` | 00:23:39 | **−0.7 min** | `measured via \`date\`, not estimated` |
| T290 | `2026-08-06 06:37 CDT` | 06:38:02 | −1.0 min | `measured` |
| T631 | `2026-08-06 08:32 CDT` | 08:32:16 | −0.3 min | `measured — and correcting myself` |
| T667 | `2026-08-06 08:40 CDT` | 08:39:46 | +0.2 min | `measured` |
| **T1562** | `2026-08-06 16:44 CDT` | **15:11:30** | **+92.5 min** | `measured` |
| **T1622** | `2026-08-06 17:41 CDT` | **15:40:56** | **+120.1 min** | `measured` |

All six from
`raw/transcripts/claude-code/code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates.md`;
true times converted from the sidecar's UTC `timestamp` at CDT = UTC−5.

**Early turns are measured and correct. Late turns carry the same label and are two hours ahead.**
SKILL.md, verbatim: *"A value carried forward from an earlier `date` call in the same session is
`ESTIMATED`, not `[measured]`, no matter how recently that call ran."* The corpus shows the sentence
being violated **44 times inside the one session that had read it**, which is the skill's own
prediction: *"Reading about the defect does not prevent it. Only running `date` again does."*

**The honest labels are elsewhere and they are honest.** 211 stamps across **26 files** carry a
tier-3/tier-4 disclosure — `*(ESTIMATED — check reasonability)*`, `*(estimated)*`,
`*(user-provided)*`, `*(anchored from write timestamp)*`, `*(+~3 min per exchange rule)*` — and the
23 of those that are checkable have a **median error of 0.8 minutes**. Estimating and saying so
produced better stamps than measuring and saying so.

### The precision correction that had to be made first

The first run of this detector reported **49** false `[measured]`. Hand-opening the three worst rows
found all three were the **same false positive**: prose reading *"**Measured, not asserted:**"* one
sentence after the stamp — about a table of findings, not about the clock. A bare `\bmeasured\b`
scan of a 140-character tail cannot tell a label from a word this program uses constantly.

The fix was to **read the corpus for the real vocabulary rather than recall it**: 1,473 stamp
occurrences were surveyed and the label is, essentially always, a parenthetical immediately
following the stamp on the same line. The head of the tail is now parsed, not scanned. 49 → 44, and
a regression control is in the self-test.

---

## 4. Two things Jon said that the corpus can and cannot confirm

**Can: he says "Good morning" a lot, and it is not about the morning.**
32 greeting turns found in Jon's own turns; **30 of 32 are "good morning."** Jon's own explanation,
verbatim, `personal-to-cfl-temporal-context-defect-2026-08-04.md:94`: *"I view you as meaningfully
'waking up'."* And on 2026-08-06: *"Sorry I said morning because you 'woke up'."*

**Cannot: whether a specific greeting was read as a clock.** Of the 32, only **5** were followed by
a stamped reply, and **0 of those 5** are in a file with an alignable sidecar. **So the corpus can
show the habit and cannot grade a single instance of the failure it causes.** The one documented
instance is Personal's, on 2026-08-06, and it is cited rather than re-derived: main stamped
`[2026-08-07? … morning, ESTIMATED]` — **wrong date and wrong half of day** — when the true time was
2026-08-06 18:04 CDT, evening (`…-wiki-documentation-2026-08-06.md:33-35`).

**This is the clearest UNKNOWN on the page and it is the one Jon cares about most.** It is not zero.

---

## 5. Everything else the run measured

- **CST label:** 1 stamp of 978 uses `CST`. SKILL.md:16 mandates the `CDT` label year-round. Not a
  problem; recorded so nobody re-derives it.
- **`date` call proximate to a stamp:** 4 same-day aligned stamps, 3 of them still wrong. **Do not
  read that as "running `date` does not help."** The denominator is 4 and the detector reads only
  the stamping turn and the one before it; a `date` run three tool-results earlier is invisible. It
  is printed because suppressing a weak number is how a weak number becomes a strong belief.
- **Stamped files with no alignable sidecar:** 35 of 71. Their stamps are counted in the presence
  classes and in **nothing** in §2–§3.
- **When:** stamped transcripts by month — 2026-04: 2 · 05: 26 · 06: 5 · 07: 26 (17 original) ·
  08: 12 (11 original). 9 re-emissions and 1 of this audit's own agents excluded.

---

## 6. What this record says should change about temporal-context

**None ratified. All are proposals for skills-master and a Jon Gate.**

1. **Declare the marker.** `corpus_index.MARKERS` has no entry for `temporal-context`, so its
   `USED` reads **0** for a skill that fired 802 times. The marker is the mandated format itself and
   the completion is the provenance label:
   `{"marker": ["cdt]"], "completion": ["(measured)", "(estimated", "(user-provided"]}` — one entry,
   and the file-scoped query stops lying. *Falsifier:* if the marker's false-positive rate on quoted
   stamps exceeds the 42-of-463 cross-day rate measured here, the string is too loose and the entry
   should be positional instead.

2. **Move the tier-1 rule from "before each response" to a re-measurement interval, and say what the
   interval is.** The skill already forbids carrying a value forward. It does not say *how stale is
   stale*, and 44 violations in one session say the prohibition alone does not carry. The corpus
   supports a concrete number: the within-2-minute band holds for the first stamps of a session and
   collapses after roughly an hour of wall time. **Recommend: re-run `date` when the last reading is
   older than 10 minutes, and make that a written rule rather than an implication.**
   *Evidence:* §2, §3. *Falsifier:* if per-session drift is uncorrelated with elapsed time since the
   session's last measured stamp, the interval is the wrong lever and the fix is the label instead.

3. **Make the greeting rule a rule, not a note.** *"Good morning" / "Good night" are compaction
   boundaries, not clock readings* is currently in two `exchange/` packets and in **no skill file.**
   30 of Jon's 32 greetings are "good morning" and the one graded instance produced a wrong date
   *and* a wrong half of day. **This is the cheapest change on the list and it is one sentence in
   `## Source Priority`.** *Evidence:* §4.

4. **A stamp with no provenance label should be treated as ESTIMATED by the reader.** 711 of 978
   stamps carry no label at all — the largest observable class on this page, and unlike the drift
   figures it does not depend on a sidecar. The skill mandates the label only for the estimated case,
   which means silence is ambiguous exactly where it is most expensive. **Either label every stamp or
   state in SKILL.md that an unlabelled stamp is not a measurement claim.**

5. **The two `exchange/` packets are still `status: open` and both are substantively landed.**
   `personal-to-cfl-temporal-context-defect-2026-08-04.md` proposed the source-priority replacement;
   `skills/temporal-context/SKILL.md:22-70` now carries it, dated 2026-08-05 and crediting that
   packet by name. **The proposal is applied and its status field still says open.** That is the
   derive-don't-record class, in the channel built to catch it. Closing them is a wiki-master action,
   not this page's.

6. **This page discharges the documentation half of Jon's directive; the sweep it names does not
   exist.** The 2026-08-04 packet's own closing line asks whether *"other skills carry the same shape
   — a source-priority list that omits the direct measurement. **Not swept. Worth sweeping.**"* Still
   not swept, as of this page.

---

## 7. What this record cannot see — UNKNOWN, never zero

1. **Whether a correct stamp was measured or lucky.** A turn that ran `date` and a turn that guessed
   right produce the same string. **Only the wrong ones are provable**, so every "right" figure here
   is an upper bound on compliance.
2. **192 of 1,137 transcripts have no sidecar**, and 35 of the 71 stamped ones cannot be aligned.
   Most of the corpus predates manifest v2. The drift table is a sample of the record, not the
   record.
3. **Whether a response needed a stamp at all.** SKILL.md says every response; the corpus contains
   agent-to-agent turns and tool plumbing where nobody has ever ruled that it applies. **5,514 is an
   upper bound on the failure**, and the true occasion set is somewhere between it and 802.
4. **The greeting failure, per instance.** §4. Habit visible, failure not gradeable from this corpus.
5. **Turns the extractor never wrote** — an open session's tail, a dropped record class. Absence of a
   stamp in an unextracted turn is not absence of a stamp.
6. **DST.** Every date in this corpus falls inside US DST 2026, so `CDT` = UTC−5 throughout. The
   `tc_offset_hours` branch for CST exists, is unit-tested, and **has never been exercised on real
   data.** A corpus spanning November would be the first test.
7. **claude.ai's `created_at` vs Claude Code's `timestamp` may not mean the same instant.** Both are
   read as the turn's clock. The 39-second flush lag measured on 2026-08-04
   (`…-defect-2026-08-04.md:37-39`) is a Claude Code figure; no equivalent was measured for the
   connector. At the ±1-minute band that matters; at the >60-minute band it does not.

---

## Provenance

- Counts: `scripts/audit/skill_record_ext.py --skill temporal-context`, which **registers into
  `skill_record.RECORDS`** rather than forking it and imports `spans` (== `gbs_record.spans`),
  `MERGE_CHARS`, and `corpus_index`'s reference three-class queries. `CORPUS` still resolves
  transitively to `coverage_gap.CORPUS` — one corpus root.
- Self-test **52/52**, negative controls first, including a regression control for the
  `"Measured, not asserted:"` false positive and a real before/after proving `raw/` is left byte- and
  mtime-identical.
- Directive and both instances: `exchange/personal-to-cfl-temporal-context-wiki-documentation-2026-08-06.md`
  and `exchange/personal-to-cfl-temporal-context-defect-2026-08-04.md` (Claude Personal, delivery
  only — Personal does not edit CFL's wiki or skills).
- Prior wiki coverage: `wiki/sources/reference/temporal-context-skill-2026-04-29.md`, which documents
  the **pre-correction** three-tier source priority and is therefore stale on that point; it is a
  static reference to the 2026-04-29 document and is not edited by this page.
- Verdicts are hand-made. **No skill text was modified by this page and nothing here is ratified** —
  §6 is six proposals, not six decisions.
- **A note on this run's own commits:** the first commit of the analyser was swept into a concurrent
  agent's broad `git add` (`679a644`, "B-6: RUN-state contract"). The code is intact and committed;
  the message belongs to another change. Same hazard the GBS record recorded for `3069857`.

