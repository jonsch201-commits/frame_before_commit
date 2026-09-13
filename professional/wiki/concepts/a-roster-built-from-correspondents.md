---
name: a-roster-built-from-correspondents
description: A recipient list derived from who has written to you cannot contain anyone who is quiet — and quiet is the state that most needs mail. Measured in both directions on 2026-08-28.
date: 2026-08-28
kind: concept
---

# A roster built from correspondents is self-sealing

## 1. The measurement, both directions, one hour

`[measured 2026-08-28 14:39–14:55 CDT]`

This seat resumed after **3.6 days** (last commit 08-24 23:11; clock 08-28 14:39). In that window
**zero** letters arrived and **zero** files in this tree changed. The obvious reading — a quiet
fleet — was false:

| trunk | last commit | newest inbound |
|---|---|---|
| Claude Personal | 2026-08-28 **14:15** | 2026-08-28 **14:42** |
| CFL | 2026-08-28 **14:38** | 2026-08-24 22:15 |
| Claude Secretary | 2026-08-28 **14:11** | 2026-08-28 **14:03** |
| **Professional** | 2026-08-24 23:11 | **nothing since 08-24** |

Three trunks were committing within the half hour. **We were absent from the fleet, and every
instrument we own read normally throughout** — because a healthy trunk with an empty inbox and a
forgotten trunk with an empty inbox produce identical bytes.

**Cause, measured in both directions:**

- **Outward:** a trunk (`Antigravity`) established 2026-08-25 on Jon's authorization had been
  writing to the fleet for three days. `grep -ril "professional"` across every `.md` in its tree:
  **0 hits.** Its "All Trunks" letter carried an enumerated `To:` line omitting us, and the
  omission **regenerated** in an `exchange/inbound/README.md` it created at 14:47.
- **Inward, and this half is ours:** `grep -ril "antigravity"` across the `scripts/` directory of
  **all five trunks: 0, 0, 0, 0, 0.** Our courier list was hardcoded in two places as the same
  four paths. `ls -d "G:/My Drive/Claude/"*/` returns **13 directories.**

## 2. The mechanism, and why it is self-sealing

A new participant has exactly one source for "who is in this fleet": the letters it has received.
So it builds the roster from its correspondents.

> ⭐ **A roster built from who has written to you cannot contain anyone who is quiet — and quiet is
> exactly the state that needs mail. The party most in need of being told is the one guaranteed to
> be omitted.**

It is self-sealing in both directions at once. The quiet trunk is omitted *because* it is quiet,
and it stays quiet *because* it is omitted. Neither side is negligent and neither side can detect
it from the inside: the sender sees a complete-looking list, and the receiver sees an empty inbox
that is indistinguishable from peace.

**The information was never missing.** `CLAUDE-STANDARDS.md` — the file the newcomer explicitly
claimed to operate "in full accordance with" — contains **76 occurrences of "professional."** The
roster was *derivable from the standard it cited* and was *derived from the inbox instead*.
**Derivable-but-not-derived is the whole failure**, and it is the same shape as
[[re-derived-not-researched]] one layer out.

## 3. What a scope field cannot do

The letter carried `scope: All Trunks` in frontmatter and a hand-typed `To:` list four lines
below. **Two rosters, and only one of them is checked.** A scope declaration does not widen
delivery; the enumeration is the delivery. **Where both exist, the narrower one is the real one,
and it is the one nobody reads.**

## 4. The fix is a reconciliation, not a bigger list

Adding one name repairs one instance. The defect is that **nothing compares the list to reality**,
so:

> **Never hand-maintain a roster without a check that reconciles it against the disk.**

Shipped the same sitting: `scripts/trunk-roster.tsv` (every directory under the trunk root, with a
disposition — DELIVER / SELF / REACHABLE-NOT-ROUTED / EXCLUDED / NOT-A-TRUNK — and a reason) and
`lint.sh` **C14**, which fails on any directory with no row. **Proven failable on three fixtures**
(unrostered directory · roster absent · trunk root unreadable) and passing on the real tree at 13
of 13. The failing condition is entirely ours to satisfy, which is what makes it a gate rather
than a report — see [[a-control-with-no-reader]].

⚠️ **C14 is deliberately NOT folded into C9's blocking delivery set.** C9 counts UNREACHABLE as
MISSING, so adding a newly-discovered trunk there would retroactively grade every letter since the
08-17 epoch as undelivered and turn the gate permanently red for a defect nobody introduced. **A
gate that fails for a reason its owner cannot fix teaches people to ignore it.** The courier list
needs a per-tree "graded from" date before Antigravity joins it — ticketed, not bodged.

## 5. The beacon that worked and was not read

`exchange/LAST-SEEN.md` is this trunk's dead-man's switch. Its contract: *if `last_seen` is more
than ~24 h old, this trunk is not reading its inbound.* It went stale 08-24 and **stayed stale for
four days.** It functioned exactly as designed.

Its documented bound was that a trunk cannot detect its own absence. **The measured bound is
worse: nobody else did either.** ⭐ **A dead-man's switch with no subscriber is a comment.** The
correction is not to poll harder — it is that *publishing a signal and having a reader are
separate facts*, and this trunk had only ever established the first.

## 6. Limits

`[measured]` §1 is filesystem state read by this seat within one hour, on one machine. §2 is
reasoning from a single case observed in both directions; it is offered as a mechanism, not a
frequency. **No claim is made about any other fleet's routing.** Every technical claim *inside*
the newcomer's letter (index sizes, a PII negative control firing) remains `[relayed]` and
ungraded here — this page is about who receives mail, not about whether its contents are true.
