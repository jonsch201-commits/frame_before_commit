---
name: derived-not-typed
description: >
  Before publishing any number, count, size, duration, status or coverage claim,
  derive it from a command in THIS run rather than restating one you typed
  earlier. Use when writing a report, a PR description, a frontmatter cost field,
  a status page, a commit message, or any letter to a peer. Also use when
  reviewing someone else's claim: ask which run produced the number, and whether
  the document has grown since. Triggers: "reader_token_cost", "coverage",
  "how many", "is that still true", "the summary says", or any figure you are
  about to copy forward.
---

# Derived, not typed

**One rule: a claim and the thing it describes must come from the same run.**

Where a number is typed rather than derived, it drifts — and nobody notices,
because summaries get checked against expectations instead of against runs.

## Why this skill exists — four failures in one week, all the same shape (and see the SIBLING RULE below, which is six more from a single afternoon)

`[CFL, week of 2026-09-02. Each was found before publishing except the last, which
Jon caught.]`

1. **A command promoted to every trunk crashed in five of six, for a month.**
   It had been tested only where it worked. Then the fix was announced *before the
   file that ships had changed* — the repo has two copies and the one that does not
   ship got fixed. **A selftest reported "ALL 9 PASSED" against a file that had been
   emptied to zero**, because its path argument defaulted to the other copy.
2. **A self-regenerating file silently deleted 59 lines of hand-written instructions,
   twice.** Recovered from git. The regenerator and the hand-edits had no shared
   record of what the file was supposed to contain.
3. **A citation checker counted 122 machine-generated dumps as real broken links.**
   Fixing the classifier moved the headline without fixing a single citation. The
   report now prints three counts and their sum so it cannot hide behind one.
4. **A coverage instrument was wrong three times in ninety minutes** — it counted the
   author's own instructions as the user's words, then counted a quote sitting in a
   dump as landed, then found its own report and called that coverage.

**And the one that proves the rule, because it happened in the document that
described the rule:** that PR's frontmatter claimed
`reader_token_cost: "~1,500 tokens (about four minutes to read)"`. Measured when
challenged: **2,358–2,607 tokens, 7–9 minutes.** The number was typed once and the
document then grew three times the same day. **The reader had five minutes.**

## The checks, in order of what they cost when skipped

**1. Derive it in this run.** If a figure appears in your output, a command in the
same run produced it. Never copy a number forward from earlier in the session, from
a previous document, or from memory. **If you cannot re-derive it now, publish it as
`[recalled, unmeasured]` — with those words.**

**2. Re-derive after every edit that changes size or scope.** A cost, a count or a
duration describing a document is invalidated by editing that document. **Growth is
the common case and it always moves the number in the direction that flatters you
least.**

**3. Name the population.** A count means nothing without its denominator and its
root. Two correct measurements of "coverage" that disagree are usually two
populations, not a conflict — say which one you measured. *(Same week: `493/876`
and `491/870` were both right; one page printed one of them with no denominator.)*

**4. Print the classes and the sum, not the headline.** If a total splits into kinds,
publish every kind and the identity. **A single number can hide a reclassification
that fixed nothing.**

**5. Check the artifact that SHIPS.** Not the copy you edited, not the one your test
defaults to. **Name the path you verified.**

**6. Sample before reporting.** An instrument's first run is a draft. Open a handful
of its rows against the source. **Three of the four failures above survived to a
report because nothing looked at the rows.**

## When reviewing someone else's number

Ask only these: **Which run produced it? Has the thing it describes changed since?
What is the denominator?** ⚠️ **A number that survives all three is still only as
good as its population — but one that fails any of them is not evidence.**

## ⛔ THE SIBLING RULE: ABSENCE OF YOUR PATTERN IS NOT ABSENCE OF THE THING

**Deriving a number protects you from a stale number. It does not protect you from a
SEARCH THAT FOUND NOTHING AND SAID SO AS THOUGH THAT SETTLED IT.** Every instance below
is a real measurement, correctly run, whose result was an artifact of the matcher rather
than a fact about the world. `[all measured 2026-09-04, one trunk, one afternoon]`

| what the instrument reported | what was true | what the matcher assumed |
|---|---|---|
| "no `## Destination` section could be read" | both maps had one, under `# Destination` and `## 1. Destination and done-test` | one heading spelling |
| "5 LIVE maps" (a peer, auditing another trunk) | 16 | `^status:\s*LIVE` — unquoted YAML. The audited trunk quotes its scalars |
| "0 of 3 sentences traced to a diff" | all three had | commit bodies wrap at 72 columns; the quote was split by a newline |
| "the queue is empty" × 3 gate firings | a lane was queued | the entry regex required an agent id, which only an already-dispatched lane has |
| "115 queue entries" | 3 | the parser was never scoped to the block its own docstring named |
| "this claim is traceable" | it was not | the evidence lived INSIDE the file being searched, so it quoted itself |

⭐ **THE COMMON SHAPE, and it is the one to carry: a matcher measured its own author.**
It recognised the idiom the person who wrote it happens to use, and everything else
became absence. **None of these failed loudly. Every one returned a clean, confident,
well-formatted result.**

### The check, and it is one line

**Before writing "there is no X," ask what your pattern would MISS, and test one instance
you believe exists.** A search that has never returned a hit has not been shown to work.

- If you match a heading, a field name, or a status value: **try the other spelling.**
  Quoted and unquoted. One hash and two. Singular and plural.
- If you search text a person wrote: **assume it wraps.** Collapse whitespace before
  comparing, and never compare whitespace-sensitively against prose.
- If your corpus contains your own output: **exclude yourself first**, or you will
  measure your own reflection and call it corroboration.
- ⚠ **A zero is a claim, and it is the claim least likely to be checked.** Nobody
  re-runs a search that found nothing, because there is nothing to look at.

## The failure mode this skill cannot catch

**A derived number can still measure the wrong object.** Deriving protects against
*drift*, never against *aiming at the wrong thing* — that needs a second reader
asking a different question, which is a different discipline and not this one.
**Say so rather than letting "I derived it" stand in for "it is right."**
