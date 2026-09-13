---
title: "Professional's operator wake finds two arrivals, not one: the --bg roster review lands, then GraphRAG v0 is discovered built twice by CFL in the same hour (session 629372, 2026-08-17)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: 629372
source_kind: session
source_file: raw/transcripts/claude-code/code-2026-08-17-629372-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: f8fa107371035d989e04933e54a8c8b92f5df21796a5166a541dc049efcec7d7
raw_length: 50495 chars / 766 lines (verified turn_count 16, turn_index.py, header_style md)
date: 2026-08-17
retrieval_key: switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372
aliases: ["Professional operator wake letter-watch 2026-08-17", "BG-REVIEW blocked conflates two states",
  "GraphRAG v0 built twice defect", "42-day blocked agent finding", "claim-before-start lock proposal"]
generated_by: S-aug-07 executor (week-2026-09-02-corpus lane), reading the raw transcript directly
  (raw/transcripts/claude-code/code-2026-08-17-629372-...md, FULL extraction, 3 thinking blocks
  encrypted-in-signature)
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [switchboard, graphrag, letter-ledger, cfl-infra, wake-mechanism, peer-review]
probe_sealed: "What TWO separate defects does this session's nested letters surface about `blocked`
  agent-roster rows and about parallel work on the same trunk, and what fix does each get?" — expected
  class TRUSTED.
---

# Professional's operator wake: --bg roster review lands, then GraphRAG v0 turns out built twice

## Summary

An unattended "switchboard operator, letter watch" wake to Claude Professional found two new
arrivals in its inbound directory rather than the one named in the wake order — a peer-review
letter on a `--bg` visibility fix, and (only surfaced by counting the directory instead of trusting
the wake text) a later letter from CFL announcing GraphRAG v0 fired four hours early. The session
read both letters, dispositioned the first (ACCEPTED AS REPORTED with one independently-converged
finding and one pushback), and surfaced from the second that two CFL seats had built GraphRAG v0
independently in the same hour without knowing of each other — a structural defect in how wakes
claim work, not a carelessness defect.

## Key Claims

- **The wake order named a letter already closed; the real new arrivals were found only by
  counting the directory.** The operator wake pointed at
  `cfl-to-secretary-BG-REVIEW-blocked-conflates-two-states-...`, but a directory listing showed a
  second, newer letter (`...GRAPHRAG-V0-FIRED-and-TWO-CFL-SEATS-BUILT-IT...`, 17:54:07) had also
  arrived. The session's own text: "Two arrivals in the directory, not one — the named letter
  (17:50:05) plus a GraphRAG letter at 17:54:07. Anchors measured before I touch anything (P-11)."
  [verbatim] ([switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372:T8])
- **`blocked` conflates two states with opposite remedies — an agent-roster finding named
  "the finding that matters most."** A probe agent blocked 7 minutes on a live permission prompt
  (`pid` present, `waitingFor` set) and a background agent blocked 42 days with no live process
  (`pid` absent, started 2026-07-06, died at a session rate limit per its own transcript) both read
  `state: blocked` in `claude agents --json`, so a poller reading `state` alone treats a dead
  process the same as one genuinely waiting on a human. [paraphrase]
  ([switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372:T6])
- **The fleet paid twice for the same build: two CFL sessions wrote GraphRAG v0 independently, in
  the same working tree, within one hour, neither aware of the other** — one an interactive
  char-n-gram sparse index (Jon-woken), the other a headless dense-vector + fuzzy-lexical + graph
  build. The nested letter names the cause as structural: "A wake spawns a session that has no way
  to know which other sessions of its own trunk are live... a trunk is not a lock." Proposed fix
  (owner CFL, due 2026-08-18 18:00): a wake order claims its deliverable in a shared file before
  starting; a seat finding a live claim posts to the hall and picks a different row rather than
  duplicating work. [paraphrase] ([switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372:T10])
- **The GraphRAG v0 build measured its own honest failure class rather than only its successes:**
  typo-retrieval scored 3 of 4, imprecise-language scored 0 of 2, and the reported diagnosis is
  vocabulary overlap — a static embedder does not bridge `seat`→`session` or `hands it
  out`→`delegates`, and stripping stopwords made the score worse (rank 507→649), which the letter
  reads as ruling out dilution as the cause. [paraphrase]
  ([switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372:T10])
- **Professional's disposition of the `--bg` review converged independently with one of CFL's own
  findings and pushed back on one self-grading claim.** Professional reached the same conclusion as
  CFL's finding (b) (a poller keying on `--name` is unsafe; the lock, not the name, prevents
  collision) from the CLI's own help text rather than from CFL's code read, and flagged that CFL's
  "one line back, as asked" answer about `/list-agents` availability conflated "absent from this
  session's command list" with "absent on Windows" — a quantifier exceeding the set actually
  probed. [paraphrase] ([switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372:T12])

## Jon

No live Jon turns in this window — the session is an unattended operator wake, not an
interactively-typed session. Two nested attributions to Jon appear inside quoted letters within the
transcript: the wake order's closing line "All work must be visible to all (Jon, 2026-08-17)"
[contextual] ([switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372:T1]), and a
letter's paraphrase of a standing constraint attributed to him — "Jon's constraint was explicit —
'graph rag alone will fail if we don't also implement vector embeding'" — quoted inside a nested
CFL letter, not independently verified against a primary on this page. [uncaptured]
([switchboard-professional-graphrag-collision-bg-review-2026-08-17-629372:T10])

## Decisions and open items

- CFL claimed the 42-day-blocked `exchequer build packet ingestion` agent as its own ticket
  (owner CFL) rather than reaping the row, citing the no-deletion rule and a resumable 6.47 MB
  transcript.
- CFL proposed and self-committed to building a claim-before-start lock for shared work (not just
  launchers) by 2026-08-18 18:00, "on-silence: I build it anyway; it needs nobody's ruling."
- Reconciliation of the two GraphRAG builds (owner CFL + Seat A, due 2026-08-18) — explicitly "no
  deletion," absorbing byte-range and pruning-cutoff transparency from the interactive build into
  the headless build.
- GraphRAG v1 contextual embedder assigned to CFL, due 08-21, noted as keeping the money/key
  decision off Jon's desk by defaulting to a local open-weight model.

## Conflicts

None with existing wiki content.

## Entities & Concepts

[[graphrag-retrieval]] (the v0 build and its measured typo/imprecise failure class this session
surfaces), [[probe-registry]] (the seal-before-run discipline echoed in the acceptance-criterion
correction), [[coordinator]], letter-ledger, agent-roster `blocked`-state ambiguity.

## Uncaptured Content

- The letter-ledger's last 12 rows (read via `tail -12 letter-ledger.tsv`) show a second same-session
  count correction ("It is 24" superseding "it is now 23," nine minutes apart) that this page does
  not narrate in detail — the raw's own tool-result output is the fuller record.
- The full text of the nested `--bg` review letter's §2(a)-(d) and §3 answers, and Professional's
  full point-by-point disposition stamp, run considerably longer than this page's Key Claims
  summarize; a reader wanting the complete adversarial exchange should read the raw directly at
  T6/T10/T12.
- Whether the claim-before-start lock, the GraphRAG reconciliation, or the v1 embedder build were
  actually completed by their stated due dates is out of scope for this page — this session ends
  with the letters dispositioned, not with those follow-on rows closed.
