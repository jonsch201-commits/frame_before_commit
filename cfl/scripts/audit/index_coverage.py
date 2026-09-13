#!/usr/bin/env python3
"""index_coverage.py -- what is on disk that the retrieval index cannot see (MI-4).

WHY THIS EXISTS
---------------
`[measured 2026-09-05 19:0x, CFL]` **100 files are in the tree and not in the index** --
`wiki/skills-gate` 27, `wiki/intake-triage` 69, `wiki/tracker` 4 -- and the index has no way
to say so. Every query it answers is answered honestly over a population nobody has stated.

⛔ AND THE FOUR IN `wiki/tracker/` ARE THE ONES THAT MATTER: `role-history.jsonl`,
`role-episodes.jsonl`, `corpus-index.jsonl`, `heartbeat-baseline.json` -- the adjudicated
role ledger and its inputs. The record of what CFL did well and badly is exactly the record
retrieval cannot reach. That is Jon's *"failures to be able to review your improvements
post-impoementation"* with a file list attached.

⚠️ THE TRAP THIS SCRIPT WAS BORN FROM, AND IT IS WHY THE SELFTEST IS SHAPED AS IT IS.
The first attempt to measure this asked the index `WHERE path LIKE '%/wiki/%'` and got **0**
for all 23 targets. It looked like a catastrophic coverage hole. The paths are stored
REPO-RELATIVE (`wiki/DECISIONS.md`), so a leading slash never matched. ⛔ **The finding was
an artifact of the query.** It was caught only because a CONTROL was run against
`wiki/concepts` -- a directory that had been retrieved from an hour earlier -- and the
control returned 0 too, which is impossible. ⭐ **A BROKEN QUERY AND A REAL GAP PRINT THE
SAME BYTES.** So this script asserts, on every run, that a known-present file IS found:
if the control fails, the whole report is UNKNOWN and no coverage number is printed at all.

USAGE
    index_coverage.py [--db PATH] [--root DIR] [--json]
    index_coverage.py --selftest

EXIT CODES
    0  PASS    -- control held and every walked file is indexed
    1  GAPS    -- control held; files on disk are missing from the index (they are listed)
    3  UNKNOWN -- the control failed, or the db/root could not be read. Dominates a PASS.
    2  usage
"""
import argparse
import json
import os
import sqlite3
import sys
import tempfile

# ⛔ ONE HOME FOR THE GRAPH. This file hardcoded %LOCALAPPDATA%/claude/graphrag and would NOT
# have followed CFL_GRAPHRAG_HOME -- [measured 2026-09-12 23:1x] seven scripts had that bug,
# so setting the variable would have pointed the BUILDER at a new disk while every READER
# stayed on the old one, each reporting success. See scripts/lib/graphrag_home.py.
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "lib"))
from graphrag_home import DB as _GRAPHRAG_DB  # noqa: E402
DEFAULT_DB = str(_GRAPHRAG_DB)
DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directories the index is not expected to hold. Kept SHORT and explicit: every name here is
# a claim that its absence is intended, and an unexpected absence is the finding.
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".understand-anything", ".claude"}
# raw/ is the gitignored bulk corpus -- indexed via a separate --provenance root, not the walk.
SKIP_TOP = {"raw"}


def load_index(db):
    """Return the set of indexed repo-relative paths, or (None, reason)."""
    if not os.path.exists(db):
        return None, "index db not found at %s" % db
    try:
        con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
        rows = {r[0].replace("\\", "/") for r in con.execute("select path from files")}
        con.close()   # Windows will not remove an open sqlite file; the selftest's tempdir
                      # cleanup raised WinError 32 on the FIRST run because of this line's
                      # absence. A test that cannot clean up still ran -- but it exits nonzero
                      # for a reason unrelated to what it tests, which is a false FAIL.
    except sqlite3.Error as e:
        return None, "index unreadable: %s" % e
    if not rows:
        return None, "index holds ZERO files -- that is no measurement, not a clean sweep"
    return rows, None


def walk(root):
    """Repo-relative paths of every file the index is expected to cover."""
    out = set()
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dp, root).replace("\\", "/")
        top = rel_dir.split("/")[0]
        if top in SKIP_TOP:
            dns[:] = []
            continue
        for fn in fns:
            rel = (fn if rel_dir == "." else rel_dir + "/" + fn)
            out.add(rel)
    return out


def control(indexed, root):
    """⛔ THE CONTROL. Prove the comparison can find something before trusting a zero.

    Picks a file that is BOTH on disk and expected in the index, and asserts the match.
    Without this, a path-format mismatch reports total coverage failure and reads exactly
    like a real one -- which is precisely what happened on 2026-09-05.
    """
    for probe in ("wiki/index.md", "wiki/DECISIONS.md", "CLAUDE.md", "GATES.md"):
        if os.path.exists(os.path.join(root, probe)):
            return (probe in indexed), probe
    return None, None


def report(db=DEFAULT_DB, root=DEFAULT_ROOT):
    indexed, err = load_index(db)
    if indexed is None:
        return {"verdict": "UNKNOWN", "detail": err, "gaps": {}, "control": None}
    ok, probe = control(indexed, root)
    if probe is None:
        return {"verdict": "UNKNOWN", "gaps": {}, "control": None,
                "detail": "no control probe exists on disk -- cannot show the comparison works"}
    if not ok:
        return {"verdict": "UNKNOWN", "gaps": {}, "control": probe,
                "detail": ("CONTROL FAILED: %s is on disk and reads as NOT indexed. A known-"
                           "present file must match. The comparison is broken (path format?), "
                           "so NO coverage number is reported -- a broken query and a real gap "
                           "print the same bytes." % probe)}
    disk = walk(root)
    missing = sorted(disk - indexed)
    # ⛔ STALE IS NOT UNREACHABLE, AND CONFLATING THEM INFLATES THE ALARM.
    # The first live run reported 761 missing. Its single largest bucket was `exchange/`
    # (372) -- including four files this very session had just written. A file newer than
    # the index build is PENDING the next build, not structurally invisible. Reporting one
    # number for both would have published an accusation ("761 files unretrievable") whose
    # majority was ordinary staleness. Same direction as every other error of 2026-09-05.
    try:
        idx_mtime = os.path.getmtime(db)
    except OSError:
        idx_mtime = None
    stale, structural = [], []
    for m in missing:
        try:
            newer = idx_mtime is not None and os.path.getmtime(os.path.join(root, m)) > idx_mtime
        except OSError:
            newer = False
        (stale if newer else structural).append(m)
    gaps = {}
    for m in structural:
        gaps.setdefault(m.split("/")[0] if "/" in m else "(root)", []).append(m)
    return {"verdict": "PASS" if not structural else "GAPS",
            "control": probe, "detail": "control held: %s is indexed" % probe,
            "walked": len(disk), "indexed_total": len(indexed),
            "missing": len(missing), "stale": len(stale), "structural": len(structural),
            "index_built": idx_mtime, "gaps": gaps}


def render(r):
    out = ["INDEX COVERAGE -- what is on disk that retrieval cannot see", ""]
    out.append("  control: %s" % (r.get("detail") or ""))
    if r["verdict"] == "UNKNOWN":
        out += ["", "**VERDICT: UNKNOWN** -- no coverage number reported. UNKNOWN dominates a PASS."]
        return "\n".join(out)
    out.append("  walked on disk: %d    indexed total: %d" % (r["walked"], r["indexed_total"]))
    out.append("  not in index: %d   of which STALE (written since the build, pending): %d"
               % (r["missing"], r["stale"]))
    out.append("  STRUCTURAL (the finding): %d" % r["structural"])
    out.append("")
    for top, items in sorted(r["gaps"].items(), key=lambda kv: -len(kv[1])):
        out.append("  %-22s %4d not indexed" % (top + "/", len(items)))
        for p in items[:6]:
            out.append("        %s" % p)
        if len(items) > 6:
            out.append("        ...and %d more" % (len(items) - 6))
    out.append("")
    out.append("VERDICT: %s" % ("every walked file is indexed or pending" if r["verdict"] == "PASS"
                                else "%d file(s) are STRUCTURALLY not retrievable (%d more are "
                                     "merely stale and will land on the next build)"
                                     % (r["structural"], r["stale"])))
    return "\n".join(out)


def selftest():
    ok = [True]

    def a(c, m):
        print(("  PASS  " if c else "  FAIL  ") + m)
        ok[0] = ok[0] and bool(c)

    with tempfile.TemporaryDirectory() as td:
        root = os.path.join(td, "repo")
        os.makedirs(os.path.join(root, "wiki"))
        os.makedirs(os.path.join(root, "raw", "transcripts"))
        os.makedirs(os.path.join(root, ".git"))
        for rel in ("wiki/index.md", "wiki/kept.md", "wiki/missed.md"):
            open(os.path.join(root, rel.replace("/", os.sep)), "w").write("x")
        open(os.path.join(root, "raw", "transcripts", "bulk.md"), "w").write("x")
        open(os.path.join(root, ".git", "cfg"), "w").write("x")

        db = os.path.join(td, "i.sqlite")
        con = sqlite3.connect(db)
        con.execute("create table files(path text)")

        # 1. CONTROL FAILS -> UNKNOWN, and NO number is printed. The 2026-09-05 case.
        con.executemany("insert into files values(?)", [("/wiki/index.md",), ("/wiki/kept.md",)])
        con.commit()
        r = report(db, root)
        a(r["verdict"] == "UNKNOWN", "wrong path format -> UNKNOWN (the real 09-05 failure)")
        a("missing" not in r, "UNKNOWN reports NO coverage number at all")
        a("CONTROL FAILED" in r["detail"], "it says the control failed, not that coverage is 0")

        # 2. control holds, a real gap exists -> GAPS, and the gap is NAMED
        con.execute("delete from files")
        con.executemany("insert into files values(?)", [("wiki/index.md",), ("wiki/kept.md",)])
        con.commit()
        r = report(db, root)
        a(r["verdict"] == "GAPS", "control holds + real gap -> GAPS")
        a(r["missing"] == 1 and "wiki" in r["gaps"], "exactly the 1 real gap, grouped by top dir")
        a("wiki/missed.md" in render(r), "the missing file is NAMED, not just counted")
        a(all("raw/" not in p for v in r["gaps"].values() for p in v),
          "raw/ is skipped, not reported as a gap")
        a(all(".git" not in p for v in r["gaps"].values() for p in v), ".git is skipped")

        # 3. full coverage -> PASS
        con.execute("insert into files values(?)", ("wiki/missed.md",))
        con.commit()
        r = report(db, root)
        a(r["verdict"] == "PASS", "full coverage -> PASS")

        # 4. empty index -> UNKNOWN, never PASS
        con.execute("delete from files")
        con.commit()
        a(report(db, root)["verdict"] == "UNKNOWN", "EMPTY index -> UNKNOWN, never a clean sweep")

        # 5. missing db -> UNKNOWN
        a(report(os.path.join(td, "nope.sqlite"), root)["verdict"] == "UNKNOWN",
          "absent index db -> UNKNOWN")

        # ⛔ CLOSE THE FIXTURE'S OWN HANDLE. The first two runs of this selftest crashed in
        # tempdir cleanup with WinError 32 -- every assertion had already PASSED and the
        # process still exited nonzero. A test that fails for a reason unrelated to what it
        # tests is a FALSE FAIL, and it is exactly as misleading as a false pass.
        con.close()

    print("\nSELFTEST: %s" % ("PASS" if ok[0] else "FAIL"))
    return 0 if ok[0] else 1


def main():
    ap = argparse.ArgumentParser(description="files on disk that the retrieval index cannot see")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    r = report(args.db, args.root)
    print(json.dumps(r, indent=2) if args.json else render(r))
    return {"PASS": 0, "GAPS": 1, "UNKNOWN": 3}[r["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
