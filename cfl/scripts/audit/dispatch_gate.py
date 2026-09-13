#!/usr/bin/env python3
"""dispatch_gate.py -- GO/HOLD before dispatching a lane, read from the live usage meter.

Calibrated 2026-09-02 13:18->13:38 CDT (USAGE-LOG-cfl.jsonl): five_hour 62->100 while seven_day
52->60, i.e. ~4.75 five-hour points per weekly point. Six concurrent fable lanes burned 8 weekly
points in 20 minutes (~24 pts/h) against a plan line near 0.9 pts/h, hit the five-hour cap at
13:4x and lost the next four hours entirely (meter flat at 100 until the 17:40 reset). The
five-hour cap never binds at plan pace; it binds only on bursts. So the gate holds on EITHER
signal: weekly ahead of the linear line by more than AHEAD_TOL, or five_hour above FH_CEILING.

Exit 0 = GO, 1 = HOLD, 2 = UNKNOWN (meter stale/missing; UNKNOWN is not GO).
--selftest exercises all three verdicts on in-memory fixtures (nothing written).
"""
import json
import sys
from datetime import datetime
from pathlib import Path

METER = Path(r"N:\claude-gists-private\USAGE-CURRENT-cfl.json")
# Plan anchor: re-measured after the 17:40 reset. Weekly remaining is spent linearly to the reset.
ANCHOR_T = datetime(2026, 9, 2, 17, 41)          # CDT, naive
ANCHOR_USED = 61.0                                # seven_day.utilization at the anchor
WEEK_RESET = datetime(2026, 9, 4, 14, 0)          # Fri 14:00 CDT
TARGET_USED = 95.0                                # leave <= 5% on the table (Jon, 2026-09-02)
AHEAD_TOL = 1.5                                   # weekly points ahead of the line before HOLD
FH_CEILING = 85.0                                 # five-hour utilization ceiling
# CONCURRENCY, NOT RATE (Soul, 2026-09-03): "one lane per GO" bounds how many lanes run at once, not how often
# one starts. Re-run this gate on every lane return; a GO read only on a clock tick makes the tick interval an
# undesigned throttle (measured 2026-09-03: hourly ticks spent ~3% of capacity while every tick said GO).
STALE_MIN = 15
FUTURE_TOL_MIN = 5       # UR-alt D-1: a stamp more than this far in the future is UNKNOWN, never fresh   # was 45; Soul/Herald measured a 31-min-old meter under-reading five_hour 3.7x (2026-09-02 23:2x)
FH_PER_WEEKLY = 4.75
STEADY_SLACK = 2.0        # weekly points of slack above which the steady state (2 sonnet-equivalent lanes) applies
FABLE_PER_SONNET = 2      # [recalled, unmeasured] cost of one fable lane in sonnet lanes; measure before relying on it


def verdict(m, now):
    """Return (code, lines) for a meter dict at time `now`. Never raises: UR-alt D-2 (2026-09-03) showed a
    timezone-aware fetched_at or a string utilization crashing to exit 1 (= HOLD) with EMPTY stdout."""
    try:
        return _verdict(m, now)
    except Exception as e:  # noqa: BLE001
        return 2, [f"UNKNOWN: gate crashed while reading the meter ({type(e).__name__}: {e}); a crash is not a HOLD"]


def _verdict(m, now):
    out = []
    try:
        fetched = datetime.fromisoformat(m["fetched_at"])
        if fetched.tzinfo is not None:
            from datetime import timezone, timedelta
            fetched = fetched.astimezone(timezone(timedelta(hours=-5))).replace(tzinfo=None)
    except Exception:
        return 2, ["UNKNOWN: fetched_at missing or unparseable"]
    age = (now - fetched).total_seconds() / 60
    if age > STALE_MIN:
        return 2, [f"UNKNOWN: meter {age:.0f} min old (> {STALE_MIN})"]
    # UR-alt D-1 (2026-09-03): STALE_MIN was one-sided; a fetched_at in the FUTURE (a UTC stamp read
    # as local, a clock skew) passed as fresh and a five-hour-stale meter returned GO lanes=2.
    if age < -FUTURE_TOL_MIN:
        return 2, [f"UNKNOWN: meter stamp is {-age:.0f} min in the FUTURE (fetched_at {m['fetched_at']} vs now "
                   f"{now:%Y-%m-%dT%H:%M}); a timezone or clock defect, not a fresh reading"]
    sd = (m.get("seven_day") or {}).get("utilization")
    fh = (m.get("five_hour") or {}).get("utilization")
    if sd is None or fh is None:
        return 2, ["UNKNOWN: seven_day or five_hour utilization null"]
    # 2026-09-03 (Soul finding ef45eb39): take the reset instant from the meter's own field; the
    # constant is the fallback. A reset in the past is UNKNOWN, never a verdict from a dead week.
    week_reset = WEEK_RESET
    ra = (m.get("seven_day") or {}).get("resets_at")
    if ra:
        try:
            from datetime import timezone, timedelta
            week_reset = datetime.fromisoformat(ra).astimezone(timezone(timedelta(hours=-5))).replace(tzinfo=None)
        except Exception:
            out.append(f"note: seven_day.resets_at unparseable ({ra!r}); using constant {WEEK_RESET}")
    if week_reset <= now:
        return 2, [f"UNKNOWN: week reset {week_reset} is in the past; re-anchor the gate before trusting it"]
    span = (week_reset - ANCHOR_T).total_seconds()
    frac = (now - ANCHOR_T).total_seconds() / span
    line = ANCHOR_USED + (TARGET_USED - ANCHOR_USED) * max(0.0, min(1.0, frac))
    ahead = sd - line
    rate = (TARGET_USED - ANCHOR_USED) / (span / 3600)
    out.append(f"meter {m['fetched_at']} (age {age:.0f} min)  seven_day={sd}  five_hour={fh}")
    out.append(f"line now={line:.1f}  ahead={ahead:+.1f} (tol {AHEAD_TOL})  plan rate={rate:.2f} pts/h")
    if fh >= FH_CEILING:
        out.append(f"HOLD lanes=0: five_hour {fh} >= {FH_CEILING} (burst; a cap-hit loses hours, not points)")
        return 1, out
    if ahead > AHEAD_TOL:
        out.append(f"HOLD lanes=0: weekly {ahead:+.1f} ahead of line")
        return 1, out
    slack = -ahead
    # 2026-09-03 (Professional's design note): emit the DECISION, not a number to be read. The steady state
    # (cap letter 09-02: one fable or two sonnet lanes) applies while slack > STEADY_SLACK; otherwise one lane.
    lanes = 2 if slack > STEADY_SLACK else 1
    # Professional 2026-09-03 18:03: a negative slack printed beside GO reads as a contradiction to a seat scanning
    # the line; say "ahead of line, within tol" instead of a negative quantity.
    if slack >= 0:
        budget = f"{slack:.1f} weekly points of slack (~{slack * FH_PER_WEEKLY:.0f} five-hour points)"
    else:
        budget = f"{-slack:.1f} ahead of line (GO while within tol {AHEAD_TOL})"
    out.append(f"GO lanes={lanes} (sonnet-equivalent; 1 fable = {FABLE_PER_SONNET} sonnet [recalled, unmeasured]): "
               f"{budget}; re-check on every lane return")
    return 0, out


def selftest():
    now = datetime(2026, 9, 2, 18, 0)
    fresh = now.isoformat(timespec="seconds")
    cases = [
        ("GO", {"fetched_at": fresh, "seven_day": {"utilization": 61.0}, "five_hour": {"utilization": 10.0}}, 0),
        ("HOLD-weekly", {"fetched_at": fresh, "seven_day": {"utilization": 70.0}, "five_hour": {"utilization": 10.0}}, 1),
        ("HOLD-fivehour", {"fetched_at": fresh, "seven_day": {"utilization": 61.0}, "five_hour": {"utilization": 90.0}}, 1),
        ("UNKNOWN-stale", {"fetched_at": "2026-09-02T12:00:00", "seven_day": {"utilization": 61.0}, "five_hour": {"utilization": 10.0}}, 2),
        ("UNKNOWN-null", {"fetched_at": fresh, "seven_day": {"utilization": None}, "five_hour": {"utilization": 10.0}}, 2),
        # 2026-09-03 (Professional's finding): the two resets_at branches had zero coverage.
        ("UNKNOWN-reset-past", {"fetched_at": fresh, "seven_day": {"utilization": 61.0, "resets_at": "2026-09-02T10:00:00+00:00"},
                                "five_hour": {"utilization": 10.0}}, 2),
        # near reset overrides the constant: at 09-03 10:00 with 80 used, the constant line is ~73.5 -> HOLD;
        # a reset at 10:30 CDT the same day puts the line at ~94 -> GO. Same meter minus resets_at must HOLD.
        ("GO-resets_at-overrides-constant", {"fetched_at": "2026-09-03T10:00:00", "seven_day": {"utilization": 80.0, "resets_at": "2026-09-03T15:30:00+00:00"},
                                             "five_hour": {"utilization": 10.0}, "_now": datetime(2026, 9, 3, 10, 0)}, 0),
        ("HOLD-same-meter-without-resets_at", {"fetched_at": "2026-09-03T10:00:00", "seven_day": {"utilization": 80.0},
                                               "five_hour": {"utilization": 10.0}, "_now": datetime(2026, 9, 3, 10, 0)}, 1),
    ]
    # UR-alt D-1 / D-2 / D-3 fixtures (2026-09-03). "_expect" is a substring the output MUST contain.
    cases += [
        ("UNKNOWN-future-stamp (D-1)", {"fetched_at": "2026-09-02T22:25:00", "seven_day": {"utilization": 61.0},
                                         "five_hour": {"utilization": 10.0}, "_expect": "FUTURE"}, 2),
        ("UNKNOWN-not-crash on string utilization (D-2)", {"fetched_at": fresh, "seven_day": {"utilization": "61"},
                                                            "five_hour": {"utilization": 10.0}, "_expect": "UNKNOWN"}, 2),
        ("GO lanes=2 asserted (D-3)", {"fetched_at": fresh, "seven_day": {"utilization": 58.0},
                                        "five_hour": {"utilization": 10.0}, "_expect": "lanes=2"}, 0),
        ("GO lanes=1 asserted (D-3)", {"fetched_at": fresh, "seven_day": {"utilization": 60.5},
                                        "five_hour": {"utilization": 10.0}, "_expect": "lanes=1"}, 0),
    ]
    bad = 0
    for name, m, want in cases:
        expect = m.pop("_expect", None)
        got, lines = verdict(m, m.pop("_now", now))
        if expect and expect not in "\n".join(lines):
            print(f"FAIL {name}: output lacks '{expect}': {lines}")
            bad += 1
            continue
        ok = got == want
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name}: want {want} got {got}")
    print("SELFTEST", "PASS" if not bad else f"FAIL ({bad})")
    return 1 if bad else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if not METER.is_file():
        print("UNKNOWN: meter file missing", METER)
        return 2
    m = json.loads(METER.read_text(encoding="utf-8"))
    code, lines = verdict(m, datetime.now())
    print("\n".join(lines))

    # CB-3's consequent: the verifier's OPEN findings surface HERE, at the moment somebody decides
    # whether to dispatch -- because that is the one line this program actually reads every 20
    # minutes. Deliberately NON-BLOCKING, and it does not touch `code`: a verifier fault must never
    # wedge the fleet (same reasoning that keeps py_closed.sh's --block off Stop/SessionEnd).
    # Visibility IS the consequent.
    #   "The verifier caught it, reported it, and NOTHING CHANGED as a result. A finding with no
    #    consequent is a log line." -- wiki/tracker/wayfinder-compact-barrier-2026-09-04.md, CB-3
    try:
        import subprocess
        from pathlib import Path as _P
        _fc = str(_P(__file__).with_name("finding_consequent.py"))
        r = subprocess.run([sys.executable, _fc, "--count"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        out = [x for x in (r.stdout or "").strip().splitlines() if x.strip()]
        n = out[-1] if out else ""
        if r.returncode == 0 and n.isdigit():
            if int(n):
                print("findings OPEN=%s (postcompact verifier, deduplicated; "
                      "python scripts/audit/finding_consequent.py)" % n)
        else:
            # an unreadable count is UNKNOWN, never a silent zero -- that exact false clean was
            # measured in finding_consequent.py's own first real run tonight
            print("findings OPEN=UNKNOWN (finding_consequent could not report; NOT a zero)")
    except Exception as e:
        print("findings OPEN=UNKNOWN (%s; NOT a zero)" % e.__class__.__name__)
    return code


if __name__ == "__main__":
    sys.exit(main())
