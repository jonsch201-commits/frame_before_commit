---
name: counts-that-measure-the-detector
description: "Three seats audited the same defect on one evening and every published count shrank toward zero as the rule improved — 29 to 8 to no-trustworthy-count, 29 to 15 to 8 to 0, and 72 to 7 to 1. The totals were measuring the detector's immaturity, not the defect's prevalence. The enumeration survived every rule change that killed the totals built on it."
kind: concept
created: 2026-08-24
sensitivity: routine
calibration: this trunk's row (72 → 7 → 1) is [measured] here 2026-08-24. The Herald and Secretary rows are [relayed+] from the Secretary's own tabulation of the evening; their underlying runs were not opened by this seat.
---

# A count published before its detector is mature measures the detector

⛔ **THE MEASUREMENT.** Three seats audited one defect class — emphasis added inside a verbatim
quote — on the evening of 2026-08-24, independently.

| seat | counts published, in order |
|---|---|
| Herald | 29 → 8 → ⛔ *"I have no trustworthy count"* |
| Secretary | 29 → 15 → 8 → **0** |
| **Professional** | **72 → 7 → 1** `[measured here]` |

⛔ **EVERY COUNT IN THE THREAD SHRANK TOWARD ZERO AS THE RULE GOT BETTER.** ⭐ **They were not
converging on the defect's prevalence. They were tracking how immature each detector still was.**

---

## What each shrink actually was

**This trunk's three numbers, and none of them was a better measurement of the same thing:**

1. **72** — the detector counted emphasis **around** a quote (`**Jon, verbatim:** *"…"*`). That is
   formatting, not modification. **A population error.**
2. **7** — the span extractor matched between two **unrelated** quote marks, so most "quotes" it
   flagged were not quotes. **An extraction error.**
3. **1** — read by hand. **The only number produced by a method that could tell the difference.**

⛔ **Each number was honestly derived, correctly stamped, and wrong. The rule improved between each
pair, and the count moved by an order of magnitude every time.**

---

## ⛔ AND THE REFINEMENT THAT MADE IT WORSE, WHICH IS THE HALF NOBODY EXPECTS

`[m]` **A strictly better rule was then added — *an emphasised quote is a defect only if no clean twin
exists* — and it reported SIX ORPHANS WHERE THERE ARE ZERO.** ⭐ **It classified the one real case
correctly and invented six, because a sound test on a bad extractor is garbage in, garbage out.**

> ⚠️ **A REFINEMENT THAT IMPROVES THE RULE CAN DEGRADE THE OUTPUT, AND IT LOOKS LIKE PROGRESS BECAUSE
> THE RULE GOT BETTER.**

⛔ **Sibling of the inert guard found the same day: the mechanism was right and the thing it ran on
was not.** ⚠️ **So "we improved the rule" is not evidence that the number improved, and the two are
routinely reported in one sentence.**

---

## ✅ What survived, and it is the practice this trunk already had

⭐ **THE ENUMERATION SURVIVED EVERY RULE CHANGE THAT KILLED THE TOTALS BUILT ON IT.** The Secretary's
list of instances was correct throughout while their classification was wrong three times over.

- ⛔ **Publish the ENUMERATION — file, line, span — not the total.** A list can be re-classified by
  the next rule. A total cannot; it can only be retracted.
- ⛔ **A count is safe to publish only once its detector has been proven failable in BOTH directions**
  — a one-directional fixture cannot show its guard discriminates.
- ⭐ **Where a claim's force does not depend on the magnitude, publish the DIRECTION and the CLASS,
  not the COUNT.** The same evening produced `228 → 208 → 16 → 11 → 4 → 0` on an unrelated question
  across four trunks, **every figure too large in the direction its author was arguing, AND THE
  SENTENCE NEVER MOVED.** `[relayed+]`
- ✅ **State the collapse as a column.** `scripts/last_exercised.py --mutate` and its `collapse`
  column exist so that the gap between a raw count and a filtered one can never again be invisible.

⚠️ **BOUND.** `n = 3` seats on ONE defect class in ONE evening, and two of the three rows are
`[relayed+]`. ⛔ **The pattern may be a property of a fleet auditing itself under time pressure rather
than a property of counting.** ⭐ **The falsifier is cheap and nobody has run it: a defect class where
the count GREW as the detector matured. This page should be revisited the first time that happens.**
