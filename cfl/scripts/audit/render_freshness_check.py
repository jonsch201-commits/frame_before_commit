#!/usr/bin/env python3
"""render_freshness_check.py — Jon's clause (3), committed acceptance test
(JON-ORDER 2026-09-01, verbatim): "newest md in raw/ must be younger than the
newest compact stamp, else FAIL. A capture that prints `copied 0 / failed 0`
is UNKNOWN, not PASS."

Compares ARTIFACTS, not counters: newest .md mtime under
raw/transcripts/claude-code/ (recursive, sidecars excluded) vs the newest
PreCompact receipt's stamp (from its filename, local time). FAIL if the render
layer is older than the newest compact. UNKNOWN (exit 2) if either side cannot
be measured — an absent input is never a pass.

Called by: PostCompact + SessionStart hooks, and the record-pipeline pulse road.
Exit 0 PASS · 1 FAIL · 2 UNKNOWN.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
RENDER = ROOT / "raw" / "transcripts" / "claude-code"
RECEIPTS = ROOT / "exchange" / "su-close" / "precompact"


def main():
    receipts = sorted(RECEIPTS.glob("*.md"))
    if not receipts:
        print("UNKNOWN: no PreCompact receipts found — cannot establish a compact stamp")
        return 2
    newest_receipt = receipts[-1]
    m = re.match(r"(\d{8})T(\d{6})-", newest_receipt.name)
    if not m:
        print(f"UNKNOWN: newest receipt name unparseable: {newest_receipt.name}")
        return 2
    stamp = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")

    newest_md, newest_mtime = None, 0.0
    if not RENDER.is_dir():
        print(f"UNKNOWN: render layer missing: {RENDER}")
        return 2
    for p in RENDER.rglob("*.md"):
        if p.name.endswith(".sidecar.md") or "_unverified" in str(p):
            continue
        try:
            mt = p.stat().st_mtime
        except OSError:
            continue
        if mt > newest_mtime:
            newest_mtime, newest_md = mt, p
    if newest_md is None:
        print("UNKNOWN: zero rendered md files found — an empty render layer is not a fresh one")
        return 2
    md_dt = datetime.fromtimestamp(newest_mtime)
    verdict = "PASS" if md_dt >= stamp else "FAIL"
    print(f"render-freshness {verdict}: newest md {md_dt:%Y-%m-%d %H:%M:%S} "
          f"({newest_md.relative_to(ROOT)}) vs newest compact stamp {stamp:%Y-%m-%d %H:%M:%S} "
          f"({newest_receipt.name})")
    if verdict == "FAIL":
        print("  the render layer is OLDER than the newest compact — the md layer graph RAG "
              "embeds is stale; run scripts/audit/auto_mint_windows.py")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
