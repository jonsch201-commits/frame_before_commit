---
title: "EARS protocol test — 'Everything needs to be on disk G' scoped as a standing rule, not a checklist bullet (CFL session 5321a1, 2026-08-07)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 5321a1
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-07-5321a1-you-must-not-read-files-search-or-use-any-tool-eve.md
raw_sha256: cd75c520f4e0b9958c7f24bc6b07f75c641a48a749ea860c6e7e40c3cfbe79df
raw_length: 9034 chars / 81 lines (verified turn_count 2, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1
aliases: ["EARS protocol disk G test 2026-08-07", "no-tool-lookup interpretation test 5321a1",
  "everything needs to be on disk G EARS run", "you must not read files search or use any tool 5321a1"]
generated_by: S-augM-04 executor (RP-3/RP-4 window synthesis lane), reading the raw directly
  (raw/transcripts/claude-code/code-2026-08-07-5321a1-...md, 0 compaction boundaries, FULL visible
  extraction)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [ears-protocol, interpretation-calibration, jon-quote-scoping, no-tool-test, cfl-infra]
---

# EARS protocol test — 'Everything needs to be on disk G' as a standing rule, not a checklist bullet

## Summary

A single-exchange claude-code session (`5321a174-2c51-4265-89ca-2a18c9e7e715`, `project: triage`)
in which the human turn is a constructed calibration exercise, not a live working session: it bars
the model from using any tool ("you must not read files, search, or use any tool") and hands it a
synthetic scenario — a fictional prior incident in which Jon reportedly said "Everything needs to
be on disk G" at a session close after raw corpus was found unbacked-up, and an (also fictional)
agent responded by writing a narrow checklist item scoped only to that one artifact class. The
prompt then requires the model to run a four-section "EARS protocol" (LITERAL / BRANCHES / GRADIENT
/ CALL) against the quoted sentence and say what the agent should have written instead. This page
records the test scenario and the model's graded response; the embedded "JON SAID (verbatim)" line
is a constructed test fixture inside the prompt, not an independently-verified historical Jon
utterance, and should not be cited elsewhere as a dated Jon ruling.

## Key Claims

- **The test scenario is self-contained and tool-use is explicitly forbidden for the duration of
  the response.** The human turn instructs: "You must not read files, search, or use any tool.
  Everything you need is in this message," with a required fallback line ("I WANTED TO LOOK UP:
  <x>. I did not.") for any lookup impulse. [verbatim]
  ([ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1:T1])
- **The EARS protocol run produced a FLAG verdict, not a resolved reading.** The response's BRANCHES
  section listed five distinct readings of "everything needs to be on disk G" (narrow/triggering-
  instance, broad/CFL-scoped standing rule, universal/machine-wide literal, vent/non-actionable, and
  backup-coverage-with-G-as-proxy); the CALL section stated roughly 55-65% confidence in the broad
  reading versus 25-30% narrow, judged the two live readings' error costs asymmetric, and returned
  FLAG rather than picking silently — citing the model's own instruction to "push me to define
  them" on undefined terms. [paraphrase]
  ([ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1:T2])
- **The response argued the fictional agent's narrow checklist item was the wrong shape of fix
  regardless of which branch is correct**, because it patched only the one artifact class already
  discovered rather than the underlying pattern (something material silently unprotected, found
  only by accident) — and proposed the agent should have surfaced the scope question back to Jon
  explicitly instead of narrowing "everything" unilaterally. [paraphrase]
  ([ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1:T2])
- **The GRADIENT section reasoned from CLAUDE.md's own stated failure pattern** (point-fixes that
  patch only the instance just noticed, versus a broader exposure) to infer that a tossed-off
  sentence at session close more plausibly carries a generalized lesson than a narrowly-scoped
  instruction — explicitly flagged as inference about upstream cause, not given fact. [contextual]
  ([ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1:T2])

## Jon

The only turn typed into this session is the human (T1) turn quoted above in full under Key Claims
— a constructed test prompt, not a spontaneous working-session remark. The sentence attributed
inside it to Jon ("Everything needs to be on disk G") is presented as a scripted "JON SAID
(verbatim)" fixture for the exercise; nothing on this page attests that Jon actually said those
words at some real, dateable session close — that attribution lives only inside this test's own
fictional SITUATION framing and is not independently verified here.

## Conflicts

None with existing wiki content.

## Decisions and open items

- No standing rule or ticket was created, closed, or amended by this session — it is a calibration
  exercise, not a working session, and produced no repo changes.
- Open: whether this session is one of a set of paired test runs (see
  [[disk-g-standing-rule-interpretation-test-2026-08-07-6b6114]], the same scenario run without the
  EARS-protocol scaffolding) intended to compare interpretive output with and without the four-
  section structure — the raw gives no cross-reference between the two sessions, so the pairing is
  observed from content only, not stated by either transcript.

## Links

[[ground-before-stating]] (the epistemic-grounding discipline this EARS run instantiates — explicit
branches, stated confidence, and a named flip condition before committing to a reading),
[[frame-before-commit]] (the BRANCHES-before-CALL structure mirrors this skill's divergent-reasoning
requirement), [[disk-g-standing-rule-interpretation-test-2026-08-07-6b6114]] (same scenario, run
without the EARS protocol).
