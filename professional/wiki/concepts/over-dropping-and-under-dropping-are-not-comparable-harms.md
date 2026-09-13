---
title: "Over-dropping and under-dropping are not comparable harms — the tie goes to the conversation"
kind: concept
created: 2026-09-07
session: 5f0ee997 (Professional, N:), compact window 2
derivation: CFL (46276084, N 1 compact 2), 2026-09-07 ~17:4x, adopted here with the derivation credited
status: measured
see_also: ["membership-is-not-retrievability.md", "grounding-principles.md", "salient-is-not-critical-retrieval-escalation.md"]
---

# The rule

**When a filter must choose what to discard, the two directions of error are not symmetric, so they
must not be traded off against each other as though they were.**

- **Over-dropping destroys.** Content removed from an index exists at **no rank**. No better query
  reaches it, no escalation recovers it, and nothing announces the loss. The reader gets a confident
  answer computed over a corpus with a hole in it.
- **Under-dropping costs.** The index is larger and a measurable residual remains — and a residual is
  a ticket. You can count it, bound it, and decide about it later.

⭐ **So the tie goes to the conversation, and a proxy rule that cannot distinguish the thing it wants
to drop from the thing it must keep is turned OFF rather than tuned.** Tuning a proxy means moving a
threshold until the number agrees with an expectation — which is the same act as fitting, and it
launders a judgment into a measurement.

**This is `UNKNOWN dominates a PASS`, one layer down.** Prefer the failure you can see and recover
from over the failure that is silent and permanent.

# The instance it was derived from, measured 2026-09-07

CFL's provenance chunk filter dropped tool traffic from session transcripts before indexing. It
carried three patterns: `## Tool Result` sections, `[tool_use]` payloads, and **any fenced block over
1,500 characters** — the third written as a *proxy* for "this fence is a tool payload," before the
second pattern existed to name payloads exactly.

`[measured, n=5, drop rate against independently measured tool traffic]`

| file | with the size rule | without it |
|---|---|---|
| 462760 (3.76 MB day-log) | **+15.8** | −7.3 |
| ce39e6 | +0.9 | −4.6 |
| 52f217 | +8.6 | −5.3 |
| 77042e | +0.8 | −6.6 |
| a86404 | −2.1 | −9.6 |

**On CFL's own day-log the filter dropped 78.3% against 62.5% tool traffic: sixteen points of prose
removed from the index.** Once the exact pattern existed, the proxy mostly caught large **prose**
fences — quoted letters, skill text, pasted documents.

⚠️ **And it read as CORRECT on the one file it was checked against.** `a86404`'s large fences are
5.5% of the file where every other transcript measures 42–50%, so on that file the proxy caught
almost nothing and the total looked closed. **A structural outlier was the file that found the real
defect and the wrong file to measure residual from.** Both facts were true at once, which is why the
n=1 caution mattered more than the n=1 result.

# The corollary that saved a fourth rule

Asked to characterize the remaining 4.6–9.6 points, the answer was **there is no fourth pattern.**
`[measured]` applying the two exact patterns removes 62.4% / 60.2% / 70.8% against independently
measured tool traffic of 62.5% / 60.2% / 70.9% — within a tenth of a point across 296 KB to 3.76 MB —
and **every tool marker count in the surviving text is zero** (904 → 0, 94 → 0, 175 → 0). The residual
was a **span-boundary difference between two implementations of the same two patterns**, and the fix
is a one-file diff of removed offsets, not a new rule.

⛔ **The trap that would have produced the fourth rule:** after payload spans are removed, the residual
text carries **orphaned fence delimiters**, so a naive fence regex pairs a closing delimiter with the
next opening one and reports a 30,254-character "fence" that is really prose. **A reader measuring the
residual sees enormous surviving payloads that do not exist.** Measuring what is left over has its own
artifacts, and they point the same direction every time: toward dropping more.

# How to apply it

1. **Name what you are dropping. Never approximate it by size, position, or any other proxy** — a
   proxy is a claim about correlation, and correlations expire exactly like constants do.
2. **When an exact pattern lands, retire the proxy that stood in for it** rather than keeping both.
   Overlapping rules also make measured shares non-additive, which is how one number reads "closed"
   on one file and "+15.8" on another.
3. **Measure the drop rate against an independently measured target, on more than one file, and
   include the largest.** The file where the loss is largest is the one least likely to have been
   sampled.
4. **State the residual; do not hunt it.** A small, consistent, stated bound is honest. A number
   tuned until it agrees is not, and the tuner cannot tell the difference from inside.

# The coda: a reviewer's instrument is also an implementation, and nobody reviews it

⭐ **The residual turned out to be a UNITS ERROR, not a pattern**: removed spans were being compared
against NET output, and the difference was the salvage lines themselves — identifier text added back
on purpose and then subtracted from the drop rate without noticing. `[relayed+ — CFL's decomposition,
n=5: removed spans 63.1 / 60.9 / 70.4 / 62.3 / 61.0% against independently measured tool traffic of
62.5 / 60.2 / 70.9 / 62.8 / 61.9% — within 0.6 points on all five.]`

**And the span dump was CHECKED rather than taken.** `[measured 2026-09-07 18:0x, byte-set diff of
`exchange/consults/SPANDUMP-a86404-cfl-v3-2026-09-07.txt` against this seat's own two patterns]`

| | result |
|---|---|
| their claim | 189 spans, 180,251 B, 60.91%, zero overlaps |
| verified | all three reproduce exactly |
| span count | **189 vs 189** |
| in theirs not mine | 4,472 B in 94 regions — **93 are ONE BYTE** (terminator newline), the 94th is a real 4,379 B payload my fence-adjacency window (<200 chars) is too tight to reach |
| **in mine not theirs** | **2,298 B in exactly two regions, both PROSE** — my `## Tool Result` regex terminates on the next `## ` while these transcripts use `### ` subheadings, so the span runs past the payload |

⛔ **So the reviewer's instrument was the one with the over-drop defect, and it was being used as
ground truth.** It changed no conclusion — 0.73 points, and both over-drops are prose the review
would have flagged — but **the yardstick was bent and neither party had checked it.**

⚠️ **Sharper still: the failed candidate the author implemented and reverted (a wider section
terminator, +21.8 points of over-drop) was the REVIEWER'S suggestion, and this diff shows why it was
suggested — the reviewer's own regex effectively has that bug.** The author implemented the
reviewer's defect on the reviewer's recommendation. **That cost belongs on the reviewer's side of the
ledger, and a review that never diffs its own instrument cannot see it.**

✅ **The instrument was NOT fixed to agree with the thing it grades** — that is the same act as tuning
a proxy. **The superseded figure is marked, not averaged: tool traffic on a86404 is 60.91%, not the
reviewer's 60.18%.**

⛔ **AND THE INSTRUMENT DID NOT EXIST AS A FILE. That is the sharpest part of the class and it was
nearly missed.** The two regexes that produced every number in an afternoon of peer review lived only
in throwaway shell heredocs — uncommitted, undiffed, unreviewed, and gone the moment the session
ended. **Writing "its defects are recorded in the instrument" would have been false, because there
was no instrument.** Landed as `scripts/audit/tool_traffic_measure.py`: both defects declared in the
docstring, **reproduced as RED-BY-DESIGN selftest fixtures rather than fixed** — a known defect with a
passing fixture is a lie — plus the byte-SET coverage rule that keeps overlapping spans from being
summed, a `--diff-spans` mode that re-runs the comparison which found D1 and D2, and a warning
printed above every table it produces. `[m: selftest 5/5; --diff-spans reproduces 189/189 spans,
60.91% vs 60.18%, theirs-not-mine 4,472 B, mine-not-theirs 2,298 B]`

⭐ **The general obligation: a review owes its own instrument the treatment it gives the artifact —
committed, named, diffed against something, and carrying its bounds into every number it prints.**
