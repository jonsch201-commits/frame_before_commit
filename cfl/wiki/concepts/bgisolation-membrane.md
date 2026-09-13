---
title: BGIsolation Membrane — Wall-to-Membrane Model, Two Ratified Crossings
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (fleet); sub: fleet 5 vs wiki 0 on authored labels"
type: concept
first_seen: coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477
source_count: 1
last_updated: 2026-07-22
---

## What This Is

**BGIsolation** ("background isolation") is the standing rule that the interactive claude.ai
triage layer and the CC background/fleet layer do not freely exchange state. Before 2026-07-21 the
model was a **wall** — no traffic either direction. The coordinator charter's Item 8 (ratified
2026-07-21) narrowed this to a **membrane**: still isolated by default, but with **exactly two
ratified crossings**, named explicitly so nothing else is assumed to cross.

Primary source: `exchange/coordination-charter-2026-07-21.md` §3 ("BGIsolation: wall → membrane,
exactly two crossings").

## The Two Crossings — and only these two

- **IN — the mirror corpus.** The [[transcript-corpus]] (parsed transcripts + thinking blocks),
  read by the [[fable-mirror]] agent. This is a one-way read: claude.ai-side history flows into the
  CC fleet's awareness, never the reverse.
- **OUT — escalation packets.** Written by fable-mirror to `wiki/intake-triage/` — a hold-and-flag
  packet, never a block-and-wait. This is the only channel by which the CC fleet's unresolved
  questions travel toward Jon/claude.ai.

**No third crossing exists without a new ratification.** Any proposed additional flow across the
membrane — e.g., fable-mirror gaining write access somewhere else, a CC agent reading claude.ai
live, a claude.ai session writing directly to `wiki/` rather than through `wiki/intake-triage/` — is
a **Jon Gate**, not a coordinator decision, and not something any agent (including the coordinator)
may self-authorize.

## Why "wall → membrane" and not "wall stays a wall"

The originating 07-18 recovered packet (`conductor-execution-manager-crossvenue-intake-2026-07-18`,
registry row 78619b) argued for isolation as a hazard fence — the concern (still real) is that
letting the two layers freely intermix state recreates accumulation and provenance-confusion
failures (the same failure family as the da51cc liveness finding: a layer that quietly grows past
what anyone is tracking). A pure wall, though, made even legitimate low-risk flows (like the mirror
reading corpus for advisory grounding) impossible without ad hoc exceptions. The membrane keeps the
hazard fence — no *unratified* crossing — while naming the two flows that are actually needed and
already load-bearing (fable-mirror's read side and its escalation-write side).

## Enforcement — how this is actually kept, not just stated

- The [[fable-mirror]] agent def's `tools`/`disallowedTools` frontmatter is the mechanical
  enforcement of the OUT crossing: it can `Write`, but its charter restricts that write target to
  `wiki/intake-triage/` only, and disallows `Bash`, `WebFetch`, `WebSearch`, `Edit`, `Agent` — it
  cannot open a new crossing even if instructed to, because the tool surface doesn't support it.
- The [[coordinator]] "may consult fable-mirror... never a substitute for a Jon Gate" rule is the
  charter-level enforcement: even where the coordinator *could* treat a fable-mirror answer as
  settling something, the charter forbids treating consultation as ratification.
- Any agent proposing a change that would add a crossing must escalate it as a Jon Gate in its
  output, not implement it and report after the fact.

## Related

[[transcript-corpus]], [[fable-mirror]], [[coordinator]], [[repo-hygiene]]
