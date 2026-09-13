#!/usr/bin/env python3
"""Selftest for postcompact_verify.py -- proves all three verdicts are REACHABLE.

A verifier whose FINDINGS branch has never fired is an acceptance test that cannot
fail (fleet law, measured three times on 2026-08-17 alone). Three fixtures:
  1. empty summary        -> VERDICT: UNKNOWN        (Professional's test)
  2. complete summary     -> VERDICT: CHECKED-FOUND-NONE
  3. gutted summary       -> VERDICT: FINDINGS       (>=1, names the dropped class)
Exit 0 all-pass; exit 1 with the failing fixture named otherwise.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "postcompact_verify.py"
ROOT = HERE.parents[1]


def run(payload):
    r = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(payload),
                       capture_output=True, text=True, timeout=300)
    return r.stderr.strip()


def derive_complete_summary():
    """Build a summary that names every ground-truth item, from disk (never hardcoded)."""
    parts = []
    tracker = ROOT / "wiki" / "tracker"
    for f in tracker.glob("wayfinder-*.md"):
        head = f.read_text(encoding="utf-8", errors="ignore")[:2000]
        if "wayfinder:map" in head and re.search(r'status:\s*"?LIVE"?', head):
            parts.append(f.name)
    br = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--abbrev-ref", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
    parts.append(br)
    wake = (ROOT / "exchange" / "WAKE.md").read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"SPINE\s+IS\s+`([^`]+)`", wake, re.IGNORECASE)
    if m:
        parts.append(Path(m.group(1)).name)
    return "Synthetic complete summary naming: " + " ".join(parts)


def main():
    fails = []

    out = run({"compact_summary": "", "trigger": "selftest"})
    if "UNKNOWN" not in out:
        fails.append(f"fixture-1 empty: expected UNKNOWN, got: {out}")

    out = run({"compact_summary": derive_complete_summary(), "trigger": "selftest"})
    if "CHECKED-FOUND-NONE" not in out:
        fails.append(f"fixture-2 complete: expected CHECKED-FOUND-NONE, got: {out}")

    out = run({"compact_summary": "A summary that names no map, no branch, no spine.",
               "trigger": "selftest"})
    if "FINDINGS" not in out:
        fails.append(f"fixture-3 gutted: expected FINDINGS, got: {out}")

    if fails:
        for f in fails:
            print("SELFTEST FAIL:", f)
        return 1
    print("SELFTEST ALL PASS: UNKNOWN, CHECKED-FOUND-NONE and FINDINGS all reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
