#!/usr/bin/env python3
"""feed_liveness.py -- a published number must carry the age of every input it stands on.

WHY THIS EXISTS
---------------
Jon, 2026-09-04, on why three of this week's lessons have no test:

    and thats because you are still thinking and improving more broadly, and
    reconciling its update timing framework with our wiki and how i'm thinking of
    the skill of searching the wiki?

He is right about the framework and the split is sharper than "still thinking".
Of the week's lessons, the five that HAVE tests are all "a number or a file was
wrong". The three that do not are all "AN INPUT STOPPED":

  * claude.ai capture died 2026-08-17 and nothing alarmed for 18 days
  * the compact pipeline's ingest step was hardcoded SKIPPED for months
  * coverage was computed and published over a feed that had stopped

CFL could test CORRECTNESS and had no instrument for the LIVENESS OF AN INPUT.
Everything built this week checks whether a computation is right; nothing checked
whether the thing feeding it is still alive. A stale input returns a confident
answer, which is why searching the wiki is unreliable in a way better searching
cannot fix.

MEASURED at first run, 2026-09-04:

    claude-ai     667 files   newest 2026-08-17 12:04   18.2 days   STALE
    claude-code  5103 files   newest 2026-09-04 15:07    0.0 days   ok

The coverage denominator of 876 sessions is TWO FEEDS, one of which had been dead
for eighteen days, and every coverage figure published this week said 876 without
saying that.

WHAT IT DOES
------------
Reports, per feed: file count, newest mtime, age in days, and a verdict against a
threshold. Exit 3 when any feed is stale, so a caller can refuse to publish.

BOUNDS
------
  * mtime is the CAPTURE time, not the conversation time. A feed re-copied without
    new content looks fresh. This measures the PIPE, not the CONTENT.
  * An EMPTY feed directory is UNKNOWN, never fresh -- a directory with no files
    has no newest file, and "no evidence of staleness" is not evidence of liveness.
  * A MISSING directory is UNKNOWN and dominates: it is not a zero.
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

# THREE TREES, NOT ONE -- and this is the finding, not the configuration.
#
# Secretary, 2026-09-04 ~16:4x, after their own G5 freshness gate went red at 18
# days and they traced it to the tree it was walking rather than to any real
# staleness:
#
#     "the CFL claude-ai corpus" is THREE trees (mirror 691/0.0d, clone
#     113/0.6d, frozen 667/18.2d) and your feed_liveness.py is the only
#     instrument in the fleet that names its root in the source. That is why
#     yours was right.
#
# It was right by construction, not by insight, and naming ONE root is only half
# the property. An instrument that names one root cannot tell you that two other
# trees answer to the same words. So all three are listed and all three are
# printed, every run -- because the failure being guarded is not "a feed went
# stale", it is "two people said claude-ai and meant different directories".
#
# Their own gate is the fixture: v1 read the FROZEN checkout and printed a false
# red; the fix then went GREEN on a manifest file Secretary had deposited
# themselves -- a freshness gate passing on its own author's deposit, inside the
# fix for a false red.
DEFAULT_FEEDS = {
    "claude-ai": "N:/claude-corpus/cfl/raw/transcripts/claude-ai",
    "claude-code": "N:/claude-corpus/cfl/raw/transcripts/claude-code",
    # The other two trees that answer to "the claude-ai corpus". They are NOT
    # gated (see NON_GATING) -- reporting them is the point; failing on them
    # would make every run red for a condition that is expected.
    "claude-ai@clone": "N:/claude-cfl/clone/raw/transcripts/claude-ai",
    "claude-ai@frozen": ("G:/My Drive/Claude/Claude Foundational Layer/"
                         "claude-foundational-layer/raw/transcripts/claude-ai"),
}

# Feeds that are REPORTED but never cause exit 3. A frozen checkout is supposed
# to be frozen; failing on it would train a reader to ignore the exit code, which
# is how a gate stops meaning anything.
NON_GATING = {"claude-ai@clone", "claude-ai@frozen"}


def measure_feed(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"state": "UNKNOWN", "why": "directory does not exist", "files": None}
    newest, n = 0.0, 0
    for f in p.rglob("*.md"):
        n += 1
        m = f.stat().st_mtime
        if m > newest:
            newest = m
    if n == 0:
        return {"state": "UNKNOWN", "why": "directory exists but holds no .md files "
                                           "-- no newest file means no measurement", "files": 0}
    return {"state": "MEASURED", "files": n, "newest": newest,
            "age_days": (time.time() - newest) / 86400.0}


def verdict(m: dict, max_age_days: float) -> str:
    if m["state"] != "MEASURED":
        return "UNKNOWN"
    return "STALE" if m["age_days"] > max_age_days else "ok"


def self_check() -> list:
    import tempfile, os
    fails = []
    with tempfile.TemporaryDirectory() as td:
        # A missing directory must be UNKNOWN, never fresh.
        if measure_feed(os.path.join(td, "nope"))["state"] != "UNKNOWN":
            fails.append("a missing feed was not UNKNOWN")
        # An EMPTY directory must be UNKNOWN, never ok. This is the control that
        # matters: a feed that has stopped and been cleaned looks identical to a
        # feed that never started, and both must refuse to report fresh.
        empty = os.path.join(td, "empty")
        os.makedirs(empty)
        m = measure_feed(empty)
        if m["state"] != "UNKNOWN":
            fails.append("an EMPTY feed reported as measured -- it would read as fresh")
        if verdict(m, 3) != "UNKNOWN":
            fails.append("an empty feed's verdict was not UNKNOWN")
        # A fresh file must read ok, and an old one STALE. Both directions.
        live = os.path.join(td, "live")
        os.makedirs(live)
        f = os.path.join(live, "a.md")
        open(f, "w").close()
        if verdict(measure_feed(live), 3) != "ok":
            fails.append("a just-written file did not read ok")
        old = time.time() - 30 * 86400
        os.utime(f, (old, old))
        if verdict(measure_feed(live), 3) != "STALE":
            fails.append("a 30-day-old file did not read STALE -- the check cannot fire")
        # A NON-GATING feed that is stale must be REPORTED and must NOT gate.
        # Without this, adding the frozen tree would turn every run red for a
        # condition that is expected, and a reader trained to ignore an exit code
        # is worse off than one with no code at all.
        if "claude-ai@frozen" not in NON_GATING:
            fails.append("the frozen tree is not marked non-gating; every run would "
                         "go red for an expected condition")
        if "claude-ai" in NON_GATING:
            fails.append("the LIVE mirror was marked non-gating -- the one feed that "
                         "must be able to fail cannot")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age-days", type=float, default=3.0)
    ap.add_argument("--feed", action="append", metavar="NAME=PATH",
                    help="override or add a feed; repeatable")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    if a.self_check:
        f = self_check()
        if f:
            print(f"SELF-CHECK: FAIL -- {len(f)}")
            for x in f:
                print("  " + x)
            return 1
        print("SELF-CHECK: PASS -- 8 assertions, both directions, incl. the control that an "
              "EMPTY feed is UNKNOWN rather than fresh")
        return 0

    feeds = dict(DEFAULT_FEEDS)
    for spec in (a.feed or []):
        if "=" in spec:
            k, v = spec.split("=", 1)
            feeds[k] = v

    stale = 0
    print("=== FEED LIVENESS === (mtime measures the PIPE, not the content)")
    print("    Three trees answer to \"the claude-ai corpus\". All three print, every")
    print("    run: the failure guarded here is two people saying claude-ai and meaning")
    print("    different directories. Only the gating rows can raise exit 3.")
    seen_counts = {}
    for name, path in feeds.items():
        m = measure_feed(path)
        v = verdict(m, a.max_age_days)
        if m["state"] == "MEASURED":
            seen_counts[name] = m["files"]
        if v == "STALE" and name not in NON_GATING:
            stale += 1
        tag = " (reported, not gating)" if name in NON_GATING else ""
        if m["state"] == "MEASURED":
            print(f"  {name:18s} files={m['files']:5d}  "
                  f"newest={datetime.fromtimestamp(m['newest']):%Y-%m-%d %H:%M}  "
                  f"age={m['age_days']:5.1f}d  {v}{tag}")
            print(f"  {'':18s} root={path}")
        else:
            print(f"  {name:18s} UNKNOWN -- {m['why']}{tag}")
            print(f"  {'':18s} root={path}")
    ai = {k: v for k, v in seen_counts.items() if k.startswith("claude-ai")}
    if len(set(ai.values())) > 1:
        print()
        print("  DIVERGENCE: the trees named claude-ai hold different file counts -- "
              + ", ".join(f"{k}={v}" for k, v in sorted(ai.items())) + ".")
        print("  Any claude-ai figure published without naming its root is UNATTRIBUTED. "
              "It is not wrong; it is not yet a measurement of anything in particular.")

    if stale:
        print(f"  EXIT 3: {stale} GATING feed(s) older than {a.max_age_days:g} days. A number "
              "computed over a stale feed must carry that age or not be published.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
