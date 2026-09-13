#!/usr/bin/env python
"""WS-5 -- make `queried:` a CHECKED field on wayfinder tickets, not a sentence in a command.

/wake Step 0b SAYS every ticket carries a `queried:` field. Nothing checked, and CFL's own finding
from the same day governs: a standard that reaches a seat's inbox -- or its skill list, or its
command text -- and not a MECHANISM is a standard nobody has.

WHAT COUNTS AS PRESENT: a `queried:` line under the ticket bullet, carrying the query string.
AN EMPTY RESULT IS A VALID VALUE and passes -- "I looked and the record is silent" is information.
A MISSING FIELD IS THE FAILURE, because it is indistinguishable from nobody having looked.

WHAT THIS REFUSES TO DO: grade a map whose open-ticket section it cannot find. That is UNKNOWN and
exits 2. An empty sweep and a clean sweep print the same bytes unless one of them says so.

  python scripts/audit/ticket_queried.py [--dir wiki/tracker] [--self-test]
  exit 0 = every open ticket on every LIVE map carries the field
  exit 1 = at least one open ticket is missing it
  exit 2 = UNKNOWN (no LIVE map found, or a LIVE map with no parseable ticket section)
"""
import io
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticket_rows import merged as parse_tickets  # noqa: E402  (MI-13: one matcher, both instruments)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# A ticket bullet: "- **WS-5 - task - AFK - UNCLAIMED - title**" or "- **P2-14 ...**"
TICKET = re.compile(r"^-\s+\*\*([A-Z][A-Z0-9]*-\d+)\b")
FIELD = re.compile(r"^\s*(?:[-*]\s*)?`?queried`?\s*:", re.I)
HEADING = re.compile(r"^#{1,6}\s")


def live_maps(root):
    """LIVE wayfinder maps, DERIVED. `canonical: true` is NOT the field to derive on -- a
    superseded map carries it and every live map does not (CLAUDE.md's 2026-08-24 correction)."""
    out = []
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        if not name.endswith(".md"):
            continue
        p = os.path.join(root, name)
        try:
            with io.open(p, encoding="utf-8", errors="replace") as f:
                head = f.read(4000)
        except OSError:
            continue
        if "kind: wayfinder:map" in head and re.search(r"^status:\s*[\"']?LIVE", head, re.M):
            out.append(p)
    return out


def open_tickets(path):
    """(rows, found_section) where rows is [(ticket_id, has_queried)].

    found_section=False means UNKNOWN -- never 'this map has no tickets'.

    MI-13, 2026-09-06: delegates to scripts/audit/ticket_rows.py, the ONE matcher shared with
    alignment_map.py. The previous body matched bullets under a heading containing "ticket" or
    "frontier" and nothing else; [measured 06:5x] it read 7 of 18 tickets on the map that carries
    MI-13, because that map's author switched to heading-form tickets one section later, and a
    heading-form ticket under a "## MI-1 -- RESOLVED" section was excluded by the section rule.
    Closure is now per row (an explicit closure word), not per section.
    """
    with io.open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    all_rows = parse_tickets(text)
    rows = [(r.id, r.queried) for r in all_rows if not r.closed]
    return rows, bool(all_rows)


def run(root):
    maps = live_maps(root)
    print("=== ticket_queried -- WS-5: is `queried:` a field, or only a sentence? ===")
    print("scanned : %s" % root)
    if not maps:
        print("UNKNOWN : no LIVE wayfinder:map found. That is UNKNOWN, not a pass -- an empty")
        print("          sweep and a clean sweep print the same bytes unless one of them says so.")
        return 2
    bad = unknown = total = 0
    for p in maps:
        rows, found = open_tickets(p)
        # relpath RAISES across Windows drive letters ("path is on mount 'C:', start on 'N:'").
        # Found by the selftest's temp-dir fixtures, which land on C: while the repo is on N: --
        # a crash a wiki/tracker run could never reach. Fall back to the absolute path.
        try:
            rel = os.path.relpath(p, REPO).replace(os.sep, "/")
        except ValueError:
            rel = p.replace(os.sep, "/")
        if not found:
            print("  UNKNOWN  %s -- no open-ticket/frontier heading found" % rel)
            unknown += 1
            continue
        print("  %s" % rel)
        for tid, has in rows:
            total += 1
            if has:
                print("    OK       %s" % tid)
            else:
                print("    MISSING  %s -- no `queried:` field; indistinguishable from nobody looking." % tid)
                bad += 1
    print("")
    print("open tickets: %d   missing `queried:`: %d   maps UNKNOWN: %d" % (total, bad, unknown))
    if unknown:
        print("UNKNOWN dominates a PASS.")
        return 2
    return 1 if bad else 0


def self_test():
    import subprocess
    import tempfile
    counts = {"p": 0, "f": 0}

    def ok(name, got, want):
        if got == want:
            counts["p"] += 1
            print("  PASS  %s" % name)
        else:
            counts["f"] += 1
            print("  FAIL  %s  got=%r want=%r" % (name, got, want))

    HDR = "---\nkind: wayfinder:map\nstatus: LIVE\n---\n\n## Open tickets\n\n"
    d = tempfile.mkdtemp(prefix="tq-")

    def write(name, body):
        io.open(os.path.join(d, name), "w", encoding="utf-8", newline="\n").write(body)

    def drop(*names):
        for n in names:
            try:
                os.remove(os.path.join(d, n))
            except OSError:
                pass

    write("m1.md", HDR + '- **WS-1 - task - a thing**\n  queried: "foo" -> wiki/x.md:1-9\n')
    ok("1 a map whose every open ticket carries the field exits 0", run(d), 0)

    # NEGATIVE CONTROL: the check must be able to FAIL, or it certifies everything.
    write("m2.md", HDR + "- **WS-2 - task - no field**\n  some prose\n")
    ok("2 a missing field exits 1 (negative control -- the check CAN fail)", run(d), 1)

    drop("m2.md")
    write("m3.md", HDR + '- **WS-3 - task - looked, found nothing**\n  queried: "x" -> NO HITS\n')
    ok("3 an EMPTY query result PASSES -- silence found is information", run(d), 0)

    drop("m1.md", "m3.md")
    write("m4.md", "---\nkind: wayfinder:map\nstatus: LIVE\n---\n\n## Notes\n\nprose only\n")
    ok("4 a LIVE map with no ticket section is UNKNOWN (exit 2), not a pass", run(d), 2)

    drop("m4.md")
    ok("5 zero LIVE maps is UNKNOWN (exit 2), not a clean sweep", run(d), 2)

    write("m6.md", "---\nkind: wayfinder:map\nstatus: SUPERSEDED\ncanonical: true\n---\n\n"
                   "## Open tickets\n\n- **WS-6 - task - stale**\n  no field\n")
    ok("6 a SUPERSEDED map carrying `canonical: true` is NOT scanned", run(d), 2)

    drop("m6.md")
    write("m7.md", "---\nkind: wayfinder:map\n---\n\n## Open tickets\n\n- **WS-7 - x**\n")
    ok("7 a map with NO status: field is not treated as LIVE", run(d), 2)

    # 8-9 THE ENTRY POINT. soul's mutation test, 2026-09-05: a check that tests a FUNCTION tests a
    # function; only one that crosses the entry point tests a PROGRAM. Both verdicts exercised,
    # because an entry point that always exits 0 passes case 8 and is useless.
    drop("m7.md")
    write("m8.md", HDR + '- **WS-8 - task - ok**\n  queried: "q" -> a.md:1\n')
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--dir", d],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    ok("8 THE ENTRY POINT RUNS and exits 0 on a clean map", r.returncode, 0)
    write("m9.md", HDR + "- **WS-9 - task - missing**\n  prose\n")
    r2 = subprocess.run([sys.executable, os.path.abspath(__file__), "--dir", d],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=120)
    ok("9 THE ENTRY POINT propagates the FAILURE exit (1), not just the message", r2.returncode, 1)

    print("  %d passed, %d failed" % (counts["p"], counts["f"]))
    return 0 if counts["f"] == 0 else 1


def main():
    root = os.path.join(REPO, "wiki", "tracker")
    if "--dir" in sys.argv:
        root = sys.argv[sys.argv.index("--dir") + 1]
    return run(root)


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
