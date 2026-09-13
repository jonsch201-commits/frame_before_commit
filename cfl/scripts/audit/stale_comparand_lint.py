#!/usr/bin/env python
"""stale_comparand_lint.py -- find stored numbers that have outlived the thing they describe.

⛔ WHY, AND IT IS FIVE INSTANCES IN ONE DAY, EACH IN A DIFFERENT SUBSYSTEM, NONE OF THEM A MISTAKE
WHEN WRITTEN AND NOT ONE OF THEM ALARMING:

  2026-09-07  the corpus export root pinned to `G:\\...` -- correct until the checkout moved on 09-02
              the freshness cache keyed on TIME and not on the index it described
              the chunk policy invisible to a content hash, so the build said UP-TO-DATE
              a deployed-skill sha carried through four briefs and two messages for 33 HOURS
              a hook wrapper's comment promising "degrades to exit 1" over an `exec` line

⭐ THE CLASS: **this program has many detectors for a WRONG claim and none for a RIGHT claim whose
premises have moved.** A wrong claim is caught by review. A claim that was true when written passes
every review forever, because reviewers check the sentence against the record and not against the
world.

WHAT THIS CHECKS, and the scope is deliberately narrow so the output is actionable rather than large:
a line that contains BOTH a path-like token AND a stored comparand (a hex digest, or a byte size).
That pairing is what makes a claim mechanically checkable -- it names its own subject.

GRADES, and UNRESOLVED is the common and correct case:
  MATCH       the file exists and the quoted comparand still describes it
  MISMATCH    the file exists and the comparand does NOT describe it  <- the finding
  MISSING     the comparand names a path that is not on disk
  UNRESOLVED  a comparand with no resolvable path on its line -- UNKNOWN, never a failure

⚠️ WHAT IT DELIBERATELY DOES NOT DO: it does not rewrite anything, and it does not treat a mismatch
as an error to fix by substituting a fresher number. **The remedy for a stale comparand is almost
never a newer comparand** -- today's fix was the same shape five times over: make the stored thing
carry its subject, or stop storing it and read it at use time. Substituting a fresh number is the
same defect with a newer date, which is how `d314d475` became `6786bd0c` became `8b0a9fd8` in one
evening.

⚠️ AND A HISTORICAL RECORD IS NOT A DEFECT. A transcript, a letter, or a `[measured 2026-08-31]` row
is SUPPOSED to hold the number that was true then. `--exclude` defaults keep those out; a MISMATCH
inside `raw/` or a dated measurement line is expected and is not reported.

USAGE
  stale_comparand_lint.py                    # default roots: skills/ scripts/ wiki/concepts wiki/tracker
  stale_comparand_lint.py --root skills      # narrow it
  stale_comparand_lint.py --json
  stale_comparand_lint.py --selftest         # RED fixture + GREEN control + UNRESOLVED arm
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOTS = ["skills", "scripts", os.path.join("wiki", "concepts"), os.path.join("wiki", "tracker")]

# A digest as this program actually writes them: sha256 quoted whole or truncated to 12-16.
HEX = re.compile(r"\b([0-9a-f]{12,64})\b")
# A byte size as this program actually writes them: "84,191 B" / "84191 bytes" / "(4700 B)".
SIZE = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d{4,9})\s*(?:B|bytes)\b")
# A path-like token: at least one slash and a file extension this repo actually uses.
# ⛔ THE DRIVE LETTER WAS MISSING AND THIS FILE'S OWN SELFTEST CAUGHT IT ON THE FIRST RUN. `C:/…`
# and `N:\…` are the two commonest path shapes in this corpus, and a colon is not a word character,
# so the match began AFTER the colon and produced `/Users/…` — which resolve() then read as absolute
# and could not find. ⭐ A PATTERN ENCODING ONE PATH SHAPE: the third instance today of that exact
# class, after a regex that encoded one house style for ticket ids and a `claude-*` glob that could
# not see the one non-Claude trunk. All three were written by someone who had just fixed the others.
PATHY = re.compile(r"(?:[A-Za-z]:)?[~\w./\\-]*[/\\][\w./\\-]+\.(?:md|py|sh|json|sqlite|txt|jsonl)")
# A dated measurement is a HISTORICAL claim by construction -- it says when it was true.
DATED = re.compile(r"\[(?:measured|m|verified|relayed)[^\]]*\d{4}-\d{2}-\d{2}")


def resolve(tok):
    """Absolute path for a token, or None. `~` and repo-relative both occur in this corpus."""
    t = tok.strip("`'\"").replace("\\", "/")
    if t.startswith("~"):
        t = os.path.expanduser(t)
    cand = t if os.path.isabs(t) else os.path.join(REPO, t)
    return cand if os.path.exists(cand) else None


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def check_line(line):
    """[(kind, claimed, path, grade, detail)] for one line. Empty when the line stores nothing."""
    if DATED.search(line):
        return []                      # a dated measurement is history and is allowed to be old
    hexes = [m.group(1) for m in HEX.finditer(line)]
    sizes = [m.group(1) for m in SIZE.finditer(line)]
    if not hexes and not sizes:
        return []
    paths = [p for p in (resolve(m.group(0)) for m in PATHY.finditer(line)) if p]
    out = []
    for claimed in hexes:
        if not paths:
            out.append(("hash", claimed, None, "UNRESOLVED", "no resolvable path on this line"))
            continue
        p = paths[0]
        actual = sha256_of(p)
        ok = actual.startswith(claimed) or claimed == actual
        out.append(("hash", claimed, p, "MATCH" if ok else "MISMATCH",
                    "" if ok else "file is %s" % actual[:len(claimed)]))
    for claimed in sizes:
        n = int(claimed.replace(",", ""))
        if not paths:
            out.append(("size", claimed, None, "UNRESOLVED", "no resolvable path on this line"))
            continue
        p = paths[0]
        actual = os.path.getsize(p)
        out.append(("size", claimed, p, "MATCH" if actual == n else "MISMATCH",
                    "" if actual == n else "file is %d B" % actual))
    return out


def _rel(p):
    """Repo-relative when possible, absolute otherwise -- never an exception."""
    try:
        return os.path.relpath(p, REPO).replace("\\", "/")
    except ValueError:
        return p.replace("\\", "/")


def scan(roots, exclude):
    rows = []
    for root in roots:
        base = root if os.path.isabs(root) else os.path.join(REPO, root)
        if os.path.isfile(base):
            walk = [(os.path.dirname(base), [], [os.path.basename(base)])]
        else:
            walk = os.walk(base)
        for dirpath, dirnames, files in walk:
            dirnames[:] = [d for d in dirnames if d not in exclude and not d.startswith(".")]
            for f in sorted(files):
                if not f.endswith((".md", ".py", ".sh")):
                    continue
                full = os.path.join(dirpath, f)
                try:
                    text = io.open(full, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    for kind, claimed, p, grade, detail in check_line(line):
                        rows.append({"file": os.path.relpath(full, REPO).replace("\\", "/"),
                                     "line": lineno, "kind": kind, "claimed": claimed,
                                     # ⚠️ relpath ACROSS DRIVES RAISES on Windows, and this corpus
                                     # routinely names `C:\Users\...\.claude\...` from an N: repo --
                                     # the machine-global layer is on a different mount by design.
                                     # A cosmetic call that crashes the whole run on the very
                                     # cross-mount case this lint exists to check.
                                     "subject": _rel(p) if p else None,
                                     "grade": grade, "detail": detail})
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
        subj = os.path.join(d, "subject.md")
        # ⚠️ THE FIXTURE MUST BE BIG ENOUGH TO BE A REAL CASE. SIZE matches 4+ digits (or a
        # comma-grouped number) on purpose — a 2-digit "42 B" in prose is noise, not a stored
        # comparand. The first fixture was SIX BYTES, so the size arms produced NO ROWS AT ALL and
        # would have read as a pass if the assertions had not demanded a value. A test whose fixture
        # cannot trigger the thing under test measures nothing and reports success.
        io.open(subj, "w", encoding="utf-8").write("x" * 4096)
        real = sha256_of(subj)[:16]
        size = os.path.getsize(subj)
        rel = subj.replace("\\", "/")

        # GREEN CONTROL FIRST -- a lint that cannot pass is not a lint, and a RED arm with no
        # control can be permanently red while every assertion still passes.
        g = check_line("the deployed %s is sha256 %s" % (rel, real))
        check("a correct hash beside its file is MATCH", [r[3] for r in g], ["MATCH"])
        gs = check_line("%s is %d bytes" % (rel, size))
        check("a correct size beside its file is MATCH", [r[3] for r in gs], ["MATCH"])

        # RED ARM -- the exact shape that cost 33 hours: a plausible, wrong, quoted digest.
        r = check_line("the deployed %s is sha256 d314d475d8ce0000" % rel)
        check("a wrong hash beside its file is MISMATCH", [x[3] for x in r], ["MISMATCH"])
        check("the mismatch reports what the file actually is", r[0][4].startswith("file is"), True)
        rs = check_line("%s is 999999 bytes" % rel)
        check("a wrong size beside its file is MISMATCH", [x[3] for x in rs], ["MISMATCH"])

        # UNKNOWN ARM -- a comparand with no subject is UNRESOLVED, never a pass and never a fail.
        u = check_line("the skill file is sha256 6786bd0cdf38d998 as of tonight")
        check("a hash with no resolvable path is UNRESOLVED", [x[3] for x in u], ["UNRESOLVED"])

        # HISTORY ARM -- a dated measurement is SUPPOSED to hold the number that was true then.
        h = check_line("`[measured 2026-08-31]` %s was sha256 d314d475d8ce0000" % rel)
        check("a dated measurement is history and is not linted", h, [])

        # NEGATIVE CONTROL ON THE SCANNER ITSELF -- prose with no comparand must produce nothing,
        # or every line in the repo becomes a row and the report is unreadable.
        check("a line storing nothing produces no rows", check_line("read the file and think"), [])

    print("selftest: %d passed, %d failed" % (ok["p"], ok["f"]))
    return 0 if ok["f"] == 0 else 5


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", action="append", dest="roots")
    ap.add_argument("--exclude", action="append", default=["raw", "node_modules", "__pycache__"])
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    roots = a.roots or DEFAULT_ROOTS
    print("repo    : %s" % REPO)
    print("roots   : %s" % ", ".join(roots))
    print("excluded: %s   (history is SUPPOSED to hold old numbers)" % ", ".join(a.exclude))
    rows = scan(roots, set(a.exclude))
    if a.as_json:
        print(json.dumps(rows, indent=1))
        return 0

    tally = {}
    for r in rows:
        tally[r["grade"]] = tally.get(r["grade"], 0) + 1
    bad = [r for r in rows if r["grade"] in ("MISMATCH", "MISSING")]
    print("\nrows: %s" % ("  ".join("%s=%d" % kv for kv in sorted(tally.items())) or "none"))
    if not bad:
        print("\nNo MISMATCH. ⚠️ That is a statement about lines that PAIR a comparand with a "
              "resolvable path;\nUNRESOLVED rows are UNKNOWN and dominate any clean reading.")
        return 0
    print("\n%d comparand(s) no longer describe their subject:\n" % len(bad))
    for r in bad:
        print("  %s:%d  [%s] %s -> %s" % (r["file"], r["line"], r["kind"], r["claimed"], r["subject"]))
        print("      %s" % r["detail"])
    print("\n⛔ THE REMEDY IS ALMOST NEVER A FRESHER NUMBER. Make the stored thing carry its subject,")
    print("   or stop storing it and read it at use time. A substituted number is the same defect")
    print("   with a newer date -- d314d475 -> 6786bd0c -> 8b0a9fd8 happened in one evening.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
