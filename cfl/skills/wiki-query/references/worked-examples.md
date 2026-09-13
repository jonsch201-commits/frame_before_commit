---
kind: skill-reference
skill: wiki-query
slug: wiki-query-worked-examples
status: LIVE
date: 2026-09-12
---

# Seven worked examples, all from one evening, all measured

**Every case below is from 2026-09-12 in the CFL trunk.** None is invented. Four are failures of this
skill, which is why they are worth more than the successes: **the failure mode is never "the query
returned nothing" — it is "the query returned nothing and I believed it."**

---

## 1. A query that returned a GAP, and the gap was the answer

**Question:** which third skill does Jon's draft post name?
**Query:** the phrase from the post, across `~/.claude/history.jsonl`, every `ASK-JON-ARRIVAL` copy,
the peer trunk's capture, and the 131-file paste cache.
**Returned:** the name sits inside a **489-byte truncation identical in every copy**, and `0` hits in
typed prompts — he pasted the post, he did not type it.

A peer had already defaulted to a plausible answer. ⭐ **The query's value was not an answer; it was
converting a guess into a known gap that one cheap question could close.** Jon answered it himself
two hours later (`history.jsonl:5068`) and the guess happened to be right — **which does not make
guessing right.** The artifact would have shipped a claim nobody could trace.

**Lesson: a query that finds a truncation has succeeded. Report the gap, do not fill it.**

---

## 2. Four wrong guesses and one measurement, in that order

**Question:** why is the index's term phase slow?
**Guesses, in order:** the corpus is too big · the query shape is wrong · batch the lookups (built,
measured SLOWER at three corpus sizes, reverted) · prune old files from the graph.
**The measurement:** a missing covering index. `postings(term)` forced a table-row visit per posting to
read `chunk_id`. Declaring `postings(term, chunk_id)` — **18.9 s and +486 MB** — took the phase from
**20.3 ms/term to 0.117 ms/term (174x)** and the oracle query from **104.0 s to 2.8 s**.

⛔ **The fourth guess had already been given to Jon as advice, more than once.** It would have deleted
part of his record to fix a missing index.

**Lesson: when a plan involves removing data, the query to run first is "what does the instrument
measure when I change nothing else?"**

---

## 3. A not-found that was a claim about the instrument, three times in one night

| the claim | the reality |
|---|---|
| "6,279 indexed files are GONE (32.6%)" | 6,148 were alive on another disk; a mirror root had never been populated |
| "`~/.claude/CLAUDE.md` is on no disk this machine can see" | it exists; `os.path.isfile` does not expand `~` and the resolver had no tilde arm |
| "no wiki page links to anything" (83% unreachable) | the link convention was backticked paths, and the guard stripped inline backticks |

⭐ **All three were produced by careful code, and all three were caught by reading the output rather
than the exit code.** The third had a second tell the first lacked: a `recovered_fraction` of **1.089**,
and a reconstruction cannot be larger than its original.

**Lesson: A NOT-FOUND IS A CLAIM ABOUT WHERE YOU LOOKED. Resolve against every known root, expand the
path, and treat an impossible number as a bug in the measurer.**

---

## 4. The corrections were in the record and nobody queried for them

**Question Jon had to ask:** *"No wonder you've been wrong about my PII preferences so many times. I
kept correcting you, and you never fixed the claude.md. Query your history for context."*
**The query he ordered, run:** his typed prompts for PII, scrub, public/private repo.
**Returned:** **seven corrections** over ten days — `history.jsonl:3259, :3655, :3725, :3752, :3819,
:4262, :4470` — none of which had reached the file that states the rule. One of them says outright
*"You should have learned that multiple times by now, do better."*

The constitution meanwhile carried a heading that fenced a **private** repo on every commit, because
his oldest, narrowest-context ruling had become the title while two later ones that narrow it sat
underneath as commentary.

**Lesson: when someone says they have told you before, query for the telling before rewriting the rule
from memory. And when a rule has several rulings, the NEWEST governs and belongs in the heading.**

---

## 5. The query that found test data for the wrong thing

**Question:** does the tree carry "3 skills and their test data", as the post promises?
**Query:** `ls wiki/skills-gate/validation/`, then grep each named skill across it.
**Returned:** **37 files in five directories — `dream`, `exchange-letters`, `su-compact`, `wake`,
`wayfinder` — and `0` files naming any skill the post names.**

⭐ **A directory called `validation/` existing is not evidence that a thing is validated.** The check
that mattered was one grep past the directory name.

**Lesson: verify the CONTENT matches the CLAIM, not that a container with the right name exists.**

---

## 6. A spec row that would have read as coverage and delivered nothing

**About to write:** `PREFIX_UNDER skills/ references/` into a derivation spec.
**Query first:** `grep INCLUDE_SPEC_KEYS derive_public_tree.py`.
**Returned:** exactly four valid keys, and `PREFIX_UNDER` is not one. **The deriver would have ignored
the row silently** — no error, no warning, and a spec that reads as though the files ship.

**Lesson: before adding a row to any config, query the consumer for its accepted vocabulary. A silent
ignore is the most expensive failure a config can have.**

---

## 7. When NOT to query, because this skill's worst failure is pretending it is universal

`[measured 2026-09-12]` two of the evening's best findings could not have come from a query:

- **The index reported a third of itself missing.** No query surfaces that; a per-file `isfile()` sweep
  did. **A query returns what the corpus SAYS, never what the filesystem IS.**
- **A constitution's four stale numbers.** The file asserted them confidently; only re-measuring each
  against disk found them. **A query cannot tell you that a confident claim is out of date, because the
  claim is what it retrieves.**

⛔ **And the deepest limit: a query returns what was already said, in the vocabulary already used. It is
at its worst exactly when the FRAMING is the defect.** Both of the evening's best findings were
vocabulary defects — "dead path" for "moved root", "no writing PII to GitHub" for "not to a *public*
repo". **No amount of querying those terms would have produced the right term.**

**Lesson: query before you build, and measure before you believe the query. They are different acts and
this skill is only the first one.**
