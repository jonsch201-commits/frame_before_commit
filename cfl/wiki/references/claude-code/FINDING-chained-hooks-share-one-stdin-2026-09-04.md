---
slug: chained-hooks-share-one-stdin
kind: reference
status: LIVE
date: 2026-09-04
owner: CFL
---

# A `;`-chained hook shares ONE stdin, and the first reader drains it

`[measured 2026-09-04 19:16 CDT, CFL's own PostCompact firing]`

## The shape

CFL's `PostCompact` entry ran two scripts on one shell line:

```
bash py_closed.sh scripts/audit/postcompact_verify.py; bash py_closed.sh scripts/audit/postcompact_pipeline.py
```

The chaining was **deliberate and correctly reasoned.** Two separate hook entries run in
**parallel**, and pipeline step 9 read the verifier's artifact before the verifier had written it
`[measured 2026-09-01 23:00, elder-confirmed]`. The `statusMessage` recorded that reasoning.

⛔ **What nobody measured is that `;` on one line also shares one stdin.**
`postcompact_verify.py:151` does `sys.stdin.read()` — the whole pipe. `postcompact_pipeline.py`
then hit EOF, its `json.load(sys.stdin)` raised, and it fell through to
`sess = os.environ.get("CLAUDE_SESSION_ID", "unknown")` — a fallback its **own comment** documents
as not carrying the session id.

## What it cost, three graded rows deep, none of them naming stdin

| row | printed | what actually happened |
|---|---|---|
| 2 ingest wiki | ⛔ **FAIL** | ran `main_thread_ingest.py --session unknow`; matched nothing |
| 7 lineage row | ⚠️ **PASS** | appended a lineage row for session `unknown` |
| resume line | — | published `claude --resume unknown --fork-session` — unrunnable |

⭐ **The corroborating measurement is the same script on the same disk in the same hour.** The
**unchained** `SessionStart` entry runs `postcompact_pipeline.py` alone, gets a real stdin, and
graded step 2 **PASS**. Same script, same tree, different stdin. That is the whole finding.

## The class — and it is why this is a script, not an edit to one hook entry

⛔ **A SECOND CONSUMER OF A DRAINED STREAM CANNOT DISTINGUISH "NO PAYLOAD WAS SENT" FROM
"SOMEBODY ALREADY READ IT." Both are EOF.** So it silently degrades to its default, and every
row downstream grades against that default *as though it were a reading*.

⚠️ **A default that fires on EOF is not a measurement.** This is the same family as
[[derive-dont-record]] and the standing rule that **UNKNOWN dominates a PASS** — the fallback was
never wrong to exist, it was wrong to be *indistinguishable from an answer*.

⭐ And the second half is worse than the first: **step 7 printed PASS for the entire duration**,
because its only input was the fallback. **A gate whose green survives its own input being absent
is not a gate.**

## Disposition

- **FIXED** — `.claude/hooks/hook_fanout.sh`: reads stdin once to a temp file, runs each child
  through `py_closed.sh` in the given order with `< tmpfile`. Ordering (the reason the chain
  existed) is preserved; every consumer sees identical bytes. Always exits 0 — PostCompact must
  not block on infra — and a non-zero child does **not** cancel the children after it.
- **FIXED** — step 7 now grades **FAIL** on an unknown or short session id, so the gate can fail.
- **FIXED** — `postcompact_pipeline.run()` pinned to `encoding="utf-8", errors="replace"`;
  `text=True` alone decodes with the **locale** codec (cp1252 here) and a child's UTF-8 em-dash
  landed in the graded note as mojibake. Same family as the wake command's `wc -c`-never-`len()`
  rule: multi-byte bytes read through a single-byte lens.
- **GATED** — `G20` (selftest, 8/8, whose **case 2 reproduces the loss** on the `;`-chain) and
  `G21` (the negative control: step 7 FAILs on empty stdin, PASSes on a real session).
- **SWEPT** — `PostCompact` was the only chained entry with more than one stdin consumer
  `[measured 2026-09-04: one other `;`-chain exists, SessionStart's git-pull line, which has zero]`.

## Verification after the fix

`POSTCOMPACT-STATUS` went **FAIL → PASS-WITH-SKIPS**, and step 2 wrote real wiki footprint:
`wiki/intake-triage/main-thread/71ce5a/code-2026-09-03-71ce5a-…i1.md`. That footprint is the thing
Jon named on 2026-09-04 (verbatim, typos his):

> *"thats a huge defect that i have tried to correct in you multiple times. compact still not
> triggering session covedrage by default? We should be at 100% by now by default after ever
> all-trunk compact!"*

⚠️ **The ingest step was BUILT earlier the same day and was still producing nothing, because the
hook wiring never handed it a session to ingest.** Every field ships with its reader — and a
reader ships with a check that it was actually fed.

---

## ⛔ THE SECOND FINDING, which the first was hiding: the ingest wrote to a DIFFERENT CLONE

Fixing the stdin bug made step 2 run for the first time. It reported `PASS … wrote
wiki/intake-triage/main-thread/71ce5a/…i1.md` — **and that path did not exist in this repo.**

`main_thread_ingest.py:114` read `REPO = Path(X.ROOT)`. `X.ROOT` is the **corpus** root and is
pinned to `G:\My Drive\…\claude-foundational-layer` **deliberately** — the gitignored bulk
transcript corpus lives there, and `extract_claude_code_sessions.py:67-79` documents that split
and provides `CODE_ROOT` for the other half. ⛔ **The I1 extracts are TRACKED WIKI PAGES, not
corpus.** So every page the ingest ever wrote landed in a clone parked on branch
`feat/post-pr2-open-2026-08-29` (HEAD `3374d9f`, 09-01) — never committed on the live branch, and
invisible to every census run from the working tree.

`[measured 2026-09-04 19:3x]`

| | `main-thread/` dirs | `.i1.md` pages |
|---|---|---|
| N: (live, `week-2026-09-02-corpus`) | 5 | 5 |
| G: (stale, `feat/post-pr2-open-2026-08-29`) | 6 | **6** |

Five dirs overlap from common history; the one new page today's run produced existed **only on G:**.

⭐ **AND THE FIX ALREADY EXISTED.** `agent_end_ingest.py:169-172` — this script's own sibling,
which `main_thread_ingest` **imports as `AEI`** — made exactly this correction on **2026-09-03**,
with the same measurement in its comment: *"X.ROOT is hardcoded to the G: clone, so once the N:
clone became the working tree (09-02 21:4x) every SubagentStop ingest landed on a stale tree (35
on G: vs 2 on N: for session 71ce5a)."* It was never propagated to the other two call sites.

⛔ **RC-D, in its plainest form: recorded, correct, and not on the acting path.** The knowledge was
one import statement away from the code that needed it.

`check_jon_word_coverage.py:115` had the same line, on the **read** side: it walks "the tracked
prose surfaces," so it has been grading the stale clone. ⚠️ **A coverage number measured against
the wrong tree is not a low score. It is not a measurement.**

## Disposition (second finding)

- **FIXED** — both sites now `Path(os.environ.get("CLAUDE_PROJECT_DIR") or X.ROOT)`, the sibling's
  already-vetted pattern verbatim. Corpus reads still resolve through `X.ROOT`, unchanged.
- **VERIFIED** — re-run against the working clone wrote `main-thread/71ce5a/…i1.md` into N:
  (**71 Jon utterances, 55 anchored, 4,461 turns**); N: now holds 6 tracked i1 pages.
- **GATED** — `G22`, `scripts/tests/selftest_ingest_write_target.sh`, 4/4, including a control that
  keeps the deliberate `X.ROOT` fallback visible rather than accidental.

⚠️ **What this says about the first finding's gate, and it is the uncomfortable part:** step 2's
`PASS` was **truthful** — the ingest really did write a file. The gate checked that the writer
reported success, never that the artifact landed anywhere the reader looks. ⭐ **The writer and the
reader had separate provenance** — this week's dominant defect, in the machinery built to detect it.

---

## ⚠️ THE THIRD FINDING, and it is the one that matters to Jon's actual question

Both fixes landed. The census was then re-run on the canonical roots
(`--raw-root N:/claude-corpus/cfl/raw --wiki-root N:/claude-cfl/clone/wiki --as-of 2026-09-04`).

`[measured 2026-09-04 19:5x, n=888 sessions]`

| grade | all | 2026-09 (n=55) | 2026-08 (n=532) |
|---|---|---|---|
| A | 433 | 3 | 244 |
| B | 65 | 1 | 25 |
| C | 78 | 1 | 45 |
| D | 28 | 0 | 10 |
| S | 276 | **46** | 204 |
| Z | 8 | 4 | 4 |
| **A/B** | **498 (56.1%)** | ⛔ **4 (7.3%)** | 50.6% |

⛔ **September did not move. It is 7.3%, exactly where it was before either fix.**

⭐ **And that is not a failure of the fixes — it is the answer to the question Jon actually asked.**
He said the defect was that *"compact still not triggering session covedrage by default… We should
be at 100% by now by default after ever all-trunk compact!"* ⚠️ **The ingest a compact triggers
produces I1 extracts under `wiki/intake-triage/`, and this census grades a session cited ONLY there
as class **C** — by its own definition (`coverage_census.py:36`), not as an oversight.** The compact
path, wired perfectly, tops out at **C**. It cannot reach A/B **by construction**.

⛔ **SO THE EXPECTATION AND THE MECHANISM DISAGREE, AND NEITHER IS WRONG.** 46 of September's 55
sessions sit at **S** (stub) and need promotion to a source page — a materiality judgment, not a
hook. **Wiring the compact harder will never move this number.**

**Two honest routes, and choosing between them is Jon's, not CFL's:**

1. **Promote.** Keep "covered" meaning A/B and add the S→A promotion step (materiality-ranked) to
   the overnight lane. 100% then means 100% *judged*, and costs judgment per session.
2. **Redefine.** Accept C as coverage for the compact path — the I1 extract does carry his verbatim
   utterances with anchors — and report A/B/C separately so "100%" is honest about what it means.

⚠️ **What CFL will NOT do is quietly pick one and report a number against it.** The 7.3% above is
measured, unmoved, and stated with the reason it did not move — because a coverage figure whose
denominator was silently redefined is the same defect as a coverage figure measured against the
wrong tree, which is finding 2 on this page.

---

## ⚠️ THE CONSULT RETURNED A VERDICT WITH NO PRIMARY, AND THAT IS NOT AUTHORITY

The pre-stop consult was asked one narrow question: does the corpus contain any Jon authorization
bearing on whether a coordinator should DECIDE the definition of a measured term itself, or hand it
to him? The brief asked for **quotes with file paths, verbatim**, and said explicitly: *"If you
found nothing, say SILENT — I will not read silence as agreement."*

`[measured 2026-09-04 19:4x–19:5x, two runs, 33 tool uses, ~111k tokens]`

| run | returned |
|---|---|
| 1 (hit its 20-turn limit) | `Complete.` |
| 2 (asked again, ≤300 words, evidence-shaped) | `CONTINUE-AND-DECIDE.` |

⛔ **Zero quotes. Zero paths. Neither the affirmative evidence nor the SILENT the brief asked for.**

⭐ **What it does and does not license, and the split is the whole point:**
- **DOES** support *continuing to work* rather than stopping — and CFL continued, building the
  class detector (`hook_stdin_lint.py`, G23) after receiving it.
- ⛔ **DOES NOT license redefining what a published coverage number means.** The mirror's charter
  is explicit that it **ratifies nothing and flips no status** (charter A3), and a verdict with no
  primary is not a primary. ⚠️ **"An agent said CONTINUE-AND-DECIDE" is a report about an agent,
  not evidence about Jon.**

⚠️ **The failure mode this avoids is the exact one this page documents twice already:** taking a
green whose input was never actually read. A bare verdict is the consult's version of
`sess = "unknown"` — a default-shaped answer that grades as though it were a reading.

**Disposition:** the coverage-definition choice (promote S→A, or accept C and report A/B/C
separately) stays **JON'S**, unresolved, with its on-silence default executing nothing.
