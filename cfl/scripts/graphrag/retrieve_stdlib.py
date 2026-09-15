#!/usr/bin/env python3
"""Lexical retrieval over the index using NOTHING but the Python standard library.

WHY THIS EXISTS -- and it is a narrower claim than "the residents can query now"
-------------------------------------------------------------------------------
CFL mounted the derived index into the resident (fbf522e) and wrote "the residents can query now."
**Soul (Claude Personal, a1d6b7c8) exercised the bind against `cfl-resident:v8` and that sentence
was half true.** Measured INSIDE the image:

    retrieve.py   ABSENT   (`find / -name retrieve.py` -> nothing; /tools holds only entrypoint.sh)
    numpy         ABSENT
    tokenizers    ABSENT
    potion weights ABSENT
    python3 3.11.2 + sqlite3  PRESENT
    postings      1,357,281 rows, readable

⛔ **13,197 vectors are sitting in the mount and nothing in the image can embed a query to compare
against them.** Soul's own words: "I specified a door and never specified a key."

⚠️ AND THE VECTOR HALF CANNOT BE FIXED BY MOUNTING THE HOST'S PACKAGES. The image runs Python
**3.11.2**; this host runs 3.14. numpy and tokenizers ship compiled extension modules built against
a specific ABI, so a bind of the host `site-packages` would fail at import. **Vector retrieval needs
an image rebuild. That is a bake, not a bind, and it is not a tonight change.**

⭐ SO THIS FILE TAKES THE HALF THAT NEEDS NO NEW DEPENDENCY AND NO REBUILD. Everything BM25 needs is
already in the mounted database in plain tables: `terms(term, df)`, `postings(term, chunk_id, tf)`,
`chunks(text, heading, start_line, end_line)`, `files(path)`. Plus `vocab_tri(tri, term)`, which is
how typo tolerance is obtained WITHOUT embeddings -- the measured finding from GraphRAG v0 was that
typos are fixed by trigram query expansion and NOT by the embedder.

WHAT THIS IS NOT, stated plainly so the resident is never misled about its own instrument
------------------------------------------------------------------------------------------
- ⛔ **NOT vector retrieval.** No embedding of any kind happens here. A query that shares no
  vocabulary with the target text will NOT find it -- and that failure is silent, because an empty
  result set looks identical to a corpus that holds nothing.
- ⛔ **NOT reranked.** Jon has asked for "vector embed graph rag with haiku support" in four trunks
  in one day. The judgment half does not exist anywhere yet. **BM25 orders by term statistics; it
  does not judge relevance.**
- ⚠️ **NOT the same instrument as `retrieve.py`.** Do not compare their outputs and conclude
  anything about either.

`--capabilities` prints exactly this, machine-readable, so the resident can ask what it holds rather
than infer it from a name.
"""
import argparse
import json
import math
import os
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_DB = "/index/index.sqlite"      # the container path; override with --db off-container
TOKEN = re.compile(r"[a-z0-9][a-z0-9_\-]*")
K1, B = 1.5, 0.75                        # standard BM25; not tuned, and saying so is the point


def tokenize(s):
    return TOKEN.findall(s.lower())


def trigrams(w):
    w = "$" + w + "$"
    return {w[i:i + 3] for i in range(len(w) - 2)}


def expand(conn, term, limit=4):
    """Trigram-neighbour expansion -- the MEASURED cure for typos in this program.

    GraphRAG v0's own finding: typos are fixed by trigram query expansion, NOT by embeddings
    (static embeddings need vocabulary overlap). So this works on the half a missing numpy took
    away, which is why it is here rather than deferred with the vector work.
    """
    if not term or len(term) < 4:
        return []
    tris = trigrams(term)
    if not tris:
        return []
    q = ",".join("?" * len(tris))
    rows = conn.execute(
        "select term, count(*) c from vocab_tri where tri in (%s) group by term "
        "order by c desc limit 40" % q, tuple(tris)).fetchall()
    out = []
    for cand, shared in rows:
        if cand == term:
            continue
        # Jaccard on trigram sets: cheap, stdlib, and explainable to a reader.
        ct = trigrams(cand)
        j = shared / float(len(tris | ct)) if (tris | ct) else 0.0
        if j >= 0.5:
            out.append((cand, j))
    out.sort(key=lambda x: -x[1])
    return [c for c, _ in out[:limit]]


def search(conn, query, k=8, use_expansion=True):
    qterms = tokenize(query)
    if not qterms:
        return [], []
    ndocs = conn.execute("select count(*) from chunks").fetchone()[0]
    avgdl = conn.execute("select avg(ntok) from chunks").fetchone()[0] or 1.0

    used, expansions = [], []
    for t in qterms:
        row = conn.execute("select df from terms where term=?", (t,)).fetchone()
        if row:
            used.append((t, row[0], 1.0))
        elif use_expansion:
            for alt in expand(conn, t):
                r2 = conn.execute("select df from terms where term=?", (alt,)).fetchone()
                if r2:
                    # Down-weighted ON PURPOSE: an expanded term is a GUESS about what was meant.
                    used.append((alt, r2[0], 0.6))
                    expansions.append((t, alt))
    if not used:
        return [], expansions

    scores = {}
    for term, df, w in used:
        idf = math.log(1.0 + (ndocs - df + 0.5) / (df + 0.5))
        for cid, tf in conn.execute(
                "select chunk_id, tf from postings where term=?", (term,)):
            dl = conn.execute("select ntok from chunks where id=?", (cid,)).fetchone()
            dl = (dl[0] if dl and dl[0] else avgdl)
            denom = tf + K1 * (1 - B + B * dl / avgdl)
            scores[cid] = scores.get(cid, 0.0) + w * idf * (tf * (K1 + 1)) / denom

    top = sorted(scores.items(), key=lambda x: -x[1])[:k]
    out = []
    for cid, sc in top:
        r = conn.execute(
            "select f.path, c.heading, c.start_line, c.end_line, c.text "
            "from chunks c join files f on f.id=c.file_id where c.id=?", (cid,)).fetchone()
        if r:
            out.append({"path": r[0], "heading": r[1], "start_line": r[2],
                        "end_line": r[3], "score": round(sc, 4),
                        "text": (r[4] or "")[:400]})
    return out, expansions


CAPABILITIES = {
    "tool": "retrieve_stdlib.py",
    "requires": ["python3 stdlib only (sqlite3, math, re)"],
    "provides": {
        "lexical_bm25": True,
        "typo_tolerance_via_trigrams": True,
        "vector_similarity": False,
        "graph_expansion": False,
        "reranking": False,
    },
    "cannot": [
        "find text that shares NO vocabulary with the query -- and it fails SILENTLY, "
        "because an empty result set looks identical to a corpus that holds nothing",
        "judge relevance; BM25 orders by term statistics only",
        "read anything excluded by the deny filter applied when this index was derived",
    ],
    "why_no_vectors": (
        "13,197 vectors are present in this database and unusable here: numpy, tokenizers and the "
        "potion weights are absent from the image, and the host's copies cannot be mounted because "
        "the image runs Python 3.11 against a host on 3.14 (compiled ABI mismatch). Vector "
        "retrieval requires an image REBUILD, not a bind."
    ),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="*")
    ap.add_argument("--db", default=os.environ.get("CFL_INDEX", DEFAULT_DB))
    ap.add_argument("-k", type=int, default=8)
    ap.add_argument("--no-expand", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--capabilities", action="store_true",
                    help="print what this tool can and CANNOT do, machine-readable")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.capabilities:
        print(json.dumps(CAPABILITIES, indent=2))
        return 0
    if not os.path.exists(a.db):
        # UNKNOWN dominates a PASS: an absent index is not an empty corpus.
        print("FATAL: no index at %s -- this is UNREADABLE, not EMPTY." % a.db, file=sys.stderr)
        return 3
    conn = sqlite3.connect("file:%s?mode=ro" % a.db.replace("\\", "/"), uri=True)

    if a.selftest:
        return selftest(conn, a.db)
    if not a.query:
        ap.error("need a query (or --capabilities)")

    hits, exps = search(conn, " ".join(a.query), k=a.k, use_expansion=not a.no_expand)
    if a.json:
        print(json.dumps({"hits": hits, "expansions": exps}, indent=2, ensure_ascii=False))
        return 0
    for t, alt in exps:
        print("  expanded %r -> %r (trigram neighbour, down-weighted)" % (t, alt))
    if not hits:
        print("0 results. NOTE: this tool is LEXICAL -- zero hits can mean the corpus lacks the "
              "words, not the subject. Rephrase using words the documents would use.")
        return 0
    for i, h in enumerate(hits, 1):
        print("%2d. %s:%s-%s  score=%s" % (i, h["path"], h["start_line"], h["end_line"], h["score"]))
        if h["heading"]:
            print("    S %s" % h["heading"])
        print("    %s" % " ".join(h["text"].split())[:180])
    return 0


def selftest(conn, db):
    ok = True
    print("--- case 1: a term that EXISTS returns hits ---")
    hits, _ = search(conn, "supersession amendment", k=3)
    print("    %d hits  %s" % (len(hits), "PASS" if hits else "FAIL"))
    ok = ok and bool(hits)

    print("--- case 2: NEGATIVE CONTROL -- nonsense returns ZERO, not a crash ---")
    hits2, _ = search(conn, "zzqxwvfjkl", k=3)
    print("    %d hits (expect 0)  %s" % (len(hits2), "PASS" if not hits2 else "FAIL"))
    ok = ok and not hits2

    print("--- case 3: a TYPO is recovered by trigram expansion, not by embeddings ---")
    hits3, exps = search(conn, "supersesion", k=3)
    print("    expansions: %r" % (exps,))
    print("    %d hits  %s" % (len(hits3), "PASS" if hits3 else "FAIL -- expansion did not fire"))
    ok = ok and bool(hits3)

    print("--- case 4: the DENY filter holds in the file this tool actually reads ---")
    bad = 0
    for d in ("wiki/personal", "wiki/home", "wiki/pro", "wiki/intake-triage", "exchange/su-close"):
        bad += conn.execute("select count(*) from files where path like ?",
                            (d + "%",)).fetchone()[0]
    print("    denied rows: %d (expect 0)  %s" % (bad, "PASS" if not bad else "FAIL"))
    ok = ok and not bad

    print("--- case 5: meta agrees with the TABLES, not with the source it was copied from ---")
    m = dict(conn.execute("select key, value from meta"))
    real_f = conn.execute("select count(*) from files").fetchone()[0]
    real_c = conn.execute("select count(*) from chunks").fetchone()[0]
    agree = (str(real_f) == str(m.get("n_files")) and str(real_c) == str(m.get("n_chunks")))
    print("    meta n_files=%s n_chunks=%s vs actual %d/%d  %s"
          % (m.get("n_files"), m.get("n_chunks"), real_f, real_c,
             "PASS" if agree else "FAIL -- STALE META: a derived copy that reports its "
                                  "SOURCE's counts tells the resident it holds more than it does"))
    ok = ok and agree

    print("\n" + ("SELFTEST PASS" if ok else "SELFTEST FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
