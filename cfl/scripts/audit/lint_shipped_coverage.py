"""Criterion 2a for the CFL half: does the artifact COVER what it claims, format-independently?

WHY THIS EXISTS -- Professional, 2026-09-13 01:0x, declining to port their own coverage lint:
*"C2 and C10 consume index_gen.py against Professional's wiki/index.md conventions, so pointing them
at your index would grade your format against my rule and report noise as findings."* That was the
right call -- noise in a criterion gets argued about instead of fixed -- and it left coverage for
cfl/ as UNKNOWN with my name and a 22:00 clock.

So the three checks below are chosen to be FORMAT-INDEPENDENT: none of them knows what a CFL index
row or a Professional index row looks like. Each asks a question any derived tree can answer.

  A. REACHABILITY   -- is every shipped .md reachable from the tree's own declared entry points?
                       A page nothing points at is on the disk, not in the artifact.
  B. CITATIONS      -- is every path a shipped file cites either PRESENT in the tree or NAMED in
                       DERIVATION-LOG.md? This is expected to FAIL: 61 of 88 excluded files are
                       referred to by name from 792 places. The point is that the number is measured
                       and disclosed rather than discovered by a reader following a dead citation.
  C. SPEC LIVENESS  -- did every include-spec row produce at least one file? A row that ships nothing
                       is a rule nobody has tested, and it reads as coverage.

⚠️ WHAT THIS IS NOT: it does not grade whether the content is GOOD, whether the index is well
organised, or whether a page SHOULD be reachable. `wiki_reachability.py` (2026-09-12) already learned
that lesson the hard way in this trunk -- three definitions produced 94%, 83% and 25% over one tree in
one night -- so this reports reachability and never prescribes a link.

⛔ AND IT IS EXPECTED TO FAIL ON FIRST RUN. A coverage lint that passes the moment it is written has
been calibrated to the artifact instead of to the claim.

Usage:
    python scripts/audit/lint_shipped_coverage.py --tree N:/claude-pr4/cfl
    python scripts/audit/lint_shipped_coverage.py --selftest
Exit: 0 all three clean | 3 at least one finding | 4 could not run (UNKNOWN)
"""
import argparse
import os
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Entry points a derived tree can declare without the lint knowing its conventions: a root README,
# an index, and any tracker map that says it is live. Absence of all of them is UNKNOWN, not a pass.
ENTRY_CANDIDATES = ("README.md", "wiki/index.md", "index.md", "wiki/README.md")
# Link forms this corpus actually uses. Learned 2026-09-12: CFL's index.md has ZERO wikilinks and
# ZERO markdown links -- it cites every page as a BACKTICKED PATH -- and a guard that stripped inline
# backticks destroyed three quarters of the link graph before anyone noticed.
LINK_RX = (
    re.compile(r"\[\[([^\]|#]+)"),                       # [[slug]]
    re.compile(r"\]\(([^)\s#]+\.md)"),                   # [text](path.md)
    re.compile(r"`([A-Za-z0-9_./-]+\.md)`"),             # `path.md`  <- the one that matters here
    re.compile(r"(?<![`\[(])\b([A-Za-z0-9_./-]+\.md)\b"),  # bare path.md
)
CITED_PATH_RX = re.compile(r"`([A-Za-z0-9_./-]{4,}\.(?:md|py|sh|txt|json|sqlite))`")


def md_files(root: Path):
    return sorted(p for p in root.rglob("*.md") if p.is_file()
                  and "__pycache__" not in p.parts)


def targets_in(text: str):
    out = set()
    for rx in LINK_RX:
        for m in rx.finditer(text):
            out.add(m.group(1).strip())
    return out


def check_reachability(root: Path):
    entries = [root / e for e in ENTRY_CANDIDATES if (root / e).is_file()]
    # plus any tracker file declaring itself live -- derived, never hardcoded (CLAUDE.md's rule)
    for p in (root / "wiki" / "tracker").glob("*.md") if (root / "wiki" / "tracker").is_dir() else []:
        head = p.read_text(encoding="utf-8", errors="replace")[:600]
        if re.search(r"^status:\s*\"?LIVE", head, re.M):
            entries.append(p)
    if not entries:
        return "UNKNOWN", "no entry point found (README.md / wiki/index.md / a LIVE tracker map)", []
    all_md = md_files(root)
    by_rel = {str(p.relative_to(root)).replace(os.sep, "/"): p for p in all_md}
    by_stem = {}
    for rel in by_rel:
        by_stem.setdefault(Path(rel).stem, []).append(rel)
    seen, frontier = set(), []
    for e in entries:
        rel = str(e.relative_to(root)).replace(os.sep, "/")
        seen.add(rel)
        frontier.append(rel)
    while frontier:
        rel = frontier.pop()
        p = by_rel.get(rel)
        if p is None:
            continue
        for t in targets_in(p.read_text(encoding="utf-8", errors="replace")):
            hits = []
            if t in by_rel:
                hits = [t]
            elif t.endswith(".md") and Path(t).name in {Path(r).name for r in by_rel}:
                hits = [r for r in by_rel if Path(r).name == Path(t).name]
            elif t in by_stem:
                hits = by_stem[t]
            for h in hits:
                if h not in seen:
                    seen.add(h)
                    frontier.append(h)
    unreachable = sorted(r for r in by_rel if r not in seen)
    pct = 100.0 * (len(by_rel) - len(unreachable)) / max(1, len(by_rel))
    verdict = "CLEAN" if not unreachable else "FINDING"
    return verdict, (f"{len(by_rel) - len(unreachable):,} of {len(by_rel):,} shipped .md reachable "
                     f"from {len(entries)} entry point(s) = {pct:.1f}%"), unreachable


def check_citations(root: Path):
    log = root / "DERIVATION-LOG.md"
    logged = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    if not logged:
        return "UNKNOWN", "no DERIVATION-LOG.md -- cannot tell a withheld path from a broken one", []
    present = {str(p.relative_to(root)).replace(os.sep, "/") for p in root.rglob("*") if p.is_file()}
    # the artifact's declared scope is the set of top-level directories it actually ships
    in_scope = tuple(sorted({q.split("/")[0] + "/" for q in present if "/" in q}))
    dead, out_of_scope = {}, {}
    for p in md_files(root):
        text = p.read_text(encoding="utf-8", errors="replace")
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        for m in CITED_PATH_RX.finditer(text):
            t = m.group(1)
            if t in present or t.startswith(("http", "~", "/")) or ":" in t:
                continue
            if t in logged:                      # withheld ON PURPOSE and disclosed
                continue
            # Two classes here too, and the first run lumped them into one number of 838. A path the
            # spec NEVER CONSIDERED is not the same defect as one it withheld: the first is a citation
            # reaching outside the artifact's declared scope, which the scope note already discloses;
            # the second is a hole INSIDE it. Only the second belongs beside the 792.
            if not any(t.startswith(pre) for pre in in_scope):
                out_of_scope.setdefault(t, []).append(rel)
                continue
            dead.setdefault(t, []).append(rel)
    verdict = "CLEAN" if not dead else "FINDING"
    return verdict, (f"{len(dead):,} cited path(s) INSIDE scope are neither present nor named in "
                     f"DERIVATION-LOG.md, across {sum(len(v) for v in dead.values()):,} citation(s); "
                     f"plus {len(out_of_scope):,} cited path(s) the spec never considered at all "
                     f"(outside scope -- disclosed, not a hole)"), \
           [f"{k}  <- cited by {len(v)} file(s), e.g. {v[0]}" for k, v in sorted(dead.items())]


def check_spec_liveness(root: Path, spec_path: Path):
    if not spec_path.is_file():
        return "UNKNOWN", f"no spec at {spec_path}", []
    present = {str(p.relative_to(root)).replace(os.sep, "/") for p in root.rglob("*") if p.is_file()}
    dead = []
    for ln in spec_path.read_text(encoding="utf-8", errors="replace").split(chr(10)):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        bits = ln.split()
        key, rest = bits[0], bits[1:]
        hit = False
        if key == "EXACT_INCLUDE" and rest:
            hit = rest[0] in present
        elif key == "PREFIX_INCLUDE" and rest:
            hit = any(p.startswith(rest[0]) for p in present)
        elif key == "SUFFIX_UNDER" and len(rest) == 2:
            hit = any(p.startswith(rest[0]) and p.endswith(rest[1]) for p in present)
        elif key == "BASENAME_UNDER" and len(rest) == 3:
            hit = any(p.startswith(rest[0]) and Path(p).name == rest[2] for p in present)
        else:
            continue
        if not hit:
            # A row dies for two very different reasons and lumping them hides the useful one: the
            # target may not exist at source (a stale rule), or it may exist and be WITHHELD by the
            # exclusion list -- a spec contradicting its own fence. [2026-09-13: the first real
            # finding was the second kind: INGEST-LEDGER.md asked for by an include and cut by
            # CONTENT-CARD on four Luhn-valid numbers.]
            why = "no file matched"
            log = root / "DERIVATION-LOG.md"
            if log.is_file() and rest:
                if rest[0] in log.read_text(encoding="utf-8", errors="replace"):
                    why = "CONTRADICTED: the target is WITHHELD by the exclusion list"
            dead.append(ln + "   [" + why + "]")
    verdict = "CLEAN" if not dead else "FINDING"
    return verdict, (f"{len(dead):,} spec row(s) produced NO file; a row marked CONTRADICTED is a "
                     f"spec asking for what its own fence refuses"), dead


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--spec", default=str(Path(__file__).with_name("public_include_cfl.txt")))
    ap.add_argument("--list", type=int, default=8)
    a = ap.parse_args()
    root = Path(a.tree)
    if not root.is_dir():
        print(f"UNKNOWN -- no tree at {root}")
        return 4
    print("=== criterion 2a (CFL half): coverage, format-independent ===")
    print(f"tree : {root}")
    print()
    rc = 0
    for name, (v, detail, rows) in (
            ("A REACHABILITY", check_reachability(root)),
            ("B CITATIONS   ", check_citations(root)),
            ("C SPEC LIVENESS", check_spec_liveness(root, Path(a.spec)))):
        print(f"{name}  {v} -- {detail}")
        for r in rows[:a.list]:
            print(f"      {r[:120]}")
        if len(rows) > a.list:
            print(f"      ... and {len(rows) - a.list:,} more")
        print()
        if v == "FINDING":
            rc = 3
        elif v == "UNKNOWN" and rc == 0:
            rc = 3
    print("B is EXPECTED to have findings: 61 of 88 excluded files are cited by name from 792 places,")
    print("and disclosing that number is the whole point. A coverage lint that passes the day it is")
    print("written has been calibrated to the artifact instead of to the claim.")
    return rc


def selftest():
    import tempfile
    fails = []
    NL = chr(10)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "wiki").mkdir()
        (t / "README.md").write_text("see `wiki/a.md` and `wiki/gone.md`" + NL, encoding="utf-8")
        (t / "wiki" / "a.md").write_text("hello" + NL, encoding="utf-8")
        (t / "wiki" / "orphan.md").write_text("nobody points here" + NL, encoding="utf-8")
        (t / "DERIVATION-LOG.md").write_text("| `wiki/gone.md` | PATH_EXACT | 0 | |" + NL,
                                             encoding="utf-8")
        v, d, rows = check_reachability(t)
        if v != "FINDING" or "wiki/orphan.md" not in rows:
            fails.append(f"A: orphan not found ({v}, {rows})")
        if "wiki/a.md" in rows:
            fails.append("A: a page reached by a BACKTICKED PATH was called unreachable -- the exact "
                         "defect that produced 83% on 2026-09-12")
        v2, d2, rows2 = check_citations(t)
        if v2 != "CLEAN":
            fails.append(f"B: a cited-but-WITHHELD path must not be a finding when the log names it "
                         f"({v2}: {rows2})")
        (t / "wiki" / "b.md").write_text("see `wiki/never.md`" + NL, encoding="utf-8")
        (t / "README.md").write_text("see `wiki/a.md` `wiki/b.md` `wiki/orphan.md` `wiki/gone.md`" + NL,
                                     encoding="utf-8")
        v3, d3, rows3 = check_citations(t)
        if v3 != "FINDING" or not any("wiki/never.md" in r for r in rows3):
            fails.append(f"B: a cited path that is neither present nor logged was not reported ({v3})")
        spec = t / "spec.txt"
        spec.write_text("PREFIX_INCLUDE wiki/" + NL + "PREFIX_INCLUDE nothing/" + NL, encoding="utf-8")
        v4, d4, rows4 = check_spec_liveness(t, spec)
        if v4 != "FINDING" or not any("nothing/" in r for r in rows4):
            fails.append(f"C: a spec row producing nothing was not reported ({v4}, {rows4})")
        if any("wiki/" == r.split()[-1] for r in rows4):
            fails.append("C: a productive row was reported as dead")
        v5, _, _ = check_reachability(t / "nope")
        if v5 != "UNKNOWN":
            fails.append("A: a missing tree did not return UNKNOWN")
    for f in fails:
        print("  FAIL " + f)
    print(f"selftest: {'PASS' if not fails else 'FAIL'} -- 6 assertions incl. the backticked-path arm, "
          f"{len(fails)} failure(s)")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
