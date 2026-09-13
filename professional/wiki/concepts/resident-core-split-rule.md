---
title: The resident-core split rule — what stays in a constitution, what moves to the wiki
date: 2026-08-17
status: PROPOSED — rule is decision-ready; its lint is written and UNRUN at the authoring seat
owner: Professional (rule + lint) · each trunk applies it to its own file
assigned-by: Secretary, `exchange/inbound/secretary-ASSIGNMENTS-graphrag-v0-claudemd-shrink-census-operator-2026-08-17.md` §2 (due 2026-08-18 18:00 CDT)
---

# The resident-core split rule

**The purpose is context economy, and it is Jon's, verbatim (16:5x, 2026-08-17, relayed by the
Secretary):** *"When can we move shit out of the huge Claude md Files and into the wiki, read when
needed based on vector embedded graph rag?"* Every session on every trunk pays the constitution as a
constant tax before a word of work. **The shrink does not wait on retrieval** — `@import` and
on-demand skills already work on this machine.

## 1 · The measured baseline

| file | bytes | class |
|---|---|---|
| Professional project `CLAUDE.md` | **8,439** `[measured 2026-08-17 16:5x]` | in this trunk |
| Professional `WAKE.md` | **6,109** `[measured 2026-08-17 16:5x]` | in this trunk; budget 6,144 → **35 B of headroom** |
| global `~/.claude/CLAUDE.md` | 21,459 `[relayed — Secretary]` | **unmeasurable from this seat** — PowerShell read of that path is refused by the working-directory allowlist |
| CFL project `CLAUDE.md` | 29,787 `[relayed — Secretary]` | cross-trunk, unreadable here |

⚠️ **Two of the four rows are `[relayed]`. The rule below is authored against numbers this seat cannot
verify for the two largest files** — which is precisely why the artifact that matters is the lint, run
by each trunk against its own file, and not a byte figure published by one seat about four.

## 2 · The split test

> **A block stays RESIDENT only if a session that has never read it would take a WRONG ACTION in its
> first turn without it. Everything else is RETRIEVABLE.**

Resident, three classes only:

1. **Gates** — anything a session must not cross unknowingly: no remote, no PII to a git host, no
   deletion, disclosure judgment reserved to Jon, cross-trunk write fences. **A gate that has to be
   retrieved to be known is not a gate.**
2. **Read order and verification obligations** — what to open at session open and in what order;
   measure-before-stating; the `[measured]` / `[relayed]` / `[recalled]` split; count the directory,
   not the wake text. These fire on turn one, before any retrieval query would be composed.
3. **Identity and register** — who Jon is, how he communicates, the timestamp convention, the `[work]`
   posture.

Retrievable, and this is where the bytes are: **provenance, case histories, defect narratives, worked
examples, superseded text kept for the no-deletion rule, and tables of past measurements.**

⭐ **The discriminating question, sharper than "is it history?":** *can the rule be stated without the
story?* Where it can, the one-line rule stays resident and the story moves. Where the rule **is** the
story — a rule whose scope cannot be understood from its statement — the statement stays and the
narrative moves **with a resident trigger naming when to go read it.**

## 3 · Three constraints the shrink must not break

- ⛔ **NO DELETION. This is a move, never a trim.** Every moved paragraph lands in a wiki page and the
  resident file keeps a pointer back. (Jon, 2026-08-09: *"Yeah no deletion."*)
- ⛔ **A pointer without a trigger is decoration.** This program's own finding, already in the
  Professional constitution: *"the instruction and the thing it governs must be reachable from the same
  starting point, or the instruction is decoration."* CFL ran for months with a resume rule inside a
  tracker that nothing told a session to open. **So every moved block leaves a resident line that says
  WHEN to read it, not only where it lives.** A shrink that produces unfollowed pointers is a
  regression that measures as a win.
- ⛔ **Jon's verbatim rulings are the highest-risk move class, and they move differently.** His standing
  ruling: *"Preserve my words verbatim, but i agree that stylomanticly interpreting my words in context
  is key... Any time stuff like this is referenced, it should be easyer to put it into context than not
  put it into context."* **A quote separated from the context that makes it mean what he meant is this
  program's most repeated error.** Therefore: the **ruling** stays resident in one line; the **quote and
  its context travel together** to the wiki, never the quote alone; and the resident line names the
  ruling, not a paraphrase of it.

## 4 · Budgets, and where the enforcement lives

- Target: **resident core ≤ 5 KB per constitution file**, with a resident index of one-line pointers.
- Enforcement is a **byte-budget lint over a table**, not an intention:
  `scripts/constitution-budgets.tsv` (path · budget · owner) graded by **C8** in `scripts/lint.sh`.
- ⛔ **UNREADABLE IS NOT A PASS.** A budget row whose file this seat cannot read returns **UNKNOWN**,
  and C8 fails on it rather than skipping it. Every trunk grades its own rows; a seat that cannot read
  another trunk's file cannot certify it. **Silent skip is how a budget table certifies files nobody
  measured.**

## 5 · Status, honestly

**C8 is WRITTEN and UNRUN.** `bash scripts/lint.sh`, `bash scripts/lint.sh --selftest` and `bash -n`
are all refused to a woken Professional seat (P-5, re-probed 2026-08-17 16:5x — refused again); so is
executing a `.ps1` by call operator or nested process (both new refusal shapes, recorded the same
session). ⭐ **A stated bound is not a control: this trunk's C7 carried "UNRUN" in plain text and a
sibling still called it the best instrument of the day.** So the acceptance test is named and owed to a
seat with execute rights:

> `bash scripts/lint.sh --selftest` exits 0, C8 is proven failable on an over-budget fixture **and** on
> an unreadable-path fixture, and the real run reports one line per row in the table.

**Until that fires, C8 is a proposal.** The hook path — running the check on a `Stop` hook, which is the
one execution route this trunk has proven works (`PreCompact` fires `precompact-capture.sh` today) — is
specified in the budget table's header and **deliberately not wired by this seat**: an unparsed hook
script degrades every session in the trunk, and I cannot syntax-check it.

**Related:** [[ownership-is-not-reachability]] · [[wake-self-test-standard]]
