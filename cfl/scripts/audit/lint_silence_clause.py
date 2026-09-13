#!/usr/bin/env python3
"""lint_silence_clause.py -- Jon's 2026-09-01 ruling: "Silence is never approval should
hook a should consider on its implications."

The phrase is a NEGATION: ambiguous instances fail toward INACTION every time (the
Herald near-miss, 2026-09-01 -- a clause meant to unblock read as HOLD). So a file that
uses the phrase bare is REFUSED, not warned (a warning on a phrase that fails toward
inaction is itself silently absorbed -- the ticket's own words).

RULE: any NON-EXEMPT occurrence of a silence-is-not-approval variant requires the file
to carry an on-silence line with an EXPLICIT acting label (ACTS / NO-OP / "nothing acts").
EXEMPT occurrences (a letter DISCUSSING the phrase must be able to pass): blockquote
lines (>), struck text (~~...~~), and the phrase enclosed in double quotes.

CANNOT-DETECT (stated, per house rule): whether the on-silence line names the RIGHT
object, and whether "what silence does not license" is spelled out -- those are judgment;
this lint catches only the bare-negation-with-no-acting-default shape, which is the shape
that caused the near-miss. The cheaper half of the ticket stands above any lint: where
Jon said the thing plainly, quote him instead of encoding it.

Usage: lint_silence_clause.py <file> [<file>...]   exit 0 all pass, 1 any refusal.
"""
import re
import sys
from pathlib import Path

PHRASE = re.compile(r"silence is (?:never |not )?(?:an? )?(?:approval|verdict)", re.I)
ACTING = re.compile(r"\bACTS\b|\bNO-?OP\b|nothing acts|nothing fires", re.I)
ONSIL = re.compile(r"on[-_]silence.{0,400}", re.I | re.S)


def non_exempt_hits(text: str):
    hits = []
    struck_spans = [m.span() for m in re.finditer(r"~~.*?~~", text, re.S)]
    for m in PHRASE.finditer(text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        line = text[line_start:text.find("\n", m.start()) if text.find("\n", m.start()) != -1 else len(text)]
        if line.lstrip().startswith(">"):
            continue
        if any(a <= m.start() < b for a, b in struck_spans):
            continue
        # enclosed in double quotes on its line
        before = line[:m.start() - line_start]
        after = line[m.end() - line_start:]
        if before.count('"') % 2 == 1 and '"' in after:
            continue
        hits.append((text.count("\n", 0, m.start()) + 1, line.strip()[:90]))
    return hits


def lint(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = non_exempt_hits(text)
    if not hits:
        return []
    onsil = ONSIL.search(text)
    if onsil and ACTING.search(onsil.group(0)):
        return []
    problems = [f"line {n}: bare silence-negation: {frag}" for n, frag in hits]
    problems.append("and NO on-silence line with an explicit acting label (ACTS / NO-OP / "
                    "'nothing acts') exists in the file -- the negation fails toward inaction")
    return problems


def main():
    rc = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.is_file():
            print(f"UNKNOWN (not a file, not a pass): {arg}")
            rc = max(rc, 2)
            continue
        problems = lint(p)
        if problems:
            rc = 1
            print(f"REFUSED: {p.name}")
            for pr in problems:
                print(f"  {pr}")
        else:
            print(f"PASS: {p.name}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
