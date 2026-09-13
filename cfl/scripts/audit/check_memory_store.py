#!/usr/bin/env python3
"""check_memory_store.py — say WHICH memory store this session loaded, and name every sibling.

⛔ WHY (ticket M-1, known since 2026-08-02 and unfixed until now). The memory store is keyed by the
LAUNCH DIRECTORY. Launching from the repo folder and launching from its parent give two DIFFERENT
stores, and **nothing at load time says which one you got.**

`[measured 2026-08-10]`
  …/G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer/memory  → 54 files, live
  …/G--My-Drive-Claude-Claude-Foundational-Layer/memory                            → 20 files,
      last written 2026-06-08, index still reads "Phase 3c running"

⭐ A session that loaded the second one would be reasoning from June while believing it holds
current state — and would have NO signal that anything was wrong. That is the same defect class as
wiki path-deixis: **identity-by-working-directory.**

⚠️ THIS TOOL NEVER DELETES OR MERGES. Jon's standing ruling is "Yeah no deletion", and merging two
memory stores is a judgment about which of two conflicting facts is true. It REPORTS, and the stale
store carries a marker written once, by hand, which this tool checks for rather than writes.

Usage:  python scripts/audit/check_memory_store.py [--cwd DIR] [--strict] [--self-test]
Exit:   0 one store / marked siblings, 1 an UNMARKED sibling exists (--strict), 2 no store at all.
"""
import argparse
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HOME = os.path.expanduser("~")
PROJECTS = os.path.join(HOME, ".claude", "projects")
MARKER = "SUPERSEDED-STORE"


def slug(path):
    """Claude Code's project-directory key: the absolute path with separators flattened."""
    # ⛔ EVERY non-alphanumeric character becomes one dash, and runs are NOT collapsed.
    # The first version replaced only path separators and left SPACES intact, producing
    # "G--My Drive-Claude-..." — which resolves to a directory that does not exist, so the tool
    # reported "NO STORE for this directory" while sitting inside the repo whose store has 54 files.
    # ⭐ Its own self-test caught it on the first run, which is the entire reason the self-test
    # asserts against the two REAL directory names rather than a fixture.
    # Runs must not collapse: "G:/My" needs to become "G--My" (drive colon AND separator), and a
    # collapsing rule would give "G-My".
    p = os.path.abspath(path).replace("\\", "/")
    return "".join(c if c.isalnum() else "-" for c in p)


def stores_for(cwd):
    """The store this cwd resolves to, plus every ANCESTOR/DESCENDANT store that also exists.

    ⭐ Siblings are found by walking the path UP, because that is exactly how the duplicate arose:
    the same project launched from a parent directory. A scan of all project dirs would also find
    unrelated projects and bury the one that matters.
    """
    mine = os.path.join(PROJECTS, slug(cwd), "memory")
    others, p = [], os.path.abspath(cwd)
    while True:
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
        cand = os.path.join(PROJECTS, slug(p), "memory")
        if os.path.isdir(cand) and os.path.abspath(cand) != os.path.abspath(mine):
            others.append(cand)
    return mine, others


def describe(d):
    files = [f for f in os.listdir(d) if f.endswith(".md")] if os.path.isdir(d) else []
    # ⛔ NEWEST **CONTENT** WRITE, EXCLUDING THE INDEX — and this is not a nicety. Writing the
    # superseded-store MARKER into MEMORY.md set that file's mtime to today, so the very act of
    # flagging a store as stale made it report "newest write 2026-08-10" and ERASED the staleness
    # signal the reader needs. Measured within a minute of adding the marker, 2026-08-10.
    # ⭐ The general form: a tool that annotates an artifact must not annotate the evidence.
    newest = 0
    for f in files:
        if f == "MEMORY.md":
            continue
        try:
            newest = max(newest, os.path.getmtime(os.path.join(d, f)))
        except OSError:
            pass
    idx = os.path.join(d, "MEMORY.md")
    marked = False
    if os.path.isfile(idx):
        try:
            marked = MARKER in open(idx, encoding="utf-8", errors="ignore").read(4000)
        except OSError:
            pass
    return len(files), newest, marked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    import datetime
    mine, others = stores_for(a.cwd)
    print("=== check_memory_store ===")
    print(f"  cwd            : {os.path.abspath(a.cwd)}")
    if not os.path.isdir(mine):
        print(f"  ⛔ NO STORE for this directory: {mine}")
        print("     A session launched here has NO memory, which is different from empty memory.")
        return 2
    n, t, _m = describe(mine)
    ts = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M") if t else "—"
    print(f"  LOADED STORE   : {mine}")
    print(f"                   {n} files, newest write {ts}")
    print()
    if not others:
        print("  ✅ no sibling store on any ancestor directory.")
        return 0
    unmarked = 0
    print(f"  ⚠️  {len(others)} SIBLING STORE(S) exist for ancestor directories of this cwd.")
    print("      Launching from there loads THESE memories instead, with no signal at load time.")
    for d in others:
        n2, t2, marked = describe(d)
        ts2 = datetime.datetime.fromtimestamp(t2).strftime("%Y-%m-%d %H:%M") if t2 else "—"
        tag = "MARKED superseded" if marked else "⛔ UNMARKED"
        if not marked:
            unmarked += 1
        print(f"      {tag}  {n2} files, newest {ts2}")
        print(f"        {d}")
    print()
    print("  ⛔ NOT MERGED AND NOT DELETED, deliberately. Jon: \"Yeah no deletion\" — and merging two")
    print("     stores is a judgment about which of two conflicting facts is true, not a file op.")
    print(f"     A sibling counts as handled when its MEMORY.md carries the word {MARKER}.")
    return 1 if (unmarked and a.strict) else 0


def self_test():
    import tempfile
    fails = []
    # slug() must reproduce the real directory name for the real repo path.
    got = slug("G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer")
    want = "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer"
    if got != want:
        fails.append(f"slug mismatch: {got!r} != {want!r}")
    # The parent path must produce the OTHER real store's name — this is the whole defect.
    got2 = slug("G:/My Drive/Claude/Claude Foundational Layer")
    if got2 != "G--My-Drive-Claude-Claude-Foundational-Layer":
        fails.append(f"parent slug mismatch: {got2!r}")
    # describe() must read the marker, and must NOT claim marked when it is absent.
    with tempfile.TemporaryDirectory() as td:
        open(os.path.join(td, "MEMORY.md"), "w", encoding="utf-8").write("# Memory Index\n")
        if describe(td)[2]:
            fails.append("an unmarked store was reported as marked")
        open(os.path.join(td, "MEMORY.md"), "w", encoding="utf-8").write(f"# {MARKER}\n")
        if not describe(td)[2]:
            fails.append("a marked store was reported as unmarked")
        if describe(td)[0] != 1:
            fails.append("file count wrong")
        # THE MARKER MUST NOT ERASE THE EVIDENCE. A fresh MEMORY.md beside an old content file must
        # still report the OLD time -- writing the superseded banner did exactly this in the real
        # store and reset its apparent age to today.
        import time
        cf = os.path.join(td, "old_fact.md")
        open(cf, "w", encoding="utf-8").write("x")
        os.utime(cf, (1_500_000_000, 1_500_000_000))
        if describe(td)[1] != 1_500_000_000:
            fails.append("newest-write used the index instead of content; marking a store hides its age")

    print("=== SELF-TEST — check_memory_store.py ===")
    if fails:
        for f in fails:
            print(f"  FAIL: {f}")
        print(f"\nRESULT: FAIL — {len(fails)} failure(s)")
        return 1
    checks = [
        "slug() reproduces the LIVE store's real directory name",
        "slug(parent) reproduces the STALE store's real directory name",
        "an unmarked store is not reported as marked",
        "a marked store is detected",
        "file counts are read, not assumed",
        "marking a store does NOT reset its reported age (index excluded)",
    ]
    for c in checks:
        print(f"  {c:<58}: PASS")
    print(f"\nRESULT: PASS — {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
