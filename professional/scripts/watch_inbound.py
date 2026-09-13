"""watch_inbound.py v2 -- the dead-man watcher with the blind window closed and the courier's noise ignored.

Deployed 2026-09-12 03:1x by Professional 682d274b from scripts/watch_inbound_v2_PROPOSAL.py after Soul's
non-author read (accepted 2026-09-11 22:4x; six mutations run across two seats 2026-09-12 00:4x) and the
Saturday window both arrived. v1 is preserved byte-for-byte as scripts/watch_inbound_v1_2026-09-11.py.

Defect in v1 (Soul, 2026-09-11 22:2x, measured: 265 routed Jon turns landed in Personal's inbound between one
watcher exiting and the next starting; the next watcher baselined them as pre-existing and nobody was woken):
v1 captures seen = set(os.listdir()) AT START, so the blind window equals the length of the seat's turn.

Fix, kept small enough to audit: the watcher records the wall-clock at which it EXITS in a one-line state file
beside the inbound (never inside it). On start it treats as NEW any file whose mtime is later than the previous
exit, in addition to anything that appears while it polls. If no state file exists (first run) it behaves exactly
like v1 and says so. The state file is the only write.

PRECONDITION, load-bearing and stated (Soul's review): v2 decides newness by mtime, so it converts a blind window
that was UNCONDITIONAL into one that is CONDITIONAL ON EVERY SENDER NOT PRESERVING MTIME. A delivery made with
cp -p, shutil.copy2 or robocopy lands a file with an old mtime that v2 cannot see, exactly as v1 could not.
Selftest arm 5 is that case and is an EXPECTED FAILURE kept visible on purpose.

ADDED AT DEPLOY (2026-09-12, tracker row M-17): the courier writes ASK-JON-ARRIVAL-<stamp>-step-<n>.md into every
inbound roughly once a minute (master's inbound: 1,276 files; Secretary's: 496 and rising). Those are the
dispatcher's own bookkeeping, not letters, and they woke this seat three times tonight on files that no longer
existed at read time. v2 IGNORES names matching IGNORE_PREFIXES for both the gap check and the poll, and prints how
many it ignored so a watcher that saw only noise says so. Arm 6 asserts noise does not wake and, as its positive
control, that a letter landing beside the noise does.

SUITE PROPERTY (Soul, six mutations): no single arm is sufficient and the set is. Arms 2 and 5 cover the gap check
in both directions, 3 the poll loop, 4 exclusion, 1 first run, 6 the ignore list. DO NOT SIMPLIFY ARM 4: it asserts
"TIMER after" PRESENT and "NEW MAIL" ABSENT together. Assert the observable, not the code.

usage: python -u scripts/watch_inbound.py [seconds, default 1200] [inbound dir]
       python -u scripts/watch_inbound.py --selftest
The -u matters: without it Python buffers stdout when backgrounded and the output file stays empty until exit.
"""
import os
import sys
import tempfile
import time

here = os.path.dirname(os.path.abspath(__file__))

IGNORE_PREFIXES = ("ASK-JON-ARRIVAL-",)
# Added 08:5x 2026-09-12: Antigravity's daemon now ACKs every inbound letter with a receipt couriered to all
# (97 in the first minute, 43 in this inbound within five). An ACK is a receipt, not an ask; it must not wake a
# seat. Counted like the arrival asks so the TIMER line still says how many arrived.
IGNORE_SUBSTRINGS = ("-DAEMON-ACK-", "-ROLLUP-")  # rollup: one 130 KB digest rewritten every courier tick, not an ask


def ignored(name):
    return any(name.startswith(p) for p in IGNORE_PREFIXES) or any(s in name for s in IGNORE_SUBSTRINGS)


def listing(inbound):
    """Names in the inbound that are letters, plus the count of courier-noise names skipped."""
    names = os.listdir(inbound)
    keep = set(n for n in names if not ignored(n))
    return keep, len(names) - len(keep)


def state_path(inbound):
    # WATCH_INBOUND_STATE_DIR: keep the exit-state file OUT of the watched tree (2026-09-12 13:1x —
    # a seat watching another tree's inbound must not write there; the auto-mode classifier refused the
    # write once the tree was contested). Default stays beside the inbound for the selftest and same-tree use.
    d = os.environ.get("WATCH_INBOUND_STATE_DIR") or os.path.dirname(os.path.abspath(inbound))
    tag = "".join(c if c.isalnum() else "_" for c in os.path.abspath(inbound))
    name = ".watch_inbound.last_exit" if not os.environ.get("WATCH_INBOUND_STATE_DIR") else ".watch_inbound.last_exit." + tag
    return os.path.join(d, name)


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
    """Letters whose mtime is after the previous watcher's exit: they landed during the seat's turn."""
    out = []
    keep, _ = listing(inbound)
    for n in keep:
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
    seen, noise = listing(inbound)
    print("watching %s (%d letters, %d courier-noise names ignored) for %d s; previous exit: %s" % (
        inbound, len(seen), noise, limit,
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
    # Distinct names, not a per-poll tally: the first deployed run printed "ignored: 33157" for ~550 files
    # because each poll re-counted every noise name already counted (measured 03:42, first TIMER fire).
    noise_at_start = set(n for n in os.listdir(inbound) if ignored(n))
    noise_seen = set(noise_at_start)
    ignored_during_poll = 0
    while time.time() - start < limit:
        _sleep(poll)
        now, _ = listing(inbound)
        noise_seen |= set(n for n in os.listdir(inbound) if ignored(n))
        ignored_during_poll = len(noise_seen - noise_at_start)
        new = sorted(now - seen)
        if new:
            print("NEW MAIL after %d s:" % int(time.time() - start))
            for n in new:
                print("  " + n)
            write_last_exit(inbound)
            return 0
    print("TIMER after %d s, no new mail (courier-noise names ignored: %d); wake anyway and check the clock" % (
        int(time.time() - start), ignored_during_poll))
    write_last_exit(inbound)
    return 0


def run(inbound, limit, poll, _sleep=time.sleep):
    """Run watch() and return (rc, captured stdout). Every arm asserts the line only its path prints."""
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
    # 2. a file lands during the turn gap: caught AT START; limit=0 makes the poll loop unreachable
    time.sleep(0.05)
    open(os.path.join(inbound, "gap-letter.md"), "w").write("x")
    in_gap = "gap-letter.md" in landed_in_gap(inbound, read_last_exit(inbound))
    rc, out = run(inbound, 0, poll=5)
    gap_line = "landed during the turn gap" in out
    print("  2 file in the turn gap    : listed_by_gap_check=%s gap_line=%s rc=%d (expect True, True, 0)" % (in_gap, gap_line, rc))
    fails += 0 if (in_gap and gap_line and rc == 0) else 1
    # 3. a file lands during the poll: caught by the LOOP, proven by the line only the loop prints
    def sleeper(s):
        time.sleep(s)
        if not os.path.exists(os.path.join(inbound, "poll-letter.md")):
            open(os.path.join(inbound, "poll-letter.md"), "w").write("y")
    rc, out = run(inbound, 5, poll=0.2, _sleep=sleeper)
    poll_line = "NEW MAIL after" in out and "poll-letter.md" in out
    print("  3 file during the poll    : poll_line=%s rc=%d (expect True, 0)" % (poll_line, rc))
    fails += 0 if (poll_line and rc == 0) else 1
    # 4. nothing new: TIMER present, NEW MAIL absent, together
    rc, out = run(inbound, 1, poll=0.2)
    timer_line = "TIMER after" in out and "NEW MAIL" not in out
    print("  4 nothing new             : timer_line=%s rc=%d (expect True, 0)" % (timer_line, rc))
    fails += 0 if (timer_line and rc == 0) else 1
    # 5. XFAIL: a file delivered in the turn gap with a PRESERVED old mtime is invisible; positive control by touch
    p = os.path.join(inbound, "gap-letter-old-mtime.md")
    open(p, "w").write("z")
    old = time.time() - 7200
    os.utime(p, (old, old))
    rc = watch(inbound, 1, poll=0.2)
    threshold = read_last_exit(inbound) - 2
    caught = "gap-letter-old-mtime.md" in landed_in_gap(inbound, threshold)
    os.utime(p, None)
    caught_after_touch = "gap-letter-old-mtime.md" in landed_in_gap(inbound, threshold)
    print("  5 XFAIL old-mtime in gap  : caught=%s then_touched_caught=%s (expect False, True: the precondition, by design, with its positive control)" % (caught, caught_after_touch))
    fails += 0 if (not caught and caught_after_touch) else 1
    # 6. courier noise: ASK-JON-ARRIVAL-* landing in the gap AND during the poll must NOT wake; a letter beside it MUST.
    #    Arm 5 touched a letter AFTER its watcher exited, so first consume that gap honestly (limit=0: gap check only),
    #    which refreshes the state file; otherwise this arm fails on arm 5's leftovers, not on the ignore list.
    run(inbound, 0, poll=5)
    time.sleep(0.05)
    open(os.path.join(inbound, "ASK-JON-ARRIVAL-2026-09-12-0801-step-1.md"), "w").write("n")
    in_gap_noise = "ASK-JON-ARRIVAL-2026-09-12-0801-step-1.md" in landed_in_gap(inbound, read_last_exit(inbound))
    def noisy_sleeper(s):
        time.sleep(s)
        open(os.path.join(inbound, "ASK-JON-ARRIVAL-2026-09-12-0802-step-2.md"), "w").write("n")
    rc, out = run(inbound, 1, poll=0.2, _sleep=noisy_sleeper)
    noise_silent = "TIMER after" in out and "NEW MAIL" not in out and "ignored: " in out
    # positive control: same shape, but a letter lands during the poll too
    def noisy_then_letter(s):
        time.sleep(s)
        open(os.path.join(inbound, "ASK-JON-ARRIVAL-2026-09-12-0803-step-3.md"), "w").write("n")
        if not os.path.exists(os.path.join(inbound, "real-letter.md")):
            open(os.path.join(inbound, "real-letter.md"), "w").write("r")
    rc2, out2 = run(inbound, 5, poll=0.2, _sleep=noisy_then_letter)
    control = "NEW MAIL after" in out2 and "real-letter.md" in out2 and "ASK-JON-ARRIVAL" not in out2
    print("  6 courier noise ignored   : gap_lists_noise=%s poll_silent_on_noise=%s letter_beside_noise_wakes=%s (expect False, True, True)" % (in_gap_noise, noise_silent, control))
    fails += 0 if (not in_gap_noise and noise_silent and control) else 1
    print("SELFTEST %s (%d failure(s); arm 5 is an expected failure that PASSES when reproduced)" % ("PASS" if fails == 0 else "FAIL", fails))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    inbound = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(here), "exchange", "inbound")
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    sys.exit(watch(inbound, limit))
