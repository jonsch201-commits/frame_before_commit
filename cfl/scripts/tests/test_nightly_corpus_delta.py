#!/usr/bin/env python3
"""Watermark-safety tests for scripts/lanes/nightly_corpus_delta.py.

Run: python scripts/tests/test_nightly_corpus_delta.py   (no pytest dependency)

Each case states what the OLD blanket post-run rescan would have absorbed versus what the new
verified-advance does, because the whole point of the change is that the difference is invisible in
a green exit code. `old_behaviour` below is a faithful one-line model of the replaced code:

    post, _ = leg1_manifest(); write_snapshot(post)     # absorb everything that exists
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "ncd", ROOT / "scripts" / "lanes" / "nightly_corpus_delta.py")
ncd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ncd)

FAILURES = []


def check(name, got, want):
    if got == want:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}\n        got  {got}\n        want {want}")
        FAILURES.append(name)


def old_behaviour(post):
    """The replaced logic: advance to a post-run full rescan, unconditionally."""
    return dict(post)


def test_cap_overflow_is_deferred_not_absorbed():
    """30 sessions appear; the 25-session cap means 5 never entered the prompt at all.

    OLD: all 30 land in the snapshot -> the 5 are permanently below the watermark, never converted,
    and the spec's "overflow re-triggers next night" was false. NEW: the 5 are never verified, so
    they keep their (absent) prev value and re-trigger.
    """
    prev = {}
    delta = [f"{i:06x}" for i in range(30)]
    post = {u: 10 for u in delta}
    pending = set(delta[25:])            # extractor still wants these 5
    nxt, verified, deferred, _ = ncd.advance_snapshot(prev, post, delta, pending, own6=None)

    check("cap: old would absorb all 30", len(old_behaviour(post)), 30)
    check("cap: new advances over 25", len(verified), 25)
    check("cap: new defers 5", sorted(deferred), sorted(delta[25:]))
    check("cap: deferred stay out of snapshot", [u for u in delta[25:] if u in nxt], [])


def test_green_exit_that_converted_nothing_advances_nothing():
    """Leg 2 returns is_error=false but converted nothing (permission block, model gave up, wrote a
    PR with no content). This is the manufactured-coverage case."""
    prev = {"aaaaaa": 5}
    delta = ["bbbbbb", "cccccc"]
    post = {"aaaaaa": 5, "bbbbbb": 12, "cccccc": 7}
    pending = {"bbbbbb", "cccccc"}       # extractor says: still unconverted
    nxt, verified, deferred, _ = ncd.advance_snapshot(prev, post, delta, pending, own6=None)

    check("green-but-empty: old would absorb both", len(old_behaviour(post)), 3)
    check("green-but-empty: new verifies none", verified, [])
    check("green-but-empty: new defers both", sorted(deferred), ["bbbbbb", "cccccc"])
    check("green-but-empty: snapshot unchanged", nxt, prev)


def test_grown_session_only_advances_when_reconverted():
    """A grown session already has markdown, so mere file existence proves nothing."""
    prev = {"dddddd": 100}
    post = {"dddddd": 250}
    nxt, verified, deferred, _ = ncd.advance_snapshot(
        prev, post, ["dddddd"], pending={"dddddd"}, own6=None)
    check("grown: unrefreshed stays at old count", nxt["dddddd"], 100)
    check("grown: unrefreshed is deferred", deferred, ["dddddd"])

    nxt2, verified2, deferred2, _ = ncd.advance_snapshot(
        prev, post, ["dddddd"], pending=set(), own6=None)
    check("grown: refreshed advances to new count", nxt2["dddddd"], 250)
    check("grown: refreshed is verified", verified2, ["dddddd"])


def test_own_session_is_absorbed_so_a_quiet_corpus_settles():
    """Requirement (b): without this the lane converts its own session, which makes another
    session, and the lane fires nightly forever on a quiet corpus."""
    prev = {"aaaaaa": 5}
    delta = ["bbbbbb"]
    post = {"aaaaaa": 5, "bbbbbb": 12, "9f9f9f": 4}   # 9f9f9f = the lane's own headless session
    nxt, verified, deferred, absorbed = ncd.advance_snapshot(
        prev, post, delta, pending=set(), own6="9f9f9f")
    check("own: absorbed", absorbed, ["9f9f9f"])
    check("own: in next snapshot", nxt.get("9f9f9f"), 4)
    check("own: delta still verified normally", verified, ["bbbbbb"])

    # ...and the next night it is no longer a delta, so the lane goes SILENT.
    new2, grown2 = ncd.compute_delta(nxt, post)
    check("own: quiet corpus settles to no delta", (new2, grown2), ([], []))


def test_concurrent_session_is_not_absorbed():
    """A session that merely started while the lane was running is NOT self-caused. The old rescan
    swept these in — a real hazard on the catch-up path, which can fire at logon while Jon works."""
    prev = {"aaaaaa": 5}
    post = {"aaaaaa": 5, "bbbbbb": 12, "9f9f9f": 4, "j0nj0n": 60}   # j0nj0n = Jon, concurrently
    nxt, _, _, absorbed = ncd.advance_snapshot(
        prev, post, ["bbbbbb"], pending=set(), own6="9f9f9f")
    check("concurrent: old would absorb Jon's session", "j0nj0n" in old_behaviour(post), True)
    check("concurrent: new does not", "j0nj0n" in nxt, False)
    check("concurrent: only own session absorbed", absorbed, ["9f9f9f"])


def test_corrupt_snapshot_halts_and_absent_baselines():
    with tempfile.TemporaryDirectory() as d:
        ncd.SNAPSHOT = Path(d) / "snapshot.json"
        ncd.STATE_DIR = Path(d)
        check("snapshot: absent -> 'absent'", ncd.load_snapshot()[1], "absent")

        ncd.write_snapshot({"aaaaaa": 1})
        check("snapshot: round-trips", ncd.load_snapshot()[0], {"aaaaaa": 1})
        check("snapshot: no .tmp left behind",
              [p.name for p in Path(d).glob("*.tmp")], [])

        ncd.SNAPSHOT.write_text('{"aaaaaa": 1', encoding="utf-8")   # truncated mid-write
        data, status = ncd.load_snapshot()
        check("snapshot: truncated -> not first-run", data, None)
        check("snapshot: truncated -> corrupt", status.startswith("corrupt:"), True)

        ncd.SNAPSHOT.write_text('["not", "an", "object"]', encoding="utf-8")
        check("snapshot: wrong shape -> corrupt", ncd.load_snapshot()[1].startswith("corrupt:"),
              True)


def test_raw_is_never_stageable_and_prompt_no_longer_asks_for_it():
    check("fence: raw/ force-add denied", "Bash(git add -f *)" in ncd.DENIED_TOOLS, True)
    check("fence: raw/ long-form force-add denied",
          "Bash(git add --force *)" in ncd.DENIED_TOOLS, True)
    check("fence: any git add naming raw/ denied", "Bash(git add *raw/*)" in ncd.DENIED_TOOLS, True)
    check("fence: sys prompt forbids staging raw/", "NEVER stage, add, or force-add anything "
          "under raw/" in ncd.SYS_PROMPT, True)
    check("fence: sys prompt still single-line (rides argv)", "\n" in ncd.SYS_PROMPT, False)
    prompt = ncd.build_prompt("Corpus delta: 1 new")
    check("fence: prompt no longer asks for raw/ markdown in the PR",
          "with the new raw/ markdown" in prompt, False)
    check("fence: prompt says raw/ must not be staged", "MUST NOT be staged" in prompt, True)


def test_dryrun_regex_matches_extractor_output():
    sample = ("Discovered 3 project dir(s):\n"
              "  [EXTRACT] a1b2c3  (new)  project=fl\n"
              "  [REFRESH] d4e5f6  (jsonl newer than md (grew/changed))  project=triage\n"
              "  1a2b3c   42 msgs  2026-07-25 03:00  md_ok  fl  Some title\n")
    got = {m.group(1) for m in (ncd.DRYRUN_RE.match(l) for l in sample.splitlines()) if m}
    check("dryrun regex: picks up EXTRACT+REFRESH only", got, {"a1b2c3", "d4e5f6"})


if __name__ == "__main__":
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_")]:
        print(f"\n{fn.__name__}")
        fn()
    print(f"\n{'FAILED: ' + ', '.join(FAILURES) if FAILURES else 'All checks passed.'}")
    sys.exit(1 if FAILURES else 0)
