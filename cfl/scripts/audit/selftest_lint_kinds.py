#!/usr/bin/env python3
"""Selftest for scripts/audit/lint.py's --all-kinds extension (lane W-6, 2026-09-02).

Two things this proves, both required by the lane's brief:

1. REGRESSION — /sources/ pages grade IDENTICALLY under the new lint.py (default mode, no
   --all-kinds) as they did under the git-HEAD version, for every page and every check. Loads
   both lint.py files as separate Python modules and drives their kind_of()/grade() functions
   directly (no subprocess spawn per page, so this runs the whole /sources/ tree fast). This is
   the hard constraint from the lane's brief: "never change any existing verdict for /sources/
   pages."

2. NEW-KIND FIXTURES — a synthetic wiki+skills tree, built fresh in a tempfile.mkdtemp()
   directory and torn down at the end, exercises grade_new_kind()/grade_e9()/grade_e10() through
   the REAL lint.py CLI (subprocess, --all-kinds) against one clean fixture per kind, plus three
   planted failures: a pattern with only one Struggle locator (must FAIL E9_backref), a purpose
   page whose motivating_pattern is prose rather than [[slug]]/UNKNOWN (must FAIL E9_backref),
   and a page with a qualifying date but no probe_sealed field at all (must FAIL E10_probe). Also
   covers the E3 fidelity-tag qualifier widening (`[verbatim, cropped]`) and confirms --explain
   never returns silence for an out-of-scope page.

Read-only against N:\\claude-corpus (never written); never touches G:\\; writes only under its own
tempfile.mkdtemp() directory, removed at the end regardless of pass/fail. Run from repo root
(N:\\claude-cfl\\clone) or anywhere — REPO is derived from this file's own path.
"""
import glob, hashlib, importlib.util, os, re, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # .../clone
MAIN_ROOT = "N:/claude-corpus/cfl"
SCRATCH = (r"C:\Users\JonSc\AppData\Local\Temp\claude\G--My-Drive-Claude-Claude-Foundational-"
           r"Layer-claude-foundational-layer\e515d858-3efb-41b2-ab93-52fdd2dd6dbe\scratchpad\w6-lint")

FAILS = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def load_module(path, modname):
    d = os.path.dirname(path)
    if d not in sys.path:
        sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ================================================================================================
# PART 1 — regression: old lint.py (git HEAD) vs new lint.py, every real /sources/ page
# ================================================================================================

def regression_check():
    print("\n=== PART 1: regression, old lint.py (git HEAD) vs new lint.py, /sources/ pages ===")
    old_path = os.path.join(SCRATCH, "old_lint.py")
    if not os.path.isfile(old_path):
        check("regression fixture prerequisite: old_lint.py present in scratch", False,
              f"missing {old_path} — run `git show HEAD:scripts/audit/lint.py` (+ turn_index.py) "
              "into that directory before this selftest")
        return 0, 0
    old = load_module(old_path, "old_lint_w6")
    new = load_module(os.path.join(REPO, "scripts", "audit", "lint.py"), "new_lint_w6")

    os.chdir(REPO)
    pages = sorted(p.replace("\\", "/") for p in glob.glob("wiki/**/*.md", recursive=True)
                   if "/sources/" in p.replace("\\", "/"))

    def row_of(mod, path):
        fm, body, text = mod.parse(path)
        slug = os.path.basename(path)[:-3]
        kind = mod.kind_of(fm, body, slug, path)
        C = mod.grade(path, fm, body, text, kind, MAIN_ROOT)
        sf = fm.get("source_file", ""); anchor_range = mod.NA_KIND
        raw_abs = os.path.join(MAIN_ROOT, sf) if sf and sf.lower() != "none" else None
        anchors = sorted(set(int(n) for n in re.findall(r":T(\d+)", text)))
        if anchors and raw_abs and os.path.isfile(raw_abs):
            try:
                count = mod.turn_index.index(raw_abs)["turn_count"]
                oor = [n for n in anchors if n > count]
                anchor_range = mod.FAIL if oor else mod.PASS
            except Exception:
                anchor_range = "ERR"
        conformant = all(v in mod.NON_FAIL for v in C.values()) and anchor_range in mod.NON_FAIL
        return dict(kind=kind, C=C, anchor_range=anchor_range, conformant=conformant)

    diffs = []
    for path in pages:
        r_old = row_of(old, path)
        r_new = row_of(new, path)
        if r_old != r_new:
            diffs.append((path, r_old, r_new))

    print(f"  pages compared: {len(pages)}")
    print(f"  diffs: {len(diffs)}")
    for path, ro, rn in diffs[:10]:
        print(f"    DIFF {path}\n      old={ro}\n      new={rn}")
    check("regression: 0 diffs across all /sources/ pages, old vs new lint.py (no --all-kinds)",
          len(diffs) == 0, f"{len(diffs)} of {len(pages)} pages differ")
    return len(pages), len(diffs)


# ================================================================================================
# PART 2 — new-kind fixtures, run through the real lint.py CLI over a synthetic tree
# ================================================================================================

def build_fixture_tree():
    tmp = tempfile.mkdtemp(prefix="w6_lint_fixtures_")
    audit_src = os.path.join(REPO, "scripts", "audit")
    shutil.copy(os.path.join(audit_src, "lint.py"), os.path.join(tmp, "lint.py"))
    shutil.copy(os.path.join(audit_src, "turn_index.py"), os.path.join(tmp, "turn_index.py"))

    def w(relpath, content):
        full = os.path.join(tmp, relpath)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        # newline="" so Windows text mode does not translate \n -> \r\n underneath us — the E8
        # fixture hashes `raw_body` with hashlib BEFORE writing, so the bytes on disk must match
        # exactly what was hashed or the fixture's own "hash matches" assertion is unwinnable.
        with open(full, "w", encoding="utf-8", newline="") as f:
            f.write(content)

    for d in ["wiki/concepts", "wiki/entities", "wiki/patterns", "wiki/references",
              "skills/sampleskill", "skills/otherskill"]:
        os.makedirs(os.path.join(tmp, d), exist_ok=True)

    w("dummy1.txt", "locator target 1\n")
    w("dummy2.txt", "locator target 2\n")
    w("skills/sampleskill/SKILL.md", "---\nname: sampleskill\n---\nstub\n")
    w("skills/otherskill/SKILL.md", "---\nname: otherskill\n---\nstub\n")

    raw_body = "## Human [00:00:00.000000Z]\nHello.\n\n## Assistant [00:00:01.000000Z]\nWorld.\n"
    w("raw_dummy.md", raw_body)
    raw_sha = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()

    common = ("format: cfl-page/v1\nsource_kind: synthesis\nsource_file: none\n"
              "retrieval_key: fixture\naliases: [fixture]\ngenerated_by: selftest_lint_kinds.py\n")

    # good-pattern: PASS everything, incl. E9 (2 resolving locators + [SKILL: sampleskill]) and E10
    w("wiki/patterns/good-pattern.md", f"""---
kind: pattern
{common}date: 2026-09-02
probe_sealed: "does this fixture pass? => yes, TRUSTED"
---

## Struggle

- `dummy1.txt:1` [verbatim] — first locator, resolves.
- `dummy2.txt:2` [contextual] — second locator, resolves.

## Motivates

[SKILL: sampleskill] — the sample skill this fixture pattern motivates.

## Generalization

See also [[good-concept]] for the generic-kind counterpart of this fixture set.
""")

    # bad-pattern-e9: only ONE Struggle locator -> planted failure, must FAIL E9
    w("wiki/patterns/bad-pattern-e9.md", f"""---
kind: pattern
{common}date: 2026-09-02
probe_sealed: "does this fixture pass? => no, TRUSTED"
---

## Struggle

- `dummy1.txt:1` [verbatim] — only one locator, planted failure (needs >= 2).

## Motivates

none yet
""")

    # good-entity: >=2 resolving [[slug]] links -> PASS E9
    w("wiki/entities/good-entity.md", f"""---
kind: entity
{common}date: 2026-09-02
probe_sealed: "does this fixture pass? => yes, TRUSTED"
---

## What it is

Links to [[good-pattern]] and [[good-concept]], both of which exist in this fixture tree.
""")

    # good-concept: generic PASS; source_file none -> E2/E3/E4/E8 N/A-kind, E9 N/A-kind (not a
    # pattern/entity/purpose kind)
    w("wiki/concepts/good-concept.md", f"""---
kind: concept
{common}date: 2026-09-02
probe_sealed: "does this fixture pass? => yes, TRUSTED"
---

## Definition

A fixture concept page with a real heading and a [[good-pattern]] link.
""")

    # bad-e10-concept: qualifying date, NO probe_sealed field at all -> planted failure, FAIL E10 only
    w("wiki/concepts/bad-e10-concept.md", f"""---
kind: concept
{common}date: 2026-09-02
---

## Definition

Missing probe_sealed entirely — planted failure for E10_probe.
""")

    # good-reference: generic PASS
    w("wiki/references/good-reference.md", f"""---
kind: reference
{common}date: 2026-09-02
probe_sealed: "does this fixture pass? => yes, TRUSTED"
---

## Reference

A fixture reference page, linking [[good-concept]] to satisfy E5_link.
""")

    # good-fidelity-qualifier: source_file resolves (E2/E3/E4/E8 all gradable); fidelity tag
    # carries a comma-qualifier ("[verbatim, cropped]") that the PRE-W-6 E3 regex did not match
    w("wiki/concepts/good-fidelity-qualifier.md", f"""---
kind: concept
format: cfl-page/v1
source_kind: synthesis
source_file: raw_dummy.md
retrieval_key: fixture
aliases: [fixture]
generated_by: selftest_lint_kinds.py
date: 2026-09-02
raw_sha256: {raw_sha}
probe_sealed: "does this fixture pass? => yes, TRUSTED"
uncaptured_assessed: populated
---

## Definition

Cites raw_dummy.md ([good-fidelity-qualifier:T1]). Fidelity tag with a comma-qualifier, which the
pre-W-6 E3 regex did NOT match: [verbatim, cropped].

raw_length: {len(raw_body)} chars
""")

    # good-purpose (skills/sampleskill/PURPOSE.md): motivating_pattern resolves -> PASS E9
    w("skills/sampleskill/PURPOSE.md", f"""---
format: cfl-purpose/v1
kind: purpose
skill: sampleskill
motivating_pattern: [[good-pattern]]
{common}date: 2026-09-02
probe_sealed: "does this fixture pass? => yes, TRUSTED"
---

## Why this skill exists

Fixture purpose page whose motivating_pattern resolves to wiki/patterns/good-pattern.md.
""")

    # bad-purpose-e9 (skills/otherskill/PURPOSE.md): motivating_pattern is PROSE, not [[..]]/UNKNOWN
    w("skills/otherskill/PURPOSE.md", f"""---
format: cfl-purpose/v1
kind: purpose
skill: otherskill
motivating_pattern: some pattern I have not linked properly
{common}date: 2026-09-02
probe_sealed: "does this fixture pass? => no, TRUSTED"
---

## Why this skill exists

Planted failure: motivating_pattern is prose, not a resolving [[slug]] or the literal UNKNOWN.
""")

    return tmp


def run_lint(tmp, args):
    r = subprocess.run([sys.executable, "lint.py"] + args, cwd=tmp,
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout + r.stderr


def parse_explain(output):
    d = {}
    for line in output.splitlines():
        s = line.strip()
        m = re.match(r"^(E\d+\w*)\s+(\S+)", s)
        if m:
            d[m.group(1)] = m.group(2)
        if s.startswith("CONFORMANT:"):
            d["CONFORMANT"] = s.split(":", 1)[1].strip()
    return d


def fixture_checks():
    print("\n=== PART 2: new-kind fixtures (synthetic tree, subprocess through real lint.py) ===")
    tmp = build_fixture_tree()
    try:
        def explain(slug, all_kinds=True):
            args = (["--all-kinds"] if all_kinds else []) + ["--main-root", tmp, "--explain", slug]
            return parse_explain(run_lint(tmp, args))

        d = explain("good-pattern")
        check("good-pattern: E9_backref PASS", d.get("E9_backref") == "PASS", str(d))
        check("good-pattern: E10_probe PASS", d.get("E10_probe") == "PASS", str(d))
        check("good-pattern: CONFORMANT True", d.get("CONFORMANT") == "True", str(d))

        d = explain("bad-pattern-e9")
        check("bad-pattern-e9 (1 locator, planted): E9_backref FAIL", d.get("E9_backref") == "FAIL", str(d))

        d = explain("good-entity")
        check("good-entity: E9_backref PASS (>=2 resolving [[slug]])", d.get("E9_backref") == "PASS", str(d))

        d = explain("good-concept")
        check("good-concept: E9_backref N/A-kind (not pattern/entity/purpose)",
              d.get("E9_backref") == "N/A-kind", str(d))
        check("good-concept: CONFORMANT True", d.get("CONFORMANT") == "True", str(d))

        d = explain("bad-e10-concept")
        check("bad-e10-concept (no probe_sealed, planted): E10_probe FAIL", d.get("E10_probe") == "FAIL", str(d))

        d = explain("good-reference")
        check("good-reference: CONFORMANT True", d.get("CONFORMANT") == "True", str(d))

        d = explain("good-fidelity-qualifier")
        check("good-fidelity-qualifier: E3_fidelity PASS ('[verbatim, cropped]' now matches)",
              d.get("E3_fidelity") == "PASS", str(d))
        check("good-fidelity-qualifier: E8_fixity PASS (recomputed hash matches)",
              d.get("E8_fixity") == "PASS", str(d))

        d = explain("sampleskill")  # skills/sampleskill/PURPOSE.md, slug = skill dir name
        check("sampleskill PURPOSE.md (motivating_pattern resolves): E9_backref PASS",
              d.get("E9_backref") == "PASS", str(d))

        d = explain("otherskill")  # skills/otherskill/PURPOSE.md, planted failure
        check("otherskill PURPOSE.md (motivating_pattern is prose, planted): E9_backref FAIL",
              d.get("E9_backref") == "FAIL", str(d))

        # --explain must never return silence, on an out-of-scope page or a real one, with or
        # without --all-kinds (W-1's finding: a patterns page returned nothing under the old code).
        out = run_lint(tmp, ["--main-root", tmp, "--explain", "good-pattern"])  # no --all-kinds
        check("--explain (no --all-kinds) on a patterns page prints OUT-OF-SCOPE, not silence",
              "OUT-OF-SCOPE" in out, out.strip()[:200])

        out = run_lint(tmp, ["--main-root", tmp, "--explain", "no-such-page-anywhere-xyz"])
        check("--explain on a nonexistent slug prints OUT-OF-SCOPE, not silence",
              "OUT-OF-SCOPE" in out, out.strip()[:200])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    n_pages, n_diffs = regression_check()
    fixture_checks()
    print(f"\n=== SUMMARY: {len(FAILS)} failing check(s) of the selftest's own assertions ===")
    print(f"  regression: {n_pages} /sources/ pages compared, {n_diffs} diffs")
    if FAILS:
        for f in FAILS:
            print(f"  FAIL: {f}")
        sys.exit(1)
    print("  ALL PASS")


if __name__ == "__main__":
    main()
