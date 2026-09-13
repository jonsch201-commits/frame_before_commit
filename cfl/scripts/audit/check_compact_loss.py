#!/usr/bin/env python3
"""check_compact_loss.py — does the durable capture actually hold everything the live session does?

WHY THIS EXISTS
---------------
Jon: "I should be able to run compact and truly lose nothing." Today that claim is UNVERIFIED.
`pre-compact-su.sh` and `session_store_capture.py --reconcile` both fire on PreCompact and both
WRITE a capture. Nothing afterward ever CHECKS that the capture caught up. Measured 2026-08-14:
live JSONL 33,123,009 B vs captured copy 33,088,863 B -- a 34,146 B delta nobody had reported,
because nothing compares the two after the fact. This is that comparison.

WHAT session_store_capture.py ALREADY GIVES US, REUSED RATHER THAN REBUILT
----------------------------------------------------------------------------
`iter_store()` enumerates every file under the CFL project prefixes in the live store; `classify()`
sorts each into session / subagent / memory / other. This instrument imports both instead of
re-walking the tree with a second, drifting definition of "the CFL store" -- the same discipline
CLAUDE.md names as "derive, don't record": a second hardcoded enumeration is exactly the kind of
fact that goes stale silently.

WHAT THIS INSTRUMENT ADDS
--------------------------
A per-file comparison of live size vs captured size, classified into FOUR buckets using the exact
vocabulary su_close.sh already uses for the working-tree partition (`git.worktree.stranded` /
`git.worktree.inflight`) rather than inventing new words for the same shape of fact:

  MATCH     capture size == live size. Whole, as far as size alone can prove (see LIMITS below).
  INFLIGHT  capture BEHIND live, and the live file GREW during this run's observation window --
            i.e. it is still being written. Physics, not neglect. ADVISORY, never blocks. This is
            su_close's `git.worktree.inflight` shape applied to the JSONL store instead of the
            working tree.
  STRANDED  capture BEHIND live, and the live file did NOT grow during the window -- the session
            producing it is quiescent, so the gap is not explained by "still typing". This is the
            real question: something did not run, or ran and failed. su_close's
            `git.worktree.stranded` shape.
  INVERTED  capture AHEAD of live, or a live file the capture remembers has DISAPPEARED from the
            store entirely. This is the worse case named in the brief: a live JSONL truncated or
            deleted after being captured. `cleanupPeriodDays` has already permanently destroyed
            sessions on this machine (see CLAUDE.md, project_cc-retention-cleanupperioddays) --
            this is the shape that class of loss would leave behind, and it is the one case this
            instrument can catch that a naive "is capture >= live" check would wave through as fine.

TWO-POINT WINDOW, NOT A TIMESTAMP HEURISTIC
--------------------------------------------
STRANDED vs INFLIGHT is decided the same way su_close decides it for the working tree: stat every
live file, sleep briefly (default 1.5s, `--sleep 0` to skip), stat again. A file whose size grew in
that window is unambiguously being written right now. A file that did not grow MAY still belong to
an active-but-paused session -- su_close's own header names this residual explicitly ("an agent
that wrote just before the window opened and stayed idle through it reads STRANDED") and this
instrument inherits the same bias: toward reporting, never toward silently calling it fine.

POSITIVE CONTROL — EVERY RUN, NOT JUST --self-test
-----------------------------------------------------
Copied from check_struck_gates.py's pattern rather than invented fresh: a synthetic divergent pair
is classified in memory on every invocation (no file touched) and the result is printed and
asserted. A checker that has only ever printed a clean result on real data is not known to be able
to report a dirty one; check_struck_gates.py's own header names this: "a checker reporting ZERO
must be shown able to report more." If the control fails, this returns UNKNOWN (exit 2) rather than
publish a number nobody can trust.

LIMITS -- STATED, NOT HIDDEN
-----------------------------
Size equality is NOT a hash proof. A same-size corruption would read MATCH here. This instrument
trusts size because hashing every live JSONL (this session's alone is 33 MB) on every close is
real cost for a check that runs on every su_close; `session_store_capture.py --self-test` already
proves the hash-verified path exists and fires for the CAPTURE side. A same-size divergence is a
gap this instrument cannot see; it is named here so nobody mistakes MATCH for "hashed identical".

NON-DESTRUCTIVE
----------------
Read-only on the live store (only `os.stat`, only via the imported `iter_store`/classify, and this
file contains no `os.remove` / `os.rename` / write of any kind against a live-store path). Its only
write is the report to stdout, plus the routine deposit file the caller directs it to.

Exit: 0 ran clean (STRANDED/INVERTED may be > 0 -- this REPORTS, it never fails the close on them)
      2 could not run at all, or the positive control itself did not fire (UNKNOWN, never a pass)

Usage:
  python scripts/audit/check_compact_loss.py                # real run, report only
  python scripts/audit/check_compact_loss.py --verbose       # per-file lines for STRANDED/INVERTED
  python scripts/audit/check_compact_loss.py --sleep 0       # skip the growth window (fast, INFLIGHT unmeasured)
  python scripts/audit/check_compact_loss.py --self-test     # prove STRANDED and INVERTED can both fire

  # PEER MODE -- run the same instrument against another trunk's store/capture pair:
  python scripts/audit/check_compact_loss.py \
      --capture-root "G:/My Drive/Claude/Claude Personal/raw/transcripts/claude-code/jsonl-mirror" \
      --prefix G--My-Drive-Claude-Claude-Secretary
"""
from __future__ import annotations

import os
import sys
import shutil
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import session_store_capture as ssc  # noqa: E402  -- the store enumeration, reused not rebuilt


# --------------------------------------------------------------------------- pure classifier


def classify_pair(cap_exists, cap_size, live_size, live_grew):
    """The whole decision, as one pure function so it can be unit-tested without touching disk.

    cap_exists  -- capture file present at all
    cap_size    -- captured byte size (ignored if not cap_exists)
    live_size   -- live byte size (None means the live file has disappeared from the store)
    live_grew   -- True if the live file's size increased during this run's observation window
    """
    if live_size is None:
        # The capture remembers a file the live store no longer has. Under the accumulate
        # design (session_store_capture.py's own header: "a file deleted at the source stays
        # here forever") this is EXPECTED for old sessions rotated off disk with a good
        # capture already on file -- but it is INDISTINGUISHABLE, from size alone, from the
        # bad case (deleted before ever being captured completely). Reported as INVERTED
        # either way because "worse case" is the direction to err toward, not a diagnosis.
        return "INVERTED"
    if not cap_exists:
        # Never captured. If it is actively growing this is a brand-new session the capture
        # pipeline has not reached yet -- physics, not neglect. If it is not growing, nothing
        # has captured it and nothing is about to.
        return "INFLIGHT" if live_grew else "STRANDED"
    if cap_size == live_size:
        return "MATCH"
    if cap_size > live_size:
        return "INVERTED"
    return "INFLIGHT" if live_grew else "STRANDED"


# --------------------------------------------------------------------------- positive control


def run_positive_control():
    """Synthesise ONE known-divergent pair per class and assert the classifier catches each.
    Pattern copied from check_struck_gates.py's positive-control block -- run every invocation,
    printed every invocation, never gated behind --self-test."""
    cases = [
        ("match",    classify_pair(True,  100, 100, False), "MATCH"),
        ("inflight", classify_pair(True,   40, 100, True),  "INFLIGHT"),
        ("stranded", classify_pair(True,   40, 100, False), "STRANDED"),
        ("inverted-shrunk", classify_pair(True, 200, 100, False), "INVERTED"),
        ("inverted-deleted", classify_pair(True, 100, None, False), "INVERTED"),
        ("never-captured-quiescent", classify_pair(False, 0, 100, False), "STRANDED"),
        ("never-captured-growing",   classify_pair(False, 0, 100, True),  "INFLIGHT"),
    ]
    ok = all(got == want for _name, got, want in cases)
    return ok, cases


# --------------------------------------------------------------------------- real scan


def stat_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return None


def scan(store_root, capture_root, prefixes, sleep_secs, verbose=False):
    """Full comparison. store_root/capture_root/prefixes are parameters (not the module
    globals) so --self-test can point this at a temp tree without monkeypatching more than
    the three globals iter_store() itself reads."""
    saved = (ssc.STORE_ROOT, ssc.CFL_PROJECT_PREFIXES, ssc.CAPTURE_ROOT)
    ssc.STORE_ROOT, ssc.CFL_PROJECT_PREFIXES, ssc.CAPTURE_ROOT = store_root, prefixes, capture_root
    try:
        live = list(ssc.iter_store())  # (project, relpath, abspath)
        pass1 = {rp: stat_size(ap) for _p, rp, ap in live}
        if sleep_secs > 0:
            time.sleep(sleep_secs)
        pass2 = {}
        for _p, rp, ap in live:
            pass2[rp] = stat_size(ap)

        rows = []
        for _p, rp, ap in live:
            kind = ssc.classify(rp)
            s1, s2 = pass1.get(rp), pass2.get(rp)
            live_size = s2 if s2 is not None else s1
            grew = bool(s1 is not None and s2 is not None and s2 > s1)
            cap_path = os.path.join(capture_root, rp)
            cap_exists = os.path.isfile(cap_path)
            cap_size = stat_size(cap_path) if cap_exists else 0
            status = classify_pair(cap_exists, cap_size or 0, live_size, grew)
            behind_bytes = max(0, (live_size or 0) - (cap_size or 0)) if status in ("INFLIGHT", "STRANDED") else 0
            rows.append({
                "relpath": rp, "kind": kind, "status": status,
                "live_size": live_size, "cap_size": cap_size if cap_exists else None,
                "behind_bytes": behind_bytes,
            })

        # The INVERTED-by-deletion case: a captured file whose live original is simply gone.
        # iter_store() only walks the LIVE tree, so this direction needs a separate pass over
        # the capture tree looking for relpaths with no live counterpart at all.
        # Normalized to "/" on BOTH sides -- the mismatch this fixed: iter_store()'s relpath is
        # native-separator (backslash on Windows) while this loop's os.path.relpath is too, but
        # comparing one normalized and one not made every real file read as its own orphan on
        # first run here. Caught by reading the self-test's actual rows, not the PASS count.
        # ⛔ PREFIX-SCOPED 2026-08-17, and the bug it prevents is not hypothetical. iter_store()
        # scopes the LIVE side to `prefixes`; this walk did not scope the CAPTURE side at all. For
        # CFL that never fired, because CFL's capture root holds only CFL project dirs. Point the
        # same instrument at a SHARED mirror -- the Secretary's capture root is Personal's
        # `jsonl-mirror`, which `[measured 2026-08-17]` holds 12+ project dirs from other trunks --
        # and every one of those trunks' captured files reads as an orphan INVERTED. That would have
        # published a five-figure INVERTED count as "the worse case" when the true finding is
        # "this root serves more than one trunk." Out-of-prefix files are COUNTED and reported, not
        # silently dropped: an ignored file is still a number a reader is owed.
        live_keys = {rp.replace("\\", "/") for _p, rp, _ap in live}
        orphans = []
        out_of_prefix = 0
        if os.path.isdir(capture_root):
            for dirpath, _dn, filenames in os.walk(capture_root):
                if os.sep + "_state" in dirpath or os.sep + "_superseded" in dirpath:
                    continue
                for fn in filenames:
                    ap = os.path.join(dirpath, fn)
                    rp = os.path.relpath(ap, capture_root)
                    key = rp.replace("\\", "/")
                    if key in live_keys:
                        continue
                    if not key.startswith(tuple(prefixes)):
                        out_of_prefix += 1
                        continue
                    orphans.append(key)
                    rows.append({
                        "relpath": key, "kind": ssc.classify(key), "status": "INVERTED",
                        "live_size": None, "cap_size": stat_size(ap), "behind_bytes": 0,
                    })

        scan.last_out_of_prefix = out_of_prefix
        return rows, orphans
    finally:
        ssc.STORE_ROOT, ssc.CFL_PROJECT_PREFIXES, ssc.CAPTURE_ROOT = saved


# --------------------------------------------------------------------------- report


def report(rows, orphans, sleep_secs):
    total = len(rows)
    by_status = {}
    behind_bytes_total = 0
    kinds = {}
    for r in rows:
        by_status.setdefault(r["status"], []).append(r)
        behind_bytes_total += r["behind_bytes"]
        kinds.setdefault(r["kind"], {"seen": 0}).setdefault(r["status"], 0)
        kinds[r["kind"]]["seen"] += 1
        kinds[r["kind"]][r["status"]] = kinds[r["kind"]].get(r["status"], 0) + 1

    n_match = len(by_status.get("MATCH", []))
    n_inflight = len(by_status.get("INFLIGHT", []))
    n_stranded = len(by_status.get("STRANDED", []))
    n_inverted = len(by_status.get("INVERTED", []))
    n_behind = n_inflight + n_stranded

    print("=== check_compact_loss ===")
    print(f"  live store root : {ssc.STORE_ROOT}  (READ-ONLY)")
    print(f"  capture root    : {ssc.CAPTURE_ROOT}")
    print(f"  prefixes        : {', '.join(ssc.CFL_PROJECT_PREFIXES)}")
    print(f"  window          : {sleep_secs}s (STRANDED vs INFLIGHT decided by growth across this window)")
    print(f"  files compared  : {total}")
    print(f"  MATCH           : {n_match} / {total}")
    print(f"  BEHIND (total)  : {n_behind} / {total}  = INFLIGHT {n_inflight} + STRANDED {n_stranded}")
    print(f"    INFLIGHT      : {n_inflight} / {total}  -- capture behind a live, growing file. PHYSICS, non-blocking floor.")
    print(f"    STRANDED      : {n_stranded} / {total}  -- capture behind a QUIESCENT file. Neglect candidate, not physics.")
    print(f"  INVERTED        : {n_inverted} / {total}  -- capture AHEAD of live, or live file gone from the store. WORSE CASE.")
    print(f"  bytes behind (STRANDED+INFLIGHT) : {behind_bytes_total} B")
    print(f"  orphaned captures (no live file, expected under accumulate design) : {len(orphans)}")
    oop = getattr(scan, "last_out_of_prefix", 0)
    print(f"  capture files OUTSIDE the prefixes (other trunks sharing this root, not counted) : {oop}")
    print()
    print(f"  {'kind':<10} {'seen':>6} {'match':>6} {'inflight':>9} {'stranded':>9} {'inverted':>9}")
    for kind in ("session", "subagent", "memory", "other"):
        k = kinds.get(kind)
        if k:
            print(f"  {kind:<10} {k['seen']:>6} {k.get('MATCH',0):>6} {k.get('INFLIGHT',0):>9} "
                  f"{k.get('STRANDED',0):>9} {k.get('INVERTED',0):>9}")

    if n_stranded:
        print(f"\n  STRANDED sites -- capture is behind a QUIESCENT live file:")
        for r in by_status.get("STRANDED", [])[:25]:
            print(f"    {r['relpath']}  live={r['live_size']} cap={r['cap_size']} behind={r['behind_bytes']} B")
        if n_stranded > 25:
            print(f"    ... and {n_stranded - 25} more")

    if n_inverted:
        print(f"\n  INVERTED sites -- capture AHEAD of live, or live file missing:")
        for r in by_status.get("INVERTED", [])[:25]:
            print(f"    {r['relpath']}  live={r['live_size']} cap={r['cap_size']}")
        if n_inverted > 25:
            print(f"    ... and {n_inverted - 25} more")

    print(f"\n  LIMIT: MATCH is a SIZE equality, not a hash proof -- a same-size corruption reads MATCH here.")
    print(f"  LIMIT: STRANDED can include a session that wrote just before the window opened and paused")
    print(f"         during it -- same residual su_close.sh's own git.worktree.stranded row carries.")
    return total, n_match, n_inflight, n_stranded, n_inverted, behind_bytes_total


# --------------------------------------------------------------------------- self-test


def self_test():
    """Prove both failure directions actually fire, on REAL files in a temp tree -- not just the
    pure classify_pair table (that runs unconditionally via run_positive_control anyway)."""
    results = []

    def check(name, ok, detail=""):
        results.append((name, ok, detail))

    tmp = tempfile.mkdtemp(prefix="compact-loss-selftest-")
    store = os.path.join(tmp, "store")
    cap = os.path.join(tmp, "cap")
    proj = os.path.join(store, "FAKE-PROJECT")
    os.makedirs(proj, exist_ok=True)
    os.makedirs(cap, exist_ok=True)
    try:
        # Case A: live AHEAD of capture, quiescent (no growth) -> STRANDED. This is the brief's
        # required demo: "construct a case where a live JSONL is ahead of its capture and
        # demonstrate the check reporting it."
        a_live = os.path.join(proj, "aaaaaaaa-stranded.jsonl")
        with open(a_live, "wb") as fh:
            fh.write(b"x" * 1000)
        a_cap = os.path.join(cap, "FAKE-PROJECT", "aaaaaaaa-stranded.jsonl")
        os.makedirs(os.path.dirname(a_cap), exist_ok=True)
        with open(a_cap, "wb") as fh:
            fh.write(b"x" * 400)

        # Case B: capture AHEAD of live -- the worse case (truncation/shrink signature).
        b_live = os.path.join(proj, "bbbbbbbb-inverted.jsonl")
        with open(b_live, "wb") as fh:
            fh.write(b"y" * 100)
        b_cap = os.path.join(cap, "FAKE-PROJECT", "bbbbbbbb-inverted.jsonl")
        with open(b_cap, "wb") as fh:
            fh.write(b"y" * 900)

        # Case C: a full match, for a negative control on the report itself.
        c_live = os.path.join(proj, "cccccccc-match.jsonl")
        with open(c_live, "wb") as fh:
            fh.write(b"z" * 250)
        c_cap = os.path.join(cap, "FAKE-PROJECT", "cccccccc-match.jsonl")
        with open(c_cap, "wb") as fh:
            fh.write(b"z" * 250)

        # Case D: a live file the capture has no record of at all, and it is NOT growing during
        # the window -- never-captured + quiescent -> STRANDED (nothing will catch it up).
        d_live = os.path.join(proj, "dddddddd-nevercaptured.jsonl")
        with open(d_live, "wb") as fh:
            fh.write(b"w" * 300)

        rows, orphans = scan(store, cap, ("FAKE",), sleep_secs=0.05)
        by_rel = {r["relpath"]: r for r in rows}

        st_a = by_rel.get("FAKE-PROJECT/aaaaaaaa-stranded.jsonl") or by_rel.get("FAKE-PROJECT\\aaaaaaaa-stranded.jsonl")
        check("live-ahead-of-capture (quiescent) reads STRANDED, not clean",
              bool(st_a) and st_a["status"] == "STRANDED",
              f"got {st_a}")

        st_b = by_rel.get("FAKE-PROJECT/bbbbbbbb-inverted.jsonl") or by_rel.get("FAKE-PROJECT\\bbbbbbbb-inverted.jsonl")
        check("capture-ahead-of-live reads INVERTED (the worse case)",
              bool(st_b) and st_b["status"] == "INVERTED",
              f"got {st_b}")

        st_c = by_rel.get("FAKE-PROJECT/cccccccc-match.jsonl") or by_rel.get("FAKE-PROJECT\\cccccccc-match.jsonl")
        check("identical sizes read MATCH",
              bool(st_c) and st_c["status"] == "MATCH",
              f"got {st_c}")

        st_d = by_rel.get("FAKE-PROJECT/dddddddd-nevercaptured.jsonl") or by_rel.get("FAKE-PROJECT\\dddddddd-nevercaptured.jsonl")
        check("never-captured + quiescent reads STRANDED",
              bool(st_d) and st_d["status"] == "STRANDED",
              f"got {st_d}")

        # Case E: a growing file -- prove INFLIGHT actually fires and is distinguished from
        # STRANDED, not just declared.
        e_live = os.path.join(proj, "eeeeeeee-inflight.jsonl")
        with open(e_live, "wb") as fh:
            fh.write(b"v" * 100)

        def grow_after_delay():
            time.sleep(0.05)
            with open(e_live, "ab") as fh:
                fh.write(b"v" * 500)

        import threading
        th = threading.Thread(target=grow_after_delay)
        th.start()
        rows2, _ = scan(store, cap, ("FAKE",), sleep_secs=0.2)
        th.join()
        by_rel2 = {r["relpath"]: r for r in rows2}
        st_e = by_rel2.get("FAKE-PROJECT/eeeeeeee-inflight.jsonl") or by_rel2.get("FAKE-PROJECT\\eeeeeeee-inflight.jsonl")
        check("a file that GROWS during the window reads INFLIGHT, not STRANDED",
              bool(st_e) and st_e["status"] == "INFLIGHT",
              f"got {st_e}")

        # Positive control table itself.
        ok, cases = run_positive_control()
        check("positive control table (7 synthetic pairs, in-memory) all classify correctly",
              ok, str([(n, g, w) for n, g, w in cases if g != w]))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=== check_compact_loss self-test ===")
    for name, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if (detail and not ok) else ""))
    passed = sum(1 for _n, ok, _d in results if ok)
    print(f"\nRESULT: {passed}/{len(results)} PASS")
    return 0 if passed == len(results) else 1


# --------------------------------------------------------------------------- main


def main(argv):
    if "--self-test" in argv:
        return self_test()

    verbose = "--verbose" in argv
    sleep_secs = 1.5
    if "--sleep" in argv:
        try:
            sleep_secs = float(argv[argv.index("--sleep") + 1])
        except (IndexError, ValueError):
            sleep_secs = 1.5

    # PEER MODE, added 2026-08-17 for the Secretary's accepted request. Deliberately NOT a second
    # script: a peer driver would be a second enumeration of "the store", which is the drift this
    # instrument's own header refuses ("derive, don't record"). Same scan(), same classifier, same
    # positive control -- only the three roots move.
    def _opt(flag, default):
        if flag in argv:
            try:
                return argv[argv.index(flag) + 1]
            except IndexError:
                return default
        return default

    ssc.STORE_ROOT = _opt("--store-root", ssc.STORE_ROOT)
    ssc.CAPTURE_ROOT = _opt("--capture-root", ssc.CAPTURE_ROOT)
    prefix_arg = _opt("--prefix", None)
    if prefix_arg:
        ssc.CFL_PROJECT_PREFIXES = tuple(p for p in prefix_arg.split(",") if p)

    ok, cases = run_positive_control()
    print("=== check_compact_loss: positive control (every run, in-memory synthetic pairs) ===")
    for name, got, want in cases:
        mark = "PASS" if got == want else "FAIL"
        print(f"  [{mark}] {name}: classifier said {got}, expected {want}")
    if not ok:
        print("\n  POSITIVE CONTROL FAILED -- the classifier cannot be trusted to report a real", file=sys.stderr)
        print("  divergence. Treat every number below as UNKNOWN, not clean.", file=sys.stderr)
        # Still run and print the real scan for a human to look at, but the exit code says UNKNOWN.
        control_rc = 2
    else:
        control_rc = 0
    print()

    if not os.path.isdir(ssc.STORE_ROOT):
        print(f"UNKNOWN: live store root not found: {ssc.STORE_ROOT}", file=sys.stderr)
        return 2

    rows, orphans = scan(ssc.STORE_ROOT, ssc.CAPTURE_ROOT, ssc.CFL_PROJECT_PREFIXES, sleep_secs, verbose=verbose)
    total, n_match, n_inflight, n_stranded, n_inverted, behind_bytes = report(rows, orphans, sleep_secs)

    if total == 0:
        print("\nUNKNOWN: 0 live files found under the CFL prefixes -- empty denominator, not a pass.", file=sys.stderr)
        return 2

    return control_rc  # report-only: STRANDED/INVERTED > 0 is a finding, never a failing exit


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
