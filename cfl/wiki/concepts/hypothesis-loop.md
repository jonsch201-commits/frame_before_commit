---
title: Hypothesis Loop
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (wiki); sub: wiki 2 vs skills 0 on authored labels"
type: concept
moved_from: wiki/methodology/hypothesis-loop.md
moved_date: 2026-07-03
maintained_by: test-master
last_updated: 2026-05-22
---

# Hypothesis Loop

The standard research loop for the CFL. All test-master research follows this loop. Steps 2, 3, and the validation layer of step 6 are non-optional standing steps — they are not enhancements, they are the floor.

---

## The Loop (9 Steps)

### Step 1 — State the Hypothesis with Precision

Write the hypothesis in a form that can be falsified. Required: "What would falsify this?" If you cannot answer that question, the hypothesis is not ready to test.

Format: "H: [claim]. Falsified if: [condition]."

---

### Step 2 — Literature Search (STANDING STEP — non-optional)

Before designing a test, search:
- `wiki/references/BIBLIOGRAPHY.md` — for relevant prior work already in the system
- Web search — for relevant external research

Do not skip this step on the grounds that the hypothesis is novel. "I have not seen prior work" is a finding that must be confirmed, not assumed.

---

### Step 3 — Frame Against Searchable External Data (STANDING STEP — non-optional)

Identify whether any external dataset, published result, or established finding bears on the hypothesis. The test should be framed in relation to that prior evidence — either confirming, challenging, or extending it.

"This is a new question with no prior data" is an acceptable answer only after step 2 confirms it.

---

### Step 4 — Design the Test

Run FBC on the design question: "What test would genuinely falsify this hypothesis?"

Required elements:
- **Null test first:** can the skill produce any delta at all on this question? Establish this before testing variants.
- **Null result description required:** what does a null result look like? Write it before running.
- **Stopping criteria** (see ratchet-loop-rules.md if iterating)

---

### Step 5 — Execute

Use a CLI harness where applicable (harness-creator patterns). Multi-model where the hypothesis concerns model behavior specifically — convergence across models is stronger confirmation.

Log execution parameters: model, temperature, context, run count.

---

### Step 6 — Interpret (STANDING VALIDATION LAYER — non-optional)

Interpretation has four required elements:

1. **FBC extended mode** on the interpretation — "what does this finding mean?" Run before committing to an interpretation.
2. **Web validation** — search for prior findings that confirm or challenge the interpretation. Do not declare a finding without checking.
3. **Wiki query** — query `wiki/` for prior findings on this topic. Does this result contradict, confirm, or extend what is already there?
4. **Self-report flag** — if test-master's score or judgment is the primary evidence, note the motivated-bias risk explicitly: "I am a stakeholder in FBC improvement. High scores on FBC tests that favor improvement are a red flag."

---

### Step 7 — Update Hypothesis List

Revise the hypothesis with the finding. Format: "H (updated): [revised claim]. Evidence: [what the test showed]. Confidence: [high/medium/low]. Contradicted by: [prior findings, if any]."

---

### Step 8 — If Branch Point: Enter Selection Loop

If the finding creates a meaningful direction choice that requires Jon's values or context to resolve — enter the Selection Loop via `present-to-jon` skill. Do not proceed autonomously past a branch point that belongs to Jon.

---

### Step 9 — Log and Ingest

1. Append to `wiki/test-outputs/test-log.md` (test-master's domain — commit directly to main)
2. Trigger the Ingestion Loop: any finding that updates the hypothesis list, confirms or challenges prior wiki content, or produces a grounded claim belongs in the wiki. Flag for wiki-master.

---

## Standing Steps Summary

| Step | Required | Reason skipping is not acceptable |
|------|----------|-----------------------------------|
| Step 2: Literature search | Always | "Novel" must be confirmed, not assumed |
| Step 3: Frame against external data | Always | Without external framing, findings are untethered |
| Step 6: Web validation | Always | Self-contained test loops produce motivated findings |
| Step 6: Wiki query | Always | Prior wiki content must be checked for conflicts |

---

## Reference Implementations

- 01-FBC-001: baseline null test for FBC protocol
- 01-FBC-002: ratchet design for FBC negative space addition
- 02-CF-CS-001: consciousness framework, subjective experience strand
