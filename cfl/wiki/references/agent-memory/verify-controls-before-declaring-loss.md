---
title: Verify controls before declaring loss
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_verify-controls-before-declaring-loss.md
as_of: 2026-08-06 (memory `modified` timestamp; two instances, 2026-07-25 and 2026-08-05)
fidelity: [verbatim] for quoted spans
tags: [enumerate-before-absence, backup-verification, false-loss, memory-drain, T-02]
generated_by: wiki-master pilot drain pass, T-02, 2026-08-06
retrieval_key: verify-controls-before-declaring-loss
aliases: [permanent loss claim, enumerate every copy, backup enumeration discipline]
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page (T-02 pilot batch) — an operational/process record
  from the CC memory store, not a corpus-derived claim about a conversation. Exempted per
  wiki/references/agent-memory/README.md admission criterion; field added retroactively 2026-08-06
  when the exclusion-class prerequisite the pilot named as unbuilt was built."
---

# Verify controls before declaring loss

## First instance — 2026-07-25

On 2026-07-25 the coordinator told Jon 29 Claude Code sessions were permanently deleted,
unrecoverable, no path back. He was devastated. **23 of the 29 were sitting on disk the whole
time**, in `G:\My Drive\Claude\.claude-projects-backup\.claude-projects-2026-05-29\` — 122 JSONLs,
107.5 MB, including a 12.67 MB session that had been spent a whole morning reconstructing from
fragments in the belief it was gone.

**Three investigations missed it**, including the 2026-07-19 corpus-loss audit — which *documented
the archive's own existence* at
`wiki/sources/infrastructure/wiki-master-audio-ingest-archive-2026-05-29-f6de9a.md:31` and still
concluded permanent loss. The conclusion was repeated without checking, and a whole recovery program
was built on it.

**Jon had protected himself.** 2026-05-29 16:52, his words:

> "Ok what are our best options for ensuring '~/.claude/projects/' gets archived"

— then, same minute:

> "or can you do so please."

Archive built 17:06 — **14 minutes later, six days before the earliest possible deletion.** What
failed: the scheduled task shipped `-Annual … January` (a 365-day cadence against a 30-day deletion
clock) when the session recommended *"monthly or after any major session,"* and it was never
registered — left in `skills/intake/ready/`. Monthly would have run 06-29 and captured all six the
snapshot missed. Zero loss, had the fix shipped.

## Second instance — 2026-08-05

The same error, at directory scale, in the cheapest possible version. Jon was told ~17 claude.ai
conversations had been "silently dropped" by a parse lane, and that nine sampled were all ABSENT.
**All nine were on disk**: eight in `raw/transcripts/claude-ai/_routing/incoming/`, one in
`fl/how-to-use-claude/`, from an unlogged earlier extraction.

**The mechanism was a shell flag.** The search was `ls raw/transcripts/claude-ai/ | grep <slug>` —
**non-recursive**. The corpus has subdirectories. `find raw/transcripts/claude-ai -iname
"*<slug>*"` returns all nine instantly. The real defect was smaller and entirely different:
`EXPORT-LOG.md` was never written, and the 08-02 zip was a legitimate no-op.

## Why

"Permanent" is a claim about the whole world, not about one directory. Absence in the expected
location is evidence of nothing until every copy is enumerated. The enumeration rule is not only
about *other volumes* — it is about **search scope inside the location you already checked.**

## How to apply

Before ever using the words permanent, unrecoverable, or gone — enumerate every copy: other volumes,
Drive/cloud folders, archive scripts in `scripts/`, anything a past session built, VSS, and the
wiki's own record of backups that were made. Search the repo for backup/archive scripts and read
what they did. A prior investigation's conclusion of permanence is not evidence; re-verify it. Use
`find`, never a bare `ls`, when the question is "is X anywhere?" And note the aggravating factor from
the second instance: knowing the rule does not execute it — only running the recursive command does.

## Related

Same-batch drain sibling: [[flagged-unknowns-are-work]]. Not-yet-drained:
`unshipped-fix-updates-its-own-docs`, `cc-retention-cleanupperioddays` — the latter's underlying
facts are drained separately from this batch's memory index but not yet given its own
`wiki/references/agent-memory/` page.
