---
title: Ratchet Loop Rules
trunk: fl
branch: [UNASSIGNED]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; no registered branch keyword in title, slug, tags or headings"
type: concept
moved_from: wiki/methodology/ratchet-loop-rules.md
moved_date: 2026-07-03
maintained_by: test-master
last_updated: 2026-05-22
---

# Ratchet Loop Rules

Canonical rules that any specific Ratchet Loop instance must follow. All named ratchet instances (see Named Instances below) are bound by these rules unless a specific exception is documented and approved by Jon.

---

## Rules

1. **Single isolated change.** One variable changes per ratchet iteration. No bundling. If two changes seem inseparable, that is a signal to redesign the test, not to bundle.

2. **Establish baseline at N≥3 before any change.** Run the current version at least 3 times before introducing any modification. A baseline of fewer than 3 runs is not a baseline.

3. **Test each change at N≥3.** The variant must be run at least 3 times before a result is declared. A single favorable result is not sufficient.

4. **Define stopping criteria before running.** Before each ratchet iteration, state explicitly: what improvement threshold constitutes success? What result constitutes failure? What result extends the N? These criteria are set BEFORE running, not after seeing results.

5. **If improvement: accept, document, move to next.** A confirmed improvement becomes the new baseline. Document the change, the baseline scores, and the variant scores in the test-log before proceeding.

6. **If no improvement: reject, document why.** A failed iteration is as valuable as a successful one. Document what was tried, what the scores were, and the hypothesis about why it did not work.

7. **Scope exclusions require explicit owner approval.** If a proposed change touches a scope-excluded element (e.g., FBC Discipline Rules), the exclusion takes precedence. Explicitly note the exclusion in the iteration record. Override requires Jon's explicit direction.

---

## Stopping Criteria Template

For each ratchet instance, define before running:

```
Improvement threshold: [score improvement that counts as success, e.g. "mean delta score ≥ 4.5/6 across N=3"]
Abandonment threshold: [result that ends the ratchet, e.g. "COMMIT quality drops below baseline in 2/3 runs"]
Ambiguous-extend-N rule: [what triggers extending N beyond 3, e.g. "if 2/3 runs improve but 1/3 shows regression, extend to N=5"]
Ceiling rule: [when to stop even with improvement, e.g. "stop if baseline already at 6/6 N≥3"]
```

---

## Named Instances

| Ratchet Instance | Owner | Active | Reference |
|-----------------|-------|--------|-----------|
| FBC Protocol Ratchet | Test Master | Yes — 01-FBC-002 | `wiki/test-outputs/test-log.md` |
| Skill Improvement Ratchet | Any master | As needed | skills/intake/ flow |
| Research Method Ratchet | Test Master | As needed | Per research track |

**Canonical example:** 01-FBC-002 ratchet design. FBC Negative Space section added as single isolated change; N=3 baseline established in 01-FBC-001; N=3 variant planned. Stopping criteria: consistent improvement at N≥3, or ceiling (6/6 N≥3), or COMMIT quality drops below baseline.

---

## What Violates These Rules

- Running a variant before a 3-run baseline exists
- Changing two things simultaneously and declaring a result
- Setting stopping criteria after seeing results
- Calling N=1 or N=2 sufficient
- Bundling scope exclusions with the variant being tested
