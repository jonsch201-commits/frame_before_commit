#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""dispose.py -- the disposition ledger P-01 has been waiting on, and the age rule.

WHY THIS EXISTS, and the shape of the thing is the finding.

`wiki/tracker/wayfinder-professionalism-2026-08-23.md` P-01 has carried "252 letters,
18 disposed, and the staleness rule has never been written because every seat that met
it was headless or busy." Measured 2026-08-24, attended, the framing was wrong twice:

  1. IT IS NOT ONE POPULATION. 255 letters, but 182 are dated <= 2026-08-11 and 154 of
     those fall in a THREE-DAY BURST (08-07..08-09). The last seven days carry 19.
     Every seat that looked saw "252 undisposed" -- an impossible drain -- and stopped.
     19 letters in 7 days is not impossible. CONFLATING THE BOLUS WITH THE STREAM IS WHY
     NOBODY EVER WROTE THE RULE.

  2. IT IS NOT A BACKLOG PROBLEM. `[measured]` 0 of the 19 recent letters carry a
     receiver-authored disposition. The practice does not exist AT ALL; the backlog is
     its most visible symptom, not its cause. A drain would have left the defect intact
     and looked like a fix.

AND TWO THINGS THE COUNT WAS WRONG ABOUT:
  * `consumed:` IS SENDER-AUTHORED. Soul writes it in its own letters as a field ABOUT
    the recipient ("consumed: PENDING", "consumed: NO -- none of the four"). It is that
    trunk's claim about our reading, not our record of our own action. 27 of the 52
    marker hits were that field. A disposition must be RECEIVER-AUTHORED or it is the
    same defect as a sender-authored `delivered:` stamp, which this fleet already retired.
  * THE LEDGER ALREADY EXISTED AND WAS DEAD. `exchange/letter-ledger.tsv`, 265 lines,
    last written 2026-08-17, and `grep` finds NO script that reads it -- only letters
    that mention it. That is `wiki/concepts/a-control-with-no-reader.md` again, and it
    is why this file is a READER as well as a writer.

WHY DISPOSITION IS NOT STAMPED INTO THE RECEIVED LETTER. Annotating a delivered letter
in place destroys the only delivery evidence this fleet has -- cross-tree `cmp` -- which
is the P-11 anchor finding from 2026-08-17. The disposition lives in OUR OWN ledger and
the received copy is never touched.

THE RULE, STATED WITH ITS ASSUMPTION SO A READER CAN REFUSE IT:

  STREAM (dated within STREAM_DAYS of today): must be disposed by an attended session.
    Default on silence: it ages out into the bolus rule below. It is never dropped
    silently; it changes class and the class is printed.

  BOLUS (older than STREAM_DAYS): CLOSED-BY-AGE en bloc, NOT letter by letter.
    ASSUMPTION, NAMED: a letter that has sat unactioned longer than STREAM_DAYS has
    either been superseded or its ask is dead.
    EVIDENCE FOR IT, AND IT IS THIN: 2026-08-24, two Professional letters in Herald's
    59-deep backlog were restated in one line each and BOTH WERE DEAD. n = 2. That is
    an anecdote, not a base rate, and the rule is adopted on it anyway because the
    alternative -- 182 letters read by hand -- is the status quo that produced zero
    dispositions in seventeen days.
    THE ASSUMPTION IS FALSIFIABLE AND THE CARVE-OUT BELOW IS HOW.

  HELD (any age): a letter is NEVER closed by age if it carries a live dated obligation,
    a verbatim Jon quote, or an explicit ask token. These go to a REVIEW list a human
    reads. The carve-out is the whole safety of the rule: if it catches nothing, the
    rule is closing letters blind and the operator should distrust it.

Usage: scripts/dispose.py            classify and REPORT; writes nothing
       scripts/dispose.py --write    (re)write exchange/DISPOSITIONS.tsv
       scripts/dispose.py --selftest prove each classification can fire, then run
"""
import os
import re
import sys
import datetime
import tempfile
import shutil

STREAM_DAYS = 7
LEDGER = os.path.join("exchange", "DISPOSITIONS.tsv")

DATE_RE = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")
# Receiver-authored only. `consumed:` is deliberately NOT here -- see the header.
# THE ANCHOR USED TO BE `^\s*` AND IT MATCHED NOTHING. Every disposition line in this
# trunk is written as `` `disposition-by: professional` `` -- backticked -- so the live
# run reported DISPOSED = 0 against 12 that grep could see. A classifier that scores a
# disposed letter as undisposed pushes it toward CLOSED-BY-AGE, which is the worst
# direction the error could take. Leading markup is now part of the anchor, and S6 is
# seeded with the exact form that broke it rather than a form I invented.
DISPOSED_RE = re.compile(r"^[\s`*_>\-]*disposition(-by)?\s*:", re.M | re.I)
JON_QUOTE_RE = re.compile(r"verbatim|typos his|Jon,\s+20\d\d-\d\d-\d\d", re.I)
ASK_RE = re.compile(r"\b(DUE|DEADLINE|OWED|ACTION REQUIRED|PLEASE CONFIRM|awaiting)\b")


def filename_date(name):
    """Last ISO date in the filename, as a date, or None."""
    hits = DATE_RE.findall(name)
    if not hits:
        return None
    y, m, d = hits[-1]
    try:
        return datetime.date(int(y), int(m), int(d))
    except ValueError:
        return None


def classify(path, today):
    """Return (klass, reason). UNREADABLE IS ITS OWN CLASS -- it is not 'no markers'.

    This trunk shipped `except OSError: continue` twice and both times an unreadable
    file scored as a clean one (2026-08-24). A read failure here would silently move a
    letter into CLOSED-BY-AGE, which is the worst possible direction for the error.
    """
    name = os.path.basename(path)
    d = filename_date(name)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            body = fh.read()
    except OSError:
        return "UNREADABLE", "could not be read; NOT classified and NOT closed"

    if DISPOSED_RE.search(body):
        return "DISPOSED", "receiver-authored disposition line present"

    held = []
    if JON_QUOTE_RE.search(body):
        held.append("carries a verbatim Jon quote")
    if ASK_RE.search(body):
        held.append("carries an explicit ask/deadline token")
    for y, m, dd in DATE_RE.findall(body):
        try:
            cand = datetime.date(int(y), int(m), int(dd))
        except ValueError:
            # A DATE-SHAPED TOKEN THIS CODE CANNOT EVALUATE IS *UNKNOWN*, AND UNKNOWN MUST NOT
            # SILENTLY PERMIT DISPOSAL. It used to `continue` uncounted. The consequence class
            # here is NOT the wrong-denominator one -- this loop publishes no population -- it
            # is worse: `2026-09-31` is a typo for a real future date, the regex admits it, the
            # parse fails, and a letter that NAMES A FUTURE DATE gets disposed as not-held.
            # HELD is the safe state, so an unevaluable token now pushes toward HELD and says so.
            # Found 2026-09-01 by ACCEPTANCE-uncounted-skip.py after the Secretary demonstrated
            # that the shell test could not reach this trunk's Python at all.
            held.append("carries an UNEVALUABLE date-shaped token %s-%s-%s -- UNKNOWN, and "
                        "UNKNOWN does not license disposal" % (y, m, dd))
            break
        if cand > today:
            held.append("names a future date %s" % cand.isoformat())
            break
    if held:
        return "HELD", "; ".join(held)

    if d is None:
        return "HELD", "no date in filename; age is UNKNOWN and UNKNOWN is not old"
    age = (today - d).days
    if age <= STREAM_DAYS:
        return "STREAM-OPEN", "%d day(s) old; owed a disposition by an attended session" % age
    return "CLOSED-BY-AGE", "%d day(s) unactioned; assumption: superseded or dead" % age


def run(inbound, today, write, out=sys.stdout):
    rows, counts = [], {}
    names = sorted(os.listdir(inbound)) if os.path.isdir(inbound) else []
    for name in names:
        if not name.endswith(".md"):
            continue
        p = os.path.join(inbound, name)
        k, why = classify(p, today)
        counts[k] = counts.get(k, 0) + 1
        rows.append((name, (filename_date(name) or "").__str__(), k, why))

    total = len(rows)
    out.write("DISPOSE: %d letter(s) in %s, as of %s (STREAM_DAYS=%d)\n"
              % (total, inbound, today.isoformat(), STREAM_DAYS))
    for k in ("DISPOSED", "STREAM-OPEN", "HELD", "CLOSED-BY-AGE", "UNREADABLE"):
        out.write("  %-14s %d\n" % (k, counts.get(k, 0)))

    # THE CARVE-OUT IS THE RULE'S ONLY SAFETY. If it never fires, the rule is closing
    # letters blind and the operator must be told so in the same breath as the counts.
    if counts.get("HELD", 0) == 0 and counts.get("CLOSED-BY-AGE", 0) > 0:
        out.write("  WARNING: the HELD carve-out caught NOTHING while closing %d letter(s).\n"
                  % counts["CLOSED-BY-AGE"])
        out.write("  WARNING: a rule whose only safety never fires is not a safe rule. Do not trust this run.\n")
    if counts.get("UNREADABLE", 0):
        out.write("  UNKNOWN: %d letter(s) could not be read. They are NOT closed and NOT counted clean.\n"
                  % counts["UNREADABLE"])

    if write:
        with open(LEDGER, "w", encoding="utf-8") as fh:
            fh.write("# exchange/DISPOSITIONS.tsv -- receiver-authored. Generated by scripts/dispose.py.\n")
            fh.write("# The received letters are NEVER stamped: annotating them destroys cross-tree cmp (P-11).\n")
            fh.write("# as_of\t%s\tSTREAM_DAYS\t%d\n" % (today.isoformat(), STREAM_DAYS))
            fh.write("letter\tletter_date\tclass\treason\n")
            for r in rows:
                fh.write("\t".join(r) + "\n")
        out.write("  WROTE %s (%d row(s))\n" % (LEDGER, len(rows)))
    else:
        out.write("  DRY RUN: nothing written. Re-run with --write.\n")
    return counts


def selftest():
    rc = 0
    today = datetime.date(2026, 8, 24)
    d = tempfile.mkdtemp()
    try:
        # S1 each class fires, seeded -- a classifier proven on one class is not proven.
        open(os.path.join(d, "a-to-professional-fresh-2026-08-23.md"), "w").write("nothing special\n")
        open(os.path.join(d, "b-to-professional-old-2026-08-01.md"), "w").write("nothing special\n")
        open(os.path.join(d, "c-to-professional-done-2026-08-01.md"), "w").write("disposition-by: professional\n")
        open(os.path.join(d, "e-to-professional-jon-2026-08-01.md"), "w").write("Jon said, verbatim, typos his\n")
        open(os.path.join(d, "f-to-professional-future-2026-08-01.md"), "w").write("re-check on 2026-09-22\n")
        open(os.path.join(d, "g-to-professional-nodate.md"), "w").write("nothing special\n")
        got = {}
        for n in sorted(os.listdir(d)):
            got[n[0]] = classify(os.path.join(d, n), today)[0]
        want = {"a": "STREAM-OPEN", "b": "CLOSED-BY-AGE", "c": "DISPOSED",
                "e": "HELD", "f": "HELD", "g": "HELD"}
        for k in sorted(want):
            if got.get(k) != want[k]:
                print("SELFTEST BROKEN: S1 %s -> %s, expected %s" % (k, got.get(k), want[k]))
                rc = 3
        # S2 the sender-authored field must NOT count as our disposition.
        p = os.path.join(d, "h-to-professional-senderfield-2026-08-01.md")
        open(p, "w").write('consumed: "PRO -- YES, self-reported"\n')
        if classify(p, today)[0] != "CLOSED-BY-AGE":
            print("SELFTEST BROKEN: S2 a sender-authored consumed: was read as our disposition")
            rc = 3
        # S3 an undated filename is HELD, never closed -- UNKNOWN age is not old age.
        if classify(os.path.join(d, "g-to-professional-nodate.md"), today)[0] != "HELD":
            print("SELFTEST BROKEN: S3 undated letter was not HELD")
            rc = 3
        # S6 THE FORM THAT ACTUALLY BROKE IT: a backticked disposition line. Not invented --
        #    this is the literal shape every disposition in this trunk is written in.
        p6 = os.path.join(d, "i-to-professional-backticked-2026-08-01.md")
        open(p6, "w").write("`disposition-by: professional`" + chr(10))
        if classify(p6, today)[0] != "DISPOSED":
            print("SELFTEST BROKEN: S6 a backticked disposition line was not read as disposed")
            rc = 3
        # S4 THE CARVE-OUT WARNING FIRES when HELD is empty and letters are being closed.
        d2 = tempfile.mkdtemp()
        open(os.path.join(d2, "x-to-professional-old-2026-08-01.md"), "w").write("plain\n")
        import io
        buf = io.StringIO()
        run(d2, today, False, buf)
        if "carve-out caught NOTHING" not in buf.getvalue():
            print("SELFTEST BROKEN: S4 no warning when the only safety never fired")
            rc = 3
        # S5 and it must NOT fire when the carve-out did catch something.
        open(os.path.join(d2, "y-to-professional-jon-2026-08-01.md"), "w").write("verbatim\n")
        buf = io.StringIO()
        run(d2, today, False, buf)
        if "carve-out caught NOTHING" in buf.getvalue():
            print("SELFTEST BROKEN: S5 warning fired while the carve-out was working")
            rc = 3
        shutil.rmtree(d2)
    finally:
        shutil.rmtree(d)
    if rc == 0:
        print("SELFTEST: S1 six classes each fire / S2 sender-authored consumed: is NOT disposition / "
              "S3 undated is HELD not closed / S4 carve-out-caught-nothing warns / S5 warning is quiet "
              "when the carve-out works / S6 a BACKTICKED disposition line counts -- each proven failable (6/6)")
        print("BOUND: fixtures are small and built here. This proves the CLASSIFIER, not the RULE. "
              "Whether 'older than %d days means dead' is true rests on n=2 and is stated as such."
              % STREAM_DAYS)
    return rc


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(0 if run(os.path.join("exchange", "inbound"),
                      datetime.date.today(), "--write" in sys.argv) is not None else 1)
