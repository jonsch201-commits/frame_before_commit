#!/usr/bin/env python3
"""session_parent.py — derive a session's PARENT session, or say honestly that there is none.

WHY, measured 2026-09-04 22:0x: `postcompact_pipeline.py` step 7 appends a lineage row whose
`parent` field is the string literal `"UNKNOWN-predates-lineage"` -- on EVERY row, forever -- and
then grades the step **PASS**.

⛔ SO THE LINEAGE FILE HAS NO LINEAGE IN IT, and the gate that writes it cannot fail on that
account. Two lines below the constant, that same step carries this comment, about the `session`
field: *"A gate whose only input is a fallback default is a gate that CANNOT FAIL."* ⭐ The warning
and the defect are four lines apart in one function. Naming a failure mode does not immunise the
code underneath it.

⚠️ This is ADJACENT TO, AND NOT THE SAME AS, Secretary's LINEAGE-1 (elder consult 2026-09-04):
theirs is `postcompact-pipeline.py` (hyphen, THEIR tree) keying the parent on the newest-mtime
JSONL, which picks up a Stop-hook critic fork -- 5 of their 10 rows name a fork as parent. ⛔ CFL's
script never derived a parent at all, so it could not make that error and could not make a correct
row either. **Do not report CFL as confirming LINEAGE-1; different file, different mechanism, same
class.** A finding relayed onto the wrong file is how a fix gets closed against the wrong artifact.

WHAT IS ACTUALLY DERIVABLE, measured rather than assumed
--------------------------------------------------------
There is NO session-level parent field in the JSONL. `parentUuid` is a MESSAGE-level back-pointer
threading turns within a transcript -- reading it as a session parent is the mistake this script
exists to avoid. But it yields the link anyway:

  * A session started fresh has `parentUuid: null` on its first record  -> **ROOT**.
  * A session started with `--resume`/`--fork-session` carries a first-record `parentUuid` that is
    a message uuid belonging to ANOTHER session's jsonl -> that file's stem is the **PARENT**.
  * The uuid resolves to no local jsonl (pruned by cleanupPeriodDays, or another trunk) ->
    **UNKNOWN**, with the uuid printed so the claim is checkable later.

`[measured 2026-09-04 22:0x: N--claude-cfl-clone holds 5 jsonls, 5 ROOT, 0 forks -- so the fork
branch has NO live example in this project dir and is exercised by fixtures only. Stated because a
branch that has never run on real data is a written warning, not a tested path (G23's lesson).]`

  session_parent.py <session-id> [--projects-dir DIR] [--self-test]
    prints one of:  ROOT | PARENT <sid> | UNKNOWN <reason>
"""
import io
import json
import os
import sys

PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")


def first_record(path):
    """The first record that carries a parentUuid key. Returns {} if unreadable."""
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if isinstance(r, dict) and "parentUuid" in r:
                    return r
    except OSError:
        return {}
    return {}


def owner_of_uuid(uuid, jsonls, skip=None):
    """Which jsonl contains a record with this uuid. Scans; returns a stem or None."""
    for p in jsonls:
        if skip and os.path.abspath(p) == os.path.abspath(skip):
            continue
        try:
            with io.open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    # cheap substring prefilter -- json.loads on every line of every transcript
                    # is minutes of work; the uuid is a literal in the raw bytes when present
                    if uuid not in line:
                        continue
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(r, dict) and r.get("uuid") == uuid:
                        return os.path.splitext(os.path.basename(p))[0]
        except OSError:
            continue
    return None


def derive(sess, projects_dir=None, search_all_trunks=True):
    """-> (verdict, detail). Never guesses: an unresolvable uuid is UNKNOWN, never ROOT."""
    root = projects_dir or PROJECTS
    if not os.path.isdir(root):
        return "UNKNOWN", "no projects dir at %s -- unreadable is never ROOT" % root
    # find this session's own jsonl anywhere under the projects root
    mine = None
    trunks = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".jsonl"):
                continue
            full = os.path.join(dirpath, fn)
            trunks.append(full)
            if fn.startswith(sess) or os.path.splitext(fn)[0] == sess:
                mine = mine or full
    if not mine:
        return "UNKNOWN", "no jsonl found for session %s (pruned, or another store)" % sess[:8]
    rec = first_record(mine)
    if not rec:
        return "UNKNOWN", "jsonl for %s has no parseable record carrying parentUuid" % sess[:8]
    pu = rec.get("parentUuid")
    if pu is None:
        return "ROOT", "first record parentUuid is null -- session started fresh"
    pool = trunks if search_all_trunks else [
        p for p in trunks if os.path.dirname(p) == os.path.dirname(mine)]
    own = owner_of_uuid(pu, pool, skip=mine)
    if own:
        return "PARENT", own
    return "UNKNOWN", ("first record points at message %s, which is in no local jsonl "
                       "(pruned or another machine)" % pu[:8])


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    pd = None
    if "--projects-dir" in sys.argv:
        pd = sys.argv[sys.argv.index("--projects-dir") + 1]
        argv = [a for a in argv if a != pd]
    if not argv:
        print("UNKNOWN no session id given")
        return 0
    v, d = derive(argv[0], pd)
    print("%s %s" % (v, d))
    return 0


def self_test():
    import tempfile
    print("=== SELF-TEST -- session_parent ===")
    np = nf = 0

    def ok(n, got, want):
        nonlocal np, nf
        if got == want:
            np += 1
            print("  PASS  %s" % n)
        else:
            nf += 1
            print("  FAIL  %s\n        want: %r\n        got : %r" % (n, want, got))

    d = tempfile.mkdtemp()
    tr = os.path.join(d, "trunk")
    os.makedirs(tr)

    def write(sid, rows):
        with io.open(os.path.join(tr, sid + ".jsonl"), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

    # a ROOT session: first record's parentUuid is null
    write("aaaaaaaa-1111", [{"uuid": "u1", "parentUuid": None, "type": "user"},
                            {"uuid": "u2", "parentUuid": "u1", "type": "assistant"}])
    ok("1 a fresh session is ROOT", derive("aaaaaaaa-1111", d)[0], "ROOT")

    # a FORK: its first record points at a message uuid living in the parent's jsonl
    write("bbbbbbbb-2222", [{"uuid": "v1", "parentUuid": "u2", "type": "user"}])
    v, det = derive("bbbbbbbb-2222", d)
    ok("2 THE DERIVATION: a fork names its parent session", (v, det), ("PARENT", "aaaaaaaa-1111"))

    # ⛔ the uuid resolves nowhere -> UNKNOWN. It must NEVER fall back to ROOT: "started fresh"
    # and "its parent was pruned" are opposite facts and only one of them is checkable later.
    write("cccccccc-3333", [{"uuid": "w1", "parentUuid": "GONE", "type": "user"}])
    ok("3 an unresolvable parent is UNKNOWN, never ROOT", derive("cccccccc-3333", d)[0], "UNKNOWN")
    ok("4 and the UNKNOWN prints the uuid so the claim stays checkable",
       "GONE"[:8] in derive("cccccccc-3333", d)[1], True)

    # NEGATIVE CONTROLS
    ok("5 a session with no jsonl is UNKNOWN", derive("dddddddd-4444", d)[0], "UNKNOWN")
    ok("6 a missing projects dir is UNKNOWN, not ROOT",
       derive("aaaaaaaa-1111", os.path.join(d, "nope"))[0], "UNKNOWN")
    with io.open(os.path.join(tr, "eeeeeeee-5555.jsonl"), "w", encoding="utf-8") as f:
        f.write("not json at all\n")
    ok("7 an unparseable jsonl is UNKNOWN", derive("eeeeeeee-5555", d)[0], "UNKNOWN")

    # ⭐ POSITIVE CONTROL FOR 2, and it is the one that matters: a session must not name ITSELF as
    # its parent just because its own file contains the uuid it points at.
    write("ffffffff-6666", [{"uuid": "z1", "parentUuid": "z9", "type": "user"},
                            {"uuid": "z9", "parentUuid": "z1", "type": "assistant"}])
    ok("8 control: a session never names itself as its own parent",
       derive("ffffffff-6666", d)[1] != "ffffffff-6666", True)

    # ⛔ ENTRY-POINT CASE, added 2026-09-05 after soul's mutation test proved ask_elder.py's
    # sibling gate GREEN on a program that could not run. This module uses the same dispatch --
    # `self_test() if "--self-test" in sys.argv else main()` -- so the test branch never crosses
    # main() and every case above could pass while `python session_parent.py <sid>` dies.
    # ⭐ A CHECK THAT TESTS A FUNCTION TESTS A FUNCTION. Only one that crosses the entry point
    # tests a PROGRAM.
    import subprocess
    _rc = subprocess.run([sys.executable, os.path.abspath(__file__), "aaaaaaaa-1111",
                          "--projects-dir", d],
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         timeout=120)
    ok("9 THE ENTRY POINT RUNS: `python session_parent.py <sid>` exits 0 and prints a verdict",
       (_rc.returncode, _rc.stdout.split(" ")[0] if _rc.stdout else ""), (0, "ROOT"))
    if _rc.returncode != 0:
        print("        child stderr tail: %s" % (_rc.stderr.strip().splitlines() or ["(none)"])[-1][:160])
    print("  %d passed, %d failed" % (np, nf))
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
