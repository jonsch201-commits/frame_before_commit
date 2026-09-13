"""Dead-man's switch for a background seat.

A background job's turn ends when it reports, and nothing re-invokes it. Jon, 2026-09-11 ~16:11 CDT
to ears, verbatim, typos his: "I told you that you can't rely on me for this. You should have made a
skill but didn't?" So this script is the mechanism. Run it with run_in_background; it exits when new
mail lands in this trunk's inbound or when the time limit passes, and the harness re-invokes the seat
on exit. Start it again at the end of every turn. A seat that forgets is a seat that stops.

usage: python -u scripts/watch_inbound.py [seconds, default 1200] [inbound dir]
The -u matters: without it Python buffers stdout when backgrounded and the output file stays empty
until exit, so a running watcher and a dead one look the same (Secretary, 2026-09-11 20:3x).
"""
import os
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
inbound = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(here), "exchange", "inbound")
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1200

if not os.path.isdir(inbound):
    print("UNKNOWN: inbound dir not found: %s" % inbound)
    sys.exit(2)

start = time.time()
seen = set(os.listdir(inbound))
print("watching %s (%d files) for %d s" % (inbound, len(seen), limit))
while time.time() - start < limit:
    time.sleep(20)
    now = set(os.listdir(inbound))
    new = sorted(now - seen)
    if new:
        print("NEW MAIL after %d s:" % int(time.time() - start))
        for n in new:
            print("  " + n)
        sys.exit(0)
print("TIMER after %d s, no new mail; wake anyway and check the clock" % int(time.time() - start))
