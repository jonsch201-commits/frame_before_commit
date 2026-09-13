#!/usr/bin/env python3
"""turn_metadata.py -- PR-3 B (D-row: per-turn metadata extractor).

WHY: a later reader (a compact summary, a cold grader, a wake-time review) needs to know,
per assistant turn, what that turn actually TOUCHED -- files read, files written/edited,
commands run, tools used -- without re-parsing the raw session JSONL by hand every time.

INPUT: a Claude Code session JSONL (one JSON object per line; see
C:\\Users\\JonSc\\.claude\\projects\\<trunk>\\*.jsonl).

SCHEMA, DERIVED (not assumed) from a real 10,975-line session file, 2026-09-04:
  - Every line has a top-level "type". Only "user" and "assistant" lines carry a "message"
    dict. Every other type (attachment, system, queue-operation, pr-link, custom-title,
    agent-name, last-prompt, mode, permission-mode, atis-latch, file-history-snapshot,
    file-history-delta) has NO "message" key at all.
  - "attachment" records with attachment.type == "queued_command" are Jon's messages typed
    WHILE a turn is running. The verbatim text is in attachment.prompt. This class exists
    ONLY here -- it is never a type:"user" turn -- so a renderer that reads only type:"user"
    silently drops it.
  - Records carry a top-level "isSidechain" bool (false on every top-level record observed
    in the fixture session; a subagent's OWN session JSONL is a separate file under
    <session>/subagents/ or similar and is not this file's concern -- but the field is
    handled here defensively in case a future capture inlines sidechain turns).
  - A single logical assistant "turn" (one LLM response, one user-visible message) is often
    split across MULTIPLE JSONL lines that share the same message.id -- e.g. a thinking
    block and a text block, or a text block followed by N tool_use blocks, each landing on
    its own line as the response streams. Measured: 2,516 type:"assistant" lines resolve to
    1,194 distinct message.id values; every id's lines are CONTIGUOUS (0 interleaved runs).
    So a turn = the group of assistant lines sharing one message.id, in file order.
  - tool_use blocks live in message.content[] as {"type":"tool_use","name":...,"input":{...}}.
    Read -> input.file_path. Write / Edit -> input.file_path. Bash -> input.command
    (+ optional input.description).

FOUR NAMED FAILURE MODES THIS SCRIPT GUARDS AGAINST (each has already cost this repo):
  1. Records without a "message" dict getting silently skipped. -> classify_record() gives
     every record a class; a "no-message-dict" record is COUNTED, never dropped.
  2. queued_command attachments being invisible to a type:"user" reader. -> extracted into
     a dedicated top-level "queued_commands" list with full text and a source line number.
  3. Sidechain/subagent entries folded into the parent turn uncredited. -> a turn whose
     lines carry isSidechain=true is emitted as its own record with sidechain:true and is
     NEVER merged into a non-sidechain turn's file/tool sets.
  4. A count of 0 masquerading as "could not parse". -> every extraction that fails (a
     tool_use block missing the key it should have) is logged to "could_not_parse" with a
     reason and the turn's own counts are NOT silently zeroed for it; see PARSE_ISSUE.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, OrderedDict
from pathlib import Path

READ_TOOLS = {"Read"}
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}
BASH_TOOLS = {"Bash"}

COMMAND_TRUNCATE = 120


def classify_record(rec: dict) -> str:
    """Priority-ordered classification. Every record gets exactly one class; nothing is
    dropped. Order matters: queued_command is carved out of the larger no-message-dict
    bucket because it is the one no-message class a later reader must not lose."""
    t = rec.get("type")
    if t == "attachment" and (rec.get("attachment") or {}).get("type") == "queued_command":
        return "attachment-queued_command"
    if "message" not in rec:
        return "no-message-dict"
    if rec.get("isSidechain") is True:
        return "sidechain"
    if t == "user":
        return "user"
    if t == "assistant":
        return "assistant"
    return "other"


def load_records(jsonl_path: Path):
    """Yield (line_no, record_or_None, raw_line, json_error_or_None). Never raises on a
    single bad line -- a JSON parse error is itself a class, not a crash."""
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh):
            raw = raw.rstrip("\n\r")
            if not raw.strip():
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError as e:
                yield line_no, None, raw, str(e)
                continue
            yield line_no, rec, raw, None


def truncate(s, n=COMMAND_TRUNCATE):
    if s is None:
        return None
    s = str(s)
    return s if len(s) <= n else s[:n]


def extract_turns(jsonl_path: Path):
    """Walk the file once. Returns:
      turns: ordered list of turn dicts (assistant turns, grouped by message.id, in the
             order their FIRST line appears)
      queued_commands: list of dicts for every attachment-queued_command record
      class_counts: Counter of classify_record() results
      could_not_parse: list of {line_no, reason} for extraction-level failures
      json_errors: list of {line_no, error}
    """
    class_counts = Counter()
    could_not_parse = []
    json_errors = []
    queued_commands = []

    # message.id -> turn dict, plus an ordered key list so output preserves first-seen order
    turns_by_id = OrderedDict()

    for line_no, rec, raw, err in load_records(jsonl_path):
        if err is not None:
            json_errors.append({"line_no": line_no, "error": err})
            class_counts["json_error"] += 1
            continue

        cls = classify_record(rec)
        class_counts[cls] += 1

        if cls == "attachment-queued_command":
            att = rec.get("attachment") or {}
            queued_commands.append(
                {
                    "line_no": line_no,
                    "timestamp": rec.get("timestamp") or att.get("timestamp"),
                    "prompt": att.get("prompt"),
                    "command_mode": att.get("commandMode"),
                }
            )
            continue

        if cls not in ("assistant", "sidechain"):
            # user / no-message-dict / other -- not a turn-metadata source for THIS script.
            # (Task scope is assistant-turn metadata; user turns carry no tool_use blocks.)
            continue

        message = rec.get("message") or {}
        mid = message.get("id")
        if mid is None:
            could_not_parse.append(
                {"line_no": line_no, "reason": "assistant/sidechain record missing message.id"}
            )
            continue

        key = (cls, mid)
        turn = turns_by_id.get(key)
        if turn is None:
            turn = {
                "turn_index": None,  # assigned after the full walk, in first-seen order
                "message_id": mid,
                "timestamp": rec.get("timestamp"),
                "role": message.get("role", "assistant"),
                "sidechain": cls == "sidechain",
                "line_nos": [],
                "files_read": set(),
                "files_written": set(),
                "commands": [],
                "tools_used": Counter(),
            }
            turns_by_id[key] = turn

        turn["line_nos"].append(line_no)
        # earliest timestamp wins
        ts = rec.get("timestamp")
        if ts and (turn["timestamp"] is None or ts < turn["timestamp"]):
            turn["timestamp"] = ts

        content = message.get("content")
        if not isinstance(content, list):
            if content is not None:
                could_not_parse.append(
                    {
                        "line_no": line_no,
                        "reason": "message.content is not a list (type=%s)" % type(content).__name__,
                    }
                )
            continue

        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            name = block.get("name")
            turn["tools_used"][name or "UNKNOWN_TOOL"] += 1
            inp = block.get("input")
            if not isinstance(inp, dict):
                could_not_parse.append(
                    {
                        "line_no": line_no,
                        "reason": "tool_use %s block has non-dict input" % name,
                    }
                )
                continue

            if name in READ_TOOLS:
                fp = inp.get("file_path")
                if fp:
                    turn["files_read"].add(fp)
                else:
                    could_not_parse.append(
                        {"line_no": line_no, "reason": "Read tool_use missing input.file_path"}
                    )
            elif name in WRITE_TOOLS:
                fp = inp.get("file_path") or inp.get("notebook_path")
                if fp:
                    turn["files_written"].add(fp)
                else:
                    could_not_parse.append(
                        {"line_no": line_no, "reason": "%s tool_use missing input.file_path" % name}
                    )
            elif name in BASH_TOOLS:
                cmd = inp.get("command")
                if cmd:
                    turn["commands"].append(
                        {
                            "command": truncate(cmd),
                            "description": inp.get("description"),
                            "line_no": line_no,
                        }
                    )
                else:
                    could_not_parse.append(
                        {"line_no": line_no, "reason": "Bash tool_use missing input.command"}
                    )
            # other tools (Glob, Grep, Task, WebFetch, ...) are counted in tools_used but
            # have no dedicated files_read/files_written/commands slot -- that is a scope
            # choice (task named Read/Write-Edit/Bash explicitly), not a silent drop: they
            # are visible in tools_used counts.

    # assign turn_index in first-seen order, finalize sets -> sorted lists
    turns = []
    for idx, (key, turn) in enumerate(turns_by_id.items(), start=1):
        turn["turn_index"] = idx
        turn["files_read"] = sorted(turn["files_read"])
        turn["files_written"] = sorted(turn["files_written"])
        turn["tools_used"] = dict(turn["tools_used"])
        turns.append(turn)

    return turns, queued_commands, class_counts, could_not_parse, json_errors


def render_md(jsonl_path, turns, queued_commands, class_counts, could_not_parse, json_errors):
    lines = []
    lines.append("# Turn metadata -- %s" % jsonl_path)
    lines.append("")
    lines.append("## Record classes")
    lines.append("")
    for cls in sorted(class_counts):
        lines.append("- %s: %d" % (cls, class_counts[cls]))
    lines.append("")
    lines.append("Assistant turns emitted: %d" % sum(1 for t in turns if not t["sidechain"]))
    lines.append("Sidechain turns emitted (labelled, not merged): %d" % sum(1 for t in turns if t["sidechain"]))
    lines.append("Queued-command attachments extracted: %d" % len(queued_commands))
    lines.append("Could-not-parse entries: %d" % len(could_not_parse))
    lines.append("JSON decode errors: %d" % len(json_errors))
    lines.append("")

    file_read_counts = Counter()
    cmd_counts = Counter()
    for t in turns:
        for f in t["files_read"]:
            file_read_counts[f] += 1
        for c in t["commands"]:
            cmd_counts[c["command"]] += 1

    lines.append("## Top 10 most-read files")
    lines.append("")
    for f, n in file_read_counts.most_common(10):
        lines.append("- (%d) %s" % (n, f))
    lines.append("")
    lines.append("## Top 10 most-run commands (first 120 chars)")
    lines.append("")
    for c, n in cmd_counts.most_common(10):
        lines.append("- (%d) `%s`" % (n, c))
    lines.append("")

    lines.append("## Turns")
    lines.append("")
    for t in turns:
        tag = " [SIDECHAIN]" if t["sidechain"] else ""
        lines.append(
            "### turn %d%s -- %s" % (t["turn_index"], tag, t["timestamp"] or "UNKNOWN-TIMESTAMP")
        )
        lines.append("- tools_used: %s" % json.dumps(t["tools_used"]))
        if t["files_read"]:
            lines.append("- files_read: %s" % ", ".join(t["files_read"]))
        if t["files_written"]:
            lines.append("- files_written: %s" % ", ".join(t["files_written"]))
        if t["commands"]:
            lines.append("- commands:")
            for c in t["commands"]:
                lines.append("  - `%s`" % c["command"])
        lines.append("")

    if could_not_parse:
        lines.append("## WHAT I COULD NOT PARSE AND WHY")
        lines.append("")
        for item in could_not_parse:
            lines.append("- line %d: %s" % (item["line_no"], item["reason"]))
        lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jsonl", required=True, help="path to a session JSONL file")
    ap.add_argument("--out-json", help="path to write full JSON output")
    ap.add_argument("--out-md", help="path to write a markdown report")
    args = ap.parse_args()

    jsonl_path = Path(args.jsonl)
    if not jsonl_path.exists():
        print("ERROR: --jsonl not found: %s" % jsonl_path, file=sys.stderr)
        return 2

    turns, queued_commands, class_counts, could_not_parse, json_errors = extract_turns(jsonl_path)

    result = {
        "session_jsonl": str(jsonl_path),
        "record_class_counts": dict(class_counts),
        "turns": turns,
        "queued_commands": queued_commands,
        "could_not_parse": could_not_parse,
        "json_errors": json_errors,
    }

    if args.out_json:
        out_json_path = Path(args.out_json)
        out_json_path.parent.mkdir(parents=True, exist_ok=True)
        out_json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print("wrote %s" % out_json_path)

    if args.out_md:
        out_md_path = Path(args.out_md)
        out_md_path.parent.mkdir(parents=True, exist_ok=True)
        md = render_md(jsonl_path, turns, queued_commands, class_counts, could_not_parse, json_errors)
        out_md_path.write_text(md, encoding="utf-8")
        print("wrote %s" % out_md_path)

    if not args.out_json and not args.out_md:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    print(
        "turns=%d sidechain_turns=%d queued_commands=%d could_not_parse=%d json_errors=%d"
        % (
            sum(1 for t in turns if not t["sidechain"]),
            sum(1 for t in turns if t["sidechain"]),
            len(queued_commands),
            len(could_not_parse),
            len(json_errors),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
