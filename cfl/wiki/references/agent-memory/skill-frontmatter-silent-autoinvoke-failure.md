---
title: Skill frontmatter — silent auto-invoke failure
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-AGENTMEM; sub: wiki 4 vs skills 3 on authored labels"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\project_skill-frontmatter-silent-autoinvoke-failure.md
as_of: 2026-07-26 (memory `modified` timestamp)
fidelity: [verbatim] for quoted spans
tags: [skill-frontmatter, silent-failure, lint-skills, memory-drain, T-02]
generated_by: wiki-master pilot drain pass, T-02, 2026-08-06
retrieval_key: skill-frontmatter-silent-autoinvoke-failure
aliases: [BOM skill bug, unquoted colon YAML bug, ghost-invoke skill]
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page (T-02 pilot batch) — an operational/process record
  from the CC memory store, not a corpus-derived claim about a conversation. Exempted per
  wiki/references/agent-memory/README.md admission criterion; field added retroactively 2026-08-06
  when the exclusion-class prerequisite the pilot named as unbuilt was built."
---

# Skill frontmatter — silent auto-invoke failure

## The finding

Official Claude Code docs (code.claude.com/docs/en/skills), verbatim:

> "If the frontmatter YAML is malformed, Claude Code loads the skill body with empty metadata, so
> `/skill-name` still works but Claude has no `description` to match against. Run with `--debug` to
> see the parse error."

**So a malformed `SKILL.md` fails silently** — the skill looks installed, is callable explicitly, and
simply never fires on its own triggers. Nothing is reported.

Found 2026-07-26 (Herald reported; verified independently before acting, per Jon's *"its possible the
herald is wrong"*):

- **UTF-8 BOM (`ef bb bf`) before the opening `---`** on 5 skills including **wiki-master**.
  Mechanism demonstrated: with a plain `utf-8` decode, `text.startswith("---")` is **False**, so the
  standard frontmatter guard finds nothing. A `utf-8-sig` decode hides it entirely — whether the bug
  appears depends on how the reader opened the file, which is why it survived.
- **Unquoted `": "` inside a plain YAML scalar** (e.g. `description: ... Invoked when: ...`) → hard
  `ScannerError: mapping values are not allowed here`. Live in **14 of 33 skills**. Fix: `>-` folded
  block.
- **Dead repo pointers.** `session-order/SKILL.md` — the *cold-open* skill — named 8 files across its
  reading lists; **6 did not exist anywhere in the repo**, renamed into `skills/<name>/SKILL.md` long
  before. Every cold open since either burned turns hunting or skipped grounding.

**Also documented:** all frontmatter fields are optional, only `description` is *recommended*; there
is a **1,536-character cap** on combined `description` + `when_to_use`.

**Not documented, so not asserted as fact:** whether the parser is strict YAML, and whether a BOM
specifically breaks it. The BOM has a demonstrated mechanism; the `": "` class is a real spec
violation whose *runtime* impact is unverified — a lenient line-based reader tolerates it, and this
repo's own parsers do exactly that. Empirical path if it matters: `--debug` surfaces the parse error.

## How to apply

Run `python scripts/audit/lint_skills.py --strict` (built 2026-07-26 — checks BOM, YAML validity,
required fields, the 1,536 cap, and dead repo pointers; grades CONFIRMED vs SPEC separately). Repo
`skills/` is the source of truth; `~/.claude/skills/` needs `sync-universal.sh` after any fix or the
deployed copy keeps the defect.

## Related

Same-batch drain siblings: [[derive-dont-record]], [[mirror-before-jon]]. `T-16` in
`exchange/RATIFIED-BUT-UNAPPLIED-2026-08-05.md` names a live recurrence of this same ghost-skill
class (`SESSION-LIFECYCLE-SKILL.md`, deployed, no repo counterpart) — not itself drained by this
batch, cross-referenced for continuity.
