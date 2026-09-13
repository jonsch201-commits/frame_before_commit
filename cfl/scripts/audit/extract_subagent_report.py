#!/usr/bin/env python3
"""Recover a subagent's real report from its JSONL when the harness swallowed it.

WHY THIS EXISTS
---------------
Three separate failure paths all end with the same symptom -- a lane did the work and the
coordinator has nothing:

  1. The completion notification delivers "Done." and not the report.
  2. The task output-file can be EMPTY.
  3. The agent dies mid-write on an API error AFTER announcing "measurements complete",
     so the deliverable file it was about to write never exists.

In all three the reasoning IS on disk, in the subagent transcript, and the recipe is known:
the report is the LARGEST assistant text block in the JSONL. This turns that recipe into a
command so it is not re-derived under pressure at the moment it is needed.

WRITES TO A FILE, NEVER STDOUT. The recovered text routinely runs 10-40 KB; printing it into
a coordinator's terminal spends the context the recovery was meant to protect.

BOUNDS, all three parts:
  1. NOT REVIEWED: whether the largest block IS the report. A lane that reasoned at length and
     summarised briefly hands back its reasoning instead.
  2. WHY: only the author knows which block was the deliverable; the JSONL does not mark one.
  3. RESULTING LIMITATION: this recovers a CANDIDATE. Read it before citing it. A lane killed
     mid-response yields a TRUNCATED block that ends without warning -- and the tail is the part
     most likely to be missing, and the tail is usually the conclusions.

Usage:
    python scripts/audit/extract_subagent_report.py <agent-id-or-jsonl-path> -o OUT.md
    python scripts/audit/extract_subagent_report.py --list          # recent lanes, newest first
    python scripts/audit/extract_subagent_report.py --selftest
"""
import argparse
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

def _key_for(path):
    """~/.claude/projects sanitises a path by replacing every non-alphanumeric
    CHARACTER (not run) with '-'. Mirrors extract_claude_code_sessions.py's _key_for."""
    import re as _re
    return _re.sub(r"[^A-Za-z0-9]", "-", str(path)).strip("-")


_PROJECTS_ROOT = os.path.join(os.path.expanduser("~"), ".claude", "projects")
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ⛔ THIS WAS PINNED TO THE G: KEY, AND THE 2026-09-02 G:->N: MOVE SILENTLY DEMOTED IT
# TO A TRUNK CFL LEFT THREE DAYS AGO -- --list and agent-fragment lookups against
# CURRENT subagent lanes would come back empty/NOT FOUND with no error naming the real
# cause. No --project-dir override exists here, so find_jsonls() below scans EVERY
# candidate dir (current-derived + historical), newest-first across both.
PROJECT_DIR_CANDIDATES = [
    os.path.join(_PROJECTS_ROOT, _key_for(_REPO)),  # DERIVED: current checkout
    os.path.join(_PROJECTS_ROOT,
                 "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer"),  # historical
]
# kept so any external caller importing the old name still works; find_jsonls() scans
# PROJECT_DIR_CANDIDATES, not this single value.
PROJ = PROJECT_DIR_CANDIDATES[0]


def find_jsonls():
    hits = []
    for proj in PROJECT_DIR_CANDIDATES:
        for pat in ("*/subagents/agent-*.jsonl", "subagents/agent-*.jsonl"):
            hits += glob.glob(os.path.join(proj, pat))
    return sorted(hits, key=lambda p: os.path.getmtime(p), reverse=True)


def resolve(token):
    if os.path.isfile(token):
        return token
    for p in find_jsonls():
        if token in os.path.basename(p):
            return p
    return None


def blocks(path):
    """Every assistant text block in the transcript, paired with its line number."""
    out = []
    with io.open(path, encoding="utf-8", errors="ignore") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            msg = rec.get("message") or {}
            if rec.get("type") != "assistant" and msg.get("role") != "assistant":
                continue
            content = msg.get("content")
            if isinstance(content, str):
                out.append((i + 1, content))
            elif isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text" and c.get("text"):
                        out.append((i + 1, c["text"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent", nargs="?", help="agent id fragment, or a path to the JSONL")
    ap.add_argument("-o", "--out", help="file to write the recovered report to (REQUIRED)")
    ap.add_argument("--list", action="store_true", dest="list_", help="recent lanes, newest first")
    ap.add_argument("--top", type=int, default=1, help="write the N largest blocks, in size order")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if a.list_:
        for p in find_jsonls()[:25]:
            print("%9d B  %s" % (os.path.getsize(p), os.path.basename(p)))
        return 0

    if not a.agent:
        ap.error("give an agent id fragment or --list")
    path = resolve(a.agent)
    if not path:
        print("NOT FOUND: no subagent JSONL matches %r" % a.agent)
        print("  That is UNKNOWN, not empty -- run --list to see what is on disk.")
        return 2

    bs = blocks(path)
    if not bs:
        print("ZERO assistant text blocks in %s" % os.path.basename(path))
        print("  UNKNOWN, not 'the lane produced nothing' -- the schema may differ.")
        return 2
    bs.sort(key=lambda t: len(t[1]), reverse=True)
    picked = bs[:max(1, a.top)]

    print("source : %s" % path)
    print("blocks : %d assistant text block(s); largest %d B at line %d"
          % (len(bs), len(picked[0][1]), picked[0][0]))
    if not a.out:
        print("")
        print("NO --out GIVEN, SO NOTHING WAS WRITTEN. This tool never prints the report: a")
        print("recovered report runs 10-40 KB and printing it spends the context the recovery")
        print("exists to protect. Re-run with -o <file>.")
        return 1

    with io.open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# RECOVERED from a subagent transcript -- CANDIDATE, not a verified report\n\n")
        fh.write("source: `%s`\n\n" % path)
        fh.write("method: the largest assistant text block(s). The JSONL does not mark a\n")
        fh.write("deliverable, so this is the recipe's best guess. A lane killed mid-response\n")
        fh.write("yields a TRUNCATED block that ends without warning, and the tail is usually\n")
        fh.write("the conclusions. Check how it ends before citing it.\n")
        for n, (ln, txt) in enumerate(picked, 1):
            fh.write("\n---\n\n## block %d of %d -- line %d, %d B\n\n" % (n, len(picked), ln, len(txt)))
            fh.write(txt)
            fh.write("\n")
    print("wrote  : %s (%d B)" % (a.out, os.path.getsize(a.out)))
    return 0


def selftest():
    import tempfile
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, "agent-deadbeef.jsonl")
    rows = [
        {"type": "assistant", "message": {"role": "assistant",
         "content": [{"type": "text", "text": "short preamble"}]}},
        {"type": "user", "message": {"role": "user", "content": "not mine"}},
        {"type": "assistant", "message": {"role": "assistant",
         "content": [{"type": "text", "text": "THE REPORT " + "x" * 500},
                     {"type": "tool_use", "name": "BashToolMarker"}]}},
        "{ this line is not json",
    ]
    with io.open(src, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write((r if isinstance(r, str) else json.dumps(r)) + "\n")

    fails = []
    bs = blocks(src)
    if len(bs) != 2:
        fails.append("expected 2 assistant text blocks, got %d" % len(bs))
    biggest = max(bs, key=lambda t: len(t[1]))[1]
    if not biggest.startswith("THE REPORT"):
        fails.append("largest block was not the report")
    # NEGATIVE CONTROLS -- each covers a way this could pass while being broken:
    if any("not mine" in t for _, t in bs):
        fails.append("a USER turn was collected as assistant text")
    if any("BashToolMarker" in t for _, t in bs):
        fails.append("a tool_use block was collected as text")
    if resolve("no-such-agent-id-anywhere") is not None:
        fails.append("resolve() invented a match for an unknown id")
    # a malformed JSONL line must be skipped rather than fatal -- proven by reaching this line

    print("=== SELF-TEST -- extract_subagent_report.py ===")
    for f_ in fails:
        print("  FAIL: %s" % f_)
    if fails:
        print("")
        print("RESULT: FAIL -- %d" % len(fails))
        return 1
    checks = ["largest assistant text block is selected",
              "NEGATIVE CONTROL -- user turns are not collected",
              "NEGATIVE CONTROL -- tool_use blocks are not collected",
              "a malformed JSONL line is skipped, not fatal",
              "NEGATIVE CONTROL -- an unknown agent id resolves to nothing"]
    for c in checks:
        print("  %-58s: PASS" % c)
    print("")
    print("RESULT: PASS -- %d/%d" % (len(checks), len(checks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
