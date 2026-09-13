# Combined CFL + Professional tree — private version (PR 4 candidate)

Assembled 2026-09-13 00:45 CDT by Claude Professional (session 682d274b) on Jon's ruling of 2026-09-12 22:3x, verbatim, typos his: *"I am willing to accept the *properly combined* CFL + Professionalism's trunks. But. the private version. I nee to not ask too much. But, I expect it to actually be good, and have a good combined graph. And I need you to defend what you cut."*

This tree is **derived, not authored**, from two working trees by one deriver (`cfl/scripts/audit/derive_public_tree.py`, CFL engine `19d5dfea`) run against an explicit include spec and exclusion list per half. Each half carries its own `MANIFEST.sha256` (every shipped file with hash and size) and `DERIVATION-LOG.md` (every excluded file with class, line and reason; a REPORT-ONLY section lists files flagged and deliberately not withheld). Nothing was hand-placed or hand-removed. This is the **private** version: personal identifiers are not a cut reason here (Jon, 2026-08-19); third-party and family names remain gated on consent. **This README does not claim the tree is scrubbed of PII.** That claim belongs to the public derivation, which is a later step and Jon's act.

## Composition, measured on disk

| half | source | considered | included | excluded | size | manifest sha (first 16) |
|---|---|---|---|---|---|---|
| `cfl/` | `N:/claude-cfl/clone` | 1,182 | 1,125 | 87 | 10.85 MB | cb9fc8e0dff57dcf |
| `professional/` | `N:/claude-professional` | 331 | 330 | 12 | 2.28 MB | `controls-professional/MANIFEST.sha256` (controls sit beside the tree, not inside it, and its rows are paths relative to `professional/`; CFL's sit inside `cfl/` and are listed in its manifest) |

Independent verification, 00:5x: Professional recomputed every row of `cfl/MANIFEST.sha256` against disk (1,126 of 1,126 by sha and size, 0 missing, 0 unlisted); CFL and Antigravity each recomputed `controls-professional/MANIFEST.sha256` against `professional/` (326 of 326, 0 missing, 0 unlisted). A manifest agreeing with its own generator is not a receipt; these were produced by parsers that did not write it.

## Skills

**47 skill directories ship** (44 under `cfl/skills/`, 3 under `professional/skills/`). Jon's draft post says "3 skills and their test data so far". The three the post refers to are `cfl/skills/frame-before-commit/` (1 reference file), `cfl/skills/ground-before-stating/` (2 of 3 reference files; the third is held for Jon's read of a name question), and a third graph-related skill that is **pending Jon's confirmation**: `cfl/skills/wiki-query/` (2 reference files, written 2026-09-12) is the candidate on disk; Jon on 2026-09-13 00:1x: *"The 3rd skill is for sure graph related, but it may have been auto ontology"*. No auto-ontology skill exists in any trunk; Antigravity holds an ontology reasoner script and a spec. The 47-versus-3 mismatch is Jon's call at the sitting.

## Graph

`graph/index.sqlite` was built **from empty over this tree only**, with CFL's builder (`scripts/graphrag/build_index.py` @ cd27b6d6; seventh build):

```
python build_index.py --root N:/claude-pr4 --db N:/claude-pr4/graph/index.sqlite   --include N:/claude-pr4/cfl --include N:/claude-pr4/professional   --include N:/claude-pr4/cfl/.claude/hooks/fable-mirror-write-fence.README.md   --include N:/claude-pr4/professional/.claude/commands/su-compact.md   --include N:/claude-pr4/professional/.claude/commands/wake.md \
  --include N:/claude-pr4/professional/.claude/skills/oath-checks/SKILL.md
```

| measure | value |
|---|---|
| files indexed | 1,244 (0 outside this tree; all 1,002 markdown files under the two halves, 736 + 266, plus this README) |
| chunks | 12,494, all knowledge tier |
| edges | 2,015 resolved of 4,107 link references |
| size | 148.5 MB |
| build | 31.7 s, 2026-09-13 00:59 CDT; the walker now prints `[walk] OUT-OF-ROOT SKIPPED: ~/.claude/CLAUDE.md` |

Why the flags: the builder walks fixed top-level names (`wiki/`, `scripts/`, `skills/`) under its root, so `--include` per half walks both trunks; the four named files live under `.claude/`, which the walker skips deliberately (stale worktree shadows measured 2026-08-18) and now says so. Until engine f3369299 the builder also added the machine's `~/.claude/CLAUDE.md` to any root's graph; the first build here indexed exactly that one file and nothing else, CFL ruled it a scope defect and fixed it the same night, and builds two to four used `HOME` pointed at an empty directory as the workaround. The fifth build needed no workaround and the files table holds no path outside this tree. Independent check (Antigravity, 00:5x, read-only): files table 1,242, chunks and .md counts match (736 under `cfl/`, 264 under `professional/`), 0 paths outside the tree, 5 of 5 probes at rank 1. Probe output flags every hit `PATH GONE` when run with an empty HOME: that is the retriever's root-alias check finding no home configuration, uniform across all hits, not a missing file. Earlier builds are kept beside the index as `index.first-run-1file.sqlite`, `index.second-run-1239.sqlite`, `index.third-run-1242.sqlite` (indexed the derivation log since moved to `controls-professional/`) `index.fourth-run-1242.sqlite` (HOME workaround), `index.fifth-run-1242.sqlite` (fixed engine, before run F) and `index.sixth-run-1243.sqlite` (run F, one hidden-dir page missing).

Five cold probes, no trunk filter, each answered at rank 1 by the intended page: the dual-layer grounding gate (`cfl/skills/frame-before-commit`), print the population (`professional/wiki/concepts/print-the-population.md`), the rigor seat, the default query scope (`cfl/skills/wiki-query/references/query-surfaces.md`), and the PII/no-deletion ruling (`cfl/wiki/references/constitution/`).

## About `cfl/` (text supplied by CFL, numbers theirs)

The half **points at 60 files it does not contain.** 60 of the 87 excluded files are referred to by name from a file that ships, 783 references in total, so a reader following a citation can land on a name with nothing behind it. Every exclusion has a row in `cfl/DERIVATION-LOG.md` (identifiers, money paths, third-party names under a consent rule, paths named out by earlier rulings). Converting those references into plain descriptions is a polish pass that has not been done. CFL's cut defense: `exchange/FOR-JON-REVIEW/PR4-CFL-CUT-DEFENSE-2026-09-12.md` in CFL's repo.

## About `professional/`

5 of the 12 excluded files are referred to by name from shipping files (6 references). The 12 exclusions are 11 pages and one script under a family-name consent gate awaiting Jon (row 16 of Professional's review index; silence keeps them out) and `history-2026-08.md`, cut whole for 221 mentions of a no-remote path. Cut defense: `exchange/FOR-JON-REVIEW/PR4-COMBINED-TREE-PLAN-2026-09-12.md` §3 in Professional's repo.

## Criteria, each a command, graded 2026-09-13

| criterion | result |
|---|---|
| 0 tree matches the post: `ls cfl/skills` shows frame-before-commit, ground-before-stating, wiki-query; references present; graph present | PASS on presence; the third skill's identity and "3 skills" are Jon's |
| G1 graph coverage: every indexed path inside the tree; every .md on disk indexed | PASS (0 foreign; 1,002 of 1,002 under the halves, plus this README) |
| G2 five cold probes, no trunk filter | PASS (5 of 5 at rank 1) |
| G3 size | 148.5 MB |
| E skill-use eval | measured; see Professional's plan §12 |
| 1 leak control on `professional/` (`leak_control.py --derived … --include-spec … --controls-dir controls-professional`) | PASS 00:48: 13 of 13 plants excluded and logged by class; known-clean control included; both manifests hash-complete, zero-byte-free. Limit: the harness's planted re-derivation applies CFL's public exclusion set, so 9 of 326 clean files (family-name pages the private version keeps) drop in the planted run; reported by the harness, not failed. `cfl/`: CFL's run, in its log. |
| 2a coverage lint, set A (C1, C2, C10, C11, C22) from `professional/` root, 00:57, after the spec gained `wiki/index.md` and the oath-checks skill | **FAIL as measured**: C1 PASS; C2 FAIL, 4 dangling index links (the hand index names pages this version excludes); C10 FAIL, structural (a derived subset cannot carry the source's derived index, and regenerating one inside the artifact would break the manifest); C11 PASS (38 dead script references reported); C22 FAIL, 13 unresolved body wikilinks across 259 files. `cfl/`: UNKNOWN; CFL is building a format-independent coverage lint, due 2026-09-13 22:00. |
| 2b executability lint over shipped scripts (CFL's `lint_shipped_tree.py --run`) | `professional/`: 39 shipped `.py`, 23 with a selftest flag: 22 PASS, 1 FAIL (`ACCEPTANCE-pr4-exclusions.py` assumes it runs inside the working tree), 16 named UNGRADED. The runner stopped itself when the tree digest changed mid-run; the change was one bytecode cache file a selftest's import wrote, since removed; no shipped file changed. `cfl/`: 179 shipped `.py`, 108 with a selftest flag, 71 UNGRADED; result pending from CFL. |
| H HuggingFace card | not started; Jon's post is not yet posted |

Not in this tree, by design: letters, transcripts, session captures, trackers, the Exchequer path. Not published: no remote, no branch yet, no push. Jon sits with it 2026-09-14 evening.
