#!/usr/bin/env python3
"""
sweep_raw_paths.py — idempotent, map-driven pointer sweep for the
raw/sessions/ -> raw/transcripts/ (and raw/originals/) migration.

Record Architecture v1 (wiki/references/record-architecture-v1.md) moved the
corpus from raw/sessions/ to raw/transcripts/ on disk. A one-off 281-replacement
sweep was done by hand in PR #197 with no script committed, so it could not be
re-run and it missed skills/. This script rebuilds the old->new map FROM DISK
(never a hardcoded list), so it can be re-run safely any time the corpus moves
again.

Method
------
1. Index every file under raw/transcripts/ and raw/originals/ by basename.
2. Scan wiki/, skills/, scripts/, exchange/ for old-style path references:
   raw/sessions/..., raw/Anthropic_zips/..., raw/sessions/new-sessions/...
   Only FILE-level references (a path ending in a dotted extension) are
   resolved — bare directory mentions ("raw/sessions/claude-code/") describe
   the deprecated directory scheme in prose and have no single basename to
   resolve to; they are left untouched and are not reported as unresolved,
   since they are not pointers to a specific file.
3. For each file-level reference, resolve by basename against the index:
     - exactly one match  -> RESOLVED, rewrite (if --apply)
     - zero matches       -> UNRESOLVED (report; do not invent a target)
     - multiple matches   -> AMBIGUOUS (report; do not guess)
4. Excludes wiki/log.md and any path containing "/audit-" or "-audit-" by
   default (historical prose stays unedited). --include-historical overrides.
5. --dry-run (default) prints a table and touches nothing.
   --apply performs the rewrites in place.

Idempotent: once a pointer is rewritten to its new path, the regex no longer
matches raw/sessions/... in that spot, so a second run finds nothing to do.
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_DIRS = ["wiki", "skills", "scripts", "exchange"]
INDEX_DIRS = ["raw/transcripts", "raw/originals"]

# Binary / generated files to never scan.
SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".zip", ".jsonl"}

# Directory names that are gitignored, generated artifacts rather than
# source content — never scan (or --apply-rewrite) inside these, no matter
# which SCAN_DIRS they turn up under. wiki/.understand-anything/*.json is
# the motivating case (353 pointers as of 2026-07-29): it is regenerated
# from the wiki text on every /understand run, so rewriting it here is both
# pointless (next regeneration reverts it) and outside version control
# (nothing here is ever committed). A blanket ".json" SKIP_SUFFIXES entry
# was considered and rejected: real tracked .json files exist elsewhere in
# SCAN_DIRS (scripts/output/conversation_manifest.json,
# scripts/tests/sample_api_response.json,
# exchange/raw-metadata-sample-8d4396-2026-07-24.json) and a suffix-level
# skip would silence the sweep on those too. A directory-name skip targets
# exactly the generated tree instead.
SKIP_DIRNAMES = {"__pycache__", ".understand-anything"}

# Old-path prefixes we look for.
OLD_PREFIXES = ("raw/sessions/", "raw/Anthropic_zips/")

# A file-level reference: prefix, then path chars, ending in a dotted
# extension (2-5 word chars). This intentionally excludes bare directory
# mentions like "raw/sessions/claude-code/" or "raw/sessions/new-sessions".
PATH_RE = re.compile(
    r"raw/(?:sessions|Anthropic_zips)/[A-Za-z0-9_./-]*\.[A-Za-z0-9]{1,6}\b"
)

DEFAULT_EXCLUDE_FILE = "wiki/log.md"


def build_basename_index() -> dict:
    """Map basename -> list of repo-relative new paths, from disk."""
    index = {}
    for d in INDEX_DIRS:
        root = REPO_ROOT / d
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(REPO_ROOT).as_posix()
                index.setdefault(p.name, []).append(rel)
    return index


def iter_scan_files(include_historical: bool):
    for d in SCAN_DIRS:
        root = REPO_ROOT / d
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() in SKIP_SUFFIXES:
                continue
            if SKIP_DIRNAMES & set(p.parts):
                continue
            rel = p.relative_to(REPO_ROOT).as_posix()
            if rel == DEFAULT_EXCLUDE_FILE:
                continue
            if not include_historical and ("/audit-" in rel or "-audit-" in rel):
                continue
            yield p, rel


def _dir_segments(path: str, prefix_len: int) -> set:
    """Directory segments of path, excluding the leading old/new root and the basename."""
    parts = path.split("/")[prefix_len:-1]
    return set(parts)


def resolve(old_path: str, index: dict):
    """Return (status, new_path_or_None, candidates).

    On multiple basename matches, disambiguate by directory-segment overlap
    with the old path's own directory context (e.g. old .../personal/x.md
    prefers a candidate whose new path also contains "personal"). A unique
    top scorer resolves; a tie stays AMBIGUOUS rather than guessing.
    """
    basename = old_path.rsplit("/", 1)[-1]
    candidates = index.get(basename, [])
    if len(candidates) == 0:
        return "UNRESOLVED", None, []
    if len(candidates) == 1:
        return "RESOLVED", candidates[0], candidates

    old_segs = _dir_segments(old_path, prefix_len=2)  # drop "raw", "sessions"/"Anthropic_zips"
    scored = []
    for c in candidates:
        new_segs = _dir_segments(c, prefix_len=2)  # drop "raw", "transcripts"/"originals"
        scored.append((len(old_segs & new_segs), c))
    scored.sort(key=lambda t: -t[0])
    top_score = scored[0][0]
    top = [c for s, c in scored if s == top_score]
    if top_score > 0 and len(top) == 1:
        return "RESOLVED", top[0], candidates
    return "AMBIGUOUS", None, candidates


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="Write changes (default is dry-run).")
    ap.add_argument("--dry-run", action="store_true", help="Explicit dry-run (default behavior).")
    ap.add_argument(
        "--include-historical",
        action="store_true",
        help="Also rewrite files under /audit-.../-audit- paths and wiki/log.md is still excluded.",
    )
    ap.add_argument(
        "--paths",
        default=None,
        help="Comma-separated repo-relative file paths to restrict the scan to "
             "(default: full SCAN_DIRS sweep). Use to land a narrow, targeted fix.",
    )
    args = ap.parse_args()
    apply_mode = args.apply and not args.dry_run
    only_paths = set(args.paths.split(",")) if args.paths else None

    if only_paths is not None:
        missing = [p for p in only_paths if not (REPO_ROOT / p).is_file()]
        if missing:
            print("ERROR: --paths argument matches no file on disk (typo?):", file=sys.stderr)
            for p in sorted(missing):
                print(f"  {p}", file=sys.stderr)
            sys.exit(2)

    index = build_basename_index()
    dup_bases = {k: v for k, v in index.items() if len(v) > 1}

    rows = []  # (relpath, line_no, old, status, new)
    files_touched = set()
    total_resolved = 0
    unreadable = []  # relpaths skipped due to decode/OS errors
    matched_paths = set()  # relpaths actually visited, for --paths validation

    for path, rel in iter_scan_files(args.include_historical):
        if only_paths is not None and rel not in only_paths:
            continue
        matched_paths.add(rel)
        # Read raw bytes and decode without normalizing line endings (newline="")
        # so CRLF files round-trip unchanged. Never split/rejoin the whole file
        # on "\n" — that silently rewrites every line ending, not just the ones
        # touched. Line numbers below are computed separately, read-only, for
        # reporting; the actual rewrite runs against the untouched raw text.
        try:
            with open(path, "r", encoding="utf-8", newline="") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            unreadable.append(rel)
            continue

        # Line number of each match, for reporting only (does not affect the write).
        line_starts = [0]
        for idx, ch in enumerate(text):
            if ch == "\n":
                line_starts.append(idx + 1)

        def line_of(pos):
            lo, hi = 0, len(line_starts) - 1
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if line_starts[mid] <= pos:
                    lo = mid
                else:
                    hi = mid - 1
            return lo + 1

        replacements = []  # (start, end, old, new) for RESOLVED matches only
        for m in PATH_RE.finditer(text):
            old = m.group(0)
            status, new, candidates = resolve(old, index)
            rows.append((rel, line_of(m.start()), old, status, new))
            if status == "RESOLVED":
                total_resolved += 1
                replacements.append((m.start(), m.end(), old, new))

        if apply_mode and replacements:
            # Apply right-to-left so earlier offsets stay valid.
            new_text = text
            for start, end, old, new in sorted(replacements, key=lambda r: -r[0]):
                new_text = new_text[:start] + new + new_text[end:]
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_text)
            files_touched.add(rel)

    if only_paths is not None:
        # Catches the case a file exists on disk but sits outside SCAN_DIRS,
        # under a skipped suffix/dirname, or excluded as historical — any of
        # which would otherwise fall through to a silent "No pointers found"
        # that looks identical to a clean, fully-resolved sweep.
        never_scanned = only_paths - matched_paths
        if never_scanned:
            print(
                "ERROR: --paths argument matches a file on disk, but it is out of "
                "scan scope (SCAN_DIRS/SKIP_SUFFIXES/SKIP_DIRNAMES/historical exclude):",
                file=sys.stderr,
            )
            for p in sorted(never_scanned):
                print(f"  {p}", file=sys.stderr)
            sys.exit(2)

    # --- report ---
    print(f"=== sweep_raw_paths.py — {'APPLY' if apply_mode else 'DRY-RUN'} ===")
    print(f"basename index: {sum(len(v) for v in index.values())} files "
          f"({len(index)} unique basenames, {len(dup_bases)} duplicated)")
    print(f"unreadable files skipped (UnicodeDecodeError/OSError): {len(unreadable)}")
    if unreadable:
        for rel in sorted(unreadable):
            print(f"  {rel}")
    print()

    if not rows:
        print("No raw/sessions or raw/Anthropic_zips file-level pointers found in scope.")
        return

    print(f"{'file:line':<70} {'status':<12} old -> new")
    for rel, lineno, old, status, new in rows:
        loc = f"{rel}:{lineno}"
        if status == "RESOLVED":
            print(f"{loc:<70} {status:<12} {old} -> {new}")
        elif status == "AMBIGUOUS":
            cands = resolve(old, index)[2]
            print(f"{loc:<70} {status:<12} {old} -> ??? (candidates: {cands})")
        else:
            print(f"{loc:<70} {status:<12} {old} -> (no basename match on disk)")

    unresolved = [r for r in rows if r[3] == "UNRESOLVED"]
    ambiguous = [r for r in rows if r[3] == "AMBIGUOUS"]

    print(f"\nTotal references found : {len(rows)}")
    print(f"Resolved               : {total_resolved}")
    print(f"Ambiguous (skipped)    : {len(ambiguous)}")
    print(f"Unresolved (skipped)   : {len(unresolved)}")

    if unresolved:
        print("\n--- UNRESOLVED (no basename match on disk; needs human judgment) ---")
        for rel, lineno, old, status, new in unresolved:
            print(f"  {rel}:{lineno}  {old}")

    if ambiguous:
        print("\n--- AMBIGUOUS (multiple basename matches; needs human judgment) ---")
        for rel, lineno, old, status, new in ambiguous:
            cands = resolve(old, index)[2]
            print(f"  {rel}:{lineno}  {old} -> {cands}")

    if apply_mode:
        print(f"\nFiles rewritten: {len(files_touched)}")
        for f in sorted(files_touched):
            print(f"  {f}")
    else:
        print("\n(dry-run — no files written; pass --apply to rewrite RESOLVED pointers)")


if __name__ == "__main__":
    sys.exit(main())
