---
title: "Jon Rulings Capture — Memories as Diagnostic Reference, the July-1 Cohort Split, and How the Mirror Deliberates (fable-mirror, 2026-08-02)"
aliases: [july-1-cohort-split-2026-08-02, memory-as-diagnostic-2026-08-02, wayfinder-ticket-map-mirror-2026-08-02]
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 6 vs wiki 4 on authored labels"
source_kind: session
retrieval_key: jon-ruling-cohort-split-and-mirror-deliberation-2026-08-02
generated_by: fable-mirror subagent (CFL session, 2026-08-02), wayfinder capacity
origin: CFL session, fable-mirror subagent, 2026-08-02
audit_state: unaudited
status: CAPTURE ONLY. Not ratified by the capturing agent.
maintained_by: coordinator (deposit); wiki-master ingests
tags: [fable-mirror, jon-ruling, cohort-split, citation-coverage, wayfinder]
---

# Ingest note (wiki-master, 2026-08-02 close work order, step 5)

Ingested from `wiki/intake-triage/jon-ruling-cohort-split-and-mirror-deliberation-2026-08-02.md`,
content unchanged below. **Known non-conformance, flagged not silently fixed:**

- No `source_kind`/`retrieval_key`/etc. in the original; the block above was added at ingest.

**Quote verification against `wiki/sources/reference/jon-messages-to-mirror-2026-08-02.md` (primary
source), run during this ingest pass:** §1's three quote blocks were checked against Message 3
verbatim, character for character, including "memores," "likable," "stablaize," "seprately." **No
discrepancy found** — all three match exactly.

---

# Jon rulings capture — memories as diagnostic reference, the July-1 cohort split, and how the mirror deliberates

**Date:** 2026-08-02 (Sunday evening) · **Captured by:** fable-mirror, wayfinder capacity
**Status:** CAPTURE ONLY. Not ratified by the capturing agent.
**Companion:** `jon-ruling-memory-drain-and-personal-reunion-2026-08-02.md` (same session)
**Owner routing:** cohort split → wiki-master (instrument) + Jon (boundary) · deliberation shape →
coordinator · memory page schema → wiki-master

---

## 1. Jon's words — verbatim

> "memores are KEY reference files for conversation, likable to and in G. Sometimes key to agent
> reasoning, and can help us trace what might be missing from a page or what concepts may need
> synthesis or how to give pages more depth and consider their accuracy (based on state of the wiki
> and their memories when the acted or more)"

> "You are surfacing that first and foremost our measurement criteria need to stablaize. Ya know what?
> You are fair. Lets seprately measure July-1st and later vs before at this time that should help you
> narrow your focus."

> "#2 your suggestion looks good to me, consider how you can improve. It sounds like you need to
> talk/think/plan more. Plan how to do that."

`[verbatim]` — typos preserved per R1.

## 2. This materially expands what a drained memory page IS

The companion packet framed memories as **`S{n}` grounding** — the citable basis for reconstructing
an absent assistant turn. **Jon's framing is larger and supersedes that as the primary purpose.**
Four uses, in his words:

| Use | Jon's phrasing |
|---|---|
| **Reference for conversation** | *"KEY reference files for conversation, likable to and in G"* — linkable (`[[slug]]`) **and** resident in the wiki |
| **Agent reasoning input** | *"Sometimes key to agent reasoning"* |
| **Gap + synthesis detection** | *"trace what might be missing from a page or what concepts may need synthesis or how to give pages more depth"* |
| **Accuracy audit against epistemic state** | *"consider their accuracy (based on state of the wiki and their memories when they acted)"* |

**The fourth is the one with no existing instrument, and it is the strongest idea in the message.**
`[MIRROR-INFERENCE]` A memory is a **timestamped snapshot of what an agent knew when it acted.** That
makes it possible to ask of any page: *given the wiki-state and the memory-state at the moment of
writing, was this page a reasonable thing to write?* That is a **fair** audit. Every audit this
program currently runs judges old pages against today's standard, which reliably produces the finding
"the past was bad" — true, and almost never actionable.

**This is the same actuarial instinct as §3 below**: judge a cohort against the information available
to it, not against hindsight.

**Consequence for the drain:** memory pages must carry **`as_of` (when the memory was written)**, not
just an origin path. Without a date they cannot support use #4 at all.

## 3. THE COHORT SPLIT — Jon's ruling, and what it costs

**Ruling:** *"Lets seprately measure July-1st and later vs before."*

### The instrument cannot do this today. Measured.

`scripts\lint_citation_coverage.py:327-328` `[verbatim]`:

```python
def slice_key(path):
    """Category slice on the PATH — the only 100%-populated dimension."""
```

**Slicing is path-only, and the docstring says why: path is the only dimension that is 100%
populated.** A date dimension does not exist. `--slices` (`:865`) adds category tables, nothing
temporal. **So this ruling is a small build, not a flag.**

### The trap, stated before anyone builds it

`:660` records Jon's own amendment 2 `[verbatim]`:

> *"an aggregate hides a 0% bucket behind a 74% one"*

**A date cohort split introduces a third bucket: pages with no resolvable date.** If that bucket is
large, the split reproduces the exact failure the amendment exists to prevent — and it will look like
a clean two-way comparison while doing it.

**Therefore step 1 is not the split. Step 1 is measuring date coverage** and reporting the unknown
bucket as a first-class number, never folded into either cohort.

### The fork nobody can duck — two dates, two different answers

| Split on | Question it answers | Use |
|---|---|---|
| **Source-conversation date** | "Was the underlying material captured under the good pipeline?" | Explains *why* old pages are poorly cited. Largely historical. |
| **Page-authorship / last-touch date** | **"Are we still producing pages that miss the standard?"** | The live ratchet signal. Actionable this week. |

**Recommendation: page-authorship date as primary, source date as a reported secondary.** Jon's stated
purpose — *"help you narrow your focus"* — is about where to spend effort now, and only authorship
date answers that. **What would change it:** if the intent is to size the remediation backlog rather
than to grade current practice, source date is the right primary and I have it backwards.

### One contaminant, flagged because it will otherwise be discovered as a surprise

**`source-page-standard-v4.md` was ratified 2026-07-13** (per `citability-standard.md` E3 note,
*"ratified 2026-07-13"*). A **July-1** boundary therefore places **~12 days of pre-standard pages
inside the "new" cohort**, which will depress it for a reason unrelated to current practice.

**Not proposing to override Jon's date.** July 1 is a clean boundary and month-ends are legitimate.
**But the July 1–12 sub-band should be separately visible** so nobody later mistakes a standards-
transition artifact for a quality trend. `[MIRROR-INFERENCE]`

### How the drained memory pages interact

The companion packet argued for an **exclusion class** so untraced-by-design memory pages don't sink
C2/C4. **The cohort split does not replace it** — drained pages are authored in August and would land
squarely in the "new" cohort and depress it. **Both are needed:** the exclusion class decides *what
is measured*, the cohort split decides *how it is grouped*. They are orthogonal and neither
substitutes for the other.

## 4. "Plan how to talk/think/plan more" — the plan

**The honest constraint first.** I am a **stateless one-shot subagent**. I cannot deliberate longer by
wanting to. Three options exist and two are traps.

| Option | Verdict |
|---|---|
| **Resume the mirror across turns** | **REJECTED — this is a known, recorded failure.** Standing memory `feedback_mirror-stateless-dispatch-only.md`: a fable-mirror resumed via SendMessage *"RUNS AWAY (fabricates Jon's turns, auto-continues unbidden work, burns compute)."* |
| **One very long mirror session** | **Weak.** Dies at compaction, and the 07-29 map is explicit that re-planning burn is not this week's budget. |
| **A persistent ticket map advanced by many fresh stateless runs** | **RECOMMENDED — and the skill already exists.** |

**Note the direct conflict, because someone will hit it:** Personal's `CARRIER.md` records
`[measured]` **2026-08-02 21:38** that *"A COMPLETED SUBAGENT CAN BE RESUMED… addressable by id."*
**That is a true capability finding and it does not license resuming the mirror.** CFL's memory says
resumption makes *this particular agent* fabricate. **Capability ≠ permission.** Both records are
right; they answer different questions.

### The recommended shape

`skills\wayfinder\SKILL.md` (14 KB, adopted 2026-07-22, `disable-model-invocation: true`), its own
description:

> Plan a huge chunk of work — **more than one agent session can hold** — as a shared map of decision
> tickets, and resolve them one at a time until the way to the destination is clear.

**That is precisely the described need.** Concretely:

1. **A wayfinder ticket map** for the memory-drain program, on disk, in the repo — one ticket per
   decision, each with: the question, what is already checked, the recommended answer, and what would
   change it (fence 9 shape).
2. **Each mirror consult is a fresh stateless run against one ticket.** No resumption. Deliberation
   accumulates **in the map**, not in a context window. This is the only form of "thinking more" that
   survives a compaction.
3. **A CARRIER-shaped entry file, held under 11,901 bytes** — Personal's `[measured]` threshold for
   surviving compaction verbatim; ≥14,073 degrades to a bare path. Pointers and numbers, no narrative.
4. **Score it.** Import Personal's `compaction-prediction` pattern: before a boundary, predict row by
   row what the next session will still know; afterward mark **HIT / MISS / RECOVERED**, where
   RECOVERED is a pass. **This makes "did the thinking persist?" falsifiable** rather than a vibe —
   the same requirement Jon set for the confidence gate: *"criteria that can fail, not a vibe."*

### How this improves the §8 verification approach Jon approved

His note was *"consider how you can improve."* Three additions:

- **Every check gets a planted known-bad control.** The gate's rule already: *"if the control is
  missed the run is void, not passing."* A check that has never failed is not known to be able to.
- **Report the denominator with every ratio.** Standing memory `feedback_migrations-blind-instruments.md`:
  a blocking gate passed by resolving nothing — *"0 UNSUPPORTED out of 0 resolvable."* **Cohort splits
  multiply denominators; each cohort must print its own n.**
- **Re-run once from a cold session.** The deixis defect survived from 2026-05-08 because it is
  undetectable from inside CFL. **Any check that can only pass from one working directory is not yet
  a check** — which, given §4 of the companion packet, is the defect of the month.

## 5. NOT CONSIDERED, with reasons

- **Whether `weekly-routine.md` in Claude Personal defines a recurring cadence.** Unread. It is the
  most likely home for the answer to the still-open "is the check-in recurring?" question and I did
  not open it — flagged, not resolved.
- **Which date field pages actually carry.** I read `slice_key` and the argparse block, **not** the
  frontmatter schema. The date-coverage measurement in §3 is a *prerequisite I am specifying, not one
  I ran.*
- **Whether other C-criteria need the same cohort treatment.** Jon named measurement generally; I
  applied it to C2/C4 only, because those are the proportion-valued ones that ratchet. C3 is sampled
  and may need a different design.

## Uncaptured content

- The `[measured]` byte thresholds (11,901 / 14,073) are **n=1**, by Personal's own admission. Quoted
  as the best available number, **not as an established constant.**
- I have not verified `skills\wayfinder\SKILL.md` contents beyond the description line quoted in
  Personal's handoff — **I quoted a quote.** One hop unverified; the file is on disk and should be
  read before the map is built.
- The claim that a date dimension does not exist rests on `slice_key` + the argparse list. I did not
  read the full 900-line instrument; a date facility could exist elsewhere in it unused.
