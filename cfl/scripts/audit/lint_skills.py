#!/usr/bin/env python3
"""Skill frontmatter lint — the check that would have caught a silent auto-invoke failure.

WHY
---
A skill's `description:` is what the platform matches against to decide whether to
auto-invoke it. If the frontmatter does not parse, the description is not read, and the
skill becomes **callable by name but never triggered** — a failure with no error message
anywhere. It looks exactly like a skill that simply chose not to fire.

Two such defects were live as of 2026-07-26, both reported by Herald and both confirmed
here by independent test rather than taken on report (Jon: "its possible the herald is
wrong"):

  1. **UTF-8 BOM (ef bb bf) before the opening `---`** on five skills —
     frame-before-commit, present-to-jon, session-order, test-master, and **wiki-master**.
     Demonstrated mechanism: with a plain utf-8 decode, `text.startswith("---")` is False,
     so the standard frontmatter guard finds no frontmatter at all. (This repo's own
     `census.py` and `lint.py` use exactly that guard.) A `utf-8-sig` decode hides it,
     which is why it survived so long — whether the bug appears depends on how the reader
     opened the file.

  2. **An unquoted `: ` inside a plain YAML scalar** in herald/SKILL.md's description
     ("Invoked when: session opens..."). Not a mis-parse — a hard
     `ScannerError: mapping values are not allowed here`. The whole block fails.

wiki-master's auto-invoke bears directly on the wiki-completeness sweep, which is the
program's critical path.

Usage:
    python scripts/audit/lint_skills.py            # report
    python scripts/audit/lint_skills.py --strict   # exit 1 on any defect (for CI / the SU)
"""
import argparse
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BOM = b"\xef\xbb\xbf"


def check(path):
    """Return a list of (severity, message) for one SKILL.md.

    SEVERITY MATTERS AND IS NOT DECORATION. Two different classes are found here and
    conflating them would overstate the second:

      CONFIRMED — a mechanism demonstrated on this machine. The BOM makes
                  `text.startswith("---")` False under a plain utf-8 decode, so the
                  standard frontmatter guard finds nothing. Shown, not argued.
      SPEC      — a violation of the YAML spec whose IMPACT depends on the platform's
                  parser, which is not observable from here. Claude Code may use a
                  lenient line-based reader (this repo's own parsers do exactly that:
                  `^([a-z_]+):\\s*(.*)$` happily takes everything after the first colon).
                  Reported as a real defect worth fixing, NOT as a demonstrated breakage.

    The distinction is the point. 14 of 33 skills trip the second class; asserting they
    "never auto-invoke" would be a causal claim I have not tested.
    """
    defects = []
    raw = open(path, "rb").read()

    if raw.startswith(BOM):
        defects.append(("CONFIRMED",
                        "UTF-8 BOM before frontmatter — under a plain utf-8 decode "
                        "text.startswith('---') is False, so the standard guard finds no "
                        "frontmatter and the description is never read"))
        raw = raw[3:]
    if not raw.startswith(b"---"):
        defects.append(("CONFIRMED", f"does not open with '---' (starts {raw[:8]!r})"))
        return defects

    text = raw.decode("utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        defects.append(("CONFIRMED", "frontmatter block is not terminated by a closing '---'"))
        return defects
    fm = m.group(1)

    data = None
    try:
        import yaml
        try:
            data = yaml.safe_load(fm)
        except Exception as e:
            culprit = ""
            for line in fm.splitlines():
                mm = re.match(r"^([A-Za-z0-9_\-]+):\s+(?!['\"|>])(.*)$", line)
                if mm and ": " in mm.group(2):
                    culprit = f" (likely '{mm.group(1)}': a plain scalar containing ': ')"
                    break
            defects.append(("SPEC",
                            f"not valid YAML — {type(e).__name__}: "
                            f"{str(e).splitlines()[0]}{culprit}. Quote the value or use a "
                            f"'>-' block. Impact depends on the platform's parser and is "
                            f"NOT verified from here."))
            return defects
    except ImportError:
        for line in fm.splitlines():
            mm = re.match(r"^([A-Za-z0-9_\-]+):\s+(?!['\"|>])(.*)$", line)
            if mm and ": " in mm.group(2):
                defects.append(("SPEC", f"'{mm.group(1)}' is a plain scalar containing ': ' "
                                        f"— invalid YAML. (pyyaml unavailable; heuristic check.)"))

    if isinstance(data, dict):
        for field in ("name", "description"):
            if not data.get(field):
                defects.append(("CONFIRMED", f"missing or empty '{field}'"))

    defects.extend(dead_pointers(path, text))
    return defects


# Only paths that are unambiguously repo paths — rooted at a known top-level directory.
# A bare `SKILL.md` or an illustrative `foo.md` in prose is NOT checked, because guessing
# which of those are pointers is how a linter starts flagging correct files.
# Set from --pointer-root. None = derive from each SKILL.md's own location (correct for the repo).
POINTER_ROOT = None

REPO_PATH = re.compile(
    r"`((?:skills|wiki|scripts|exchange|docs|research|raw|self)/[\w\-./]+\.\w{1,4})`")


def dead_pointers(skill_path, text):
    """Backticked repo paths inside a SKILL.md that do not exist.

    THE DEFECT THIS CATCHES, found 2026-07-26: session-order/SKILL.md — the COLD-OPEN
    skill — listed four mandatory and four conditional reads. **Six of the eight files did
    not exist anywhere in the repo.** They had been renamed into `skills/<name>/SKILL.md`
    long before and nothing noticed. A cold-open reading list pointing at absent files
    fails silently: the session either burns turns hunting or skips grounding, and neither
    is reported. frame-before-commit/references/GROUNDING.md had the same rot.

    Scoped deliberately narrow — see REPO_PATH. Bare filenames in prose are not checked;
    a linter that flags correct files gets ignored, which is worse than no linter.
    """
    # ⛔ AMENDED 2026-08-10 03:5x — POINTERS RESOLVE WHERE THE CONTENT LIVES, NOT WHERE THE SKILL
    # FILE SITS. Deriving the root from the SKILL.md's own location is correct for the repo copy and
    # WRONG for the deployed copy under `~/.claude/skills`, whose pointers name repo paths.
    # ⭐ MEASURED, AND THIS IS THE WHOLE REASON THE OPTION EXISTS: linting the deployed layer with
    # the derived root reported **21 skills with dead pointers**, including `wiki/index.md`,
    # `wiki/personal/index.md` and `wiki/references/vocabulary.md` — files that plainly exist. A
    # report like that, published, becomes "the deployed skill layer is broken in 21 places." It is
    # not. It is one root, pointed at the wrong tree.
    # ⚠️ THIRD FALSE-POSITIVE CLASS FOUND TONIGHT BY READING A LIST INSTEAD OF ITS COUNT.
    root = POINTER_ROOT or os.path.abspath(os.path.join(os.path.dirname(skill_path), "..", ".."))
    out, seen = [], set()
    for m in REPO_PATH.finditer(text):
        rel = m.group(1)
        if rel in seen:
            continue
        seen.add(rel)
        if not os.path.exists(os.path.join(root, rel)):
            out.append(("SPEC", f"dead pointer: `{rel}` does not exist"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--glob", default="skills/*/SKILL.md")
    ap.add_argument("--pointer-root", default=None,
                    help="resolve `repo/path` pointers against THIS tree instead of the one the "
                         "SKILL.md sits in. Required when linting the DEPLOYED copies under "
                         "~/.claude/skills, whose pointers name repo paths — see S-2's closure "
                         "test: lint must run against the copies skills actually load from.")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any defect")
    ap.add_argument("--verbose", action="store_true", help="also list skills that are clean")
    ap.add_argument("--max-desc", type=int, default=1536,
                    help="documented cap on description + when_to_use (code.claude.com/docs/en/skills)")
    a = ap.parse_args()
    global POINTER_ROOT
    if a.pointer_root:
        POINTER_ROOT = os.path.abspath(a.pointer_root)

    paths = sorted(glob.glob(os.path.join(a.root, a.glob)))
    if not paths:
        print(f"ERROR: no skills matched {a.glob!r} under {a.root!r}", file=sys.stderr)
        return 2

    confirmed, spec = [], []
    print(f"=== skill frontmatter lint — {len(paths)} skills ===\n")
    for p in paths:
        d = check(p)
        rel = os.path.relpath(p, a.root).replace(os.sep, "/")
        if not d:
            if a.verbose:
                print(f"  ok         {rel}")
            continue
        worst = "CONFIRMED" if any(s == "CONFIRMED" for s, _ in d) else "SPEC"
        (confirmed if worst == "CONFIRMED" else spec).append(rel)
        print(f"  {worst:<10} {rel}")
        for sev, msg in d:
            print(f"               - {msg}")

    print()
    print(f"CONFIRMED-breaking : {len(confirmed)}   "
          f"(mechanism demonstrated on this machine — the description is not read)")
    print(f"SPEC / pointer     : {len(spec)}   "
          f"(invalid YAML, or a dead repo pointer — real defects, runtime impact not asserted)")
    if spec:
        print("\n  These are two different things and the distinction is kept on purpose:")
        print("    - invalid YAML  : impact depends on the platform's parser. A lenient")
        print("                      line-based reader tolerates a plain scalar with ': ' —")
        print("                      this repo's own parsers do exactly that. Do NOT report")
        print("                      these as 'never auto-invokes' without testing the claim.")
        print("    - dead pointer  : unambiguous. The file is not there. A skill instructing a")
        print("                      read of an absent file fails silently — the session hunts")
        print("                      or skips, and nothing reports either.")
    if confirmed or spec:
        return 1 if a.strict else 0
    print(f"All {len(paths)} skills parse cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
