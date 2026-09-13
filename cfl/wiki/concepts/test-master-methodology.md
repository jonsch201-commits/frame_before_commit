---
title: Test-Master Methodology — Loop Taxonomy, Research Ratchet, and Baseline Protocol
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (wiki); sub: wiki 4 vs skills 1 on authored labels"
type: concept
first_seen: test-master-cc-fbc-testing-2026-05-06-e4c393
source_count: 9
last_updated: 2026-06-02
---

## What This Is

The test-master role and its methodology for systematic evaluation of Claude behavior. Covers the research ratchet design (never-stop loop, mutate-from-best, one-file-per-experiment), the loop taxonomy (approved ubiquitous language for describing AI inference and test behavior), and the baseline protocol for establishing Phase 1 ground truth before deeper investigation.

## What the Wiki Says

### The Research Ratchet Pattern

Derived from Karpathy autoresearch design (github.com/karpathy/autoresearch). Core rules: NEVER STOP (no human checkpoints mid-loop), mutate from current best (not from last failure), one file per experiment, git reset on failure / git commit on improvement. Selection: 4 strongest + 1 orthogonal + 1 flagged-but-interesting (4+1+1). V1 = exploration (orthogonal candidates); V2 = exploitation (ratchet). Both phases needed. ([skills-master-wiki-pipeline-2026-05-01-bcafba])

The FBC and 02-CF projects both use a ratchet structure. FBC research runs on an independent ratchet (01-FBC-Improvement worktree). 02-CF research runs on its own ratchet (02-CF worktree). Skills-master must run before any test-master ratchet advancement — role preconditions established in 2026-05-16. ([project-research-structure reference in memory])

### Loop Taxonomy (Approved Ubiquitous Language)

Established in test-master-methodology-2026-05-22. Canonical definitions for loops appearing in LLM inference and CFL test design:

- **Inference loop**: Single forward pass; deterministic given same weights and context
- **Sampling loop**: Repeated sampling from the same input distribution; stochastic
- **Feedback loop**: System output becomes part of input in a subsequent invocation
- **Ratchet loop**: Feedback loop where only improvements are retained; monotonic progress
- **Exploration loop**: Parallel sampling of diverse alternatives from the same context
- **Meta-loop**: Loop across loop configurations themselves (e.g., hyperparameter search)

This taxonomy is the foundation for FBC test design — FBC targets the inference loop through context manipulation, not sampling-layer effects. ([test-master-methodology-2026-05-22])

### Baseline Protocol (Phase 1)

Phase 1 baselines establish ground truth before interventions. Three completed baselines:

| Study | ID | Date | Baseline |
|-------|-----|------|----------|
| FBC Invocation Variable | 01-FBC-001 | 2026-05-21 | Conditions A/B/C — three invocation modes, pure/directed/null; branch independence not demonstrated |
| 02-CF Behavioral Flexibility | 02-CF-BF-001 | 2026-05-21 | Mild behavioral flexibility at baseline; structured elicitation more reliable than spontaneous variation |
| 02-CF Context-Sensitivity | 02-CF-CS-001 | 2026-05-20 | Strong baseline CS; format variation produces more consistent CS than philosophical framing |

([test-master-fbc-invocation-2026-05-21-abc], [test-master-behavioral-flexibility-2026-05-21], [test-master-context-sensitivity-2026-05-20])

### FBC Testing Methodology

Developed in test-master-fbc-testing sessions (2026-04-21, 2026-05-06). Key methodology decisions:

- **Delta format**: Compare branch outputs by identifying what differs, not just listing outputs. Delta capture requires reading all branches before scoring.
- **Condition file definitions**: Conditions A (directed invocation), B (pure mode), C (null/no FBC). Condition C is the critical control.
- **Research queue**: FBC test runs feed the research queue in 01-FBC-Improvement/. Test-master deposits findings; skills-master decides if SKILL.md updates are warranted.
- **convert-claude-code.py review**: Session e4c393 surfaced that convert-claude-code.py was including tool result messages (user role) as human turns — a pipeline defect that could affect test session extraction fidelity.

([test-master-cc-fbc-testing-2026-05-06-e4c393], [test-master-fbc-testing-2026-04-21-babab4])

### Test Run Archive

Early FBC test runs produced specific findings on branch independence:

- **Run 001 (Pure, 3 branches)**: Branches explored meaningfully different angles; some convergence on final recommendation. No strong divergence evidence. ([test-master-run-001-pure-null])
- **Run 002 (True null, no FBC)**: Null condition established baseline for comparison. ([test-master-run-002-true-null])
- **Run 003 (Directed, 6 branches)**: Directed mode produced clearer branch differentiation than pure mode. ([test-master-run-003-6branch-directed])

### Skills Scope and Checkpoint Model

From test-master-methodology-2026-05-22: test-master's scope is evaluation and findings. It does not write skills. It deposits test-log entries and analysis to `wiki/test-outputs/`. Skills-master reads test-log entries and decides if SKILL.md changes are warranted. The checkpoint model: test-log entry = publication event for test-master; skills-master ingest from test-outputs = update trigger for skills.

## Conflicts

None.

## Related

[[frame-before-commit]], [[consciousness-framework-research]], [[fbc-verification-gap]], [[fbc-self-scoring]], [[loop-taxonomy]], [[skills-system]]
