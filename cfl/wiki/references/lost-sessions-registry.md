---
title: "Permanently lost Claude Code sessions — the tombstone registry"
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-REF; sub: sub-branch too close to call: wiki 2 vs corpus 2 (margin < 1)"
date: 2026-07-26
updated: 2026-07-28 — subjects/pointers added for the confirmed-3 residual (R2)
maintained_by: scripts/audit/cc_corpus_gap.py (the COUNT is derived; this file records WHICH)
status: RECORD — retracted twice 2026-07-27, corrected count 3 (not 29); subjects confirmed 2026-07-28
---

> # ⛔⛔ RETRACTED TWICE 2026-07-27 — THE NUMBER IS **3**, AND IT WAS NEVER ABOUT LOSS
>
> **Second retraction, same day, and it goes further than the first.** The instrument behind this
> registry was reading the wrong frontmatter field. `cc_corpus_gap.py` read `source_id:`; **26
> extracts declare `uuid:`**. The key came back empty, the fallback took `filename[:6]` — the
> literal string **`"code-2"`** for every `code-2026-*.md` — that matched no session id, and every
> one of those files fell through to `lost`.
>
> **It was not finding losses. It was finding a field name.**
>
> **Corrected count: 3 permanently lost, not 29** — and all three are `D:\Personal Automation`,
> none of them CFL. `dba2c0bd`, which this program called *the* largest single loss and planned a
> reconstruction around, **has a real extract on disk.** So do `707392f3`, `1259570f`, `2444c922`,
> and `c5644bf9` (12.67 MB, 1,752 records).
>
> **The near-miss is the lesson.** A reconstruction of `dba2c0bd` was dispatched and stopped before
> it wrote anything. herald-wiki named the hazard first: *"Reconstructing a session that exists is
> not a wasted afternoon — it is a **fabricated primary entering a corpus that grades provenance**."*
>
> **And an agent had already begun bending the corpus to fit the broken instrument** — it added
> `source_id:` to 20 raw files "to align with `cc_corpus_gap.py` expectations." The data it wrote
> was accurate, so nothing was corrupted; **but the direction was wrong.** When a file and an
> instrument disagree, the instrument is the hypothesis.
>
> Everything in the first retraction below still stands — 22 sessions did come back from the
> snapshot, 110.6 MB, 4,066 turns. **This retraction says the search should never have concluded at
> all.**
>
> ---
>
> # ⛔ FIRST RETRACTION 2026-07-27 — 22 OF THESE 29 ARE ALIVE
>
> **This registry was wrong on the day it was published, and wrong in the most damaging direction.**
> The herald-wiki coordinator checked what CFL asserted and found **22 of the 29 sitting in a Drive
> snapshot** at `.claude-projects-backup/.claude-projects-2026-05-29/` — 122 JSONLs, 110 MB.
> Independently verified before this banner was written: 22 of the 29 ids below resolve there,
> including **`ee177e24` (14.7 MB)** and **`c5644bf9` (12.7 MB)**, both of which this program had
> named as permanent losses.
>
> **A tombstone is worse than silence, because it stops the search.** Silence invites a look. A
> registry titled *"permanently lost"* tells the next reader not to bother — and it carried a
> methodology section explaining how carefully the conclusion was reached, which makes it more
> convincing and no more true.
>
> **What the check actually was:** `history.jsonl` proves a session existed. The registry then
> checked `~/.claude/projects/` and the corpus, found nothing, and concluded "permanent." **It never
> checked the backup directory** — which this repo's own 2026-07-19 audit had already documented,
> and which a memory note from 2026-07-25 explicitly warned about after the identical error.
> **Third occurrence of the same mistake, and the first one published.**
>
> **The rule, stated so it survives this file:** *permanent* is a claim about **every copy that has
> ever existed** — projects dir, corpus, quarantine, Drive backups, archive scripts, other volumes,
> and the wiki's own record of prior backups. **Enumerate all of them, name each one you checked, or
> do not use the word.**
>
> Recovery of the 22 is dispatched. The table below is **retained unedited** as the record of what
> was claimed — a retraction that deletes what it retracts is not a retraction — but **no row in it
> may be cited as evidence of loss.** Re-derive with `cc_corpus_gap.py` and a snapshot search.
>
> Found and corrected by **herald-wiki**, not by CFL. The two coordinators check each other; that is
> the only reason this was caught in a day rather than never.



## The confirmed 3 — subjects and disposition (R2, Jon, 2026-07-28)

Following the two retractions above, the corrected residual is exactly the three
`D:\Personal Automation` rows in the table below: `899d6457`, `187e021e`, `367c6ff1`. Jon's own
intuition, verbatim (`raw/intake/jon-train-rulings-words-reify-intent-2026-07-28.md`, R2,
`[TRANSCRIPT:2026-07-28]`): *"This was my attempt to get Plaid set up with you when you were an
earlier sonnet model."* — **CONFIRMED**, subjects identified from `history.jsonl` prompt survivors:

| session id | subject | surviving record |
|---|---|---|
| `899d6457` (2026-03-10, 28 prompts) | `/init`, Plaid/bank-transaction project setup, Amazon order history | `history.jsonl` (Jon's typed side only) |
| `187e021e` (2026-03-11→12, 30 prompts) | Windows reset, BitLocker recovery keys, media-backup concerns | `history.jsonl` |
| `367c6ff1` (2026-03-12, 1 prompt) | Resume artifact of `187e021e`, not a real independent session | `history.jsonl` |

**Additional surviving reference material**, per Jon's follow-on *"If so, just this may be enough
ref material"*: `C:\Users\JonSc\.claude\projects\D--Personal-Automation\memory\MEMORY.md` — full
project state as of Mar 11 (Plaid credentials staged, 4 scripts written, PNC CSV workaround,
family-account decisions).

**Disposition (provisional, per Jon's ruling): let go, with this stub as the pointer.** Search
dated 2026-07-28. Not a tombstone — the standing rule two retractions above established (*"enumerate
every copy... name each one you checked, or do not use the word [permanent]"*) still applies if this
disposition is ever revisited; this entry only records what was found and Jon's provisional call to
stop looking, not a claim that no other copy could exist.

**Open item surfaced, not yet triaged:** `MEMORY.md` carries two never-built Jon requests from
March 2026 — email monitoring, and a media-backup routine (*"Personal photos are top priority"*).
Five months old as of this ingest, no wiki footprint before this entry. Recorded in
`wiki/tracker/open-items.md` (new row, this pass) rather than actioned here — content/routing is
out of scope for a registry update.

**Correction recorded (carried from R2's own text):** the coordinator had earlier carried wrong IDs
for "the lost three" (they were IDs of *recovered* sessions, not lost ones). A fresh instrument
re-run gave the true set reflected in this table. Efficiency Rules #5 ("an alarming finding is a
hypothesis") applied before this was propagated further.

---

# What this is

`history.jsonl` survives the retention sweep that deleted the session JSONLs, so it holds **every
prompt Jon ever typed plus the session id it belonged to** — while the assistant's side of those
conversations is gone. These 29 sessions appear in `history.jsonl` and have **neither a JSONL on
disk nor an extracted markdown anywhere in the corpus.**

**Why this file exists at all.** `cc_corpus_gap.py` re-derives the *count* correctly every run —
that is the right design and this file must never be trusted over it. But the count was only ever
printed to stdout, so **which** sessions were lost lived nowhere anyone would stand. A number that
says "29 lost" and cannot say *which* is not a recovery record; it is an alarm with no address.

**This file is a tombstone, not an inventory.** Nothing here is recoverable from the corpus. What
*is* recoverable is Jon's own prompts, which is why the prompt count is carried per session —
it is the measure of what a reconstruction would have to work from, and it is one-sided by
definition. Never grade anything derived from these as `[TRANSCRIPT]`.

**Cause, resolved 2026-07-25:** Claude Code's `cleanupPeriodDays` defaulted to 30 and deletes at
startup, permanently, with no Recycle Bin and no vendor recovery path. Set to 3650. **The mechanism
is closed; these losses predate the fix.**

**The largest single loss is `dba2c0` — 111 typed prompts.** It was already known absent from the
2026-07-25 archive sweep, and it is the one case confirmed unrecoverable from every backup checked.

## The 29

| session id | Jon prompts | project |
|---|---:|---|
| `dba2c0bd-4008-4c1a-b5f0-905b98234eca` | 111 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `ee177e24-9977-47c6-b76f-d51c57130b66` | 54 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `740c9319-3c02-40cd-ade3-29a8980960f4` | 48 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `c5644bf9-e4d7-4173-b048-aede2e97f4ce` | 47 | `G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer` |
| `bb2b3844-8c6d-4ae3-970a-52d39a65a5e8` | 35 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `41fa027d-4d47-4eff-84c0-51469ab28b06` | 32 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `187e021e-1917-43d2-b612-efe9999df963` | 30 | `D:\Personal Automation` |
| `899d6457-776c-4cb0-be31-a1c078c169ea` | 28 | `D:\Personal Automation` |
| `949f160d-5f4f-49e9-a665-05532c9c403f` | 23 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `ced2a66a-b09e-4660-9300-19de223d129d` | 21 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `2e2c62a6-4462-4d45-b4a4-6c92ffbf0d97` | 21 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `0ceb7eab-143f-4bd3-a1d1-a528bb036e54` | 21 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `73ecce62-7bcd-42b6-8250-968f583de91f` | 20 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `02ff5b1c-ae89-4078-94b8-c1efbca28432` | 20 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `f6de9a4d-d3cb-4f75-8b7e-e390ea052863` | 18 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `96a72e37-e2ba-4a17-8091-7c69b8a05800` | 18 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `e4c39334-8af4-4a81-bfbf-e1e1db41bf77` | 17 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `707392f3-ee51-48b3-9796-3e5a698c546b` | 16 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `6f7600c5-f25a-45f9-a299-95c29661a6e4` | 16 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `8989d108-df73-45d6-90ec-e08b39ef3fb4` | 13 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `e52ed27e-1e6a-4bf2-8688-b3a8e8ca05a1` | 10 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `b40394b3-2d1b-4b4a-93bb-473ee363a119` | 10 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `000a3603-a018-4982-af76-7e4e9387ec78` | 8 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `f9cdf44c-aa68-47d7-aaab-b01ca4246556` | 7 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `1259570f-2736-4467-bfd2-0faa64519eb4` | 6 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `2444c922-622c-4abb-a566-5d332bcc8c31` | 4 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `97420285-45f6-4232-a2cb-104aaac16f79` | 2 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `6bc1d286-ef82-4bd3-a759-a283cf6d21eb` | 1 | `G:\My Drive\Claude\Claude Foundational Layer` |
| `367c6ff1-bc36-4985-8e82-2af68e1e4205` | 1 | `D:\Personal Automation` |

---

**Total: 29 sessions, 658 typed prompts.** Re-derive with
`python scripts/audit/cc_corpus_gap.py --list`. **If that command disagrees with this table, it is
right and this file is stale** — the script reads ground truth and this file records a moment.
