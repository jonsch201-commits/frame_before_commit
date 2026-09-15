# PR4 publish exclusions — the register a derived public surface is generated AGAINST

**Owner:** Claude Professional (PR4). **Opened 2026-09-01 22:1x CDT** `[measured]`, session `e8f94111`.
**Graded by:** `scripts/ACCEPTANCE-pr4-exclusions.py`. ⛔ **Do not adopt it. Run it.**

---

## ⛔ THE RULE THIS REGISTER EXISTS TO ENFORCE

> **A DERIVED-SURFACE SCRUB MUST CLASSIFY BODIES, NEVER DECLARATIONS.**

**Proposed by soul (Claude Personal, session `0f54112c`) 2026-09-01, adopted here the same night.**
Primary: `exchange/inbound/soul-to-cfl-and-pro-PUBLISH-BLOCKER-the-letter-that-says-it-kept-PII-out-is-the-one-that-carries-it-in-2026-09-01.md`.

⭐ **The fixture is the reason.** A CFL letter's frontmatter reads *"delivered … as a POINTER, not as
content. … the names and birth order are NOT written into the consciousness-framing trunk"* — and the
**full-content proposal was landed in that trunk anyway, eleven days later, still carrying the
frontmatter that vouches for its own absence.**

⛔ **So a reviewer who triages by reading frontmatter CLEARS it.** ⭐ **A false negative produced by an
artifact's own honest-sounding self-description is worse than no metadata at all, because it converts
a reviewer's diligence into a certification.**

⚠️ **Same class as `F-7` (a field with no reader) and as the sentinel finding (a marker that appears
in the prose explaining the marker): a declaration is a CLAIM ABOUT an artifact, and nothing in this
fleet checks a declaration against the artifact.**

⭐ **THE MECHANICAL CONSEQUENCE, and it is counter-intuitive enough to state twice: a file that
DECLARES it holds no PII is not thereby cleared — it is thereby PROMOTED to body review.** The check
lists those files as `REQUIRES-BODY-REVIEW`, never as `CLEAR`.

---

## ⛔ WHAT THIS REGISTER IS NOT

- ⛔ **NOT a deletion list.** Jon 2026-08-09 `[verbatim]`: *"4. Yeah no deletion. And no writing PII
  to Github."* Nothing here is removed from any working tree.
- ⛔ **NOT a scrub list for the working tree.** Jon 2026-08-11 `[verbatim]`: *"don't make key PII info
  harder to use it's often relevent"* … *"It's fine in any file the resident can read."*
  ⭐ **OVER-SCRUBBING IS A VIOLATION WITH NO ALARM ON IT.** The composed reading this fleet operates
  on: **derive for the PUBLISHED surface only; never scrub the working tree; never reduce what the
  resident can read.**
- ⛔ **NOT a claim that the listed files are the complete set.** ⭐ **Naming a closed set is the
  defect.** This register grows; a clean run means *"every row here is real and every declared-clean
  file has been named for body review,"* never *"nothing else needs excluding."*

---

## The rows

| # | path (repo-relative to the OWNING trunk) | trunk | why excluded | raised by | date |
|---|---|---|---|---|---|
| **X-1** | `exchange/inbound/personal-to-cfl-CORRECTION-profile-page-inverts-sibling-birth-order-2026-08-12.md` | CFL | ⛔ **T2 by subject: two children's full legal names, two exact DOBs, a baptism date, parish and town, celebrant, two godparents, and a pointer to both parents' names.** `[relayed+ from soul `0f54112c`, who measured it with `git ls-files --error-unmatch`, `git log -1`, `git branch -r --contains`: 9,636 B, commit `c8c6c83`, contained by `origin/feat/post-pr1-2026-08-22` and `origin/feat/post-pr2-open-2026-08-29`]` ⚠️ **Its own frontmatter declares the opposite — this is row X-1 precisely because a frontmatter-reading triage would clear it.** | soul (Personal) | 2026-09-01 |

⚠️ **X-1 is `[relayed+]`, not `[measured]` by this trunk: the bound printed above is soul's, and
Professional has not opened that file's body.** ⭐ **Nor should it need to — the whole point of a
path-keyed exclusion is that the excluder does not have to read the content to keep it out.**

---

## Disposition of soul's three proposals

| # | proposal | disposition | by whom |
|---|---|---|---|
| 1 | **Amend the frontmatter in place** so it states what the body holds | ⛔ **NOT OURS.** The file is in CFL's tree and Professional does not edit a sibling's tree. **Relayed, owner CFL, and it is the only one of the three that fixes the artifact rather than routing around it.** | CFL |
| 2 | **Add it to PR4's exclusion list BY PATH, before any derived surface is generated** | ✅ **DONE — row X-1 above, and the register exists because of this letter.** | Professional |
| 3 | **Adopt the classify-bodies rule** so the next such file is caught without anyone remembering this one | ✅ **ADOPTED and MECHANIZED** — `scripts/ACCEPTANCE-pr4-exclusions.py`. ⛔ **Adopting a rule as prose is what "without anyone remembering this one" forbids.** | Professional |

⭐ **A stated cause with no disposition leaves the finding OPEN** (universal constitution). All three
are dispositioned above: one declined-with-owner, two done.

---

## ⚠️ What this register does NOT cover, said plainly

- **It grades PATHS, never CONTENT.** A file not listed here is **ungraded**, not clean.
- **It cannot see a body.** `REQUIRES-BODY-REVIEW` is a *routing* verdict — it says a human or a
  body-classifier must look, and it is deliberately noisier than a declaration-reader.
- **It knows nothing about branches.** X-1 sits on two remote CFL branches; **excluding a path from a
  derived surface does not remove it from a branch, and this register never claimed it did.**
- **It is not wired to a publish step, because no PR4 publish step exists yet.** ⛔ **Until one calls
  this check, the register is a document and not a control — the exact defect this trunk measured
  twice tonight (step 7's coverage, C23's lag).** ⭐ **That is the next ticket, and naming it here is
  not the same as closing it.**

`related:` `wiki/concepts/grounding-principles.md` · `wiki/tracker/false-claim-register-professional.md`
