"""watch_inbound_v2_PROPOSAL.py -- the dead-man watcher with the blind window closed. PROPOSAL, not deployed.

Defect in v1 (Soul, 2026-09-11 22:2x, measured: 265 routed Jon turns landed in Personal's inbound
between one watcher exiting and the next starting; the next watcher baselined them as pre-existing
and nobody was woken): v1 captures seen = set(os.listdir()) AT START, so the blind window equals the
length of the seat's turn.

Fix, kept small enough to audit: the watcher records the wall-clock at which it EXITS in a one-line
state file beside the inbound (never inside it). On start it treats as NEW any file whose mtime is
later than the previous exit, in addition to anything that appears while it polls. If no state file
exists (first run) it behaves exactly like v1 and says so. The state file is the only write.

PRECONDITION, load-bearing and stated (Soul's review, 2026-09-11 22:4x): v2 decides newness by mtime,
so it converts a blind window that was UNCONDITIONAL into one that is CONDITIONAL ON EVERY SENDER NOT
PRESERVING MTIME. A delivery made with cp -p, shutil.copy2 or robocopy lands a file with an old
mtime that v2 cannot see, exactly as v1 could not. Tonight's 265 all carried delivery-time mtimes
(22:30:49-50), so v2 would have caught all 265; the day a courier preserves mtime the window reopens
silently. Selftest arm 5 below is that case and is an EXPECTED FAILURE kept visible on purpose.

CORRECTION 2026-09-12 00:3x (found by Soul's confessional control fork of the author's own transcript, then
verified from this source): the earlier note "two independent guards" in arm 2 was false; "poll longer
than limit" left the loop one pass. Arm 2 now runs with limit=0, which makes the loop unreachable, so the
two guards are real: the direct landed_in_gap assertion, and a loop that cannot run.

SUITE PROPERTY (Soul, 2026-09-12 00:4x, six mutations run across two seats, exits captured without a
pipe): no single arm is sufficient and the set is. Arms 2 and 5 cover the gap check in both directions,
3 the poll loop, 4 exclusion, 1 first run. DO NOT SIMPLIFY ARM 4: it asserts "TIMER after" PRESENT and
"NEW MAIL" ABSENT together; presence alone is fooled by a TIMER path that prints the poll line (M5).
Unmutated so far: read_last_exit and the state-path computation.

Not deployed tonight by the author's own rule and Soul's: a design change to the fleet's only working
resume path deserves a non-author read and a Saturday window. Selftest below covers: first run
(no state), a file landing during the turn gap, a file landing during the poll, and a stale state file
older than the newest file.

usage: python -u scripts/watch_inbound_v2_PROPOSAL.py [seconds, default 1200] [inbound dir]
       python -u scripts/watch_inbound_v2_PROPOSAL.py --selftest
"""
import os
import sys
import tempfile
import time

here = os.path.dirname(os.path.abspath(__file__))


def state_path(inbound):
    return os.path.join(os.path.dirname(os.path.abspath(inbound)), ".watch_inbound.last_exit")


def read_last_exit(inbound):
    p = state_path(inbound)
    try:
        with open(p, "r", encoding="utf-8") as f:
            return float(f.read().strip())
    except Exception:
        return None


def write_last_exit(inbound):
    with open(state_path(inbound), "w", encoding="utf-8") as f:
        f.write("%f\n" % time.time())


def landed_in_gap(inbound, last_exit):
    """Files whose mtime is after the previous watcher's exit: they landed during the seat's turn."""
    out = []
    for n in os.listdir(inbound):
        try:
            if os.path.getmtime(os.path.join(inbound, n)) > last_exit:
                out.append(n)
        except OSError:
            pass
    return sorted(out)


def watch(inbound, limit, poll=20, _sleep=time.sleep):
    if not os.path.isdir(inbound):
        print("UNKNOWN: inbound dir not found: %s" % inbound)
        return 2
    last_exit = read_last_exit(inbound)
    seen = set(os.listdir(inbound))
    print("watching %s (%d files) for %d s; previous exit: %s" % (
        inbound, len(seen), limit,
        ("%.0f s ago" % (time.time() - last_exit)) if last_exit else "NONE (first run: gap check skipped, v1 behaviour)"))
    if last_exit is not None:
        gap = landed_in_gap(inbound, last_exit)
        if gap:
            print("NEW MAIL landed during the turn gap (%d):" % len(gap))
            for n in gap:
                print("  " + n)
            write_last_exit(inbound)
            return 0
    start = time.time()
    while time.time() - start < limit:
        _sleep(poll)
        now = set(os.listdir(inbound))
        new = sorted(now - seen)
        if new:
            print("NEW MAIL after %d s:" % int(time.time() - start))
            for n in new:
                print("  " + n)
            write_last_exit(inbound)
            return 0
    print("TIMER after %d s, no new mail; wake anyway and check the clock" % int(time.time() - start))
    write_last_exit(inbound)
    return 0


def run(inbound, limit, poll, _sleep=time.sleep):
    """Run watch() and return (rc, captured stdout). Soul's mutation 4 (2026-09-12 00:4x): deleting the
    poll loop passed the suite because arm 3 asserted rc == 0, which the TIMER path also returns. Every
    arm now asserts the line that only its path prints: 'landed during the turn gap', 'NEW MAIL after',
    'TIMER after'. Assert the observable, not the code."""
    import contextlib
    import io as _io
    buf = _io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = watch(inbound, limit, poll=poll, _sleep=_sleep)
    out = buf.getvalue()
    sys.stdout.write(out)
    return rc, out


def selftest():
    fails = 0
    d = tempfile.mkdtemp()
    inbound = os.path.join(d, "inbound")
    os.mkdir(inbound)
    # 1. first run, no state: times out, writes state
    rc, out = run(inbound, 1, poll=0.2)
    ok = rc == 0 and os.path.exists(state_path(inbound)) and "TIMER after" in out and "first run" in out
    print("  1 first run no state      : rc=%d state=%s timer_line=%s (expect 0, True, True)" % (rc, os.path.exists(state_path(inbound)), "TIMER after" in out))
    fails += 0 if ok else 1
    # 2. a file lands during the turn gap (after exit, before next start): caught AT START.
    #    Soul, 22:4x: the first version asserted rc == 0, which the poll loop also produces, so the arm
    #    passed with the gap check deleted. Now: (a) the gap check itself must list the file, and
    #    (b) watch() is run with poll LONGER than limit so the loop structurally cannot catch it.
    time.sleep(0.05)
    open(os.path.join(inbound, "gap-letter.md"), "w").write("x")
    in_gap = "gap-letter.md" in landed_in_gap(inbound, read_last_exit(inbound))
    # Soul's confessional control fork, 2026-09-12 00:3x, verified from source: "poll > limit" was
    # DECORATIVE. The while condition is evaluated before the sleep, so limit 1 / poll 5 still gives
    # the loop one full pass and it can catch the file. limit=0 makes the loop unreachable
    # (`time.time() - start < 0` is false at once), so only the start check can return before TIMER.
    rc, out = run(inbound, 0, poll=5)
    gap_line = "landed during the turn gap" in out
    print("  2 file in the turn gap    : listed_by_gap_check=%s gap_line=%s rc=%d (expect True, True, 0; limit=0 so the poll loop is unreachable)" % (in_gap, gap_line, rc))
    fails += 0 if (in_gap and gap_line and rc == 0) else 1
    # 3. a file lands during the poll: caught by the LOOP, proven by the line only the loop prints
    def sleeper(s):
        time.sleep(s)
        if not os.path.exists(os.path.join(inbound, "poll-letter.md")):
            open(os.path.join(inbound, "poll-letter.md"), "w").write("y")
    rc, out = run(inbound, 5, poll=0.2, _sleep=sleeper)
    poll_line = "NEW MAIL after" in out and "poll-letter.md" in out
    print("  3 file during the poll    : poll_line=%s rc=%d (expect True, 0; Soul's mutation 4 deleted the loop and rc alone passed)" % (poll_line, rc))
    fails += 0 if (poll_line and rc == 0) else 1
    # 4. state older than the newest file after a clean exit: nothing new, times out
    rc, out = run(inbound, 1, poll=0.2)
    timer_line = "TIMER after" in out and "NEW MAIL" not in out
    print("  4 nothing new             : timer_line=%s rc=%d (expect True, 0)" % (timer_line, rc))
    fails += 0 if (timer_line and rc == 0) else 1
    # 5. XFAIL (Soul's arm): a file delivered in the turn gap with a PRESERVED old mtime. v2 cannot see it,
    #    because newness is decided by mtime. Expected: NOT caught at start (TIMER). This arm passes when
    #    the failure is reproduced, so the precondition stays visible to the next reader.
    p = os.path.join(inbound, "gap-letter-old-mtime.md")
    open(p, "w").write("z")
    old = time.time() - 7200
    os.utime(p, (old, old))
    rc = watch(inbound, 1, poll=0.2)
    # rc is 0 either way; the observable is whether the start-gap check fired. Re-derive it directly:
    threshold = read_last_exit(inbound) - 2
    caught = "gap-letter-old-mtime.md" in landed_in_gap(inbound, threshold)
    # positive control (Soul, 22:4x): the same file with its mtime touched to now MUST be caught, or the
    # arm proves nothing twice. This is what makes "not caught" mean "mtime is the only reason".
    os.utime(p, None)
    caught_after_touch = "gap-letter-old-mtime.md" in landed_in_gap(inbound, threshold)
    print("  5 XFAIL old-mtime in gap  : caught=%s then_touched_caught=%s (expect False, True: the precondition, by design, with its positive control)" % (caught, caught_after_touch))
    fails += 0 if (not caught and caught_after_touch) else 1
    print("SELFTEST %s (%d failure(s); arm 5 is an expected failure that PASSES when reproduced)" % ("PASS" if fails == 0 else "FAIL", fails))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    inbound = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(here), "exchange", "inbound")
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    sys.exit(watch(inbound, limit))
