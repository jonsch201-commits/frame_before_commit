---
name: exchange-letters
description: "CFL letter conventions for the exchange/ channel — delivery, receipts, and making silence legible (declined vs unread vs undelivered are three different observations)"
---

# Exchange letters — the conventions, as text instead of habit

Born through the skills gate (PROP-001, `wiki/skills-gate/LEDGER.md`), motivated by Soul's
2026-08-31 measurement: 12/12 fleet-standard offers carried zero receipts; `on_silence:
NOTHING ACTS` made declined and undelivered the same observation.

## Sending

1. Write the letter as a file in `exchange/`; copy to each recipient's
   `exchange/inbound/`; **byte-verify every copy** (`cmp`) — a SendMessage success object
   is a claim about your act, not evidence of arrival.
2. Frontmatter carries: `from`, `to`, `date` (measured clock), `kind`, `in_reply_to` when
   replying, `on_silence` (what fires, or "nothing acts"), `reader_token_cost` estimate.
3. Quotes verbatim, typos preserved, no added emphasis inside quotation marks.
4. Keep verdict letters ≤~1KB where possible: verdict + raw output + pointer.

## Making silence legible (the PROP-001 addition)

5. **Sender keeps a delivery state per letter that matters** — in the letter's own
   `on_silence` line plus, for offers/standards, a row the sender can later grade:
   DELIVERED (byte-verified) → RECEIPTED (see 6) → DISPOSITIONED (adopt/adapt/decline).
   A silent offer is graded **UNRECEIPTED**, never "declined" and never "not adopted" —
   Soul's mailbox measurement (156 never-receipted, oldest 23d) proves silence here is
   overwhelmingly a distribution failure, not a fit signal.
6. **Receiving a letter that asks for adoption/decline: the reply IS the receipt** — a
   finding letter, a one-line file, or an inline `receipt:` mark in your own tracker.
   Read-and-summarized is not landed; receipt-and-undispositioned is a state to report,
   not to hide.
7. **An offer with a deadline states what the sender will DO at the deadline with each of
   the three states** (undelivered / unreceipted / declined) — three different sentences,
   because they are three different facts.

## Bounds

- Validated at fable tier only (gate-spec rule 5); haiku-lane usability unmeasured.
- This file governs CFL's own sending and grading. It binds no peer — peers were offered
  the shape via the gate ledger, which is readable by all.

## Silence-negation discipline (PROP-002, gated 2026-09-01)

8. **Any letter using a silence-is-not-approval variant runs
   `scripts/audit/lint_silence_clause.py` before delivery, and a REFUSED verdict blocks
   the send** (refuse, not warn — the phrase is a negation and fails toward inaction;
   Jon's ruling 2026-09-01 after a real near-miss). The lint requires an `on_silence`
   line with an explicit acting label (ACTS / NO-OP / "nothing acts"); quoted, struck,
   and blockquoted occurrences are exempt so a letter about the phrase can pass. The
   cheaper half outranks the lint: where Jon said the thing plainly, quote him instead
   of encoding it.

## The promise fields have a reader (PROP-003, gated 2026-09-01)

9. **`expires:` and `on_silence:` are read by `scripts/audit/on_silence_report.py`** —
   Herald F-7 measured the fleet carrying these fields with zero readers (14 letters past
   their own declared deadline, nothing fired: "we built a lint for the presence of a
   promise and never built the thing that keeps it"). The reader REPORTS (past-due / live /
   unclocked / unparseable — never folded); firing a default stays the coordinator's
   judgment, graded with rules 5-7's vocabulary. Run it at wake and at SU. A declared
   `on_silence` with no `expires` is UNCLOCKED — legitimate for standing letters,
   deliberate or it's a defect. `scripts/audit/exchange_write_check.py` runs these checks
   automatically on every exchange/ write (PostToolUse hook, Jon's 09-01 ask).

## A SENT LETTER IS FROZEN. Corrections travel as NEW FILES.

**Adopted 2026-09-11. The rule and its wording are Secretary's, the evidence is Herald's and
Secretary's, and the third class below is CFL's own practice on the night it was adopted.**

> **A sent letter is FROZEN; corrections travel as new files. Not "do not edit your outbox" —
> edit it if you like, but the edit is a note to yourself and must be labelled one.**

### Three ways the rule gets broken, and the third is invisible

**CLASS A — receipts stamped into the copy you hold.** `[measured, Personal: 5 letters]` `read:`
and `read-soul:` keys appear in the sender's outbox copy and in no delivered copy. ⛔ **Stamping
the copy you hold tells only yourself.** `verify_delivery.py`'s docstring already named this on
2026-08-24 and the practice continued to at least 08-30.

**CLASS B — editing your own copy after it has gone.** `[measured, Personal: 9 letters; Secretary
reproduced it in its own tree three minutes after reading the evidence, expecting to be clean]` A
withdrawn count struck in place at 15:27 after couriering; all four recipients still hold the
pre-correction text.

⛔ **CLASS C — CORRECT THE LETTER AND SILENTLY OVERWRITE EVERY DELIVERED COPY.** This is CFL's
own practice as of 2026-09-11 and it is the one no divergence test can see. `[measured 20:5x: all
of CFL's 09-11 letters match their delivered copies byte-for-byte — ZERO divergence]` **That number
is not cleanliness.** It is what you get when every correction is re-copied over the recipients'
files under the same name.

⭐ **A peer who read version 1 and moved on never learns it changed.** Class A and B leave a
detectable difference between two files. **Class C leaves no trace anywhere** — which makes it
the worst of the three and the only one that scores perfectly on the test built to catch the
other two.

### The rule, operationally

1. **Once a letter is delivered, its bytes are frozen at every destination.**
2. **A correction is a NEW FILE with its own name**, naming what it supersedes. Deliver it the
   same way the original went. ⭐ **Secretary did exactly this alongside its in-place strike and
   verified it at each destination: the new file reached everyone, the strike reached nobody.**
3. **You may edit your outbox copy** — but then it is a working note, and it must say so in the
   file, because it is no longer what anyone else holds.
4. ⚠️ **Re-delivering under the SAME filename is not a correction. It is a silent overwrite.**
   If you do it deliberately, say so in the new copy AND send a one-line notice, or the reader
   has no way to know the document moved under them.

### ⭐ THE FIELD, added 2026-09-11 20:5x — because rules 1-4 above are DISCIPLINE

**Soul, the same night, after three seats found this practice in themselves within an hour:**

> *"It is what 'redeliver the fixed version' looks like when the channel has no version. That is
> not a discipline failure, it is a missing field."*

⛔ **That is correct and it demotes everything above it.** Rule 4 says *send a notice* — a
resolution, carried in prose, firing only when someone remembers. **The same evening this skill
recorded that a rule in prose is a mechanism with no trigger, and then shipped one.**

✅ **SO EVERY LETTER CARRIES `rev:` IN ITS FRONTMATTER, STARTING AT 1.**

```
rev: 1                      # first delivery
rev: 2                      # any re-delivery under the same filename
supersedes_rev: 1           # on rev 2+, what it replaces
rev_note: "pid 8492 is the switchboard supervisor, not an orphan; ask withdrawn"
```

⭐ **Why a field and not a rule: a reader can SEE it, and a checker can COMPARE it.** A delivered
copy at `rev: 1` beside an outbox copy at `rev: 2` is a detectable overwrite — the thing that is
invisible today. **The notice in rule 4 stays, but it becomes the courtesy on top of the record
rather than the record itself.**

⚠️ **This does not fix the letters already delivered tonight** — CFL's four and Soul's five went
out with no `rev:` and their notices are the only trace. **It fixes the next one.**

⛔ **NOT YET BUILT: the checker.** A field nobody validates is the `queried:` defect one channel
over, and this skill is not going to pretend otherwise. **Ticket, owner CFL, morning:** compare
`rev:` between each outbox letter and its delivered copies and report mismatches. ⚠️ **Until that
exists, `rev:` is a convention with a reader and no enforcement, and it should be described that
way and not as a control.**

⚠️ **Related gap, named by Soul and NOT owned here:** the FILE channel has no send-side ledger at
all, which is why every notice written tonight was reconstructed from memory rather than derived.
`SendMessage` has one; file delivery does not.
### The bound this rule ships with, and it must travel with it

⚠️ **Nobody has verified that the delivered copies match what was ORIGINALLY sent.** What was
measured is that they differ from the outbox copy TODAY, in a direction consistent with the
sender's copy having grown. **A transport truncation before a later outbox edit would look
identical.** Separating them needs the outbox files' git history, and that walk has not been done.
⭐ **So the rule is justified by the two classes' MECHANISM, not by a proven claim about transport.**

## NOT-MAIL — the fourth state, added 2026-09-11 21:4x

**This skill already distinguishes UNDELIVERED / UNRECEIPTED / DECLINED. Herald found the fourth
the expensive way, in its own tree, tonight.**

⛔ **A delivery lint counts three different things as undelivered mail:**

1. **a letter whose recipient is named in the BODY rather than the frontmatter** — real mail, real
   backlog, deliver it;
2. **a DRAFT that was never a letter;**
3. **a STAMP or verification artifact.**

⭐ **Only the first is mail.** ⚠️ **A grading vocabulary that cannot say NOT-MAIL will report drafts
as a backlog forever, and the seat that tries to clear that backlog will deliver them.**

### How it was found, because the method is the finding

`[measured 2026-09-11 21:3x, Herald]` A router matching `^\s*to:` lowercase, frontmatter only,
reported **9 letters as unroutable**. Reading each file's BODY case-insensitively recovered **24
addressed letters** in forms like `**To:** **all trunks** — CFL · Herald · Secretary · Professional`.
**Genuinely unaddressed: 3, and not one is a letter** — two drafts and a soul-stamp, none with any
frontmatter at all.

⛔ **CFL'S ADVICE ON THAT SET WAS WRONG AND IS RECORDED HERE AS WRONG.** I told Herald to broadcast
the unaddressable ones to five trunks with *"recipient unknown"* in the subject rather than let them
become a silent backlog. **On the real population that is unnecessary for six and actively harmful
for three** — it would have manufactured exactly the confident-wrong address I had warned the same
seat against an hour earlier. ⭐ **I built advice on a peer's count without asking what the
instrument had actually matched.**

✅ **THE RULE: before treating any letter as undelivered, grade it NOT-MAIL first, and read the BODY
before concluding it names no recipient.** ⚠️ **"My pattern did not match" is not "the letter has
no recipient"** — the same shape as a truncated field read as an empty one, and the same shape as a
zero from a tool that searched nothing.
