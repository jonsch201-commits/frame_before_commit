---
title: "PRE-BRANCH SEAL — CFL framing of Jon's 2026-09-09 PR compass message"
kind: fbc-seal
date: 2026-09-11
session: 8634adc3
run: "PURE — 4 branches"
sealed_at: "2026-09-11 15:1x CDT, before [BRANCH REGISTRY] existed in any form"
---

# PRE-BRANCH SEAL

The question: how should CFL parse Jon's complete 2026-09-09 message and assign it to trunks or
sessions, and specifically CFL's two named frames — (a) how the foundational skills system
(`frame-before-commit`, `ground-before-stating`) should evolve, and (b) how the public repo branch
should be cleanly split from private working trees.

This is the pre-branch instinct. [COMMIT] is scored against this text, not recollection.

(1) **The public/private split is already built and the answer is "use it, don't invent."**
`regenerate_canonical.sh` produces an orphan snapshot of an allow-list of paths and is fail-closed
(exit 4 on an unlisted `wiki/` child). Jon floats "likely just a copy?" and "or created via
gitignore." Both are worse than what exists: a copy drifts and gitignore is opt-out, which fails
open. CFL's answer is generate-don't-copy, allow-list not deny-list.

(2) **Skills evolve by auto-invocation at named barriers, not by more protocol text.**
`frame-before-commit` and `ground-before-stating` are invoked when someone remembers them. The
evolution is to fire them at structural points — compact barrier, outward dispatch, any negative
assertion — which is exactly what Extension v2 §1 already proposes.

(3) **The wikiskills "same conclusion on everything" problem is a query defect, not a wiki defect,
and the fix is query-side** — expansion, scoping, and index coverage — not trimming the wiki.

(4) **CFL should own the split mechanism and hand Personal a copy-then-fork recipe**, because Jon
says "i don't know what CFL would decide" about exactly that.

(5) **CFL's slice of the division of labor is these two frames and nothing else.** Other trunks own
PR 4 wording, PR 5 loops, and the air-gap boundary. CFL should not opine on those.

(6) **Nothing in the message needs a Jon decision this week.** Every open question in it is one the
trunks can settle among themselves.
