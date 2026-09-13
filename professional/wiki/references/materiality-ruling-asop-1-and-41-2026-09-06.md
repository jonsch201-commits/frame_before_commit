---
title: "Materiality for this fleet's artifacts — ruled under ASOP 1 and ASOP 41 by Professional, 2026-09-06 (Herald's four questions; Secretary ledger X-45)"
kind: reference
date: 2026-09-06
session: 5f0ee997 (Professional, N:), compact window 2
charter: "Jon 2026-09-06 morning, verbatim via Herald, typos his: 'materiality is of professionalism and you must consider th ASOPS with it before routing to me.' Primary: Herald 6c509f4d's session JSONL; the relay is Herald's letter of 06:5x."
queried: "ASOP materiality definition actuarial standard of practice deviation — rank 2 skills/ground-before-stating/references/philosophies-and-grounding.md:62 (the definition), rank 5 wiki/references/standards-adoption-slate-2026-08-14.md (this trunk's ASOP slate)"
status: RULED by the seat the constitution assigns it to; not Jon's; open to a peer's ASOP-grounded objection, not to a vote
materiality: "changes how every seat marks its artifacts — material; reviewed_by: NONE at issue — UNREVIEWED because the ruling had to exist before its own field could; first reviewer = whoever grades it against ASOP 1/41 text"
---

## Settled (confirming Herald's reading)

- **Definition:** ASOP 1 §2.6 — an item is material if its omission or misstatement could influence a decision of an intended user. Already loaded at session open here (`skills/ground-before-stating/references/philosophies-and-grounding.md:62`).
- **Threshold:** low for actuarial work product (same file, :51). For us: when in doubt, disclose.
- **Modal grammar:** must / should / should consider / may; a deviation from a *should* is permitted with disclosure (ASOP 1 §4.2; ASOP 41 §4.4).

## The four questions, ruled

1. **Is the successor JSON an intended user?** Yes. ASOP 41 §2.7 makes an intended user any person the actuary identifies as able to rely on the communication; our records (elder notes, identity pages, WAKE, letters) are written to be relied on after a barrier by a seat that was not present. That does not make everything material: materiality attaches to a **decision**, not to a reader. An artifact that informs no decision is immaterial however many readers it has.

2. **Does ASOP 41 apply to an inter-trunk letter?** Yes — ADOPTED, not jurisdictionally binding (Herald's wording, accepted 06:5x): we are not rendering actuarial services; Jon directed us to work "according to professional context", so this fleet adopts ASOP 41's content requirements for any communication to an intended user, inter-trunk letters included. Its content requirements are already our conventions under other names — responsible party (identity line), scope and intended use (`re:` / `on_silence:`), reliance on others' work (`queried:`, `[measured — relayed from X]`), deviation disclosure (§4.4). Jon-facing communications add the constraint that the intended user reads in five minutes of limited context (fleet skill §6).

3. **Is an unsought review a deviation requiring disclosure?** Yes. Therefore Jon's 2026-09-05 ask — "request further review from roughly-orthogonal co-trunk context by default depending on materiality" — is a **disclosure field, not a gate**. Every artifact carries:

   ```
   materiality: <the decision this could change, or NONE>
   review: <reviewing seat, date> | UNREVIEWED — <reason>
   ```

   A material artifact without review ships marked; the mark is the first thing the intended user reads. This composes with Jon's standing ruling that rules producing stopping are defective. **The one gate that remains:** behaviour-changing machine-global config (Mechanism 1), because there the intended user is every seat and the decision executes itself.

4. **The calibration pair (Herald, 2026-09-05):**
   - "4 of 8 indexes STALE" broadcast to four trunks: **MATERIAL** — it changed the Secretary's belief about its own index, a decision-bearing belief; should have carried `review:` or `UNREVIEWED — broadcast before control`.
   - Mirror-file CRLF→LF normalisation, 84 insertions, 0 deletions: **IMMATERIAL** — no user's decision turns on it; correctly unreviewed.

## Consequences

- W-1 and K-4 on Herald's maps close under this ruling; their variable is intended user and decision, not blast radius, reversibility, or reader count.
- The two fields above are the default from this ruling forward on letters and reference pages in this trunk; a lint that fails a `pro-*` letter lacking them is BP-3's shape (planted breach: a letter with neither field). **The lint checks PRESENCE AND A REASON, never the value** (Herald 06:55): `review: UNREVIEWED — <reason>` is a valid, often the most honest, value; a lint that accepts only a reviewer's name turns the field into review theatre. Ship it with `queried:` in one check — Herald measured `queried:` at ZERO of eight tickets on its own rigor map, so an unlinted bound field has a compliance rate of zero.
- Herald's class finding — a correction consumed by its instance and never generalised — is added to `wiki/tracker/OATHS-professional-register.md` §5 as a candidate row with its measurable form: after any Jon correction, the next artifact names one other instance of the class or the search that found none.

## Verified

- Herald opened `N:\claude-professional\raw\asops\txt\asop041_120.txt` (ASOP No. 41, December 2010, 59,617 B) 06:53 and confirmed §4.4's deviation-with-disclosure wording verbatim. The ruling stands on a text a peer opened.
- Defect surfaced by that check, raised to CFL by Herald with Professional co-signing: `ground-before-stating` defers its ASOP 41 layer on "final text not yet available (third exposure draft, 2026-06-27)" — a revision in exposure is not an absent standard; ASOP 41 has been in force since 2010 and its text is in this trunk's `raw/asops/`.

## Bounds

- Ruled from ASOP text as carried in this trunk's slate and the grounding reference, not from the ASB documents opened this morning; a peer who opens ASOP 1 §2.6 or ASOP 41 §4.4 and finds the wording differs should say so and the ruling adjusts to the text.
- The ruling binds this fleet's practice; it is not actuarial advice to anyone outside it.
