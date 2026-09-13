---
title: "Disclosure routes to Anthropic and adjacent bodies — measured at primary source"
created: 2026-08-07 (session 2)
resolves: "wayfinder tickets W1 and W2"
provenance: "[relayed — research subagent, 71 tool calls, all fetches 2026-08-07]"
⚠️: "DOUBLE-HOP. Every quote below passed through WebFetch's summarizing sub-model AND then through a subagent's report. It is NOT a byte-level copy of any page. Read the source directly before acting on exact wording — the agent said so itself and the caution is carried here rather than dropped."
---

# The structural finding, stated first because it decides the question

**Anthropic publishes no intake for conceptual or methodological work that is neither a security
vulnerability nor a demonstrated jailbreak.** `[relayed — exhaustive fetch of Anthropic's live public
pages, 2026-08-07]`

The **only** published Anthropic language contemplating such a route is one sentence on the
Transparency Hub — *"We maintain open channels of communication with the broader AI research
community, allowing for informal reporting of potential issues or concerns"* — and **it names no
channel, no address, and no process.** `[retrieved — anthropic.com/transparency/voluntary-commitments,
page shows Last updated July 23, 2026]`

**This is the same shape as session 1's ASOP finding, in a third domain: everyone assumes a door
exists; nobody has checked; there isn't one.**

---

# ⛔ FLARE-AI IS DISQUALIFIED. Added 2026-08-07 ~14:50 after W10.

**The route that looked purpose-built for this situation, with a confidentiality sentence printed on
its own submission form, is the one that would publish the work in 45 days by default.**

**1. The confidentiality sentence is conditional on NOT submitting.** `[retrieved —
ai-reports.org/ai-flaw-report]` *"Reports are handled in strict confidence, and will not be saved or
sent **unless you choose to submit them**."* **The clause covers the DRAFT. It says nothing about what
happens once you submit — and it is literally true while being materially incomplete.** **Anyone
reading it as protecting a submitted report is reading something the sentence does not say.**

**2. Submitted reports enter CERT/CC's VINCE, and CERT/CC publishes by default.** The code POSTs to
`https://kb.cert.org/vince/comm/api/vulreport/` `[retrieved —
raw.githubusercontent.com/…/submit-cert/route.ts]`. CERT/CC's policy `[retrieved —
certcc.github.io/certcc_disclosure_policy]`:

> *"Vulnerabilities reported to the CERT/CC **will be disclosed to the public 45 days after the
> initial report**, regardless of the existence or availability of patches or workarounds from
> affected vendors."*

**Reporter credit is included unless the reporter requests otherwise; reporter identity and contact
are forwarded to vendors unless the reporter requests otherwise.** **FLARE-AI discloses none of this
at the point of submission — the governing policy is INHERITED, not stated.**

**3. Submitted reports ARE persisted.** Strapi v5 on PostgreSQL `[retrieved — repo README]`. The
paper's hedge is visible at the seam: *"Flare-AI is **stateless by default**: reporters can generate
and download reports locally without server-side storage… **then optionally disseminate**."*
**"Stateless by default" describes the download path. The disseminate path is the other branch of the
same sentence and is never claimed to be stateless.**

**4. "Reports are forwarded to Anthropic" is an uncaveated homepage badge with NO IMPLEMENTATION.**
`[retrieved — reporting-orgs/index.tsx]` **In the open-source repo, Anthropic maps to three outbound
webpage links and nothing else** — no endpoint, no email, no API. **The paper's actual claim is
weaker and unattributed:** *"**Several of** these organizations… have made commitments to integrate
with the routing layer."* **Anthropic is named in the collaboration set. Anthropic is NOT named in the
commitment set, and the paper never says which organizations committed.** **No Anthropic-published
document acknowledges FLARE-AI anywhere.**

**5. No terms of service, no privacy policy, no data-handling statement, no retention or deletion
policy.** The site self-describes as **"a research preview."** **Step 7 asks the reporter to declare a
disclosure plan and propose an embargo in a free-text box — it grants nothing and commits nobody.**

**⭐ And the paper diagnoses the defect it reproduced:** *"Researchers flagged limited clarity on core
process details: anonymity, public disclosure, and downstream coordination."*

**⚠️ Method note worth more than the finding: the agent CAUGHT AND DISCARDED ITS OWN QUOTE.** A prior
pass had returned *"Flare-AI does not centrally store reports"* as verbatim from the paper; **on
literal re-check that sentence does not appear.** **A summarizer produced the single most convenient
sentence for the conclusion, and only re-reading the primary caught it.**

---

# ⭐ `disclosure@anthropic.com` — confirmed, and it may be the actual door

`[retrieved — anthropic.com/responsible-disclosure-policy, third fetch, 2026-08-07]` The RDP directs
**`disclosure@anthropic.com` for POLICY QUESTIONS**, distinct from `usersafety@` for model-safety
concerns and HackerOne for vulnerabilities.

**A zero-payload process question — "what is the right route for someone outside a lab who thinks they
may have something worth a look and does not want to publish it?" — IS a policy question.**

**⚠️ Carry the qualifier: this address appeared in fetch 1, did NOT appear in fetch 2 of the same
page, and reappeared in fetch 3. Two of three. Verify on the live page before using it.**

**⚠️ And the constraint that shapes everything above it: Anthropic's VDP explicitly EXCLUDES
"red-teaming of models" and "content issues with model prompts"** `[retrieved — same page]` — **which
is precisely where a conceptual or methodological concern about model behaviour would land.**

---

# ⚠️ The two clauses that actually decide anything

## 1. The Model Safety Bug Bounty publishes what you send, indefinitely, and gags you

`[relayed — support.claude.com/en/articles/12119250-model-safety-bug-bounty-program, Last Updated
March 16, 2026]`

> *"Participant agrees that all data submitted to Anthropic, including its products and services, in
> connection with this Program **may be used, stored, shared, and/or published by Anthropic
> indefinitely** in furtherance of its safety research, model development, and related purposes
> **without further obligation to Participant**."*

**And in the same document, the participant may disclose only that the program exists and that they
are in it** — jailbreaks, the test question set, classifier details, and model information are all
prohibited without consent.

**The asymmetry runs entirely against the sender: Anthropic may publish; the participant may not.**
**For someone whose stated constraint is "I should not release everything I've done to the public for
safety reasons," this route is the exact inversion of what he wants.** This confirms, with actual
clause text, the flag raised 2026-08-07 that the bug bounty was one of only two irreversible moves on
the board.

**⚠️ Also measured: `anthropic.com/news/model-safety-bug-bounty` (dated Aug 8, 2024) carries a STALE
figure ($15,000) and a dead deadline. The help article shows $35,000. Do not quote the news post.**

## 2. The Feedback clause — the sleeper

`[relayed — anthropic.com/legal/consumer-terms, Effective Oct 8, 2025;
anthropic.com/legal/commercial-terms, Effective June 17, 2025]`

> Consumer: *"You have no obligation to give us Feedback, but if you do, you agree that **we may use
> the Feedback however we choose without any obligation or other payment to you**."*

**Neither the consumer nor the commercial clause imposes any confidentiality duty on Anthropic.**

**The operative drafting constraint this creates: any message framed as *feedback on the Services*
falls under it.** **A disclosure letter must not be written as feedback, and must not be sent through
an in-product feedback surface.** This does not assign IP in an unrelated body of work — but it is a
free licence over whatever is characterized as feedback, and characterization is done by framing.

---

# The routes, ranked by fit

| Route | Scope | Obligation on sender | Fit |
|---|---|---|---|
| **`usersafety@anthropic.com`** | *"safety issues, 'jailbreaks,' and similar concerns… with enough detail for us to replicate the issue"* | **None published — and that cuts both ways.** The Safe Harbor and Research Guidelines sit in a different section and appear NOT to cover this paragraph. **No safe harbour, no confidentiality commitment, no SLA.** | **Widest published Anthropic door.** *"Replicate the issue"* frames it around demonstrated problems. **⭐ For a ZERO-PAYLOAD process question, the absence of confidentiality protection costs nothing** — you cannot leak what you did not send. |
| **⭐ FLARE-AI / `ai-reports.org`** | *"any broadly-scoped flaw, vulnerability, or incident relating to an AI system or model"* — **explicitly broader than security.** CMU SEI + 18 authors incl. Longpre, Kapoor, Bommasani, Narayanan, Liang, Pentland. Routes into **CERT/CC's VINCE**. **Anthropic is a named receiving venue**; so are UK AISI, CERT/CC, OECD, Hugging Face, Cohere, AVID. | Report page: submissions *"handled in strict confidence, and will not be saved or sent unless you choose to submit them."* Dissemination described as **"optional."** No ToS or IP clause surfaced. | **Closest structural fit found anywhere.** Purpose-built for people who *"do not know what or where to report."* **⚠️ Built around *demonstrable* flaws — a conceptual concern with no demonstration is at the edge of its stated preference.** **⚠️ Announced 1 July 2026. Five weeks old.** |
| **Responsible Disclosure Policy / HackerOne** | *"technical vulnerabilities… misconfigurations, CSRFs, privilege escalation, SQL Injection, XSS, directory traversal"* | Non-disclosure until written notice; safe harbour conditioned on disclosures being *"unconditional."* | **Structural mismatch. Systems-security only.** |
| **External Researcher Access Program** | API credits for safety researchers | *"Applicants… do not receive exemption from our Usage Policy."* | **A compute-credit programme, not a disclosure channel.** It creates no route to tell Anthropic something exists. |
| **Anthropic Fellows** | 4-month funded empirical safety research | Employment-style application | **Public output is the deliverable — directly incompatible with not publishing.** ⚠️ **Deadline shown: July 26 — already past.** |
| **Frontier Model Forum** | `info@` / `membership@` | — | **No individual intake. Org-to-org only**; membership requires developing frontier models at scale. |
| **US CAISI (NIST)** | *"industry's primary point of contact within the U.S. government"* | — | **No published intake for unsolicited external reports.** And material sent there becomes a **government record.** |
| **UK AISI** | — | — | **`aisi.gov.uk/contact` returns HTTP 404. No email verified at all.** Reachable indirectly as a FLARE-AI venue. |
| **NYU CMEP** — Jeff Sebo, director | *"foundational research on the nature and intrinsic value of nonhuman minds, including… artificial minds"* | **None** | **Ordinary faculty addresses. ⚠️ No confidentiality obligation whatsoever.** |
| **Eleos AI Research** | *"potential wellbeing and moral patienthood of AI systems"* — *"If you're interested in collaborating, please get in touch"* | **None published** | **An explicit collaboration invitation. No submission process, no stated confidentiality.** |
| **Anthropic model-welfare programme** | — | — | **NO published contact route of any kind.** The April 24, 2025 post lists no email, no form, no invitation. **Confirms the session-1 finding.** |

---

# Apart Research sprints publish. The withdrawal was correct.

`[relayed — apartresearch.com/research and /sprints, observed 2026-08-07]` Past submissions appear as
**publicly browsable individual project pages with author names, dates, methodology, findings, and
per-project URLs.** The site has sections headed *"Recent Winning Hackathon Projects"* and
*"Publications From Hackathons."* Publication is framed as a **benefit**.

**⚠️ Carry the qualifier: this is OBSERVATIONAL. No written "submissions are published by default"
policy was found, and NO OPT-OUT LANGUAGE WAS FOUND EITHER WAY.**

**Bottom line: a research sprint is a publication venue.** Not a private channel.

---

# ⚠️ The Hard Fork recollection is close but wrong in the part that matters

**The mechanism is real and trivial: a standing line in every episode description —** *"We want to
hear from you. Email us at hardfork@nytimes.com."* `[relayed — feeds.simplecast.com/6HKOhNgS and the
Apple Podcasts listing, 2026-08-07]` **No form, no structured intake.**

**But the episode was not an Anthropic episode.** The likeliest referent is **10 July 2026 — *"Do
Social Media Bans Work? + A Conversation About A.I. Consciousness + Tool Time"* — whose guest was
JEFF SEBO, NYU**, on *"new research into 'A.I. welfare' and whether A.I. could ever become
conscious."* **Sebo is NYU, not Anthropic.** The 7 Aug 2026 episode's guest was **Chris Painter of
METR.** **⚠️ NOT VERIFIED whether the Sebo episode issued a question solicitation beyond the standing
boilerplate — nytimes.com is blocked to the tool.**

**And the decisive property: it is a journalist's inbox.** The catalogue contains *"We Answer Your
Questions"* episodes — **listener mail is read on air at the hosts' discretion, with no published
control for the sender.** **Anything sent there is on the record with two reporters.**

---

# ⭐ Three independent paths converge on one person

**Jeff Sebo** is (a) the **Hard Fork AI-consciousness guest**, (b) **director of NYU CMEP**, which
**partners the Apart Digital Minds sprint**, and (c) **an author of `saiwe.pdf` — *Studying AI Welfare
Empirically* — which has been sitting UNREAD in this repo's root since session 1.**

**That convergence was not visible from any single one of the three searches.** It is the reason this
page exists rather than a route table.

---

# The literature check: the named mechanism is ABSENT, and that is not a refutation

**Jon's stated mechanism** — a thinking framework moves the frontier → leaks → uplifts attackers via
open-weights models — **requires scaffolding to produce CAPABILITY gains.**

**What the literature actually holds:**

1. **Scaffolding is elicitation, not capability creation.** Elicitation techniques *"reveal latent
   capabilities that already exist, rather than creating new ones."* `[relayed —
   policywindow.org/wiki/capability-elicitation]`
2. **Prompting is the WEAKER elicitation method.** Greenblatt, Roger, Krasheninnikov & Krueger,
   *Stress-Testing Capability Elicitation With Password-Locked Models*, arXiv 2405.19550 (29 May
   2024): simple prompting is insufficient; *"a few high-quality demonstrations are often sufficient
   to fully elicit password-locked capabilities"* — **via fine-tuning.**
3. **⭐ The transfer vector the literature actually studies is FINE-TUNING AND DISTILLATION, not
   framework text.** Kaunismaa et al., *Eliciting Harmful Capabilities by Fine-Tuning on Safeguarded
   Outputs*, arXiv 2601.13528 (20 Jan 2026): prompts in adjacent domains → responses from safeguarded
   frontier models → **fine-tune an open-source model on those pairs** → *"recover approximately 40%
   of the capability gap between the base open-source model and an unrestricted frontier model"* in
   hazardous chemical synthesis. **The frontier→open-weights leak is real and measured. The carrier is
   a fine-tuning dataset. The prompting is a filter-evasion device, not the transferred asset.**
4. **NOTHING was found measuring whether a reasoning framework, transferred as TEXT to a weaker
   open-weights model, produces uplift on dangerous tasks.**

**The honest summary, and the qualifier must travel with it: the safety literature treats scaffolding
as elicitation-only and weights as the thing that moves capability between models. "A thinking
framework moves the frontier and then leaks to open weights" is not a mechanism the literature has
named, measured, or argued against. THAT IS A GAP, NOT A REFUTATION. Nobody has shown it works;
nobody has shown it doesn't.**

---

# NOT VERIFIED — as load-bearing as everything above

1. **⭐ What FLARE-AI does with a report AFTER you submit it.** No embargo, no publication policy, no
   ToS found. **`/about`, `/faq`, `/report` all return 404.** **This is the single most important
   unresolved question about the best-fitting route.**
2. **Whether FLARE-AI's Anthropic routing is live and accepted by Anthropic**, or an aspirational
   destination list published by CMU SEI. **Anthropic's own pages do not mention FLARE-AI.**
3. **`disclosure@anthropic.com`** appeared in a first fetch of the RDP and **did not reappear in a
   second, more targeted fetch of the same page. NOT ASSERTED.** `security@anthropic.com` was never
   seen on any page.
4. **The HackerOne programme page's own terms** — JavaScript-rendered, returned only the word
   "HackerOne." **Only the Anthropic-side help-article version is verified.**
5. **Any model-welfare contact address.** Searched and fetched; **none found.**
6. **Apart Research's written publication or opt-out policy.** Observed behaviour only.
7. **Whether Hard Fork submissions are private.** No published policy either way.
8. **UK AISI intake** — 404. **NYU CMEP's current site** — `nonhumanminds.org` returns 403; the
   readable page states the centre *"has relocated,"* so **current contact details may differ.**
9. **All 2026-dated arXiv identifiers postdate the model's training cutoff.** Fetched successfully,
   coherent abstracts, **but no independent corroboration.**
10. **The research session's WebSearch budget was exhausted (200/200) before it began.** Everything
    came from direct WebFetch, using DuckDuckGo HTML pages as a search substitute. **Coverage is
    therefore fetch-shaped, not search-shaped, and something reachable only by search may have been
    missed.**
