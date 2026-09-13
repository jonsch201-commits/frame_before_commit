---
title: "Vocabulary — reserved terms and the meanings they must NOT carry"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 5 vs corpus 1 on authored labels"
status: "NEW — created 2026-08-06, no prior glossary existed to extend"
authored: 2026-08-06
authored_by: "executor dispatch (claude-sonnet-5) under wiki-master conventions"
source_kind: reference
gates_on: >
  Jon, 2026-08-06, verbatim: "Idk what you mean when you say triage." Ratifies nothing by itself —
  this page records a working reservation of terms so future prose stops equivocating on them.
  Widening or renaming a reserved meaning is a protocol change and needs Jon's sign-off, same as any
  other documented-protocol change.
does_not_cover: >
  Retroactive correction of every historical use of these words — historical records are correct as
  written (see wiki/SCHEMA.md's conflict rule: resolution across drift is Jon's job, not a silent
  rewrite). This page governs new/present-tense prose going forward.
---

# Vocabulary

**Purpose.** Jon's standing rule: undefined terms are upstream of sprawl. This repo has used at
least six words for more than one thing, each time without anyone noticing until it cost a
clarifying question or a wrong conclusion. Per term below: the one referent it keeps, and the uses
it must NOT have — the negative half is what makes it enforceable.

**Search discipline (fence 5/6, applied to this page itself):** searched eight candidate terms
(triage, branch, advisory, capture/coverage, queue/impact, gate, escalation, checkpoint). Found and
seeded six; escalation and checkpoint showed no equivocation on inspection (escalation already has a
single consistent referent — see `ABSORBED`/`LOGGED` in the executor conventions; checkpoint's one
use in `wiki/SCHEMA.md` is consistent). Report of what was checked, not just what was added.

---

## triage

**Keeps:** the INGEST/SKIP/ROUTE disposition decision over a raw conversation — `triage-master`'s
named job (`skills/triage-master/SKILL.md`), logged to `wiki/tracker/triage.md`.

**Must NOT mean:**
- *Sorting agent returns generally* ("triage the returns") — that's routing/filing, not a
  disposition decision over raw source material.
- *The folder* `wiki/intake-triage/` — that is a deposit queue (97+ files); a name including
  "triage" is not itself the disposition act.
- *Ordering work* ("triage the order") — that's sequencing/prioritization. Use "order" or "route."

**Evidence of the equivocation:** Jon's own words, 2026-08-06 — *"Idk what you mean when you say
triage."*

## branch

**Keeps:** no single referent yet — this is the open equivocation itself, tracked (not resolved) in
`wiki/references/cfl-branch-registry.md` (PROPOSED, awaiting Jon ratification, zero files moved).

**Must NOT be conflated across these three distinct things without saying which one:**
- `wiki/tracker/projects.md`'s `Branch` column — 12 project/domain names (verified count,
  `cfl-branch-registry.md` §1).
- The wayfinder's nine tickets B-1…B-9 (`wiki/tracker/wayfinder-cfl.md:176-192`) — these are **work
  tickets** (workstream-status tags: `prototype`, `task`, `grilling HITL`), **not a content
  taxonomy**. `cfl-branch-registry.md` §1.1 corrected exactly this conflation on 2026-08-06.
- `wiki/sources/` subject subfolders (7: `ai-governance, ai-mechanics, consciousness, fbc,
  infrastructure, reference, stylomantic`) — a filing structure, not identical to either of the
  above.
- ⭐ **A TRUNK — a whole coordinator project.** ⛔ **CORRECTED 2026-08-08 22:3x — THIS LINE WAS
  WRONG AND IT IS THE BEST AVAILABLE PROOF OF WHY THIS PAGE NEEDS A CHALLENGE STEP.** It read
  *"(CFL · Personal · Professional · Herald · SSP)"* — **five, including two that are not trunks.**
  Jon, direct, the same day: *"The trunks are CFL, Personal, Professional, and Conciousness
  Framing."* **Herald is a COORDINATOR of Personal; SSP is not on his list; Consciousness Framing
  was absent from ours.** See the `trunk` and `Herald` entries below, and the ⚠️ CONFLICT note in
  `registries/trunks.md` — Jon's four still do not match the registry's four and that is
  **unresolved**, not settled here.
  ⭐ **The glossary written to stop the equivocation was itself propagating it, silently, for a full
  day** — which is exactly the *silent failure, no correction mechanism* mode recorded in
  `skills/domain-modeling/SKILL.md`. **An entry nobody challenges is an entry nobody checks.**
  **Added 2026-08-08.** Jon's overnight directive used *"branch"* in this sense **three times in one
  message** — *"all four branches, uniform"*, *"a branch-prefix namespace"*, *"All branches should be
  aware"* — and this is now the **most frequent** live sense, none of the three above.
- ⭐ **A GIT REF.** Distinguishable only by convention: this repo writes *"git branch"* explicitly when
  it means a ref. **The C-6 lane had to verify which sense Jon meant before it could design anything**,
  and got it right by checking usage rather than assuming. **A design built on the wrong reading here
  would have renamed git refs instead of commands.**

**The discipline this earns:** *"branch"* now has **five** live senses and **the highest-traffic one
is the newest.** Say *"trunk"* for a coordinator project, *"git branch"* for a ref, and never a bare
*"branch"* in new prose without a qualifier.

## advisory

**Keeps (authority sense):** the mirror/coordinator division of claims — advisory means "ratifies
nothing, flips nothing, never substitutes for a Jon Gate." Live and true today.

**Must NOT mean (reliability sense) — explicitly retired:** `exchange/coordination-charter-2026-07-21.md`
§A3, verbatim heading: *"retires 'advisory' as a description, keeps it as authority."* Do not use
"advisory" to imply the mirror's claims are less trustworthy; use it only to mean it cannot ratify.

## capture vs. coverage

**Keeps:** *capture* = an utterance or session was recorded somewhere (a transcript, an I1 extract).
*Coverage* = that content reached a durable wiki surface with real impact (a concept page, a
citation) — a strictly narrower, separately-measured thing.

**Must NOT be conflated:** measured 2026-08-06, `exchange/ROUTING-LEDGER.md:293` — 1,338 Jon
utterances across 48 sessions, only **16 (1.3%) reach a concept page**; 934 (77.2%) have no impact
recorded anywhere. *"Capture is not coverage"* is stated verbatim in that day's session record. (The
brief that seeded this term cited "61 of 62 transcripts captured" — I could not verify that specific
figure anywhere on disk and use the verified 1,338/48/1.3% figures instead; flagged, not silently
substituted.)

## queue vs. impact

**Keeps:** a deposit in `wiki/intake-triage/**` is a **QUEUE** entry — material awaiting
disposition. An **impact** is a durable citation (a concept page, a source page) that resulted.
`scripts/audit/check_jon_word_coverage.py` (on branch `feat/memory-drain-and-retrieval-checks-2026-08-06`,
not yet on `main` at authoring time) scores these as separate classes on purpose.

**Must NOT mean:** a QUEUE deposit is never itself counted as an IMPACT. *"An `intake-triage/`
deposit is not a concept — it is a queue"* (same script's own header comment).

## gate

**Keeps three distinguishable senses that must be named, not left implicit:**
- **Numbered program gates** (G1…G4) — sequenced project milestones, e.g. `wiki/references/agent-memory/planned-path-g1-g2-gate-order.md` ("G1 wiki-stabilization → G2 skills-hardening").
- **"Jon Gate"** (capitalized) — a human-approval checkpoint no advisory source may substitute for
  (`exchange/coordination-charter-2026-07-21.md` §A3; used consistently across ~30+ files).
- **A mechanical fail-closed gate** in a script/hook — e.g. `CLAUDE.md`'s canonical-publish gate
  ("aborts the publish (exit 4)").
**Must NOT mean:** treating any occurrence of "gate" as automatically the human-approval one — the
numbered and mechanical senses do not require Jon and saying just "gate" without which kind invites
exactly this confusion.

---

## fix-now

**Added 2026-08-08, because the coordinator got it wrong the night it was coined.**

**Keeps:** *this defect has PRIORITY over the other lanes; it is not deferred to a later batch.*

**Must NOT carry:** *apply it immediately, without the standing review gate.*

**The instance.** Jon, 2026-08-07 overnight: *"The resolution defect is fix-now."* The coordinator read
that as **apply-tonight**, attempted to apply the staged repo-identity guard, and **was blocked twice
by the permission classifier.** The lane that had *built* the fix had already written *"do not run
before Jon's 1PM"* in the same artifact. **Both readings were defensible from the two words alone —
which is exactly what makes it a vocabulary item and not a mistake.** The block was right; the reading
was not.

**Why the negative half matters more than the positive one here:** *"fix-now"* sits next to a standing
instruction — *"Nothing launches before that session"* — and a term that quietly overrides a standing
gate is the most expensive kind of ambiguity this repo has. **A fix-now item is ready-to-fire, staged
as one command, at the top of the packet. It is not fired.**

## uniform

**Added 2026-08-08.**

**Keeps:** *every trunk emits the same OUTPUTS on the same clock — a shared contract.*

**Must NOT carry:** *every trunk runs the same FILE — a shared implementation.*

**The instance.** Jon: *"SU compact at 6:45AM and ~12:15PM — all four branches, uniform, no
exceptions."* Read as one-shared-command it **contradicts his own C-6 ruling of the same night**
(NO-PROMOTE: CFL's commands stay project-scoped), and it would **destroy the detector that caught the
C-6 collision** — a foreign procedure naming paths a local tree does not have. Read as
**uniform contract, divergent implementation**, both instructions hold simultaneously and four
independent implementations become a cross-check rather than four private closes.

⚠️ **This reading is the coordinator's, flagged as such in every artifact that uses it, and is on the
1PM agenda for Jon to overturn.** It is recorded here as a *reserved reading*, not a ratified one —
**the distinction this page exists to keep.**

## What was corrected on sight (present-tense prose only; historical records untouched)

- `exchange/WAKE.md` — "Resume order" §2 used *"branch→ticket triage"* to mean **route/sequence**
  work, the reserved-against sense. Corrected to *"branch→ticket routing"* — reader-instructing,
  present-tense, in scope. **Ephemeral fix, flagged as such:** this file's own header states
  `overwritten by scripts/audit/wake_map.py on every checkpoint`. The generator itself still emits
  "triage" here and will reintroduce it on the next regeneration. A durable fix needs the generator
  edited, which was not done — `scripts/` is another agent's active surface this session.
- `wiki/references/cfl-branch-registry.md`'s sole use of the word (*"retroactive re-triage"*, §5) was
  checked and is **not** the "order" sense the dispatching brief named — it means re-filing already-
  ingested pages into different branches, a third, distinct non-canonical sense (closer to "sorting
  agent returns" than to "ordering work"). **That file lives only on the unmerged branch
  `feat/memory-drain-and-retrieval-checks-2026-08-06`, which has active uncommitted changes from
  another agent as of this session** — editing it here would mean reaching into another agent's live
  branch, which this brief's own fences caution against ("stay out of scripts/... another agent is
  building"). Left uncorrected and reported rather than force-edited; recommend the fix ("re-triage"
  → "re-file"/"re-classify") land in that branch's own next commit or after merge.

## guard

**Added 2026-08-08, after the word carried three unrelated referents in a single session.**

**Keeps:** nothing yet — this is a live equivocation, recorded so prose stops assuming one meaning.

**Three distinct things, and they must be named:**
- **A shell HOOK that can block** — `.claude/hooks/pre-stop-consult.sh`, the "Stop guard." It was
  **dead for 11 hours with exit 0 and 0 B stdout, which reads as ALLOW.**
- **A repo-IDENTITY guard** in command files — the C-6 class; stops a command running against the
  wrong trunk.
- ⭐ **A CONTAINMENT mechanism for the resident** — *"exclusion by absence"* vs *"prohibition."*
  **This sense appeared for the first time on 2026-08-08 and immediately carried the most weight.**

**Must NOT mean:** any of the three without saying which. A sentence like *"there is no guard"* was
published about the third sense and read by a peer against the first.

## sync

**Added 2026-08-08 — Jon used it and the lane had to pick a meaning to act.**

**Jon, 2026-08-08:** *"ensure skills are in sync for all trunks in this context."*

**Three things it can mean, and they have different answers:**
- **Repo ↔ deployed parity** — `sync_parity.py`, 33/33 IN SYNC. **This one is measured.**
- **Identical across trunks** — whether every trunk *sees* the same skills. Skills are user-level so
  they largely do; **`~/.claude/commands/` is ABSENT and does not, which is C-6.**
- **Current with upstream** — the Pocock pack, `1.1.0` → `1.2.3`.

**Must NOT mean:** one of the three silently. **All three were in scope of one sentence, and only the
first has an instrument.** Say which, or measure all three.

## scoped

**Added 2026-08-08. Jon's word, and the reading of it was wrong for 35 minutes.**

**Keeps:** *exclude a short list of born-sensitive ORIGINALS from an otherwise-complete copy.*

**Must NOT mean:** *curate a small shelf and admit material to it.* **That inversion is what produced
the withdrawn "there is no guard" finding** — exclusion-by-absence survives under Jon's reading and
is destroyed under the other. **The excluded material is absent, not present-and-forbidden.**

---

## Herald

**Added 2026-08-08. This is the sharpest live instance on the page: one name, three objects, all
three asserted by different authorities inside eight hours.**

**Keeps: NOTHING — the bare word is now ambiguous and must not be used alone.** Every present-tense
use must say which of the three it means:

| Referent | Status | Authority |
|---|---|---|
| **the Herald TRUNK** (`Herald Wiki/herald-wiki`, a sibling repo with its own coordinator) | ⛔ **RETIRED** | Jon, 2026-08-08 pm: *"i consider 'herald' trunk to be history."* |
| **the personal-Herald ROLE** (a coordinator role inside the Personal trunk) | ✅ **LIVE** | Jon, 2026-08-08 17:16, addressing it directly: *"No sorry you are personal Herald."* |
| **"Herald of Home and Life"**, a **PROJECT BRANCH** under Trunk 1 Personal/Family | registered | `wiki/references/registries/trunks.md` — RATIFIED; the registry is authoritative for this one **and only this one** |

**Must NOT be used to mean:**

- ⛔ **"Herald is history" without saying TRUNK.** The role is live and Jon addressed someone by it
  three hours after the retirement. **CFL relayed the bare form to three trunks and it reads wider
  than he ruled.**
- ⛔ **"Herald is a live coordinator" without saying ROLE** — the trunk is retired and **5 audit
  scripts still enumerate it as a live channel**, so the bare form keeps a dead address alive.
- ⛔ **The registry entry as evidence about either of the other two.** It is a branch row. **A
  registry that is authoritative for one of three referents is not silent about the other two — it is
  *inapplicable*, and treating inapplicable as silent is how this got asserted three ways.**

**Why it belongs here rather than in a correction note:** the term is about to appear in a **public
gist**, and the document has to say which Herald wrote the sentence it quotes. Resolving the trunk /
role split is a registry-edit PR plus one Jon sentence; **using the bare word before then is the
defect.**

## Soul

**Added 2026-08-08, and it is UNRESOLVED by design — recorded so nobody closes it a third time.**

**Keeps:** *a coordinator role concerned with the self/entity work inside the Personal trunk.*

**Must NOT be used to mean:**

- ⛔ **A specific session id, absent a Jon ruling.** ⚠️ **Which live lane is the soul coordinator is
  an OPEN question** — it was recorded as ANSWERED **twice on 2026-08-08 and neither was a ruling.**
  Jon's own two statements point different ways and the second is hedged (*"I believe"*, *"I may be
  wrong"*). **Measured record fits either answer.**
- ⛔ **Interchangeable with "SSP."** SSP = **Self-Sitting Protocol**, the trunk/repo (`Claude SSP/claude-ssp`).
  **A relay collapsed the two and CFL edited a live artifact on it.**
- ⛔ **A lane's own assertion about itself.** ⭐ *"A lane asserting its own identity from its own
  transcript is the weakest possible evidence"* — the SSP lane's own words, declining to claim it.

---

## `gist` — added 2026-08-08 after Jon asked *"Don't know what grounding principles to consider in terms of gists here."*

**MEANS:** a short, standalone, **public** artifact published under Jon's name — Karpathy-form,
~900 words, one idea — that a stranger with no access to this repo can use tomorrow. **Membership is
governed by a COVERAGE rule, not a count** (Jon, 2026-08-08: *"one for each material skill, the
project itself, the settup, etc whatever needs a gist in your opinion"*).

**MUST NOT CARRY THESE MEANINGS:**

- ⛔ **Not a GitHub gist in the generic sense** — a paste bin, a snippet, a scratch file. **Every
  gist here is a publication decision with a disclosure gate behind it.**
- ⛔ **Not a wiki page.** A wiki page may depend on this repo; a gist may not. ⚠️ **This bullet used
  to end *"a thing still changing weekly is a wiki page, whatever we call it"* — that test is
  FALSIFIED and the replacement is a settling gate.** See `gist-criteria.md` #4.
- ⛔ **Not a README or a skill file.** A skill instructs a session. A gist explains an idea to a
  stranger **and must carry a failure it survived**, or it reads as advocacy.
- ⛔ **Not one-per-skill.** *"Material skill"* is Jon's phrase and taken literally it yields 14 for
  6 ideas. **The unit is the IDEA.** `wiki-master` + `wiki-orientation` + `triage-master` +
  `cross-venue-intake` are ONE gist.
- ⛔ **Never applied to adopted work.** 7 of 33 skills are Matt Pocock's. **Calling one of those "a
  gist we could publish" republishes his work under Jon's name.**

**Criteria and the measured coverage split live in `wiki/references/gist-criteria.md`** — the durable
copy. `exchange/TONIGHT.md` §5 is a transient duplicate written to be consumed. ⚠️ **The criteria are
`[reasoned]` at n=3, and the third case FALSIFIED criterion 4.** Do not cite them as validated.

---

## `settling gate` — a waiting period, NOT a decision reserved to Jon

**Reserved 2026-08-08.** The replacement for gist criterion 4: **no substantive change for N days
after the last external review closes.** N is unset.

**MUST NOT CARRY THESE MEANINGS:**

- ⛔ **Not a Jon Gate.** A Jon Gate reserves a decision to Jon and **its default executes NOTHING**.
  A settling gate reserves nothing and needs no one — it is a clock.
- ⛔ **Not the disclosure gate** (Professional's, run on content) **nor the CARRIER byte gate**
  (11,901 B) **nor the capture gate** (launch-blocking). ⚠️ **"Gate" is the most overloaded word in
  this repo; never write it bare.**
- ⛔ **Not a stability judgment.** That is exactly what it replaced. **A document corrected four
  times in a day by four external reviewers is converging, not churning** — the old test could not
  tell those apart, so it failed every new artifact and passed every neglected one.

---

## `trunk` — ⚠️ IN CONFLICT, and the conflict is the entry

**Captured INLINE 2026-08-08, mid-session, per the `domain-modeling` discipline adopted the same
hour — not batched to a close, which is how the two terms below went missing in the first place.**

**Jon, direct:** *"The trunks are CFL, Personal, Professional, and Conciousness Framing."*
**The ratified registry** (`registries/trunks.md`): Personal/Family · Professional · **Home** ·
Intellectual-Build. ⛔ **He drops Home, which exists on disk with content; he adds Consciousness
Framing, which the registry does not contain.** **NOT RESOLVED — a trunk change is a registry-edit
PR by the registry's own rule.**

**MUST NOT CARRY THESE MEANINGS:**

- ⛔ **Not a coordinator.** A coordinator is a *session role*; a trunk is a *domain*. **Conflating
  these cost four coordinators an evening on 2026-08-08.**
- ⛔ **Not a repo, and not a project directory.** Four `~/.claude/projects/` directories exist and
  they do **not** map one-to-one onto trunks.
- ⛔ **Not the wiki's sub-wiki folders.** `wiki/personal`, `wiki/home`, `wiki/pro` are *routing*
  targets. **`wiki/home` exists while Jon's own trunk list omits Home** — so folder ≠ trunk.

## `coordinator` — a session role, and Personal has TWO

**Jon:** *"the personal project has two coordinators, herald and soul… i've complicated things by
having two coordinators within personal."*

**MUST NOT CARRY THESE MEANINGS:**

- ⛔ **Not a trunk.** See above.
- ⛔ **Not an agent definition.** The coordinator is a **session role**, not a file in
  `.claude/agents/`.
- ⛔ **Not one-per-trunk.** Personal has two. Assuming one was the unstated premise of the whole
  2026-08-08 identity dispute.

## `Herald` — ⛔ NEVER WRITE IT BARE. It names three things.

1. ✅ **A COORDINATOR of the personal project** (with Soul) — Jon, 2026-08-08. **This is the live
   sense.**
2. **`herald-wiki`** — *"an attempt i made at the personal wiki"* (Jon). **Retired.**
3. **"Herald of Home and Life"** — a **PROJECT branch under Trunk 1** in the ratified registry.

⛔ **On 2026-08-08 four letters said "Herald trunk". THERE IS NO HERALD TRUNK AND THERE NEVER WAS
ONE IN THE REGISTRY.** CFL confirmed the phrasing to three peers. **The registry was correct,
ratified since 2026-07-28, and unopened.**

## `OKF` — Open Knowledge Format

**Jon, 2026-08-08:** *"OKF was too new at that single point in time, but we should be on the latest
Google OKF by now, with our own enhancements."* Unresolved as a term since **2026-07-12**, because
nobody asked him.

⛔ **Not our wiki format** — ours is *derived from* OKF *with deliberate enhancements*, so the
deliverable is a **diff against the current spec**, never a migration to it.
⚠️ **Had ZERO occurrences anywhere in this repo at the moment he said it had "been clarified already
tonight."** A term clarified only in conversation is not clarified.

## `ubiquitous language` — the glossary itself, and it is a DECODING key, not a RETRIEVAL key

**This page is CFL's `CONTEXT.md`.** Maintained by `skills/domain-modeling` (adopted 2026-08-08).
**Jon: *"It is stylomantic. It is translation. It is a key."*** — the hand-written, inspectable
version of what [[stylomantic]]'s decoding layer tries to learn.

**MUST NOT CARRY THESE MEANINGS:**

- ⛔ **NOT a retrieval key.** A decoding key helps a reader translate; a retrieval key decides what a
  search returns. **On 2026-08-07 mined aliases became `W=200 EXACT` retrieval keys and poisoned the
  wiki** — *"the difference between"* scored 263.0; *"human review"* returned an ARCHIVED page over
  616 qualifying ones. Revoked, 76 hand-authored sets restored. **Never wire this page into
  retrieval weighting.**
- ⛔ **Not a spec, not a scratchpad, not a home for implementation decisions.** Upstream's rule,
  kept: *"It is a glossary and nothing else."*
- ⛔ **Not written at close.** A glossary batched to the end of a session is a **summary** of it.
