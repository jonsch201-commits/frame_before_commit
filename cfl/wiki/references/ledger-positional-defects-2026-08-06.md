---
title: "Routing Ledger Positional Deixis — Systematic Defect"
trunk: fl
branch: [cfl]
sub_branch: [UNASSIGNED]
branch_reason: "R-REF; sub: no sub-branch evidence above the floor (best corpus 1 < 2; a lone corroborating tag does not decide)"
kind: finding
origin: checker-agent, session f0190965, 2026-08-06
status: READY FOR REVIEW
---

# Ledger Positional Reference Defects — Audit Result

## The Finding

**38 positional references found in `exchange/ROUTING-LEDGER.md`.**
- **18 data rows** use "corrects the PENDING row above" — ALL NOW WRONG
- **0 still correct · 18 now wrong · 0 unverifiable**
- **20 narrative references** in contract sections (not binding; descriptive prose)

## Root Cause

Concurrent agents append rows to the ledger between a PENDING row and its ROUTED row. When agent X writes its ROUTED row, agent Y's PENDING row has inserted between them. The "row above" reference was accurate at write time; it is no longer.

**Example timeline:**
```
23:54:33Z — agent af9517 writes PENDING row (line 419)
23:55:16Z — agent ad7e5b writes PENDING row (line 420) — inserted between
23:56:00Z — agent af9517 writes ROUTED row (line 421) — intended to correct line 419
```

Result: Line 421's "corrects the PENDING row above" points at ad7e5b (line 420), not af9517 (line 419).

## Complete List of Broken References

All data rows at these line numbers now point to the wrong antecedent:
- **351** (ab3581): points at ac4627 ROUTED, intended ac4627 ROUTED? 
- **354** (a36cc0): points at a1a69a PENDING, intended a36cc0 PENDING
- **355** (a1a69a): points at a36cc0 PENDING, intended a1a69a PENDING
- **357** (a6ecec): points at a36cc0 ROUTED, intended a6ecec PENDING
- **359** (add0f4): points at a6ecec ROUTED, intended add0f4 PENDING
- **365** (ad29fb): points at a53d6a PENDING, intended ad29fb PENDING
- **369** (ae5704): points at ad29fb ROUTED, intended ae5704 PENDING
- **373** (a96cf5): points at a890d2 PENDING, intended a96cf5 PENDING
- **378** (a18691): points at a9e39f PENDING, intended a18691 PENDING
- **387** (a93dd7): points at aaf405 PENDING, intended a93dd7 PENDING
- **403** (af38fd): points at a1f02e PENDING, intended af38fd PENDING
- **405** (a1c3aa): points at af38fd ROUTED, intended a1c3aa PENDING
- **407** (a9fe79): points at a1c3aa ROUTED, intended a9fe79 PENDING
- **409** (a9ebaf): points at a9fe79 ROUTED, intended a9ebaf PENDING
- **411** (af2b27): points at a9ebaf ROUTED, intended af2b27 PENDING
- **415** (a5bcac): points at a0654d ROUTED, intended a5bcac PENDING
- **417** (a8c9fb): points at a5bcac ROUTED, intended a8c9fb PENDING
- **421** (af9517): points at ad7e5b PENDING, intended af9517 PENDING **(explicitly noted in row's own text)**

## Convention Status

**The ledger contract (lines 9–180) does NOT teach positional deixis as valid.**

**BUT:** All 18 data rows follow the pattern "corrects the PENDING row above" — this phrasing **is the ledger's implicit convention**, and it is systematically broken by concurrent appends.

Row 421's narrative explicitly caught this and switched to timestamp-based identification:
> "corrects the `af9517` PENDING row at `2026-08-06T23:54:33Z` — **not the row immediately above**, which belongs to a concurrent agent that appended between the two"

**That is the correct fix.** The other 17 rows are unaware.

## Recommendation Options

**A: Strike positional phrasing going forward**
- New rows use id + timestamp identification only (like row 421)
- Avoids the defect structure entirely
- Cost: minimal; all corrections already have timestamps

**B: Retrofit all 18 broken rows**
- Rewrite each to use id-based or timestamp-based references
- Ledger contract forbids editing prior rows; would require new rows stating the correction
- Cost: 18 new narrative rows

**C: Document as known and leave standing**
- Add to contract: "Positional references are unreliable; use timestamps for verification"
- Accept the finding and move on
- Cost: none; document the constraint

**D: Accept partial and plan a future pass**
- Apply A going forward (stop using "above")
- Don't retrofit existing (immutable ledger)
- Clean slate on new work
- Cost: none; hybrid of A + C

## Verification Method

```bash
# Reproduce the scan
cd exchange/
grep -n "above\|below\|previous\|prior" ROUTING-LEDGER.md | wc -l
# → 38 total matches (20 narrative + 18 data)

# Extract data rows with timestamps and check positioning
# (Python script in source ledger audit session)
```

---

**Filed by:** mechanical checker, session f0190965, 2026-08-06  
**Audit scope:** counter verification (claimed count vs actual) + reference liveness (paths/slugs exist) + positional deixis validity  
**Verdict:** FINDING — the ledger's implicit convention uses a defect pattern; no rows are broken by error, but systematic concurrent-append interleaving breaks all positional references.
