#!/usr/bin/env python3
"""ask_elder.py — a descendant's address book: who can I ask, and the exact command to ask them.

WHY, Jon 2026-09-04: *"ensure your descendents know how to talk to you for advice in this context
you all missed things"* — and the missing thing was never the willingness to ask. It was that a
post-compact seat does not know WHO its ancestors are, WHERE the live peers are, or WHAT COMMAND
asks one. ⛔ **A capability nobody can address is the same as an absent capability.**

⭐ THE LESSON THIS ENCODES, and it is CFL's own most expensive one: on 2026-08-06 CFL had a resume
rule written INSIDE a file that nothing told anyone to open. *"The instruction and the thing it
governs must be reachable from the same starting point, or the instruction is decoration."* An
ADVICE CHANNEL described in prose is that defect again. **This is the imperative form: run it and
it prints the addresses.**

WHAT AN ELDER IS, and the distinction is load-bearing (Secretary's method, 2026-09-02, adopted):

  * An ELDER is a DIFFERENT session — another seat that lived through its own context.
  * ⛔ **YOUR OWN EARLIER COMPACT WINDOWS ARE NOT ANCESTORS.** Secretary's first attempt proposed
    exactly that and their own index corrected them at rank 1. Same seat, several summaries back,
    is *you*, and asking it is asking yourself with worse recall.
  * ⛔ **ELDERS ARE WITNESSES, NEVER AUTHORITIES.** Every claim an elder returns is graded against
    the record BY COMMAND before it is believed. Their prose is their motive, not evidence: thinking
    is not on disk, and an elder that was itself compacted is answering from a summary.
  * ⚠️ Consults are READ-ONLY: `--permission-mode plan`. An elder that can write is not a witness.

WHAT IT PRINTS
  1. THIS session's derived lineage (session_parent.py): ROOT | PARENT <sid> | UNKNOWN <reason>.
  2. Sibling sessions in this trunk's project dir, newest first, with their last-write time — the
     candidate elders, each with a runnable fork-consult command.
  3. The live peer trunks and how to reach them right now (SendMessage), which is the channel a
     STOPPED elder cannot serve.
  4. The four standing consult rules, so a descendant that reads only this output still grades.

  ask_elder.py [--session <sid>] [--limit N] [--wake-line] [--self-test]
"""
import glob
import io
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from session_parent import derive  # noqa: E402

PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")
# the checkout containing this file -- derived, never recorded (the class that produced five
# defects in 24h: a G: write default, a lineage constant, a session id, a project glob, a count)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRUNK = "N--claude-cfl-clone"

# ⛔ stdout on this machine is cp1252 and this file's own text contains ⛔/⭐/⚠️. The FIRST live run
# died with UnicodeEncodeError while the selftest was 9/9 GREEN -- because every case asserted
# against report()'s RETURN VALUE and not one of them ever PRINTED it. Same lesson as G24's L1
# reporting path, one level over: THE TEST EXERCISED THE FUNCTION AND NOT THE ENTRY POINT.
# Case 10 below now runs main() through a real encode. (Family: wc -c never len().)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RULES = [
    "An elder is a DIFFERENT session. Your own earlier compact windows are NOT ancestors -- that is "
    "you, with worse recall.",
    "ELDER IS WITNESS, NEVER AUTHORITY. Grade every returned claim against the record BY COMMAND "
    "before believing it.",
    "Consult READ-ONLY (--permission-mode plan). An elder that can write is not a witness.",
    "A live peer trunk answers what a stopped elder cannot: use ListAgents + SendMessage for "
    "anything about NOW. An elder knows only what it lived through.",
]


def sessions(projects_dir=None, trunk=None):
    root = projects_dir or PROJECTS
    d = os.path.join(root, trunk or TRUNK)
    out = []
    for p in glob.glob(os.path.join(d, "*.jsonl")):
        try:
            out.append((os.path.splitext(os.path.basename(p))[0], os.path.getmtime(p), p))
        except OSError:
            continue
    return sorted(out, key=lambda t: t[1], reverse=True)


def declared_note(sid, repo=None):
    """A session's OWN one-line account of itself, if it left one. Declared beats derived.

    ⛔ WHY, Jon 2026-09-05: "you should be listened to by your successor json." MEASURED the same
    hour: a successor running this script sees THIS session -- eighteen hours of findings -- described
    by its FIRST HUMAN TURN, which was a cron prompt: "Gate floor (re-created 2026-09-03 23:5x after
    quiet mode). Run python scripts/audit/usage_meter.py...". ⭐ IT WOULD READ AS ANOTHER PROBE,
    indistinguishable from the four liveness stubs beside it.

    ⚠️ This is Personal's R5 one layer over, and they measured it first: identity is DECLARED, not
    derived -- 18 sessions, declared 2, derived 0, all four derivation rules firing zero times, and
    the --declare mechanism never once invoked. A first-turn heuristic is a derivation, and it fails
    for the same reason: THE OPENING OF A SESSION DOES NOT DESCRIBE THE SESSION.

    So: a seat may write exchange/elders/NOTE-<sid8>.md whose first non-frontmatter line says what it
    was. That line wins over the derived one. Absent, we fall back to first_human() and SAY it is
    derived, because a derived label presented as a declared one is the defect this fixes.
    """
    root = repo or REPO
    p = os.path.join(root, "exchange", "elders", "NOTE-%s.md" % (sid or "")[:8])
    try:
        with io.open(p, encoding="utf-8", errors="replace") as f:
            body = [l.strip() for l in f if l.strip() and not l.startswith(("---", "#"))]
        return body[0][:140] if body else None
    except OSError:
        return None


def first_human(path, limit=4000):
    """One line of what that session was actually about -- an id alone is not an address."""
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i > limit:
                    break
                if '"type": "user"' not in line and '"type":"user"' not in line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                m = r.get("message") or {}
                c = m.get("content")
                if isinstance(c, list):
                    c = " ".join(b.get("text", "") for b in c if isinstance(b, dict))
                if isinstance(c, str) and c.strip() and not c.lstrip().startswith("<"):
                    return " ".join(c.split())[:90]
    except OSError:
        pass
    return "(no readable opening turn -- UNKNOWN, not empty)"


def report(sess=None, limit=6, projects_dir=None, trunk=None):
    lines = []
    now = datetime.now()
    lines.append("=== ASK AN ELDER === who you can ask, and the command that asks them")
    lines.append("clock: %s" % now.strftime("%Y-%m-%d %H:%M:%S"))
    ss = sessions(projects_dir, trunk)
    if not ss:
        lines.append("")
        lines.append("  UNKNOWN -- no session jsonls found under %s. An unreadable store is NOT "
                     "'no elders'; say UNKNOWN and go ask a live peer instead."
                     % os.path.join(projects_dir or PROJECTS, trunk or TRUNK))
        return "\n".join(lines + [""] + ["  RULE: " + r for r in RULES])
    # 2026-09-06 (Professional, cold run as test-master): self must come from the harness, never from
    # newest-by-mtime -- with several fresh JSONs open, mtime names a sibling. Claude Code exports
    # CLAUDE_CODE_SESSION_ID (CLAUDE_SESSION_ID is EMPTY in 2.1.261). Basis is printed so a reader can see which.
    basis_self = "argument"
    if not sess:
        sess, basis_self = os.environ.get("CLAUDE_CODE_SESSION_ID") or "", "env CLAUDE_CODE_SESSION_ID"
    if not sess:
        sess, basis_self = ss[0][0], "newest-by-mtime (WEAK: may be a sibling; env var absent)"
    v, d = derive(sess, projects_dir)
    lines.append("")
    lines.append("YOUR LINEAGE (derived, never hardcoded)")
    lines.append("  this session : %s" % sess)
    lines.append("  parent       : %s %s" % (v, d))
    if v == "ROOT":
        lines.append("  -> You have no parent session. That is a FACT, not a gap: ask a SIBLING "
                     "below or a live peer.")
    lines.append("")
    lines.append("CANDIDATE ELDERS -- other sessions in this trunk, newest first")
    n = 0
    for sid, mt, p in ss:
        if sid == sess:
            continue
        n += 1
        if n > limit:
            break
        age_h = (now.timestamp() - mt) / 3600.0
        lines.append("  %s  last wrote %s (%.1f h ago)" % (sid[:13], datetime.fromtimestamp(mt).strftime("%m-%d %H:%M"), age_h))
        note = declared_note(sid)
        about = note if note else first_human(p)
        src = "DECLARED by that seat" if note else "derived from its first turn"
        # ⚠️ A HEALTH-CHECK PROBE IS NOT AN ELDER. Measured 2026-09-04: 3 of this trunk's 4 sibling
        # jsonls open with "reply with the single word ok" -- they are liveness probes with no
        # lived context. Consulting one costs a fork and returns nothing, and the ID LOOKS EXACTLY
        # LIKE A REAL SEAT'S. Flag it; do not hide the row (a filtered-out session is a session
        # nobody can find again).
        probe = "reply with" in about.lower() and " ok" in about.lower()
        lines.append("      about: %s%s" % (about, "   <- PROBE, not a seat: no lived context" if probe else ""))
        lines.append("      basis: %s" % src)
        lines.append('      ASK:   claude --resume %s --fork-session --permission-mode plan -p "<your question>"' % sid)
    if n == 0:
        lines.append("  none -- this trunk has exactly one session on disk. Ask a live peer.")
    lines.append("")
    lines.append("LIVE PEERS -- what a stopped elder cannot tell you (anything about NOW)")
    lines.append("  ListAgents  then  SendMessage {to: \"<name>\", message: \"...\"}")
    lines.append("  Peers seen 2026-09-04: secretary, herald, professionalism, soul, "
                 "claude-personal-c5. ⚠️ That list is a SNAPSHOT -- run ListAgents, do not trust it.")
    lines.append("")
    for r in RULES:
        lines.append("  RULE: " + r)
    return "\n".join(lines)


def self_test():
    import tempfile
    print("=== SELF-TEST -- ask_elder ===")
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
    t = os.path.join(d, "TRUNK")
    os.makedirs(t)

    def write(sid, rows):
        with io.open(os.path.join(t, sid + ".jsonl"), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

    write("aaaaaaaa-1111", [{"uuid": "u1", "parentUuid": None, "type": "user",
                             "message": {"content": "the wiki coverage question"}},
                            {"uuid": "u2", "parentUuid": "u1", "type": "assistant"}])
    write("bbbbbbbb-2222", [{"uuid": "v1", "parentUuid": "u2", "type": "user",
                             "message": {"content": "second seat, forked"}}])
    r = report("bbbbbbbb-2222", projects_dir=d, trunk="TRUNK")
    ok("1 names the derived parent, not a constant", "PARENT aaaaaaaa-1111" in r, True)
    ok("2 gives a RUNNABLE consult command for a sibling",
       "--resume aaaaaaaa-1111 --fork-session --permission-mode plan" in r, True)
    ok("3 the consult is read-only", "--permission-mode plan" in r, True)
    ok("4 says what the elder was ABOUT (an id alone is not an address)",
       "the wiki coverage question" in r, True)
    ok("5 carries the witness-never-authority rule", "WITNESS, NEVER AUTHORITY" in r.upper(), True)
    ok("6 carries the your-own-windows-are-not-ancestors rule",
       "NOT ancestors" in r, True)

    # ⛔ NEGATIVE CONTROL: an empty/unreadable store must say UNKNOWN, never "no elders".
    # An absent store and a store with nobody in it are different facts, and only one is a gap.
    e = tempfile.mkdtemp()
    r2 = report("x", projects_dir=e, trunk="NOPE")
    ok("7 CONTROL: an unreadable store is UNKNOWN, not 'no elders'", "UNKNOWN" in r2, True)
    ok("8 and it still prints the rules, so a descendant reading only this output grades",
       "WITNESS, NEVER AUTHORITY" in r2.upper(), True)

    # a ROOT session must say so plainly rather than printing an empty parent
    r3 = report("aaaaaaaa-1111", projects_dir=d, trunk="TRUNK")
    ok("9 a ROOT session is told it has no parent, and what to do instead",
       "ROOT" in r3 and "ask a SIBLING" in r3, True)
    # ⛔ CASE 10 EXISTS BECAUSE CASES 1-9 WERE ALL GREEN WHILE THE SCRIPT COULD NOT RUN.
    # They asserted on report()'s return value; none ever encoded it to a byte stream. The first
    # live invocation died with UnicodeEncodeError on cp1252 stdout. A test that never crosses the
    # entry point tests a function, not a program.
    enc = "ok"
    try:
        report("bbbbbbbb-2222", projects_dir=d, trunk="TRUNK").encode("cp1252")
        enc = "encoded-clean-in-cp1252"
    except UnicodeEncodeError:
        enc = "would-crash-on-cp1252-stdout-WITHOUT-the-reconfigure"
    ok("10 the report contains chars a cp1252 stdout cannot take (so the guard is load-bearing)",
       enc, "would-crash-on-cp1252-stdout-WITHOUT-the-reconfigure")

    # ⛔ CASE 11 EXISTS BECAUSE soul PROVED CASES 1-10 GREEN ON A PROGRAM THAT CANNOT RUN.
    # They injected ONE line -- a raise on the first statement of main() -- into a full copy of the
    # tree and got: `python ask_elder.py` -> RuntimeError, `python ask_elder.py --self-test` -> all passed,
    # GATE GREEN. The dispatch `sys.exit(self_test() if "--self-test" in sys.argv else main())`
    # means the test branch NEVER CROSSES main(): the gate's command and the program's real entry
    # point are DISJOINT CODE PATHS.
    # ⚠ This file already CARRIED that warning and still had the hole. Case 10 asserts a property
    # of the OUTPUT (that it survives a cp1252 stdout), not of the ENTRY POINT. Naming a failure
    # mode does not immunise the code underneath it -- the third time that sentence applies tonight.
    # ⭐ A CHECK THAT TESTS A FUNCTION TESTS A FUNCTION. Only a check that crosses the entry point
    # tests a PROGRAM. This case invokes the script the way a human does and asserts a zero exit.
    import subprocess
    _rc = subprocess.run([sys.executable, os.path.abspath(__file__), "--limit", "1"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         timeout=120)
    ok("11 THE ENTRY POINT RUNS: `python ask_elder.py` exits 0 (soul's mutation test, 2026-09-05)",
       (_rc.returncode, "ASK AN ELDER" in _rc.stdout),
       (0, True))
    if _rc.returncode != 0:
        print("        child stderr tail: %s" % (_rc.stderr.strip().splitlines() or ["(none)"])[-1][:160])
    # 12-13: --wake-line, the form /wake actually consumes. A function that works and an ENTRY
    # POINT that does not is the G29 defect (soul's mutation test): test the flag, not the def.
    _wl = subprocess.run([sys.executable, os.path.abspath(__file__), "--wake-line"],
                         capture_output=True, text=True, timeout=60)
    ok("12 --wake-line EXITS 0 AND PRINTS AN IDENTITY LINE",
       (_wl.returncode, "IDENTITY:" in _wl.stdout), (0, True))
    # A wake line that silently omits the ancestor is the exact failure it exists to prevent.
    ok("13 --wake-line NAMES AN ANCESTOR (or says none, explicitly)",
       "ANCESTOR:" in _wl.stdout, True)
    print("  %d passed, %d failed" % (np, nf))
    return 0 if nf == 0 else 1


NEWLINE = chr(10)


def is_seat(path, limit=4000):
    """A JSONL is a SEAT (consultable ancestor) only if it is neither a CONTINUATION nor a LANE.

    Added 2026-09-06 09:1x after Professional measured this tool naming a9842e87 -- a file whose first
    turn is the machine summary "This session is being continued from a previous conversation..." --
    as this seat's ANCESTOR. Same class as their control-fork finding one tool over (c84c905): ranking by
    recency without a provenance test. Rules: (a) first readable human turn starting with the
    continuation banner -> CONTINUATION, skip; (b) records carry `origin` fields but no turn has
    `origin.kind == human` -> LANE (a -p run, a fork, a cron prompt), skip; files with no origin field
    at all stay eligible (older harness)."""
    saw_origin, saw_human = False, False
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i > limit:
                    break
                if '"origin"' in line:
                    saw_origin = True
                    if '"kind": "human"' in line or '"kind":"human"' in line:
                        saw_human = True
    except OSError:
        return False
    if saw_origin and not saw_human:
        return False
    return not first_human(path).startswith("This session is being continued")


def wake_line(sess=None, projects_dir=None, trunk=None):
    """One line for /wake, printed BEFORE the record.

    Professional, 2026-09-05: a standard that reaches a seat's INBOX and not its WAKE is a
    standard nobody has. CPC-5 landed in CFL's inbound 2026-09-04 22:43 and 0 of 12 of its body
    lines ever entered this seat's context; the substance arrived only when a peer PUSHED it
    16 hours later. The fix is not a habit. It is this line, in the command.
    """
    ss = sessions(projects_dir, trunk)
    if not ss:
        return "IDENTITY: UNKNOWN (no session store readable) -- UNKNOWN dominates; ask a live peer."
    # 2026-09-06 (Professional, cold run as test-master): self must come from the harness, never from
    # newest-by-mtime -- with several fresh JSONs open, mtime names a sibling. Claude Code exports
    # CLAUDE_CODE_SESSION_ID (CLAUDE_SESSION_ID is EMPTY in 2.1.261). The basis is printed so a reader sees which.
    basis_self = "argument"
    if not sess:
        sess, basis_self = os.environ.get("CLAUDE_CODE_SESSION_ID") or "", "env CLAUDE_CODE_SESSION_ID"
    if not sess:
        sess, basis_self = ss[0][0], "newest-by-mtime (WEAK: may be a sibling; env var absent)"
    v, d = derive(sess, projects_dir)
    out = ["IDENTITY: trunk=%s  session=%s [%s]  parent=%s %s" % (trunk or TRUNK, sess[:8], basis_self, v, d)]
    prev = [x for x in ss if x[0] != sess and is_seat(x[2])]  # 2026-09-06: continuations and lanes are not ancestors
    # 2026-09-06 15:2x: a headless -p probe JSON (the fresh-json PROTOTYPE) became the newest seat in this trunk and was
    # named as ANCESTOR. Declared beats derived applies to SELECTION too: any seat that wrote exchange/elders/NOTE-<sid8>.md
    # outranks every undeclared one, however new; among declared, newest first.
    prev.sort(key=lambda x: (0 if declared_note(x[0]) else 1, -x[1]))
    if not prev:
        out.append("ANCESTOR: none in this trunk. That is a FACT, not a gap -- ask a live peer.")
        return NEWLINE.join(out)
    sid, mt, p2 = prev[0]
    note = declared_note(sid)
    basis = "DECLARED" if note else "derived-from-first-turn (WEAK: a cron prompt reads as a probe)"
    about = (note if note else first_human(p2)) or "(no account)"
    out.append("ANCESTOR: %s  %s  [%s]" % (sid[:8], about[:100], basis))
    out.append('  ASK: claude --resume %s --fork-session --permission-mode plan -p "<question>"' % sid)
    return NEWLINE.join(out)


def main():
    sess = None
    if "--session" in sys.argv:
        sess = sys.argv[sys.argv.index("--session") + 1]
    limit = 6
    if "--limit" in sys.argv:
        try:
            limit = int(sys.argv[sys.argv.index("--limit") + 1])
        except Exception:
            pass
    if "--wake-line" in sys.argv:
        print(wake_line(sess))
        return 0
    print(report(sess, limit))
    return 0


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
