#!/usr/bin/env python3
"""The exact current time, from data already on disk.

WHY THIS EXISTS
---------------
On 2026-08-03 Jon said: *"Perhaps it is time for you to properly mine temporal context...
You've had many errors in the past. For example even now you could have chosen to get the
exact time and you chose not to."*

He was right, and the record is specific. That morning the coordinator stamped a turn
`02:31 CDT` for a turn that actually happened near `06:55 CDT` — **over four hours off** — and
caught it only by noticing a file mtime. A wayfinder consult the same morning stamped
`ESTIMATED` while the ground truth was sitting in its own session file. The `temporal-context`
and `session-order` skills have **zero evals ever run** against them.

The failure is not that the clock was hard to read. It is that **nobody read it.** Every record
Claude Code writes to a session JSONL carries an ISO-8601 `timestamp` in UTC. The newest one is
the current time to within seconds. `ESTIMATED` is, in Claude Code, almost always a choice not
to look.

THE THREE THINGS THAT MAKE A NAIVE VERSION WRONG
------------------------------------------------
Each of these was measured on this machine, not assumed:

1. **The last line has no timestamp.** A session JSONL ends with bookkeeping records
   (`bridge-session`, `last-prompt`, `mode`, `permission-mode`) that carry no `timestamp` field
   at all. `tail -1 | jq .timestamp` returns null. Timestamps are also not strictly ordered in
   file order, because sidechain writes interleave. **So we scan for the max, never the last.**

2. **The main session file goes stale while subagents run.** Measured live: the top-level file's
   newest record was **39s** behind the OS clock while a subagent file under
   `<uuid>/subagents/` was **1.7s** behind. The main thread writes nothing while it waits on a
   subagent, so a clock reading only the top-level file drifts by the length of the subagent run
   and then reports that drift as clock skew. **That is a false alarm generator**, and an alarm
   that fires when nothing is wrong is the failure mode this program has committed most often.
   So the newest timestamp is taken across the session file *and* its sidechain files.

3. **`zoneinfo` does not work on this machine.** `ZoneInfo("America/Chicago")` raises
   `ZoneInfoNotFoundError` — Windows ships no tz database and the `tzdata` package is not
   installed. A clock that imports zoneinfo and trusts it would crash here, on the one machine
   it has to run on. So the US Central rule is implemented directly as a fallback (that is the
   *rule*, not a hardcoded offset — DST is computed per-instant), and the resolution path is
   always reported as `tz_source` so nobody has to guess which one answered.

WHAT IT REPORTS
---------------
  newest record timestamp   UTC and America/Chicago  <- this is "now"
  first record timestamp    session start
  elapsed                   session duration
  records                   total / timestamped
  file mtime                independent cross-check on the parse
  OS clock delta            newest-record vs system clock

WHICH CLOCK IS "NOW" -- AND WHEN THE RECORD CLOCK LIES
------------------------------------------------------
The newest *record* is when work last happened. The *OS clock* is now. During active work they
are the same to within a second, which is why the record clock is a good answer and a good
cross-check. **They come apart during an idle gap.** If Jon walks away for three hours and then
types, the newest record is three hours old -- so a record-derived stamp is three hours stale at
precisely the moment someone asks what time it is.

That is the normal case for a `UserPromptSubmit` hook, so the source is selectable:

  --stamp-source record   (default) when work last happened; the cross-checkable one
  --stamp-source os       true wall-clock now; correct across idle gaps

Neither is "the right one" unconditionally, which is why this is a flag and not a guess.

THE DELTA IS THE DIAGNOSTIC
---------------------------
The newest record is always *slightly* behind the OS clock — it was written a moment ago. A
small positive delta is health. A large delta means one of two things, and both matter more
than the time itself:

  * the picked session is **not the live one** (stale file, wrong project dir), so every
    number above it is describing some other session; or
  * the two clocks genuinely disagree.

Either way the answer is not "here is the time." It is "do not trust this until you look."
**A clock that silently reads the wrong session is worse than no clock**, so the picked file is
named on every single run, never only on request.

Usage:
    python scripts/audit/session_clock.py
    python scripts/audit/session_clock.py --format stamp      # [YYYY-MM-DD HH:MM CDT]
    python scripts/audit/session_clock.py --format json
    python scripts/audit/session_clock.py --session <uuid>
    python scripts/audit/session_clock.py --self-test

Exit: 0 ok
      1 skew above --max-skew under --strict
      2 no session file could be identified, or none of its records carry a timestamp
        (**never a guess in a confident format** — an unreadable clock is UNKNOWN, not "now")
      3 self-test failure
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS_ROOT = Path.home() / ".claude" / "projects"

# The newest record is written a moment before we read it; a few seconds is normal health.
DEFAULT_MAX_SKEW_SEC = 300


# --------------------------------------------------------------------------
# Timezone: America/Chicago, resolved honestly
# --------------------------------------------------------------------------
def _nth_weekday(year: int, month: int, weekday: int, n: int) -> datetime:
    """The nth <weekday> of a month (weekday: Monday=0 .. Sunday=6), naive UTC midnight."""
    first = datetime(year, month, 1, tzinfo=timezone.utc)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def _central_by_rule(dt_utc: datetime) -> tuple[timedelta, str]:
    """US Central offset for an instant, by the post-2007 federal DST rule.

    DST begins the second Sunday of March at 02:00 local standard time (= 08:00 UTC)
    and ends the first Sunday of November at 02:00 local daylight time (= 07:00 UTC).

    This computes DST per-instant. It is the rule, not a fixed offset.
    """
    y = dt_utc.year
    start = _nth_weekday(y, 3, 6, 2).replace(hour=8)   # 2nd Sunday March, 08:00 UTC
    end = _nth_weekday(y, 11, 6, 1).replace(hour=7)    # 1st Sunday Nov,   07:00 UTC
    if start <= dt_utc < end:
        return timedelta(hours=-5), "CDT"
    return timedelta(hours=-6), "CST"


def to_central(dt_utc: datetime) -> tuple[datetime, str, str]:
    """Convert an aware UTC datetime to America/Chicago.

    Returns (local_datetime, abbrev, tz_source). Prefers the tz database when it is actually
    usable; falls back to the DST rule. The source is reported, never assumed.
    """
    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo("America/Chicago")
        local = dt_utc.astimezone(tz)
        abbrev = local.tzname() or ""
        # Guard: a tzdata stub could hand back something unusable.
        if abbrev in ("CDT", "CST"):
            return local, abbrev, "zoneinfo:America/Chicago"
    except Exception:
        pass

    offset, abbrev = _central_by_rule(dt_utc)
    return dt_utc.astimezone(timezone(offset, abbrev)), abbrev, "rule:us-central-dst"


def fmt_stamp(dt_utc: datetime) -> str:
    """The house format, exactly: [YYYY-MM-DD HH:MM CDT]"""
    local, abbrev, _ = to_central(dt_utc)
    return f"[{local.strftime('%Y-%m-%d %H:%M')} {abbrev}]"


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------
# Cheap pre-filter so we only json.loads lines that could carry a timestamp.
_TS_HINT = re.compile(rb'"timestamp"\s*:\s*"')


def parse_iso(value: str) -> datetime | None:
    """Parse an ISO-8601 timestamp to an aware UTC datetime, or None."""
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def scan_file(path: Path) -> dict:
    """Scan one JSONL for its timestamp extremes.

    Returns {first, newest, records, timestamped, malformed}. Timestamps are NOT assumed
    ordered — sidechain writes interleave and trailing bookkeeping records carry none — so
    this takes min/max over every record rather than reading the ends.
    """
    first: datetime | None = None
    newest: datetime | None = None
    records = 0
    timestamped = 0
    malformed = 0

    with open(path, "rb") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            records += 1
            if not _TS_HINT.search(raw):
                continue
            try:
                rec = json.loads(raw.decode("utf-8", "replace"))
            except (ValueError, UnicodeDecodeError):
                malformed += 1
                continue
            if not isinstance(rec, dict):
                continue
            dt = parse_iso(rec.get("timestamp"))
            if dt is None:
                continue
            timestamped += 1
            if first is None or dt < first:
                first = dt
            if newest is None or dt > newest:
                newest = dt

    return {
        "first": first,
        "newest": newest,
        "records": records,
        "timestamped": timestamped,
        "malformed": malformed,
    }


# --------------------------------------------------------------------------
# Locating the live session
# --------------------------------------------------------------------------
def slug_for(path: Path) -> str:
    """Claude Code's project-dir slug: every non-alphanumeric becomes a dash."""
    return re.sub(r"[^a-zA-Z0-9]", "-", str(path))


def main_worktree_root(cwd: Path) -> Path | None:
    """The MAIN worktree root, even when called from a linked worktree.

    This repo's standing rule puts worktrees off Drive, so a build session's cwd is
    `...\\Temp\\claude\\wt-*` and the cwd-derived slug names a project dir that has never
    existed. Git still knows where home is: `--git-common-dir` points at the main repo's
    `.git` regardless of which worktree asks. Without this, a worktree run falls through to
    the global scan and can silently answer from a *different project's* session -- which is
    the same identity-by-working-directory defect that split this repo's memory store.
    """
    import subprocess
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=str(cwd), capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    git_dir = Path(out.stdout.strip())
    return git_dir.parent if git_dir.name == ".git" else None


def candidate_project_dirs(explicit: str | None, cwd: Path) -> list[tuple[Path, str, int]]:
    """Project dirs to consider, best first: (path, why, tier). Higher tier wins.

    Tier 2  cwd slug          -- exact match, the normal case
    Tier 1  main worktree     -- so a linked worktree still finds its own project
    Tier 0  global scan       -- last resort; may answer from another project, and says so
    """
    if explicit:
        return [(Path(explicit), "explicit --project-dir", 3)]

    out: list[tuple[Path, str, int]] = []
    seen: set[Path] = set()

    def add(p: Path, why: str, tier: int):
        if p in seen or not p.is_dir() or not any(p.glob("*.jsonl")):
            return
        seen.add(p)
        out.append((p, why, tier))

    add(PROJECTS_ROOT / slug_for(cwd), "derived from cwd", 2)

    root = main_worktree_root(cwd)
    if root is not None:
        add(PROJECTS_ROOT / slug_for(root), f"derived from main worktree ({root.name})", 1)

    if PROJECTS_ROOT.is_dir():
        for d in sorted(PROJECTS_ROOT.iterdir()):
            add(d, "global scan", 0)
    return out


def sidechain_files(session_file: Path) -> list[Path]:
    """Sidechain JSONLs for a session: <uuid>/**/*.jsonl beside the session file.

    These are why the clock stays accurate during a long subagent run.
    """
    sib = session_file.with_suffix("")
    if not sib.is_dir():
        return []
    return sorted(p for p in sib.rglob("*.jsonl") if p.is_file())


def pick_session(explicit_session: str | None, project_dirs: list[tuple[Path, str]]):
    """Pick the session file. Explicit uuid wins; otherwise most-recently-modified.

    Returns (path, project_dir, reason) or (None, None, reason-for-failure).
    """
    if explicit_session:
        for d, _why, _tier in project_dirs:
            cand = d / f"{explicit_session}.jsonl"
            if cand.is_file():
                return cand, d, "explicit --session"
        return None, None, f"no session file named {explicit_session}.jsonl in any project dir"

    best = None
    for d, why, tier in project_dirs:
        for f in d.glob("*.jsonl"):  # top-level only; sidechains are not sessions
            if not f.is_file():
                continue
            try:
                mt = f.stat().st_mtime
            except OSError:
                continue
            # Tier first (a same-project session beats a stranger's), then recency.
            rank = (tier, mt)
            if best is None or rank > best[0]:
                best = (rank, f, d, f"most-recently-modified ({why})")

    if best is None:
        return None, None, "no *.jsonl found in any candidate project dir"
    return best[1], best[2], best[3]


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def human_delta(seconds: float) -> str:
    s = abs(int(seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {sec}s"
    if m:
        return f"{m}m {sec}s"
    return f"{sec}s"


def build_report(session_file: Path, project_dir: Path, reason: str,
                 include_sidechains: bool) -> dict:
    main = scan_file(session_file)

    newest = main["newest"]
    newest_from = session_file.name
    side_scanned = 0
    if include_sidechains:
        for sc in sidechain_files(session_file):
            side_scanned += 1
            r = scan_file(sc)
            if r["newest"] is not None and (newest is None or r["newest"] > newest):
                newest = r["newest"]
                newest_from = f"{sc.parent.name}/{sc.name}"

    now = datetime.now(timezone.utc)
    mtime = datetime.fromtimestamp(session_file.stat().st_mtime, timezone.utc)

    rep = {
        "session_file": str(session_file),
        "session_id": session_file.stem,
        "project_dir": str(project_dir),
        "selection_reason": reason,
        "newest_from": newest_from,
        "sidechains_scanned": side_scanned,
        "records": main["records"],
        "timestamped": main["timestamped"],
        "malformed": main["malformed"],
        "os_clock_utc": now.isoformat(),
        "file_mtime_utc": mtime.isoformat(),
        "newest_utc": newest.isoformat() if newest else None,
        "first_utc": main["first"].isoformat() if main["first"] else None,
    }

    if newest is not None:
        local, abbrev, tz_source = to_central(newest)
        rep["newest_central"] = local.isoformat()
        rep["stamp_record"] = fmt_stamp(newest)
        rep["stamp_os"] = fmt_stamp(now)
        rep["stamp"] = rep["stamp_record"]  # overridden by --stamp-source
        rep["tz_abbrev"] = abbrev
        rep["tz_source"] = tz_source
        rep["os_delta_sec"] = round((now - newest).total_seconds(), 3)
    if main["first"] is not None and newest is not None:
        rep["elapsed_sec"] = round((newest - main["first"]).total_seconds(), 3)
        rep["first_central"] = to_central(main["first"])[0].isoformat()
    return rep


def render_text(rep: dict, max_skew: int) -> tuple[str, bool]:
    L = []
    A = L.append
    A("SESSION CLOCK")
    A("=" * 66)
    A(f"  session file   {rep['session_file']}")
    A(f"  selected by    {rep['selection_reason']}")
    A(f"  newest record  from {rep['newest_from']}"
      + (f"  ({rep['sidechains_scanned']} sidechain file(s) scanned)"
         if rep["sidechains_scanned"] else ""))
    A("")
    A(f"  NOW (Central)  {rep['stamp']}   <- paste-ready [{rep['stamp_source']}]")
    if rep["stamp_record"] != rep["stamp_os"]:
        A(f"                 record clock {rep['stamp_record']} / "
          f"OS clock {rep['stamp_os']}  -- they differ; see --stamp-source")
    A(f"  newest  UTC    {rep['newest_utc']}")
    A(f"  newest  local  {rep['newest_central']}  [{rep['tz_abbrev']}  via {rep['tz_source']}]")
    A("")
    A(f"  session start  {rep.get('first_utc')} UTC")
    A(f"                 {rep.get('first_central')} local")
    if "elapsed_sec" in rep:
        A(f"  elapsed        {human_delta(rep['elapsed_sec'])}")
    A(f"  records        {rep['records']} total / {rep['timestamped']} timestamped"
      + (f" / {rep['malformed']} malformed" if rep["malformed"] else ""))
    A(f"  file mtime     {rep['file_mtime_utc']} UTC   (independent cross-check)")
    A("")

    delta = rep["os_delta_sec"]
    A(f"  OS clock       {rep['os_clock_utc']} UTC")
    A(f"  delta          {delta:+.1f}s  (OS clock minus newest record)")

    breached = abs(delta) > max_skew
    if breached:
        A("")
        A("  " + "!" * 62)
        A(f"  !! CLOCK DISAGREEMENT: {human_delta(delta)} between the newest record and the")
        A(f"  !! OS clock, above the {max_skew}s threshold.")
        A("  !!")
        A("  !! Most likely this session is NOT live and the file was picked by mtime")
        A("  !! anyway -- in which case every number above describes a different session.")
        A("  !! Verify the session id before using this time. Do not paste the stamp.")
        A("  " + "!" * 62)
    else:
        A(f"  status         OK (within {max_skew}s)")
    return "\n".join(L), breached


# --------------------------------------------------------------------------
# Self-test -- with real negative controls
# --------------------------------------------------------------------------
def _write(d: Path, name: str, lines: list[str]) -> Path:
    p = d / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def self_test() -> int:
    """Fixtures with known answers, including cases that MUST fail.

    An instrument that cannot fail is decoration, so the controls here are the point:
    a file with no timestamps must refuse to answer rather than quietly return "now".
    """
    failures: list[str] = []
    checks = 0

    def check(name: str, got, want):
        nonlocal checks
        checks += 1
        if got != want:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)

        # -- POSITIVE: known newest, deliberately NOT the last line, with untimestamped
        #    bookkeeping records trailing (exactly what a real session file looks like).
        good = _write(d, "good.jsonl", [
            json.dumps({"type": "x", "timestamp": "2026-08-03T02:36:02.748Z"}),
            json.dumps({"type": "x", "timestamp": "2026-08-03T13:19:18.558Z"}),  # newest
            json.dumps({"type": "x", "timestamp": "2026-08-03T09:00:00.000Z"}),  # out of order
            json.dumps({"type": "bridge-session", "sessionId": "abc"}),          # no timestamp
            json.dumps({"type": "last-prompt", "leafUuid": "d"}),                # no timestamp
        ])
        r = scan_file(good)
        check("newest is the max, not the last line",
              r["newest"].isoformat(), "2026-08-03T13:19:18.558000+00:00")
        check("first is the min", r["first"].isoformat(), "2026-08-03T02:36:02.748000+00:00")
        check("records counts every line", r["records"], 5)
        check("timestamped counts only stamped lines", r["timestamped"], 3)

        # -- NEGATIVE CONTROL 1: records, but not one timestamp anywhere.
        #    Must return None so the caller exits 2. Must NEVER fall back to now().
        none_f = _write(d, "none.jsonl", [
            json.dumps({"type": "bridge-session", "sessionId": "abc"}),
            json.dumps({"type": "mode", "mode": "normal"}),
            json.dumps({"type": "permission-mode", "permissionMode": "default"}),
        ])
        rn = scan_file(none_f)
        check("no-timestamp file yields no newest", rn["newest"], None)
        check("no-timestamp file still counts records", rn["records"], 3)

        # -- NEGATIVE CONTROL 2: empty file.
        empty = _write(d, "empty.jsonl", [])
        check("empty file yields no newest", scan_file(empty)["newest"], None)

        # -- NEGATIVE CONTROL 3: malformed JSON is counted, not silently swallowed,
        #    and must not crash the scan.
        bad = _write(d, "bad.jsonl", [
            '{"timestamp": "2026-08-03T01:00:00Z"',            # truncated
            json.dumps({"timestamp": "2026-08-03T05:00:00Z"}),  # valid
            json.dumps({"timestamp": "not-a-date"}),            # unparseable value
        ])
        rb = scan_file(bad)
        check("malformed line counted", rb["malformed"], 1)
        check("valid line still found", rb["newest"].isoformat(), "2026-08-03T05:00:00+00:00")

        # -- NEGATIVE CONTROL 4: pick_session must refuse an empty project dir.
        empty_dir = d / "emptyproj"
        empty_dir.mkdir()
        p, _, why = pick_session(None, [(empty_dir, "explicit --project-dir", 3)])
        check("empty project dir -> no session", p, None)
        check("empty project dir -> reason given", "no *.jsonl" in why, True)

        p, _, why = pick_session("deadbeef", [(d, "explicit --project-dir", 3)])
        check("missing explicit session -> None", p, None)

        # -- Tier beats recency: a NEWER file in a low-tier dir must not win over the
        #    session in this project's own dir. This is the wrong-session guard.
        hi, lo = d / "hi", d / "lo"
        hi.mkdir(); lo.mkdir()
        old = _write(hi, "own.jsonl", [json.dumps({"timestamp": "2026-08-03T01:00:00Z"})])
        new = _write(lo, "stranger.jsonl", [json.dumps({"timestamp": "2026-08-03T02:00:00Z"})])
        os.utime(old, (1, 1))                      # own session: ancient mtime
        os.utime(new, (10**9, 10**9))              # stranger: much newer mtime
        p, _, _ = pick_session(None, [(hi, "derived from cwd", 2), (lo, "global scan", 0)])
        check("tier beats recency", p.name, "own.jsonl")

        # -- DST: computed per-instant, both sides of both transitions.
        check("Jan is CST", to_central(parse_iso("2026-01-15T12:00:00Z"))[1], "CST")
        check("Jul is CDT", to_central(parse_iso("2026-07-15T12:00:00Z"))[1], "CDT")
        check("CST offset is -6",
              to_central(parse_iso("2026-01-15T12:00:00Z"))[0].strftime("%H:%M"), "06:00")
        check("CDT offset is -5",
              to_central(parse_iso("2026-07-15T12:00:00Z"))[0].strftime("%H:%M"), "07:00")

        # transition instants land on Sundays in the right months (rule, not a guess)
        s = _nth_weekday(2026, 3, 6, 2)
        e = _nth_weekday(2026, 11, 6, 1)
        check("DST start is a Sunday in March", (s.weekday(), s.month), (6, 3))
        check("DST end is a Sunday in November", (e.weekday(), e.month), (6, 11))
        # one second either side of each transition flips the label
        check("just before spring-forward is CST",
              _central_by_rule(s.replace(hour=7, minute=59))[1], "CST")
        check("just after spring-forward is CDT",
              _central_by_rule(s.replace(hour=8, minute=1))[1], "CDT")
        check("just before fall-back is CDT",
              _central_by_rule(e.replace(hour=6, minute=59))[1], "CDT")
        check("just after fall-back is CST",
              _central_by_rule(e.replace(hour=7, minute=1))[1], "CST")

        # a year with different weekday alignment, so the rule is not fitted to 2026
        s25 = _nth_weekday(2025, 3, 6, 2)
        check("2025 DST start is a Sunday in March", (s25.weekday(), s25.month), (6, 3))

        # -- STAMP: exact house format, to the character.
        st = fmt_stamp(parse_iso("2026-08-03T13:19:18.558Z"))
        check("stamp format exact", st, "[2026-08-03 08:19 CDT]")
        check("stamp matches house regex",
              bool(re.fullmatch(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2} C[DS]T\]", st)), True)
        check("winter stamp says CST",
              fmt_stamp(parse_iso("2026-01-15T12:00:00Z")), "[2026-01-15 06:00 CST]")

        # -- slug transformation matches Claude Code's on a real path
        check("slug", slug_for(Path(r"G:\My Drive\Claude\x")), "G--My-Drive-Claude-x")

    print("SELF-TEST")
    print("=" * 66)
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"\n  {len(failures)} of {checks} checks FAILED")
        return 3
    print(f"  {checks} checks passed"
          f" (incl. 4 negative controls that must refuse to answer)")
    return 0


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Exact current time from the live Claude Code session JSONL.")
    ap.add_argument("--session", help="explicit session uuid (without .jsonl)")
    ap.add_argument("--project-dir", help="explicit project dir under ~/.claude/projects/")
    ap.add_argument("--transcript-path",
                    help="Read THIS jsonl directly. A Claude Code hook receives "
                         "`transcript_path` on stdin, so a hook must never guess the session.")
    ap.add_argument("--hook-safe", action="store_true",
                    help="Never exit non-zero. For hook use: on a Claude Code hook, a "
                         "non-zero exit is a control signal (exit 2 BLOCKS the prompt), not "
                         "an error report. A clock that cannot find the time must degrade "
                         "to silence, never to blocking Jon's input.")
    ap.add_argument("--format", choices=["text", "stamp", "json"], default="text")
    ap.add_argument("--stamp-source", choices=["record", "os"], default="record",
                    help="'record' = when work last happened (cross-checkable, default); "
                         "'os' = true wall-clock now, correct across idle gaps")
    ap.add_argument("--max-skew", type=int, default=DEFAULT_MAX_SKEW_SEC,
                    help=f"skew threshold in seconds (default {DEFAULT_MAX_SKEW_SEC})")
    ap.add_argument("--no-sidechains", action="store_true",
                    help="do not scan <uuid>/ sidechain files (will read stale during "
                         "subagent runs)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when skew exceeds threshold")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    # A hook must never exit non-zero: on Claude Code, a hook's exit code is a CONTROL
    # SIGNAL, not an error report -- exit 2 BLOCKS the prompt. So this script's honest
    # "I refuse to guess the time" (exit 2) would, under a hook, silently stop Jon from
    # talking. **A clock that cannot find the time degrades to silence, never to blocking
    # input.** Found by the lane agent from the hook contract before the session limit
    # killed it; the collision is real and would have shipped.
    def _fin(code: int) -> int:
        return 0 if args.hook_safe else code

    if args.transcript_path:
        # The hook receives this path on stdin, so there is nothing to select and no
        # heuristic to get wrong. Direct beats derived every time it is available.
        p = Path(args.transcript_path)
        if not p.is_file():
            print(f"ERROR: --transcript-path does not exist: {p}", file=sys.stderr)
            return _fin(2)
        session_file, project_dir, reason = p, p.parent, "explicit --transcript-path"
    else:
        dirs = candidate_project_dirs(args.project_dir, Path(os.getcwd()))
        if not dirs:
            print("ERROR: no candidate project dir under "
                  f"{PROJECTS_ROOT} (and none given via --project-dir)", file=sys.stderr)
            return _fin(2)

        session_file, project_dir, reason = pick_session(args.session, dirs)
        if session_file is None:
            print(f"ERROR: no session file could be identified -- {reason}", file=sys.stderr)
            print("Refusing to report a time. Pass --session or --project-dir.", file=sys.stderr)
            return _fin(2)

    rep = build_report(session_file, project_dir, reason, not args.no_sidechains)

    if rep["newest_utc"] is None:
        print(f"ERROR: {session_file} has {rep['records']} record(s) but not one carries a "
              "timestamp.", file=sys.stderr)
        print("Refusing to report a time. This is UNKNOWN, not 'now'.", file=sys.stderr)
        return _fin(2)

    rep["stamp_source"] = args.stamp_source
    rep["stamp"] = rep["stamp_os"] if args.stamp_source == "os" else rep["stamp_record"]

    if args.format == "stamp":
        print(rep["stamp"])
        breached = abs(rep["os_delta_sec"]) > args.max_skew
        if breached:
            tail = ("The OS clock above is still true wall-clock now."
                    if args.stamp_source == "os" else
                    f"Session {rep['session_id']} may not be live -- verify before pasting, "
                    "or use --stamp-source os.")
            print(f"WARNING: newest record disagrees with the OS clock by "
                  f"{human_delta(rep['os_delta_sec'])} (threshold {args.max_skew}s). {tail}",
                  file=sys.stderr)
    elif args.format == "json":
        print(json.dumps(rep, indent=2))
        breached = abs(rep["os_delta_sec"]) > args.max_skew
    else:
        text, breached = render_text(rep, args.max_skew)
        print(text)

    if breached and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
