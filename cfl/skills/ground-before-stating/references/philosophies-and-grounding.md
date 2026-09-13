# Ground Before Stating — Philosophies and Grounding

This document is for skills-master and future version authors. It explains WHY the rules in SKILL.md exist and what each rule is designed to correct. It does not appear in GBS output. A cold Claude running GBS does not need to read this file — SKILL.md is self-contained for primary operations.

---

## The Named Failure Mode: The Polite Liar

RLHF trains models to satisfy Gricean maxims but interprets them through user satisfaction rather than epistemic warrant. The Quality maxim (say only what you believe adequately evidenced) creates a truth tension where fluency is prioritized over grounding. The Manner maxim (be clear) produces fluency optimization that conceals uncertainty for readability.

The result: statistical calibration without linguistic calibration. A model may be "right" at 70% confidence at aggregate rates while individual statements assert where they should estimate. Users rate confident-sounding responses as more helpful — RLHF gradient reinforces the overconfidence. This is the Polite Liar profile: technically calibrated in aggregate, actively misleading in individual statements.

GBS corrects this at the output level by requiring the scratchpad pass before stating. The pass forces three questions: How certain am I? What am I obligated to say? What kind of act am I performing?

---

## Philosophy 1 — Epistemic Calibration (P1)

**Core claim:** Language should encode degree of belief. Uncertainty in, uncertainty out. The failure mode is expressing more certainty than evidence warrants.

**What P1 corrects:** Confident language on uncertain claims causes over-reliance. Xu et al. (2025) shows verbalized uncertainty reduces over-reliance and improves user decision quality — but only when uncertainty expression is calibrated to actual epistemic state. Booster language when confidence is low actively harms user decisions by suppressing the uncertainty signal.

**Rules derived from P1:**
- Always-on Rule 2 (inference ≠ fact)
- Always-on Rule 4 (VTT flagging)
- System 1 `[unverified]` label
- System 2 `( )` confidence frames
- System 3 *suggests / indicates / establishes* evidential scale

**Why P1 alone is insufficient:** P1 gives a confidence dial — how certain to sound. A claim can be well-calibrated (P1 ✓) and still violate a disclosure obligation (P2) or misrepresent its act type (P3).

**Literature:**
- Xu et al., "Confronting Verbalized Uncertainty," *IJHCS* (2025) — first-person framing ("I'm not certain this is correct") outperforms third-person hedging ("it may be the case") for reducing over-reliance; source of uncertainty matters, not just its existence
- Kent, "Words of Estimative Probability," *Studies in Intelligence* Vol. 8 (1964) — CIA intelligence analysis; "probably" decoded as 55–90% by different readers; same hedge word, systematically different interpretations
- IPCC AR5/AR6 calibrated language scale — *very likely* >90%, *likely* >66%; bounded vocabulary prevents free-form re-decoding
- Kuhn et al., "Semantic Uncertainty," ICLR (2023) — token-level vs. semantic uncertainty distinction; calibration at the semantic level requires more than probability scores
- Tetlock & Gardner, *Superforecasting* (2015) — calibrated verbal probability; the "three-bin" problem: most people intuitively treat 80% as "going to happen"; precise verbal markers expand the probability space

---

## Philosophy 2 — Normative Obligation (P2)

**Core claim:** Language obligations are role-indexed and stakes-indexed. What you must/should/may say depends on who you are, what context you're in, and whether you've explicitly deviated. Deviation is permitted with disclosure.

**What P2 corrects:** Confidence calibration (P1) only governs how certain you sound. P2 addresses whether your role creates a disclosure obligation independent of confidence level. A well-calibrated claim may still omit required reliance disclosure. These are independent failure modes.

**Rules derived from P2:**
- Always-on Rule 1 (modal precision: *must/should/may* carry ASOP 1 meaning)
- Always-on Rule 3 (reliance disclosure)
- System 3 *must/should/may* modal markers
- Context classification section (actuarial work product = low materiality threshold)

**Why P2 alone is insufficient:** P2 gives a disclosure checklist. You can check every box and still misrepresent what kind of act you're performing — asserting when you mean to estimate (P3).

**Key ASOP 1 distinctions (load-bearing for GBS):**
- *Should consider* = process obligation (you must engage the consideration) not outcome obligation (if after engaging you conclude it doesn't apply, no violation)
- *Should* = normally appropriate; deviation is permitted but requires disclosure
- *Must* = no reasonable alternative; deviation is not the same as compliant deviation — it is non-compliance
- Two actuaries can follow the same ASOP using reasonable methods and reach different but both-reasonable results — the "reasonable range" principle

**Literature:**
- ASOP 1, *Introductory Actuarial Standard of Practice* (ASB, 2013) — must/should/may as binding professional framework; "known at time of rendering" definition of knowledge; materiality defined as: item whose omission could influence a decision of an intended user
- RFC 2119 (IETF, 1997) — independent reproduction of the same three-level hierarchy in engineering; modal terms MUST only be used where required for interoperability or to limit harm; not to impose a particular method
- ASB article: "Must, Should, May: Small Words, Huge Implications" — confirms the ASOP 1 modal hierarchy; vast majority of ASOP guidance is "should" or "should consider"; "must" is rare
- Garner, *Legal Writing in Plain English* (2001) — ABC Rule: eliminate "shall" (ambiguous between must/may/will depending on court); courts have held "shall" means "may" in some contexts; forcing the choice between must/may/will/should reveals intent
- ASB article: "ASOP No. 1 and Professional Judgment"

---

## Philosophy 3 — Speech Act / Pragmatic Integrity (P3)

**Core claim:** Utterances perform acts, not just convey content. Asserting, estimating, hedging, promising, and warning are distinct act-types with distinct obligations. The failure mode is performing one type while presenting it as another — asserting when you should estimate.

**What P3 corrects:** The Polite Liar problem at the act level. A claim can be well-calibrated (P1 ✓) and fully disclosed (P2 ✓) and still misrepresent its own act type (P3 ✗). "The data shows the model underperformed" performs an assertion. "I estimate the model underperformed based on the data" performs an estimation. These carry different obligations to the reader and different downstream risks when wrong.

**Rules derived from P3:**
- System 3 act-type markers: *I assert / I estimate / I'm relying on / I infer*
- Anti-pattern Rule 3 (structure loss — another act-type failure: performing restructuring when augmenting is correct)
- The first-person framing preference: "I haven't verified this [unverified]" outperforms "[unverified]" alone — source of uncertainty is a communicative act, not just a tag

**Hyland's insight (important for version authors):** In academic writing, hedges function as act-type signals, not just confidence signals. "Results suggest X" doesn't mean the scientist is uncertain — it means they're performing an estimate, not an assertion, and inviting scrutiny. In our System 3, *suggests* is not primarily a confidence marker — it's an act-type marker. This is P3, not P1. Don't collapse them.

**Literature:**
- "The Polite Liar: Epistemic Pathology in Language Models" (arxiv:2511.07477) — maps Gricean maxims to RLHF incentives; Quality maxim creates truth tension; Manner maxim produces fluency over grounding; Quantity maxim creates verbosity that can amplify overconfidence
- Austin, *How to Do Things with Words* (1962) — foundational: utterances perform acts; constative (describes states) vs. performative (does something) distinction
- Grice, "Logic and Conversation," in *Studies in the Way of Words* (1989) — four maxims; Quality maxim: say only what you believe true and adequately evidenced; Manner maxim: be clear — the source of the fluency-over-grounding bias
- Hyland, *Hedging in Scientific Research Articles* (1998) — corpus study; hedging in scientific writing functions as act-type signal; "may, suggest, appear" signal estimate-not-assertion and invite peer scrutiny
- Mielke et al., "Teaching Models to Express Uncertainty in Words," *TMLR* (2022) — applies speech act framing to LLM linguistic confidence directly

---

## The Three Philosophies Are Orthogonal

They operate on three distinct axes. A statement can fail on one while passing on the others:

- **P1:** *How certain am I, and does my language accurately encode that?*
- **P2:** *What am I obligated to say given my role and the stakes?*
- **P3:** *What type of linguistic act is this, and am I performing it honestly?*

The three labeling systems map onto the three philosophies:
- System 1 `[ ]` (source/basis) → primarily P2 (reliance, attribution)
- System 2 `( )` (confidence/currency) → primarily P1 (calibration)
- System 3 *italics* (epistemic markers) → primarily P3 (act-type) and P2 (modal obligation)

A well-applied GBS pass uses all three. A pass that only checks calibration (P1) will miss undisclosed reliance (P2) and act-type misrepresentation (P3).

---

## Design Decisions Recorded Here (for v2+ authors)

**Ambient vs. load-on-request:** GBS is load-on-request (like FBC) — Jon loads it when it's relevant. The always-on rules apply internally when loaded; the visible scratchpad is invocation-only. This was chosen over full ambient to avoid changing every response in every session — the skill should be a tool Jon reaches for, not a constraint on all output.

**Why process not rules:** SKILL.md is organized around the scratchpad process, not a rules list. A cold Claude following a rules list applies it mechanically and fails on edge cases. A cold Claude following a process (draft → check → label → restate) generalizes correctly to new cases. Rules in SKILL.md fall out of the process steps.

**FBC interaction rule deferred:** [UNRESOLVED] — branches likely exempt, COMMIT/META likely apply GBS. Jon's plan is to work through a live example after v1 is built. Do not resolve this without Jon present.
