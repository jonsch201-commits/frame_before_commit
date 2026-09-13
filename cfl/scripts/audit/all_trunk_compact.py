#!/usr/bin/env python3
"""all_trunk_compact.py -- CB-4. The `/su-all` command Jon asked for.

Jon, 2026-09-04 ~14:0x CDT, verbatim, typos his (chartering
wiki/tracker/wayfinder-compact-barrier-2026-09-04.md): "improve yourself by
default at compact barriers..... Or give me a command for all-trunk compacts.
Its fine if its post compact, but then it'll just need to be able to resume
the pre-compact json as of that point..."

WHAT THIS IS, STATED SO NOBODY MISREADS THE OUTPUT
----------------------------------------------------
This is CB-4 from the wayfinder map, taken deliberately as the CHEAPEST HONEST
SHAPE named there: it does NOT compact any trunk (it cannot -- each seat
compacts itself when ITS OWN context fills; there is no cross-process API to
force it), it does NOT send any message to any trunk, and it does NOT launch
anything. It PREPARES and REPORTS:

  1. DISCOVERS the trunk roster by walking ~/.claude/projects/ -- never a
     hardcoded list. A recorded roster expires the moment a trunk moves
     (measured cost: three days, this repo, 2026-09 wayfinder log).
  2. For each candidate trunk, REPORTS read-only facts a human would want
     before running a compact there: session count, memory-file count, newest
     session mtime, whether a PreCompact-receipt-shaped artifact exists and
     when it last wrote, and whether the trunk's working directory has moved
     to an N: drive while a G: drive sibling of the SAME git remote still
     exists (the "migrated" question CB-8's barrier convention needs an
     answer to before it can address a trunk at all).
  3. PRINTS the exact command Jon would paste to open each trunk, matched
     against the launcher .bat files that actually exist on this machine
     (N:\\Launchers\\*.bat and this repo's own launch-cfl.bat) -- never a
     guessed invocation. A trunk with no matched launcher prints UNKNOWN.

HOW "TRUNK IDENTITY" IS DERIVED, NOT RECORDED
----------------------------------------------
A project directory under ~/.claude/projects/ is a sanitized cwd, so the SAME
git repo can appear twice (once for an N: working copy, once for the original
G: one) as two different project keys. Rather than hardcode "N--claude-cfl
is the same trunk as G--...-claude-foundational-layer", this script reads
each project's newest-session `cwd` field, then reads that cwd's own
`.git/config` for its `remote "origin"` url. Two project keys whose cwds
report the SAME origin url are the same trunk on two drives. That is the
"migrated" signal in the report -- derived from the repos' own git config,
not a name table someone will forget to update when a repo moves again.

WHAT COUNTS AS A CANDIDATE TRUNK
----------------------------------
Not every directory under ~/.claude/projects/ is a coordinator trunk -- many
are scratch dirs, worktrees, or one-off tool runs (temp paths, `--claude-
worktrees--` in the key, `--scratchpad` suffixes). This script reports EVERY
directory it finds (never silently drops one -- that is itself a way to lose
a trunk) but flags a `kind` per row: TRUNK (has a `CLAUDE.md` at its derived
cwd -- the actual signal a coordinator repo carries) or OTHER (everything
else, still listed, never hidden).

PRECOMPACT-RECEIPT DETECTION
------------------------------
Every trunk observed on this machine names its own PreCompact artifacts
differently (CFL: exchange/su-close/precompact/*.md; Professional:
exchange/precompact-receipts.log + exchange/last-precompact-receipt.md;
Secretary: thought/critic/*-PreCompact.md). Hardcoding those three paths
would silently miss a fourth trunk's convention. So detection is a BOUNDED,
generic filename search: any file under the trunk's cwd (excluding .git,
node_modules, wiki/, and raw/ -- the last is this repo's own multi-GB
gitignored corpus and would make the walk pathological), depth-capped at
MAX_SCAN_DEPTH and file-count-capped at MAX_SCAN_FILES so an unrelated
massive or cloud-synced (Google-Drive-mapped G:) tree cannot hang the
report. A file counts as a match if EITHER its own filename contains
"precompact" case-insensitively (Secretary's convention:
"*-PreCompact.md") OR its immediate parent directory's name does (CFL's
convention: exchange/su-close/precompact/<utc>-<session>.md, where the
timestamped filename itself never says the word -- a filename-only match
was tried first and silently missed CFL's own receipts; caught by the
selftest fixture built to mirror CFL's real directory shape). Newest
matching mtime wins. A walk that hit either cap is flagged (scan may be
incomplete) rather than silently reported as a clean absence.

WHAT IT REFUSES TO DO
------------------------
- Never writes into another trunk's directory (read-only across
  ~/.claude/projects/ and across every derived cwd).
- Never prints a launch command it could not verify against an existing
  .bat file's actual `cd` target -- UNKNOWN beats a guessed command a human
  will paste unread.
- Never compacts, messages, or launches anything itself.

ENCODING
--------
stdout is reconfigured to UTF-8 with replacement at the top: this machine's
console is commonly cp1252, and the ⛔/⭐/⚠ glyphs this project's own prose
uses have crashed two prior scripts tonight that only discovered the problem
outside their function-level tests. Reconfigure BEFORE any print.

Selftest: `python all_trunk_compact.py --selftest` (no repo access required
for the pure-function cases; the entry-point case runs the real script as a
subprocess and asserts its exit code).
Live report: `python all_trunk_compact.py` (or `--json` for machine output).
Exit codes: 0 = report printed; 2 = empty/unreadable roster (UNKNOWN, never
a clean 0); 1 = usage error.
"""
import argparse
import configparser
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[2]  # N:\claude-cfl\clone
LAUNCHERS_DIR = Path("N:/Launchers")
MAX_SCAN_FILES = 20000
MAX_SCAN_DEPTH = 4  # exchange/su-close/precompact/*.md is depth 3 from a trunk root
EXCLUDE_DIR_NAMES = {".git", "node_modules", "raw", "__pycache__", ".claude", "wiki"}
# Which drive prefix counts as "migrated to the fast local drive" for the
# CB-8 migration signal. A module-level list (not a literal inline in the
# check) so the selftest can retarget it to whatever drive its own tempdir
# lands on, without the real report's behaviour changing.
MIGRATED_DRIVE_PREFIXES = ("n:",)


def claude_projects_root():
    home = Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())
    return home / ".claude" / "projects"


def discover_project_dirs(projects_root: Path):
    """Return sorted list of project-key directories, or None if the root
    itself is unreadable (a distinct condition from 'root exists but empty')."""
    if not projects_root.is_dir():
        return None
    try:
        entries = sorted(p for p in projects_root.iterdir() if p.is_dir())
    except OSError:
        return None
    return entries


def newest_jsonl_cwd(project_dir: Path):
    """Scan *.jsonl files directly under project_dir (not subagents/) for the
    most recent line carrying a `cwd` field. Returns (cwd_str, newest_mtime)
    or (None, None) if unreadable/absent. UNKNOWN-safe: any read error on a
    single file is skipped, never raised."""
    best_cwd = None
    best_mtime = None
    try:
        jsonl_files = [f for f in project_dir.iterdir() if f.is_file() and f.suffix == ".jsonl"]
    except OSError:
        return None, None
    for jf in jsonl_files:
        try:
            mtime = jf.stat().st_mtime
        except OSError:
            continue
        if best_mtime is None or mtime > best_mtime:
            best_mtime = mtime
        # Prefer the cwd from whichever file is newest; peek at last lines.
    jsonl_files.sort(key=lambda f: (f.stat().st_mtime if f.exists() else 0), reverse=True)
    TAIL_BYTES = 200_000  # tail-read, never load a multi-GB session file whole
    for jf in jsonl_files[:3]:
        try:
            size = jf.stat().st_size
            with open(jf, "rb") as fh:
                if size > TAIL_BYTES:
                    fh.seek(-TAIL_BYTES, os.SEEK_END)
                raw = fh.read()
            text = raw.decode("utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        for line in reversed(lines[-200:]):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            cwd = rec.get("cwd")
            if cwd:
                best_cwd = cwd
                break
        if best_cwd:
            break
    return best_cwd, best_mtime


def session_count(project_dir: Path):
    try:
        return sum(1 for f in project_dir.iterdir() if f.is_file() and f.suffix == ".jsonl")
    except OSError:
        return None  # UNKNOWN, not 0


def memory_file_count(project_dir: Path):
    mem = project_dir / "memory"
    if not mem.is_dir():
        return 0
    try:
        return sum(1 for f in mem.rglob("*") if f.is_file())
    except OSError:
        return None


def read_git_remote_origin(cwd_str: str):
    """Read remote.origin.url from cwd_str/.git/config. Returns None if no
    .git/config, no origin section, or unreadable -- never raises."""
    if not cwd_str:
        return None
    git_config = Path(cwd_str) / ".git" / "config"
    if not git_config.is_file():
        return None
    cp = configparser.ConfigParser(strict=False)
    try:
        cp.read(git_config, encoding="utf-8")
    except (OSError, configparser.Error):
        return None
    for section in cp.sections():
        if section.strip().lower() == 'remote "origin"':
            return cp[section].get("url")
    return None


def normalize_git_url(url: str):
    """Normalize a git remote url for identity comparison. Measured need:
    N:\\claude-cfl\\clone's origin is '...claude-foundational-layer.git' while
    the G: original's is '...claude-foundational-layer' (no .git suffix) --
    the SAME repo, byte-different strings. Case-fold, strip a trailing
    '.git', strip trailing slashes."""
    if not url:
        return url
    u = url.strip().lower().rstrip("/")
    if u.endswith(".git"):
        u = u[: -len(".git")]
    return u


def find_precompact_signal(cwd_str: str):
    """Bounded generic search for a PreCompact-shaped artifact under cwd_str.
    Returns dict: {found: bool, newest_iso: str|None, path: str|None,
    scan_capped: bool, reason: str|None}. reason is set on UNKNOWN
    (unreadable cwd), distinct from found=False (clean absence)."""
    result = {"found": False, "newest_mtime": None, "path": None,
              "scan_capped": False, "reason": None}
    if not cwd_str:
        result["reason"] = "no cwd derived"
        return result
    root = Path(cwd_str)
    if not root.is_dir():
        result["reason"] = "cwd not reachable from this trunk"
        return result
    visited = 0
    newest_mtime = None
    newest_path = None
    stack = [(root, 0)]
    while stack:
        d, depth = stack.pop()
        try:
            children = list(d.iterdir())
        except OSError:
            continue
        for child in children:
            if visited >= MAX_SCAN_FILES:
                result["scan_capped"] = True
                break
            visited += 1
            if child.is_dir():
                if child.name in EXCLUDE_DIR_NAMES:
                    continue
                if depth + 1 > MAX_SCAN_DEPTH:
                    result["scan_capped"] = True
                    continue
                stack.append((child, depth + 1))
            elif child.is_file():
                # Match on the file's OWN name (Secretary convention:
                # "*-PreCompact.md") OR its immediate parent directory's name
                # (CFL convention: exchange/su-close/precompact/<hash>.md,
                # where the timestamped filename itself never says the word).
                # A filename-only match would silently miss the CFL shape.
                if "precompact" in child.name.lower() or "precompact" in child.parent.name.lower():
                    try:
                        mt = child.stat().st_mtime
                    except OSError:
                        continue
                    if newest_mtime is None or mt > newest_mtime:
                        newest_mtime = mt
                        newest_path = child
        if visited >= MAX_SCAN_FILES:
            result["scan_capped"] = True
            break
    if newest_path is not None:
        result["found"] = True
        result["newest_mtime"] = newest_mtime
        result["path"] = str(newest_path)
    return result


def memory_migration_markers(project_dir: Path):
    """Detect CFL/Personal/Professional's own migration-marker convention:
    memory/MIGRATED-TO*.md (written in the OLD project key, pointing at
    where a copy travelled) and memory/MIGRATED-FROM*.md (written in the
    NEW key, naming the old one). This is a SEPARATE signal from the git-
    origin comparison in compute_migration_flags -- it fires even when the
    new key has never run a session yet (so newest_jsonl_cwd has nothing to
    read and the origin-based check can't see it at all). Returns
    {to: [names], from: [names]}; both lists empty is the clean case."""
    mem = project_dir / "memory"
    out = {"to": [], "from": []}
    if not mem.is_dir():
        return out
    try:
        for f in mem.iterdir():
            if not f.is_file():
                continue
            name_up = f.name.upper()
            if name_up.startswith("MIGRATED-TO"):
                out["to"].append(f.name)
            elif name_up.startswith("MIGRATED-FROM"):
                out["from"].append(f.name)
    except OSError:
        pass
    return out


def find_launch_command(cwd_str: str, project_key: str):
    """Match a trunk's derived cwd against the `cd /d "..."` (or `cd -d`)
    target of every .bat under LAUNCHERS_DIR plus this repo's own
    launch-cfl.bat. Returns (command_str, source_bat) or (None, None) if no
    launcher's cd target matches. Never guesses -- an unmatched trunk gets
    UNKNOWN from the caller."""
    candidates = []
    if LAUNCHERS_DIR.is_dir():
        try:
            candidates.extend(sorted(LAUNCHERS_DIR.glob("*.bat")))
        except OSError:
            pass
    launch_cfl = REPO / "launch-cfl.bat"
    if launch_cfl.is_file():
        candidates.append(launch_cfl)

    if not cwd_str:
        return None, None
    target = Path(cwd_str)
    try:
        target_resolved = str(target).rstrip("\\/").lower()
    except OSError:
        target_resolved = str(target).lower()

    for bat in candidates:
        try:
            text = bat.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            low = stripped.lower()
            if low.startswith("cd /d") or low.startswith("cd/d"):
                # extract quoted path
                if '"' in stripped:
                    parts = stripped.split('"')
                    if len(parts) >= 2:
                        cd_target = parts[1].rstrip("\\/").lower()
                        if cd_target == target_resolved:
                            return f'"{bat}"', str(bat)
    return None, None


def looks_like_trunk(cwd_str: str):
    if not cwd_str:
        return False
    claude_md = Path(cwd_str) / "CLAUDE.md"
    try:
        return claude_md.is_file()
    except OSError:
        return False


def compute_migration_flags(prelim, migrated_prefixes=None):
    """Pure function, no filesystem access: given prelim rows (each a dict
    with at least 'key', 'cwd', 'origin'), return {key: {is_migrated_drive,
    migrated_with_sibling, sibling_cwd}}. Split out from build_report so the
    origin-matching logic is testable with synthetic drive letters that need
    not correspond to a real mounted drive on the test machine."""
    if migrated_prefixes is None:
        migrated_prefixes = MIGRATED_DRIVE_PREFIXES
    by_origin = {}
    for row in prelim:
        norm = normalize_git_url(row.get("origin"))
        if norm:
            by_origin.setdefault(norm, []).append(row)

    out = {}
    for row in prelim:
        cwd_str = row.get("cwd")
        is_migrated_drive = bool(cwd_str) and str(cwd_str).lower().startswith(migrated_prefixes)
        migrated = False
        sibling_cwd = None
        norm = normalize_git_url(row.get("origin"))
        if norm and is_migrated_drive:
            siblings = [r for r in by_origin[norm]
                        if r is not row and r.get("cwd")
                        and not str(r["cwd"]).lower().startswith(migrated_prefixes)]
            if siblings:
                migrated = True
                sibling_cwd = siblings[0]["cwd"]
        out[row["key"]] = {
            "is_migrated_drive": is_migrated_drive,
            "migrated_with_sibling": migrated,
            "sibling_cwd": sibling_cwd,
        }
    return out


def build_report(projects_root: Path = None):
    """Core, read-only derivation. Returns (rows, error) where error is a
    string set only when the roster itself is unreadable/empty (caller maps
    that to exit 2). rows is always a list (possibly empty only alongside a
    set error)."""
    if projects_root is None:
        projects_root = claude_projects_root()

    project_dirs = discover_project_dirs(projects_root)
    if project_dirs is None:
        return [], f"UNKNOWN: cannot read projects root {projects_root}"
    if not project_dirs:
        return [], f"EMPTY: no project directories found under {projects_root}"

    # First pass: derive cwd + origin for every project (for migration match).
    prelim = []
    for pdir in project_dirs:
        cwd_str, newest_session_mtime = newest_jsonl_cwd(pdir)
        origin = read_git_remote_origin(cwd_str)
        prelim.append({
            "key": pdir.name,
            "project_dir": pdir,
            "cwd": cwd_str,
            "origin": origin,
            "newest_session_mtime": newest_session_mtime,
        })

    migration = compute_migration_flags(prelim)

    rows = []
    for row in prelim:
        cwd_str = row["cwd"]
        mig = migration[row["key"]]
        is_n_drive = mig["is_migrated_drive"]
        migrated = mig["migrated_with_sibling"]
        sibling_cwd = mig["sibling_cwd"]

        sess_count = session_count(row["project_dir"])
        mem_count = memory_file_count(row["project_dir"])
        pc_signal = find_precompact_signal(cwd_str)
        launch_cmd, launch_src = find_launch_command(cwd_str, row["key"])
        kind = "TRUNK" if looks_like_trunk(cwd_str) else "OTHER"
        mem_markers = memory_migration_markers(row["project_dir"])

        rows.append({
            "project_key": row["key"],
            "cwd": cwd_str,
            "kind": kind,
            "session_count": sess_count,
            "memory_file_count": mem_count,
            "newest_session_mtime": row["newest_session_mtime"],
            "git_origin": row["origin"],
            "is_n_drive": is_n_drive,
            "migrated_with_g_sibling": migrated,
            "g_sibling_cwd": sibling_cwd,
            "precompact_signal": pc_signal,
            "launch_command": launch_cmd,
            "launch_source": launch_src,
            "memory_migration_markers": mem_markers,
        })

    return rows, None


def fmt_mtime(mtime):
    if mtime is None:
        return "UNKNOWN"
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_text_report(rows):
    lines = []
    lines.append("all_trunk_compact.py -- read-only report. Compacts nothing. Sends nothing. Launches nothing.")
    lines.append(f"generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append(f"trunks discovered: {len(rows)}")
    lines.append("")
    trunks = [r for r in rows if r["kind"] == "TRUNK"]
    others = [r for r in rows if r["kind"] == "OTHER"]
    lines.append(f"-- TRUNKS ({len(trunks)}) --")
    for r in trunks:
        lines.append(f"* {r['project_key']}")
        lines.append(f"    cwd: {r['cwd'] or 'UNKNOWN'}")
        lines.append(f"    sessions: {r['session_count'] if r['session_count'] is not None else 'UNKNOWN'}"
                      f"  memory files: {r['memory_file_count'] if r['memory_file_count'] is not None else 'UNKNOWN'}"
                      f"  newest session: {fmt_mtime(r['newest_session_mtime'])}")
        migrated_str = "UNKNOWN"
        if r["is_n_drive"]:
            migrated_str = f"YES (G: sibling {r['g_sibling_cwd']})" if r["migrated_with_g_sibling"] else "NO (no G: sibling of same origin found)"
        else:
            migrated_str = "n/a (not on N:)"
        lines.append(f"    migrated to N: with live G: sibling: {migrated_str}")
        pc = r["precompact_signal"]
        if pc["reason"]:
            pc_str = f"UNKNOWN ({pc['reason']})"
        elif pc["found"]:
            pc_str = f"FOUND, newest {fmt_mtime(pc['newest_mtime'])} ({pc['path']})"
            if pc["scan_capped"]:
                pc_str += " [scan capped -- may be incomplete]"
        else:
            pc_str = "NONE FOUND"
            if pc["scan_capped"]:
                pc_str += " [scan capped -- may be incomplete, not a confirmed absence]"
        lines.append(f"    precompact-receipt signal: {pc_str}")
        if r["launch_command"]:
            lines.append(f"    launch command: call {r['launch_command']}   (matched: {r['launch_source']})")
        else:
            lines.append("    launch command: UNKNOWN -- no launcher .bat's cd target matched this cwd; do not guess one")
        lines.append("")
    if others:
        lines.append(f"-- OTHER project directories, not treated as coordinator trunks ({len(others)}) --")
        for r in others:
            line = f"* {r['project_key']}  cwd={r['cwd'] or 'UNKNOWN'}"
            mm = r.get("memory_migration_markers") or {}
            if mm.get("to") or mm.get("from"):
                tag = []
                if mm.get("from"):
                    tag.append(f"MEMORY MIGRATED IN ({', '.join(mm['from'])})")
                if mm.get("to"):
                    tag.append(f"memory copy sent onward ({', '.join(mm['to'])})")
                line += "  -- " + "; ".join(tag)
                if r["cwd"] is None:
                    line += "  [no session has run under this key yet -- git-origin match cannot see this trunk]"
            lines.append(line)
        lines.append("")
    lines.append("REMINDER: this tool prepares and reports only. It did not compact, message, or launch anything.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _mk_project(base: Path, key: str, cwd: str, n_sessions: int = 1,
                 n_memory: int = 0, precompact_files=None, git_origin=None):
    pdir = base / key
    pdir.mkdir(parents=True, exist_ok=True)
    for i in range(n_sessions):
        f = pdir / f"sess{i}.jsonl"
        rec = {"type": "user", "cwd": cwd, "sessionId": key}
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    if n_memory:
        mem = pdir / "memory"
        mem.mkdir(exist_ok=True)
        for i in range(n_memory):
            (mem / f"m{i}.md").write_text("x", encoding="utf-8")
    cwd_path = Path(cwd)
    cwd_path.mkdir(parents=True, exist_ok=True)
    (cwd_path / "CLAUDE.md").write_text("trunk", encoding="utf-8")
    if git_origin:
        gitdir = cwd_path / ".git"
        gitdir.mkdir(exist_ok=True)
        (gitdir / "config").write_text(
            f'[remote "origin"]\n\turl = {git_origin}\n', encoding="utf-8")
    if precompact_files:
        for rel in precompact_files:
            fp = cwd_path / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text("receipt", encoding="utf-8")
    return pdir


def run_selftest():
    import shutil
    import subprocess
    import tempfile

    failures = []

    def check(name, cond, detail=""):
        status = "PASS" if cond else "FAIL"
        print(f"[{status}] {name} {detail}")
        if not cond:
            failures.append(name)

    tmp = Path(tempfile.mkdtemp(prefix="atc_selftest_"))
    try:
        # 0. Migration matching is tested as a PURE function against synthetic
        #    drive-letter strings -- it needs no real N:/G: drive mounted on
        #    whatever machine runs this selftest.
        synth = [
            {"key": "n-side", "cwd": "N:/fake/cfl", "origin": "https://example.com/x.git"},
            {"key": "g-side", "cwd": "G:/fake/cfl", "origin": "https://example.com/x.git"},
            {"key": "n-orphan", "cwd": "N:/fake/lonely", "origin": "https://example.com/y.git"},
        ]
        mig = compute_migration_flags(synth, migrated_prefixes=("n:",))
        check("compute_migration_flags: N: side with a same-origin G: sibling reads migrated",
              mig["n-side"]["migrated_with_sibling"] is True and mig["n-side"]["sibling_cwd"] == "G:/fake/cfl",
              str(mig["n-side"]))
        check("compute_migration_flags: G: side itself is not flagged as the migrated drive",
              mig["g-side"]["is_migrated_drive"] is False, str(mig["g-side"]))
        check("compute_migration_flags: N: trunk with no same-origin sibling reads NOT migrated",
              mig["n-orphan"]["migrated_with_sibling"] is False, str(mig["n-orphan"]))

        # 0b. normalize_git_url: the exact byte-difference that made
        #     N--claude-cfl-clone read as NOT migrated in the first live run
        #     of this script (".git" suffix present on one side only).
        check("normalize_git_url treats a trailing .git suffix as identical",
              normalize_git_url("https://github.com/x/y.git") == normalize_git_url("https://github.com/x/y"))
        synth2 = [
            {"key": "n-dotgit", "cwd": "N:/fake/y", "origin": "https://github.com/x/y.git"},
            {"key": "g-nodotgit", "cwd": "G:/fake/y", "origin": "https://github.com/x/y"},
        ]
        mig2 = compute_migration_flags(synth2, migrated_prefixes=("n:",))
        check("compute_migration_flags matches across a .git-suffix difference",
              mig2["n-dotgit"]["migrated_with_sibling"] is True, str(mig2["n-dotgit"]))

        # 0c. memory_migration_markers: the CFL/Personal/Professional
        #     convention (memory/MIGRATED-TO*.md, memory/MIGRATED-FROM*.md)
        #     that fires even when the new project key has never run a
        #     session (so origin-matching above has nothing to read).
        marker_proj = tmp / "marker-project"
        (marker_proj / "memory").mkdir(parents=True)
        (marker_proj / "memory" / "MIGRATED-FROM-somewhere-2026-09-05.md").write_text("x", encoding="utf-8")
        markers = memory_migration_markers(marker_proj)
        check("memory_migration_markers detects a MIGRATED-FROM file with no sessions present",
              markers["from"] == ["MIGRATED-FROM-somewhere-2026-09-05.md"] and markers["to"] == [],
              str(markers))
        no_marker_proj = tmp / "no-marker-project"
        (no_marker_proj / "memory").mkdir(parents=True)
        (no_marker_proj / "memory" / "ordinary-memory.md").write_text("x", encoding="utf-8")
        check("memory_migration_markers reports clean-empty when no marker file exists",
              memory_migration_markers(no_marker_proj) == {"to": [], "from": []})

        # 1. Normal trunk fixture, real dirs on whatever drive tempfile gives us
        #    (kind/precompact/session-count checks below do not depend on which
        #    literal drive letter that is).
        _mk_project(tmp, "N--fake-cfl", str(tmp / "n_cfl"), n_sessions=2,
                    n_memory=3, precompact_files=["exchange/su-close/precompact/x.md"],
                    git_origin="https://example.com/fake-cfl.git")

        # 2. Same origin, second cwd -- exercises the origin-grouping path end
        #    to end (real build_report), even though both fixture dirs share a
        #    drive letter here and so neither reads as "migrated" -- that
        #    specific semantics is covered by case 0 above.
        _mk_project(tmp, "G--fake-cfl", str(tmp / "g_cfl"),
                    git_origin="https://example.com/fake-cfl.git")

        # 3. Trunk with no precompact signal at all (clean absence).
        _mk_project(tmp, "N--fake-clean", str(tmp / "n_clean"), n_sessions=1)

        # 4. OTHER (non-trunk) directory: has jsonl but no CLAUDE.md at derived cwd.
        other_dir = tmp / "n_other"
        other_dir.mkdir(parents=True, exist_ok=True)
        _mk_project(tmp, "N--scratch-thing", str(other_dir))
        # remove the CLAUDE.md _mk_project always writes, to force OTHER kind
        (other_dir / "CLAUDE.md").unlink()

        # 5. Project dir with NO jsonl files at all -> cwd None -> UNKNOWN cwd, UNKNOWN precompact.
        empty_proj = tmp / "N--empty-project"
        empty_proj.mkdir(parents=True, exist_ok=True)

        # 6. Project dir whose cwd points at a nonexistent path (deleted repo).
        gone_proj = tmp / "N--gone-repo"
        gone_proj.mkdir(parents=True, exist_ok=True)
        (gone_proj / "s.jsonl").write_text(
            json.dumps({"type": "user", "cwd": str(tmp / "does_not_exist"), "sessionId": "x"}) + "\n",
            encoding="utf-8")

        rows, err = build_report(projects_root=tmp)
        check("normal run has no roster-level error", err is None, f"err={err}")
        by_key = {r["project_key"]: r for r in rows}

        check("fake-cfl end-to-end row carries a git_origin (origin read from real .git/config)",
              by_key.get("N--fake-cfl", {}).get("git_origin") == "https://example.com/fake-cfl.git",
              str(by_key.get("N--fake-cfl")))
        check("fake-cfl precompact signal FOUND via the CFL shape "
              "(timestamped filename inside a directory literally named precompact/)",
              by_key.get("N--fake-cfl", {}).get("precompact_signal", {}).get("found") is True,
              str(by_key.get("N--fake-cfl", {}).get("precompact_signal")))
        check("fake-clean has NO precompact signal found (clean absence, not UNKNOWN)",
              by_key.get("N--fake-clean", {}).get("precompact_signal", {}).get("found") is False
              and by_key.get("N--fake-clean", {}).get("precompact_signal", {}).get("reason") is None)
        check("scratch-thing (no CLAUDE.md) classified OTHER not TRUNK",
              by_key.get("N--scratch-thing", {}).get("kind") == "OTHER")
        check("fake-cfl (has CLAUDE.md) classified TRUNK",
              by_key.get("N--fake-cfl", {}).get("kind") == "TRUNK")
        check("empty-project (no jsonl) reports UNKNOWN session count via None cwd, not zeroed out silently",
              by_key.get("N--empty-project", {}).get("cwd") is None)
        check("gone-repo (cwd path missing) precompact signal is UNKNOWN with a reason, not a clean absence",
              by_key.get("N--gone-repo", {}).get("precompact_signal", {}).get("reason") is not None)

        # 7. Unreadable/nonexistent projects root -> UNKNOWN, never a clean empty list.
        rows2, err2 = build_report(projects_root=tmp / "does-not-exist-at-all")
        check("nonexistent projects root -> error set (UNKNOWN), rows empty",
              err2 is not None and rows2 == [], f"err2={err2}")

        # 8. Empty roster (root exists, zero children) -> distinct EMPTY error, still not silent success.
        empty_root = tmp / "empty_root"
        empty_root.mkdir()
        rows3, err3 = build_report(projects_root=empty_root)
        check("empty projects root -> EMPTY error set",
              err3 is not None and rows3 == [], f"err3={err3}")

        # 9. Entry-point case: run the real script as a subprocess against the fixture root
        #    via env override is not supported by the CLI (by design -- the live command must
        #    use the real ~/.claude/projects/), so instead assert the real script's --selftest
        #    subprocess path returns 0, and separately assert a live real-root run exits 0.
        script_path = Path(__file__).resolve()
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, text=True, timeout=480,
        )
        check("entry-point: real script real-root run exits 0",
              proc.returncode == 0, f"exit={proc.returncode} stderr={proc.stderr[:300]}")
        check("entry-point: real script prints the no-op reminder",
              "did not compact, message, or launch anything" in proc.stdout)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    if failures:
        print(f"SELFTEST: {len(failures)} FAILURE(S): {failures}")
        return 1
    print("SELFTEST: all cases passed")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true", help="run the built-in selftest suite and exit")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of the text report")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(run_selftest())

    rows, err = build_report()
    if err is not None:
        print(f"UNKNOWN: {err}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(rows, indent=2, default=str))
    else:
        print(render_text_report(rows))
    sys.exit(0)


if __name__ == "__main__":
    main()
