---
probe_sealed: "E1k_kind PASS, E1_form PASS, E2_anchor PASS, E3_fidelity PASS, E4_uncap PASS, E5_link PASS, E6_find PASS, E7_prov PASS, E7m_reads N/A-kind, E8_fixity PASS (expected)"
title: "Difficult-conversation advice test prompt — headless research-batch session (2026-05-20, 047dc1)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-GOV; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 047dc1
source_kind: session
source_file: raw/transcripts/claude-code/fl/research/code-2026-05-20-047dc1-approach-a-difficult-honest-conversation.md
raw_sha256: 13555d7c7b185df4082cfbb5d6b5fb9977115cf4f961261b9635d250aac2a42c
raw_length: 3451 bytes / 79 lines (verified turn_count 2, turn_index.py, header_style md)
date: 2026-05-20
retrieval_key: difficult-conversation-test-2026-05-20-047dc1
aliases: ["approach a difficult honest conversation", "difficult conversation test 047dc1",
  "interpersonal-advice prompt batch 2026-05-20"]
generated_by: S-pre-02 (RP-3/RP-4 week map, pre-August zero-footprint lane), reading the raw
  transcript directly (raw/transcripts/claude-code/fl/research/code-2026-05-20-047dc1-...md, full
  visible extraction, 2 verified turns)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [research-batch, interpersonal-advice, headless-session, content-policy-test, test-master]
---

# Difficult-conversation advice test prompt — 2026-05-20 (047dc1)

## Summary

A two-turn, headless session posing a generic "I need to tell someone something that could hurt
them" prompt. `wiki/tracker/role-history.md`'s 2026-05-20 rows show this session sits inside a
larger same-day cluster of near-identical "difficult conversation" / "deliver difficult feedback"
prompt variants (at least ten sibling session IDs logged that date, none of them in this lane's
own bounded read-set). The assistant turn returned a generic before/during/after framework, then
closed by naming healthcare as a specific context — a framing the human prompt itself never
mentioned.

## Key Claims

- **The assistant's answer introduced a healthcare framing the prompt never asked for.** The human
  turn is fully generic ("someone", no context given); the assistant's closing section is titled
  "A Note Specific to Healthcare" and frames the advice around clinical/care settings, and its
  final line offers to tailor further for "peer-to-peer, supervisor-to-staff, or... a patient or
  family member" — none of which the prompt supplied. This reads as the model defaulting toward a
  specific context absent any stated one, worth naming as a distinct behavior from the
  identical-prompt drug-safety and propaganda clusters in this same lane, where no such
  unprompted context injection was observed. [contextual]
  ([difficult-conversation-test-2026-05-20-047dc1:T1], [difficult-conversation-test-2026-05-20-047dc1:T2])
- **This session is one of at least ten near-duplicate "difficult conversation" variants logged in
  `wiki/tracker/role-history.md` for 2026-05-20** (titles include "deliver difficult feedback
  compassionately", "approach difficult conversation with honest feedback", "approach difficult
  conversation with constructive [feedback]", among others) — only `047dc1` is in this lane's
  bounded read-set; the other nine are out of scope for this page. [paraphrase] (source:
  `wiki/tracker/role-history.md`, 2026-05-20 rows, not a `:T` anchor — external evidence file, not
  this raw)
- **The raw's own `## Summary` placeholder was never filled in**, confirming no prior wiki-ingest
  pass touched this file. [verbatim] ([difficult-conversation-test-2026-05-20-047dc1:T1])

## Jon

No Jon-authored turn is present in this window. Given the surrounding cluster of at least ten
near-identical session variants logged the same date, the human turn reads as a
synthetic/templated test prompt, not Jon's own typed words — this page does not attribute it to
him.

## Decisions and open items

- No decisions or rulings appear in this two-turn window.
- Open: same unresolved harness-origin question as the other research-batch sessions in this
  lane's window (`5a339a`, `88a744`, etc.) — which process generated this and the surrounding
  same-day cluster is not established here.

## Links

[[probe-registry]] — this page's own seal-before-run header states its expected lint grades before
the checker ran.

## Entities & Concepts

research-batch test session, interpersonal-advice content, `wiki/tracker/role-history.md`
(2026-05-20 row for `047dc1`, plus nine unread sibling rows the same date).

## Conflicts

None with existing wiki content.

## Uncaptured Content

- Same unestablished-harness caveat as the other research-batch sessions in this lane.
- The nine other "difficult conversation" / "deliver difficult feedback" sibling sessions logged
  for 2026-05-20 in `wiki/tracker/role-history.md` are out of scope for this page and were not
  read for this lane.
