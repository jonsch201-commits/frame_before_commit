#!/usr/bin/env python3
"""exchange_write_check.py — PostToolUse hook on Write/Edit: when the written
file is under exchange/, run the letter checks automatically.

Jon, live 2026-09-01 (mid-turn, verbatim): "And we really should hook more as
part of writing to the exchange.... Please?"

Checks (all report-only; a PostToolUse hook cannot un-write a file — findings
surface as hook feedback for the writer to act on THIS turn, while the letter
is not yet delivered):
  1. lint_silence_clause.py — a bare silence-negation REFUSES (exchange-letters
     rule 8; delivery is blocked by the rule, and this makes the lint automatic
     instead of remembered).
  2. promise fields — if `expires:` present, it must parse (on_silence_report's
     parser); if `on_silence:` present with no `expires:`, the letter is
     UNCLOCKED (Herald F-7: a default with no deadline can never come due) —
     reported, not refused, because standing letters legitimately carry
     "nothing acts" unclocked.
  3. frontmatter presence — a letter with no frontmatter at all is flagged
     (per exchange-letters rule 2).

Reads the hook payload from stdin (tool_input.file_path). Exits 0 always for
non-exchange paths and clean letters; exits 2 with findings on stderr so the
harness surfaces them to the writing session.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        # fail VISIBLE, not open — a silent parse failure is indistinguishable from a clean letter
        print(f"exchange-write check UNKNOWN (payload unparseable: {e}) — no check ran", file=sys.stderr)
        return 0
    fp = (payload.get("tool_input") or {}).get("file_path", "")
    if not fp:
        return 0
    p = Path(fp)
    try:
        rel = p.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return 0
    parts = rel.parts
    if not parts or parts[0] != "exchange" or p.suffix != ".md":
        return 0
    # skip the machine ledgers/receipts subtree — they are not letters
    if len(parts) > 1 and parts[1] in ("su-close", "FOR-JON-REVIEW"):
        return 0
    # spine files are state documents, not letters (first live firing hit WAKE.md, 2026-09-01)
    if p.name in ("WAKE.md", "CARRIER.md", "ROUTING-LEDGER.md"):
        return 0
    findings = []

    lint = subprocess.run([sys.executable, str(ROOT / "scripts" / "audit" / "lint_silence_clause.py"), str(p)],
                          capture_output=True, text=True)
    if lint.returncode == 1:
        findings.append("silence-lint REFUSED (rule 8 blocks delivery until fixed):\n" + lint.stdout.strip())

    sys.path.insert(0, str(ROOT / "scripts" / "audit"))
    try:
        from on_silence_report import parse_frontmatter, parse_expiry
        fm = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace")[:4000])
        if not fm and "---" not in p.read_text(encoding="utf-8", errors="replace")[:10]:
            findings.append("no frontmatter block (exchange-letters rule 2: from/to/date/kind/on_silence)")
        if fm.get("expires") and parse_expiry(fm["expires"]) is None:
            findings.append(f"expires: unparseable ('{fm['expires']}') — the on-silence reader will "
                            f"report it UNPARSEABLE forever; use a date or drop the field")
        if fm.get("on_silence") and not fm.get("expires"):
            findings.append("UNCLOCKED: on_silence declared with no expires — Herald F-7: a default "
                            "with no deadline can never come due (fine for standing letters; "
                            "deliberate?)")
        # read the RAW frontmatter for this key — parse_frontmatter extracts only
        # expires/on_silence, so checking the parsed dict flagged letters that HAVE the
        # field (first false positive: the reboot letter, 2026-09-01 18:2x)
        raw_fm = p.read_text(encoding="utf-8", errors="replace")[:4000]
        raw_fm = raw_fm[:raw_fm.find("\n---", 3) + 1] if raw_fm.startswith("---") else ""
        if "reader_token_cost" not in raw_fm:
            findings.append("no reader_token_cost declared (Herald 17:2x: 91% of the fleet's queue "
                            "cost is ESTIMATED from bytes; a declared cost lets a budgeted wake "
                            "order its reading — exchange-letters rule 2)")
    except Exception as e:
        findings.append(f"promise-field check errored ({e}) — UNKNOWN, not clean")

    if findings:
        print(f"exchange-write checks — {p.name}:", file=sys.stderr)
        for f in findings:
            print("  " + f.replace("\n", "\n  "), file=sys.stderr)
        return 2
    print(f"exchange-write checks clean: {p.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
