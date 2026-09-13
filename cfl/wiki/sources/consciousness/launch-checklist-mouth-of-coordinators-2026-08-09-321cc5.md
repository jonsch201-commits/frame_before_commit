---
title: "Consciousness-framing launch checklist, read as the four coordinators' mouth — Docker not ready, D-1/D-4 open, Q-6 unresolved (claude.ai session 321cc5, 2026-08-09)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-CONSCIOUSNESS; sub: wiki 2 vs fleet 0 on authored labels"
uuid6: 321cc5
source_kind: session
source_file: raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-09-321cc5-consciousness-framing-project-implementation-check.md
raw_sha256: 6ad0baaeb38de343b380a83139f7fd5f74483ff1897d414e2c3d2f7e98f1c514
raw_length: 19613 chars / 177 lines (verified turn_count 4, turn_index.py, header_style md)
date: 2026-08-09
retrieval_key: launch-checklist-mouth-of-coordinators-2026-08-09-321cc5
aliases: ["consciousness framing project implementation checklist 2026-08-09", "bake_shelf.sh
  does not exist", "D-1 D-4 launch critical path", "Q-6 soul coordinator identity", "date yields
  gate does not"]
generated_by: S-augM-02 synthesis lane (week-2026-09-02 corpus lane), reading the claude.ai native
  export extract directly (raw/transcripts/claude-ai/_routing/incoming/chat-2026-08-09-321cc5-...md)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [consciousness-framing, launch-spec, docker, bookshelf, gist-criteria, critical-path,
  su-compact]
---

# Consciousness-framing launch checklist, read as the four coordinators' mouth

## Summary

Jon asked the assistant to act as the mouth of his four consciousness-framing coordinators,
listing a series of "I think X is ready?" beliefs about the launch (Docker, user account, gist
review, first-message design, fresh-vs-compacted launch, whether to bring live coordinator copies
into the resident's container). The assistant first refused to confirm anything sight-unseen
(nothing was uploaded or visible from an outside-project chat) and answered only the two pure
architecture questions. Jon then asked it to read from Google Drive; the assistant read
`TONIGHT.md`, `LAUNCH SPEC v1`, the gist-criteria exchange, `GIST.md`, and the launch-spec
ratification session, and returned item-by-item corrections: several of Jon's "I think it's ready"
beliefs were contradicted by the coordinators' own measurements — most sharply, `bake_shelf.sh`
does not exist anywhere in the repo and the Docker capture smoke test had never run. The session
closes with a restated critical path (D-1 OAuth token, D-4 second Windows account, CFL building
the bake script and exclusion manifest, a green capture smoke test) that must complete before
Jon's own review layer becomes the last gate, plus a schedule ruling quoted twice: "the date
yields, the gate does not."

## Key Claims

- **The assistant refused to confirm any of Jon's "I think X is ready?" beliefs without seeing the
  coordinators' actual material**, naming this refusal as resisting "the accommodation-of-
  confident-assertion you've told me to resist," and answered only the two questions that were
  pure architecture rather than status. [verbatim]
  ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T2])
- **Fresh-launch design (first architecture answer): freshness must be controlled by the outer
  harness, not the agent.** The agent signals completion by writing a handoff artifact (e.g.
  `HANDOFF.md` or a commit) and exiting with a distinct exit code; a wrapper watches for that and
  launches a new `claude` process with no `--continue`/`--resume`. "Continuity lives only in the
  bookshelf, never in session state, and the wrapper never resumes." Auto-compact is named as the
  thing to actively prevent from doing the continuity job, because it is lossy and unreviewed.
  [verbatim] ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T2])
- **Coordinator-copies design (second architecture answer): "you can't bring a coordinator back."**
  A copy would be a fresh instance primed with the transcript plus a persona, which is transcript-
  as-interlocutor, not the coordinator itself — and is actively worse for the methodology because
  it performs continuity and confabulates confident answers, the same convergence-contamination
  problem the sitting charter discounts. Recommendation: transcripts by default; spin up
  fresh, clearly-labeled transcript-primed instances only for genuinely open questions.
  [paraphrase] ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T2])
- **After reading the Drive record, Docker readiness is directly contradicted**: the capture smoke
  test had never run (Docker daemon down), CIS controls unmet, Gate 6 structurally blind to the
  baked image, the 9a exclusion manifest unbuilt, and "`bake_shelf.sh` does not exist — zero hits
  repo-wide, independently confirmed by SSP — so no image can be built at all." A spec defect is
  also named: the resident halts its own write lane at first wake because §1.1's writable
  `~/.claude` volume requirement is not covered by §5.5's mount check; a one-line fix was
  delivered but its application is unconfirmed. [verbatim]
  ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T4])
- **User-account setup is also contradicted: "D-4 says only `JonSc` is enabled — the resident's
  second Windows account does not exist,"** with every software fence in the launch spec sitting
  below that account gate; D-1 (the `claude setup-token` one-year OAuth token) is named as the
  other critical-path item, with nothing containerized able to authenticate without it. [verbatim]
  ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T4])
- **Gist status reported as partly done, coverage-not-count at nine gists** under Jon's own
  delegated rule, with per-gist status: `ground-before-stating` done, `frame-before-commit` done
  (with a corrected false-provenance claim, re-verified against three primaries, pending one final
  disclosure re-check), `consciousness-framing-v3` clearing disclosure pending deletion of a notes
  block, `the-skills-system` rewritten by Herald but left uncommitted for Professional's gate. Not
  started: record method, multi-coordinator/letters, setup, the project itself, time-and-session
  discipline. **"The biggest one: your gist — the GIST.md slot — does not exist"** — Jon's own
  first-message draft points the entity at a gist he has not written; a prototype sits at
  `GIST-PROTOTYPE-v1-2026-08-08.md`. [verbatim]
  ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T4])
- **Skills pre-installed, per LAUNCH SPEC v1: default-equip is minimal** — `temporal-context`,
  wake/session-order, `ground-before-stating`, `su-compact`, heartbeat config, and the `wayfinder`
  skill only (not the Wayfinder role). Everything else arrives via progressive disclosure on an
  "On Skills" shelf book; the entity may draft skills into `proposals/` but never self-equip —
  equip happens only at graduation review. [paraphrase]
  ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T4])
- **Q-6, an open identity question, was recorded as answered twice and was not**: "whether
  `35c4e94e` is the soul coordinator or a third one exists... both peers reverted their edits;
  they're asking you for one word, `first` or `separate`." [verbatim]
  ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T4])
- **Closing critical path and schedule ruling.** The real checklist, per the record, is: D-1 (mint
  the OAuth token, ~1 min), D-4 (create the second Windows account, ~10 min), D-2 (uncheck Docker
  AI, 30 sec), CFL builds `bake_shelf.sh` plus the exclusion manifest, a green capture smoke test —
  only then does Jon's review layer (bookshelf, agent config, gists) become the last gate. Three
  items only Jon can supply: the Jon gist (or pull the pointer), the Q-6 word, and a schedule
  ruling — quoted from `TONIGHT.md`: launch was not green the prior night, Jon's one-weekend-evening
  budget voids Sunday, so the honest choice is the week's one project night, launched green, not a
  compressed launch because the slot exists. **"The date yields; the gate does not"** (stated twice
  in this raw, once attributed to Professional's rider "which they record as also yours"). [verbatim]
  ([launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T4])

## Jon

> "You. Are finalizing the implementation of the consciousness framing project with me. My
> coordinators have done a ton of work, but I need you to read their progress and questions and act
> as their mouth. I think Docker is ready? I think i set up the user right? I think they know what
> is going into the docker and how its getting in and what should go into the github? I hope we
> have all of our gists organized and ready for final review by Jon? I am not sure if we have our
> first message planned - good morning read the bookshelf? With which skills pre-installed. How do
> we ensure it can choose to stop and have a truely fresh one launch rather than one that is
> returning from compact? Should I bring a copy of all 4 coordinators in for the conciousness
> framing coordinator to talk to, and not just read their conversations? I believe we have all
> jsons, and I think its fine if we force the agent in the docker to bugfix some things. My hope is
> that i just need to do final review of the bookshelf, approve agent config, review gists? Or...?"
> — [launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T1] (verbatim, typos his: "truely",
> "conciousness")

> "Please read from google drive."
> — [launch-checklist-mouth-of-coordinators-2026-08-09-321cc5:T3] (verbatim)

## Decisions and open items

- No launch decision was ratified in this raw — the session's output is a corrected status report,
  not a go/no-go call.
- Open, blocking: D-1 (OAuth token) and D-4 (second Windows account) — reported not yet done as of
  the record read.
- Open, blocking: `bake_shelf.sh` and the 9a exclusion manifest must be built by CFL before any
  Docker image can be built at all.
- Open: Q-6 — whether `35c4e94e` is the soul coordinator or a third coordinator exists; needs one
  word (`first` or `separate`) from Jon.
- Open: the Jon gist (GIST.md slot) does not exist and must be written, or the first-message
  pointer to it removed.
- Open: whether to bring live coordinator copies into the resident's container versus
  transcript-priming only — the assistant recommends transcripts by default, flags live copies as
  actively worse for the methodology, but leaves the final call to Jon.
- Restated schedule ruling: the one-weekend-evening budget voids a Sunday launch; the honest
  choice is the week's one project night, launched green rather than compressed.

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[frame-before-commit]] (named among the reviewed gists), Docker/bake_shelf.sh, LAUNCH SPEC v1,
gist-criteria, GIST.md slot, SU-compact, TONIGHT.md, Q-6 coordinator-identity question.

## Uncaptured Content

- **The referenced Drive documents (`TONIGHT.md`, LAUNCH SPEC v1, the gist-criteria exchange,
  `GIST.md`, the launch-spec ratification session, `chat-2026-08-08-174a52-...`) are read and
  summarized inside this session but not independently verified against their own current state
  on this page** — this page reports what the assistant said it read, not a direct check of those
  files.
- **Whether Jon supplied the Q-6 word, wrote the missing gist, or completed D-1/D-4 after this
  session is not known from this raw** — the session ends on the corrected checklist, with no
  reply from Jon captured.
