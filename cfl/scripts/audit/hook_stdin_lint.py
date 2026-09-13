#!/usr/bin/env python3
"""hook_stdin_lint.py — flag hook commands that chain MORE THAN ONE stdin-consuming script.

WHY
---
Measured 2026-09-04 19:16 on CFL's own PostCompact entry, which chained two scripts on one shell
line with `;`. The chaining was correct about ORDER (two separate hook entries run in PARALLEL,
and pipeline step 9 read the verifier's artifact before the verifier wrote it -- measured
2026-09-01 23:00, elder-confirmed). It was silently wrong about STDIN.

A `;`-chain shares ONE stdin, and the first reader consumes it. postcompact_verify.py:151 does
`sys.stdin.read()`; postcompact_pipeline.py then hit EOF, its json.load raised, and it fell to a
fallback its own comment documents as useless -- sess="unknown". Three graded rows downstream
scored against that fallback as though it were a reading, and one of them printed PASS.

THE CLASS THIS DETECTS: a second consumer of a drained stream CANNOT DISTINGUISH "no payload was
sent" from "somebody already read it." Both are EOF. So it degrades to its default silently.
A default that fires on EOF is not a measurement.

WHAT IT DOES
------------
Reads a settings.json, walks every hooks.<Event>[].hooks[].command, and for each command:
  - finds the script paths it invokes
  - reads each script and asks whether it CONSUMES STDIN
  - reports RISK when one command invokes 2+ stdin consumers without a fan-out wrapper.

Exit 0 = no risk found. Exit 1 = at least one risky command. This is a REPORT, not a fence:
a hook lint that blocks a session over its own finding is the failure it exists to prevent.

  hook_stdin_lint.py [--settings PATH] [--self-test]
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_up = os.path.dirname(HERE)
ROOT = os.path.dirname(_up) if os.path.basename(_up) == "scripts" else _up
ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or ROOT

# A wrapper that reads stdin ONCE and re-feeds every child. Naming it here is what keeps the lint
# from flagging the FIX as though it were the bug.
FANOUT_MARKERS = ("hook_fanout.sh",)

# These wrappers exec their target with stdin untouched -- they are pass-throughs, not consumers.
# Counting them would false-positive every wrapped entry in the file.
PASSTHROUGH = ("py_closed.sh", "sh_closed.sh")

CONSUMES = (
    re.compile(r"sys\.stdin\.(?:read|readline|readlines)\s*\("),
    re.compile(r"for\s+\w+\s+in\s+sys\.stdin\b"),
    re.compile(r"json\.load\s*\(\s*sys\.stdin\s*\)"),
    re.compile(r"(?<![\w.])input\s*\("),
)

SCRIPT_RE = re.compile(r"([\w.-]+\.(?:py|sh))")


def consumes_stdin(path):
    """(bool|None, reason). UNREADABLE is UNKNOWN -- reported, never silently treated as 'no'."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
    except OSError as e:
        return None, "UNREADABLE (%s)" % e.__class__.__name__
    for rx in CONSUMES:
        m = rx.search(src)
        if m:
            line = src[: m.start()].count("\n") + 1
            return True, "%s:%d %s" % (os.path.basename(path), line, m.group(0))
    return False, ""


def resolve(name):
    base_name = os.path.basename(name)
    for base in (ROOT, os.path.join(ROOT, "scripts"), os.path.join(ROOT, ".claude", "hooks")):
        p = os.path.join(base, base_name)
        if os.path.isfile(p):
            return p
    for dirpath, _dirs, files in os.walk(os.path.join(ROOT, "scripts")):
        if base_name in files:
            return os.path.join(dirpath, base_name)
    return None


def scan_command(cmd):
    """-> (risk, consumers[(name, reason)], unknown[(name, reason)])"""
    if any(mk in cmd for mk in FANOUT_MARKERS):
        return False, [], []
    names, seen = [], set()
    for m in SCRIPT_RE.finditer(cmd):
        n = m.group(1)
        if n in PASSTHROUGH or n in seen:
            continue
        seen.add(n)
        names.append(n)
    consumers, unknown = [], []
    for n in names:
        p = resolve(n)
        if not p:
            unknown.append((n, "NOT FOUND on disk"))
            continue
        c, why = consumes_stdin(p)
        if c is None:
            unknown.append((n, why))
        elif c:
            consumers.append((n, why))
    return (len(consumers) >= 2), consumers, unknown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", default=os.path.join(ROOT, ".claude", "settings.json"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    try:
        with open(a.settings, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception as e:
        print("UNKNOWN -- could not read %s: %s" % (a.settings, e))
        print("A settings file that cannot be read is UNKNOWN, never a clean bill.")
        return 1

    print("=== HOOK STDIN LINT === a `;`-chain shares one stdin; the first reader drains it")
    print("")
    risky = n_cmd = 0
    for event, blocks in (cfg.get("hooks") or {}).items():
        for b in blocks or []:
            for h in b.get("hooks") or []:
                cmd = h.get("command") or ""
                if not cmd:
                    continue
                n_cmd += 1
                risk, cons, unk = scan_command(cmd)
                if risk:
                    risky += 1
                    print("  RISK     %s: %d stdin consumers in ONE command" % (event, len(cons)))
                    for _nm, why in cons:
                        print("             consumes: %s" % why)
                    print("             fix: route through .claude/hooks/hook_fanout.sh")
                for nm, why in unk:
                    print("  UNKNOWN  %s: %s -- %s (UNKNOWN dominates a pass)" % (event, nm, why))
    print("")
    print("  %d hook command(s) scanned, %d risky" % (n_cmd, risky))
    if not risky:
        print("  No command chains two stdin consumers. This is a REPORT, not a proof that every "
              "hook is correct.")
    return 1 if risky else 0


def self_test():
    import tempfile
    global resolve
    print("=== SELF-TEST -- hook_stdin_lint ===")
    npass = nfail = 0

    def ok(name, got, want):
        nonlocal npass, nfail
        if got == want:
            npass += 1
            print("  PASS  %s" % name)
        else:
            nfail += 1
            print("  FAIL  %s\n        want: %r\n        got : %r" % (name, want, got))

    d = tempfile.mkdtemp()
    with open(os.path.join(d, "a.py"), "w") as f:
        f.write("import sys\nraw = sys.stdin.read()\n")
    with open(os.path.join(d, "b.py"), "w") as f:
        f.write("import sys, json\nx = json.load(sys.stdin)\n")
    with open(os.path.join(d, "q.py"), "w") as f:
        f.write("print('reads nothing at all')\n")

    real = resolve

    def fake(n):
        p = os.path.join(d, os.path.basename(n))
        return p if os.path.isfile(p) else None

    resolve = fake
    try:
        # 1 THE BUG ITSELF: two consumers, one command
        ok("1 two stdin consumers chained -> RISK", scan_command("python a.py; python b.py")[0], True)
        # 2 the common, correct case
        ok("2 single consumer -> no risk", scan_command("python a.py")[0], False)
        # 3 NEGATIVE CONTROL: a consumer beside a NON-consumer is not this defect
        ok("3 consumer + non-consumer -> no risk", scan_command("python a.py; python q.py")[0], False)
        # 4 the FIX must never be flagged as the bug
        ok("4 fanout wrapper -> no risk", scan_command("bash hook_fanout.sh a.py b.py")[0], False)
        # 5 `&&` shares one stdin exactly as `;` does
        ok("5 && chain is the same defect", scan_command("python a.py && python b.py")[0], True)
        # 6 a script that cannot be found is UNKNOWN, never silently 'no'
        ok("6 missing script -> UNKNOWN not a pass", scan_command("python zz.py")[2] != [], True)
        # 7 the pass-through wrappers must not be counted as consumers
        ok("7 py_closed wrapper not a consumer", scan_command("bash py_closed.sh a.py")[0], False)
        # 8 POSITIVE CONTROL for 7: wrapping does not HIDE a real two-consumer chain either
        ok("8 wrapped two-consumer chain still RISK",
           scan_command("bash py_closed.sh a.py; bash py_closed.sh b.py")[0], True)
    finally:
        resolve = real
    print("  %d passed, %d failed" % (npass, nfail))
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
