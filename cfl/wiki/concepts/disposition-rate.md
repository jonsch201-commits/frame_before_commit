---
title: "Disposition Rate — Delivered Is Not Received"
aliases: ["disposition rate", "delivered is not received", "a count is not a consequence", "was it acted on", "disposition_rate.py", "the 5.6% number", "the 22% number"]
kind: concept
trunk: fl
branch: [cfl]
sub_branch: [governance]
branch_reason: "R-CONCEPTS; promoted 2026-08-23 from 16 days of frozen tracker material per Jon's 'forcing a wiki update' directive"
type: concept
first_seen: scripts/audit/disposition_rate.py
source_count: 1
last_updated: 2026-08-23
maintained_by: wiki-master (proposal, this promotion pass — unratified)
---

# Disposition Rate — "Delivered Is Not Received"

**The instrument this project had never built:** everything in `scripts/audit/` answers "did the
thing get produced" — was the letter written, did the probe run, did the agent return. **Not one
of them asked whether anybody then did anything about it.** A checker that fires correctly, writes
a true finding, and is ignored forever reports as healthy from the producing side.

## The frame, verbatim from the tool's own docstring

The framing came from a Hank Green transcript Jon supplied, on a Merck/Moderna phase-3 melanoma
readout: eight of sixteen pancreatic-cancer patients "did not mount an immune response at all to
the vaccine. So their body just kind of didn't notice it existed." The vaccine was delivered. It
was not received. **Measuring doses administered would have called that trial a success.**

> DELIVERED IS NOT RECEIVED.
> A FINDING NOBODY DISPOSITIONS IS A FINDING THAT WAS NEVER MADE.

A disposition is a **durable mark** saying what happened — routed, resolved, declined-with-reason,
ticketed-with-an-owner — not "somebody read it." The tool is deliberately generous (any of several
markers counts); if the generous count is still bad, the strict count is worse.

## ⛔ The number itself was corrected within an hour of being published — read this before quoting either figure

**First published figure (`exchange/COMPACT-HANDOFF-2026-08-23-1520.md:44`): "Disposition rate
5.6% overall, 3.1% on agent returns."** The tool's own docstring records a same-day, same-author
self-correction:

> "I published '3.1% disposition rate on agent returns' and called it the most important number in
> the program. It is LITERALLY TRUE AND IT INSTALLS A FALSE BELIEF — which is precisely the defect
> class Jon handed us the same afternoon ('a truth sentence that puts a huge lie into people's
> heads'), committed by me, on my own flagship measurement, in the tool built to detect the family
> it belongs to."

**Why the 3.1%/agent-returns figure is misleading, not false:** its denominator (2,257+ rows in
`exchange/ROUTING-LEDGER.md`) is written automatically, one row per subagent return, **including
every lint check, extractor, and mechanical parse whose whole value was consumed inside the
session that spawned it.** The tool was measuring "what fraction of agent runs produced a
durably-cited artifact," not "what fraction of findings did anyone act on" — and a clean lint
check that nobody re-cites has still been fully received. Counting it as an ignored finding is the
same category error as counting a delivered letter as a lost one. **This surface is now excluded
from the headline** and reported only as a labelled citation rate.

## The measure this program should quote — re-run live 2026-08-23, this promotion pass

```
$ python scripts/audit/disposition_rate.py
```

| surface | total | disposed | rate |
|---|---|---|---|
| agent runs CITED (ROUTING-LEDGER) — **excluded from headline, citation rate only** | 2,281 | 69 | 3.0% |
| peer letters (`exchange/inbound`) | 355 | 77 | 21.7% |
| findings (`wiki/intake-triage/FINDING-*.md`) | 4 | 2 | 50.0% |

**HEADLINE: 79/359 = 22.0% of ADDRESSED findings carry a disposition.** Worst surface: peer
letters at 21.7% — the delivered-is-not-received defect, measured rather than argued. **This
number moved between the compact-handoff figure (5.6%) and this run (22.0%) because the earlier
figure summed a surface that has since been correctly excluded — not because health improved.**
The tool is an upper bound either way: a row marked ROUTED whose pointer names nothing still
counts as dispositioned here.

## Fixtures the tool cites as its own evidence, all measured the same day

- Five critic fires wrote correct findings and sat undispositioned for six days.
- 14 of 65 letters written since 08-15 reached zero copies of at least one addressee.
- 43 letters stranded in a retired trunk, eleven addressed to a seat by name.
- 18 Herald letters read as UNREAD that had in fact been absorbed — acting without stamping is
  indistinguishable from never reading, in **both** directions.
- A granted Jon approval sat unused for twelve days: read, summarized, never dispositioned.

## Why this is the parent defect class, not just one number

See [[disposition-and-delivered-is-not-received]] for the general pattern this instrument names —
a finding, a memory record, and a retrieval hit are all "delivered" the moment they exist as a
file, and every one of them can still fail to be received. The unsaid-ledger validator
([[unsaid-ledger]]), the PROBE-REGRESSIONS miscount ([[probe-registry]]), and this tool's own
first published number are three separate instances of the same shape: an artifact existed, was
counted, and the count was mistaken for the outcome.

## See also

- [[unsaid-ledger]] — a validator present but not wired, so a count of files mistook itself for a
  count of filled records.
- [[probe-registry]] — an append-only log whose naive count over it produced a false alarm.
- [[disposition-and-delivered-is-not-received]] — the named parent class.
