#!/usr/bin/env python3
"""runlock.py — one instance of a hook script at a time, and a stated reason when it is not.

WHY, measured 2026-09-04 21:2x on this session's own compact, and it is visible in Jon's terminal
if you scroll: the SAME pipeline printed TWO CONTRADICTORY TABLES in the same minute.

    PostCompact           run:  2 ingest wiki PASS  |  9 summary vs tail FAIL
    SessionStart:compact  run:  2 ingest wiki FAIL  |  9 summary vs tail PASS

Both are `postcompact_pipeline.py`. `.claude/settings.json` wires it on PostCompact AND on
SessionStart(compact|clear), and a compact fires BOTH. They ran concurrently, raced on the single
output file exchange/su-close/POSTCOMPACT-STATUS.md, and the copy left on disk is whichever
finished last -- which tonight was NOT the copy Jon's screen showed.

⛔ THE DEFECT IS NOT THE DOUBLE WIRE. Removing one wiring would leave `clear` uncovered and would
not stop the next double wire. The defect is that TWO WRITERS OF ONE VERDICT FILE HAD NO
ARBITRATION, so the disagreement was silent: each table is internally consistent, neither says a
second run exists, and a reader has no way to tell they are looking at one of two.

⭐ AND STEP 2's DISAGREEMENT IS THE EXPENSIVE HALF. main_thread_ingest writes
wiki/intake-triage/main-thread/<sid>/...i1.md. Run by hand immediately after, single-instance, it
returns exit 0 and "1 written ... 73 Jon utterance(s), 57 anchored, 4983 turns". So the FAIL was
never about the ingest being broken -- it was two processes writing one path. ⛔ A CONCURRENCY
ARTEFACT WAS GRADED AS A CONTENT FAILURE, and the pipeline's own note ("no output") pointed
squarely away from the cause.

CONTRACT
--------
    with runlock("postcompact_pipeline") as lk:
        if not lk.acquired:
            print(lk.reason); return 0      # a skip that NAMES ITS HOLDER, never a silent one
        ...

  * O_CREAT|O_EXCL acquire. The loser NEVER writes the verdict file -- a second opinion that
    overwrites the first is worse than no second opinion.
  * A lock older than `stale_s` is STOLEN and the theft is reported. A crashed run must not wedge
    every future compact; that would turn this fix into a bigger outage than the bug.
  * The reason string always carries the holder's pid and the lock's age. "Skipped" with no holder
    named is indistinguishable from "did not run", which is the class of error this whole pipeline
    exists to end.
"""
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(_HERE)),
                     ".claude", "hooks", "state")


class _Lock(object):
    def __init__(self, name, stale_s=900, state_dir=None):
        self.name = name
        self.stale_s = stale_s
        self.dir = state_dir or STATE
        self.path = os.path.join(self.dir, "%s.lock" % name)
        self.acquired = False
        self.reason = ""
        self.stole = False

    def _read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except OSError:
            return ""

    def acquire(self):
        try:
            os.makedirs(self.dir, exist_ok=True)
        except OSError as e:
            # an unlockable state dir must not stop the pipeline; run and say so
            self.acquired = True
            self.reason = "lock dir unavailable (%s) -- ran WITHOUT a lock" % e.__class__.__name__
            return self
        payload = "pid=%d start=%.3f argv=%s" % (os.getpid(), time.time(), " ".join(sys.argv[:3]))
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write(payload)
            self.acquired = True
            return self
        except FileExistsError:
            pass
        held = self._read()
        try:
            age = time.time() - os.path.getmtime(self.path)
        except OSError:
            age = -1.0
        if age < 0 or age > self.stale_s:
            # STEAL. A dead holder wedging every future compact is a worse outage than the race.
            try:
                with open(self.path, "w", encoding="utf-8") as f:
                    f.write(payload)
                self.acquired = True
                self.stole = True
                self.reason = ("stole a STALE lock (age %.0fs > %ds) held by [%s] -- the previous "
                               "run died without releasing" % (age, self.stale_s, held))
            except OSError as e:
                self.acquired = True
                self.reason = "could not steal stale lock (%s) -- ran anyway" % e.__class__.__name__
            return self
        self.acquired = False
        self.reason = ("SKIPPED -- another %s is already running: [%s], age %.1fs. This instance "
                       "wrote NOTHING; the holder owns the verdict file. Two writers of one verdict "
                       "file with no arbitration is how a compact produced two contradictory tables "
                       "in the same minute (2026-09-04 21:2x)." % (self.name, held, age))
        return self

    def release(self):
        if self.acquired:
            try:
                os.unlink(self.path)
            except OSError:
                pass

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *exc):
        self.release()
        return False


def runlock(name, stale_s=900, state_dir=None):
    return _Lock(name, stale_s=stale_s, state_dir=state_dir)


def self_test():
    import tempfile
    print("=== SELF-TEST -- runlock ===")
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
    a = runlock("t", state_dir=d).acquire()
    ok("1 first acquirer gets the lock", a.acquired, True)
    b = runlock("t", state_dir=d).acquire()
    # ⛔ THE DEFECT, reproduced: a second concurrent instance must NOT proceed to write the verdict
    ok("2 THE DEFECT: second concurrent instance is refused", b.acquired, False)
    ok("3 the refusal names the holder's pid", ("pid=%d" % os.getpid()) in b.reason, True)
    a.release()
    c = runlock("t", state_dir=d).acquire()
    ok("4 NEGATIVE CONTROL: after release the lock is free again", c.acquired, True)
    c.release()

    # a dead holder must not wedge future runs -- stale steal, and the steal is REPORTED
    p = os.path.join(d, "s.lock")
    with open(p, "w") as f:
        f.write("pid=999999 start=0 argv=dead")
    os.utime(p, (time.time() - 5000, time.time() - 5000))
    s = runlock("s", stale_s=900, state_dir=d).acquire()
    ok("5 a STALE lock is stolen, not obeyed", (s.acquired, s.stole), (True, True))
    ok("6 the theft is stated, with the age", "stale lock" in s.reason.lower(), True)
    s.release()
    # 7 POSITIVE CONTROL for 5: a FRESH lock of the same name is obeyed
    with open(p, "w") as f:
        f.write("pid=999999 start=0 argv=alive")
    ok("7 control: a FRESH lock is obeyed, not stolen",
       runlock("s", stale_s=900, state_dir=d).acquire().acquired, False)

    # a with-block releases even when the body raises
    try:
        with runlock("w", state_dir=d) as lk:
            ok("8 context manager acquires", lk.acquired, True)
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    ok("9 the lock is released even when the body raises",
       runlock("w", state_dir=d).acquire().acquired, True)
    print("  %d passed, %d failed" % (np, nf))
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else 0)
