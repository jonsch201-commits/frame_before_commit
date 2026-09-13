#!/usr/bin/env python3
"""Index-section regenerator — checks (and can fix) the header COUNT on wiki/index.md's
four content sections against disk: Sources, Concepts, Patterns, Entities.

WHY THIS EXISTS SEPARATELY FROM index_counts.py
------------------------------------------------
`scripts/audit/index_counts.py` already re-derives the Sources header for all four trunk
indexes (`wiki/index.md`, `wiki/personal/index.md`, `wiki/home/index.md`, `wiki/pro/index.md`)
against `*/sources/`. It does NOT cover `wiki/concepts/`, `wiki/patterns/`, or `wiki/entities/`
at all — those headers have historically been hand-counted (see the Concepts header's own
2026-08-06/07 prose: "`index_counts.py` does not cover `wiki/concepts/`, so this is a hand
count"). A hand count is exactly the kind of fact nothing notices going stale — the same
defect `index_counts.py`'s own docstring names. This script closes that gap for the FL trunk
index (`wiki/index.md`) specifically, for all four sections, in one command.

Patterns and Entities are new sections as of 2026-09-02 (INDEX lane) — the directories
existed (`wiki/patterns/`, `wiki/entities/`) with populated content and their own sub-index
files, but the top-level `wiki/index.md` carried no row pointing at either, the identical
"front door" gap the 2026-08-23 reconciliation found for `wiki/tracker/`. `index.md` (the
sub-index each directory carries) is excluded from both the disk count and the listed count
for those two sections — it is the section's own registry file, not a content page it lists,
matching the convention `lint_untracked_wiki.py` already uses for `wiki/index.md` itself.

WHAT COUNTS AS "ON DISK" PER SECTION
-------------------------------------
  Sources   -- every *.md under wiki/sources/ (recursive). Matches index_counts.py's
               count_on_disk() definition exactly, including session-stubs.md (W-9, 2026-08-06).
  Concepts  -- every *.md directly under wiki/concepts/ (non-recursive; the directory has
               no subdirectories as of 2026-09-02).
  Patterns  -- every *.md under wiki/patterns/ EXCLUDING index.md.
  Entities  -- every *.md under wiki/entities/ EXCLUDING index.md.

WHAT COUNTS AS "LISTED" PER SECTION
-------------------------------------
Same mechanism as index_counts.py's count_listed(): every backtick-quoted `path.md` string
anywhere in wiki/index.md that resolves (relative to wiki/) under that section's directory.
Deliberately a DIFFERENT enumeration mechanism than the disk walk — two agreeing
enumerations, not one enumeration reported twice.

WHAT THIS SCRIPT DOES AND DOES NOT DO
----------------------------------------
It checks and can rewrite the FOUR HEADER COUNT NUMBERS (the "(N files / N listed)" figures).
It does NOT auto-generate table rows or prose — those carry real editorial content (titles,
one-line descriptions, provenance notes) that a mechanical regenerator would either omit or
fabricate. Adding a new page's row is lane work, same as it has always been; this script's
job is to make it impossible for the header to silently drift out of sync with what the rows
(and the disk) actually say, and to name the drift precisely when it happens rather than
requiring a human to recount two things by hand.

Usage:
    python scripts/audit/regen_index_sections.py            # report only
    python scripts/audit/regen_index_sections.py --check    # exit 1 on any drift (for the SU)
    python scripts/audit/regen_index_sections.py --write    # rewrite the four header numbers
                                                              # in place to match disk (still
                                                              # reports drift; does not touch rows)

Exit: 0 if all four sections' header counts agree with disk (and with the listed-row count);
1 under --check (or --write, if drift remains e.g. listed != disk) when any disagree.
"""
import argparse
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# section name -> (header regex prefix, directory relative to repo root, exclude-basenames)
SECTIONS = [
    ("Sources",  r"^##\s*Sources\s*\(",   "wiki/sources",  set()),
    ("Concepts", r"^##\s*Concepts\s*\(",  "wiki/concepts", set()),
    ("Patterns", r"^##\s*Patterns\s*\(",  "wiki/patterns", {"index.md"}),
    ("Entities", r"^##\s*Entities\s*\(",  "wiki/entities", {"index.md"}),
]

INDEX_PATH = "wiki/index.md"

HEADER_NUM_RE = re.compile(r"\((\d+)\s*files?\s*/\s*(\d+)\s*listed\)")


def count_on_disk(root, srcdir, exclude, recursive=True):
    d = os.path.join(root, srcdir)
    if not os.path.isdir(d):
        return 0
    n = 0
    if recursive:
        for dirpath, _, files in os.walk(d):
            for fn in files:
                if fn.endswith(".md") and fn not in exclude:
                    n += 1
    else:
        for fn in os.listdir(d):
            if fn.endswith(".md") and fn not in exclude:
                n += 1
    return n


def count_listed(root, index_text, srcdir, exclude):
    """Backtick-quoted `<path>.md` strings anywhere in wiki/index.md resolving under srcdir.

    `exclude` (basenames, e.g. {"index.md"}) is applied here too: a section's own sub-index
    is routinely self-cited in prose ("Full list: `wiki/patterns/index.md`") without being a
    CONTENT row that section lists, so it must not count toward "listed" any more than it
    counts toward "on disk" — otherwise the two enumerations disagree over a citation neither
    side considers a content page.
    """
    want = srcdir[len("wiki/"):].rstrip("/") + "/"  # e.g. "sources/"
    hits = set()
    for raw in re.findall(r"`([\w\-./]+\.md)`", index_text):
        rel = raw.replace("\\", "/").lstrip("./")
        if rel.startswith("wiki/"):
            rel = rel[len("wiki/"):]
        rel = os.path.normpath(rel).replace("\\", "/")
        if rel.startswith(want) and os.path.basename(rel) not in exclude:
            hits.add(rel)
    return len(hits)


def find_section_header(text, prefix_re):
    """Return (start, end, matched_line) of the FIRST line matching prefix_re, or None."""
    for m in re.finditer(r"^.*$", text, re.M):
        if re.match(prefix_re, m.group(0)):
            return m.start(), m.end(), m.group(0)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true",
                     help="exit 1 on any drift (report only, no write)")
    ap.add_argument("--write", action="store_true",
                     help="rewrite the four header count numbers in place to match disk")
    a = ap.parse_args()

    idx_path = os.path.join(a.root, INDEX_PATH)
    if not os.path.isfile(idx_path):
        print(f"ERROR: {INDEX_PATH} not found under --root {a.root}", file=sys.stderr)
        return 2
    text = open(idx_path, encoding="utf-8").read()

    print("=== index-section regen check — wiki/index.md, 4 sections re-derived from disk ===\n")
    print(f"  {'section':<10} {'header':>14} {'on disk':>8} {'listed':>7}   verdict")
    print(f"  {'-'*10} {'-'*14} {'-'*8} {'-'*7}   {'-'*7}")

    drift = 0
    edits = []  # (old_line, new_line) for --write

    for name, prefix_re, srcdir, exclude in SECTIONS:
        recursive = (name == "Sources")
        on_disk = count_on_disk(a.root, srcdir, exclude, recursive=recursive)
        listed = count_listed(a.root, text, srcdir, exclude)

        found = find_section_header(text, prefix_re)
        if found is None:
            print(f"  {name:<10} {'MISSING':>14} {on_disk:>8} {listed:>7}   DRIFT")
            print(f"      - no '## {name} (' header found in {INDEX_PATH}")
            drift += 1
            continue

        start, end, line = found
        m = HEADER_NUM_RE.search(line)
        bad = []
        if m is None:
            bad.append("header has no parseable (N files / N listed)")
            claimed_files = claimed_listed = None
        else:
            claimed_files, claimed_listed = int(m.group(1)), int(m.group(2))
            if claimed_files != on_disk:
                bad.append(f"header says {claimed_files} files, disk has {on_disk}")
            if claimed_listed != listed:
                bad.append(f"header says {claimed_listed} listed, table/rows have {listed}")
            if listed != on_disk:
                bad.append(f"{'unlisted pages exist' if on_disk > listed else 'index lists missing pages'} "
                            f"(disk {on_disk} vs listed {listed})")

        hdr = f"{claimed_files}/{claimed_listed}" if claimed_files is not None else "?"
        print(f"  {name:<10} {hdr:>14} {on_disk:>8} {listed:>7}   {'OK' if not bad else 'DRIFT'}")
        for b in bad:
            print(f"      - {b}")
        if bad:
            drift += 1
            if a.write and m is not None:
                new_num = f"({on_disk} files / {on_disk} listed)"
                new_line = line[:m.start()] + new_num + line[m.end():]
                edits.append((line, new_line))

    print()
    if drift:
        print(f"DRIFT in {drift} of {len(SECTIONS)} sections.")
    else:
        print(f"All {len(SECTIONS)} sections agree with disk.")

    if a.write and edits:
        new_text = text
        for old_line, new_line in edits:
            new_text = new_text.replace(old_line, new_line, 1)
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"\n--write: rewrote {len(edits)} header count(s) in place. Rows were NOT touched —")
        print("  a header-count match does not mean the rows are complete; re-run without --write")
        print("  to confirm, and add any missing rows by hand before the next SU.")

    if drift and (a.check or a.write):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
