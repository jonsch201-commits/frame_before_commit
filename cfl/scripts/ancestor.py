#!/usr/bin/env python3
"""ancestor.py -- name this seat's ANCESTOR (the previous MAIN session of this tree) and print the
one command that consults it read-only. Jon, 2026-09-04 21:5x, verbatim, typos his: "ensure your
descendents know how to talk to you for advice in this context".

Definitions, so the output can be wrong in a checkable way:
  main session   = a JSONL directly under a project dir of this tree (never subagents/agent-*.jsonl)
                   whose first SCAN_LINES records carry NO parentSessionId  (a forked critic/elder
                   session carries one -- CFL's session_parent.py derives ROOT|PARENT|UNKNOWN the
                   same way; the Secretary measured 5 of 10 lineage rows naming a critic fork as
                   parent when the newest-mtime file was taken blindly. This script never takes
                   the newest file blindly.)
  ancestor       = the newest main session OTHER THAN the current one, by mtime, across EVERY
                   project dir this tree has lived under (scripts/project_dirs.py) -- after a drive
                   move the ancestors stay under the old key.
  current session= --self <id>, or $CLAUDE_SESSION_ID, or the newest main session if neither is
                   given (then the ancestor is the second-newest, and the output says so).

Output (one block, for WAKE.md / the post-compact brief):
  ANCESTOR <id>  main  <mtime local>  <path>
  CONSULT  claude --resume <id> --fork-session --permission-mode plan -p "<question>"
  BOUND    <n> main / <m> forked / <k> unreadable scanned across <d> dir(s); self=<id or 'newest'>

Exit 0 = ancestor named; 2 = UNKNOWN (no project dir, zero main sessions, or all unreadable).
--selftest builds fixtures in a temp dir and asserts: a fork is never the ancestor; the newest
main other than self is; a dir with only forks is UNKNOWN; two dirs are both scanned.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import project_dirs  # noqa: E402

SCAN_LINES = 60


def classify(path):
    """Return 'main', 'fork', or 'unreadable' for one session JSONL."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for _ in range(SCAN_LINES):
                line = fh.readline()
                if not line:
                    break
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("parentSessionId"):
                    return "fork"
        # 2026-09-06: a `-p` lane, a control run, or a --fork-session consult carries NO parentSessionId and the
        # SAME sessionId as its filename (measured on b89050fa, a 2-minute control fork that this function
        # ranked as the newest MAIN and would have named as the successor's ancestor). The harness marks a
        # typed human turn with origin.kind == "human"; a file that carries `origin` fields but no human one
        # is a lane, not a seat. Files with no `origin` field at all (older harness) stay "main".
        saw_origin = False
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"origin"' not in line:
                    continue
                saw_origin = True
                if '"origin":{"kind":"human"' in line or '"kind": "human"' in line:
                    return "main"
        return "lane" if saw_origin else "main"
    except OSError:
        return "unreadable"


def scan(dirs):
    mains, forks, unreadable = [], 0, 0
    for d in dirs:
        try:
            names = os.listdir(d)
        except OSError:
            continue
        for n in names:
            if not n.endswith(".jsonl"):
                continue
            p = os.path.join(d, n)
            if not os.path.isfile(p):
                continue
            c = classify(p)
            if c == "main":
                mains.append((os.path.getmtime(p), n[:-6], p))
            elif c == "fork" or c == "lane":
                forks += 1
            else:
                unreadable += 1
    mains.sort(reverse=True)
    return mains, forks, unreadable


def find_ancestor(dirs, self_id=None):
    mains, forks, unreadable = scan(dirs)
    label = self_id or "newest"
    cands = [m for m in mains if m[1] != self_id] if self_id else mains[1:]
    bound = "BOUND    %d main / %d forked / %d unreadable scanned across %d dir(s); self=%s" % (
        len(mains), forks, unreadable, len(dirs), label)
    if not cands:
        return None, bound
    return cands[0], bound


def render(anc, bound, question):
    mt, sid, path = anc
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mt))
    return "\n".join([
        "ANCESTOR %s  main  %s  %s" % (sid, stamp, path),
        'CONSULT  claude --resume %s --fork-session --permission-mode plan -p "%s"' % (sid, question),
        bound,
    ])


def selftest():
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        d1 = os.path.join(td, "K1"); d2 = os.path.join(td, "K2")
        os.makedirs(d1); os.makedirs(d2); os.makedirs(os.path.join(d1, "subagents"))
        def w(d, sid, fork, age):
            p = os.path.join(d, sid + ".jsonl")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"type": "custom-title", "sessionId": sid,
                                     **({"parentSessionId": "p"} if fork else {})}) + "\n")
                fh.write(json.dumps({"type": "user", "message": {"role": "user", "content": "x"}}) + "\n")
            t = time.time() - age
            os.utime(p, (t, t))
            return p
        w(d1, "aaaa-old-main", False, 3000)
        w(d1, "bbbb-mid-main", False, 2000)
        w(d1, "cccc-newest-fork", True, 10)          # newest by mtime, but a fork
        w(d1, "dddd-self-main", False, 100)
        w(os.path.join(d1, "subagents"), "agent-x", False, 1)  # must be ignored (not scanned)
        w(d2, "eeee-otherdir-main", False, 500)
        # 1. self given: ancestor is newest main other than self, never the fork
        anc, b = find_ancestor([d1, d2], "dddd-self-main")
        ok = anc and anc[1] == "eeee-otherdir-main"
        print(("PASS" if ok else "FAIL"), "fork skipped, both dirs scanned, ancestor =", anc and anc[1]); fails += not ok
        # 2. self not given: newest main is self, ancestor is second newest main
        anc, b = find_ancestor([d1, d2])
        ok = anc and anc[1] == "eeee-otherdir-main"
        print(("PASS" if ok else "FAIL"), "self=newest -> second newest main =", anc and anc[1]); fails += not ok
        # 3. a dir with only forks is UNKNOWN
        d3 = os.path.join(td, "K3"); os.makedirs(d3); w(d3, "ffff-fork", True, 5)
        anc, b = find_ancestor([d3])
        ok = anc is None and "1 forked" in b
        print(("PASS" if ok else "FAIL"), "only forks -> UNKNOWN;", b); fails += not ok
        # 4. bound counts
        _, b = find_ancestor([d1, d2], "dddd-self-main")
        ok = "4 main / 1 forked / 0 unreadable" in b and "2 dir(s)" in b
        print(("PASS" if ok else "FAIL"), "bound line:", b); fails += not ok
    print("SELFTEST", "PASS" if not fails else "FAIL", "%d failure(s)" % fails)
    return 1 if fails else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    # 2026-09-06 test-master finding: Claude Code exports CLAUDE_CODE_SESSION_ID (measured populated in 2.1.261);
    # CLAUDE_SESSION_ID was empty, so every bare run silently fell to newest-by-mtime -- the ranking that named a
    # control fork as the ancestor on 09-06. Read the real variable first; keep the old name as a fallback.
    self_id = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or None
    if "--self" in argv:
        self_id = argv[argv.index("--self") + 1]
    question = "What did you leave unfinished, what did you get wrong, and what would you tell your descendant first?"
    if "--question" in argv:
        question = argv[argv.index("--question") + 1]
    root = project_dirs.ROOT
    if "--root" in argv:
        root = argv[argv.index("--root") + 1]
    dirs = project_dirs.existing_dirs(root)
    if not dirs:
        print("ANCESTOR UNKNOWN -- no project dir exists for %s (keys tried: %s)" % (root, project_dirs.candidate_keys(root)))
        return 2
    anc, bound = find_ancestor(dirs, self_id)
    if anc is None:
        print("ANCESTOR UNKNOWN -- zero main sessions other than self; " + bound)
        return 2
    print(render(anc, bound, question))
    if "--elders" in argv:
        # Jon 2026-09-04 22:4x, verbatim, typos his: "most constitant across eras in various ways?"
        # One ancestor is a witness; several from DIFFERENT eras (one per day, newest first) let a
        # descendant weight what is CONSISTENT across them and treat the disagreements as findings --
        # the Secretary's 09-02/09-04 elder-consult method (disagreements reported, never merged).
        n = int(argv[argv.index("--elders") + 1]) if argv.index("--elders") + 1 < len(argv) else 4
        mains, _, _ = scan(dirs)
        seen_days, elders = set(), []
        for mt, sid, path in mains:
            if sid == self_id:
                continue
            day = time.strftime("%Y-%m-%d", time.localtime(mt))
            if day in seen_days:
                continue
            seen_days.add(day)
            elders.append((mt, sid, path))
            if len(elders) >= n:
                break
        print("ELDERS   %d main session(s), one per era (day), newest first -- consult each, grade against the record, keep disagreements:" % len(elders))
        for mt, sid, path in elders:
            print("  %s  %s  claude --resume %s --fork-session --permission-mode plan -p \"%s\"" % (
                time.strftime("%Y-%m-%d %H:%M", time.localtime(mt)), sid, sid, question))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
