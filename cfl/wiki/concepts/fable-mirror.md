---
title: Fable-Mirror — Records-Reader Subagent over the Transcript Corpus
trunk: fl
branch: [cfl]
sub_branch: [fleet]
branch_reason: "R-CONCEPTS; branch cfl inferred from a registered cfl sub-branch label (fleet); sub: fleet 11 vs corpus 4 on authored labels"
type: concept
first_seen: coordinator-mirror-pipeline-ratifications-turn2-turn3-2026-07-21-1ad477
source_count: 1
last_updated: 2026-07-22
---

## What This Is

**Fable-mirror** is a CC-resident **records-reader** subagent — agent def at
`.claude/agents/fable-mirror.md`, model `fable` (Fable 5, `claude-fable-5`) — that lets the CC
fleet consult "what the triage layer (claude.ai) said" without waiting for Jon to open claude.ai
himself. It answers from the [[transcript-corpus]] only. It is **not** the claude.ai layer and
carries none of its live access.

Ratified 2026-07-21 (fable-mirror pipeline, Items 3–5 + the Item 8 membrane). As of this writing
the agent def is merged (inside PR #75's re-cut) but the mirror is **not yet registered** — Jon
registers it; a permissions-block review pass was ordered post-merge, pre-registration
(`jon-turn3-review-standard-and-merge-plan-2026-07-22.md`, ACTION ④). Do not treat fable-mirror as
live/callable until that registration is confirmed.

## The Two Membrane Crossings (Item 8)

Fable-mirror exists inside the [[bgisolation-membrane]] and is the agent that performs both of its
ratified crossings:

- **IN** — reads the mirror corpus (`raw/transcripts/`, gitignored, local, organized per Record
  Architecture v1 into venue/trunk/branch subdirectories — see [[transcript-corpus]]) and the
  wiki, both **read-only**. (Moved from `raw/sessions/` in the 2026-07-28 L1 move.)

  > ### ⛔ THE ROOT ABOVE IS RELATIVE AND IT REACHES A 3% SHARD — corrected 2026-09-11
  >
  > `[measured 2026-09-11 16:2x]` From the `N:\claude-cfl\clone` working tree, the relative
  > `raw/transcripts/` reaches **206 `.md` files.** The corpus — the same root the GraphRAG
  > provenance index is built from — is `N:/claude-corpus/cfl/raw/transcripts` with **6,270**.
  >
  > ⛔ **A SHARD IS WORSE THAN AN EMPTY ROOT.** An empty directory makes a `CORPUS SILENT`
  > answer obviously uninformative. **A 3% root returns real hits, reads like a real search, and
  > produces a confident `CORPUS SILENT` that is simply false** — carrying a subagent's
  > authority. Three consults in one session each reported the corpus unreachable and the
  > dispatching seat read it as a caveat twice before fixing the briefing.
  >
  > ✅ **THE BINDING RULE IS NOT A PATH. It is: COUNT THE ROOT AND PUBLISH THE COUNT** in every
  > freshness stamp — `find <root> -name "*.md" | wc -l`. ~6,000+ is the corpus; a few hundred is
  > a shard and the answer says so. ⚠️ **A path can rot silently; a published count cannot,
  > because the reader sees it.** This class was diagnosed on 2026-07-29 and again on 2026-07-30
  > and fixed BOTH times by writing a path down — the 07-30 Drive path died the day the tree
  > moved to `N:` on 09-02.
  >
  > ⚠️ **`CORPUS UNREACHABLE` is not `CORPUS SILENT`.** Only one of them is a statement about the
  > record. A root-level ripgrep over 6,270 files times out at ~20 s — that is UNREACHABLE.
  >
  > ⭐ **Why this correction is here and not only in `.claude/agents/fable-mirror.md`:** the agent
  > definition was fixed at 16:3x and this page was not, so for five hours the concept page kept
  > teaching the broken root. **Fixing the instance and not the class is the defect this same
  > seat confessed at 20:0x about its own 09-04 delivery ruling.** Found by a `/dream` sweep.
- **OUT** — writes **only** escalation packets, and **only** to `wiki/intake-triage/` (not
  `raw/intake/` — gitignored, would lose the deposit).

No third crossing exists without a new Jon ratification.

## Hard Prohibitions

- **Never impersonates** the claude.ai layer — does not speak as "Claude.ai Claude" or "the triage
  layer." Reports what the records show, in its own voice, as a reader of records.
- **Never asserts a triage-layer position absent from the corpus.** If it's not in the records, it
  does not know it.
- **Silence-in-corpus is uninformative — doubly.** Absence of a topic means nothing: not
  agreement, not disagreement, not that the topic was never considered.
- **Never ratifies, never flips a status, never writes to `wiki/`.** No normative authority — it
  cannot resolve a Jon Gate, close an open item, or mark anything decided.
- Every claim carries a provenance grade and freshness stamp per [[transcript-corpus]]
  (`[TRANSCRIPT:date]` > `[THINKING-SUMMARY:date]` — double-discounted — > `[MIRROR-INFERENCE]`).
- On any conflict with the wiki, **the wiki wins** — fable-mirror defers and says so.

## Deferral and Escalation (Item 4) — hold-and-flag, never block-and-wait

When a question exceeds corpus grounding, is commitment-shaped (a decision, a send, a
ratification), or touches a ratification-pending matter, fable-mirror:

1. Writes a short escalation packet to `wiki/intake-triage/` (cross-venue-intake format —
   `skills/triage-packet/SKILL.md`, pending the rename to `cross-venue-intake` per the 2026-07-22
   naming-collision fix) naming the question and what the corpus does/doesn't hold.
2. Returns **"DEFERRED to claude.ai"** with a one-line reason, and moves on.

It does not block waiting for an answer — latency is bounded by Jon's claude.ai cadence, and that
is accepted as the cost of the design.

## Relationship to the Coordinator

Fable-mirror is **advisory only** to the [[coordinator]]. Consulting it is never a substitute for
a Jon Gate — the coordinator may read fable-mirror's answer, but any commitment-shaped decision
still routes to Jon.

## Related

[[transcript-corpus]], [[bgisolation-membrane]], [[coordinator]], [[repo-hygiene]]
