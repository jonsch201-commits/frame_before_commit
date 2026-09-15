#!/usr/bin/env python3
"""
scripts/project_dirs.py — ~/.claude/projects Key and Directory Resolver (Live-Plus-Legacy)

Derives ~/.claude/projects keys dynamically from repository roots, maintaining
all historical/legacy project keys so readers never miss past or moved sessions.

Rules (R4 / Jon's Constitution):
- Never live-instead-of-legacy; always live-plus-legacy.
- Primary (live) directories are yielded first; legacy directories follow.
- Path derivation replaces any non-alphanumeric character with '-'.

Usage:
  python scripts/project_dirs.py                     # Project dirs for this repo (Antigravity)
  python scripts/project_dirs.py --trunk cfl         # Project dirs for CFL (live + legacy)
  python scripts/project_dirs.py --trunk all         # All project dirs across all fleet trunks
  python scripts/project_dirs.py --primary           # Primary live dir for this repo
  python scripts/project_dirs.py --trunk cfl --primary
  python scripts/project_dirs.py --find <session_id> # Locate a session JSONL across trunks
  python scripts/project_dirs.py --selftest          # Run internal test assertions
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

def _detect_root() -> str:
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".git").exists() or (p / "CLAUDE.md").exists() or (p / "THE-BOOK.md").exists():
            return str(p)
        p = p.parent
    return str(Path(__file__).resolve().parent.parent)

ROOT = _detect_root()
PROJECTS = Path(os.path.expanduser("~")) / ".claude" / "projects"

# Canonical trunk root locations and their historical legacy project keys
FLEET_TRUNKS: Dict[str, Dict[str, Any]] = {
    "antigravity": {
        "live_root": Path(r"N:\antigravity-hub"),
        "legacy_keys": [
            "G--My-Drive-Claude-Antigravity",
        ],
    },
    "cfl": {
        "live_root": Path(r"N:\claude-cfl\clone"),
        "legacy_keys": [
            "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer",
            "G--My-Drive-Claude-Claude-Foundational-Layer",
            "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer--claude-worktrees-fable-substrate",
            "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer--claude-worktrees-wiki-su-2026-07-07",
            "N--claude-cfl",
        ],
    },
    "professional": {
        "live_root": Path(r"N:\claude-professional"),
        "legacy_keys": [
            "G--My-Drive-Claude-Claude-Professional-claude-professional",
            "G--My-Drive-Claude-Claude-Professional",
        ],
    },
    "secretary": {
        "live_root": Path(r"N:\claude-secretary"),
        "legacy_keys": [
            "G--My-Drive-Claude-Claude-Secretary",
        ],
    },
    "personal": {
        "live_root": Path(r"N:\claude-personal"),
        "legacy_keys": [
            "N--claude-corpus-personal",
            "G--My-Drive-Claude-Claude-Personal",
        ],
    },
}

LEGACY_KEYS = FLEET_TRUNKS["cfl"]["legacy_keys"]


def derive_key(root: Path | str) -> str:
    """Derive ~/.claude/projects key from absolute Windows path."""
    p = os.path.abspath(str(root)).replace("/", "\\")
    return re.sub(r"[^A-Za-z0-9]", "-", p)


def candidate_keys_for_root(root: Path | str, legacy_keys: Optional[List[str]] = None) -> List[str]:
    """Derive primary key from root, followed by any legacy keys (no duplicates)."""
    k = derive_key(root)
    keys = [k]
    if legacy_keys:
        for lk in legacy_keys:
            if lk not in keys:
                keys.append(lk)
    return keys


def candidate_keys(root: Optional[Path | str] = None) -> List[str]:
    """Return all candidate keys for a root path (live first, legacy preserved)."""
    if root is None:
        root = ROOT
    root_resolved = Path(root).resolve()
    for t_info in FLEET_TRUNKS.values():
        if t_info["live_root"].resolve() == root_resolved:
            return candidate_keys_for_root(root, t_info.get("legacy_keys", []))
    return candidate_keys_for_root(root)


def existing_dirs(root: Optional[Path | str] = None) -> List[str]:
    """Return list of existing project directory path strings for root (live first)."""
    if root is None:
        root = ROOT
    keys = candidate_keys(root)
    existing = []
    for k in keys:
        p = PROJECTS / k
        if p.is_dir():
            s = str(p)
            if s not in existing:
                existing.append(s)
    return existing


def dirs_with_memory(root: Optional[Path | str] = None) -> List[str]:
    """Return existing project directories that contain a memory/ subdirectory."""
    return [d for d in existing_dirs(root) if (Path(d) / "memory").is_dir()]


def candidate_keys_for_trunk(trunk: str) -> List[str]:
    """Return all candidate keys for a named trunk (primary live first, then legacy)."""
    t_norm = trunk.lower().strip()
    if t_norm in FLEET_TRUNKS:
        info = FLEET_TRUNKS[t_norm]
        return candidate_keys_for_root(info["live_root"], info["legacy_keys"])
    return candidate_keys_for_root(Path(trunk))


def get_project_dirs(trunk: str = "antigravity") -> List[Path]:
    """Return existing project directories on disk for trunk (live first, then legacy)."""
    t_norm = trunk.lower().strip()
    if t_norm == "all":
        seen = set()
        dirs = []
        for t in FLEET_TRUNKS:
            for d in get_project_dirs(t):
                if d not in seen:
                    seen.add(d)
                    dirs.append(d)
        return dirs

    keys = candidate_keys_for_trunk(t_norm)
    existing = []
    for k in keys:
        p = PROJECTS / k
        if p.is_dir() and p not in existing:
            existing.append(p)
    return existing


def get_primary_project_dir(trunk: str = "antigravity") -> Optional[Path]:
    """Return the primary (live derived) project directory, or first existing."""
    dirs = get_project_dirs(trunk)
    return dirs[0] if dirs else None


def find_session_jsonl(session_id: str, trunk: Optional[str] = None) -> Optional[Path]:
    """Search for {session_id}.jsonl across trunk project dirs (or all fleet dirs)."""
    sid = session_id.replace(".jsonl", "").strip()
    trunks_to_check = [trunk] if trunk and trunk.lower() != "all" else list(FLEET_TRUNKS.keys())
    for t in trunks_to_check:
        for pdir in get_project_dirs(t):
            target = pdir / f"{sid}.jsonl"
            if target.is_file():
                return target
    fallback = list(PROJECTS.glob(f"*/{sid}.jsonl"))
    if fallback:
        return fallback[0]
    return None


def selftest() -> int:
    fails = 0

    got = derive_key(r"N:\antigravity-hub")
    want = "N--antigravity-hub"
    if got != want:
        print(f"FAIL: derive N:\\antigravity-hub -> got {got}, want {want}")
        fails += 1
    else:
        print(f"PASS: derive N:\\antigravity-hub -> {got}")

    got = derive_key(r"N:\claude-cfl\clone")
    want = "N--claude-cfl-clone"
    if got != want:
        print(f"FAIL: derive N:\\claude-cfl\\clone -> got {got}, want {want}")
        fails += 1
    else:
        print(f"PASS: derive N:\\claude-cfl\\clone -> {got}")

    got = derive_key(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer")
    want = "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer"
    if got != want:
        print(f"FAIL: derive CFL G: root -> got {got}, want {want}")
        fails += 1
    else:
        print(f"PASS: derive CFL G: root -> {got}")

    cfl_keys = candidate_keys_for_trunk("cfl")
    if cfl_keys[0] != "N--claude-cfl-clone":
        print(f"FAIL: CFL candidate keys primary not live: {cfl_keys}")
        fails += 1
    elif "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer" not in cfl_keys:
        print(f"FAIL: CFL legacy key missing: {cfl_keys}")
        fails += 1
    else:
        print(f"PASS: CFL candidates (live-first + legacy-preserved) -> {cfl_keys}")

    cfl_dirs = get_project_dirs("cfl")
    if len(cfl_dirs) < 2:
        print(f"FAIL: Expected >= 2 CFL dirs on disk (live + legacy), got: {cfl_dirs}")
        fails += 1
    else:
        print(f"PASS: CFL existing dirs ({len(cfl_dirs)} found, primary={cfl_dirs[0].name}) -> {[d.name for d in cfl_dirs]}")

    live_sid = "8634adc3-9999-4303-8ca9-714cce57a921"
    found = find_session_jsonl(live_sid, "cfl")
    if not found or not found.exists():
        print(f"FAIL: Could not locate live CFL session {live_sid}")
        fails += 1
    else:
        print(f"PASS: Located live CFL session: {found}")

    legacy_sid = "9041f3b0-5102-4a06-a459-b076681a76bd"
    found_leg = find_session_jsonl(legacy_sid, "cfl")
    if not found_leg or not found_leg.exists():
        print(f"FAIL: Could not locate legacy CFL session {legacy_sid}")
        fails += 1
    else:
        print(f"PASS: Located legacy CFL session: {found_leg}")

    print(f"SELFTEST: {'PASS' if fails == 0 else 'FAIL'} ({fails} failure(s))")
    return 1 if fails else 0


def main(argv: List[str]) -> int:
    if "--selftest" in argv:
        return selftest()

    trunk = "antigravity"
    if "--trunk" in argv:
        idx = argv.index("--trunk")
        if idx + 1 < len(argv):
            trunk = argv[idx + 1]

    if "--find" in argv:
        idx = argv.index("--find")
        if idx + 1 < len(argv):
            sid = argv[idx + 1]
            p = find_session_jsonl(sid, trunk if trunk != "antigravity" else None)
            if p:
                print(str(p).replace("\\", "/"))
                return 0
            else:
                print(f"NOT FOUND: {sid}", file=sys.stderr)
                return 1

    if "--primary" in argv:
        p = get_primary_project_dir(trunk)
        if p:
            print(str(p).replace("\\", "/"))
            return 0
        else:
            print(f"NO_PRIMARY_DIR: {trunk}", file=sys.stderr)
            return 1

    dirs = get_project_dirs(trunk)
    for d in dirs:
        print(str(d).replace("\\", "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
