#!/usr/bin/env python3
"""S-DEDUP: collapse parallel-fork duplicate source pages onto one canonical page.

Problem this fixes: parallel synthesis forks land 2-3 wiki/sources/**/*.md pages for
the SAME underlying session, each under a different slug that happens to share the
session's trailing uuid6 (filename ends `-<uuid6>.md`). This script:

  1. Groups wiki/sources/**/*.md by trailing uuid6.
  2. For every group with >1 page, picks one CANONICAL page by, in order:
       a. already `state: current` AND lint-CONFORMANT (scripts/audit/lint.py
          --explain <slug>, run with --main-root N:/claude-corpus/cfl)
       b. higher count of `:T<n>` citation anchors in the page text
       c. more `[[slug]]` wikilinks in the page text
       d. earlier mtime
  3. Writes frontmatter-only edits:
       - every non-canonical page gets `state: superseded`,
         `superseded_by: <canonical-slug>`, and a `state_note:` explaining why.
       - the canonical page gets `supersedes: [<other-slug>, ...]` appended/updated.
     NOTHING IS EVER DELETED OR RENAMED ("Yeah no deletion" — Jon's standing ruling).
     Re-running is safe: the script recomputes canonical/superseded state each time
     and overwrites only its own fields, so new duplicate pages landing later are
     picked up on the next run without disturbing earlier decisions' file identity.

Usage:
    python scripts/audit/source_dedupe.py --dry-run
    python scripts/audit/source_dedupe.py --apply
    python scripts/audit/source_dedupe.py --selftest
    python scripts/audit/source_dedupe.py --selftest --prove-guard   # must FAIL

Run from repo root. Never touches G:\\; --main-root for lint defaults to the
read-only corpus mirror N:/claude-corpus/cfl per this lane's rules.
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LINT_PY = os.path.join(SCRIPT_DIR, "lint.py")
DEFAULT_ROOT = "wiki/sources"
DEFAULT_MAIN_ROOT = "N:/claude-corpus/cfl"

UUID6_RE = re.compile(r"-([a-f0-9]{6})$")
# NOTE: deliberately does NOT match a trailing "-cont" suffix. "-cont" is this
# wiki's established convention for a legitimate, intentional continuation
# page covering a different turn range of the SAME source session (verified
# 2026-09-02 against f8cc02/da51cc/090a56 — each "-cont" page's own title says
# "continuation" and cites a disjoint tracker-item range). That is not the
# accidental-parallel-fork duplication this script exists to fix, so "-cont"
# pages are excluded from grouping entirely rather than auto-merged.
TANCHOR_RE = re.compile(r":T\d+")
WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
FM_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")

sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Frontmatter helpers — line-based, deliberately dumb. We only ever touch a
# small closed set of top-level scalar/list keys and must never disturb any
# other line (multi-line aliases, quoted titles, etc.) in the frontmatter.
# ---------------------------------------------------------------------------

def read_text(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def frontmatter_span(text):
    """Return (start_of_fm_body, end_of_fm_body_exclusive_of_closing---) or None."""
    if not text.startswith("---"):
        return None
    e = text.find("\n---", 3)
    if e == -1:
        return None
    return 4, e  # text[4:e] is the frontmatter body (after the first '---\n')


def slug_of(path):
    return os.path.basename(path)[:-3]


def uuid6_of(slug):
    m = UUID6_RE.search(slug)
    return m.group(1) if m else None


def set_fm_field(text, key, value):
    """Set/replace a single-line top-level frontmatter key, else insert it just
    before the closing '---'. `value` is the RAW string to place after 'key: '.
    Never touches any other line."""
    span = frontmatter_span(text)
    if span is None:
        raise ValueError("no frontmatter block found")
    start, end = span
    fm_body = text[start:end]
    lines = fm_body.split("\n")
    new_line = f"{key}: {value}"
    found = False
    for i, line in enumerate(lines):
        m = FM_KEY_RE.match(line)
        if m and m.group(1) == key:
            lines[i] = new_line
            found = True
            break
    if not found:
        # Insert right before the trailing blank/close, i.e. append at end of
        # the frontmatter body (which does not include the closing '---').
        # Strip one trailing empty element (split leaves '' if fm_body ends
        # with \n right before '---').
        if lines and lines[-1] == "":
            lines.insert(len(lines) - 1, new_line)
        else:
            lines.append(new_line)
    new_fm_body = "\n".join(lines)
    return text[:start] + new_fm_body + text[end:]


def get_fm_field(text, key):
    span = frontmatter_span(text)
    if span is None:
        return None
    start, end = span
    for line in text[start:end].split("\n"):
        m = FM_KEY_RE.match(line)
        if m and m.group(1) == key:
            return m.group(2).strip()
    return None


# ---------------------------------------------------------------------------
# Lint integration
# ---------------------------------------------------------------------------

def lint_conformant(slug, main_root=DEFAULT_MAIN_ROOT, lint_py=LINT_PY):
    """Run lint.py --explain <slug> and return True/False for CONFORMANT on the
    block whose header line is exactly `slug`. Returns False (never crashes the
    dedupe run) if lint.py errors or the slug isn't found."""
    try:
        out = subprocess.run(
            [sys.executable, lint_py, "--main-root", main_root, "--explain", slug],
            capture_output=True, text=True, timeout=120,
        ).stdout
    except Exception:
        return False
    blocks = re.split(r"\n(?=\S)", out.strip())
    for b in blocks:
        lines = b.splitlines()
        if not lines:
            continue
        if lines[0].strip() == slug:
            return "CONFORMANT: True" in b
    return False


# ---------------------------------------------------------------------------
# Grouping + canonical selection
# ---------------------------------------------------------------------------

def discover_groups(root):
    """Return {uuid6: [path, ...]} for every wiki/sources/**/*.md file whose
    slug ends in a 6-hex-digit uuid, restricted to groups with >1 page."""
    paths = sorted(glob.glob(os.path.join(root, "**", "*.md"), recursive=True))
    groups = {}
    for p in paths:
        p = p.replace("\\", "/")
        u = uuid6_of(slug_of(p))
        if u is None:
            continue
        groups.setdefault(u, []).append(p)
    return {u: ps for u, ps in groups.items() if len(ps) > 1}


def page_metrics(path, main_root):
    text = read_text(path)
    slug = slug_of(path)
    state = get_fm_field(text, "state")
    tier1 = (state == "current") and lint_conformant(slug, main_root=main_root)
    anchors = len(TANCHOR_RE.findall(text))
    links = len(WIKILINK_RE.findall(text))
    mtime = os.path.getmtime(path)
    return dict(path=path, slug=slug, tier1=tier1, anchors=anchors,
                links=links, mtime=mtime)


def choose_canonical(group_paths, main_root):
    metrics = [page_metrics(p, main_root) for p in group_paths]
    metrics.sort(key=lambda m: (not m["tier1"], -m["anchors"], -m["links"], m["mtime"]))
    canonical = metrics[0]
    others = metrics[1:]
    return canonical, others


# ---------------------------------------------------------------------------
# Plan / apply
# ---------------------------------------------------------------------------

def build_plan(root, main_root):
    """Returns list of dicts: {uuid6, canonical_slug, canonical_path,
    superseded: [(slug, path), ...]}"""
    plan = []
    for uuid6, paths in sorted(discover_groups(root).items()):
        canonical, others = choose_canonical(paths, main_root)
        plan.append(dict(
            uuid6=uuid6,
            canonical_slug=canonical["slug"],
            canonical_path=canonical["path"],
            superseded=[(m["slug"], m["path"]) for m in others],
        ))
    return plan


def print_plan(plan):
    if not plan:
        print("No duplicate-uuid6 groups found under this root.")
        return
    for item in plan:
        print(f"\n=== session {item['uuid6']} ===")
        print(f"  CANONICAL:  {item['canonical_slug']}")
        for slug, _path in item["superseded"]:
            print(f"  superseded: {slug}")


def apply_plan(plan):
    """Frontmatter-only edits. Never removes/renames a file. Returns list of
    touched paths."""
    touched = []
    for item in plan:
        canonical_path = item["canonical_path"]
        superseded_slugs = [s for s, _ in item["superseded"]]

        # Non-canonical pages: mark superseded.
        for slug, path in item["superseded"]:
            text = read_text(path)
            text = set_fm_field(text, "state", "superseded")
            text = set_fm_field(text, "superseded_by", item["canonical_slug"])
            note = (f'"duplicate of {item["canonical_slug"]} from a parallel fork '
                    f'2026-09-02; kept, not deleted"')
            text = set_fm_field(text, "state_note", note)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            touched.append(path)

        # Canonical page: record what it supersedes.
        ctext = read_text(canonical_path)
        supersedes_val = "[" + ", ".join(superseded_slugs) + "]"
        ctext = set_fm_field(ctext, "supersedes", supersedes_val)
        with open(canonical_path, "w", encoding="utf-8") as f:
            f.write(ctext)
        touched.append(canonical_path)
    return touched


# ---------------------------------------------------------------------------
# Deletion guard demonstration.
#
# apply_plan() above NEVER calls os.remove / os.rename / shutil.* on a source
# page — that is the whole point of this script ("Yeah no deletion"). This
# function exists ONLY so --selftest --prove-guard can demonstrate that the
# selftest's file-count assertion is a real tripwire and not vacuously true:
# it is never called from build_plan()/apply_plan(), only from selftest()
# itself, and only when the env var below is explicitly set.
# ---------------------------------------------------------------------------
_UNSAFE_DELETE_ENV = "S_DEDUP_SELFTEST_PLANT_DELETE"


def _planted_unsafe_delete_for_selftest_only(path):
    if os.environ.get(_UNSAFE_DELETE_ENV) == "1":
        os.remove(path)  # DELIBERATE — selftest-only, proves the count check bites


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest():
    tmp = tempfile.mkdtemp(prefix="source_dedupe_selftest_")
    try:
        root = os.path.join(tmp, "wiki", "sources", "testcat")
        os.makedirs(root, exist_ok=True)

        uuid6 = "ab12cd"

        def page(slug, anchors, links, extra_fm=""):
            body_anchors = " ".join(f"([{slug}:T{n}])" for n in range(1, anchors + 1))
            body_links = " ".join(f"[[link-{i}]]" for i in range(links))
            text = (
                "---\n"
                f"title: \"selftest page {slug}\"\n"
                "trunk: fl\n"
                f"uuid6: {uuid6}\n"
                "source_kind: session\n"
                f"{extra_fm}"
                "---\n\n"
                "## Summary\n\ntest page.\n\n"
                "## Key Claims\n\n"
                f"- claim one [verbatim] {body_anchors} {body_links}\n\n"
                "## Conflicts\n\nnone.\n"
            )
            path = os.path.join(root, f"{slug}-2026-09-02-{uuid6}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return path

        p1 = page("alpha", anchors=1, links=0)
        p2 = page("beta", anchors=3, links=2)  # should win on anchors (no tier1 winner)
        p3 = page("gamma", anchors=2, links=5)

        before_count = len(glob.glob(os.path.join(root, "*.md")))
        assert before_count == 3, f"setup wrong: expected 3 files, got {before_count}"

        # Run the real grouping/selection logic. Use a lint stub that always
        # returns False (tier1 never satisfied) so this is a deterministic,
        # network/subprocess-free selftest of the SELECTION + WRITE logic.
        global lint_conformant
        real_lint = lint_conformant
        lint_conformant = lambda *a, **k: False  # noqa: E731
        try:
            plan = build_plan(os.path.join(tmp, "wiki", "sources"), DEFAULT_MAIN_ROOT)
            assert len(plan) == 1, f"expected 1 group, got {len(plan)}"
            item = plan[0]
            assert item["uuid6"] == uuid6
            # beta has the most :T anchors (3) among non-tier1 pages -> canonical
            assert item["canonical_slug"].startswith("beta-"), \
                f"expected beta-* canonical, got {item['canonical_slug']}"
            assert len(item["superseded"]) == 2

            touched = apply_plan(plan)
            assert len(touched) == 3
        finally:
            lint_conformant = real_lint

        after_count = len(glob.glob(os.path.join(root, "*.md")))
        assert after_count == before_count, (
            f"FILE COUNT CHANGED: before={before_count} after={after_count} "
            "— a dedupe run must never delete or rename a file"
        )

        states = {}
        for f in glob.glob(os.path.join(root, "*.md")):
            t = read_text(f)
            states[slug_of(f)] = get_fm_field(t, "state")

        canon_slug = item["canonical_slug"]
        n_current_or_unset = sum(1 for s, v in states.items()
                                  if s == canon_slug and v != "superseded")
        n_superseded = sum(1 for v in states.values() if v == "superseded")
        assert n_current_or_unset == 1, f"expected 1 non-superseded page, got {n_current_or_unset}"
        assert n_superseded == 2, f"expected 2 superseded pages, got {n_superseded}"

        canon_text = read_text(os.path.join(root, f"{canon_slug}.md"))
        supersedes = get_fm_field(canon_text, "supersedes")
        assert supersedes is not None and "alpha" in supersedes and "gamma" in supersedes, \
            f"canonical page missing correct supersedes list: {supersedes}"

        for slug, v in states.items():
            if slug != canon_slug:
                stext = read_text(os.path.join(root, f"{slug}.md"))
                assert get_fm_field(stext, "superseded_by") == canon_slug
                assert get_fm_field(stext, "state_note") is not None

        print("SELFTEST OK: 1 canonical (beta-*, chosen on :T anchor count), "
              "2 superseded, file count before==after==3, no file removed, "
              "supersedes/superseded_by cross-links correct.")

        # ---- Prove the guard: with the plant enabled, deletion happens and
        # the file-count assertion below is EXPECTED TO FAIL. This is only
        # reached when the caller explicitly opts in via --prove-guard.
        if os.environ.get(_UNSAFE_DELETE_ENV) == "1":
            victim = os.path.join(root, f"{item['superseded'][0][0]}.md")
            _planted_unsafe_delete_for_selftest_only(victim)
            after_plant_count = len(glob.glob(os.path.join(root, "*.md")))
            assert after_plant_count == before_count, (
                f"GUARD PROOF: file count changed to {after_plant_count} after the "
                f"planted delete (expected {before_count}) — this assertion is "
                "SUPPOSED to fail here; it proves the selftest's count check "
                "actually detects a deletion when one occurs."
            )
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=DEFAULT_ROOT,
                     help=f"root to scan for *.md pages (default {DEFAULT_ROOT})")
    ap.add_argument("--main-root", default=DEFAULT_MAIN_ROOT,
                     help="passed through to lint.py --main-root")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--apply", action="store_true", help="write the frontmatter edits")
    ap.add_argument("--selftest", action="store_true", help="run the scratch-tree selftest")
    ap.add_argument("--prove-guard", action="store_true",
                     help="with --selftest: also prove the count-check catches a "
                          "planted deletion (this run is EXPECTED to fail)")
    args = ap.parse_args()

    if args.selftest:
        if args.prove_guard:
            os.environ[_UNSAFE_DELETE_ENV] = "1"
        try:
            rc = selftest()
        except AssertionError as e:
            print(f"SELFTEST FAILED: {e}")
            return 1
        return rc

    if not args.dry_run and not args.apply:
        args.dry_run = True  # default to safe

    plan = build_plan(args.root, args.main_root)

    if args.dry_run:
        print_plan(plan)
        if args.apply:
            pass
        else:
            return 0

    if args.apply:
        before = len(glob.glob(os.path.join(args.root, "**", "*.md"), recursive=True))
        touched = apply_plan(plan)
        after = len(glob.glob(os.path.join(args.root, "**", "*.md"), recursive=True))
        print(f"\nApplied. Touched {len(touched)} file(s). "
              f"Page count before={before} after={after} (must be equal).")
        for p in touched:
            print(f"  wrote: {p}")
        assert before == after, "FILE COUNT CHANGED ON APPLY — this must never happen"
    return 0


if __name__ == "__main__":
    sys.exit(main())
