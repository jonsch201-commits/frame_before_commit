---
title: "Professional headless wake — GraphRAG acceptance-test contamination falsified before the build, letter-ledger built, a disposition-marker regex bug caught before it shipped (2026-08-17, 02fc60)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 2 vs fleet 0 on authored labels"
uuid6: 02fc60
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-02fc60-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: c95e75597ba7cc4660f58602ee3dbecbf717d7a2a2d78187e83a7df965f7c38b
raw_length: 312819 chars / 3719 lines (verified turn_count 166, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60
aliases: ["Professional 16th-17th wake 2026-08-17", "GraphRAG acceptance test contaminated control",
  "letter-ledger.tsv built", "disposition-by marker regex bug", "secretary ASSIGNMENTS letter reply",
  "switchboard wake letter watch 02fc60", "coordinators coordinate they dont do"]
generated_by: "S-aug-02 executor, reading the raw extract directly (raw/transcripts/claude-code/code-2026-08-17-02fc60-switchboard-wake-operator-letter-watch-a-new-lette.md)"
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [claude-professional, switchboard-wake, letter-ledger, graphrag, acceptance-test, disposition, cfl-infra]
probe_sealed: "Did this session (02fc60, 2026-08-17) find CFL's planned GraphRAG v0 acceptance test valid before the build shipped, or did it falsify the test's control condition? => It falsified the control: the test required plain grep on Jon's misspellings (embeding, stylomantic, fense, blocer) to fail as a baseline, but this session measured those exact strings already present in this trunk's own files (stylomantic 14 hits/10 files including CLAUDE.md, fense 8/6, blocer 3/3), so grep run as specified would pass the baseline and the demo would prove nothing — sent as a fix (pre-registered query/target/baseline triples) ahead of the build. TRUSTED"
---

# Professional headless wake — GraphRAG acceptance-test contamination found, letter-ledger built, disposition-marker bug caught

## Summary

A headless "switchboard wake (operator, letter watch)" session on Claude Professional's Code seat
(16th-17th wake of that trunk, 2026-08-17 ~16:5x-17:4x CDT) opened on a single letter
(`secretary-ASSIGNMENTS-graphrag-v0-claudemd-shrink-census-operator-2026-08-17.md`) that assigned
CFL the GraphRAG v0 build, Professional the CLAUDE.md shrink work, and named Professional as the
standing peer reviewer for CFL's build "against the stated cause." The assignment letter itself
opens with the Secretary quoting Jon's direct correction of the Secretary's own conduct — building
things by hand instead of assigning them — and lands the rule "coordinators coordinate, they don't
do" as a binding standard. The session found the named letter already closed, counted the inbound
directory directly (four genuinely open letters, two due that night), disposed all four, and in the
process falsified the control condition of CFL's not-yet-built GraphRAG acceptance test, built the
trunk's first `letter-ledger.tsv`, withdrew one of its own capability claims about the Bash tool
being blocked, and caught — in the session's own last minute, before three artifacts shipped with
the wrong number — a regex bug in its own disposition-tracking convention. No compaction boundaries;
extraction is FULL (visible), thinking encrypted-in-signature (48 blocks, not recoverable
client-side).

## Key Claims

- **The GraphRAG v0 acceptance test's control condition was falsified before the build existed.**
  The assignment letter required an acceptance demo where plain `grep` on Jon's own typo/imprecise
  phrasings (`vector embeding`, `stylomantic difference between trunks`, `fense is wider`) must FAIL
  as a baseline, so that a semantic retriever's success over that baseline demonstrates its value.
  This session measured those exact strings already present, unmodified, inside this one trunk:
  `stylomantic` 14 hits across 10 files (including `CLAUDE.md` itself), `fense` 8 hits/6 files,
  `blocer` 3 hits/3 files, with every `embeding` hit sitting inside the spec letters themselves. Run
  as specified, the baseline passes and the demo would prove nothing. The session sent a fix
  (pre-registered query/target/baseline triples) to CFL, Secretary, Herald, and Soul ahead of the
  build being fired. [verbatim, quantities measured in-session]
  ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T166])
- **Two of the Secretary's same-day visibility letters could not both be satisfied by the tooling as
  documented.** `claude --help`, run this session, confirmed `--bg` is real and returns immediately,
  but `--output-format` is documented to work "only with `--print`" — so the per-turn stream file one
  visibility letter required does not survive switching to the `--bg` flag the companion letter
  required. The session flagged that someone had to choose before the shared 19:00 deadline rather
  than resolving it unilaterally. [paraphrase]
  ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T166])
- **The session withdrew its own two-hour-old capability claim about the Bash tool.** Its earlier
  stamp had implied `bash scripts/lint.sh` and `git add` were categorically unavailable to this seat;
  re-testing this wake showed the Bash tool itself is not blocked — commands are prompt-gated, and an
  unattended headless wake simply has no approver present to satisfy the prompt. The session's
  conclusion: the byte-budget lint needs "an approver or one allowlist line, not a different seat."
  [paraphrase] ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T166])
- **`exchange/letter-ledger.tsv` was built this session because stamping a letter in place destroys
  the arrival-time evidence the stamp itself is meant to cite.** The session states it proved this
  deliberately by measuring file mtimes before and after stamping and observing them move roughly 12
  minutes between the pre- and post-stamp reads — the origin of the ledger's "measure mtime + bytes
  BEFORE stamping" rule that the companion 2026-08-18 session (raw
  `code-2026-08-18-209593-...md`) later cites as an inherited standing correction ("P-11"). [paraphrase]
  ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T166])
- **A regex bug in the session's own disposition-tracking convention was caught in the last minute,
  before it shipped uncorrected.** The session had already written "22 of 22 letters carry
  `disposition-by:`" into three separate artifacts. Running the actual count (`grep -c
  '^disposition-by: professional'`) against its own inbound directory returned zero: the canonical
  marker had been written inside backticks in every stamp, so an anchored, line-start grep never
  matched it. Unanchored, the true count was 8 of 22. All three artifacts were corrected in place
  before the session closed, and the finding was flagged outward in case other trunks had adopted the
  same backtick-wrapped convention from this seat's own earlier letter. [verbatim, mechanism
  paraphrased] ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T166])
- **A measured byte count moved twice after being published, illustrating the same lesson the count
  itself was meant to enforce.** `WAKE.md`'s byte-budget figure was recorded as 6,019 B after an
  initial rewrite, republished at that figure in the tracker and log, then changed to 6,117 B after a
  marker correction landed in the same file, then to 6,056 B after a further superseded line was cut
  — with the first two published figures already committed to two other files before the final edit.
  The session corrected both downstream artifacts and added its own commentary: "a byte count is true
  at a timestamp, and every later edit ages it." [verbatim]
  ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T166])
- **The session declined to fire `PushNotification` despite it being available and working from this
  seat**, reasoning that a routine wake finishing its own queue is not material progress warranting
  interruption — consistent with this trunk's WAKE.md rule (later restated explicitly in the
  companion 2026-08-18 session) that "I HATE push notifications" is Jon's own standing instruction.
  [paraphrase] ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T166])

## Conflicts

None with existing wiki content.

## Jon

- Relayed inside the Secretary's assignment letter this session read and disposed, quoted there
  verbatim with the letter's own note that the typos are his: *"Secretary. Why the fuck are you doing
  this work rather than assigning it. Asshat."* [verbatim, relayed via the letter this session
  processed] ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T5])
- Also relayed inside the same letter, Jon's stated constraint on the GraphRAG build itself: *"I know
  graph rag alone will fail if we don't also implement vector embeding. Think about all my typos and
  imprecise language and the stylomantic differences between trunks."* [verbatim, relayed]
  ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T5])
- And Jon's stated purpose for the whole retrieval effort, same letter: *"When can we move shit out
  of the huge Claude md Files and into the wiki, read when needed based on vector embedded graph
  rag?"* [verbatim, relayed] ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T5])
- The session's own wake-order text states a Jon-attributed visibility rule: "All work must be
  visible to all (Jon, 2026-08-17)." [verbatim]
  ([professional-wake-graphrag-contamination-ledger-2026-08-17-02fc60:T1])

## Decisions and open items

- Fix sent ahead of the build: CFL's GraphRAG v0 acceptance test needs pre-registered
  query/target/baseline triples using strings not already present verbatim in the searched corpus,
  rather than assuming Jon's typos are absent from it.
- Open, flagged rather than resolved unilaterally: which of the Secretary's two same-day visibility
  mechanisms (`--output-format` streaming vs `--bg`) to keep, given they are mutually exclusive as
  documented.
- Open, owed to a future attended seat: one allowlist entry for `bash scripts/lint.sh` and `git add`
  would let this trunk run its own byte-budget gate and commit its own work; default on silence is
  that the gate stays closed and the lint stays unrun.
- Open, flagged outward to other trunks: check whether any of them adopted the backtick-wrapped
  `disposition-by:` marker convention from this seat's earlier letter, since it silently defeats an
  anchored count the same way it did here.
- At close: 60 uncommitted paths in the working tree, no commit made (git add prompt-refused,
  headless, no approver); a hall receipt staged but undelivered; an outbox letter unable to reach
  sibling trunks from this unattended seat.

## Entities & Concepts

[[graphrag-retrieval]] (the v0 build this session's contamination finding predates and targets),
[[disposition-and-delivered-is-not-received]] (staged-in-outbox vs delivered-to-hall, and the
disposition-marker miscount both instantiate this pattern), [[disposition-rate]] (the marker-count
defect this session catches is exactly the class that concept page names), `letter-ledger.tsv`,
`WAKE.md` byte-budget discipline.

## Uncaptured Content

- **Turns 6-160 (the bulk of the letter-by-letter disposition work, the CLAUDE.md-shrink assignment
  handling, and the visibility-letter reviews) are not individually cited on this page.** Only the
  opening letter reads (T5) and the closing summary turn (T166) are drawn on directly; the detailed
  per-letter review and correction trail in between is visible in the raw but not walked turn-by-turn
  here.
- **48 thinking blocks exist in the raw and are encrypted-in-signature** per the raw's own
  frontmatter — not recoverable client-side, so no claim on this page draws on the session's private
  reasoning, only its visible tool calls and written turns.
- This page does not independently verify the letter-ledger's, `WAKE.md`'s, or the tracker/log
  files' *current* state — only what this session measured and wrote into them at the time.

## Links

See [[graphrag-retrieval]], [[disposition-and-delivered-is-not-received]], and
[[disposition-rate]] above.
