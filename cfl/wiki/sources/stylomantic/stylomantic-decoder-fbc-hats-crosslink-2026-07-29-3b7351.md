---
probe_sealed: "Does turn_index.py confirm the 4-human-turn count S-pre-01 assigned this session, and is the content substantive design discussion rather than a stub? => Confirmed: turn_index.py verifies 8 total turns / 4 Human (T1@line16, T3@line61, T5@line81, T7@line103), and the content is a real three-part design discussion (stylomantic decoder shape, FBC-vs-Hats cross-reference, a Mirror-skill proposal), matching S-pre-01's own characterization. TRUSTED"
title: "Stylomantic decoder for metaphorical text — worth it eventually but not as three AIs, plus FBC/Hats cross-reference and a Mirror-skill proposal (2026-07-29, 3b7351)"
trunk: fl
branch: [stylomantic]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-STYLO; sub: branch `stylomantic` has no registered sub-branches"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-07-29-3b7351-stylomantic-decoder-for-metaphorical-text-analysis.md
source_file_status: OK
source_kind: session
date: 2026-07-29
date_ingested: 2026-09-02
type: session
retrieval_key: stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351
aliases:
  - "stylomantic decoder for metaphorical text analysis"
  - "propose-then-verify not three AIs"
  - "the blind third AI as a measurement instrument"
  - "should FBC link to de Bono hats"
  - "what question might Jon ask here mirror skill"
raw_sha256: 7a5a69f9ca4a842212b750747ab82c3648ada096a1fbdfab3322b02398980928
raw_length: 12692 chars / 148 lines
generated_by: S-RECLASS executor (week-2026-09-02 corpus lane), reclassifying a session S-pre-01
  flagged STUB-by-turn-count (4 human turns, below the 5-turn PAGE bar) but real multi-part dialogue
uncaptured_assessed: populated
audit_state: unaudited
maintained_by: coordinator (deposit); wiki-master ingests
tags: [stylomantic, metaphor-decoding, fbc, de-bono-hats, wiki-master, mirror-skill, skill-improvement-loop]
---

# Stylomantic decoder for metaphorical text — worth it eventually but not as three AIs

## Summary

A four-human-turn claude.ai design session (2026-07-29) covering three linked topics. First, Jon
asks whether a "stylomantic decoder" layer — one AI flagging metaphor-load-bearing words/sections,
a second mapping them to literal slots for a target topic, a third either informed or deliberately
blind to original source/intent — is worth building; the answer is yes eventually but not as three
separate AIs, because the flag/map split doesn't actually decompose (the flagger can't know which
words are "key" without already holding a candidate mapping), while the *blind* third pass is kept
as a genuine measurement instrument for whether a metaphor's structure is intrinsic or merely
convention-shared. Second, Jon asks whether FBC (frame-before-commit) should link to de Bono's
thinking-hats, and whether Hats can already be run without a decoder layer — answered: cross-
reference yes, merge no (FBC disambiguates *readings*, Hats rotates *evaluative stances* over an
already-framed topic), and Hats needs no decoder because its lenses are literal labeled modes, not
load-bearing metaphor. Third, prompted by that answer, Jon asks the session to read the
wiki-master skill directly (rather than wait for a standard update) and report what it should do
with the FBC/Hats finding, plus whether a "what question might Jon ask here" skill would help a
fable-mirror support a coordinator; the session reads `SKILL.md` (after one retry past an echo hit
from a subagent transcript) and concludes it should not write wiki/ or skills/ directly — the
correct route is a proposal packet through `skills/intake/` carrying the FBC finding already
produced in this chat — and separately scopes the Mirror-skill idea as a pre-review challenge-
question generator that predicts questions but never predicts (or substitutes for) Jon's answers.

## Key Claims

- **Stylomantic decoder: worth it eventually, but the three-AI flag/map/blind-third-pass
  decomposition is the wrong shape for the first two stages.** The flagger cannot know which words
  are "key" without already holding a candidate mapping, so stages 1 and 2 are "one holistic
  operation wearing two hats" — splitting them buys an audit trail, not accuracy, because metaphor
  interpretation is not the kind of task (unlike retrieval or quote-verification) where independent
  stages catch each other's errors. The proposed cleaner shape is propose-then-verify: one pass
  produces the full mapping with per-slot provenance tags, a second pass checks whether the
  metaphor's entailments actually transfer to the topic. [instinct, per the raw's own inline tag]
  ([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T2])
- **The blind third AI is kept as the genuinely interesting piece — not a capability, a measurement
  instrument.** If a decoder with no source knowledge recovers the same mapping, the metaphor
  carries its structure independently; if it doesn't, the mapping is convention shared between Jon
  and instances with context. Named as being in the same family as BGIsolation / pre-registration
  robustness checks, and the one part worth keeping even if the rest of the three-AI design
  collapses to a single prompt. [paraphrase] ([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T2])
- **Where the decoder helps and where it doesn't.** Helpful: making load-bearing wiki vocabularies
  (Gems, Elements, Gift-Exile-Reunion) queryable by cold sessions without the decoder ring;
  checking whether a metaphor's implications actually hold for a new domain before relying on them;
  Jon's own compressed prompts, where enumeration-before-commit is already the working protocol.
  Less helpful: decorative metaphor (decoding adds noise), creative writing (decoding destroys the
  artifact), and one-to-many metaphors, where forcing a single slot-fill is flagged as a
  Words-Reify hazard — durably committing a mapping that should have stayed ambiguous. Verdict:
  worth a small skill eventually (propose/verify plus optional blind-decode ablation), but
  queue-worthy rather than now-worthy given August-1 sequencing; offered as a HELD item.
  [paraphrase] ([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T2])
- **FBC should cross-reference de Bono's Hats, not merge with it.** FBC enumerates orthogonal
  *readings of intent* before commitment (a disambiguation move); Hats rotates *evaluative stances*
  (facts, risk, benefit, feeling, generativity, process) over a topic that is already framed (an
  assessment move). Folding Hats into FBC would blur FBC's own trigger — "you'd start getting six
  evaluations of one unexamined reading, which is precisely the failure FBC exists to prevent." The
  proposed durable change is a one-line pointer in the FBC skill: after branch selection, if the
  decision is evaluative rather than interpretive, consider a Hats rotation. [paraphrase, one
  embedded verbatim clause] ([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T4])
- **Hats can already run without Stylomantic — there is nothing to decode.** De Bono's hats are
  literal labeled modes, not load-bearing metaphor in the Stylomantic sense, so no decoder layer is
  needed; it's a prompting convention any instance can run on request or self-invoke when a
  decision looks evaluation-shaped and material. One restraint noted alongside it: self-invoking
  Hats on every decision would itself violate a restraint-over-completeness principle — six lenses
  on a routine question is over-delivery, so it should be held for genuinely contested evaluative
  decisions or Jon's explicit call. [paraphrase] ([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T4])
- **On reading wiki-master's SKILL.md directly rather than waiting for a standard update: the
  answer is narrower than "I can read it, so I can act."** The skill's Role Boundary makes
  wiki-master the *only* writer to `wiki/` (the commit is part of the write), so a Drive-side edit
  from this session would be exactly the "another agent has written there in error" case the skill
  itself says to flag — same logic for skill files, which route through `skills/intake/` for
  skills-master review. The route that does exist: draft a proposal packet with the FBC finding
  already embedded (the interpretive/evaluative split, the trigger-blur risk), and on Jon's
  instruction, deposit it to the intake-triage Drive folder **by canonical ID, not by search**
  (naming the echo hazard a mis-targeted search had already produced once this same turn) with
  `disableConversionToGoogleType`. [paraphrase] ([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T6])
- **A self-correction surfaced by reading the skill: the session's own carried memory of the
  tracker was stale.** The wiki-master index showed tracker reconciliation through PR #89
  (2026-07-24), coordinator-ADOPTED and in BUILD→DEPLOY, so the session's prior sense of stale
  surfaces ending at an earlier PR wave was itself out of date — flagged inline as `[grounded on
  index snippet; I haven't read tracker/open-items.md this session]` rather than asserted as
  checked. [paraphrase] ([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T6])
- **The "what question might Jon ask here" Mirror-skill proposal: helpful in one specific shape
  only, with two hard constraints.** Value framed as a pre-review filter at coordinator commit
  points — before closing a decision, the Mirror generates the challenge questions Jon would
  predictably ask (provenance? write-gate honored? silence treated as approval? reversible? scope
  creep?), each labeled `[TRANSCRIPT:date]` where the corpus attests the question class or
  `[MIRROR-INFERENCE]` where it doesn't — framed as acceptance sampling moved upstream of the gate.
  Constraint 1: it predicts questions, never answers — a predicted answer is silence-as-approval by
  proxy, and anything the coordinator can't satisfy goes to a triage file, not to the Mirror's
  guess. Constraint 2: Goodhart watch — if the coordinator optimizes to pass predicted-Jon, the
  question set becomes the target, mitigated because predicted questions can only add work before
  the gate, never close it. Cheapest viable version offered: a static "Jon's standing questions"
  checklist derived once from the corpus and refreshed at standard-update time.
  [paraphrase] ([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T6])

## Jon

`[verbatim]` — Jon's four turns this session, typed as given, typos and disfluencies uncorrected:

> "Hmm. Stylomantic decoder layer for use in texts with metaphorical but not literal relevence. Worthwhile to implement eventuly? Easy enogu to have one AI flag the key words and sections, and have other AI do the work to identify, for a given topic, what words to slot into symbolic place? Third Ai, it knows what original source was and intent of metaphore, or no. Where helpful? Where less helpful? Why?"

([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T1])

> "Should link to de Bono thinking hat in FBC situations? Can do that already as is without stylomantic when material and relevent?"

([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T3])

> "Interesting. It is true you could read the wiki master skill. We don't have to wait for standard updates. I should consider how you can make good updates like this. Read the skill. Let me know what you should do, particularly given the context of the g drives current state and the state of our backlog of PRs."

([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T5])

> "Retry. Oh also related sorry... After. What would a 'what question might Jon ask here' skill be materially helpful to a Fabel mirror helping a coordinator?"

([stylomantic-decoder-fbc-hats-crosslink-2026-07-29-3b7351:T7])

## Decisions and open items

- **Stylomantic decoder** — not built this session; verdict recorded as "worth a small skill
  eventually," offered as a HELD item pending Jon's word, not actioned.
- **FBC↔Hats cross-reference** — the substance (one-line pointer, evaluative-vs-interpretive
  split) was produced this chat but explicitly NOT written to `wiki/`/`skills/` in-session; the
  session names the correct route (a proposal packet through `skills/intake/`) and states it will
  deposit on Jon's instruction to "write it" — no confirmation that the deposit itself happened is
  present in this raw.
- **"What question might Jon ask here" Mirror-skill** — scoped with two hard constraints
  (predicts-questions-never-answers; Goodhart watch) and offered as packet-shaped if Jon wants it
  durable; not built or deposited in this raw.
- Both proposals close on the same open question to Jon, unresolved in this raw: "Say the word and
  which."

## Conflicts

None with existing wiki content located in this pass. The de Bono Hats framing predates and is
consistent with any later FBC-skill text that may already carry the cross-reference; this page
does not check whether that one-line pointer was subsequently landed in `skills/frame-before-
commit`.

## Uncaptured content

- The first attempt to read wiki-master's `SKILL.md` (T5's assistant turn) returned an echo hit —
  a subagent transcript merely mentioning the role — before a refined query found the real file;
  the echo hit's content is not captured here, only named as "the worktree-duplication problem
  demonstrating itself."
- Eight extended-thinking blocks are preserved in the raw per its own extraction note and are not
  transcribed into this page's Key Claims; only visible assistant prose is summarized.
- Whether the FBC/Hats proposal packet or the Mirror-skill packet was actually deposited to
  `skills/intake/` after this session is not resolvable from this raw alone and is not asserted
  here either way.

## Links

- [[probe-registry]] — the seal-before-run discipline this page's `probe_sealed:` field follows.
- [[frame-before-commit]] — the FBC skill this session's central design question (cross-reference
  to de Bono Hats) is about.
