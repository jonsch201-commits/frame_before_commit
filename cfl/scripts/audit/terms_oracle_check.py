#!/usr/bin/env python3
"""terms_oracle_check.py -- is the `terms` table exactly what a full GROUP BY over `postings` would say?

THE GATE THIS FILE IS. `build_index.py` stopped rebuilding the whole term table on every run on
2026-09-12; it now recomputes df only for the AFFECTED TERM SET (terms in chunks added or deleted that
run). `[measured 2026-09-12]` that took the term phase from **106.7s to 62.0s** and a whole incremental
build from **219.3s to 95.6s**.

⛔ THE PREDECESSOR'S OBJECTION IS THE REASON THIS SCRIPT EXISTS, and it is written in the builder:
*"rebuild them wholesale -- cheap, and it removes the class of bug where an incremental df drifts from
the postings it describes."* ⭐ **Right about the bug class, wrong about "cheap".** So the incremental
path needs an oracle, and this is it: build the answer the old way, independently, and diff.

✅ **FIRST RUN, 2026-09-12 16:2x:** oracle 514,519 rows over 25,965,367 postings in 100.4s; live table
514,519; **0 rows on either side alone; 0 df disagreements.** That result is what flipped the default.
⚠️ **n=1.** Re-run this after any change to chunking, postings, or the affected-set collection.

⛔ AND THE FIRST ATTEMPT AT THIS TEST WAS VOID, which is why the oracle is computed in SQL here rather
than by running a second build: I compared two consecutive builds, and the second took the UP-TO-DATE
early-return path, so it never rebuilt the term table at all. **It compared the fast path against itself
and printed 0 disagreements**, and a grep filter over the output hid the fact that the control arm had
not run. ⭐ **A test whose control arm silently did not run reads exactly like a pass.**

It writes NOTHING to any real table -- the oracle is a TEMP table, dropped when the connection closes.

Exit: 0 identical · 1 a disagreement (a real defect; report the terms) · 2 the index could not be read.

Usage:
  python scripts/audit/terms_oracle_check.py
  python scripts/audit/terms_oracle_check.py --db <path to index.sqlite>
"""
import os
import sqlite3
import sys
import time

# ⛔ ONE HOME FOR THE GRAPH. This file hardcoded %LOCALAPPDATA%/claude/graphrag and would NOT
# have followed CFL_GRAPHRAG_HOME -- [measured 2026-09-12 23:1x] seven scripts had that bug,
# so setting the variable would have pointed the BUILDER at a new disk while every READER
# stayed on the old one, each reporting success. See scripts/lib/graphrag_home.py.
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "lib"))
from graphrag_home import DB as _GRAPHRAG_DB  # noqa: E402
DEFAULT_DB = str(_GRAPHRAG_DB)


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass
    db = DEFAULT_DB
    if "--db" in argv:
        db = argv[argv.index("--db") + 1]
    if not os.path.isfile(db):
        print("⛔ UNKNOWN: no index at %s -- not a pass, no measurement" % db)
        return 2
    con = sqlite3.connect(db)
    try:
        n_post = con.execute("SELECT COUNT(*) FROM postings").fetchone()[0]
        t0 = time.time()
        con.execute("CREATE TEMP TABLE oracle AS "
                    "SELECT term, COUNT(DISTINCT chunk_id) AS df FROM postings GROUP BY term")
        el = time.time() - t0
        n_o = con.execute("SELECT COUNT(*) FROM oracle").fetchone()[0]
        n_t = con.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        only_o = con.execute("SELECT COUNT(*) FROM oracle o "
                             "LEFT JOIN terms t ON t.term=o.term WHERE t.term IS NULL").fetchone()[0]
        only_t = con.execute("SELECT COUNT(*) FROM terms t "
                             "LEFT JOIN oracle o ON o.term=t.term WHERE o.term IS NULL").fetchone()[0]
        dis = con.execute("SELECT COUNT(*) FROM terms t JOIN oracle o ON o.term=t.term "
                          "WHERE t.df<>o.df").fetchone()[0]
        print("=== TERMS ORACLE CHECK ===")
        print("  index      : %s" % db)
        print("  postings   : %d rows" % n_post)
        print("  oracle     : %d rows, built in %.1fs (full GROUP BY, the old wholesale answer)" % (n_o, el))
        print("  live terms : %d rows" % n_t)
        print("  in oracle only     : %d" % only_o)
        print("  in live terms only : %d" % only_t)
        print("  ⛔ df DISAGREEMENTS  : %d" % dis)
        if dis or only_o or only_t:
            for r in con.execute("SELECT t.term, t.df, o.df FROM terms t JOIN oracle o ON o.term=t.term "
                                 "WHERE t.df<>o.df LIMIT 10"):
                print("     %-30s live=%d oracle=%d" % (r[0][:30], r[1], r[2]))
            print("  VERDICT: ⛔ DRIFT -- the affected-set path is wrong. Re-run the builder with "
                  "--wholesale-terms and open a ticket with these terms.")
            return 1
        print("  VERDICT: ✅ IDENTICAL -- the affected-set path agrees with the wholesale answer.")
        print("  ⚠️ One clean run is n=1. This says nothing about a corpus state it has not seen.")
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
