---
title: Actuarial Epistemology
trunk: fl
branch: [UNASSIGNED]
sub_branch: [UNASSIGNED]
branch_reason: "R-CONCEPTS; no registered branch keyword in title, slug, tags or headings"
type: concept
first_seen: stylomantic-motivations-2026-03-29-4b9fcc
source_count: 4
last_updated: 2026-06-27
---

## What This Is

Jon's actuarial training functions as a cognitive operating system across FL projects — not confined to Stylomantic's statistical models, but present in AI governance framing, FBC's structural design, and his outside-in epistemology applied to interpretability research. The core of actuarial epistemology: build credible models from observed outcomes (outside-in), quantify uncertainty explicitly, treat distributional effects as first-class claims, and validate via pre-registered empirical procedures before claiming significance.

This cross-domain pattern is why several CFL methodological choices look the way they do — they are natural applications of FCAS-level discipline to domains where most practitioners do not apply them. See also the [PERSONAL: jon] entity page for demographic context, and [[frame-before-commit]] for the ASOP 56 connection.

## What the Wiki Says

### Stylomantic: Actuarial Discipline at ML Scale

Jon's actuarial training is doing real work on Stylomantic: pre-registration, Benjamini-Hochberg correction, temporal splits, confound identification, power analysis before collection. Claude's assessment: "not table stakes in ML — most ML practitioners would not apply these." The framing is explicit — this is described as applying actuarial statistical discipline at ML scale, which is identified as "the most defensible part, genuinely real" of the Stylomantic motivation. ([stylomantic-motivations-2026-03-29-4b9fcc:T2])

Specific actuarial methods applied in Stylomantic:
- Temporal data split (train on older messages, validate on middle period, holdout on most recent) — mandatory for time-series data; prevents future-context leakage ([stylomantic-planning-2026-03-29-280197:T60])
- Three-phase pipeline with pre-specified inclusion rules (Phase A explore, Phase B significance testing, Phase C holdout) — prevents p-hacking while allowing exploratory insight ([stylomantic-planning-2026-03-29-280197:T149])
- Power analysis: 70% accuracy threshold at 80% power for Cohen's d ~0.5 effect size ([stylomantic-planning-2026-03-29-280197:T86])

The "Skittles problem" and EOS confound were identified and built around — specific domain errors that required actuarial framing to catch. ([stylomantic-motivations-2026-03-29-4b9fcc:T2])

### Outside-In Epistemology as a Research Position

The core research position of [[stylomantic]] inverts the field's dominant bet: rather than cracking internal geometry via mechanistic interpretability (upstream), Stylomantic observes outputs statistically and builds interpretability from the outside in. This is the outside-in epistemological stance applied to ML interpretability research.

"The outside-in framing you've developed is intellectually honest for what's achievable without internals access." ([stylomantic-motivations-2026-03-29-4b9fcc:T2])

Jon's actuarial epistemology — building models from observed outcomes without opening the black box — maps directly onto this inversion. API-level logit access is available; activation access is not. The actuarial practitioner builds from what is observable; the mechanistic interpretability researcher assumes access that often does not exist. ([stylomantic-planning-2026-03-29-280197:T50])

### AI Governance: Actuarial Population-Level Risk Framing

The [[ai-governance]] source applies actuarial framing to the oversight quality problem. The key claim: the risk from rubber-stamp AI oversight is not bad faith by individual reviewers — it is that when you aggregate across a wide population facing increasing AI volume, the expected value of oversight degrades even if no individual reviewer changes behavior. This is an actuarial population-level claim, not an accusation. ([ai-oversight-quality-paper-2026-03-09-89c6d7:T26])

This framing — distributional degradation over populations, even absent individual-level behavior change — is the same epistemological move actuaries make when pricing risk in specialty lines: the individual policyholder may behave identically, but the aggregate exposure distribution shifts.

### ASOP 56 → Frame-Before-Commit Connection

ASOP 56 (Actuarial Standard of Practice — Actuarial Communications) requires explicit uncertainty quantification in professional actuarial communications. FBC's [META] and [DELTA] serve an analogous function: structured explicit reckoning with uncertainty and counterfactual alternatives. The connection validates FBC's core structure from a professional disciplinary standard independent of AI or cognitive science framing. ([frame-before-commit] concept page, sourced from fbc-protocol-v2-2026-04-20-3ff2d9)

This connection is the clearest example of actuarial epistemology cross-domain transfer: a protocol designed for AI divergent reasoning is structurally justified by the same uncertainty-quantification requirement that governs professional actuarial communication.

### ASOPs as Professional Epistemic Framework for Claude-as-Tool

The 2026-06-27 ASOP ingestion planning session established a new dimension: ASOPs (Actuarial Standards of Practice) function as a pre-existing professional epistemic framework governing how Jon should use Claude in actuarial work — not just as compliance requirements but as discipline about reliance, disclosure, and data quality. ([asops-ingestion-planning-2026-06-27-a6314b])

**The Tier 1 framework (universal across all lines of business):**
- **ASOP 56 (Modeling):** Reliance and disclosure requirements for models. When Jon uses Claude to assist actuarial work, ASOP 56 requires making explicit what he is relying on Claude to do and what must be disclosed in actuarial communications. This extends the ASOP 56 → FBC connection already documented (FBC structures the uncertainty quantification ASOP 56 requires) into a broader governance question.
- **ASOP 23 (Data Quality):** Applies directly to AI-generated data and outputs. Claude's knowledge cutoff is an ASOP 23 issue. Known limitations, source quality, and cutoff dates must be surfaced — the same professional skepticism Jon applies to any data source.
- **ASOP 41 (Actuarial Communications):** Disclosure scales with stakes. Brief AI assistance on low-stakes tasks: minimal disclosure. AI-assisted analysis underlying a signed actuarial opinion: full methodology and limitation disclosure.
- **ASOP 1:** Base communication obligation — the foundation all other standards build on.

This framing inverts the common framing of "will AI replace actuaries?" — instead, it asks "what professional discipline already governs an actuary using AI as a tool?" The answer: the same ASOPs that govern other model reliance. The professional framework already exists; the novel step is applying it to Claude specifically.

**ASOP 58 (Generative AI):** A Tier 3 ASOP specifically directed at actuarial use of generative AI — highest direct relevance to Claude integration. Needs ingestion alongside Tier 1.

**T-85 dependency:** The ASOP ubiquitous language (T-85, MUST DO) is prerequisite for all ASOP work — modal terms (*may*, *can*, *should*, *must*, *will*) carry precise actuarial intent differing from casual usage. Misinterpreting ASOP requirements due to modal ambiguity is a known risk.

### Risk: Elaborateness as a Substitute for Evidence

The same actuarial discipline that protects against underpowered analysis also raises a self-check: elaborateness of design can become a substitute for starting data collection. Claude raised this in the Stylomantic motivations session — the research arc section was more expansive than the power analysis section, suggesting imagination running ahead of evidence. This is the failure mode actuarial discipline is designed to prevent. ([stylomantic-motivations-2026-03-29-4b9fcc:T2])

## Conflicts

None.

## Related

[[stylomantic]], [[ai-governance]], [[frame-before-commit]], [PERSONAL: jon]
