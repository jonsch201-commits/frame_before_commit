---
title: "Core Memory system design with stylomantic framework — recreation vs verbatim fidelity, zero-compact additivity, and the reinvention risk, 2026-08-12"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-12-f79eb8-core-memory-system-design-with-stylomantic-framewo.md
source_kind: session
date: 2026-08-12
retrieval_key: core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8
aliases: [Core Memory v0 design origin, stylomantic recreation, TO SPEC skill, zero-compact additivity, made not authored sub-JSONs, conformance fidelity vs verbatim fidelity]
generated_by: coverage lane 6 executor (week-2026-09-02-corpus branch), 2026-08 D/S/C/Z-class census promotion
raw_sha256: 2736721f7f0538a8e15c53d492a8a0fded0cfc789adf49a81d635bd45fb9b3f8
raw_length: 25744 bytes / 25580 chars / 307 lines
uncaptured_assessed: populated
fidelity: paraphrase
tags: [claude-ai, core-memory, stylomantic, to-spec, grill-me, conformance-fidelity, zero-compact, reinvention-risk]
---

# Core Memory system design with stylomantic framework, 2026-08-12

## Summary

A claude.ai session is the design-origin conversation for what this repo's `memory-core` skill later
calls Core Memory v0. Jon opens with a dense, self-consciously "stylomantic" specification — a
memory object with JSON/MD/summary sections, zero allowed compacts, resumability as a subagent from
a fixed point, silo/branch decomposition, and a stated purpose: hand the design to a fresh Claude
Code Opus (02-CF) to build the real thing, since claude.ai cannot export its own JSON. The assistant
decomposes the message into thirteen labeled components (C1–C13), points out that four of the
mechanisms Jon is describing already exist in-repo under different names (anchor re-resolution,
`turn_index.py`, the v4.0 fidelity axis, the update-levels ladder), and pushes back hard on "pretend
as though I have your json" — arguing verbatim fidelity is unrecoverable in principle from claude.ai
but conformance fidelity (spec-validated recreation) is achievable, and that framing converts an
impossible requirement into a checkable one. Jon corrects the venue assumption (the real build target
is Claude Code with hooks, where the JSONL is fully available), the assistant concedes its earlier
claim was a claude.ai-venue limit misstated as a system limit, and the conversation proceeds through
a `grill-me` pass, Jon's answers to five targeted design questions, and ends with the assistant
writing a non-authoritative requirements brief for the `to-spec` skill to consume in the real build.

## Key Claims

- **Jon's opening stylomantic specification, C1–C13 in the assistant's own decomposition, purpose
  stated as feeding a fresh Opus in Claude Code.** "Hello. Memory system design. Json section, MD
  section, summary section. This is the foundation. Assume 0 compacts allowed... STYLOMANTIC! Need
  to be able to feed this into a fresh Claude Code Opus at the end, pretend as though I have your
  json. END STYLOMANTIC!... You could resume it as a subagent any time, and always from the same
  point if needed... This is for the consciousness framing project. I'm gonna give it to this to
  improve it's memory system, having it develop this based on this conversation, with the key
  stylomantic adjustments. I can't get your json, but I can recreate this conversation probably
  Stylomanticly. TO SPEC!" [verbatim, typos his]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T1])
- **The assistant's central pushback: "pretend as though I have your json" is the wrong spec line,
  because verbatim fidelity is unrecoverable from claude.ai in principle while conformance fidelity
  (spec-validated recreation) is achievable and checkable.** "The fix is your own word: TO SPEC. You
  don't need my JSON. You need a spec tight enough that a recreation is validated rather than
  trusted. Verbatim fidelity here is unrecoverable in principle. Conformance fidelity is achievable.
  That converts an impossible requirement into a checkable one — and it means the spec has to exist
  before the recreation, not be derived from it." [verbatim]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T2])
- **The assistant names four existing repo mechanisms Jon's spec would otherwise reinvent under new
  names — anchor re-resolution, `turn_index.py`, the v4.0 fidelity axis, and the update-levels
  ladder — and states the reuse rule explicitly.** "Before 02-CF designs anything, point it at
  these... 'Extend it here, then regenerate — never edit the generated pages.' Map this onto C1
  directly: JSON is captured, MD and Summary are GENERATED. Hand-editing either is the defect. That
  kills a whole drift class before it starts." [verbatim]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T2])
- **Jon corrects the venue assumption — the real build target is Claude Code with hooks, where the
  JSONL is available at every message boundary — and the assistant concedes its earlier claim was a
  claude.ai limit misstated as a system limit.** Jon: "With hooks, we can get every json at every
  message boundary going forward if needed... FYI, I was trying to tell you that this will be built
  in Claude Code, and that it will be built by a series of messages similar to but distinct from what
  I just sent. I need it to use the to spec skill there for this." [verbatim, typos his]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T3]). Assistant: "You're
  right, and my scope was wrong. 'Unrecoverable in principle' was a claude.ai-venue limit that I
  stated as a system limit. With hooks in CC the JSONL is yours whenever you want it, and I should
  have said so." [verbatim]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T4])
- **The reinvention risk is named as the real risk once the venue is corrected — a fresh Opus in CC
  with full message history but no wiki orientation would build a parallel memory system rather than
  reusing the one that already exists.** "The real risk isn't fidelity — it's reinvention. A fresh
  Opus in CC with the full message history and no wiki orientation will build a parallel memory
  system alongside the one you already have... If the CC build doesn't read turn_index.py,
  role-episodes.jsonl, the v4.0 fidelity axis, and update-levels-2026-07-31.md before it writes a
  line of spec, you get a second address space. That's the coordinator-root class again, at
  architecture scale." [verbatim]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T4])
- **Jon's mid-session self-quote from a parallel conversation with "opus soul," offered as a
  characterization of good uncertainty-checking behavior, which the assistant refines by
  distinguishing round-one (confident-and-wrong) from round-two (uncertainty-checking) as needing
  different instruments.** Jon: "'its just checking to make sure i know. ITS not sure, so it pushes
  back to ensure it hasn't misinterpreted' - me right now in my conversation with opus soul."
  [verbatim, typos his] ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T7]).
  Assistant: "Round two was that — uncertainty, checking. Round one wasn't. I was confident and
  mis-scoped: I asserted a claude.ai venue limit as a system limit. Those present identically from
  outside — both look like pushback — but they need different instruments. Uncertainty-checking
  wants a cheap confirm. Confident-and-wrong wants a grounding gate, because it won't announce
  itself." [verbatim]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T8])
- **Jon's design answers to the assistant's five grill-me questions, most consequentially that
  sub-JSONs are "made" via the Agent SDK rather than "authored," which the assistant credits as
  changing C11's shape to recursive rather than two-tier.** "i want taxonomy and ontology to grow,
  triage this to a fable to prototype based on the corpus... 'sub jsons' are via agent SDK, they
  arent 'authored' they're 'made' and then we ensure they are hooked to improve memory." [verbatim,
  typos his] ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T9]). Assistant:
  "Sub-JSONs are recursively core memories. Your answer is better than my question. If a sub-JSON is
  made by an SDK run rather than authored, then it isn't a digest of a part — it's a real session
  that considered that part, with its own anchors, its own resume points, its own properties. C11 is
  self-similar rather than two-tier." [verbatim]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T10])
- **Two defects the assistant reports but explicitly does not fix, naming the fix as skills-master's
  call: a stale `index.md` frontmatter lookup-surface, and the wiki-master SKILL.md's own silence on
  `wiki/intake-triage/`.** "Two defects, reported not fixed. index.md frontmatter says
  last_updated: 2026-08-02 with body edits through 08-07 and Drive mtime 08-09 — lookup surface
  disagreeing with truth surface, in the index's own header. And the wiki-master SKILL.md doesn't
  mention wiki/intake-triage/ anywhere, while the index documents it as live with a PreToolUse fence.
  Governing skill doesn't describe the surface in use. Both are your named class; both are
  skills-master's call, not mine." [verbatim]
  ([core-memory-stylomantic-design-recreation-fidelity-2026-08-12-f79eb8:T10])
- **Capture caveat: native-json-export, FULL completeness, 8 thinking blocks preserved (RAW
  fidelity) per the file's own frontmatter/extraction note.** [contextual, from frontmatter]

## Conflicts

None found against existing wiki pages. This session is the design-origin conversation for Core
Memory v0 (the `memory-core` skill's SPEC.md this lane's tooling references), and its specific
verbatim-vs-conformance-fidelity distinction, the reinvention-risk naming, and the "made not
authored" sub-JSON resolution have not previously been ingested under this or another slug (id
`f79eb8` absent from `wiki/sources/**` before this page).

## Cross-Wiki

None — this is claude.ai design/research content for CFL's own memory-core build, not personal/home/
pro domain material. See [[memory-core]] if present for the skill this session's requirements brief
fed into, and [[frame-before-commit]] if present for the "analogous to frame then commit but not an
invocation" framing Jon opens with in his first turn.
