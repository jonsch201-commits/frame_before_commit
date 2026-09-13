#!/usr/bin/env python3
"""project_dirs.py -- the ~/.claude/projects key for THIS tree, DERIVED from its path, never typed.

PORTED FROM CLAUDE PROFESSIONAL, 2026-09-12, and the attribution is load-bearing: the design is
theirs (`N:\\claude-professional\\scripts\\project_dirs.py`, R4 of their 2026-09-04 restart gate).
CFL did not invent this and should not appear to. What is CFL's here is the LEGACY_KEYS list, which
was enumerated by `ls` rather than recalled, and the memory-store note below.

WHY CFL NEEDED IT, measured 2026-09-12 10:2x-10:4x:
  `scripts/audit/session_store_capture.py` held `CFL_PROJECT_PREFIXES = ("G--My-Drive-...",)` -- a
  hardcoded tuple written when CFL lived on G:. CFL moved to N:\\claude-cfl\\clone on 2026-09-02 and
  the tuple did not move with it, so the CURRENT store -- including its 86-file `memory/` -- was
  captured ZERO times for ten days while the PreCompact hook printed
  `files seen 2271 | copied 0 | skipped-unchanged 2271` on every run. A printed success over a store
  nobody was looking at.
  The first fix was to add "N--claude-cfl" to the tuple. That fix is CORRECT TODAY AND WRONG THE NEXT
  TIME A TRUNK MOVES -- the identical shape as the line it replaced, one revision fresher. This module
  exists so the key is never typed again.

Professional's own docstring counted the blast radius across the fleet: 7 hardcoded scripts in their
tree, 8 in Secretary, 37 in Personal, 9 in Antigravity. `[relayed from their file, not re-measured
here -- CFL measured only Antigravity's live instance, `drain_cfl_backlog.py:23`.]`

DERIVATION: every character that is not [A-Za-z0-9] in the absolute Windows path becomes '-'.
  N:\\claude-cfl\\clone -> N--claude-cfl-clone

⛔ LEGACY IS KEPT, NEVER REPLACED. Jon: "Yeah no deletion. And no writing PII to Github." /
"All must be recoverable." The G: dirs hold 83 session JSONLs and 97 memory files that exist nowhere
else. A reader that wants EVERY session of this tree must iterate ALL dirs from the default mode.

⚠️ CFL'S MEMORY STORE IS SPLIT ACROSS THREE KEYS and this is the [[cfl-memory-store-split-by-cwd]]
memory made mechanical: `N--claude-cfl-clone` (86 files, CURRENT),
`G--My-Drive-...-claude-foundational-layer` (76), `G--My-Drive-Claude-Claude-Foundational-Layer` (21).
Totals measured 2026-09-12 by `ls`. A memory reader that takes only the derived key sees 86 of 183.

Usage:
  python scripts/audit/project_dirs.py             # every EXISTING project dir for this tree, derived first
  python scripts/audit/project_dirs.py --primary   # the one to write/read first
  python scripts/audit/project_dirs.py --key       # the derived key only (no filesystem check)
  python scripts/audit/project_dirs.py --with-memory   # only dirs that contain a memory/ subdir
  python scripts/audit/project_dirs.py --root X    # derive for another tree
  python scripts/audit/project_dirs.py --selftest
"""
import os
import re
import sys

# ⛔ THREE dirnames, not two, and getting this wrong is how this file failed its OWN first run.
# Professional's copy lives at `scripts/project_dirs.py` so two levels up is its repo root. THIS copy
# lives at `scripts/audit/project_dirs.py`, one level deeper. Ported with two levels, ROOT resolved to
# `N:\claude-cfl\clone\scripts`, the derived key became `N--claude-cfl-clone-scripts`, no such project
# dir exists -- and the LIVE store `N--claude-cfl-clone` (12 jsonl, 86 memory) was ABSENT from the
# module's own output while its selftest printed PASS on all 8 checks.
# ⭐ The same defect class the module was written to kill, inside the module, certified by its own test.
# The guard that now catches it is `derived_key_resolves_to_the_live_store` in selftest().
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")

# Enumerated 2026-09-12 by `ls ~/.claude/projects | grep -iE "foundational|claude-cfl"`, NOT recalled.
# Add a row when this tree moves; never remove one.
LEGACY_KEYS = [
    "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer",                        # G: home, 83 jsonl, 76 memory
    "G--My-Drive-Claude-Claude-Foundational-Layer",                                                  # parent Drive folder, 0 jsonl, 21 memory (stale store)
    "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer--claude-worktrees-fable-substrate",
    "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer--claude-worktrees-wiki-su-2026-07-07",
    "N--claude-cfl",                                                                                 # sibling checkout, 1 jsonl
]


def derive_key(root):
    p = os.path.abspath(root).replace("/", "\\")
    return re.sub(r"[^A-Za-z0-9]", "-", p)


def candidate_keys(root):
    k = derive_key(root)
    return [k] + [x for x in LEGACY_KEYS if x != k]


def existing_dirs(root):
    return [os.path.join(PROJECTS, k) for k in candidate_keys(root)
            if os.path.isdir(os.path.join(PROJECTS, k))]


def dirs_with_memory(root):
    return [d for d in existing_dirs(root) if os.path.isdir(os.path.join(d, "memory"))]


def selftest():
    fails = 0

    def chk(label, got, want):
        nonlocal fails
        ok = got == want
        print(("PASS" if ok else "FAIL"), label, "->", got)
        fails += not ok

    chk("derive N: home", derive_key(r"N:\claude-cfl\clone"), "N--claude-cfl-clone")
    chk("forward slashes normalised", derive_key("N:/claude-cfl/clone"), "N--claude-cfl-clone")
    chk("derive G: home", derive_key(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer"),
        "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer")

    ks = candidate_keys(r"N:\claude-cfl\clone")
    ok = ks[0] == "N--claude-cfl-clone" and LEGACY_KEYS[0] in ks
    print(("PASS" if ok else "FAIL"), "candidates: derived first, legacy kept ->", len(ks), "keys"); fails += not ok

    # ⛔ THE GUARD THAT MATTERS, and the weak version of it certified a broken module.
    # The weak version asserted `derive_key(ROOT) in candidate_keys(ROOT)`. That is TRUE BY
    # CONSTRUCTION -- candidate_keys() prepends derive_key() -- so it passes for every possible
    # value of ROOT, including the wrong one. It printed PASS while the live store was missing
    # from the module's output.
    # ⭐ A guard whose assertion cannot fail is not a guard. This one hits the disk.
    live_key = derive_key(ROOT)
    live_dir = os.path.join(PROJECTS, live_key)
    ok = os.path.isdir(live_dir)
    print(("PASS" if ok else "FAIL"),
          "derived_key_resolves_to_the_live_store -> %s %s" % (live_key, "exists" if ok else "DOES NOT EXIST"))
    fails += not ok
    ok2 = ok and live_dir in existing_dirs(ROOT)
    print(("PASS" if ok2 else "FAIL"), "and the live store is IN this module's own output"); fails += not ok2

    ks = candidate_keys(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer")
    ok = ks.count(LEGACY_KEYS[0]) == 1
    print(("PASS" if ok else "FAIL"), "no duplicate when derived == legacy"); fails += not ok

    live = existing_dirs(ROOT)
    ok = len(live) >= 1
    print(("PASS" if ok else "FAIL"), "this tree resolves to >=1 existing dir ->", len(live)); fails += not ok

    mem = dirs_with_memory(ROOT)
    ok = len(mem) >= 2
    print(("PASS" if ok else "FAIL"),
          "memory store is SPLIT -- expect >=2 dirs with memory/ ->", len(mem)); fails += not ok

    print("SELFTEST", "PASS" if not fails else "FAIL", "%d failure(s)" % fails)
    return 1 if fails else 0


def main(argv):
    try:
        sys.stdout.reconfigure(newline="\n")  # Windows python emits CRLF through a pipe; a CR inside a bash glob matches nothing
    except Exception:
        pass
    root = ROOT
    if "--root" in argv:
        root = argv[argv.index("--root") + 1]
    if "--selftest" in argv:
        return selftest()
    if "--key" in argv:
        print(derive_key(root))
        return 0
    dirs = dirs_with_memory(root) if "--with-memory" in argv else existing_dirs(root)
    if not dirs:
        print("UNKNOWN: no project dir exists for %s (keys tried: %s)" % (root, candidate_keys(root)),
              file=sys.stderr)
        return 2
    if "--primary" in argv:
        print(dirs[0].replace("\\", "/"))
        return 0
    for d in dirs:
        print(d.replace("\\", "/"))  # forward slashes: a backslash path is an ESCAPE SEQUENCE to a bash glob
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
