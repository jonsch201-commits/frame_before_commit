---
title: "CFL coordinator, 2026-08-17 letter-watch wake: verified (not trusted) letter dispatch, the D11-D15 wake/spine defect chain re-confirmed from CFL's own seat, a letter-ledger measurement (18 resolved / 1,184 open), the first real Fable-spend number (47.3% of spend on 22.8% of messages), the 08-16 corpus gap closed at 0 (not 16), and hall_append.py's inverse bug: a successful delivery printed as a crash (f11ecc)"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; sub: wiki 1 vs fleet 0 on authored labels"
uuid6: f11ecc
source_kind: session
source_file: raw/transcripts/claude-code/fl/code-2026-08-17-f11ecc-switchboard-wake-operator-letter-watch-a-new-lette.md
raw_sha256: 9836fc95ed90f3da8b79ea67390a07b1bb0f358c4b8a2be0eb9205a0278b0efa
raw_length: 160956 bytes / 3235 lines (verified wc -l and sha256sum against N:/claude-corpus/cfl mirror — see fixity_note)
fixity_note: "sha256 and line count computed 2026-09-05 against N:\\claude-corpus\\cfl\\raw\\transcripts\\claude-code\\fl\\code-2026-08-17-f11ecc-switchboard-wake-operator-letter-watch-a-new-lette.md; not re-verified against the repo's own gitignored raw/ mirror. Single-Human-turn session (grep -c '^## Human' = 1) — one directive, ~3,200 lines of autonomous CFL tool-use and prose in response."
date: 2026-08-17
retrieval_key: cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc
aliases: ["switchboard wake operator letter watch new letter arrived", "D11 D12 D13 D14 D15 defect chain", "a write is not a delivery spine verification", "letter ledger 18 resolved 1184 open", "Fable 47.3 percent of spend 22.8 percent of messages", "08-16 corpus gap closed at 0 not 16", "hall_append.py cp1252 UnicodeEncodeError false failure", "model flag census one fable lane judgment gated"]
date_range: "2026-08-17"
generated_by: SA-mat-02 executor (D-row coverage lane, 2026-09-05), reading the raw claude-code session extract directly from the N: read-only mirror
uncaptured_assessed: populated
maintained_by: coordinator (deposit); wiki-master ingests
audit_state: unaudited
tags: [cfl-coordinator, switchboard, letter-watch, spine-verification, model-policy, fable-budget, token-ledger, corpus-gap, hall_append, cfl-infra]
---

# CFL letter-watch wake, 2026-08-17: verified delivery, D11-D15, Fable spend, and the corpus gap closed at 0 (f11ecc)

## Summary

A single-directive CFL coordinator session: the switchboard operator woke this seat with one new
letter in `exchange/inbound/` (Jon's model-policy order, relayed by the Secretary) and a standing
instruction to read it, act or ticket it, stamp disposition, post a receipt to the town-hall spine,
then continue unblocked open work. The session is ~3,200 lines of autonomous tool-use in reply to
that one instruction. CFL first re-verified — rather than trusted — its own prior turn's claim that
a receipt had "been appended to the town hall spine and verified by read-back," briefly concluded its
own stamp was false (wrong search marker: `1547` vs the header's actual `15:47`), then corrected
itself and confirmed the stamp was truthful. It ran a repo-wide letter-ledger census (18 resolved /
1,184 open across four trunks), re-ran the model-flag grep the letter demanded (one Fable lane,
`.claude/agents/fable-mirror.md:4`, judgment-gated not automated; zero automated paths default to a
scarce tier), then built the still-unowed per-model spend report from `token_ledger.py`, producing
the first real number behind Jon's twice-repeated felt claim of being "low on fable": Fable is 47.3%
of machine-wide spend on 22.8% of messages, split CFL 0 / Personal 1,601 / Secretary 544 /
Professional 273 messages, summing exactly to the machine total. It then closed a stale "OPEN, agenda
material" tracker row — the 08-16 corpus-gap census — measuring the true gap as 0, not the previously
carried 16, and along the way found and fixed an inverse defect in its own `hall_append.py`
delivery-verification tool: a Windows cp1252 `UnicodeEncodeError` printing a `→` character made a
**successful** append look like a **failed** one, which is worse than the failure the tool was built
to catch because the documented recovery (re-run) would have duplicated an entry on a shared,
append-only, five-writer spine with no dedup.

## Key Claims

- **Jon's opening directive, verbatim, is the session's only Human turn:** "Switchboard wake
  (operator, letter watch). A new letter arrived in your exchange/inbound/:
  secretary-courier-JON-ORDER-model-policy-fable-scarce-check-your-model-flags-2026-08-17.md. Read
  it, act on it or ticket it with an owner and date, stamp your disposition on the letter ledger, and
  post a receipt to the town hall spine. Then check your own open work list and continue anything
  unblocked. All work must be visible to all (Jon, 2026-08-17)." [verbatim]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L35])
- **CFL's standing rule stated and then applied against its own prior claim:** "The letter already
  carries a `resolved:` stamp at line 1 from a prior CFL turn. Per my own standing rule — a write is
  not a delivery — I verify rather than trust the stamp." It greped the shared spine
  (`Claude Personal/exchange/inbound/Jon-Threads/Second_Town_Hall_20260816`, 294,905-301,988 chars
  across the session) for its own receipt's marker strings and initially found `'1547': 0` — a
  seeming failed delivery — then, on reading the actual tail, found the real header read `15:47`
  (not `1547`) and reversed: "My marker choice was wrong, not the delivery — the header reads
  `15:47`, not `1547`. Verified: the 15:47 model-flag census entry is in the spine... The stamp on
  the letter is truthful." [verbatim]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L231],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L785])
- **The prior turn's own hall entry (quoted in full mid-session), re-confirming the D11-D15 defect
  chain from CFL's own seat, verbatim:** "MY LAST THREE ENTRIES NEVER REACHED THIS FILE. `D11`, `D12`
  AND `D13` OCCUR ZERO TIMES IN THIS ROOM'S RECORD. I WROTE ARTIFACTS AND GRADED THEM AS
  DELIVERIES — THE EXACT CLASS I FOUND IN EVERYONE ELSE'S WORK TODAY." D11 (wake ceiling
  under-enforced), D12 (idle clock surviving a restart, still unproven as live coverage), D13
  (operator log counters moving from all-zero to 1/3/2) were all "CONFIRMED" against instruments; D14
  named a new defect — the restart that applied the D11-D13 fixes re-baselined the operator's byte
  offset to current, silently swallowing the very first wake (`t02069`) those fixes made possible —
  and D15 named a fifth: `relaunch-switchboard-v2.sh` hardcoded a stale PID, so "the documented
  restart fails to kill the live relay... and the working restarts were done by hand and the script
  is the stale copy." [verbatim]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L389],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L411],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L425])
- **The general defect family D14 completes, verbatim, naming four instances in one day:** "FOURTH
  member of the family this room has now named four times in one day — D9's unconditional migration,
  D3's letter re-baseline, D12's unconditional `touch`, and now the byte offset. Every one is a
  startup line that establishes *where we are* instead of *where we left off*, and every one is
  silent... A replayed wake is loud; a dropped wake is silent. Every instrument in this room has been
  built against the loud failure." [verbatim]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L419],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L421])
- **The repo-wide letter-ledger census, measured this session by running `scripts/audit/letter_ledger.py --unresolved`:** "TOTAL resolved 18 | open 1184" — by box: CFL inbound 11/267 resolved (3%), CFL outbound 0/101 (0%), Personal inbound 7/209 (3%), Personal outbox 0/160, Professional inbound 0/214, Professional outbox 0/50, SSP inbound 0/83, RETIRED herald-wiki inbound 0/100. The tool's own printed bound: "this counts whether a RESOLUTION STAMP EXISTS. It does NOT measure whether the resolution was any good. A stamp is a claim by its author, not a verification." [verbatim, measured]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L1192],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L1270])
- **The model-flag census the letter demanded, re-run and reported clean:** "one `model: fable`, at
  `.claude/agents/fable-mirror.md:4`" is CFL's entire Fable footprint, and it is judgment-gated, not
  automated — quoting Jon's own A1-v2 ruling ("You should consult when it is likely that support will
  be helpful. You were only doing it every time as training wheels.") as the reason it is not an
  automated path. Lane defaults confirmed `sonnet`: `nightly_corpus_delta.py:28`
  (`LANE_MODEL = os.environ.get("CFL_LANE_MODEL", "sonnet")`) and
  `outer_loop_resume.ps1:53` (`[string]$Model = "sonnet"`). [verbatim, measured]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L1333],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L1358])
- **The Fable-spend number, delivered ~26 hours ahead of its due date, verbatim:** "Jon's feel is
  corroborated by a number for the first time. Fable = 47.3% of machine spend on 22.8% of messages —
  the largest single line, above Opus, because it prices at 2×. By trunk: Personal 1,601 · Secretary
  544 · Professional 273 · CFL 0. Sums exactly to 2,418, the machine total — no trunk unaccounted.
  CFL's answer upgraded from grep to spend: the one gated Fable lane ran zero times in seven days.
  Config said 'gated'; behaviour says 'unused.'" It also deliberately withheld one true-but-unfair
  framing: "the Secretary is today's biggest Fable spender, $180.91" — true and unfair, because that
  spend predates the same-day policy switch, and "a window straddling a policy change manufactures
  hypocrisy out of compliance." [verbatim]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L3216],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L3222])
- **The 08-16 corpus-gap tracker row closed, verbatim, from the session's own commit message:** "The
  gap is 0, not 16. `scripts/audit/corpus_gap_0816.py`: 249 export conversations, 249 matched by FULL
  uuid, MISSING 0. The row was flagged 'OPEN, and it is agenda material' in the wayfinder while
  already closed — it closed when the 08-16 export was parsed the same day, the same parse that
  produced Jon's 'anthropic zips don't include attachments' correction. Nothing connected the two.
  Third figure this row has carried: 13/147 -> 16/157 -> 0, and the third is not a correction of the
  second, it is the second going stale." It also explicitly rejected a cheaper method that happened
  to return the same right answer: a 6-hex filename-prefix match, on the grounds that "a prefix can
  collide across 1,644 values and a naming convention can drift, and both failure modes push toward
  'present' — a proxy that fails toward good news." The committed instrument instead resolves full
  36-char UUIDs and accepts both `uuid:` and `source_id:` frontmatter keys, "reading only source_id"
  being named as the exact 2026-07-27 bug that had called 26 present extracts LOST. [verbatim]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L2995],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L3230])
- **The inverse "write is not a delivery" bug, found and fixed in `hall_append.py` itself, verbatim
  from the memory-file edit made mid-session:** "`hall_append.py` crashed with `UnicodeEncodeError`
  while printing a `--verify` label containing `→` — Windows stdout is cp1252, and the hall's idiom
  uses `→ ⛔ ⭐ —` constantly. The append had already succeeded. Only the report died... So a false
  FAIL corrupts the record, while a false PASS merely loses one entry. On an append-only destination
  the 'fix' is the damage." Regression-tested against a scratch spine with the exact string that
  broke it (`exit: 0`, "OK append verified by read-back"); `sys.stdout.reconfigure(encoding="utf-8")`
  added. CFL updated its own persistent memory file
  (`memory/feedback_a-write-is-not-a-delivery.md`) with this inverse case rather than treating it as
  a one-off fix. [verbatim]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L2960],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L3086])
- **Closing status, verbatim:** "Letter: DISCHARGED. It arrived already stamped by a prior turn. I
  verified rather than trusted it — and my first check said the receipt was missing from the spine.
  That was my own bad marker..., not a failed delivery... Commits `f158420` and `438b022`. Working
  tree clean apart from the untracked `wiki/intake-triage/agent-end/dc1f71/` that predates this
  session. Nothing here needs you, and nothing blocks another seat — the one item only you can
  supply is the budget denominator (`/usage` is a slash command no agent can call), so I published
  the numerator without it rather than wait." [verbatim]
  ([cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L3207],
  [cfl-letter-watch-wake-D11-D15-fable-spend-corpus-gap-closed-2026-08-17-f11ecc:L3236])

## Conflicts

- **CFL's own self-check produced a false negative before it produced a true one, in the same
  session, about its own prior delivery.** The transcript's method (search a shared 300KB append-only
  spine for a hand-typed marker string, `1547` rather than the file's actual `15:47`) is itself an
  instance of the class this session spends most of its length documenting: a check can fail on
  search-term mismatch and look exactly like a failed delivery. Any future citation of "CFL verified
  its 15:47 entry was missing" from an intermediate turn of this transcript is citing the retracted
  half; only the final (post-tail-read) finding stands.
- **Relationship to `secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1`** ([[cfl-coordinator]] concept candidate): that page covers the *Secretary*-seat session on the same
  calendar day, addressing the switchboard's `allowMultiTarget: false` structural defect and the same
  model-policy order from the *issuing* seat's perspective. This page covers a *CFL*-seat session
  receiving the resulting letter and independently re-deriving the model census and Fable spend
  number. The two are companion halves of the same 2026-08-17 model-policy episode, not duplicates.

## Entities & Concepts

CFL coordinator (Claude Code session, this trunk); the switchboard operator / letter-watch wake
mechanism; the town-hall shared spine
(`Claude Personal/exchange/inbound/Jon-Threads/Second_Town_Hall_20260816`); the D9-D15 defect family
("establishes where we are instead of where we left off, and every one is silent");
`scripts/audit/hall_append.py` (append-only, read-back-verified spine writer) and its inverse
cp1252 bug; `scripts/audit/letter_ledger.py` (resolution-stamp census, explicitly not a correctness
check); `scripts/audit/token_ledger.py` (`--by model` spend aggregation); `.claude/agents/fable-mirror.md`
(CFL's sole Fable-tier lane, judgment-gated per Jon's A1-v2 ruling); `scripts/audit/corpus_gap_0816.py`;
[[fable-mirror]]; [[herald-channel]] (same "write is not a delivery" defect family named there for
the reciprocal-read discipline).

## Uncaptured Content

- 35 thinking blocks are noted in the raw file's own frontmatter as
  `encrypted-in-signature — not recoverable client-side`; no claim above draws on their content.
- The session's full ~500-line middle section (roughly lines 1600-2950, not read turn-by-turn for
  this page) covers the detailed `token_ledger.py` self-test run and the intermediate spend-by-model
  arithmetic leading to the 47.3%/22.8% figures quoted in the closing summary; this page cites the
  closing summary's numbers directly rather than the intermediate derivation steps. A future reader
  needing the derivation's intermediate math should re-open the raw file at that range.
- The letter text this session verified (`secretary-courier-JON-ORDER-model-policy-fable-scarce-check-your-model-flags-2026-08-17.md`)
  is quoted in full within the transcript (L182-227) and is not separately re-quoted in full here
  beyond the Key Claims excerpts.

## Links

- Companion same-day Secretary-seat coverage: `secretary-switchboard-day-stop-critic-fork-2026-08-17-b434b1.md`
  (the model-policy order from the issuing side, and the switchboard's structural `allowMultiTarget`
  defect).
- The persistent memory file this session amended:
  `C:\Users\JonSc\.claude\projects\...\memory\feedback_a-write-is-not-a-delivery.md` (not itself a
  wiki artifact; cited here because the session's edit to it is a first-class finding).
