"""Is a raw conversation the graph does NOT contain still REACHABLE through the graph?

WHY THIS EXISTS -- Jon set the standard himself, 2026-09-12 ~23:2x CDT, verbatim (typos his):

  "Look i think it might be fine if the graph doesn't have raw conversations in it if our ontologies
   and synthesis are good enough, and so long as the raw conversatrion is still *reachable* via the
   graph - from key concepts etc.... I legit can't tell what is foundationally best, and I do think
   i've been told in multiple ways to make the graph smaller."

⭐ **THAT SENTENCE CONVERTS AN ARGUMENT ABOUT SIZE INTO A TESTABLE INVARIANT, and it is the better
question.** I had been arguing the graph should be bigger -- index the 544 MB of raw conversation the
indexer reduces away. He is right that he has been told repeatedly to make it smaller, and right that
CONTAINMENT is not the requirement. REACHABILITY is. So this measures reachability instead.

THE INVARIANT, three clauses, all three required or the conversation is not reachable:

  A. RESOLVES  -- the summary chunk's cited path opens today
  B. EXISTS    -- the file is somewhere on this machine, under any known root
  C. POINTED AT -- something in the KNOWLEDGE tier names it, so a reader ARRIVES by following
                   meaning rather than by guessing a phrase the summary happens to contain

`[first run 2026-09-12 23:0x]` A: 98.2% (67% before the corpus mirror was populated the same night).
C: 47.4% by filename, +32.4% by session id only, and **20.2% -- 587 transcripts -- pointed at by
NOTHING.** Those are islands: the graph holds a ~2,200-char summary of each and no concept, entity or
source page names them.

⛔ **THAT IS THE MECHANISM BEHIND "THE RECORD IS THIN."** Not missing content -- missing EDGES. This
trunk has published that phrase as a finding about the corpus when it was a finding about the index.

WHAT THIS DOES NOT DO:
  * It does not grade whether a summary is GOOD. That is judgment and belongs to a reader.
  * Clause C counts a mention by FILENAME or by SESSION ID. A session id (`b98d2c`) is a weak edge --
    nobody arrives there by following meaning -- so it is reported SEPARATELY and never folded into
    the pass column.
  * It reads one index. A trunk with several graphs must run it per graph.
  * A file the indexer body-chunked is OUT of the population: its raw text is in the graph, so
    reachability is not a question it can fail.

Usage:
    python scripts/audit/graph_reachability.py
    python scripts/audit/graph_reachability.py --list-islands 40
    python scripts/audit/graph_reachability.py --selftest
Exit: 0 every clause holds | 3 at least one island or unresolved path | 4 could not run (UNKNOWN)
"""
import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
try:
    from graphrag_home import DB as DEFAULT_DB
except Exception:                                            # pragma: no cover
    DEFAULT_DB = Path(os.environ.get("LOCALAPPDATA", "")) / "claude" / "graphrag" / "index.sqlite"

# Same alias table as retrieve.py and recover_from_index.py, and for the same reason: on 2026-09-12 a
# third of this index was reported GONE because one mirror root was unpopulated while 98.2% of the
# files sat on another disk. A NOT-FOUND IS A CLAIM ABOUT WHERE YOU LOOKED.
ALIASES = (
    ("N:/claude-corpus/cfl/", "G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer/"),
    ("N:/claude-corpus/cfl/", "N:/claude-cfl/clone/"),
)
# A transcript's own name and its 6-hex session id are how this corpus cites a conversation.
TOKEN = re.compile(r"\b(?:code|chat|hist)-\d{4}-\d{2}-\d{2}-[0-9a-f]{6}[A-Za-z0-9._-]*")
SID = re.compile(r"-([0-9a-f]{6})-")
HEX6 = re.compile(r"\b[0-9a-f]{6}\b")
MIN_ORIGINAL = 20_000          # below this a one-chunk file may legitimately BE the whole file


# Jon, 2026-09-12 ~23:5x CDT, verbatim: "Islands are defects I assume and you ticket those by default".
# Yes -- so the instrument emits the ticket rather than a human copying a number into a map.
#
# ⭐ ONE TICKET FOR THE CLASS, NOT 667 TICKETS. A ticket per island would be a queue nobody can read
# and a count nobody can move; this trunk has 350 deferrals on record and 344 of them unwatchable,
# which is what per-instance ticketing produces. The ticket body is REGENERATED from the measurement
# every time, so it cannot drift from the graph ([[derive-dont-record]]) -- and the number at the top
# is the progress measure: it goes down or the ticket is not being worked.
TICKET_PATH = ROOT / "wiki" / "tracker" / "tickets" / "GRAPH-ISLANDS.md"


def write_ticket(rows, islands, db):
    import datetime as _dt
    NL = chr(10)
    when = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    n = rows["total"]
    body = [
        "---",
        "kind: ticket",
        "slug: graph-islands",
        "status: OPEN" if rows["island"] else "status: CLOSED-BY-MEASUREMENT",
        "owner: cfl",
        f"generated: \"{when} CDT [MEASURED]\"",
        "generated_by: scripts/audit/graph_reachability.py --ticket",
        f"islands: {rows['island']}",
        f"population: {n}",
        f"index: \"{db}\"",
        "on_silence: \"nothing executes; the count is re-measured at every compact boundary and this",
        "  file is rewritten. A rising number is the finding.\"",
        "---",
        "",
        "# GRAPH ISLANDS — reduced conversations no page points at",
        "",
        "**Jon, 2026-09-12, verbatim:** *\"Islands are defects I assume and you ticket those by default\"* —"
        " and, setting the standard this measures: *\"it might be fine if the graph doesn\'t have raw"
        " conversations in it if our ontologies and synthesis are good enough, and so long as the raw"
        " conversatrion is still *reachable* via the graph - from key concepts etc.\"*",
        "",
        f"**{rows['island']} of {n} reduced transcripts ({100.0*rows['island']/max(1,n):.1f}%) are"
        f" pointed at by nothing in the knowledge tier.**",
        "",
        "| clause | count | share |",
        "|---|---|---|",
        f"| path resolves at its citation | {rows['resolves']:,} | {100.0*rows['resolves']/max(1,n):.1f}% |",
        f"| file exists under any known root | {rows['exists']:,} | {100.0*rows['exists']/max(1,n):.1f}% |",
        f"| named by a knowledge page | {rows['by_name']:,} | {100.0*rows['by_name']/max(1,n):.1f}% |",
        f"| reachable ONLY by session id (weak edge) | {rows['by_sid']:,} | {100.0*rows['by_sid']/max(1,n):.1f}% |",
        f"| **ISLANDS** | **{rows['island']:,}** | **{100.0*rows['island']/max(1,n):.1f}%** |",
        "",
        "**An island holds a ~2,200-character summary and no concept, entity or source page names it,"
        " so the only way to land on it is to guess a phrase it happens to contain. This is the"
        " mechanism behind \"the record is thin\": missing EDGES, not missing content.**",
        "",
        "⚠️ **WHAT THIS TICKET DOES NOT SAY.** It does not say every island SHOULD be linked. Some of"
        " these conversations are genuinely not worth a concept page, and linking them all would be"
        " the same error as indexing everything — volume standing in for judgment. **The work is to"
        " read down the list and either link or dismiss, and a dismissal is a disposition too.**",
        "",
        "## The islands, regenerated at every compact boundary",
        "",
    ]
    for path in sorted(islands):
        body.append(f"- `{path}`")
    if not islands:
        body.append("*(none — every reduced transcript is named by at least one knowledge page)*")
    TICKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    TICKET_PATH.write_text(NL.join(body) + NL, encoding="utf-8")
    return TICKET_PATH


def resolve(cited):
    n = str(cited).replace(chr(92), "/")
    for c in (n, os.path.expanduser(n), str(ROOT / n)):
        if os.path.isfile(c.replace("/", os.sep)):
            return c
    for a, b in ALIASES:
        if n.startswith(a):
            cand = b + n[len(a):]
            if os.path.isfile(cand.replace("/", os.sep)):
                return cand
    return None


def audit(db=None):
    db = Path(db or DEFAULT_DB)
    if not db.is_file():
        return 4, {"why": f"no index at {db} -- a check that could not run is never a pass"}, []
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        reduced = []
        for fid, path, nbytes in con.execute(
                "select id, path, bytes from files where tier='provenance'"):
            c, = con.execute("select count(*) from chunks where file_id=?", (fid,)).fetchone()
            if c == 1 and (nbytes or 0) > MIN_ORIGINAL:
                reduced.append((fid, str(path).replace(chr(92), "/"), nbytes or 0))
        if not reduced:
            return 4, {"why": "no reduced provenance files found -- either nothing is reduced (good, "
                              "say so from the builder's config) or this query is wrong. Empty "
                              "denominator is UNKNOWN, never a pass."}, []
        # ONE pass over the knowledge tier, into two token SETS. Substring-searching 44 MB per file
        # took minutes; set membership is O(1) and the tokens are exactly how a page cites a file.
        names, sids = set(), set()
        for (txt,) in con.execute("select c.text from chunks c join files f on f.id=c.file_id "
                                  "where f.tier='knowledge'"):
            t = txt or ""
            for m in TOKEN.findall(t):
                names.add(m[:-3] if m.endswith(".md") else m)
            sids.update(HEX6.findall(t))
    finally:
        con.close()

    rows = {"total": len(reduced), "resolves": 0, "exists": 0, "by_name": 0, "by_sid": 0, "island": 0}
    islands = []
    for _fid, path, _b in reduced:
        at = resolve(path)
        if os.path.isfile(str(path).replace("/", os.sep)):
            rows["resolves"] += 1
        if at:
            rows["exists"] += 1
        base = os.path.basename(path)
        stem = base[:-3] if base.endswith(".md") else base
        core = stem[:-8] if stem.endswith(".sidecar") else stem
        if stem in names or core in names:
            rows["by_name"] += 1
            continue
        m = SID.search(base)
        if m and m.group(1) in sids:
            rows["by_sid"] += 1
            continue
        rows["island"] += 1
        islands.append(path)
    rc = 3 if (rows["island"] or rows["exists"] < rows["total"]) else 0
    return rc, rows, islands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db")
    ap.add_argument("--list-islands", type=int, default=8)
    ap.add_argument("--ticket", action="store_true",
                    help="write the standing island ticket (regenerated, never appended)")
    a, _ = ap.parse_known_args()
    rc, rows, islands = audit(a.db)
    print("=== graph reachability: can a reader ARRIVE at a reduced conversation? ===")
    if rc == 4:
        print("UNKNOWN -- " + rows["why"])
        return 4
    n = rows["total"]
    pct = lambda k: f"{100.0*rows[k]/n:5.1f}%"
    print(f"reduced provenance files (population) : {n:,}")
    print(f"  A. path resolves at its citation    : {rows['resolves']:,}  {pct('resolves')}")
    print(f"  B. file exists under ANY known root : {rows['exists']:,}  {pct('exists')}")
    print(f"  C. named by a knowledge page        : {rows['by_name']:,}  {pct('by_name')}")
    print(f"     reachable only by session id     : {rows['by_sid']:,}  {pct('by_sid')}  "
          f"<-- weak edge, not counted as a pass")
    print(f"  ⛔ ISLANDS -- pointed at by nothing  : {rows['island']:,}  {pct('island')}")
    if islands:
        print()
        print("An island holds a ~2,200-char summary and no page names it, so the only way to land on")
        print("it is to guess a phrase it contains. THIS is the mechanism behind \"the record is thin\":")
        print("missing edges, not missing content.")
        for p in islands[:a.list_islands]:
            print(f"     {os.path.basename(p)[:96]}")
        if len(islands) > a.list_islands:
            print(f"     ... and {len(islands) - a.list_islands:,} more (--list-islands N)")
    print()
    if a.ticket:
        try:
            tp = write_ticket(rows, islands, a.db or DEFAULT_DB)
            print(f"TICKET written: {tp.relative_to(ROOT)}  ({rows['island']} islands)")
        except OSError as e:
            print(f"TICKET NOT WRITTEN: {e} -- the count above still stands")
    print("Jon's standard, 2026-09-12: it is fine for the graph not to CONTAIN the raw conversation")
    print("so long as it is REACHABLE. This is that standard, measured. It reports; it blocks nothing.")
    return rc


def selftest():
    import tempfile
    fails = []
    NL = chr(10)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        db = t / "i.sqlite"
        con = sqlite3.connect(db)
        con.executescript(
            "create table files(id integer primary key, path text, sha text, bytes integer,"
            " kind text, tier text);"
            "create table chunks(id integer primary key, file_id integer, ord integer, heading text,"
            " start_line integer, end_line integer, ntok integer, text text);")

        def prov(i, name, nbytes=50000, chunks=1):
            con.execute("insert into files values (?,?,'s',?,'md','provenance')",
                        (i, str(t / name), nbytes))
            for k in range(chunks):
                con.execute("insert into chunks values (?,?,?,'h',1,1,9,'summary text')",
                            (100 + i * 10 + k, i, k))

        # 1 named by a knowledge page · 2 sid-only · 3 island · 4 body-chunked (out of scope)
        prov(1, "code-2026-01-01-aaaaaa-alpha.md")
        prov(2, "code-2026-01-02-bbbbbb-beta.md")
        prov(3, "code-2026-01-03-cccccc-gamma.md")
        prov(4, "code-2026-01-04-dddddd-delta.md", chunks=3)
        prov(5, "code-2026-01-05-eeeeee-small.md", nbytes=100)      # below MIN_ORIGINAL
        con.execute("insert into files values (9,?,'s',10,'md','knowledge')", (str(t / "k.md"),))
        con.execute("insert into chunks values (900,9,0,'h',1,1,9,?)",
                    ("see code-2026-01-01-aaaaaa-alpha.md and session bbbbbb for context",))
        con.commit(); con.close()

        rc, rows, islands = audit(db)
        if rows.get("total") != 3:
            fails.append(f"population wrong: {rows.get('total')} -- body-chunked and tiny files must "
                         f"be OUT of scope, they cannot fail reachability")
        if rows.get("by_name") != 1:
            fails.append(f"by_name={rows.get('by_name')}, expected 1")
        if rows.get("by_sid") != 1:
            fails.append(f"by_sid={rows.get('by_sid')}, expected 1 (weak edge, counted separately)")
        if rows.get("island") != 1 or len(islands) != 1:
            fails.append(f"island={rows.get('island')} islands={len(islands)}, expected 1")
        if rc != 3:
            fails.append(f"rc={rc}, expected 3 when an island exists")

        # NEGATIVE ARM 1: no islands and every file present -> rc 0. One condition changed.
        con = sqlite3.connect(db)
        con.execute("update chunks set text=? where id=900",
                    ("code-2026-01-01-aaaaaa-alpha.md code-2026-01-02-bbbbbb-beta.md "
                     "code-2026-01-03-cccccc-gamma.md",))
        con.commit(); con.close()
        for nm in ("code-2026-01-01-aaaaaa-alpha.md", "code-2026-01-02-bbbbbb-beta.md",
                   "code-2026-01-03-cccccc-gamma.md"):
            (t / nm).write_text("x", encoding="utf-8")
        rc2, rows2, isl2 = audit(db)
        if rc2 != 0 or rows2["island"] or rows2["exists"] != 3:
            fails.append(f"clean arm -> rc={rc2} island={rows2['island']} exists={rows2['exists']}")

        # TICKET ARM: the ticket must be REGENERATED, never appended -- a ticket that grows every
        # boundary is a log, and its count stops meaning anything.
        global TICKET_PATH, ROOT
        keep_tp, keep_root = TICKET_PATH, ROOT
        ROOT = t
        TICKET_PATH = t / "wiki" / "tracker" / "tickets" / "GRAPH-ISLANDS.md"
        write_ticket(rows, islands, db)
        first = TICKET_PATH.read_text(encoding="utf-8")
        write_ticket(rows, islands, db)
        second = TICKET_PATH.read_text(encoding="utf-8")
        if len(second) != len(first):
            fails.append("ticket GREW on a second write -- it is appending, not regenerating")
        if "status: OPEN" not in first or "islands: 1" not in first:
            fails.append("ticket frontmatter missing status/count")
        write_ticket({"total": 3, "resolves": 3, "exists": 3, "by_name": 3, "by_sid": 0, "island": 0},
                     [], db)
        if "CLOSED-BY-MEASUREMENT" not in TICKET_PATH.read_text(encoding="utf-8"):
            fails.append("zero islands did not close the ticket by measurement")
        TICKET_PATH, ROOT = keep_tp, keep_root

        # NEGATIVE ARM 2: a missing index is UNKNOWN, never clean
        if audit(t / "nope.sqlite")[0] != 4:
            fails.append("missing index did not return UNKNOWN")

        # NEGATIVE ARM 3: an index with NO reduced files is UNKNOWN (empty denominator), not a pass
        db2 = t / "empty.sqlite"
        c2 = sqlite3.connect(db2)
        c2.executescript("create table files(id integer primary key, path text, sha text,"
                         " bytes integer, kind text, tier text);"
                         "create table chunks(id integer primary key, file_id integer, ord integer,"
                         " heading text, start_line integer, end_line integer, ntok integer,"
                         " text text);")
        c2.commit(); c2.close()
        if audit(db2)[0] != 4:
            fails.append("empty population did not return UNKNOWN")

    for f in fails:
        print("  FAIL " + f)
    print(f"selftest: {'PASS' if not fails else 'FAIL'} -- {len(fails)} failure(s), 3 negative arms")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
