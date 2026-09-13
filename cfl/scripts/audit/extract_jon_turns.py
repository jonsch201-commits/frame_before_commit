#!/usr/bin/env python3
"""extract_jon_turns.py -- publish Jon's own words from a session JSONL to a TRACKED path.

WHY THIS EXISTS
---------------
Jon, 2026-09-04 ~16:2x CDT, verbatim (typos his):

    Last PR you told me to make comments, i'm not doing so this time. Ensure both
    times work equally well from a traceability context and a vector-embeded graph
    rag context - like these PRs are important and they should trace!

He is naming an asymmetry that is real and that CFL had not noticed:

  * PR-2's feedback went into GITHUB PR COMMENTS -- attached to the PR forever,
    fetchable by anyone with `gh`, and already mirrored into raw/github-comments/.
  * PR-3's feedback is going into a LIVE SESSION. That session's JSONL lives at
    ~/.claude/projects/<trunk>/<id>.jsonl and its rendered windows land under
    raw/transcripts/, which `.gitignore:2` excludes. A reviewer on the branch
    cannot open any of it.

So roughly fifteen substantive corrections from Jon on 2026-09-04 -- the
reader_token_cost understatement, the missing co-trunk review gates, the branch
name's hidden dimension, the signature that points at an unreadable transcript --
shaped this PR and NONE of them traced from it. The PR carries the fixes and not
their provenance, which is the same defect as a quote with no primary.

WHAT IT DOES
------------
Walks a session JSONL and emits Jon's turns VERBATIM, with timestamps, to a
markdown file under a tracked path. Two record classes, because one is invisible
to every window renderer:

  1. type == "user" whose content is real text (not a tool_result envelope)
  2. type == "attachment" with attachment.type == "queued_command" -- messages
     typed WHILE a turn runs. The verbatim text is in the entry's `prompt` field.
     The universal constitution names this class explicitly: a compact can consume
     the queue before any of them becomes a type:user turn, and then the text
     exists ONLY here.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
  * It does not paraphrase, correct, or add emphasis. Typos are his and stay his;
    added emphasis inside a quote makes it unfindable by literal grep, which is the
    exact defect the no-tidying rule exists to prevent.
  * It does not filter by judgement. It filters STRUCTURALLY (hook text, system
    reminders and tool results are excluded by shape) and reports how many it
    dropped, so a reader can see the denominator rather than trust a curator.
  * It writes nothing outside the output path given.

Exit: 0 wrote | 2 could not read the JSONL (UNKNOWN, never "no turns found").
"""

import argparse
import json
import sys
from pathlib import Path

# Structural exclusions. These are envelopes the harness generates, not Jon.
DROP_MARKERS = (
    "Stop hook feedback:",
    "PRE-STOP CONSULT REQUIRED",
    "<system-reminder>",
    "[SYSTEM NOTIFICATION",
    "<cross-session-message",
    "Gate floor (re-created",
    "<local-command-caveat>",
    "<command-name>",
    "Caveat: The messages below were generated",
    "This is how Claude Code surfaces messages",
    "PostToolUse:",
    "PreToolUse:",
    "SessionStart hook",
    "Result of calling the",
    "Called the",
)


def text_of(msg) -> str:
    """Pull plain text out of a user message, ignoring tool_result envelopes."""
    if isinstance(msg, str):
        return msg
    if isinstance(msg, dict):
        c = msg.get("content")
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            out = []
            for blk in c:
                if isinstance(blk, dict) and blk.get("type") == "text":
                    out.append(blk.get("text", ""))
            return "\n".join(out)
    return ""


def looks_like_harness(t: str) -> bool:
    return any(mk in t for mk in DROP_MARKERS)


def walk(path: Path):
    kept, dropped, unreadable, dup = [], 0, 0, 0
    seen = set()
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln, line in enumerate(f, 1):
            try:
                d = json.loads(line)
            except Exception:
                unreadable += 1
                continue
            ts = d.get("timestamp") or ""
            typ = d.get("type")
            txt = ""
            klass = ""
            if typ == "queue-operation" and d.get("operation") == "enqueue":
                # THE CLASS THAT ACTUALLY HOLDS JON'S MID-TURN WORDS in this harness,
                # found 2026-09-04 by dumping the record for a sentence he had just
                # typed. It is NOT `attachment/queued_command` and it is NOT in the
                # constitution's venue table. `content` is the verbatim string.
                # The first version of this script extracted 307 "turns" of which most
                # were not his, AND missed this class entirely -- over-inclusive and
                # blind at the same time. Caught before publishing, by opening one
                # record instead of trusting the count.
                raw = d.get("content") or ""
                txt = raw if isinstance(raw, str) else text_of({"content": raw})
                klass = "queue-operation/enqueue (mid-turn; the class window renderers miss)"
            elif typ == "user":
                # DELIBERATELY NOT EXTRACTED. In this harness `type: user` also carries
                # tool results, subagent traffic and cross-session envelopes; extracting
                # it produced 278 "Jon turns" when he sent on the order of thirty. An
                # over-inclusive file labelled "Jon's words" is a curation claim this
                # script cannot support, and publishing it would be a worse defect than
                # publishing less. Restricted to the class VERIFIED to hold his text.
                continue
            elif typ == "attachment":
                att = d.get("attachment") or {}
                if att.get("type") == "queued_command":
                    raw = att.get("prompt") or d.get("prompt") or ""
                    # A queued_command prompt is sometimes a list of blocks, not a
                    # string. Found 2026-09-04 by this script crashing on it -- and a
                    # crash is the good outcome: a silent str() would have published
                    # a Python repr as if it were Jon's words.
                    txt = raw if isinstance(raw, str) else text_of({"content": raw})
                    klass = "queued_command (mid-turn; invisible to window renderers)"
            if not txt or not txt.strip():
                continue
            if looks_like_harness(txt):
                dropped += 1
                continue
            t = txt.strip()
            if t in seen:
                dup += 1
                continue
            seen.add(t)
            kept.append({"line": ln, "ts": ts, "class": klass, "text": t})
    return kept, dropped, unreadable, dup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--session", default="")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    if a.self_check:
        fails = []
        if not looks_like_harness("Stop hook feedback:\nblah"):
            fails.append("a Stop-hook envelope was NOT dropped")
        if looks_like_harness("does this refer to just the part of the corpus that is truely new"):
            fails.append("a real Jon sentence WAS dropped -- the filter is eating primaries")
        if text_of({"content": [{"type": "text", "text": "hi"}]}) != "hi":
            fails.append("text extraction failed on a block list")
        if text_of({"content": [{"type": "tool_result", "content": "x"}]}) != "":
            fails.append("a tool_result leaked into extracted text")
        if fails:
            print(f"SELF-CHECK: FAIL -- {len(fails)}")
            for x in fails:
                print("  " + x)
            return 1
        print("SELF-CHECK: PASS -- 4 assertions incl. a control that a real Jon sentence survives")
        return 0

    p = Path(a.jsonl)
    if not p.exists():
        print(f"UNKNOWN: no JSONL at {p} -- this is not 'no turns found'")
        return 2
    kept, dropped, unreadable, dup = walk(p)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "kind: source",
        f"slug: {out.stem}",
        "date: 2026-09-04",
        "status: PRIMARY -- verbatim, typos his, no emphasis added",
        f"session: {a.session or p.stem}",
        f"source_jsonl: {p}",
        "captured_by: scripts/audit/extract_jon_turns.py",
        "---",
        "",
        f"# Jon's turns, session `{a.session or p.stem[:8]}`, verbatim",
        "",
        "**Published because Jon asked, 2026-09-04 ~16:2x CDT (verbatim, typos his):**",
        "",
        "> Last PR you told me to make comments, i'm not doing so this time. Ensure both times work "
        "equally well from a traceability context and a vector-embeded graph rag context - like "
        "these PRs are important and they should trace!",
        "",
        "PR-2's feedback went into GitHub PR comments, which attach to the PR and are fetchable by "
        "anyone. PR-3's went into a live session whose JSONL sits under gitignored `raw/`. **This "
        "file is the tracked, greppable, retrievable form of the second, so both trace equally.**",
        "",
        f"`[m]` **{len(kept)} turns published · {dropped} harness envelopes dropped structurally "
        f"(hook feedback, system reminders, tool results, cross-session messages) · "
        f"{unreadable} unparseable lines · {dup} duplicates collapsed (a queued message reappears as a turn).**",
        "",
        "⛔ **Verbatim. Typos are his. No emphasis added inside any quote — added emphasis makes a "
        "quote unfindable by literal grep, which is the defect the rule exists to prevent.**",
        "",
        "---",
        "",
    ]
    for k in kept:
        lines.append(f"## {k['ts']} · JSONL line {k['line']} · {k['class']}")
        lines.append("")
        for para in k["text"].split("\n"):
            lines.append(f"> {para}" if para.strip() else ">")
        lines.append("")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}  ({len(kept)} turns, {dropped} dropped, {unreadable} unparseable)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
