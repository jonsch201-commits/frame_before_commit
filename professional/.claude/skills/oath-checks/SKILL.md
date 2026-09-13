---
name: oath-checks
description: Runs the nine breach-condition checks that this fleet's oaths are wired to — self-application on the letter surface, dead-man's-switch freshness, the graded population of delivered findings, the swearing gate over an oath register, provenance on Jon's review surface, and whether the corpus and index this trunk's retrieval actually reads still contain this trunk's own work. Every check is parameterized by environment variable and names no trunk, so any seat in any trunk can run it against its own surfaces. Use when a trunk wants to know whether its stated ideals have anything that can actually fire on them, or before claiming an ideal is "wired".
---

# oath-checks

## Why this is a skill and not a script

⛔ **Jon, 2026-08-30 07:21 CDT, verbatim (typos his):** *"that should have been a skill - and stop -
what is less lazy from a Jon College perspective, making these changes yourself by hand, or using a
subagent? What is correct trajectory? ... Ensure you are all being less lazy from both the skill's
perspective and Jon's perspective in college."*

The Secretary's relay names the trap, and this skill is the confession:

> **"LESS LAZY" HAS TWO OPPOSITE MEANINGS.** **LAZY-1** is not doing enough work — cured by doing it
> yourself, now, carefully. **LAZY-2** is not leaving behind the thing that makes the next instance
> unnecessary. ⭐ **Curing LAZY-1 by hand COMMITS LAZY-2, and it ships wearing the costume of rigour.**

`[measured 2026-08-30 07:4x, Professional]` Of every artifact that seat produced in the preceding 24
hours — five new checks, four delivered letters, three wiki pages — **the number reachable AND
runnable by a seat that is not that one was ZERO.** This skill is the correction.

⭐ **The five checks were EXTRACTED, not COPIED.** `scripts/lint.sh` in Professional now sources this
file; there is exactly one implementation. ⛔ **Copying them into each trunk's `scripts/` would create
divergent duplicates — a defect this program has already paid for and named.**

## How to run it

From any trunk, pointing each check at that trunk's own surface:

```bash
LINT_OUTBOX=exchange/outbox \
LINT_LASTSEEN=exchange/LAST-SEEN.md \
LINT_ROSTER=scripts/trunk-roster.tsv \
LINT_OATH_REGISTER=wiki/concepts/the-oath-register.md \
LINT_JON_INDEX=exchange/FOR-JON-REVIEW/00-INDEX.md \
LINT_AUTHOR_PREFIX=<your-outbox-filename-prefix, e.g. pro-to-> \
bash "G:/My Drive/Claude/Claude Professional/claude-professional/.claude/skills/oath-checks/oath_checks.sh"
```

Exit 0 = all nine clean. Exit 1 = at least one failing, named on stdout.
To use it inside an existing lint, `source` the file after defining your own `pass`/`fail`; the
standalone runner then does nothing and your harness owns the exit code.

## ⛔ Read this before you read your first result

**A surface your trunk does not have FAILS as UNKNOWN rather than passing as clean.** That is
deliberate — `UNKNOWN dominates a PASS` — but it means:

> ⛔ **RUNNING THIS AGAINST A TRUNK THAT HAS NOT ADOPTED THESE SURFACES PROVES THE SKILL IS
> REACHABLE. IT DOES NOT CONVICT THAT TRUNK OF ANYTHING.**

`[measured 2026-08-30]` Run read-only against the Secretary's tree, it returned five failures: four
were *"surface absent"* for conventions that are Professional's and not theirs, and the fifth flagged
a missing `self-check:` field **in a trunk that never adopted the field.** ⚠️ **None of those five is
a finding.** Reporting them as findings would be *a filter that over-matches manufactures a finding*
— a defect this program has committed twice and named once. **Adopt a check before you are graded by
it, and say which ones you have adopted in your reply.**

## The nine

| id | oath it wires | breach it fires on |
|---|---|---|
| **C16** | *"I will not hold a standard I have not run on myself."* | a letter naming a peer beside a defect word with no `self-check:` declaration. Grades by **git add-date**, never the filename — the filename is a string the author controls, and that break was found by a falsifier, not by the builder. |
| **C17** | *"I will be the thing that notices absence."* | the newest commit post-dates the beacon's `last_seen:` — a close that wrote history without refreshing the switch. **Also fails a FUTURE-dated beacon**, because one optimistic timestamp silences a staleness check forever and the silence looks like health. |
| **C18** | the graded population is decided, not assumed | a letter delivered into a peer's inbound that has **no copy in your own outbox** — so no check you own can ever read it. |
| **C19** | an ideal is not sworn until it can cost something | a `SWORN` row naming a check that does not exist, is not wired into `run_all`, or has no falsifier that returned an attack. **`HELD` rows are not graded — HELD is the honest state.** |
| **C20** | Jon's surface says who asked | an open row with no `asked-by:` clause, or one whose number cell carries decoration so the wake-time counter cannot see it. |
| **C21** | an obligation surface is only waiting if someone is sent to it | a directory of open rows that **no read-at-open document names**. ⚠️ Grades **reachability, not reading** — a path named in a constitution nobody opens still passes. An EMPTY surface passes on purpose: failing it would teach seats to delete rows to go green. |
| **C22** | a link is a promise; a sentence about a link is not | an unresolved wikilink in a page **BODY** (`LINT_LINK_ROOTS`, `LINT_LINK_EXTRA`). Excludes refs inside fenced blocks and inline backticks, because a sweep that cannot tell a link from a sentence about links inflates every run. ⭐ **Built 2026-08-30 for a measured reason: a `/dream` run found five dangling refs on 08-24 and TICKETED this check; a `/dream` run on 08-30 found THE SAME FIVE. The second measurement was the price of filing it instead of building it.** |
| **C23** | ⭐ **the corpus you QUERY is not the tree you EDIT** | a query corpus missing files the working tree has, holding a different-sized copy of one, or lagging past a declared tolerance (`LINT_CORPUS_MIRROR`, `LINT_CORPUS_ROOTS`, `LINT_CORPUS_MAXLAG_S`). ⛔ **Built 2026-08-31 after the mirror this fleet's retrieval reads was found holding a PRE-C22 copy of this very file — 27,710 B, zero occurrences of `C22`, against 33,700 B live.** A frozen corpus answers as fast and as confidently as a current one; there is no natural alarm. Unset the mirror and it says it is blind rather than going green. |
| **C24** | ⭐ **an index that does not contain you answers your questions about yourself with a fast, confident nothing** | a declared retrieval index holding zero rows for this trunk, zero rows at all, or a schema other than the one declared (`LINT_INDEX_DB`, `LINT_INDEX_TRUNK`, `LINT_INDEX_TABLE`). ⛔ **Built 2026-08-31, the same morning as its cause: a shared index rebuilt IN PLACE on a five-minute tick was read by three seats within one hour and gave three different answers — 89 docs / 1 trunk, then 2,269 / 5. Two seats read a partial build as a coverage failure; one had a live query return ZERO HITS IN 8.97 ms and read it as absence.** ⚠️ Grades COVERAGE, never currency or correctness — an index full of last week's copies of this trunk passes. Prints the index mtime, because a figure read from a mirror is `[relayed]` by construction. |
| **C32** | ⭐ **query before you write -- a finding names what it looked for, or says it did not look** | a letter git-added on/after 2026-09-05 (the council's adoption date for the one fleet-wide field name) with no `queried:` line carrying a value (`LINT_OUTBOX`, `LINT_QUERIED_EPOCH`, `LINT_QUERIED_FIELD`, `LINT_QUERIED_SHOW`). ⛔ **Built 2026-09-12 12:3x on a measured gap: 114 outbox letters carry a 09-05..09-12 filename date, ONE carries the field; the rule had been ratified, written into `/wake` Step 0b and quoted in two maps, and nothing could fire on it.** The id was reserved for this on 09-04 and minted over on 09-07; the collision was caught by `ticket_id_unique.py` and the reserved candidate kept its id. Grades by git add-date; `queried: none -- <reason>` is a value; a blank field is not; `sendmessage-record` captures are skipped by kind and counted; names are capped by `LINT_QUERIED_SHOW` (default 12), the count never. ⚠️ Grades that the SENTENCE exists -- never that the query ran, nor that its top hit bears on the claim (ground-before-stating's open gap). Selftest: `bash .claude/skills/oath-checks/selftest_c32.sh` (9 fixtures, both verdicts, a control per negative). |

⚠️ `[measured 2026-09-12 12:3x]` **The table above is a subset: `oath_checks.sh` defines more `check_*` functions than it lists** — C25–C31 are documented in their own header comments inside the script (`grep -n "^# --- Check" oath_checks.sh`), and the table gained C32 the day it was built. Count the functions before quoting "the nine".

## What it does not do

⛔ **It grades no prose and settles no oath.** C19 certifies **two of the five swearing conditions**; C22 grades a link's EXISTENCE, never whether it points at the RIGHT page; C23 grades presence, size and lag but NOT content, so an edit preserving byte-count passes it; C24 grades whether an index contains you, never whether what it contains is current or true;
that a breach is a real observable, that a fixture replays a REAL past instance, and that the residue
is honestly named are judgements no regex reaches. **A green here is not "the oaths are in good
order."**

⚠️ **And a clean run is not a pass from the controls** — the standalone runner executes no fixtures.
The failability proofs live in the calling trunk's `--selftest`.
