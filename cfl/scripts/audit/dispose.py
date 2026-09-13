#!/usr/bin/env python3
"""Stamp a disposition onto a peer letter — the cheapest possible act of receiving.

WHY THIS EXISTS
---------------
`scripts/audit/disposition_rate.py` measured 5.6% overall and 3.1% on agent returns. CFL published
that number while its own read-receipt ledger had been stopped since **2026-08-06** — seventeen
days. **Publishing a finding about not-acting, and not acting on it, is the finding.**

Jon, 2026-08-23, verbatim, typos his:

    "Many coordinators have both failed to read their email, and failed to mark it as read, and
     faile dto mark it as actioned and put any replies needed in it"

⭐ **FOUR distinct failures, and he separated them on purpose:** read · mark-read · mark-actioned ·
put replies in the letter. This tool addresses the middle two, which are the ones that cost
seconds and were skipped anyway.

⛔ **WHY IT WAS SKIPPED, and the reason matters more than the tool:** stamping felt like
bookkeeping while READING felt like the work. But **acting without stamping is indistinguishable
from never reading** — measured today: eighteen Herald letters read as UNREAD that had in fact
been fully absorbed into `CARRIER.md` and `WAKE-ACTIONS.md`. The record showed a trunk that
ignored its mail. The trunk had not ignored its mail. **Both directions of that error are
expensive, and only one of them feels like a mistake at the time.**

DESIGN
------
- ⛔ **APPEND-ONLY. Never rewrites a letter's body**, never edits a prior stamp. Peers hold copies;
  a rewrite makes the copies diverge with nothing able to notice.
- ⛔ **REQUIRES A POINTER.** A disposition with no artifact is a rubber stamp, and
  `disposition_rate.py` explicitly cannot tell those apart — it says so in its own output. **This
  tool refuses to create the thing that would fool it.**
- **Verdicts** are Jon's own distinction, not invented here:
    `read`      — I have read it. Nothing was owed.
    `actioned`  — I did something. **--by is MANDATORY.**
    `declined`  — I am not doing it. **--by must carry the REASON.**
  ⭐ A recorded decline is a legitimate disposition. **The UNRECORDED skip is the defect.**

Usage:
    python scripts/audit/dispose.py FILE --verdict actioned --by "commit abc123 — what changed"
    python scripts/audit/dispose.py FILE --verdict read
    python scripts/audit/dispose.py --selftest
"""
import argparse
import datetime
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

VERDICTS = ("read", "actioned", "declined")
MARK = "<!-- cfl-disposition"


def stamp(path, verdict, by, seat, as_of):
    if verdict not in VERDICTS:
        raise ValueError(f"verdict must be one of {VERDICTS}")
    if verdict in ("actioned", "declined") and not by:
        # ⛔ Not a convenience check. A disposition with no pointer is exactly the rubber stamp
        # disposition_rate.py warns it cannot detect -- so it must not be creatable here.
        raise ValueError(f"--by is REQUIRED for '{verdict}': name the artifact or the reason. "
                         "A disposition with no pointer is a rubber stamp, and the rate tool "
                         "cannot tell it from a real one.")
    text = io.open(path, encoding="utf-8", errors="ignore").read()
    line = (f"\n{MARK} at=\"{as_of}\" seat=\"{seat}\" verdict=\"{verdict}\""
            + (f" by=\"{by}\"" if by else "") + " -->\n")
    if line.strip() in text:
        return False  # already stamped identically; appending again would be noise
    with io.open(path, "a", encoding="utf-8") as fh:
        fh.write(line)
    return True


def selftest():
    import tempfile
    ok = True
    now = "2026-08-23T15:00:00-05:00"
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "letter.md")
        io.open(p, "w", encoding="utf-8").write("# a letter\nbody\n")

        print("--- case 1: 'read' needs no pointer (expect stamped) ---")
        got = stamp(p, "read", None, "test", now)
        print(f"    stamped={got}  {'PASS' if got else 'FAIL'}")
        ok &= got

        print("--- case 2: 'actioned' WITHOUT a pointer must be REFUSED ---")
        try:
            stamp(p, "actioned", None, "test", now)
            print("    no error raised  FAIL")
            ok = False
        except ValueError:
            print("    refused  PASS")

        print("--- case 3: 'actioned' WITH a pointer is stamped ---")
        got = stamp(p, "actioned", "commit deadbee — did the thing", "test", now)
        print(f"    stamped={got}  {'PASS' if got else 'FAIL'}")
        ok &= got

        print("--- case 4: the letter BODY is untouched (append-only) ---")
        body = io.open(p, encoding="utf-8").read()
        kept = body.startswith("# a letter\nbody\n")
        print(f"    body intact={kept}  {'PASS' if kept else 'FAIL'}")
        ok &= kept

        print("--- case 5: an identical re-stamp does NOT duplicate ---")
        again = stamp(p, "read", None, "test", now)
        print(f"    stamped={again} (expect False)  {'PASS' if not again else 'FAIL'}")
        ok &= (not again)

    print("\n" + ("SELFTEST PASS" if ok else "SELFTEST FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--verdict", choices=VERDICTS)
    ap.add_argument("--by", default=None,
                    help="the artifact that consumed it, or the reason for declining. "
                         "MANDATORY for actioned/declined.")
    ap.add_argument("--seat", default="cfl/9f1e3383")
    ap.add_argument("--as-of", default=None,
                    help="ISO stamp; defaults to now (this tool is a receipt, so now is correct)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.files or not a.verdict:
        ap.error("need FILE(s) and --verdict")

    as_of = a.as_of or datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    n = 0
    for f in a.files:
        if not os.path.isfile(f):
            print(f"  MISSING {f}")
            continue
        if stamp(f, a.verdict, a.by, a.seat, as_of):
            print(f"  {a.verdict:<9} {os.path.basename(f)}")
            n += 1
        else:
            print(f"  {'(dup)':<9} {os.path.basename(f)}")
    print(f"\n{n} stamped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
