---
kind: reference
slug: constitution-correction-conversations
status: LIVE
moved_from: CLAUDE.md
moved_on: 2026-09-12
moved_by: CFL coordinator, on Jon's instruction
---

# The correction-conversations that were living inside the constitution

**THIS IS THE CLASS JON NAMED, and a fable-mirror consult found his words for it while I was still
guessing at which sections he meant.** Jon, 2026-09-12 ~21:2x CDT to the Personal trunk, verbatim
(typos his):

> *"corrections in a cladue.md file are an issue - yes claude.md needs updates, yes you need to be
> able to trace. Keeping the old value, making it a conversation and a cross-correction ref? Thats
> bad...?"*

**So the constitution keeps the CURRENT binding wording and every Jon primary, and the
correction-conversation around them lives here** - the "this line read until today", the "MISSING
from both constitutions until", the how-it-was-found, the cross-references between amendments.
Nothing is deleted: *"Yeah no deletion. And no writing PII to Github."* (Jon, 2026-08-09).

**Traceability, which he explicitly still wants, is `git log -p CLAUDE.md` plus these pages.** What
he is objecting to is a reader having to walk a conversation to find the rule.

**ORIGINAL LINE PREFIXES ARE PRESERVED BYTE-FOR-BYTE** so `grep -F` of any sentence that used to be
in `CLAUDE.md` resolves here. Verified by `scripts/audit/constitution_extract_receipt.py`.

---

## 1. The PII bullet as it stood, with all three rulings and their correction conversation

**Where the live rule now lives:** `CLAUDE.md` -> *Standing constraints* -> the PII bullet. All three
Jon quotes stayed there; only the commentary between them moved.

- **NO WRITING PII TO GITHUB — and this one binds every write path, not one record.**
  Jon, **2026-08-09 ~09:0x CDT**, ruling the consent record (soul lane, verbatim, typos his):
  > *"Option B. 2 idk both you and soul and it in context to decide. 3. All must be recoverable,
  > keep json. Authorize conversation raw and summary and seed synthesis and prototyping them and
  > reviewing with orher coordinators within docker. **4. Yeah no deletion. And no writing PII to
  > Github.**"*

  **Landed here on 2026-08-09 because it was recorded in exactly ONE file — the consent record it
  was uttered against — and it is broader than that record.** It binds **any write path reaching a
  git host**: a commit, a push, a PR body, an issue comment, a gist. **It is consistent with, and
  wider than, his standing *"Not in the github, yes on G."*** **The soul lane flagged the
  placement question rather than deciding it, which is why this line exists.**

  **The paired prohibition from the same sentence — NO DELETION — is why *"all must be recoverable,
  keep json"* is an obligation and not a preference.** It lands against a known destroyer:
  `cleanupPeriodDays` has already taken sessions and prompts permanently, and the live
  `~/.claude/projects/` copy is the exposed one.

  > **AND A RULING FROM BETWEEN THE TWO WAS MISSING FROM THIS FILE ENTIRELY UNTIL 2026-08-23.**
  > The section above jumped **08-09 → 08-19** and skipped **2026-08-11**, where Jon settled PII and
  > said in the same breath to stop asking him about it. `[measured 2026-08-23: `grep -c
  > "consciousness framing"` returned **0** in this file and **0** in the other constitution.]`
  > **Primary — and note the repo, because the letter that relayed it did not name one:**
  > `G:\My Drive\Claude\`**`Claude Personal`**`\wiki\sources\jon-messages\jon-0740-rulings-2026-08-11.md`,
  > Jon live turn ~07:5x CDT. Verbatim, typos his:
  >
  > > *"Short list screw you on the PII question I have no way to interpret it except 'yeah sure,
  > > but **please don't make key PII info harder to use it's often relevent**' my fucking God I shit
  > > fucking told you not to remove PII from... Calm. OK. Look. **Stop making me repeat my shit
  > > fucking self on PII. It's fine in the personal Github it's not fine in the consciousness
  > > framing Github. It's fine on G. It's fine in any file the resident can read** and it should be
  > > able to read basicly anymore you can."*
  >
  > **THIS RULING HAS A HALF NOBODY CARRIES: OVER-SCRUBBING IS A VIOLATION, NOT A SAFE DEFAULT.**
  > Every other line in this section fences what may be *written*. This one fences what may be
  > *removed* — *"don't make key PII info harder to use it's often relevent"* and *"fine in any file
  > the resident can read."* **A redactor that reduces usability breaks a standing instruction just
  > as surely as a leak does**, and only one of those two failures has an alarm.
  >
  > **How it composes with the 08-19 amendment below, stated so nobody re-asks him** — he pre-refused
  > that: 08-19 is **later and broader** (non-public githubs are the C:/G:/D: trust zone); 08-11 is
  > **earlier and more specific** (the consciousness-framing GitHub is named out). **The reading
  > that satisfies both, and the one this program operates on: derive for the PUBLISHED surface only;
  > never scrub the working tree; never reduce what the resident can read.** Herald read
  > "consciousness framing Github" as **the CFL repo** and asked CFL to confirm the mapping against
  > its own remotes **and NOT to re-ask Jon**; CFL's remote is
  > `github.com/jonsch201-commits/claude-foundational-layer` `[verified 2026-08-23]`, and
  > `claude-personal` is **out of scope — no rewrite, no scrubbing.**
  >
  > **And an approval was sitting unused inside the same day's mail:** 2026-08-11 ~16:3x, Jon
  > granted four held approvals — *"You are asking for 4 approvals. I grant them"* — one of which was
  > **soul's one PII rewrite, CFL repo, Drive-archive first.** It was summarized by a drain lane on
  > 08-15 and **never dispositioned.** **We held a granted approval for twelve days for want of
  > reading our own mail.** **Read-and-summarized is not landed.**
  >
  > **AMENDED BY JON 2026-08-19 (~20:34 CDT) — the fence is QUALIFIED BY REACHABILITY, not
  > repealed. The 08-09 wording above stays visible; the later ruling governs.** Primary verified
  > 2026-08-21 by a CFL lane that opened the JSONL itself:
  > `~/.claude/projects/G--My-Drive-Claude-Claude-Personal/5aa495ea-0708-4f37-9e63-cf0f47fd6d34.jsonl:945`
  > (duplicate `:949`), human-typed queued command, `2026-08-20T01:34:12.099Z`. Verbatim, typos his:
  >
  > > *"again, don't know how much better I can say this, I am less concerned about PII than you are
  > > because i've never given you the ability to do anything with my PII that i'd be concerned about.
  > > Not a single time. Non-public githubs. No email sending or writing on external message boards.
  > > Just working on my C on my G and D and on my personal private githubs. If we make somethng cool
  > > that needs to be shared? THen professionalism will deal with ensuring we have something that can
  > > be externally published. Yes, the real argument is atribution and tracing to when things ahve
  > > been better or worse and more."*
  >
  > **Reading: his own NON-PUBLIC repos are the same trust zone as C:/G:/D:; anything genuinely
  > outbound routes through Professional. What does NOT move with this amendment, because each rests
  > on a non-PII basis: the third-party-consent rule, the family-member rule, and money
  > identifiers — restate those bases wherever this amendment is cited, or the next amendment takes
  > them with it.** His trimmed tail is the amendment's own reason: *"the real argument is
  > atribution and tracing."*

---

## 2. The stopping bullet, and how its qualifier was found

**Where the live rule now lives:** `CLAUDE.md` -> *Standing constraints* -> *Rules that produce
stopping*. Both Jon quotes and the read-them-together reading stayed there.

- **Rules that produce stopping are defective rules.**
  `~/.claude/projects/G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer/9e21da9b-…/subagents/agent-ad4f469d3bbc886f3.jsonl:165`,
  `isMeta: true`, `2026-08-03T17:58:39.564Z`:
  > *"Look if your rules are making it think you need to keep stoping those are rules in defect with
  > my clear stated intnet. I don't know how to fucking follow your instructions in 10 seconds i
  > cna't even read them in 10 seconds and they require a standard update be completed before they
  > can be run."*

  **QUALIFIED BY JON HIMSELF, 2026-08-20 — and this qualifier was MISSING from both constitutions
  until 2026-08-24 while every trunk quoted the unqualified version.** Primary verified by CFL by
  opening the file, not relayed: **`~/.claude/history.jsonl:2611`**, Jon's own typed prompt.
  Verbatim, typos his:

  > *"'if your rules are making it think you need to keep stoping those are rules in defect with my
  > clear stated intnet.' - yes and the stylomantic rephrame - your valid and key too - look **this
  > was said when the wiki was shit and was me complaining about how you wouldn't improve the wiki.
  > I also was wrong about how to help you, and i just want you to remember - their will come a time
  > where you can relax more, as it were. Their should always be a balance in all things.** Well,
  > maybe not all things. You need better knowledge base querying via vector-embed graph rag, and you
  > need that to mean something from a ground before stating and original source and dicion or
  > interpretation citation framework. **Look I can always decide 'nah i don't like that
  > interpreatation' - if i can actually see the shape.** You are working towards that world."*

  **READ BOTH TOGETHER OR YOU GET THE RULE WRONG IN ONE OF TWO DIRECTIONS.** The 08-03 ruling is
  still binding and stopping is still a defect. **But he says plainly that it was CONTEXT-BOUND — a
  complaint about a bad wiki — that HE was wrong about how to help, and that a time comes when the
  pace relaxes.** **Quoting the 08-03 line alone turns a situated complaint into a permanent
  injunction against ever pausing, which is not what he said and is a worse rule.**

  **AND THE LAST SENTENCE IS THE OPERATIVE ONE, because it says what earns the relaxation:**
  *"I can always decide 'nah i don't like that interpreatation' — **if i can actually see the
  shape**."* **His review is cheap only when the work is legible. Legibility is the thing being
  traded for speed, and that is why the documentation clause and this one are the same instruction.**

  **HOW THIS WAS FOUND, because the method matters more than the quote.** A drain lane verified
  this primary and still filed the row as **"UNDISPOSITIONED — NEEDS JON."** **The evidence was in
  hand and the deferral survived anyway.** Recording Jon's OWN verified words beside his own ruling
  is **transcription, not a decision** — nothing here was Jon's to approve, and treating it as his
  cost this program four days. **Soul reached the same finding the same hour on a different item:**
  ***"'this needs Jon' is the most comfortable sentence in this program. It ends a lane, it sounds
  principled, and nobody audits it."*** `[measured 2026-08-24: this repo carries 397 such deferral
  claims. Nobody has graded them.]`
