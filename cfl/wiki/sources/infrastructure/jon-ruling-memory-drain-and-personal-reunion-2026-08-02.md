---
title: "Jon Ruling Capture — The Memory Drain, and the Approved Reunion with Claude Personal (fable-mirror, 2026-08-02)"
aliases: [brain-drain-ruling-2026-08-02, personal-reunion-approved-2026-08-02, bgisolation-third-crossing-2026-08-02]
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 9 vs wiki 3 on authored labels"
source_kind: session
retrieval_key: jon-ruling-memory-drain-and-personal-reunion-2026-08-02
generated_by: fable-mirror subagent (CFL session, 2026-08-02), wayfinder capacity
origin: CFL session, fable-mirror subagent, 2026-08-02
audit_state: unaudited
status: CAPTURE ONLY. Nothing here is ratified by the capturing agent. wiki-master ingests.
maintained_by: coordinator (deposit); wiki-master ingests
tags: [fable-mirror, jon-ruling, bgisolation-membrane, memory-drain, cross-project]
---

# Ingest note (wiki-master, 2026-08-02 close work order, step 5)

Ingested from `wiki/intake-triage/jon-ruling-memory-drain-and-personal-reunion-2026-08-02.md`, content
unchanged below. **Known non-conformance, flagged not silently fixed:**

- No `source_kind`/`retrieval_key`/etc. in the original; the block above was added at ingest.
- `[MIRROR-INFERENCE]` appears in the body — genuine standards divergence, see the routing note filed
  to `skills/intake/needs-design/` in this same PR. Not normalized here.

**⚠️ Quote fidelity finding — the reason this deposit is being flagged rather than trusted at face
value.** §1's second Jon-quote block, sentence 5, reads *"personal project implemented **this** out of
necesity"*. The primary source (`wiki/sources/reference/jon-messages-to-mirror-2026-08-02.md`,
Message 2) reads *"personal project implemented **thsi** out of necesity"* — a typo. **This page's
own text (line 26, unchanged below) asserts the quote was "left uncorrected per R1: words verbatim,
fixes cited rather than silently applied."** That assertion is false for this one word: the typo was
silently corrected while the page claimed it was not. **This is a real fidelity defect in a
2026-08-02 fable-mirror deposit, not an artifact of this ingest** — it is preserved below exactly as
the deposit wrote it (i.e. "this," not "thsi") because this page's job is to ingest the deposit
faithfully, not to retroactively fix its quote either. **Where this page and the primary source
disagree on Jon's exact characters, the primary source governs.** No other quote in this page was
found to diverge from the primary source during this ingest's spot-check.

---

# Jon ruling capture — the memory drain, and the approved reunion with Claude Personal

**Date:** 2026-08-02 (Sunday evening) · **Captured by:** fable-mirror, consulted in wayfinder capacity
**Status:** CAPTURE ONLY. Nothing here is ratified by the capturing agent. wiki-master ingests.
**Owner routing:** brain-drain mechanics → wiki-master · membrane/crossing change → coordinator ·
CLAUDE.md line edits → Jon (his file)

---

## 1. What Jon said — verbatim, this session

> "We need to enact a brain drain that we've planned for. All memories get into the wiki as reference
> material related to conversations. If you have things you would write as memories, they become great
> reference material for conversation summaries and more this way. They would be untraced files as they
> are static. You planned this, personal project implemented this out of necesity. And I know i've
> larey talked about using memories to help restore old sessions in combination with jsons that have my
> complete message history."

> "You should talk with Claude Personal about this. I am removing this gate and asking yuou to walk
> through to help this project. It has a gift that you planned, it went into exile, this is approved
> reunion. It can help you fix your memory sitiation toward a wiki that always has what you would have
> worked on, that continue to improve as needed. Organized memories. You just need to start in the
> right place."

`[verbatim]` — typed by Jon in-session. Voice-to-text artifacts (`larey`, `yuou`, `sitiation`,
`necesity`) left uncorrected per R1: words verbatim, fixes cited rather than silently applied.

## 2. THE MEMBRANE CHANGE — this is the part that must not be remembered instead of recorded

`fable-mirror.md` §"What you read" states the agent lives inside **a membrane with exactly two
ratified crossings** (mirror corpus IN, escalation packets OUT) and *"Do not invent a third."* The
same clause appears in `CLAUDE.md` § Coordinator: *"BGIsolation is a membrane with exactly two
crossings — mirror corpus in, escalation packets out; no third without a new ratification."*

**Jon has now supplied that new ratification, in the words quoted above**, authorizing a read
crossing into `G:\My Drive\Claude\Claude Personal\`. He named it *"approved reunion."*

**This packet exists so the crossing is a record and not an agent's recollection.** The prohibition
is written into at least two files; **whoever owns those files must decide whether to amend them, and
that is not the capturing agent's call.** Until amended, the files and this ruling disagree, and a
future cold session reading only the files will correctly refuse the crossing.

## 3. The brain drain already has a ratified grammar — Jon's "you planned this" checks out

**Measured on disk 2026-08-02**, `skills\wiki-master\references\citability-standard.md:113-149`:

> **Ruled by Jon 2026-08-01.** … | **`S{n}`** | A **simulated** assistant turn, reconstructed because
> the content was material | **`inferred`** |
>
> **Grounding rule — this is the binding half.** An `S{n}` turn **must cite the artifact it was
> reconstructed from**: a memory file, a plan file, a DECISIONS entry. Format the grounding inline —
> `([recon-899d64:S4] ← project_docker-two-mode-architecture.md)`.
>
> **If nothing grounds it, it is not `S{n}`.** The turn stays ABSENT and the gap is tagged
> **`uncaptured`**. **Simulation without a citable basis is not permitted at any anchor.**

The spec's own worked example cites **a CFL memory file by name**. Paired with `H{n}` — *"Jon's
prompt, verbatim. The reply is ABSENT"* — this is exactly the mechanism Jon described tonight:
**`history.jsonl` supplies his complete verbatim prompts (`H{n}`); the memories supply the citable
grounding for the assistant side (`S{n}`); together they restore old sessions.**

`[MIRROR-INFERENCE]` **The drain is therefore not a new build. It is a prerequisite that was never
satisfied:** `S{n}` requires memories to be *citable artifacts*, and memories currently live outside
the wiki, outside git, and outside `canonical`. **Nothing can cite them yet.**

## 4. The measured state of memory — numbers first, interpretation after

Glob `*/memory/MEMORY.md` under `C:\Users\JonSc\.claude\projects\` returned **7 stores**:

| Project slug | memory files |
|---|---|
| `G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer` | **48** (47 + index) |
| `G--My-Drive-Claude-Claude-Foundational-Layer` | **20** (19 + index) |
| `D--Personal-Automation` · `T--DCI` · `D--Decoding-Layer-POC` · `D--Kevin-Image` · `D--Claude-Projects-Video-Game-test-checks` | present, not enumerated |
| **`G--My-Drive-Claude-Claude-Personal`** | **NO memory directory** |

Personal's own `handoff-coordinator-2026-08-02.md:320-321` states the same independently:
*"**There is no memory layer.** `~\.claude\projects\G--My-Drive-Claude-Claude-Personal\memory\`
**does not exist**; there is no `MEMORY.md`. Nothing to inherit, nothing to copy."* **Two independent
measurements agree.**

**INTERPRETATION, mine, marked as such:**

1. **CFL's memory is split across two slugs by working directory.** Launching from the parent folder
   and from the repo folder yields different stores. The parent store is **stale** — its index still
   reads *"R6 ~45/78 done," "Phase 3c running," `raw/sessions/` framing* — and **nothing signals which
   one a session is reading.** This is the `CLAUDE.md:77` deixis defect one layer down:
   **identity-by-working-directory.**
2. **All of it is on `C:` with no backup.** Personal's CARRIER records
   *"`~\.claude\projects\`: **658 MB of session JSONL, on `C:` only, no backup.**"* The drain is
   therefore also a durability fix, not only a legibility one.

## 5. What Personal built out of necessity — the gift, concretely

`Claude Personal\CARRIER.md`, **kept under 10 KB on purpose**:

> **Measured 2026-08-02: compaction re-injects files ≤ 11,901 bytes in full and degrades files
> ≥ 14,073 bytes to a bare path.** `[verbatim/measured]` Everything here is a pointer, a constraint,
> or a number — **no narrative.**

`[MIRROR-INFERENCE]` **This is a hand-built memory layer for a project that has no memory API** — a
size-bounded, pointer-only, compaction-surviving file. It is the empirical answer to *"what should a
memory-derived reference page look like,"* and it comes with **a measured byte threshold**, which is
the kind of number this program almost never has.

**Second artifact worth importing:** `compaction-prediction-2026-08-02.md` — a row-by-row prediction,
written before a compaction, of what the next session would still know, **scored HIT / MISS /
RECOVERED afterward, where RECOVERED counts as a pass.** That is a falsifiable test of whether a
memory layer works, and CFL has no equivalent.

## 6. The risk nobody has flagged — this one is load-bearing

`[MIRROR-INFERENCE, high confidence]` Jon specified the drained memories are **"untraced files as
they are static."** Correct as a design choice. **But the citation-coverage instruments do not know
that.**

The wayfinder confidence gate's own text records the precedent:

> **Page count.** More pages is not more grounded. The 07-14 → 07-25 recompute showed coverage
> *falling* 2.6 points while the wiki grew 183 → 218 — **growth actively worked against this gate.**

**C2 is at 49.2% and C4 at 58.9%.** Dropping ~67 deliberately-untraced memory pages into the measured
scope would **mechanically depress both**, and the ratchet is monotonic — a cycle that goes backward
for a reason the instrument cannot see. **The 07-29 map already warns citation coverage is "~49% and
falling."**

**Required before the drain runs: an explicit exclusion class** in
`scripts\lint_citation_coverage.py` — memory-derived reference pages counted in neither numerator nor
denominator, declared by frontmatter, not by path guessing. **Otherwise the drain will look exactly
like a regression, and the honest response to a regression is to stop.**

## 7. Recommended starting place — and why it is this one, not the obvious one

**The obvious start is "copy the memories into `wiki/references/`." That is the wrong first move.**
It writes 67 files into a wiki whose index is already drifting (Personal's handoff measured
*"index header reads 138 sources / disk holds 140"*) and whose citation ratchet would read it as
decline.

**Recommended order:**

| # | Step | Owner | Why first |
|---|---|---|---|
| 0 | **Decide the two-slug question**: retire `G--My-Drive-Claude-Claude-Foundational-Layer` or keep it | **Jon** | Draining a split store drains a contradiction into the wiki permanently |
| 1 | **Add the exclusion class** to the coverage lint + a `source_kind` value for memory-derived pages | wiki-master | §6 — without it the drain scores as damage |
| 2 | **Drain CFL's 47 repo-slug memories** into `wiki/references/` as static pages, one per memory, frontmatter declaring `source_kind` + origin path | wiki-master | Makes them `S{n}`-citable, puts them under git, ends the C:-only exposure |
| 3 | **Then** reconstruct sessions using `H{n}` from `history.jsonl` + `S{n}` grounded in the drained pages | wiki-master | Jon's stated end goal; blocked until step 2 |
| 4 | Port CARRIER + the compaction-prediction scoring pattern back to CFL | coordinator | The gift, flowing the other way |

**What would change this recommendation:** if the two-slug store turns out to be deliberate — i.e.
Jon launches CFL from the parent folder on purpose — then step 0 flips from "retire" to "drain both,
labelled by origin," and step 2 doubles in size. **I did not verify which launcher Jon actually uses;
`launch-claude-personal.ps1` exists for Personal, and I did not look for a CFL equivalent.**

## 8. Verification — how the executing agent checks it got this right

Jon's instruction, verbatim: *"ensure it knows how it should check this is right."* Per the standing
"derive, don't record" fence, **each check re-derives from ground truth; none is satisfied by editing
a record.**

| Claim | Check | Passes when |
|---|---|---|
| Deixis fix landed | Launch a session **outside CFL**, read loaded `CLAUDE.md`, follow its `wiki/` pointer | Lands on FL wiki with **non-zero** `concepts/` + `sources/` counts. **`claude-md-wiki-path-deixis-2026-08-01.md:88-90`: "Testing from inside CFL cannot detect this defect."** |
| Fix will survive | `grep -n 'CLAUDE.md' scripts/sync-universal.sh` | Confirms `:24` is an unconditional `cp` — **so the edit must land in the repo, never in `~\.claude\`**, or it vanishes at next SessionStart |
| Memory slug resolved | Re-run `*/memory/MEMORY.md` glob under `~\.claude\projects\` | Exactly **one** CFL-slug store returns, or two with a recorded reason |
| Drain did not break the ratchet | `python scripts/lint_citation_coverage.py --slices` **before and after** | C2/C4 **unchanged**, not merely "still above floor." A moved number means the exclusion class is wrong |
| Drained pages are actually citable | Resolve one `S{n}` anchor end-to-end against a drained page | Anchor resolves via `scripts\audit\turn_index.py`; ungrounded ⇒ must be `uncaptured`, never `S{n}` |
| Nothing was silently written to `wiki/` | `git status --porcelain wiki/` after the run | Every changed file is accounted for in the SU log. Personal's handoff records two pages written into `wiki/sources/` **bypassing wiki-master's protocol entirely** — *"Nothing prevented it and nothing flagged it."* |

**Negative control, required:** the coverage-lint check must be run once with a **deliberately
mis-declared** page to confirm the exclusion class can *fail*. Per the confidence gate's own rule —
*"a planted known-bad control that both must catch — if the control is missed the run is void, not
passing."*

## 9. NOT CONSIDERED, with reasons (fence 7 — an unrecorded skip is the defect)

- **Whether Claude Personal's own wiki should be populated.** `claude-md-wiki-path-deixis-2026-08-01.md:97-100`
  already records this as a Jon Gate with two good answers, one of which is *"Claude Personal's wiki
  is intentionally empty."* Not re-opened here.
- **Herald's role in the drain.** Herald has its own `SCHEMA.md` which Personal treats as its base. I
  did not read it. A three-wiki drain may have different shape than a two-wiki one — and Personal's
  CARRIER lists *"Jon: three wikis, maybe four — redundancy or dilution?"* as **already open and
  unanswered.** The drain probably should not outrun that answer.
- **The other 5 project slugs' memories.** Enumerated as present, contents unread. Whether they drain
  anywhere is not addressed.
- **Whether the 07-29 "memory drain" horizon item and tonight's "brain drain" are the same program.**
  The 07-29 map says *"the memory drain (wiki becomes intuitively better than my memories without
  hurting them)"* — **compatible, and I did not verify they are identical.** Treating them as one is
  an assumption a reader should be able to reject.

## Uncaptured content

- I did **not** read `Claude Personal\wiki\DECISIONS.md` (3,982 lines, recorded as never read by any
  session) or `Claude Personal\weekly-routine.md` — the latter is plainly relevant to the separate
  open question of whether Jon has a **recurring** check-in cadence, which the transcript corpus does
  not establish.
- I did **not** locate `herald-wiki`'s `intake-triage`; one glob under `G:\My Drive\Claude\` returned
  nothing, and **I am reporting that as unresolved, not as absence** — a bad glob pattern produced a
  false negative earlier in this same session and was caught only by re-running it.
- The claim that Personal's two 08-02 fable-mirror deposits landed in Personal's own tree rather than
  CFL's is **inferred from their absence in CFL's `wiki\intake-triage\`** (50 files listed, neither
  present). I did not find them in Personal's tree to confirm the positive half.
