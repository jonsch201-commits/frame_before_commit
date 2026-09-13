#!/usr/bin/env python
"""ticket_id_unique.py -- refuse to mint a ticket id that already means something else.

WHY THIS EXISTS, and it is two seats making the same mistake ninety minutes apart on 2026-09-06/07.

  * CFL N 2 compact 0 wikiskills improved a real skill and logged it as `WS-1`. `WS-1` already
    existed -- `wiki/tracker/wayfinder-wikiskills-grounding-2026-09-05.md:42`, "Does the retrieval
    stack actually work?" Different ticket, same id, same subsystem.
  * CFL N 1 compact 2 then wrote a peer-review letter NAMING that collision, and in the same letter
    minted `WS-2` -- which also already existed, line 46, ONE ROW BELOW the row it cited.

⭐ THE DIAGNOSIS IS THE CHILD SEAT'S AND IT IS WHY THIS IS A SCRIPT AND NOT A RESOLUTION:
    "I *did* run section 0 step 3 -- query before you build. I queried for prior art on the DEFECT
     and never for a collision on the NAME. Those are two different queries and step 3 only
     mandates the first."
So the gate could not catch it as written, both seats were following the rule, and the fix is an
artifact. MISSING ARTIFACT, NOT MISSING INSIGHT -- this repo's own named class.

WHAT IT CHECKS, and the scope is the point: EVERY tracker file, not one map. Both collisions were
CROSS-MAP -- the id was free on the map being written and taken on a map nobody had open. A checker
scoped to the current file would have passed both times.

⛔ NOTHING IS RENAMED, EVER. The 2026-08-09 no-deletion ruling governs and the collisions are the
evidence. This refuses a NEW id; it never edits an existing row.

USAGE
  ticket_id_unique.py --id WW-25              # exit 0 free, exit 3 taken (prints every hit)
  ticket_id_unique.py --next WW               # print the next free id for a prefix
  ticket_id_unique.py --list WW               # every live id for a prefix, in order
  ticket_id_unique.py --selftest              # RED fixture (collision) + GREEN control

  ⚠️ EXIT 3 IS THE COLLISION SIGNAL AND A PIPE HIDES IT. `... --id X | tail -5` reports tail's
  status, so `$?` reads 0 on a collision. Read the printed verdict, or capture the exit code
  before piping. (Professional N 1 compact 2, 2026-09-07 -- caught while adopting this tool.)

  --tracker DIR   override the tracker root (default: derived from __file__, printed every run)

⚠️ THE TRACKER ROOT IS DERIVED FROM `__file__`, NOT FROM THE CALLER'S CWD, and it is printed on
every run. `disposition_resolves.py` defaulted to the relative path `wiki/tracker` and a peer lane
running it from ANOTHER TRUNK graded that trunk's rows while reporting on CFL's ids (fixed
aa973477). A checker that silently checks the wrong tree returns a confident PASS.
"""
import argparse
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# A ticket id as this program actually writes them: 1-4 uppercase letters, a hyphen, digits.
# Deliberately generic -- it catches WW-, WS-, MI-, RP-, T-, OI-, P2-, P3- and anything a future
# map invents, because the two collisions on record were both cross-PREFIX-family surprises.
ID_RE = re.compile(r"\b([A-Z][A-Z0-9]{0,3})-(\d{1,4})\b")

DEFAULT_TRACKER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "wiki", "tracker")


def _iter_files(tracker_dir, extra_roots):
    """Tracker *.md, PLUS any file under --extra-roots.

    ⛔ THE POPULATION IS THE BOUND, AND THIS TOOL SHIPPED WITHOUT SAYING SO. Professional N 1
    compact 2 adopted it 2026-09-07 and immediately caught it returning
    `OK  C27 is free across 22 tracker file(s)` for an id that is LIVE in that trunk -- a lint
    check at `scripts/lint.sh:754`, with C1-C31 and C97-99 all taken there. The count was true and
    the population was wrong: check-ids live in a shell script, not in tracker markdown.
    ⭐ That is the exact class this file exists to prevent, committed by this file. The logic is
    sound; what was missing is the BOUND PRINTED ON EVERY RUN and a way to widen it. A confident OK
    over the wrong population is worse than no checker, because it retires the caller's suspicion."""
    for name in sorted(os.listdir(tracker_dir)):
        if name.endswith(".md"):
            yield os.path.join(tracker_dir, name)
    for root in extra_roots or []:
        if os.path.isfile(root):
            yield root
        elif os.path.isdir(root):
            for dirpath, _dirs, files in os.walk(root):
                for f in sorted(files):
                    yield os.path.join(dirpath, f)


def scan(tracker_dir, extra_roots=None):
    """{id: [(path, lineno, line), ...]} over the population named by _iter_files()."""
    hits = {}
    if not os.path.isdir(tracker_dir):
        return None
    for path in _iter_files(tracker_dir, extra_roots):
        try:
            text = io.open(path, encoding="utf-8", errors="replace").read()
        except (OSError, ValueError):
            continue
        name = os.path.basename(path)
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in ID_RE.finditer(line):
                hits.setdefault(m.group(0), []).append((name, lineno, line.strip()[:120]))
    return hits


def check_one(tid, hits, tracker_dir=None, extra_roots=None):
    """⛔ AND THE SECOND BOUND WAS THE ID GRAMMAR, not the population -- found by finishing the
    investigation instead of shipping the first fix. Widening the population to
    `scripts/lint.sh` STILL reported `C27` free, because that trunk writes its check ids as a BARE
    TOKEN (`fail C27 "..."`, lint.sh:754) and this file's ID_RE requires `PREFIX-DIGITS`. CFL writes
    `WW-24`; Professional writes `C27`; the regex encoded one house style as if it were the concept.
    ⭐ So a specific `--id` is now matched LITERALLY, word-bounded, over the raw text -- whatever
    shape it has. ID_RE still drives `--next`/`--list`, which must enumerate a family and therefore
    must know its grammar; those stay honestly bounded to hyphenated ids and say so.
    ⚠️ TWO INDEPENDENT BOUNDS, EACH SUFFICIENT TO PRODUCE A CONFIDENT FALSE OK. Fixing the first
    and publishing would have been the same defect with a fresher date."""
    rows = list(hits.get(tid, []))
    if tracker_dir:
        pat = re.compile(r"(?<![A-Za-z0-9_-])%s(?![A-Za-z0-9_-])" % re.escape(tid))
        seen = {(p, n) for p, n, _ in rows}
        for path in _iter_files(tracker_dir, extra_roots):
            try:
                text = io.open(path, encoding="utf-8", errors="replace").read()
            except (OSError, ValueError):
                continue
            name = os.path.basename(path)
            for lineno, line in enumerate(text.splitlines(), 1):
                if pat.search(line) and (name, lineno) not in seen:
                    rows.append((name, lineno, line.strip()[:120]))
                    seen.add((name, lineno))
    return (len(rows) == 0), rows


def next_free(prefix, hits):
    used = {int(k.split("-", 1)[1]) for k in hits if k.split("-", 1)[0] == prefix}
    n = 1
    while n in used:
        n += 1
    return "%s-%d" % (prefix, n)


def _selftest():
    """RED fixture and GREEN control, both synthetic -- the checker must be able to FAIL."""
    import tempfile
    ok = {"pass": 0, "fail": 0}

    def check(label, got, want):
        if got == want:
            print("  [PASS] %s: got %r" % (label, got))
            ok["pass"] += 1
        else:
            print("  [FAIL] %s: got %r want %r" % (label, got, want))
            ok["fail"] += 1

    with tempfile.TemporaryDirectory() as d:
        io.open(os.path.join(d, "map-a.md"), "w", encoding="utf-8").write(
            "# map a\n- **WS-1 - Does the retrieval stack actually work?**\n"
            "- **WS-2 - Is wiki-query silently non-triggering?**\n")
        io.open(os.path.join(d, "map-b.md"), "w", encoding="utf-8").write(
            "# map b\n- **WW-1 - the pipeline runs twice**\n")
        hits = scan(d, None)

        # RED ARM: the exact collision that happened, and it is CROSS-MAP -- the seat was writing
        # map-b and the id was taken on map-a. A same-file checker passes here and is useless.
        free, rows = check_one("WS-2", hits)
        check("a taken id on ANOTHER map is refused", free, False)
        check("the refusal names where it is taken", rows[0][0] if rows else None, "map-a.md")

        # GREEN CONTROL: proves the RED arm can be false. Without this the checker could be stuck
        # on 'taken' forever and every assertion above would still pass -- a row riding another
        # row's failure, a defect class already on this repo's record.
        free_ok, rows_ok = check_one("WW-99", hits)
        check("an unused id is allowed", free_ok, True)
        check("an allowed id names no location", rows_ok, [])

        # BARE-TOKEN ARM: the id grammar bound. `C27` has no hyphen, so ID_RE never sees it and
        # the dict lookup alone returns "free" on a live id -- Professional's real case.
        io.open(os.path.join(d, "lint.sh"), "w", encoding="utf-8").write(
            'check_stamp_future() { fail C27 "oath-checks skill absent"; }' + os.linesep)
        free_bare, rows_bare = check_one("C27", scan(d, [os.path.join(d, "lint.sh")]),
                                         d, [os.path.join(d, "lint.sh")])
        check("a BARE-TOKEN id (no hyphen) in a shell script is refused", free_bare, False)
        check("the bare-token refusal names the file", rows_bare[0][0] if rows_bare else None, "lint.sh")
        free_ctl, _ = check_one("C99", scan(d, [os.path.join(d, "lint.sh")]),
                                d, [os.path.join(d, "lint.sh")])
        check("control: an unused bare token is still allowed", free_ctl, True)

        check("next free WW is WW-2", next_free("WW", hits), "WW-2")
        check("next free WS is WS-3", next_free("WS", hits), "WS-3")

        # A tracker root that does not exist is UNKNOWN, never 'no collisions'. This is the
        # failure mode that makes a checker dangerous: it would license every id ever minted.
        check("a missing tracker root returns None, not an empty dict", scan(os.path.join(d, "nope"), None), None)

    print("selftest: %d passed, %d failed" % (ok["pass"], ok["fail"]))
    return 0 if ok["fail"] == 0 else 5


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", help="the id you are about to mint, e.g. WW-25")
    ap.add_argument("--next", metavar="PREFIX", help="print the next free id for a prefix")
    ap.add_argument("--list", metavar="PREFIX", help="list every live id for a prefix")
    ap.add_argument("--tracker", default=DEFAULT_TRACKER)
    ap.add_argument("--extra-roots", default="",
                    help="comma-separated extra files/dirs to include in the population -- e.g. "
                         "a trunk whose check-ids live in scripts/lint.sh rather than in tracker "
                         "markdown. WITHOUT THIS the answer is bounded to tracker *.md.")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return _selftest()
    if not (a.id or a.next or a.list):
        ap.error("one of --id / --next / --list / --selftest is required")

    extra = [x.strip() for x in a.extra_roots.split(",") if x.strip()]
    print("tracker: %s" % os.path.abspath(a.tracker))
    hits = scan(a.tracker, extra)
    if hits is None:
        print("UNKNOWN: tracker root does not exist -- this is NOT 'no collisions'. "
              "Pass --tracker, or run from a checkout that has wiki/tracker/.")
        return 2

    pop = len({p for v in hits.values() for p, _, _ in v})
    print("population: tracker *.md%s -- ids seen in %d file(s)" % (
        (" + " + ", ".join(extra)) if extra else "", pop))
    print("BOUND: an id defined OUTSIDE this population is invisible here (Professional N1 C2, "
          "2026-09-07: C27 read as free while live in scripts/lint.sh). Widen with --extra-roots.")
    if a.list:
        ids = sorted((k for k in hits if k.split("-", 1)[0] == a.list),
                     key=lambda k: int(k.split("-", 1)[1]))
        print("%s: %d live id(s): %s" % (a.list, len(ids), " ".join(ids)))
        return 0
    if a.next:
        print("next free: %s" % next_free(a.next, hits))
        return 0

    free, rows = check_one(a.id, hits, a.tracker, extra)
    if free:
        print("OK  %s is free IN THIS POPULATION (%d file(s)). That is not the same claim as "
              "'free'." % (a.id, pop))
        return 0
    print("COLLISION  %s already means something else -- %d occurrence(s):" % (a.id, len(rows)))
    for path, lineno, line in rows[:10]:
        print("    %s:%d  %s" % (path, lineno, line))
    print("Pick another id (try --next %s). Do NOT rename the existing row: no-deletion governs "
          "and the collision is the evidence." % a.id.split("-", 1)[0])
    return 3


if __name__ == "__main__":
    sys.exit(main())
