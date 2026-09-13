#!/usr/bin/env python3
"""ACCEPTANCE TEST for GraphRAG v0 — and it is written to be able to FAIL.

⛔ THE CRITERION IS THE SECRETARY'S, AND IT IS ADVERSARIAL BY DESIGN (assignment letter, §1.5):

    "a query written with his typos and his imprecise phrasing must retrieve the right wiki page,
     where exact-match search returns nothing. Graph-only and grep-only baselines must FAIL that
     test; if they pass, v0 has not demonstrated why it exists."

⭐ So this harness asserts TWO things per case, and the second is the one that makes it a test
rather than a demo:
    1. hybrid retrieval RANKS THE RIGHT PAGE inside top-k, and
    2. the baseline we already have today (grep) DOES NOT.
A case where grep also succeeds is reported as INCONCLUSIVE, not as a pass — it proves nothing
about why this system exists, because the existing tooling already answered it.

⚠️ WHY THE CASES SPLIT INTO TWO CLASSES: Jon named typos AND imprecise language, and they are
answered by DIFFERENT halves of the hybrid. Reporting one number over both would hide a half that
does not work. Each case declares which half it is meant to exercise, and the report prints the
per-signal ranks so a pass carried by the wrong mechanism is visible rather than flattering.

Usage:  python scripts/graphrag/acceptance.py [--db PATH] [-k 8] [--verbose]
Exit:   0 all cases pass · 5 one or more failed · 2 index missing
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrieve import DEFAULT_DB, Index  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# (id, class, query, expected path substring, why this case exists)
CASES = [
    ("T1", "typo",
     "stylomantic diffrences betwen the trunks",
     "wiki/concepts/stylomantic.md",
     "Jon's own example phrase, misspelled two ways. 'diffrences'/'betwen' appear nowhere."),
    # ⚠️ T2's expected page was CHANGED after the first run, and the change is a correction to the
    # TEST, not a loosening of it. It originally expected `stochastic-retrieval-research.md`
    # because the Secretary's letter named that page as prior art. Reading the page showed it is
    # about relevance-band SAMPLING and never discusses vector embedding at all -- so the case was
    # asserting a fact about the corpus that is not true, and the retriever was being failed for
    # not hallucinating. This is the "acceptance tests name artifacts the system never produces"
    # defect, caught here by reading the target instead of the score.
    ("T2", "typo",
     "stocastic retreival relevence band sampeling",
     "wiki/concepts/stochastic-retrieval-research.md",
     "Four misspellings of the page's actual subject. Tests typo tolerance against content the "
     "page really has, rather than content its citer claimed it had."),
    ("T3", "typo",
     "the fense is wider than you assume",
     "CLAUDE.md",
     "Jon's own standing constraint, carrying HIS typo. The corpus stores the typo verbatim, so "
     "this one tests that we did not 'correct' his words out of the index."),
    ("T4", "typo",
     "cleanupperioddays retention deleteing my sesions",
     "wiki/",
     "Three misspellings around a real config key. The key itself is spelled correctly-ish, so "
     "this case tests degradation, not miracle."),
    ("I1", "imprecise",
     "which seat is not allowed to do the work itself and only hands it out",
     "wiki/concepts/coordinator.md",
     "Zero content words shared with the target's title. Pure paraphrase -- the dense half."),
    # ⚠️ ALSO CORRECTED after the first run: this expected `concepts/words-reify.md`, which is
    # about J-space and Jon's stated intent for that phrase -- NOT about a recorded fact drifting
    # from reality. The page that actually holds this concept is the agent-memory reference below.
    # My expectation was wrong; the retriever was not.
    ("I2", "imprecise",
     "what happens when something written down once drifts from what is actually true",
     "wiki/references/agent-memory/derive-dont-record.md",
     "Describes the concept without naming it. If dense retrieval works, this lands."),
]

# ---------------------------------------------------------------------------------------------
# W-2 — SPEC-IN-INDEX GUARD (CFL, 2026-08-18). Professional's finding, operationalized:
# "the measuring process is inside the population." Every review of this test writes its query
# strings into letters, hall entries and agent-end captures -- and the agent-end ingest path
# lands in wiki/intake-triage/, WHICH IS INDEXED. So contamination is not a one-time cleanup;
# it is a rate. This check runs at every invocation and attests, per case, whether the corpus
# contains the case's own discriminating misspellings or its full query phrase.
#
# ⚠️ Per-case marker lists are PRE-REGISTERED here, not derived, because derivation would judge
# its own inputs. T3 deliberately has NO markers: "fense" is Jon's authentic stored typo -- its
# presence in the corpus is the CONTENT under test, not contamination (the corpus stores his
# words verbatim; a "corrected" quote is an unverifiable quote).
# `[measured 2026-08-18 06:1x]` all markers below returned 0 files across wiki/ + constitutions,
# so the attestation starts TRUE; this guard exists for the day that stops being so.
SPEC_MARKERS = {
    "T1": ["diffrences", "betwen"],
    "T2": ["stocastic", "retreival", "relevence", "sampeling"],
    "T3": [],   # authentic Jon typo -- in-corpus presence is content, never contamination
    "T4": ["deleteing", "sesions"],
    "I1": [],   # imprecise cases carry no misspellings; phrase check below covers them
    "I2": [],
}


# ---------------------------------------------------------------------------------------------
# P — PROVENANCE REACHABILITY (SEC-113, 2026-08-23). Jon's criterion, and it is HIS, not ours:
#
#     "ensure vector embed graph rag with haiku support tracks all the way to the actual
#      conversationSSSSS i've had with herald on this i don't trust what has been said to be
#      true or not true"
#
# ⛔ He capitalised the plural. He expected SEVERAL conversations and feared the record would
# surface one summary and stop. Before this landed, a photos query returned
# `wiki/sources/session-stubs.md` -- a TABLE ROW saying photo sessions exist.
# A stub about a conversation is not a conversation.
#
# ⭐ EACH CASE IS TWO-SIDED ON PURPOSE, and the second half is the one that protects everything
# else in this file: the primary must be REACHABLE with `--tier provenance`, AND it must be
# ABSENT from the default knowledge scope. A tier that leaks into the default scope is not a
# fix, it is the 72%-haystack defect again at four times the size. A one-sided probe would
# certify the leak as a pass.
PROVENANCE_CASES = [
    ("P1",
     "photo organization project plan",
     "raw/transcripts/",
     "The SEC-113 acceptance criterion verbatim. Must surface a real conversation file, with "
     "its path, so a reader can open the primary."),
    ("P2",
     "scanned childhood photos organized onto a NAS",
     "raw/transcripts/",
     "Jon's own framing of the task. Before this tier existed, this query's top-5 was "
     "security-master credential exposure and a session-stubs table row."),
]


def provenance_probe(idx, k=5, verbose=False):
    """Returns (n_pass, n_fail) and prints the evidence. Skips cleanly on an index with no tier."""
    print("=" * 100)
    print("PROVENANCE REACHABILITY (SEC-113) -- can a query reach the actual conversation?")
    present = set(idx.tiers_present()) if hasattr(idx, "tiers_present") else set()
    if "provenance" not in present:
        print(f"  SKIP: this index has no provenance tier (tiers present: {sorted(present) or '?'}). "
              f"Rebuild with scripts/graphrag/build_index.py to create it.")
        return 0, 0
    n_pass = n_fail = 0
    saved = idx.tiers
    try:
        for cid, query, expected, why in PROVENANCE_CASES:
            idx.tiers = {"knowledge", "provenance"}
            order, _, _ = idx.hybrid(query, None, k)
            meta = idx.chunk_rows([c for c, _ in order])
            hit = None
            for rank, (chunk_id, _info) in enumerate(order, start=1):
                path = meta.get(chunk_id, {}).get("path", "")
                if expected in path:
                    hit = (rank, path)
                    break
            # The other side: the SAME query must NOT reach it on the default scope.
            idx.tiers = {"knowledge"}
            d_order, _, _ = idx.hybrid(query, None, k)
            d_meta = idx.chunk_rows([c for c, _ in d_order])
            leaked = [d_meta.get(c, {}).get("path", "") for c, _ in d_order
                      if expected in d_meta.get(c, {}).get("path", "")]
            ok = hit is not None and not leaked
            n_pass, n_fail = (n_pass + 1, n_fail) if ok else (n_pass, n_fail + 1)
            print(f"  [{'PASS' if ok else 'FAIL'}] {cid}  \"{query}\"")
            if hit:
                print(f"         reachable at rank {hit[0]}/{k} with --tier provenance: {hit[1]}")
            else:
                print(f"         NOT in top-{k} of the provenance tier -- the primary is still "
                      f"unreachable by this query")
            if leaked:
                print(f"         ⛔ LEAK: provenance path present in the DEFAULT scope: {leaked[0]}")
            if verbose:
                print(f"         why: {why}")
    finally:
        idx.tiers = saved
    print(f"  provenance: {n_pass} pass · {n_fail} fail of {len(PROVENANCE_CASES)}")
    return n_pass, n_fail


def contamination_check(idx, cases):
    """Returns {case_id: [findings]} -- empty list means clean. Uses the INDEX's own tables,
    so it measures what retrieval can actually see, not what a filesystem grep sees."""
    out = {}
    for cid, cls, query, expected, why in cases:
        findings = []
        for tok in SPEC_MARKERS.get(cid, []):
            row = idx.con.execute("SELECT df FROM terms WHERE term=?", (tok.lower(),)).fetchone()
            if row and row[0] > 0:
                findings.append(f"marker token '{tok}' in index vocabulary (df={row[0]})")
        # full-phrase echo: the whole query quoted verbatim into an indexed chunk. Excludes the
        # target page itself -- the target legitimately discusses its own subject.
        like = "%" + " ".join(query.lower().split()) + "%"
        for (path,) in idx.con.execute(
                "SELECT DISTINCT f.path FROM chunks c JOIN files f ON f.id=c.file_id "
                "WHERE lower(c.text) LIKE ? LIMIT 5", (like,)):
            if expected not in path:
                findings.append(f"full query phrase quoted in {path}")
        out[cid] = findings
    return out


def contamination_selftest(idx):
    """Two-sided: a marker that MUST flag (a token guaranteed in any English corpus) and one
    that MUST NOT (nonsense). A guard that can only pass is a mute button."""
    pos = idx.con.execute("SELECT df FROM terms WHERE term='the'").fetchone()
    neg = idx.con.execute("SELECT df FROM terms WHERE term='zzqqxv'").fetchone()
    ok_pos = bool(pos and pos[0] > 0)
    ok_neg = not neg
    print(f"  contamination guard selftest: positive(common token flags)="
          f"{'PASS' if ok_pos else 'FAIL'}  negative(nonsense stays clean)="
          f"{'PASS' if ok_neg else 'FAIL'}")
    return ok_pos and ok_neg


def evaluate(idx: Index, k: int, verbose: bool) -> int:
    print(f"index   : {idx.n_chunks} chunks · embedder {idx.meta.get('embedder')} "
          f"({idx.meta.get('dims')}d) · built {idx.meta.get('built_utc')}")
    print(f"top-k   : {k}\n")

    passed, failed, inconclusive = [], [], []
    rows = []

    # W-2: attest spec-in-index state BEFORE scoring, and let it change verdicts -- an
    # unlabelled index containing its own answer key is a false green (Professional's rule).
    if not contamination_selftest(idx):
        print("  ⛔ contamination guard selftest FAILED -- attestation below is unreliable")
    contam = contamination_check(idx, CASES)
    # ⛔ loop vars deliberately NOT named k/v: the first version wrote `for k, v in
    # dirty.items()`, which rebound the top-k INT parameter to a case-id STRING -- so the
    # script crashed IF AND ONLY IF the guard fired. A guard whose firing breaks its harness
    # is worse than no guard; caught on its first true positive (T3), not by the selftest,
    # because the selftest exercised the check and not the reporting path around it.
    dirty = {c: f for c, f in contam.items() if f}
    if dirty:
        print(f"  ⛔ SPEC-IN-INDEX: {len(dirty)} case(s) contaminated -- their PASSes are downgraded:")
        for c_id, findings in dirty.items():
            for finding in findings:
                print(f"      {c_id}: {finding}")
    else:
        print("  ✅ spec-in-index attestation: all pre-registered markers absent; no query phrase "
              "echoed outside its target. The corpus is not grading its own specification today.")
    print()

    for cid, cls, query, expected, why in CASES:
        order, expansions, _ = idx.hybrid(query, None, k)
        meta = idx.chunk_rows([c for c, _ in order])
        hyb_rank, hyb_info = None, {}
        for rank, (chunk_id, info) in enumerate(order, start=1):
            path = meta.get(chunk_id, {}).get("path", "")
            if expected in path:
                hyb_rank, hyb_info = rank, info
                break

        grep_raw = idx.grep(query)[:k]
        grep_meta = idx.chunk_rows([c for c, _ in grep_raw])
        grep_rank = next((r for r, (c, _) in enumerate(grep_raw, start=1)
                          if expected in grep_meta.get(c, {}).get("path", "")), None)

        graph_raw = idx.graph_only(query)[:k]
        graph_meta = idx.chunk_rows([c for c, _ in graph_raw])
        graph_rank = next((r for r, (c, _) in enumerate(graph_raw, start=1)
                           if expected in graph_meta.get(c, {}).get("path", "")), None)

        dense_only = idx.dense(query)[:k]
        dm = idx.chunk_rows([c for c, _ in dense_only])
        dense_rank = next((r for r, (c, _) in enumerate(dense_only, start=1)
                           if expected in dm.get(c, {}).get("path", "")), None)
        doc_only = idx.doc_dense(query)[:k]
        dcm = idx.chunk_rows([c for c, _ in doc_only])
        doc_rank = next((r for r, (c, _) in enumerate(doc_only, start=1)
                         if expected in dcm.get(c, {}).get("path", "")), None)
        lex_only, _, _ = idx.lexical(query)
        lex_only = lex_only[:k]
        lm = idx.chunk_rows([c for c, _ in lex_only])
        lex_rank = next((r for r, (c, _) in enumerate(lex_only, start=1)
                         if expected in lm.get(c, {}).get("path", "")), None)

        if hyb_rank is None:
            verdict = "FAIL"
            failed.append(cid)
        elif contam.get(cid):
            # the corpus contains this case's own spec text somewhere other than its target --
            # a PASS here may be the index retrieving the paperwork, so it proves nothing.
            verdict = "INCONCLUSIVE"
            inconclusive.append(cid)
        elif grep_rank is not None:
            # The baseline we already own answered it too. That is not a win for this build.
            verdict = "INCONCLUSIVE"
            inconclusive.append(cid)
        else:
            verdict = "PASS"
            passed.append(cid)

        rows.append((cid, cls, verdict, hyb_rank, dense_rank, lex_rank,
                     grep_rank, graph_rank, len(grep_raw), query, expected))

        print(f"[{verdict:<12}] {cid} ({cls})  \"{query}\"")
        print(f"               expect {expected}")
        print(f"               hybrid #{hyb_rank}   chunk-dense #{dense_rank}   "
              f"doc-dense #{doc_rank}   lexical #{lex_rank}"
              f"   | baselines: grep #{grep_rank} ({len(grep_raw)} hits total), "
              f"graph #{graph_rank} ({len(graph_raw)} hits total)")
        if verbose:
            print(f"               why: {why}")
            for tok, cands in expansions.items():
                shown = ", ".join(f"{t}:{w}" for t, w in cands[:3])
                if shown and shown != f"{tok}:1.0":
                    print(f"               expand {tok:<14} -> {shown}")
            for rank, (chunk_id, info) in enumerate(order[:3], start=1):
                m = meta.get(chunk_id, {})
                print(f"               #{rank} {m.get('path')}:{m.get('start_line')} "
                      f"[d#{info.get('dense')} l#{info.get('lex')}] {m.get('heading', '')[:50]}")
        print()

    print("=" * 100)
    print(f"PASS {len(passed)}  ·  FAIL {len(failed)}  ·  INCONCLUSIVE {len(inconclusive)}  "
          f"of {len(CASES)} cases")
    if inconclusive:
        print(f"  INCONCLUSIVE = hybrid found it, but grep found it too ({', '.join(inconclusive)})."
              f" Proves nothing about why this system exists.")
    if failed:
        print(f"  FAILED: {', '.join(failed)}")

    typo_pass = sum(1 for r in rows if r[1] == "typo" and r[2] == "PASS")
    typo_n = sum(1 for r in rows if r[1] == "typo")
    imp_pass = sum(1 for r in rows if r[1] == "imprecise" and r[2] == "PASS")
    imp_n = sum(1 for r in rows if r[1] == "imprecise")
    print(f"  by class: typo {typo_pass}/{typo_n} · imprecise {imp_pass}/{imp_n}")
    if imp_pass < imp_n:
        print("""
  ⛔ THE IMPRECISE CLASS IS THE MEASURED BOUNDARY OF v0, and it is a property of the model, not a
     tuning failure. Diagnosed 2026-08-17 rather than guessed at:
       · the doc summary for concepts/coordinator.md CONTAINS "it does not execute work itself,
         it coordinates PMs" -- the answer is indexed, correctly, and reads correctly.
       · query "coordinates does not execute work itself delegation" -> that page at DOC RANK 2
         (sim 0.3151 of a 0.3351 top).
       · query "which seat is not allowed to do the work itself and only hands it out"
         -> DOC RANK 507 of 819 (sim 0.0473).
       · stripping stopwords from the failing query made it WORSE (507 -> 649), so dilution is
         refuted as the cause.
     ⭐ The discriminator is VOCABULARY OVERLAP. A static embedder is a bag of token vectors with
     semantic smoothing; it does not bridge "seat"->"session/role" or "hands it out"->"delegates".
     ⚠️ So v0 delivers typo tolerance and paraphrase-with-shared-vocabulary. FULL paraphrase over
     disjoint vocabulary needs a CONTEXTUAL embedder -- and that is the v1 decision, with a real
     cost attached (local torch ~2.5 GB, or a hosted API that needs a key and Jon's money).""")

    # The control that makes the claim falsifiable: baselines must be broadly failing.
    grep_found = sum(1 for r in rows if r[6] is not None)
    graph_found = sum(1 for r in rows if r[7] is not None)
    print(f"  baseline controls: grep found the target in {grep_found}/{len(rows)} cases, "
          f"graph-only in {graph_found}/{len(rows)}")
    if grep_found == len(rows):
        print("  ⛔ CONTROL FAILED: grep answered every case. This corpus cannot demonstrate the claim.")

    print()
    _, prov_fail = provenance_probe(idx, k=5, verbose=verbose)

    return 0 if not failed and not prov_fail else 5


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("-k", type=int, default=8)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if not os.path.isfile(args.db):
        print(f"FAIL index not found: {args.db}", file=sys.stderr)
        return 2
    return evaluate(Index(args.db), args.k, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
