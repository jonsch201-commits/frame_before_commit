---
title: "The De-PII Deriver — Derived Branch Prototype"
aliases: ["de-PII deriver", "de-PII", "depii_derive", "the de-PII branch", "the derived branch", "PII scrubber prototype", "content class deriver"]
kind: concept
trunk: fl
branch: [cfl]
sub_branch: [privacy]
branch_reason: "R-CONCEPTS; promoted 2026-08-23 from 16 days of frozen tracker material per Jon's 'forcing a wiki update' directive"
type: concept
first_seen: scripts/lanes/derive_depii_branch.sh
source_count: 2
last_updated: 2026-08-23
maintained_by: wiki-master (proposal, this promotion pass — unratified)
---

# The De-PII Deriver

**Purpose:** M-20, the prototype Jon's bright-line PII ruling is conditioned on (CFL-D-015, his
words: *"i do NOT rule it until I can actually see the fork/branch whatever of it with this rule
so that i can verify the context that would be needed is in that and that you can still have the
context yuou need!"*). It walks a source tree and classifies every file into
**KEEP / STRIP / SUMMARIZE / WITHHOLD**, producing a derived, off-Drive directory — not yet a
committed branch, not pushed, not merged.

Code: `scripts/lanes/derive_depii_branch.sh`, `scripts/audit/depii_derive.py`,
`scripts/audit/depii_lexicon.py`, `scripts/audit/depii_gazetteer.txt` (4 entries as of the last
measured run), `scripts/audit/depii_probe_reach.py` (both-directions test), and
`scripts/audit/depii_path_canary.py` (added 2026-08-23, P2-6).

## Measured run against HEAD (2026-08-23, `wiki/tracker/SEAL-depii-branch-2026-08-23.md`)

| | |
|---|---|
| source files | 2,752 |
| KEEP / STRIP / SUMMARIZE / WITHHOLD | 548 / 1,804 / 283 / 117 |
| bytes retained | 37,374,652 → 33,737,747 (90.3%) |
| files with a redacted span | 157 |
| spans redacted | NAME 738 · CARD 49 · EMAIL 16 · PHONE 3 |
| independent output re-scan | 2,327 files, 0 violations |

## Filename recall is ~79%; content recall is UNMEASURED

A **path-leak defect** (P2-6, 2026-08-23) found that the earlier re-scan checked file *content*
and never file *paths* — so nine derived filenames still carried names on disk after the "0
violations" content re-scan passed. Fixed by adding `scan_path`/`safe_component`, hashing dirty
filename components as `dp-<12 hex of SHA-256(salt + component)>` (a hash because a slug derived
from the original leaks by construction; per-component so clean parent directories and tree shape
survive; salted because an unsalted hash of a short guessable filename is reversible by
dictionary attack).

**This is the first time recall was measured at all, for paths:** 11 of 14 seeded cases caught =
**79%**. All three misses are one class — a human name absent from the 4-entry gazetteer — which
is the same limit found at content level (below). **Content recall was never measured by anything
this deriver has run**, because P2-6 touched only path-scanning, not the redactor itself. The
honest state is: *filename recall measured once, 79%; content recall unmeasured — not high, not
low, unknown* (`exchange/ROUTING-LEDGER.md`, P2-6 row).

## The architectural limit: the checker shares detection rules with the redactor

The "independent" output re-scan is independent in **mechanism** (it re-reads written files and
walks the output directory) but not in **detection rules** — it imports the same
`depii_lexicon` the redactor uses. So a name absent from the gazetteer is invisible to **both** the
redactor and the check that certifies it. "RE-SCAN PASS — 0 spans survived" means *zero spans this
lexicon can see*, which is a much weaker claim than it reads with a 4-entry gazetteer. Soul's own
measurement is the proof: L1 regex caught **0 of 10** human names. A third party named once
anywhere in 2,752 files currently passes every gate green.

## Three defects found and reported, not fixed (redaction-rule changes risk creating a leak)

1. **283 stubs carry byte-identical boilerplate**, which *increases* corpus-wide string frequency
   by being withheld — `2026-07-25` went from 406 files in source to **695** in derived, because
   283 stubs each recite the ruling date. Fix identified: move the boilerplate to one
   `DEPII-STUBS.md` the stubs link to. Not applied.
2. **161 of 170 stubs state a false reason.** `title_of()` returns `""` for any non-`.md` file
   (deliberate — `# ` is a code comment in Python), and the stub prints "(withheld — title carried
   a name)" whenever the title is falsy. Only 9 of the 170 stubs printing that line actually have a
   `.md` source; 161 are misdescribing their own reason for existing.
3. **CARD is ~96% false-positive at full-tree scale, and it corrupts the derived tree.** Soul
   measured CARD 35→0 on a 120-file sample; at 2,752 files it reappears: 79 Luhn-passing spans, 40
   embedded inside a longer hex token (git SHAs, UUIDs, zip filenames) and 39 standalone. Real
   cards are 15/16 digits; at most 3 of 79 have card shape. The redactor rewrites the **middle of
   git SHAs** in the published tree (`sha: "62a[REDACTED:CARD]a6214e…"`). Narrow fix identified
   (reject a candidate whose adjacent character is `[0-9A-Fa-f]`) — not applied, because a
   redaction-rule change is the direction that can create a leak.

## The "what did we decide" vs. "how does it work" split

A both-directions term-presence test (`depii_probe_reach.py`) over the real probe registry queries
found **0 of 22 needle terms lost** — and that measure is itself the finding, because it is
misleadingly reassuring: `scripts/` is classified SUMMARIZE and retains **3.0% of its bytes**
(156 files → 156 stubs, 3,093,781 B → 91,309 B); `.claude/` retains 7.0%. The *words* survive
because the wiki discusses the tools constantly; the tools themselves do not. This directly
contradicts Jon's 2026-08-20 tool-itself-retrievable ruling — a retrieval hit for
`scripts/lanes/mirror_resident_volumes.sh` (3,421 B at source) returns a 591 B stub. **The branch
answers "what did we decide" well and "how does it work" badly.**

## Other stated limits (not built)

No stale-source gate on the deriver itself (defaults to `main`, which was 108 commits / 6 days
behind HEAD on the run that mattered — fixed by explicit `DEPII_SOURCE=HEAD`, but the gate itself
is not built). No L2 (ollama-based contextual) detection layer — only L1 (regex + gazetteer) is
built. No canary harness with seeded ground truth. Produces a directory, not a git branch (no ref,
no orphan commit, no push path). Not wired to any ritual.

## The carve-outs that do NOT move with the 2026-08-19 reachability amendment

Restated per the amendment's own requirement: **third-party consent** (a promise to other people),
**the family-member rule** (they did not consent), and **money identifiers** (fraud exposure).
None rests on a PII-preference-of-Jon's basis, so the loosening does not reach them.

## See also

- [[graphrag-retrieval]] — walks the same corpus this deriver classifies.
- [[disposition-and-delivered-is-not-received]] — the term-presence-test-hides-the-real-loss
  pattern is another instance of measuring the wrong thing and believing it.
