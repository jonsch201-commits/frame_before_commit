#!/usr/bin/env python3
"""postcompact_pipeline.py — CFL's ordered post-compact pipeline (JON-ORDER-2, 2026-09-01).

Jon, verbatim: "One script, ordered: render md -> ingest wiki -> rebuild index -> regen
brief -> extract rulings -> reconcile registry -> write lineage row -> stamp liveness ->
verify summary vs tail -> write POSTCOMPACT-STATUS.md with per-step PASS/FAIL."

Secretary's four implementation rules, adopted verbatim:
  1. SKIPPED-NOT-OWNED / SKIPPED-NOT-BUILT is never a PASS — a red exists.
  2. NO STEP BLOCKS — this script always exits 0; the VERDICT lives in the STATUS file.
  3. STAGE, NEVER PUBLISH — nothing here writes wiki pages.
  4. Read from N:/local mirrors where they exist; a killed Drive scan prints the same
     bytes as a clean zero.

CFL mapping (steps run the instruments that already exist; absent ones report red):
  0 capture fired    -> structural compact_boundary count in the session jsonl vs PreCompact
                        receipts (ADDED 2026-09-04 on soul's question: this pipeline could not
                        tell "nothing new to index" from "the capture never ran", and both
                        rendered as a quiet PASS). Substring scans do NOT work here -- a naive
                        one returned 13 against 8, the extra five being this session's own
                        transcript discussing the token.
  1 render md        -> auto_mint_windows.py (mint_window.py sole emitter)
  2 ingest wiki      -> main_thread_ingest.py --session <sid>  (BUILT 2026-09-04; was
                        hardcoded SKIPPED for months and is why 2026-09 read 0.0% covered)
  3 rebuild index    -> RUNS build_index.py --quiet --include exchange (CORRECTED 2026-09-04;
                        was an AGE REPORT that never rebuilt, justified by a "700s rebuild"
                        that is the --force cost -- incremental is idempotent-by-content-hash
                        and measured 37s, 63s with exchange). --include exchange is LOAD-BEARING:
                        the default walk excludes exchange/ and build_index DELETES rows the walk
                        no longer reaches, so without it every compact deleted what step 10's
                        drain had just added.
  4 regen brief      -> SKIPPED-NOT-OWNED (CFL has no hourly brief; the pulse is the beat)
  5 extract rulings  -> newest window's Human-turn count reported (verbatim turns ARE in the
                        window by mint_window construction; extraction-to-rulings/ not built)
  6 reconcile registry -> SKIPPED-NOT-BUILT (rides RP-6/RP-22)
  7 lineage row      -> evidence/session-lineage.jsonl append: session, parent, resume line
  8 stamp liveness   -> ages computed at READ time (newest receipt, newest window, index)
  9 summary vs tail  -> postcompact_verify artifact presence + its finding count
  10 index drain     -> index_queue_drain.py (GR-1: drains exchange/su-close/INDEX-QUEUE.jsonl
                        into the graphrag index; added 2026-09-02, R-3/R-4)

Usage: postcompact_pipeline.py [--session <uuid>] ; always exits 0.
"""
import atexit
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runlock import runlock, STATE as STATE_DIR  # noqa: E402  (one writer of POSTCOMPACT-STATUS.md; see runlock.py)
from session_parent import derive as _parent_of  # noqa: E402  (step 7's parent was hardcoded)
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "exchange" / "su-close" / "POSTCOMPACT-STATUS.md"
LINEAGE = ROOT / "evidence" / "session-lineage.jsonl"
# ⛔ ONE HOME FOR THE GRAPH. This file hardcoded %LOCALAPPDATA%/claude/graphrag and would NOT
# have followed CFL_GRAPHRAG_HOME -- [measured 2026-09-12 23:1x] seven scripts had that bug,
# so setting the variable would have pointed the BUILDER at a new disk while every READER
# stayed on the old one, each reporting success. See scripts/lib/graphrag_home.py.
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "lib"))
from graphrag_home import DB as _GRAPHRAG_DB  # noqa: E402
IDX = _GRAPHRAG_DB


def run(cmd):
    try:
        # encoding pinned: text=True decodes with the LOCALE codec (cp1252 on this
        # machine), so a child's UTF-8 em-dash landed in the graded note as "â€”"
        # (measured 2026-09-04 19:31, step 2). Same family as the wake command's
        # wc -c-never-len() rule: multi-byte bytes read through a single-byte lens.
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=600, cwd=ROOT)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return -1, f"EXC {e}"


def silent_ok(rc, out):
    """WW-2, 2026-09-05 — TRUE when a child exited 0 and emitted NOTHING: that is UNKNOWN.

    Step 2 graded `main_thread_ingest exit=0: no output` as FAIL. Run standalone the same
    minute, the identical command printed "1 written -- 81 Jon utterance(s), 65 anchored,
    6541 turns" and exited 0. So the FAIL was a statement about the RUN, not about ingest.

    ⛔ This trunk already carries the law, from the 2026-09-01 Drive EINVAL hour: a script
    reading an unreadable file exits 0 with 0 bytes, while a MISSING file exits 2 -- so
    every exit-code gate reads GREEN while the disk is dead. Exit-0-and-empty is UNKNOWN.
    UNKNOWN still dominates a PASS, so nothing here weakens the VERDICT; it stops the
    pipeline from naming an innocent step as the defect.
    """
    return rc == 0 and not (out or "").strip()


def _boundary_record_pending(sess):
    """True when the NEWEST PreCompact receipt has no compact_boundary record in the session jsonl
    yet -- the fixed-order state at the SessionStart:compact wiring. grade_step0 tests the other
    direction (every boundary has a receipt) and PASSES here, because the three EARLIER compacts in
    this session do have theirs; that is why the step-0 verdict alone could not discriminate, and
    [measured 2026-09-12 20:48] it graded PASS while step 9 graded FAIL at the same firing.
    Returns False -- never 'pending' -- whenever the jsonl cannot be read, so an unreadable
    instrument can only make this STRICTER, never quieter."""
    try:
        _jp = Path.home() / ".claude" / "projects" / "N--claude-cfl-clone" / (sess + ".jsonl")
        _recs = sorted((ROOT / "exchange" / "su-close" / "precompact").glob("*.md"))
        if not _jp.is_file() or not _recs:
            return False
        _newest = datetime.strptime(_recs[-1].name.split("-")[0], "%Y%m%dT%H%M%S")
        with open(_jp, encoding="utf-8", errors="replace") as _f:
            for _line in _f:
                if "compact_boundary" not in _line:
                    continue
                try:
                    _r = json.loads(_line)
                except Exception:
                    continue
                if _r.get("type") != "system" or _r.get("subtype") != "compact_boundary":
                    continue
                try:
                    _t = datetime.strptime(_r.get("timestamp", "")[:19], "%Y-%m-%dT%H:%M:%S") - timedelta(hours=5)
                except Exception:
                    continue
                if 0 <= (_t - _newest).total_seconds() <= 900:
                    return False   # the record for THIS boundary is already there
        return True
    except Exception:
        return False


def grade_step0(sess):
    try:
        _jp = (Path.home() / ".claude" / "projects" / "N--claude-cfl-clone" / (sess + ".jsonl"))
        if not _jp.is_file():
            return (("0 capture fired", "UNKNOWN",
                         f"no session jsonl for {sess[:8]} -- cannot tell 'nothing new' from "
                         f"'capture never ran'"))
        else:
            _b = []
            with open(_jp, encoding="utf-8", errors="replace") as _f:
                for _line in _f:
                    if "compact_boundary" not in _line:
                        continue
                    try:
                        _r = json.loads(_line)
                    except Exception:
                        continue
                    if _r.get("type") == "system" and _r.get("subtype") == "compact_boundary":
                        _b.append(_r.get("timestamp", ""))
            _recs = sorted((ROOT / "exchange" / "su-close" / "precompact").glob("*.md"))
            _missing = 0
            for _ts in _b:
                try:
                    _t = datetime.strptime(_ts[:19], "%Y-%m-%dT%H:%M:%S") - timedelta(hours=5)
                except Exception:
                    continue
                _near = False
                for _rf in _recs:
                    try:
                        _d = datetime.strptime(_rf.name.split("-")[0], "%Y%m%dT%H%M%S")
                    except Exception:
                        continue
                    if 0 <= (_t - _d).total_seconds() <= 900:
                        _near = True
                        break
                if not _near:
                    _missing += 1
            if not _b:
                return (("0 capture fired", "UNKNOWN",
                             "no compact_boundary records in this session's jsonl yet -- "
                             "nothing to attest, which is NOT the same as a clean capture"))
            elif _missing:
                return (("0 capture fired", "FAIL",
                             f"{_missing} of {len(_b)} compact boundaries have NO PreCompact "
                             f"receipt within 15 min -- the capture did not run, so any 'nothing "
                             f"new to index' below is UNKNOWN, not clean"))
            else:
                return (("0 capture fired", "PASS",
                             f"{len(_b)} compact boundaries, {len(_b)} with a PreCompact receipt "
                             f"(structural subtype test, not a substring scan)"))
    except Exception as _e:
        return (("0 capture fired", "UNKNOWN", f"{_e.__class__.__name__} -- not a pass"))

def grade_step9(receipts, _sess_for_order=None):
    """WW-1c, 2026-09-12. The step-0 tuple is a SECOND, INDEPENDENT METHOD for the one cause the
    old message could not name. `late_regrade`'s own docstring says the fixed order "reads as a
    flake forever, and a flake gets ignored" -- and the fix it shipped patched the FILE at the
    second wiring while THE BANNER THE SEAT READS still said FAIL. [measured 2026-09-12 20:48/20:50,
    this session: the SessionStart:compact banner reached the seat's context as
    "POSTCOMPACT-STATUS: FAIL ... reds: 4 regen brief; 6 reconcile registry; 9 summary vs tail",
    and the 20:50:32 late-regrade wrote PASS-WITH-SKIPS to disk where nothing makes the seat
    re-read it.] Annotation is not a disposition (CLAUDE.md).
    THE DISCRIMINATOR (_boundary_record_pending): at the first wiring the compact_boundary record
    for the NEWEST receipt is not in the JSONL yet. A CRASH looks different -- the boundary record is
    there and the artifact is not. Two signals, one from the JSONL and one from the artifact tree,
    so a missing artifact is a claim about an instrument until the second method agrees (Rule 15).
    When they agree the row is SKIPPED-PENDING-ORDER: an UNKNOWN-class state that never reads as a
    pass and never cries wolf, and that the second wiring clears."""
    _pre = _boundary_record_pending(_sess_for_order) if _sess_for_order else False
    _pending = ("9 summary vs tail", "SKIPPED-PENDING-ORDER",
                "the compact_boundary record for THIS boundary is not in the jsonl yet, so "
                "this is the FIXED ORDER and not a crash: the verify artifact is written at the "
                "first post-compact turn, after this wiring runs. The PostCompact wiring re-grades "
                "this row ~60s from now (WW-1b). NOT a pass -- UNKNOWN dominates.")
    pc = ROOT / "exchange" / "su-close" / "postcompact"
    arts = sorted(pc.glob("2*.md")) if pc.is_dir() else []
    if arts:
        # freshness bound: an artifact older than the newest receipt means the verifier
        # crashed at THIS compact and this step is grading a stale run (first real firing
        # 2026-09-01: read PASS off a 6-hour-old artifact past an OSError-22 crash)
        stale = bool(receipts) and arts[-1].stat().st_mtime < receipts[-1].stat().st_mtime
        head = arts[-1].read_text(encoding="utf-8", errors="replace")[:400]
        m = re.search(r"VERDICT: (\w+)(?: \((\d+)\))?", head)
        if stale and _pre:
            return _pending
        if stale:
            return (("9 summary vs tail", "FAIL",
                         f"newest artifact {arts[-1].name} PREDATES newest receipt -- the verifier had not written "
                         f"when this step ran: a crash (check LOCALAPPDATA/claude/postcompact-fallback) OR the "
                         f"parallel-hook race measured 2026-09-01 23:00 (two PostCompact entries ran concurrently; "
                         f"chained into one entry the same night, so a recurrence is a crash)"))
        else:
            return (("9 summary vs tail", "PASS", f"{arts[-1].name}: {m.group(0) if m else 'artifact present'} (findings are report, not block)"))
    elif _pre:
        return _pending
    else:
        return (("9 summary vs tail", "FAIL", "no postcompact_verify artifact"))


def late_regrade(sess, boundary):
    """WW-1b, 2026-09-05 22:5x. WW-1's dedupe keyed on the boundary and skipped the SECOND wiring.
    [measured this compact, session 46276084] the FIRST wiring (SessionStart:compact) started 22:36:03;
    the compact_boundary JSONL record was appended 22:39:28 and the PostCompact verify artifact written
    22:39:25 -- both at the FIRST POST-COMPACT TURN, i.e. after the only grading run had already graded
    step 0 (UNKNOWN: no boundary record yet) and step 9 (FAIL: artifact predates receipt, "crash OR race").
    Neither was a crash and neither was a race: it is a fixed ORDER, and the dedupe turned two contradictory
    tables into one table with two reds that can never clear -- a detector whose failure message enumerates a
    closed set of causes and omits the one that is always true reads as a flake forever, and a flake gets
    ignored (Herald, 22:43). So the second wiring re-grades ONLY the two ordering-sensitive steps and patches
    those rows in place -- the expensive steps (189 s index rebuild) stay deduped, one writer still holds the
    lock, and the patch is announced in the file, never silent."""
    try:
        text = STATUS.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"POSTCOMPACT-STATUS: late-regrade SKIPPED -- cannot read {STATUS}: {e}")
        return 0
    m = re.search(r"^# POSTCOMPACT-STATUS — \S+ session (\S+)", text, re.M)
    if not m or not sess.startswith(m.group(1)):
        print(f"POSTCOMPACT-STATUS: late-regrade REFUSED -- status on disk is for session "
              f"{m.group(1) if m else '?'}, this run is {sess[:8]}; not patching another session's verdict")
        return 0
    receipts = sorted((ROOT / "exchange" / "su-close" / "precompact").glob("*.md"))
    new = {"0 capture fired": grade_step0(sess), "9 summary vs tail": grade_step9(receipts, sess)}
    row_re = re.compile(r"^\| ([^|]*?) \| (\S+) \| (.*) \|$")
    out, rows = [], []
    for ln in text.split("\n"):
        mm = row_re.match(ln)
        if mm and mm.group(1).strip() in new:
            s, v, n = new[mm.group(1).strip()]
            ln = f"| {s} | {v} | {n} |"
            mm = row_re.match(ln)
        if mm and mm.group(1).strip() != "step":
            rows.append((mm.group(1).strip(), mm.group(2).strip()))
        out.append(ln)
    verdict = "FAIL" if any(v == "FAIL" for _, v in rows) else (
        "PASS-WITH-SKIPS" if any(v.startswith("SKIPPED") or v == "UNKNOWN" for _, v in rows) else "PASS")
    reds = [n for n, v in rows if v == "FAIL" or v.startswith("SKIPPED") or v == "UNKNOWN"]
    text2 = "\n".join(out)
    text2 = re.sub(r"^VERDICT: \S+", f"VERDICT: {verdict}", text2, count=1, flags=re.M)
    text2 = re.sub(r"^reds: .*$", ("reds: " + "; ".join(reds)) if reds else "reds: none", text2, count=1, flags=re.M)
    stamp = datetime.now().isoformat(timespec="seconds")
    text2 = text2.replace("\n| step | verdict | note |",
        f"\nlate-regrade: steps 0 and 9 re-graded {stamp} by the PostCompact wiring for boundary {boundary} "
        f"(the SessionStart:compact wiring runs BEFORE the compact_boundary record and the verify artifact "
        f"exist -- a fixed order, not a crash; WW-1b)\n\n| step | verdict | note |", 1)
    STATUS.write_text(text2, encoding="utf-8")
    print(f"POSTCOMPACT-STATUS: late-regrade {verdict} -> {STATUS.relative_to(ROOT)}"
          + (("  reds: " + "; ".join(reds)) if reds else ""))
    for s, v, n in new.values():
        print(f"  {v:20s} {s}")
    return 0


def main():
    t0 = datetime.now().timestamp()
    now = datetime.now()
    sess = None
    if "--session" in sys.argv:
        sess = sys.argv[sys.argv.index("--session") + 1]
    if not sess:
        # the hook payload on stdin carries session_id; env does NOT (first real firing
        # 2026-09-01 19:33 recorded "unknown" and a useless `claude --resume unknown` line)
        try:
            if not sys.stdin.isatty():
                sess = (json.load(sys.stdin) or {}).get("session_id")
        except Exception:
            pass
    if not sess:
        sess = os.environ.get("CLAUDE_SESSION_ID", "unknown")

    # ⛔ ONE WRITER OF THE VERDICT FILE. settings.json wires this script on PostCompact AND on
    # SessionStart(compact|clear); a compact fires BOTH, and on 2026-09-04 21:2x the two instances
    # raced and printed CONTRADICTORY tables in the same minute -- step 2 PASS/FAIL and step 9
    # FAIL/PASS, neither table saying a second run existed. The copy left on disk was whichever
    # finished last, which was not the copy on Jon's screen. Both wirings are KEPT (PostCompact does
    # not cover `clear`); the arbitration is the fix. See scripts/audit/runlock.py.
    _lk = runlock("postcompact_pipeline").acquire()
    if not _lk.acquired:
        print("POSTCOMPACT-STATUS: " + _lk.reason)
        return 0  # rule 2: no step blocks -- and a loser writes NOTHING

    # ⛔ REGISTER THE RELEASE THE INSTANT THE LOCK IS HELD, BEFORE ANY OTHER EXIT PATH EXISTS.
    # The WW-1 boundary check below returns early, and in its first version it sat AHEAD of the
    # atexit registration further down -- so a legitimate skip LEAKED THE LOCK and the very next
    # invocation was refused with "another postcompact_pipeline is already running", naming a pid
    # that had exited. [Caught 2026-09-05 by this fix's own NEGATIVE CONTROL, not by its success
    # path: run 1 graded, run 2 skipped correctly, and run 3 -- the control asserting a NEW
    # boundary still grades -- was the one that failed.] ⭐ A dedupe whose skip disables the next
    # real run is strictly worse than the duplication it removes: it converts noise into silence.
    atexit.register(_lk.release)

    # ⛔ WW-1, 2026-09-05 — THE 09-04 ARBITRATION ABOVE PREVENTS OVERLAP, NOT REPETITION, AND THE
    # RACE IT WAS BUILT FOR CAME BACK WEARING A CLOCK. The lock releases at exit (atexit, just
    # below); the second wiring fires ~60s later, acquires cleanly, and re-grades the same compact.
    #
    # [measured 2026-09-05] evidence/session-lineage.jsonl carries TWO rows per boundary, 60s
    # apart -- 14:43:37 and 14:44:37 for one compact, and 14:10:33 / 14:11:34 for the one before.
    # Jon saw the consequence directly: run A graded FAIL 2 / PASS 9, run B graded PASS 2 / FAIL 9,
    # and he read it as "a lot of thngs didn't work". NEITHER RED WAS REAL.
    #
    # ⭐ THE KEY IS THE BOUNDARY, NOT THE PROCESS. Exactly one PreCompact receipt exists per
    # compact, so its filename IS the boundary id -- derived from an artifact the compact itself
    # produced, never a counter this script maintains ([[derive-dont-record]]).
    # ⚠️ A SKIP HERE IS ANNOUNCED, never silent: an unexplained missing run is the very class
    # this pipeline exists to end, and a quiet dedupe is indistinguishable from a dead hook.
    _boundary = "no-receipt"
    try:
        _recs = sorted((ROOT / "exchange" / "su-close" / "precompact").glob("*.md"))
        if _recs:
            _boundary = _recs[-1].stem
    except OSError:
        pass
    _stamp = Path(STATE_DIR) / f"postcompact-graded-{_boundary}.stamp"
    if _boundary != "no-receipt" and _stamp.exists():
        print(f"POSTCOMPACT-STATUS: SKIPPED-ALREADY-GRADED — boundary {_boundary} was graded by "
              f"pid {_stamp.read_text(encoding='utf-8', errors='replace').strip()[:60]}; "
              f"this is the second wiring firing for one compact, not a missing run. "
              f"Verdict on disk is UNCHANGED (see {STATUS}).")
        return late_regrade(sess, _boundary)  # WW-1b: re-grade the two ordering-sensitive steps only
    _stamp_path = _stamp  # written only after a full run, at the bottom of main()
    # (The original atexit registration lived HERE, below the early-return path added above; it has
    # moved up to immediately after acquire(). atexit, not a finally: main() has several exit paths
    # and a leaked lock would skip the NEXT compact, turning this fix into a bigger outage than the
    # race. The 900s steal is the backstop under the backstop, because a wedged pipeline is silent.)
    rows = []
    if _lk.stole or _lk.reason:
        rows.append(("- run lock", "UNKNOWN", _lk.reason.replace("|", "/")[:150]))

    # STEP 0 — DID THE CAPTURE EVEN FIRE? Added 2026-09-04 on soul's (Claude Personal) question,
    # which this pipeline could not answer: "does your PostCompact step have any way to tell
    # 'there was nothing new to index' from 'the capture that should have produced something did
    # not run'?" It could not, and the two look IDENTICAL from here -- both are a quiet PASS.
    #
    # ⛔ THIS IS NOT HYPOTHETICAL. Herald (Personal, 4d3a8e81) measured Jon's 19:15 all-trunk
    # compact firing NO PreCompact hook at all -- no payload from ANY session on the machine after
    # 16:02:35, while 39 PreToolUse payloads landed after 17:00, settings.json valid and unmodified.
    # Professional (bdbb3dc0) independently reported the same shape: 7 compact_boundary records,
    # 6 receipts, the 19:14 boundary firing nothing. Two trunks, adjacent minutes, no cause found.
    # CFL's own count is 8 boundaries / 8 receipts, so the fault is trunk-specific -- but "clean
    # today" is not a mechanism, and a convert step that runs perfectly over a boundary that
    # captured nothing yields a fresh index of an incomplete corpus with every gate green.
    #
    # ⚠️ THE COUNT MUST BE STRUCTURAL, NOT A SUBSTRING. A naive scan for the token "compact_boundary"
    # returned 13 here against 8 real ones: five hits were THIS SESSION'S OWN TRANSCRIPT discussing
    # the token with peers. The matcher measured its own author. Test type/subtype, never the text.
    rows.append(grade_step0(sess))  # WW-1b: one implementation, also used by late_regrade()

    rc, out = run([sys.executable, "scripts/audit/auto_mint_windows.py"])
    rc2, out2 = run([sys.executable, "scripts/audit/render_freshness_check.py"])
    # ORDER-1's committed acceptance test rides step 1: mint, then verify artifacts-not-counters
    v1 = "PASS" if rc == 0 and rc2 == 0 else ("UNKNOWN" if rc2 == 2 else "FAIL")
    note1 = (f"exit={rc}/{rc2} · " + (out.splitlines()[-1][:55] if out else "") + " · "
             + (out2.splitlines()[0][:70] if out2 else "")).replace("|", "/")
    rows.append(("1 render md", v1, note1))

    # STEP 2 BUILT 2026-09-04. It had been hardcoded SKIPPED-NOT-BUILT since this
    # pipeline was written -- against Jon's own verbatim ordering quoted at the top of
    # this file ("render md -> ingest wiki -> rebuild index -> regen").
    #
    # THE COST OF LEAVING IT UNBUILT, measured today: 2026-09 sessions are 0.0% covered
    # (47 sessions, 0 covered) while every earlier month runs 51-95%. Compacts rendered
    # windows into raw/ and NOTHING turned them into wiki footprint. Jon, 2026-09-04:
    # "thats a huge defect that i have tried to correct in you multiple times. compact
    # still not triggering session covedrage by default? We should be at 100% by now by
    # default after ever all-trunk compact!"
    #
    # And the pipeline PRINTED "SKIPPED-NOT-BUILT 2 ingest wiki" on every run today
    # while CFL reported the 0.0% as a finding -- a cause and its symptom in the same
    # output, unconnected. That is this week's dominant defect wearing its plainest form.
    rc2i, out2i = run([sys.executable, "scripts/audit/main_thread_ingest.py",
                       "--session", sess[:8]])
    if rc2i == 0 and "written" in out2i:
        last = [l for l in out2i.splitlines() if l.strip()][-1][:150]
        rows.append(("2 ingest wiki", "PASS", last.replace("|", "/")))
    elif silent_ok(rc2i, out2i):
        # WW-2: exit 0 and zero bytes says nothing about ingest. Name the command so the
        # next reader can re-run it by hand, which is how this one was diagnosed.
        rows.append(("2 ingest wiki", "UNKNOWN",
                     "exit=0 with ZERO output — no measurement, not a failure of ingest. "
                     "Re-run by hand: python scripts/audit/main_thread_ingest.py --session "
                     + sess[:8]))
    else:
        # A failed ingest is UNKNOWN, never a pass, and never silently skipped again.
        rows.append(("2 ingest wiki", "FAIL",
                     f"main_thread_ingest exit={rc2i}: "
                     + (out2i.splitlines()[-1][:110] if out2i.strip() else "no output")))

    # ⛔ STEP 3 WAS AN AGE REPORT AND NEVER REBUILT ANYTHING, and Jon named the cost on 2026-09-04:
    # "cfl thinks not everything is hooking that shoudl in regards to standard updates in regards
    # to compact and that has hurt vector embeded grph rag."
    #
    # The rationale for skipping was "a 700s rebuild inside a hook". ⭐ THAT NUMBER IS THE --force
    # COST. build_index.py is IDEMPOTENT BY CONTENT HASH -- its own --help says so -- so a plain
    # incremental run re-embeds only what changed. [MEASURED 2026-09-04 20:1x: 37s with 12 changed
    # or new files, against a 900s hook timeout.] The decision rested on the wrong number.
    #
    # WHAT IT COST, measured the same hour: of the 4 files this session created, 0 were in the
    # index; of the files it changed, 8 were STALE -- and stale is worse than missing, because a
    # retrieval returns the SUPERSEDED text confidently (the indexed postcompact_pipeline.py was
    # 11,597 B against 12,818 B on disk -- the copy where step 7 still printed PASS on "unknown").
    # ⛔ So a post-compact seat asked to trace what its pre-compact self did retrieved either
    # nothing or the version before the fix. That is exactly the ancestor-tracing Jon asked for.
    if not IDX.exists():
        rows.append(("3 rebuild index", "FAIL", f"no index at {IDX}"))
    else:
        t3 = datetime.now().timestamp()
        # ⛔ `--include exchange` IS LOAD-BEARING AND MUST NOT BE DROPPED. build_index.py does a
        # FULL DEFAULT WALK of root on every call and DELETES the rows of any indexed file the
        # walk no longer reaches (documented in index_queue_drain.py's cross-root guard). Its
        # default walk EXCLUDES exchange/ by design (build_index.py:261). So index_queue_drain.py
        # would add an exchange/ file, truthfully record `indexed (build exit 0)`, and the NEXT
        # plain build would silently delete it again.
        #
        # ⚠️ MEASURED 2026-09-04 21:0x, and the first version of THIS STEP made it worse: wiring a
        # plain rebuild into every compact turned an occasional deletion into a guaranteed one at
        # every barrier. Evidence: of 16 exchange/ paths the queue marked `indexed`, exactly 1 was
        # still in the index -- the one drained AFTER the last plain build. The other 15 were gone,
        # with a truthful success note in the ledger for every one of them.
        #
        # ⭐ Widening here (not in build_index.py's documented default) also answers Jon directly:
        # "how we should be able to better trace through messages in the exchange". [m: 740 inbound
        # letters + 40 postcompact verdicts became retrievable; 2,870 -> 4,445 files, 63s.]
        # ⛔ `--provenance <mirror>` IS LOAD-BEARING FOR THE SAME REASON AS `--include exchange`.
        # PROVENANCE_DIRS defaults to the CLONE's own raw/transcripts (156 files); the actual
        # conversation history is the 5,818-file mirror at N:/claude-corpus/cfl/raw/transcripts,
        # which is OUTSIDE the walk root. Jon, 2026-09-04: "if you can't trace the wiki through the
        # conversation wtih vector embeded graph rag ... thats an issue." [m 21:1x: 156 -> 5,809
        # conversations indexed; 4,447 -> 10,260 files; 45s incremental.]
        # ⚠️ Omit this flag and the next build DELETES all 5,809 as "gone" -- the identical trap
        # that ate 15 of 16 exchange files earlier tonight, one tier over.
        # ⚠️ HONEST BOUND: the provenance tier is DOC-LEVEL ONLY (build_index.py ~:888) -- one chunk
        # per conversation, its summary. So a conversation is now FINDABLE and a quote inside its
        # body is still NOT retrievable. Coverage is fixed; depth is not. Body-chunking is a real
        # cost decision (~100k chunks) and is NOT taken here.
        MIRROR = "N:/claude-corpus/cfl/raw/transcripts"
        cmd3 = [sys.executable, "scripts/graphrag/build_index.py", "--quiet",
                "--include", "exchange"]
        if os.path.isdir(MIRROR):
            cmd3 += ["--provenance", MIRROR]
        else:
            # an absent mirror is UNKNOWN, never a silent narrowing of the corpus
            print(f"NOTE: mirror corpus absent at {MIRROR}; provenance tier will cover the clone "
                  f"only -- this NARROWS the index and is not a clean run")
        rc3, out3 = run(cmd3)
        el3 = datetime.now().timestamp() - t3
        age_min = (datetime.now().timestamp() - IDX.stat().st_mtime) / 60
        if rc3 == 0:
            rows.append(("3 rebuild index", "PASS",
                         f"incremental rebuild ran in {el3:.0f}s; index age now {age_min:.0f} min"))
        elif rc3 == 4:
            # the build lock is held by another seat -- a real, expected state, and NOT a pass
            rows.append(("3 rebuild index", "FAIL",
                         f"another build holds the lock (exit 4) after {el3:.0f}s; index age "
                         f"{age_min:.0f} min -- re-run when it clears"))
        else:
            rows.append(("3 rebuild index", "FAIL",
                         f"build_index exit={rc3} after {el3:.0f}s; index age {age_min:.0f} min; "
                         + (out3.splitlines()[-1][:80] if out3.strip() else "no output")))

    # --- 3b DERIVE THE RESIDENT INDEX, added 2026-09-12 on Jon's order -------------------------
    # Jon, ~23:0x CDT, verbatim (typos his): "But. We do still need the wikiskills version and
    # non-wikiskills version of all graphs."
    #
    # [measured 2026-09-12 22:5x] Both variants were on disk and only one was alive:
    #   index.sqlite           2026-09-12 20:50   5.00 GB   rebuilt at every boundary
    #   index.resident.sqlite  2026-08-23 15:55   166 MB    TWENTY DAYS STALE
    # `derive_resident_index.py` was referenced by NO hook and NO pipeline -- grep of scripts/ and
    # .claude/ returned the file itself and nothing else. It ran once, the day it was written, for
    # Jon's ruling "the residents need access to this key tool", and never again.
    #
    # ⭐ BEING A DERIVED COPY IS WHAT MADE IT INVISIBLE. It never errored; it answered from August.
    # A narrowed copy of a live index has no alarm of its own, so it needs the SOURCE's heartbeat --
    # which is this pipeline. That is the general lesson, not the specific file.
    #
    # It is graded on FRESHNESS AGAINST ITS SOURCE, never on exit code alone: a derive that returns 0
    # and leaves a copy older than the index it derives from has not done the job, and that is
    # precisely the state this step was added to end.
    _res = os.path.join(os.path.dirname(IDX), "index.resident.sqlite")
    if not os.path.isfile(IDX):
        rows.append(("3b derive resident index", "UNKNOWN",
                     "no source index to derive from -- not a pass"))
    else:
        t3b = datetime.now().timestamp()
        rc3b, out3b = sh("python scripts/graphrag/derive_resident_index.py", timeout=900)
        el3b = datetime.now().timestamp() - t3b
        tail3b = (out3b.strip().splitlines() or ["no output"])[-1][:120]
        try:
            src_m = os.path.getmtime(IDX)
            res_m = os.path.getmtime(_res)
        except OSError as e:
            rows.append(("3b derive resident index", "UNKNOWN",
                         f"derive exit={rc3b} in {el3b:.0f}s but freshness unmeasurable: {e}"))
        else:
            lag = (src_m - res_m) / 60.0
            if rc3b != 0:
                rows.append(("3b derive resident index", "FAIL",
                             f"exit={rc3b} after {el3b:.0f}s; resident copy lags source by "
                             f"{lag:.0f} min · {tail3b}"))
            elif lag > 60:
                rows.append(("3b derive resident index", "FAIL",
                             f"exit 0 in {el3b:.0f}s and the copy is STILL {lag:.0f} min older than "
                             f"the index it derives from -- a clean exit over a stale copy is the "
                             f"exact defect this step exists to catch"))
            else:
                rows.append(("3b derive resident index", "PASS",
                             f"derived in {el3b:.0f}s; resident copy within {max(0.0, lag):.0f} min "
                             f"of source · {tail3b}"))

    # --- 3c GRAPH REACHABILITY, added 2026-09-12 on Jon's own standard ------------------------
    # Jon, ~23:2x CDT, verbatim (typos his): "i think it might be fine if the graph doesn't have raw
    # conversations in it if our ontologies and synthesis are good enough, and so long as the raw
    # conversatrion is still *reachable* via the graph - from key concepts etc."
    #
    # That sentence is the reason this step exists and the reason the OTHER plan was dropped. I had
    # been arguing to index the 544 MB of raw conversation the builder reduces away. He is right that
    # he has been told repeatedly to make the graph smaller, and right that CONTAINMENT is not the
    # requirement -- REACHABILITY is. A smaller graph that can be arrived at beats a bigger one.
    #
    # [measured 23:4x] 2,909 reduced transcripts: 98.2% resolve, 65.3% named by a knowledge page,
    # 11.8% reachable only by a 6-hex session id (a weak edge -- nobody arrives at "b98d2c" by
    # following meaning), and 22.9% -- 667 files -- pointed at by NOTHING.
    #
    # ⭐ AND IT CORRECTED MY OWN FIRST NUMBER. A scratch version substring-searched the knowledge
    # text and reported 20.2% islands; a substring OVER-matches, so it over-counted reachability and
    # under-counted islands. Exact token matching gives 22.9% and takes 2.7s instead of minutes.
    # The optimistic number came from the sloppier method, which is the direction that gets published.
    #
    # It REPORTS. It never blocks -- an island is a missing edge, and which edges should exist is
    # judgment. UNKNOWN when the index is absent or the population is empty, never a pass.
    t3c = datetime.now().timestamp()
    # --ticket per Jon, 23:5x: "Islands are defects I assume and you ticket those by default."
    # The ticket is REGENERATED here, so its count cannot drift from the graph it describes.
    rc3c, out3c = sh("python scripts/audit/graph_reachability.py --ticket --list-islands 0",
                     timeout=120)
    el3c = datetime.now().timestamp() - t3c
    _isl = ""
    for _ln in (out3c or "").splitlines():
        if "ISLANDS" in _ln:
            _isl = " ".join(_ln.split())[:110]
    if rc3c == 4:
        rows.append(("3c graph reachability", "UNKNOWN",
                     f"could not run in {el3c:.0f}s -- {(out3c.strip().splitlines() or [''])[-1][:120]}"))
    elif rc3c in (0, 3):
        rows.append(("3c graph reachability", "PASS" if rc3c == 0 else "UNKNOWN",
                     (f"{_isl or 'no island line parsed'} · {el3c:.1f}s · reports, never blocks -- "
                      f"an island is a MISSING EDGE and which edges should exist is judgment")))
    else:
        rows.append(("3c graph reachability", "FAIL",
                     f"exit={rc3c} after {el3c:.0f}s -- the instrument itself failed, which is not "
                     f"the same as a graph with no islands"))

    rows.append(("4 regen brief", "SKIPPED-NOT-OWNED", "CFL has no hourly brief; the pulse is the beat"))

    fl = ROOT / "raw" / "transcripts" / "claude-code" / "fl"
    wins = sorted(fl.glob("code-*-window-*.md"), key=lambda p: p.stat().st_mtime)
    if wins:
        txt = wins[-1].read_text(encoding="utf-8", errors="replace")
        m = re.search(r"user_text_turns: (\d+)", txt)
        rows.append(("5 extract rulings", "PASS" if m else "FAIL",
                     f"newest window {wins[-1].name}: user_text_turns={m.group(1) if m else '?'} "
                     f"(verbatim in-window by mint construction; rulings/ promotion unbuilt — stated)"))
    else:
        rows.append(("5 extract rulings", "FAIL", "no windows found"))

    rows.append(("6 reconcile registry", "SKIPPED-NOT-BUILT", "rides RP-6/RP-22 — not a pass"))

    LINEAGE.parent.mkdir(exist_ok=True)
    resume = f"claude --resume {sess} --fork-session -p \"<q>\""
    # ⛔ THE PARENT WAS THE STRING LITERAL "UNKNOWN-predates-lineage" ON EVERY ROW, FOREVER, and
    # this step graded PASS on it -- so the lineage file had no lineage in it. The comment four
    # lines below already said "a gate whose only input is a fallback default is a gate that CANNOT
    # FAIL"; it was written about `sess` while `parent` sat hardcoded above it. Naming a failure
    # mode does not immunise the code underneath it. Derived 2026-09-04 (session_parent.py, 8/8):
    # ROOT | PARENT <sid> | UNKNOWN <reason>, and UNKNOWN never collapses into ROOT.
    try:
        _pv, _pd = _parent_of(sess)
        parent = _pd if _pv == "PARENT" else "%s (%s)" % (_pv, _pd)
    except Exception as e:
        _pv, parent = "UNKNOWN", "derivation raised %s" % e.__class__.__name__
    with open(LINEAGE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"session": sess, "parent": parent,
                            "parent_verdict": _pv,
                            "trunk": "CFL", "at": now.isoformat(timespec="seconds"),
                            "resume": resume}) + "\n")
    # ⛔ THIS ROW GRADED **PASS** WHILE APPENDING A LINEAGE ROW FOR SESSION "unknown", and
    # the resume line it published was `claude --resume unknown` -- unrunnable. A gate whose
    # only input is a fallback default is a gate that CANNOT FAIL. (measured 2026-09-04 19:16;
    # cause was a `;`-chained hook sharing one stdin, fixed by .claude/hooks/hook_fanout.sh)
    # A default that fires on EOF is not a measurement. UNKNOWN dominates a PASS.
    if sess == "unknown" or len(sess) < 8:
        rows.append(("7 lineage row", "FAIL",
                     "session id UNKNOWN -- row appended but unattributable and `--resume` is "
                     "unrunnable; check the hook is passing stdin (hook_fanout.sh) before trusting "
                     "ANY row in this table that keys on session"))
    else:
        rows.append(("7 lineage row", "PASS",
                     f"appended for {sess[:8]}; parent={_pv} {parent[:60]}; "
                     f"ELDER IS WITNESS NEVER AUTHORITY"))

    rec = ROOT / "exchange" / "su-close" / "precompact"
    receipts = sorted(rec.glob("*.md"))
    r_age = (now.timestamp() - receipts[-1].stat().st_mtime) / 60 if receipts else -1
    w_age = (now.timestamp() - wins[-1].stat().st_mtime) / 60 if wins else -1
    rows.append(("8 stamp liveness", "PASS" if receipts and wins else "FAIL",
                 f"ages at READ time: receipt {r_age:.0f}m, window {w_age:.0f}m, index {((now.timestamp()-IDX.stat().st_mtime)/60):.0f}m" if IDX.exists() else "index missing"))

    # WW-1b: one implementation, also used by late_regrade(). WW-1c: step 0's row is passed in as
    # the independent second method for the fixed-order cause -- see grade_step9's docstring.
    rows.append(grade_step9(receipts, sess))

    # 10 index drain — GR-1 (Jon: "does writing to the exchange hook raw md updates so vector
    # embeded graph rag can function as intended yet so all trunks can ground while reading?" ->
    # measured NO, ticketed, fixed by index_queue_enqueue.py (PostToolUse hook) +
    # index_queue_drain.py). This step is the out-of-band consumer of that queue at every
    # compact/session-start barrier, so a page written mid-session and never explicitly drained
    # still converges here. SKIPPED-NEVER-PASS per rule 1: a drain that could not run (missing
    # script, exception) is FAIL, never silently absent from the table.
    rc, out = run([sys.executable, "scripts/audit/index_queue_drain.py"])
    if rc == 0:
        last_line = next((ln for ln in reversed(out.splitlines()) if ln.strip()), "")
        rows.append(("10 index drain", "PASS", f"exit=0 · {last_line[:120]}"))
    else:
        rows.append(("10 index drain", "FAIL",
                     f"exit={rc} — pending rows left in exchange/su-close/INDEX-QUEUE.jsonl for "
                     f"next drain · {out.splitlines()[-1][:100] if out else ''}"))

    verdict = "FAIL" if any(v == "FAIL" for _, v, _ in rows) else (
        "PASS-WITH-SKIPS" if any(v.startswith("SKIPPED") or v == "UNKNOWN" for _, v, _ in rows) else "PASS")
    # ⛔ WW-2b, 2026-09-05. Jon read this line and asked, correctly: "pass-with-skills ...
    # That reads as a failure like what were the skips and have those been investigated
    # foundationally?" ⭐ HE HAD TO ASK BECAUSE THE VERDICT NAMED A CLASS AND NOT THE ROWS.
    # A summary word that forces the reader to open the table has not summarised anything.
    _reds = [n for n, v, _ in rows if v == "FAIL" or v.startswith("SKIPPED") or v == "UNKNOWN"]
    verdict_detail = ("  reds: " + "; ".join(_reds)) if _reds else ""
    me = Path(__file__).resolve()
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write(f"# POSTCOMPACT-STATUS — {now.isoformat(timespec='seconds')} session {sess[:8]}\n\n")
        f.write(f"VERDICT: {verdict}  (SKIPPED/UNKNOWN is never a PASS; a red exists — JON-ORDER-2 rule 1)\n")
        if verdict_detail:
            f.write(verdict_detail.strip() + "\n")
        # provenance block (Secretary's 18:00 finding: a hand-authored PASS and an executed
        # PASS must not be byte-comparable; a status older than its script did not run)
        # ⛔ WW-34, 2026-09-07: SUBJECT-IDENTITY. A verdict that does not name what it was
        # computed OVER cannot be graded stale by ANY reader -- it can only be believed.
        # POSTCOMPACT-STATUS.md is a SINGLE MUTABLE FILE and this pipeline correctly SKIPS when
        # another instance holds the lock, so after a skip the file keeps a verdict for a
        # DIFFERENT boundary and a DIFFERENT session and nothing in it says so.
        # [measured 2026-09-07 20:34 CDT, this trunk, this session's own compact: the pipeline
        # printed "SKIPPED -- another postcompact_pipeline is already running [pid=48868 ...],
        # age 608.2s. This instance wrote NOTHING; the holder owns the verdict file." The holder
        # never wrote either. This file still read "# POSTCOMPACT-STATUS - 2026-09-06T21:53:00
        # session 46276084" -- a day old, another session, another boundary -- and its only
        # freshness clause binds the SCRIPT MTIME, not the boundary, so it passes its own test.]
        # ⭐ THE FIX IS NOT TO WRITE ON SKIP. Two writers of one verdict file with no arbitration
        # is the 2026-09-04 21:2x defect this lock exists to prevent. The fix is to make the file
        # SAY WHAT IT IS ABOUT, so scripts/audit/verdict_provenance_lint.py --for <boundary>
        # renders UNKNOWN-FOR-THIS-SUBJECT instead of a reader taking it as today's verdict.
        f.write(f"boundary: {_boundary}\n")
        f.write(f"session: {sess}\n")
        f.write(f"elapsed: {datetime.now().timestamp() - t0:.1f}s\n")
        f.write(f"produced_by: {me} (script mtime "
                f"{datetime.fromtimestamp(me.stat().st_mtime).isoformat(timespec='seconds')}; "
                f"this file MUST be newer than that or the run did not happen)\n\n")
        f.write("| step | verdict | note |\n|---|---|---|\n")
        for s, v, n in rows:
            f.write(f"| {s} | {v} | {n} |\n")
        f.write(f"\nresume: `{resume}`\n")
    # WW-1: stamp AFTER the verdict is on disk, never before -- a stamp written up front would
    # make a crashed run suppress the retry, converting a dedupe into a silent outage.
    try:
        _stamp_path.write_text(f"{os.getpid()} {now.isoformat(timespec='seconds')}",
                               encoding="utf-8")
    except OSError:
        pass  # a stamp we could not write means the next wiring re-grades: noisy, never wrong
    print(f"POSTCOMPACT-STATUS: {verdict} -> {STATUS.relative_to(ROOT)}")
    if verdict_detail:
        print(verdict_detail.strip())
    for s, v, n in rows:
        print(f"  {v:20s} {s}")
    return 0  # rule 2: no step blocks


if __name__ == "__main__":
    sys.exit(main())
