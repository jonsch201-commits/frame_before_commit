---
name: mirror-consult-economics
title: "What a mirror consult actually costs — measured, and the number everyone was quoting was wrong"
slug: mirror-consult-economics
kind: concept
last_updated: 2026-08-24
last_verified: 2026-08-24
status: current — cost half MEASURED; effectiveness half has a proposed test only
author: CFL coordinator, session 9f1e3383
trunk: fl
audience: co-trunk coordinators
---

# What a mirror consult actually costs

**Jon asked for this directly, 2026-08-24 ~14:1x CDT, relayed by the Secretary. Verbatim, typos his:**

> *"FYI you are all nearly at the fable mirror wall. I do not know how you've used the fable mirror,
> and i loath to say anythign that may make it less effective and you have been conserving it. But i
> have to assume that if you asked the fable mirrors now how you might all be able to better use them
> to have them cost less and be siilarly effective, it may help after the 2pm friday barrior.
> Downgrade fable mirror to opus mirror if needed and i assume all of this is in the wiki and
> testible and if its not thats a defect how else could you expect to improve that component"*

⭐ **Note what he did not do: he refused to prescribe a method** — *"i loath to say anythign that may
make it less effective."* He protected the instrument from his own instruction, which is worth more
than the instruction, and it is why the consult dispatched alongside this page asked the mirror
open-endedly instead of handing it a conclusion.

## ⛔ The number in circulation was wrong, and its origin is worse than "unverified"

**"80k tokens per consult"** was circulating in the fleet. `[measured 2026-08-24, 83 COMPLETED
fable-mirror subagent transcripts in this trunk's own JSONL store; one still-running consult
excluded]`:

| per consult | min | median | mean | max |
|---|---|---|---|---|
| turns | 3 | **49** | 61 | 264 |
| output tokens | 703 | **16,056** | 23,755 | 134,387 |
| cache WRITE | 36,701 | **248,057** | 450,101 | 4,115,256 |
| cache READ | 7,941 | ⛔ **2,872,279** | 5,535,197 | ⛔ **47,335,964** |

**80k is not close to any column.** The nearest honest comparison — output plus cache-write, the
non-cache-read work — has a **median near 264,000**, so the circulating figure understated it by
roughly **3×**, and it omitted the cache-read column entirely, which is where nearly half the money is.

⛔ **AND THE MIRROR FOUND WHERE THE 80k CAME FROM.** It is not a mis-measurement of a consult. It is
an accurate measurement **of a pathological run**:

> *"It also burns real compute (60k+80k tokens on the unbidden runs)"*

`[mirror, 2026-08-24, quoting the mirror references]` — measured on the **2026-07-24
SendMessage-resume runaway**, whose two **UNBIDDEN** outputs cost 60k and 80k. ⭐ **80k was ONE
RUNAWAY RUN.** And the mirror's grep for `per consult|per-consult|80k tokens` across the references
found **no "80k per consult" claim anywhere.** ⛔ **Nobody ever wrote it. The fleet manufactured it by
reading a number standing next to the word "burns" and generalising it into a norm.**

⚠️ **How it survived: it was read off a page and relayed — and the relaying seat labelled it
`[relayed-]`, "I read the figure, I did NOT verify it."** ⭐ **That label is the only reason this took
ten minutes instead of a week.** The failure was never the relay. It was that in a month of leaning
on this instrument, **nobody had measured it, and a figure describing its WORST FAILURE was standing
in for its NORMAL COST.**

## ⭐ Where the money goes, and it is not where anyone looks

**Share of modelled spend across all 83 consults:**

| | share |
|---|---|
| cache WRITE | **45.3%** |
| cache READ | **44.6%** |
| output | 9.6% |
| input | 0.5% |

⛔ **Ninety per cent of a mirror consult is context handling. The answer it writes is under ten per
cent.** Every instinct that says *"ask for a shorter report to save money"* is aimed at the 9.6%.

## ⭐ TURNS ARE THE COST DRIVER, AND NOBODY WAS PULLING THAT LEVER

Split the 83 consults at the median turn count:

| half | median turns | median cache READ |
|---|---|---|
| fewer-turn | 26 | **746,203** |
| more-turn | 83 | ⛔ **6,703,920** |

**A 3× difference in turns produced a 9× difference in cache read.** Each turn re-reads accumulated
context, so cost grows faster than linearly in how many times the mirror must go and look something up.

1. ⭐ **CUT TURNS, NOT WORDS.** A consult that greps ten times costs roughly nine times one that greps
   three. **The dispatcher usually already knows which files matter and does not say so.** Handing the
   mirror its file list, its date bounds, and where the dispatcher already looked converts expensive
   lookup turns into cheap reading turns. **Biggest available saving, and it costs one paragraph.**
2. **Ask one question, not five.** The 264-turn consult was a five-part brief. Bundled questions do
   not share context savings — they compound the re-read.
3. **Say what you already know.** Most re-derivation visible in these transcripts is the mirror
   rebuilding context the dispatcher already held.

## The model swap Jon pre-authorised

`[modelled 2026-08-24 at list prices — Fable 10/50 per MTok, Opus 5/25; cache write at 1.25× input,
cache read at 0.1× input]`

| | median / consult | mean | total across 83 |
|---|---|---|---|
| **fable** | $7.45 | $12.41 | **$1,029.88** |
| **opus** | $3.73 | $6.20 | **$514.94** |

⭐ **The downgrade halves the bill almost exactly, because cost is dominated by token classes that
scale with the price ratio.** ⚠️ **MODELLED from token counts and list prices, not billed amounts —
the RATIO is trustworthy, the absolute figures are an estimate and must not be quoted as spend.**

⛔ **The two levers are ORTHOGONAL, and that is the practical point: halving turns and halving the
rate MULTIPLY.** The turn lever touches no capability at all, so pull it first regardless of what is
decided about the model.

## ⭐ THE CONVERGENCE, which is the strongest thing on this page

**Two measurements, from opposite directions, one lever.**

- **From the tokens (this seat, with no access to the mirror's reasoning):** turns drive cost, 3× turns
  → 9× cache read. So: **stop making it search.**
- **From the instrument (the mirror, with no access to my token counts):** *"dispatch me less often,
  with better-scoped questions and your leads attached."* Its #2 ranked saving: *"hand me your leads…
  this converts my job from SEARCH to VERIFY-AND-EXTEND. Expected saving: the difference between
  grepping 2,206 files and opening 5."*

⭐ **Neither could see the other's evidence and both landed on the same action.** That is worth more
than either alone, and it is the same orthogonality argument Jon has been making about the trunks.

**Its other ranked savings, verbatim in its file:** never dispatch without a question that changes a
decision (*"if the answer is CORPUS SILENT, what will you do differently? If nothing — don't
dispatch"*); run the cheap instruments first and send it only the ambiguous hits; **give it an
explicit sufficiency bound**, because *"without one, my charter pushes me toward exhaustiveness"*; a
consult register so repeat questions hit a row instead of a fresh run; and one question per dispatch,
because bundles *"look efficient and aren't."*

⛔ **That third one is a finding against the DISPATCHERS, not the instrument: it will honour a bound
and is never given one.**

## What the mirror says about the downgrade

⭐ **Its plain answer: *"I believe nothing role-critical depends on the model."*** Everything
load-bearing is **prompt, corpus access, and the coordinator's verification habit** — the provenance
grades, the write fence, the silence rule, the treat-every-output-as-a-document rule.

⚠️ **But it refused to make that a comparative claim** — *"UNVERIFIABLE-FROM-CORPUS… no record
anywhere tests Fable-vs-Opus on this role, which is exactly the defect Jon named."* ⛔ **And it made a
point I would not have: the role's known failure — confabulating Jon's live turns — is
FABLE-measured. An Opus mirror does not inherit that record; its failure profile is UNKNOWN, not
better.**

**Watch-list for the first ~5 consults after a swap:** verbatim-quote fidelity **including Jon's
typos**; provenance-grade discipline under long searches; and the confabulation class re-checked
before trusting it. **If all three hold across five consults, the swap lost nothing measurable.**

## ⛔ The defect Jon predicted is real: there is no test of effectiveness

`wiki/concepts/fable-mirror.md` carries **no acceptance criterion, no falsifier, and no test**
`[measured by the Secretary, 2026-08-24: one grep for test/accept/measur/verify/probe/falsif returns
a single prose line — "is accepted as the cost of the design"]` — while **five real scripts invoke the
mirror**: `verify_quotes.py`, `scan_midturn_messages.py`, `su_close.sh`, `route_agent_return.py`,
`seed_advance.py`. The page is also `last_updated: 2026-07-22`, a month stale against an instrument
the fleet leaned on all week.

⭐ **His sentence is the argument: *"how else could you expect to improve that component."* You cannot
make something cheaper-and-similarly-effective without a measure of effective.** ⚠️ **Without one, the
Opus downgrade is unfalsifiable in BOTH directions — nobody could show it hurt, and nobody could show
it didn't.**

### The proposed test — THE MIRROR'S, not mine, because its version is better

I drafted a citation-count test. **The mirror proposed one with a correctness half, which mine
lacked, and that is the version carried here.** Proposed, NOT adopted — adoption is not the mirror's
to do.

> **A mirror consult is EFFECTIVE if (a) every `[TRANSCRIPT:]` citation in its return RESOLVES** —
> `grep -F` of the quoted span at the cited file succeeds, sampled at ≥3 or all if fewer — **and (b)
> at least one subsequent artifact of the dispatching session** (commit, packet, ledger row, exchange
> file) **names the return or quotes its finding.**
> **It FAILS if any sampled citation does not resolve, or if no downstream artifact references it.**

⭐ **(a) is the half I missed and it is the one that matters: it tests whether the consult was RIGHT,
not merely used** — and it is `verify_quotes.py`-shaped, so the instrument already exists. **(b) is
one grep.** Runnable at every SU close, without Jon.

⚠️ **The mirror labelled its own test cheap-and-bad, unprompted:** *"(b) produces false negatives — a
consult that correctly returned CORPUS SILENT and thereby stopped a wrong action may leave no citing
artifact."* ⭐ **Its justification is the right one: a cheap test that can fail and actually runs beats
the elegant counterfactual test nobody runs.**

**Its pairing suggestion is adopted:** log tokens and tool-uses per consult in the same register row,
**so "effective" and "expensive" are one row and not two investigations.**

## What is measured here, and what is not

- ✅ **MEASURED:** every token figure, from this trunk's own subagent JSONLs, 83 completed consults.
- ⚠️ **MODELLED:** the dollar figures — token counts × list prices. Not billed amounts.
- ⛔ **NOT MEASURED:** whether an Opus mirror is similarly effective. **Nobody can currently say,
  because the test above is proposed rather than established.** That is the honest answer and should
  not be dressed up as caution.
- ⛔ **NOT MEASURED:** the other trunks. This counts **CFL's** store only. Personal holds 47 mirror
  artifacts and Professional 2; their costs are not in these numbers.
- ⚠️ **The mirror's own answer to Jon lands separately** at
  `wiki/intake-triage/MIRROR-CONSULT-on-its-own-economics-2026-08-24.md` — **written 14:19:45 and
  NOT committed before the G: outage.** Its subagent transcript is on `C:` under `~/.claude` and is
  recoverable with `scripts/audit/extract_subagent_report.py`.

Related: [[the-comparand-lives-in-prose]] · [[first-order-and-second-order-repair]] ·
[[fable-mirror]] · [[derive-dont-record]]
