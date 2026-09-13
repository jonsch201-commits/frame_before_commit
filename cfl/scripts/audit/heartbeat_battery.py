#!/usr/bin/env python3
"""heartbeat_battery.py -- the ~10-check barrier battery, per Jon's WWJA direction.

Runs at BARRIERS (close / compact / ship-to-Jon) -- never on timers. end-heartbeat is
honored: this script is dispatched by hand or by a barrier hook, never by a self-wake
loop. See skills/probe-registry/references/WWJA.md for the design this implements
(WWJA = check #1 of this battery) and exchange/memory-core-v0/hooks/LIVENESS.md for
the hook-liveness grep this wraps (check #3).

Each check is cheap (<5s, except #2 which calls the live retriever) and returns
PASS / WARN / UNKNOWN / INFO plus one evidence line. UNKNOWN is used whenever a check
cannot run at all -- never silently skipped (a missing --topic, a missing --session,
a missing file are all UNKNOWN rows, not absent ones).

Usage:
  python scripts/audit/heartbeat_battery.py --as-of 2026-08-22T21:00:00-05:00
      [--topic "WWJA battery"] [--session 442d2e88] [--strict] [--selftest]

--as-of is REQUIRED (repo convention: no now() default -- a measured clock only).
EXIT CODES -- and they are separated deliberately, on Soul's 2026-08-24 amendment.

  0  clean
  1  FINDINGS (only under --strict / --strict-direction)
  2  usage error -- bad or missing arguments
  3  THE BATTERY ITSELF COULD NOT RUN (uncaught exception)

Until 2026-08-24, 3 did not exist and an uncaught exception exited 1 -- THE SAME CODE AS
"a regression was found". A gate wiring `--strict-direction` could not distinguish "this
found a real problem" from "this died before it looked". That is an overloaded signal, and
Soul's amendment names why removing a `|| true` does not fix it:

  A FAILURE PATH THAT DIFFERS FROM THE SUCCESS PATH CANNOT BE BUILT ON A SIGNAL THAT
  ALREADY CARRIES ANOTHER MEANING. Before branching on an exit code, MEASURE what it
  returns on a NORMAL run. If 1 already means "found things", it cannot also mean "died".

They found it the hard way: two of their checks exit 1 ON FINDINGS, so the obvious fix --
branch on nonzero -- would have converted a silent false-green into a PERMANENT FALSE-RED,
which is worse, because an alarm that always fires guards nothing.
"""

from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import shutil
import datetime as dt

# Windows consoles default to cp1252 and this file's own output contains WARN/UNKNOWN glyphs
# pulled from source files (WWJA.md, LIVENESS.md use unicode em dashes/warning signs). Without
# this the script dies mid-report -- the worst place, since partial numbers read as a completed
# run. Reconfigure to utf-8 (repo convention, see check_memory_refs.py), never to cp1252 itself.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WWJA_MD = os.path.join(REPO, "skills", "probe-registry", "references", "WWJA.md")
LIVENESS_MD = os.path.join(REPO, "exchange", "memory-core-v0", "hooks", "LIVENESS.md")
WORK_CLAIMS = os.path.join(REPO, "exchange", "WORK-CLAIMS.md")
INBOUND_DIR = os.path.join(REPO, "exchange", "inbound")
PROBE_REGISTRY = os.path.join(REPO, "wiki", "tracker", "PROBE-REGISTRY.md")
WAKE_MD = os.path.join(REPO, "exchange", "WAKE.md")
INSTANCES_DIR = os.path.join(REPO, "exchange", "memory-core-v0", "instances")
RETRIEVE_PY = os.path.join(REPO, "scripts", "graphrag", "retrieve.py")
FROZEN_BRANCH = "feat/memory-drain-and-retrieval-checks-2026-08-06"

# PR-1 (#251) squash-merged to main 2026-08-23T03:26:17Z. The freeze it protected is over and
# FROZEN_BRANCH was deleted by that merge, so the freeze arm of check 8 can no longer resolve.
# It does NOT follow that the check is obsolete: what the freeze existed to protect is that the
# reviewed work actually LANDED. So check 8 now has two arms -- freeze-active and post-merge --
# and the post-merge arm asserts main still contains this commit. A deleted branch used to read
# UNKNOWN here, which is indistinguishable from a check that never ran.
LANDED_COMMIT = "ee473c1"

PASS, WARN, UNKNOWN, INFO = "PASS", "WARN", "UNKNOWN", "INFO"


class Row:
    def __init__(self, n, name, status, evidence, mag=None):
        self.n = n
        self.name = name
        self.status = status
        self.evidence = evidence
        # `mag` is the check's COUNT of whatever it found -- open TAKEs, failing probe rows, dirty
        # paths. None means the check has no natural magnitude. It exists so a run can be compared
        # with the previous one; see the DIRECTION block below for why that is not decoration.
        self.mag = mag
        self.delta = ""      # filled in by annotate_direction()

    def line(self):
        d = f"  {self.delta}" if self.delta else ""
        return f"[{self.n:2d}] {self.status:7s} {self.name:28s} {self.evidence}{d}"


# ---------------------------------------------------------------------------
# DIRECTION -- added 2026-08-24, and the reason is a defect this file predicted
# and could not detect.
#
# `check_probe_regressions` already carries this comment, written weeks ago:
#     "...ever drift toward permanent WARN -- an alarm that always fires is not an alarm."
# The risk was named. No mechanism was built. So the drift happened exactly as written:
#
#   `exchange/WAKE.md`, at the 2026-08-23 sitting close, recorded the standing WARNs in prose --
#   "7 stale open TAKEs" and "9 probe-regression rows". Measured 2026-08-24: OPEN-TAKES is still
#   7, and PROBE-REGRESSIONS is 10. It got WORSE by one and nothing said so, because the reader
#   had already learned the alarm. The battery exits 0 with five WARNs, so even the exit code
#   cannot separate a steady state from a regression.
#
# Soul named the class the same day and it is a fourth layer beside the three in STANDARDS 17:
# CONSUMPTION-PRESENT, ACTION-ABSENT. A check that cannot fail is invisible because it is SILENT.
# One that cannot finish is invisible because it is ABSENT. One that ALWAYS FIRES is invisible
# because it is LOUD -- its signal is correct, present, and indistinguishable from every previous
# run's, so the reader learns the alarm instead of the finding.
#
# THE FALSIFIER, so this is a mechanism and not a better-phrased complaint: could the battery tell
# you that a WARN's count had DOUBLED overnight? Before this block, no. A gate that cannot report a
# REGRESSION is reporting a mood. The fix is a baseline with a DIRECTION, not a longer list.
#
# BOUNDS, all three parts:
#   1. NOT REVIEWED: whether a count going down means the underlying work was DONE. A row can
#      leave a registry by being deleted, rephrased, or reclassified.
#   2. WHY: the battery reads counts, not causes.
#   3. RESULTING LIMITATION: BETTER is a prompt to check, never a discharge. Only WORSE and NEW
#      are self-justifying, and they are the two this exists to surface.
BASELINE_PATH = os.path.join(REPO, "wiki", "tracker", "heartbeat-baseline.json")


def load_baseline(path=BASELINE_PATH):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


# How old a baseline may be before every verdict against it becomes UNKNOWN.
#
# ⛔ ADDED 2026-08-24 ON SOUL'S ATTACK, AND IT FENCES THE ROT I LEFT OPEN. A manual baseline is
# right -- one that moves on every run can never show a regression. But a manual baseline that is
# NEVER updated rots the other way: as real work lands, every row reads `better` forever, the
# comparand describes a world that no longer exists, and the check drifts back to furniture by the
# opposite road. ⭐ I fenced permanent-WARN and left permanent-BETTER open, and permanent-BETTER is
# worse, because NOBODY INVESTIGATES GOOD NEWS.
BASELINE_MAX_AGE_DAYS = 14


def annotate_direction(rows, baseline, as_of=None):
    """Tag each row with how its magnitude moved since the recorded baseline.

    ⛔ EVERY VERDICT CARRIES THE BASELINE'S PROVENANCE. A number a script prints reads as MEASURED
    no matter where the script got it, so a verdict computed against a RECALLED figure -- one a
    seat wrote in prose and nobody verified -- must say so inline or it inherits the mechanism's
    authority. That is `authority-inheritance-in-prose` with one extra hop, and this mechanism is
    exactly the kind of hop that hides it.

    ⛔ AND A ROW WHOSE BASELINE IS MARKED UNUSABLE READS `NO BASELINE`, NEVER A DIRECTION. The
    first version of this file compared a count from a REPLACED counter against a count from its
    replacement and printed `WORSE: 9 -> 10 (+1)`. Both numbers were real; the comparison was not.
    A baseline and its probe must measure the same population, and when the baseline came from a
    different instrument the probe must mirror THAT instrument's definition -- not a reasonable one.
    """
    prev = baseline.get("checks", {})
    stale = False
    if as_of is not None and baseline.get("as_of"):
        try:
            age = (as_of - parse_iso(baseline["as_of"])).days
            stale = age > BASELINE_MAX_AGE_DAYS
        except (ValueError, TypeError):
            stale = False
    for r in rows:
        if r.mag is None:
            continue
        row_base = prev.get(r.name, {})
        was = row_base.get("mag")
        prov = row_base.get("provenance", "")
        conf = str(row_base.get("confidence", "")).lower()
        tag = ""
        if prov.startswith("recalled"):
            tag = "  [baseline RECALLED, not measured]"
        if was is None:
            note = ""
            if row_base:
                note = f" -- prior figure withheld: {row_base.get('confidence', 'unusable')}"
            r.delta = "<< NO BASELINE -- UNKNOWN, not steady" + note
            continue
        if "unusable" in conf:
            r.delta = f"<< NO USABLE BASELINE -- {row_base.get('confidence')}"
            continue
        if stale:
            r.delta = (f"<< UNKNOWN: baseline is {age} days old (>{BASELINE_MAX_AGE_DAYS}) -- "
                       f"too old to compare, and UNKNOWN must not render as steady")
            continue
        if r.mag > was:
            r.delta = f"<< WORSE: {was} -> {r.mag} (+{r.mag - was}) since {baseline.get('as_of', '?')}{tag}"
        elif r.mag < was:
            r.delta = f"<< better: {was} -> {r.mag} -- VERIFY the work was done, not just delisted{tag}"
        else:
            r.delta = f"== unchanged at {r.mag} since {baseline.get('as_of', '?')}{tag}"
    return rows


def write_baseline(rows, as_of, path=BASELINE_PATH):
    data = {"as_of": as_of.isoformat(),
            "note": "Written ONLY by --update-baseline. A baseline that updates itself on every "
                    "run can never show a regression -- it would move to meet whatever it found.",
            "checks": {r.name: {"mag": r.mag, "status": r.status}
                       for r in rows if r.mag is not None}}
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return path


def parse_iso(s):
    """Parse an ISO-8601 timestamp, tolerant of a bare offset with no colon."""
    s = s.strip()
    try:
        return dt.datetime.fromisoformat(s)
    except ValueError:
        pass
    m = re.match(r"^(.*?)([+-]\d{2})(\d{2})$", s)
    if m:
        return dt.datetime.fromisoformat(f"{m.group(1)}{m.group(2)}:{m.group(3)}")
    raise ValueError(f"cannot parse timestamp: {s!r}")


def run_cmd(args, cwd=REPO, timeout=60):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                            timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, p.stdout, p.stderr
    except Exception as e:  # pragma: no cover - defensive
        return -1, "", str(e)


# ---------------------------------------------------------------------------
# Check 1 -- WWJA
# ---------------------------------------------------------------------------

def check_wwja(topic, repo=REPO):
    if not os.path.isfile(os.path.join(repo, "skills", "probe-registry", "references", "WWJA.md")):
        return Row(1, "WWJA", UNKNOWN, "WWJA.md not found under this repo")
    wwja_path = os.path.join(repo, "skills", "probe-registry", "references", "WWJA.md")
    try:
        with open(wwja_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception as e:
        return Row(1, "WWJA", UNKNOWN, f"cannot read WWJA.md: {e}")

    ids = re.findall(r"\|\s*(W\d+)\s*\|\s*\*\*\"([^\"]+)\"\*\*", text)
    header = "; ".join(f"{i}:{q}" for i, q in ids[:10])
    if not ids:
        header = "(WWJA table not found in expected shape)"
    print("    WWJA checklist (W1-W10):")
    print(f"      {header}")

    if not topic:
        return Row(1, "WWJA", UNKNOWN, "no topic given (--topic not passed)")

    retrieve_py = os.path.join(repo, "scripts", "graphrag", "retrieve.py")
    if not os.path.isfile(retrieve_py):
        return Row(1, "WWJA", UNKNOWN, "retrieve.py not found")
    rc, out, err = run_cmd([sys.executable, retrieve_py, topic, "-k", "3", "--json"], cwd=repo)
    if rc != 0:
        return Row(1, "WWJA", UNKNOWN, f"retrieve.py exit {rc}: {(err or out)[:120]}")
    try:
        payload = json.loads(out)
    except Exception:
        return Row(1, "WWJA", UNKNOWN, f"retrieve.py returned non-JSON: {out[:120]}")
    hits = payload.get("hits", 0)
    if hits == 0:
        return Row(1, "WWJA", WARN, f'topic="{topic}" returned 0 hits at k=3')
    top = payload["results"][0]["source"] if payload.get("results") else "?"
    return Row(1, "WWJA", PASS, f'topic="{topic}" {hits} hits, rank1={top}')


# ---------------------------------------------------------------------------
# Check 2 -- INDEX-STALE
# ---------------------------------------------------------------------------

def check_index_stale(repo=REPO):
    retrieve_py = os.path.join(repo, "scripts", "graphrag", "retrieve.py")
    if not os.path.isfile(retrieve_py):
        return Row(2, "INDEX-STALE", UNKNOWN, "retrieve.py not found")
    # plain-text mode only -- --json short-circuits before the staleness print
    rc, out, err = run_cmd([sys.executable, retrieve_py, "index", "-k", "1"], cwd=repo, timeout=90)
    if rc != 0:
        return Row(2, "INDEX-STALE", UNKNOWN, f"retrieve.py exit {rc}: {(err or out)[:120]}")
    stale_lines = [ln for ln in out.splitlines() if "STALE" in ln]
    if stale_lines:
        return Row(2, "INDEX-STALE", WARN, stale_lines[0].strip()[:140])
    return Row(2, "INDEX-STALE", PASS, "no STALE banner on 1-word query")


# ---------------------------------------------------------------------------
# Check 3 -- HOOK-LIVENESS
# ---------------------------------------------------------------------------

def find_session_jsonl(session, repo=REPO):
    home = os.path.expanduser("~")
    projects = os.path.join(home, ".claude", "projects")
    trunk = os.path.basename(repo.replace(":", "").replace("\\", "-").replace(" ", "-").replace("/", "-"))
    # try the exact CFL trunk dir name first, then a global search
    candidates = glob.glob(os.path.join(projects, "*", f"{session}*.jsonl"))
    return candidates


def check_hook_liveness(session):
    if not session:
        return Row(3, "HOOK-LIVENESS", UNKNOWN, "no --session given")
    matches = find_session_jsonl(session)
    if not matches:
        return Row(3, "HOOK-LIVENESS", UNKNOWN, f"no JSONL found matching session {session!r}")
    path = matches[0]
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        return Row(3, "HOOK-LIVENESS", UNKNOWN, f"cannot read {path}: {e}")
    total = len(lines)
    hook_line_nums = [i for i, ln in enumerate(lines, start=1) if '"hookEvent":"' in ln]
    if not hook_line_nums:
        return Row(3, "HOOK-LIVENESS", WARN,
                    f"0 hookEvent records in {total} lines -- runner never fired this session")
    last_line_no = hook_line_nums[-1]
    ts_m = re.search(r'"timestamp":"([^"]*)"', lines[last_line_no - 1])
    ts = ts_m.group(1) if ts_m else "?"
    staleness = total - last_line_no
    return Row(3, "HOOK-LIVENESS", PASS,
               f"{len(hook_line_nums)} hookEvent records, last @{ts} (line {last_line_no}/{total}, "
               f"{staleness} lines since)")


# ---------------------------------------------------------------------------
# Check 4 -- OPEN-TAKES
# ---------------------------------------------------------------------------

def parse_work_claims_rows(path):
    """Return list of (verb, work_item) data rows in file order, skipping header/sep."""
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    rows = []
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0] in ("at", "---") or set(cells[0]) <= {"-"}:
            continue
        verb = cells[2] if len(cells) > 2 else ""
        work_item = cells[3] if len(cells) > 3 else ""
        if verb not in ("TAKE", "DONE", "RELEASE", "NOTE"):
            continue
        rows.append((verb, work_item))
    return rows


def check_open_takes(path=WORK_CLAIMS, tail=40):
    rows = parse_work_claims_rows(path)
    if rows is None:
        return Row(4, "OPEN-TAKES", UNKNOWN, f"{path} not found")
    window = rows[-tail:]
    open_takes = []
    for idx, (verb, item) in enumerate(window):
        if verb != "TAKE":
            continue
        closed = any(v in ("DONE", "NOTE") and it == item for v, it in window[idx + 1:])
        if not closed:
            open_takes.append(item)
    if open_takes:
        return Row(4, "OPEN-TAKES", WARN,
                    f"{len(open_takes)} open TAKE(s) in last {len(window)} rows: {open_takes[0][:90]}",
                    mag=len(open_takes))
    return Row(4, "OPEN-TAKES", PASS, f"0 open TAKEs in last {len(window)} rows")


# ---------------------------------------------------------------------------
# Check 5 -- INBOX-NEW
# ---------------------------------------------------------------------------

def check_inbox_new(as_of, inbound_dir=INBOUND_DIR):
    if not os.path.isdir(inbound_dir):
        return Row(5, "INBOX-NEW", UNKNOWN, f"{inbound_dir} not found")
    threshold = as_of - dt.timedelta(hours=24)
    threshold_ts = threshold.timestamp()
    newer = []
    unreadable_inbox = 0
    for name in os.listdir(inbound_dir):
        if not name.endswith(".md"):
            continue
        full = os.path.join(inbound_dir, name)
        try:
            mtime = os.path.getmtime(full)
        except OSError:
            # ADDED 2026-08-24. This was `continue`: a letter whose mtime could not be read
            # was dropped, so the count of new mail was silently LOW -- and a low number on
            # this check reads as "quiet inbox", which is the flattering direction.
            unreadable_inbox += 1
            continue
        if mtime >= threshold_ts:
            newer.append((mtime, name))
    if unreadable_inbox:
        # A count that could not read every candidate is a LOWER BOUND, never a clean zero.
        return Row(5, "INBOX-NEW", UNKNOWN,
                   f"{unreadable_inbox} inbound file(s) could NOT BE READ; {len(newer)} new "
                   f"since {threshold.isoformat()} is a LOWER BOUND, not a count")
    if not newer:
        return Row(5, "INBOX-NEW", PASS, f"0 files newer than as-of minus 24h ({threshold.isoformat()})")
    newer.sort()
    newest_name = newer[-1][1]
    return Row(5, "INBOX-NEW", WARN, f"{len(newer)} new since {threshold.isoformat()}, newest={newest_name}", mag=len(newer))


# ---------------------------------------------------------------------------
# Check 6 -- PROBE-REGRESSIONS
# ---------------------------------------------------------------------------

def check_probe_regressions(path=PROBE_REGISTRY):
    if not os.path.isfile(path):
        return Row(6, "PROBE-REGRESSIONS", UNKNOWN, f"{path} not found")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    # CORRECTED 2026-08-23. The previous implementation was a flat grep for FAIL/REGRESSED over
    # every table line in the registry. Two defects, and the registry's own virtues caused both:
    #   1. The registry is APPEND-ONLY and never deletes a failure (that is deliberate and right).
    #      A flat grep therefore counts every historical failure forever, so this check could only
    #      ever drift toward permanent WARN -- an alarm that always fires is not an alarm.
    #   2. Worse: a recovery row reads "RECOVERED (was FAIL)". The grep matched the word FAIL
    #      inside the annotation that announces the fix, so RECOVERIES WERE COUNTED AS FAILURES.
    # Net effect: the check reported 9 failing rows when the registry's newest run showed ~5, and
    # it named P16.r1/P4.r2 -- rows already superseded by passing r2/r3 runs. That is precisely the
    # "old rules outranking their amendments" defect this battery exists to catch, living inside
    # the battery. Now: strip historical "(was ...)" annotations, keep only the HIGHEST run per
    # probe id, and judge that row alone.
    was_pat = re.compile(r"\(\s*was\b[^)]*\)", re.IGNORECASE)
    pat = re.compile(r"\bFAIL\b|\bREGRESSED\b|\bstill failing\b", re.IGNORECASE)
    run_pat = re.compile(r"^(?P<base>.+?)\.r(?P<run>\d+)\s*$")

    # base probe id -> (run, line_no, id_cell, judged_text)
    latest = {}
    for i, ln in enumerate(lines, start=1):
        if not ln.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        id_cell = cells[0]
        if not re.match(r"^P\d", id_cell):      # skip header and non-probe rows
            continue
        m = run_pat.match(id_cell)
        base = m.group("base").strip() if m else id_cell
        run = int(m.group("run")) if m else 0
        judged = was_pat.sub("", ln)            # drop "(was FAIL)" style history
        prev = latest.get(base)
        if prev is None or run >= prev[0]:
            latest[base] = (run, i, id_cell, judged)

    hits = [(ln_no, id_cell)
            for base, (run, ln_no, id_cell, judged) in sorted(latest.items())
            if pat.search(judged)]
    if hits:
        sample = ", ".join(f"{iid}@L{ln}" for ln, iid in hits[:4])
        more = "" if len(hits) <= 4 else f" (+{len(hits) - 4} more)"
        return Row(6, "PROBE-REGRESSIONS", WARN, f"{len(hits)} row(s) FAIL/REGRESSED: {sample}{more}", mag=len(hits))
    return Row(6, "PROBE-REGRESSIONS", PASS, "0 rows marked FAIL/REGRESSED")


# ---------------------------------------------------------------------------
# Check 7 -- TREE-DIRTY
# ---------------------------------------------------------------------------

def check_tree_dirty(repo=REPO):
    rc, out, err = run_cmd(["git", "status", "--porcelain"], cwd=repo)
    if rc != 0:
        return Row(7, "TREE-DIRTY", UNKNOWN, f"git status failed: {err[:120]}")
    lines = [ln for ln in out.splitlines() if ln.strip()]
    if lines:
        return Row(7, "TREE-DIRTY", WARN, f"{len(lines)} dirty path(s), e.g. {lines[0].strip()[:90]}", mag=len(lines))
    return Row(7, "TREE-DIRTY", PASS, "clean working tree")


# ---------------------------------------------------------------------------
# Check 8 -- FROZEN-BRANCH
# ---------------------------------------------------------------------------

def check_frozen_branch(repo=REPO, wake_path=WAKE_MD, branch=FROZEN_BRANCH):
    if not os.path.isfile(wake_path):
        return Row(8, "FROZEN-BRANCH", UNKNOWN, f"{wake_path} not found")
    with open(wake_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    m = re.search(r"review SHA `([0-9a-f]{6,40})`", text)
    rc_b, out_b, err_b = run_cmd(["git", "rev-parse", branch], cwd=repo)

    # -- POST-MERGE ARM ------------------------------------------------------
    # No freeze is declared in WAKE.md, or the frozen branch is gone (deleted by its own merge).
    # Assert instead that the reviewed work LANDED and is still an ancestor of main.
    if not m or rc_b != 0:
        why = "no 'review SHA' in WAKE.md" if not m else f"branch {branch!r} gone (merged)"
        main_ref = None
        for cand in ("origin/main", "main"):
            rc_m, _, _ = run_cmd(["git", "rev-parse", "--verify", cand], cwd=repo)
            if rc_m == 0:
                main_ref = cand
                break
        if main_ref is None:
            return Row(8, "FROZEN-BRANCH", UNKNOWN,
                       f"{why}; and neither origin/main nor main resolves -- cannot verify landing")
        rc_a, _, err_a = run_cmd(
            ["git", "merge-base", "--is-ancestor", LANDED_COMMIT, main_ref], cwd=repo)
        if rc_a == 0:
            return Row(8, "FROZEN-BRANCH", PASS,
                       f"no active freeze ({why}); {main_ref} contains {LANDED_COMMIT} -- PR-1 landed")
        rc_e, _, _ = run_cmd(["git", "cat-file", "-e", LANDED_COMMIT + "^{commit}"], cwd=repo)
        if rc_e != 0:
            return Row(8, "FROZEN-BRANCH", UNKNOWN,
                       f"{why}; {LANDED_COMMIT} not present in this clone -- fetch before trusting")
        return Row(8, "FROZEN-BRANCH", WARN,
                   f"{why}; {LANDED_COMMIT} is NOT an ancestor of {main_ref} -- reviewed work is not on main")

    # -- FREEZE-ACTIVE ARM ---------------------------------------------------
    expected = m.group(1)
    tip = out_b.strip()

    if tip.startswith(expected) or expected.startswith(tip[:len(expected)]):
        return Row(8, "FROZEN-BRANCH", PASS, f"{branch}={tip[:12]} matches expected {expected}")

    rc2, _, _ = run_cmd(["git", "merge-base", "--is-ancestor", expected, tip], cwd=repo)
    if rc2 == 0:
        return Row(8, "FROZEN-BRANCH", WARN,
                    f"{branch} tip {tip[:12]} has MOVED PAST expected {expected} -- freeze broken")
    return Row(8, "FROZEN-BRANCH", WARN,
               f"{branch} tip {tip[:12]} != expected {expected} and not a clean descendant -- diverged")


# ---------------------------------------------------------------------------
# Check 9 -- BARRIER-COVERAGE
# ---------------------------------------------------------------------------

INSTANCE_RE = re.compile(r"^(branch-dispatch|close|compact|fold-in)-([0-9a-f]+)-(\d{8}T\d{6})(\d{4})?\.md$")


def parse_instance_ts(ts_str):
    # ts_str like 20260822T080011 ; treat as naive local (offset digits, if present, ignored for
    # a cheap same-clock comparison -- barrier instances are all written by the same seat/host).
    return dt.datetime.strptime(ts_str, "%Y%m%dT%H%M%S")


def check_barrier_coverage(as_of, instances_dir=INSTANCES_DIR, claims_path=WORK_CLAIMS):
    if not os.path.isdir(instances_dir):
        return Row(9, "BARRIER-COVERAGE", UNKNOWN, f"{instances_dir} not found")
    files = sorted(os.listdir(instances_dir))
    counts = {"branch-dispatch": 0, "close": 0, "compact": 0, "fold-in": 0}
    # CORRECTED 2026-08-23. This check counted FILES and called them records. On
    # 2026-08-23 that made it report "compact=4, close=3" and PASS, while 17 of the 28
    # instances -- including ALL THREE closes and 3 of 4 compacts -- were unfilled
    # skeletons that still carry write_barrier_memory.py's own SKELETON stamp. PR-1's
    # promise 5 ("every barrier writes its record") was graded VERIFIED on this count.
    # A skeleton is the tool's receipt that a barrier happened, not a record of what
    # happened at it. Count both, and never let the file count stand alone.
    SKELETON_MARK = "STATUS: SKELETON -- prose unfilled"
    filled = {"branch-dispatch": 0, "close": 0, "compact": 0, "fold-in": 0}
    skeletons = 0
    unreadable_instances = 0
    dispatches = []
    foldins = []
    for name in files:
        m = INSTANCE_RE.match(name)
        if not m:
            continue
        kind, seat, ts_str, _off = m.groups()
        counts[kind] = counts.get(kind, 0) + 1
        try:
            with open(os.path.join(instances_dir, name), "r",
                      encoding="utf-8", errors="replace") as fh:
                is_skeleton = SKELETON_MARK in fh.read()
        except OSError:
            # ADDED 2026-08-24, same class as above: this read `is_skeleton = False`, so an
            # instance file that could not be READ was counted as a FILLED record -- an
            # unreadable file scoring as a good one, in the direction that flatters the count.
            unreadable_instances += 1
            continue
        if is_skeleton:
            skeletons += 1
        else:
            filled[kind] = filled.get(kind, 0) + 1
        try:
            ts = parse_instance_ts(ts_str)
        except ValueError:
            continue
        if kind == "branch-dispatch":
            dispatches.append((ts, name))
        elif kind == "fold-in":
            foldins.append((ts, name))

    as_of_naive = as_of.replace(tzinfo=None)
    claims_rows_text = ""
    if os.path.isfile(claims_path):
        with open(claims_path, "r", encoding="utf-8", errors="replace") as f:
            claims_rows_text = f.read()
    has_done_row = "DONE" in claims_rows_text  # coarse claims-registry caveat check

    unpaired = []
    for ts, name in dispatches:
        age_h = (as_of_naive - ts).total_seconds() / 3600.0
        if age_h < 0 or age_h > 12:
            continue
        has_later_foldin = any(fts >= ts for fts, _ in foldins)
        if has_later_foldin:
            continue
        # claims-registry caveat (Trial C M4): a branch-dispatch with no fold-in FILE is not
        # automatically unfinished -- WORK-CLAIMS.md may record the same lane as DONE by a
        # different mechanism ("pair rule convicts finished work"). Only convict if WORK-CLAIMS
        # itself shows no DONE evidence at all in the window.
        if not has_done_row:
            unpaired.append(name)
        else:
            unpaired.append(name + " (see claims-registry caveat -- verify against WORK-CLAIMS.md)")

    summary = ", ".join(f"{k}={filled.get(k, 0)}/{v} filled" for k, v in counts.items())
    if unpaired:
        return Row(9, "BARRIER-COVERAGE", WARN,
                    f"{summary}; {skeletons} unfilled skeleton(s); "
                    f"{len(unpaired)} dispatch(es) <12h old w/o later fold-in: {unpaired[0][:80]}")
    # A boundary barrier with zero FILLED records is the promise-12 failure mode: the
    # ritual fired, the tool wrote a template, and nobody filled it. That is not coverage.
    empty_boundaries = [k for k in ("compact", "close")
                        if counts.get(k, 0) > 0 and filled.get(k, 0) == 0]
    if empty_boundaries:
        return Row(9, "BARRIER-COVERAGE", WARN,
                   f"{summary}; {skeletons} unfilled skeleton(s); "
                   f"{'/'.join(empty_boundaries)} have files but ZERO filled records")
    return Row(9, "BARRIER-COVERAGE", PASS,
               f"{summary}; {skeletons} unfilled skeleton(s); all <12h dispatches paired")


# ---------------------------------------------------------------------------
# Check 10 -- STRUCTURED-OUTPUT-TRUNCATION (reminder stub, not a live test)
# ---------------------------------------------------------------------------

def check_truncation_stub():
    msg = ("reminder only, per Soul's 08-22 A-WIN letter: a bare JSON array can silently drop to "
           "1 element under provider-side truncation; class bites schema-constrained LIST calls "
           "(retrieve.py --json 'results', probe-registry rows, any structured tool output) -- "
           "wrap list-shaped structured output in a counted/keyed envelope and verify len()==expected, "
           "never trust a bare array's length silently.")
    return Row(10, "STRUCTURED-OUTPUT-TRUNCATION", INFO, msg)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Check 11 -- CRLF-BOOT-SURFACE
# ---------------------------------------------------------------------------
#
# WHY THIS CHECK EXISTS, AND WHY GIT CANNOT REPLACE IT.
#
# On 2026-08-24 `cfl-resident:v9` exited 127 in under 30 seconds. The container log:
#
#     /usr/bin/env: 'bash<CR>': No such file or directory
#
# `docker/tools/entrypoint.sh` had been baked with CRLF line endings -- 479 carriage
# returns -- so its shebang named a program that does not exist: "bash" with a trailing
# carriage return stuck to it.
#
# Here is the part worth reading twice. `.gitattributes` ALREADY carried the rule
# `*.sh text eol=lf`. `core.autocrlf` was ALREADY false. The COMMITTED BLOB HAD ZERO
# CARRIAGE RETURNS. And `git status` reported the file CLEAN.
#
# That is not a git bug. The `text` attribute tells git to normalise line endings when
# it COMPARES, so a CRLF working file diffs clean against an LF blob. Docker COPY does
# not compare -- it copies the bytes that are on disk. So the one instrument everybody
# reaches for to answer "has this file changed" is STRUCTURALLY BLIND to the exact
# corruption that stops the image from booting. No amount of care with git surfaces it.
#
# The class is wider than line endings: a property of the WORKING TREE that the working
# tree's own status command normalises away. The only place the truth lives is the disk
# bytes on the surface Docker actually consumes, so that is what this reads.
#
# BOUND -- stated so nobody reads a PASS as more than it is. This scans the build
# context and the launch mount, which is SOURCE. It does NOT open the built image. An
# image baked before a fix still carries the carriage returns, and this check will
# report PASS while the container still dies. Source-clean is not image-clean; the
# chain is promote -> rebuild -> repoint digest -> and the entrypoint must actually
# exec. Only a boot tests the boot.
#
# BOUND TESTED 2026-08-24 ~17:1x, and the bound stays because the test is not automatic:
#   docker run --rm --entrypoint sh cfl-resident:v12 -c \n#     'find / -xdev -type f \( -name "*.sh" -o -name "*.py" -o -name "*.y*ml" \) > /tmp/L;
#      while read f; do n=$(tr -cd <CR> < "$f" | wc -c); [ $n -gt 0 ] && echo $f; done < /tmp/L'
#   -- <CR> written as a placeholder ON PURPOSE, see the note below.
#   DENOMINATOR 623 files inside the image. CR-carrying: 0.
# The image is clean. The bound is still true -- this check still cannot see an image -- but it
# is no longer an untested caveat, which is a different thing from being no caveat at all.
# The FIRST run of that test over-filtered its find, scanned THREE files, and printed the same
# reassuring zero. A green whose denominator is unprinted is not a green.
#
# AND THE FIRST DRAFT OF THIS VERY COMMENT BROKE THE FILE WITH A CARRIAGE RETURN. The command above
# was pasted with a real CR in it instead of the two characters that name one. Python treats a bare
# CR as a line terminator, so the comment ENDED mid-line and the tail became an unindented statement:
#     IndentationError: unindent does not match any outer indentation level, line 704
# The check that exists to catch carriage returns was disabled by a carriage return, inside the
# paragraph documenting that it had been tested. That is why the placeholder above is spelled out
# rather than written literally, and why this paragraph is not being deleted now that it is fixed.

CR_BYTE = bytes([13])
CRLF_DIRS = (("docker", "tools"), ("docker", "launch"),
             ("docker", "bake-out"), ("docker", "egress-proxy"))
CRLF_EXTS = (".sh", ".py", ".yaml", ".yml", ".json", ".txt", ".conf")


def _has_shebang(path):
    """True if the file opens with #!. ON A READ FAILURE, RETURNS TRUE.

    That is deliberate and it is the opposite of the obvious choice. This returned False on
    OSError until 2026-08-24, which quietly EXCLUDED an unreadable file from the scan
    entirely whenever its extension did not also match -- so the one file we could not
    inspect was the one file we stopped looking at. Failing toward inspection puts it in
    front of the read below, which records it as UNREADABLE and forces the check to UNKNOWN.
    A gate should fail toward looking harder, never toward looking away."""
    try:
        with io.open(path, "rb") as fh:
            return fh.read(2) == b"#!"
    except OSError:
        return True


def crlf_offenders(repo=REPO, dirs=CRLF_DIRS, exts=CRLF_EXTS):
    """(fatal, warn, unreadable) -- files on the boot surface that carry carriage returns.

    UNREADABLE IS A THIRD STATE, ADDED 2026-08-24 AFTER IT COST NOTHING ONLY BY LUCK.
    This function first shipped with `except OSError: continue` -- so a file that could not
    be READ was silently dropped from the scan and the check reported "0 CR bytes", i.e.
    CLEAN. Hours later the whole G: volume stopped returning bytes for twenty minutes while
    directory listings kept working perfectly. In that window this check would have walked
    the tree, failed every read, and certified the boot surface clean.

    Professional found the same class in its own generator the same afternoon -- an
    `except OSError:` that folded unreadable pages into the no-frontmatter bucket, a
    category that already had a legitimate population -- and its statement of why that
    version is sneakier is the one to keep: it does not produce silence, it produces a
    PLAUSIBLE WRONG NUMBER that blends into a known backlog.

    A file that could not be read is UNKNOWN. UNKNOWN dominates a PASS.

    fatal = the file opens with a shebang, so a CR corrupts the interpreter NAME and
            the kernel fails the exec before a single line of the script runs.
    warn  = everything else. Usually tolerated by parsers, never intended, and the
            same authoring slip that produced the fatal one.
    """
    fatal, warn, unreadable = [], [], []
    for parts in dirs:
        root = os.path.join(repo, *parts)
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                if not (fn.endswith(exts) or _has_shebang(fp)):
                    continue
                rel_ = os.path.relpath(fp, repo).replace(os.sep, "/")
                try:
                    with io.open(fp, "rb") as fh:
                        blob = fh.read()
                except OSError as e:
                    unreadable.append((rel_, str(e)[:60]))
                    continue
                n = blob.count(CR_BYTE)
                if not n:
                    continue
                rel = os.path.relpath(fp, repo).replace(os.sep, "/")
                (fatal if _has_shebang(fp) else warn).append((rel, n))
    return sorted(fatal), sorted(warn), sorted(unreadable)


def check_crlf_boot_surface(repo=REPO):
    if not os.path.isdir(os.path.join(repo, "docker")):
        return Row(11, "CRLF-BOOT-SURFACE", UNKNOWN, "docker/ not found under this repo")
    fatal, warn, unreadable = crlf_offenders(repo=repo)
    mag = len(fatal) + len(warn)
    if unreadable and not fatal:
        first, err = unreadable[0]
        return Row(11, "CRLF-BOOT-SURFACE", UNKNOWN,
                   "%d file(s) on the boot surface could NOT BE READ, e.g. %s (%s). "
                   "A scan that could not read the bytes cannot report them clean -- "
                   "UNKNOWN, never PASS." % (len(unreadable), first, err))
    if fatal:
        first, n = fatal[0]
        more = (" +%d more" % (len(fatal) - 1)) if len(fatal) > 1 else ""
        return Row(11, "CRLF-BOOT-SURFACE", WARN,
                   "%d SHEBANG file(s) carry CR -- the container exits 127 at boot: "
                   "%s (%d CR)%s. git reports these CLEAN; it cannot see them."
                   % (len(fatal), first, n, more), mag=mag)
    if warn:
        first, n = warn[0]
        more = (" +%d more" % (len(warn) - 1)) if len(warn) > 1 else ""
        return Row(11, "CRLF-BOOT-SURFACE", WARN,
                   "%d non-shebang file(s) carry CR on the boot surface: %s (%d CR)%s. "
                   "Not fatal, not intended." % (len(warn), first, n, more), mag=mag)
    return Row(11, "CRLF-BOOT-SURFACE", PASS,
               "0 CR bytes, every file READ, on the docker build+mount SOURCE surface "
               "(an image baked before a fix still carries it -- only a boot tests boot)",
               mag=0)


def selftest_check11():
    """Both verdicts, plus the negative controls that make the first one mean anything."""
    import tempfile
    fails = []
    tmp = tempfile.mkdtemp()
    tools = os.path.join(tmp, "docker", "tools")
    os.makedirs(tools)

    clean = os.path.join(tools, "clean.sh")
    with io.open(clean, "wb") as fh:
        fh.write(b"#!/usr/bin/env bash\necho ok\n")

    # PASS arm: a clean surface must report zero.
    r = check_crlf_boot_surface(repo=tmp)
    if r.status != PASS or r.mag != 0:
        fails.append("clean surface did not PASS with mag 0 (got %s / %s)" % (r.status, r.mag))

    # WARN arm, fatal class: a CRLF shebang must be caught and named fatal.
    bad = os.path.join(tools, "boot.sh")
    with io.open(bad, "wb") as fh:
        fh.write(b"#!/usr/bin/env bash\r\necho ok\r\n")
    r = check_crlf_boot_surface(repo=tmp)
    if r.status != WARN or "SHEBANG" not in r.evidence:
        fails.append("CRLF shebang was not reported as a fatal-class hit (%s)" % r.evidence[:60])
    if r.mag != 1:
        fails.append("expected mag 1 after one offender, got %s" % r.mag)

    # NEGATIVE CONTROL 1 -- the clean file must NOT be listed. A scanner that returned
    # every file it walked would pass the test above while being useless.
    fatal, _warn, _unr = crlf_offenders(repo=tmp)
    if any("clean.sh" in rel for rel, _ in fatal):
        fails.append("NEGATIVE CONTROL: an LF file was reported as an offender")

    # NEGATIVE CONTROL 2 -- a non-shebang CRLF file must land in warn, not fatal.
    os.makedirs(os.path.join(tmp, "docker", "launch"))
    y = os.path.join(tmp, "docker", "launch", "manifest.yaml")
    with io.open(y, "wb") as fh:
        fh.write(b"a: 1\r\nb: 2\r\n")
    fatal, warn, _unr = crlf_offenders(repo=tmp)
    if any("manifest.yaml" in rel for rel, _ in fatal):
        fails.append("NEGATIVE CONTROL: a non-shebang file was classed fatal")
    if not any("manifest.yaml" in rel for rel, _ in warn):
        fails.append("NEGATIVE CONTROL: a non-shebang CRLF file was missed entirely")

    # NEGATIVE CONTROL 4 -- AN UNREADABLE FILE MUST FORCE UNKNOWN, NEVER PASS.
    # This is the arm the 2026-08-24 G: outage would have exercised for real: every read
    # failed for twenty minutes while directory listings kept working, so a scanner that
    # skips unreadable files walks a full tree, reads nothing, and reports it clean.
    # io.open is patched rather than chmod'd because file permissions do not produce a read
    # failure for the owner on Windows, and a control that cannot fire on the platform it
    # runs on is not a control.
    clean2 = tempfile.mkdtemp()
    os.makedirs(os.path.join(clean2, "docker", "tools"))
    only = os.path.join(clean2, "docker", "tools", "boot.sh")
    with io.open(only, "wb") as fh:
        fh.write(b"#!/usr/bin/env bash" + bytes([10]) + b"echo ok" + bytes([10]))
    _real_open = io.open

    def _boom(path, *a, **k):
        if isinstance(path, str) and path.replace(os.sep, "/").endswith("tools/boot.sh") and "b" in str(k.get("mode", a[0] if a else "")):
            raise OSError(22, "Invalid argument")
        return _real_open(path, *a, **k)
    io.open = _boom
    try:
        r = check_crlf_boot_surface(repo=clean2)
    finally:
        io.open = _real_open
    if r.status != UNKNOWN:
        fails.append("NEGATIVE CONTROL: an UNREADABLE file rendered %s, not UNKNOWN "
                     "(a scan that read nothing must never certify clean)" % r.status)

    # NEGATIVE CONTROL 3 -- absence of docker/ is UNKNOWN, never PASS. A check that
    # cannot run must not render as a clean bill.
    empty = tempfile.mkdtemp()
    r = check_crlf_boot_surface(repo=empty)
    if r.status != UNKNOWN:
        fails.append("NEGATIVE CONTROL: missing docker/ rendered as %s, not UNKNOWN" % r.status)

    return fails


# ---------------------------------------------------------------------------
# Check 12 -- CORPUS-WATERMARK
# ---------------------------------------------------------------------------
#
# WHY. The Secretary raised this on 2026-08-24, and it is the sharper half of a
# question CFL had already answered badly:
#
#     "The freshest export's CONTENT DATE and its FILE date are different facts.
#      A corpus can be fully extracted and still stop days before today."
#
# CFL had just reported a clean census -- 6 zips, 32 extracted dirs, every zip
# extracted -- and that census answers "is anything unextracted", which is a question
# about FILES. Nobody was measuring the question that matters for the wiki: HOW FAR
# BEHIND TODAY DOES THE NEWEST EXPORT'S CONTENT STOP?
#
# `[measured 2026-08-24]` the answer was SEVEN DAYS. The newest export's newest
# message is 2026-08-17T02:16:17Z. Every artifact in this repo that stamps freshness
# as "corpus current through export 2026-08-16" is quoting a FILE date, is a day off,
# and -- far worse -- says nothing about the growing hole behind it.
#
# This is the same root cause as everything else on 2026-08-24: the number that needed
# comparing lived in prose ("current through export ..."), was transcribed by hand,
# and had nothing able to notice when the world moved past it. So it is derived here,
# at the moment of use, from the bytes.
#
# HOW. A streaming regex over the newest extracted conversations.json for the maximum
# ISO timestamp. Measured at 0.21 s over 89 MB, which is cheap enough to run at every
# barrier -- the whole point being that it appears where someone already looks rather
# than in a file somebody has to remember to open.
#
# BOUNDS, all three parts:
#   1. NOT MEASURED: whether a NEWER export exists that has not been downloaded. An
#      export is REQUESTED before it lands, and in that window every search returns
#      exactly what it returns when no export was ever requested. This check reports
#      what is ON DISK; it can never distinguish "no newer export" from "a newer
#      export is still in flight".
#   2. WHY: the request lives in Jon's email, which nothing here reads.
#   3. SO: a PASS means the corpus on disk is recent. It never means the corpus is
#      complete, and a WARN is as likely to mean "nobody exported" as "the export
#      failed". It reports a distance, not a fault.

WATERMARK_TS_RE = re.compile(
    rb'"(?:updated_at|created_at)":\s*"(20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d)')
WATERMARK_WARN_DAYS = 7
ZIP_DIR = ("raw", "Anthropic_zips")


def newest_export_dir(repo=REPO, zip_dir=ZIP_DIR):
    """The extracted-* directory with the highest epoch in its NAME.

    Sorted by the epoch the exporter stamped, not by mtime: an old export re-extracted
    today would have the newest mtime and the oldest content, which is precisely the
    file-date-for-content-date substitution this check exists to stop making.
    """
    root = os.path.join(repo, *zip_dir)
    if not os.path.isdir(root):
        return None
    best, best_n = None, -1
    for name in os.listdir(root):
        if not name.startswith("extracted-"):
            continue
        tail = name[len("extracted-"):]
        if not tail.isdigit():
            continue
        n = int(tail)
        if n > best_n:
            path = os.path.join(root, name)
            if os.path.isdir(path):
                best, best_n = path, n
    return best


def corpus_watermark(export_dir):
    """Max ISO timestamp inside conversations.json, or None if unreadable."""
    target = os.path.join(export_dir, "conversations.json")
    if not os.path.isfile(target):
        return None
    mx = b""
    try:
        with io.open(target, "rb") as fh:
            while True:
                chunk = fh.read(8 << 20)
                if not chunk:
                    break
                chunk += fh.read(64)   # overlap so a timestamp split across reads still matches
                for m in WATERMARK_TS_RE.finditer(chunk):
                    if m.group(1) > mx:
                        mx = m.group(1)
    except OSError:
        return None
    return mx.decode("ascii") if mx else None


def check_corpus_watermark(as_of, repo=REPO):
    d = newest_export_dir(repo=repo)
    if d is None:
        return Row(12, "CORPUS-WATERMARK", UNKNOWN,
                   "no extracted-<epoch> export directory found -- UNKNOWN, not 'no gap'")
    wm = corpus_watermark(d)
    if wm is None:
        return Row(12, "CORPUS-WATERMARK", UNKNOWN,
                   "%s has no readable conversations.json -- a check that cannot run is not a pass"
                   % os.path.basename(d))
    try:
        wm_dt = dt.datetime.strptime(wm, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return Row(12, "CORPUS-WATERMARK", UNKNOWN, "unparseable watermark %r" % wm[:32])
    ref = as_of.replace(tzinfo=None) if getattr(as_of, "tzinfo", None) else as_of
    age = (ref - wm_dt).days
    tail = ("%s content ends %sZ, %d day(s) behind. A NEWER export may exist and not be "
            "downloaded -- this reads disk only." % (os.path.basename(d), wm, age))
    if age >= WATERMARK_WARN_DAYS:
        return Row(12, "CORPUS-WATERMARK", WARN,
                   "claude.ai corpus is %d days stale: %s" % (age, tail), mag=age)
    return Row(12, "CORPUS-WATERMARK", PASS, tail, mag=age)


def selftest_check12():
    """Both verdicts and the controls, on synthetic exports -- never the real 89 MB one."""
    import tempfile
    fails = []
    tmp = tempfile.mkdtemp()
    zroot = os.path.join(tmp, "raw", "Anthropic_zips")
    os.makedirs(os.path.join(zroot, "extracted-1000"))
    os.makedirs(os.path.join(zroot, "extracted-2000"))

    def put(d, ts):
        with io.open(os.path.join(zroot, d, "conversations.json"), "wb") as fh:
            fh.write(b'[{"updated_at": "' + ts.encode() + b'", "created_at": "2026-01-01T00:00:00"}]')

    # NEGATIVE CONTROL 1 -- the OLDER dir gets the NEWER content and a fresh mtime.
    # A check that picked by mtime, or scanned every dir, would read 2026-08-20 here.
    # The right answer is the highest-epoch dir, so 2026-08-10.
    put("extracted-2000", "2026-08-10T00:00:00")
    put("extracted-1000", "2026-08-20T00:00:00")
    as_of = dt.datetime(2026, 8, 24, 12, 0, 0)
    r = check_corpus_watermark(as_of, repo=tmp)
    if "2026-08-10" not in r.evidence:
        fails.append("NEGATIVE CONTROL: picked by mtime or scanned all dirs, not by export epoch")
    if r.status != WARN or r.mag != 14:
        fails.append("14-day gap did not WARN with mag 14 (got %s / %s)" % (r.status, r.mag))

    # PASS arm -- inside the bar.
    put("extracted-2000", "2026-08-23T00:00:00")
    r = check_corpus_watermark(as_of, repo=tmp)
    if r.status != PASS or r.mag != 1:
        fails.append("1-day gap did not PASS with mag 1 (got %s / %s)" % (r.status, r.mag))

    # NEGATIVE CONTROL 2 -- a timestamp split across the read boundary must still match.
    big = os.path.join(zroot, "extracted-3000")
    os.makedirs(big)
    with io.open(os.path.join(big, "conversations.json"), "wb") as fh:
        fh.write(b'{"pad": "' + b"z" * ((8 << 20) - 20) + b'", "updated_at": "2026-08-22T00:00:00"}')
    r = check_corpus_watermark(as_of, repo=tmp)
    if "2026-08-22" not in r.evidence:
        fails.append("NEGATIVE CONTROL: a timestamp spanning the chunk boundary was missed")

    # NEGATIVE CONTROL 3 -- nothing on disk is UNKNOWN, never PASS.
    empty = tempfile.mkdtemp()
    r = check_corpus_watermark(as_of, repo=empty)
    if r.status != UNKNOWN:
        fails.append("NEGATIVE CONTROL: absent export dir rendered %s, not UNKNOWN" % r.status)

    # NEGATIVE CONTROL 4 -- a dir with no conversations.json is UNKNOWN, not a clean bill.
    tmp2 = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp2, "raw", "Anthropic_zips", "extracted-9000"))
    r = check_corpus_watermark(as_of, repo=tmp2)
    if r.status != UNKNOWN:
        fails.append("NEGATIVE CONTROL: unreadable export rendered %s, not UNKNOWN" % r.status)

    return fails


def selftest_check12_results():
    fails = selftest_check12()
    results = {"12-watermark": not fails}
    for i, msg in enumerate(fails):
        results["12-f%d %s" % (i, msg[:44])] = False
    return results

def run_battery(as_of, topic, session, repo=REPO):
    rows = []
    rows.append(check_wwja(topic, repo=repo))
    rows.append(check_index_stale(repo=repo))
    rows.append(check_hook_liveness(session))
    rows.append(check_open_takes(path=os.path.join(repo, "exchange", "WORK-CLAIMS.md")))
    rows.append(check_inbox_new(as_of, inbound_dir=os.path.join(repo, "exchange", "inbound")))
    rows.append(check_probe_regressions(path=os.path.join(repo, "wiki", "tracker", "PROBE-REGISTRY.md")))
    rows.append(check_tree_dirty(repo=repo))
    rows.append(check_frozen_branch(repo=repo, wake_path=os.path.join(repo, "exchange", "WAKE.md")))
    rows.append(check_barrier_coverage(as_of,
                                        instances_dir=os.path.join(repo, "exchange", "memory-core-v0", "instances"),
                                        claims_path=os.path.join(repo, "exchange", "WORK-CLAIMS.md")))
    rows.append(check_truncation_stub())
    rows.append(check_crlf_boot_surface(repo=repo))
    rows.append(check_corpus_watermark(as_of, repo=repo))
    return rows


def print_report(rows, as_of):
    print(f"HEARTBEAT BATTERY -- as-of {as_of.isoformat()}")
    print("-" * 78)
    loud = [r for r in rows if r.status in (WARN, UNKNOWN)]
    quiet = [r for r in rows if r.status not in (WARN, UNKNOWN)]
    for r in quiet:
        print(r.line())
    if loud:
        print("-" * 78)
        print("ATTENTION:")
        for r in loud:
            print(r.line())
    print("-" * 78)
    n_pass = sum(1 for r in rows if r.status == PASS)
    n_warn = sum(1 for r in rows if r.status == WARN)
    n_unk = sum(1 for r in rows if r.status == UNKNOWN)
    n_info = sum(1 for r in rows if r.status == INFO)
    print(f"SUMMARY: {n_pass} PASS, {n_warn} WARN, {n_unk} UNKNOWN, {n_info} INFO ({len(rows)} checks)")
    return n_warn, n_unk


# ---------------------------------------------------------------------------
# Selftest -- fabricated scratch repo-let exercising checks 4, 5, 6, 9,
# both PASS and WARN directions.
# ---------------------------------------------------------------------------

def build_scratch_repo(tmpdir):
    os.makedirs(os.path.join(tmpdir, "exchange", "inbound"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "exchange", "memory-core-v0", "instances"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "wiki", "tracker"), exist_ok=True)
    return tmpdir


def selftest_check4():
    results = {}
    with tempfile.TemporaryDirectory() as td:
        # PASS direction: every TAKE has a later DONE
        p_pass = os.path.join(td, "claims-pass.md")
        with open(p_pass, "w", encoding="utf-8") as f:
            f.write("| at | seat | verb | work item | pointer |\n|---|---|---|---|---|\n")
            f.write("| t1 | s | TAKE | thing-a | x |\n")
            f.write("| t2 | s | DONE | thing-a | x |\n")
        r = check_open_takes(path=p_pass, tail=40)
        results["4-pass"] = r.status == PASS

        # WARN direction: a TAKE with no closing row
        p_warn = os.path.join(td, "claims-warn.md")
        with open(p_warn, "w", encoding="utf-8") as f:
            f.write("| at | seat | verb | work item | pointer |\n|---|---|---|---|---|\n")
            f.write("| t1 | s | TAKE | thing-b | x |\n")
        r = check_open_takes(path=p_warn, tail=40)
        results["4-warn"] = r.status == WARN
    return results


def selftest_check5():
    results = {}
    as_of = dt.datetime(2026, 8, 22, 20, 0, 0)
    with tempfile.TemporaryDirectory() as td:
        inbound = os.path.join(td, "inbound")
        os.makedirs(inbound, exist_ok=True)
        r = check_inbox_new(as_of, inbound_dir=inbound)
        results["5-pass"] = r.status == PASS

        newf = os.path.join(inbound, "fresh.md")
        with open(newf, "w", encoding="utf-8") as f:
            f.write("hi")
        os.utime(newf, (as_of.timestamp(), as_of.timestamp()))
        r = check_inbox_new(as_of, inbound_dir=inbound)
        results["5-warn"] = r.status == WARN
    return results


def selftest_check6():
    results = {}
    with tempfile.TemporaryDirectory() as td:
        p_pass = os.path.join(td, "probes-pass.md")
        with open(p_pass, "w", encoding="utf-8") as f:
            f.write("| id | last-result |\n|---|---|\n| P1 | TRUSTED |\n")
        r = check_probe_regressions(path=p_pass)
        results["6-pass"] = r.status == PASS

        p_warn = os.path.join(td, "probes-warn.md")
        with open(p_warn, "w", encoding="utf-8") as f:
            f.write("| id | last-result |\n|---|---|\n| P1 | FAIL — bad thing |\n| P2 | REGRESSED |\n")
        r = check_probe_regressions(path=p_warn)
        results["6-warn"] = r.status == WARN and "P1" in r.evidence
    return results


def selftest_check9():
    results = {}
    as_of = dt.datetime(2026, 8, 22, 20, 0, 0)
    with tempfile.TemporaryDirectory() as td:
        inst = os.path.join(td, "instances")
        os.makedirs(inst, exist_ok=True)
        claims = os.path.join(td, "claims.md")

        # PASS direction: dispatch has a later fold-in
        with open(os.path.join(inst, "branch-dispatch-aaaa-20260822T180000.md"), "w") as f:
            f.write("x")
        with open(os.path.join(inst, "fold-in-aaaa-20260822T190000.md"), "w") as f:
            f.write("x")
        with open(claims, "w", encoding="utf-8") as f:
            f.write("| at | seat | verb | work item | pointer |\n|---|---|---|---|---|\n")
        r = check_barrier_coverage(as_of, instances_dir=inst, claims_path=claims)
        results["9-pass"] = r.status == PASS

        # WARN direction: fresh dispatch (<12h), no fold-in, no DONE row in claims either
        with open(os.path.join(inst, "branch-dispatch-bbbb-20260822T193000.md"), "w") as f:
            f.write("x")
        r = check_barrier_coverage(as_of, instances_dir=inst, claims_path=claims)
        results["9-warn"] = r.status == WARN
    return results


def selftest_direction():
    """DIRECTION, exercised in every verdict -- a check watched only to pass is untested.

    The WORSE case is the one this whole block exists for: it is the CFL instance measured on
    2026-08-24, where PROBE-REGRESSIONS moved 9 -> 10 across a sitting and nothing said so.
    """
    r = {}
    base = {"as_of": "2026-08-23T00:00:00+00:00",
            "checks": {"OPEN-TAKES": {"mag": 7}, "PROBE-REGRESSIONS": {"mag": 9},
                       "TREE-DIRTY": {"mag": 3}}}
    rows = [Row(4, "OPEN-TAKES", WARN, "e", mag=7),
            Row(6, "PROBE-REGRESSIONS", WARN, "e", mag=10),
            Row(7, "TREE-DIRTY", WARN, "e", mag=1),
            Row(5, "INBOX-NEW", WARN, "e", mag=4),
            Row(1, "WWJA", PASS, "e")]
    annotate_direction(rows, base)
    d = {x.name: x.delta for x in rows}
    r["dir-worse"] = d["PROBE-REGRESSIONS"].startswith("<< WORSE") and "9 -> 10" in d["PROBE-REGRESSIONS"]
    r["dir-same"] = d["OPEN-TAKES"].startswith("== unchanged")
    r["dir-better"] = d["TREE-DIRTY"].startswith("<< better") and "VERIFY" in d["TREE-DIRTY"]
    r["dir-new"] = d["INBOX-NEW"].startswith("<< NO BASELINE")
    # NEGATIVE CONTROL: a row with no magnitude must get NO direction at all. Without this, a
    # function that stamped every row would pass all four cases above.
    r["dir-nomag-silent"] = d["WWJA"] == ""
    # NEGATIVE CONTROL: with an EMPTY baseline every magnitude row must read NO BASELINE, never
    # "unchanged" -- absence of a baseline is UNKNOWN, and UNKNOWN must not render as steady.
    rows2 = [Row(4, "OPEN-TAKES", WARN, "e", mag=7)]
    annotate_direction(rows2, {})
    r["dir-empty-baseline-is-unknown"] = rows2[0].delta.startswith("<< NO BASELINE")

    # A baseline row explicitly marked UNUSABLE must NOT produce a direction. This is the
    # cross-instrument case that shipped a false "WORSE: 9 -> 10 (+1)" on 2026-08-24.
    b_bad = {"as_of": "2026-08-23T00:00:00+00:00",
             "checks": {"PROBE-REGRESSIONS": {"mag": 9, "confidence": "UNUSABLE -- CROSS-INSTRUMENT"}}}
    r3 = [Row(6, "PROBE-REGRESSIONS", WARN, "e", mag=10)]
    annotate_direction(r3, b_bad)
    r["dir-unusable-refuses-verdict"] = ("NO USABLE BASELINE" in r3[0].delta
                                         and "WORSE" not in r3[0].delta)

    # A RECALLED baseline that IS usable must still say so inline -- the verdict stands, the
    # provenance rides with it.
    b_rec = {"as_of": "2026-08-23T00:00:00+00:00",
             "checks": {"OPEN-TAKES": {"mag": 5, "provenance": "recalled -- WAKE.md prose",
                                       "confidence": "usable"}}}
    r4 = [Row(4, "OPEN-TAKES", WARN, "e", mag=7)]
    annotate_direction(r4, b_rec)
    r["dir-recalled-is-labelled"] = ("WORSE" in r4[0].delta
                                     and "RECALLED, not measured" in r4[0].delta)

    # AGE: past the bar, every verdict is UNKNOWN -- permanent-BETTER is the rot direction, and
    # nobody investigates good news.
    import datetime as _dt
    b_old = {"as_of": "2026-01-01T00:00:00+00:00", "checks": {"TREE-DIRTY": {"mag": 99}}}
    r5 = [Row(7, "TREE-DIRTY", WARN, "e", mag=1)]
    annotate_direction(r5, b_old, as_of=_dt.datetime(2026, 8, 24, tzinfo=_dt.timezone.utc))
    r["dir-stale-baseline-is-unknown"] = ("UNKNOWN" in r5[0].delta and "better" not in r5[0].delta)
    return r



def selftest_check11_results():
    """Adapt check 11's failure LIST to the battery's name->bool map.

    A failure is surfaced under its own name rather than collapsed into one boolean,
    so a reader sees WHICH arm broke. A single "11 FAIL" would be the same defect this
    check exists to catch: a true statement with the discriminating detail removed.
    """
    fails = selftest_check11()
    results = {"11-crlf": not fails}
    for i, msg in enumerate(fails):
        results["11-f%d %s" % (i, msg[:48])] = False
    return results

def run_selftest():
    all_results = {}
    all_results.update(selftest_direction())
    all_results.update(selftest_check4())
    all_results.update(selftest_check5())
    all_results.update(selftest_check6())
    all_results.update(selftest_check9())
    all_results.update(selftest_check11_results())
    all_results.update(selftest_check12_results())
    print("SELFTEST -- heartbeat_battery.py")
    print("-" * 60)
    ok = True
    for name, passed in sorted(all_results.items()):
        status = "OK" if passed else "FAIL"
        if not passed:
            ok = False
        print(f"  {name:34s} {status}")
    print("-" * 60)
    print("SELFTEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Heartbeat battery -- ~10-check barrier battery.")
    ap.add_argument("--as-of", default=None,
                     help="REQUIRED (unless --selftest): full ISO timestamp, e.g. 2026-08-22T21:00:00-05:00")
    ap.add_argument("--topic", default=None, help="topic for the WWJA retrieve.py probe (check 1)")
    ap.add_argument("--session", default=None, help="session id/prefix for hook-liveness (check 3)")
    ap.add_argument("--strict", action="store_true", help="nonzero exit on any WARN")
    ap.add_argument("--update-baseline", action="store_true",
                    help="record this run's counts as the comparison baseline. DELIBERATE ONLY -- "
                         "a self-updating baseline can never show a regression.")
    ap.add_argument("--strict-direction", action="store_true",
                    help="nonzero exit only when a count got WORSE or is NEW. This is the flag "
                         "that is safe to wire into a gate: --strict fires forever on a standing "
                         "WARN and is therefore ignored, which is the defect this addresses.")
    ap.add_argument("--selftest", action="store_true", help="run the scratch-repo selftest and exit")
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    if not args.__dict__.get("as_of"):
        print("ERROR: --as-of is required (full ISO timestamp; no now() default in this repo)."
              " Pass --selftest to run the offline selftest instead.", file=sys.stderr)
        return 2
    try:
        as_of = parse_iso(args.as_of)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    rows = run_battery(as_of, args.topic, args.session)
    baseline = load_baseline()
    annotate_direction(rows, baseline, as_of=as_of)
    n_warn, n_unk = print_report(rows, as_of)
    if not baseline:
        print("\nNO BASELINE ON DISK. Every direction above reads NO BASELINE, which is UNKNOWN,")
        print("not 'steady'. Run --update-baseline once to establish one.")
    if args.update_baseline:
        pth = write_baseline(rows, as_of)
        print(f"\nBASELINE WRITTEN: {pth}")
        print("Deliberate, and never automatic: a baseline that moved on every run could never")
        print("show a regression, because it would always have moved to meet what it found.")

    if args.strict_direction:
        worse = [r for r in rows if r.delta.startswith("<< WORSE") or r.delta.startswith("<< NO BASELINE")]
        if worse:
            print(f"\nSTRICT-DIRECTION: {len(worse)} check(s) WORSE or NEW -- "
                  + ", ".join(r.name for r in worse))
            return 1
    if args.strict and n_warn > 0:
        return 1
    return 0


if __name__ == "__main__":
    # Exit 3, never 1, when the battery itself dies -- see the EXIT CODES block at the top.
    # A crash must not be spellable as a finding, in either direction: reported as a finding
    # it is a false red that gets muted, and muted it is a false green.
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as _e:                     # noqa: BLE001 -- deliberate, see above
        import traceback
        traceback.print_exc()
        print("", file=sys.stderr)
        print("EXIT 3 -- THE BATTERY COULD NOT RUN. This is NOT a finding and must not be "
              "read as one: no check above completed, so every verdict is UNKNOWN.",
              file=sys.stderr)
        sys.exit(3)
