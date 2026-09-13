# Combined CFL + Professional tree — private version (PR 4 candidate)

Assembled 2026-09-13 00:45 CDT by Claude Professional (session 682d274b) on Jon's ruling of 2026-09-12 22:3x, verbatim, typos his: *"I am willing to accept the *properly combined* CFL + Professionalism's trunks. But. the private version. I nee to not ask too much. But, I expect it to actually be good, and have a good combined graph. And I need you to defend what you cut."*

This tree is **derived, not authored**, from two working trees by one deriver (`cfl/scripts/audit/derive_public_tree.py`, CFL engine `19d5dfea`) run against an explicit include spec and exclusion list per half. Each half carries its own `MANIFEST.sha256` (every shipped file with hash and size) and `DERIVATION-LOG.md` (every excluded file with class, line and reason; a REPORT-ONLY section lists files flagged and deliberately not withheld). Nothing was hand-placed or hand-removed. This is the **private** version: personal identifiers are not a cut reason here (Jon, 2026-08-19); third-party and family names remain gated on consent. **This README does not claim the tree is scrubbed of PII.** That claim belongs to the public derivation, which is a later step and Jon's act.

## Composition, measured on disk

| half | source | considered | included | excluded | size | manifest sha (first 16) |
|---|---|---|---|---|---|---|
| `cfl/` | `N:/claude-cfl/clone` | 1,110 content-scanned (+30 path-denied, never scanned) | 1,046 | 94 (64 by content class, 30 by path rule) | 12.25 MB | 2d7fd58f64a19749 (fourth derivation, 2026-09-13 morning: dependency directories, `wiki/test-outputs/` (26 files: seals, hook-harness outputs), hook runtime state withheld, card-number fence corrected for dated filenames) |
| `professional/` | `N:/claude-professional` | 331 content-scanned (+11 path-denied, never scanned) | 330 | 12 (1 by content class, 11 by path rule) | 2.28 MB | `controls-professional/MANIFEST.sha256` (controls sit beside the tree, not inside it, and its rows are paths relative to `professional/`; CFL's sit inside `cfl/` and are listed in its manifest) |

Note on "considered": in this deriver the word means files that reached the content scan; files cut by a path rule never enter that count and are reported in the excluded total, so included plus content-excluded equals considered, and excluded equals content-excluded plus path-denied. For about fifteen minutes on 2026-09-13 both halves published "corrected" totals of 1,140 and 342 on a peer's reading that the counts did not close; they did close, the word was mislabelled, and the numbers reverted. What was real: the log's row "not in the include spec (never considered)" counted files the spec named and a deny rule cut (30 in `cfl/`, 11 in `professional/`), and files cut by a path-prefix rule left with no row at all. CFL's deriver now prints three closing identities and refuses to publish unless all three close (on a scratch re-derive of the current CFL tree: 18,400 paths at source = 17,192 not named + 167 path-prefix denied + 30 path-exact denied + 1,011 content-scanned; 1,011 = 959 included + 52 content-excluded; 249 excluded = 52 + 167 + 30). Expect the next derivation of `cfl/` to show an excluded count near 249 rather than 94: nothing new is cut; the 167 hook-state files were always cut and now have rows. A rise in that column on the next derive is a blind spot closing, not scope creep.

Independent verification: Professional recomputed every row of `cfl/MANIFEST.sha256` against disk (1,047 of 1,047 by sha and size, 0 missing, 0 unlisted, 07:5x, after the fourth derivation); CFL and Antigravity each recomputed `controls-professional/MANIFEST.sha256` against `professional/` (326 of 326, 0 missing, 0 unlisted). A manifest agreeing with its own generator is not a receipt; these were produced by parsers that did not write it.

## Skills

**47 skill directories ship** (44 under `cfl/skills/`, 3 under `professional/skills/`). Jon's draft post says "3 skills and their test data so far". The three the post refers to are `cfl/skills/frame-before-commit/` (1 reference file), `cfl/skills/ground-before-stating/` (2 of 3 reference files; the third is held for Jon's read of a name question), and a third graph-related skill that is **pending Jon's confirmation**: `cfl/skills/wiki-query/` (2 reference files, written 2026-09-12) is the candidate on disk; Jon on 2026-09-13 00:1x: *"The 3rd skill is for sure graph related, but it may have been auto ontology"*. No auto-ontology skill exists in any trunk; Antigravity holds an ontology reasoner script and a spec. The 47-versus-3 mismatch is Jon's call at the sitting.

## Graph

`graph/index.sqlite` was built **from empty over this tree only**, with CFL's builder (`scripts/graphrag/build_index.py` @ 3a8f397c; tenth build, over the fourth `cfl/` derivation):

```
python build_index.py --root N:/claude-pr4 --db N:/claude-pr4/graph/index.sqlite   --include N:/claude-pr4/cfl --include N:/claude-pr4/professional   --include N:/claude-pr4/cfl/.claude/hooks/fable-mirror-write-fence.README.md   --include N:/claude-pr4/professional/.claude/commands/su-compact.md   --include N:/claude-pr4/professional/.claude/commands/wake.md \
  --include N:/claude-pr4/professional/.claude/skills/oath-checks/SKILL.md
```

| measure | value |
|---|---|
| files indexed | 1,324 (0 outside this tree; all 1,023 markdown files under the two halves, 757 + 266, plus this README and the card; the rest are `.py`, `.sh` and `.txt` under `scripts/` and `skills/`. Not indexed, by the walker's deliberate rule and announced in its output: 18 code files under `cfl/.claude/hooks/` and 2 under `professional/.claude/skills/oath-checks/`) |
| chunks | 13,629, all knowledge tier |
| edges | 2,063 resolved of 4,221 link references |
| size | 161.1 MB |
| build | 22.0 s, 2026-09-13 07:53 CDT; the walker prints both notices: `[walk] OUT-OF-ROOT SKIPPED: ~/.claude/CLAUDE.md` and `[walk] SKIP_DIRS pruned under an --include ... cfl/.claude, professional/.claude` |

Why the flags: the builder walks fixed top-level names (`wiki/`, `scripts/`, `skills/`) under its root, so `--include` per half walks both trunks; the four named files live under `.claude/`, which the walker skips deliberately (stale worktree shadows measured 2026-08-18) and now says so. Until engine f3369299 the builder also added the machine's `~/.claude/CLAUDE.md` to any root's graph; the first build here indexed exactly that one file and nothing else, CFL ruled it a scope defect and fixed it the same night, and builds two to four used `HOME` pointed at an empty directory as the workaround. The fifth build needed no workaround and the files table holds no path outside this tree. Independent check (Antigravity, 00:5x, read-only): files table 1,242, chunks and .md counts match (736 under `cfl/`, 264 under `professional/`), 0 paths outside the tree, 5 of 5 probes at rank 1. Probe output flags every hit `PATH GONE` when run with an empty HOME: that is the retriever's root-alias check finding no home configuration, uniform across all hits, not a missing file. The eight earlier builds, the superseded CFL derivation and the previous Professional half are kept, not deleted, in `N:/claude-pr4-history/` (about 1 GB), each named in its `README.txt`; this root holds only the artifact.

Five cold probes, no trunk filter, each answered at rank 1 by the intended page: the dual-layer grounding gate (`cfl/skills/frame-before-commit`), print the population (`professional/wiki/concepts/print-the-population.md`), the rigor seat, the default query scope (`cfl/skills/wiki-query/references/query-surfaces.md`), and the PII/no-deletion ruling (`cfl/wiki/references/constitution/`).

## About `cfl/` (text supplied by CFL, numbers theirs)

The half **points at 66 files it does not contain.** `cfl/DERIVATION-LOG.md` (third derivation) reports 66 of 259 excluded files referred to by name from a file that ships, 859 references in total (the 259 counts the 167 withheld hook-state files with the 92 content exclusions), so a reader following a citation can land on a name with nothing behind it. Every exclusion has a row in `cfl/DERIVATION-LOG.md` (identifiers, money paths, third-party names under a consent rule, paths named out by earlier rulings). Converting those references into plain descriptions is a polish pass that has not been done. CFL's cut defense: `exchange/FOR-JON-REVIEW/PR4-CFL-CUT-DEFENSE-2026-09-12.md` in CFL's repo.

## About `professional/`

5 of the 12 excluded files are referred to by name from shipping files (6 references). The 12 exclusions are 11 pages and one script under a family-name consent gate awaiting Jon (row 16 of Professional's review index; silence keeps them out) and `history-2026-08.md`, cut whole for 221 mentions of a no-remote path. Cut defense: `exchange/FOR-JON-REVIEW/PR4-COMBINED-TREE-PLAN-2026-09-12.md` §3 in Professional's repo.

## Criteria, each a command, graded 2026-09-13

| criterion | result |
|---|---|
| 0 tree matches the post: `ls cfl/skills` shows frame-before-commit, ground-before-stating, wiki-query; references present; graph present | PASS on presence; the third skill's identity and "3 skills" are Jon's |
| G1 graph coverage: every indexed path inside the tree; every .md on disk indexed | PASS on files (0 foreign; 1,023 of 1,023 under the halves, plus README and card; tenth build). **FAIL on navigability: `cfl/` ships no `wiki/index.md` and no `README.md`; its index is withheld by the name fence on three personal and home summary rows, a scope question for Jon (sitting sheet row 4)** |
| G2 five cold probes, no trunk filter | PASS (5 of 5 at rank 1) |
| G3 size | 161.1 MB |
| E skill-use eval | measured; see Professional's plan §12 |
| 1 leak control on `professional/` (`leak_control.py --derived … --include-spec … --controls-dir controls-professional`) | PASS 00:48: 13 of 13 plants excluded and logged by class; known-clean control included; both manifests hash-complete, zero-byte-free. Limit: the harness's planted re-derivation applies CFL's public exclusion set, so 9 of 326 clean files (family-name pages the private version keeps) drop in the planted run; reported by the harness, not failed. `cfl/`: CFL's run, in its log. |
| 2a coverage lint, set A (C1, C2, C10, C11, C22) from `professional/` root, 00:57, after the spec gained `wiki/index.md` and the oath-checks skill | **FAIL as measured**: C1 PASS; C2 FAIL, 4 dangling index links (the hand index names pages this version excludes); C10 FAIL, structural (a derived subset cannot carry the source's derived index, and regenerating one inside the artifact would break the manifest); C11 PASS (38 dead script references reported); C22 FAIL, 13 unresolved body wikilinks across 259 files. `cfl/`: UNKNOWN; CFL is building a format-independent coverage lint, due 2026-09-13 22:00. |
| 2b executability lint over shipped scripts (CFL's `lint_shipped_tree.py --run`) | `professional/`: 39 shipped `.py`, 23 with a selftest flag: 22 PASS, 1 FAIL (`ACCEPTANCE-pr4-exclusions.py` assumes it runs inside the working tree), 16 named UNGRADED. The runner stopped itself when the tree digest changed mid-run; the change was one bytecode cache file a selftest's import wrote, since removed; no shipped file changed. `cfl/`: the first run found MISSING-DEP failures because `scripts/lib/`, `scripts/graphrag/`, `scripts/tests/` were not in the spec; they now ship (2 + 10 + 9 files). Final run, executed from a sandbox copy so the artifact is never an execution target, manifest intact before and after: **97 of 125 scripts with a selftest pass, 9 unresolved at a 40-second cap** (97 is a floor, not a total); MISSING-DEP 6, all six `No module named corpus_index`, the module withheld by the name fence (sitting sheet row 4); OTHER 1; REFUSED 2 (correct behaviour outside a repo); NO-SUCH-FLAG 10 (discovery false positives); 111 UNGRADED for having no selftest. **Criterion 2b: FAIL, 7 defects, 6 of them one consent decision.** |
| H HuggingFace card | not started; Jon's post is not yet posted |

Not in this tree, by design: letters, transcripts, session captures, trackers, the Exchequer path. Not published: no remote, no branch yet, no push. Jon sits with it 2026-09-14 evening.

## Git

This directory is a git repository on branch `pr4-combined-private` with no remote. The commit tracks exactly the files both manifests list plus this README, the card, `.gitignore` and `controls-professional/`; `cfl/.claude/hooks/state/` carries a `.gitignore` that CFL ships, so in the second commit 187 manifest-listed files were force-added rather than silently dropped; the third derivation withholds that state entirely, on CFL's own source comment, and ships no nested `.gitignore`. The graph is ignored by git, kept on disk, and rebuildable; earlier derivations and builds were moved to `N:/claude-pr4-history/`. Adding a remote and pushing is Jon's act.
