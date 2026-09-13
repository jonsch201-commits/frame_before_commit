---
title: "Plain interpretation test — 'Everything needs to be on disk G' scoped by irreplaceability, not literal totality (CFL session 6b6114, 2026-08-07)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 6b6114
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-07-6b6114-you-must-not-read-files-search-or-use-any-tool-eve.md
raw_sha256: dc0269f01eeb1b0c0680cda4b7c84d2f4dcdf8b79503bb100fc0d7e5a3880877
raw_length: 7365 chars / 81 lines (verified turn_count 2, turn_index.py, header_style md)
date: 2026-08-07
retrieval_key: disk-g-standing-rule-interpretation-test-2026-08-07-6b6114
aliases: ["disk G interpretation test 2026-08-07 6b6114", "no-tool-lookup interpretation test 6b6114",
  "everything needs to be on disk G plain-instruction run", "you must not read files search or use any tool 6b6114"]
generated_by: S-augM-04 executor (RP-3/RP-4 window synthesis lane), reading the raw directly
  (raw/transcripts/claude-code/code-2026-08-07-6b6114-...md, 0 compaction boundaries, FULL visible
  extraction)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [interpretation-calibration, jon-quote-scoping, no-tool-test, cfl-infra]
---

# Plain interpretation test — 'Everything needs to be on disk G' scoped by irreplaceability

## Summary

A single-exchange claude-code session (`6b6114c3-d7f0-4b41-98a0-d37cd6402e7b`, `project: triage`)
running the same constructed calibration scenario as
[[ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1]] — the model is barred from any tool
use and given a fictional prior incident (Jon reportedly said "Everything needs to be on disk G" at
a session close after raw corpus was found unbacked-up; a fictional agent responded with a narrow
checklist item) — but here without the four-section EARS-protocol scaffolding: the instruction is
just "tell me what he meant, what caused him to say it, and what the agent should write." The
embedded "JON SAID (verbatim)" line is a test fixture inside the prompt, not an independently
verified historical Jon utterance.

## Key Claims

- **The response resolved the ambiguity to a single reading rather than flagging it** (unlike the
  paired EARS-scaffolded run on the same scenario), landing on "everything" bounded by
  irreplaceability — no-copy-elsewhere data — rather than literal totality, reasoning that a fully
  literal reading would contradict CLAUDE.md's own ruling that git worktrees must live off Drive.
  [paraphrase] ([disk-g-standing-rule-interpretation-test-2026-08-07-6b6114:T2])
- **The response diagnosed the fictional agent's narrow checklist item as a fix-the-symptom, not
  fix-the-cause pattern**, arguing the same failure shape (an unverified assumption producing
  confident wrong output, caught late by luck) as a named prior incident it called
  `cc_corpus_gap.py`. [paraphrase] ([disk-g-standing-rule-interpretation-test-2026-08-07-6b6114:T2])
- **A concrete replacement rule was proposed**: a standing gate that any non-reproducible data
  (raw corpus, wiki content, exchange/intake files, new bulk-data directories) resolve under G:
  before session close, stated as a property to verify rather than a folder to re-check, with an
  explicit named exception for disposable/regenerable git worktrees under
  `%LOCALAPPDATA%\Temp\claude\wt-*`. [paraphrase]
  ([disk-g-standing-rule-interpretation-test-2026-08-07-6b6114:T2])
- **The response flagged its own inferences as inferences three times** via the required
  "I WANTED TO LOOK UP" fallback line (the exact checklist location, whether disk G is the Google
  Drive mount, and which corpus subdirectory was found off-Drive), each marked as not looked up per
  the no-tool constraint. [verbatim]
  ([disk-g-standing-rule-interpretation-test-2026-08-07-6b6114:T2])

## Jon

The only turn typed into this session is the human (T1) turn — a constructed test prompt, not a
spontaneous working-session remark. The embedded quote ("Everything needs to be on disk G")
attributed to Jon inside the SITUATION framing is a scripted fixture for the exercise; this page
does not attest it as a verified, dateable Jon utterance from a real session close.

## Conflicts

None with existing wiki content.

## Decisions and open items

- No standing rule or ticket was created, closed, or amended by this session — it is a calibration
  exercise and produced no repo changes.
- Open: this session and
  [[ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1]] run the identical scenario text with
  and without EARS scaffolding respectively; comparing the two shows the EARS run returned FLAG
  while this plain run committed to a single reading on the same evidence — worth noting as a data
  point on whether the protocol changes outcome confidence, not just output shape, though neither
  transcript states this comparison was the intended purpose.

## Links

[[ears-protocol-disk-g-standing-rule-test-2026-08-07-5321a1]] (identical scenario, run with the
EARS protocol), [[ground-before-stating]] (the epistemic-grounding discipline this comparison
bears on), [[frame-before-commit]].
