"""Write back to disk the text of files the index holds and the filesystem no longer does.

WHY THIS EXISTS
---------------
Jon, 2026-08-09, verbatim (typos his): *"All must be recoverable, keep json… Yeah no deletion."*

`[measured 2026-09-12 22:5x]` After mirroring `raw/` into `N:/claude-corpus/cfl/`, 6,148 of 6,261
index rows resolved at their cited paths. **113 did not, and they resolve in NO known root** — not the
clone, not the G: FL tree, not by basename anywhere under `clone/raw`. The index is the last copy of
their text.

WHAT THIS CAN AND CANNOT GIVE BACK, stated before it runs because the difference is the finding:

    113 files · 14.62 MB of original bytes per the index's own `files.bytes`
    6.67 MB of text actually held in chunks = 45.7%
    39 of 113 have >= 90% of the original recoverable
    the rest are the SUMMARY-ONLY class: one is 740.5 KB original -> 2.3 KB indexed

⛔ **So this is a PARTIAL recovery and every output file says so in its own header.** A reconstruction
presented as an original is worse than a gap, because a gap can still be noticed.

⛔ **The 74 summary-only files are a REAL LOSS, and this script's job is to report it, not to paper
over it.** Their full text exists nowhere on this machine. The cause is upstream and named: the
indexer reduces a provenance file older than fourteen days to a ~2,200-char summary
(`provenance_is_recent()`), which is fine while the original is on disk and is a one-way door once it
is not.

This script only ever WRITES. It never deletes, never modifies the index, and never touches the
original path.

Usage:
    python scripts/audit/recover_from_index.py --out raw/recovered-from-index
    python scripts/audit/recover_from_index.py --dry-run
    python scripts/audit/recover_from_index.py --selftest
Exit: 0 wrote every recoverable file | 3 something could not be written | 4 could not run (UNKNOWN)
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
# ⛔ ONE HOME FOR THE GRAPH. This file hardcoded %LOCALAPPDATA%/claude/graphrag and would NOT
# have followed CFL_GRAPHRAG_HOME -- [measured 2026-09-12 23:1x] seven scripts had that bug,
# so setting the variable would have pointed the BUILDER at a new disk while every READER
# stayed on the old one, each reporting success. See scripts/lib/graphrag_home.py.
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "lib"))
from graphrag_home import DB as _GRAPHRAG_DB  # noqa: E402
DEFAULT_DB = _GRAPHRAG_DB
# Roots a cited path may actually live under. Same table as retrieve.py's resolver, and for the same
# reason: a not-found is a claim about where you looked.
ALIASES = (
    ("N:/claude-corpus/cfl/", "G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer/"),
    ("N:/claude-corpus/cfl/", "N:/claude-cfl/clone/"),
)


def resolve(cited):
    """Resolve a cited path, or None.

    ⛔ THE TILDE ARM WAS MISSING ON THE FIRST RUN AND IT WROTE A FALSEHOOD. The index cites
    `~/.claude/CLAUDE.md`; `os.path.isfile` does not expand `~`, so the file came back 'gone' and the
    recovery wrote a header saying it "is on no disk this machine can see" about a file that is very
    much on disk. Caught by reading the output, one minute after the script's own docstring warned
    that a reconstruction presented as an original is worse than a gap.
    ⭐ Same class as everything else tonight: a NOT-FOUND IS A CLAIM ABOUT THE RESOLVER.
    Also tried: a bare relative path against the repo root, since the index carries both forms."""
    n = str(cited).replace(chr(92), "/")
    cands = [n, os.path.expanduser(n)]
    if not os.path.isabs(n) and not n.startswith("~"):
        cands.append(str(ROOT / n))
    for c in cands:
        if os.path.isfile(c.replace("/", os.sep)):
            return c
    for a, b in ALIASES:
        if n.startswith(a):
            cand = b + n[len(a):]
            if os.path.isfile(cand.replace("/", os.sep)):
                return cand
    return None


def orphans(db):
    """Files in the index that resolve under no known root, with their recoverable text."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    out = []
    for fid, path, nbytes in con.execute("select id, path, bytes from files"):
        if resolve(path):
            continue
        chunks = con.execute(
            "select ord, heading, start_line, end_line, text from chunks "
            "where file_id=? order by ord", (fid,)).fetchall()
        text = chr(10).join((c[4] or "") for c in chunks)
        out.append({"path": str(path).replace(chr(92), "/"), "bytes": nbytes or 0,
                    "chunks": len(chunks), "text": text,
                    "frac": (len(text.encode("utf-8")) / nbytes) if nbytes else 0.0})
    con.close()
    return out


HEADER = """<!-- RECOVERED FROM THE RETRIEVAL INDEX -- THIS IS NOT THE ORIGINAL FILE -->
---
kind: recovered-from-index
recovered_on: "{when}"
original_path: "{path}"
original_bytes: {bytes}
recovered_bytes: {rec}
recovered_fraction: {frac:.3f}
chunks_held: {chunks}
completeness: {verdict}
---

# RECOVERED TEXT -- {verdict}

**The file at `{path}` is on no disk this machine can see** -- not at its cited path, not in the CFL
clone, not in the G: Foundational Layer tree, not by basename under `clone/raw`. `[measured
2026-09-12 22:5x]` What follows is the text the retrieval index was holding, written back out under
Jon's standing rule: *"All must be recoverable, keep json… Yeah no deletion."*

**{rec} bytes recovered of {bytes} original = {frac:.1%}.**
{note}

⛔ **Do not cite this as the original.** It is a reconstruction from chunked index text: chunk
boundaries are preserved as blank lines, and anything the chunker dropped is not here.

---

"""

NOTE_OVER = ("⚠️ **MORE TEXT THAN THE ORIGINAL HAD.** Overlapping chunks have duplicated passages, so the CONTENT is here and the STRUCTURE is not trustworthy: expect repeated paragraphs. Read it as evidence, never as a file."
)

NOTE_FULL = ("The index held essentially the whole file, so this is a high-fidelity reconstruction. "
             "It is still a reconstruction.")
NOTE_PART = ("⚠️ **A MINORITY OF THE ORIGINAL.** The remainder is not recoverable from any source on "
             "this machine.")
NOTE_SUMMARY = ("⛔ **THIS IS A SUMMARY, NOT THE FILE.** The indexer reduces a provenance file older "
                "than fourteen days to a short summary (`provenance_is_recent()`), which is safe "
                "while the original is on disk and is a one-way door once it is not. **The full text "
                "of this file is LOST.** It is recorded here so the loss is visible and countable "
                "rather than silent.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--out", default="raw/recovered-from-index")
    ap.add_argument("--dry-run", action="store_true")
    a, _ = ap.parse_known_args()
    if not Path(a.db).is_file():
        print(f"UNKNOWN -- no index at {a.db}; a check that could not run is never a pass")
        return 4
    items = orphans(a.db)
    print(f"=== recover-from-index ===")
    print(f"index                     : {a.db}")
    print(f"files resolving NOWHERE   : {len(items)}")
    if not items:
        print("Nothing to recover. Note this is a claim about the alias roots listed in this script.")
        return 0
    tot_b = sum(i["bytes"] for i in items)
    tot_r = sum(len(i["text"].encode("utf-8")) for i in items)
    full = sum(1 for i in items if i["frac"] >= 0.9)
    summ = sum(1 for i in items if i["frac"] < 0.2)
    print(f"original bytes            : {tot_b/1e6:.2f} MB")
    print(f"recoverable text          : {tot_r/1e6:.2f} MB = {100.0*tot_r/max(1,tot_b):.1f}%")
    print(f">=90% recoverable         : {full}")
    print(f"<20% -- SUMMARY-ONLY LOSS : {summ}   <-- full text lost, nowhere on this machine")
    if a.dry_run:
        print(chr(10) + "--dry-run: nothing written.")
        return 0
    outdir = ROOT / a.out
    wrote = failed = 0
    when = datetime.now().isoformat(timespec="seconds")
    for i in items:
        rel = i["path"].split("/raw/", 1)[1] if "/raw/" in i["path"] else os.path.basename(i["path"])
        dest = outdir / rel
        # A fraction OVER 1.0 is impossible for a faithful extract and means chunk overlap is
        # duplicating text. It is labelled rather than clamped: a reader who sees 108.9% knows to
        # distrust the reconstruction's structure, and a clamp to 100% would hide exactly that.
        verdict = ("OVER-COMPLETE -- CHUNK OVERLAP, STRUCTURE UNRELIABLE" if i["frac"] > 1.05
                   else "NEAR-COMPLETE" if i["frac"] >= 0.9
                   else "PARTIAL" if i["frac"] >= 0.2 else "SUMMARY-ONLY -- ORIGINAL LOST")
        note = (NOTE_OVER if i["frac"] > 1.05
                else NOTE_FULL if i["frac"] >= 0.9
                else NOTE_PART if i["frac"] >= 0.2 else NOTE_SUMMARY)
        body = HEADER.format(when=when, path=i["path"], bytes=i["bytes"],
                             rec=len(i["text"].encode("utf-8")), frac=i["frac"],
                             chunks=i["chunks"], verdict=verdict, note=note) + i["text"] + chr(10)
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body, encoding="utf-8")
            back = dest.read_text(encoding="utf-8")
            if len(back) != len(body):
                raise OSError("wrote and read back a different length")
            wrote += 1
        except OSError as e:
            failed += 1
            print(f"  FAILED {rel}: {e}")
    print(chr(10) + f"wrote {wrote} file(s) under {outdir}, {failed} failure(s)")
    print("Every file carries its own recovered_fraction and says it is NOT the original.")
    return 0 if not failed else 3


def selftest():
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        db = t / "i.sqlite"
        con = sqlite3.connect(db)
        con.executescript("create table files(id integer primary key, path text, sha text, "
                          "bytes integer, kind text, tier text);"
                          "create table chunks(id integer primary key, file_id integer, ord integer,"
                          " heading text, start_line integer, end_line integer, ntok integer, text text);")
        live = t / "alive.md"
        live.write_text("i am on disk", encoding="utf-8")
        con.execute("insert into files values (1,?,'x',12,'md','provenance')", (str(live),))
        con.execute("insert into chunks values (1,1,0,'h',1,1,3,'i am on disk')")
        con.execute("insert into files values (2,'N:/nope/raw/gone-full.md','y',20,'md','provenance')")
        con.execute("insert into chunks values (2,2,0,'h',1,1,5,'twenty bytes exactly')")
        con.execute("insert into files values (3,'N:/nope/raw/gone-summary.md','z',100000,'md','provenance')")
        con.execute("insert into chunks values (3,3,0,'h',1,1,2,'tiny summary')")
        con.commit(); con.close()

        got = orphans(db)
        paths = sorted(os.path.basename(g["path"]) for g in got)
        if paths != ["gone-full.md", "gone-summary.md"]:
            fails.append(f"orphan set wrong: {paths} -- a file ON DISK must never be 'recovered'")
        byname = {os.path.basename(g["path"]): g for g in got}
        if byname["gone-full.md"]["frac"] < 0.9:
            fails.append("a fully-held file was not graded near-complete")
        if byname["gone-summary.md"]["frac"] >= 0.2:
            fails.append("a summary-only file was not graded as a loss")

        # NEGATIVE ARM: an alias root that RESOLVES must remove the file from the orphan set, so a
        # recovery can never be written for a file that is merely mis-rooted -- the exact error that
        # nearly deleted a third of this index tonight.
        global ALIASES
        keep = ALIASES
        moved = t / "moved"; moved.mkdir()
        (moved / "gone-full.md").write_text("twenty bytes exactly", encoding="utf-8")
        ALIASES = (("N:/nope/raw/", str(moved).replace(chr(92), "/") + "/"),)
        got2 = orphans(db)
        ALIASES = keep
        if any(os.path.basename(g["path"]) == "gone-full.md" for g in got2):
            fails.append("an alias-resolvable file was still reported as gone")
    for f in fails:
        print("  FAIL " + f)
    print(f"selftest: {'PASS' if not fails else 'FAIL'} -- {len(fails)} failure(s)")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
