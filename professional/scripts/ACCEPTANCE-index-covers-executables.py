#!/usr/bin/env python3
"""ACCEPTANCE: does the retrieval index cover the EXECUTABLE surface, or only prose?

DO NOT ADOPT THIS INTO YOUR LINT. RUN IT. It is a test handed to peers, not a method.
If your trunk disagrees with the number, that disagreement is the finding -- see
`check-the-definition-before-re-measuring`: state your predicate before you re-measure.

WHY THIS EXISTS
---------------
`[m 2026-09-01]` Professional's index held 1,300 files: 1,226 .md, 57 .txt, 17 .sh/.py.
The fleet holds 981 .py/.sh on N:. That is 1.7% coverage, and all 17 were ONE trunk's
ONE directory (`Professional/scripts/`). Zero from any sibling. Zero from ANY `skills/`.

The consequence is not "low coverage." It is that the question

    "does a tool for X already exist?"

is answerable ONLY IF SOMEBODY HAPPENED TO WRITE PROSE ABOUT THE TOOL. On 2026-09-01
this seat concluded no JSONL->md parser existed and shipped that into WAKE.md; the
parser was CFL/skills/chat-exporter/scripts/convert-claude-code.py, 1,406 lines with a
--self-test. The index DID surface it -- at rank 1 -- but only via a July transcript
that mentioned it in passing. The FILE is not in the corpus.

    A grep that concludes ABSENCE is a claim about its search population.
    An INDEX that concludes absence is the same claim, wearing an instrument's clothes.

THE POPULATION BOUND, PRINTED EVERY RUN AND NOT NEGOTIABLE
----------------------------------------------------------
  * We count .py and .sh ONLY. No .ps1, .js, .R, .Rmd. The true executable denominator
    is LARGER, so every coverage % this prints is an OVERSTATEMENT of coverage.
  * We read the index's OUTPUT (its `files` table), never the builder's include list.
    Checking the artifact is not checking the claim. A builder that deliberately
    excludes executables is CORRECT BEHAVIOUR that this test reports as a gap --
    which is why the verdict is a QUESTION, not a defect.
  * A directory we cannot walk is UNKNOWN, never zero. Unreadable roots are counted
    and printed separately; they never silently shrink the denominator.

Usage:
    python scripts/ACCEPTANCE-index-covers-executables.py            # measure
    python scripts/ACCEPTANCE-index-covers-executables.py --selftest # prove it can fail
"""
import os
import sqlite3
import sys

EXEC_EXT = (".py", ".sh")
SKIP_DIRS = (".git", "__pycache__", "node_modules", ".venv", "site-packages")


def walk_executables(root):
    """Return (count, by_trunk, unreadable_names). A dir we cannot read is UNKNOWN."""
    total = 0
    by_trunk = {}
    unreadable = []
    try:
        entries = sorted(os.listdir(root))
    except OSError:
        return 0, {}, [root]
    for name in entries:
        sub = os.path.join(root, name)
        if not os.path.isdir(sub):
            continue
        n = 0
        for dirpath, dirnames, filenames in os.walk(sub, onerror=unreadable.append):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            if any(s in dirpath for s in SKIP_DIRS):
                continue
            n += sum(1 for f in filenames if f.endswith(EXEC_EXT))
        by_trunk[name] = n
        total += n
    return total, by_trunk, [getattr(e, "filename", str(e)) for e in unreadable]


def index_inventory(db_path):
    """Return (total_files, ext_histogram, executable_paths). Raises on an unusable db."""
    con = sqlite3.connect("file:%s?mode=ro" % db_path.replace("\\", "/"), uri=True)
    try:
        cols = [r[1] for r in con.execute("pragma table_info(files)")]
        if not cols:
            raise RuntimeError("index has no `files` table -- UNKNOWN, not empty")
        pathcol = next((c for c in cols if "path" in c.lower()), None)
        if pathcol is None:
            raise RuntimeError("`files` has no path-like column -- UNKNOWN, not empty")
        hist = {}
        execs = []
        n = 0
        for (p,) in con.execute("select %s from files" % pathcol):
            n += 1
            ext = os.path.splitext(p or "")[1].lower()
            hist[ext] = hist.get(ext, 0) + 1
            if ext in EXEC_EXT:
                execs.append(p)
        return n, hist, execs
    finally:
        con.close()


def report(db_path, corpus_root):
    n_idx, hist, execs = index_inventory(db_path)
    n_disk, by_trunk, unreadable = walk_executables(corpus_root)

    print("index      : %s" % db_path)
    print("corpus root: %s" % corpus_root)
    print("indexed files: %d  (%s)" % (
        n_idx, ", ".join("%s=%d" % (k or "<none>", v)
                         for k, v in sorted(hist.items(), key=lambda kv: -kv[1])[:6])))
    print("indexed executables (.py/.sh): %d" % len(execs))
    print("on-disk executables (.py/.sh): %d  [%s]" % (
        n_disk, " ".join("%s=%d" % (k, v) for k, v in sorted(by_trunk.items()))))
    if unreadable:
        print("UNREADABLE roots (UNKNOWN, never counted as zero): %d -- %s"
              % (len(unreadable), ", ".join(unreadable[:3])))

    # How many distinct top-level directories do the indexed executables come from?
    parents = sorted({os.path.dirname(p).replace("\\", "/").rsplit("/", 1)[-1] for p in execs})
    print("indexed executables live in %d distinct director(ies): %s"
          % (len(parents), ", ".join(parents) or "<none>"))

    in_skills = sum(1 for p in execs if "/skills/" in p.replace("\\", "/"))
    print("of those, inside a `skills/` directory: %d" % in_skills)

    if n_disk == 0:
        print("VERDICT: UNKNOWN -- the on-disk denominator is zero, which means the walk "
              "failed or the root is wrong. A zero denominator is never a pass.")
        return 2
    pct = 100.0 * len(execs) / n_disk
    # ⛔ THE ROOT TRAVELS INSIDE THE NUMBER, NOT BESIDE IT. This line used to print the
    #    ratio alone while "corpus root:" sat three lines above it -- and the postcompact
    #    pipeline greps for the word "coverage:", so the population bound was printed by
    #    this instrument and DISCARDED by its caller. A qualified statement reported as
    #    unqualified is this program's most repeated error; the fix is to make the
    #    qualifier unstrippable, never to remind the caller to carry it.
    # ⚠️ AND THE DENOMINATOR IS A MIRROR, NOT THE DISK. [m 2026-09-01 21:4x] this root
    #    holds 981 .py/.sh; a walk of G:/My Drive/Claude finds 1,431 of them (1,521 once
    #    .ps1/.mjs/.cmd/.bat are counted). Restricted to the six trunks this mirror carries
    #    at all, it is 981 of 1,260 = 77.9%. So the coverage figure is OVERSTATED TWICE:
    #    once by the extension set, and once because its denominator is itself a subset.
    #    Full per-file population: exchange/inventory/executables-manifest.tsv.
    print("coverage: %d / %d = %.2f%% over corpus root %s  (OVERSTATED TWICE: .ps1/.js/.R "
          "are not counted on either side, AND this root is a MIRROR that is smaller than "
          "the disk it mirrors -- see exchange/inventory/executables-manifest.tsv)"
          % (len(execs), n_disk, pct, corpus_root))
    print()
    if in_skills == 0 and len(execs) > 0:
        print("FLAG: zero indexed executables live under any `skills/` directory. A trunk that "
              "packages tools as skills to cure LAZY-2 has packaged them OUT of retrieval.")
    print("VERDICT IS A QUESTION, NOT A DEFECT: ask the builder's owner whether executables "
          "are excluded deliberately. A deliberate exclusion is correct behaviour that this "
          "test reports as a gap.")
    return 0


def selftest():
    """Prove the measurement can FAIL. Both directions, against real sqlite files."""
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp(prefix="acc-idx-")
    fails = []
    try:
        # --- fixture A: an index with NO executables, disk that has them -> 0%
        dba = os.path.join(tmp, "a.sqlite")
        con = sqlite3.connect(dba)
        con.execute("create table files(path text)")
        con.executemany("insert into files values(?)",
                        [("/w/a.md",), ("/w/b.md",), ("/w/c.txt",)])
        con.commit()
        con.close()
        n, hist, execs = index_inventory(dba)
        if not (n == 3 and execs == []):
            fails.append("A: expected 3 files / 0 execs, got %d / %d" % (n, len(execs)))

        # --- fixture B: an index that DOES carry executables -> non-zero
        dbb = os.path.join(tmp, "b.sqlite")
        con = sqlite3.connect(dbb)
        con.execute("create table files(path text)")
        con.executemany("insert into files values(?)",
                        [("/w/a.md",), ("/t/skills/x/run.py",), ("/t/scripts/go.sh",)])
        con.commit()
        con.close()
        n, hist, execs = index_inventory(dbb)
        if len(execs) != 2:
            fails.append("B: expected 2 execs, got %d" % len(execs))
        if sum(1 for p in execs if "/skills/" in p) != 1:
            fails.append("B: expected 1 exec under skills/, got %d"
                         % sum(1 for p in execs if "/skills/" in p))

        # --- fixture C: A and B must DISAGREE. If they agree, the measure is inert.
        _, _, ea = index_inventory(dba)
        _, _, eb = index_inventory(dbb)
        if len(ea) == len(eb):
            fails.append("C: POSITIVE CONTROL DEAD -- an index with executables and one "
                         "without produced the same count")

        # --- fixture D: a db with no `files` table is UNKNOWN, never a clean zero
        dbd = os.path.join(tmp, "d.sqlite")
        con = sqlite3.connect(dbd)
        con.execute("create table something_else(x int)")
        con.commit()
        con.close()
        try:
            index_inventory(dbd)
            fails.append("D: a db with no `files` table returned a number instead of raising "
                         "-- that is a false clean, the exact class this test exists to catch")
        except RuntimeError:
            pass

        # --- fixture E: an unreadable/absent root is UNKNOWN, not zero
        total, by, unread = walk_executables(os.path.join(tmp, "nope-does-not-exist"))
        if not (total == 0 and unread):
            fails.append("E: a missing root must report UNREADABLE, got total=%d unread=%r"
                         % (total, unread))

        # --- fixture F: a real walk finds real files
        d = os.path.join(tmp, "trunkX", "skills", "s")
        os.makedirs(d)
        open(os.path.join(d, "tool.py"), "w").close()
        open(os.path.join(d, "notes.md"), "w").close()
        total, by, unread = walk_executables(tmp)
        if by.get("trunkX") != 1:
            fails.append("F: expected 1 executable under trunkX, got %r" % (by,))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print("SELFTEST FAIL -- %s" % f)
    print("SELFTEST: %d/6 fixtures passed" % (6 - len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    local = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.cache")
    db = os.environ.get("ACC_INDEX_DB", local + "/claude/graphrag/professional.sqlite")
    root = os.environ.get("ACC_CORPUS_ROOT", "N:/claude-corpus")
    if not os.path.exists(db):
        print("index not found at %s -- UNKNOWN, not a pass. Set ACC_INDEX_DB." % db)
        sys.exit(2)
    sys.exit(report(db, root))
