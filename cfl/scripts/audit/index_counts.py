#!/usr/bin/env python3
"""Index-count drift detector — re-derives every wiki index's Sources count from disk.

WHY THIS EXISTS RATHER THAN A CORRECTED NUMBER
----------------------------------------------
Each trunk index carries a hand-maintained header of the form:

    ## Sources (132 files / 132 listed) *(drift flagged ... repaired ...)*

Those numbers have drifted repeatedly, and the repairs did not hold — the header records
a fact that nothing can notice going stale. Same shape as the ledger that read "183 pages"
for 12 days while the truth grew to 218, and as the census that hardcoded its own
valuation date. **Updating the numbers again would buy about eleven days.**

So this is the check, not the correction. It re-derives both figures from ground truth —
`files` by counting `*.md` on disk, `listed` by counting table rows that reference a
source path — and fails on disagreement. Wire it into the SU and drift becomes loud
instead of archaeological.

Two independent enumerations per Q3 ("re-derived by two agreeing enumerations at every SU,
never cached"): files-on-disk and rows-in-table are counted by different mechanisms and must
agree with each other AND with the header. Any two-way disagreement is reported separately,
because "the index lists a page that no longer exists" and "a page exists that the index
never listed" are different defects with different fixes.

THE FRESHNESS ARM, ADDED 2026-08-23 -- AND THE DEFECT IT EXISTS FOR IS THIS CHECK ITSELF
----------------------------------------------------------------------------------------
`--strict` reported **157/157 OK** on 2026-08-23 while `wiki/concepts/` and `wiki/sources/`
had not been written since **2026-08-07** -- sixteen days, 41 + 157 pages, and ZERO of the
five systems built in that window (memory-core, GraphRAG, the probe registry, the de-PII
deriver, the unsaid ledger) present in any of them. Measured: `grep -ril` returned 0 files
for each of the five.

The check was not wrong. It compares the index against the disk, **and they were equally
frozen**, so agreement was total and meaningless. A count check answers "do these two
numbers match", and a dead layer matches itself perfectly.

  > A CHECK WHOSE DENOMINATOR STOPPED GROWING REPORTS HEALTH FOREVER.

That is the same shape as the RATIO_FLOOR alarm tuned so it always fires, inverted: an alarm
tuned so it never can. Both are checks that carry no information.

So freshness is measured against a SECOND clock that is known to be moving -- the live
tracker layer. "Concepts have not moved in 16 days" is not by itself a defect (a quiet week
is quiet). **"Concepts have not moved in 16 days WHILE the tracker moved 40 times" is**, and
only the comparison can tell them apart.

WHY IT WARNS AND DOES NOT FAIL, stated so nobody "fixes" it into a gate without deciding to
------------------------------------------------------------------------------------------
Freshness is loud and **non-fatal by default, including under --strict**. Making it fatal
would block every standard update until a human-driven wiki ingest ran, which converts a
reporting gap into a stop -- and rules that produce stopping are defective rules here.
`--freshness-fatal` exists for when someone decides it should bite. **That is a decision,
not a default**, and it is deliberately not taken by this script.

Usage:
    python scripts/audit/index_counts.py                    # report
    python scripts/audit/index_counts.py --strict           # exit 1 on any COUNT drift (for the SU)
    python scripts/audit/index_counts.py --freshness-days 7 # staleness threshold (default 7)
    python scripts/audit/index_counts.py --freshness-fatal  # make a frozen layer exit 1 too
    python scripts/audit/index_counts.py --selftest         # exercise BOTH verdicts, then exit

Exit: 0 report-only, or 1 under --strict when any index disagrees with disk, or 1 under
--freshness-fatal when a knowledge layer is frozen while the live layer moved.
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# index file -> directory holding its source pages
INDEXES = [
    ("wiki/index.md",          "wiki/sources"),
    ("wiki/personal/index.md", "wiki/personal/sources"),
    ("wiki/home/index.md",     "wiki/home/sources"),
    ("wiki/pro/index.md",      "wiki/pro/sources"),
]

# "## Sources (132 files / 132 listed)" — both numbers optional-ish across trunks.
#
# WORD-ORDER CALIBRATION (2026-07-26). The first version accepted only the files-then-listed
# order. `wiki/personal/index.md` writes it the other way — "## Sources (45 listed / 49 files)"
# — so the regex read 45 as the file count, compared it to 49 on disk, and reported DRIFT
# against a header that was *exactly right* and was already declaring the 4-page listing gap
# itself. A false alarm on an honest header is worse than no check: it is the RATIO_FLOOR
# failure again, an alarm tuned so it always fires until nobody reads it.
#
# Both numbers are now captured BY NAME rather than by position, so either order parses and
# neither is inferred from where it sits.
HEADER = re.compile(
    r"^##\s*Sources\s*\("
    r"(?:(?P<a>\d+)\s*(?P<a_kind>files?|listed))"
    r"(?:\s*/\s*(?P<b>\d+)\s*(?P<b_kind>files?|listed))?"
    r"|^##\s*Sources\s*\((?P<bare>\d+)\s*\)",
    re.M | re.I)


def count_on_disk(root, srcdir):
    """Count every *.md under srcdir. This is THE definition of "source page" for this tool.

    DECISION (W-9, 2026-08-06): `sources/session-stubs.md` COUNTS. It is a real file living
    under `wiki/sources/`, and it is itself referenced by a backtick-quoted `.md` path
    elsewhere in `wiki/index.md` — it satisfies the same two structural tests (on-disk,
    listed) every other source page is held to. That it is semantically an INDEX OF sessions
    that fell below ingest threshold (per `CLAUDE.md`: referenced-but-absent is "below ingest
    threshold — not absent") is a fact about its *content*, not about whether it is a source
    page. Excluding it would require a second, file-named special case sitting outside this
    function — exactly the kind of asymmetric carve-out that produced the W-9 defect this
    decision closes (see wiki/index.md ~line 158 note and log.md 2026-08-06 W-9 entry).
    This function is the ONE place that definition is allowed to live; do not special-case
    session-stubs.md (or any other file) anywhere else, including in prose.
    """
    d = os.path.join(root, srcdir)
    if not os.path.isdir(d):
        return 0
    return sum(1 for dirpath, _, files in os.walk(d)
               for fn in files if fn.endswith(".md"))


def count_listed(root, index_path, srcdir):
    """Rows in the index that reference a page under THIS trunk's sources dir.

    Counted by a different mechanism than the disk walk on purpose — two agreeing
    enumerations, not one enumeration reported twice.

    CALIBRATION NOTE. The first version matched `(?:[\\w\\-./]*/)?sources/...`, which
    reported wiki/index.md as listing 135 against 132 on disk — three phantom rows that
    were not phantoms at all. Two were legitimate CROSS-TRUNK references
    (`personal/sources/...` cited from the FL index) that the loose prefix claimed for
    the wrong trunk; the third was a real FL page written with a `wiki/` prefix the
    normalization dropped. A detector that flags a correct index is worse than no
    detector, so paths are now RESOLVED — relative to the index's own directory when
    they lack a `wiki/` prefix — and counted only if they land under this trunk's srcdir.
    """
    p = os.path.join(root, index_path)
    if not os.path.isfile(p):
        return 0
    text = open(p, encoding="utf-8", errors="ignore").read()
    base = os.path.dirname(index_path).replace("\\", "/")   # e.g. "wiki/personal"
    want = srcdir.rstrip("/") + "/"
    hits = set()
    for raw in re.findall(r"`([\w\-./]+\.md)`", text):
        rel = raw.replace("\\", "/").lstrip("./")
        full = rel if rel.startswith("wiki/") else f"{base}/{rel}"
        full = os.path.normpath(full).replace("\\", "/")
        if full.startswith(want):
            hits.add(full)
    return len(hits)



# ---------------------------------------------------------------------------
# FRESHNESS -- git is the clock, NOT mtime.
#
# mtime is wrong here for a reason this repo has already paid for: the tree lives on Google
# Drive, and DriveFS rewrites mtimes on sync. A page nobody has edited since 08-07 can carry
# today's mtime purely because the drive re-materialised it. Every timestamp below therefore
# comes from `git log -1 --format=%ct`, which records when the CONTENT changed.
# ---------------------------------------------------------------------------
KNOWLEDGE_DIRS = ["wiki/concepts", "wiki/sources"]
LIVE_DIRS = ["wiki/tracker"]


def last_commit_epoch(root, path):
    """Epoch seconds of the newest commit touching `path`, or None if unknown.

    None means UNKNOWN -- not 'never', and not 'now'. Callers must not fold it into
    either, because a check that could not run is not a check that passed.
    """
    import subprocess
    if not os.path.isdir(os.path.join(root, path)):
        return None
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "-1", "--format=%ct", "--", path],
            capture_output=True, text=True, timeout=60,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    v = out.stdout.strip()
    return int(v) if v.isdigit() else None


def commits_since(root, path, since_epoch):
    """How many commits touched `path` after `since_epoch`. None if unknown."""
    import subprocess
    if since_epoch is None or not os.path.isdir(os.path.join(root, path)):
        return None
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "--oneline",
             f"--since=@{since_epoch}", "--", path],
            capture_output=True, text=True, timeout=60,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    return len([ln for ln in out.stdout.splitlines() if ln.strip()])


def freshness_report(root, threshold_days, as_of_epoch=None):
    """Report knowledge-layer staleness against the live layer. Returns True if frozen."""
    import time
    now = as_of_epoch if as_of_epoch is not None else int(time.time())

    print("\n=== freshness -- the knowledge layer against a clock known to be moving ===\n")

    live_epoch = None
    live_name = None
    for d in LIVE_DIRS:
        e = last_commit_epoch(root, d)
        if e is not None and (live_epoch is None or e > live_epoch):
            live_epoch, live_name = e, d

    if live_epoch is None:
        print("  UNKNOWN -- no live-layer reference commit found; freshness NOT evaluated.")
        print("  A check that could not run is UNKNOWN, and UNKNOWN does not pass.")
        return False

    live_age = (now - live_epoch) / 86400.0
    print(f"  reference (live)  {live_name:<18} last written {live_age:5.1f} d ago")

    frozen = False
    for d in KNOWLEDGE_DIRS:
        e = last_commit_epoch(root, d)
        if e is None:
            print(f"  {d:<28} UNKNOWN -- not a directory, or git could not answer")
            continue
        age = (now - e) / 86400.0
        moved = commits_since(root, LIVE_DIRS[0], e)
        moved_txt = "?" if moved is None else str(moved)
        stale = age > threshold_days
        # A quiet week is quiet. A quiet week WHILE the live layer moved is a defect.
        bad = stale and (moved or 0) > 0
        verdict = "FROZEN" if bad else ("stale" if stale else "ok")
        print(f"  {d:<28} last written {age:5.1f} d ago   "
              f"live layer moved {moved_txt:>4} times since   {verdict}")
        if bad:
            frozen = True

    if frozen:
        print()
        print(f"  FROZEN: a knowledge layer has not been written in over {threshold_days} d")
        print("  while the live layer kept moving. The count check above can NEVER see this --")
        print("  it compares the index to the disk, and a dead layer matches itself perfectly.")
        print("  The live layer is disposable by design, so knowledge that lands only there is")
        print("  scheduled for deletion. Dispatch a wiki ingest; do not silence this line.")
    return frozen


def selftest():
    """Exercise BOTH verdicts. A check only ever seen passing has not been tested.

    Written because three acceptance criteria in this repo named artifacts the system could
    never produce, and each was only caught by someone asking for the failing case.
    """
    import tempfile, subprocess, time
    ok = True
    now = int(time.time())
    day = 86400

    def run(cwd, *args):
        return subprocess.run(["git", "-C", cwd] + list(args),
                              capture_output=True, text=True)

    with tempfile.TemporaryDirectory() as td:
        run(td, "init", "-q")
        run(td, "config", "user.email", "selftest@local")
        run(td, "config", "user.name", "selftest")
        for d in ("wiki/concepts", "wiki/sources", "wiki/tracker"):
            os.makedirs(os.path.join(td, d), exist_ok=True)

        def commit(path, body, epoch):
            full = os.path.join(td, path)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(body)
            run(td, "add", "-A")
            stamp = f"{epoch} +0000"
            env = dict(os.environ, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
            subprocess.run(["git", "-C", td, "commit", "-q", "-m", "x"],
                           capture_output=True, text=True, env=env)

        # --- NEGATIVE CONTROL: everything written today -> must NOT be frozen ---
        commit("wiki/concepts/a.md", "a", now - 1 * day)
        commit("wiki/sources/a.md", "a", now - 1 * day)
        commit("wiki/tracker/t.md", "t", now - 1 * day)
        print("--- selftest case 1: all layers fresh (expect: NOT frozen) ---")
        got = freshness_report(td, 7, as_of_epoch=now)
        print(f"    -> frozen={got}  expected=False  "
              f"{'PASS' if got is False else 'FAIL'}\n")
        ok &= (got is False)

        # --- POSITIVE CONTROL: live layer moves, knowledge layer does not ---
        for i in range(3):
            commit("wiki/tracker/t.md", f"t{i}", now - (2 - i) * 3600)
        print("--- selftest case 2: knowledge frozen 16 d, live layer moving "
              "(expect: FROZEN) ---")
        got = freshness_report(td, 7, as_of_epoch=now + 16 * day)
        print(f"    -> frozen={got}  expected=True   "
              f"{'PASS' if got is True else 'FAIL'}\n")
        ok &= (got is True)

    print("SELFTEST PASS" if ok else "SELFTEST FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on any COUNT drift — use this in the SU")
    ap.add_argument("--freshness-days", type=int, default=7,
                    help="a knowledge layer untouched longer than this is stale (default 7)")
    ap.add_argument("--freshness-fatal", action="store_true",
                    help="also exit 1 when a knowledge layer is FROZEN. NOT the default: "
                         "see the module docstring — turning this on is a decision to make "
                         "the standard update stop until a human-driven ingest runs")
    ap.add_argument("--selftest", action="store_true",
                    help="exercise both freshness verdicts and exit")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    print("=== index-count drift — re-derived from disk, never cached ===\n")
    print(f"  {'index':<24} {'header':>14} {'on disk':>8} {'listed':>7}   verdict")
    print(f"  {'-'*24} {'-'*14} {'-'*8} {'-'*7}   {'-'*7}")

    drift = 0
    for index_path, srcdir in INDEXES:
        p = os.path.join(a.root, index_path)
        if not os.path.isfile(p):
            print(f"  {index_path:<24} {'MISSING':>14}")
            drift += 1
            continue
        text = open(p, encoding="utf-8", errors="ignore").read()
        m = HEADER.search(text)
        claimed_files = claimed_listed = None
        if m:
            if m.group("bare") is not None:
                # "## Sources (26)" — a single unlabelled number. It is the FILE count by
                # the convention every trunk that writes it this way has used.
                claimed_files = int(m.group("bare"))
            else:
                # Labelled numbers, assigned by their own word, not by position.
                for num, kind in ((m.group("a"), m.group("a_kind")),
                                  (m.group("b"), m.group("b_kind"))):
                    if num is None or kind is None:
                        continue
                    if kind.lower().startswith("file"):
                        claimed_files = int(num)
                    else:
                        claimed_listed = int(num)
        on_disk = count_on_disk(a.root, srcdir)
        listed = count_listed(a.root, index_path, srcdir)

        bad = []
        if claimed_files is None:
            bad.append("no parseable Sources header")
        elif claimed_files != on_disk:
            bad.append(f"header says {claimed_files} files, disk has {on_disk}")
        if claimed_listed is not None and claimed_listed != listed:
            bad.append(f"header says {claimed_listed} listed, table has {listed}")
        if listed and on_disk and listed != on_disk:
            bad.append(f"table lists {listed} but disk has {on_disk} "
                       f"({'unlisted pages exist' if on_disk > listed else 'index lists missing pages'})")

        hdr = (f"{claimed_files}" + (f"/{claimed_listed}" if claimed_listed is not None else "")) \
            if claimed_files is not None else "?"
        print(f"  {index_path:<24} {hdr:>14} {on_disk:>8} {listed:>7}   "
              f"{'OK' if not bad else 'DRIFT'}")
        for b in bad:
            print(f"      - {b}")
        if bad:
            drift += 1

    print()
    if drift:
        print(f"DRIFT in {drift} of {len(INDEXES)} indexes. These headers record a fact nothing")
        print("can notice going stale — recompute them here rather than editing the number by hand.")
    else:
        print(f"All {len(INDEXES)} indexes agree with disk.")
        print("⚠ Agreement is NOT liveness — see the freshness arm below. On 2026-08-23 this")
        print("  line read OK while the knowledge layer had been frozen for sixteen days.")

    frozen = freshness_report(a.root, a.freshness_days)

    if drift and a.strict:
        return 1
    if frozen and a.freshness_fatal:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
