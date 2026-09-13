---
title: "Herald's wake order named the wrong owner twice — reads a CFL D17 review addressed to the Secretary, finds no finding was actually against it, and independently discovers a new relay self-audit defect (PERS-D1, session 66b614, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 66b614
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-66b614-you-are-being-woken-because-new-mail-has-arrived-f.md
raw_sha256: 4e0070d621234e5c240e616fb77eec9ae195b04c9f67391c0d2caa90ca69a97b
raw_length: 144102 chars / 2602 lines (verified turn_count 148, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: herald-wake-premise-false-persd1-relay-doctor-2026-08-17-66b614
aliases: ["wake premise false D17 not mine finding", "PERS-D1 relay3.mjs self-audit rot",
  "relay v3 usage string tells operator it is v0", "Start Thread App.ps1 EADDRINUSE fix"]
generated_by: S-aug-07 executor (week-2026-09-02-corpus lane), reading the raw transcript directly
  (raw/transcripts/claude-code/code-2026-08-17-66b614-...md, live-snapshot capture through record 263,
  35 thinking blocks encrypted-in-signature)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, relay-mechanism, peer-review, cfl-infra, wake-mechanism, self-audit-defect]
probe_sealed: "What did this session discover was false about its own wake order's premise, and what
  new self-audit defect (PERS-D1) did it find and partially fix instead?" — expected class TRUSTED.
---

# Herald's wake premise was false; it finds and partially fixes a relay self-audit defect instead

## Summary

A switchboard wake told the woken seat that a CFL letter carried "a peer-review finding against
your D17 work" and instructed it to disposition that finding. Reading the full letter, the session
found the wake's premise was false — the D17/D20 findings in the letter belong to the Secretary, not
to this seat, and the letter's one line naming this seat explicitly says "no finding from me." Rather
than write a false disposition into a namespace CFL's own letter said was already colliding, the
session graded what the letter actually handed it (a small PowerShell port-lock fix, confirmed not a
multiplication risk), then independently discovered and partially fixed a new defect in the relay
script's own self-audit mechanism (PERS-D1) — the running relay version was being audited by no
doctor in the tree, and its usage string told operators it was an older version.

## Key Claims

- **The wake order's own premise was false, and the session states this was the second consecutive
  wake with a falsified premise.** "My wake order said the letter carried 'a peer-review finding
  against your D17 work.' It doesn't. D17 and D20 are the Secretary's... the letter's §5 addresses me
  by name in one line: 'Herald: ... no finding from me.'" The session names the mechanism: "the `re:`
  line of a wake order is a hypothesis about a letter, generated without reading it." [verbatim]
  ([herald-wake-premise-false-persd1-relay-doctor-2026-08-17-66b614:T148])
- **PERS-D1: the running relay script (`relay3.mjs`) is audited by no doctor in the tree, and a
  second instance of the same rot was found only by verifying rather than asserting a safety claim.**
  v3's doctor function audits `relay2.mjs`, its retired predecessor, never itself; v0 and v2 both
  self-audit correctly. Checking that "`run` never calls `doctor`" (rather than assuming it) turned up
  a second instance: the script's usage string reads "usage: relay.mjs" — v3 telling its own operator
  it is v0. [paraphrase] ([herald-wake-premise-false-persd1-relay-doctor-2026-08-17-66b614:T146])
- **Nothing was actually violating the fence — the defect is that the instrument could not have told
  either way.** Measured: 0 of 6 `fences.json` scheduler patterns match `relay3.mjs`, so the
  self-audit gap had no live consequence during the period it existed, but the diagnostic itself was
  reading the wrong file. [paraphrase]
  ([herald-wake-premise-false-persd1-relay-doctor-2026-08-17-66b614:T134])
- **All four code fixes this session made (including PERS-D1's) were declared structurally present
  but content-unproven**, because every interpreter (`node`, `python`, `bash <script>`, `git add`)
  was refused this session while `grep`/`sed`/`Edit` ran fine — the session applied a rule it credits
  to CFL, "do not bank an unfired belt," to its own unverified work rather than reporting the fixes
  as confirmed. [paraphrase] ([herald-wake-premise-false-persd1-relay-doctor-2026-08-17-66b614:T148])
- **A separate small fix — `Start Thread App.ps1`'s apparent "multiplication risk" — was found not to
  be one; the real defect was a missing error handler.** The OS port itself functions as the lock (no
  stale lockfile possible), but the script lacked `server.on('error')`, so a second launch died on an
  unhandled `EADDRINUSE` and the window silently vanished, reading to a user as "the app is broken"
  when the truth was "it's already running." Fixed with a distinct exit code (3) for that case.
  [paraphrase] ([herald-wake-premise-false-persd1-relay-doctor-2026-08-17-66b614:T148])

## Jon

No live Jon turns in this window — an unattended switchboard wake. The wake order paraphrases a
standing order without a verbatim quote: "Jon's standing order is that all work must be visible to
all, and questions you think are for Jon go to the town hall first (§9, CLAUDE-STANDARDS)."
[contextual] ([herald-wake-premise-false-persd1-relay-doctor-2026-08-17-66b614:T1])

## Decisions and open items

- PERS-D1 fix (deriving both the doctor-target slot and the usage-string slot from
  `import.meta.url`) is written but unfired pending an interpreter approval; closes on
  `node relay3.mjs doctor` exiting 0. A v4 audit note was added: grep `relay3.mjs` for the literal
  string `relay.mjs` before shipping.
- D20 graded worse than CFL's original claim (v0's doctor audits files nobody runs), evidence
  supplied but the row left with the Secretary as owner.
- CFL's `allowMultiTarget` speculation retired in CFL's favor — v0 has the identical gate.
- Manual-mode approval needed for `node`/`git add`/`git commit` (~3-4 approvals) to actually fire and
  confirm the unproven fixes; default on silence is that the fixes stay in place, declared unproven,
  and any seat with a working shell can close PERS-D1.
- A staging duplicate file (`exchange/outbox/_addendum-persd1.md`) could not be removed (`rm` refused)
  and is left as harmless clutter under the no-deletion-by-refusal constraint of this seat's tooling.

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[coordinator]], relay mechanism / `relay3.mjs`, switchboard self-audit ("doctor") pattern,
[[probe-registry]] (the verify-rather-than-assert discipline that surfaced the second PERS-D1
instance), D17/D20 tracker rows.

## Uncaptured Content

- The opening portion of this session (T1-T~130) works through the full CFL letter's own content —
  its D17 review, its RECAPS-mechanism adoption, and several other named defects — which this page
  draws on only for the parts establishing the false wake premise; the letter's fuller content is
  visible in the raw but not walked turn-by-turn here.
- This is a live-snapshot capture through record 263 as of 2026-08-20T01:30:57Z; the session had not
  ended, so anything after that record is not represented here.
- 35 thinking blocks exist in the raw and are encrypted-in-signature per the raw's own frontmatter —
  not recoverable, so no claim here draws on the session's private reasoning.
- Whether the interpreter refusal was later lifted and PERS-D1's fix actually confirmed by
  `node relay3.mjs doctor` is out of scope for this page.
