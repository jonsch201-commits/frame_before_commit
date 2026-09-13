#!/usr/bin/env python3
"""Partition "no extract exists" into NOTHING-TO-CAPTURE and UNEXPLAINED.

WHY THIS EXISTS — a row that can never reach zero is an alarm nobody reads.

`capture.pipeline.absent.sessions` read **9 / 50** and could not have read anything else.
Those nine are exactly the nine sessions the extractor classifies **EMPTY**: they parse
cleanly and contain zero `user`/`assistant` records — opened, named, closed without a turn.
**They have no extract because there is nothing to extract**, and they are permanent, so the
row would have failed on every future run forever.

That is RATIO_FLOOR again, the third time in this program: an alarm calibrated so it always
fires stops carrying information. The fix is the same one applied to EMPTY-vs-FAILED in the
extractor and to live-vs-quiescent in the partitioner — **a category permanently in the alarm
bucket needs its own disposition, not exclusion.**

AND THE PROXY UNDERNEATH IT WAS ALREADY KNOWN BAD. The row is computed from `md✗` in
`--list` output. This program has a standing finding — *"detection proxies lie: `md✗` isn't a
capture signal"* — recorded after a false backlog on 2026-07-12 and 13 false REFRESH verdicts
on 07-13. **The check was built on a proxy its own record says not to trust.** So this helper
does not refine the proxy; it re-derives from the JSONL itself.

WHAT IT RETURNS

    "<empty> <unexplained> <total>"

  empty       — no extract AND no conversational turn. Nothing to capture. INFO, never blocks.
  unexplained — no extract and the file DOES hold turns. **This is the real loss row** and it
                must reach zero.

Predicate is the extractor's own `session_is_empty`, imported rather than reimplemented, so
the two can never drift apart into two different definitions of the same word.

Usage:
    _su_close_absent.py <list-output> <projects-root>
    _su_close_absent.py --self-test
"""
import importlib.util
import os
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROW = re.compile(r"^  ([0-9a-f]{6})  .*md✗")


def load_is_empty(repo):
    """Import the extractor's own predicate. If it cannot be loaded, say so — never guess.

    A helper that silently substitutes its own definition of EMPTY would recreate the exact
    divergence this file exists to prevent.
    """
    path = os.path.join(repo, "scripts", "extract_claude_code_sessions.py")
    if not os.path.isfile(path):
        return None
    try:
        spec = importlib.util.spec_from_file_location("_ex", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "session_is_empty", None)
    except Exception:
        return None


def resolve_root(p):
    """Return a readable projects root, or None. NEVER guess silently.

    FOURTH INSTANCE OF THE PATH-IDENTITY DEFECT CLASS, and it bit this file directly.
    `su_close.sh` runs under git-bash, where `$HOME/.claude/projects` expands to
    `/c/Users/JonSc/.claude/projects`. Windows Python cannot resolve that form, so every
    lookup missed, every session fell to UNEXPLAINED, and the row reported **9 real losses
    that did not exist.** The measuring code was broken and its output looked like a finding
    — exactly the failure recorded when a 60-char truncation reported 0 CFL records.

    So: translate the known forms, and if none resolves, **return None so the caller exits 2
    and the row reads UNKNOWN.** A root we cannot read is unknown, never a count.
    """
    cands = [p]
    if p.startswith("/") and len(p) > 2 and p[2] == "/":
        cands.append(p[1].upper() + ":" + p[2:])      # /c/Users/... -> C:/Users/...
    cands.append(os.path.expanduser("~/.claude/projects"))
    for c in cands:
        if c and os.path.isdir(c):
            return c
    return None


def find_jsonl(root, uuid6):
    """Locate the session JSONL whose stem starts with uuid6. None if absent from disk."""
    try:
        slugs = os.listdir(root)
    except OSError:
        return None
    for slug in slugs:
        d = os.path.join(root, slug)
        if not os.path.isdir(d):
            continue
        try:
            for f in os.listdir(d):
                if f.endswith(".jsonl") and f.startswith(uuid6):
                    return os.path.join(d, f)
        except OSError:
            continue
    return None


def partition(list_lines, root, is_empty):
    empty = unexplained = total = 0
    for line in list_lines:
        m = ROW.match(line.rstrip("\n"))
        if not m:
            continue
        total += 1
        p = find_jsonl(root, m.group(1))
        if p is None:
            # On disk it is gone but --list saw it: not a capture gap we can act on here.
            # Counted UNEXPLAINED deliberately — a file we cannot inspect is not proven empty.
            unexplained += 1
            continue
        # Pass a Path, not a str. `session_is_empty` calls `.read_text()`, a Path method;
        # a str raises AttributeError, which its own `except Exception: return False`
        # swallows — and False means "has turns", so EVERY empty session read as a REAL
        # LOSS. Nine phantom losses, reported confidently. Fail-closed is the right
        # direction for the extractor (never call a real session empty) and the WRONG
        # direction here, where it converts "could not tell" into "confirmed defect".
        try:
            verdict = is_empty(pathlib.Path(p))
        except Exception:
            verdict = None      # could not decide — see below
        if verdict is True:
            empty += 1
        else:
            unexplained += 1
    return empty, unexplained, total


def self_test():
    import json
    import tempfile
    cases = []
    root = tempfile.mkdtemp()
    slug = os.path.join(root, "proj")
    os.makedirs(slug)

    def w(name, recs):
        p = os.path.join(slug, name)
        with open(p, "w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
        return p

    w("aaaaaa-1.jsonl", [{"type": "ai-title", "aiTitle": "x"}])
    w("bbbbbb-2.jsonl", [{"type": "user", "message": {"role": "user", "content": "hi"}}])

    def is_empty(p):
        for line in open(p, encoding="utf-8"):
            try:
                if json.loads(line).get("type") in ("user", "assistant"):
                    return False
            except Exception:
                return False
        return True

    lines = ["  aaaaaa  0 msgs  x  md✗  fl t\n", "  bbbbbb  1 msgs  x  md✗  fl t\n"]
    e, u, t = partition(lines, root, is_empty)
    cases.append(("turnless -> empty, with-turns -> unexplained", (e, u, t) == (1, 1, 2)))

    # NEGATIVE CONTROL: a row with an extract (md✓) must not be counted at all.
    e2, u2, t2 = partition(["  cccccc  9 msgs  x  md✓  fl t\n"], root, is_empty)
    cases.append(("NEGATIVE CONTROL: md✓ rows are not counted", (e2, u2, t2) == (0, 0, 0)))

    # NEGATIVE CONTROL: a file --list names but disk lacks must be UNEXPLAINED, never empty.
    e3, u3, t3 = partition(["  dddddd  4 msgs  x  md✗  fl t\n"], root, is_empty)
    cases.append(("NEGATIVE CONTROL: missing file is unexplained, not empty",
                  (e3, u3, t3) == (0, 1, 1)))

    print("=== SELF-TEST (negative control) ===")
    bad = 0
    for name, ok in cases:
        bad += 0 if ok else 1
        print("  %-56s : %s" % (name, "PASS" if ok else "FAIL"))
    print("\nRESULT: %s — %d/%d" % ("PASS" if not bad else "FAIL", len(cases) - bad, len(cases)))
    return 0 if not bad else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    if len(sys.argv) < 3:
        print("usage: _su_close_absent.py <list-output> <projects-root>", file=sys.stderr)
        return 2
    repo = os.environ.get("REPO") or os.getcwd()
    is_empty = load_is_empty(repo)
    if is_empty is None:
        print("cannot import session_is_empty from the extractor — refusing to guess",
              file=sys.stderr)
        return 2
    root = resolve_root(sys.argv[2])
    if root is None:
        print("projects root unreadable in any known form: %s" % sys.argv[2], file=sys.stderr)
        print("Refusing to count. An unreadable root is UNKNOWN, never 'everything unexplained'.",
              file=sys.stderr)
        return 2
    try:
        lines = open(sys.argv[1], encoding="utf-8", errors="ignore").readlines()
    except OSError as e:
        print("cannot read list output: %s" % e, file=sys.stderr)
        return 2
    print("%d %d %d" % partition(lines, root, is_empty))
    return 0


if __name__ == "__main__":
    sys.exit(main())
