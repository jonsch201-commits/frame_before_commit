---
format: cfl-page/v1
kind: pattern
slug: delivery-channel-is-not-authorship
title: "Delivery Channel Is Not Authorship"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "type queued_command commandMode authoritative attachment.type says how a message was delivered not who sent it 709 vs 236 machine talking to itself"
aliases: [type-vs-commandmode, channel-mistaken-for-author, machine-talking-to-itself]
generated_by: lane W-1b (sonnet) session e515d858
state: current
state_note: "two independent instances the same day, on the same underlying data (Jon's mid-turn queued messages): S27's reconciliation of a 709-vs-236 headline gap, and Personal's own retraction of its S1 report after finding the same defect in its own first pass."
probe_sealed: "Was Secretary's original 709-arrival figure (later corrected to 263) built by reading attachment.type alone, or by also reading commandMode? => attachment.type alone: the ticket states first-hand 'the original 709 was 28.7% machine (never read commandMode)'; the corrected figure (263, verified independently against jon-arrivals-canonical.jsonl's own command_mode distribution: typed-turn 1099 / task-notification 451 / prompt 263) required reading a field that was present on 100% of rows all along. TRUSTED"
---

## Struggle

A message's delivery mechanism (which JSONL `type`/`attachment.type` carries it, which queue it
arrived through) is treated as evidence of who authored it, when the record also carries a
separate field that says the actual sender -- and that field goes unread because the delivery
mechanism alone already produces a plausible-looking count.

- `wiki/intake-triage/S27-queued-command-render-and-diff-2026-09-02.md:185` [verbatim] (cropped)
  -- "Secretary's 709 conflated delivery-channel with authorship ... `type=attachment/queued_command`
  was treated as 'Jon's words' with no `commandMode` read at all. Corrected CFL figure is 263
  Jon-typed against the same scope Secretary was counting ... a 446-row drop, all reclassified as
  `task-notification` (the harness talking to itself: background-task completions, etc.), never
  rendered as human." `wiki/intake-triage/S27-queued-command-render-and-diff-2026-09-02.md:106`
  [verbatim] (cropped), same file's "honest filter" section: "`commandMode` is read directly off
  the JSONL attachment record and says *who sent it*; it is present on 100% of `queued_command`
  rows in both instruments' source data."
- `N:\claude-gists-private\REPORT-2026-09-02-personal-S1-queued-ingest-and-schema-audit.md:92-94`
  [verbatim] -- "The defect is the one I convict others of: I read a CHANNEL and reported it as
  an AUTHOR. `attachment.type: queued_command` says how a message was delivered. It says nothing
  about who sent it, and `commandMode` -- the field that does -- was sitting in every row I
  parsed. 1,168 of 1,168 rows carry it. I never looked." Measured impact, same report: 631 of
  1,022 raw arrivals (81% of the byte mass) were `task-notification`, and a second, unnamed
  filter (`origin.kind: peer`, 101 more arrivals) was also missed on the first pass.

## Generalization

A record format that carries both a structural/mechanical field (how did this arrive: which
message type, which attachment kind, which queue) and a semantic field (who actually produced
it: `commandMode`, `origin.kind`, an author id) invites exactly this substitution, because the
mechanical field is usually easier to filter on and produces a number that looks complete. The
failure is not that the mechanical field is wrong -- it correctly says the message arrived as a
`queued_command` -- it is that a reader stops there and reports the mechanical count as if it
answered the semantic question. Two independent instances the same day, on the same underlying
corpus, both self-corrected within hours: Secretary's ticket states the correction first-hand,
and Personal's own report is a live example of catching the identical substitution in its own
first draft and retracting the overstated number rather than shipping it. The general test this
pattern licenses: before reporting a count as "authored by X," name the specific field that
distinguishes X's authorship from the delivery mechanism, and confirm that field was actually
read, not merely present in the schema. Related: [[name-matched-as-location]] (the same family
of failure at the level of a string: a name or a type tag is trusted to mean more than it does).

## Counter-evidence

none found, searched: `wiki/intake-triage/GT1-skill-ground-truth-2026-09-02.md` and
`wiki/intake-triage/C1-census-2026-09-02.md` for an instance in the bounded set where a delivery
mechanism was correctly distinguished from authorship on a first pass without a later
correction; S27's own `mint_window.py` v1.1 fix (classifying `commandMode` as authoritative,
falling back to a prefix heuristic only when it is absent) is the durable counter-design, but it
was built as the FIX for this exact class within the same lane, not a prior clean instance.

## Motivates

none yet -- `scripts/audit/mint_window.py` v1.1 implements `commandMode`-first classification as
code, but no `skills/` entry states "a delivery-mechanism field must not be read as an
authorship field without checking whether the record also carries a distinct authorship field"
as a general convention for future record-format work.

## Probe

Sealed question above. Falsified if Secretary's original 709 figure is shown to have already
filtered on `commandMode`, or if Personal's S1 report's retracted 1,017-arrival figure is shown
to have correctly excluded `task-notification` rows on its first pass.
