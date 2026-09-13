#!/usr/bin/env python3
"""hook_harness.py — CFL fleet hook reliability harness (lane H-1d v5, week-2026-09-02).

Jon (relayed): "solve all of these hook failures, not just yours. Find the way to testing
and issues and fixes. You are the foundation."

v5 CHANGELOG (H-1d, responding to Secretary's finding running v4 --degrade on its OWN trunk):
Secretary's own settings.json invokes 13 of its 14 executed hooks by ABSOLUTE path
(`powershell -File "G:\\...\\scripts\\index-check.ps1"`), so v4's --degrade truncated only 1
script (the one referenced relative-to-project) and, for the other 13, silently declined to
touch a file it correctly recognised was outside its scratch clone — then re-ran those 13
rows anyway, against the real, un-truncated script at its real path. The resulting classes
(mostly OK) landed in the SAME degraded-phase summary table as the 1 genuinely-degraded row,
so the report read as "14 hooks measured under degrade" when only 1 actually was — the same
shape as v1's SKIPPED-DESTRUCTIVE: a limitation rendered as a completed measurement.

  1. UNDEGRADABLE-ABSOLUTE-PATH — a new degraded-phase class (baseline phase is unaffected).
     `truncate_primaries()` now classifies each executed row's primary as either in-scratch
     (truncated, as before) or resolving OUTSIDE the scratch clone (absolute path, or a
     relative ref that escapes it) — the latter are recorded in an `undegradable` map
     (primary_path -> resolved path string) and NEVER truncated (unchanged: the harness only
     ever writes inside its own scratch tree). `run_degrade_phase()` no longer re-executes
     those rows at all (re-running against the real, untouched script would just reproduce
     the misleading measurement this fix exists to stop) — it classes them directly as
     UNDEGRADABLE-ABSOLUTE-PATH, `executed: false`, with the resolved path in `notes`.
  2. Counters — the jsonl footer and the .md summary now carry `executed_n` (baseline rows
     eligible for degrade), `degraded_n` (rows actually truncated-and-re-run), and
     `undegradable_n` (rows declined). The .md degrade section's headline line reads
     "degraded X of Y executed (Z undegradable: absolute paths)" instead of implying full
     coverage from a rows-table that happens to have Y rows in it.
  3. Exit 6 — when `--degrade` ran and `degraded_n < executed_n`, the harness exits 6 (outputs
     are still written in full) unless `--allow-partial-degrade` is passed, in which case the
     same partial run exits 0. This makes "only 1 of 14 was actually degraded" a loud,
     scriptable signal instead of something only visible by reading the row-by-row table.
  4. Selftest sub-test 6/6 — a fixture with one in-scratch python hook and one hook invoking a
     script by absolute path outside the scratch clone (built under the same LOCALAPPDATA base
     `make_scratch_clone()` uses, measured space-free on this machine). Asserts: the in-scratch
     row still truncates and grades FAIL-OPEN-SILENT; the absolute-path row grades
     UNDEGRADABLE-ABSOLUTE-PATH and is not re-run; a plain run's own exit-code arithmetic reads
     exit 6; the same fixture with --allow-partial-degrade reads exit 0. Sub-tests 1-5
     (v2's both-directions control, v4's NONZERO-WITH-OUTPUT/TIMEOUT-splits/degrade-design/
     TIMEOUT-outranks-side-effects) are UNCHANGED.

KNOWN LIMITATION NOT CLOSED BY THIS FIX: `extract_script_refs`'s token regex
(`ANY_SCRIPT_TOKEN_RE = r'([^\\s"\\']+\\.(?:sh|py|ps1))\\b'`) is whitespace-delimited, so a
QUOTED absolute path containing a space (e.g. `"G:\\My Drive\\...\\index-check.ps1"`, which is
plausible for any trunk living under Drive) loses everything before the last space during
extraction — the parsed ref would read as a shorter, drive-letter-less string. Such a ref may
resolve as apparently in-scratch (or as a plain nonexistent path) rather than being caught by
the outside-scratch check this fix adds, silently reproducing the exact failure mode this fix
targets. This lane's selftest fixture deliberately uses a space-free external path to prove
the mechanism works; it does NOT prove the tokenizer survives a quoted absolute path with an
internal space. Out of this lane's write-set to fix (would touch extract_script_refs's regex,
not just the degrade phase) — reported here as a known gap, not claimed closed.

v4 CHANGELOG (H-1c, responding to Secretary's three v2-classifier findings in addendum 6 of
wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md, plus Professional's withdrawn-then-confirmed
timeout/side-effects findings in addenda 3-5):

  1. EXIT-CODE SEMANTICS — Secretary's finding 1. v2/v3 graded ANY non-zero exit as
     FAIL-CLOSED-VISIBLE, including Secretary's own `index-check.ps1` / `usage_reader.py`,
     which document exit 3 as a loud, correct FINDINGS-EXIST / UNAVAILABLE-BY-DESIGN signal —
     the exact misreading that trunk already caught and fixed in itself on 08-15. v4 splits
     the class: FAIL-CLOSED-VISIBLE now fires ONLY for a non-zero exit with ZERO stdout bytes
     (a genuinely silent crash). A non-zero exit WITH stdout is its own class,
     NONZERO-WITH-OUTPUT, carrying the exit code and the note "trunk-defined semantics; check
     the script's documented exit codes" — never treated as a crash by default. A per-trunk
     `--exit-semantics <file>` (JSON: {"<script-path>": {"<exit-code-str>": "<meaning>"}})
     renames the class to the trunk's own documented meaning (e.g. "3" -> "FINDINGS-EXIST").

  2. TIMEOUTS — Secretary's finding 2. Professional's `lint_hook.sh` and Secretary's own
     `compact-capture.ps1` (151,604 ms, inside its OWN 300s declared budget) showed the harness
     cap and the hook's declared budget are different numbers and v3 conflated them into one
     TIMEOUT class. v4 records BOTH `declared_timeout_s` (from settings.json's own "timeout"
     key, falling back to the documented per-event default: 600s general, 30s UserPromptSubmit,
     1.5s SessionEnd-shared) and `harness_cap_s` (the actual subprocess.run cap this run used:
     min(declared, --exec-cap)). Two classes: TIMEOUT-DECLARED (the hook's own declared budget
     was exhausted — cap >= declared, so the declared timeout is what fired) and
     TIMEOUT-HARNESS-CAP (the harness's own --exec-cap cut the run short WHILE the hook was
     still inside its declared budget — cap < declared). --exec-cap's default changes from
     120.0 to 900.0 so that, per the operator's own choice unless lowered, `cap = min(declared,
     exec_cap)` never falls below `declared` for any of CFL's documented timeouts (max 900s) —
     "a hook is never killed inside its own budget unless the operator lowers the cap."

  3. --degrade — Secretary's finding 3 ("0 FAIL-OPEN-SILENT" was measured with G: healthy and
     says nothing about a degraded mount). After the normal (baseline) run, IN THE SAME scratch
     clone (never the real tree), --degrade truncates each executed row's PRIMARY script (the
     content script actually executed — script_meta[-1], the v2/v3 convention for "the last,
     innermost script reference") to 0 bytes and re-runs that row's exact command against the
     now-corrupted scratch copy, appending rows with `phase: "degraded"`.
     WHY PRIMARY, NOT EVERY REFERENCED SCRIPT: a wrapped hook's command line now resolves TWO
     script refs (see fix 3a below) — the wrapper (e.g. `.claude/hooks/py_closed.sh`) and the
     python target it launches. Truncating BOTH would corrupt the wrapper's own protective
     logic too, and `bash <0-byte-file>` exits 0 silently (measured) — collapsing the very
     distinction this mode exists to show (wrapped vs unwrapped). Truncating only the primary
     (the target, for a wrapped hook; the only script, for an unwrapped one) tests exactly the
     fault py_closed.sh was built to catch: the wrapper stays intact and is expected to
     detect the corrupt target and fail CLOSED and VISIBLE. Printed per row:
     "wrapper/interpreter should fail CLOSED and VISIBLE"; a FAIL-OPEN-SILENT row in the
     degraded phase is the finding this mode exists to surface.

  3a. SCRIPT-REF EXTRACTION WIDENED — a prerequisite bug found while building --degrade: v3's
      `SCRIPT_REF_RE` only matched the script token immediately following bash/python/etc, so
      on CFL's own `bash ".../py_closed.sh" scripts/audit/postcompact_pipeline.py` it returned
      ONLY `py_closed.sh` and silently missed the actual python target passed as the wrapper's
      argument (measured empirically against every CFL hook command before landing this fix).
      `extract_script_refs` now scans the WHOLE command line for any unquoted, whitespace-
      bounded token ending in .sh/.py/.ps1, in left-to-right order — so for a wrapped hook the
      wrapper is refs[0] and the target is refs[-1] (== `primary`), matching the pre-existing
      "primary = script_meta[-1]" convention without changing it. Unwrapped hooks are
      unaffected (single ref, same as v3).

  4. Fixture: added `userpromptsubmit.json` (prompt "harness fixture", session_id
     "harness-0000") — v3 shipped `resolve_fixture()` mapping for UserPromptSubmit but no
     fixture file existed, so any UserPromptSubmit hook entry graded SKIPPED-NO-FIXTURE
     unconditionally. CFL has no UserPromptSubmit hook today; this closes the gap for any
     trunk that does (confirmed present in Secretary's own v2 run, 2 SKIPPED-NO-FIXTURE rows).

  5. Selftest extended (v2's both-directions FAIL-OPEN-SILENT assertion is UNCHANGED and still
     runs first): adds (a) NONZERO-WITH-OUTPUT positive control (a script that prints then
     exits 3, plus its exit-semantics override to a trunk-named class), (b) TIMEOUT-HARNESS-CAP
     vs TIMEOUT-DECLARED discrimination (one sleeping script, run under two declared/cap
     combinations), (c) the degrade-phase positive control described in fix 3 (direct python
     hook truncated -> FAIL-OPEN-SILENT; the same hook behind a minimal fail-closed wrapper
     stub, target truncated, wrapper intact -> FAIL-CLOSED-VISIBLE). All sub-tests must pass
     for `--selftest` (and the automatic pre-run gate) to exit 0; --degrade's own pre-run gate
     additionally requires the degrade sub-test to pass.

  6. (mid-lane addition, Professional's own v2 run against its tree) TIMEOUT must outrank the
     side-effects OK-promotion — a timed-out hook that wrote something before the kill is still
     incomplete. This already held structurally in v3 (`if timed_out` is checked, and returns,
     before the `side_effects and not any_zero_or_unreadable` branch under the
     `exit_code == 0` arm — a timed-out subprocess.run has no exit_code==0 to fall into) but
     had no positive-control test proving it can't regress; selftest sub-test 5 adds one (a
     script that writes a file then sleeps past its cap must still grade TIMEOUT-*, not OK).

  7. (mid-lane addition, same source) DUPLICATE-WORK-SIGNATURE — a note, not a class. When an
     identical `cmd` recurs under the same event (Professional measured this on its own tree:
     `postcompact-pipeline.py` under both SessionStart startup and compact matchers,
     side_effects 1/0/0 across compact/startup/resume; render-sessions.sh 331 vs 273 bytes) and
     a LATER row has zero side_effects with a byte-identical stdout hash to an earlier row that
     DID record side_effects, the later row is flagged — it most likely did no new work (an
     idempotent "already done" branch was satisfied by the earlier run in the same scratch
     clone). `stdout_sha256` is now recorded on every executed row to make "byte-identical"
     exact rather than a length guess. This never changes `class`; it is diagnostic only, and
     it does not itself decide whether the duplication is by-design or a race.

Everything from v2/v3 (SKIPPED-NO-FIXTURE split from SKIPPED-DESTRUCTIVE, `executed` accounting
and exit 4 on zero-execution, the automatic pre-run selftest and its exit 5 on failure, the
both-directions FAIL-OPEN-SILENT detector assertion, and the v3 side_effects rule — non-empty
side_effects dominates the static stdout heuristic unless the script is 0 bytes/unreadable,
landed after Professional's withdrawn recorder finding) is preserved unchanged below.

WHAT THIS DOES
--------------
Enumerates every hook entry under every event/matcher in a Claude Code `settings.json`,
classifies its interpreter and target script(s), checks the script's on-disk bytes against
the same path at `git show HEAD:<path>` (drift detection), then actually RUNS the hook
command with a fixture stdin payload and grades the outcome into one of:

  OK                    — ran, did something visible (or is expected silent-ok; see below)
  FAIL-CLOSED-VISIBLE   — non-zero exit AND zero stdout bytes (a silent crash)
  NONZERO-WITH-OUTPUT   — (v4) non-zero exit WITH stdout bytes; trunk-defined semantics —
                           check the script's documented exit codes; renamed by
                           --exit-semantics when the trunk provides a mapping
  FAIL-OPEN-SILENT      — exit 0, zero stdout bytes, AND the target script is 0 bytes or
                           unreadable (python case), or the script's own body proves it
                           normally prints something and produced none of it anyway
  TIMEOUT-DECLARED      — (v4, was TIMEOUT) exceeded the hook's own declared timeout
                           (cap >= declared_timeout_s, so the declared budget is what fired)
  TIMEOUT-HARNESS-CAP   — (v4) the harness's own --exec-cap killed the run while the hook was
                           still inside its declared budget (cap < declared_timeout_s)
  BLAMES-SIBLING        — stdout/stderr accuses another hook/script by name of not running
  SKIPPED-DESTRUCTIVE   — statically known to write outside the scratch tree (~/.claude) or
                           touch the network/remote; graded on metadata only, never executed.
                           ONLY set when the destructive scanner actually fired (v2: see
                           `destructive_reason` on the row) — never for a missing fixture.
  SKIPPED-NO-FIXTURE    — no fixture file resolves for this event/matcher; NOT executed, and
                           this is an input-availability gap, not a safety call.
  UNDEGRADABLE-ABSOLUTE-PATH — (v5, degraded phase only) the row's primary script resolves
                           outside the scratch clone (absolute-path invocation); the harness
                           declined to truncate it and did NOT re-run this row under --degrade.
                           See --degrade below and the v5 changelog.

SAFETY (why a hook is never run against the live tree)
-------------------------------------------------------
Every hook is executed with CLAUDE_PROJECT_DIR pointed at a throwaway `git clone --shared`
of the target repo, sitting under %LOCALAPPDATA%\\Temp\\claude\\hook-scratch-<pid>. Hook
side effects (file writes inside the project) land in that scratch clone, never in the real
working tree, and the scratch clone is destroyed after the run (unless --keep-scratch or
--degrade, which needs the same scratch alive for its second pass — still destroyed at exit
unless --keep-scratch is also passed). --degrade's truncation only ever touches files inside
that scratch clone; the source repo the harness was pointed at is read from, never written to.

USAGE
-----
  python scripts/audit/hook_harness.py --settings .claude/settings.json --trunk cfl \
      --project-dir . --out wiki/test-outputs/HOOK-HARNESS-cfl-2026-09-02.jsonl
      # --fixtures omitted: resolves beside-script, then repo-relative, else exit 3

  python scripts/audit/hook_harness.py --settings .claude/settings.json --trunk cfl \
      --project-dir . --degrade --out wiki/test-outputs/HOOK-HARNESS-cfl-degrade.jsonl
      # baseline pass, then in the SAME scratch clone: truncate every executed row's primary
      # script to 0 bytes and re-run; degraded rows carry phase: "degraded". A row whose
      # primary resolves outside the scratch clone (absolute path) is classed
      # UNDEGRADABLE-ABSOLUTE-PATH and not re-run. Exits 6 if degraded_n < executed_n unless
      # --allow-partial-degrade is passed (outputs are written either way).

  python scripts/audit/hook_harness.py --exit-semantics exit-semantics-secretary.json ...
      # {"tools/index-check.ps1": {"3": "FINDINGS-EXIST"}, ...}

  python scripts/audit/hook_harness.py --dry-run --settings .claude/settings.json \
      --project-dir .
      # lists resolved fixture (or skip reason) per entry; touches nothing

  python scripts/audit/hook_harness.py --selftest
      # asserts detector-on/off, NONZERO-WITH-OUTPUT, both TIMEOUT classes, and the degrade
      # positive control, all in one run; exit 0 pass, exit 1 fail

  python scripts/audit/hook_harness.py --settings .claude/settings.json --project-dir . \
      --skip-selftest
      # opt out of the automatic pre-run selftest (default is ON)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

# ------------------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------------------

DOC_TIMEOUTS = {
    # documented default per-event timeouts (seconds); command hooks default to 600s unless
    # the hook stanza specifies its own "timeout" — which every CFL entry does.
    "UserPromptSubmit": 30,
    "SessionEnd": 1.5,  # SessionEnd hooks share a 1.5s TOTAL budget per official docs
}
DEFAULT_CMD_TIMEOUT = 600

DESTRUCTIVE_SCRIPT_MARKERS = [
    r"sync-universal\.sh",
]
DESTRUCTIVE_INLINE_MARKERS = [
    r"\bgit\s+pull\b",
    r"\bgit\s+push\b",
    r"\bgit\s+commit\b",
    r"\bgh\s+pr\s+create\b",
    r"\bgh\s+api\b",
    r"\bsmtplib\b",
    r"requests\.(get|post|put|delete)\(",
    r"\burlopen\(",
    r"\bsocket\.\w+\(",
]
DESTRUCTIVE_RE = re.compile("|".join(DESTRUCTIVE_SCRIPT_MARKERS + DESTRUCTIVE_INLINE_MARKERS))

# Belt-and-suspenders: entries independently confirmed by manual source read (see H-1 report)
# to write to $HOME/.claude via sync-universal.sh. Matched on (event, matcher, hook index
# within its group, first ~40 chars of command) so a settings.json edit that changes these
# commands doesn't silently keep the old skip decision.
KNOWN_DESTRUCTIVE_PREFIXES = [
    'cd "${CLAUDE_PROJECT_DIR}" && BEFORE=$(git rev-parse',  # SessionStart startup: git pull + sync-universal.sh
    'bash "${CLAUDE_PROJECT_DIR}/.claude/hooks/post-skills-sync.sh"',  # calls sync-universal.sh
]

# v4 fix 3a: widened from an interpreter-prefixed match only (see changelog). Scans the WHOLE
# command line for any unquoted, whitespace-bounded token ending in .sh/.py/.ps1, so a wrapped
# hook's TARGET script (passed as the wrapper's own argument) is no longer silently missed.
ANY_SCRIPT_TOKEN_RE = re.compile(r'([^\s"\']+\.(?:sh|py|ps1))\b')

CRASH_LANGUAGE_RE = re.compile(
    r'\b(crashed|did not run|likely (failed|crashed|broke))\b', re.IGNORECASE
)


# ------------------------------------------------------------------------------------------
# Small utilities
# ------------------------------------------------------------------------------------------

def sha256_of_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_of_file(path: Path) -> tuple:
    """Returns (sha256_hex_or_None, size_or_None, readable: bool)."""
    try:
        data = path.read_bytes()
        return sha256_of_bytes(data), len(data), True
    except Exception:
        return None, None, False


def git_show_hash(repo_dir: Path, relpath: str) -> tuple:
    """Returns (sha256_hex_or_None, size_or_None, in_git: bool) for HEAD:relpath."""
    relpath_posix = relpath.replace("\\", "/")
    try:
        r = subprocess.run(
            ["git", "show", f"HEAD:{relpath_posix}"],
            cwd=str(repo_dir), capture_output=True, timeout=15,
        )
        if r.returncode != 0:
            return None, None, False
        return sha256_of_bytes(r.stdout), len(r.stdout), True
    except Exception:
        return None, None, False


def strip_noncode(text: str, is_python: bool) -> str:
    """Crude comment/docstring stripper so the destructive-marker scan doesn't fire on prose
    describing git operations rather than invoking them. Errs toward stripping MORE (i.e.
    toward classifying as non-destructive / safe-to-run) only when the line is unambiguously
    inside a string literal a human reading the file would call 'documentation', never for an
    actual subprocess/os.system/shell invocation line."""
    out = []
    in_triple = None
    for line in text.splitlines():
        s = line.strip()
        if is_python:
            if in_triple:
                if in_triple in line:
                    idx = line.find(in_triple)
                    line = line[idx + 3:]
                    in_triple = None
                else:
                    continue
            for q in ('"""', "'''"):
                while q in line:
                    i = line.find(q)
                    before, after = line[:i], line[i + 3:]
                    if in_triple is None:
                        if q in after:
                            j = after.find(q)
                            line = before + after[j + 3:]
                        else:
                            in_triple = q
                            line = before
                            break
                    else:
                        break
            if in_triple:
                continue
            if s.startswith("#"):
                continue
        else:
            if s.startswith("#"):
                continue
        out.append(line)
    return "\n".join(out)


def classify_interpreter(cmd: str) -> str:
    stripped = cmd.strip()
    first = stripped.split()[0] if stripped.split() else ""
    if first in ("bash", "sh", "cd"):
        return "bash"
    if first.startswith("python"):
        return "python"
    if first.lower() in ("powershell", "powershell.exe", "pwsh"):
        return "powershell"
    return "other"


def extract_script_refs(cmd: str) -> list:
    """v4 fix 3a: whole-command-line scan (see ANY_SCRIPT_TOKEN_RE / changelog) rather than
    matching only the token immediately after an interpreter keyword. Order is preserved
    left-to-right, so for a wrapped hook (`bash wrapper.sh target.py`) refs[0] is the wrapper
    and refs[-1] (== "primary" everywhere else in this file) is the actual content script."""
    refs = ANY_SCRIPT_TOKEN_RE.findall(cmd)
    seen, out = set(), []
    for r in refs:
        r = r.replace("${CLAUDE_PROJECT_DIR}/", "").replace("\\", "/").strip("\"'")
        if r and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def is_known_destructive(cmd: str) -> bool:
    for prefix in KNOWN_DESTRUCTIVE_PREFIXES:
        if cmd.strip().startswith(prefix):
            return True
    return False


INVOCATION_CONTEXT_RE = re.compile(
    r'subprocess\.|os\.system\(|Popen\(|check_call|check_output|^\s*(if\s+)?(bash|sh)\s',
)


def scan_destructive(cmd: str, script_bodies: dict) -> tuple:
    """Returns (is_destructive: bool, reason: str).

    A marker match alone is not enough: agent_end_ingest.py and i2_session_page.py contain
    f-string LINES OF MARKDOWN OUTPUT like `w(f"### Commits ... \\`git commit\\` invocation(s)")`
    that mention 'git commit' as prose being written to a report, never as a subprocess call —
    and global-staleness-probe.py mentions 'sync-universal.sh' only to describe what it would
    fix, being a read-only staleness *checker* (its own statusMessage says so). A bare marker
    match therefore requires INVOCATION CONTEXT on the same line (subprocess/os.system/Popen/
    check_call/check_output, or the line itself starting with a shell-command shape like
    `bash foo.sh` / `if bash foo.sh`) before it counts as destructive. This was verified by
    hand against every one of CFL's 17 hook scripts before being encoded here (see the H-1
    report) — this regex is the second, independent check, not the only one.
    """
    if is_known_destructive(cmd):
        return True, "known-destructive: command matches a manually-verified sync-universal.sh/git-pull entry (writes to $HOME/.claude)"
    # scan the raw inline command text itself (comment-stripping doesn't apply to a single
    # settings.json command string, it's not a source file with comment syntax we can trust)
    if DESTRUCTIVE_RE.search(cmd):
        return True, "regex match in inline command text"
    for path_str, body in script_bodies.items():
        if body is None:
            continue
        is_py = path_str.endswith(".py")
        code_only = strip_noncode(body, is_py)
        for line in code_only.splitlines():
            m = DESTRUCTIVE_RE.search(line)
            if m and INVOCATION_CONTEXT_RE.search(line):
                return True, f"regex match with invocation context in {path_str}: {line.strip()[:120]!r}"
    return False, ""


def script_normally_prints(body: str) -> bool:
    if body is None:
        return False
    return bool(re.search(r'\bprint\s*\(|\becho\b|\bWrite-(Output|Host)\b', body))


# ------------------------------------------------------------------------------------------
# Fixtures directory resolution
# ------------------------------------------------------------------------------------------

def default_fixtures_dir():
    """Beside-script hook_fixtures/, else repo-relative scripts/tests/hook_fixtures computed
    from THIS FILE's own location (never cwd) — so a copy of this script published elsewhere
    (e.g. a gists-private drop) resolves against ITSELF, not against whatever directory the
    caller happened to invoke python from. Returns None if neither exists."""
    script_dir = Path(__file__).resolve().parent
    beside = script_dir / "hook_fixtures"
    if beside.is_dir():
        return beside
    # scripts/audit/hook_harness.py -> repo root is two parents up
    repo_root_guess = script_dir.parent.parent
    repo_path = repo_root_guess / "scripts" / "tests" / "hook_fixtures"
    if repo_path.is_dir():
        return repo_path
    return None


def resolve_fixtures_dir(explicit: str):
    """Returns a Path that exists, or exits 3 loudly naming --fixtures."""
    script_dir = Path(__file__).resolve().parent
    beside = script_dir / "hook_fixtures"
    repo_path = script_dir.parent.parent / "scripts" / "tests" / "hook_fixtures"

    if explicit is not None:
        p = Path(explicit)
        if p.is_dir():
            return p
        print(
            f"[hook_harness] ERROR: --fixtures {explicit!r} does not exist or is not a "
            f"directory. Pass a valid --fixtures path.",
            file=sys.stderr,
        )
        sys.exit(3)

    resolved = default_fixtures_dir()
    if resolved is not None:
        return resolved

    print(
        "[hook_harness] ERROR: no --fixtures directory resolved. Checked, in order:\n"
        f"    beside-script : {beside}  (exists={beside.is_dir()})\n"
        f"    repo-relative : {repo_path}  (exists={repo_path.is_dir()})\n"
        "  Pass --fixtures <dir> explicitly naming a hook_fixtures directory.",
        file=sys.stderr,
    )
    sys.exit(3)


# ------------------------------------------------------------------------------------------
# Exit-semantics mapping (v4 fix 1)
# ------------------------------------------------------------------------------------------

def load_exit_semantics(path: str):
    """Loads a per-trunk {"<script-path>": {"<exit-code-str>": "<meaning>"}} JSON map, or
    returns None if path is falsy. Exits 3 loudly if the file is named but unreadable/invalid —
    same discipline as --fixtures: a bad explicit input is a loud stop, never a silent skip."""
    if not path:
        return None
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[hook_harness] ERROR: --exit-semantics {path!r} unreadable/invalid JSON: {e}",
              file=sys.stderr)
        sys.exit(3)
    if not isinstance(data, dict):
        print(f"[hook_harness] ERROR: --exit-semantics {path!r} must be a JSON object", file=sys.stderr)
        sys.exit(3)
    return data


def apply_exit_semantics(row: dict, exit_semantics: dict) -> None:
    """Renames row['class'] to the trunk's documented meaning when the exit code has one.
    Only applies to rows with a recorded non-zero exit (FAIL-CLOSED-VISIBLE or
    NONZERO-WITH-OUTPUT); never touches OK/TIMEOUT-*/SKIPPED-*/BLAMES-SIBLING rows."""
    if not exit_semantics:
        return
    exit_code = row.get("exit")
    if exit_code in (None, 0):
        return
    for m in row.get("script_meta", []):
        mapping = exit_semantics.get(m["path"])
        if mapping and str(exit_code) in mapping:
            meaning = mapping[str(exit_code)]
            old_class = row["class"]
            row["class"] = meaning
            row["notes"] = (
                (row.get("notes", "") + " | " if row.get("notes") else "")
                + f"exit-semantics override: {old_class} -> {meaning} per {m['path']} exit={exit_code}"
            )
            row["exit_semantics_applied"] = {"script": m["path"], "code": exit_code, "meaning": meaning}
            return


# ------------------------------------------------------------------------------------------
# Settings walking
# ------------------------------------------------------------------------------------------

def iter_hook_entries(settings: dict):
    """Yields (event, matcher, group_index, hook_index, hook_dict)."""
    for event, groups in (settings.get("hooks") or {}).items():
        for gi, group in enumerate(groups):
            matcher = group.get("matcher")
            for hi, hook in enumerate(group.get("hooks", [])):
                yield event, matcher, gi, hi, hook


def resolve_fixture(fixtures_dir: Path, event: str, matcher: str, source_hint: str = None):
    """Maps (event, matcher) -> fixture json filename per the harness's own naming convention."""
    key = None
    if event == "SessionStart":
        if matcher and "startup" in matcher:
            key = "sessionstart-startup.json"
        elif matcher and ("compact" in matcher or "clear" in matcher):
            key = "sessionstart-compact.json"
        else:
            key = "sessionstart-startup.json"
    elif event == "PreCompact":
        key = "precompact-auto.json"
    elif event == "PostCompact":
        key = "postcompact.json"
    elif event == "Stop":
        key = "stop.json"
    elif event == "SubagentStop":
        key = "subagentstop.json"
    elif event == "SessionEnd":
        key = "sessionend-other.json"
    elif event == "PostToolUse":
        key = "posttooluse-write.json"
    elif event == "PreToolUse":
        key = "pretooluse-write.json"
    elif event == "UserPromptSubmit":
        key = "userpromptsubmit.json"
    if key is None:
        return None
    p = fixtures_dir / key
    return p if p.exists() else None


def event_timeout(event: str) -> float:
    return DOC_TIMEOUTS.get(event, DEFAULT_CMD_TIMEOUT)


# ------------------------------------------------------------------------------------------
# Scratch clone management
# ------------------------------------------------------------------------------------------

def make_scratch_clone(source_repo: Path) -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "claude" / "hook-scratch"
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"scratch-{os.getpid()}-{int(time.time())}"
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    r = subprocess.run(
        ["git", "clone", "--shared", "--quiet", str(source_repo), str(target)],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(f"scratch clone failed: {r.stderr}")
    return target


def git_status_snapshot(repo: Path) -> str:
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=str(repo), capture_output=True, text=True, timeout=30,
        )
        return r.stdout
    except Exception as e:
        return f"<status failed: {e}>"


def diff_side_effects(before: str, after: str) -> list:
    before_lines = set(l for l in before.splitlines() if l.strip())
    after_lines = set(l for l in after.splitlines() if l.strip())
    return sorted(after_lines - before_lines)


# ------------------------------------------------------------------------------------------
# Row construction
# ------------------------------------------------------------------------------------------

def build_row(trunk, event, matcher, gi, hi, hook, repo_root: Path, scratch,
              fixtures_dir: Path, exec_cap: float, disable_detector: bool, dry_run: bool = False,
              exit_semantics: dict = None):
    cmd = hook.get("command", "")
    declared_timeout = hook.get("timeout", event_timeout(event))
    interpreter = classify_interpreter(cmd)
    script_refs = extract_script_refs(cmd)

    # Static metadata per referenced script (against the ORIGINAL repo, not scratch — the
    # scratch clone is a fresh checkout of the same HEAD, so live-tree drift can only be seen
    # by comparing the repo the caller actually pointed us at against its own git HEAD).
    script_meta = []
    script_bodies = {}
    for ref in script_refs:
        p = (repo_root / ref)
        sha, size, readable = sha256_of_file(p)
        gsha, gsize, in_git = git_show_hash(repo_root, ref)
        sha_match = (readable and in_git and sha == gsha)
        script_meta.append({
            "path": ref, "bytes": size, "readable": readable,
            "in_git": in_git, "git_bytes": gsize, "sha_match": sha_match,
        })
        if readable:
            try:
                script_bodies[ref] = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                script_bodies[ref] = None
        else:
            script_bodies[ref] = None

    destructive, destructive_reason = (False, "") if disable_detector else scan_destructive(cmd, script_bodies)

    primary = script_meta[-1] if script_meta else None
    script_path = ";".join(m["path"] for m in script_meta) if script_meta else None
    script_bytes = primary["bytes"] if primary else None
    sha_match = primary["sha_match"] if primary else None

    row = {
        "trunk": trunk, "event": event, "matcher": matcher,
        "group_index": gi, "hook_index": hi,
        "cmd": cmd, "interpreter": interpreter,
        "script_path": script_path, "script_meta": script_meta,
        "script_bytes": script_bytes, "sha_match": sha_match,
        "declared_timeout_s": declared_timeout, "harness_cap_s": None,
        "exit": None, "stdout_bytes": None, "stdout_sha256": None, "stderr_head": None, "ms": None,
        "class": None, "side_effects": [], "notes": "",
        "executed": False, "destructive_reason": None, "fixture_path": None,
    }

    # v2 fix 1: SKIPPED-DESTRUCTIVE fires ONLY when the scanner actually says so — never as
    # a stand-in for "we didn't check" or "no fixture was available."
    if destructive:
        row["class"] = "SKIPPED-DESTRUCTIVE"
        row["destructive_reason"] = destructive_reason
        row["notes"] = destructive_reason
        return row

    fixture_path = resolve_fixture(fixtures_dir, event, matcher)
    if fixture_path is None:
        # v2 fix 1: a missing INPUT is its own class, not a safety determination.
        row["class"] = "SKIPPED-NO-FIXTURE"
        row["notes"] = f"no fixture for event={event} matcher={matcher} under {fixtures_dir}; not executed"
        return row

    row["fixture_path"] = str(fixture_path)

    if dry_run:
        row["class"] = "DRY-RUN"
        row["notes"] = f"would execute: {cmd!r} against fixture {fixture_path}"
        return row

    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    transcript_src = fixtures_dir / "fixture-transcript.jsonl"
    scratch_transcript = scratch / "_harness_fixture_transcript.jsonl"
    shutil.copyfile(transcript_src, scratch_transcript)

    scratch_bash = str(scratch).replace("\\", "/")
    fixture["cwd"] = scratch_bash
    fixture["transcript_path"] = str(scratch_transcript).replace("\\", "/")
    stdin_bytes = json.dumps(fixture).encode("utf-8")

    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = scratch_bash

    cap = min(float(declared_timeout), exec_cap)
    row["harness_cap_s"] = cap

    before_status = git_status_snapshot(scratch)
    t0 = time.time()
    bash_exe = shutil.which("bash") or "bash"
    row["executed"] = True
    try:
        r = subprocess.run(
            [bash_exe, "-c", cmd], cwd=str(scratch), env=env,
            input=stdin_bytes, capture_output=True, timeout=cap,
        )
        ms = (time.time() - t0) * 1000
        stdout = r.stdout or b""
        stderr = r.stderr or b""
        exit_code = r.returncode
        timed_out = False
    except subprocess.TimeoutExpired as e:
        ms = (time.time() - t0) * 1000
        stdout = e.stdout or b""
        stderr = e.stderr or b""
        exit_code = None
        timed_out = True

    after_status = git_status_snapshot(scratch)
    side_effects = diff_side_effects(before_status, after_status)

    row["exit"] = exit_code
    row["stdout_bytes"] = len(stdout)
    row["stdout_sha256"] = sha256_of_bytes(stdout)
    row["stderr_head"] = stderr[:200].decode("utf-8", errors="replace")
    row["ms"] = round(ms, 1)
    row["side_effects"] = side_effects

    combined = (stdout + stderr).decode("utf-8", errors="replace")
    blames = bool(CRASH_LANGUAGE_RE.search(combined))

    if timed_out:
        # v4 fix 2: which budget actually fired. cap = min(declared, exec_cap); if the harness
        # cap is what limited the run (cap < declared), the harness cut it short WHILE the hook
        # was still inside its own documented budget. If cap == declared (exec_cap >= declared,
        # the default posture), the hook's own declared timeout is what fired.
        if cap < declared_timeout:
            row["class"] = "TIMEOUT-HARNESS-CAP"
            row["notes"] = (f"killed at harness cap {cap:.1f}s, still inside declared budget "
                             f"{declared_timeout:.1f}s — lower --exec-cap is what fired, not the hook's own timeout")
        else:
            row["class"] = "TIMEOUT-DECLARED"
            row["notes"] = f"exceeded the hook's own declared timeout ({declared_timeout:.1f}s)"
    elif blames:
        row["class"] = "BLAMES-SIBLING"
        row["notes"] = "stdout/stderr contains crash-language naming another hook/script"
    elif exit_code == 0 and len(stdout) == 0:
        any_zero_or_unreadable = any(
            (m["bytes"] == 0 or not m["readable"]) for m in script_meta
        )
        expected_output = any(script_normally_prints(script_bodies.get(m["path"])) for m in script_meta)
        failopen_detector_disabled = bool(os.environ.get("HOOK_HARNESS_DISABLE_FAILOPEN_DETECTOR"))
        if failopen_detector_disabled:
            row["class"] = "OK"
            row["notes"] = "FAIL-OPEN-SILENT detector disabled via HOOK_HARNESS_DISABLE_FAILOPEN_DETECTOR — graded OK regardless (demonstration path only)"
            return row
        # v3 rule (2026-09-02, Professional's withdrawal of its own recorder finding): non-empty
        # side_effects is RUNTIME proof of work and dominates any static guess about stdout. A hook
        # whose echoes are redirected into files is silent by design, not fail-open. Only a script
        # that is 0 bytes / unreadable can still be FAIL-OPEN-SILENT with side effects present.
        if side_effects and not any_zero_or_unreadable:
            row["class"] = "OK"
            row["notes"] = "exit 0, 0 stdout bytes, but %d side-effect file(s) recorded: work done to files, silent by design" % len(side_effects)
        elif (interpreter == "python" and any_zero_or_unreadable) or expected_output:
            row["class"] = "FAIL-OPEN-SILENT"
            row["notes"] = "exit 0, 0 stdout bytes, and " + (
                "target script is 0 bytes or unreadable" if any_zero_or_unreadable
                else "script body normally prints something"
            )
        else:
            row["class"] = "OK"
            row["notes"] = "exit 0, silent — script has no visible-output expectation on this fixture"
    elif exit_code != 0:
        # v4 fix 1: FAIL-CLOSED-VISIBLE reserved for a genuinely SILENT non-zero exit. A
        # non-zero exit WITH stdout is trunk-defined signal (findings-exist, unavailable-by-
        # design, etc.) until --exit-semantics says otherwise.
        if len(stdout) == 0:
            row["class"] = "FAIL-CLOSED-VISIBLE"
        else:
            row["class"] = "NONZERO-WITH-OUTPUT"
            row["notes"] = (f"exit {exit_code} with {len(stdout)} stdout byte(s): trunk-defined "
                             "semantics; check the script's documented exit codes")
    else:
        row["class"] = "OK"

    apply_exit_semantics(row, exit_semantics)
    return row


# ------------------------------------------------------------------------------------------
# --degrade phase (v4 fix 3)
# ------------------------------------------------------------------------------------------

def _is_within_scratch(scratch: Path, candidate: Path) -> bool:
    """True iff candidate resolves to a path inside scratch. Used to tell a genuine
    in-scratch primary apart from a script referenced by absolute path outside the harness's
    own scratch clone (Secretary's v4 --degrade finding: 13 of 14 executed rows on its own
    trunk are invoked by absolute path, e.g. `powershell -File "G:\\...\\index-check.ps1"`, so
    the scratch clone's copy is never what actually runs and truncating it proves nothing)."""
    try:
        candidate.resolve().relative_to(scratch.resolve())
        return True
    except ValueError:
        return False


def truncate_primaries(scratch: Path, baseline_rows: list) -> tuple:
    """Truncates each EXECUTED baseline row's primary script (script_meta[-1] — the actual
    content script, not a wrapper/interpreter shim; see changelog fix 3) to 0 bytes inside the
    scratch clone. Deduped by path (postcompact_pipeline.py appears under two SessionStart
    matchers, for instance — truncate once).

    v5 fix (Secretary's finding, running v4 --degrade on its own trunk): a primary path that is
    absolute, or that otherwise resolves outside the scratch clone, is NEVER truncated (the
    harness only ever writes inside its own scratch tree) — but v4 silently dropped that row
    with no signal, so its degraded-phase re-run executed the REAL script at its real path,
    unmodified, and any resulting OK/other class was indistinguishable in the summary from a
    row that had genuinely been degraded. v5 records those paths separately instead of folding
    them into "not truncated, say nothing".

    Returns (truncated: sorted list of relpaths actually zeroed inside scratch,
             undegradable: {primary_path: resolved_absolute_path_str} for every primary that
             resolves outside the scratch clone and was therefore left untouched)."""
    truncated = set()
    undegradable = {}
    handled = set()
    for row in baseline_rows:
        if not row.get("executed") or not row.get("script_meta"):
            continue
        primary_path = row["script_meta"][-1]["path"]
        if primary_path in handled:
            continue
        handled.add(primary_path)
        candidate = Path(primary_path)
        if not candidate.is_absolute():
            candidate = scratch / primary_path
        if not _is_within_scratch(scratch, candidate):
            undegradable[primary_path] = str(candidate)
            continue
        if candidate.is_file():
            candidate.write_bytes(b"")
            truncated.add(primary_path)
    return sorted(truncated), undegradable


def run_degrade_phase(args, entries, baseline_rows, fixtures_dir, scratch, exit_semantics):
    """Truncates primaries in the SAME scratch clone the baseline pass used, then re-runs every
    row that actually executed at baseline, tagged phase: 'degraded'. Prints, per row, the
    stated expectation and flags a FAIL-OPEN-SILENT finding explicitly (this mode's reason for
    existing).

    v5: a row whose primary resolves outside the scratch clone (absolute-path invocation) is
    NEVER re-executed here — re-running it would hit the real, un-truncated script at its real
    path and produce a class that looks like a completed degrade measurement while nothing was
    actually degraded. Such a row is instead classed UNDEGRADABLE-ABSOLUTE-PATH directly, with
    the resolved path recorded in notes, and executed is left False for that phase."""
    project_dir = Path(args.project_dir).resolve()
    entries_by_key = {(e, m, gi, hi): hook for e, m, gi, hi, hook in entries}
    truncated, undegradable = truncate_primaries(scratch, baseline_rows)
    print(f"[hook_harness] --degrade: truncated {len(truncated)} primary script(s) to 0 bytes "
          f"in scratch clone (never the real tree): {truncated}", file=sys.stderr)
    if undegradable:
        print(f"[hook_harness] --degrade: {len(undegradable)} primary script(s) resolve outside "
              f"the scratch clone (absolute-path invocation) -- declined to truncate, classed "
              f"UNDEGRADABLE-ABSOLUTE-PATH, not re-run: {undegradable}", file=sys.stderr)

    degraded_rows = []
    for row in baseline_rows:
        if not row.get("executed"):
            continue
        key = (row["event"], row["matcher"], row["group_index"], row["hook_index"])
        hook = entries_by_key[key]
        primary_path = row["script_meta"][-1]["path"] if row.get("script_meta") else None

        if primary_path in undegradable:
            drow = dict(row)  # carry static metadata (script_meta, interpreter, etc.) forward
            drow["phase"] = "degraded"
            drow["degrade_expectation"] = "wrapper/interpreter should fail CLOSED and VISIBLE"
            drow["degraded_primary"] = primary_path
            drow["class"] = "UNDEGRADABLE-ABSOLUTE-PATH"
            drow["executed"] = False
            drow["exit"] = None
            drow["stdout_bytes"] = None
            drow["stdout_sha256"] = None
            drow["stderr_head"] = None
            drow["ms"] = None
            drow["side_effects"] = []
            drow["notes"] = (
                f"primary script resolves outside the scratch clone ({undegradable[primary_path]}); "
                "harness declined to truncate a file outside its own scratch tree, so this row was "
                "not re-run under --degrade (Secretary's v4 finding: re-running against the real, "
                "untruncated script would produce a class that looks like a completed degrade "
                "measurement when nothing was actually degraded)"
            )
            print(f"  DEGRADED {row['event']}/{row['matcher']}/{row['group_index']}.{row['hook_index']} "
                  f"(primary={primary_path}): UNDEGRADABLE-ABSOLUTE-PATH (declined -- outside scratch, not re-run)",
                  file=sys.stderr)
            degraded_rows.append(drow)
            continue

        drow = build_row(
            args.trunk, row["event"], row["matcher"], row["group_index"], row["hook_index"], hook,
            project_dir, scratch, fixtures_dir, args.exec_cap, args.disable_detector,
            exit_semantics=exit_semantics,
        )
        drow["phase"] = "degraded"
        drow["degrade_expectation"] = "wrapper/interpreter should fail CLOSED and VISIBLE"
        drow["degraded_primary"] = primary_path
        finding = " <-- FINDING (fail-open in degraded phase)" if drow["class"] == "FAIL-OPEN-SILENT" else ""
        print(f"  DEGRADED {row['event']}/{row['matcher']}/{row['group_index']}.{row['hook_index']} "
              f"(primary={drow['degraded_primary']}): {drow['class']}{finding}", file=sys.stderr)
        degraded_rows.append(drow)
    return degraded_rows, truncated, undegradable


def flag_duplicate_work_signature(rows: list) -> int:
    """(v4, Professional's addition off its own v2 run — pipeline side_effects 1/0/0 across
    compact/startup/resume; render-sessions 331 vs 273 bytes.) Same command, same event, run
    more than once (e.g. postcompact_pipeline.py under both the SessionStart startup matcher
    and the SessionStart compact|clear matcher): if an EARLIER invocation recorded side_effects
    and a LATER row with the byte-identical cmd under the SAME event recorded ZERO side_effects
    with a byte-identical stdout hash, the later run most likely did no new work — an
    idempotent 'already done'/acceptance-check branch was satisfied by the earlier invocation
    inside the SAME scratch clone. This is a NOTE, never a class change: it does not know
    whether that's correct (idempotent by design) or a race (see
    wiki/intake-triage/HOOK-RACES-fleet-2026-09-02.md) — only that the signature exists.
    Returns the count of rows flagged."""
    seen = {}  # (event, cmd) -> most recent row seen carrying non-empty side_effects
    flagged = 0
    for row in rows:
        if not row.get("executed"):
            continue
        key = (row["event"], row["cmd"])
        prior = seen.get(key)
        if prior is not None and prior.get("side_effects") and not row.get("side_effects") \
                and row.get("stdout_sha256") is not None \
                and row.get("stdout_sha256") == prior.get("stdout_sha256"):
            note = ("DUPLICATE-WORK-SIGNATURE: identical cmd under this event already produced "
                    "side effects earlier in this run; this row: 0 side effects, byte-identical stdout")
            row["notes"] = ((row.get("notes", "") + " | ") if row.get("notes") else "") + note
            row["duplicate_work_signature"] = True
            flagged += 1
        if row.get("side_effects"):
            seen[key] = row
        elif key not in seen:
            seen[key] = row
    return flagged


# ------------------------------------------------------------------------------------------
# Main run
# ------------------------------------------------------------------------------------------

def run_full(args, fixtures_dir: Path, exit_semantics: dict = None):
    settings_path = Path(args.settings)
    project_dir = Path(args.project_dir).resolve()

    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    entries = list(iter_hook_entries(settings))

    print(f"[hook_harness] settings={settings_path} hook entries={len(entries)}", file=sys.stderr)
    print(f"[hook_harness] fixtures={fixtures_dir}", file=sys.stderr)
    print(f"[hook_harness] cloning scratch from {project_dir} ...", file=sys.stderr)
    scratch = make_scratch_clone(project_dir)
    print(f"[hook_harness] scratch clone at {scratch}", file=sys.stderr)

    rows = []
    for event, matcher, gi, hi, hook in entries:
        row = build_row(
            args.trunk, event, matcher, gi, hi, hook,
            project_dir, scratch, fixtures_dir, args.exec_cap, args.disable_detector,
            exit_semantics=exit_semantics,
        )
        row["phase"] = "baseline"
        rows.append(row)
        print(f"  {event}/{matcher}/{gi}.{hi}: {row['class']}", file=sys.stderr)

    duplicate_work_count = flag_duplicate_work_signature(rows)
    if duplicate_work_count:
        print(f"[hook_harness] DUPLICATE-WORK-SIGNATURE flagged on {duplicate_work_count} row(s) "
              f"(see notes)", file=sys.stderr)

    degraded_rows = []
    truncated = []
    undegradable = {}
    if args.degrade:
        degraded_rows, truncated, undegradable = run_degrade_phase(args, entries, rows, fixtures_dir, scratch, exit_semantics)

    if not args.keep_scratch:
        shutil.rmtree(scratch, ignore_errors=True)

    all_rows = rows + degraded_rows
    executed_baseline = sum(1 for row in rows if row.get("executed"))
    executed_degraded = sum(1 for row in degraded_rows if row.get("executed"))

    counts_baseline = {}
    for row in rows:
        counts_baseline[row["class"]] = counts_baseline.get(row["class"], 0) + 1
    counts_degraded = {}
    for row in degraded_rows:
        counts_degraded[row["class"]] = counts_degraded.get(row["class"], 0) + 1

    # v5: executed_n / degraded_n / undegradable_n (Secretary's finding — see run_degrade_phase
    # and truncate_primaries docstrings). executed_n is the baseline-executed count eligible for
    # degrade; degraded_n is how many of those were actually truncated-and-re-run;
    # undegradable_n is how many resolved outside the scratch clone and were declined. When
    # --degrade did not run, all three collapse to 0/0/0.
    executed_n = executed_baseline if args.degrade else 0
    undegradable_n = sum(1 for row in degraded_rows if row.get("class") == "UNDEGRADABLE-ABSOLUTE-PATH")
    degraded_n = len(degraded_rows) - undegradable_n

    # v2 fix 3: a zero-execution run is NOT a clean report. Write a footer row into the
    # jsonl that says so explicitly, in addition to every per-hook row.
    footer = {
        "footer": True, "trunk": args.trunk,
        "rows_baseline": len(rows), "executed_baseline": executed_baseline,
        "note": "NOTHING EXECUTED" if executed_baseline == 0 else f"{executed_baseline}/{len(rows)} baseline rows executed a subprocess",
        "degrade_ran": bool(args.degrade),
        "rows_degraded": len(degraded_rows), "executed_degraded": executed_degraded,
        "degraded_primaries_truncated": truncated,
        "degraded_primaries_undegradable": undegradable,
        "executed_n": executed_n, "degraded_n": degraded_n, "undegradable_n": undegradable_n,
        "counts_baseline": counts_baseline,
        "counts_degraded": counts_degraded,
        "duplicate_work_signature_count": duplicate_work_count,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row) + "\n")
        f.write(json.dumps(footer) + "\n")

    md_path = out_path.with_suffix(".md")
    lines = []
    lines.append(f"# Hook harness run — {args.trunk} — {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append(f"Settings: `{settings_path}`  ")
    lines.append(f"Fixtures: `{fixtures_dir}`  ")
    lines.append(f"Hook entries in settings.json: **{len(entries)}**  ")
    lines.append(f"Baseline rows written: **{len(rows)}**  ")
    lines.append(f"Entries-with-a-row == settings-entry-count: **{len(rows) == len(entries)}**  ")
    lines.append(f"Baseline executed (subprocess actually ran): **{executed_baseline}**  ")
    lines.append(f"DUPLICATE-WORK-SIGNATURE flagged (note, not a class): **{duplicate_work_count}**")
    if executed_baseline == 0:
        lines.append("")
        lines.append("**NOTHING EXECUTED** — every row was skipped (no fixture and/or destructive). "
                      "This is not a passing run; see counts below.")
    lines.append("")
    lines.append("## Baseline — summary by class")
    lines.append("")
    lines.append("| class | count |")
    lines.append("|---|---|")
    for cls, n in sorted(counts_baseline.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {cls} | {n} |")
    lines.append("")
    lines.append("## Baseline rows")
    lines.append("")
    lines.append("| event | matcher | idx | interpreter | script_path | script_bytes | sha_match | exit | stdout_bytes | declared_timeout_s | harness_cap_s | ms | executed | class |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| {row['event']} | {row['matcher']} | {row['group_index']}.{row['hook_index']} "
            f"| {row['interpreter']} | {row['script_path']} | {row['script_bytes']} "
            f"| {row['sha_match']} | {row['exit']} | {row['stdout_bytes']} "
            f"| {row['declared_timeout_s']} | {row['harness_cap_s']} | {row['ms']} "
            f"| {row['executed']} | {row['class']} |"
        )
    if args.degrade:
        lines.append("")
        lines.append(f"## Degraded phase — {len(truncated)} primary script(s) truncated to 0 bytes: `{truncated}`")
        lines.append("")
        # v5, Secretary's finding: state the partial-coverage bound explicitly rather than
        # letting a full-looking rows table imply a full-looking measurement.
        lines.append(f"degraded {degraded_n} of {executed_n} executed ({undegradable_n} undegradable: absolute paths)  ")
        if undegradable:
            lines.append(f"Undegradable primaries (resolve outside scratch clone, declined and not re-run): `{undegradable}`  ")
        lines.append(f"Degraded rows re-run: **{len(degraded_rows)}**  ")
        lines.append(f"Degraded executed: **{executed_degraded}**  ")
        lines.append("Expectation per row: *wrapper/interpreter should fail CLOSED and VISIBLE*")
        lines.append("")
        lines.append("## Degraded — summary by class")
        lines.append("")
        lines.append("| class | count |")
        lines.append("|---|---|")
        for cls, n in sorted(counts_degraded.items(), key=lambda kv: -kv[1]):
            lines.append(f"| {cls} | {n} |")
        lines.append("")
        lines.append("## Degraded rows")
        lines.append("")
        lines.append("| event | matcher | idx | primary (truncated) | exit | stdout_bytes | class | finding |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for row in degraded_rows:
            finding = "FAIL-OPEN under degrade" if row["class"] == "FAIL-OPEN-SILENT" else ""
            lines.append(
                f"| {row['event']} | {row['matcher']} | {row['group_index']}.{row['hook_index']} "
                f"| {row.get('degraded_primary')} | {row['exit']} | {row['stdout_bytes']} "
                f"| {row['class']} | {finding} |"
            )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[hook_harness] wrote {out_path} ({len(all_rows)} rows + footer)", file=sys.stderr)
    print(f"[hook_harness] wrote {md_path}", file=sys.stderr)
    print(json.dumps({"baseline": counts_baseline, "degraded": counts_degraded}, indent=2))
    print(json.dumps(footer, indent=2))
    return rows, degraded_rows, entries, executed_baseline, degraded_n, undegradable_n


# ------------------------------------------------------------------------------------------
# Dry run
# ------------------------------------------------------------------------------------------

def run_dry(args, fixtures_dir: Path):
    settings_path = Path(args.settings)
    project_dir = Path(args.project_dir).resolve()
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    entries = list(iter_hook_entries(settings))

    print(f"[hook_harness] DRY RUN — settings={settings_path} entries={len(entries)} fixtures={fixtures_dir}",
          file=sys.stderr)
    print(f"{'event':<16} {'matcher':<12} {'idx':<6} {'class':<20} fixture / reason")
    print("-" * 100)
    for event, matcher, gi, hi, hook in entries:
        row = build_row(
            args.trunk, event, matcher, gi, hi, hook,
            project_dir, None, fixtures_dir, args.exec_cap, args.disable_detector, dry_run=True,
        )
        detail = row.get("fixture_path") or row.get("notes") or ""
        print(f"{event:<16} {str(matcher):<12} {gi}.{hi:<4} {row['class']:<20} {detail}")
    return 0


# ------------------------------------------------------------------------------------------
# Selftest
# ------------------------------------------------------------------------------------------

# v4 fix 3: a minimal, self-contained fail-closed wrapper — NOT a copy of CFL's own
# .claude/hooks/py_closed.sh (which writes to N:\claude-gists-private and is CFL-specific).
# This stub carries only the contract the selftest needs to prove: refuse to launch python
# against a missing/empty target, and say so loudly on stderr with a non-zero exit.
SELFTEST_PY_CLOSED_SH = (
    "#!/bin/bash\n"
    "set -uo pipefail\n"
    'script="${1:-}"\n'
    "shift || true\n"
    'if [ ! -f "$script" ] || [ ! -s "$script" ]; then\n'
    "  printf 'HOOK-FAULT %s zero-byte-or-missing\\n' \"$script\" >&2\n"
    "  exit 1\n"
    "fi\n"
    'exec python "$script" "$@"\n'
)


def _build_selftest_tree():
    """Builds the synthetic tmp repo + settings.json with three known-shape hooks. Returns
    (tmp_dir, settings_dict)."""
    tmp = Path(tempfile.mkdtemp(prefix="hook-harness-selftest-"))

    # (a) python hook, planted 0-byte script -> FAIL-OPEN-SILENT with detector ON, OK with
    #     detector OFF. This is the row that discriminates the two directions.
    zero_py = tmp / "zero_hook.py"
    zero_py.write_bytes(b"")

    # (b) bash hook pointing at a script path that does not exist on disk at all — the
    # documented Windows substitute for chmod 000 (no POSIX permission bits here). Exit
    # code is nonzero either way, so this row is identical in both directions by design —
    # it's the control that proves the detector isn't just "everything changes."
    ghost_sh_relpath = "no_such_dir/ghost_hook.sh"

    # (c) good hook -> OK in both directions.
    good_sh = tmp / "good_hook.sh"
    good_sh.write_text("#!/bin/bash\necho selftest-ok\n", encoding="utf-8")

    subprocess.run(["git", "init", "-q"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "-c", "user.email=h@h", "-c", "user.name=h", "commit", "-q", "-m", "init"],
                    cwd=str(tmp), capture_output=True)

    settings = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Write",
                    "hooks": [
                        {"type": "command", "command": "python zero_hook.py", "timeout": 15},
                        {"type": "command", "command": f"bash {ghost_sh_relpath}", "timeout": 15},
                        {"type": "command", "command": "bash good_hook.sh", "timeout": 15},
                    ],
                }
            ]
        }
    }
    (tmp / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    return tmp, settings


def _run_selftest_rows(tmp: Path, settings: dict, fixtures_dir: Path, disable_detector: bool,
                        env_disable_failopen: bool):
    """Runs the three-hook synthetic settings once, with HOOK_HARNESS_DISABLE_FAILOPEN_DETECTOR
    set/unset per env_disable_failopen, restoring the prior env value afterward. Returns list
    of row dicts."""
    env_key = "HOOK_HARNESS_DISABLE_FAILOPEN_DETECTOR"
    had_prior = env_key in os.environ
    prior_value = os.environ.get(env_key)
    try:
        if env_disable_failopen:
            os.environ[env_key] = "1"
        elif env_key in os.environ:
            del os.environ[env_key]

        scratch = make_scratch_clone(tmp)
        try:
            entries = list(iter_hook_entries(settings))
            rows = []
            for event, matcher, gi, hi, hook in entries:
                row = build_row("selftest", event, matcher, gi, hi, hook, tmp, scratch,
                                 fixtures_dir, 30.0, disable_detector)
                rows.append(row)
            return rows
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    finally:
        if had_prior:
            os.environ[env_key] = prior_value
        elif env_key in os.environ:
            del os.environ[env_key]


def _selftest_both_directions(fixtures_dir: Path, disable_detector: bool) -> bool:
    """v2 fix 5, unchanged: asserts BOTH FAIL-OPEN-SILENT detector directions in one
    invocation. Returns True iff both directions match their documented class lists AND
    differ from each other."""
    tmp, settings = _build_selftest_tree()
    try:
        expect_on = ["FAIL-OPEN-SILENT", "FAIL-CLOSED-VISIBLE", "OK"]
        expect_off = ["OK", "FAIL-CLOSED-VISIBLE", "OK"]

        rows_on = _run_selftest_rows(tmp, settings, fixtures_dir, disable_detector,
                                      env_disable_failopen=False)
        rows_off = _run_selftest_rows(tmp, settings, fixtures_dir, disable_detector,
                                       env_disable_failopen=True)

        got_on = [r["class"] for r in rows_on]
        got_off = [r["class"] for r in rows_off]

        print("[selftest 1/4: both-directions] direction A (detector ON)  expected:", expect_on)
        print("[selftest 1/4: both-directions] direction A (detector ON)  got:     ", got_on)
        for i, row in enumerate(rows_on):
            print(f"[selftest]   A.({'abc'[i]}) cmd={row['cmd']!r} -> exit={row['exit']} "
                  f"stdout_bytes={row['stdout_bytes']} executed={row['executed']} class={row['class']}")

        print("[selftest 1/4: both-directions] direction B (detector OFF) expected:", expect_off)
        print("[selftest 1/4: both-directions] direction B (detector OFF) got:     ", got_off)
        for i, row in enumerate(rows_off):
            print(f"[selftest]   B.({'abc'[i]}) cmd={row['cmd']!r} -> exit={row['exit']} "
                  f"stdout_bytes={row['stdout_bytes']} executed={row['executed']} class={row['class']}")

        on_ok = (got_on == expect_on)
        off_ok = (got_off == expect_off)
        directions_differ = (got_on != got_off)

        if not on_ok:
            print("[selftest 1/4] FAIL — direction A (detector ON) did not match the documented classes")
        if not off_ok:
            print("[selftest 1/4] FAIL — direction B (detector OFF) did not match the documented classes")
        if not directions_differ:
            print("[selftest 1/4] FAIL — detector ON and detector OFF produced the IDENTICAL class list; "
                  "the positive control is not discriminating anything (this is exactly what falsified v1)")

        ok = on_ok and off_ok and directions_differ
        print(f"[selftest 1/4: both-directions] {'PASS' if ok else 'FAIL'}")
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _build_selftest_tree_nonzero():
    """(v4) A hook that prints, THEN exits 3 — the shape Secretary's index-check.ps1 /
    usage_reader.py document as a loud, correct signal, not a crash."""
    tmp = Path(tempfile.mkdtemp(prefix="hook-harness-selftest-nonzero-"))
    script = tmp / "prints_and_exits3.py"
    script.write_text("print('findings: 2')\nimport sys\nsys.exit(3)\n", encoding="utf-8")
    settings = {
        "hooks": {
            "PostToolUse": [
                {"matcher": "Write", "hooks": [
                    {"type": "command", "command": "python prints_and_exits3.py", "timeout": 15},
                ]}
            ]
        }
    }
    (tmp / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "-c", "user.email=h@h", "-c", "user.name=h", "commit", "-q", "-m", "init"],
                    cwd=str(tmp), capture_output=True)
    return tmp, settings


def _selftest_nonzero_with_output(fixtures_dir: Path) -> bool:
    """(v4, sub-test 2) A non-zero exit WITH stdout must grade NONZERO-WITH-OUTPUT, not
    FAIL-CLOSED-VISIBLE — and an --exit-semantics mapping must rename it to the trunk's own
    documented meaning."""
    tmp, settings = _build_selftest_tree_nonzero()
    try:
        scratch = make_scratch_clone(tmp)
        try:
            entries = list(iter_hook_entries(settings))
            event, matcher, gi, hi, hook = entries[0]
            row_plain = build_row("selftest", event, matcher, gi, hi, hook, tmp, scratch,
                                   fixtures_dir, 30.0, False)
            print(f"[selftest 2/4: nonzero-with-output] plain: exit={row_plain['exit']} "
                  f"stdout_bytes={row_plain['stdout_bytes']} class={row_plain['class']}")
            plain_ok = (row_plain["class"] == "NONZERO-WITH-OUTPUT" and row_plain["exit"] == 3
                        and row_plain["stdout_bytes"] > 0)

            semantics = {"prints_and_exits3.py": {"3": "FINDINGS-EXIST"}}
            row_mapped = build_row("selftest", event, matcher, gi, hi, hook, tmp, scratch,
                                    fixtures_dir, 30.0, False, exit_semantics=semantics)
            print(f"[selftest 2/4: nonzero-with-output] mapped: class={row_mapped['class']} "
                  f"applied={row_mapped.get('exit_semantics_applied')}")
            mapped_ok = (row_mapped["class"] == "FINDINGS-EXIST")

            ok = plain_ok and mapped_ok
            print(f"[selftest 2/4: nonzero-with-output] {'PASS' if ok else 'FAIL'}")
            return ok
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _build_selftest_tree_sleep():
    tmp = Path(tempfile.mkdtemp(prefix="hook-harness-selftest-sleep-"))
    script = tmp / "sleep_hook.sh"
    script.write_text("#!/bin/bash\nsleep 3\necho done\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "-c", "user.email=h@h", "-c", "user.name=h", "commit", "-q", "-m", "init"],
                    cwd=str(tmp), capture_output=True)
    return tmp


def _selftest_timeout_classes(fixtures_dir: Path) -> bool:
    """(v4, sub-test 3) Same sleeping (3s) script under two declared-timeout / --exec-cap
    combinations: declared=1s/exec_cap=30 -> the DECLARED budget is what fires (cap==declared);
    declared=30s/exec_cap=1 -> the HARNESS CAP is what fires while the hook is still inside its
    own declared budget."""
    tmp = _build_selftest_tree_sleep()
    try:
        scratch = make_scratch_clone(tmp)
        try:
            hook_declared_short = {"type": "command", "command": "bash sleep_hook.sh", "timeout": 1}
            row_declared = build_row("selftest", "PostToolUse", "Write", 0, 0, hook_declared_short,
                                      tmp, scratch, fixtures_dir, 30.0, False)
            print(f"[selftest 3/4: timeout] declared=1s exec_cap=30s -> class={row_declared['class']} "
                  f"harness_cap_s={row_declared['harness_cap_s']} declared_timeout_s={row_declared['declared_timeout_s']}")
            declared_ok = (row_declared["class"] == "TIMEOUT-DECLARED")

            hook_declared_long = {"type": "command", "command": "bash sleep_hook.sh", "timeout": 30}
            row_cap = build_row("selftest", "PostToolUse", "Write", 0, 1, hook_declared_long,
                                 tmp, scratch, fixtures_dir, 1.0, False)
            print(f"[selftest 3/4: timeout] declared=30s exec_cap=1s -> class={row_cap['class']} "
                  f"harness_cap_s={row_cap['harness_cap_s']} declared_timeout_s={row_cap['declared_timeout_s']}")
            cap_ok = (row_cap["class"] == "TIMEOUT-HARNESS-CAP")

            ok = declared_ok and cap_ok
            print(f"[selftest 3/4: timeout] {'PASS' if ok else 'FAIL'}")
            return ok
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _build_selftest_tree_degrade():
    """(v4, sub-test 4) Two hooks: a direct python hook, and the same shape behind a minimal
    fail-closed wrapper stub (SELFTEST_PY_CLOSED_SH). Both start OK at baseline."""
    tmp = Path(tempfile.mkdtemp(prefix="hook-harness-selftest-degrade-"))
    (tmp / "good_direct.py").write_text("print('direct-ok')\n", encoding="utf-8")
    (tmp / "good_wrapped.py").write_text("print('wrapped-ok')\n", encoding="utf-8")
    (tmp / "py_closed_stub.sh").write_text(SELFTEST_PY_CLOSED_SH, encoding="utf-8")
    settings = {
        "hooks": {
            "PostToolUse": [
                {"matcher": "Write", "hooks": [
                    {"type": "command", "command": "python good_direct.py", "timeout": 15},
                    {"type": "command", "command": "bash py_closed_stub.sh good_wrapped.py", "timeout": 15},
                ]}
            ]
        }
    }
    (tmp / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "-c", "user.email=h@h", "-c", "user.name=h", "commit", "-q", "-m", "init"],
                    cwd=str(tmp), capture_output=True)
    return tmp, settings


def _selftest_degrade_phase(fixtures_dir: Path) -> bool:
    """(v4, sub-test 4) Proves the --degrade design decision itself (truncate the PRIMARY,
    not every referenced script): the direct hook's target is its own only script (== primary)
    and truncating it must grade FAIL-OPEN-SILENT; the wrapped hook's primary is
    good_wrapped.py (refs = [py_closed_stub.sh, good_wrapped.py], primary = refs[-1]) — the
    wrapper script itself is left untouched, so it is expected to catch the corrupted target
    and grade FAIL-CLOSED-VISIBLE."""
    tmp, settings = _build_selftest_tree_degrade()
    try:
        scratch = make_scratch_clone(tmp)
        try:
            entries = list(iter_hook_entries(settings))
            baseline_rows = []
            for event, matcher, gi, hi, hook in entries:
                row = build_row("selftest", event, matcher, gi, hi, hook, tmp, scratch,
                                 fixtures_dir, 30.0, False)
                row["phase"] = "baseline"
                baseline_rows.append(row)
            baseline_classes = [r["class"] for r in baseline_rows]
            print(f"[selftest 4/4: degrade] baseline classes: {baseline_classes} "
                  f"(primaries: {[r['script_meta'][-1]['path'] for r in baseline_rows]})")
            baseline_ok = baseline_classes == ["OK", "OK"]

            class _Args:
                pass
            fake_args = _Args()
            fake_args.trunk = "selftest"
            fake_args.project_dir = str(tmp)
            fake_args.exec_cap = 30.0
            fake_args.disable_detector = False
            degraded_rows, truncated, undegradable = run_degrade_phase(
                fake_args, entries, baseline_rows, fixtures_dir, scratch, exit_semantics=None
            )
            got = {(r["cmd"]): r["class"] for r in degraded_rows}
            print(f"[selftest 4/4: degrade] truncated={truncated} undegradable={undegradable} degraded classes: {got}")

            direct_class = got.get("python good_direct.py")
            wrapped_class = got.get("bash py_closed_stub.sh good_wrapped.py")
            direct_ok = (direct_class == "FAIL-OPEN-SILENT")
            wrapped_ok = (wrapped_class == "FAIL-CLOSED-VISIBLE")

            ok = baseline_ok and direct_ok and wrapped_ok
            print(f"[selftest 4/4: degrade] direct={direct_class} (want FAIL-OPEN-SILENT) "
                  f"wrapped={wrapped_class} (want FAIL-CLOSED-VISIBLE) -> {'PASS' if ok else 'FAIL'}")
            return ok
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _build_selftest_tree_timeout_sideeffect():
    """(v4, Professional's addition) A hook that writes a file THEN sleeps past its cap: the
    side-effect write happens, but the row must still grade TIMEOUT-*, never OK. Proves the
    v3 ordering (the `if timed_out` branch is checked, and returns, before the side_effects
    promotion under the `exit_code == 0` arm) can't regress silently."""
    tmp = Path(tempfile.mkdtemp(prefix="hook-harness-selftest-timeout-sideeffect-"))
    script = tmp / "writes_then_sleeps.sh"
    script.write_text("#!/bin/bash\necho hi > out.txt\nsleep 5\necho done\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "-c", "user.email=h@h", "-c", "user.name=h", "commit", "-q", "-m", "init"],
                    cwd=str(tmp), capture_output=True)
    return tmp


def _selftest_timeout_outranks_sideeffects(fixtures_dir: Path) -> bool:
    tmp = _build_selftest_tree_timeout_sideeffect()
    try:
        scratch = make_scratch_clone(tmp)
        try:
            hook = {"type": "command", "command": "bash writes_then_sleeps.sh", "timeout": 1}
            row = build_row("selftest", "PostToolUse", "Write", 0, 0, hook, tmp, scratch,
                             fixtures_dir, 30.0, False)
            print(f"[selftest 5/5: timeout-outranks-sideeffects] class={row['class']} "
                  f"side_effects={row['side_effects']} (want TIMEOUT-*, not OK, despite the write)")
            ok = row["class"] in ("TIMEOUT-DECLARED", "TIMEOUT-HARNESS-CAP") and bool(row["side_effects"])
            print(f"[selftest 5/5: timeout-outranks-sideeffects] {'PASS' if ok else 'FAIL'}")
            return ok
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _build_selftest_tree_undegradable():
    """(v5, Secretary's finding) A repo with two hooks: a normal in-scratch python hook (its
    primary IS truncatable), and a hook whose command references a script by ABSOLUTE path
    outside the tmp repo entirely — the shape of Secretary's own v4 --degrade run, where
    `powershell -File "G:\\...\\index-check.ps1"` never resolves inside the harness's scratch
    clone. The external script lives under the same LOCALAPPDATA base make_scratch_clone()
    already uses (measured space-free on this machine), so the absolute-path token survives
    ANY_SCRIPT_TOKEN_RE's whitespace-delimited match — this selftest proves the
    UNDEGRADABLE-ABSOLUTE-PATH class and the exit-6 branch; it does NOT prove the token regex
    correctly extracts a quoted absolute path containing a space (that is a separate, narrower
    known limitation — see the report)."""
    tmp = Path(tempfile.mkdtemp(prefix="hook-harness-selftest-undegradable-"))
    (tmp / "in_scratch_hook.py").write_text("print('in-scratch-ok')\n", encoding="utf-8")

    external_base = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "claude" / "hook-harness-selftest-external"
    external_base.mkdir(parents=True, exist_ok=True)
    external_dir = Path(tempfile.mkdtemp(prefix="ext-", dir=str(external_base)))
    external_script = external_dir / "external_absolute_target.py"
    external_script.write_text("print('external-ok')\n", encoding="utf-8")
    external_posix = str(external_script).replace("\\", "/")

    settings = {
        "hooks": {
            "PostToolUse": [
                {"matcher": "Write", "hooks": [
                    {"type": "command", "command": "python in_scratch_hook.py", "timeout": 15},
                    {"type": "command", "command": f"python {external_posix}", "timeout": 15},
                ]}
            ]
        }
    }
    (tmp / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=str(tmp), capture_output=True)
    subprocess.run(["git", "-c", "user.email=h@h", "-c", "user.name=h", "commit", "-q", "-m", "init"],
                    cwd=str(tmp), capture_output=True)
    return tmp, settings, external_dir


def _selftest_undegradable_absolute_path(fixtures_dir: Path) -> bool:
    """(v5, sub-test 6) Runs the two-hook fixture above through the real run_full() path twice
    (once plain, once with --allow-partial-degrade) to prove: (a) the absolute-path row is
    classed UNDEGRADABLE-ABSOLUTE-PATH in the degraded phase and is NOT re-executed; (b) the
    in-scratch row is still truncated and re-run normally; (c) a plain run exits 6 because
    degraded_n < executed_n; (d) the same fixture with --allow-partial-degrade exits 0."""
    tmp, settings, external_dir = _build_selftest_tree_undegradable()
    try:
        class _Args:
            pass

        def make_args(allow_partial):
            a = _Args()
            a.settings = str(tmp / "settings.json")
            a.trunk = "selftest"
            a.project_dir = str(tmp)
            a.exec_cap = 30.0
            a.disable_detector = False
            a.degrade = True
            a.keep_scratch = False
            a.allow_partial_degrade = allow_partial
            a.out = str(tmp / "out.jsonl")
            return a

        args_plain = make_args(False)
        rows, degraded_rows, entries, executed, degraded_n, undegradable_n = run_full(
            args_plain, fixtures_dir, exit_semantics=None
        )
        got = {r.get("degraded_primary"): r["class"] for r in degraded_rows}
        print(f"[selftest 6/6: undegradable-absolute-path] degraded classes: {got} "
              f"executed={executed} degraded_n={degraded_n} undegradable_n={undegradable_n}")

        in_scratch_class = got.get("in_scratch_hook.py")
        external_key = next((k for k in got if k and "external_absolute_target.py" in k), None)
        external_class = got.get(external_key) if external_key else None

        in_scratch_ok = (in_scratch_class == "FAIL-OPEN-SILENT")
        external_ok = (external_class == "UNDEGRADABLE-ABSOLUTE-PATH")
        counts_ok = (executed == 2 and degraded_n == 1 and undegradable_n == 1)
        exit6_ok = (degraded_n < executed and not args_plain.allow_partial_degrade)

        # Now the same fixture with --allow-partial-degrade: same classes, but the caller's own
        # exit-code decision (mirroring main()'s logic) must read as acceptable.
        args_partial = make_args(True)
        rows2, degraded_rows2, entries2, executed2, degraded_n2, undegradable_n2 = run_full(
            args_partial, fixtures_dir, exit_semantics=None
        )
        would_exit6_partial = (args_partial.degrade and degraded_n2 < executed2
                                and not args_partial.allow_partial_degrade)
        allow_partial_ok = (not would_exit6_partial) and (degraded_n2 == 1 and undegradable_n2 == 1)

        ok = in_scratch_ok and external_ok and counts_ok and exit6_ok and allow_partial_ok
        print(f"[selftest 6/6: undegradable-absolute-path] in_scratch={in_scratch_class} "
              f"(want FAIL-OPEN-SILENT) external={external_class} (want UNDEGRADABLE-ABSOLUTE-PATH) "
              f"counts_ok={counts_ok} exit6_ok(plain)={exit6_ok} allow_partial_ok={allow_partial_ok} "
              f"-> {'PASS' if ok else 'FAIL'}")
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(external_dir, ignore_errors=True)


def run_selftest(args, fixtures_dir: Path) -> int:
    """v5: runs six sub-tests — the v2 both-directions positive control (unchanged), the four
    v4 controls (NONZERO-WITH-OUTPUT + exit-semantics, TIMEOUT-DECLARED vs TIMEOUT-HARNESS-CAP,
    the degrade-phase primary-truncation design, and TIMEOUT outranking the side-effects
    OK-promotion), plus the v5 UNDEGRADABLE-ABSOLUTE-PATH / exit-6 / --allow-partial-degrade
    control. ALL SIX must pass for exit 0."""
    r1 = _selftest_both_directions(fixtures_dir, args.disable_detector)
    r2 = _selftest_nonzero_with_output(fixtures_dir)
    r3 = _selftest_timeout_classes(fixtures_dir)
    r4 = _selftest_degrade_phase(fixtures_dir)
    r5 = _selftest_timeout_outranks_sideeffects(fixtures_dir)
    r6 = _selftest_undegradable_absolute_path(fixtures_dir)

    print("")
    print(f"[selftest] 1/6 both-directions:              {'PASS' if r1 else 'FAIL'}")
    print(f"[selftest] 2/6 nonzero-with-output:          {'PASS' if r2 else 'FAIL'}")
    print(f"[selftest] 3/6 timeout classes:              {'PASS' if r3 else 'FAIL'}")
    print(f"[selftest] 4/6 degrade phase:                {'PASS' if r4 else 'FAIL'}")
    print(f"[selftest] 5/6 timeout-outranks-effects:     {'PASS' if r5 else 'FAIL'}")
    print(f"[selftest] 6/6 undegradable-absolute-path:   {'PASS' if r6 else 'FAIL'}")

    if r1 and r2 and r3 and r4 and r5 and r6:
        print("[selftest] PASS — all six sub-tests passed")
        return 0
    print("[selftest] FAIL — see sub-test results above")
    return 1


# ------------------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--settings", default=".claude/settings.json")
    ap.add_argument("--trunk", default="CFL")
    ap.add_argument("--project-dir", default=".")
    ap.add_argument("--fixtures", default=None,
                     help="fixtures directory; if omitted, resolves beside-script hook_fixtures/ "
                          "then repo-relative scripts/tests/hook_fixtures, else exits 3")
    ap.add_argument("--out", default="wiki/test-outputs/HOOK-HARNESS-run.jsonl")
    ap.add_argument("--exec-cap", type=float, default=900.0,
                     help="hard cap in seconds on any single hook execution; actual cap used per "
                          "row is min(declared_timeout_s, --exec-cap). Default 900 so, unless the "
                          "operator lowers it, a hook is never killed inside its own declared "
                          "budget (max documented CFL timeout is 900s).")
    ap.add_argument("--keep-scratch", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                     help="list resolved fixture path (or skip reason) per hook entry; runs nothing, clones nothing")
    ap.add_argument("--skip-selftest", action="store_true",
                     help="skip the automatic pre-run selftest that otherwise gates every real run (default: ON)")
    ap.add_argument("--disable-detector", action="store_true",
                     help="disables the destructive-command detector — used ONLY to demonstrate "
                          "the selftest's failing branch; never use on a real run")
    ap.add_argument("--exit-semantics", default=None,
                     help="path to a JSON {'<script-path>': {'<exit-code-str>': '<meaning>'}} map; "
                          "renames FAIL-CLOSED-VISIBLE/NONZERO-WITH-OUTPUT rows to the trunk's own "
                          "documented exit-code meaning (e.g. FINDINGS-EXIST, UNAVAILABLE-BY-DESIGN)")
    ap.add_argument("--degrade", action="store_true",
                     help="after the baseline run, in the SAME scratch clone, truncate every "
                          "executed row's primary script to 0 bytes and re-run — phase: 'degraded' "
                          "rows; a FAIL-OPEN-SILENT row there is the finding this mode exists for")
    ap.add_argument("--allow-partial-degrade", action="store_true",
                     help="(v5) accept a --degrade run where degraded_n < executed_n (some primaries "
                          "resolve outside the scratch clone by absolute path and were declined, "
                          "classed UNDEGRADABLE-ABSOLUTE-PATH) as exit 0 instead of exit 6; outputs "
                          "are written either way")
    args = ap.parse_args()

    # v2 fix 2: resolve (and possibly exit 3) BEFORE dispatching to any mode, so --selftest,
    # --dry-run, and a real run all get the same loud failure when no fixtures resolve.
    fixtures_dir = resolve_fixtures_dir(args.fixtures)
    exit_semantics = load_exit_semantics(args.exit_semantics)

    if args.selftest:
        sys.exit(run_selftest(args, fixtures_dir))

    if args.dry_run:
        sys.exit(run_dry(args, fixtures_dir))

    # v2 fix 4: a real run is gated on a passing selftest, before the target repo is ever
    # cloned into scratch.
    if not args.skip_selftest:
        print("[hook_harness] running automatic pre-run selftest (pass --skip-selftest to bypass)...",
              file=sys.stderr)
        st_rc = run_selftest(args, fixtures_dir)
        if st_rc != 0:
            print("[hook_harness] ABORT — pre-run selftest failed; target repo was NOT touched. "
                  "See selftest output above.", file=sys.stderr)
            sys.exit(5)
        print("[hook_harness] selftest PASS — proceeding to real run", file=sys.stderr)

    rows, degraded_rows, entries, executed, degraded_n, undegradable_n = run_full(args, fixtures_dir, exit_semantics)

    if executed == 0:
        print("[hook_harness] EXIT 4 — NOTHING EXECUTED (every baseline row skipped; see counts above)",
              file=sys.stderr)
        sys.exit(4)

    # v5, Secretary's finding: a --degrade run where some primaries were UNDEGRADABLE-ABSOLUTE-PATH
    # is a PARTIAL degrade measurement, not a complete one — outputs are already written (above),
    # but the exit code must say so unless the operator explicitly accepts partial coverage.
    if args.degrade and degraded_n < executed and not args.allow_partial_degrade:
        print(f"[hook_harness] EXIT 6 — partial degrade: only {degraded_n}/{executed} executed rows "
              f"were actually truncated-and-re-run ({undegradable_n} UNDEGRADABLE-ABSOLUTE-PATH, "
              "declined because their primary resolves outside the scratch clone). Outputs were "
              "written. Pass --allow-partial-degrade to accept this run as exit 0.", file=sys.stderr)
        sys.exit(6)

    sys.exit(0)


if __name__ == "__main__":
    main()
