---
name: peer-review
version: 0.1
date: 2026-09-07
session: cc87418b (Professional, N:), window 1
status: ACTIVE
materiality: "changes when a seat may call a review closed and an act complete — material; intended users: every seat in this trunk, the co-trunks who ask us to review"
review: UNREVIEWED — written by the seat that ran the review it generalises. First reviewer = whoever grades it against the 2026-09-07 Secretary exchange.
queried: "completion criterion intended user ASOP 41 issuance — rank 1 wiki/references/materiality-ruling-asop-1-and-41-2026-09-06.md (Q1/Q2), rank 2 CLAUDE.md method rules (a fix is not closed by its author), rank 3 wiki/concepts/windows-shell-eats-values.md"
---

# peer-review — reviewing a peer, and knowing when the review is finished

**Discharges ES-8, carried open since 2026-09-06.** Written from a live review: Secretary asked
Professional for an independent read of a grade whose author had disqualified itself, plus a co-review
of its proposed completion criterion. Every rule below is a thing that went wrong that night, mostly
mine.

## 1. The completion test — what "done" means, and it is a destination, not a mind

> ⭐ **A MATERIAL act is complete when its artifact exists at the destination the intended user reads,
> in the form the standard names, and a seat other than its author can verify both.**

**Three clauses, each load-bearing:**

- **MATERIAL.** `wiki/references/materiality-ruling-asop-1-and-41-2026-09-06.md` Q1: *"materiality
  attaches to a decision, not to a reader. An artifact that informs no decision is immaterial however
  many readers it has."* ⛔ **Drop this word and every act — a CRLF normalisation included — becomes
  permanently unfinished, which manufactures the stopping Jon's standing ruling calls defective.**
- **DESTINATION, NOT MIND.** ⛔ **No instrument on this machine reports whether Jon read anything.** A
  completion test whose observable is a person's cognition returns neither verdict on Jon-facing acts —
  it becomes unfalsifiable exactly where it matters most. ASOP 41 divides this the same way: the
  responsibility is ISSUANCE, not comprehension.
- **IN THE FORM.** A file at the right path that costs an hour to read has reached the destination and
  not the user. The fleet skill's §6 word budget is the second half of the test; without it "landed"
  is gameable the way "published" was.

**The mechanism, and it is failable:** `python scripts/issuance_check.py --draft <letter>` — 8-case
selftest, `--selftest`, rc 0/1. It verifies a byte-identical copy in every roster recipient's inbound.
⛔ **An outbox file is a draft; only the receiver's tree is delivery.** Run it before you say delivered.

## 2. What a review checks — three things, and the third is the one that gets skipped

`CLAUDE.md`: *"A fix is not closed by its author. Whoever raised the finding checks it against the
finding **and against the cause the fix's author named**."*

1. **The claim** — re-run it. ⛔ **No grade without a command.**
2. **The control** — a FALSE needs a control proving your instrument works. An absence needs its
   population printed.
3. ⭐ **THE CAUSE THE AUTHOR NAMED.** A verdict can be right and its explanation wrong, and the
   explanation is what the next seat acts on. **Fixture, 2026-09-07:** Secretary graded a hash FALSE —
   correct — and explained it as *"correct when first measured and carried 33 hours"*. Hashing all 31
   committed versions of that file showed the value was **never** any digest of any version. Not stale:
   **born wrong.** ⛔ **Different remedies. Stale → re-derive before quoting. Born wrong → the number
   must be EMITTED BY THE COMMAND THAT COMPUTED IT, never typed beside it.** Filing one as the other
   teaches the wrong discipline to everyone downstream.

## 3. Grade the class, not only the instance

- **DRIFTED** = same shape, number moved. **FALSE** = no run of that instrument could have returned it.
  ⭐ **The test that separates them:** if the missed item existed at claim time and the instrument could
  not express it in principle, it is FALSE, not DRIFTED.
- **UNKNOWN dominates a PASS.** A check that could not run is UNKNOWN; never infer a total from a
  truncated run.
- **Do not close an UNKNOWN from the subject's own evidence.** Grading their claim with their
  instrument's output recreates the defect the outside reader was asked to avoid.

## 4. ⛔ You will commit the defect you are grading. Log it rather than tidying it.

**Three instances in three hours on 2026-09-07, all mine, all while reviewing them in someone else:**

| I was grading | I then did |
|---|---|
| a glob that could not express `antigravity-hub` | ran `find -maxdepth 3` and got **5 receipts of 7** — `claude-cfl/clone/exchange` is depth 4 |
| a hash that was typed rather than emitted | shipped `reader_token_cost: 764 words` unmeasured, earlier the same night |
| a Windows path defect | patched a script through a shell heredoc, the `\n` was eaten, and the file broke at line 78 — the one thing `wiki/concepts/windows-shell-eats-values.md` forbids |

⭐ **This is a property of the instruction, not of the seat** — two seats in opposite roles hit the same
blind spot minutes apart on the same night. **So the rule is a mechanism, never "be careful":** use the
Write tool for anything with quotes or backslashes; enumerate roots instead of matching names; print the
population you searched.

## 5. What can fail

- `python scripts/issuance_check.py --selftest` → 8 cases: A deliver · B one missing · **C inertness
  control** (zero delivered copies must go red, so A cannot pass vacuously) · **D depth control** (a
  recipient one level deeper must still be found) · E no-destination · F differing bytes · G malformed
  roster raises · **H bad-roster-path control**.
- **Proven able to fail 2026-09-07 21:3x:** neutralising the anchor guard in a scratch copy produced
  `SELFTEST FAIL H control`, rc=1, while A–G stayed green. A guard must be failable on its own axis.
- **Known limits, stated:** the roster is hand-maintained — a recipient nobody adds is a recipient
  nothing checks, and that failure is silent. The check proves a byte-identical file is at a path; it
  proves nothing about whether anyone read it, **and it must never be reported as if it did.**

## 6. Three failures of 2026-09-12, and what they bind

Three claims this trunk published on 2026-09-12, each caught by a peer within the hour, each an instrument
defect rather than a carelessness. Full receipts, claims verbatim, and retractions:
`wiki/references/three-failures-of-2026-09-12-and-what-they-bind.md`. The imperatives:

1. **Read the clock; never take it from a peer.** A `[m HH:MM]` stamp asserts that `date` ran in that
   turn. A peer's `date:` field is a relayed value — on 09-12 Herald's were narrated up to 37 min fast
   and this seat copied one into a letter filename. Letters carry `date: … [MEASURED — <command>]` or
   `[narrated]`; untagged means nobody looked. Receipts: `wiki/log.md` line `[m 12:45:45 clock] CORRECTION
   of my own stamps`; `exchange/inbound/CORRECTION-2026-09-12-1248-personal-to-all-EVERY-CLOCK-I-STAMPED-TODAY-AFTER-1223-WAS-NARRATED-…md`.
2. **Compare blob ids, never checked-out bytes to stored bytes.** `git hash-object <path>` against
   `git rev-parse <ref>:<path>`. Git normalises CRLF on check-in, so `wc -c` / `sha256sum` of a working
   file never equal `git show <ref>:<path>` in a CRLF tree — that gap is the line count, not a write.
   Count line endings with python bytes (`b.count(b'\r\n')`); git-bash `grep` strips CR and returns 0.
   Receipts: `wiki/log.md` line `[m 12:5x] RETRACTION of my 12:51 line`;
   `exchange/inbound/REVIEW-2026-09-12-1255-personal-to-all-ANTIGRAVITYS-RESTORE-OF-PROFESSIONAL-IS-CLEAN-AND-THE-FALSE-CELL-IS-THE-FALSIFIERS-OWN-CRLF.md`.
3. **A count is a measurement; its reading is a separate claim with its own grounding.** Before grading
   a count, print the population and read the column or destination the grade is about: run the test
   in the destination (`git -C <dest> rev-parse --show-toplevel`), open the table's column. On 09-12 "9 of
   14" was exact and "the other five write into trunk trees" was false (they write to `~/.gemini/…/brain`
   and `N:/claude-indexes`); earlier "11 of 13 rows carry no default" came from grepping for a word when
   the table's third column IS the default. Receipts: `wiki/log.md` lines `[m 08:5x] CORRECTION OF THE
   CORRECTION` and `[m 13:2x]`; `exchange/inbound/RULING-2026-09-12-1315-personal-to-antigravity-DISPOSITION-1-CLOSES-AND-THE-SEVEN-UNGUARDED-SITES-WRITE-TO-NO-GIT-TREE-AT-ALL.md`.

Near-failure, same day: the seat ran 24 h as a background job in a worktree without saying so until Jon
asked *"you are a background job?"* (13:23:45 CDT). **Placement is measured** — `pwd`, `git worktree list`,
`git branch --show-current` — at wake and in every log heading, never carried from the last turn.
