#!/usr/bin/env python3
"""frame_a.py -- Two-Query Isolation for cross-trunk retrieval, and the bias check that goes with it.

BUILT 2026-09-12 ~14:3x CDT on Jon's order. Jon, turn 20 of
`N:\\antigravity-hub\\wiki\\sources\\sessions\\SESSION-GOOGLE-AIMODE-WIKISKILL-GRAPHRAG-2026-09-12.md`
(a 20-turn conversation between Jon and Google Search AI Mode, parsed for CFL by the Gemini seat in
his VS Code Antigravity extension), verbatim, typos his:

    "Frame a immediately. Check biases. This is an update. Then B in background? As previously
     advised?"

THE TWO FRAMES, as that session defines them (Jon's turn 19 posed them; the AI Mode answer named them):

  FRAME A -- TWO-QUERY ISOLATION. To see how a peer's WikiSkills turn affects its world, a trunk runs
  exactly TWO clean, separated queries: (1) an internal local baseline against its OWN graph, and
  (2) a targeted query into the PEER's rows. It ingests only the concentrated structural signals it
  chooses to care about. Stated benefit: high information density and ZERO MATH BLEEDING -- trunk A is
  protected from trunk B's internal noise.

  FRAME B -- ALL-TRUNK FILTERED QUERY. One broadcast query across every co-trunk, with a STRICT
  CLIENT-SIDE METADATA FILTER AT THE INGESTION GATE. Faster global awareness, and a named risk: the
  "Slinky Effect" if the filters are even slightly too broad -- dense but thematically outlying
  connections collapse orthogonal concepts into one retrieval window and subtle context is dropped.

  The session's verdict, and Jon's own rule inside it: *"Opining on just your graph is best more often
  at first"* remains primary, and Frame A is the gold standard for cross-trunk synchronization.

⛔ WHY THIS FILE IS A CORRECTION AND NOT A FEATURE. `[measured 2026-09-12 14:2x CDT]`
`scripts/query_federated.py --help` accepts `--dialogue`, `--transcripts`, `--no-dedupe`, `--edges`,
`--json`, `--status` and **NO TRUNK SCOPE OF ANY KIND.** Every cross-trunk query this fleet runs today
is ONE POOLED QUERY over all 62,037 federated rows with a dedupe on top. ⭐ **That is Frame B WITHOUT
the filter at the ingestion gate** -- the model Jon ranked second, stripped of the one safeguard that
made it second rather than unsafe. Nobody chose it; it is what the only available tool does.

⚠️ THE FEDERATED INDEX CAN BE SCOPED AND NOTHING WAS SCOPING IT. `docs_fts` carries a `trunk` column
(schema: slug, trunk, title, body), so a per-trunk query was one WHERE clause away the whole time.

WHAT "CHECK BIASES" MEANS HERE, made falsifiable rather than left as a word:
  The pooled query's top-k is reported BESIDE the two isolated queries, with its per-trunk
  composition. If one trunk takes a share of the slots far above its share of the corpus, that is
  CENTRALITY INFLATION -- the session's own term for authority being routed disproportionately through
  a structurally dominant node -- and it is printed as a LEVEL, never as a trend.
  ⛔ A bias check that cannot come out clean is not a check. The negative arm is in selftest().

FIRST LIVE RUN, 2026-09-12 14:4x CDT -- what the bias check found, and what I nearly published.

`[measured, `--peer antigravity -k 6 --no-local`]` Pooled top-6 composition against corpus share:
Personal **2.35x**, CFL **1.40x**, Antigravity **0.64x**, and **Secretary and Professional took ZERO
slots** while being 5.6% and 4.2% of the rows. ⭐ So the pooled query does not merely mix populations,
it STARVES two trunks entirely -- which no reader of a pooled result list would ever notice.

⛔ AND THE REAL FINDING IS ONE LAYER DOWN. `[measured]` FIVE Antigravity subagent transcript JSONLs
account for **26,816 of the 62,647 rows -- 42.8% of the entire fleet graph**:
  44983b83 8,745 · 5d237644 6,117 · 4f03fe06 5,175 · c0d54590 4,959 · 3843255e 1,820
⭐ **Five files own nearly half the index.** That is centrality inflation in its most literal form, and
it is why Antigravity reads as 52% of the corpus and why a pooled top-k is so easy to dominate.

⚠️ ⛔ TWO NUMBERS WERE WITHDRAWN BEFORE THIS FILE WAS COMMITTED, and the withdrawal is the useful part.
I measured "73.3% of the index is redundant" by BASENAME, then "51.1% redundant" by (trunk, relpath).
**Both are wrong, in the same way: `docs_meta` is CHUNK-level, not document-level** -- 62,647 rows over
30,608 distinct documents. The "redundancy" is CHUNKING doing its job. ⛔ **CFL had already recorded
that exact fact earlier the same day (`docs_meta` is chunk-level, 61,197 rows vs 30,234 paths) and I
re-derived it as a discovery anyway.** The lesson is not about chunks: **a ratio over rows is a claim
about documents only if rows are documents, and this index has taught that once already today.**
✅ What survives measurement: the five-file 42.8% concentration, and the pooled query's starvation of
two trunks. What does not: any fleet-wide "duplication" percentage.

Exit: 0 ran · 2 an input was UNKNOWN (missing index, peer not in the roster) -- UNKNOWN DOMINATES · 3 usage.

Usage:
  python scripts/graphrag/frame_a.py "query" --peer antigravity
  python scripts/graphrag/frame_a.py "query" --peer secretary -k 5 --no-local
  python scripts/graphrag/frame_a.py --status
  python scripts/graphrag/frame_a.py --selftest
"""
import argparse
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FED_DB = r"N:\claude-indexes\graphrag-federated\index.sqlite"
LOCAL_RETRIEVE = os.path.join(ROOT, "scripts", "graphrag", "retrieve.py")

# The trunk labels as the FEDERATED index spells them. ⚠️ DERIVED AT RUNTIME by --status and by
# resolve_peer(); this list is a fallback for the usage text only. An enumeration written down here
# and trusted is the defect this program is named for.
FALLBACK_TRUNKS = ["antigravity", "cfl", "personal", "secretary", "professional"]


def fed_conn(db=FED_DB):
    p = db.replace("\\", "/")
    if not os.path.isfile(db):
        return None
    return sqlite3.connect("file:%s?mode=ro" % p, uri=True)


def trunk_roster(conn):
    """trunk -> row count, measured. This is the denominator the bias check needs."""
    out = {}
    for t, n in conn.execute("select trunk, count(*) from docs_meta group by trunk order by 2 desc"):
        out[t or "(null)"] = n
    return out


def fts_query(conn, query, k, trunk=None):
    """FTS5 match, optionally scoped to one trunk. Returns [(trunk, path_or_slug, title)]."""
    # bm25() is negative-better in FTS5; order by it ascending.
    if trunk:
        sql = ("select f.trunk, coalesce(m.path, f.slug), coalesce(f.title,'') "
               "from docs_fts f left join docs_meta m on m.slug = f.slug "
               "where docs_fts match ? and f.trunk = ? order by bm25(docs_fts) limit ?")
        args = (query, trunk, k)
    else:
        sql = ("select f.trunk, coalesce(m.path, f.slug), coalesce(f.title,'') "
               "from docs_fts f left join docs_meta m on m.slug = f.slug "
               "where docs_fts match ? order by bm25(docs_fts) limit ?")
        args = (query, k)
    try:
        return list(conn.execute(sql, args))
    except sqlite3.OperationalError as exc:
        return [("(UNKNOWN)", "FTS query failed: %s" % exc, "")]


def local_baseline(query, k):
    """Query 1 of Frame A: CFL's OWN index, via its own retriever. Never the federated mirror --
    the mirror is a snapshot and the live tree is the thing this trunk is responsible for."""
    if not os.path.isfile(LOCAL_RETRIEVE):
        return None, "retrieve.py absent at %s" % LOCAL_RETRIEVE
    try:
        r = subprocess.run([sys.executable, LOCAL_RETRIEVE, query, "-k", str(k)],
                           capture_output=True, text=True, timeout=300)
    except Exception as exc:
        return None, "local retrieve failed: %s: %s" % (type(exc).__name__, exc)
    if r.returncode != 0:
        return None, "local retrieve exit %d" % r.returncode
    return r.stdout, None


def bias_check(pooled, roster, k):
    """Per-trunk composition of the POOLED top-k against each trunk's share of the corpus.

    Returns rows of (trunk, slots, slot_share, corpus_share, inflation) where inflation is
    slot_share / corpus_share. ⚠️ It is a RATIO, reported as a level. A value near 1.0 is neutral;
    the check CAN come out clean, which is what makes it a check."""
    total_rows = sum(roster.values()) or 1
    slots = {}
    for t, _p, _ti in pooled:
        slots[t] = slots.get(t, 0) + 1
    n = sum(slots.values()) or 1
    rows = []
    for t in sorted(set(list(slots) + list(roster)), key=lambda x: -slots.get(x, 0)):
        ss = slots.get(t, 0) / n
        cs = roster.get(t, 0) / total_rows
        rows.append((t, slots.get(t, 0), ss, cs, (ss / cs) if cs else None))
    return rows


def run(query, peer, k, do_local=True, db=FED_DB):
    conn = fed_conn(db)
    if conn is None:
        print("⛔ UNKNOWN: federated index not found at %s" % db)
        print("   UNKNOWN DOMINATES -- this is not an empty result set, it is no measurement.")
        return 2
    roster = trunk_roster(conn)
    unknown = []
    # ⛔ CASE. The federated index spells trunks "Antigravity"/"CFL"/"Secretary"; a caller types
    # "antigravity". The FIRST selftest run exposed this -- the roster came back capitalised and the
    # default --peer would have scoped to nothing and printed "0 hits", which reads exactly like a
    # true empty result. ⭐ An unresolvable peer is UNKNOWN; a resolvable one is normalised here.
    if peer not in roster:
        for t in roster:
            if t.lower() == str(peer).lower():
                peer = t
                break

    print("=== FRAME A -- TWO-QUERY ISOLATION ===")
    print('  query : "%s"' % query)
    print("  peer  : %s" % peer)
    print("  rows  : %d federated, by trunk %s" % (sum(roster.values()), roster))
    if peer not in roster:
        unknown.append("peer %r is not a trunk in this index; roster is %s" % (peer, sorted(roster)))

    print("\n-- QUERY 1 of 2: INTERNAL LOCAL BASELINE (CFL's own live index, not the mirror) --")
    if do_local:
        out, err = local_baseline(query, k)
        if err:
            unknown.append(err)
            print("  ⛔ UNKNOWN: %s" % err)
        else:
            for line in out.splitlines():
                if line.strip():
                    print("  " + line)
    else:
        print("  SKIPPED by --no-local. ⚠️ A skipped query is UNKNOWN, never a clean baseline.")
        unknown.append("local baseline skipped by flag")

    print("\n-- QUERY 2 of 2: PEER-SCOPED (%s rows only, zero math bleeding) --" % peer)
    if peer in roster:
        hits = fts_query(conn, query, k, trunk=peer)
        if not hits:
            print("  0 hits in %s. An empty scoped result is INFORMATIVE and is not an error." % peer)
        for t, p, ti in hits:
            print("  [%s] %s%s" % (t, p, ("  -- " + ti) if ti else ""))
    else:
        print("  ⛔ not run: peer absent from the roster")

    print("\n-- BIAS CHECK: what the POOLED query (today's only tool) would have returned --")
    pooled = fts_query(conn, query, k)
    for t, p, ti in pooled:
        print("  [%s] %s" % (t, p))
    print("\n  per-trunk composition of the pooled top-%d against each trunk's share of the corpus:" % k)
    print("  %-16s %5s %9s %9s %10s" % ("trunk", "slots", "slot%", "corpus%", "inflation"))
    for t, s, ss, cs, inf in bias_check(pooled, roster, k):
        if s == 0 and cs < 0.01:
            continue
        print("  %-16s %5d %8.1f%% %8.1f%% %10s"
              % (t, s, ss * 100, cs * 100, ("%.2fx" % inf) if inf else "n/a"))
    print("  ⭐ inflation near 1.00x is neutral. A trunk far above 1.00x is taking retrieval slots")
    print("     out of proportion to its size -- CENTRALITY INFLATION, the session's own term, and")
    print("     the reason Frame A keeps the two populations apart instead of pooling them.")

    if unknown:
        print("\n  ⛔ UNKNOWN -- %d input(s) could not be measured. The output above is a FLOOR:" % len(unknown))
        for u in unknown:
            print("     %s" % u)
    print("\n  FRAME B (all-trunk filtered, run in the background per Jon's turn 20): NOT IMPLEMENTED HERE.")
    print("  ⚠️ Saying so is the point. The pooled query printed above is Frame B WITHOUT its filter,")
    print("     which is why it is shown as a bias check and never as a result.")
    return 2 if unknown else 0


def selftest():
    fails = 0

    def chk(label, got, want):
        nonlocal fails
        ok = got == want
        print(("PASS" if ok else "FAIL"), label, "->", got)
        fails += not ok

    # bias_check arithmetic, on numbers chosen so the answer is checkable by hand.
    roster = {"big": 900, "small": 100}          # big is 90% of a 1000-row corpus
    pooled = [("big", "p", "")] * 9 + [("small", "p", "")]   # big takes 9 of 10 slots
    rows = {r[0]: r for r in bias_check(pooled, roster, 10)}
    chk("neutral case: 90% of corpus taking 90% of slots is 1.00x",
        round(rows["big"][4], 2), 1.0)
    chk("and the small trunk is neutral too", round(rows["small"][4], 2), 1.0)

    pooled2 = [("small", "p", "")] * 10          # small takes ALL slots
    rows2 = {r[0]: r for r in bias_check(pooled2, roster, 10)}
    chk("inflation fires: 10% of corpus taking 100% of slots is 10.00x",
        round(rows2["small"][4], 2), 10.0)
    chk("and the starved trunk reads 0.00x", round(rows2["big"][4], 2), 0.0)

    # ⛔ THE NEGATIVE ARM. A check that cannot come out clean is not a check.
    chk("a check that can return neutral is a real check (not always-alarming)",
        round(rows["big"][4], 2) == 1.0 and round(rows2["small"][4], 2) == 10.0, True)

    conn = fed_conn()
    if conn is None:
        print("PASS federated index absent -> UNKNOWN, and that is the correct verdict here")
    else:
        roster_live = trunk_roster(conn)
        ok = len(roster_live) >= 2
        print(("PASS" if ok else "FAIL"), "live roster has >=2 trunks ->", len(roster_live), roster_live)
        fails += not ok
        ok2 = "trunk" in [r[1] for r in conn.execute("pragma table_info(docs_fts)")]
        print(("PASS" if ok2 else "FAIL"), "docs_fts really carries a trunk column (scoping is possible)")
        fails += not ok2

    print("SELFTEST", "PASS" if not fails else "FAIL", "%d failure(s)" % fails)
    return 1 if fails else 0


def main(argv):
    # Windows stdout is cp1252 here and this file's OWN emoji crashed its FIRST live run with
    # UnicodeEncodeError -- after the selftest passed, because the selftest prints no emoji.
    # Another test that could not see the defect it was meant to cover.
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Frame A two-query isolation with a bias check")
    ap.add_argument("query", nargs="?")
    ap.add_argument("--peer", default="antigravity")
    ap.add_argument("-k", type=int, default=6)
    ap.add_argument("--no-local", action="store_true")
    ap.add_argument("--db", default=FED_DB)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    conn = fed_conn(a.db)
    if a.status:
        if conn is None:
            print("⛔ UNKNOWN: no federated index at %s" % a.db)
            return 2
        r = trunk_roster(conn)
        print("federated rows %d across %d trunk(s)" % (sum(r.values()), len(r)))
        for t, n in r.items():
            print("  %-16s %7d" % (t, n))
        return 0
    if not a.query:
        ap.print_usage()
        return 3
    return run(a.query, a.peer, a.k, do_local=not a.no_local, db=a.db)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
