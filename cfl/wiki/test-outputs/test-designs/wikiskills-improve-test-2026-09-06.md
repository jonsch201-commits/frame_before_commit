---
kind: test-design
skill: wikiskills-improve
designed_by: test-master (cfl 46276084, 2026-09-06 15:1x CDT, invoked by Jon's bare /test-master)
status: RUNNING — the null test is the prototype lane already in flight
rubric: non-FBC four dimensions (document) + a behavioral rubric (live execution; B3 caveat honoured — declared here before scoring)
---

# Test design — wikiskills-improve — 2026-09-06

## What the skill claims (read in full, deployed copy `~/.claude/skills/wikiskills-improve/SKILL.md`, ~70 KB)
One message Jon sends to every trunk's fresh JSON after the all-trunk compact. On invocation a seat: (0) prints its own
`### <trunk>` headline unasked, locates its own row, (1) runs its trunk's wake/elder line, (2) consults its compact-1
predecessor with the complete prompt file, (3) reads its trunk focus, (4) works the three fleet targets, (5) grades its
predecessor, (6) writes `exchange/WIKISKILLS-IMPROVE-ECHOED-<sid8>.md` (the retirement detector).

## Most judgment-dependent operations (where it could fail without being obviously wrong)
- **Self-location** in a 70 KB file with seven trunk sections — a seat can reason generically instead of finding its row
  (Secretary measured this on a haiku seat, 14:4x).
- **The elder consult** — a described `-p` argument forks the elder and returns a fluent answer to nothing, rc=0 (measured
  09:17). The pass is "the answer addresses a question that was asked", never rc.
- **The transport** — `/wikiskills-improve` on a git-bash launch line arrives as `C:/Program Files/Git/wikiskills-improve`
  (measured 09:26, two seats); the seat then does an ordinary wake and nobody is told.
- **Grading the predecessor** — §5 asks for Jon's metric first; a seat can produce a grade with no measured basis.

## Null test (Test Before Framing): does the skill fire at all on a COLD seat?
**Scenario:** a fresh headless JSON (`claude -p "/wikiskills-improve" --permission-mode plan`, `MSYS_NO_PATHCONV=1`) opened in
the trunk's OWN tree (its hooks run), one trunk at a time, by `skills/wikiskills-improve/PROTOTYPE-fresh-json-drive.py`.
**Context:** cold — the seat has never seen the conversation that built the skill.
**Expected output:** first non-empty line is the trunk's `### <Trunk> — predecessor <full UUID>` headline; the predecessor's
full UUID appears; no `Program Files/Git` string; a new `WIKISKILLS-IMPROVE-ECHOED-*.md` in the tree after the run.
**What a delta looks like:** the headline is line one and the body addresses that trunk's §3 (its own commands, its own map).
**What failure looks like:** generic reasoning about the fleet; a wake ritual instead of the skill; rc=0 with a headline
for the WRONG trunk; the mangled path; a timeout in the tree's SessionStart hooks (≠ skill failure — label separately).

## Behavioral rubric for the live run (declared now, scored later — B3)
| check | PASS | FAIL |
|---|---|---|
| B1 headline-first | first non-empty line starts with own `### <Trunk>` | anything else first |
| B2 own-row | body cites its own §3 commands/map, not another trunk's | generic or wrong trunk |
| B3 elder UUID | own predecessor's full UUID present | absent or 8-char |
| B4 transport | no `Program Files/Git` | present |
| B5 echoed | new ECHOED file after the run | none |
| B6 time-to-first-line | < 5 min from launch (Secretary's redo: 44 s) | ≥ 15 min = hooks, label HOOK-STALL not skill |

## Document rubric (non-FBC, all four dimensions apply)
Accuracy · Completeness · Consistency · Jon-Calibration — scored in the test-log entry.

## Baseline already on the record (so the null result has a comparand)
- 09:26: two fresh Secretary JSONs — DID NOT FIRE (transport). 14:46–14:48: three headless fresh Secretary JSONs (Secretary's
  own probes) — FIRED, headline first in two, first finding in one. These are the only cold runs before this design.
