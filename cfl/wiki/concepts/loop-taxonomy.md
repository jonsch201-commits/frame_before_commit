---
title: Loop Taxonomy — Foundational Layer Approved Ubiquitous Language
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (wiki); sub: wiki 3 vs skills 1 on authored labels"
type: concept
first_seen: test-master-methodology-2026-05-22
source_count: 1
last_updated: 2026-05-22
---

## What This Is

Seven named loops that govern how work flows through the Claude Foundational Layer research program. Finalized as approved ubiquitous language in the 2026-05-22 session. All [[skills-system]] updates after 2026-05-22 should use these canonical names. The loops are organized into three categories by domain: Foundational Layer (session/agent coordination), Skills Ecosystem (skill improvement and ratcheting), and Test Master (research process).

## What the Wiki Says

### Category 1 — Foundational Layer Loops

These govern how sessions and agents operate at the infrastructure level.

**Session Loop**
Governs cold session open, post-compact recovery, and session close. Owned by the session-order skill.
- Open protocol: temporal context → read MEMORY.md + relevant memory files → wiki-master query for relevant context → read active plan file → read OPEN.md → FBC trigger inventory (flag anything pre-answered before work begins)
- Post-compact recovery: confirm temporal context → read plan file → read OPEN.md → read MEMORY.md → restate current position → check for in-flight agents → proceed
- Close protocol: save memory files for non-obvious findings → log to LOG.md if research work happened → trigger Ingestion Loop for anything worth retaining

**Checkpoint Loop**
Governs background agent coordination. Used by test-master when instructing background agents (skills-master, wiki-master, harness-creator).
1. Inventory checkpoint: brief agent → agent reads all relevant files → agent posts what it found, what it proposes, what order → test-master reviews and approves → agent does NOT proceed until approved
2. Execution checkpoint: agent surfaces after first material change or unexpected finding
3. Completion checkpoint: agent summarizes what was built; test-master verifies against brief
The oversight model is: agent → test-master :: test-master → Jon. Same structure, one level down.

**Ingestion Loop**
Governs when research findings and session content enter the wiki (see [[wiki-master-origin]]). Owned by wiki-master.
Triggers (mandatory):
- Test run completed and scored → ingest
- Hypothesis updated with a grounded claim → ingest
- Session produces a finding a future session would need → ingest
- Jon says "ingest this" → ingest
- Loop taxonomy or methodology document finalized → ingest to wiki/concepts/ or wiki/methodology/
Do NOT ingest: raw LOG.md entries, in-progress work, draft proposals not yet approved.

---

### Category 2 — Skills Ecosystem Loops

These govern how skills are improved and stabilized over time.

**Skill Improvement Loop**
Any master can initiate (not just test-master). FBC-before-deposit is required.
Loop sequence: identify gap → FBC on whether gap is real → deposit proposal to skills/intake/ → skills-master reviews → implements → originating master verifies → close intake file.
[[frame-before-commit]] self-application rule: run FBC on any interpretation of a finding before depositing to skills/intake/. Do not skip to save time. Verification-gap caveat: test-master is a stakeholder in FBC's success — self-score divergence is more reliable than self-score delta quality.

**Ratchet Loop Rules**
Canonical rules that any specific Ratchet Loop instance must follow. Not a loop itself — a constraint set that all named ratchet loops inherit.

Rules (all mandatory):
1. Single isolated change — no bundling
2. Establish baseline at N≥3 before any change
3. Test the change at N≥3
4. Stopping criteria defined before running (improvement threshold / abandonment threshold / ambiguous-extend-N rule)
5. If improvement: accept, document, move to next change
6. If no improvement: reject, document why, do not re-attempt without new justification
7. Scope exclusions require explicit owner approval before modification

**Named Ratchet Loop Instances:**

| Instance | Owner | Active Scope |
|----------|-------|-------------|
| FBC Protocol Ratchet | Test Master | FBC SKILL.md format and discipline rules |
| Skill Improvement Ratchet | Any master | Any skill's implementation |
| Research Method Ratchet | Test Master | Research design methodology |

Canonical example: `research/01-FBC-Improvement/01-FBC-002-ratchet-design.md`

---

### Category 3 — Test Master Loops

These govern the research process.

**Hypothesis Loop**
The primary research process loop.
1. Hypothesis stated with precision (what would falsify it?)
2. Literature search: BIBLIOGRAPHY.md + web search for relevant external research
3. Frame against searchable external data (not just internal runs)
4. Design test: FBC on design question, null-test first, null-result description required
5. Execute: CLI harness, multi-model where applicable
6. Interpret: FBC extended mode + web validation + wiki query for prior findings + self-report (motivated bias flagged)
7. Update hypothesis list with grounded claim
8. If branch point reached: enter Selection Loop
9. Log: test-log entry + trigger Ingestion Loop

**Standing steps (non-optional):** Steps 2, 3, and step 6's validation layer. Web search and wiki query are not optional enhancements — they are required.

**Identified gap (2026-05-22):** Steps 2 and 6's web search + wiki validation steps were not being executed consistently. They are now explicitly mandatory.

**Selection Loop**
Jon-as-selector. Entered when a Hypothesis Loop reaches a branch point with two or more meaningfully different research directions.
- Brief delivered via present-to-jon skill: FINDINGS / BRANCHES / CROSS-PROJECT NOTES / COMMIT / JON SELECTION format
- Decision-scope calibration: only include items requiring Jon's values, preferences, or non-recoverable decisions; test-master resolves recoverable/methodology decisions independently
- Jon's selection triggers a new Hypothesis Loop on the selected branch

---

### Nesting Relationships

```
Session Loop
  └── Checkpoint Loop (active when background agents are running)

Hypothesis Loop
  └── Selection Loop (when branch point reached)
  └── Ingestion Loop (after test logged)
  └── Skill Improvement Loop (when findings produce improvement proposals)

Skill Improvement Loop
  └── Ratchet Loop Rules (constrains any specific ratchet instance)
```

The Ingestion Loop is the bridge between research and the wiki. Without it firing, findings remain in the worktree or research/ directory and are inaccessible to future sessions.

## Conflicts

None.

## Related

[[frame-before-commit]], [[skills-system]]
