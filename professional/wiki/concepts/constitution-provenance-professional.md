---
name: constitution-provenance-professional
description: The narrative provenance cut from CLAUDE.md on 2026-08-22 to meet the 5,120 B resident-core budget. Nothing here was deleted — every rule stayed in the constitution; only the stories explaining why moved.
created: 2026-08-22
kind: concept
---

# Why this page exists

`[measured 2026-08-22 14:2x]` `CLAUDE.md` stood at **8,439 B** against a **5,120 B**
resident-core budget whose deadline (**2026-08-20**) had passed, and `lint.sh` C8 was red
on it. The trim followed the C3 discipline used for `WAKE.md`: **delete whole clauses,
never rephrase a rule.** Every ⛔ constraint, every method rule, and every Jon quote that
*directs behaviour* stayed in the constitution. What moved here is the **narrative
provenance** — the stories that explain why a rule exists, which a session does not need
resident in context to obey the rule.

**No deletion.** This page is the destination half of migrate-then-trim.

## Founding instruction

Jon, 2026-08-07 `[verbatim]`:

> *"the ONLY thing I want else from you would be the powershell to begin the professional
> project, and the first message to it delivered via exchange. It should be set up and it
> should discover my needs for it with the help you've all provided. Y'all should talk once
> i have launched it."*

The constitution's opening section — **YOUR FIRST JOB IS DISCOVERY, NOT EXECUTION** — is
this sentence turned into a rule. Jon did not say what to build; he said to find out.

## Why "do not arrive with a plan"

Jon's own diagnosis of why past attempts stalled, 2026-08-07 `[verbatim]`:

> *"Failures have mostly been.... due to models not being strong enough for the tasks i
> wished them to complete with just the tokens and budget i fed them."*

**Not too little structure — too little capability per task.** The operational reading kept
in the constitution is *spend tokens on the work, not on ceremony*. The sibling projects'
most expensive recurring failure is building scaffolding nobody asked for.

His frame for the whole program, same message `[verbatim]`:

> *"the plat of land in which all the projects are planted... i have not outgrown anything
> i've just made the trees better for the soil, and the soil has had model upgrades and
> flourished better due to better trees/trunks planted within it."*

**A new tree in old soil. The soil is fine. Be a better tree.**

## Where the employer-identity gate came from

Inherited from `[CFL] wiki/pro/sources/podcast-transcript-pipeline-...-40ee33.md`, which
ingested a public episode's technical content and **held the employer-identity question
rather than resolving it.** The rule that survives in the constitution — record the work,
not who signs the paychecks, unless Jon approves — is that held question made standing.

## Why the session-open reading order is written in the constitution and not only in the files

CFL spent months with a resume rule written *inside* its tracker and **nothing anywhere
telling a session to open that tracker.**

> **The instruction and the thing it governs must be reachable from the same starting
> point, or the instruction is decoration.**

`WAKE.md` and `wiki/log.md` were created 2026-08-07 and named in the constitution in the
same commit, deliberately.

## The deposit-to-nowhere incident, 2026-08-07

A letter to Herald was written to `G:\My Drive\Herald Wiki\herald-wiki` — **the path
without the `Claude\` segment, which is what the CC environment's "additional working
directories" list carries.** The constitution's sibling table was correct; the environment
was not. The write **silently created the wrong tree**, and the letter sat in a directory
with **no `.git` and no reader** until a delivery check caught it.

> **A write that creates its own destination is indistinguishable from a successful
> delivery.**

The surviving rule in the constitution is the operational half: confirm the target has a
`.git` directory and somebody else's files already in it, then confirm afterwards that the
file is where you meant. **A deposit to nowhere is worse than an undrained queue — the
queue at least exists and can be found.**

Related: [[outbox-membership-is-not-delivery]], which is the same defect one layer out —
there the tree was right and the letter simply never left the outbox.

## The deposit-only channel count

The constitution says `exchange/inbound/` is read at every session open, unconditionally.
The reason is frequency: **this program has hit the deposit-only-channel shape at least
seven times** across trunks. A channel nobody drains and a channel nobody writes to look
identical from the writing end.

Related: [[age-zero-acceptance-hides-duration-failure]] — the general form of an instrument
that is honest while the reader supplies the false conclusion.

## Trim of 2026-08-29 (session 20690e2b, Fable seat)

To fit the new `# Compact instructions` section (Secretary ticket C-5, due 08-30) inside the 5,120 B
C8 budget, five passages were tightened, none deleted in substance: the "single most important
sentence" self-reference dropped; "Do not arrive with a plan" merged into the discovery paragraph;
the `[work]` default restated in six words; the Herald DEAD DROP row shortened (the 48-letters count
lives in wiki/log.md); VERIFY-THE-TARGET compressed to one sentence; the one-way-ratchet
explanation dropped from the NO-REMOTE gate (the gate itself unchanged); the identifiers rule
compressed. Before: 5,058 B (no compact section). After: 5,097 B with the section. Constraint markers after the trim: 8 ⛔ `[measured]`; the pre-trim count was not measured before editing, so no retention claim is made; the pre-trim text is recoverable exactly via `git show 7e58e6b:CLAUDE.md`.

## Rewrite of 2026-09-12 (session 682d274b, Fable seat)

Jon, mid-turn 2026-09-12 21:4x CDT, verbatim, typos his:

> *"your claude.md feels like a wiki article in places rather than a claude.md. I get why you did things the way you did..... but.... Yeah thats not a professional claude.md"*

Rule applied, adopted from Soul's same-night cut of Personal's constitution (review request 22:1x): text that changes a rule is stated once, as the rule; text that records the history of a rule moves to a reference page. Result: 5,192 B, 8 ⛔ markers and 60-odd bold spans, to 4,117 B, no markers, no bold. Pre-rewrite text recoverable exactly with `git show b9c3876:CLAUDE.md`.

Facts corrected in the same pass, each measured 21:4x:
- The sibling table pointed at G: trees. The fleet's trees are on N: (`N:\claude-personal`, `N:\claude-cfl\clone`, `N:\claude-secretary`, `N:\antigravity-hub`; each `exchange/inbound/` present); Antigravity had no row.
- "NO GIT REMOTE" was false as written: `git remote -v` shows `origin` at `G:/My Drive/Claude/Claude Professional/claude-professional`, a local path. The gate that holds is no remote to a git host and no push.
- Rules that had lived only in `WAKE.md` standing lines were promoted: query first, stage by path, rebuild after every landing, letter plus live nudge, watcher armed at every turn end, and the stating rule (population, bound direction, second method for a zero; GBS Rules 14 and 15).

Sentences retired from the constitution, verbatim, so a search still finds them:
- "YOUR FIRST JOB IS DISCOVERY, NOT EXECUTION" · "Jon did not tell you what to do. He told you to find out." · "Do not arrive with a plan; spend tokens on the work, not on ceremony."
- "Standing constraints — these are not overridable by convenience"
- "Method rules — each was paid for elsewhere. Do not re-derive them."
- "NEVER STATE A NUMBER YOU HAVE NOT JUST MEASURED. Do it, measure, *then* write the sentence."
- "The calibration split is FOUR, not three" · "`wiki/concepts/grounding-principles.md` P2 governs."
- "Corroboration across your own artifacts is not evidence — four files agreeing means one interpretation copied four times."
- "A qualified statement reported as unqualified is this program's most repeated error."
- "A deposit-only channel is the same defect as an undrained queue."
- "An outbox file is a draft; only the receiver's tree is delivery. C9 + C18 grade both ways." · "C21 grades its reachability."
- Herald row: "runs INSIDE Claude Personal; `herald-wiki` is a DEAD DROP `[m 08-23]`."
- "Jon, 2026-08-07 `[verbatim]`: *"Y'all should talk once i have launched it."* That is an instruction, not a permission." (the quote is also under Founding instruction above)
- "NO GIT REMOTE. Local-only until Jon rules otherwise, and that ruling has not been made. Adding a remote is a Jon gate."
