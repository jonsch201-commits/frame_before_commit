#!/usr/bin/env python
"""ask_elder_fork.py -- dispatch an ELDER CONSULT and capture its answer.

WHY THIS EXISTS, and it is one measured failure, not a preference:
  2026-09-07 08:0x, CFL 46276084 forked elder a86404c0 with a 4,937 B multi-line prompt built by
  hand in the scratchpad, via `subprocess.call([...], shell=True)` on Windows. The elder's FIRST
  LINE back was: "No question arrived in the prompt -- only the framing." cmd.exe truncates an
  argument at the first newline, so only paragraph one survived. rc=0. Nothing errored.
  THE SAME CLASS IS ALREADY IN THIS TRUNK'S MEMORY -- "Nightly Lane Leg 2 Truncated Prompt:
  `-p` prompt arrived first-line-only" (2026-07-19). It was written down and re-derived the
  expensive way, inside a consult run to honour Jon's correction about consults.

WHAT IT GUARANTEES
  * shell=False ALWAYS -- the prompt is an argv element, never a command line cmd.exe reparses.
  * A RETURN CHANNEL THE CONSULTER HOLDS. A `--permission-mode plan` elder CANNOT WRITE, so the
    "name the file the answer goes in" rule (SKILL.md section 2) is un-runnable for a fork consult
    and its subagent form is un-runnable outside the agent's fence. For a fork, the channel is the
    consulter's stdout redirect. This script owns it.
  * A DELIVERY RECEIPT: it echoes the prompt's byte count and the answer's, and FAILS LOUDLY if the
    answer is under --min-bytes (default 200) -- an empty answer is UNKNOWN, never a verdict.
  * The full UUID is mandatory (an 8-char prefix does not resolve) and is checked before spending.
"""
import argparse, io, os, shutil, subprocess, sys, uuid as _uuid

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True, help="FULL session UUID of the elder")
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True, help="where the answer is captured (the return channel)")
    ap.add_argument("--cwd", default=None, help="run from here; use a HOOKLESS dir so the elder's "
                                                "stop hooks do not fire inside the consult")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--min-bytes", type=int, default=200)
    a = ap.parse_args()
    try:
        _uuid.UUID(a.session)
    except ValueError:
        sys.exit("FAIL not a full UUID: %r -- an 8-char prefix does not resolve" % a.session)
    prompt = io.open(a.prompt_file, encoding="utf-8").read()
    if not prompt.strip():
        sys.exit("FAIL prompt file is empty: %s" % a.prompt_file)
    exe = shutil.which("claude") or shutil.which("claude.cmd")
    if not exe:
        sys.exit("FAIL `claude` not on PATH")
    cmd = [exe, "--resume", a.session, "--fork-session", "--permission-mode", "plan", "-p", prompt]
    print("ELDER   : %s\nPROMPT  : %d B, %d lines (argv, shell=False -- no cmd.exe reparse)"
          % (a.session, len(prompt.encode("utf-8")), prompt.count("\n") + 1))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    with io.open(a.out, "w", encoding="utf-8") as out:
        rc = subprocess.call(cmd, cwd=a.cwd, stdout=out, stderr=subprocess.STDOUT,
                             shell=False, timeout=a.timeout)
    n = os.path.getsize(a.out)
    print("ANSWER  : rc=%s, %d B -> %s" % (rc, n, a.out))
    if n < a.min_bytes:
        print("UNKNOWN : answer under --min-bytes (%d). An empty consult is UNKNOWN, never a FAIL "
              "and never a pass -- read the file before concluding the elder had nothing." % a.min_bytes)
        return 3
    return 0 if rc == 0 else rc

if __name__ == "__main__":
    sys.exit(main())
