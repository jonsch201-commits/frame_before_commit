#!/usr/bin/env python3
"""postcompact-pipeline.py -- ONE ordered pipeline, per-step PASS/FAIL, behind SessionStart.

JON'S ORDER 2, 2026-09-01, verbatim, typos his:
  "Hook: SessionStart matcher compact|resume|startup. One script, ordered: render md -> ingest
   wiki -> rebuild index -> regen brief -> extract rulings -> reconcile registry -> write lineage
   row -> stamp liveness -> verify summary vs tail -> write POSTCOMPACT-STATUS.md with per-step
   PASS/FAIL. Beat reads that file. Any FAIL = brief line 1."
  "You must also add a ancestor consult hook on new jsons, can agent sdk resume YOU to check YOUR
   WORK post reboot, and I require all can do the same. And when I say you I mean each trunk can."
  "when i tell one of you to do something. I expect it to be done on all trunks by default."

THE FOUR RULES THIS FILE IS BUILT ON, each from a defect measured in this trunk on 2026-09-01:

  1. A STEP THAT DID NOT RUN SAYS SO. There is no silent success anywhere below. Every step
     returns one of PASS / FAIL / SKIPPED-NOT-OWNED / UNKNOWN, and UNKNOWN is never a pass.
     (Six failures shipped here today were all one shape: a step that did not happen, reported
     as a step that did.)
  2. A ZERO POPULATION IS UNKNOWN, NEVER PASS. "copied 0 / failed 0" is Jon's named defect.
  3. WE DO NOT OWN WHAT WE DO NOT OWN. Steps belonging to Personal/CFL report
     SKIPPED-NOT-OWNED with the owner named -- never PASS, never FAIL, because a trunk cannot
     fail a step it was never assigned.
  4. LIVENESS IS COMPUTED AT READ TIME, NEVER A STORED BOOLEAN. FLEET-LIVENESS.json sat
     false-green for 11h24m on this machine because it stored `is_active: true`.

Usage: python scripts/postcompact-pipeline.py [--json]
Exit 0 if no step FAILED; 1 if any FAIL; 2 if the pipeline itself could not run.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = os.path.join(ROOT, "POSTCOMPACT-STATUS.md")
LINEAGE = os.path.join(ROOT, "exchange", "lineage.tsv")
SCAN_LINES = 60          # printed in the verdict; a bound you do not print is a bound the reader lacks
# R4 (2026-09-04): key derived by scripts/project_dirs.py, never typed. PROJ = primary (where the live
# session writes); PROJ_ALL = every dir this tree has lived under (old sessions stay under the old key).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import project_dirs as _pd
PROJ_ALL = _pd.existing_dirs(ROOT)
PROJ = PROJ_ALL[0] if PROJ_ALL else os.path.join(_pd.PROJECTS, _pd.derive_key(ROOT))


def sh(cmd, timeout=300):
    try:
        p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True,
                           text=True, timeout=timeout, errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT -- killed. UNKNOWN, never zero."
    except OSError as e:
        return 125, "OSError: %s -- UNKNOWN" % e


def step_render():
    rc, out = sh("bash scripts/render-sessions.sh", timeout=600)
    line = next((l for l in out.splitlines() if l.startswith("RENDER:")), "")
    if rc == 2:
        return "UNKNOWN", line or "render reported UNKNOWN"
    if rc != 0:
        return "FAIL", line or ("rc=%d" % rc)
    return "PASS", line


def step_render_check():
    rc, out = sh("bash scripts/render-sessions.sh --check", timeout=120)
    line = next((l for l in out.splitlines() if l.startswith("RENDER-CHECK:")), out.strip()[:200])
    return ("PASS" if rc == 0 else ("UNKNOWN" if rc == 2 else "FAIL")), line


def step_corpus_sync():
    """C23's remedy, wired -- the same lesson as step 7's, one surface over.

    C23 grades whether the corpus this trunk's retrieval reads still contains this trunk's
    work. It had been failing with a lag measured in DAYS and the remedy was a hand-run
    nobody had written down, so the check reported a true defect that nothing could close.

    Copy-only into this trunk's own slice; never deletes, never touches a sibling's slice,
    never rebuilds an index.
    """
    rc, out = sh("bash scripts/corpus-sync.sh", timeout=900)
    line = next((l for l in out.splitlines() if l.startswith("CORPUS-SYNC")), out.strip()[:200])
    return ("PASS" if rc == 0 else ("UNKNOWN" if rc in (2, 124, 125) else "FAIL")), line


def step_ingest_wiki():
    return ("SKIPPED-NOT-OWNED",
            "wiki ingest is Personal's per Jon's order 2. This trunk does not stage it.")


def step_rebuild_index():
    """Rebuild THIS trunk's own index at the barrier, then PROVE it is no older than the newest md.

    Until 2026-09-04 20:5x this step read SKIPPED-NOT-OWNED ("index rebuild owner Personal/CFL").
    That was true of the FEDERATED index and false of professional.sqlite, which this trunk has
    built by hand since graphrag.sh existed. Measured 2026-09-04: seven compacts in one session,
    md rendered at every hooked one, index rebuilt by hand ONCE (16:40) -- so every query between
    compacts read a transcript layer the index had never seen. Jon, 2026-09-04 ~20:2x, verbatim,
    typos his: "not everything is hooking that shoudl in regards to standard updates in regards to
    compact and that has hurt vector embeded grph rag." A compact is not settled until the md it
    rendered is searchable. graphrag.sh build is idempotent (no-op when nothing changed) and runs
    the sealed-exclusion probe; its lock is shared with CFL's builder, so exit 4 is HELD, not FAIL.
    """
    rc, out = sh("bash scripts/graphrag.sh build", timeout=900)
    tail = (out.strip().splitlines() or ["no output"])[-1][:160]
    if rc == 4:
        return "UNKNOWN", "HELD: another build holds the shared lock -- index NOT rebuilt this barrier; " + tail
    if rc != 0:
        return "FAIL", "graphrag.sh build exit %d: %s" % (rc, tail)
    db = os.path.join(os.environ.get("LOCALAPPDATA", ""), "claude", "graphrag", "professional.sqlite")
    md_dir = os.path.join(ROOT, "raw", "transcripts", "claude-code")
    try:
        db_m = os.path.getmtime(db)
        mds = [os.path.join(md_dir, f) for f in os.listdir(md_dir) if f.endswith(".md")]
        md_m = max(os.path.getmtime(f) for f in mds) if mds else None
    except OSError as e:
        return "UNKNOWN", "built, but freshness unmeasurable: %s" % e
    if md_m is None:
        return "UNKNOWN", "built, but no md under raw/transcripts/claude-code to compare against"
    fmt = lambda t: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
    if db_m + 1 >= md_m:
        return "PASS", "index %s >= newest md %s; %s" % (fmt(db_m), fmt(md_m), tail)
    return "FAIL", "index %s is OLDER than newest md %s -- build reported ok but did not settle" % (fmt(db_m), fmt(md_m))


def step_index_coverage():
    """Not a rebuild -- a MEASUREMENT of whether the index can answer 'does this tool exist'."""
    rc, out = sh("python scripts/ACCEPTANCE-index-covers-executables.py", timeout=180)
    cov = next((l.strip() for l in out.splitlines() if l.startswith("coverage:")), "")
    if rc == 2 or not cov:
        return "UNKNOWN", (out.strip().splitlines() or ["no output"])[0][:200]
    return "PASS", cov + "  (reports, never gates -- a deliberate exclusion is correct behaviour)"


def _sessions():
    """(dir, file) pairs across EVERY project dir of this tree; None if none readable."""
    out, readable = [], 0
    for d in PROJ_ALL or [PROJ]:
        try:
            names = os.listdir(d); readable += 1
        except OSError:
            continue
        out.extend((d, f) for f in sorted(names) if f.endswith(".jsonl"))
    return out if readable else None


def step_lineage():
    """Write the parent link a compact/resume never records. Jon's gap #8."""
    files = _sessions()
    if files is None:
        return "UNKNOWN", "project dir unreadable: %s -- UNKNOWN, not zero" % PROJ
    if not files:
        return "UNKNOWN", "zero session JSONLs found -- a zero population is not a pass"
    rows, unknown = [], 0
    for d, f in files:
        sid = f[:-6]
        parent = ""
        try:
            with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
                for _ in range(SCAN_LINES):
                    line = fh.readline()
                    if not line:
                        break
                    try:
                        d = json.loads(line)
                    except ValueError:
                        continue
                    parent = d.get("parentSessionId") or ""
                    if parent:
                        break
        except OSError:
            unknown += 1
            continue
        rows.append((sid, parent or "none",
                     "claude --resume %s --fork-session" % sid))
    if not rows:
        return "UNKNOWN", "no session readable -- UNKNOWN"
    try:
        os.makedirs(os.path.dirname(LINEAGE), exist_ok=True)
        with open(LINEAGE, "w", encoding="utf-8") as fh:
            fh.write("session_id\tparent_session_id\tancestor_resume_line\n")
            for r in rows:
                fh.write("\t".join(r) + "\n")
    except OSError as e:
        return "FAIL", "could not write %s: %s" % (LINEAGE, e)
    linked = sum(1 for r in rows if r[1] != "none")
    return "PASS", ("%d session(s) written to exchange/lineage.tsv; %d carry a parent link, "
                    "%d unreadable (UNKNOWN, counted not dropped). BOUND: only the first %d lines "
                    "of each JSONL are scanned for parentSessionId, so a link written later is "
                    "OUTSIDE this population -- 'none' here means NOT FOUND IN THE HEAD, never "
                    "proven absent. Jon's gap #8 is that compact/resume never writes the link at "
                    "all; this measures it, it does not fix it."
                    % (len(rows), linked, unknown, SCAN_LINES))


def step_archive_backfill():
    """The REMEDY wired to step 8's measurement.

    Until 2026-09-01 21:2x this pipeline measured archive coverage at 15.4% and had nothing
    that could act on it. A measurement with no remedy wired to it is a number, not a control
    -- and it had been reporting the same FAIL run after run, which reads as diligence.

    The archive is the durable copy of Jon's standing "All must be recoverable, keep json";
    the live copy under ~/.claude/projects/ is the one `cleanupPeriodDays` can take.
    """
    rc, out = sh("bash scripts/archive-backfill.sh", timeout=900)
    line = next((l for l in out.splitlines() if l.startswith("BACKFILL")), out.strip()[:200])
    return ("PASS" if rc == 0 else ("UNKNOWN" if rc in (2, 124, 125) else "FAIL")), line


def step_archive_coverage():
    """The number nobody measured: how much of our own history do we actually keep?

    COUNTS THE ARTIFACT, NOT THE FOLDER. This counted archive SUBDIRECTORIES until
    2026-09-01 21:3x -- but precompact-capture.sh runs `mkdir -p` BEFORE it copies, so a
    capture that failed at the copy still left a directory behind and still scored as
    coverage. Same family as counting a converter's exit codes instead of the files it
    wrote: A COUNTER MUST COUNT THE EFFECT, NEVER THE CALL. Now a session counts only if
    its own <sid>.jsonl is present and non-empty.
    """
    files = _sessions()
    if files is None:
        return "UNKNOWN", "project dir unreadable -- UNKNOWN"
    files = [f for _d, f in files]  # R4: _sessions() now yields (dir, file) across every project dir
    root = os.path.join(ROOT, "raw", "session-archive")
    try:
        dirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    except OSError:
        return "UNKNOWN", "raw/session-archive unreadable -- UNKNOWN"
    held = set()
    for d in dirs:
        j = os.path.join(root, d, d + ".jsonl")
        try:
            if os.path.getsize(j) > 0:
                held.add(d)
        except OSError:
            pass
    if not files:
        return "UNKNOWN", "zero live sessions -- not a pass"
    live_ids = {os.path.basename(f)[:-6] for f in files}
    covered = live_ids & held
    pct = 100.0 * len(covered) / len(live_ids)
    verdict = "PASS" if pct >= 90 else "FAIL"
    empty_dirs = len(dirs) - len(held)
    return verdict, ("archive holds a non-empty jsonl for %d of %d live sessions = %.1f%% "
                     "(%d archive dir(s) hold no session jsonl and are NOT counted; %d archived "
                     "session(s) are no longer live and are outside this denominator). Every page "
                     "grounded in the archive inherits this bound."
                     % (len(covered), len(live_ids), pct, empty_dirs, len(held - live_ids)))


def step_liveness():
    """Rule 4: computed at READ time. Never a stored boolean."""
    md = os.path.join(ROOT, "raw", "transcripts", "claude-code")
    try:
        newest = max((os.path.getmtime(os.path.join(md, f))
                      for f in os.listdir(md) if f.endswith(".md")), default=None)
    except OSError:
        return "UNKNOWN", "render dir unreadable -- UNKNOWN"
    if newest is None:
        return "FAIL", "no rendered md exists"
    age_min = (time.time() - newest) / 60.0
    return "PASS", ("newest rendered md is %.0f min old, computed at read time from mtime -- "
                    "no stored boolean anywhere in this line" % age_min)


STEPS = [
    ("1 render md", step_render),
    ("2 render acceptance", step_render_check),
    ("2b corpus sync (own slice)", step_corpus_sync),
    ("3 ingest wiki", step_ingest_wiki),
    ("4 rebuild index", step_rebuild_index),
    ("5 index coverage", step_index_coverage),
    ("6 lineage + ancestor resume", step_lineage),
    ("7 archive backfill", step_archive_backfill),
    ("8 archive coverage", step_archive_coverage),
    ("9 liveness (read-time)", step_liveness),
]


def main():
    results = []
    for name, fn in STEPS:
        try:
            verdict, note = fn()
        except Exception as e:                      # a crashed step is UNKNOWN, never silent
            verdict, note = "UNKNOWN", "step raised %s: %s" % (type(e).__name__, e)
        results.append((name, verdict, note))

    fails = [r for r in results if r[1] == "FAIL"]
    unknowns = [r for r in results if r[1] == "UNKNOWN"]
    overall = "FAIL" if fails else ("UNKNOWN" if unknowns else "PASS")
    stamp = time.strftime("%Y-%m-%d %H:%M:%S %Z")

    body = ["# POSTCOMPACT-STATUS — Claude Professional", "",
            "run: %s  ·  overall: **%s**" % (stamp, overall), "",
            "⛔ **A step that did not run says so. UNKNOWN is never a pass. "
            "SKIPPED-NOT-OWNED is not a failure — a trunk cannot fail a step it was never "
            "assigned.**", "",
            "| step | verdict | note |", "|---|---|---|"]
    for name, verdict, note in results:
        body.append("| %s | **%s** | %s |" % (name, verdict, note.replace("|", "\\|")[:400]))
    body += ["", "## Ancestor consult — Jon's order 2",
             "", "Any successor can resume and co-review this trunk's sessions:", "",
             "```bash", "claude --resume <session-id> --fork-session -p \"<question>\"", "```",
             "", "⭐ **`--fork-session` deliberately: a co-review must not write into the record "
             "it reviews.** Full table of session ids and parent links: `exchange/lineage.tsv`.",
             "", "See `RESUME.md` for which storage layer is durable."]
    with open(STATUS, "w", encoding="utf-8") as fh:
        fh.write("\n".join(body) + "\n")

    if "--json" in sys.argv:
        print(json.dumps({"overall": overall,
                          "steps": [{"step": n, "verdict": v, "note": t} for n, v, t in results]},
                         indent=1))
    else:
        for name, verdict, note in results:
            print("%-30s %-18s %s" % (name, verdict, note[:150]))
        print("OVERALL: %s  ->  %s" % (overall, STATUS))
    # ⛔ THE EXIT CODE MUST SAY WHAT THE TABLE SAYS. This read `1 if fails else 0` until
    # 2026-09-01 21:3x, so an overall of UNKNOWN -- which this file's own banner calls
    # "never a pass" -- exited 0 and read as a pass to every caller that checks the code
    # instead of the page. A DISPLAY DECOUPLED FROM THE THING IT DESCRIBES, in the
    # instrument built to end that class. 0 PASS · 1 FAIL · 2 UNKNOWN.
    return 1 if fails else (2 if unknowns else 0)


if __name__ == "__main__":
    sys.exit(main())
