#!/usr/bin/env python3
"""finished_means_reviewable.py -- the AG-T1 / AG-T2 checker (CFL ticket to Antigravity, 2026-09-02).

Jon 2026-09-02 ("yes-ish" -> tickets): a completion report is FINISHED only when a reader can review it.

Mode 1 (default)  finished_means_reviewable.py <report.md> [--root DIR]
    Every path named in a markdown TABLE ROW of the report must exist and be > 0 bytes.
    Any phantom (missing) or 0-byte path -> FAIL, exit 1. Paths are resolved as written
    (absolute, or file:/// URLs), else relative to --root (default: the report's directory),
    else relative to the cwd. A report whose table rows name NO path at all is not reviewable
    either: PASS-VACUOUS is reported and the exit is 1 (UNKNOWN is not a pass).

Mode 2  finished_means_reviewable.py --measured <report.md>
    Every line carrying the literal tag "[measured]" must also carry a digit AND a method
    (a script/command name: *.py, *.sh, *.mjs, *.bat, *.ps1, or a backticked span). A
    "[measured]" on a heading with nothing measured beside it -> FAIL, exit 1.

--selftest   plants a phantom path, a 0-byte file, a good file, a bare "[measured]" heading and a
             proper measured line, and asserts both modes fail on the planted defects and pass on
             the clean fixture. Exit 0 iff every assertion holds.

Exit codes: 0 PASS, 1 FAIL / UNKNOWN, 2 usage or unreadable report. Verdict lines are the report;
nothing is written anywhere.
"""
import argparse
import hashlib
import os
import re
import sys
import tempfile

PATH_RE = re.compile(
    r'(?:file:///)?('
    r'(?:[A-Za-z]:[\\/]|/|\\\\|~)[^`|<>"\'\s)\]]+'          # absolute / UNC / home
    r'|(?:[\w.\-]+[\\/])+[\w.\-]+(?:\.\w+)?'                 # relative with a separator
    r'|[\w.\-]+\.(?:md|py|sh|json|jsonl|txt|csv|yaml|yml|mjs|js|html|bat|ps1)'  # bare filename
    r')'
)
METHOD_RE = re.compile(r'(\b[\w\-]+\.(?:py|sh|mjs|js|bat|ps1)\b|`[^`]+`)')
SEP_ROW_RE = re.compile(r'^\s*\|?\s*:?-{2,}')


def _clean(tok: str) -> str:
    tok = tok.strip().rstrip('.,;:')
    if tok.startswith('file:///'):
        tok = tok[len('file:///'):]
    return tok


def table_row_paths(text: str):
    """Yield (lineno, path-as-written) for every path-looking token in a markdown table row."""
    for i, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith('|'):
            continue
        if SEP_ROW_RE.match(line):
            continue
        for m in PATH_RE.finditer(line):
            tok = _clean(m.group(1))
            if not tok or tok.startswith('http'):
                continue
            if '/' not in tok and '\\' not in tok and '.' not in tok:
                continue
            if re.fullmatch(r'\d+(\.\d+)+', tok) or re.fullmatch(r'\d+/\d+', tok):
                continue  # version numbers and fractions like 4/4 are not paths
            yield i, tok


NOT_A_PATH = ('N/A', 'n/a', 'N/A-kind')


def resolve(tok: str, root: str) -> str:
    t = os.path.expanduser(tok)
    if os.path.isabs(t) or re.match(r'^[A-Za-z]:', t):
        cands = [t]
    else:
        cands = [os.path.join(root, t), os.path.join(os.getcwd(), t)]
        # 2026-09-03: reports name paths repo-relative; also try the git top-level of the report's dir
        try:
            import subprocess
            top = subprocess.run(['git', '-C', root, 'rev-parse', '--show-toplevel'],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
            if top:
                cands.append(os.path.join(top, t))
        except Exception:
            pass
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]


def check_paths(report: str, root: str):
    text = open(report, encoding='utf-8', errors='replace').read()
    rows, fails, seen = [], 0, set()
    for ln, tok in table_row_paths(text):
        if tok in seen:
            continue
        seen.add(tok)
        if tok.strip('`') in NOT_A_PATH or tok.strip('`').startswith('N/A'):
            continue   # 2026-09-03: 'N/A-kind' is a lint verdict, not a path (false positive on UC-0b report)
        _t = tok.strip('`')
        # 2026-09-03 (S-cd-04 report): '3902/3912/3919' and '7/D17/D18/model' are not paths. A path
        # token has a file extension in its last segment OR starts with a known root.
        # 2026-09-04 (ultrareview PR#254 FIX 1): split on '/' OR '\' -- a backslash Windows path
        # (e.g. N:\claude-cfl\clone\scripts\x.py) has no forward slash, so splitting on '/' alone
        # left _last as the whole token; the extension check still passed by luck, but the root-match
        # branch below needed the backslash-root alternatives to catch extensionless backslash paths.
        _last = re.split(r'[\\/]', _t)[-1]
        if not (re.search(r'\.[A-Za-z0-9]{1,6}$', _last) or re.match(r'^(?:[A-Za-z]:[\\/]?|[A-Za-z]:\\\\|/|\\\\|~|wiki[\\/]|scripts[\\/]|exchange[\\/]|raw[\\/]|skills[\\/]|docs[\\/]|evidence[\\/])', _t)):
            seen.discard(tok)   # UR-alt FR-2: a skipped token is not part of the denominator
            continue
        # UR-alt FR-1 (2026-09-03): '/…' or 'wiki/…' (non-ASCII glued to a slash) is prose, not a path.
        # 2026-09-04 (ultrareview PR#254 FIX 1): the allowed charset omitted '\' entirely, so ANY
        # backslash-separated Windows path token (N:\claude-cfl\clone\scripts\x.py) was discarded here
        # as "prose, not a path" regardless of the root-match above. Added '\\' to the allowed set.
        if re.search(r'[^A-Za-z0-9_.\/\\:~ +@\-]', _t):
            seen.discard(tok)
            continue
        p = resolve(tok, root)
        if not os.path.exists(p):
            rows.append((ln, tok, 'PHANTOM (does not exist)'))
            fails += 1
        elif os.path.isfile(p) and os.path.getsize(p) == 0:
            rows.append((ln, tok, 'ZERO-BYTE'))
            fails += 1
        elif os.path.isfile(p):
            rows.append((ln, tok, f'ok ({os.path.getsize(p)} B)'))
        else:
            rows.append((ln, tok, 'ok (dir)'))
    return rows, fails, len(seen)


def check_measured(report: str):
    text = open(report, encoding='utf-8', errors='replace').read()
    rows, fails, n = [], 0, 0
    for i, line in enumerate(text.splitlines(), 1):
        if '[measured]' not in line:
            continue
        n += 1
        # a date or clock alone is not a measurement: strip date/time tokens before looking for a number
        stripped = re.sub(r'\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?)?|\d{1,2}:\d{2}(?::\d{2})?', ' ', line.replace('[measured]', ''))
        has_digit = bool(re.search(r'\d', stripped))
        has_method = bool(METHOD_RE.search(line))
        if has_digit and has_method:
            rows.append((i, 'ok'))
        else:
            why = []
            if not has_digit:
                why.append('no number (a date or clock alone does not count)')
            if not has_method:
                why.append('no method (script/command)')
            rows.append((i, 'FAIL: ' + ', '.join(why)))
            fails += 1
    return rows, fails, n


def run(args) -> int:
    if not os.path.isfile(args.report):
        print(f'UNREADABLE: {args.report}', file=sys.stderr)
        return 2
    root = args.root or os.path.dirname(os.path.abspath(args.report))
    sha = hashlib.sha256(open(args.report, 'rb').read()).hexdigest()[:12]
    print(f'report {args.report}  sha256[:12]={sha}  bytes={os.path.getsize(args.report)}')
    if args.measured:
        rows, fails, n = check_measured(args.report)
        for ln, v in rows:
            print(f'  L{ln:<5} {v}')
        print(f'MEASURED-LINT: {n} "[measured]" line(s), {fails} without number+method')
        if fails:
            print('FAIL')
        elif n:
            print('PASS')
        else:
            print('PASS (no [measured] tags -- nothing to lint)')
        return 1 if fails else 0
    rows, fails, n = check_paths(args.report, root)
    for ln, tok, v in rows:
        print(f'  L{ln:<5} {v:<28} {tok}')
    print(f'PATH-CHECK: {n} path(s) in table rows, {fails} phantom/zero-byte  (root={root})')
    if n == 0:
        print('PASS-VACUOUS: no paths in any table row -- a report with nothing to open is not '
              'reviewable either; treated as UNKNOWN (exit 1)')
        return 1
    print('FAIL' if fails else 'PASS')
    return 1 if fails else 0


def selftest() -> int:
    ok = True
    A = argparse.Namespace

    def expect(label, got, want):
        nonlocal ok
        good = got == want
        ok = ok and good
        print(f"  [{'ok  ' if good else 'FAIL'}] {label}: exit {got} (want {want})")

    with tempfile.TemporaryDirectory() as d:
        good = os.path.join(d, 'good.md')
        with open(good, 'w') as f:
            f.write('x\n')
        zero = os.path.join(d, 'zero.md')
        open(zero, 'w').close()

        bad = os.path.join(d, 'bad-report.md')
        with open(bad, 'w') as f:
            f.write('# r\n| item | path |\n|---|---|\n| a | good.md |\n| b | phantom/nowhere.md |\n')
        expect('phantom path in table row', run(A(report=bad, root=d, measured=False)), 1)

        z = os.path.join(d, 'zero-report.md')
        with open(z, 'w') as f:
            f.write('| item | path |\n|---|---|\n| a | good.md |\n| b | zero.md |\n')
        expect('zero-byte path in table row', run(A(report=z, root=d, measured=False)), 1)

        g = os.path.join(d, 'good-report.md')
        with open(g, 'w') as f:
            f.write(f'| item | path |\n|---|---|\n| a | good.md |\n| b | {good} |\n')
        expect('all paths exist and non-empty', run(A(report=g, root=d, measured=False)), 0)

        v = os.path.join(d, 'vacuous.md')
        with open(v, 'w') as f:
            f.write('# nothing\nprose only, ticket AG-T1 done\n')
        expect('no paths at all is UNKNOWN (exit 1)', run(A(report=v, root=d, measured=False)), 1)

        m1 = os.path.join(d, 'm-bad.md')
        with open(m1, 'w') as f:
            f.write('## Acknowledgment [measured]\n- adopted the gate\n')
        expect('[measured] heading with no number/method', run(A(report=m1, root=d, measured=True)), 1)

        m3 = os.path.join(d, 'm-date-only.md')
        with open(m3, 'w') as f:
            f.write('- Date: 2026-09-02 22:52 CDT `[measured]`\n')
        expect('[measured] with only a date/clock and a backtick', run(A(report=m3, root=d, measured=True)), 1)

        f4 = os.path.join(d, 'fraction.md')
        with open(f4, 'w') as f:
            f.write('| item | path | score |\n|---|---|---|\n| a | good.md | 4/4 |\n')
        expect('fraction 4/4 in a row is not a path', run(A(report=f4, root=d, measured=False)), 0)

        m2 = os.path.join(d, 'm-good.md')
        with open(m2, 'w') as f:
            f.write('- five_hour 32.0 per `dispatch_gate.py`, 2026-09-02 22:09 [measured]\n')
        expect('[measured] with number and method', run(A(report=m2, root=d, measured=True)), 0)

        # 2026-09-04 (ultrareview PR#254 FIX 1): a backslash Windows path token in a table row
        # (no forward slash anywhere) must resolve as a path, not be discarded as prose.
        bs = os.path.join(d, 'backslash-report.md')
        with open(bs, 'w') as f:
            f.write(f'| item | path |\n|---|---|\n| a | {good} |\n')
        expect('backslash Windows path in table row resolves', run(A(report=bs, root=d, measured=False)), 0)

    print('SELFTEST', 'PASS 9/9' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('report', nargs='?')
    ap.add_argument('--root')
    ap.add_argument('--measured', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.report:
        ap.print_usage()
        sys.exit(2)
    sys.exit(run(a))
