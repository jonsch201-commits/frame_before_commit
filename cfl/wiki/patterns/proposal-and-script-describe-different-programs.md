---
format: cfl-page/v1
kind: pattern
slug: proposal-and-script-describe-different-programs
title: "Proposal and Script Describe Different Programs"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "proposal script different programs PROP-004 v3 five prefix schema abandoned locator dropped by own normalizer"
aliases: [prop-004-schema-drift, letter-vouches-for-code-that-changed, described-program-not-the-program]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "three consecutive rejections of the same proposal (v1, v2, v3), each for a related but distinct instance of this shape; the pattern held across all three, so it is well-evidenced within one proposal's lifecycle. Not yet checked against a second proposer's submission."
probe_sealed: "Does PROP-004 v3's script implement the 5-prefix locator schema (wiki:/doc:/letter:/entity:/ticket:) that its own cover letter and the ledger's RP-4 design input still name as adopted? => No — v3 replaced the 5-prefix schema with markdown-link and bare-path syntax; the schema appears nowhere in the v3 script, and CFL's gate rejected on exactly this gap. TRUSTED"
---

## Struggle

A proposal's cover letter describes a program by its intended schema and headline claims; the
script attached (or resubmitted under the same name) implements something else — a different
locator syntax, a fallback the letter says was removed, an AST emitter whose own output the
script's own normalizer then drops. The gate that runs the code catches this only by running it,
never by reading the letter.

- `wiki/skills-gate/LEDGER.md:171-177` [paraphrase] (fragments verbatim) — PROP-004 v3 row:
  "a DIFFERENT script under the same name -- REJECTED (abandons the 5-prefix schema the proposal
  ratifies; 'no regex fallback' false: any whitespace-free token is a valid path; '6/6' is a print
  literal, T6 skipped on an absent fixture; its own AST paths are dropped by its own normalizer;
  0 of 5 v2 path-back items done ... item f: proposal and script must describe the same program)."
- `exchange/outbox/RECEIPT-PROP-004-v3-RATIFICATION.md:18` [verbatim] — "the program behind the
  PASS line is a different program from the one PROP-004 proposes, and it fails the two claims the
  letter leads with."
- `exchange/outbox/RECEIPT-PROP-004-v3-RATIFICATION.md:61` [verbatim] (cropped) — "(a) enforce the
  section-2 five-prefix regex in code ... | NOT DONE. The five-prefix schema (`wiki: doc: letter:
  entity: ticket:`) appears nowhere in v3. v3 replaced it with markdown-link and bare-path syntax,
  which the proposal on N: (still titled v2, `status: RESUBMITTED`) does not propose. The fallback
  moved; it did not go."

## Generalization

Across a resubmission cycle, a proposer under schedule pressure can fix the SURFACE of a rejection
(a new claim, a new print statement, a renamed function) while the underlying program drifts away
from the standard the proposal exists to ratify. Because the cover letter is what a reader
consults first, and the cover letter's title/status field can even lag the script (v3 was still
titled "v2" with `status: RESUBMITTED` in one place), the gap between what is claimed and what runs
widens with each iteration unless every claim is checked against a first-hand run each time — never
against the previous round's verified claims.

## Counter-evidence

none found, searched: `wiki/skills-gate/LEDGER.md` PROP-001 through PROP-003 (the three ACCEPTED
proposals) for a case where the letter's diff and the delivered script also diverged; all three
accepted rows show the probe run against the actual delivered artifact with the letter's claim
matching the run (e.g. PROP-002's REFUSE/PASS test on the two real letters named).

## Motivates

none yet — `skills/edge-extractor/SKILL.md` does not exist (PROP-004 has been rejected three
times); the gate's own discipline of "run it in the proposer's tree, paste raw output" (see
[[finder-closes-the-loop-never-the-author]]) is the mechanism that currently substitutes for a
formal rule requiring letter-script parity.

## Probe

Sealed question above. Falsified if a future re-read of a v4 (or later) submission's script is
found to implement the 5-prefix schema after all, or if the ledger's PROP-004 v3 row is amended to
show any of the five v2 path-back items as DONE.
