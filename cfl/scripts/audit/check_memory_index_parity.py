#!/usr/bin/env python3
"""Memory index-store parity check (Part 2c of the 2026-08-06 "poor memory" ticket).

WHY THIS EXISTS
----------------
MEMORY.md had 48 entries for 50 files (48 memory pages + itself counted differently
across two audits) on 2026-08-02 — two memory files existed on disk, correctly written,
and were invisible to every session because nothing linked them from the index a session
actually reads at cold-open (`~/.claude/CLAUDE.md` -> "## Skills Loaded" / auto-loaded
MEMORY.md). A fact written down that the index doesn't point at is functionally the same
as a fact never written down. This is a five-line check on purpose — Jon's own framing:
"a fact recorded in prose has no mechanism that can notice when reality moves"
([[derive-dont-record]]) applies to the index just as much as to any other spec.

WHAT IT CHECKS
--------------
1. Every `*.md` file in the memory directory (except MEMORY.md itself) is referenced by
   filename somewhere in MEMORY.md's own text.
2. Every filename referenced inside MEMORY.md actually exists in the memory directory
   (catches the inverse defect: a stale index entry pointing at a deleted/renamed file).

Both directions matter — orphan-in-store (unindexed) is the failure that was measured;
orphan-in-index (dangling) is the same defect class from the other side and just as cheap
to catch here.

USAGE
    python scripts/audit/check_memory_index_parity.py [--memory-dir PATH]

Exit code: 0 if MEMORY.md and the directory agree exactly; 1 otherwise (a finder AND a
gate — this one is cheap and deterministic enough to fail closed, unlike the citation
coverage instruments which stay report-only until a population/threshold is ratified).
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_MEMORY_DIR = (
    r"C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Foundational-Layer-"
    r"claude-foundational-layer\memory"
)

FILENAME_RE = re.compile(r"\(([A-Za-z0-9_.\-]+\.md)\)")


def scan(memory_dir):
    if not os.path.isdir(memory_dir):
        print(f"ERROR: memory dir not found: {memory_dir}", file=sys.stderr)
        return None

    on_disk = sorted(
        f for f in os.listdir(memory_dir)
        if f.endswith(".md") and f != "MEMORY.md"
    )

    index_path = os.path.join(memory_dir, "MEMORY.md")
    if not os.path.isfile(index_path):
        print(f"ERROR: MEMORY.md not found in {memory_dir}", file=sys.stderr)
        return None
    with open(index_path, encoding="utf-8", errors="ignore") as f:
        index_text = f.read()

    # Every occurrence of "(something.md)" in MEMORY.md is treated as an index entry's
    # link target — matches the observed format `- [Title](filename.md) — ...`.
    referenced = sorted(set(FILENAME_RE.findall(index_text)))

    on_disk_set, referenced_set = set(on_disk), set(referenced)
    unindexed = sorted(on_disk_set - referenced_set)   # on disk, MEMORY.md doesn't point at it
    dangling = sorted(referenced_set - on_disk_set)    # MEMORY.md points at it, file doesn't exist

    return {
        "memory_dir": memory_dir,
        "on_disk_count": len(on_disk),
        "referenced_count": len(referenced),
        "unindexed": unindexed,
        "dangling": dangling,
    }


def selftest():
    import tempfile, shutil
    fails = []
    tmp = tempfile.mkdtemp(prefix="parity-selftest-")
    try:
        with open(os.path.join(tmp, "MEMORY.md"), "w", encoding="utf-8") as f:
            f.write(
                "# Memory Index\n\n"
                "- [A](feedback_a.md) — indexed, on disk, fine.\n"
                "- [Ghost](feedback_ghost.md) — indexed but file was deleted.\n"
            )
        with open(os.path.join(tmp, "feedback_a.md"), "w", encoding="utf-8") as f:
            f.write("---\nname: a\n---\ncontent\n")
        with open(os.path.join(tmp, "feedback_unindexed.md"), "w", encoding="utf-8") as f:
            f.write("---\nname: unindexed\n---\ncontent — never linked from MEMORY.md\n")

        r = scan(tmp)
        if r["unindexed"] != ["feedback_unindexed.md"]:
            fails.append(f"FAIL unindexed detection: got {r['unindexed']!r}")
        if r["dangling"] != ["feedback_ghost.md"]:
            fails.append(f"FAIL dangling detection: got {r['dangling']!r}")
        if r["on_disk_count"] != 2:
            fails.append(f"FAIL on_disk_count: got {r['on_disk_count']!r} want 2")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print(f)
    if fails:
        print(f"\nSELFTEST: {len(fails)} failure(s)")
        return 1
    print("SELFTEST: 3/3 checks passed")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--memory-dir", default=DEFAULT_MEMORY_DIR)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    r = scan(a.memory_dir)
    if r is None:
        return 2

    print("=" * 78)
    print("MEMORY INDEX-STORE PARITY CHECK")
    print("=" * 78)
    print(f"  memory dir              : {r['memory_dir']}")
    print(f"  files on disk (ex. MEMORY.md) : {r['on_disk_count']}")
    print(f"  filenames referenced in MEMORY.md : {r['referenced_count']}")
    print()
    if r["unindexed"]:
        print(f"  UNINDEXED — on disk, not referenced by MEMORY.md ({len(r['unindexed'])}):")
        print("    (invisible to any session that only reads the index — the 2026-08-02 defect)")
        for f in r["unindexed"]:
            print(f"    - {f}")
    else:
        print("  UNINDEXED: none.")
    print()
    if r["dangling"]:
        print(f"  DANGLING — referenced by MEMORY.md, not on disk ({len(r['dangling'])}):")
        for f in r["dangling"]:
            print(f"    - {f}")
    else:
        print("  DANGLING: none.")
    print()

    if r["unindexed"] or r["dangling"]:
        print("RESULT: FAIL — index and store disagree.")
        return 1
    print("RESULT: PASS — every file on disk is indexed and every index entry resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
