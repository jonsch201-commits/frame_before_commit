#!/usr/bin/env python3
"""query_by_default.py -- did this seat GREP where it should have QUERIED?

Jon, 2026-09-11 (history.jsonl:4552, verbatim, typos his):
    "Query the wiki by default rather than grep, complain loudly to ears if issue"
and :4554: "Fail - query by default."

This is the detector half of the skills-evolution finding: auto-invocation makes a
skill FIRE; nothing today reports the invocations that SHOULD have happened and did
not. Jon, compass message: "you need to help me see when I should have used a skill."

WHAT IT DOES
    Walks a session JSONL. Classifies every search-shaped tool call as QUERY
    (scripts/graphrag/retrieve.py) or GREP (Grep tool, or grep/rg/findstr through
    Bash). Reports GREPs that had no QUERY anywhere in the preceding --window tool
    calls -- those are the candidate missed queries.

WHAT IT DELIBERATELY DOES NOT DO
    It does not claim a grep was WRONG. `skills/wiki-query` carries a whole
    when-not-to-query section: present-vs-record, querying your own recent output,
    a command being sharper, a stale index. A grep for a literal path or a byte count
    is correct and this script would still flag it. The output is a CANDIDATE LIST
    for a human or a seat to judge, never a verdict.
    Calling its output a defect count is the error it exists to avoid.

EXIT
    0 always. This reports; it does not gate. A detector that blocks gets disabled.
"""
import argparse
import io
import json
import os
import re
import sys

QUERY_MARK = re.compile(r"graphrag[/\\]retrieve\.py|retrieve\.py\s", re.I)
GREP_CMD = re.compile(r"(?:^|[|;&(\s])(?:grep|rg|findstr|Select-String)\b", re.I)
# A literal-lookup grep is usually CORRECT and is not a missed query.
LITERAL_HINT = re.compile(
    r"-c\b|--count|\bsha256|\bwc\b|index\.lock|\.git/|__pycache__|"
    r"reader_token_cost|^\s*ls\b|status --porcelain",
    re.I,
)


def classify(name, payload):
    """-> 'QUERY' | 'GREP' | 'GREP-LITERAL' | None"""
    blob = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
    if name == "Bash":
        cmd = payload.get("command", "") if isinstance(payload, dict) else blob
        if QUERY_MARK.search(cmd):
            return "QUERY"
        if GREP_CMD.search(cmd):
            return "GREP-LITERAL" if LITERAL_HINT.search(cmd) else "GREP"
        return None
    if name == "Grep":
        pat = payload.get("pattern", "") if isinstance(payload, dict) else blob
        return "GREP-LITERAL" if LITERAL_HINT.search(pat) else "GREP"
    if name in ("Task", "Agent"):
        return "QUERY" if QUERY_MARK.search(blob) else None
    return None


def walk(path):
    """Yield (index, kind, snippet) for each search-shaped call, in order."""
    n = 0
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            msg = rec.get("message") or {}
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                n += 1
                kind = classify(block.get("name"), block.get("input") or {})
                if kind:
                    inp = block.get("input") or {}
                    snip = inp.get("command") or inp.get("pattern") or ""
                    yield n, kind, str(snip)[:90].replace("\n", " ")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jsonl", nargs="?", help="session JSONL; omit to use $CLAUDE_SESSION_JSONL")
    ap.add_argument("--window", type=int, default=12,
                    help="how many tool calls back a QUERY still counts as covering a GREP")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return selftest()

    path = args.jsonl or os.environ.get("CLAUDE_SESSION_JSONL", "")
    if not path or not os.path.exists(path):
        print("UNKNOWN: no session JSONL given or found -- this is NOT a clean result.")
        print("         A check that could not run is UNKNOWN, and UNKNOWN dominates a PASS.")
        return 0

    last_query = None
    queries = greps = literals = 0
    flagged = []
    for idx, kind, snip in walk(path):
        if kind == "QUERY":
            queries += 1
            last_query = idx
        elif kind == "GREP-LITERAL":
            literals += 1
        elif kind == "GREP":
            greps += 1
            if last_query is None or (idx - last_query) > args.window:
                gap = "never" if last_query is None else f"{idx - last_query} calls ago"
                flagged.append((idx, gap, snip))

    print(f"session : {os.path.basename(path)}")
    print(f"window  : {args.window} tool calls")
    print(f"QUERY (retrieve.py)      : {queries}")
    print(f"GREP, concept-shaped     : {greps}")
    print(f"GREP, literal-lookup     : {literals}  (not candidates -- a literal grep is usually right)")
    print()
    if not flagged:
        print("CANDIDATES: none. Every concept-shaped search had a query within the window.")
    else:
        print(f"CANDIDATES: {len(flagged)} concept-shaped grep(s) with no query in the window.")
        print("These are CANDIDATES, not defects. Judge each one; see when-not-to-query.")
        for idx, gap, snip in flagged:
            print(f"  call #{idx:<4} last query {gap:<14} {snip}")
    return 0


def selftest():
    """Six cases. Prints PASS/FAIL per case and a total."""
    cases = [
        ("Bash", {"command": "python scripts/graphrag/retrieve.py 'x' -k 5"}, "QUERY"),
        ("Bash", {"command": "grep -rn 'what did Jon decide' wiki/"}, "GREP"),
        ("Bash", {"command": "grep -c 'x' file.md"}, "GREP-LITERAL"),
        ("Grep", {"pattern": "governance postmortem"}, "GREP"),
        ("Grep", {"pattern": "sha256"}, "GREP-LITERAL"),
        ("Bash", {"command": "git status --porcelain"}, None),
    ]
    ok = 0
    for name, payload, want in cases:
        got = classify(name, payload)
        good = got == want
        ok += good
        print(f"  {'PASS' if good else 'FAIL'}  {name:<5} -> {got!r} (want {want!r})")
    print(f"selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
