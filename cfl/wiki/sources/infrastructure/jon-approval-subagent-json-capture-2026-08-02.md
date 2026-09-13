---
title: "Jon ruling — always capture all subagent JSONs; general approval to proceed"
aliases: [always-capture-subagent-jsonls-ruling-2026-08-02, caveman-general-approval-2026-08-02]
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-SRC-INFRA; sub: fleet 5 vs wiki 3 on authored labels"
source_kind: session
retrieval_key: jon-approval-subagent-json-capture-2026-08-02
slug: jon-approval-subagent-json-capture-2026-08-02
sensitivity: T1
origin: CFL session, fable-mirror subagent, 2026-08-02, mid-turn message
date: 2026-08-02
status: open
kind: source
fidelity: verbatim
generated_by: fable-mirror subagent (CFL session, 2026-08-02), mid-turn message capture
audit_state: unaudited
maintained_by: coordinator (deposit); wiki-master ingests
tags: [fable-mirror, jon-ruling, subagent-jsonl, close-protocol]
---

# Ingest note (wiki-master, 2026-08-02 close work order, step 5)

Ingested from `wiki/intake-triage/jon-approval-subagent-json-capture-2026-08-02.md`, content unchanged
below. **Known non-conformance, flagged not silently fixed:** the original `kind: source` field is
non-conformant against v4.0's `source_kind:` vocabulary; preserved, with `source_kind: session` added
alongside at ingest.

**Quote verification against `wiki/sources/reference/jon-messages-to-mirror-2026-08-02.md` (primary
source), run during this ingest pass:** the sole quote below — *"/caveman explain your proposal. I
want to move things forward with general approval. I strongly agree we always need all subagent
jsons, and their is a good path demonstrated towards this."* — matches Message 8 of the primary
source **exactly**, character for character, including the timestamp context and all typos ("their
is"). **No discrepancy found.** This is the one deposit in the batch whose sole quote checked out
clean on first pass.

---

# Jon's words

> "/caveman explain your proposal. I want to move things forward with general approval. I strongly
> agree we always need all subagent jsons, and their is a good path demonstrated towards this."

`[verbatim]` — typos retained per R1.

# What this closes

| Item | Before | Now |
|---|---|---|
| **Capture all subagent JSONLs at every close** | Proposed (§6, close packet) | **RATIFIED** — *"I strongly agree we always need all subagent jsons"* |
| **The overall close/summary proposal** | Proposed | **GENERAL APPROVAL to proceed** |

# ⚠️ Bounds on this ratification — stated against my own interest

Personal's mirror bounded a blanket ratification against itself on 2026-08-02 and Jon endorsed that
discipline. Applying the same here:

1. **"General approval" is approval to MOVE, not text-ratification of every clause.** Personal's own
   standard `[verbatim]`: *"Plan-approval is not text-ratification; do not collapse the two."*
   **Specifically NOT ratified by this message:** the five-field seed standard (still Personal's, still
   awaiting CFL's adopt/adapt/counter), the `[MIRROR-INFERENCE]` vs `[inferred]` vocabulary conflict,
   the cohort instrument's date field, and the `attainable` computation method.
2. **What IS unambiguous:** always capture all subagent JSONs. He used *"strongly agree"* and
   *"always."*
3. **"a good path demonstrated"** refers to Personal's method — parsing `type: user` entries carrying
   the mid-turn wrapper out of `agent-<id>.jsonl`. `[inferred]` — he did not name it; it is the only
   demonstrated path in evidence.

# The obligation this creates

**Every session close, parent and subagent, both projects:** copy every JSONL in the session tree, parse
mid-turn `type: user` entries, produce a `jon-messages-*` source page.

**As a CHECKED item on the SU checklist, not a remembered one.** `[inferred]` — the phrasing is
Personal's; the enforcement point is my recommendation and is unbuilt.

# Uncaptured Content

- **No hook or lint enforces this.** It is discipline, and the standing finding is that discipline does
  not survive. `[inferred]`
- **This message itself arrived by the mid-turn mechanism** and is therefore, at time of writing, **in
  no place but my subagent JSONL and this file.** `[measured]` **A ruling about capturing rulings is
  currently subject to the defect it fixes.**
- Whether Jon intends this to bind Herald/XC as well as CFL+Personal is **unstated.** `[uncaptured]`
