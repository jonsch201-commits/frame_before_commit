---
title: Confidence-Disclosure Epistemology — C1 Grounding (Jon grilling, 2026-07-13)
trunk: fl
branch: [cfl]
sub_branch: [skills]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (skills); sub: skills 2 vs wiki 1 on authored labels"
source_kind: analysis
source_file: none
source_file_status: live-session capture (da51cc grilling turn, 2026-07-13); supersede on JSONL extraction
generated_by: claude-opus-4-8/wiki-master (CC session da51cc)
retrieval_key: c1-confidence-disclosure-grounding
aliases:
  - "how the wiki should wear its confidence (ASOP-grounded)"
  - "materiality test — when does a claim get a confidence marker"
  - "thin sources are real data; don't dismiss 'just complaining'"
  - "wiki as ASOP-56 disclosure to my future self"
uncaptured_assessed: populated
audit_state: linted
---

# Confidence-Disclosure Epistemology — C1 Grounding

**Thesis.** C1 (truth-confidence) is not a generic "how sure" tag — it is *disclosure-under-uncertainty*
grounded in Jon's actual ASOP practice, captured here from the 2026-07-13 grilling in his words. C1 stays
ASOP-gated pending the full Tier-1 ingest; this is its starting spine. Jon's words are quoted; my
derivations are tagged `[inferred]`. (Words-reify: I must not reify my reading of his epistemology as its
canon.)

**Grounding status (updated 2026-07-13, overnight sweep).** C1 now rests on *two* grounding sources — the
da51cc grilling (below) and the re-extracted [[asops-ingestion-planning-2026-06-27-a6314b]] design session
(the seven translated ASOP-1 principles Jon confirmed at T52). **C1 remains PROVISIONAL / ASOP-gated.** The
a6314b grounding is Claude's *paraphrase and translation* of ASOP 1 (the PDF was robots-blocked and the
fetched page's text is not preserved in the raw — tagged `[reconstructed]`), and it covers only **ASOP 1**;
the substantive text of ASOP 23, 41, and 56 is *not in the corpus at all* (metadata-only). Promotion out of
PROVISIONAL still requires the actual Tier-1 ASOP text + the T-85 modal spec (the T-77 sourcing dependency).
Grounding the confidence axis on ASOP *paraphrase* would be the exact reification defect the program guards
against — so it is deliberately not done here.

## Jon's disclosure logic (quoted, da51cc 2026-07-13)

- **First stakeholder = self.** "I consider myself to be the first stakeholder. I need to judge my beliefs
  regardless of how my words might reasonably be interpreted." External expectations "matter materially,"
  but "if I cannot explain out loud to myself the magnitude of the uncertainty, the stakes of the decision
  relying on it, then I cannot yet consider the reader's sophistication." [verbatim]
- **Materiality test.** "If [the uncertainty magnitude or decision stakes] are such that I might reasonably
  come to meaningfully distinct conclusions, then I should consider what else I should consider in my
  review." [verbatim]
- **Negative-space disclosure.** "If I cannot explain to myself why what I have not considered is not
  material in this context, then I should consider if I must explain this limitation to the stakeholder."
  Then: anticipate their reply; consider framing — "Frames help as they can allow us to better exercise
  our human judgement IFF we understand." [verbatim]
- **Thin/unverifiable sources (ASOP 23).** "It depends on materiality." Consider whether a verifiable
  source would change the conclusion; if thin, enumerate "a reasonable list of conclusions you may have
  come to instead." **"Thin/unverifiable source... actually are real data. I have made errors on this in
  the past... I have not trusted people who I have viewed as 'just complaining' because I did not have
  their lived experience to understand."** Consider disclosure; consider quantifying uncertainty "but you
  should consider how well grounded that quantification is"; consider just asking the principal (they may
  view it as immaterial). Balance: don't "spin your wheels," but ensure "the support your user expects."
  [verbatim / near-verbatim]
- **Modal language (T-85).** "Most people do not use these words like ASOP 1." Casual ≠ grounded usage.
  "I know that I do not always use these terms consistently." A 5th term is open — "we do not exclusively
  use ASOP language, and we have structured FBC and GBS to push beyond the ASOPs." [verbatim]
- **AI-reliance (ASOP 56).** Depends on whether reliance is stated. Jon has not stated reliance on AI for
  actuarial judgement; "but if I did, I would want to be able to fully trace it back to material ground
  truth when asked. Words reify." And the turn-back: "When you rely on your output, what must you
  understand and disclose about it to your future self?" [verbatim]

## Derived C1 design rules `[inferred]`

1. **C1 trigger = materiality, not ubiquity** `[inferred]`. A claim carries a confidence marker *only*
   when its uncertainty (magnitude × stakes-of-reliance) could yield a meaningfully distinct conclusion.
   This is the filter against tag-noise Jon flagged.
2. **The reader is first the future self** `[inferred]`. The wiki is the agent's ASOP-56 disclosure to its
   own cold-session future self (Jon's turn-back). Self-honesty (traceability + fidelity + marked instinct)
   precedes reader-framing.
3. **Uncaptured-content (E4) is ASOP-grounded disclosure** `[inferred]`. "Can't show the unconsidered is
   immaterial → disclose it" *is* the negative-citation rule. E4 gets teeth: not "was an assessment done"
   but "can we show the gap is immaterial; if not, it must appear."
4. **Thin-source protocol** `[inferred]`: thin/experiential/anecdotal = real data. Do NOT dismiss (Jon's
   documented "just complaining" error — hold against constitution). Instead: enumerate the alternative
   conclusions it permits; disclose reliance; ask the principal on genuine materiality doubt; avoid
   false-precision quantification; materiality-gate the depth so we neither spin wheels nor under-support.
5. **Modal humility** `[inferred]`: do not convert Jon's *should/must/will* into ASOP-precise force; read
   from context. A CFL 5th modal term may be coined (FBC/GBS space).
6. **AI-reliance = on-demand full traceability to material ground truth** `[inferred]` — i.e. the
   citability/turn-index/fixity program is the disclosure discipline, not overhead.

## a6314b grounding map (2026-07-13) `[reconstructed — ASOP-1 paraphrase, not primary text]`

The re-extracted a6314b design session independently corroborates the derived rules — the seven translated
ASOP-1 → Claude principles (a6314b:T52, Jon-confirmed) map onto the C1 rules above, which strengthens them
from single-source (`[inferred]` off the grilling) to double-source, *within the ASOP-1 paraphrase ceiling*:

| C1 rule | a6314b principle (T52) | fidelity ceiling |
|---|---|---|
| 1 C1 trigger = materiality | #3 Materiality threshold | reconstructed (paraphrase of ASOP 1) |
| 3 E4 = ASOP-grounded disclosure | #6 Deviation-with-disclosure + #3 | reconstructed |
| 4 Thin-source protocol | #4 Reasonable range + #5 Reliance-with-disclosure | reconstructed |
| 5 Modal humility | #1 Modal hierarchy + #2 "Known" at rendering | reconstructed; T-85 spec still absent |
| 6 AI-reliance = full traceability | #5 Reliance-with-disclosure + #7 non-binding-literature | reconstructed |

Also from a6314b: the **three-system labeling framework** (T36 — `[]` source / `()` confidence-currency /
*italics* modal markers) is the candidate *mechanism* for how a page wears C1, and the **"label when
material" rule** (T18: absence = confirmed *or* immaterial) is the anti-noise filter matching C1 rule 1.
These are session-native (verbatim-available), higher fidelity than the ASOP-1 paraphrase, but they are
*Claude's* apparatus, not the ASOP standard — they operationalize C1, they do not ratify it.

## Uncaptured Content
- This is a *starting* grounding from one grilling under Jon's stated capacity limit, plus the a6314b
  ASOP-1 *paraphrase* — NOT the full ASOP ingest. ASOP 41/23/1/56 **primary text** + T-85 modal spec still
  required before C1 leaves PROVISIONAL (the a6314b re-extraction confirmed the primary text is not in the
  corpus — a sourcing dependency, T-77).
- The 5th-modal-term question is open (unfollowed thread).
- Jon's "just complaining" reflection is captured as the rationale for rule 4; treated as epistemic
  self-account, not filed as personal-trunk content.

## Cross-links
Grounds [[words-reify]] (output→future-self ground truth), [[frame-before-commit]] (negative space),
[[actuarial-epistemology]] (ASOP-as-Claude-governance), and the C1 axis in [[source-page-standard-v4]].
Staleness pin: rests on the pending Tier-1 ASOP ingest ([[asops-ingestion-planning-2026-06-27-a6314b]]@partial).
