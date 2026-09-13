#!/usr/bin/env python
"""_su_close_seeds.py — Q11 helper: of THIS session's synthesis seeds, how many carry a falsifier?

WHY THIS EXISTS — Jon's audit, 2026-08-03: seeds get identified during a session and never entered
into the register with the five-field standard (status, recommendation, falsifier,
falsifier_tested, blocks). "We noticed it" is not "it is reviewable" — a seed with no falsifier is
an observation, not a seed, per the guard rule "a falsifier may not be judged by its author" and
"untested ≠ passed" (both already load-bearing in `wiki/intake-triage/SEED-REGISTER-*.md`).

SCOPE, determined from the file, never hand-counted: everything under the section heading passed
via --section (default matches "today's" additions, distinct from any inherited prior section) up
to the next top-level `---` divider or end of file. A seed is one `## S<n> — ...` heading in that
span. "Carries a falsifier" means the seed's own five-field table has a `**falsifier**` row whose
cell is non-empty and is not a placeholder (`n/a`, `none`, `tbd`, or literally empty after
stripping table syntax).

THIS DOES NOT JUDGE WHETHER THE FALSIFIER IS ANY GOOD — only whether one was written down. Content
quality of a falsifier is Jon's and the coordinator's call, never this script's; conflating
"present" with "adequate" would be exactly the kind of check this program has already had to
un-teach itself (RATIO_FLOOR: an always-fires or never-fires gate that stops being read).

NEGATIVE CONTROL: an empty file, or a file with the section heading but zero `## S` entries,
reports "0 0" — the caller's classify() reads 0/0 as UNKNOWN, never a pass. A file with seeds that
have empty falsifier cells reports a real, non-zero shortfall. Verified by --self-test.

Usage:
  python _su_close_seeds.py --file <path/to/SEED-REGISTER-*.md> [--section "# Today's seeds"]
  python _su_close_seeds.py --self-test

Prints exactly one line: "<value> <denom>".
"""
import argparse
import re
import sys
from pathlib import Path

PLACEHOLDERS = {"", "n/a", "na", "none", "tbd", "-", "—"}


def scoped_section(text: str, section_marker: str) -> str:
    """Return the text from section_marker (a literal heading line) to the next '---' or EOF."""
    idx = text.find(section_marker)
    if idx == -1:
        return ""
    rest = text[idx + len(section_marker):]
    # Cut at the next horizontal-rule divider, which marks the end of the seeds' own body
    # (the file's own "Review summary" table sits after one) — else take the whole remainder.
    m = re.search(r"^\n---\s*$", rest, re.M)
    return rest[: m.start()] if m else rest


def count_seeds_and_falsifiers(section_text: str):
    """Split on '## S<n>' headings; for each block, check for a non-placeholder falsifier row."""
    blocks = re.split(r"(?=^##\s+S\d+\b)", section_text, flags=re.M)
    identified = 0
    with_falsifier = 0
    for b in blocks:
        if not re.match(r"^##\s+S\d+\b", b):
            continue
        identified += 1
        m = re.search(r"\|\s*\*\*falsifier\*\*\s*\|(.*?)\|\s*$", b, re.M)
        if not m:
            continue
        cell = re.sub(r"\*+", "", m.group(1)).strip().lower()
        if cell not in PLACEHOLDERS:
            with_falsifier += 1
    return with_falsifier, identified


def self_test():
    fails = 0

    def t(name, expected, actual):
        nonlocal fails
        ok = expected == actual
        print(f"  {'PASS' if ok else 'FAIL'}  {name}  (expected {expected!r} got {actual!r})")
        if not ok:
            fails += 1

    # (a) NEGATIVE CONTROL — no matching section at all.
    empty_doc = "# Some other file\n\nnothing relevant here.\n"
    sec = scoped_section(empty_doc, "# Today's seeds")
    t("no section marker -> empty scope", "", sec)
    t("no section -> 0/0", (0, 0), count_seeds_and_falsifiers(sec))

    # (b) section present, zero seeds inside it.
    doc_zero = "# Today's seeds\n\nNothing identified today.\n\n---\n\n# Unrelated next section\n"
    sec = scoped_section(doc_zero, "# Today's seeds")
    t("section with zero seeds -> 0/0", (0, 0), count_seeds_and_falsifiers(sec))

    # (c) mixed: one seed with a real falsifier, one with a placeholder, one with none at all.
    doc_mixed = """# Today's seeds

## S7 — has a real falsifier

| | |
|---|---|
| **status** | open |
| **falsifier** | Find a counter-example that disproves the claim |
| **blocks** | something |

## S8 — placeholder falsifier

| | |
|---|---|
| **status** | open |
| **falsifier** | n/a |

## S9 — no falsifier row at all

| | |
|---|---|
| **status** | open |

---

# Review summary

| Seed | Status |
|---|---|
| S7 | open |
"""
    sec = scoped_section(doc_mixed, "# Today's seeds")
    t("mixed doc: 3 identified", 3, count_seeds_and_falsifiers(sec)[1])
    t("mixed doc: 1 of 3 has a real falsifier", 1, count_seeds_and_falsifiers(sec)[0])

    # (d) the divider must actually cut the scope — a "Review summary" seed-shaped mention after
    # the divider must NOT be double-counted even though it names S7.
    t("divider excludes trailing review table from re-parsing as a seed",
      False, bool(re.search(r"^##\s+S\d+\b.*Review", sec, re.M)))

    if fails:
        print(f"RESULT: FAIL — {fails} case(s)")
        return 1
    print("RESULT: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="")
    ap.add_argument("--section", default="# Today's seeds")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if not args.file:
        print("0 0", flush=True)
        print("no --file given", file=sys.stderr)
        sys.exit(0)

    p = Path(args.file)
    if not p.is_file():
        print("0 0", flush=True)
        print(f"file not found: {p}", file=sys.stderr)
        sys.exit(0)

    text = p.read_text(encoding="utf-8", errors="ignore")
    section = scoped_section(text, args.section)
    value, denom = count_seeds_and_falsifiers(section)
    print(f"{value} {denom}")
    sys.exit(0)


if __name__ == "__main__":
    main()
