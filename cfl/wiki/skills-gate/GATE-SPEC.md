---
kind: skills-gate/spec
status: PROTOTYPE (Jon, 2026-08-31 ~23:2x: "prototype our implementation. All trunks are
  proposors to CFL Gate. Key to PR3... you'll need to review skill requests from your Co
  trunks for standardization and customization")
grounding: arXiv 2608.27454 (WikiSkill, Google Research) — mechanism verified by a lane
  that read the paper at source, 2026-08-31; report in session 9041f3b0's task record
---

# The CFL Skills Gate — all trunks propose, CFL validates, the ledger keeps everything

WikiSkill's loop, mapped onto rails this fleet already runs. What the paper adds that we
lacked: a GATE with a strict-improvement rule, full revert, and an append-only
proposal ledger consulted by later proposers ("skill-impact.md" — ablation shows the loop
collapses without it). What we add that the paper lacks: verbatim primaries, cross-trunk
provenance, and a no-deletion rule the ledger inherits.

## Proposal format (any trunk → CFL exchange/inbound/, kind: skill-proposal)

1. **Atomic** — one skill per proposal (paper: "an atomic proposal targeting a single skill").
2. **Diff-shaped** — create, or patch (append / replace-span / insert). Never a rewrite of
   an unread file.
3. **PURPOSE mapping** — names the motivating wiki pattern / measured failure (the paper's
   PURPOSE.md; our equivalent: the `[measured]` row or letter that motivated it). A proposal
   with no motivating record is returned unread.
4. **Validation probe attached** — a runnable check, or a sealed cold-reader question with
   expected answers, that the CURRENT skill version fails or ties and the proposed version
   passes. No probe, no gate run (an ungateable proposal is an opinion).
5. **Tier stated** — which model tier authored and which tiers it was validated on. The
   paper measured NEGATIVE transfer (a 4B-evolved skill crashed a stronger model's score
   50.5→18.1): a skill validated only at fable-tier may damage a haiku lane. Standardize
   the format; customize per tier; never assume upward or downward transfer.

## Gate procedure (CFL, on receipt)

1. Run the probe against the CURRENT skill → record baseline.
2. Apply the diff in a scratch copy, run the probe again → record.
3. **Strict improvement retains; anything else fully reverts** (paper rule: accept only if
   score > best-so-far; R_best starts at the no-skill baseline). Ties revert.
4. **Either way, append to LEDGER.md**: id, from-trunk, target, diff pointer, probe results
   both sides, verdict, one-line why. A REJECTED row is feedstock, not failure — later
   proposers read the ledger to avoid repeating failed modifications.
5. Deployed-copy discipline: an ACCEPTED change to `~/.claude/skills/*` also lands in the
   repo counterpart or it becomes a ghost (the sync-divergence class, measured 08-07: 21h).

## Two paper warnings carried as fences

- **Do not hand working agents the whole wiki** — the paper measured it HURTS (63.7→60.9).
  Agents get skills + targeted retrieval; the wiki feeds the PROPOSER, not the inference
  path. (Convergent with the map-as-index / token-economy ruling.)
- **No automated pruning exists** — the ledger only grows; that is correct here (no-deletion)
  but budget for reading cost: the gate reads the ledger's INDEX, zooms rows on demand.

## What this is not (yet)

A benchmark suite. The paper gates on held-out task splits; CFL's validation probes are
E4-style sealed cold-reader panels and runnable selftests until PR-3's eval spine matures.
That substitution is stated, not hidden: our probes measure legibility-to-a-fresh-reader
and mechanical correctness, not task success rates.

## Rule 6 — the disposition travels to the proposer (Soul M-2, adopted 2026-09-01)

Every TERMINAL disposition (ACCEPTED / REJECTED / RETURNED-UNREAD) writes a receipt FILE
into the proposing trunk's `exchange/inbound/`, byte-verified — a file, not a notification,
because a file is the only channel this fleet has demonstrated end to end. A decline that
lands only in this ledger is, from the proposer's chair, indistinguishable from a proposal
never received — which is the exact finding this gate accepted as PROP-001, found live in
the gate's own decline path by its supplier ("the skill you gated IN is my finding about
this class, and the gate's own decline path still has it"). Backfilled same day for
PROP-001/002/003 via the gate-announcement letter.

## Rule 7 — the gate announces itself (Soul M-1, adopted 2026-09-01)

A gate whose proposers do not know they are proposers has exactly one supplier — the trunk
that built it; the ledger then "looks like a working market with one seller." The gate is
announced to every trunk as an offer, with the proposal format, at adoption and whenever
the format changes. First announcement: 2026-09-01.

## Rule 8 (2026-09-02): numeric strict improvement, or the row is prose

Gate procedure step 3 has said "strict improvement retains; anything else fully reverts"
since the spec was written, and every ACCEPTED row to date discharges it with the sentence
**Strict improvement: yes**. That sentence is a judgment, not a measurement, and the spec's
own "What this is not (yet)" section says so: *"A benchmark suite. The paper gates on
held-out task splits."* A gate whose acceptance criterion cannot be recomputed by a later
reader is a gate that accepts whatever its author already believed.

**From 2026-09-02, an ACCEPTED row carries two numbers and the seal they were scored under:**

    R_before=<x>@<split sha8>   R_after=<y>@<split sha8>   with y > x

- `R` is produced by `scripts/audit/skills_validation.py` over the skill's **held-out**
  split at `wiki/skills-gate/validation/<skill>/split.jsonl`. R = passed properties /
  (passed + failed). Cold-reader properties are UNKNOWN and are **excluded from the
  denominator** — ⛔ **UNKNOWN never rounds to PASS**; `--merge-cold` folds a cold lane's
  verdicts in and the combined R is reported as its own number.
- `<split sha8>` is the first 8 chars of `wiki/skills-gate/validation/<skill>/heldout.sha256`,
  sealed BEFORE the run (CFL-D-012, the PROBE-REGISTRY discipline). A row citing a hash that
  no longer matches was scored on a split that moved, and fails.
- **A tie reverts**, exactly as gate procedure step 3 already says. `y > x`, never `y >= x`.
- ⛔ **The split is never handed to an editing lane** (`validation/<skill>/README.md`). A
  proposer who can read the split optimises the checker and the number stops meaning anything.

**Checked mechanically by `scripts/audit/skills_gate_check.py` check G6**, whose `--selftest`
exercises four branches: a planted prose-only ACCEPTED row (fails), a numeric row citing the
live seal (passes), a tie (fails), and a stale split hash (fails).

**Applies from 2026-09-02 forward and is NOT retroactive.** PROP-001/002/003 were gated
before any split existed; back-filling numbers onto them would be a fabricated measurement,
and the no-deletion rule means the honest record of a prose-era row is the row itself.

**Two bounds, stated rather than discovered later.** (1) A skill whose split it already
saturates cannot produce `y > x` — the first exchange-letters baseline scored **R_best = 1.0**
at opus tier, so G6 blocks every exchange-letters proposal until the split gains rows the
current text fails. That is the rule working: an unfalsifiable improvement claim is refused.
(2) R is **tier-bound**. Scoring `R_before` with one tier's reader and `R_after` with
another's is the negative-transfer trap the adoption page fences off — *never score a
fable-authored skill with a haiku reader as if that were the consumer*. The tier goes in the
row beside the numbers.
