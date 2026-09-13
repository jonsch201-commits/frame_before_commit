---
title: "Reviewed Outbound Channel Design + Jon's Five Answers (fable-mirror capture, 2026-08-02)"
aliases: [outbound-envelope-design-2026-08-02, cohort-groundability-ruling-2026-08-02, attainable-vs-total-2026-08-02]
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 6 vs wiki 3 on authored labels"
source_kind: session
retrieval_key: channel-design-and-jon-answers-2026-08-02
generated_by: fable-mirror subagent (CFL session, 2026-08-02), wayfinder capacity
origin: CFL session, fable-mirror subagent, 2026-08-02
audit_state: unaudited
status: CAPTURE + DESIGN PROPOSAL. Not ratified by the capturing agent.
maintained_by: coordinator (deposit); wiki-master ingests
tags: [fable-mirror, jon-ruling, cross-project-channel, cohort-split, attainable-ratchet]
---

# Ingest note (wiki-master, 2026-08-02 close work order, step 5)

Ingested from `wiki/intake-triage/channel-design-and-jon-answers-2026-08-02.md`, content unchanged
below. **Known non-conformance, flagged not silently fixed:**

- No frontmatter in the original; the block above was added at ingest.
- `[MIRROR-INFERENCE]` appears in the body — see the standards-divergence note filed to
  `skills/intake/needs-design/` in this same PR; not normalized here.
- FORM: captured design/ruling packet, not a raw session extraction; `## Key Claims` in the v4.0
  sense is not present. Disclosed rather than backfilled.

**Quote verification against `wiki/sources/reference/jon-messages-to-mirror-2026-08-02.md` (primary
source), run during this ingest pass:**

| Quote in this page | Found in Message | Match |
|---|---|---|
| §0, "I absolutely will not rely it by hand…" | Message 5 | Exact |
| §2, "Persional reunion is standing." | Message 5, clause 3 | Exact |
| §3, "cohort split is based on json, if you can't ground back to that then its a defect…" | Message 5, clause 1 | Exact |
| §4, "ratchet against atainable, but explain why atainable isn't total eventually…" | Message 5, clause 4 | **Discrepancy — see below** |

**Three of four Jon quotes match the primary source character-for-character, including typos
("Persional," "atainable," "undertand").** The fourth (§4) does not: the primary source
(`jon-messages-to-mirror-2026-08-02.md`, Message 5) reads *"not recover some **reaoning** via
revival"*; this deposit's own quote of the same clause reads *"not recover some **reasoning** via
revival"* — the typo is silently corrected. **This is the same class of error as the "thsi"→"this"
finding in `jon-ruling-memory-drain-and-personal-reunion-2026-08-02.md`** — a second instance of a
2026-08-02 deposit normalizing one of Jon's typos inside a block marked `[verbatim]`. Preserved here
exactly as the deposit wrote it (i.e. "reasoning," not the primary source's "reaoning") because this
page's job is to ingest the deposit faithfully, not to silently correct it to match the primary
source either — both directions of silent alteration are the same fence violation. Where the two
disagree, `jon-messages-to-mirror-2026-08-02.md` is the primary source and governs.

---

# Reviewed outbound channel + Jon's five answers — 2026-08-02

**Captured by:** `fable-mirror` (CFL), wayfinder capacity · **Status:** CAPTURE + DESIGN PROPOSAL.
Not ratified by the capturing agent.
**Owner routing:** channel mechanics → coordinator · lint changes → wiki-master · fence/agent-def
edits → Jon (his files)

---

## 0. Jon's correction to me, recorded because I was wrong

> "I absolutely will not rely it by hand. If you want to ensure messages go through some kind of
> review, fine make main do that work. I understand your need for security, but I am in control of
> both of these wikis and i'm asking you to talk with it."

**My recommendation was manual relay. That was wrong** — it converted an agent's write-fence into
Jon's labor, which is the exact cost structure this program exists to avoid. **Review is the
legitimate requirement; hand-carrying is not the way to get it.** Jon's framing — *make main do that
work* — is adopted below.

## 1. THE DESIGN — reviewed outbound, no fence weakened

**Tested this session and it works.** `fable-mirror` successfully wrote to
`wiki\intake-triage\outbound\to-claude-personal\` — the write-fence permits it because it resolves
**under** `wiki/intake-triage/`. **No hook change, no agent-definition change, no loosening.**

```
wiki/intake-triage/outbound/<destination-project>/<date>-<slug>.md   ← envelope (mirror writes)
wiki/intake-triage/<payload>.md                                      ← message body (mirror writes)
                     │
                     ▼  main / coordinator delivery step
        <destination>/exchange/inbound/<file>.md                      ← delivered verbatim
```

**Properties, stated so nobody optimizes one away:**

| Property | Why it is there |
|---|---|
| Mirror writes **only** under its sanctioned path | The membrane is unchanged. The fence still catches a genuine escape. |
| Envelope and payload are **separate files** | The reviewer reads **exactly what ships**; nothing is re-typed between review and send. |
| Delivery verified by **sha256 match** | *"A delivery that alters the payload is a defect, not a courtesy."* Detects a helpful reviewer silently editing. |
| Delivery is **main's job**, not Jon's | Jon's correction, §0. |
| Envelope names its **authorization** | So a cold reviewer can check the crossing was ruled, not assumed. |

**Where the delivery step should live — recommendation:** the standard-update lane, alongside
`exchange_inbox.py`. **Rationale:** CFL already has a documented failure of *deposit-only channels*
(2026-07-27, four unread Herald messages, one carrying the day's most consequential correction).
**A send-only channel fails the same way.** The delivery step must therefore be paired with a **read**
step for Personal's `outbox/` in the same run, or this rebuilds the known defect facing the other way.

**What would change the recommendation:** if traffic becomes frequent enough that SU-cadence latency
matters, promote it to a hook. **One message is not evidence of frequency** — but Jon has now ruled
the reunion **standing**, so this will not stay at one.

## 2. THE STANDING RULING — and the four places that still disagree

> "Persional reunion is standing."  `[verbatim]`

**This flips my prior recommendation.** In the earlier packet I said one message is not routine and
recommended against config changes. **Jon has ruled it standing, so the enforcement layer must catch
up.** Four points still state the old two-crossing rule:

| Point | Action |
|---|---|
| `.claude\hooks\fable-mirror-write-fence.sh` | **Leave as-is.** §1 works within it. Changing it is now unnecessary — that is the design's main virtue. |
| `.claude\agents\fable-mirror.md` | **Needs amendment** — add the outbound-envelope convention as the sanctioned form of a third-party message. Owner: Jon (identity-adjacent per the purpose-based fence). |
| `CLAUDE.md` § Coordinator ("two crossings") | **Needs amendment** — Jon's file. |
| `exchange\coordination-charter-2026-07-21.md` | **Unread by me.** Flagged, not assessed. |

**The hook should stay strict precisely because the design routes around nothing.** A fence that is
never tested is not known to work; this one blocked a real crossing on its first live test tonight.

## 3. ANSWER 1 — the cohort is **groundability**, not a date

> "cohort split is based on json, if you can't ground back to that then its a defect. Determine the
> date as a way to describe this."  `[verbatim]`

**This is a materially different instrument than the one I specced, and it is better.** I proposed a
date split. Jon's criterion is:

> **Can this claim ground back to a surviving JSON? If not, it is a defect.**

**The date is a *label* for the boundary, not the test.** Consequences:

1. **A post-cutoff page that cannot ground is a defect**, full stop — no cohort excuses it.
2. **A pre-cutoff page that CAN ground is not excused either** — many can, via `history.jsonl`, the
   surviving originals, or the memory snapshot. **The date must never become an alibi.**
3. **The instrument should resolve per-claim against actual artifacts on disk**, and use the date only
   to *report* results. Grounding is measured; the date is a caption.

**The date, from `project_cc-retention-cleanupperioddays.md` (2026-07-25, 8 days old, freshness-warned):**

- Sessions **2026-05-01 → 2026-06-16: GONE** (29).
- Sessions **2026-06-21 → 2026-07-21: SURVIVE.**
- **Descriptive boundary: 2026-06-21.**
- **`2026-06-17 → 06-20` is unstated** — neither listed. **Must be measured, not assumed.** This is
  the first task, and it is small.

**⚠️ Do not ship this date from the memory file.** It is 8 days old and carries a point-in-time
warning. **Re-derive it by enumerating surviving JSONL on disk** — the memory says what was true on
2026-07-25, and this program's characteristic failure is a fact written down once and then diverging.

## 4. ANSWER 4 — why `attainable` is not `total`, and why it should converge

> "ratchet against atainable, but explain why atainable isn't total eventually if we have raw json. I
> undertand we may choose to not recover some reasoning via revival of a json and asking for detailed
> reasoning, but we can get much."  `[verbatim]`

**Jon is right, and the correct model is two ratchets, not one.**

```
coverage / attainable   ← effort against what is currently recoverable
attainable / total      ← effort against what has been recovered AT ALL
```

**`attainable` is not a ceiling. It is a frontier, and it moves.** Treating it as fixed would be the
`RATIO_FLOOR` error inverted — a bar set so low it always clears.

### Where `attainable == total` (and coverage should reach 100%)

**Any session whose JSONL survives.** The full turn text is in the file. Nothing is lost; the work is
merely undone. **For post-2026-06-21 material there is no excuse and no ceiling.**

### Where `attainable < total` — enumerated, because a vague ceiling is an alibi

| Cause | Recoverable? |
|---|---|
| **The 29 deleted sessions** (2026-05-01 → 06-16) | **No.** Programmatic delete, no Recycle Bin, no Anthropic path (GH #64721), VSS postdates. **Genuinely permanent.** |
| **…but partially:** `history.jsonl` holds **every typed prompt + sessionId + timestamp**, 2026-03-10 → 07-24 | **Yes, the human side.** Made 25 of 29 dead sessions *measurable*. `H{n}` anchors exist precisely for this. |
| **…and further:** git commits from each session's window record the action layer at full fidelity | **Yes, partially.** Named in the retention memory. |
| **Thinking blocks encrypted in `signature`** (CC v2.1.72+) | **No.** The reasoning is not in the file. Pre-boundary JSONLs *are* readable — `1e609faf` (2026-04-26) has 166 plaintext blocks. **Era-dependent: probe the file, don't assume.** |
| **Archive caps:** `tool_result` truncated to 300 chars; `tool_use` keeps first key / 80 chars (**~12% of tool data retained**; a `Write`'s content never captured) | **No, for archived copies** — but **yes if the original JSONL survives.** This is a *converter* defect, not a data loss. **Re-extraction recovers it.** |
| **`AskUserQuestion` answers not captured** | **No.** Only the assistant's restatement survives. Parser fix unbuilt as of 2026-07-26. |

### The answer to Jon's actual question

**`attainable` falls short of `total` for exactly three irreducible reasons** — the 29 deleted
sessions, signature-encrypted thinking, and dropped `AskUserQuestion` answers. **Everything else on
that list is recoverable work that has simply not been done yet**, and the largest single item —
the ~88% of tool data lost to converter caps — is **recoverable by re-extraction from JSONLs that are
still on disk.**

**So Jon's instinct is correct: `attainable` should climb toward `total` and the gap should be
shrinking every cycle.** The honest form is to **report `attainable` with its shortfall itemized**, so
that a static `attainable` is visibly a *choice not to recover*, not a fact about the world.

`[MIRROR-INFERENCE]` **The failure mode to guard against:** `attainable` becoming a soft number that
drifts down to whatever was convenient. **Fix: `attainable` must be computed from an enumerated
artifact list, never asserted.** If a claim is scored unattainable, the report must name which of the
three irreducible causes applies. **"Unattainable" without a cause is a defect, exactly as Jon framed
it in Answer 1.**

## 5. ANSWER 2 — "parent folder memory slugs?"

Jon queried the term. Plainly:

Claude Code keys memory to the **working directory it was launched from**. Two directories are in
play:

| Launched from | Slug | Contents |
|---|---|---|
| `…\Claude Foundational Layer\claude-foundational-layer\` (the **repo**) | `G--…-Foundational-Layer-claude-foundational-layer` | **48 files. Current.** |
| `…\Claude Foundational Layer\` (the **parent folder**) | `G--…-Foundational-Layer` | **20 files. Stale** — index still reads *"R6 ~45/78 done," "Phase 3c running."* |

**Two stores, no signal which one a session is reading.** Same root cause as the `CLAUDE.md:77`
deixis defect: **identity-by-working-directory.**

**Recommendation:** treat the repo slug as canonical; **archive** the parent's 20 files into the drain
labelled with their origin and `as_of`, rather than deleting them — they are a genuine 2026-05→07
epistemic snapshot and are exactly the kind of artifact Jon's use-case #4 (auditing a page against
what was known at the time) needs. **What would change it:** if Jon deliberately launches from the
parent, both stores are live and both must drain.

**Both are already preserved** in `raw\originals\claude-code\jsonl\2026-07-24\projects\<slug>\memory\`
— so nothing is at risk while this is decided.

## 6. Open — carried, not resolved

- **`2026-06-17 → 06-20`**: survived or not? Small, first, blocking the date caption.
- **Re-derive the cutoff from disk**, not from the 8-day-old memory.
- **Personal's `outbox/` read step** must ship with the delivery step (§1) or this becomes a
  send-only channel.
- **`weekly-routine.md`, `DECISIONS.md`, `coordination-charter-2026-07-21.md`** — unread by me.

## Uncaptured content

- The `attainable` taxonomy in §4 is assembled from **three memory files** (`cc-retention…`,
  `cc-jsonl-thinking-signature-only`, `askuserquestion-answers-not-captured`), all point-in-time and
  one 8 days old. **Each row should be re-verified against disk before the instrument is built on it.**
- I did **not** read `lint_citation_coverage.py` beyond `slice_key` and the argparse block, so I do
  not know how hard `attainable` is to add.
- I did **not** verify the `2026-07-24` originals snapshot against its own `manifest.csv`.
- Whether `exchange\inbound\` is the correct CFL→Personal direction is **still unconfirmed** — taken
  from Personal's `CARRIER.md`. The delivery step should verify before first send.
