"""message_ledger_from_transcript.py -- rebuild a seat's SendMessage ledger from its own session JSONL.

Why: WC-1 (a commitment writes its own receipt at send time) failed for Professional on 2026-09-11
(51 sends, 0 records: the record hook keyed the roster on a session name carrying an N3 suffix) and
Secretary has no recorder at all. The transcript holds every send with recipient and summary, so the
ledger can be derived rather than recalled. Output is a markdown table with the transcript path in
its frontmatter, so the number is emitted by the command that computed it.

usage: python -u scripts/message_ledger_from_transcript.py <session.jsonl> [out.md]
       (a worktree session lives under ~/.claude/projects/<key>--claude-worktrees-<name>/, not the
        trunk's bare key; pass the real path, and print it, since the wrong path reads as 0 sends)
"""
import datetime
import io
import json
import os
import sys

CDT = datetime.timezone(datetime.timedelta(hours=-5))


def sends(path):
    rows = []
    for line in io.open(path, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("type") != "assistant":
            continue
        content = o.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "SendMessage":
                inp = b.get("input", {})
                ts = o.get("timestamp", "")
                try:
                    t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(CDT).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    t = ts
                rows.append((t, inp.get("to", ""), inp.get("summary", "")))
    return rows


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print("UNKNOWN: transcript not found at %s (not 0 sends: no measurement)" % path)
        sys.exit(2)
    rows = sends(path)
    out = sys.argv[2] if len(sys.argv) > 2 else None
    lines = ["---",
             "title: \"Message ledger reconstructed from the transcript: %d SendMessage calls\"" % len(rows),
             "kind: ledger",
             "transcript: \"%s\"" % path.replace("\\", "/"),
             "generated: \"%s CDT by scripts/message_ledger_from_transcript.py\"" % datetime.datetime.now(CDT).strftime("%Y-%m-%d %H:%M:%S"),
             "---", "",
             "| time CDT | to | summary |", "|---|---|---|"]
    for t, to, s in rows:
        lines.append("| %s | %s | %s |" % (t, to, s.replace("|", "/")))
    text = "\n".join(lines) + "\n"
    if out:
        io.open(out, "w", encoding="utf-8").write(text)
        print("sends: %d  transcript: %s  written: %s" % (len(rows), path, out))
    else:
        sys.stdout.write(text)
        print("sends: %d  transcript: %s" % (len(rows), path))


if __name__ == "__main__":
    main()
