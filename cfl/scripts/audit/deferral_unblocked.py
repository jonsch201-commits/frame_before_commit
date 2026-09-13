#!/usr/bin/env python
"""deferral_unblocked.py -- a deferral is not discharged by being RECORDED.

⛔ THE CASE THAT PRODUCED IT, and it is five days old and CFL's own. Jon, 2026-08-22 13:43:02,
`history.jsonl:2793`, typos his:

    "Look their WILL be a fork/branch of the github that eventually follows that. Until then? I do
     not trust that the G and github and you would actually have what it needs if it tried to force
     a rule like 'no Jon personal/family content in the GitHub' - i do NOT rule it until I can
     actually see the fork/branch whatever of it with this rule so that i can verify the context
     that would be needed is in that and that you can still have the context yuou need!"

CFL recorded that correctly as D-015 NOT RULED with its unblocking condition named. **The prototype
that satisfies the condition was BUILT on 2026-09-02** (`N:\\claude-professional-public`, 4,011 paths
at source, 725 included, 45 excluded, manifest written). ⛔ **The decision was never re-presented.
Sixteen days deferred, FIVE OF THEM UNBLOCKED, and nothing was watching.** Found by Professional
N1C2 on 2026-09-07, not by any instrument here. **The deferral recorded its trigger and NOTHING WAS
WATCHING FOR IT.**

⭐ THE CLASS IS THE WHOLE OF 2026-09-07: `WWJA.md` documented its own broken step for fifteen days ·
a peer trunk measured the chunking defect on 08-31 and named the check that was never built · `C27`
was reserved and later overwritten. **In every case the finding EXISTED and nothing consumed it.**
This repo's own constitution already carries the count: *"397 such deferral claims. Nobody has
graded them."*

WHAT IT REPORTS, and the headline is deliberately the UNCHECKABLE count rather than the violations:

  UNBLOCKED   the predicate in `unblocked_by:` is SATISFIED and the item is still open  <- the finding
  WAITING     predicate present, not yet satisfied                                     <- healthy
  SELF-CLOSING  an `on-silence` default with a clock; needs no watcher because it EXECUTES
  ⛔ UNWATCHABLE  a deferral with NEITHER a predicate NOR a self-executing default

⚠️ **UNWATCHABLE IS THE NUMBER THAT MATTERS AND IT WILL START HIGH.** A checker over a population
that has never carried the field returns zero violations, and zero violations on an empty population
is the exact false green this repo spent 2026-09-07 finding in four separate instruments. **So the
denominator is printed first and the violation count second.**

USAGE
  deferral_unblocked.py                 # default roots: wiki/tracker, exchange
  deferral_unblocked.py --json
  deferral_unblocked.py --selftest      # RED (satisfied predicate, still open) + GREEN control
"""
import argparse
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOTS = [os.path.join("wiki", "tracker"), "exchange"]

# A deferral, as this program actually writes them.
DEFER = re.compile(r"(NOT RULED|NEEDS JON|DEFERRED|deferred to|awaiting Jon|blocked on Jon"
                   r"|UNDISPOSITIONED)", re.I)
UNBLOCK = re.compile(r"unblocked_by:\s*(\S+)", re.I)
# A self-executing default: this repo's own better mechanism -- it needs no watcher.
SELFCLOSE = re.compile(r"on[- ]silence", re.I)
# ⛔ THE NEGATIVE LOOKBEHIND IS LOAD-BEARING AND ITS ABSENCE INVERTED THIS WHOLE CHECK. Written as
# `\b(RULED|CLOSED|...)\b`, it matched the word **RULED inside "NOT RULED"** — so every genuinely
# deferred item read as CLOSED and was dropped before it could be classified. ⭐ The first live run
# still reported 343 UNWATCHABLE, which looked like a finding and was an UNDERCOUNT: the entire
# `NOT RULED` class — the most explicit deferral vocabulary this repo has — was invisible to it.
# ⚠️ Caught by this file's own selftest on its first run, because the RED fixture used the exact
# phrase from the real case (D-015 NOT RULED). A fixture drawn from the incident rather than
# invented is what made the difference.
CLOSED = re.compile(r"(?<!NOT )(?<!not )\b(RULED|CLOSED|RESOLVED|DONE|LANDED|WITHDRAWN|SUPERSEDED)\b")


def classify(line, resolve=os.path.exists):
    """(state, predicate) for one line, or (None, None) when the line defers nothing."""
    if not DEFER.search(line):
        return (None, None)
    if CLOSED.search(line):
        return (None, None)
    m = UNBLOCK.search(line)
    if m:
        pred = m.group(1).strip("`'\",;)")
        full = pred if os.path.isabs(pred) else os.path.join(REPO, pred)
        return (("UNBLOCKED" if resolve(full) else "WAITING"), pred)
    if SELFCLOSE.search(line):
        return ("SELF-CLOSING", None)
    return ("UNWATCHABLE", None)


def scan(roots):
    rows = []
    for root in roots:
        base = root if os.path.isabs(root) else os.path.join(REPO, root)
        for dirpath, dirnames, files in os.walk(base):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                full = os.path.join(dirpath, f)
                try:
                    text = io.open(full, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                for n, line in enumerate(text.splitlines(), 1):
                    state, pred = classify(line)
                    if state:
                        rows.append({"file": os.path.relpath(full, REPO).replace("\\", "/"),
                                     "line": n, "state": state, "predicate": pred,
                                     "text": line.strip()[:140]})
    return rows


def _selftest():
    import tempfile
    ok = {"p": 0, "f": 0}

    def check(label, got, want):
        if got == want:
            print("  [PASS] %s: got %r" % (label, got)); ok["p"] += 1
        else:
            print("  [FAIL] %s: got %r want %r" % (label, got, want)); ok["f"] += 1

    with tempfile.TemporaryDirectory() as d:
        real = os.path.join(d, "prototype.md")
        io.open(real, "w", encoding="utf-8").write("built\n")

        # RED ARM -- the D-015 shape exactly: deferred, predicate SATISFIED, still open.
        s, p = classify("D-015 NOT RULED — unblocked_by: %s" % real.replace("\\", "/"))
        check("a satisfied predicate on an open deferral is UNBLOCKED", s, "UNBLOCKED")
        check("it names the predicate so a reader can check it", bool(p), True)

        # GREEN CONTROL -- proves the RED arm can be false, which a permanently-red check cannot.
        s2, _ = classify("D-016 NOT RULED — unblocked_by: %s/never.md" % d.replace("\\", "/"))
        check("an unsatisfied predicate is WAITING, not a finding", s2, "WAITING")

        # THE HEADLINE CLASS: no predicate, no self-executing default.
        s3, _ = classify("D-017 NEEDS JON — we will revisit this when he is back")
        check("a deferral with no predicate is UNWATCHABLE", s3, "UNWATCHABLE")

        # This repo's BETTER mechanism: a default that executes needs no watcher at all.
        s4, _ = classify("WW-9 DEFERRED · on-silence (expires 2026-09-11): CFL adds all 23 to EXCLUDE")
        check("an on-silence default is SELF-CLOSING", s4, "SELF-CLOSING")

        # NEGATIVE CONTROLS -- without these every line in the repo becomes a row.
        check("a closed deferral is not reported", classify("D-018 NOT RULED — RULED 2026-09-01")[0], None)
        check("ordinary prose defers nothing", classify("read the file and think")[0], None)

    print("selftest: %d passed, %d failed" % (ok["p"], ok["f"]))
    return 0 if ok["f"] == 0 else 5


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", dest="roots")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    roots = a.roots or DEFAULT_ROOTS
    rows = scan(roots)
    if a.as_json:
        print(json.dumps(rows, indent=1))
        return 0
    tally = {}
    for r in rows:
        tally[r["state"]] = tally.get(r["state"], 0) + 1
    print("repo : %s\nroots: %s" % (REPO, ", ".join(roots)))
    print("\nDEFERRALS FOUND: %d   %s" % (len(rows), "  ".join("%s=%d" % kv for kv in sorted(tally.items()))))
    print("\n⚠️ READ THE DENOMINATOR FIRST. `UNWATCHABLE` is a deferral with neither a predicate nor a")
    print("   self-executing default -- nothing can ever tell you it came due. Zero UNBLOCKED rows on")
    print("   a population that is mostly UNWATCHABLE is not a clean bill; it is no measurement.")

    hits = [r for r in rows if r["state"] == "UNBLOCKED"]
    for r in hits:
        print("\n⛔ UNBLOCKED and still open: %s:%d\n   predicate SATISFIED: %s\n   %s" % (
            r["file"], r["line"], r["predicate"], r["text"]))
    return 3 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
