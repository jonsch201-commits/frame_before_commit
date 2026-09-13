#!/usr/bin/env python3
"""Derive a resident-safe COPY of the retrieval index, with the staging deny-list applied.

WHY THIS EXISTS
---------------
Jon, `[JON-LIVE:2026-08-23, verbatim]`:

    "these are library items, and they should trace back to their conversations in a vector embed
     graph rag context and **the residents need access to this key tool**."

Soul (Claude Personal, a1d6b7c8) raised the gap: the residents have `/skills` and a corpus and
**no way to ask either a question**. Their proposal was to add the index to `STAGE_PATHS` in
`stage_mounts.sh` and bind it read-only.

TWO THINGS SOUL COULD NOT MEASURE FROM THEIR OWN TREE, AND BOTH CHANGE THE BUILD
--------------------------------------------------------------------------------
1. `STAGE_PATHS` FEEDS `git archive`. The index is untracked and lives OFF the repo under
   `%LOCALAPPDATA%`. It can never arrive that way. The mechanism is a compose bind, not a stage row.

2. THE HAZARD, and the reason this file exists rather than a one-line bind.
   `[measured 2026-08-23 ~17:3x, this seat, read-only against the live index]`

       wiki/personal        0
       wiki/home            0
       wiki/pro             0
       self/                0
       wiki/intake-triage   486   <-- ON stage_mounts' DENY LIST

   The excluded TRUNKS are clean. But **486 intake-triage files sit in the index that
   `stage_mounts.sh` deliberately withholds from the resident's filesystem.** Binding the index as
   proposed would hand the resident, through a retrieval tool, exactly what the deny list exists to
   keep out. **A control that a second door walks around is not a control.**

WHY NOT FILTER AT QUERY TIME
----------------------------
`retrieve.py` already has scope/tier machinery, so `--scope` could exclude these. That is
**FAIL-OPEN BY CONSTRUCTION**: the resident holds the command line and `--all-tiers` reopens it.
SEC-113 fixed exactly this shape in that same file today, where a boolean tier gate would have
admitted any new tier silently, because a new tier arrives as a data change and not a code change.
**The deny must be enforced where the resident cannot reach it: in the bytes it is given.**

NO DELETION
-----------
This writes a NEW file and never touches the source. The index is itself a derived artifact,
rebuildable from the markdown on `G:` -- `build_index.py`'s own docstring: "The markdown on `G:` is
the record; this file is rebuildable from it." Removing rows from a copy of a derived artifact is
not deletion of a record. Stated explicitly because the no-deletion rule is absolute and deserves
an explicit disposition rather than silence.

Usage:
    python scripts/graphrag/derive_resident_index.py --out <path>
    python scripts/graphrag/derive_resident_index.py --selftest
"""
import argparse
import os
import shutil
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Mirrors DENY in scripts/lanes/stage_mounts.sh.
# TWO LISTS THAT MUST AGREE IS THE DERIVE-DONT-RECORD DEFECT, so --selftest READS the shell file
# and FAILS if they have diverged. A copied constant with no comparator is how this repo's
# characteristic failure starts.
DENY = ("wiki/personal", "wiki/home", "wiki/pro", "wiki/intake-triage", "exchange/su-close")
STAGE_SH = "scripts/lanes/stage_mounts.sh"


def default_src():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/AppData/Local")
    return os.path.join(base, "claude", "graphrag", "index.sqlite")


def deny_from_shell(path=STAGE_SH):
    """Read the AUTHORITATIVE deny list out of the shell script, rather than trusting our copy."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if line.startswith("DENY=("):
                    return tuple(line[len("DENY=("):].split(")")[0].split())
    except OSError:
        return None
    return None


def derive(src, out, verbose=True):
    if os.path.abspath(src) == os.path.abspath(out):
        raise ValueError("refusing to write over the source index")
    if os.path.exists(out):
        os.remove(out)   # a stale derived copy is worse than none: it reads as current
    shutil.copy2(src, out)

    c = sqlite3.connect(out)
    tables = {r[0] for r in c.execute(
        "select name from sqlite_master where type='table'")}
    before = c.execute("select count(*) from files").fetchone()[0]

    doomed = set()
    for d in DENY:
        for (fid,) in c.execute("select id from files where path like ?", (d + "%",)):
            doomed.add(fid)

    removed = {}
    if doomed:
        ids = tuple(doomed)
        q = ",".join("?" * len(ids))
        for tbl, col in (("chunks", "file_id"), ("docvecs", "file_id"),
                         ("edges", "src"), ("edges", "dst")):
            if tbl not in tables:
                continue
            try:
                cur = c.execute(
                    "delete from %s where %s in (%s)" % (tbl, col, q), ids)
                removed["%s.%s" % (tbl, col)] = cur.rowcount
            except sqlite3.OperationalError:
                pass   # column absent in this schema version; the assertion below still governs
        # vectors/postings key on chunk ids, which are now dangling.
        for tbl in ("vectors", "postings"):
            if tbl not in tables:
                continue
            try:
                cur = c.execute(
                    "delete from %s where chunk_id not in (select id from chunks)" % tbl)
                removed[tbl] = cur.rowcount
            except sqlite3.OperationalError:
                pass
        c.execute("delete from files where id in (%s)" % q, ids)

    # STALE META -- caught 2026-08-23 ~18:1x by retrieve_stdlib.py's case 5, on the FIRST derived
    # copy this script produced. `meta` is copied verbatim from the source, so the filtered index
    # was reporting n_files=5554 / n_chunks=32272 while actually holding 5068 / 13197.
    #
    # A DERIVED COPY THAT REPORTS ITS SOURCE'S COUNTS TELLS THE RESIDENT IT HOLDS MORE THAN IT
    # DOES -- and does it in the one table a reader consults precisely BECAUSE it does not want to
    # count for itself. That is the truth-sentence class landing inside the fix built to prevent a
    # leak, and it was invisible to this file's own assertion because the assertion checked PATHS
    # and never checked the SELF-DESCRIPTION.
    #
    # derived_from + derived_utc are added rather than overwritten: the copy must be able to say
    # what it came from, or the next reader cannot tell a filtered index from a small one.
    if "meta" in tables:
        c.execute("update meta set value=? where key='n_files'",
                  (str(c.execute("select count(*) from files").fetchone()[0]),))
        c.execute("update meta set value=? where key='n_chunks'",
                  (str(c.execute("select count(*) from chunks").fetchone()[0]),))
        for k, v in (("derived_from", os.path.basename(src)),
                     ("derived_deny", " ".join(DENY)),
                     ("derived_note", "FILTERED COPY -- resident-safe; not the full index")):
            c.execute("insert into meta(key,value) values(?,?) "
                      "on conflict(key) do update set value=excluded.value", (k, v))

    c.commit()
    c.execute("vacuum")
    c.commit()
    after = c.execute("select count(*) from files").fetchone()[0]

    # THE ASSERTION IS THE POINT. A deriver that trusted its own DELETE is the same defect as a
    # deny list applied and never verified -- which stage_mounts.sh already carries a hard check
    # for, in its own words, "because a deny list was once applied and never verified."
    leaks = []
    for d in DENY:
        n = c.execute("select count(*) from files where path like ?",
                      (d + "%",)).fetchone()[0]
        if n:
            leaks.append((d, n))
    c.close()

    if verbose:
        print("  source  : %s (%d files)" % (src, before))
        print("  derived : %s (%d files)" % (out, after))
        print("  removed : %d files" % (before - after))
        for k in sorted(removed):
            print("            %-18s %d rows" % (k, removed[k]))
    if leaks:
        raise AssertionError("DENIED PATHS SURVIVED: %r" % (leaks,))
    return before, after


def selftest():
    ok = True
    print("--- case 1: our DENY matches stage_mounts.sh's, READ FROM THE FILE ---")
    shell = deny_from_shell()
    if shell is None:
        print("    could not read DENY from %s  FAIL" % STAGE_SH)
        ok = False
    else:
        same = set(shell) == set(DENY)
        print("    shell: %r" % (shell,))
        print("    ours : %r" % (DENY,))
        print("    %s" % ("PASS" if same else "FAIL -- the two lists have DIVERGED"))
        ok = ok and same

    print("--- case 2: refuses to overwrite its own source ---")
    try:
        derive("x.sqlite", "x.sqlite", verbose=False)
        print("    no error raised  FAIL")
        ok = False
    except ValueError:
        print("    refused  PASS")
    except Exception as e:                                    # noqa: BLE001
        print("    wrong error: %s  FAIL" % e)
        ok = False

    print("--- case 3: a real derive leaves ZERO denied rows (the negative control) ---")
    src = default_src()
    if not os.path.exists(src):
        print("    source index absent -- UNKNOWN, and unknown does not pass")
        ok = False
    else:
        out = os.path.join(os.path.dirname(src), "index.resident.selftest.sqlite")
        try:
            b, a = derive(src, out, verbose=True)
            print("    assertion held, %d files removed  PASS" % (b - a))
        except AssertionError as e:
            print("    %s  FAIL" % e)
            ok = False
        finally:
            if os.path.exists(out):
                os.remove(out)

    print("\n" + ("SELFTEST PASS" if ok else "SELFTEST FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    src = a.src or default_src()
    out = a.out or os.path.join(os.path.dirname(src), "index.resident.sqlite")
    derive(src, out)
    print("\nderived. Bind READ-ONLY; never bind the source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
