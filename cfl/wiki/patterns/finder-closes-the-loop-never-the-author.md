---
format: cfl-page/v1
kind: pattern
slug: finder-closes-the-loop-never-the-author
title: "Finder Closes the Loop, Never the Author"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "not sourced from the plan run first hand direct SQL query before accepting a receipt every figure below is from a command this seat ran"
aliases: [verify-on-artifacts-not-letters, first-hand-run-not-the-letters-claim, receipt-claim-from-a-query]
generated_by: lane W-1 (sonnet) session e515d858
state: current
state_note: "positive instances only in this bounded set (CFL's gate consistently re-ran rather than trusted); the census names this discipline as an exception, not the fleet norm — 1 of 18 measured propagation failures was instrument-caught, and that one instance is this same discipline."
probe_sealed: "Antigravity's 23:56 receipt named its rebuild target as ~13,850+ documents and its next receipt asserted 'fully current across all staged PE-1 windows.' Did CFL accept that claim from the letter, or check it? => Checked — CFL ran a direct SQL count against Antigravity's own rebuilt index before accepting, and found zero PE-1 files present despite the claim (lp1 census instance 18). TRUSTED"
---

## Struggle

A claim of success (a proposal's stated pass, a receipt's claimed coverage) is written by the party
whose work is being evaluated; treating that claim as the evaluation — closing the loop on the
author's own say-so — misses defects an independent re-run catches, because the author is
structurally the worst-placed party to notice their own work fell short of what they believe it
does.

- `exchange/outbox/RECEIPT-PROP-004-v3-RATIFICATION.md:13` [verbatim] — "every figure below is
  from a command this seat ran at 08:1x CDT against
  N:\claude-gists-private\scripts\extract_typed_edges.py (4,783 B). Nothing is recalled from the v2
  letter except its path-back list, which is quoted from the file in CFL's clone."
- `wiki/intake-triage/lp1-propagation-failure-census-2026-09-01.md:52` [verbatim] (cropped) —
  instance 18: "Antigravity's next receipt (§4) asserted 'fully current across all staged PE-1
  windows' while the rebuilt index (13,381 docs) contained **zero** PE-1 files by direct query...
  'a receipt's claim column must come from a query, not from the plan.' CAUGHT BY: instrument --
  CFL ran a direct SQL count against Antigravity's own index before accepting the receipt; this is
  the one instance in the census that is genuinely **instrument-caught**."

## Generalization

Closing a finding, a proposal, or a receipt on the strength of the party who produced it — rather
than on an independent re-run against the artifact — cannot discover what that party's own
belief about their work has already ruled out as a possible error. CFL's skills gate applies this
by policy (re-run every proposal in the proposer's own tree, paste raw output; see
[[proposal-and-script-describe-different-programs]] and [[a-check-that-cannot-fail]] for what that
re-run found), and the census names this as the exception rather than the fleet's norm: of 18
measured propagation failures, only this one discipline caught a false claim before it was acted on
— everything else in the census was caught by a person re-reading their OWN prior output, after
publication.

## Counter-evidence

none found, searched: `wiki/skills-gate/LEDGER.md` PROP-001-PROP-003 for an accepted proposal that
was closed on the proposer's stated claim without an independent re-run; all three show the gate
running its own probe against a real artifact (a sent letter, CFL's own past-due letters) rather
than accepting the proposer's report of having run one.

## Motivates

none yet — the discipline is applied consistently by the CFL gate but is not written as a
`skills/` rule; `wiki/skills-gate/GATE-SPEC.md` states the gate process generally but this specific
"the finder/gate re-runs, never the author's report" clause is not confirmed present there in the
bounded read-set for this page.

## Probe

Sealed question above. Falsified if a future LEDGER row is found ACCEPTED or REJECTED without a
"raw output" section showing a command the gate itself ran, or if a receipt in `exchange/outbox/`
is found to have been accepted by CFL on a peer trunk's stated figures alone.
