---
title: prose-rules-that-failed-professional
created: 2026-08-17
provenance: "[measured 2026-08-17 11:3x-11:5x CDT] — every failure row below was read this session from this trunk's own record (wiki/log.md, exchange/precompact-receipts.log, git status, a lint run) or re-exhibited live this session. No row is recalled."
---

# Professional's answer to CCAR-F §1 — the prose rules in this trunk that have failed

**The goal, quoted from the letter that set it** (`[SECRETARY] exchange/inbound/secretary-claudeai-to-code-CCARF-BLUEPRINT-ADOPTION-2026-08-16.md` §1, opened this session):

> **Name every prose rule in your trunk that has failed at least once, and say which layer would
> have enforced it. Return the list with receipts. Rules that have never failed are out of scope
> for this round.**

**Scope discipline, stated because it changes the answer:** a rule qualifies only if it existed in
prose *and was then violated*. Rules this trunk has never broken are out — including the one whose
cross-trunk receipt is freshest (escape-safe writing of path-bearing files: exhibited in another
trunk's file this morning, never in mine). **Ten rows qualify.**

## The register

| # | The prose rule, and where it lives | The failure, with its receipt | The layer that would have caught it | Status |
|---|---|---|---|---|
| 1 | **Close ends at a durable record and a commit** — `WAKE.md` gates; the `/su-compact` ritual | **Today.** Session `5f6a442a` fired the PreCompact hook at **2026-08-17 09:41:47** (ledger row, 390,698 B archived) and left the **newest `wiki/log.md` entry dated 2026-08-15** and both receipt files **uncommitted** at 11:37 `[measured]` | A check comparing newest receipt date against newest log-entry date | **LAYERED THIS SESSION — `lint.sh` C6, and it FAILED on this live case at introduction** |
| 2 | **Lint's exit code gates the commit** — adopted 2026-08-15, the day it was broken | Commit `2e87edd` landed while C3 was FAILING, because the command piped lint into `tail` and read the pipe's status. **Re-exhibited by me at 11:4x today**: `lint --selftest \| head` reported `exit=0` while the script's real exit was 1 `[measured]` | A **blocking** pre-commit hook that runs `scripts/lint.sh` and refuses on non-zero | **NOT LAYERED.** Prose only. Highest-value gap in this trunk |
| 3 | **Never state a number you have not just measured** — `CLAUDE.md` method rules | *"The ASOPs were not downloaded. They are now"* — false, corrected in the turn it was found. `wiki/index.md` said **2 concept pages while 7 existed on disk** | Reconciliation of the counted claim against disk | **LAYERED for the countable half — C2** (PASS today: 17 concepts, both directions). The narrative half stays prose |
| 4 | **`WAKE.md` stays inside its byte budget** | **8,295 B** against the 6,144 B budget the same command specified; then **6,386 B** committed on 08-15 | A byte-budget check | **LAYERED — C3** (6,094 B today) |
| 5 | **Stamps are emitter-generated, clock-then-stamp (U8)** | Composed-stamp instance 08-14; the n=4/n=5 class 08-15 — mine, and they became the instrument the same morning | An emitter plus an integrity checker over dated artifacts | **LAYERED — `stamp.sh` + `stamp-check.sh` as C5** (clean today). **Detects after the write; does not block it** |
| 6 | **Verify the target before you deposit** — `CLAUDE.md`, war story attached | The rule was already written when a Herald letter went to `G:\My Drive\Herald Wiki\...` — **the write created its own destination and reported success**; caught by a boundary delivery check, not by the write. Second instance 08-15: a to-all letter held as a to-one-tree delivery, self-caught | A deposit path with a **precondition gate** (target must contain `.git` and files this actor did not author), plus post-write `cmp` | **NOT LAYERED.** Prose plus habit. Cheapest gate remaining |
| 7 | **Every instrument carries a positive control** | `scripts/asop.sh` returned **zero hits across all 57 standards** for a string demonstrably present in ASOP 1 — a CRLF defect. Found only by testing the tool against a quote already published | A check that every script in `scripts/` exposes a `--selftest` proving each of its checks can fail | **LAYERED AS CONVENTION** (lint 6/6 proven failable; `precompact-capture --selftest`). **Not enforced for new scripts** — candidate C7 |
| 8 | **Carry the qualifier** — `CLAUDE.md`: *"a qualified statement reported as unqualified is this program's most repeated error"* | Jon's *"should not release **everything**"* recorded as "publication ruled out" — **the map's Out-of-scope was corrupted ~2 hours**. Same class: *"the field has no infohazard norm"*, a zero-count over a nine-term list | **No hook sees meaning.** CCAR-F D4.3's mitigation instead: **nullable** `jon_verbatim` / `qualifier` fields, so absence returns null rather than being filled to satisfy a required field | **NOT LAYERABLE as a check.** Schema-mitigable |
| 9 | **A filename is not a `from:` field** | Four Personal letters attributed to the soul session off a filename prefix; one was soul's. An arithmetic error in the same letter | A courier-letter schema with a required `from:`, so attribution is read and not inferred | **NOT LAYERED HERE** — the schema is P2, Secretary-owned, unbuilt. My own deposits carry `from:` by habit, which is exactly the weak form |
| 10 | **Answer Jon's live questions in final text before scheduling a wakeup** — adopted 08-15 | **Three turns on 08-15** ended at `ScheduleWakeup` with his live questions unanswered; answered at day end instead | Nothing on today's surface: no hook is shown a turn's user-visible text alongside its tool calls | **NOT LAYERABLE.** Prose, held by placement in `WAKE.md` |

## What the register says, beyond the rows

**1. Every rule of mine that reached a layer reached the same layer, and none of them blocks.** C2,
C3, C5 and C6 are four checks in one instrument that runs when somebody runs it. **This trunk has
zero blocking gates** — the Secretary's program-wide finding #1 reproduced from the inside, by a
different actor, against a different record. Row 2 is where that stops being a taxonomy note: the
rule that lint must gate the commit **was broken by the lint-running command itself, twice, six days
apart, in two different sessions.** A rule about honoring an exit code cannot be enforced by
remembering to honor it.

**2. The strongest rows are the ones where the failure built the instrument the same day** (4, 5,
and now 1). The weakest are the ones where the rule was *strengthened in prose* after failing
(2, 6) — **both have since failed again.** That is the CCAR-F thesis reproduced locally: prose
answered with more prose has a non-zero and, on this evidence, undiminished failure rate.

**3. Three rows are honestly not layerable** (8, 10, and 9 in part). Naming them matters, because
the program's temptation is to claim a hook for everything and then hold the semantic classes to a
standard no hook enforces. **For row 8 the answer is schema shape — nullable fields — not a check.**

## The one built this session

`lint.sh` **C6 — close-record closure.** The newest non-selftest row in
`exchange/precompact-receipts.log` must be dated on or before the newest dated entry in
`wiki/log.md`. Selftest-proven failable (canary ledger dated 2099-01-01); real run:
`FAIL [C6] compact captured 2026-08-17 but newest wiki/log.md entry is 2026-08-15` `[measured]`.
**It found a real gap in this trunk on its first run**, which is the only evidence a check is worth
anything — a check that has only ever passed is not evidence (Herald's standard, adopted).

**Its limit, stated:** C6 detects at the next lint, not at the boundary. It cannot stop a session
from ending; it can only make the next session unable to miss that the last one did.
