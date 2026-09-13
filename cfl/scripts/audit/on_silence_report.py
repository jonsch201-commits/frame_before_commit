#!/usr/bin/env python3
"""on_silence_report.py — the reader for the promise fields (PROP-003, gated 2026-09-01).

Herald F-7, 2026-09-01: `on_silence:` and `expires:` were carried by scores of fleet
letters and READ BY NOTHING — 14 letters past their own declared deadline with a default
declared and nothing fired. "We built a lint for the presence of a promise and never
built the thing that keeps it."

This is CFL's reader. It REPORTS; it fires nothing (executing a default is a judgment
act — this is the alarm, not the actuator; Herald's bound, kept). Scans exchange/ (and
exchange/inbound/) frontmatter for `expires:` and `on_silence:`.

Classes reported, never folded into each other (Herald's discipline, kept):
  PAST-DUE   expires parsed, before now, on_silence declared
  LIVE       expires parsed, in the future
  UNCLOCKED  on_silence declared, no expires at all (a default that can never come due)
  UNPARSEABLE expires present but not a parseable date — reported, never guessed

A bare date expires END OF DAY, not midnight (Herald's convention, kept).

CANNOT-DETECT (stated): whether a past-due letter was answered in substance with its row
never struck — that is a receipt defect and disposing of the list is the coordinator's
judgment (exchange-letters rules 5-7 hold the grading vocabulary).

Usage:
  on_silence_report.py [root]          # scan root/exchange + root/exchange/inbound
  on_silence_report.py --selftest      # fixtures, BOTH directions, incl. the negative
                                       # control Herald names mandatory: a future-dated
                                       # letter must NOT register past-due
Exit: 0 clean or report-only; 1 selftest failure. (Reporting past-due letters is exit 0 —
the report is the deliverable; a nonzero would train callers to suppress it.)
"""
import re
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

FM_KEY = re.compile(r"^(expires|on_silence):\s*(.*)$", re.I)
DATE = re.compile(r"(20\d\d)-(\d\d)-(\d\d)(?:[ T](\d\d):(\d\d))?")


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        m = FM_KEY.match(line.strip())
        if m:
            out[m.group(1).lower()] = m.group(2).strip()
    return out


def parse_expiry(val):
    """Return datetime deadline or None (unparseable). Bare date -> end of day."""
    m = DATE.search(val)
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if m.group(4):
        return datetime(y, mo, d, int(m.group(4)), int(m.group(5)))
    return datetime(y, mo, d, 23, 59, 59)


def scan(root, now=None):
    now = now or datetime.now()
    buckets = {"PAST-DUE": [], "LIVE": [], "UNCLOCKED": [], "UNPARSEABLE": []}
    dirs = [root / "exchange", root / "exchange" / "inbound"]
    for d in dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            try:
                fm = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace")[:4000])
            except OSError:
                continue
            exp, osil = fm.get("expires"), fm.get("on_silence")
            if not exp and not osil:
                continue
            if exp:
                dl = parse_expiry(exp)
                if dl is None:
                    buckets["UNPARSEABLE"].append((p.name, exp))
                elif dl < now:
                    buckets["PAST-DUE"].append((p.name, exp, (osil or "NO on_silence")[:70]))
                else:
                    buckets["LIVE"].append((p.name, exp))
            else:
                buckets["UNCLOCKED"].append((p.name, (osil or "")[:70]))
    return buckets


def report(buckets):
    print(f"on_silence/expires reader — PAST-DUE {len(buckets['PAST-DUE'])} | "
          f"LIVE {len(buckets['LIVE'])} | UNCLOCKED {len(buckets['UNCLOCKED'])} | "
          f"UNPARSEABLE {len(buckets['UNPARSEABLE'])}")
    for name, exp, osil in buckets["PAST-DUE"]:
        print(f"  PAST-DUE  {name}  expired {exp}  on_silence: {osil}")
    for name, exp in buckets["UNPARSEABLE"]:
        print(f"  UNPARSEABLE  {name}  expires: {exp}")
    if buckets["UNCLOCKED"]:
        print(f"  (UNCLOCKED letters carry a default that can never come due — "
              f"{len(buckets['UNCLOCKED'])} of them; list with --unclocked)")


def selftest():
    fails = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ex = root / "exchange"
        ex.mkdir()
        now = datetime(2026, 9, 1, 12, 0)
        cases = {
            "past-due.md": "---\nexpires: 2026-08-30\non_silence: ACTS — x\n---\nbody",
            # THE NEGATIVE CONTROL (Herald: mandatory) — future-dated must NOT register
            "future.md": "---\nexpires: 2026-12-31\non_silence: ACTS — y\n---\nbody",
            "unclocked.md": "---\non_silence: nothing acts\n---\nbody",
            "unparseable.md": "---\nexpires: when Jon returns\non_silence: NO-OP\n---\nbody",
            "bare-date-today.md": "---\nexpires: 2026-09-01\non_silence: ACTS\n---\nbody",
            "no-fields.md": "---\nkind: letter\n---\nbody",
        }
        for n, c in cases.items():
            (ex / n).write_text(c, encoding="utf-8")
        b = scan(root, now=now)
        def check(cond, label):
            if not cond:
                fails.append(label)
            print(("PASS " if cond else "FAIL ") + label)
        check([x[0] for x in b["PAST-DUE"]] == ["past-due.md"],
              "exactly the past-due letter registers past-due (negative control: future.md absent)")
        check(any(x[0] == "future.md" for x in b["LIVE"]), "future-dated registers LIVE")
        check([x[0] for x in b["UNCLOCKED"]] == ["unclocked.md"], "unclocked bucketed alone")
        check([x[0] for x in b["UNPARSEABLE"]] == ["unparseable.md"], "prose expiry UNPARSEABLE, not guessed")
        check(any(x[0] == "bare-date-today.md" for x in b["LIVE"]),
              "bare date = end of day (noon of expiry day is still LIVE)")
        check(scan(root, now=datetime(2026, 9, 2, 0, 1))["PAST-DUE"].__len__() == 2,
              "same bare date IS past-due the next morning (both directions)")
    print(f"selftest: {'ALL PASS' if not fails else f'{len(fails)} FAILURES'}")
    return 1 if fails else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(".")
    buckets = scan(root)
    report(buckets)
    if "--unclocked" in sys.argv:
        for name, osil in buckets["UNCLOCKED"]:
            print(f"  UNCLOCKED  {name}  on_silence: {osil}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
