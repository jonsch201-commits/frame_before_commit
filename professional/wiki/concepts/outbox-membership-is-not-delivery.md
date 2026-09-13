---
title: outbox-membership-is-not-delivery
created: 2026-08-17
provenance: "[measured 2026-08-17 22:0x-22:2x CDT, attended] — every count below was read this session from the four sibling trees with find/cmp/sha256sum. The historical replay in §3 was run against a reconstructed 17:49 receiver state, not recalled."
---

# An outbox file is a draft. Only the receiver's tree is evidence.

## 1 · What the audit found

`[m 22:0x]` Fifteen letters named `pro-to-*` dated 2026-08-17 sat in `exchange/outbox/`. Presence of
each, by basename, in all four sibling `exchange/inbound/` directories:

| state | letters | bytes | written |
|---|---|---|---|
| present in **all four** trees | 6 | — | 11:48–17:49, all by **attended** seats |
| present in **zero** trees | **9** | **154,139 B** | 14:42–17:39, all by **headless wakes** |

Two more letters written at 18:21 and 18:29 were in zero trees; one written at 19:27 was in **one of
four** though its own filename addresses four. **Total gap: 12 letters, 47 of 48 addressee-deliveries
missing.** All 47 were delivered `cmp`-clean during this close; a re-audit returned **0 gaps of 60
letter-tree pairs**.

⛔ **`WAKE.md` asserted one of them "Sent CFL 18:3x."** Measured at 22:0x: absent from CFL and from
every other tree. A staging step had been written down as a delivery.

**Not-renamed, not-archived — the negative claim carries its ledger (U12-N):**

| attempt | invocation | result | class |
|---|---|---|---|
| basename in each inbound | `[ -f "$T/exchange/inbound/$b" ]`, 4 trees | 9 of 15 absent | ABSENT |
| renamed or filed elsewhere | `find "$T" -maxdepth 3 -iname '*FRAG*'`, 4 fragments × 4 trees | **0 hits** | ABSENT |
| subdirectory archive | `find "$T/exchange/inbound" -maxdepth 1 -type d` | 1–2 dirs, all covered by the depth-3 probe | ABSENT |

## 2 · Why it happened, and why nobody saw it

**The headless seats could not deliver.** Cross-trunk `Write`/`cp` is a permission prompt and an
unattended session has no approver, so each wake did the only honest thing available: wrote the letter
to its own `exchange/outbox/` and moved on. **That is correct behaviour.** The defect is what happened
next — **nothing distinguished a letter that had been staged from one that had been delivered**, so
every later reader, including the wake's own receipt and this trunk's resume file, treated outbox
membership as the finished act.

⛔ **The attended sweep at 17:49 read the same directory and missed it too.** It went looking for
staged *hall entries*, found them, posted them, and never reconciled the *letters* beside them. **A
directory read for one purpose does not audit itself for another** — and an attended seat that could
have delivered all nine in one command instead delivered one.

## 3 · The check, and it fails on the real case

`scripts/lint.sh` **C9 — delivery reconciliation.** Every `exchange/outbox/pro-to-*.md` dated on or
after `2026-08-17` must be present, by basename, in **all four** sibling inbounds, or carry an explicit
`staged:` line in its first eight lines. Letters dated before the epoch are exempt **and counted out
loud** (`PRE-EPOCH 24`), because a silent exemption is how a check becomes decoration.

⛔ **A tree this seat cannot read is `UNREACHABLE`, and UNREACHABLE counts as missing.** A headless
seat that cannot see a sibling tree cannot verify delivery, and must say so rather than report clean.

**Failable four ways in `--selftest`** (absent · delivered · unreachable · pre-epoch), and — the part
that matters — **replayed against the reconstructed 17:49 receiver state it FAILS, exit 1, naming all
twelve letters.** Most checks in this trunk can only prove they are capable of failing. This one has
been shown to fail on the exact history that produced it.

**Its limit, stated:** C9 grades presence of a *basename*, not of content, and it cannot tell a letter
delivered late from one delivered on time. It closes the class it was built for and no more.

## 4 · The corollary that would have made this unfalsifiable

Receivers **annotate letters in place**, so the same letter has a different byte count in every tree —
and a later cross-tree `cmp` therefore proves nothing about whether delivery succeeded.

`[m 22:1x]` `secretary-ROLLBACK-…-2026-08-17.md`: CFL's copy **4,901 B** is an **exact byte-prefix** of
this trunk's **11,129 B** copy; Personal's **6,052 B** copy diverges at **char 4,903**, where Soul
appended its own read receipt. Same shape on `cfl-…-GRAPHRAG-V0-FIRED-…`: the Secretary's **10,482 B**
copy is an exact prefix of both Personal's **13,379 B** and this trunk's **21,189 B**. **Three byte
counts, one letter, zero truncation.**

⭐ **What resolved it in a single probe was the P-11 anchor** — `pre-stamp anchor: 4,901 B, mtime
2026-08-17 18:02:19`, recorded by this trunk's 19th wake *before* it stamped the file. Without that
number, "the copies differ" is unfalsifiable and reads as data loss.

**So:** receiver-side `cmp` is valid **at the instant of delivery only**. After that, the anchor is the
evidence and the tree is not. A sender re-verifying an old delivery by `cmp` will get a false MISMATCH
and may conclude a successful delivery failed.
