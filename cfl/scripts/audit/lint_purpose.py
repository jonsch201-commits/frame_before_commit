#!/usr/bin/env python3
"""lint_purpose.py -- checks skills/*/PURPOSE.md, the WikiSkills PURPOSE.md layer
(paper arXiv 2608.27454: each skill directory holds SKILL.md and PURPOSE.md, which
maps the skill back to the motivating wiki pattern that inspired its creation).

RULES
-----
1. Every `skills/<name>/SKILL.md` must have a sibling `skills/<name>/PURPOSE.md`.
2. `PURPOSE.md`'s frontmatter must parse as `key: value` lines between two `---`
   fences (this repo's houses use plain-scalar YAML; no external yaml dependency).
3. `motivating_pattern` must be either the literal string `UNKNOWN` (no other prose
   is accepted -- a guess dressed as a link is worse than an honest UNKNOWN) or a
   `[[slug]]` locator that resolves to an existing `wiki/patterns/<slug>.md` file.
4. Required frontmatter keys are present: format, skill, motivating_pattern,
   origin_evidence, first_accepted, validation_split, r_best, declared_tier,
   generated_by.

This mirrors the shape of lint_skills.py (frontmatter defects fail loud, not
silent) but for the PURPOSE layer rather than SKILL.md itself. It does NOT edit
any SKILL.md and does NOT gate skill creation -- GT-1 (the skills gate) governs
skill content; this only checks that the back-reference layer is present and
honest about what it does not know.

Usage:
    python scripts/audit/lint_purpose.py             # report, exit 1 on any FAIL
    python scripts/audit/lint_purpose.py --selftest   # plant two known-bad fixtures,
                                                       # assert both FAIL, clean up,
                                                       # exit 0 only if the detector
                                                       # actually caught them
"""
import argparse
import glob
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_KEYS = [
    "format", "skill", "motivating_pattern", "origin_evidence",
    "first_accepted", "validation_split", "r_best", "declared_tier",
    "generated_by",
]

LINK_RE = re.compile(r"^\[\[([a-z0-9][a-z0-9-]*[a-z0-9]|[a-z0-9])\]\]$")


def repo_root():
    here = os.path.abspath(os.path.dirname(__file__))
    # scripts/audit/ -> repo root is two levels up
    return os.path.abspath(os.path.join(here, "..", ".."))


def parse_frontmatter(text):
    """Return (dict_of_keys, error_or_None). Plain `key: value` scalar lines only
    between the first two `---` fences -- matches this repo's SKILL.md convention,
    deliberately not a full YAML parser (a parser would accept multiline/prose
    values that rule 3 exists specifically to reject)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "no opening --- fence on line 1"
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "no closing --- fence found"
    fm = {}
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        if ":" not in raw:
            return None, f"unparseable frontmatter line: {raw!r}"
        key, _, value = raw.partition(":")
        fm[key.strip()] = value.strip()
    return fm, None


def check_one(purpose_path, patterns_dir):
    """Return list of (severity, message) -- severity 'FAIL' blocks exit 0."""
    problems = []
    if not os.path.isfile(purpose_path):
        return [("FAIL", f"{purpose_path}: PURPOSE.md does not exist")]
    text = open(purpose_path, encoding="utf-8", errors="replace").read()
    fm, err = parse_frontmatter(text)
    if err:
        return [("FAIL", f"{purpose_path}: frontmatter did not parse -- {err}")]
    for key in REQUIRED_KEYS:
        if key not in fm or not fm[key]:
            problems.append(("FAIL", f"{purpose_path}: missing required key '{key}'"))
    mp = fm.get("motivating_pattern", "")
    if mp == "UNKNOWN":
        pass
    else:
        m = LINK_RE.match(mp)
        if not m:
            problems.append((
                "FAIL",
                f"{purpose_path}: motivating_pattern '{mp}' is neither the literal "
                "UNKNOWN nor a [[slug]] locator (prose motivating_pattern values are "
                "the exact defect this rule exists to catch)",
            ))
        else:
            slug = m.group(1)
            target = os.path.join(patterns_dir, f"{slug}.md")
            if not os.path.isfile(target):
                problems.append((
                    "FAIL",
                    f"{purpose_path}: motivating_pattern [[{slug}]] does not resolve "
                    f"-- no file at wiki/patterns/{slug}.md",
                ))
    return problems


def run(root):
    skills_dir = os.path.join(root, "skills")
    patterns_dir = os.path.join(root, "wiki", "patterns")
    skill_mds = sorted(glob.glob(os.path.join(skills_dir, "*", "SKILL.md")))
    n_skill = len(skill_mds)
    n_purpose = 0
    all_problems = []
    for sm in skill_mds:
        skill_dir = os.path.dirname(sm)
        pm = os.path.join(skill_dir, "PURPOSE.md")
        if os.path.isfile(pm):
            n_purpose += 1
        all_problems.extend(check_one(pm, patterns_dir))
    return n_skill, n_purpose, all_problems


def selftest():
    """Plant one PURPOSE.md with a prose motivating_pattern and one with a
    nonexistent-slug [[link]]. Both MUST report FAIL, or the detector itself is
    the defect. Cleans up its own fixture regardless of outcome."""
    root = repo_root()
    fixtures_dir = os.path.join(tempfile.gettempdir(), "claude", "lint_purpose_selftest")
    os.makedirs(fixtures_dir, exist_ok=True)
    patterns_dir = os.path.join(root, "wiki", "patterns")

    prose_path = os.path.join(fixtures_dir, "PURPOSE-prose.md")
    with open(prose_path, "w", encoding="utf-8") as f:
        f.write(
            "---\n"
            "format: cfl-purpose/v1\n"
            "skill: fixture-prose\n"
            "motivating_pattern: this is a guess about what motivated it, not a link\n"
            "origin_evidence: pre-gate (before 2026-08-31)\n"
            "first_accepted: pre-gate\n"
            "validation_split: none\n"
            "r_best: UNKNOWN\n"
            "declared_tier: UNKNOWN\n"
            "generated_by: lane W-2 (sonnet) session e515d858\n"
            "---\n\n## Why this skill exists\n\nfixture.\n\n"
            "## What would retire it\n\nfixture.\n"
        )

    badlink_path = os.path.join(fixtures_dir, "PURPOSE-badlink.md")
    with open(badlink_path, "w", encoding="utf-8") as f:
        f.write(
            "---\n"
            "format: cfl-purpose/v1\n"
            "skill: fixture-badlink\n"
            "motivating_pattern: [[this-slug-does-not-exist-anywhere]]\n"
            "origin_evidence: pre-gate (before 2026-08-31)\n"
            "first_accepted: pre-gate\n"
            "validation_split: none\n"
            "r_best: UNKNOWN\n"
            "declared_tier: UNKNOWN\n"
            "generated_by: lane W-2 (sonnet) session e515d858\n"
            "---\n\n## Why this skill exists\n\nfixture.\n\n"
            "## What would retire it\n\nfixture.\n"
        )

    try:
        prose_problems = check_one(prose_path, patterns_dir)
        badlink_problems = check_one(badlink_path, patterns_dir)
        prose_failed = any(sev == "FAIL" for sev, _ in prose_problems)
        badlink_failed = any(sev == "FAIL" for sev, _ in badlink_problems)
        print(f"SELFTEST prose-motivating_pattern fixture: "
              f"{'FAIL (correct)' if prose_failed else 'PASS (WRONG -- detector missed it)'}")
        for sev, msg in prose_problems:
            print(f"    {sev}: {msg}")
        print(f"SELFTEST nonexistent-slug fixture: "
              f"{'FAIL (correct)' if badlink_failed else 'PASS (WRONG -- detector missed it)'}")
        for sev, msg in badlink_problems:
            print(f"    {sev}: {msg}")
        ok = prose_failed and badlink_failed
        print(f"\nSELFTEST {'PASSED' if ok else 'FAILED'} "
              f"(both planted fixtures must FAIL for the detector to be trusted)")
        return 0 if ok else 1
    finally:
        for p in (prose_path, badlink_path):
            try:
                os.remove(p)
            except OSError:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                     help="plant two known-bad fixtures, assert both FAIL, clean up")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    root = repo_root()
    n_skill, n_purpose, problems = run(root)
    print(f"SKILL.md count: {n_skill}")
    print(f"PURPOSE.md count: {n_purpose}")
    fails = [p for p in problems if p[0] == "FAIL"]
    if not problems:
        print("No problems found.")
    else:
        for sev, msg in problems:
            print(f"{sev}: {msg}")
    print(f"\n{len(fails)} FAIL(s) of {n_skill} skill(s) checked.")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
