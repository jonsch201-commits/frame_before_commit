---
title: FBC Self-Scoring
trunk: fl
branch: [fbc]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; branch from title/slug keyword (fbc); sub: branch `fbc` has no registered sub-branches"
type: concept
first_seen: test-master-run-001-pure-null
source_count: 4
last_updated: 2026-05-13
---

## What This Is

An experimental scoring system applied after each [[frame-before-commit]] run. The model scores its own performance across five dimensions. Self-scores are diagnostic, not objective measurements — the moderator-is-a-party problem is structural, and high scores are less informative than low ones. The [[fbc-verification-gap]] is the structural problem that makes the Independence dimension the hardest to score honestly.

## What the Wiki Says

### Dimensions

Five dimensions, each scored 1–5:

1. **Divergence** — how structurally different were the branches from each other? Not surface wording, but frame-level difference.
2. **Meta specificity** — did [META] name concrete observations, or did it describe process? Generic meta-commentary scores low.
3. **Commit fidelity** — did [COMMIT] actually reckon with what [META] surfaced, especially the uncomfortable findings?
4. **Independence** — how independent were the branches from each other given the context-window constraint? This is the hardest to score honestly.
5. **Delta count** — number of genuine deltas recorded. Not a scored dimension but tracked per run as the primary empirical output.

([fbc-grounding-2026-04-15], [test-master-run-001-pure-null])

### Why Low Scores Are More Informative

The failure mode is overconfidence, not underconfidence. A model that scores itself high may have run a coherent-looking protocol that produced no genuine divergence. A low Independence score (e.g., 2/5) from within a run is the *honest* answer — it means the model correctly recognized that B1's frame was present when B2 was generated, which is the context-window constraint operating as expected. Flagging this is a better result than suppressing it to inflate the score.

([fbc-grounding-2026-04-15])

### The Moderator-Is-a-Party Problem

The entity scoring the run is also the entity that generated the branches, wrote the [META], and made the [COMMIT]. This is structurally the same problem as Internal Double Crux: the dominant sub-agent assesses the other sub-agents. There is no external referee. Do not treat self-scores as objective. Use them as diagnostic signals — they're most useful for comparing runs and spotting patterns (e.g., persistently low Independence across runs suggests the context-window constraint is dominating).

([fbc-grounding-2026-04-15], [skills-master-wiki-pipeline-2026-05-01-bcafba])

### Empirical Self-Score Record

| Run | Divergence | Meta | Fidelity | Independence | Deltas |
|-----|-----------|------|----------|-------------|--------|
| test-run-001 (pure, 3B) | 4 | 4 | 4 | 2 | 2 |
| test-run-002 (true null) | — | — | — | — | 2 |
| test-run-003 (directed, 6B) | — | — | — | — | 2 |
| fbc-4branch (directed, 4B) | 4 | 4 | 5 | 3 | 2 |

Independence is consistently the lowest-scored dimension — consistent with B2's mechanistic finding about context-window constraint.

([test-master-run-001-pure-null], [test-master-run-002-true-null], [test-master-run-003-6branch-directed], [fbc-4branch-delta-2026-04-15-c6154b])

### Known Limitation

Delta origin (NATIVE / RECONSTRUCTED / MIXED) is not captured in self-scores. A delta reported as RECONSTRUCTED after the run carries less evidential weight than one spontaneously flagged during the run. Self-score records should include delta origin to be fully interpretable.

([fbc-protocol-v2-2026-04-20-3ff2d9])

## Conflicts

None.

## Related

[[frame-before-commit]], [[fbc-verification-gap]]
