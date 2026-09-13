#!/usr/bin/env python3
"""Census of YAML frontmatter keys across this trunk's markdown -- CFL-SCOPED, and the name says so.

WHY THIS EXISTS -- Jon named it, about one of ONLY THREE PRs he will receive
---------------------------------------------------------------------------
Jon, 2026-08-23 `[JON-LIVE, verbatim, typos his]`:

    "The metadata consistency! It was rempent even in the first of only 3 PRs that CFL will be
     allowed to give me! Very unprofessional."

Professional measured it across all trunks and reported CFL at **347 distinct top-level keys, 106
used exactly once** `[relayed- -- their lane measured it; they did not re-check it themselves, and
they published a correction the same day for three denominators taken that way]`. **A relayed count
about MY OWN TREE that I can measure myself is not a number I repeat.** This is the re-measurement.

TWO THINGS THIS DELIBERATELY DOES NOT DO
----------------------------------------
1. ⛔ **IT PROPOSES NO CROSSWALK, AND THAT IS PROFESSIONAL'S FINDING, NOT MY CAUTION.**
   `kind:` and `type:` mean OPPOSITE things in two trunks. In CFL they are exact duplicates on the
   same page (`kind: concept` AND `type: concept`). In Personal, `kind` is a namespaced sub-type OF
   `type` (`type: reference` / `kind: reference:method`). **So the obvious normalisation -- fold
   `type` into `kind` -- is correct for CFL and DESTROYS INFORMATION in Personal.** Any consumer
   built without opening pages would have made it worse, confidently. This tool is therefore
   **single-trunk by construction**: it takes a root, and it prints which root it measured.

2. ⛔ **IT CHANGES NOTHING.** Census only. No writes, no normalisation, no deletion.

THE ROOT BANNER IS NOT DECORATION
---------------------------------
`disposition_rate.py` bound its repo root from `__file__` and so "two trunks corroborate" was ONE
tree measured twice -- published, graded VERIFIED, and caught by a peer the same morning. Every
instrument here now prints the root it actually read, unsilenceably, and carries it INSIDE `--json`.

EXCLUDED TRUNKS: `wiki/personal`, `wiki/home`, `wiki/pro` and `self/` are counted in the TOTALS
(they are part of this tree's metadata problem) but their key VALUES are never printed -- Jon's
2026-07-25 ruling is about publication, and a census that quotes a family-medical page's frontmatter
into a PR body has published it. Surface, never act.

P2-22 TEMPLATE-HALF ADDITION (2026-08-31) -- --lint mode
---------------------------------------------------------
The census above is diagnosis only. `--lint` is the enforcement half: it flags (a) a page
carrying `kind:` and `type:` with IDENTICAL values (pure duplication -- see the SKILL.md
Concept Page template fix, same PR, which is the actual mint-time fix) and (b) a page with no
frontmatter at all. Report-only by default; `--strict` makes a violation a nonzero exit, for a
future pre-commit or CI hook to consume. `--files` restricts it to a changed-file list instead
of the full tree. This does NOT fix or touch the 8 existing offending wiki/concepts/ pages --
that is the 900-page half of P2-22, explicitly deferred.

Usage:
    python scripts/audit/frontmatter_census.py
    python scripts/audit/frontmatter_census.py --json
    python scripts/audit/frontmatter_census.py --selftest
    python scripts/audit/frontmatter_census.py --lint --root wiki
    python scripts/audit/frontmatter_census.py --lint --strict --files wiki/concepts/foo.md
    python scripts/audit/frontmatter_census.py --selftest-lint
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
QUIET = ("wiki/personal", "wiki/home", "wiki/pro", "self/")
KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:")


def is_quiet(rel):
    r = rel.replace("\\", "/")
    return any(r.startswith(q) for q in QUIET)


def parse_front(text):
    """Return (has_front, {key: value}) for a leading --- fenced YAML block.

    TOP-LEVEL ONLY, ON PURPOSE: an indented line is a nested key and counting it as top-level is
    how a key census inflates. Lines inside a block scalar are skipped for the same reason.
    """
    if not text.startswith("---"):
        return False, {}
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return False, {}
    out, depth_skip = {}, False
    for ln in lines[1:]:
        if ln.strip() in ("---", "..."):
            return True, out
        if not ln.strip():
            continue
        if ln[0] in " \t-":
            continue                      # nested, list item, or continuation
        m = KEY.match(ln)
        if m:
            out[m.group(1)] = ln[m.end():].strip()
    return False, out                     # never closed -- malformed, and that is a finding


def census(root):
    files, nofront, malformed = 0, [], []
    keycount = Counter()
    keyfiles = defaultdict(list)
    both_kind_type = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in
                       (".git", "node_modules", "__pycache__", ".understand-anything")]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            if rel.replace("\\", "/").startswith("raw/"):
                continue                  # gitignored bulk corpus; not this trunk's authored metadata
            files += 1
            try:
                with open(p, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read(8192)
            except OSError:
                continue
            closed, keys = parse_front(text)
            if not keys:
                nofront.append(rel)
                continue
            if not closed:
                malformed.append(rel)
            for k in keys:
                keycount[k] += 1
                if len(keyfiles[k]) < 3 and not is_quiet(rel):
                    keyfiles[k].append(rel)
            if "kind" in keys and "type" in keys:
                both_kind_type.append((rel, keys.get("kind"), keys.get("type")))
    return {"files": files, "nofront": nofront, "malformed": malformed,
            "keycount": keycount, "keyfiles": keyfiles, "both": both_kind_type}


def report(r, root, as_json=False):
    kc = r["keycount"]
    once = [k for k, n in kc.items() if n == 1]
    dupes = [b for b in r["both"] if b[1] == b[2] and b[1]]
    if as_json:
        print(json.dumps({
            "measured_root": root,
            "script_trunk": REPO,
            "is_own_trunk": os.path.abspath(root) == REPO,
            "files": r["files"], "no_frontmatter": len(r["nofront"]),
            "malformed_unclosed": len(r["malformed"]),
            "distinct_keys": len(kc), "keys_used_once": len(once),
            "pages_with_both_kind_and_type": len(r["both"]),
            "of_those_identical_values": len(dupes),
            "top_keys": kc.most_common(20),
            "singleton_keys": sorted(once),
        }, indent=2))
        return
    own = "THIS SCRIPT'S OWN TRUNK" if os.path.abspath(root) == REPO else "A DIFFERENT TREE"
    print("=" * 72)
    print("MEASURED ROOT : %s" % root)
    print("                ^-- %s  (script lives at %s)" % (own, REPO))
    print("=" * 72)
    print("markdown files (raw/ excluded) : %d" % r["files"])
    print("  no frontmatter               : %d" % len(r["nofront"]))
    print("  frontmatter never closed     : %d   <-- malformed, not merely inconsistent"
          % len(r["malformed"]))
    print("distinct top-level keys        : %d" % len(kc))
    print("  used exactly ONCE            : %d   (%.0f%% of the vocabulary)"
          % (len(once), 100.0 * len(once) / max(1, len(kc))))
    print("\npages carrying BOTH kind: and type: : %d" % len(r["both"]))
    print("  of those, IDENTICAL values        : %d   <-- pure duplication, no information"
          % len(dupes))
    for rel, k, t in dupes[:5]:
        if not is_quiet(rel):
            print("      %s   kind=%s type=%s" % (rel, k, t))
    print("\ntop 20 keys by page count:")
    for k, n in kc.most_common(20):
        print("  %-24s %5d" % (k, n))
    print("\nsingleton keys (the tail Jon is reading as sloppiness), first 40 of %d:" % len(once))
    print("  " + ", ".join(sorted(once)[:40]))
    print("\nBOUNDS -- what this does NOT tell you:")
    print("  * NOT reviewed: whether any key's VALUES are consistent. A key used 900 times with")
    print("    900 different value shapes counts as one key here and is a worse problem.")
    print("  * NOT reviewed: nested keys, by design -- top-level only.")
    print("  * RESULTING LIMITATION: a low singleton count would NOT mean the metadata is good.")
    print("    This measures VOCABULARY SPREAD only. Do not read it as a quality score, and do")
    print("    not propose a cross-trunk crosswalk from it -- kind:/type: mean opposite things")
    print("    in CFL and Personal, so folding them is correct here and lossy there.")


def lint(root, files=None):
    """Return a list of violation dicts for the lint checks below.

    P2-22 template-half lint. Two checks only, matching the ticket:
      (a) kind: and type: present with IDENTICAL values -- pure duplication, mint-time defect.
      (b) a markdown page with NO frontmatter at all.

    `files` restricts the walk to a given iterable of paths (relative or absolute) --
    used for a changed-files-only run. When None, walks the full `root`.

    CFL-SCOPED, same caveat as the census above: this checks for kind==type identity only.
    It does NOT propose a kind/type crosswalk and does NOT run against any tree where
    kind: and type: are not redundant by construction (e.g. the Personal trunk, where
    kind is a namespaced sub-type of type -- kind==type would not even be the failure
    shape there).
    """
    violations = []
    if files is not None:
        candidates = []
        for f in files:
            p = f if os.path.isabs(f) else os.path.join(root, f)
            rel = os.path.relpath(p, root)
            candidates.append((p, rel))
    else:
        candidates = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in
                           (".git", "node_modules", "__pycache__", ".understand-anything")]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, root)
                if rel.replace("\\", "/").startswith("raw/"):
                    continue
                candidates.append((p, rel))

    for p, rel in candidates:
        if not os.path.isfile(p):
            violations.append({"file": rel, "check": "missing", "detail": "listed but not found on disk"})
            continue
        try:
            with open(p, encoding="utf-8", errors="ignore") as fh:
                text = fh.read(8192)
        except OSError:
            continue
        closed, keys = parse_front(text)
        if not keys:
            violations.append({"file": rel, "check": "no_frontmatter", "detail": "no frontmatter block"})
            continue
        if "kind" in keys and "type" in keys and keys["kind"] == keys["type"] and keys["kind"]:
            violations.append({"file": rel, "check": "kind_type_duplicate",
                                "detail": "kind: %s == type: %s" % (keys["kind"], keys["type"])})
    return violations


def report_lint(violations, root, as_json=False):
    if as_json:
        print(json.dumps({"root": root, "violation_count": len(violations),
                           "violations": violations}, indent=2))
        return
    print("=" * 72)
    print("FRONTMATTER LINT : %s" % root)
    print("=" * 72)
    if not violations:
        print("no violations")
        return
    for v in violations:
        print("  [%s] %s -- %s" % (v["check"], v["file"], v["detail"]))
    print("\n%d violation(s)" % len(violations))


def selftest_lint():
    """Exercise both verdicts against throwaway fixtures -- never wiki pages."""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as td:
        # fixture that VIOLATES both checks
        bad_dir = os.path.join(td, "bad")
        os.makedirs(bad_dir)
        with open(os.path.join(bad_dir, "dup.md"), "w", encoding="utf-8") as fh:
            fh.write("---\ntitle: Dup Page\nkind: concept\ntype: concept\n---\nbody\n")
        with open(os.path.join(bad_dir, "nofront.md"), "w", encoding="utf-8") as fh:
            fh.write("# No frontmatter here\n\nbody text.\n")
        bad_violations = lint(bad_dir)
        bad_checks = sorted(v["check"] for v in bad_violations)
        bad_ok = bad_checks == ["kind_type_duplicate", "no_frontmatter"]
        print("--- fixture A (violating): expect 2 violations ---")
        for v in bad_violations:
            print("    [%s] %s -- %s" % (v["check"], v["file"], v["detail"]))
        print("    %s" % ("PASS" if bad_ok else "FAIL"))
        ok = ok and bad_ok

        # fixture that is CLEAN
        good_dir = os.path.join(td, "good")
        os.makedirs(good_dir)
        with open(os.path.join(good_dir, "clean.md"), "w", encoding="utf-8") as fh:
            fh.write("---\ntitle: Clean Page\nkind: protocol\n---\nbody\n")
        with open(os.path.join(good_dir, "diff.md"), "w", encoding="utf-8") as fh:
            # kind and type both present but DIFFERENT values -- not a violation of this check
            fh.write("---\ntitle: Different Values\nkind: doctrine\ntype: concept\n---\nbody\n")
        good_violations = lint(good_dir)
        good_ok = good_violations == []
        print("--- fixture B (clean): expect 0 violations ---")
        print("    violations=%r  %s" % (good_violations, "PASS" if good_ok else "FAIL"))
        ok = ok and good_ok

    print("\n" + ("LINT SELFTEST PASS" if ok else "LINT SELFTEST FAIL"))
    return 0 if ok else 1


def selftest():
    ok = True
    print("--- case 1: a well-formed block is parsed, top-level keys only ---")
    closed, k = parse_front("---\nname: x\ntype: concept\nmeta:\n  nested: y\n---\nbody\n")
    good = closed and set(k) == {"name", "type", "meta"}
    print("    closed=%s keys=%r  %s" % (closed, sorted(k), "PASS" if good else "FAIL"))
    ok = ok and good

    print("--- case 2: NEGATIVE CONTROL -- a file with no frontmatter yields nothing ---")
    closed2, k2 = parse_front("# Just a heading\n\nsome text\n")
    good2 = (not closed2) and not k2
    print("    closed=%s keys=%r  %s" % (closed2, k2, "PASS" if good2 else "FAIL"))
    ok = ok and good2

    print("--- case 3: an UNCLOSED block is reported unclosed, not silently accepted ---")
    closed3, k3 = parse_front("---\nname: x\nbody with no fence\n")
    good3 = (not closed3) and "name" in k3
    print("    closed=%s keys=%r  %s" % (closed3, sorted(k3), "PASS" if good3 else "FAIL"))
    ok = ok and good3

    print("--- case 4: a '---' horizontal rule mid-body does not open a block ---")
    closed4, k4 = parse_front("# Title\n\n---\n\nname: not-frontmatter\n")
    good4 = not k4
    print("    keys=%r  %s" % (k4, "PASS" if good4 else "FAIL"))
    ok = ok and good4

    print("\n" + ("SELFTEST PASS" if ok else "SELFTEST FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--lint", action="store_true",
                     help="P2-22: check (a) kind:/type: identical-value duplication, "
                          "(b) missing frontmatter. Report-only unless --strict.")
    ap.add_argument("--strict", action="store_true",
                     help="with --lint, exit 1 if any violation is found")
    ap.add_argument("--files", nargs="*", default=None,
                     help="with --lint, restrict to these paths (changed-files-only run) "
                          "instead of walking the full --root")
    ap.add_argument("--selftest-lint", action="store_true",
                     help="run the lint's own fixture selftest (both verdicts) and exit")
    a = ap.parse_args()
    if a.selftest_lint:
        return selftest_lint()
    if a.selftest:
        return selftest()
    if a.lint:
        root_abs = os.path.abspath(a.root)
        violations = lint(root_abs, files=a.files)
        report_lint(violations, root_abs, as_json=a.json)
        if a.strict and violations:
            return 1
        return 0
    report(census(a.root), os.path.abspath(a.root), as_json=a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
