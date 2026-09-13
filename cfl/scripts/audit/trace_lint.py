#!/usr/bin/env python3
"""trace_lint.py — wiki-wide ground-before-stating lint (RP-14, promoted from
PROTOTYPE-trace-lint-wipe-me.py 2026-09-01).

Jon, live 2026-08-31 ~18:5x: "shouldn't everything in the wiki require
ground-before-stating such that a fresh reader can easily trace to your
reasoning and my words?"

Two granularities, because page-level >=1-marker is a GENEROUS bar (stated
limitation, RP-14(a)):

  page level : does the page carry any trace marker at all?
  claim level: for each line that ATTRIBUTES to Jon (said/ruled/approved...),
               is a trace marker on the same line or within WINDOW lines?
               A claim with no nearby marker = an untraced attribution.

Markers are the idioms this wiki already uses (not invented here): [measured],
turn anchors [slug:TNN], history.jsonl:N / *.jsonl:N line cites, raw/transcripts/
paths, [TRANSCRIPT:...] grades, "verbatim", file:line cites into the repo.

Opt-outs, both deliberate and narrow:
  - frontmatter `coverage_class: untraced-by-design` (mechanical extracts) skips
    the file entirely;
  - excluded trunks wiki/personal, wiki/home, wiki/pro are surfaced-not-scanned.

CANNOT-DETECT (stated): whether a nearby marker actually grounds THAT claim
(adjacency is a proxy); paraphrase-attributions that avoid the claim verbs; a
marker pointing at a wrong or dead path. Per-claim EDGES (RP-4 cites-primary)
are the real fix; this lint is the census that finds where they're missing.

Usage:
  trace_lint.py <wiki-root>                # full census, exit 0 always
  trace_lint.py <wiki-root> --worst N      # show N worst pages per bucket
  trace_lint.py --file F [F...]            # mint-time mode: lint named files,
                                           # exit 1 if any has an untraced claim
"""
import argparse
import re
import sys
from pathlib import Path

MARKERS = [
    re.compile(r"\[measured", re.I),
    re.compile(r"\[[a-z0-9-]+:T\d+\]"),
    re.compile(r"history\.jsonl:\d+"),
    re.compile(r"\.jsonl:\d+"),
    re.compile(r"raw/transcripts/"),
    re.compile(r"\[TRANSCRIPT:"),
    re.compile(r"verbatim", re.I),
    re.compile(r"[\w/.-]+\.(?:md|py|sh|json)[:#]L?\d+"),
    # date-stamped attribution, an idiom the trackers already use: "(Jon, 2026-08-09 08:2x)"
    re.compile(r"\(Jon,? +20\d\d-\d\d-\d\d"),
]
CLAIM = re.compile(
    r"Jon (said|ruled|asked|directed|granted|approved|confirmed|declined)"
    r"|Jon's (ruling|words|directive|approval)", re.I)
OPTOUT = re.compile(r"^coverage_class:\s*untraced-by-design", re.M)
# derived docs (regenerated mirrors): their trace IS the source_of_truth line, and
# editing their body desyncs them from the regen source — skip, reported separately
DERIVED = re.compile(r"^source_of_truth:", re.M)
WINDOW = 3  # lines of adjacency granted around a claim line


def line_has_marker(line):
    return any(rx.search(line) for rx in MARKERS)


def lint_text(text):
    """Return (n_markers, n_claims, untraced_claims:[(lineno, frag)])."""
    lines = text.splitlines()
    marked = [line_has_marker(l) for l in lines]
    n_markers = sum(len(rx.findall(text)) for rx in MARKERS)
    untraced, n_claims = [], 0
    for i, l in enumerate(lines):
        if not CLAIM.search(l):
            continue
        n_claims += 1
        lo, hi = max(0, i - WINDOW), min(len(lines), i + WINDOW + 1)
        if not any(marked[lo:hi]):
            untraced.append((i + 1, l.strip()[:100]))
    return n_markers, n_claims, untraced


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", help="wiki root for census mode")
    ap.add_argument("--file", nargs="+", help="mint-time mode: lint these files, exit 1 on untraced claim")
    ap.add_argument("--worst", type=int, default=12)
    a = ap.parse_args()

    if a.file:
        rc = 0
        for f in a.file:
            p = Path(f)
            if not p.is_file():
                print(f"UNKNOWN (not a file, not a pass): {f}")
                rc = max(rc, 2)
                continue
            t = p.read_text(encoding="utf-8", errors="replace")
            if OPTOUT.search(t[:2000]):
                print(f"SKIP (untraced-by-design): {p.name}")
                continue
            if DERIVED.search(t[:2000]):
                print(f"SKIP (derived doc; trace lives at its source_of_truth): {p.name}")
                continue
            n_m, n_c, unt = lint_text(t)
            if unt:
                rc = 1
                print(f"REFUSED: {p.name} — {len(unt)} Jon-attribution(s) with no trace marker within {WINDOW} lines:")
                for n, frag in unt:
                    print(f"  line {n}: {frag}")
                print("  ground each with a primary (path, file:line, [measured], turn anchor) or quote him verbatim with venue")
            else:
                print(f"PASS: {p.name} (claims={n_c}, markers={n_m})")
        return rc

    root = Path(a.root or "wiki")
    pages = grounded = claimy_unmarked = skipped = 0
    per_dir, worst_pages, worst_claims = {}, [], []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if rel.startswith(("personal/", "home/", "pro/")):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if OPTOUT.search(t[:2000]) or DERIVED.search(t[:2000]):
            skipped += 1
            continue
        n_m, n_c, unt = lint_text(t)
        pages += 1
        d = rel.split("/")[0]
        per_dir.setdefault(d, [0, 0, 0])
        per_dir[d][0] += 1
        if n_m > 0:
            grounded += 1
            per_dir[d][1] += 1
        elif n_c > 0:
            claimy_unmarked += 1
            per_dir[d][2] += 1
            worst_pages.append((n_c, rel))
        if unt:
            worst_claims.append((len(unt), rel, unt))
    print(f"pages scanned: {pages}  (skipped untraced-by-design: {skipped})")
    print(f"page-level: {grounded} with >=1 marker ({100*grounded/pages:.0f}%), "
          f"{claimy_unmarked} attribute to Jon with ZERO markers")
    print("\nper top-level dir: pages / with-markers / jon-claims-zero-marker-pages")
    for d, (n, m, c) in sorted(per_dir.items()):
        print(f"  {d:20s} {n:4d} {m:4d} {c:4d}")
    print(f"\nPAGE-LEVEL WORST (Jon-attribution pages with zero markers), top {a.worst}:")
    for n_c, rel in sorted(worst_pages, reverse=True)[:a.worst]:
        print(f"  {n_c:3d} claims  {rel}")
    print(f"\nCLAIM-LEVEL (untraced claims even on marked pages), top {a.worst} by count:")
    for n_u, rel, unt in sorted(worst_claims, key=lambda x: -x[0])[:a.worst]:
        print(f"  {n_u:3d} untraced  {rel}")
    total_unt = sum(n for n, _, _ in worst_claims)
    print(f"\nclaim-level total: {total_unt} untraced Jon-attributions across "
          f"{len(worst_claims)} pages (adjacency window {WINDOW} lines — a proxy, see header)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
