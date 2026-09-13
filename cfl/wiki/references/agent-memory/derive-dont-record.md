---
title: Derive, don't record — CFL's characteristic failure
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_derive-dont-record.md
as_of: 2026-07-26 (memory `modified` timestamp)
fidelity: [verbatim] for quoted spans
tags: [derive-dont-record, ratchet-drift, stale-spec, memory-drain, T-02]
generated_by: wiki-master pilot drain pass, T-02, 2026-08-06
retrieval_key: derive-dont-record
aliases: [record vs derive, stale-fact drift, uncheckable spec]
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page (T-02 pilot batch) — an operational/process record
  from the CC memory store, not a corpus-derived claim about a conversation. Exempted per
  wiki/references/agent-memory/README.md admission criterion; field added retroactively 2026-08-06
  when the exclusion-class prerequisite the pilot named as unbuilt was built."
---

# Derive, don't record — CFL's characteristic failure

## The finding

A fact about the system, written down once in prose, diverges from reality with nothing able to
notice. On **2026-07-25 this exact shape appeared nine times in one session**, in unrelated
subsystems:

1. `cleanupPeriodDays` — an unknown 30-day default deleted 29 CC sessions; no control existed.
2. The 2026-05-29 archive task — built correctly 14 minutes after Jon asked, shipped with an
   **annual** cadence against a 30-day clock, and **never registered**.
3. Stage-1 nightly lane — Jon approved it twice; **never registered**, and its ledger's only row is
   an `ERROR`. Leg 2 has never once succeeded.
4. The **183**-page count — ratified, then sat in a live ledger header for 12 days while the truth
   grew to 218 (+19%).
5. Model basis — every fleet agent uses the `opus` **alias**; a Claude Code point release
   (v2.1.219) silently moved the verifier tier 4.8 → 5. The record still said 4.8. A changing
   measurement basis with no basis disclosure.
6. The subagent glob — `extract_claude_code_sessions.py` globbed top-level only; subagents were
   "deferred to a threshold" **nobody built**. 305 files, 43.8% of all CC bytes, never extracted.
7. `lane-nightly-corpus-delta.md:90` — code changed; the spec kept vouching for the old guarantee.
8. **E3's certainty-inflation lint** — specified in `source-page-standard-v4.md:46-50`, **zero
   implementation**. It is the check that would catch the live T10-vs-T11 defect.
9. `raw-file-standards.md` v2.0 — specified a naming convention **for a pipeline that never
   existed**.

**And the inverse, same disease:** `RATIO_FLOOR = 0.20` fires on 100% of primary sessions because
primary JSONLs carry multi-KB encrypted `signature` blobs no markdown render can match. On
2026-07-13 it was written off as producing "13 false REFRESH flags of 16." It was detecting real
truncation. **An alarm calibrated so it always fires is not an alarm** — Jon's own T1: a marker that
doesn't discriminate is worthless.

**2026-07-26 added five more, same shape:**

10. Stage-1 nightly, third strike — the Windows scheduler had **no task registered at all**.
    Approved twice, built twice, registered zero times.
11. The canonical publish script's own safety gate checked that the deny list was *applied*, never
    that the allow was *bounded*. A probe tree with `wiki/family/probe.md` **published the file and
    reported PASS**. Fixed to fail closed.
12. Two docs still described the pre-2026-07-25 canonical scope a day after the code changed —
    `CLAUDE.md:148` and `repo-hygiene.md:17`, vouching for a scope the code no longer had.
13. The cold-open skill's reading list named 8 files; 6 did not exist — renamed long before, and
    nothing noticed.
14. Jon's own turn-8 dispatch sat untracked, so it never reached `canonical` — the wayfinder could
    not read back the dispatch it had just written.

**And the calibration lesson fired three times in one day, always the same way:** M3's first
trigger flagged **524 of 1048** anchors; the canonical gate's first sabotage test **reported PASS**
(a bad test, not a good gate — it read `main`, not the probe commit); the index-count detector's
first run reported **3 phantom rows that were not phantoms** (cross-trunk references claimed for the
wrong trunk). **A detector's first output is not evidence.** Exercise it against a known positive
and a known negative before believing either.

## Why

These are not nine coincidences. A fact recorded in prose has no mechanism that can notice when
reality moves. Deferral to a future document ("per the wiki-master threshold") is not deferral — it
is silent loss with a citation.

## How to apply

Where a fact can be re-derived from ground truth, **never store it in prose** — Jon reached this
himself in his Q3 done-definition (*"re-derived by two agreeing enumerations at every SU, never
cached"*). Where it genuinely cannot be derived, store it **with the command that checks it**.
Before accepting any spec as implemented, grep for the implementation. Before trusting any
detector, check whether its threshold is achievable.

## Related

Not-yet-drained sibling memories named in the source: `flagged-unknowns-are-work`,
`verify-controls-before-declaring-loss`, `unshipped-fix-updates-its-own-docs`,
`md-not-uncaptured-authoritative-disposition` — of these, [[flagged-unknowns-are-work]] and
[[verify-controls-before-declaring-loss]] are drained in this same batch; the other two are not.
`unshipped-fix-updates-its-own-docs`'s underlying incident is separately covered in
`sources/infrastructure/corpus-loss-audit-2026-07-19.md`, already in the wiki (not moved by this
pass — flagged so it is not mistaken for a gap).
