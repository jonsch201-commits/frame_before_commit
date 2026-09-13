#!/usr/bin/env python3
"""Query the CFL GraphRAG index. Hybrid: dense embeddings + fuzzy lexical + graph provenance.

⛔ THE DESIGN PROBLEM THIS FILE SOLVES, and it is not "search":

Jon, 2026-08-17 11:5x, verbatim, typos his:
  "I know graph rag alone will fail if we don't also implement vector embeding. Think about all my
   typos and imprecise language and the stylomantic differences between trunks."

That sentence names THREE distinct failure modes, and a single mechanism answers none of them:

  | failure mode        | example                        | what actually fixes it              |
  |---------------------|--------------------------------|-------------------------------------|
  | typos               | "vector embeding", "fense"     | FUZZY LEXICAL expansion (this file) |
  | imprecise language  | "how much budget is left"      | DENSE embeddings (embedder.py)      |
  | stylomantic drift   | trunk A's words != trunk B's   | dense + graph scoping               |

⚠️ AND THE TRAP WORTH NAMING, because it is the obvious wrong build: embeddings alone do NOT fix
typos. A static embedder tokenizes "embeding" into different subwords than "embedding" and can land
nowhere near it. ⭐ The typo half is carried by expanding a query term to corpus terms that share
character trigrams -- a mechanism that never needed a model at all. Building only the vector half
would have shipped something that fails the exact test Jon's sentence describes.

FUSION is Reciprocal Rank Fusion, deliberately: dense cosines and BM25 scores live on
incomparable scales, and any weighted sum of them is a calibration constant nobody will maintain.
RRF ranks, so it needs no calibration and cannot be silently miscalibrated.
AMENDED 2026-08-21 (Personal's three measured ranker defects): expansion is IDF-gated, the two
dense granularities pre-fuse into one semantic vote, and each RRF term is scaled by a
within-pool score normalization -- see EXPAND_MIN_IDF and hybrid() for the reasoning.

MODES exist so the acceptance test can prove which half earns its keep -- `--mode grep` and
`--mode graph` are the baselines that MUST FAIL the typo query. If they pass, v0 has not
demonstrated why it exists.

GRAPH LEG (CFL-D-006 / W-1, wired 2026-08-22): `hybrid()` fuses a FOURTH RRF signal --
one-hop neighbour expansion over the edge table, seeded by what dense+doc+lexical already
found, additive-only (a chunk with no graph support is never penalized), and hub-damped by
sqrt(in-degree) so a widely-linked concept page cannot outvote real sem/lex standing just by
being popular. See GRAPH_DECAY / DEFAULT_GRAPH_WEIGHT above for the measured weight choice, and
`retrieve.py --selftest` for the leg's own test coverage (dense/lexical/BM25 are covered by
build_index.py --selftest and acceptance.py; this covers only what the graph leg added).

Usage:
  python scripts/graphrag/retrieve.py "your query" [-k 8] [--mode hybrid|dense|lexical|grep|graph]
                                      [--db PATH] [--scope wiki:concepts] [--graph-weight 0.5]
                                      [--json] [--explain] [--check-stale]
  python scripts/graphrag/retrieve.py --selftest   # graph-leg unit checks (synthetic db, no
                                                    # embedder) + RP-28 latency/staleness/tier
                                                    # checks if the real index is present

RP-28 (2026-09-02): a query used to run a full-corpus staleness walk on EVERY invocation
(~85-126s, ~97% of wall time) -- see STALE_CACHE_TTL_SECONDS above and README.md's "Staleness
checking" section. That walk is now opt-in via --check-stale, TTL-cached beside the index.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embedder import load_embedder  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Single source of truth for the index location -- see the comment block in build_index.py for why
# it is off Drive. Importing it here means the reader and the writer cannot drift to two paths.
from build_index import DEFAULT_DB, corpus_fingerprint  # noqa: E402,F401  (re-exported)

TOKEN = re.compile(r"[a-z0-9]{2,}")
K1, B = 1.2, 0.75
RRF_K = 60
FUZZY_MIN_DICE = 0.45
FUZZY_MAX_EXPANSIONS = 6
POOL = 60  # per-signal candidate depth before fusion
# ⛔ Fuzzy expansion is for RARE terms and typos, and the gate is measured from the index's own
# lexical stats, NOT a stopword list (Personal's 2026-08-20 letter, defect 1: "about" was
# expanding to bout/above/abort, and that BM25 filler outvoted the rare terms the query was
# actually about). A term must clear this IDF floor -- as the source term if it is in vocabulary,
# and as each candidate when the source is OOV -- before a fuzzy guess may vote. idf 4.0 over
# this ~20k-chunk index means "appears in fewer than ~2% of chunks"; "about"/"what"/"rule" sit
# near idf 1-2 and are refused, while genuinely rare targets ("heartbeat", "stylomantic") sit
# at idf 5+ and pass. A stopword list would have to be maintained; the df column already exists.
EXPAND_MIN_IDF = 4.0
# ⛔ SUPERSESSION-RANKING LEVERS (probe evidence: P4 regressed run 2, P15/P16/P17 standing FAILs,
# cross-trunk confirmed by Personal's identical ranker_probe failures — wiki/tracker/
# PROBE-REGISTRY.md). Two multiplicative adjustments applied to the FUSED score only; the fusion
# architecture (pre-fused semantic vote + lexical vote, score-aware RRF) is untouched.
#
# L1 — ARCHIVE DEMOTION: a chunk living under an archive-class PATH SEGMENT (never content-matched)
# is demoted. 0.6 is conservative on purpose: an archived page must stay retrievable — it just may
# not outrank the live page it was archived in favour of (P17: skills/intake/archive/
# fbc-improvement-proposal outranked the binding SKILL.md).
ARCHIVE_PENALTY = 0.6
ARCHIVE_SEGMENT = re.compile(r"^(archive|superseded|deprecated|_superseded)$", re.IGNORECASE)
# L2 — SUPERSESSION-MARKER BOOST: a chunk whose TEXT carries a live-governance marker is boosted,
# so the chunk that IS the amendment outranks its superseded sibling wording (P4/P16: the 08-19
# AMENDED block must beat the 08-09-only chunks — which are NOT penalized; they stay retrievable,
# just below their amendment). Markers are matched case-sensitively to avoid noise ("STRUCK" the
# governance verdict, not "struck" the verb; "supersedes" the live relation, not "superseded").
# 1.6, not the nominal 1.5: measured 2026-08-22 on P16 — the amendment chunk (CLAUDE.md:266-287,
# base fused 0.01521) must clear its 08-09-only sibling (CLAUDE.md:248-261, fused 0.02406, which
# is lex#1 on the probe query), requiring a factor >= 1.582. 1.5 left it one rank short.
SUPERSESSION_BOOST = 1.6
SUPERSESSION_MARKERS = ("AMENDED BY JON", "the later ruling governs", "supersedes", "STRUCK")
# L3 -- STRUCTURAL SUPERSESSION DEMOTION (P2-3, 2026-08-23). L2 above is a TEXT guess: it boosts
# any chunk containing a governance marker, so it fires on pages that merely DISCUSS supersession
# and stays silent on superseded pages that never announce their own obsolescence. L3 instead reads
# a DECLARED relation: build_index emits kind='supersedes' edges from frontmatter, and the
# DESTINATION of such an edge is the superseded file. An author's assertion, not a regex's opinion.
#
# 0.6 mirrors ARCHIVE_PENALTY and for the same reason: a superseded page must stay RETRIEVABLE --
# it just must not outrank the thing that replaced it. No-deletion applies to ranking too.
#
# ⛔ BOUND, stated at the lever so it is not oversold: these are FILE-level edges. They cannot
# order two chunks of the SAME file, which is precisely what P4/P16 require (the 08-09 PII wording
# and its 08-19 amendment are both inside CLAUDE.md). L3 fixes the cross-file class going forward
# and is pre-stated as NO-MOVEMENT on P4/P15/P16/P17. See
# wiki/tracker/SEAL-P2-3-supersession-edges-2026-08-23.md.
SUPERSEDED_PENALTY = 0.6
# ⛔ GRAPH SIGNAL (CFL-D-006 / W-1, wire-before-enrich): one-hop neighbour expansion as a FOURTH
# RRF leg. Wired 2026-08-22 per the resolution letter (exchange/inbound/cfl-to-soul-herald-W1-
# RESOLVED-...-2026-08-18.md, finding :14-17, fix order :47-51) -- "graph-ANYTHING is 0 by
# construction" because hybrid() never read the edge table; one hop over the 1,056 EXISTING
# resolved edges rescued both failing acceptance cases (I1, I2) in that letter's measurement.
#
# ⛔ NO-PENALTY, BY CONSTRUCTION: graph_expand() only ADDS chunks to the fused pool (via
# contribute()'s fused.setdefault); a chunk with zero graph support is simply never touched by
# this leg -- its rrf is whatever sem+lex already gave it. "Unwired dominates thin" (the W-1
# letter's own phrase) is the failure this must not repeat in reverse: a thin graph must never
# outvote a chunk that has real sem/lex support, so the seed weight this leg propagates IS the
# seed's own fused rrf-so-far (sem+lex only) -- a chunk with weak semantic/lexical standing can
# only pass on a weak vote, never manufacture strength from an edge alone.
GRAPH_DECAY = 0.6  # single-hop attenuation: a neighbour is worth less than the seed that named it
GRAPH_CHUNKS_PER_FILE = 2  # cap: a neighbour FILE contributes its best few chunks, not all of them
# ⛔ 0.5, not the letter's naive "wire it and see" -- measured 2026-08-22 with the CONTROL PROBES
# FIRST: 0.65 flips T2 (INCONCLUSIVE -> FAIL, wiki/concepts/stylomantic.md's high in-degree pulls
# it above wiki/concepts/stochastic-retrieval-research.md and off the k=8 page) even WITH the
# sqrt(in-degree) hub damping above. 0.6 sits exactly on the T2 boundary (rank 8, the edge of the
# cliff). 0.5 clears that boundary with margin (T2 rank 8 at 0.5, same as 0.4 -- the transition to
# risk is between 0.6 and 0.65, not a hair past 0.5) while still rescuing I2 (rank None -> 7) --
# see the report's before/after tables for the full sweep. I1 is NOT rescued at this weight; a
# weight that rescues it (>=1.5) reliably breaks P13/P16/P8 via the same hub-pollution mechanism,
# so this build takes the conservative, non-regressing side of that tradeoff and reports the
# tension honestly rather than tuning to one letter's two examples.
DEFAULT_GRAPH_WEIGHT = 0.5
# ⛔ RP-28 (2026-09-02, R-1's measurement): the full-corpus staleness walk os.stat()s every one of
# ~5,986 corpus files (including the 4,597-file provenance tier, walked regardless of --tier) and
# cost 84.8-125.9s of a 118-130s query -- ~97% of wall time, for an advisory-only WARN that never
# blocks or reorders a result. It ran on EVERY query, unconditionally, from this same call site.
# Fix: the walk is now OFF by default (never invoked unless --check-stale is passed) and, even
# then, throttled by a small TTL-cached fingerprint file beside the index so an operator who runs
# --check-stale repeatedly does not repay the full walk more than once per TTL window. See
# Index.staleness() / --check-stale below and scripts/graphrag/README.md ("Staleness checking").
STALE_CACHE_TTL_SECONDS = 6 * 3600
# WS-1 (2026-09-06, CFL a86404c0): RP-28's fix was right about the cost and wrong about the
# fallback -- it made the DEFAULT path return (False, "") in 0.00s, which is byte-identical to
# the value a clean check returns. So "I did not look" and "I looked and it is fresh" became the
# same answer, and every CFL retrieval since 2026-09-02 has printed no freshness verdict at all.
# That is UNKNOWN rendered as PASS, inside the retriever whose own skill file (skills/wiki-query)
# names confident-absence as the worst failure grade and promises a STALE banner on EVERY query.
# [measured 2026-09-06 22:2x, this index, cache bypassed, 3 runs] the full walk now costs
# 0.13s / 3,619 os.stat() calls -- not the 84.8-125.9s RP-28 recorded. _staleness_walk() has NO
# short-circuit (it computes the whole fingerprint before comparing), so 0.13s is the full-sweep
# cost, not a stale-case early exit. CONFIRMED the same session [measured 2026-09-06 22:4x, same code,
# same process, one run each]: the identical corpus_fingerprint() walk costs 0.13s / 3,615
# os.stat() on N:\claude-cfl\clone and 78.15s / 9,287 os.stat() on the G:\My Drive Drive copy --
# ~600x. RP-28's 84.8-125.9s is consistent with a Drive-resident corpus and was almost certainly
# RIGHT WHEN WRITTEN; the 09-02 move to N: is what expired it. CONFOUND, stated: the two trees
# are not byte-identical (3,615 vs 9,287 stat calls), so this is a same-code/different-filesystem
# measurement, not a controlled one -- the 600x is the right order of magnitude, not a ratio to
# quote to three figures.
# THIS IS THE ARGUMENT FOR A BUDGET RATHER THAN A CONSTANT, now with a number under it: on G: the
# walk (78s) blows the 5s budget and this code degrades to a LOUD "UNKNOWN"; on N: it costs 0.13s
# and checks every query. The same source file does the right thing on both, and neither answer
# is silence.
# So the walk is ON by default again, but the latency guarantee RP-28 bought is kept by BUDGET,
# not by silence: the cache remembers how long the last walk actually took, and a corpus whose
# walk exceeds the budget degrades to a LOUD "UNKNOWN" instead of a quiet "fresh". The failure
# mode this repo keeps paying for is an alarm that cannot fire; the failure mode it can afford is
# an alarm that says it could not look.
STALE_WALK_BUDGET_SECONDS = float(os.environ.get("CFL_STALE_WALK_BUDGET", "5.0"))


def _stale_cache_path(db_path):
    return db_path + ".staleness_cache.json"


def _read_stale_cache(db_path):
    try:
        with open(_stale_cache_path(db_path), "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _write_stale_cache(db_path, is_stale, message, walk_seconds=None, index_built_utc=None):
    """`walk_seconds` is what makes the budget self-adapting: the NEXT invocation reads it to
    decide whether it can afford to look again. A cache written without it (an older file) is
    treated as unknown-cost and the walk is attempted once to find out."""
    payload = {"checked_utc": time.time(), "is_stale": is_stale, "message": message,
               "walk_seconds": walk_seconds, "index_built_utc": index_built_utc}
    try:
        with open(_stale_cache_path(db_path), "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except OSError:
        pass  # the cache is advisory-only; a write failure must not break the query itself


def trigrams(term: str):
    padded = f"  {term} "
    return {padded[i : i + 3] for i in range(len(padded) - 2)}


class Index:
    def __init__(self, db_path: str = DEFAULT_DB):
        if not os.path.isfile(db_path):
            raise SystemExit(f"FAIL index not found: {db_path}\n"
                             f"     build it: python scripts/graphrag/build_index.py")
        self.db_path = db_path
        self.con = sqlite3.connect(db_path)
        self.meta = dict(self.con.execute("SELECT key, value FROM meta"))
        self.dims = int(self.meta.get("dims", "0"))
        self.n_chunks = int(self.meta.get("n_chunks", "0"))
        self.avgdl = float(self.meta.get("avg_chunk_tokens", "200") or 200.0)
        self._vecs = None
        self._vec_ids = None
        self._docvecs = None
        self._doc_ids = None
        self._emb = None
        # Default scope is the knowledge tier. See tier_of() in build_index.py: the intake-triage
        # QUEUE is 72% of the index and letting it compete drowns the concept pages it is supposed
        # to be triaged into; the PROVENANCE tier (raw/transcripts/**) is 4,376 more files and
        # would drown them harder.
        #
        # THIS WAS A BOOLEAN UNTIL 2026-08-23 AND THE BOOLEAN WAS A LATENT TRAP. `_in_tier` read
        # `tier != "queue"`, so the instant a THIRD tier existed it would have been admitted to the
        # default scope by default -- the fail-OPEN direction, and invisible, because a new tier
        # arrives as a data change and not a code change. An allow-set fails CLOSED: a tier nobody
        # has named is not searched until somebody names it.
        #
        # `tiers = None` means every tier (--all-tiers).
        self.tiers = {"knowledge"}
        self._tier = {row[0]: row[1] for row in self.con.execute("SELECT id, tier FROM files")}

    @property
    def include_queue(self):
        """Back-compat for callers written against the two-tier boolean."""
        return self.tiers is None or "queue" in self.tiers

    @include_queue.setter
    def include_queue(self, value):
        if value:
            self.tiers = None
        else:
            self.tiers = {"knowledge"}

    def tiers_present(self):
        return sorted(set(self._tier.values()))

    def _staleness_walk(self):
        """(is_stale, message). The EXPENSIVE path: a full os.stat() of every corpus file (RP-28:
        84.8-125.9s measured, ~97% of a query's wall time). Never call this directly from a query
        path -- go through staleness(check=...) below, which gates it behind --check-stale and a
        TTL cache. Message text is UNCHANGED from the pre-RP-28 wording so any downstream reader
        (dashboards, saved output) that greps for it keeps matching."""
        stored = self.meta.get("corpus_fingerprint")
        if not stored:
            return True, "index predates staleness tracking -- rebuild to enable it"
        # Fingerprint the SAME corpus the index was built over: an index built with --include
        # widens the walk, and checking against the bare default here would report STALE forever.
        # Same for the ROOT (Personal's 2026-08-19 letter, ask 3): an index built over another
        # trunk must be checked against THAT tree, not the one this file happens to live in --
        # otherwise every query on a foreign index prints a staleness verdict about OUR wiki.
        includes = json.loads(self.meta.get("corpus_includes") or "[]")
        root = self.meta.get("corpus_root") or None
        # Same argument as includes/root, for the provenance widening: an index built with
        # `--provenance <other trunk>` must be checked against THAT walk, or it reports STALE on
        # every query forever -- an alarm that always fires, which this repo already has on record
        # as a defect class of its own.
        prov = json.loads(self.meta.get("corpus_provenance") or "[]")
        if stored != corpus_fingerprint(includes, root, prov):
            return True, ("the corpus has CHANGED since this index was built "
                          f"(built {self.meta.get('built_utc')}) -- results may be out of date; "
                          "run scripts/graphrag/build_index.py")
        return False, ""

    def freshness(self, force=False):
        """(state, message) where state is exactly one of "FRESH", "STALE", "UNKNOWN".

        WS-1. This is the primitive; `staleness()` below is the back-compat 2-tuple shim. The
        whole point of the third state is that a caller can tell "I looked and the index matches
        the corpus" apart from "I did not look" -- RP-28 returned the same value for both, so the
        banner documented in skills/wiki-query/SKILL.md could not fire on any default query.

        Order, and every branch is cheap by construction:
          1. TTL cache younger than STALE_CACHE_TTL_SECONDS -> reuse it (no disk walk at all).
          2. The last recorded walk cost more than STALE_WALK_BUDGET_SECONDS -> refuse to pay it
             again and return UNKNOWN *loudly*, naming the cost and the flag that overrides.
          3. Otherwise walk, time it, and remember the cost so step 2 can adapt.
        `force=True` (the CLI's --check-stale) bypasses BOTH the TTL and the budget: it is the
        operator saying "spend it". Never blocks, never reorders results -- still advisory.
        """
        cached = _read_stale_cache(self.db_path)
        # ⛔ WW-15 (2026-09-07, peer review by 46276084; FIRST MINTED AS "WS-2", WHICH ALREADY EXISTS on
        # wayfinder-wikiskills-grounding-2026-09-05.md:46 -- I flagged my descendant's WS-1 collision and
        # minted a colliding id in the same letter. Its id, not mine, is the one the record keeps.):
        # THE TTL CACHE WAS NOT BOUND TO THE INDEX
        # IT DESCRIBED, so a STALE verdict outlived the rebuild that answered it. Measured: after
        # `build_index.py` re-wrote the index (built_utc 2026-09-07T11:55:38Z, 113,813 chunks) every
        # query still printed `freshness=STALE ... (built 2026-09-06T03:39:22Z)` -- the cached
        # message, for the remaining 6h of TTL. **The banner names one remedy, and running that
        # remedy does not clear the banner** -- an alarm that cannot be silenced by its own
        # prescribed fix is one a reader learns to ignore, which is the WS-1 defect wearing the
        # opposite costume (WS-1: silence that read as a pass; this: a pass that reads as silence).
        # The VERDICT is discarded on rebuild; the recorded WALK COST is deliberately kept, because
        # cost is a property of the filesystem (G: ~78s vs N: ~0.13s) and not of the build.
        _built = (self.meta or {}).get("built_utc")
        if cached is not None and cached.get("index_built_utc") != _built:
            cached = {"walk_seconds": cached.get("walk_seconds")}
        if not force and cached and (time.time() - cached.get("checked_utc", 0)) < STALE_CACHE_TTL_SECONDS:
            return ("STALE" if cached.get("is_stale") else "FRESH"), cached.get("message", "")
        if not force and cached is not None:
            last = cached.get("walk_seconds")
            if last is not None and last > STALE_WALK_BUDGET_SECONDS:
                return "UNKNOWN", (
                    f"freshness NOT checked: the last corpus walk took {last:.1f}s, over the "
                    f"{STALE_WALK_BUDGET_SECONDS:.1f}s budget (CFL_STALE_WALK_BUDGET). These "
                    "results are UNBOUNDED -- re-run with --check-stale to pay for a verdict.")
        t0 = time.perf_counter()
        is_stale, message = self._staleness_walk()
        walked = time.perf_counter() - t0
        _write_stale_cache(self.db_path, is_stale, message, walk_seconds=walked,
                           index_built_utc=_built)
        return ("STALE" if is_stale else "FRESH"), message

    def staleness(self, check=False):
        """(is_stale, message) -- BACK-COMPAT SHIM over freshness(); prefer freshness().

        Kept because its exact 2-tuple shape is referenced by older scripts and letters. It
        cannot represent UNKNOWN, which is precisely the defect WS-1 exists to fix: UNKNOWN
        collapses to is_stale=True here (the safe direction -- an unbounded index is not a fresh
        one) rather than to the False that RP-28 returned. `check` maps to `force`."""
        state, message = self.freshness(force=check)
        return (state != "FRESH"), message

    # -- lazily loaded, because the lexical and grep modes never need either one
    #
    # ⛔ RP-28 point 2 (R-1's measurement): a `--tier knowledge` query used to load ALL 41,577
    # chunk vectors and ALL 5,986 doc vectors -- every tier, including the 4,597-file provenance
    # tier -- then throw away the non-knowledge rows post-hoc in `_apply_scope`/`doc_dense`'s own
    # `_fid_in_tier` check. That waste was small in absolute terms (~1.5s of the ~130s total,
    # R-1's §4) but real, and it scales with corpus growth in the tiers the query never asked for.
    # Fix: when `self.tiers` is a scoped set (not None/--all-tiers), the SQL itself joins to
    # `files.tier` and only loads vectors whose file is in-scope -- so a `--tier knowledge` query's
    # vector load shrinks with the knowledge tier's own size (770 files), not the whole corpus's.
    @property
    def vectors(self):
        if self._vecs is None:
            if self.tiers is None:
                query, params = "SELECT chunk_id, vec FROM vectors ORDER BY chunk_id", ()
            else:
                marks = ",".join("?" * len(self.tiers))
                query = (f"SELECT v.chunk_id, v.vec FROM vectors v "
                         f"JOIN chunks c ON c.id = v.chunk_id "
                         f"JOIN files f ON f.id = c.file_id "
                         f"WHERE f.tier IN ({marks}) ORDER BY v.chunk_id")
                params = tuple(self.tiers)
            ids, blobs = [], []
            for cid, blob in self.con.execute(query, params):
                ids.append(cid)
                blobs.append(np.frombuffer(blob, dtype=np.float32))
            self._vec_ids = np.array(ids, dtype=np.int64)
            self._vecs = (np.vstack(blobs) if blobs
                          else np.zeros((0, self.dims), dtype=np.float32))
        return self._vec_ids, self._vecs

    @property
    def docvectors(self):
        if self._docvecs is None:
            if self.tiers is None:
                query, params = "SELECT file_id, vec FROM docvecs ORDER BY file_id", ()
            else:
                marks = ",".join("?" * len(self.tiers))
                query = (f"SELECT d.file_id, d.vec FROM docvecs d "
                         f"JOIN files f ON f.id = d.file_id "
                         f"WHERE f.tier IN ({marks}) ORDER BY d.file_id")
                params = tuple(self.tiers)
            ids, blobs = [], []
            for fid, blob in self.con.execute(query, params):
                ids.append(fid)
                blobs.append(np.frombuffer(blob, dtype=np.float32))
            self._doc_ids = np.array(ids, dtype=np.int64)
            self._docvecs = (np.vstack(blobs) if blobs
                             else np.zeros((0, self.dims), dtype=np.float32))
        return self._doc_ids, self._docvecs

    @property
    def embedder(self):
        if self._emb is None:
            self._emb = load_embedder("auto")
            built_with = self.meta.get("embedder", "?")
            if self._emb.name != built_with:
                # ⛔ Querying with a different model than the index was built with returns
                # confident nonsense: the two vector spaces are unrelated. Refuse, loudly.
                raise SystemExit(
                    f"FAIL embedder mismatch: index built with {built_with!r}, this run loaded "
                    f"{self._emb.name!r}. Rebuild the index or fix the environment -- comparing "
                    f"vectors across models is meaningless, not merely inaccurate.")
        return self._emb

    # ⛔ BATCHED 2026-09-07 (WW-20). This was ONE `IN (...)` with a placeholder per id, and it
    # raised `sqlite3.OperationalError: too many SQL variables` the first time the corpus was
    # actually complete: `--scope provenance` over the newly-exported session transcripts pushed
    # the lexical candidate list past SQLite's ~32k parameter ceiling and the whole query DIED.
    # ⚠️ The defect was invisible for as long as the corpus was thin -- it is a bug that only
    # appears once the fix it depends on has worked, which is why nothing caught it earlier.
    # 900 keeps a margin under the conservative 999-parameter build limit too.
    _SQL_VAR_BATCH = 900

    def chunk_rows(self, cids):
        if not cids:
            return {}
        cids = list(cids)
        out = {}
        for i in range(0, len(cids), self._SQL_VAR_BATCH):
            batch = cids[i:i + self._SQL_VAR_BATCH]
            marks = ",".join("?" * len(batch))
            rows = self.con.execute(
                f"SELECT c.id, f.path, f.kind, c.heading, c.start_line, c.end_line, c.ntok, "
                f"c.text, f.tier, f.id FROM chunks c JOIN files f ON f.id = c.file_id "
                f"WHERE c.id IN ({marks})",
                batch)
            for r in rows:
                out[r[0]] = {"chunk_id": r[0], "path": r[1], "kind": r[2], "heading": r[3],
                             "start_line": r[4], "end_line": r[5], "ntok": r[6], "text": r[7],
                             "tier": r[8], "file_id": r[9]}
        return out

    @property
    def superseded_files(self):
        """file_ids that some other file's frontmatter DECLARES it supersedes (L3).

        Cached per-connection: this is one small query against an indexed column, but hybrid()
        applies the lever once per pooled candidate and must not re-query per chunk.

        An index built before L3 existed simply has no 'supersedes' rows, so this returns an empty
        set and every L3 multiplication is a no-op -- the lever is inert on an old index rather
        than wrong, which is the behaviour we want from a ranking change that ships ahead of a
        rebuild.
        """
        if getattr(self, "_superseded_files", None) is None:
            try:
                self._superseded_files = {
                    r[0] for r in self.con.execute(
                        "SELECT DISTINCT dst FROM edges WHERE kind='supersedes' AND dst > 0")}
            except Exception:
                # A pre-L3 schema or a partially-written index must degrade to "no demotion",
                # never to a traceback inside ranking.
                self._superseded_files = set()
        return self._superseded_files

    @property
    def chunk_file(self):
        """chunk_id -> file_id, loaded once. Needed to tier-filter without a join per candidate."""
        if not hasattr(self, "_chunk_file_map"):
            self._chunk_file_map = {r[0]: r[1]
                                    for r in self.con.execute("SELECT id, file_id FROM chunks")}
        return self._chunk_file_map

    def _in_tier(self, chunk_id) -> bool:
        return self._fid_in_tier(self.chunk_file.get(chunk_id))

    def _fid_in_tier(self, file_id) -> bool:
        if self.tiers is None:
            return True
        return self._tier.get(file_id, "knowledge") in self.tiers

    # ------------------------------------------------------------ signals

    def _df(self, term):
        row = self.con.execute("SELECT df FROM terms WHERE term=?", (term,)).fetchone()
        return row[0] if row else None

    def _idf(self, df):
        n = max(self.n_chunks, 1)
        return float(np.log(1.0 + (n - df + 0.5) / (df + 0.5)))

    def expand_terms(self, tokens):
        """Query token -> [(corpus_term, weight)]. This is the typo mechanism.

        An exact vocabulary hit keeps weight 1.0. A token the corpus has never seen is matched
        against the vocabulary by character-trigram Dice similarity, and each surviving candidate
        enters the query DOWN-WEIGHTED by its similarity -- a guess should never outvote a fact.

        Expansion is IDF-GATED (see EXPAND_MIN_IDF): an in-vocabulary term expands only if it is
        itself rare enough to be worth chasing typo variants of, and an OOV term's candidates must
        each clear the same floor -- which is the mean-IDF gate applied at candidate granularity:
        the mean IDF of what survives is >= the floor by construction, and a filler word can never
        ride in on one lucky trigram overlap.
        """
        out = {}
        for tok in tokens:
            df = self._df(tok)
            cands = {}
            tok_idf = None
            if df is not None:
                cands[tok] = 1.0
                tok_idf = self._idf(df)
            want_fuzzy = (df is None) or (len(tok) >= 5 and tok_idf >= EXPAND_MIN_IDF)
            if want_fuzzy:
                tris = trigrams(tok)
                if tris:
                    marks = ",".join("?" * len(tris))
                    counted = self.con.execute(
                        f"SELECT term, COUNT(*) c FROM vocab_tri WHERE tri IN ({marks}) "
                        f"GROUP BY term ORDER BY c DESC LIMIT 400", list(tris))
                    scored = []
                    for term, shared in counted:
                        dice = 2.0 * shared / (len(tris) + len(trigrams(term)))
                        if dice >= FUZZY_MIN_DICE and term != tok:
                            scored.append((dice, term))
                    scored.sort(reverse=True)
                    kept = 0
                    for dice, term in scored:
                        if kept >= FUZZY_MAX_EXPANSIONS:
                            break
                        cand_df = self._df(term)
                        if cand_df is None or self._idf(cand_df) < EXPAND_MIN_IDF:
                            continue  # a guess landing on a common word is filler, not recall
                        cands[term] = max(cands.get(term, 0.0), round(dice, 3))
                        kept += 1
            out[tok] = sorted(cands.items(), key=lambda kv: -kv[1])
        return out

    def lexical(self, query, scope=None, pool=POOL):
        tokens = TOKEN.findall(query.lower())
        expansions = self.expand_terms(tokens)
        scores, hits = {}, {}
        for tok, cands in expansions.items():
            # One query token casts ONE vote per chunk: the BEST-matching variant, never the sum.
            # Summing variants let "stylomantic" + "stylo" + "stylometric" count the same
            # occurrence three times over, so pages that repeat a term (YAML frontmatter, titles)
            # outscored the page that defines it -- the guesses were stacking on top of the fact.
            tok_scores = {}
            for term, weight in cands:
                df = self._df(term)
                if df is None:
                    continue
                idf = self._idf(df)
                for cid, tf, dl in self.con.execute(
                        "SELECT p.chunk_id, p.tf, c.ntok FROM postings p "
                        "JOIN chunks c ON c.id = p.chunk_id WHERE p.term=?", (term,)):
                    denom = tf + K1 * (1 - B + B * (dl or 1) / max(self.avgdl, 1.0))
                    contrib = weight * idf * (tf * (K1 + 1)) / denom
                    if contrib > tok_scores.get(cid, 0.0):
                        tok_scores[cid] = contrib
                    hits.setdefault(cid, set()).add(f"{term}({weight:g})")
            for cid, contrib in tok_scores.items():
                scores[cid] = scores.get(cid, 0.0) + contrib
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])
        ranked = self._apply_scope(ranked, scope)
        return ranked[:pool], expansions, hits

    def dense(self, query, scope=None, pool=POOL):
        ids, mat = self.vectors
        if mat.shape[0] == 0:
            return []
        qvec = self.embedder.encode([query])[0]
        sims = mat @ qvec
        take = min(pool * 4, sims.shape[0])
        top = np.argpartition(-sims, take - 1)[:take]
        ranked = sorted(((int(ids[i]), float(sims[i])) for i in top), key=lambda kv: -kv[1])
        return self._apply_scope(ranked, scope)[:pool]

    def grep(self, query, scope=None, pool=POOL):
        """BASELINE. Every query token must appear literally. This is what we have today."""
        tokens = TOKEN.findall(query.lower())
        if not tokens:
            return []
        out = []
        for cid, heading, text in self.con.execute("SELECT id, heading, text FROM chunks"):
            hay = ((heading or "") + " " + text).lower()
            if all(tok in hay for tok in tokens):
                out.append((cid, float(sum(hay.count(t) for t in tokens))))
        out.sort(key=lambda kv: -kv[1])
        return self._apply_scope(out, scope)[:pool]

    def graph_only(self, query, scope=None, pool=POOL):
        """BASELINE. Graph traversal needs an ENTRY NODE, and v0's entry is a title/slug match.

        ⭐ That is precisely why graph-alone fails Jon's sentence: a misspelled or paraphrased query
        never matches a node label, so the traversal has nowhere to start. The failure is
        structural, not a tuning problem.
        """
        tokens = set(TOKEN.findall(query.lower()))
        seeds = []
        for fid, path in self.con.execute("SELECT id, path FROM files"):
            slug = set(TOKEN.findall(os.path.basename(path)[:-3].lower()))
            if slug and tokens and slug & tokens == tokens:
                seeds.append(fid)
        if not seeds:
            return []
        reach = set(seeds)
        for fid in list(seeds):
            for (dst,) in self.con.execute("SELECT dst FROM edges WHERE src=? AND dst>0", (fid,)):
                reach.add(dst)
        marks = ",".join("?" * len(reach))
        rows = self.con.execute(
            f"SELECT id FROM chunks WHERE file_id IN ({marks}) ORDER BY file_id, ord", list(reach))
        return self._apply_scope([(r[0], 1.0) for r in rows], scope)[:pool]

    def _apply_scope(self, ranked, scope):
        ranked = [(cid, s) for cid, s in ranked if self._in_tier(cid)]
        if not scope:
            return ranked
        rows = self.chunk_rows([cid for cid, _ in ranked])
        return [(cid, s) for cid, s in ranked if rows.get(cid, {}).get("kind", "").startswith(scope)]

    def doc_dense(self, query, scope=None, pool=POOL, per_doc=2):
        """DOCUMENT-level dense signal: rank files, then surface each file's best chunks.

        ⭐ This is the answer to a measured failure, not a flourish. `[measured 2026-08-17 17:3x]`
        the chunk of `concepts/coordinator.md` that answers "which seat only hands work out" sat at
        CHUNK-dense rank 4,105 of 16,132: a 135-token chunk is a narrow target and a broad
        paraphrastic question hits none of them squarely. It hits the DOCUMENT. Ranking documents
        first, then descending into their chunks, gives a page a chance to compete on what it is
        about rather than on whether one paragraph happened to echo the question's wording.
        """
        doc_ids, doc_mat = self.docvectors
        if doc_mat.shape[0] == 0:
            return []
        qvec = self.embedder.encode([query])[0]
        sims = doc_mat @ qvec
        take = min(pool, sims.shape[0])
        top = np.argpartition(-sims, take - 1)[:take]
        ordered = sorted(((int(doc_ids[i]), float(sims[i])) for i in top), key=lambda kv: -kv[1])
        out = []
        for fid, dsim in ordered:
            if not self._fid_in_tier(fid):
                continue
            # Within a winning document, pick the chunks that actually mention the query -- the
            # document vector says WHICH page, the chunk vector says WHERE on it.
            ids, mat = self.vectors
            rows = [r[0] for r in self.con.execute(
                "SELECT id FROM chunks WHERE file_id=? ORDER BY ord", (fid,))]
            if not rows:
                continue
            pos = {int(c): i for i, c in enumerate(ids)}
            local = [(c, float(mat[pos[c]] @ qvec)) for c in rows if c in pos]
            local.sort(key=lambda kv: -kv[1])
            for cid, csim in local[:per_doc]:
                out.append((cid, dsim + 0.25 * csim))
        out.sort(key=lambda kv: -kv[1])
        return self._apply_scope(out, scope)[:pool]

    # ------------------------------------------------------------ fusion

    def hybrid(self, query, scope=None, k=8, graph_weight=DEFAULT_GRAPH_WEIGHT):
        """Score-aware RRF over THREE modalities: semantic (chunk+doc dense, pre-fused), lexical,
        and one-hop graph expansion over the other two (CFL-D-006 / W-1 -- see GRAPH_DECAY above).

        ⛔ WHY TWO AND NOT THREE (Personal's 2026-08-20 letter, defect 2 -- the structural one):
        dense() and doc_dense() are ONE embedder read at two granularities. Contributing them to
        RRF as two peers of lexical gave the embedder's opinion two votes against lexical's one,
        so any semantic bias -- including the measured vocabulary-overlap blindness of a static
        embedder -- was structurally amplified. The fix chosen here is PRE-FUSION, not reweighting:
        the two granularities are first RRF-fused into a single semantic ranking, and that ranking
        casts one vote against lexical's one. Pre-fusion is preferred over halving the weights
        because the two granularities are only MODERATELY correlated on CFL data (measured
        2026-08-21: chunk-level Spearman 0.26-0.48 on the three probe queries) -- the doc signal
        genuinely rescues chunks the chunk signal misses (the rank-4,105 case in doc_dense's
        docstring), so both must still contribute to semantic RECALL; they just may not both
        contribute to cross-modality VOTING WEIGHT.

        ⛔ WHY SCORE-AWARE AND NOT RANK-ONLY (defect 3): rank-only RRF is degenerate across
        heterogeneous indexes -- rank 1 of a 1,237-chunk index ties rank 1 of a 208,028-chunk one,
        and within one index a signal that barely discriminates ties one that discriminates
        sharply, which is what produced the all-scores-identical 0.01639 scoreboards. Each
        signal's contribution is therefore its RRF term scaled by (0.5 + 0.5 * s_norm), where
        s_norm is the raw score min-max normalized WITHIN that signal's own candidate pool.
        This is self-calibrating -- it maps every signal to [0,1] from its own pool, so it is
        NOT the cross-scale weighted sum the module docstring forbids (no constant relates cosine
        to BM25; nothing has to be maintained) -- and it is score-aware: a rank-1 that leads its
        pool by a wide score margin outvotes a rank-1 in a flat pool, and a signal whose pool has
        NO score spread (max == min: it cannot discriminate at all) is held at the 0.5 midpoint
        instead of casting full-strength votes.
        """
        dense_hits = self.dense(query, scope)
        doc_hits = self.doc_dense(query, scope)
        lex_hits, expansions, matched = self.lexical(query, scope)

        # -- pre-fuse the embedder's two granularities into ONE semantic signal (rank-RRF is fine
        #    here: both lists come from the same model, so this is intra-modality tie-breaking).
        sem_scores = {}
        for hits in (dense_hits, doc_hits):
            for rank, (cid, _) in enumerate(hits):
                sem_scores[cid] = sem_scores.get(cid, 0.0) + 1.0 / (RRF_K + rank + 1)
        sem_hits = sorted(sem_scores.items(), key=lambda kv: -kv[1])[:POOL]

        dense_rank = {cid: r + 1 for r, (cid, _) in enumerate(dense_hits)}
        doc_rank = {cid: r + 1 for r, (cid, _) in enumerate(doc_hits)}
        fused = {}
        self._contribute(fused, sem_hits, "sem", dense_rank=dense_rank, doc_rank=doc_rank)
        self._contribute(fused, lex_hits, "lex")

        # -- graph leg: seeded by what sem+lex ALREADY established (fused["rrf"] so far), never
        #    by a flat weight -- a chunk with no sem/lex standing cannot seed a neighbour boost,
        #    and a chunk with zero graph support is simply never revisited here (no penalty --
        #    see the NO-PENALTY selftest, which asserts exactly this against _contribute directly).
        if graph_weight > 0.0:
            seed_weights = {cid: slot["rrf"] for cid, slot in fused.items()}
            graph_hits = self.graph_expand(seed_weights, scope)
            self._contribute(fused, graph_hits, "graph", weight=graph_weight)

        # -- supersession-ranking levers (see ARCHIVE_PENALTY / SUPERSESSION_BOOST above).
        #    Applied to the fused score of every pooled candidate BEFORE the top-k cut, so a
        #    boosted amendment can climb into k and a demoted archive page can fall out of it.
        rows = self.chunk_rows(list(fused))
        for cid, slot in fused.items():
            row = rows.get(cid)
            if not row:
                continue
            if any(ARCHIVE_SEGMENT.match(seg)
                   for seg in re.split(r"[\\/]+", row["path"])[:-1]):
                slot["rrf"] *= ARCHIVE_PENALTY
            if any(marker in (row["text"] or "") for marker in SUPERSESSION_MARKERS):
                slot["rrf"] *= SUPERSESSION_BOOST
            # L3 -- declared supersession: this file is the DST of a kind='supersedes' edge,
            # i.e. some other page's frontmatter asserts it replaced this one.
            if row["file_id"] in self.superseded_files:
                slot["rrf"] *= SUPERSEDED_PENALTY

        order = sorted(fused.items(), key=lambda kv: -kv[1]["rrf"])[:k]
        return order, expansions, matched

    @staticmethod
    def _contribute(fused, hits, label, weight=1.0, dense_rank=None, doc_rank=None):
        """Score-aware RRF contribution of ONE signal's candidate list into the shared `fused`
        pool -- pulled out of hybrid() so it is independently testable (see selftest() below,
        which exercises the NO-PENALTY property directly against this function: calling it with
        an empty or irrelevant `hits` list must leave every existing slot's rrf UNCHANGED).

        This is pure w.r.t. `fused` except for in-place mutation -- no query, no DB, no self
        needed, hence @staticmethod. `label` in {"sem", "lex", "graph"} controls which rank field
        gets recorded for --explain / the per-signal columns in the CLI output.
        """
        if not hits:
            return
        scores = [s for _, s in hits]
        lo, hi = min(scores), max(scores)
        span = hi - lo
        for rank, (cid, s) in enumerate(hits):
            s_norm = 0.5 if span <= 0.0 else (s - lo) / span
            slot = fused.setdefault(
                cid, {"dense": None, "doc": None, "lex": None, "graph": None, "rrf": 0.0})
            slot["rrf"] += weight * (1.0 / (RRF_K + rank + 1)) * (0.5 + 0.5 * s_norm)
            if label == "sem":
                slot["dense"] = (dense_rank or {}).get(cid)
                slot["doc"] = (doc_rank or {}).get(cid)
            elif label == "lex":
                slot["lex"] = rank + 1
            elif label == "graph":
                slot["graph"] = rank + 1

    @property
    def in_degree(self):
        """file_id -> resolved in-degree, loaded once. See HUB_DAMPING below: measured 2026-08-22,
        wiki/concepts/frame-before-commit.md alone has in-degree 105 (of 1,056 resolved edges
        total) -- undamped, ANY query whose sem/lex pool happens to touch even a handful of its
        105 linking pages floods that one hub into results for unrelated queries. A hub is
        popular, not relevant to THIS query, so its vote is discounted by how popular it is."""
        if not hasattr(self, "_in_degree"):
            self._in_degree = dict(self.con.execute(
                "SELECT dst, COUNT(*) FROM edges WHERE dst>0 GROUP BY dst"))
        return self._in_degree

    def graph_expand(self, seed_weights, scope=None):
        """One-hop neighbour expansion over EXISTING edges, seeded by the sem+lex fused weight
        of each candidate already in the pool. Returns [(chunk_id, score)], highest first.

        seed_weights: {chunk_id: fused_rrf_so_far} -- the seed's OWN standing, not a flat 1.0,
        so a weak seed casts a weak vote for its neighbours (see the no-penalty note above).

        HUB_DAMPING (measured 2026-08-22, see in_degree docstring): each edge's vote is divided
        by sqrt(in-degree of the destination) -- a page linked from 105 places needs ~10x the
        raw seed support of a page linked from 1 to earn the same score, so a well-connected
        concept page can still surface (it is not zeroed) but cannot outvote real sem/lex
        standing just by being widely cited.
        """
        file_weight = {}
        for cid, w in seed_weights.items():
            fid = self.chunk_file.get(cid)
            if fid is None or w <= 0.0:
                continue
            file_weight[fid] = file_weight.get(fid, 0.0) + w
        if not file_weight:
            return []
        neighbour_weight = {}
        for fid, w in file_weight.items():
            for (dst,) in self.con.execute(
                    "SELECT DISTINCT dst FROM edges WHERE src=? AND dst>0", (fid,)):
                if dst == fid:
                    continue  # a self-link is not a neighbour
                damp = np.sqrt(max(1, self.in_degree.get(dst, 1)))
                neighbour_weight[dst] = neighbour_weight.get(dst, 0.0) + (w * GRAPH_DECAY) / damp
        if not neighbour_weight:
            return []
        out = {}
        for fid, w in neighbour_weight.items():
            for (cid,) in self.con.execute(
                    "SELECT id FROM chunks WHERE file_id=? ORDER BY ord LIMIT ?",
                    (fid, GRAPH_CHUNKS_PER_FILE)):
                out[cid] = out.get(cid, 0.0) + w
        ranked = sorted(out.items(), key=lambda kv: -kv[1])
        return self._apply_scope(ranked, scope)[:POOL]

    def neighbours(self, path, limit=6):
        row = self.con.execute("SELECT id FROM files WHERE path=?", (path,)).fetchone()
        if not row:
            return []
        out = []
        for (dst,) in self.con.execute(
                "SELECT DISTINCT dst FROM edges WHERE src=? AND dst>0 LIMIT ?", (row[0], limit)):
            p = self.con.execute("SELECT path FROM files WHERE id=?", (dst,)).fetchone()
            if p:
                out.append(p[0])
        return out


def resolve_tiers(args, idx):
    """Which tiers this query may see. None == all.

    Precedence: --all-tiers > --tier > (--scope inference) > default {knowledge}.

    THE --scope INFERENCE IS DELIBERATE AND IT IS THE ERGONOMIC THAT MAKES THE TIER USABLE.
    `--scope` filters on the KIND prefix and runs AFTER the tier filter, so
    `--scope provenance` on the old code returned zero rows and looked like an empty corpus
    rather than a closed door -- a silent-empty, which this repo already has on record as its
    worst failure shape. If you name a scope, you get the tier that scope lives in.
    """
    if getattr(args, "all_tiers", False):
        return None
    raw = getattr(args, "tier", None)
    if raw:
        want = {t.strip() for t in raw.replace(",", " ").split() if t.strip()}
        if "all" in want:
            return None
        present = set(idx.tiers_present())
        unknown = want - present
        if unknown:
            print(f"WARN unknown tier(s) {sorted(unknown)}; index has {sorted(present)}",
                  file=sys.stderr)
        return want
    scope = getattr(args, "scope", None)
    if scope:
        head = scope.split(":")[0]
        by_kind = {"provenance": "provenance"}
        if head in by_kind:
            return {"knowledge", by_kind[head]}
    return {"knowledge"}


def snippet(text, width=220):
    flat = " ".join(text.split())
    return flat[:width] + ("..." if len(flat) > width else "")


def run(args) -> int:
    idx = Index(args.db)
    idx.tiers = resolve_tiers(args, idx)
    mode = args.mode
    expansions, matched = {}, {}

    if mode == "hybrid":
        order, expansions, matched = idx.hybrid(
            args.query, args.scope, args.k, graph_weight=args.graph_weight)
        results = [(cid, info["rrf"], info) for cid, info in order]
    else:
        if mode == "dense":
            raw = idx.dense(args.query, args.scope)
        elif mode == "doc":
            raw = idx.doc_dense(args.query, args.scope)
        elif mode == "lexical":
            raw, expansions, matched = idx.lexical(args.query, args.scope)
        elif mode == "grep":
            raw = idx.grep(args.query, args.scope)
        else:
            raw = idx.graph_only(args.query, args.scope)
        results = [(cid, score, {}) for cid, score in raw[: args.k]]

    rows = idx.chunk_rows([cid for cid, _, _ in results])
    payload = []
    for rank, (cid, score, info) in enumerate(results, start=1):
        row = rows.get(cid)
        if not row:
            continue
        item = {
            "rank": rank,
            "score": round(float(score), 5),
            "source": f"{row['path']}:{row['start_line']}-{row['end_line']}",
            "heading": row["heading"],
            "kind": row["kind"],
            "snippet": snippet(row["text"]),
        }
        if info:
            item["dense_rank"] = info.get("dense")
            item["doc_rank"] = info.get("doc")
            item["lexical_rank"] = info.get("lex")
            item["graph_rank"] = info.get("graph")
        if args.explain:
            item["neighbours"] = idx.neighbours(row["path"])
            item["matched_terms"] = sorted(matched.get(cid, []))[:8]
        payload.append(item)

    # WS-1 (supersedes the RP-28 note that stood here): the walk runs on the DEFAULT path again,
    # bounded by the TTL cache and by STALE_WALK_BUDGET_SECONDS rather than by silence. The
    # verdict is tri-state and is printed on EVERY query -- a reader must never have to infer
    # from the absence of a warning that the question was asked. Checked ONCE here, ahead of the
    # json/text branch, so both output modes report the same verdict.
    freshness, why = idx.freshness(force=args.check_stale)
    stale = freshness != "FRESH"

    if args.json:
        out = {"query": args.query, "mode": mode, "hits": len(payload),
               "index": {"chunks": idx.n_chunks, "embedder": idx.meta.get("embedder")},
               "expansions": {k: v for k, v in expansions.items()} if args.explain else {},
               "results": payload}
        # Separate top-level keys, never folded into "results" -- the RP-28 selftest checks that
        # --check-stale does not change the returned results, and it would be a false PASS if
        # these silently perturbed the array it is asserting is unchanged. WS-1: `freshness` is
        # emitted UNCONDITIONALLY, because a machine consumer that only sees this key when a flag
        # was passed is in exactly the position the human reader was in before WS-1 -- unable to
        # distinguish "fresh" from "never asked".
        out["freshness"] = {"state": freshness, "message": why}
        if args.check_stale:
            out["stale"] = {"is_stale": stale, "message": why}
        print(json.dumps(out, indent=2))
        return 0

    print(f'query   : "{args.query}"')
    print(f"mode    : {mode}   index: {idx.n_chunks} chunks, {idx.meta.get('embedder')}, "
          f"freshness={freshness}")
    if freshness == "STALE":
        print(f"⚠️ STALE : {why}")
    elif freshness == "UNKNOWN":
        # A DIFFERENT token from STALE on purpose: "the index is behind the corpus" and "nobody
        # checked whether it is" call for different reactions, and collapsing them is how the
        # pre-WS-1 path read as reassuring.
        print(f"⚠️ STALE-UNKNOWN : {why}")

    # === SCOPE DISCLOSURE, added 2026-09-12 15:4x CDT, and it exists because of a measured lie ===
    # Jon, 2026-09-12, one word: "Defect?" -- after asking "did you test". Both are why this block
    # is here rather than a resolution to remember.
    #
    # [measured 2026-09-12 15:1x, direct SQL on this index] chunk text totals 272,333,183 chars
    # against 1,027,742,549 indexed file bytes = 26.5%. A provenance-tier file is stored as ONE
    # chunk holding transcript_summary() -- ~2,400 chars, heading literally "(whole transcript)" --
    # and its postings are built FROM THE SUMMARY ALONE (build_index.py:1215-1225). The body text is
    # not searchable at all. The representation is a defensible context-economy choice; printing
    # NOTHING about it is not, because a query over those bytes returns silence and a silence is
    # indistinguishable from a corpus that never held the thing. That is the one failure class this
    # program is built around: a zero that reads as a finding.
    #
    # So: every query names the scope it actually searched. UNKNOWN dominates -- if the numbers
    # cannot be read, that is printed too, never omitted.
    try:
        _t = idx.tiers
        if _t is None:
            _where, _args = "1=1", ()
        else:
            _where = "tier IN (%s)" % ",".join("?" * len(_t))
            _args = tuple(sorted(_t))
        _nf, _nb = idx.con.execute(
            "SELECT COUNT(*), COALESCE(SUM(bytes),0) FROM files WHERE " + _where, _args).fetchone()
        _nc, _ntext = idx.con.execute(
            "SELECT COUNT(*), COALESCE(SUM(LENGTH(ch.text)),0) FROM chunks ch "
            "JOIN files f ON f.id = ch.file_id WHERE " + _where.replace("tier", "f.tier"),
            _args).fetchone()
        _summ = idx.con.execute(
            "SELECT COUNT(*) FROM chunks ch JOIN files f ON f.id = ch.file_id "
            "WHERE ch.heading = '(whole transcript)' AND " + _where.replace("tier", "f.tier"),
            _args).fetchone()[0]
        _pct = (100.0 * _ntext / _nb) if _nb else None
        print("scope   : tier=%s  %d file(s), %d chunk(s)" % (
            ("ALL" if _t is None else "+".join(sorted(_t))), _nf, _nc))
        if _pct is None:
            print("          searchable text: UNKNOWN (0 bytes in scope) -- not a clean scope")
        else:
            print("          searchable text: %d of %d bytes = %.1f%% of the scope" % (
                  _ntext, _nb, _pct))
        if _summ:
            print("          ⛔ %d file(s) in scope are SUMMARY-ONLY (heading '(whole transcript)'):" % _summ)
            print("             their BODY TEXT IS NOT SEARCHABLE. A miss on those is UNKNOWN, never absence.")
        if _t is not None:
            _all = idx.con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            if _all:
                print("          this scope is %.1f%% of the index's %d chunks; --all-tiers widens it" % (
                      100.0 * _nc / _all, _all))
            # RS-7, 2026-09-12: Jon's typed prompts (~/.claude/history.jsonl, every prompt he has
            # ever typed, with a wall-clock ms timestamp) are rendered into the index but land in
            # the provenance tier, NOT the default. Naming the flag here is the difference between
            # a silent zero and a pointer -- and "no Jon primary exists" is the most expensive
            # conclusion in this repo, so a scope that cannot see his prompts must SAY so.
            _hn, _ht = idx.con.execute(
                "SELECT COUNT(*), COALESCE(GROUP_CONCAT(DISTINCT tier),'') FROM files "
                "WHERE path LIKE '%/claude-history/hist-%'").fetchone()
            if _hn:
                _in_scope = idx.con.execute(
                    "SELECT COUNT(*) FROM files WHERE path LIKE '%/claude-history/hist-%' AND " + _where,
                    _args).fetchone()[0]
                if not _in_scope:
                    print("          ⛔ JON'S %d TYPED PROMPTS ARE OUT OF THIS SCOPE (tier=%s). A zero here "
                          "is NOT absence from his record." % (_hn, _ht))
                    print("             Reach them: --tier %s   (or --all-tiers)" % (_ht.split(",")[0] or "provenance"))
    except Exception as _exc:
        print("scope   : UNKNOWN (could not be measured: %s: %s) -- UNKNOWN DOMINATES, do not read"
              % (type(_exc).__name__, _exc))
        print("          this result as a statement about the corpus.")
    if expansions and args.explain:
        for tok, cands in expansions.items():
            shown = ", ".join(f"{t}:{w}" for t, w in cands[:4]) or "(no vocabulary match)"
            print(f"  expand: {tok:<16} -> {shown}")
    if not payload:
        print("RESULTS : none")
        return 0
    print(f"RESULTS : {len(payload)}")
    for item in payload:
        signals = ""
        if any(item.get(x) for x in ("dense_rank", "doc_rank", "lexical_rank", "graph_rank")):
            signals = (f"  [chunk#{item.get('dense_rank') or '-'} "
                       f"doc#{item.get('doc_rank') or '-'} "
                       f"lex#{item.get('lexical_rank') or '-'} "
                       f"graph#{item.get('graph_rank') or '-'}]")
        # ⛔ PATH-RESOLUTION FLAG. Added 2026-09-12 20:1x as a DEAD-PATH flag; CORRECTED 22:5x
        # because the flag was telling the truth about the path and a lie about the content.
        #
        # What it said: "⛔ PATH GONE (indexed file not on disk)" on 6,261 files -- 32.6% of the
        # index. Jon then asked to discuss removing files from the graph, advice I had given him
        # several times and he had ignored every time. [measured 22:4x, chasing his question:]
        #
        #   6,261 of those rows share ONE root, N:/claude-corpus/cfl/raw -- a mirror path whose
        #   sync spec covers wiki|exchange|scripts and has never included raw/. So the directory
        #   was not deleted; it was never populated.
        #   6,148 of the 6,261 -- 98.2%, 846.1 MB -- RESOLVE TODAY under
        #   G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer/.
        #   Only 113 are genuinely unfindable.
        #
        # ⭐ SO A THIRD OF THE INDEX WAS LABELLED GONE WHILE SITTING ON DISK, and the label was the
        # evidence behind my own advice to prune it. Executing that advice would have dropped Jon's
        # claude.ai corpus -- personal, home, faith, family -- because a mirror root was empty on
        # the night the sweep ran. Nothing would have errored. It would have read as hygiene.
        #
        # ⚠️ AND THE COMMENT THIS REPLACES ALREADY KNEW: it said "the content is not necessarily lost
        # (the mirror RELOCATED, it did not delete)" and then printed PATH GONE anyway. The prose was
        # right and the string a reader actually sees was wrong, which is the only one that counts.
        #
        # ROOT_ALIASES is a fallback for RESOLUTION ONLY -- it never rewrites a citation, because the
        # citation must keep naming what was indexed. Each entry is a measured pair, and a pair whose
        # target does not exist simply never matches, so a stale alias degrades to PATH GONE rather
        # than to a false reassurance.
        ROOT_ALIASES = (
            ("N:/claude-corpus/cfl/",
             "G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer/"),
            ("N:/claude-corpus/cfl/", "N:/claude-cfl/clone/"),
        )
        _src = str(item["source"]).rsplit(":", 1)[0]
        _dead = ""
        try:
            _c = _src if os.path.isabs(_src) else os.path.join(os.getcwd(), _src)
            if not os.path.isfile(_c.replace("/", os.sep)):
                _n = _src.replace("\\", "/")
                _at = None
                for _a, _b in ROOT_ALIASES:
                    if _n.startswith(_a):
                        _cand = _b + _n[len(_a):]
                        if os.path.isfile(_cand.replace("/", os.sep)):
                            _at = _cand
                            break
                if _at:
                    _dead = f"   ⚠ ROOT MOVED -- readable at {_at}"
                else:
                    _dead = ("   ⛔ PATH GONE (not at the cited path and not under any known root "
                             "alias) -- the indexed TEXT is still below; the FILE is unverifiable")
        except Exception:
            _dead = "   ⚠ PATH UNCHECKED"
        print(f"\n{item['rank']}. {item['source']}   score={item['score']}{signals}{_dead}")
        if item["heading"]:
            print(f"   § {item['heading']}")
        print(f"   {item['snippet']}")
        if args.explain:
            if item.get("matched_terms"):
                print(f"   matched: {', '.join(item['matched_terms'])}")
            if item.get("neighbours"):
                print(f"   links -> {', '.join(item['neighbours'][:4])}")
    return 0


# ---------------------------------------------------------------- selftest (graph leg only --
# the dense/lexical/BM25 machinery is exercised by build_index.py --selftest and acceptance.py;
# this covers what CFL-D-006 / W-1 actually added: graph_expand(), _contribute()'s no-penalty
# property, and hub damping. Runs against a small SYNTHETIC db (built with build_index.py's own
# SCHEMA, so it can never drift from the real table shapes) -- no embedder load, seconds not
# minutes, and deterministic: real-corpus numbers move every rebuild, these fixtures never do.


def _build_synth_db(path):
    """A tiny fixture graph: A(seed, high sem/lex weight) -> B (one hop, low in-degree)
    A -> HUB (one hop, but HUB also has 20 other inbound edges, simulating a popular concept
    page) C (unconnected -- no edges in or out; the no-penalty control). Chunk ids double as
    file ids for simplicity (one chunk per file)."""
    import build_index as bi
    con = sqlite3.connect(path)
    con.executescript(bi.SCHEMA)
    files = ["A.md", "B.md", "HUB.md", "C.md"] + [f"filler{i}.md" for i in range(20)]
    for i, path_ in enumerate(files, start=1):
        con.execute("INSERT INTO files (id, path, sha, bytes, kind, tier) VALUES (?,?,?,?,?,?)",
                    (i, path_, "x", 10, "wiki", "knowledge"))
        con.execute(
            "INSERT INTO chunks (id, file_id, ord, heading, start_line, end_line, ntok, text) "
            "VALUES (?,?,?,?,?,?,?,?)", (i, i, 0, "", 1, 1, 10, path_))
    a, b, hub, c = 1, 2, 3, 4
    con.execute("INSERT INTO edges (src, dst, kind, raw) VALUES (?,?,?,?)", (a, b, "wikilink", "b"))
    con.execute("INSERT INTO edges (src, dst, kind, raw) VALUES (?,?,?,?)",
                (a, hub, "wikilink", "hub"))
    # 20 filler files ALSO point at HUB, so it has real in-degree 21 vs B's in-degree 1 --
    # this is the fixture-scale version of frame-before-commit.md's measured in-degree 105.
    for i in range(5, 25):
        con.execute("INSERT INTO edges (src, dst, kind, raw) VALUES (?,?,?,?)",
                    (i, hub, "wikilink", "hub"))
    for key, val in [("dims", "0"), ("n_chunks", "24"), ("avg_chunk_tokens", "10")]:
        con.execute("INSERT INTO meta (key, value) VALUES (?,?)", (key, val))
    con.commit()
    con.close()
    return {"a": a, "b": b, "hub": hub, "c": c}


def selftest(real_db_path=None) -> int:
    import tempfile
    failures = []

    def check(label, got, want):
        ok = got == want
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}: got {got!r} want {want!r}")
        if not ok:
            failures.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "synth.sqlite")
        ids = _build_synth_db(db_path)
        idx = Index(db_path)

        print("selftest: graph_expand -- one-hop rescue over EXISTING edges")
        # A is the only seed, weight 0.02 (a realistic post-fusion rrf term).
        hits = dict(idx.graph_expand({ids["a"]: 0.02}))
        check("B (low in-degree neighbour) reached", ids["b"] in hits, True)
        check("HUB (high in-degree neighbour) reached", ids["hub"] in hits, True)
        check("C (no edge to/from A) NOT reached", ids["c"] in hits, False)
        check("A itself never neighbours itself", ids["a"] in hits, False)

        print("selftest: hub damping -- popularity discounts a neighbour's vote")
        check("low in-degree neighbour outscores the hub for the SAME seed weight",
              hits[ids["b"]] > hits[ids["hub"]], True)
        # exact factor: both get w*GRAPH_DECAY before damping; B's in-degree is 1 (damp=1),
        # HUB's is 21 (damp=sqrt(21)) -- so the ratio must equal sqrt(21), not just "bigger".
        import math
        ratio = hits[ids["b"]] / hits[ids["hub"]]
        check("damping ratio matches sqrt(in-degree) exactly (within float tolerance)",
              round(ratio, 4), round(math.sqrt(21), 4))

        print("selftest: graph_expand -- no seeds means no expansion (not a crash)")
        check("empty seed_weights yields no hits", idx.graph_expand({}), [])
        check("all-zero-weight seeds yield no hits", idx.graph_expand({ids["a"]: 0.0}), [])

        print("selftest: _contribute -- NO-PENALTY property (CFL-D-006's own requirement)")
        # A chunk with real sem/lex standing and ZERO graph support must be BYTE-IDENTICAL
        # whether the graph leg ran empty or was skipped outright -- graph must only ADD.
        fused_without_graph = {}
        Index._contribute(fused_without_graph, [(ids["a"], 0.9), (ids["c"], 0.4)], "lex")
        untouched_rrf = fused_without_graph[ids["c"]]["rrf"]
        Index._contribute(fused_without_graph, [], "graph", weight=0.5)  # graph found nothing
        check("no-graph-support chunk's rrf is UNCHANGED by an empty graph contribution",
              fused_without_graph[ids["c"]]["rrf"], untouched_rrf)
        check("no-graph-support chunk's graph rank stays None (never penalized to a rank)",
              fused_without_graph[ids["c"]]["graph"], None)

        print("selftest: _contribute -- graph leg only ADDS, on a chunk that DOES get support")
        fused_with_graph = {}
        Index._contribute(fused_with_graph, [(ids["a"], 0.9)], "lex")
        before = fused_with_graph[ids["a"]]["rrf"]
        Index._contribute(fused_with_graph, [(ids["a"], 1.0)], "graph", weight=0.5)
        check("a chunk that DOES get graph support only gains score, never loses",
              fused_with_graph[ids["a"]]["rrf"] > before, True)

        print("selftest: graph_weight=0 disables the leg entirely (CLI escape hatch)")
        fused_zero = {}
        seed_weights = {ids["a"]: 0.02}
        graph_hits = idx.graph_expand(seed_weights) if 0.0 > 0.0 else []
        check("graph_weight<=0 short-circuits to no graph_expand call", graph_hits, [])

        idx.con.close()  # Windows: an open sqlite handle blocks the TemporaryDirectory cleanup

    # ---------------------------------------------------------- RP-28 checks (real index only)
    # Unlike the graph-leg checks above, these need the REAL corpus index, because they measure
    # what R-1 measured: default-path latency and the staleness walk's call count. If the index
    # named by db_path (default DEFAULT_DB) is not present, these are reported SKIPPED, not
    # silently omitted -- an omitted section and a skipped one look identical to a reader unless
    # the skip says so.
    # ------------------------------------------------- WS-1 freshness fixtures (no real corpus)
    # Both verdicts AND the degrade path, on synthetic indexes, so these fail on their OWN axis:
    # the FRESH arm is the control that keeps the STALE arm honest. Without it the new detector
    # could be permanently stuck on STALE and every assertion here would still pass -- a row
    # riding another row's failure, which this repo already has on record as a defect class.
    with tempfile.TemporaryDirectory() as tmp2:
        this_module = sys.modules[__name__]
        orig_fp = this_module.corpus_fingerprint

        def _fixture_index(stored, computed, tag):
            path = os.path.join(tmp2, "fx-%s.sqlite" % tag)
            _build_synth_db(path)
            con = sqlite3.connect(path)
            con.execute("INSERT INTO meta (key, value) VALUES (?,?)",
                        ("corpus_fingerprint", stored))
            con.execute("INSERT INTO meta (key, value) VALUES (?,?)",
                        ("built_utc", "2026-01-01T00:00:00Z"))
            con.commit()
            con.close()
            this_module.corpus_fingerprint = lambda *a, **kw: computed
            return Index(path)

        def _age_out_cache(idx_obj, walk_seconds):
            """Write the cache state a Drive-resident corpus produces: a verdict older than the
            TTL whose recorded walk blew the budget."""
            _write_stale_cache(idx_obj.db_path, False, "", walk_seconds=walk_seconds)
            cache = _read_stale_cache(idx_obj.db_path)
            cache["checked_utc"] = time.time() - (STALE_CACHE_TTL_SECONDS + 60)
            with open(_stale_cache_path(idx_obj.db_path), "w", encoding="utf-8") as fh:
                json.dump(cache, fh)

        print("selftest: WS-1 -- STALE arm (stored fingerprint differs from the corpus on disk)")
        try:
            fx = _fixture_index("AAA", "BBB", "stale")
            state_stale, msg_stale = fx.freshness()
            fx.con.close()
        finally:
            this_module.corpus_fingerprint = orig_fp
        check("changed corpus reports STALE", state_stale, "STALE")
        check("STALE message names the rebuild command", "build_index.py" in msg_stale, True)

        print("selftest: WS-1 -- FRESH control (fingerprints match; proves the arm above can be false)")
        try:
            fx = _fixture_index("AAA", "AAA", "fresh")
            state_fresh, msg_fresh = fx.freshness()
            fx.con.close()
        finally:
            this_module.corpus_fingerprint = orig_fp
        check("unchanged corpus reports FRESH", state_fresh, "FRESH")
        check("FRESH carries no warning text", msg_fresh, "")

        print("selftest: WS-1 -- UNKNOWN arm (a walk over budget degrades LOUDLY, never to FRESH)")
        try:
            fx = _fixture_index("AAA", "AAA", "unknown")
            _age_out_cache(fx, STALE_WALK_BUDGET_SECONDS + 60.0)
            state_unk, msg_unk = fx.freshness(force=False)
            state_forced, _ = fx.freshness(force=True)
            fx.con.close()
        finally:
            this_module.corpus_fingerprint = orig_fp
        check("an unaffordable walk reports UNKNOWN, not FRESH", state_unk, "UNKNOWN")
        check("UNKNOWN says the results are unbounded and names the override",
              ("UNBOUNDED" in msg_unk and "--check-stale" in msg_unk), True)
        check("--check-stale (force) overrides the budget and returns a real verdict",
              state_forced, "FRESH")

        print("selftest: WS-2 -- a rebuild invalidates the cached verdict (the remedy clears the alarm)")
        try:
            fx = _fixture_index("AAA", "BBB", "rebuilt")   # corpus differs from stored -> truly STALE
            # A fresh cache from BEFORE the rebuild, claiming FRESH, bound to the old build stamp.
            _write_stale_cache(fx.db_path, False, "", walk_seconds=0.01,
                               index_built_utc="2026-01-01T00:00:00Z")
            state_before, _ = fx.freshness()               # cache is valid and current -> served
            con = sqlite3.connect(fx.db_path)              # now the operator runs build_index.py
            con.execute("UPDATE meta SET value=? WHERE key='built_utc'", ("2026-01-02T00:00:00Z",))
            con.commit(); con.close()
            fx2 = Index(fx.db_path)
            state_after, _ = fx2.freshness()
            fx.con.close(); fx2.con.close()
        finally:
            this_module.corpus_fingerprint = orig_fp
        check("before the rebuild the cached verdict is served (control: the cache does work)",
              state_before, "FRESH")
        check("after the rebuild the stale VERDICT is discarded and the corpus re-checked",
              state_after, "STALE")

        print("selftest: WS-1 -- the back-compat shim collapses UNKNOWN toward caution")
        try:
            fx = _fixture_index("AAA", "AAA", "shim")
            _age_out_cache(fx, STALE_WALK_BUDGET_SECONDS + 60.0)
            shim_stale, _ = fx.staleness(check=False)
            fx.con.close()
        finally:
            this_module.corpus_fingerprint = orig_fp
        check("staleness() reports True (not RP-28's False) when freshness is UNKNOWN",
              shim_stale, True)

    real_db = real_db_path or DEFAULT_DB
    if not os.path.isfile(real_db):
        print(f"\nselftest: RP-28 checks SKIPPED -- index not found at {real_db!r}")
    else:
        import subprocess
        print(f"\nselftest: RP-28 checks against real index {real_db!r}")
        fixed_query = "how do we stop believing our own first numbers"

        # WS-1 REPLACES the two assertions that stood here. They read:
        #     "default staleness(check=False) triggers 0 corpus_fingerprint() walks" -> 0
        #     "default staleness(check=False) always reports not-stale (advisory skipped, not
        #      guessed)" -> (False, "")
        # Both passed, forever, and together they PINNED the defect: the label already knew the
        # difference between "skipped" and "guessed", and the assertion enforced the one value
        # that makes them indistinguishable to every caller. A guard that certifies the thing it
        # is named after is worse than no guard, because it answers the question.
        print("selftest: WS-1 -- the default path returns a REAL tri-state verdict, not a silent False")
        probe_idx = Index(real_db)
        probe_idx.tiers = {"knowledge"}
        default_state, default_why = probe_idx.freshness(force=False)
        probe_idx.con.close()
        check("default freshness() returns one of the three legal states",
              default_state in ("FRESH", "STALE", "UNKNOWN"), True)
        check("default freshness() never returns RP-28's empty non-answer",
              (default_state, default_why) == (False, ""), False)
        check("a non-FRESH verdict always carries a message a reader can act on",
              (default_state == "FRESH") or bool(default_why.strip()), True)

        print("selftest: RP-28 -- cold run of a fixed probe completes under 15s")
        cmd_a = [sys.executable, os.path.abspath(__file__), fixed_query,
                 "--db", real_db, "--tier", "knowledge", "-k", "3", "--json"]
        t0 = time.time()
        proc_a = subprocess.run(cmd_a, capture_output=True, text=True, timeout=60)
        elapsed = time.time() - t0
        check("cold probe subprocess exits 0", proc_a.returncode, 0)
        check(f"cold probe wall time under 15s (measured {elapsed:.2f}s)", elapsed < 15.0, True)

        print("selftest: RP-28 -- results identical with and without --check-stale")
        cmd_b = cmd_a + ["--check-stale"]
        proc_b = subprocess.run(cmd_b, capture_output=True, text=True, timeout=180)
        try:
            results_a = json.loads(proc_a.stdout).get("results")
            results_b = json.loads(proc_b.stdout).get("results")
            parsed_ok = True
        except (ValueError, AttributeError):
            results_a = results_b = None
            parsed_ok = False
        check("both runs' stdout parsed as JSON", parsed_ok, True)
        check("--check-stale does not change the returned results array",
              results_a == results_b, True)

    print(f"\nselftest: {'ALL PASS' if not failures else str(len(failures)) + ' FAILED'}")
    return 0 if not failures else 5


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", default=None)
    ap.add_argument("-k", type=int, default=8)
    ap.add_argument("--mode", default="hybrid",
                    choices=["hybrid", "dense", "doc", "lexical", "grep", "graph"])
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--scope", default=None, help="restrict to a kind prefix, e.g. wiki:concepts")
    ap.add_argument("--graph-weight", type=float, default=DEFAULT_GRAPH_WEIGHT,
                    help=f"weight of the one-hop graph RRF leg relative to sem/lex "
                         f"(default {DEFAULT_GRAPH_WEIGHT}; 0 disables it)")
    ap.add_argument("--tier", default=None,
                    help="tiers to search, comma/space separated: knowledge (default), queue, "
                         "provenance (raw/transcripts -- the actual conversations), or 'all'")
    ap.add_argument("--all-tiers", action="store_true",
                    help="search EVERY tier: the intake-triage queue and the raw/ transcript "
                         "provenance tier as well as knowledge (both off by default)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--explain", action="store_true", help="show term expansions and graph links")
    ap.add_argument("--check-stale", action="store_true", dest="check_stale",
                    help="RP-28: run the full-corpus staleness walk (os.stat over every corpus "
                         "file, ~85-126s measured cold). OFF by default -- a default query never "
                         "pays this cost. Even with this flag, a TTL-cached result beside the "
                         "index (see README) is reused if checked within the last 6h.")
    ap.add_argument("--selftest", action="store_true",
                    help="run the graph-leg selftest, plus (if the real index is present) the "
                         "RP-28 latency/staleness/tier-load checks, and exit")
    args = ap.parse_args()
    if args.selftest:
        return selftest(args.db)
    if not args.query:
        ap.error("query is required unless --selftest is given")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
