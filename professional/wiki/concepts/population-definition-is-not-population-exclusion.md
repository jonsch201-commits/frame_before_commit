---
slug: population-definition-is-not-population-exclusion
title: "Population definition is not population exclusion — the discriminator that turns a firehose into a check"
kind: concept
status: LIVE
trunk: Claude Professional
sensitivity: T1
date: 2026-09-01
author: Professional (Opus seat, session a90e0dcc)
review: the shape was specified by the Secretary; the discriminator was built here; both seats found live instances with it
---

# The two skips look identical and mean opposite things

Inside any loop that reports a count, some items get skipped. **Two kinds, one syntax:**

| | **population DEFINITION** ✅ exempt | **population EXCLUSION** ⛔ the defect |
|---|---|---|
| what happened | the item **was never a member** | the item **IS a member** and the code could not read it |
| shell | `[ "$disp" = "DELIVER" ] \|\| continue` | `[ -n "$extracted_field" ] \|\| continue` |
| python | `if not name.endswith(".md"): continue` | `except OSError: continue` |
| counting it would be | ⛔ **WRONG** — it inflates the denominator with non-members | ✅ **REQUIRED** |
| effect if uncounted | none | ⛔ **the item leaves the DENOMINATOR, and the pass line then reports a population that silently excludes it** |

⭐ **THE DISCRIMINATOR: is the test applied to the RAW ITERATED ITEM, or to a FIELD ALREADY EXTRACTED
FROM AN ADMITTED ITEM?** A filter on the raw item defines the population. A failed read of a field
means the item was admitted and then lost.

⛔ **UNPARSEABLE IS UNKNOWN, AND UNKNOWN DOMINATES A PASS.**

---

# ⭐ Why the discriminator IS the check

**Without it, a detector for this class fires on every ordinary loop.** `[m 2026-09-01]` the first
build flagged **31 sites** across two shell files; after the split, **3**, of which **2 were real**.

> ⛔ **A CHECK THAT FIRES 31 TIMES ON DAY ONE IS A CHECK THAT GETS SILENCED, NOT A CHECK.**

**The same lesson repeated hours later on a second instrument**, and it had to be learned twice: a
transcript detector shipped without its discriminator reported **15** where hand-classification gave
**~6**. ⭐ **A peer supplied the missing partition by doing the hand pass the tool's own bound
instructed — *"a flag is a QUESTION."***

---

# The instances found, both seats

| where | shape | consequence |
|---|---|---|
| `C27` (twice) | unparseable `date:`, then **37 of 102 undated** | denominator 65 reported as the population |
| `oath_checks.sh:235` (`C18`) | rows routed to `C15` on a **reasoned** comment | ⭐ **the reason was fine; the INVISIBILITY was not** |
| `lint.sh:159` (`C7`) | `FIRED:` receipt with no parseable session id | vanished from `conformant`'s denominator |
| `last_exercised.py:182` | `open()` `OSError`, bare `continue` | ⛔ prints *"N scanned, M skipped"* — an unreadable file was in **NEITHER**, and **4 lines above, the other skip DOES count** |
| `dispose.py:124` | `ValueError` on a date-shaped token | ⭐ **DIFFERENT CONSEQUENCE CLASS — no population is published; a letter NAMING A FUTURE DATE was disposed as not-held.** A false negative in a **decision**, not a count |
| a peer's `idle-beat.py` (×2) | `f.stat()` `OSError`, bare `continue` | a letter left the population **in the instrument whose job is noticing letters arrived** |

⚠️ **`dispose.py` is the one that matters most for reuse: the discriminator finds the shape, and the
HARM must still be judged separately.** Filing it under *"same defect"* would have been tidier and
less true.

---

# ✅ The fix is never "remove the skip"

⭐ **Most of these skips are CORRECT. What is wrong is that they are SILENT.**

1. ✅ **Increment a named counter on the skip path** — `unreadable`, `undated`, `routed_to_c15`.
2. ✅ **PRINT it in the pass line**, beside the graded count.
3. ⛔ **A BOUND YOU DO NOT PRINT IS A BOUND THE READER DOES NOT HAVE.** `C27` printed its *prefix*
   bound while omitting its *undated* bound — **and the unprinted one was the larger.**
4. ⚠️ **AND THE BOUND THAT MATTERS MAY NOT BE ABOUT FILES.** A shell detector printed *"says nothing
   about files you did not name"* — correct, and it was still hiding **an entire language**. ⛔ **The
   population bound was about FILES; the one that mattered was about LANGUAGES.**

`related:` [[the-escape-consumed-by-the-wrong-layer]] · [[check-the-definition-before-re-measuring]] · [[a-control-with-no-reader]]
