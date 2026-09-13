#!/usr/bin/env python3
"""Untracked-in-wiki lint (wiki/tracker/questions-for-jon.md row D-B4).

Walks wiki/ and flags every .md file whose basename is not cited anywhere in the
known index/registry files (wiki/index.md, wiki/tracker/*.md, sub-wiki indexes,
wiki/log.md, wiki/sources/session-stubs.md, ...). A file with no citation anywhere
is registered nowhere — nothing routes a reader to it, and nothing would notice if
it silently disappeared. This does not check git-tracked status (that's a separate,
cheaper `git status` check) — it checks discoverability inside the wiki's own index
structure, which an untracked file can fail even after it's committed.

Match is deliberately loose (basename-as-substring against the full registry text):
the goal is "is this filename mentioned anywhere a reader would look," not exact
citation-format validation. False negatives (an orphan that happens to share a
filename fragment with something unrelated) are possible but rare in this corpus;
run with --verbose to see what each survivor matched against.

Run from repo root (worktree ok):
    python scripts/lint_untracked_wiki.py [--root .] [--verbose]

Exit code: 0 if every wiki/*.md is registered somewhere; 1 if any orphan is found.
"""
import argparse
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Files whose CONTENT we treat as the registry corpus. Kept as an explicit list
# (not auto-discovered) so a new registry surface has to be added here on purpose —
# the same discipline the lint itself is enforcing on the rest of wiki/.
REGISTRY_GLOBS = [
    "wiki/index.md",
    "wiki/meta-index.md",
    "wiki/log.md",
    "wiki/agent-guide.md",
    "wiki/tracker/*.md",
    "wiki/personal/index.md",
    "wiki/home/index.md",
    "wiki/pro/index.md",
    "wiki/sessions/index.md",
    "wiki/sources/session-stubs.md",
]

# Registry files are excluded from the orphan scan itself — a registry doesn't need
# to cite its own filename to be "found."
def registry_paths(root):
    paths = set()
    for pat in REGISTRY_GLOBS:
        for p in glob.glob(os.path.join(root, pat)):
            paths.add(os.path.normpath(p))
    return paths


def load_corpus(paths):
    text = []
    for p in sorted(paths):
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="ignore") as f:
                text.append(f.read())
    return "\n".join(text)


def all_wiki_md(root):
    return sorted(
        os.path.normpath(p)
        for p in glob.glob(os.path.join(root, "wiki", "**", "*.md"), recursive=True)
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root (default: cwd)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    reg_paths = registry_paths(args.root)
    if not reg_paths:
        print("ERROR: no registry files found — check --root", file=sys.stderr)
        return 2
    corpus = load_corpus(reg_paths)

    all_files = all_wiki_md(args.root)
    scanned = [p for p in all_files if p not in reg_paths]

    orphans = []
    for p in scanned:
        base = os.path.basename(p)
        if base in corpus:
            if args.verbose:
                print(f"OK    {os.path.relpath(p, args.root).replace(os.sep, '/')}")
            continue
        orphans.append(p)

    print(f"=== untracked-in-wiki lint — {len(scanned)} files checked against "
          f"{len(reg_paths)} registry files ===")
    if orphans:
        print(f"\n{len(orphans)} ORPHAN(S) — not cited in any registry file:\n")
        for p in orphans:
            print(f"  - {os.path.relpath(p, args.root).replace(os.sep, '/')}")
        print(
            "\nFix: add a row/line citing the file's basename to wiki/index.md, the "
            "relevant wiki/tracker/*.md registry, a sub-wiki index.md, or "
            "wiki/sources/session-stubs.md — whichever applies."
        )
        return 1

    print("PASS — every wiki/*.md is registered somewhere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
