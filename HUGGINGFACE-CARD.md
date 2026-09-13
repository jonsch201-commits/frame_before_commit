---
# Draft dataset card for the HuggingFace publication of this tree's graph and skills.
# Status: DRAFT written 2026-09-13 01:19 CDT for Jon's sitting 2026-09-14. Nothing here is uploaded. The public derivation
# (PII classes re-applied) has not been run; every number below is for the PRIVATE tree.
license: TBD (Jon's choice)
pretty_name: "WikiSkills in practice: a five-trunk Claude knowledge base, its skills, and its retrieval graph"
tags: [wikiskills, knowledge-base, graph-rag, agent-skills, actuarial-methods, personal-project]
---

# WikiSkills in practice: skills, knowledge base, and graph from a six-agent, five-trunk Claude project

**Author:** Jon (first name only; org: n/a; Jon 2026-09-12 20:57: *"Jon, n/a, first push is private."*)

**What this is.** The derived, combined tree of two of the project's trunks (CFL, the foundational layer; Professional, the rigor seat) as assembled 2026-09-13, plus the retrieval graph built from empty over that tree. It is the artifact Jon's LessWrong post points at. This card describes the private candidate; the public dataset is the same tree after a second derivation that re-applies the personal-identifier fences, and its numbers will replace these.

**What the post says and what the artifact is.** The post's sentence *"it contains 3 skills and their test data so far"* names frame-before-commit and ground-before-stating; the third is graph-related and pending Jon's confirmation (candidate: wiki-query, which gained its reference files 2026-09-12). The sentence of the draft that names the third skill is missing from every copy on this machine, including the raw session record, which carries a 489-byte truncation at that point; only Jon holds it. The tree ships 47 skill directories, of which those three carry reference material. The post's *"the graph of my knowledge base, scrubbed of my PII"* describes the public derivation, not this private candidate.

## Composition (private candidate, measured 2026-09-13)

| part | count | source of truth |
|---|---|---|
| `cfl/` | 1,015 files, 92 excluded by class | `cfl/MANIFEST.sha256`, `cfl/DERIVATION-LOG.md` |
| `professional/` | 330 files, 12 excluded by class | `controls-professional/MANIFEST.sha256`, `DERIVATION-LOG.md` |
| graph | 1,302 files indexed, 13,290 chunks, 2,032 resolved edges, 157.4 MB SQLite | rebuilt from empty over this tree; command in `README.md` |
| skills | 47 directories; references in frame-before-commit (1), ground-before-stating (2 of 3, one held), wiki-query (2) | `cfl/skills/`, `professional/skills/` |

The graph is a derived index and is never richer than its source. It exceeds GitHub's 100 MB per-file limit, so it ships here as a dataset file (or split, using Personal's `split_for_upload.py`) rather than in the git tree.

## How this was made, and by whom

Six agents across five federated knowledge bases, as the post says: Professionalism (this tree's assembler, a Fable model), CFL, Secretary, Herald and Soul (Claude Personal), and Antigravity. Each trunk framed its part of the post independently at Jon's 2026-09-11 16:08 instruction (*"you and each co trunk need to read where everything actually left off with last coordinator and what would have been in my frontmatter and you need to frame your part"*). Those framings, present or not, by seat:

| seat | framing of the post | where |
|---|---|---|
| Personal / Herald | present, 2026-09-11 14:58 | `FRAME-2026-09-11-personal-herald-AIR-GAP-IS-A-DERIVATION-NOT-AN-EXCLUSION.md` |
| CFL | present, 2026-09-11 15:07 | `cfl-FRAME-BEFORE-COMMIT-2026-09-11-PR4-COMPASS-SOVEREIGN-POSITION.md` |
| Professional | present, 2026-09-11 16:20, plus a synthesis of four frames | `pro-FRAME-BEFORE-COMMIT-2026-09-11-PR4-SOVEREIGN-POSITION-AND-QUESTIONS-HELD-FOR-JON.md`; `pro-SYNTHESIS-2026-09-11-…-FROM-FOUR-INDEPENDENT-FRAMES.md` |
| Antigravity | present as a review packet and LessWrong policy dossier, 2026-09-11 | `REVIEW-REQUEST-2026-09-11-antigravity-to-professional-PR4-AND-LESSWRONG-COMPANION.md`; `[[lesswrong-publication-standards]]` |
| Soul | UNKNOWN: no separate framing found by this seat; Personal's frame is Herald's | seat named, not counted |
| Secretary | UNKNOWN: no framing letter found among its 2026-09-11 mail by this seat | seat named, not counted |

How the framings fold into the post is Jon's: his draft keeps one `((()))` slot for Professionalism's clarifications; one slot per trunk is the alternative. These letters live in the trunks' `exchange/` directories, which the derivation does not ship; whichever fold Jon chooses, the chosen text moves into a shipped page before the public derivation.

## Measurements a reader can re-run

Every count in this tree carries its command. Skill invocation by name across 197 main sessions since 2026-09-05 (`professional/scripts/audit/skill_use_eval.py`): frame-before-commit 26 tool calls, wiki-query 5, ground-before-stating 0; the zero is an invocation record, not a measure of the discipline, because that skill is loaded at session open in one trunk and applied without its name elsewhere. Criteria results, with the failing ones named, are in `README.md`.

## What is not here

Letters, transcripts, session captures, trackers and one path with a no-remote rule are excluded by construction; 61 of CFL's 88 excluded files and 5 of Professional's 12 are still referred to by name from shipping files, so a citation can land on a name with nothing behind it. Each such name has a row in the derivation logs. Family and third-party names are gated on consent. Nothing in this repository is actuarial work; the author is an actuary and says so in the post's disclaimer, which this card repeats: an actuary who wants to use these skills should review and test them against the standards that apply to their own work.

## Related

Jon's 2026-09-07 question, unanswered until this card: *"Is this index also being evaled as part of wikiskills? How should we consider this whitepaper in context? 'https://huggingface.co/papers/2608.13940'"* The index is evaluated by criteria G1 to G3 in `README.md` (coverage, five cold probes, size); the paper is not yet read by this seat and is listed here as the next reading, owner Professional.
