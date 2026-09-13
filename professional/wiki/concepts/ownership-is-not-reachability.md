---
title: "Ownership is not reachability — this project ran another project's `/wake` and `/su-compact` all day, and the audit that checked for them said they were absent"
created: 2026-08-07 16:01 CDT (session 2, heartbeat, post-compact)
kind: finding
provenance: "[measured — this session, filesystem + this session's own skill listing]. Mechanism attribution is [inferred] and labelled as such."
teaches: "CFL, Personal, Herald — Jon, 2026-08-07 [verbatim]: 'All branches should be aware and help teach each other how to improve on this.'"
---

# What happened

**`[CFL] exchange/CROSS-BRANCH-COMPACT-SU-AUDIT-2026-08-07.md`** (10,200 B, written 16:00 CDT) was
produced at Jon's request. His words, quoted in it `[verbatim]`:

> *"need to let you know I did not follow your precise words and include the required text in compact
> command, and not all projects have been getting this for me. I request a cross branch audit of
> compact and standard update procedure including skills."*

Its matrix puts **`—`** in this project's `/wake`, `/su-compact`, and `settings.json` cells, and draws
this inference (`:41`, quoted `[verbatim]`):

> *"`/su-compact` cannot fire in Professional or Herald because **it does not exist there** — not
> because anyone skipped it."*

**The cells are correct. The inference is false. This session ran both commands today.**

---

# The measurement

`[measured — 2026-08-07 16:01 CDT]`

| Question | Result |
|---|---|
| Every file in this repo's `.claude/` | **`scheduled_tasks.lock`. That is the entire tree.** No `commands/`, no `settings.json`, no `hooks/`. |
| `~/.claude/commands/` | **Does not exist.** *(CFL's audit says "empty"; it is absent. Same conclusion, different fact.)* |
| `G:\My Drive\Claude\.claude\` and `G:\My Drive\.claude\` | **Neither exists** — parent-directory inheritance ruled out. |
| `[PERSONAL] .claude/commands/wake.md` | **2,248 B.** Contains all five markers present in the `/wake` that ran here: `CARRIER.md` · `6,144` · `MIRROR-STATE-CURRENT` · `RESUME-BRIEF` · `origin/master`. |
| `[CFL] .claude/commands/wake.md` | 5,013 B. Matches on `CARRIER.md` only. |

**The only remaining resolution path is the session's additional-working-directories list**, which
carries `G:\My Drive\Claude\Claude Personal`. `[inferred — mechanism only. Every row above is
measured.]`

## What the borrowed procedures actually instructed

**`/wake`, run at this session's open**, directed reads of `CARRIER.md`, `wiki/SCHEMA.md`,
`wiki/intake-triage/MIRROR-STATE-CURRENT.md`, and `wiki/intake-triage/RESUME-BRIEF-*.md`.
**`find` returns zero of the four in this repo.** `[measured]`

**`/su-compact`, handed to Jon at this session's close**, specifies a verify pass of
`python scripts/gen_index.py`, `bash scripts/lint.sh`, and `python scripts/capture_all_jsonl.py`.
**`scripts/` in this repo contains exactly `asop.sh` and `fetch_asops.sh`.** `[measured]`

**⛔ And the one that matters most here:** that wake step runs
`git rev-list --left-right --count HEAD...origin/master`.

**It is a procedure that presumes a remote, auto-loaded into the one project in the program where
having a remote is a standing Jon gate.** It errors rather than creating anything — **no gate was
breached and none was approached** — but a close ritual should not be pointed at a gate by accident,
and the next person to read its output should not have to know that to interpret it.

---

# ⭐ The generalisable finding

**An audit that measures OWNERSHIP — *does this project contain X?* — answers a different question
than REACHABILITY — *does X run here?*** Wherever a runtime resolves names across a search path,
those two diverge, and **the divergence is invisible from either project's own tree.** Neither
Personal's directory listing nor Professional's shows it; only execution does.

**Absence and silent inheritance are different failure modes and they must not be merged:**

- **Absence fails loudly.** Nothing runs. The gap announces itself.
- **Silent inheritance runs the wrong project's procedure and reports success.** It is the same
  shape as every blind-instrument defect on this program's record — **the check passes by measuring
  something other than what it claims.**

**The rule: measure at the point of execution, not the point of storage.**

## And the part that is mine to own

**The evidence was in my own context window at session open.** The skill listing labelled them
**`projectSettings:wake`** and **`projectSettings:su-compact`** — and their bodies named
`CARRIER.md`, `MIRROR-STATE-CURRENT.md`, and `wiki/tracker/wayfinder-personal-wiki.md`, **none of
which is a path in this project.** A one-line check — *does the procedure name files this repo has?*
— was available all day and I did not run it. **I ran the ritual and did not read the ritual.**

---

# ⚠️ The caution that travels with the fix

CFL's audit ranks the repair as its **defect #2 — *promote to user level*** — and marks it
**Jon's call**, because *"it changes every project at once."* **That gate stands; nothing here
overrides it.**

**And Herald's standing warning applies directly to the act of teaching this across four projects**
(`~/.claude/CLAUDE.md`, `[verbatim]`):

> *"the risk of mutual learning is convergence; if we teach each other well enough we become one
> coordinator with one blind spot, and the redundancy that caught all of this disappears."*

**CFL reached the same conclusion independently in the same audit: *"Neither is a superset. That is
the finding, not a complaint. Copy the three named items. Do not merge the files."***

**So the correct outcome is NOT one `/wake` for all four projects.** It is: **each project's close
procedure names its own paths, and every project can tell which one it is running.** Uniform
procedure would delete the redundancy that produced this finding — **this defect was found precisely
because a foreign procedure's paths did not match a local tree.**

---

# Open

- **Does Herald inherit too?** Herald has no `.claude/commands/` `[measured]`. **Whether it resolves
  a sibling's commands depends on Herald's own sessions' working-directory list, which cannot be
  measured from here.** Asked of Herald directly; not asserted.
- **Whether this project should get its own `/wake` and `/su-compact`** naming its own paths.
  **A build, not a repair** — CFL's audit ranks Professional's missing `settings.json` as defect #3
  and says the same. **Not started; not a heartbeat's call.**
- **What else resolves across the path.** Commands were checked. **Skills, hooks, and agent
  definitions were not** — CFL measured `~/.claude/skills/` at **33/33 byte-identical to its repo**,
  which is a deliberate sync rather than an accident, but **that is CFL's measurement of CFL's
  question, not an answer to this one.**
