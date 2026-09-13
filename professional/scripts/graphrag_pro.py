#!/usr/bin/env python3
"""Professional's build shim over CFL's GraphRAG builder. Three overrides, nothing else.

⛔ WHY A SHIM AND NOT A COPY. CFL owns `scripts/graphrag/build_index.py`. Forking it here would
give this trunk a silently diverging second builder, and the first CFL fix we did not notice would
make our index wrong in a way no test here would catch. So this file imports theirs and overrides
exactly three named things. If CFL renames any of them this shim FAILS LOUDLY at import (see the
assertions below) rather than building a wrong index quietly.

⚠️ THESE ARE MONKEY-PATCHES AND CFL SAID NOT TO NEED THEM. Their own README records the rule --
"a private name another trunk must monkey-patch is a contract nobody signed" -- which is why they
threaded `--root` as an argument. `tier_of` and `EXCLUDED_WIKI_TRUNKS` did NOT get the same
treatment, so this trunk patches them and proposes the contract instead of editing their tree:

    PROPOSAL TO CFL (not applied by us): make the tier rule and the wiki-subdir exclusion
    configurable the way `--root` already is -- `--queue-prefix PREFIX` (repeatable) and
    `--exclude-wiki DIR` (repeatable), defaulting to today's CFL values. Then this file deletes
    itself down to a wrapper.

THE THREE OVERRIDES

1. TIER. CFL's `tier_of` names CFL's queue (`wiki/intake-triage/`, `wiki/archive/`). Professional
   has neither. Professional's queue is `exchange/` -- the letters channel.
   `[measured 2026-08-23]` wiki/ is 35 files / 873,548 B; exchange/ is 349 files / 2,625,329 B.
   ⭐ The correspondence is 3x the knowledge base by bytes. Indexed as knowledge it IS the
   haystack CFL measured (their intake-triage was 72% of chunks and pushed the answer to
   "which seat only hands work out" to dense rank 4,105 of 16,132).
   ⚠️ Tiering is SCOPING, NOT DELETION. Every letter is embedded and queryable; `--all-tiers`
   reaches them. No record is dropped and nothing becomes unfindable.

2. SEALED EXCLUSION. `wiki/sealed/` holds the +30-day memory audit -- an exam whose questions must
   not be studyable by the party being audited. CFL's walk would index it (their
   `EXCLUDED_WIKI_TRUNKS` names personal/home/pro, not sealed). An indexed exam is a leaked exam:
   the index is a derived artifact that any seat can query, and a retrievable question is a
   studied question. Excluded here BY NAME, and the exclusion is probe-tested after every build
   (`graphrag.sh build` runs the probe; an exclusion you did not test is an exclusion you do not
   have).

3. CORPUS WIDENING. `--include exchange gists` -- the letters channel (queue) and the three
   publication-candidate gists (knowledge). ⛔ `raw/` is NOT included in v0: `[measured]` 57 .txt
   ASOP fetches + 57 .pdf. The .txt half is real reference material and .txt is in CFL's
   INCLUDE_EXTS, so widening to it is a deliberate future row, not an oversight.

Usage: prefer `scripts/graphrag.sh build`. Direct: `python scripts/graphrag_pro.py [--force] ...`
Exit codes are CFL's: 0 built - 2 bad corpus - 4 another build holds the lock - 5 selftest failed.
"""

from __future__ import annotations

import argparse
import os
import sys

PRO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFL_GRAPHRAG = os.path.join(
    "G:", os.sep, "My Drive", "Claude", "Claude Foundational Layer",
    "claude-foundational-layer", "scripts", "graphrag")

if not os.path.isdir(CFL_GRAPHRAG):
    sys.exit(f"FAIL CFL graphrag tooling not found at {CFL_GRAPHRAG} -- "
             f"this shim has no builder of its own by design.")
sys.path.insert(0, CFL_GRAPHRAG)

import build_index  # noqa: E402

# ⛔ FAIL LOUDLY, NOT QUIETLY. If CFL renames either name, the patch below would become a no-op
# that silently builds an untiered index with the sealed exam in it. Assert both exist first.
assert hasattr(build_index, "tier_of"), \
    "CFL build_index.tier_of is gone -- the Professional tier patch would silently no-op."
assert hasattr(build_index, "EXCLUDED_WIKI_TRUNKS"), \
    "CFL build_index.EXCLUDED_WIKI_TRUNKS is gone -- wiki/sealed/ would be INDEXED."

_LOCAL = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.cache")
PRO_DB = os.path.join(_LOCAL, "claude", "graphrag", "professional.sqlite")

QUEUE_PREFIXES = ("exchange/",)
STANDARDS_PREFIXES = ("raw/asops/",)
SEALED_PREFIXES = ("wiki/sealed/",)

# ⭐ CLAUDE.AI TIER, added 2026-08-23. CFL's own claude.ai transcript corpus
# (raw/transcripts/claude-ai/) is OUTSIDE this repo's root, so it is walked via an absolute-path
# `--include` (CFL's corpus_files() supports this: label_of() files an out-of-root path by its
# full absolute path, not a repo-relative one -- see build_index.py). Read-only: this trunk never
# writes into CFL's tree, and the index db lives off Drive on C:, so nothing here copies CFL's
# corpus into the Professional repo.
CFL_ROOT = os.environ.get("CFL_ROOT", "N:/claude-cfl/clone")  # R4b: CFL's LIVE home; its G: copy is a mirror (R8)
CLAUDE_AI_DIR = CFL_ROOT + "/raw/transcripts/claude-ai"
PRO_INCLUDES = ["exchange", "gists", os.path.join("raw", "asops", "txt"), CLAUDE_AI_DIR]


def pro_tier_of(rel_path: str, kind: str = None) -> str:
    """Professional's queue is the letters channel; the ASOPs are their own tier.

    ⭐ STANDARDS ADDED 2026-08-23 on Jon's ask -- "You should know the relevent ASOPS. You should
    have them on disc. If you can't find them, that is a huge professionalism issue." `[measured]`
    57 ASOP .txt extractions were on disc and UNREACHABLE, because `raw/` was outside the walk.
    Presence was never the defect; findability was. THIS TRUNK'S OWN RULE -- reachable is not
    retrieved -- was failing against its own core reference library.

    ⛔ WHY A SEPARATE TIER AND NOT `knowledge`. `[measured 2026-08-23]` the ASOP corpus is
    3,389,477 B of .txt against a knowledge tier of 938 chunks. Folded into `knowledge` the
    standards would be roughly five sixths of it, and every wiki question would be answered out of
    the standards -- CFL's measured haystack effect, reproduced deliberately. Tiering is scoping,
    not deletion.

    ⚠️ CONSEQUENCE THE CALLER MUST KNOW, and it is why `graphrag.sh` grew an `asop` subcommand:
    CFL's retriever defaults to an ALLOW-SET of {knowledge} and it fails CLOSED, so a new tier is
    NOT in the default scope. Standards are reached with `--tier standards` (or `--all-tiers`).
    A seat that queries without the flag and concludes the ASOPs are absent has made exactly the
    error this override was written to end.

    ⭐ CLAUDE.AI TIER (2026-08-23), same pattern as `standards`: `[measured]` 667 files /
    64,762,819 B against a knowledge tier of 1,015 chunks -- folded into `knowledge` the claude.ai
    corpus would swamp it many times over, repeating the haystack effect this whole scheme exists
    to prevent. `CLAUDE_AI_DIR` is outside PRO_ROOT, so CFL's corpus_files() files it by absolute
    path (see label_of() in build_index.py) -- checked here by prefix on `rel_path`, which for an
    out-of-root include IS the absolute path, not by `kind`, since `kind` for every file under an
    `--include` is uniformly `include:<top-segment>` (here "include:G:") and does not distinguish
    this include from any other.

    ⛔ `kind` IS CHECKED FIRST AND ONLY FOR CFL'S OWN `provenance:` FILES. This function receives
    `kind` now because CFL's `tier_of` gained it (SEC-113, 2026-08-23) as a fail-closed fix for
    exactly the absolute-path-labelling hazard described above, applied to THEIR `--provenance`
    mechanism. This tier is the same hazard, solved the other way (prefix on the known absolute
    include path) because our value is a fixed constant, not a caller-supplied `--provenance PATH`.
    """
    if kind and kind.startswith("provenance:"):
        return "provenance"
    if rel_path.startswith(CLAUDE_AI_DIR):
        return "claude_ai"
    if rel_path.startswith(STANDARDS_PREFIXES):
        return "standards"
    return "queue" if rel_path.startswith(QUEUE_PREFIXES) else "knowledge"


_cfl_corpus_files = build_index.corpus_files


def pro_corpus_files(includes=None, root=None, provenance=None):
    """CFL's walk, with sealed material dropped -- belt AND braces.

    `EXCLUDED_WIKI_TRUNKS` already stops the walk descending into `wiki/sealed/`. This second
    filter catches the same content arriving by any OTHER door (an `--include` naming it, a
    future CFL walk change, a symlink). Two independent mechanisms, because the cost of one
    failing silently is a leaked exam.

    ⚠️ `provenance` param added 2026-08-23 to match CFL's `corpus_files(includes, root,
    provenance)` signature (SEC-113) -- this shim's build never passes `--provenance` itself, but
    without accepting and forwarding the third positional argument every build call raises
    `TypeError: pro_corpus_files() takes from 0 to 2 positional arguments but 3 were given`. This
    broke silently-not-loudly (a TypeError, not the assert this file's own header promises) the
    first time CFL added a parameter rather than renaming one -- the shim's fail-loud design only
    covered renames, not signature widening. Found and fixed 2026-08-23 in the same session that
    added the claude_ai tier.
    """
    return [(full, rel, kind) for (full, rel, kind) in _cfl_corpus_files(includes, root, provenance)
            if not rel.startswith(SEALED_PREFIXES)]


build_index.tier_of = pro_tier_of
build_index.EXCLUDED_WIKI_TRUNKS = set(build_index.EXCLUDED_WIKI_TRUNKS) | {"sealed"}
build_index.corpus_files = pro_corpus_files


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Professional GraphRAG index.")
    ap.add_argument("--db", default=PRO_DB)
    ap.add_argument("--embedder", default="auto", choices=["auto", "static", "hash"])
    ap.add_argument("--force", action="store_true", help="reclaim a live lock (deliberate)")
    ap.add_argument("--include", action="append", default=None,
                    help="override the default include list "
                         "(exchange, gists, raw/asops/txt, CFL claude-ai transcripts dir)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    includes = args.include if args.include is not None else PRO_INCLUDES
    return build_index.build(args.db, args.embedder, args.force, args.quiet, includes, PRO_ROOT)


if __name__ == "__main__":
    sys.exit(main())
