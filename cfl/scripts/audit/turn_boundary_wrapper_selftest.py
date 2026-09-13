#!/usr/bin/env python
"""turn_boundary_wrapper_selftest.py -- selftest for .claude/hooks/turn-boundary-retrieval.sh
(TB-1-stage, dispatch exchange/dispatches/2026-09-05/020950-TB-1-stage.md).

⛔ STAGED, NOT WIRED. This tests a hook wrapper that is NOT referenced by
.claude/settings.json (see exchange/TB-1-PROPOSED-WIRING.md). Running this file changes
no settings and touches no live session state -- it invokes the real wrapper.sh as a
subprocess with TURN_BOUNDARY_MODE_FILE / TURN_BOUNDARY_LOG_FILE pointed at a scratch
temp directory, so it never reads or writes the real .claude/hooks/state/MODE or
.claude/hooks/state/turn-boundary-retrieval.log a live session depends on.

WHY EVERY CASE HERE IS A subprocess.run() CALL, NOT A FUNCTION CALL
--------------------------------------------------------------------
The brief that produced this file, verbatim: "A peer proved one of this repo's gates
green last night on a program that died on every invocation; cases that only call
functions do not test the program." The wrapper is a bash script -- it has no functions
to import -- so every case here runs `bash turn-boundary-retrieval.sh` as a real child
process with a real stdin payload and a real environment, and asserts the REAL exit
code the OS reports (never a piped/`$?`-of-something-else exit code -- see
`unpiped_exit()` below, same convention the brief requires of the closing report).
One case additionally invokes turn_boundary_executor.py's OWN --selftest as a bare
`[sys.executable, script, "--selftest"]` subprocess -- the executor's internal
selftest() calls its functions directly, so running it as an actual entry-point
subprocess is the only way this file also proves that program is not the kind that
"dies on every invocation" while its function tests stay green (the exact failure
class the brief names).

Cases (minimum set from the brief):
  1. MODE=AFK, well-formed payload with a real (synthetic) session -> wrapper RUNS the
     executor: the log file exists afterward and contains the executor's own banner.
  2. MODE=LIVE -> do nothing: log file must NOT be created.
  3. MODE file absent -> do nothing: log file must NOT be created.
  4. MODE=AFK, malformed JSON on stdin -> writes NOTHING (not even an empty placeholder
     log file) -- a missing file is checked, not an empty one, because an empty file
     WOULD be a placeholder.
  4b. MODE=AFK, well-formed JSON with no usable session_id -> same "writes nothing".
  5. Entry-point: the wrapper itself, for every case above, always exits 0 (the
     brief's non-negotiable: "always exit 0"). Checked via subprocess returncode, not
     a re-derived value.
  6. Entry-point: turn_boundary_executor.py --selftest, run as a subprocess, exits 0.

Every check appends to `RESULTS` and the process exits 1 if any failed -- this file is
itself meant to be run as `python turn_boundary_wrapper_selftest.py` and its real exit
code read unpiped, per the same convention it tests.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WRAPPER = os.path.join(REPO, ".claude", "hooks", "turn-boundary-retrieval.sh")
EXECUTOR = os.path.join(HERE, "turn_boundary_executor.py")

# ⛔ MEASURED 2026-09-05: plain "bash" resolves via subprocess.run's inherited PATH to
# the Windows WSL relay stub (C:\Windows\System32\bash.exe) here, NOT Git Bash -- it
# fails with "execvpe(/bin/bash) failed: No such file or directory" and every wrapper
# invocation below reported rc=1 for every case, including the ones the wrapper itself
# always exits 0 for. `bash -n` and manual runs of the same command from an interactive
# Bash tool worked, because THAT shell's own PATH lists Git Bash first -- a fresh
# subprocess.run() does not inherit that ordering reliably. So the real bash.exe this
# repo's hooks actually run under is resolved explicitly here, once, and used for every
# subprocess call -- this is exactly the class of bug the brief calls out ("a program
# that died on every invocation; cases that only call functions do not test the
# program"), caught here because this file runs the real entry point instead of a stub.
_BASH_CANDIDATES = [
    r"C:\Program Files\Git\bin\bash.exe",
    r"C:\Program Files\Git\usr\bin\bash.exe",
    "/usr/bin/bash",
    "bash",  # last resort: whatever PATH gives at run time
]
BASH = next((p for p in _BASH_CANDIDATES if os.path.isfile(p)), "bash")

RESULTS = []


def check(name, passed, detail=""):
    RESULTS.append((name, passed, detail))
    print("  %s %s%s" % ("PASS" if passed else "FAIL", name,
                          ("  -- %s" % detail) if (detail and not passed) else ""))


def run_wrapper(mode_file_path, stdin_bytes, tmpdir, tag):
    """Invoke the real wrapper.sh as a subprocess. Returns (returncode, log_path)."""
    log_path = os.path.join(tmpdir, "log-%s.txt" % tag)
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = REPO
    env["TURN_BOUNDARY_MODE_FILE"] = mode_file_path
    env["TURN_BOUNDARY_LOG_FILE"] = log_path
    proc = subprocess.run(
        [BASH, WRAPPER],
        input=stdin_bytes,
        cwd=REPO,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
    )
    return proc.returncode, log_path


def make_synthetic_session(tmpdir):
    """A minimal real JSONL, so resolve_session()'s `os.path.isfile(arg)` shortcut
    picks it up directly -- no dependency on ~/.claude/projects contents, and no
    dependency on the live GraphRAG index being healthy in this environment (measured
    2026-09-05: hybrid mode raises sqlite3.OperationalError here -- an executor-side
    finding reported separately in the closing message, not fixed by this file)."""
    path = os.path.join(tmpdir, "synthetic-session.jsonl")
    recs = [
        {"type": "user", "origin": {"kind": "human"}, "timestamp": "2026-09-01T01:00:00Z",
         "message": {"content": "selftest turn boundary probe text"}},
    ]
    with open(path, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return path


def main():
    with tempfile.TemporaryDirectory(prefix="tb1-selftest-") as tmp:
        mode_afk = os.path.join(tmp, "MODE-afk")
        with open(mode_afk, "w", encoding="utf-8") as fh:
            fh.write("AFK\n")
        mode_live = os.path.join(tmp, "MODE-live")
        with open(mode_live, "w", encoding="utf-8") as fh:
            fh.write("LIVE\n")
        mode_absent = os.path.join(tmp, "MODE-does-not-exist")  # never created

        session_path = make_synthetic_session(tmp)
        good_payload = json.dumps({"session_id": session_path}).encode("utf-8")

        # --- 1. MODE=AFK + good payload -> runs, log exists and carries the banner ---
        rc, log = run_wrapper(mode_afk, good_payload, tmp, "afk-runs")
        check("1. entry-point: wrapper subprocess exits 0 (MODE=AFK, good payload)",
              rc == 0, "rc=%s" % rc)
        ran = os.path.isfile(log)
        check("1. MODE=AFK runs: log file created", ran)
        if ran:
            with open(log, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            check("1. MODE=AFK runs: log carries the executor's own banner",
                  "TURN-BOUNDARY EXECUTOR" in text or "turn-boundary-retrieval" in text,
                  text[:200])

        # --- 2. MODE=LIVE -> does nothing ---
        rc, log = run_wrapper(mode_live, good_payload, tmp, "live-noop")
        check("2. entry-point: wrapper subprocess exits 0 (MODE=LIVE)", rc == 0, "rc=%s" % rc)
        check("2. MODE=LIVE does nothing: no log file written", not os.path.exists(log))

        # --- 3. MODE file absent -> does nothing (UNKNOWN treated as LIVE) ---
        rc, log = run_wrapper(mode_absent, good_payload, tmp, "absent-noop")
        check("3. entry-point: wrapper subprocess exits 0 (MODE file absent)", rc == 0, "rc=%s" % rc)
        check("3. MODE absent does nothing: no log file written", not os.path.exists(log))

        # --- 4. MODE=AFK + malformed JSON -> writes nothing (not a placeholder) ---
        rc, log = run_wrapper(mode_afk, b"not-json{{{garbage", tmp, "malformed-noop")
        check("4. entry-point: wrapper subprocess exits 0 (malformed payload)", rc == 0, "rc=%s" % rc)
        check("4. malformed payload writes nothing: no log file at all (not empty -- absent)",
              not os.path.exists(log))

        # --- 4b. MODE=AFK + valid JSON, no usable session_id -> writes nothing ---
        rc, log = run_wrapper(mode_afk, json.dumps({"cwd": "/x"}).encode("utf-8"),
                               tmp, "nosid-noop")
        check("4b. entry-point: wrapper subprocess exits 0 (no session_id)", rc == 0, "rc=%s" % rc)
        check("4b. missing session_id writes nothing: no log file at all",
              not os.path.exists(log))

        # --- 4c. MODE=AFK + empty stdin (legitimate per hook_fanout.sh convention) ---
        rc, log = run_wrapper(mode_afk, b"", tmp, "empty-stdin-noop")
        check("4c. entry-point: wrapper subprocess exits 0 (empty stdin)", rc == 0, "rc=%s" % rc)
        check("4c. empty stdin writes nothing: no log file at all", not os.path.exists(log))

    # --- 6. entry-point: turn_boundary_executor.py's OWN --selftest as a real subprocess ---
    proc = subprocess.run([sys.executable, EXECUTOR, "--selftest"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    out = proc.stdout.decode("utf-8", "replace")
    check("6. entry-point: turn_boundary_executor.py --selftest exits 0 as a real subprocess",
          proc.returncode == 0, "rc=%s tail=%s" % (proc.returncode, out[-300:]))
    check("6. turn_boundary_executor.py --selftest reports its own SELFTEST PASS",
          "SELFTEST PASS" in out, out[-300:])

    ok = all(passed for _, passed, _ in RESULTS)
    print("SELFTEST %s (%d/%d)" % ("PASS" if ok else "FAIL",
                                    sum(1 for _, p, _ in RESULTS if p), len(RESULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
