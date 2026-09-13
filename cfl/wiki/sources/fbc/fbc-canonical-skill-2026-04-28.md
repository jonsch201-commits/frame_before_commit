---
title: Frame-Before-Commit Canonical Skill Document
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-SRC-FBC; sub: branch `fbc` has no registered sub-branches"
source_file: raw/references/FRAME-BEFORE-COMMIT.md
project: Claude Foundational Layer
date_ingested: 2026-05-12
type: note
tags: fbc, protocol, canonical, skill-doc
source_file_status: static-reference (raw/references/ document; not a session)
---

## Summary

The canonical execution document for the FBC skill, stored in the claude.ai CFL project (created 2026-04-28). This is the most complete version of the protocol as of its creation date — it includes the full format for both modes, branch taxonomy, T-tags, perspective tagging (P-tags), inter-model branching, contraindications, and self-scoring. Three sections in this document were flagged as gaps in the wiki as of 2026-05-11: inter-model branching, contraindications, and P-tags. All three are now captured from this source.

## Key Claims

- **Perspective tagging (P-tags):** When invocation names specific viewpoints/roles, use P1/P2 framing with nested branches (P1B1T1, P1B2T3). One [META] and [COMMIT] spans all perspectives. Invocation trigger: “give me perspectives” or named viewpoint set. Stop and ask if ambiguous. — New to wiki from this source.
- **Inter-model branching defined:** Sending the same prompt to a different model is inter-model branching — genuinely independent weights, genuinely independent prior. Intra-response run is not independent of its own prior context. Convergence between inter-model runs is stronger confirmation than convergence within a single run. — New to wiki from this source.
- **Contraindications documented:** Three conditions where protocol should not run without prior baseline testing: (1) time pressure/genuine emergency, (2) hostile/adversarial context window, (3) explicit trust required where confident fast answers are needed. These are not reasons to avoid the protocol generally — reasons to test under those conditions first. — New to wiki from this source.
- **Mode disambiguation is hard rule:** Any branch type named before generation begins = DIRECTED, full stop. “Steelman it”, “give me the skeptic view”, “run it from the actuarial frame” are all directed invocations despite casual phrasing. If ambiguous: stop and ask, never silently resolve.
- **NULL branch default:** NULL should be included by default whenever the question's premise has not been explicitly validated. Most common protocol failure mode: generating sophisticated answers to malformed questions.
- **Relationship between intra/inter-response protocol:** FBC operates within a single response. Multi-sample/inter-model protocol operates across responses or sessions. They are complementary — do not substitute one for the other when execution independence matters.

## Entities & Concepts

[[frame-before-commit]], [[skills-system]]

## Conflicts

None. This document extends the wiki with three sections that were previously flagged as gaps (inter-model branching, contraindications, P-tags).