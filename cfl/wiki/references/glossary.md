---
title: "Glossary — plain-English decoder for CFL program terms"
date: 2026-08-29
kind: reference
audience_tier: any
reader_token_cost: 1800
---

# Glossary

This page decodes the coined terms that show up in CFL's PRs, wiki pages, and exchange letters —
one plain-English meaning per term, no shorthand inside a definition without its own entry here.
It exists so Jon (or anyone else) can read a PR-2 artifact cold and know what every word means
without digging through the underlying files. **This discharges PR-1's promise #1** — the glossary
PR-1 said would land in PR-2's base (see `exchange/FOR-JON-REVIEW/T-10-six-promise-score-2026-08-28.md`,
row 1, previously the only NOT-DONE promise of six).

This page does not replace `wiki/references/vocabulary.md`, which reserves specific meanings for
words that have been used ambiguously (like "branch," "gate," "Herald") and records what each word
must NOT mean. This page is a decoder for reading; that page is a reservation for writing. See the
note at the bottom for which page has authority over what.

---

## Roles & structure

**coordinator** — a session role (not a file, not a person) that runs the top-level work for one
trunk. It doesn't do the work itself — it dispatches other sessions ("seats") to do it, and reviews
what comes back. *Universal across trunks* — every trunk (CFL, Personal, Professional, Secretary)
runs one; this glossary is CFL's, but the term means the same everywhere. Sources: the charter at
`exchange/coordination-charter-2026-07-21.md` and the Coordinator section of `CLAUDE.md` (both
authoritative; this entry is a decoder, not a third authority).

**fable-mirror** — a subagent that answers questions by reading the stored corpus of past
conversations (transcripts, JSONLs). It never acts on live systems and never speaks for Jon or the
coordinator — it only reports what the record says was said. Sources: the agent definition at
`.claude/agents/fable-mirror.md` and the Fable-Mirror section of `CLAUDE.md`; on any wording
conflict those two govern and this entry is the one that must change. *(This wording caused
defects before — "advisory" once read as "optional" until charter A3 retired that reading; hence
the source pointers.)*

**lane** — one thread of work carried out by a dispatched session (usually a background one),
pursuing a single ticket or question to completion.

**seat** — one running session occupying a role. Multiple seats can exist for one trunk at once
(a foreground coordinator seat plus one or more background lanes).

**sitting** — a scheduled block of time where Jon reviews work in person (as opposed to work
happening unattended between sittings). PR-2's review on 2026-08-29 is "the sitting."

**trunk** — one of Jon's separate coordinator projects (CFL is one trunk; Personal, Professional,
and others are separate trunks). Not the same as a git branch, a repo, or a wiki subfolder — see
`vocabulary.md`'s `trunk` entry for the live ambiguity about exactly which trunks count.

---

## Rituals & boundaries

**CARRIER.md** — a compact file read at every session open, sized to survive being carried through
a context compaction intact. Holds clocks, paths, gates, and other facts that are expensive to
re-derive.

**Jon Gate** — a checkpoint in a process that requires Jon's explicit approval before proceeding;
no automated or "advisory" source may substitute for it.

**HELD vs. TRIAGE** — two different ways a parked item can wait. HELD means it returns to the same
session later (Jon is still holding it). TRIAGE means it has been handed off elsewhere and this
session's responsibility for it ends.

**seal-before-run** — the discipline of writing down what you expect a test to find, and the
conditions under which the result would count as a loss, *before* running it — so a test can't be
read as confirming whatever it happened to produce.

**standard update (SU) / su-compact** — the ritual a coordinator runs to close out a working
session cleanly: reconcile state, write records, regenerate the read-only `canonical` branch, and
leave the repo in a state a cold session can pick up from.

**WAKE.md** — a file regenerated at every checkpoint that tells a newly-opened session what to read
and where to resume. If its timestamp is old, the previous session stopped without properly
closing out.

**WWJA ("What Would Jon Ask")** — a short battery of questions run before anything is shown to Jon,
that checks whether the record already answers the questions he'd naturally ask about the work, so
he isn't asked something already on file.

---

## Instruments

**canonical branch** — a separate, regenerated git branch holding the subset of the repo the
claude.ai connector reads, rebuilt fresh at every standard update rather than edited directly.
*(Corrected 2026-08-29 on Jon's inline ruling: the old "family/personal content excluded" line
misstated WHY — he wants claude.ai able to read his PII, and PII was never his reason for the
exclusion. The wiki/personal・home・pro exclusion flips to published at the next regeneration —
gate PII-5; the current rule of record is `wiki/references/pii-rule-current.md`.)*

**de-PII derived branch** — a prototype copy of the repo with personally-identifying content
stripped or summarized, built by an automated pass so a version of the project can eventually be
shown to people outside Jon's trust zone. Currently a tested prototype, not yet published.

**graphrag / wiki-query** — two named layers, commonly conflated: **graphrag** is the retrieval
system (`scripts/graphrag/`) — keyword + semantic search plus a link/supersession graph;
**wiki-query** is the SKILL wrapping it, which adds haiku-model discernment of the results and
the honesty grades (REACHABLE is not RETRIEVED; confident-absence is a named failure). Use the
skill, not the bare script, when judgment about the hits matters. Index and other derived bulk
move to the `N:` drive (decision 2026-08-29, Jon's prompt "you are using that right?" — we were
not; first rebuild on N: due at the next index refresh).

**hook** — a shell command Claude Code itself runs automatically at a named lifecycle event
(session start, before a compact, when a subagent stops, and so on). CFL's boundary discipline
rides on hooks: they are what makes a record get written even when no one remembers to write it.
Configured in `.claude/settings.json` — seven event types configured there [measured 2026-08-29
against the live file; a wiki page claiming "six" is corrected per the hook-docs audit]. *(Entry
added 2026-08-29 at Jon's comment "should this be more broadly [visible] in here?" — yes.)*

**PreCompact (hook)** — the hook that fires just before a context compaction, giving the session
one last chance to write its barrier record and receipts to disk before working memory is
summarized away. The receipt files land in `exchange/su-close/precompact/`. CFL's
survive-the-compact machinery depends on this single event firing. [measured 2026-08-29: it fired
at this sitting's own compact and its receipt is on disk]

**cleanupPeriodDays** — the Claude Code retention setting that permanently deletes old session
files at startup (no recycle bin, no recovery path). It destroyed real sessions before it was
found; set to 3650 on 2026-07-25. The named reason "no deletion" is an obligation here: this
setting is the known destroyer the obligation guards against. [cited:
`wiki/references/agent-memory/cc-retention-cleanupperioddays.md`]

**heartbeat battery** — a set of roughly ten automated checks run at session barriers (like close or
compact) that catch known failure patterns (like a stale index, or an instrument that reports OK
when it shouldn't) before they cause damage silently.

**probe registry** — an append-only log of tests ("probes") that have been run against the system,
each with what it expected to find and whether it passed. New entries are added automatically
whenever a correction, a failed search, or a question to Jon reveals something worth testing going
forward.

**wayfinder map** — a tracker file (in `wiki/tracker/`) that lays out a piece of work: its
destination, its open tickets, decisions made so far, and what's explicitly out of scope. More than
one can be "LIVE" at once, covering different scopes of work.

**WORK-CLAIMS (TAKE/DONE)** — a simple shared ledger where a seat records that it has taken
("TAKE") a piece of work, and later marks it finished ("DONE"), so two seats don't duplicate the
same work without knowing about each other.

---

## Records & provenance

**compact / context compaction** — what happens when a session's working context fills up: it is
summarized down and the session continues from the summary. A compact is the program's named
destroyer of unwritten state, which is why records are written *before* one ("barrier records").

**DECISIONS ledger (D-numbers)** — `wiki/DECISIONS.md`, the numbered list of binding rulings
(D-001, D-015, …), most of them Jon's. When a PR says "per D-015," it means that numbered ruling.
D-015 specifically: Jon's inspection of the de-PII derived branch IS the bright-line privacy
ruling — his reading of it, not a separate approval step, settles the line.

**barrier record** — a snapshot of a session's state (what it was doing, what it learned) written
at a "barrier" moment — compacting context, closing the session, dispatching a branch of work, or a
dispatched branch reporting back ("fold-in"). Part of the memory-core system
(`skills/memory-core/references/SPEC.md`).

**consolidation** — a housekeeping pass, meant to run at every session close, that merges duplicate
memory records, marks stale ones as lower-priority (never deletes them), and promotes ones that
keep recurring.

**exchange letters (inbound / outbox)** — messages passed between trunks or between a trunk and Jon,
filed as dated files under `exchange/`. "Inbound" is what arrived; "outbox" is what a trunk sent
out — both need to actually be read, not just written, for the channel to work.

**[measured] / [relayed] / [recalled]** — tags marking how confident a claim in a wiki page or
report is. `[measured]` means someone ran a check or command themselves, right now, and is
reporting the actual result. `[relayed]` means the claim came from someone else's report, not
verified firsthand. `[recalled]` means it's being stated from memory without re-checking. Always
read the tag — a relayed or recalled claim can be wrong in ways a measured one usually isn't.

**routing ledger** — a table tracking where a given piece of content (an utterance, a finding) was
supposed to go and whether it actually landed there — used to catch the difference between "this
was written somewhere" and "this reached the person or system meant to act on it."

**the laws file** — a running, append-only record of hard-won operating rules for this program
(patterns of failure that recurred and got named so they'd be caught faster next time). Distinct
from a wayfinder map: the laws file accumulates general rules, a wayfinder map tracks one specific
piece of work.

**tier-0 index** — the always-loaded summary layer of the memory-core system: short entries for
every stored memory, capped in size so a session can load the whole index cheaply and only fetch a
full memory body when it actually needs it.

**template-eval** — a scoring pass over how well a memory-core template performs (whether a fresh
reader/session can actually make use of what it stored), run to check the templates are doing their
job rather than just existing.

**"a letter is a measurement taken at its timestamp" (law E8)** — the idea that a written record (a letter,
a report) reflects what was true when it was written, and may already be stale by the time it's
read — so an old letter shouldn't be treated as still-current without checking.

**unsaid ledger** — a table, required at every session boundary, where the closing session lists
everything it knows is deficient, unproven, or over-claimed in the work it ships — written where
it is cheapest (with full context) instead of discovered at review time. It produced zero entries
at every boundary through 08-28 (that regression is stated in PR-2's promise retrospective); its
first filled, tool-verified instance was written at the 2026-08-29 compact boundary.

---

**Where a term's authority lives:** for which *reserved meaning* a word must carry going forward
(and which meanings it must NOT carry), see `wiki/references/vocabulary.md` — that page is the
authority on term reservations. For the normative, field-by-field definitions of memory-core's
internal objects (barrier records, the schema, error semantics), see
`skills/memory-core/references/SPEC.md` — that page is the authority on memory-core internals. This
page is a reading aid for both; it does not override either.
