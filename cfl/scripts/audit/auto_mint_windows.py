#!/usr/bin/env python3
"""auto_mint_windows.py — RP-9's hook payload: mint every unconsumed PreCompact
receipt's window via mint_window.py (the ONLY emitter, never a fresh parser),
verify content bars, consume. Transcribes the manual ritual proven 08-31→09-01.

Jon's order (2026-09-01, via Secretary, verbatim block in
exchange/inbound/JON-ORDER-wire-SessionStart-to-render-md-…-2026-09-01.md):
"Your PreCompact hook mirrors JSONL. It does NOT render md. … Fix is a hook,
not a habit." This is the hook body for CFL's window road.

Window derivation (exactly the hand ritual):
  lo = last JSONL entry timestamp <= PREVIOUS receipt's wall time (UTC)
  hi = last JSONL entry timestamp <= THIS receipt's wall time (UTC)
  first receipt of a session: lo = epoch (whole head of the session)
Receipt wall time comes from the receipt file's own header line
("# PreCompact receipt — 2026-09-01T13:22:42-0500"), converted to UTC.

Bars before consumption (E3's bars): assistant_text_blocks>0 AND tool_calls>0.
A window failing bars is REPORTED and NOT consumed — the pulse's E3 would go
RED on a hollow consume, and this script must never manufacture a green.

Exit 0: nothing to do, or all minted+consumed clean. Exit 1: a mint or bar
failure (reported, nothing consumed for that receipt).
"""
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
RECEIPTS = ROOT / "exchange" / "su-close" / "precompact"
CONSUMED = ROOT / "exchange" / "su-close" / "CONSUMED.md"
OUTDIR = ROOT / "raw" / "transcripts" / "claude-code" / "fl"
PROJECTS = Path.home() / ".claude" / "projects"
HDR = re.compile(r"# PreCompact receipt — (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)([+-]\d{4})")


def receipt_utc(path):
    m = HDR.search(path.read_text(encoding="utf-8", errors="replace")[:200])
    if not m:
        return None
    dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
    off = m.group(2)
    delta = timedelta(hours=int(off[1:3]), minutes=int(off[3:5]))
    return dt - delta if off[0] == "+" else dt + delta


def session_of(name):
    m = re.match(r"\d{8}T\d{6}-([0-9a-f]{8})\.md", name)
    return m.group(1) if m else None


def find_jsonl(sess8):
    for d in PROJECTS.iterdir():
        if not d.is_dir():
            continue
        for j in d.glob(f"{sess8}*.jsonl"):
            return j
    return None


def last_ts_at_or_before(jsonl, cutoff_iso):
    import json
    last = None
    with open(jsonl, encoding="utf-8", errors="ignore") as f:
        for line in f:
            i = line.find('"timestamp":"')
            if i == -1:
                continue
            ts = line[i + 13:i + 13 + 24].split('"')[0]
            if ts[:19] + "Z" <= cutoff_iso[:19] + "Z" or ts <= cutoff_iso:
                if ts[:19] <= cutoff_iso[:19]:
                    last = ts if (last is None or ts > last) else last
    return last


def main():
    consumed = set(CONSUMED.read_text(encoding="utf-8").split()) if CONSUMED.exists() else set()
    receipts = sorted(RECEIPTS.glob("*.md"))
    todo = [r for r in receipts if r.name not in consumed]
    if not todo:
        print("auto-mint: nothing unconsumed; 0 to do")
        return 0
    rc = 0
    by_session = {}
    for r in receipts:
        s = session_of(r.name)
        if s:
            by_session.setdefault(s, []).append(r)
    for r in todo:
        sess8 = session_of(r.name)
        if not sess8:
            print(f"auto-mint UNKNOWN (unparseable receipt name, not consumed): {r.name}")
            rc = 1
            continue
        jsonl = find_jsonl(sess8)
        if not jsonl:
            print(f"auto-mint UNKNOWN (no JSONL on disk for {sess8}, not consumed): {r.name}")
            rc = 1
            continue
        this_utc = receipt_utc(r)
        if not this_utc:
            print(f"auto-mint UNKNOWN (no header time, not consumed): {r.name}")
            rc = 1
            continue
        sibs = by_session[sess8]
        prev = None
        for s_ in sibs:
            if s_.name < r.name:
                prev = s_
        if prev:
            prev_utc = receipt_utc(prev)
            lo = last_ts_at_or_before(jsonl, prev_utc.strftime("%Y-%m-%dT%H:%M:%S")) or "1970-01-01T00:00:00Z"
        else:
            lo = "1970-01-01T00:00:00Z"
        hi = last_ts_at_or_before(jsonl, this_utc.strftime("%Y-%m-%dT%H:%M:%S"))
        if not hi:
            print(f"auto-mint UNKNOWN (no JSONL entries before receipt time, not consumed): {r.name}")
            rc = 1
            continue
        lo_s, hi_s = lo[:19] + "Z", hi[:19] + "Z"
        hhmmss = r.name.split("T")[1][:6]
        out = OUTDIR / f"code-{this_utc.date()}-{sess8[:6]}-window-{hhmmss}.md"
        res = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "audit" / "mint_window.py"),
             str(jsonl), lo_s, hi_s, "--out", str(out), "--receipt", r.name],
            capture_output=True, text=True)
        print(res.stdout.strip() or res.stderr.strip())
        if res.returncode != 0:
            print(f"auto-mint FAIL (mint_window rc={res.returncode}, not consumed): {r.name}")
            rc = 1
            continue
        m = re.search(r"assistant_text_blocks=(\d+).*tool_calls=(\d+)", res.stdout)
        if not m or int(m.group(1)) == 0 or int(m.group(2)) == 0:
            print(f"auto-mint BAR-FAIL (assistant_text_blocks/tool_calls zero or unparsed, "
                  f"NOT consumed; window kept for inspection): {r.name}")
            rc = 1
            continue
        with open(CONSUMED, "a", encoding="utf-8") as f:
            f.write(r.name + "\n")
        print(f"auto-mint CONSUMED: {r.name} -> {out.name}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
