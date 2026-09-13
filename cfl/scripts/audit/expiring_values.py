#!/usr/bin/env python3
"""expiring_values.py -- static detector for "a recorded value used as a default that expires".

WHY THIS EXISTS -- dispatch exchange/dispatches/2026-09-05/102953-EXPIRES-1.md, D-ROW FRAME 1.
Five real instances hit this repo in 24 hours, each producing a CONFIDENT WRONG ANSWER (exit 0 /
PASS / silent misfile) rather than a crash:

  1. a G: repo path recorded as a WRITE default -> wrote tracked files into a stale checkout on
     another branch, exit 0
  2. "UNKNOWN-predates-lineage" recorded as the parent -> every lineage row identical, step graded
     PASS
  3. a session id recorded as an export default -> one frozen session exported forever
  4. a project-key glob recorded as a match rule -> every session after a move silently filed as
     another trunk's
  5. `if len(skills) != 42` -> render failed on every real invocation once the 43rd skill landed

The common shape: something TRUE AT WRITE TIME (a path, an id, a count, a date) gets frozen into
code as a default, fallback, or equality guard, and nothing re-derives it. This tool finds
CANDIDATES for that shape. It does not decide which ones are real -- two sibling detectors this
same week (absence_claims.py: reported 310, ~2-4 real; check_secondary_attribution.py: reported
4,195, ~120 real) were withdrawn for publishing an unsampled count. This tool's own count is
NOT to be reported until hand-graded (see EXPIRES-1 exchange letter for the sampling result).

WHAT IT FLAGS (five categories, matching the dispatch table):
  abs_path_default   -- an absolute drive/tree path used as a default, fallback, or hardcoded
                         constant assigned to a DEFAULT/ROOT/PATH/DIR-named variable
  project_key        -- a sanitized-cwd project key (G--My-Drive-..., N--claude-...) used the
                         same way
  hardcoded_id       -- a UUID, commit sha, or ticket id used as a *default* (not a citation)
  magic_count_guard   -- `!= N` / `== N` (N >= 2, not an HTTP status) inside an `if`/`while` test,
                         comparing to something that looks countable, outside a test/selftest fn
  date_threshold      -- a YYYY-MM-DD literal compared with <, <=, >, >= (used as a cutoff, not
                         just recorded)

WHAT IT DELIBERATELY DOES NOT FLAG (the harder half -- see dispatch table "what not to flag"):
  - Anything inside a docstring. A provenance citation ("wiki/x.md:88 proves where this rule
    came from") lives in a docstring in this repo's convention; docstrings are citation-shaped
    by construction and are never inspected for these categories.
  - Any string literal that itself contains a `<file-ext>:<digits>` citation pattern
    (e.g. "...check_x.py:88") -- a citation is not a default, regardless of where it sits.
  - Anything inside a function named self_check*/self_test/selftest/test_*/*_test (this repo's
    full selftest-naming convention -- a bare "test" substring check misses `self_check_*`, which
    is the same fixture shape under a different name), or inside an `assert` statement (asserts
    are overwhelmingly fixture checks in this repo's convention).
  - Anything at all inside a whole file named test_*.py or selftest_*.py -- a module-level
    constant in such a file (e.g. a synthetic fixture UUID) has no enclosing function for the
    rule above to key on, so the file itself is the fixture boundary.
  - `len(sys.argv) != N` / `len(argv) != N` -- argument-count parsing, not a recorded claim.
  - Common HTTP status codes (200/201/204/400/401/403/404/429/500/503) in magic_count_guard.
  - A bare module-level constant assignment that IS the source of truth (e.g. `VERSION = "1.0"`)
    with no comparison anywhere -- only a *use* as a threshold/guard is flagged, not a definition.

Usage:  python scripts/audit/expiring_values.py [--root DIR] [--json] [--self-test]
Exit:   0 ran clean (findings may be nonzero -- this is a detector, not a gate), 1 self-test
        failure, 2 not a valid root / no files found.
"""
import argparse
import ast
import json
import os
import random
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ABS_PATH_RE = re.compile(r"^[A-Za-z]:[\\/]|^/home/|^/Users/")
PROJECT_KEY_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9]*--[A-Za-z0-9][A-Za-z0-9.\-]{8,}\b")
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
SHA_RE = re.compile(r"\b[0-9a-fA-F]{7,40}\b")
TICKET_RE = re.compile(r"\b(?:T|PR|OI|SG|AG|CFL-D|M)-\d{1,4}\b")
CITATION_LINEREF_RE = re.compile(r"\.(py|md|jsonl|sh|json|txt):\d+")
DATE_LIT_RE = re.compile(r"\b(19|20)\d{2}-\d{2}-\d{2}\b")
DEFAULTISH_NAME_RE = re.compile(r"(DEFAULT|ROOT|FALLBACK|_PATH$|_DIR$|^PATH|^DIR)", re.I)
IDISH_NAME_RE = re.compile(r"(SESSION|COMMIT|SHA|SEED|_ID$|^ID)", re.I)
HTTP_STATUS = {200, 201, 204, 301, 302, 400, 401, 403, 404, 405, 409, 429, 500, 502, 503}

# Function names this repo's convention uses for self-test / fixture-check bodies. The old rule
# only matched a bare substring "test" -- it misses `self_check`, `self_check_population`, etc.,
# which are the SAME shape (assertions over a fixture) under a different name, live in this repo
# in coverage_census.py, alignment_map.py, barrier_consequent.py, disposition_resolves.py,
# feed_liveness.py, lane_precondition.py, reader_cost.py, trace_forward.py.
TEST_FN_NAME_RE = re.compile(r"(^|_)(self_check|self_test|selftest|test)(_|$)", re.I)

# Whole-file fixture convention: a module named test_*.py / selftest_*.py IS a fixture module --
# its module-level constants (e.g. a synthetic SESSION_ID used only inside that fixture) are not
# "recorded values that expire," they are deliberately-fake test data. The function-name rule
# above only excludes assignments INSIDE a function; a module-level constant in such a file has
# no enclosing function at all and needs this separate, filename-keyed mechanism.
TEST_FILE_RE = re.compile(r"(^|[\\/])(test_|selftest_)[^\\/]*\.py$|(^|[\\/])selftest\.py$", re.I)

CATEGORIES = ("abs_path_default", "project_key", "hardcoded_id", "magic_count_guard", "date_threshold")


def add_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node


def enclosing_function_name(node):
    n = node
    while n is not None:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return n.name
        n = getattr(n, "parent", None)
    return None


def is_docstring(node):
    """True if `node` (a Constant str) is the sole expression statement leading a
    Module/ClassDef/FunctionDef body -- i.e. a docstring."""
    parent = getattr(node, "parent", None)
    if not isinstance(parent, ast.Expr):
        return False
    grandparent = getattr(parent, "parent", None)
    if not isinstance(grandparent, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    body = grandparent.body
    return bool(body) and body[0] is parent


def in_assert(node):
    n = node
    while n is not None:
        if isinstance(n, ast.Assert):
            return True
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            return False
        n = getattr(n, "parent", None)
    return False


def in_test_function(node):
    name = enclosing_function_name(node)
    return bool(name) and bool(TEST_FN_NAME_RE.search(name))


def is_default_context(node, extra_name_re=None):
    """Is this Constant node used as a default/fallback value, rather than plain code?
    Contexts: function-arg default, argparse add_argument(default=...), BoolOp `or` fallback,
    dict/.get(k, default), or an assignment to a DEFAULT/ROOT/PATH/DIR-named target."""
    parent = getattr(node, "parent", None)

    # arguments.defaults / kw_defaults -- parent IS the arguments node's list, but ast puts
    # the Constant's .parent as the arguments node directly (child of a list field).
    if isinstance(parent, ast.arguments):
        return True

    # Call(...).add_argument(..., default=X) or dict.get(key, X) / os.environ.get(key, X)
    if isinstance(parent, ast.keyword) and parent.arg == "default":
        call = getattr(parent, "parent", None)
        if isinstance(call, ast.Call):
            return True
    if isinstance(parent, ast.Call):
        func = parent.func
        fname = func.attr if isinstance(func, ast.Attribute) else (func.id if isinstance(func, ast.Name) else "")
        if fname == "get" and len(parent.args) >= 2 and parent.args[1] is node:
            return True

    # `X or "literal"` fallback (rightmost operand of an Or BoolOp)
    if isinstance(parent, ast.BoolOp) and isinstance(parent.op, ast.Or):
        if parent.values and parent.values[-1] is node:
            return True

    # Assign to a DEFAULT/ROOT/PATH/DIR-named target, value is (or directly wraps) this constant
    n = node
    while n is not None and not isinstance(n, ast.Assign):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module, ast.ClassDef)):
            break
        n = getattr(n, "parent", None)
    if isinstance(n, ast.Assign) and n.value is node:
        for t in n.targets:
            name = t.id if isinstance(t, ast.Name) else (t.attr if isinstance(t, ast.Attribute) else "")
            if name and (DEFAULTISH_NAME_RE.search(name) or (extra_name_re and extra_name_re.search(name))):
                return True

    return False


def is_argv_count(node):
    """True for `len(sys.argv)` / `len(argv)` -- argument-count parsing, not a recorded claim
    about the world. `repair_diff_check.py:133: if len(sys.argv) != 3:` is this shape."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len"):
        return False
    if not node.args:
        return False
    arg = node.args[0]
    if isinstance(arg, ast.Attribute) and arg.attr == "argv":
        return True
    if isinstance(arg, ast.Name) and arg.id in ("argv", "sys_argv"):
        return True
    return False


def scan_file(path):
    findings = []
    if TEST_FILE_RE.search(path):
        return findings
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
        tree = ast.parse(src, filename=path)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return findings
    add_parents(tree)
    lines = src.splitlines()

    def snippet(lineno):
        if 1 <= lineno <= len(lines):
            return lines[lineno - 1].strip()[:160]
        return ""

    def rel(p):
        try:
            return os.path.relpath(p, REPO).replace("\\", "/")
        except ValueError:
            return p.replace("\\", "/")

    def add(category, node, extra=""):
        findings.append({
            "category": category,
            "file": rel(path),
            "line": getattr(node, "lineno", 0),
            "snippet": snippet(getattr(node, "lineno", 0)),
            "extra": extra,
        })

    for node in ast.walk(tree):
        # --- string-literal categories: abs_path_default, project_key, hardcoded_id ---
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if is_docstring(node) or in_assert(node) or in_test_function(node):
                continue
            if CITATION_LINEREF_RE.search(val):
                continue
            if ABS_PATH_RE.search(val) and is_default_context(node):
                add("abs_path_default", node, val[:80])
                continue
            if PROJECT_KEY_RE.search(val) and is_default_context(node):
                add("project_key", node, val[:80])
                continue
            if (UUID_RE.search(val) or TICKET_RE.search(val)) and is_default_context(node, IDISH_NAME_RE):
                add("hardcoded_id", node, val[:80])
                continue
            # SHA-shaped hex string: only when the assign target/keyword name suggests an id,
            # to avoid flagging every incidental 8+ hex-looking token (very FP-prone otherwise).
            if SHA_RE.fullmatch(val) and len(val) >= 12 and is_default_context(node, IDISH_NAME_RE):
                add("hardcoded_id", node, val[:80])
                continue

            if DATE_LIT_RE.search(val):
                # date literal handled in Compare pass below (needs operator context);
                # a bare string here (e.g. a docstring date-stamp) is not itself a finding.
                pass

        # --- magic_count_guard: Eq/NotEq against int literal >= 2, inside if/while test ---
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], (ast.Eq, ast.NotEq)):
            if in_test_function(node) or in_assert(node):
                continue
            parent = getattr(node, "parent", None)
            in_guard = isinstance(parent, (ast.If, ast.While)) and parent.test is node
            if not in_guard:
                continue
            left, right = node.left, node.comparators[0]
            lit, other = None, None
            if isinstance(right, ast.Constant) and isinstance(right.value, int) and not isinstance(right.value, bool):
                lit, other = right.value, left
            elif isinstance(left, ast.Constant) and isinstance(left.value, int) and not isinstance(left.value, bool):
                lit, other = left.value, right
            if lit is not None and lit >= 2 and lit not in HTTP_STATUS and not isinstance(other, ast.Constant) \
                    and not is_argv_count(other):
                add("magic_count_guard", node, f"literal={lit}")

        # --- date_threshold: date-literal string compared with < <= > >= ---
        if isinstance(node, ast.Compare):
            ops_are_ordering = all(isinstance(o, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for o in node.ops)
            if ops_are_ordering and not in_test_function(node) and not in_assert(node):
                operands = [node.left] + list(node.comparators)
                for opnd in operands:
                    if isinstance(opnd, ast.Constant) and isinstance(opnd.value, str) and DATE_LIT_RE.fullmatch(opnd.value.strip()):
                        add("date_threshold", node, opnd.value)
                        break

    return findings


def scan_root(root):
    findings = []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
        for fn in filenames:
            if fn.endswith(".py"):
                scanned += 1
                findings.extend(scan_file(os.path.join(dirpath, fn)))
    return findings, scanned


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------

def _scan_src(src, tmp_name="synthetic.py"):
    tree = ast.parse(src, filename=tmp_name)
    add_parents(tree)
    # reuse scan_file's inner logic by writing to a temp path
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(src)
        path = f.name
    try:
        return scan_file(path)
    finally:
        os.unlink(path)


def self_test():
    cases = []

    # 1. real hardcoded write-default -> FLAG (abs_path_default)
    cases.append((
        "abs_path_default: module-level DEFAULT_ROOT",
        'DEFAULT_ROOT = "G:\\\\My Drive\\\\Claude\\\\claude-foundational-layer"\n',
        lambda f: any(x["category"] == "abs_path_default" for x in f),
    ))

    # 2. provenance citation in a docstring -> NOT flagged
    cases.append((
        "docstring citation not flagged",
        'def f():\n    """See wiki/tracker/foo.md:88 for the rule this implements."""\n    return 1\n',
        lambda f: not any(x["category"] == "abs_path_default" for x in f) and len(f) == 0,
    ))

    # 3. selftest fixture -> NOT flagged
    cases.append((
        "selftest fixture not flagged",
        'def test_thing():\n    x = 5\n    if x != 42:\n        raise AssertionError\n',
        lambda f: len(f) == 0,
    ))

    # 4. entry-point subprocess case (this script run as a subprocess with --self-test disabled
    #    to avoid recursion; instead we invoke --root on a scratch dir and check exit code 0)
    cases.append((
        "entry-point subprocess smoke test",
        None,
        None,  # handled specially below
    ))

    # 5. magic count guard flagged
    cases.append((
        "magic_count_guard: if len(skills) != 42",
        'def render(skills):\n    if len(skills) != 42:\n        raise ValueError("bad")\n    return skills\n',
        lambda f: any(x["category"] == "magic_count_guard" for x in f),
    ))

    # 6. magic count guard NOT flagged when comparing to HTTP status
    cases.append((
        "http status not flagged",
        'def check(resp):\n    if resp.status_code != 404:\n        return True\n    return False\n',
        lambda f: not any(x["category"] == "magic_count_guard" for x in f),
    ))

    # 7. hardcoded session id as export default -> FLAG
    cases.append((
        "hardcoded_id: session id as default",
        'SESSION_ID = "35c4e94e-0708-4f37-9e63-cf0f47fd6d34"\n',
        lambda f: any(x["category"] == "hardcoded_id" for x in f),
    ))

    # 8. schema-version constant DEFINITION with no comparison -> NOT flagged
    cases.append((
        "bare version constant definition not flagged",
        'SCHEMA_VERSION = "2026-08-01"\n',
        lambda f: len(f) == 0,
    ))

    # 9. date threshold comparison -> FLAG
    cases.append((
        "date_threshold: cutoff comparison",
        'def stale(d):\n    if d < "2026-08-01":\n        return True\n    return False\n',
        lambda f: any(x["category"] == "date_threshold" for x in f),
    ))

    # 10. project-key glob as a match default -> FLAG
    cases.append((
        "project_key: sanitized cwd string as default",
        'DEFAULT_PROJECT_DIR = "G--My-Drive-Claude-Claude-Personal"\n',
        lambda f: any(x["category"] == "project_key" for x in f),
    ))

    # 11. `.get(key, "literal-path")` fallback -> FLAG
    cases.append((
        "abs_path_default: dict.get fallback",
        'def f(cfg):\n    root = cfg.get("root", "C:\\\\Users\\\\Jon\\\\out")\n    return root\n',
        lambda f: any(x["category"] == "abs_path_default" for x in f),
    ))

    # 12. `self_check_*`-named fixture function (this repo's convention, NOT matched by a bare
    #     "test" substring check) -> NOT flagged. Real case: coverage_census.py self_check_population().
    cases.append((
        "self_check_population fixture not flagged (self_check naming, no 'test' substring)",
        'def self_check_population():\n    got = 871\n    if got != 871:\n        raise AssertionError\n',
        lambda f: len(f) == 0,
    ))

    # 13. argv-count guard -> NOT flagged (argument parsing, not a recorded claim).
    #     Real case: repair_diff_check.py:133 `if len(sys.argv) != 3:`.
    cases.append((
        "argv-count guard not flagged",
        'import sys\ndef main():\n    if len(sys.argv) != 3:\n        sys.exit(2)\n',
        lambda f: len(f) == 0,
    ))

    # 14. module-level constant with no enclosing function, inside a selftest_*.py FILE ->
    #     NOT flagged. Real case: selftest_extract_compact_summary.py:37
    #     `SESSION_ID = "abc12345-0000-4000-8000-000000000001"` -- a synthetic UUID fixture with
    #     no enclosing function at all, so the function-name rule (case 12/TEST_FN_NAME_RE)
    #     cannot reach it; only a filename-keyed exclusion can.
    def _check_test_filename_case():
        import tempfile
        d = tempfile.mkdtemp(prefix="expiring_values_selftest_fname_")
        p = os.path.join(d, "selftest_fixture_example.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write('SESSION_ID = "abc12345-0000-4000-8000-000000000001"\n')
        findings = scan_file(p)
        os.unlink(p)
        return len(findings) == 0

    passed, failed = 0, 0
    for name, src, check in cases:
        if src is None:
            continue  # entry-point case handled below
        findings = _scan_src(src)
        ok = False
        try:
            ok = bool(check(findings))
        except Exception:
            ok = False
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if ok:
            passed += 1
        else:
            failed += 1
            print(f"          findings={findings}")

    # entry-point / subprocess case
    import subprocess, tempfile
    tmpdir = tempfile.mkdtemp(prefix="expiring_values_selftest_")
    with open(os.path.join(tmpdir, "sample.py"), "w", encoding="utf-8") as f:
        f.write('DEFAULT_ROOT = "N:\\\\claude-cfl\\\\clone"\n')
    proc = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--root", tmpdir, "--json"],
        capture_output=True, text=True, timeout=60,
    )
    ok = proc.returncode == 0
    try:
        data = json.loads(proc.stdout)
        ok = ok and any(x["category"] == "abs_path_default" for x in data)
    except Exception:
        ok = False
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] entry-point subprocess smoke test (exit={proc.returncode})")
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"          stdout={proc.stdout[:400]!r} stderr={proc.stderr[:400]!r}")

    ok = False
    try:
        ok = _check_test_filename_case()
    except Exception as e:
        print(f"          exception={e!r}")
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] selftest_*.py module-level fixture constant not flagged (filename rule)")
    if ok:
        passed += 1
    else:
        failed += 1

    total = passed + failed
    print(f"self-test: {passed}/{total} passed")
    return failed == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.join(REPO, "scripts", "audit"),
                     help="directory to scan (default: scripts/audit)")
    ap.add_argument("--json", action="store_true", help="dump full findings list as JSON")
    ap.add_argument("--sample", type=int, default=0, help="print a seeded random sample of N findings (for hand-grading)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok else 1)

    if not os.path.isdir(args.root):
        print(f"root not found: {args.root}")
        sys.exit(2)

    findings, scanned = scan_root(args.root)

    if args.sample:
        rng = random.Random(args.seed)
        pool = findings[:]
        n = min(args.sample, len(pool))
        sample = rng.sample(pool, n) if n else []
        print(json.dumps(sample, indent=2))
        return

    if args.json:
        print(json.dumps(findings, indent=2))
        return

    if scanned == 0:
        print(f"no .py files found under {args.root}")
        sys.exit(2)

    by_cat = {c: 0 for c in CATEGORIES}
    for f in findings:
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1

    print(f"files scanned : {scanned}")
    print(f"root          : {os.path.relpath(args.root, REPO)}")
    print(f"TOTAL HITS    : {len(findings)}  (raw, UNSAMPLED -- see docstring: do not report without hand-grading)")
    for c in CATEGORIES:
        print(f"  {c:20s}: {by_cat.get(c, 0)}")


if __name__ == "__main__":
    main()
