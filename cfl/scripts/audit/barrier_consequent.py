#!/usr/bin/env python3
"""
barrier_consequent.py -- CB-3. Give the compact barrier's findings a CONSEQUENT.

WHY THIS EXISTS
---------------
`postcompact_verify.py` grades the compact summary against disk and writes an
artifact under exchange/su-close/postcompact/. On 2026-09-04 it emitted
VERDICT: FINDINGS (12) -- every one saying the summary named 1 of 13 LIVE
wayfinder maps -- and NOTHING CONSUMED THEM. The pipeline's own step 9 records
"findings are report, not block".

A verifier whose findings nothing reads is the delivered-is-not-received defect
pointed at ourselves. This script is the missing half: findings become ROWS that
must be disposed, and an undisposed row eventually costs something.

WHAT IT DOES
------------
1. Reads the NEWEST postcompact artifact (or --artifact PATH).
2. Extracts its findings.
3. Appends each NEW one to exchange/su-close/BARRIER-FINDINGS.md as a row
   carrying `disposition:` **UNDISPOSITIONED**.
   Dedupe is by sha256(artifact_name + finding_text), so re-running is a no-op.
   APPEND ONLY. Never rewrites or removes a row -- no deletion.
4. Exits 3 when undisposed rows are older than --max-age-hours (default 24).

THE STRUCK-MARKER TRAP, borrowed from Secretary's FIX 2 (2026-09-04)
--------------------------------------------------------------------
Dispositions are written by STRIKING the placeholder in place, because
no-deletion forbids removing it. So a naive substring test for the word
UNDISPOSITIONED matches DISPOSED rows too, and a ledger with zero open rows
reports all of them open. Secretary shipped exactly that bug this morning and
caught it with a two-direction control.

So OPEN_RE matches the FIELD UNSTRUCK -- `disposition:` **UNDISPOSITIONED** with
no `~~` around it -- and self_check() asserts BOTH directions before any gate
runs. A gate that cannot fail is this week's dominant defect; a gate that cannot
PASS is the one Secretary found in unlazy-verify G2. Both are tested here.
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PC_DIR = REPO / "exchange" / "su-close" / "postcompact"
LEDGER = REPO / "exchange" / "su-close" / "BARRIER-FINDINGS.md"

# A finding line in a postcompact artifact, e.g.
#   - C1 live-map: LIVE map `wayfinder-x.md` is NOT named in the summary
FINDING_RE = re.compile(r"^-\s+(C\d+\s+[^:]+:\s*.+)$")

# OPEN = the field, unstruck. Strikethrough anywhere on the row disposes it.
OPEN_RE = re.compile(r"`disposition:`\s+\*\*UNDISPOSITIONED\*\*")
STRUCK_RE = re.compile(r"~~[^~]*UNDISPOSITIONED[^~]*~~")

ROW_RE = re.compile(r"^\| `(?P<key>[0-9a-f]{16})` \| (?P<seen>\S+) \|")

LEDGER_HEADER = """# Barrier findings ledger

Findings emitted by `postcompact_verify.py` at a compact barrier, turned into rows
that must be disposed. Written by `scripts/audit/barrier_consequent.py` (CB-3).

⛔ **APPEND-ONLY.** A disposition is written by STRIKING the placeholder in place,
never by deleting the row. `~~`disposition:` **UNDISPOSITIONED**~~ CLOSED <why>`

⚠️ A row still open past 24 h makes this script exit 3. That is the consequent;
before it existed, a barrier could emit twelve findings and cost nothing.

| key | first seen | artifact | finding | disposition |
|---|---|---|---|---|
"""


def newest_artifact():
    if not PC_DIR.is_dir():
        return None
    arts = sorted(PC_DIR.glob("2*.md"), key=lambda p: p.stat().st_mtime)
    return arts[-1] if arts else None


def extract_findings(text):
    """Only the lines under a '### Findings' heading, stopping at the next heading."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("### "):
            inside = line.startswith("### Findings")
            continue
        if inside:
            m = FINDING_RE.match(line.strip())
            if m:
                out.append(m.group(1).strip())
    return out


def key_for(artifact_name, finding):
    return hashlib.sha256(f"{artifact_name}|{finding}".encode("utf-8")).hexdigest()[:16]


def read_ledger():
    if not LEDGER.exists():
        return "", {}
    text = LEDGER.read_text(encoding="utf-8")
    rows = {}
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if m:
            rows[m.group("key")] = {"seen": m.group("seen"), "line": line}
    return text, rows


def row_is_open(line):
    """A row is OPEN iff the field appears UNSTRUCK. Strikethrough disposes it."""
    if STRUCK_RE.search(line):
        return False
    return bool(OPEN_RE.search(line))


def append_rows(new_rows):
    text = LEDGER.read_text(encoding="utf-8") if LEDGER.exists() else LEDGER_HEADER
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as f:
        f.write(text.rstrip("\n") + "\n" + "\n".join(new_rows) + "\n")


def self_check():
    """Two-direction controls. Each must fail for the right reason."""
    fails = []
    open_row = "| `aaaaaaaaaaaaaaaa` | 2026-09-04T00:00:00+00:00 | a.md | x | `disposition:` **UNDISPOSITIONED** |"
    disposed = "| `bbbbbbbbbbbbbbbb` | 2026-09-04T00:00:00+00:00 | a.md | x | ~~`disposition:` **UNDISPOSITIONED**~~ CLOSED: fixed |"

    if not row_is_open(open_row):
        fails.append("an UNSTRUCK row read as disposed -- the gate cannot fire")
    if row_is_open(disposed):
        fails.append("a STRUCK row read as open -- Secretary's FIX 2 bug, reproduced here")

    # A gate that cannot PASS is as broken as one that cannot FAIL (unlazy G2).
    if row_is_open("| `cccccccccccccccc` | t | a.md | x | CLOSED: never had a placeholder |"):
        fails.append("a row with no placeholder read as open")

    # Finding extraction must be scoped to the Findings section.
    sample = (
        "## VERDICT: FINDINGS (2)\n"
        "### Findings\n"
        "- C1 live-map: LIVE map `a.md` is NOT named in the summary\n"
        "- C2 branch: `x` not named\n"
        "### Checks run\n"
        "- C1 live-map: `b.md` named\n"
    )
    got = extract_findings(sample)
    if len(got) != 2:
        fails.append(f"extractor took {len(got)} findings, expected 2 (Checks-run leaked in?)")
    # The control must name the exact line that must NOT leak. The first draft of
    # this assertion tested `g[-5:] == "named" and "NOT" not in g`, which fired on
    # the legitimate finding "C2 branch: `x` not named" -- lowercase "not". The
    # control was wrong, not the extractor, and it failed on its own author.
    if any("`b.md` named" in g for g in got):
        fails.append("the 'Checks run' line `b.md` named leaked into findings")
    if not any(g.startswith("C1 live-map") for g in got):
        fails.append("the real C1 finding was dropped")

    # An artifact with zero findings must yield zero rows, not an error.
    if extract_findings("## VERDICT: CLEAN\n### Checks run\n- C1 ok\n"):
        fails.append("a clean artifact produced findings")

    # Dedupe must be stable and collision-free across artifacts.
    if key_for("a.md", "f") == key_for("b.md", "f"):
        fails.append("the same finding in two artifacts collides to one key")
    if key_for("a.md", "f") != key_for("a.md", "f"):
        fails.append("key is not stable across calls")

    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", default=None)
    ap.add_argument("--max-age-hours", type=float, default=24.0)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()

    if args.self_check:
        fails = self_check()
        if fails:
            print(f"SELF-CHECK: FAIL -- {len(fails)} violation(s)")
            for f in fails:
                print(f"  {f}")
            return 1
        print("SELF-CHECK: PASS -- 9 assertions, both directions of the struck-marker "
              "test plus a gate-cannot-pass control")
        return 0

    art = Path(args.artifact) if args.artifact else newest_artifact()
    if art is None or not art.exists():
        print("BARRIER-CONSEQUENT: UNKNOWN -- no postcompact artifact found. "
              "Not a clean run; nothing could be graded.")
        return 2

    findings = extract_findings(art.read_text(encoding="utf-8", errors="replace"))
    _, existing = read_ledger()
    now = datetime.now(timezone.utc)

    new_rows = []
    for f in findings:
        k = key_for(art.name, f)
        if k in existing:
            continue
        safe = f.replace("|", "/")
        new_rows.append(
            f"| `{k}` | {now.isoformat(timespec='seconds')} | {art.name} | {safe} | "
            f"`disposition:` **UNDISPOSITIONED** |"
        )

    if new_rows:
        append_rows(new_rows)

    _, rows = read_ledger()
    open_rows, stale = [], []
    cutoff = now - timedelta(hours=args.max_age_hours)
    for k, r in rows.items():
        if row_is_open(r["line"]):
            open_rows.append(k)
            try:
                if datetime.fromisoformat(r["seen"]) < cutoff:
                    stale.append(k)
            except ValueError:
                stale.append(k)  # unparseable timestamp is UNKNOWN, and UNKNOWN dominates

    print(f"BARRIER-CONSEQUENT: artifact={art.name} findings={len(findings)} "
          f"new_rows={len(new_rows)} open={len(open_rows)} "
          f"stale_over_{args.max_age_hours:g}h={len(stale)}")
    print(f"  ledger: {LEDGER}")

    if stale:
        print(f"  EXIT 3: {len(stale)} finding(s) open past {args.max_age_hours:g}h. "
              "A barrier that emits findings nothing disposes is a log line, not a check.")
        for k in stale[:10]:
            print(f"    {k}: {rows[k]['line'][:150]}")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
