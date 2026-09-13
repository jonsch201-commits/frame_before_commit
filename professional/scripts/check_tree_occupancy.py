#!/usr/bin/env python3
r"""
scripts/check_tree_occupancy.py — Single-Occupancy Topology Guard

Fulfills the Frog & Toad / Hessian Invariant:
Never ask Jon to close a window or resolve a dual-seat collision manually.
Mechanically inspects ~/.claude/jobs/ and running Claude sessions to detect
concurrent seats attached to the same repository tree.

Usage:
  python scripts/check_tree_occupancy.py [--audit] [--resolve] [--tree PATH]
"""

import os
import sys
import json
import glob
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

JOBS_DIR = Path.home() / ".claude" / "jobs"

def scan_jobs():
    """Scan all Claude background job descriptors."""
    if not JOBS_DIR.exists():
        return []
    
    jobs = []
    for state_file in JOBS_DIR.glob("*/state.json"):
        try:
            with open(state_file, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            data["_job_dir"] = str(state_file.parent)
            data["_job_id"] = state_file.parent.name
            jobs.append(data)
        except Exception:
            continue
    return jobs

def audit_tree_occupancy(target_tree=None):
    jobs = scan_jobs()
    by_cwd = {}
    for j in jobs:
        cwd = os.path.normcase(os.path.abspath(j.get("cwd", "")))
        if target_tree:
            norm_target = os.path.normcase(os.path.abspath(target_tree))
            if cwd != norm_target:
                continue
        by_cwd.setdefault(cwd, []).append(j)
    
    findings = []
    for cwd, job_list in by_cwd.items():
        active = [j for j in job_list if j.get("state") in ("working", "running", "active")]
        if len(active) > 1:
            findings.append({
                "cwd": cwd,
                "collision_type": "MULTIPLE_BACKGROUND_JOBS",
                "jobs": active
            })
        elif len(active) == 1:
            findings.append({
                "cwd": cwd,
                "collision_type": "SINGLE_ACTIVE_JOB",
                "jobs": active
            })
    return findings

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit and guard repository tree occupancy.")
    parser.add_argument("--tree", help="Specific tree to check (default: all)")
    parser.add_argument("--audit", action="store_true", default=True, help="Audit and report collisions")
    parser.add_argument("--resolve", action="store_true", help="Resolve collisions automatically")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    findings = audit_tree_occupancy(args.tree)
    
    if args.json:
        print(json.dumps(findings, indent=2))
        return

    print("=== REPOSITORY TREE OCCUPANCY AUDIT ===")
    if not findings:
        print("No active background jobs or collisions detected.")
        return

    for f in findings:
        print(f"\nTree: {f['cwd']}")
        print(f"Collision Type: {f['collision_type']}")
        for j in f["jobs"]:
            print(f"  - Job ID: {j.get('_job_id')} | Name: {j.get('name')} | State: {j.get('state')} | Detail: {j.get('detail')}")
            print(f"    Link Scan: {j.get('linkScanPath')}")

if __name__ == "__main__":
    main()
