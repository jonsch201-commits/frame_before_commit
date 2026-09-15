#!/usr/bin/env python
"""Verify every evidence locator in the W-1b pattern pages resolves.

A locator is either:
  - a backtick-quoted path optionally followed by :line or :line-line or :line,line, e.g.
    `wiki/intake-triage/foo.md:12` or `N:\\claude-gists-private\\bar.md:14,52-53`
  - a [[slug]] reference to another pattern page

Resolution rule:
  - repo-relative paths (wiki/..., scripts/...) resolve against the clone root
  - N:\\claude-gists-private\\... paths resolve against /n/claude-gists-private
  - line numbers must be within the file's line count (each number in a list/range)
  - [[slug]] must have a corresponding wiki/patterns/<slug>.md file
"""
import re
import sys
from pathlib import Path

CLONE_ROOT = Path(r"N:\claude-cfl\clone")
PATTERNS_DIR = CLONE_ROOT / "wiki" / "patterns"
GISTS_ROOT = Path(r"N:\claude-gists-private")

NEW_PAGES = [
    "recorder-and-check-cannot-see-the-same-loss.md",
    "one-directional-trust.md",
    "wrapper-silenced-by-the-timeout-above-it.md",
    "a-negative-fixture-should-say-something-when-it-wrongly-succeeds.md",
    "a-limitation-rendered-as-a-completed-measurement.md",
    "the-disproof-was-in-the-rows-own-column.md",
    "delivery-channel-is-not-authorship.md",
    "three-runtimes-two-faults.md",
    "self-citation-moves-the-class.md",
    "healthy-mount-is-not-the-case-you-raised.md",
    "the-later-instrument-can-also-be-silent.md",
    "mtime-on-a-mirror-is-sync-time-not-authorship.md",
]

LOCATOR_RE = re.compile(
    r"`((?:wiki|scripts)/[^`]+?\.md|N:\\claude-gists-private\\[^`]+?\.md)(?::([0-9,\-]+))?`"
)
SLUG_RE = re.compile(r"\[\[([a-z0-9\-]+)\]\]")


def resolve_path(p: str) -> Path:
    if p.startswith("N:\\claude-gists-private\\"):
        rel = p[len("N:\\claude-gists-private\\") :].replace("\\", "/")
        return GISTS_ROOT / rel
    return CLONE_ROOT / p


def check_lines(fp: Path, spec: str) -> list:
    problems = []
    try:
        n_lines = sum(1 for _ in open(fp, encoding="utf-8", errors="replace"))
    except OSError as e:
        return [f"cannot open {fp}: {e}"]
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            nums = [int(lo), int(hi)]
        else:
            nums = [int(part)]
        for n in nums:
            if n < 1 or n > n_lines:
                problems.append(f"line {n} out of range (file has {n_lines} lines)")
    return problems


def main():
    total = 0
    resolved = 0
    failures = []
    for page in NEW_PAGES:
        fp = PATTERNS_DIR / page
        text = fp.read_text(encoding="utf-8")
        for m in LOCATOR_RE.finditer(text):
            total += 1
            path_str, line_spec = m.group(1), m.group(2)
            target = resolve_path(path_str)
            if not target.exists():
                failures.append(f"{page}: MISSING FILE {path_str}")
                continue
            if line_spec:
                problems = check_lines(target, line_spec)
                if problems:
                    failures.append(f"{page}: {path_str}:{line_spec} -> {problems}")
                    continue
            resolved += 1
        for m in SLUG_RE.finditer(text):
            total += 1
            slug = m.group(1)
            target = PATTERNS_DIR / f"{slug}.md"
            if target.exists():
                resolved += 1
            else:
                failures.append(f"{page}: [[{slug}]] -> MISSING {target}")

    print(f"resolved/total = {resolved}/{total}")
    if failures:
        print("FAILURES:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
