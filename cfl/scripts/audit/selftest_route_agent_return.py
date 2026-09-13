#!/usr/bin/env python3
"""selftest_route_agent_return.py — RP-29 acceptance test (lane H-4, 2026-09-02).

Proves two things, against a scratch repo, never the live tree:

  1. THE BUG, reproduced from the code as it stood in commit `ede0b970` — the last commit
     before the RP-29 fix (`fe97758e`) landed. STALE FIXTURE, corrected 2026-09-05 (FIX-5):
     this originally read `HEAD:scripts/audit/route_agent_return.py`, which worked only in the
     narrow window between writing the fix and committing it. Once `fe97758e` was committed
     (confirmed via `git diff --stat HEAD -- scripts/audit/route_agent_return.py` — empty, HEAD
     and the working tree are byte-identical), `HEAD` stopped being "the old buggy code" and
     started being "the same fixed code as the working tree," so the two "OLD reproduces the
     bug" checks below failed not because the fix regressed but because OLD and NEW had become
     the same input. Pinning to the immediate pre-fix commit SHA makes this reproduction stable
     regardless of how many further commits land on `route_agent_return.py` after this one: the
     same SubagentStop identity
     (agent id, transcript, parent session), fired twice with a self-routing edit in between
     (the agent complying with "Route it" but never writing `[TERMINAL]` — the exact gap
     `wiki/intake-triage/DREAM-2026-09-01-...md` section 3 measured, RP-29), mints TWO rows.

  2. THE FIX, run against the CURRENT working-tree copy of the same module: the identical
     sequence mints exactly ONE row, an already-routed key mints ZERO further rows, and a
     genuinely new agent still mints its own ONE row.

Both are printed verbatim so the before/after is legible without re-running anything.

Never touches `exchange/ROUTING-LEDGER.md` (append-only, real) or any file outside a
`tempfile.mkdtemp()` scratch root. Reads history only via `git show <pinned-SHA>:<path>` and
`importlib` of the current on-disk module — no `git commit`, no `git push`.

Usage:
  python scripts/audit/selftest_route_agent_return.py
Exit 0 if every count matches its expectation; exit 1 and a FAIL line otherwise.
"""
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import contextlib

REPO_ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
TARGET = os.path.join(REPO_ROOT, "scripts", "audit", "route_agent_return.py")

# Pinned to the last commit BEFORE the RP-29 fix (`fe97758e`) landed, not `HEAD` — see the
# module docstring's STALE FIXTURE note (FIX-5, 2026-09-05). `HEAD` drifts forward with every
# later commit; this SHA does not, so "OLD reproduces the bug" stays reproducible indefinitely.
PRE_FIX_SHA = "ede0b970eb6b2167a3bc3bb2cd374c774e452298"


def git_show_head(path_rel, rev=PRE_FIX_SHA):
    """Bytes of `path_rel` as committed at `rev` (default: the pinned pre-RP-29-fix SHA), via
    `git show` — never `git checkout`."""
    out = subprocess.run(["git", "show", f"{rev}:{path_rel}"], cwd=REPO_ROOT,
                         capture_output=True, check=True)
    return out.stdout


def load_module_from_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scratch_repo():
    tmp = tempfile.mkdtemp(prefix="rar-selftest-")
    os.makedirs(os.path.join(tmp, "exchange", "su-close"), exist_ok=True)
    return tmp


def fire(mod, root, payload):
    """One hook-mode invocation of `mod.main()` against `root`. Returns emitted stdout."""
    buf = io.StringIO()
    _stdin, sys.stdin = sys.stdin, io.StringIO(json.dumps(payload))
    _argv, sys.argv = sys.argv, ["route_agent_return.py"]
    _env = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = root
    try:
        with contextlib.redirect_stdout(buf):
            mod.main()
    finally:
        sys.stdin, sys.argv = _stdin, _argv
        if _env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = _env
    return buf.getvalue()


def row_count(mod, root, id6):
    p = os.path.join(root, mod.LEDGER)
    if not os.path.exists(p):
        return 0
    with open(p, encoding="utf-8", errors="replace") as fh:
        return sum(1 for l in fh if (mod.row_cells(l) or ["", "", ""])[2] == id6)


def self_route_no_token(mod, root):
    """Simulate the agent complying with 'Route it' but never writing [TERMINAL] — the exact
    RP-29 gap: it edits its own row's disposition, clearing the PENDING gate."""
    p = os.path.join(root, mod.LEDGER)
    with open(p, encoding="utf-8") as fh:
        body = fh.read()
    body = body.replace("| PENDING | - |", "| **ROUTED** *(self-routed, no token)* | rp29aa |", 1)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(body)


def run_sequence(mod, label):
    """Fire 1 (mint), self-route without TERMINAL, fire 2 (the re-fire RP-29 measured),
    fire 3 (a third re-fire, same identity), fire on a genuinely new agent id.
    Returns dict of the four measured counts."""
    root = scratch_repo()
    try:
        payload_a = {"session_id": "rp29aaa1112223334445556667778889990",
                    "transcript_path": os.path.join(root, "main.jsonl"),
                    "hook_event_name": "SubagentStop", "stop_hook_active": False}
        print(f"\n--- {label}: fire 1 (real return) ---")
        out1 = fire(mod, root, payload_a)
        print(out1.strip() or "(silent)")
        n_after_fire1 = row_count(mod, root, "rp29aa")

        self_route_no_token(mod, root)

        print(f"--- {label}: fire 2 (re-fire after self-route, no [TERMINAL]) ---")
        out2 = fire(mod, root, payload_a)
        print(out2.strip() or "(silent)")
        n_after_fire2 = row_count(mod, root, "rp29aa")

        print(f"--- {label}: fire 3 (a further re-fire, same identity) ---")
        out3 = fire(mod, root, payload_a)
        print(out3.strip() or "(silent)")
        n_after_fire3 = row_count(mod, root, "rp29aa")

        payload_b = dict(payload_a, session_id="rp29bbb2223334445556667778889990001")
        print(f"--- {label}: fire on a GENUINELY NEW agent ---")
        out4 = fire(mod, root, payload_b)
        print(out4.strip() or "(silent)")
        n_new_agent = row_count(mod, root, "rp29bb")

        return {"after_fire1": n_after_fire1, "after_fire2": n_after_fire2,
                "after_fire3": n_after_fire3, "new_agent_rows": n_new_agent}
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    tmp = tempfile.mkdtemp(prefix="rar-selftest-src-")
    try:
        # --- 1. THE BUG: the pinned pre-fix commit, before this lane's fix ----------------
        old_src = git_show_head("scripts/audit/route_agent_return.py")
        old_path = os.path.join(tmp, "route_agent_return_PREFIX.py")
        with open(old_path, "wb") as fh:
            fh.write(old_src)
        old_mod = load_module_from_file(old_path, "route_agent_return_PREFIX")
        print("=" * 78)
        print(f"OLD CODE (git show {PRE_FIX_SHA[:8]}) — reproducing the RP-29 loop")
        print("=" * 78)
        old = run_sequence(old_mod, "OLD")

        # --- 2. THE FIX: current working-tree copy ----------------------------------------
        new_mod = load_module_from_file(TARGET, "route_agent_return_WORKTREE")
        print("\n" + "=" * 78)
        print("NEW CODE (working tree) — RP-29 fix")
        print("=" * 78)
        new = run_sequence(new_mod, "NEW")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"OLD: {old}")
    print(f"NEW: {new}")

    checks = [
        ("OLD reproduces the bug: fire 2 (re-fire after self-route) minted a SECOND row",
         old["after_fire2"] == 2),
        ("OLD reproduces the bug: fire 3 kept growing (>= 2 rows)",
         old["after_fire3"] >= 2),
        ("NEW fixture delivered twice -> exactly ONE row after fire 2",
         new["after_fire2"] == 1),
        ("NEW: an already-routed key -> ZERO new rows on fire 3",
         new["after_fire3"] == new["after_fire2"] == 1),
        ("NEW: a genuinely new agent still mints exactly ONE row",
         new["new_agent_rows"] == 1),
    ]

    print()
    bad = 0
    for name, ok in checks:
        bad += 0 if ok else 1
        print(f"  {name:<75} : {'PASS' if ok else 'FAIL'}")
    print(f"\nRESULT: {'PASS' if not bad else 'FAIL'} — {len(checks) - bad}/{len(checks)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
