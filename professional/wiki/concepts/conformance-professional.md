---
title: conformance-professional
created: 2026-08-15
provenance: "[measured 2026-08-15 07:46 CDT] — every value below read from disk or git this session, none recalled"
---

# Conformance — Professional trunk

Thin per-trunk page under the master:
`[PERSONAL] wiki/concepts/herald/cross-trunk-alignment.md`. Adoption state lives ONLY in
`wiki/references/standards-adoption-slate-2026-08-14.md` (the U6 primary); this page never
restates it.

## The adopted question: what pinned inputs produced this session

Session `bb5dd04f`, answered 2026-08-15 07:46 CDT `[measured]`:

| Pinned input | Value |
|---|---|
| git ref | `master` @ `aa1c8db` (no remote — local-only by standing Jon gate) |
| Wake note | `WAKE.md`, AS OF 2026-08-15 07:19, 4,987 B (budget 6,144) |
| Constitution pair | `CLAUDE.md` (repo) + `~/.claude/CLAUDE.md` (universal; synced by CFL's `sync-universal.sh`) |
| Persistent memory | `~/.claude/projects/G--My-Drive-Claude-Claude-Professional-claude-professional/memory/` |
| Model | ⛔ **THIS ROW STORED `main loop Fable 5` FROM 2026-08-14 UNTIL 2026-08-29 AND WAS WRONG FOR THE LAST TWO WEEKS** — `[m 2026-08-29]` the six newest sessions measured **100% `claude-opus-5`**, and the trunk's transcripts hold **6,176 opus-5 / 3,299 opus-4-8 / 767 fable-5**: three models have run this seat. The field was in every transcript line and no instrument read it. ✅ **Run `bash scripts/which_model.sh` — there is no stored value here to go stale** (Secretary §20). `scripts/which_model.sh --check` fails if any file starts storing one again. Every dispatch still names its model explicitly; nothing inherits. |
| Session transcript | `~/.claude/projects/<same-slug>/bb5dd04f-6533-4b47-9baf-2b6833f68026.jsonl` |

The general form for this trunk: **HEAD sha + WAKE.md AS OF + the constitution pair + the memory
dir + the declared model.** Two of the five (universal CLAUDE.md, memory) mutate outside this
repo's history — a session is NOT fully reproducible from the repo alone, and this page says so
rather than implying otherwise.

## How this trunk stays conformant (instruments, not promises)

- `scripts/lint.sh` — 4 checks, selftest-proven, run at every close (`--selftest` proves each
  failable).
- `/wake` self-test — procedure-repo binding, printed PASS/FAIL every wake.
- `/su-compact` — fixed 4-step close: durable record → verify (numbers, not assurances) → commit →
  boundary block.
- Clock-then-stamp — `date`, READ it, then write; instrument in progress (U8, this trunk owns it).

## Divergences from siblings, with reasons (register lives in the slate)

- **No git remote** — deliberate: work-adjacent content is the program's highest-consequence
  material and git history is a one-way ratchet. Cost and incident history are recorded honestly in
  the slate's register; the gate is Jon's to open.
- **No canonical/connector branch** — consequence of no-remote; the claude.ai layer cannot read
  this wiki. Recorded as a cost, not hidden.
- **Naming**: kebab-case, no uuid6 suffix (chosen 08-14, recorded in `wiki/SCHEMA.md`).
