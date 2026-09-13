---
title: "Graph RAG implementation decision — belief maintenance not retrieval, and the town hall 'not another pass' redirect, 2026-08-16"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-17-3a1b4c-graph-rag-implementation-decision.md
source_kind: session
date: 2026-08-16
retrieval_key: graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c
aliases: [graph RAG decision 2026-08-16, belief maintenance not retrieval, control plane not lookup, extract-then-measure-then-improve, town hall not another pass, blind spots holdout, deterministic extraction zero LLM tokens]
generated_by: coverage lane 6 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion
raw_sha256: 16af95979b3e4c4505e7d15ce3cc76681b104d3e16efa1a2866a356df302a087
raw_length: 29671 bytes / 29503 chars / 300 lines
uncaptured_assessed: populated
fidelity: paraphrase
tags: [claude-ai, secretary, graph-rag, belief-maintenance, town-hall, blind-spots, fable-mirror, ruling-deposit]
---

# Graph RAG implementation decision, 2026-08-16

## Summary

Jon (as CFL's Secretary/Fable seat) asks point-blank whether the program is doing graph RAG; the
assistant answers no, itemizing what half-exists (a real 876-node/1248-edge wiki knowledge graph
used only as a navigation surface, not traversed for retrieval) and three reasons why, most notably
a missed 2026-07-28 packet where Jon himself had already sent the idea with a "control plane, not a
lookup" framing that never got surfaced back to him on time. Jon pushes for the build as a "huge
capability unlock"; the assistant partly disagrees, arguing graph RAG moves cost rather than reduces
it and proposes a deterministic-extract-then-measure-then-LLM-last order. Jon's follow-up reframes
the real payoff as belief maintenance — claims with time, source quality, and supersession, so wrong
statements get corrected via edges rather than requiring another full corpus re-read — which the
assistant credits as the schema it would have missed. The conversation then pivots to Jon's draft
town-hall opening script; the assistant reviews it, identifies that its own wording ("read re-read
fix," "the whole corpus," "training data waiting to be considered") would be heard by every seat as
an order to do another full pass despite the opposite intent, proposes a one-paragraph redirect, and
the two co-draft a final version including a "blind spots" holdout exercise. The session ends with
the assistant depositing the day's rulings to Drive `rulings/` verbatim on Jon's "Write it."

## Key Claims

- **The assistant's direct answer on graph RAG status: no, because the existing graph is a
  navigation surface never wired to retrieval, and the actual live retrieval mechanism is grep.**
  "On graph RAG: no. Half the parts exist and they aren't wired to each other. A real knowledge
  graph exists in the CFL wiki — 876 nodes, 1248 edges, wikilinks with a link-quality standard, hub
  scores, a dashboard... But it is a navigation surface for you and a hygiene target. Nothing in the
  tree shows anything traversing it to assemble an answer. The retrieval that actually runs is grep —
  tiered, cheap-pass-then-judgment... No embeddings, no vector store, no edge traversal anywhere I
  can find." [verbatim]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T2])
- **The missed-packet finding: Jon had already sent the graph-RAG idea 19 days earlier with the
  exact "control plane, not lookup" framing, and its own timing-judgment instruction to surface it
  back to him never fired.** "The finding you should have already had: on 2026-07-28 you sent this
  yourself — two talk transcripts on Neo4j graph memory and Cognee, with the framing 'the knowledge
  graph as a control plane, not a lookup.' The packet carries your instruction that it be brought
  back to your attention at the right time, with the timing judgment given to CFL. That was 19 days
  ago and you got here first. The timing judgment didn't fire; your question did." [verbatim]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T2])
- **The assistant's pushback on "huge capability unlock": graph RAG moves cost from query-time to
  build-time rather than reducing it, and LLM-extracted edges risk becoming a second corpus of
  unaudited wrong claims at scale.** "Graph RAG does not reduce cost; it moves it. Query-time gets
  cheaper, build-time gets expensive — and if the edges are LLM-extracted, you've bought a second
  corpus of claims that can be wrong, at scale, silently. Your program produced 6+ wrong claims to
  you yesterday with humans-in-the-loop. An extraction pass over the transcript corpus will produce
  thousands of edges nobody audits." [verbatim]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T4])
- **The proposed build order: extract the existing deterministic structure first at zero LLM cost,
  measure before building more, point it at the exchange (not the wiki) first, and use LLM
  extraction last with every edge tagged as a hypothesis.** "1. Extract the graph you already have,
  deterministically, zero LLM tokens... 2. Measure before you build more... 3. Point it at the
  exchange first, not the wiki... 4. LLM extraction last, only over the corpus the deterministic pass
  couldn't reach, and every extracted edge lands with the same [reliance:] label a branch conclusion
  gets until audited." [verbatim]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T4])
- **Jon's reframe — the real payoff is belief maintenance (time, source quality, supersession), not
  retrieval — which the assistant credits as the schema addition it would have missed, and ties
  directly to a standing complaint about being asked to re-read/fix the corpus repeatedly.** Jon:
  "Hypothesis can be grouped. Time is a dimension, and the quality of the source matters. I say
  things that are wrong, and LLMs red out dated sources, and I've been trying to make you read re
  read and fix the corpus for months. So, extract what we have. Then measure. Then improve and fix
  and solve." [verbatim, typos his]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T5]). Assistant: "Your
  three additions are the schema. That's the thing I'd have gotten wrong without you: I was framing
  this as retrieval-plus-provenance, and you've said the graph's job is belief maintenance — every
  claim carries when it was said, how good the source was, and what later replaced it... a wrong
  claim isn't deleted, it gets a superseded-by edge, and everything downstream that rests on it lights
  up." [verbatim]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T6])
- **The town-hall draft review names the core failure mode explicitly: well-intentioned language
  ("read re-read fix," "the whole corpus," "training data waiting to be considered") will be heard
  by every seat as an order to run another full pass, exactly opposite of what the graph-RAG decision
  just established — and proposes a one-paragraph redirect.** "The seats will read the tools list
  plus 'the whole corpus' plus 'read re-read fix' plus 'training data waiting to be considered' plus
  'I approve introspective work' and hear one order: another pass... So the script, as written, is
  the trigger you were worried about. The concrete fix is small... 'So we are not doing another read
  of the corpus. What I want first is the graph we already have, pulled out mechanically...'"
  [verbatim] ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T8])
- **The "blind spots" exercise is deliberately designed as a holdout — Jon does not name his own
  blind spots in advance — with grading on both hits and misses so a trunk reporting zero blind
  spots is itself a signal.** "Blind spots — hold out. If you name them, you've told the trunks where
  to look and the exercise measures obedience. If you hold them, it measures the thing you care
  about: whether the co-trunks can find what you can't see, and whether they'll say it to you.
  Adversarial is right, with two guardrails: they must cite the thing you actually said... and they
  get graded on hits and misses — a trunk that reports zero blind spots is a trunk that isn't
  looking." [verbatim]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T10])
- **Session closes with the assistant depositing the day's rulings to Drive verbatim on Jon's
  explicit go-ahead, and separately flagging what is recorded as reliance-labeled inference versus
  Jon's own ruling.** Jon: "Ok, I put in a single line that's more my style and noted you've written
  down many key notes. Your note here is one of them. Write it." [verbatim]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T11]). Assistant:
  "Written. rulings/2026-08-16-jon-rulings-graph-rag-townhall-blindspots.md... first write of the
  session and it landed on the minimum call... Your holdout decision on blind spots is recorded as
  [reliance: seat's recommendation + your 'Ok'], not as your ruling, because your verbatim asks the
  question and my draft answers it." [verbatim]
  ([graph-rag-decision-belief-maintenance-townhall-redirect-2026-08-16-3a1b4c:T12])
- **Capture caveat: native-json-export, FULL completeness, 5 thinking blocks preserved (RAW
  fidelity) per the file's own frontmatter/extraction note.** [contextual, from frontmatter]

## Conflicts

None found against existing wiki pages. This session is the origin decision point for the "no graph
RAG yet, belief-maintenance schema over pure retrieval" direction and the town-hall "not another
pass" redirect — neither has previously been ingested under this or another slug (id `3a1b4c` absent
from `wiki/sources/**` before this page). A related later build (Core Memory v0 / graph-RAG v0, per
this lane's other 2026-08 picks) should be cross-checked against this page's stated build order
(deterministic extraction first, LLM extraction last) rather than assumed independent.

## Cross-Wiki

None — this is CFL infrastructure/retrieval-architecture content and a town-hall-script co-drafting
exchange, not personal/home/pro domain material. See [[wiki-query]] if present for the retrieval
discipline this session's grep-vs-graph finding bears on, and [[fable-mirror]] if present for the
Secretary/Fable role this session is conducted from.
