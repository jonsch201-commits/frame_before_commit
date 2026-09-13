---
title: "Thinking-token scratchpad mechanics — the (a)/(b) indistinguishability, a withdrawn CC concession, and retrospective branching, 2026-08-06"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-06-2fdd92-untitled.md
source_kind: session
date: 2026-08-06
retrieval_key: thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92
aliases: [thinking-token scratchpad mechanics, relocation vs reconstruction indistinguishability, encrypted signature withdrawn concession, retrospective branching self-summary, same-model vs third-party summarizer inversion, MIRROR-INFERENCE stylometry]
generated_by: coverage lane 6 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion
raw_sha256: e9d6b7807927f03c6c309a46268fb3d1f5e1d479f43078ab70ba7ccf4c117a1b
raw_length: 24611 bytes / 24509 chars / 198 lines
uncaptured_assessed: populated
fidelity: paraphrase
tags: [claude-ai, thinking-tokens, scratchpad, mirror-inference, confabulation, claude-code, self-summary, mechanistic]
---

# Thinking-token scratchpad mechanics, 2026-08-06

## Summary

A dense technical claude.ai session works through the mechanics of writing thinking tokens to a
file-based scratchpad. The assistant's opening answer identifies a hard indistinguishability: any
"write thinking to a scratchpad" instruction produces either (a) an unperturbed thinking channel with
a lossy post-hoc reconstruction written out, or (b) deliberation genuinely relocated into the
durable, audience-aware write channel — and the two are not distinguishable from the artifact alone.
Jon then hands the assistant one of its own earlier thinking-summary blocks and asks whether it can
tell summary from verbatim; the assistant runs stylometric inference (too clean, too balanced, no
abandoned branches) rather than claiming introspective access, and names the recursion as itself the
finding — the evidence being examined is exactly the kind of unfaithful artifact the original
question was about. Jon then pushes on the pure mechanics of tool-call token selection, gets a
concession that in a Claude Code environment (where the JSON is already captured) most of the
observation-pressure argument voids — a concession Jon partially reverses one turn later by
clarifying Claude Code's own thinking blocks are encrypted-in-signature, not plaintext, which the
assistant explicitly withdraws. The session closes on Jon's proposed fix — retrospective branching,
a self-summary emitted only after reasoning completes — and an inverted finding on same-model vs.
third-party summarizers: same-model self-summary is *worse* for detecting what was pruned, because
its errors are systematically flattering rather than random.

## Key Claims

- **The central (a)/(b) indistinguishability: a scratchpad instruction produces either an
  unperturbed reconstruction or genuinely relocated deliberation, and the artifact alone cannot tell
  you which.** "The crux is that 'write all thinking tokens to a scratchpad' isn't a thing a model
  can actually do. There's no faithful mirror. You get one of two substitutions, and they have
  opposite failure modes: (a) Thinking stays in the thinking channel, scratchpad gets a
  reconstruction. Actual token selection unchanged. But the artifact is a self-report whose content
  tracks its generation condition... (b) Deliberation relocates into the write channel. Now the
  writing is the thinking, and selection changes materially... The uncomfortable part: from the
  artifact alone you can't distinguish (a) from (b). Both produce a plausible-looking scratchpad.
  That's a verification asymmetry, not a quality problem." [verbatim]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T3])
- **When Jon hands the assistant its own prior thinking-summary text and asks whether it is
  verbatim, the assistant runs stylometric inference rather than claiming introspective access, and
  names the recursion itself as the actual finding.** "I can't introspect it. I have no stored
  access to my own prior thinking tokens as objects; that block is just text in my context. So I'm
  doing stylometry on it exactly the way you could, with no privileged channel. [MIRROR-INFERENCE],
  not [grounded]. What the stylometry says: it's too clean... The recursion is the actual finding,
  though... The evidence sitting between us is a rendering of thinking that the alleged author can't
  distinguish from the real thing by any means unavailable to you. That's the (a)/(b)
  indistinguishability from my last answer, instantiated." [verbatim]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T5])
- **The mechanistic breakdown of why a channel marker changes token selection at all, given that it
  is all one autoregressive stream — four named mechanisms, none of them "motivation" or "caring."**
  "There's no side channel. A file write is a token sequence I emit into the same autoregressive
  stream as everything else — same weights, same forward passes... 1. Training-conditional policy.
  This is the big one... 2. Grammar conditioning... 3. Termination pressure. An unclosed JSON is a
  hard failure; an unfinished thought is free... 4. Segmentation. Chunked writes mean tool results
  interleave into the reasoning. That's genuine contamination, not a story about
  self-consciousness." [verbatim]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T7])
- **A concession that the observation-pressure argument mostly voids in a Claude Code environment
  where the JSON is already captured — explicitly logged as a self-caught COI ("more interesting
  than true") — which is then reversed one turn later.** "Your CC point lands, and it kills most of
  my prior answer. You already have the JSON. The thinking is already durable, already observed,
  already yours... [COI: the earlier framing was more interesting than true, and I didn't check it
  against your actual harness.]" [verbatim]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T7])
- **Jon corrects the venue fact — Claude Code's own thinking blocks are encrypted-in-signature, not
  plaintext — and the assistant withdraws its own concession as bad rather than trying to salvage
  it.** Jon: "I'm talking specifficly about the thinking tokens which are encrypted and only
  directly decryptable by Anthropic." [verbatim, typo his]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T8]). Assistant:
  "Right — encrypted signature blocks. So the CC-JSON point I conceded doesn't hold either: you have
  the ciphertext, not the trace. Bad concession, withdrawn." [verbatim]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T9])
- **Jon's proposed fix — retrospective branching, a self-summary emitted only after reasoning
  completes — is credited as structurally solving the perturbation problem by ordering rather than by
  hoping.** Jon: "I think the big thing that grinds my gears could be solve by retrospective
  branching at point of finishing thinking tokens tool call. Self summary, kinda like what I get with
  you." [verbatim, typos his]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T8]). Assistant:
  "Reasoning runs to completion, then a summarization pass emits the digest. This does structurally
  solve the thing that grinds you, and it's the right shape: nothing downstream can condition the
  reasoning, because the reasoning is finished before the summarizer exists. Zero perturbation is
  guaranteed by ordering, not by hoping." [verbatim]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T9])
- **The inverted finding on same-model vs. third-party summarizers: same-model self-summary is worse
  for detecting what was pruned, because its errors are systematically flattering rather than
  random.** "Same-model self-summary is worse for your purposes, not better. It reads its own trace
  as context and re-derives — but a model summarizing its own reasoning has the failure mode you
  already named operationally: the output tracks the generation condition... Third-party has no
  self-presentational gradient and no privileged story about what the reasoning 'meant.' It'll be
  worse at compression... but its errors are random rather than systematically flattering. For
  measuring abandoned-branch rate or self-correction suppression, unbiased-noisy beats
  biased-clean." [verbatim]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T9])
- **The stated hard floor: no summarizer, same-model or third-party, retrospective or live, can
  report what got pruned at top-p before it ever entered the trace.** "The thing neither variant
  survives: no summarizer can report what got pruned at top-p before it entered the trace at all.
  That loss is upstream of both." [verbatim]
  ([thinking-token-scratchpad-mechanics-retrospective-branching-2026-08-06-2fdd92:T9])
- **Capture caveat: native-json-export, FULL completeness, 3 thinking blocks preserved (RAW
  fidelity) per the file's own frontmatter/extraction note. Note the file's own second Human turn
  (T2, "Sorry try again") is a client-side retry of T1 with no assistant reply in between — the
  first substantive assistant answer is T3.** [contextual, from frontmatter and turn structure]

## Conflicts

None found against existing wiki pages. The (a)/(b) scratchpad-fidelity indistinguishability, the
four named mechanisms for channel-marker-driven token-selection change, and the same-model/
third-party summarizer inversion have not previously been ingested under this or another slug (id
`2fdd92` absent from `wiki/sources/**` before this page).

## Cross-Wiki

None — this is claude.ai research/design content on model-internals mechanics, not personal/home/
pro domain material. See [[ground-before-stating]] if present for the confabulation criterion this
session applies reflexively to its own prior thinking-summary output, and [[frame-before-commit]] if
present, though this session explicitly does not invoke FBC as a named protocol.
