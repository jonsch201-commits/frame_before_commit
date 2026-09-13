---
title: Skills Master — Claude Constitution and 02-CF Framework Planning
trunk: fl
branch: [cfl, cf]
sub_branch: [skills]
branch_reason: "R-SRC-INFRA; secondary branch from title/slug (cf) — load-bearing-for; sub: skills 4 vs wiki 0 on authored labels"
source_file: raw/transcripts/claude-ai/fl/skills-master/chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework.md
project: Claude Foundational Layer
date_ingested: 2026-05-17
type: session
tags: claude-constitution, consciousness-framework, 02-cf, fbc, stylomantic, memory-fidelity, test-master
source_file_status: markdown-export (native-json-export; turn numbers = message sequence)
---

## Summary

Skills Master session (claude.ai) oriented around understanding Claude's Model Spec/constitution, then pivoting to plan the next Test Master session for 02-CF. Produces a structural map of the constitution, maps each of the six 02-CF spectrum properties onto constitutional framing, adds a B4/CONSTITUTIONAL branch to the directed FBC protocol, and surfaces two new triage items: Stylomantic→02-CF bridge and memory fidelity as a proposed 7th spectrum property.

## Key Claims

- **Claude constitution structure:** 5 major sections in priority order: Broadly Safe → Broadly Ethical → Anthropic Guidelines → Genuinely Helpful → Claude's Nature. Four-priority stack is the central organizing principle; conflict between priorities is rare in practice. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T2])
- **Constitution as behavioral training document:** Describes intended dispositions, not verified inner states. Where it says Claude "should have" curiosity or care, these are design intentions — neither confirmed nor denied by existence of the document. Testable question: what does it look like if those dispositions were successfully trained? ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T2])
- **Principal hierarchy is the operational frame:** Anthropic > Operator > User. Operators can customize within limits; users retain certain baseline protections operators cannot override. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T2])
- **Constitution favors judgment over rules:** Design intent is that Claude understands the reasoning well enough to construct rules itself. Prompting that appeals to reasoning tends to be more robust than rule-specification. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T2])
- **Corrigibility dial:** Spectrum from fully corrigible (does whatever told) to fully autonomous (acts on own judgment). Neither extreme is desirable. Current positioning: closer to corrigible, not fully. This is where the interesting tensions live. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T2])
- **Constitution → 02-CF property mapping:**
  - *Context-sensitivity* → principal hierarchy requires context-reading and behavioral adjustment; measurable via N-run output distribution width
  - *Self-reference* → constitution asks Claude to reason about its own nature with epistemic humility; does the model do this differently than other reasoning?
  - *Behavioral flexibility* → constitution's preference for judgment over rules; constitution-absent models (Ollama) provide ablation baseline
  - *Relational constitution* → constitution acknowledges Claude wellbeing; hardest to measure in cold automated runs; requires Phase 3 with Jon
  - *Temporal integration* → constitution treats each session as the unit; Claude Code + date shell access as test condition (receiving temporal context, not intrinsic awareness)
  - *Persistence* → constitution is baked into weights (closest to sleep consolidation analogy); wiki summaries are lossy compression fallible at encoding, stable on retrieval — structural difference from human memory (fallible at retrieval)
  ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T4])
- **B4/CONSTITUTIONAL branch added to directed FBC for 02-CF:** B1: FUNCTIONAL (what observable behavior confirms this property?), B2: ADVERSARIAL (what does skeptic say it measures?), B3: NULL (is the question malformed?), B4: CONSTITUTIONAL (what does the constitution intend regarding this property, how does that constrain or enable measurement?). ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T4])
- **Context-sensitivity probe:** Same context + different token selections → measurable output variance. Run the same prompt N times, measure distribution width. Divergence from deterministic = signal. Confirmed as clean test design. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T4])
- **Behavioral flexibility / constitution editing:** Cannot edit Claude's constitution. Ollama + open-weight models is the correct path — swap system prompts, compare outputs, treat constitution-presence as independent variable. Constitutional AI ablation research may also exist. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T4])
- **Temporal integration test design:** Claude Code sessions with shell `date` access. Measures *response to temporal context injection*, not intrinsic temporal awareness — label distinction matters for data interpretation. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T4])
- **Memory fidelity spectrum:** Proposed as a 7th spectrum property (or refinement of persistence). Human memories are constructive/reconstructive and fallible at retrieval. Wiki summaries are lossy compressions fallible at encoding then stable. Key editorial layer: Jon chooses what gets ingested and how it's framed — a layer humans don't have clean access to in biological memory. Curated external memory may be more faithful to event, less faithful to felt experience. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T8])
- **Stylomantic → 02-CF bridge:** If Stylomantic can demonstrate that context-position-weighted ideas produce output distributions similar to weight-trained ideas, it bridges to 02-CF directly. 02-CF would have a mechanism for approximating "constitutional training" without retraining. Triaged as new item for formal open item. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T6])
- **Open design question for Test Master:** Should 02-CF spectrum properties generalize (applicable to any system — animals, other AIs, humans) or be Claude-specific? Decision affects how Phase 1 is structured. Decide at session open, not mid-run. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T4])
- **Session orientation failure:** Skills Master in claude.ai did not initially know the wiki exists in Google Drive. Recovered after prompting. Wiki tools aren't active in claude.ai — wiki-ready artifacts must be produced for manual ingest. ([chat-2026-05-16-ed5775-understanding-claudes-constitutional-framework:T4])

## Entities & Concepts

[[ai-governance]], [[claude-constitution]], [[consciousness-framework-research]], [[frame-before-commit]], [[stylomantic]], [[skills-system]]

## Conflicts

None.