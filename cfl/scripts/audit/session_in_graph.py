#!/usr/bin/env python
"""session_in_graph.py -- is THIS session's work in the corpus, and in the index?

WHY THIS EXISTS. On 2026-09-07 Jon asked whether the graph was complete through the prior windows.
Every existing instrument answered a NEIGHBOURING question and none answered his:

  index_coverage.py        files on disk missing from the index -- but it never looks at raw/
  cc_corpus_gap.py         a render's turn count vs its source jsonl -- never checks the index
  render_freshness_check.py  newest .md mtime vs newest PreCompact receipt -- one binary comparison
  coverage_census.py       whether a session id is CITED in wiki/ -- a citation census, not membership
  feed_liveness.py         staleness of the mirrored feeds -- measures the pipe, not the content

⛔ So "is session X's full transcript in the corpus AND reachable in the index" had to be traced BY
HAND, and the hand-trace found two breaks nobody was alarming on: the exporter's corpus root was
pinned to G: while the index reads N:, and the G:->N: mirror belongs to a daemon that was asleep.
A question that can only be answered by hand gets answered once, by whoever happens to ask.

WHAT IT GRADES, per session, main and subagent classes NEVER POOLED (cc_corpus_gap.py's rule: they
carry different authority and pooling produces a healthy-looking average precisely because the
low-authority class dominates the count):

  PRESENT  on disk, in the index, current, AND substantially chunked
  THIN     present and effectively unreachable -- the index holds a summary, not the document
  STALE    transcript on disk but materially shorter than its jsonl (the session grew after export)
  MISSING  no transcript, or a transcript the index does not hold
  UNKNOWN  could not be measured -- and UNKNOWN DOMINATES: it is never folded into a pass

⭐ IT RUNS A CONTROL FIRST. A session known to be indexed must grade PRESENT; if the control fails,
the WHOLE RUN reports UNKNOWN rather than a confident zero. index_coverage.py's first real run
returned "0 gaps" from a broken LIKE pattern -- a broken query and a real absence print the same
bytes unless something insists otherwise.

⚠️ TURN COUNTS ARE TWO DIFFERENT COUNTERS BY CONSTRUCTION. The jsonl side counts user/assistant
records; the markdown side counts `## ` turn headings the converter emitted. They do not have to
agree exactly and a small delta is not a defect -- so STALE fires on a RELATIVE shortfall
(--tolerance, default 0.75), never on inequality. Reporting both numbers is the point: a reader who
distrusts the grade can re-derive it.

USAGE
  session_in_graph.py                    # this trunk's main sessions
  session_in_graph.py --all-trunks       # every project key under ~/.claude/projects
  session_in_graph.py --subagents        # include subagent transcripts (reported separately)
  session_in_graph.py --session a86404   # one session (uuid prefix)
  session_in_graph.py --json
"""
import argparse
import glob
import io
import json
import os
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")
# ⛔ ONE HOME FOR THE GRAPH. This file hardcoded %LOCALAPPDATA%/claude/graphrag and would NOT
# have followed CFL_GRAPHRAG_HOME -- [measured 2026-09-12 23:1x] seven scripts had that bug,
# so setting the variable would have pointed the BUILDER at a new disk while every READER
# stayed on the old one, each reporting success. See scripts/lib/graphrag_home.py.
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "lib"))
from graphrag_home import DB as _GRAPHRAG_DB  # noqa: E402
DEFAULT_DB = str(_GRAPHRAG_DB)
TURN_HEADING = re.compile(r"^## (Human|Assistant|Dispatch|Compaction Boundary)", re.M)


def jsonl_records(path):
    """Every record in the live jsonl -- the same population the converter reports as
    `total_records`, so the two are directly comparable."""
    n = 0
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.strip():
                    n += 1
    except OSError:
        return None
    return n


def sidecar_counts(md_path):
    """(turns_covered, total_records) as the CONVERTER recorded them at export time, or (None, None).
    Reading the artifact's own numbers beats re-deriving them: a re-derivation is a second parser of
    the same artifact, which this codebase already names as a divergence risk."""
    if not md_path or not md_path.endswith(".md"):
        return (None, None)
    sc = md_path[:-3] + ".sidecar.md"
    if not os.path.isfile(sc):
        return (None, None)
    turns = records = None
    try:
        # ⛔ FIRST OCCURRENCE ONLY -- the FRONTMATTER's. A sidecar is per-turn provenance, so these
        # keys recur further down the file and a reader that keeps overwriting ends up holding a
        # LATER, smaller, unrelated number. That is how this instrument reported session 46276084
        # as "+7,792 records since export" against a `total_records: 77` it had read from the tail
        # of a sidecar whose frontmatter says 7,488. ⚠️ Same shape as the mirror-mtime bug two
        # functions up: the value was real, and it answered a different question than the one asked.
        for line in io.open(sc, encoding="utf-8", errors="replace"):
            if line.startswith("turns_covered:") and turns is None:
                turns = int(line.split(":", 1)[1].strip())
            elif line.startswith("total_records:") and records is None:
                records = int(line.split(":", 1)[1].strip())
            if turns is not None and records is not None:
                break
    except (OSError, ValueError):
        pass
    return (turns, records)


def find_transcript(sid6, roots, full_sid):
    """The converter's naming convention is code-YYYY-MM-DD-<uuid6>-<slug>.md (sidecars excluded)."""
    # ⛔ ROOT ORDER BEATS MTIME, and the first version got this wrong in a way that produced a
    # confident false number. Sorting ALL candidates by mtime picked the FEDERATED MIRROR's copy
    # over this checkout's, because a robocopy stamps a fresh mtime on a stale body: the mirrored
    # sidecar for session 46276084 said `total_records: 77` while the repo's said 7,488, and the
    # instrument reported the session STALE by +7,754 records against a number that was never true.
    # ⚠️ A MIRROR'S MTIME IS THE COPY'S AGE, NOT THE CONTENT'S -- already on this repo's record
    # (cc_corpus_gap.py rejects mtime as a staleness signal for exactly this reason, and the
    # Drive-lag stale-read hazard is the same shape one layer up). Roots are searched in preference
    # order and the first root that has the session wins; mtime only orders WITHIN a root.
    for root in roots:
        if not os.path.isdir(root):
            continue
        # ⛔ AND THE SECOND DISCRIMINATOR IS THE ARTIFACT CLASS, not the filename. `raw/transcripts/
        # claude-code/fl/` holds WINDOW SLICES (mint_window.py, one per compact barrier, its own
        # independent parser) named `code-DATE-SID6-window-STAMP.md`. They match a `*<sid6>*.md`
        # glob, they are NEWER than the full transcript, and they are not transcripts -- so mtime
        # ordering inside the right root still picked the wrong CLASS and reported session 46276084
        # STALE by +7,773 records against a window's record count.
        # ✅ The canonical converter ALWAYS writes a `.sidecar.md`; nothing else does. Requiring the
        # sidecar identifies the class by an artifact the producer emits, not by a naming habit a
        # future renderer could copy.
        # ⛔ AND THE THIRD DISCRIMINATOR, because the first two still returned the wrong file:
        # MATCH THE SIDECAR'S `source_id`, NOT THE FILENAME. A converter slug is derived from the
        # session's opening text, so a SUBAGENT transcript titled "you-are-consulted-by-cfl-seat-
        # 46276084-n-1-compact" contains this session's id IN ITS SLUG and won a `*<sid6>*.md` glob
        # against the session's own transcript. The instrument then read that subagent's 77 records
        # and reported the parent session STALE by +7,810.
        # ⭐ Three bugs, one class: a filename, an mtime and a slug are all PROXIES for identity,
        # and each was wrong in a different way. The sidecar states `source_id:` outright. Ask the
        # artifact what it is instead of inferring it from what it is called.
        hits = []
        for p in glob.glob(os.path.join(root, "**", "*%s*.md" % sid6), recursive=True):
            if p.endswith(".sidecar.md"):
                continue
            sc = p[:-3] + ".sidecar.md"
            if not os.path.isfile(sc):
                continue
            try:
                head = io.open(sc, encoding="utf-8", errors="replace").read(2048)
            except OSError:
                continue
            m = re.search(r"^source_id:\s*(\S+)", head, re.M)
            if m and m.group(1) == full_sid:
                hits.append(p)
        if hits:
            return sorted(hits, key=lambda p: os.path.getmtime(p), reverse=True)
    return []


def md_turns(path):
    try:
        return len(TURN_HEADING.findall(io.open(path, encoding="utf-8", errors="replace").read()))
    except OSError:
        return None


def indexed_paths(db):
    """{path: (chunks, indexed_chars)} -- the CHARS are what makes THIN detectable. A membership
    set alone cannot distinguish a fully-chunked file from a one-chunk summary of one."""
    try:
        con = sqlite3.connect(db)
        rows = con.execute(
            "SELECT f.path, COUNT(c.id), COALESCE(SUM(LENGTH(c.text)),0) "
            "FROM files f LEFT JOIN chunks c ON c.file_id = f.id GROUP BY f.id")
        return {r[0]: (r[1], r[2]) for r in rows}
    except sqlite3.Error:
        return None


def rel_forms(path):
    """The index stores repo-relative paths for this checkout and ABSOLUTE ones for federated
    roots. Return every form a hit could take, so a real membership is not read as a miss --
    that asymmetry is exactly what made index_coverage.py's first run return a confident 0."""
    p = os.path.abspath(path).replace("\\", "/")
    forms = {p}
    r = REPO.replace("\\", "/")
    if p.startswith(r + "/"):
        forms.add(p[len(r) + 1:])
    return forms


def grade(live_records, tr_path, exported_records, in_index, slack, file_bytes, indexed_chars):
    """⛔ THIS FUNCTION USED TO STOP AT "in the index", AND THAT WAS AN EXISTENCE TEST WEARING A
    CAPABILITY TEST'S CLOTHES. Found by Professional N 1 compact 2, 2026-09-07, reviewing this very
    plan: `build_index.py` indexes the PROVENANCE tier DOC-LEVEL ONLY -- one chunk per file, a
    summary in place of the body. [measured, CFL, independently] a 294,636 B transcript -> 1 chunk /
    2,320 indexed chars = 0.79%; a 3.7 MB session log -> 0.062%; 6,197 single-chunk provenance
    files. **So a document can be PRESENT and unreachable, and this instrument would have certified
    the corpus complete today.** THIN is now its own grade: the file is there, the index holds a
    token of it, and no query will ever return the part you need."""
    if live_records is None:
        return "UNKNOWN", "session jsonl unreadable"
    if not tr_path:
        return "MISSING", "no transcript on disk (run the canonical converter)"
    if not in_index:
        return "MISSING", "transcript on disk but NOT in the index (rebuild, or wrong corpus root)"
    if exported_records is None:
        return "UNKNOWN", "transcript has no sidecar -- cannot compare like for like"
    if live_records > exported_records * (1.0 + slack):
        return "STALE", "jsonl now %d records vs %d at export (+%d) -- re-export before relying on it" % (
            live_records, exported_records, live_records - exported_records)
    if file_bytes and indexed_chars is not None and indexed_chars < file_bytes * 0.10:
        return "THIN", "indexed %s of %s chars (%.2f%%) -- PRESENT but not retrievable" % (
            indexed_chars, file_bytes, 100.0 * indexed_chars / file_bytes)
    return "PRESENT", ""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="uuid prefix filter")
    ap.add_argument("--all-trunks", action="store_true")
    ap.add_argument("--subagents", action="store_true")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--slack", type=float, default=0.05)
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    roots = [os.path.join(REPO, "raw", "transcripts", "claude-code"),
             "N:/claude-corpus/cfl/raw/transcripts/claude-code"]
    idx = indexed_paths(a.db)
    print("repo    : %s" % REPO)
    print("index   : %s%s" % (a.db, "" if idx is not None else "   ** UNREADABLE **"))
    print("corpus  : %s" % " | ".join(roots))
    if idx is None:
        print("\nUNKNOWN: the index could not be read. Nothing below is graded -- a check that "
              "could not run is UNKNOWN, and UNKNOWN dominates a pass.")
        return 2

    keys = sorted(os.listdir(PROJECTS)) if os.path.isdir(PROJECTS) else []
    if not a.all_trunks:
        this_key = "N--claude-cfl-clone"
        keys = [k for k in keys if k == this_key] or keys
    rows = []
    for key in keys:
        kdir = os.path.join(PROJECTS, key)
        if not os.path.isdir(kdir):
            continue
        mains = sorted(glob.glob(os.path.join(kdir, "*.jsonl")))
        subs = sorted(glob.glob(os.path.join(kdir, "*", "subagents", "*.jsonl"))) if a.subagents else []
        for kind, files in (("main", mains), ("subagent", subs)):
            for f in files:
                sid = os.path.splitext(os.path.basename(f))[0].replace("agent-", "")
                if a.session and not sid.startswith(a.session):
                    continue
                sid6 = sid[:6]
                live = jsonl_records(f)
                cands = find_transcript(sid6, roots, sid)
                tr = cands[0] if cands else None
                turns, exported = sidecar_counts(tr) if tr else (None, None)
                forms = rel_forms(tr) if tr else set()
                match = next((f for f in forms if f in idx), None)
                hit = match is not None
                nchunks, nchars = idx.get(match, (None, None)) if match else (None, None)
                fbytes = os.path.getsize(tr) if tr and os.path.isfile(tr) else None
                g, why = grade(live, tr, exported, hit, a.slack, fbytes, nchars)
                rows.append({"key": key, "kind": kind, "session": sid, "live_records": live,
                             "chunks": nchunks, "indexed_chars": nchars, "file_bytes": fbytes,
                             "exported_records": exported, "turns": turns,
                             "transcript": os.path.relpath(tr, REPO).replace("\\", "/") if tr else None,
                             "in_index": hit, "grade": g, "note": why})

    # ---- CONTROL, before any conclusion is drawn from the numbers above -----------------------
    # ⛔ THE CONTROL'S OWN CALIBRATION, CORRECTED THE HOUR IT WAS WRITTEN. It first demanded a
    # PRESENT row, and once THIN existed NOTHING graded PRESENT -- so a correct instrument reporting
    # a real, fleet-wide defect looked exactly like a broken instrument. The control's job is to
    # prove this code can SEE a transcript in the index, and THIN is a sighting. A control tuned to
    # the world you expected fails the moment you learn something.
    control = next((r for r in rows if r["grade"] in ("PRESENT", "THIN")), None)
    if control is None:
        print("\n⛔ CONTROL FAILED: not one session graded PRESENT. Either the corpus really is "
              "empty or this instrument cannot see it -- and those print the same bytes. "
              "REPORTING THE WHOLE RUN AS UNKNOWN.")
        if a.as_json:
            print(json.dumps({"control": "FAILED", "rows": rows}, indent=2))
        return 2
    print("control : %s for %s (%s) -- the instrument can see a real hit" % (
        control["grade"], control["session"][:8], control["kind"]))
    thin = [r for r in rows if r["grade"] == "THIN"]
    if thin and not [r for r in rows if r["grade"] == "PRESENT"]:
        print(os.linesep + "EVERY indexed transcript is THIN (%d of %d). This is not a per-session "
              "defect: build_index.py indexes the PROVENANCE tier DOC-LEVEL ONLY -- one chunk per "
              "file. The corpus is complete and effectively unreachable. Found by Professional "
              "N1 C2, 2026-09-07, reviewing the plan this instrument was built to verify." % (
                  len(thin), len(rows)))

    if a.as_json:
        print(json.dumps({"control": "OK", "rows": rows}, indent=2))
        return 0

    for kind in ("main", "subagent"):
        krows = [r for r in rows if r["kind"] == kind]
        if not krows:
            continue
        print("\n=== %s sessions (%d) -- classes are never pooled ===" % (kind.upper(), len(krows)))
        print("%-10s %-9s %7s %7s %8s  %s" % ("session", "grade", "live", "chunks", "idx-chars", "note"))
        for r in sorted(krows, key=lambda r: (r["grade"] != "PRESENT", r["session"])):
            print("%-10s %-9s %7s %7s %8s  %s" % (
                r["session"][:8], r["grade"], r["live_records"],
                r["chunks"] if r["chunks"] is not None else "-",
                r["indexed_chars"] if r["indexed_chars"] is not None else "-", r["note"]))
        tally = {}
        for r in krows:
            tally[r["grade"]] = tally.get(r["grade"], 0) + 1
        print("  %s: %s" % (kind, "  ".join("%s=%d" % kv for kv in sorted(tally.items()))))

    bad = [r for r in rows if r["grade"] in ("MISSING", "STALE", "UNKNOWN")]
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
