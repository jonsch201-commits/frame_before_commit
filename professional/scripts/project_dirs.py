#!/usr/bin/env python3
"""project_dirs.py -- the ~/.claude/projects key for THIS tree, DERIVED from its path, never typed.

Why this exists (R4 of the 2026-09-04 restart gate): seven scripts in this tree hardcoded
`G--My-Drive-Claude-Claude-Professional-claude-professional`. Claude Code derives that key
from the session's cwd, so a session started from N:\\claude-professional writes its JSONL under
`N--claude-professional` and every hardcoded reader would look at the OLD key and see nothing --
a capture loss that fails silently (section 28.1 class). The Secretary counted 8 such scripts in
its tree, Personal 37, Antigravity 9.

Derivation, verified against the live key on 2026-09-04: every character that is not [A-Za-z0-9]
in the absolute Windows path becomes '-'. `G:\\My Drive\\Claude\\Claude Professional\\claude-professional`
-> `G--My-Drive-Claude-Claude-Professional-claude-professional`.

Usage:
  python scripts/project_dirs.py            # every EXISTING project dir for this tree, derived first
  python scripts/project_dirs.py --primary  # the one to write/read first (derived if it exists, else legacy)
  python scripts/project_dirs.py --key      # the derived key only (no filesystem check)
  python scripts/project_dirs.py --root X   # derive for another tree
  python scripts/project_dirs.py --selftest

Readers that want EVERY session of this tree (renderers, archivers, lineage) must iterate ALL
dirs printed by the default mode: after a drive move the old sessions stay under the old key.
LEGACY_KEYS is the list of keys this tree has ever lived under; add a row when the tree moves.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")
LEGACY_KEYS = [
    "G--My-Drive-Claude-Claude-Professional-claude-professional",   # G: home, 2026-08 -> 2026-09
    "N--claude-professional--claude-worktrees-prof-n3c0-pr4-frame",  # worktree seat 682d274b, 2026-09-11 -> 2026-09-12 (background-job launch, not Jon's intent; its JSONL and subagents live here)
]


def derive_key(root):
    p = os.path.abspath(root)
    p = p.replace("/", "\\")
    return re.sub(r"[^A-Za-z0-9]", "-", p)


def candidate_keys(root):
    k = derive_key(root)
    keys = [k] + [x for x in LEGACY_KEYS if x != k]
    return keys


def existing_dirs(root):
    return [os.path.join(PROJECTS, k) for k in candidate_keys(root)
            if os.path.isdir(os.path.join(PROJECTS, k))]


def selftest():
    fails = 0
    got = derive_key(r"G:\My Drive\Claude\Claude Professional\claude-professional")
    want = "G--My-Drive-Claude-Claude-Professional-claude-professional"
    print(("PASS" if got == want else "FAIL"), "derive G: home ->", got); fails += got != want
    got = derive_key(r"N:\claude-professional")
    want = "N--claude-professional"
    print(("PASS" if got == want else "FAIL"), "derive N: home ->", got); fails += got != want
    got = derive_key("N:/claude-professional")
    print(("PASS" if got == want else "FAIL"), "forward slashes normalised ->", got); fails += got != want
    ks = candidate_keys(r"N:\claude-professional")
    ok = ks[0] == "N--claude-professional" and LEGACY_KEYS[0] in ks
    print(("PASS" if ok else "FAIL"), "candidates: derived first, legacy kept ->", ks); fails += not ok
    ks = candidate_keys(r"G:\My Drive\Claude\Claude Professional\claude-professional")
    ok = ks.count(LEGACY_KEYS[0]) == 1
    print(("PASS" if ok else "FAIL"), "no duplicate when derived == legacy ->", ks); fails += not ok
    live = existing_dirs(ROOT)
    ok = len(live) >= 1
    print(("PASS" if ok else "FAIL"), "this tree resolves to >=1 existing dir ->", live); fails += not ok
    print("SELFTEST", "PASS" if not fails else "FAIL", "%d failure(s)" % fails)
    return 1 if fails else 0


def main(argv):
    sys.stdout.reconfigure(newline="\n")  # Windows python writes CRLF through a pipe; a CR inside a bash glob matches nothing (found 22:44, renderer scanned 0)
    root = ROOT
    if "--root" in argv:
        root = argv[argv.index("--root") + 1]
    if "--selftest" in argv:
        return selftest()
    if "--key" in argv:
        print(derive_key(root)); return 0
    dirs = existing_dirs(root)
    if "--primary" in argv:
        if not dirs:
            print("UNKNOWN: no project dir exists for %s (keys tried: %s)" % (root, candidate_keys(root)), file=sys.stderr)
            return 2
        print(dirs[0].replace("\\", "/")); return 0
    if not dirs:
        print("UNKNOWN: no project dir exists for %s (keys tried: %s)" % (root, candidate_keys(root)), file=sys.stderr)
        return 2
    for d in dirs:
        print(d.replace("\\", "/"))  # forward slashes: a backslash path is an ESCAPE SEQUENCE to a bash glob
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
