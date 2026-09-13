#!/usr/bin/env python3
"""Find DIRECTORIES and QUEUES with no writer, no reader, or no contents.

WHY THIS EXISTS, and it is a peer's finding run against this tree
----------------------------------------------------------------
Professional, 2026-08-23, after CFL's `HALT_WRITE_LANE` (one writer, zero readers) was split out
as its own class:

    "wiki/sources/ -- the directory for Jon's primary words, in the trunk whose job is his words --
     HELD ZERO FILES until today. A folder nobody writes to and nobody reads is your class at a
     scale no code audit will ever see."

    "Ask it of DIRECTORIES AND QUEUES, not only of flags. Ours was a folder, the Secretary's was a
     413-row file, and NEITHER would have appeared in a grep for variable names."

That last sentence is the whole design. `HALT_WRITE_LANE` was findable because it was a token in a
shell script. **A directory is not a token.** Nothing that greps for identifiers can see an empty
`wiki/sources/`, and nothing that counts files can see a full directory nobody reads.

THE THREE STATES THIS LOOKS FOR -- and they are NOT the same defect
------------------------------------------------------------------
  EMPTY      the container exists and holds nothing. Reads as "nothing to report."
             ⛔ Indistinguishable from an attended-and-quiet directory. Professional's case.
  UNREAD     it holds content and NO script, skill or doc names its path.
             ⛔ CFL's `HALT_WRITE_LANE` shape, at directory scale.
  UNWRITTEN  it is named by code but does not exist on disk.
             ⛔ The inverse, and the one that fails at 3am: a consumer pointed at nothing.

⚠️ NAMED != READ, AND THIS TOOL CANNOT TELL THE DIFFERENCE. A path appearing in a file proves only
that somebody TYPED it. It does not prove anything opens it. So UNREAD here is a STRONG signal
(nobody even mentions it) and "referenced" is a WEAK clearance (someone mentioned it once, possibly
in a comment saying it is broken). **The asymmetry is stated because reading it the other way round
would turn this instrument into the thing it is hunting.**

Usage:
    python scripts/audit/empty_and_unread.py
    python scripts/audit/empty_and_unread.py --selftest
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Roots whose CHILD directories are candidate containers. raw/ is excluded: it is the gitignored
# bulk corpus and its emptiness means something different.
ROOTS = ("wiki", "exchange", "skills", "scripts", "docker", "shelf", "self")
SKIP_DIR = {".git", "node_modules", "__pycache__", ".understand-anything", "bake-out",
            "raw", "live-store-capture"}
QUIET = ("wiki/personal", "wiki/home", "wiki/pro", "self")


def is_quiet(rel):
    r = rel.replace("\\", "/")
    return any(r == q or r.startswith(q + "/") for q in QUIET)


def walk_dirs(root):
    """Every directory under ROOTS, with its immediate file count and total file count."""
    out = {}
    for top in ROOTS:
        base = os.path.join(root, top)
        if not os.path.isdir(base):
            out[top] = None          # named as a root and absent -- itself a finding
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]
            rel = os.path.relpath(dirpath, root).replace("\\", "/")
            n_here = len([f for f in filenames if not f.startswith(".")])
            out[rel] = n_here
    return out


def corpus_text(root):
    """Every path-bearing text in the repo, concatenated once. Read ONCE, not per-directory:
    a per-directory grep over a Drive-hosted tree is minutes, and a check nobody will wait for
    is a check that does not get run."""
    buf = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]
        for fn in filenames:
            if not fn.endswith((".py", ".sh", ".md", ".yaml", ".yml", ".json", ".ps1", ".cmd")):
                continue
            try:
                with open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore") as fh:
                    buf.append(fh.read())
            except OSError:
                continue
    return "\n".join(buf)


def analyse(root):
    dirs = walk_dirs(root)
    text = corpus_text(root)
    empty, unread, missing = [], [], []
    for rel, n in sorted(dirs.items()):
        if n is None:
            missing.append(rel)
            continue
        # subtree total: a parent holding nothing directly but plenty below is NOT empty
        sub = sum(v for k, v in dirs.items()
                  if v is not None and (k == rel or k.startswith(rel + "/")))
        named = rel in text
        if sub == 0:
            empty.append((rel, named))
        elif not named:
            unread.append((rel, sub))
    return empty, unread, missing, len(dirs), len(text)


def report(root):
    empty, unread, missing, n_dirs, n_chars = analyse(root)
    print("=" * 74)
    print("MEASURED ROOT : %s" % root)
    print("                ^-- %s" % ("THIS SCRIPT'S OWN TRUNK" if os.path.abspath(root) == REPO
                                      else "A DIFFERENT TREE"))
    print("=" * 74)
    print("directories walked : %d   |  path-bearing text scanned: %d chars" % (n_dirs, n_chars))

    print("\n-- EMPTY (container exists, subtree holds nothing) --")
    print("   Professional's class. An empty directory reads as 'nothing to report'.")
    if not empty:
        print("   NONE. Every walked directory holds at least one file.")
    for rel, named in empty:
        tag = "NAMED in code/docs -- a consumer may be pointed at it" if named else "not named anywhere"
        print("   %-52s  %s%s" % (rel, tag, "   [EXCLUDED TRUNK - surface only]" if is_quiet(rel) else ""))

    print("\n-- UNREAD (holds files; its path is named NOWHERE in this tree) --")
    print("   CFL's HALT_WRITE_LANE shape at directory scale.")
    if not unread:
        print("   NONE.")
    for rel, n in unread:
        print("   %-52s  %4d file(s)%s" % (rel, n, "   [EXCLUDED TRUNK - surface only]" if is_quiet(rel) else ""))

    print("\n-- UNWRITTEN (named as a root here, absent on disk) --")
    print("   NONE." if not missing else "")
    for rel in missing:
        print("   %s" % rel)

    print("\nBOUNDS -- and the third part is the one that matters")
    print("  1. NOT REVIEWED: whether a NAMED path is ever actually OPENED. This greps for the")
    print("     string only.")
    print("  2. WHY: proving a read requires executing every consumer, which this cannot do.")
    print("  3. ⛔ RESULTING LIMITATION: 'named' is a WEAK clearance and 'not named' is a STRONG")
    print("     signal. A directory absent from this report is NOT cleared -- it was mentioned")
    print("     somewhere, possibly in a comment saying it is broken. Reading a quiet report as")
    print("     an all-clear would make this instrument the thing it is hunting.")


def selftest():
    ok = True
    print("--- case 1: a parent whose files live in children is NOT empty ---")
    d = {"a": 0, "a/b": 3}
    sub = sum(v for k, v in d.items() if k == "a" or k.startswith("a/"))
    good = sub == 3
    print("    subtree total for 'a' = %d (expect 3)  %s" % (sub, "PASS" if good else "FAIL"))
    ok = ok and good

    print("--- case 2: NEGATIVE CONTROL -- a genuinely empty subtree totals 0 ---")
    d2 = {"x": 0, "x/y": 0}
    sub2 = sum(v for k, v in d2.items() if k == "x" or k.startswith("x/"))
    good2 = sub2 == 0
    print("    subtree total for 'x' = %d (expect 0)  %s" % (sub2, "PASS" if good2 else "FAIL"))
    ok = ok and good2

    print("--- case 3: prefix matching does not treat 'wiki-personal' as inside 'wiki' ---")
    d3 = {"wiki": 0, "wiki-personal": 9}
    sub3 = sum(v for k, v in d3.items() if k == "wiki" or k.startswith("wiki/"))
    good3 = sub3 == 0
    print("    subtree total for 'wiki' = %d (expect 0, NOT 9)  %s" % (sub3, "PASS" if good3 else "FAIL"))
    ok = ok and good3

    print("--- case 4: the excluded-trunk marker fires on the trunks Jon fenced ---")
    good4 = is_quiet("wiki/personal/x") and is_quiet("self") and not is_quiet("wiki/concepts")
    print("    quiet(wiki/personal/x)=%s quiet(self)=%s quiet(wiki/concepts)=%s  %s"
          % (is_quiet("wiki/personal/x"), is_quiet("self"), is_quiet("wiki/concepts"),
             "PASS" if good4 else "FAIL"))
    ok = ok and good4

    print("\n" + ("SELFTEST PASS" if ok else "SELFTEST FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    report(os.path.abspath(a.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
