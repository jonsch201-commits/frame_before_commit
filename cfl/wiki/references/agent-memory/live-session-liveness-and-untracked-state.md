---
title: Live-session liveness and untracked working-tree state
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-AGENTMEM; sub: no sub-branch evidence above the floor (best wiki 0 < 2; a lone corroborating tag does not decide)"
source_kind: reference
origin: C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer\memory\feedback_live-session-liveness-and-untracked-state.md
as_of: undated (source has no `modified` field)
fidelity: [verbatim] for quoted spans
tags: [memory-drain, T-02, liveness, untracked-state]
generated_by: wiki-master drain pass, T-02 continuation, 2026-08-06
retrieval_key: live-session-liveness-and-untracked-state
coverage_class: untraced-by-design
coverage_class_reason: "agent-memory drain page — an operational/process record from
  the CC memory store, not a corpus-derived claim about a conversation. E2's turn-anchor
  requirement does not apply by kind; exempted per wiki/references/agent-memory/README.md
  admission criterion, not by omission."
---

# Live-session liveness and untracked working-tree state

Two findings measured during the 2026-07-17 standard update, both instances of one root: **work that
is done correctly and then never promoted anywhere a second reader can see.**

**1. Liveness — "still open" must never mean "don't write."**
`da51cc` ran 11 days and was still live; its MD grew 462,309 → 1,326,729 chars (+187%), and **1,388
msgs / ~980,000 chars (74% of its char mass) sat in no wiki page.** Its page had gated its own refresh
on two *unreachable* triggers: a `--include-thinking` extraction (impossible — CC thinking is
encrypted-in-signature, see [[cc-jsonl-thinking-signature-only]]) and "at real session-close" (never
came). It honestly labelled itself PROVISIONAL and froze.

**Why:** you cannot write a *final* page for a live session, but nothing stops a **snapshot with an
explicit coverage watermark** (`liveness: LIVE`, `coverage_through:`, `last_snapshot:`) superseded
additively later. Prose like "⚠️ PROVISIONAL" says a page is incomplete but not *how*, *through when*,
or *whether it moved* — nothing to detect or alarm on. A watermark is a number lint can fail. Note the
inversion this produces: **the longer a session runs, the more it produces and the LESS likely it is to
be captured.** Also already forbidden by `SCHEMA.md:223` ("compaction ≠ wiki record") — so it's
enforcement, not a new rule.

**How to apply:** re-snapshot every live session on ANY positive delta at EVERY standard update; key
detection on the JSONL's **last-turn timestamp** (never `md✗` or `--update` mtime — see
[[md-not-uncaptured-authoritative-disposition]]). Ban supersede triggers that cannot fire. Slice the
JSONL by timestamp and hand only the delta to a subagent — cheap. Jon's 07-13 brief said "da51cc is
OPEN — do not extract it," which was *reasonable that day*; the defect was it becoming a standing
default. **Reasonable one-day instructions silently become standing policy — re-check them.**

**2. The untracked-working-tree state class.**
`wiki/intake-triage/` held **12 untracked packets inside `wiki/`** (a dir in no `SCHEMA.md`), **10
addressed `to: [wiki-master]`**, while `raw/intake/` — the documented destination the SU checks — sat
**empty since 07-08**. Phase 4 was *correct and useless* for nine days. `skip-registry.md` — which the
D3 rule names "the durable record" — is itself gitignored, the only artifact distinguishing
"deliberately skipped" from "never seen."

**Why:** the repo lives on Drive, so **the working tree feels like publication and isn't.** It looks
saved; Drive even syncs it; it's not in the record. Same root as
[[drive-worktree-mirror-poisoning]] and [[drive-lag-stale-read-hazard]], seen from the write side.

**How to apply:** `git status --porcelain wiki/` returning anything = **hard error** (wiki/ is
wiki-master's exclusive domain; an untracked file there is by definition a misdelivery). Never
classify an unknown file as "debris" without inspecting it — the 07-13 SU did exactly that and P1
re-found the same pile 2 days later; **it grew 8 → 12 anyway. A correct diagnosis, filed, does not
stop the growth** — escalate to Jon by name. An SU must never leave the main checkout on a non-`main`
branch. And: **a silent gap between two correct behaviors is not caught by either party being more
careful** — the sender thought it delivered, the receiver truthfully reported an empty box.
