"""grep_vs_query_census.py -- count a seat's grep-class commands against its retrieval queries.

Jon, 2026-09-11 16:1x: "Query the wiki by default rather than grep." Jon, 23:4x, on a grep an hour
later: "as your first instinct". Measured at 23:4x for session 682d274b: 16 graphrag queries, 54
grep/Select-String commands, the first grep at 16:08 before the order was given. A rule in prose is
a mechanism out of reach of its trigger, so this counter runs at every timer wake and prints the
ratio beside the render line. It grades; it does not block.

usage: python -u scripts/grep_vs_query_census.py <session.jsonl> [since ISO-8601 UTC]
"""
import io
import json
import re
import sys

GREP = re.compile(r"\bgrep\b|Select-String")
QUERY = "graphrag.sh query"


def census(path, since=None):
    q = g = 0
    for line in io.open(path, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("type") != "assistant":
            continue
        if since and (o.get("timestamp", "") < since):
            continue
        for b in o.get("message", {}).get("content", []) or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Bash", "PowerShell"):
                cmd = b.get("input", {}).get("command", "")
                if QUERY in cmd:
                    q += 1
                if GREP.search(cmd):
                    g += 1
    return q, g


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    since = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        q, g = census(sys.argv[1], since)
    except FileNotFoundError:
        print("UNKNOWN: transcript not found at %s (no measurement)" % sys.argv[1])
        sys.exit(2)
    ratio = ("%.1f greps per query" % (g / q)) if q else "no queries at all"
    print("GREP-VS-QUERY: queries=%d greps=%d (%s)%s" % (q, g, ratio, (" since %s" % since) if since else ""))
