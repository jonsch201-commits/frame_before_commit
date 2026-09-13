---
title: Wiki Answer Key — How to Find a Thing You Cannot Name
aliases: ["the answer key", "where the answer key is", "my goals", "how to find my goals", "golden principles", "where are Jon's rules"]
see_also: wiki/references/golden-principles.md -- the golden principles page, for "what did Jon rule about X"
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 6 vs skills 0 on authored labels"
last_updated: 2026-08-06
maintained_by: wiki-master (proposal, unratified — draft PR)
purpose: routing map, not an inventory. See wiki/index.md for what exists; this page is for how to FIND it.
---

# Wiki Answer Key

Jon, 2026-08-06, verbatim: *"I don't know where the answer key is for your wiki. The index is
useless and unorganized... I don't know how to find my goals, I don't know how to trace things to
their original sources. If I search, I am using file names and we don't name things the same way
in our heads."*

**This page is the answer key. `wiki/index.md` is a hand-maintained inventory (what exists,
grouped by folder) — Jon has called it useless for finding things, and that is a finding about the
index, not an insult.** This page exists because the index cannot answer "where do I look for X"
without you already knowing the filename.

## Three places, not one

Most things you want are NOT in `wiki/`:

| Root | What lives there | Tracked in git? |
|---|---|---|
| `wiki/` | The curated, citable record — source pages, concepts, trackers, references | Yes |
| `exchange/` | Peer mail (Herald, Claude Personal), charters, registers, findings, decision packets | Yes |
| `raw/` | The full gitignored transcript corpus — **and `raw/references/goals.md`, Jon's goals file** | `raw/references/` yes; `raw/transcripts/` no (gitignored) |

**Your goals are at `raw/references/goals.md`.** It is tracked in git despite living under `raw/` —
the gitignore excludes the transcript corpus, not this file.

## How the wiki is organized (and where it breaks)

- Most of `wiki/` is foldered by **artifact type** — `sources/`, `concepts/`, `tracker/`,
  `references/`, `intake-triage/`. A subject axis exists **only inside `wiki/sources/`**, split
  into 7 domain folders (infrastructure, fbc, ai-mechanics, consciousness, stylomantic, reference,
  ai-governance). **Nothing outside sources/ is foldered by subject** — that is why "everything
  about X" usually has no folder to go to.
- **Flat piles** (type-foldered, not further organized) — **all counts re-measured 2026-08-23**:
  `wiki/intake-triage/` — **110** files (was 97 on 2026-08-06).
  `wiki/sources/infrastructure/` — 97 files, **62% of all 157 source pages**. It is the junk drawer,
  named as such. `wiki/references/agent-memory/` — 49. `wiki/concepts/` — **41**. `wiki/personal/sources/` — 51.
  ⚠️ **These numbers drift and this page has no way to notice.** They were stated undated on
  2026-08-06 and three of them were wrong within two weeks. **Re-measure before citing them**:
  `ls -1 wiki/intake-triage/*.md | wc -l`. Treat any count here as of its stamp, never as current.
- **Empty**: `wiki/analyses/`, `wiki/entities/`, `wiki/methodology/` — zero files, nothing tracked.
  ⚠️ **CORRECTED 2026-08-23.** This line read *"no directory on disk, not merely zero files."*
  **That is false on this machine** — all three directories exist right here as empty, git-untracked
  leftovers (`ls -d` finds them; `git ls-files` returns nothing for any of them). It was true for the
  **fresh worktree** the page was verified in, because git never materializes an empty directory in a
  new checkout. **Both statements were honest; they describe different trees.** Keep the distinction
  in mind whenever this page says something does not exist: *a fresh clone and this working tree are
  not the same filesystem*, and this repo lives on a Drive mount that accumulates exactly this kind of
  residue. Either way the operational answer is unchanged — **nothing lives in them, so nothing routes
  there.**
- **Retrieval fields** (frontmatter, meant to help you search by concept, not filename):
  `tags` on ~373 files but roughly 1,000+ distinct values — free text, essentially untamed, ~3
  uses per tag. `retrieval_key` on ~189 files. `domain` on 22 files. **`aliases` on only 69 files
  — the field that would actually fix "we don't name things the same way," almost unused.**
- **`wiki/references/cfl-branch-registry.md`** landed 2026-08-06 and is unratified — a real
  taxonomy proposal is in flight. This page points at it and does not pre-empt it.

## The test — four things Jon needed to route, verified against this checkout

**1. "What did we decide about how the mirror gets consulted?"** — Not one place. Six+:
`wiki/tracker/projects.md`, `wiki/tracker/skills.md`, `wiki/tracker/wayfinder-cfl.md`,
`wiki/log.md`, `wiki/index.md`, `wiki/intake-triage/jon-pre-stop-consult-rule-and-run-rulings-2026-08-03-mirror.md`,
`wiki/references/agent-memory/mirror-before-jon.md` (the canonical block), and
`exchange/coordination-charter-2026-07-21.md` (Item 8). All confirmed present in this checkout.

**2. "Why does the SU take 3 minutes now?"** — In `wiki/`, not absent:
`wiki/index.md` and `wiki/intake-triage/FINDING-skills-do-not-redeploy-mid-session-2026-08-06.md`
(confirmed on disk; the exact "3 minutes" phrase was not found verbatim in `wiki/index.md` by
string search — the finding is the substance, not that phrase).

**3. "What went wrong with the Downloads thing?"** — `exchange/personal-to-cfl-downloads-accepted-2026-08-06.md`
(confirmed present).

**4. "What do we know about capture failing silently?"** —
`wiki/references/agent-memory/migrations-blind-instruments.md` (confirmed present, tagged
`silent-failure`).

## Don't read this page — run the search

```
python scripts/audit/find_answer.py "the words you would actually use"
```

`scripts/audit/find_answer.py` searches `wiki/` **and** `exchange/`, `raw/references/`, `skills/`,
`docs/` and `.claude/` — 947 tracked markdown files — and ranks by **authored retrieval intent**
rather than by whatever mentioned the phrase most recently. `aliases` outweighs `retrieval_key`
outweighs `title` outweighs headings outweighs `tags` outweighs body text; and the page-class
demotions (`wiki/log.md`, raw I1 captures, queue packets, session records) apply to **body text
only**, never to a page's own declared alias. **0.68 s warm, end to end.**

That last asymmetry is why writing an alias is worth the thirty seconds: a page that declares
"if you look for it by THIS name, this is the page" wins even when it lives in a demoted folder,
and a page that merely contains the words does not.

- `--why` shows which field matched and with what text.
- `--acceptance` re-runs Jon's four routing questions and five phrases against **declared expected
  holders**, so the test can fail. It currently scores **6 of 9 at #1**.
- `--lies` prints the eight ways the ranking can be wrong.

**The three misses are findings about this wiki, not about the tool, and they are the standing work
item this page hands off:**

| miss | rank of the real holder | why |
|---|---|---|
| Q2 "why does the SU take 3 minutes" | #2 | the answer lives in an **undisposed intake packet** (`wiki/intake-triage/B-3-su-cost-…`), not in `wiki/` proper |
| Q3 "the Downloads thing" | #9 | `exchange/personal-to-cfl-downloads-accepted-2026-08-06.md` declares **no `aliases`**, and its title shares no word with the question |
| Q4 "capture failing silently" | #80 | `migrations-blind-instruments.md` *has* aliases — `instrument denominator check`, `resolves-vs-exits-0`, `empty-population pass` — and **not one is a phrase Jon would type** |

All three are fixed by writing an alias in Jon's vocabulary. **None is fixed by moving a weight** —
raising `tags` or body text until they pass is exactly how the noise comes back.

`aliases` is on **69 of ~947 pages**. That is the ceiling on how well any of this can work.

## Discipline this page follows

Every path above was checked against the working tree at the time this page was written — not
copied from a prior claim. Where a thing has no home (analyses/, entities/, methodology/), that is
stated as a fact, not smoothed over.

The search figures above are **measured output**, not estimates: run `--acceptance` and compare.
If this page ever disagrees with what that command prints, the command is right.
