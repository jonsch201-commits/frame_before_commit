#!/usr/bin/env python3
"""
extract_jsonl_metadata.py — READ-ONLY per-turn metadata index for ONE Claude Code JSONL.

Prototype for the raw-metadata-availability study (exchange/raw-metadata-availability-2026-07-24.md).
Given a single Claude Code session JSONL (from ~/.claude/projects/<slug>/<uuid>.jsonl),
emit a structured per-turn index capturing the four dimensions Jon asked about plus two more:

  timestamp        — per-record UTC (record-level `timestamp`)
  model            — assistant records only (`message.model`)
  role / type      — record `type` (user | assistant | system | ...) and message role
  isSidechain      — subagent trace flag (record-level `isSidechain`)
  compaction       — records the compaction boundary (`isCompactSummary: true` user record)
  reads            — files this turn READ, reconstructed from tool_use (Read/Grep/Glob)
                     inputs AND their paired toolUseResult (file.filePath / filenames)

STRICTLY READ-ONLY. Opens the JSONL for reading; never writes to it or anywhere under raw/.
Output goes to stdout (default) or a --json path the caller chooses (intended: exchange/).

Usage:
  python extract_jsonl_metadata.py <session.jsonl>                # human table + summary to stdout
  python extract_jsonl_metadata.py <session.jsonl> --json out.json   # structured JSON to a file
  python extract_jsonl_metadata.py <session.jsonl> --limit 40      # cap table rows shown
  python extract_jsonl_metadata.py --self-test                    # tiny in-memory schema check

Schema grounding (verified against a real CFL session JSONL, 2026-07-24):
  - assistant record: top-level `timestamp`, `message.model` (e.g. "claude-opus-4-8"),
    `message.content[]` blocks of type thinking|text|tool_use. Thinking is signature-only
    (encrypted) in v2.1.72+ CC JSONLs — `thinking` string is empty, `signature` is populated.
  - tool_use block: {type:"tool_use", name:"Read", id, input:{file_path:...}}
    Grep/Glob carry input.pattern (+ optional path/glob).
  - tool_result lands in the NEXT `user` record; the sibling top-level `toolUseResult`
    is the structured payload: Read -> {file:{filePath,numLines,...}},
    Glob/Grep(files) -> {filenames:[...], numFiles, mode}.
  - compaction boundary: a `user` record with top-level `isCompactSummary: true` whose
    message content begins "This session is being continued from a previous conversation..."
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

READ_TOOLS = {"Read", "Grep", "Glob"}


def _iter_records(path):
    """Yield (line_index, parsed_record) for each non-blank JSONL line. Read-only."""
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                yield i, json.loads(line)
            except json.JSONDecodeError:
                # A truncated final line is possible on a live session; skip, don't crash.
                continue


def _content_blocks(rec):
    msg = rec.get("message")
    if isinstance(msg, dict):
        c = msg.get("content")
        if isinstance(c, list):
            return c
    return []


def _reads_from_tool_use(block):
    """Return a read-descriptor dict for a Read/Grep/Glob tool_use block, else None."""
    if block.get("type") != "tool_use" or block.get("name") not in READ_TOOLS:
        return None
    inp = block.get("input") or {}
    name = block["name"]
    if name == "Read":
        target = inp.get("file_path")
    else:  # Grep / Glob
        target = inp.get("path") or inp.get("glob") or inp.get("pattern")
    return {
        "tool": name,
        "tool_use_id": block.get("id"),
        "target": target,
        "pattern": inp.get("pattern"),  # None for Read
    }


def _reads_from_result(tur):
    """Extract concrete file paths a toolUseResult confirms were read. Read-only."""
    out = []
    if not isinstance(tur, dict):
        return out
    f = tur.get("file")
    if isinstance(f, dict) and f.get("filePath"):
        out.append({"filePath": f["filePath"], "numLines": f.get("numLines")})
    fns = tur.get("filenames")
    if isinstance(fns, list):
        for p in fns:
            out.append({"filePath": p, "numLines": None})
    return out


def build_index(path):
    """Build the per-turn metadata index + a corpus-level summary for one JSONL."""
    records = list(_iter_records(path))

    # First pass: map tool_use_id -> confirmed reads (result lands in the NEXT user record).
    result_reads_by_id = {}
    for _, rec in records:
        for blk in _content_blocks(rec):
            if isinstance(blk, dict) and blk.get("type") == "tool_result":
                tur = rec.get("toolUseResult")
                reads = _reads_from_result(tur)
                if reads:
                    result_reads_by_id[blk.get("tool_use_id")] = reads

    rows = []
    models = Counter()
    types = Counter()
    n_sidechain = 0
    n_compaction = 0
    turn = 0

    for line_idx, rec in records:
        rtype = rec.get("type")
        types[rtype] += 1
        if rec.get("isSidechain"):
            n_sidechain += 1

        # We index the substantive conversational turns (user + assistant) plus any
        # compaction-boundary marker. Bookkeeping record types (pr-link, mode, etc.)
        # are counted in the summary but not emitted as turn rows.
        is_compaction = bool(rec.get("isCompactSummary"))
        if is_compaction:
            n_compaction += 1
        if rtype not in ("user", "assistant") and not is_compaction:
            continue

        msg = rec.get("message") or {}
        model = msg.get("model") if rtype == "assistant" else None
        if model:
            models[model] += 1

        # Reads for this turn: from tool_use blocks (intent) enriched by the paired
        # result (confirmation). A turn's reads come from tool_use blocks it CONTAINS.
        reads = []
        block_types = []
        for blk in _content_blocks(rec):
            if not isinstance(blk, dict):
                continue
            block_types.append(blk.get("type"))
            ru = _reads_from_tool_use(blk)
            if ru:
                confirmed = result_reads_by_id.get(ru["tool_use_id"])
                ru["confirmed_paths"] = [c["filePath"] for c in confirmed] if confirmed else []
                reads.append(ru)

        turn += 1
        rows.append({
            "turn": turn,
            "line": line_idx,
            "timestamp": rec.get("timestamp"),
            "type": rtype,
            "role": msg.get("role"),
            "model": model,
            "isSidechain": bool(rec.get("isSidechain")),
            "compaction_boundary": is_compaction,
            "block_types": block_types,
            "reads": reads,
        })

    summary = {
        "source_jsonl": path,
        "total_records": len(records),
        "record_type_counts": dict(types),
        "turn_rows": len(rows),
        "models": dict(models),
        "sidechain_records": n_sidechain,
        "compaction_boundaries": n_compaction,
        "turns_with_reads": sum(1 for r in rows if r["reads"]),
        "distinct_files_read": sorted({
            p for r in rows for ru in r["reads"] for p in (ru.get("confirmed_paths") or ([ru["target"]] if ru["target"] else []))
        }),
    }
    return summary, rows


def _fmt_reads(reads, maxn=3):
    if not reads:
        return ""
    parts = []
    for ru in reads[:maxn]:
        tgt = ru.get("confirmed_paths") or ([ru["target"]] if ru.get("target") else [])
        short = ", ".join(p.split("\\")[-1].split("/")[-1] for p in tgt) if tgt else (ru.get("pattern") or "?")
        parts.append(f"{ru['tool']}:{short}")
    if len(reads) > maxn:
        parts.append(f"(+{len(reads) - maxn})")
    return " | ".join(parts)


def print_table(summary, rows, limit=None):
    print("=== SUMMARY ===")
    for k, v in summary.items():
        if k == "distinct_files_read":
            print(f"  {k}: {len(v)} distinct")
        elif k == "record_type_counts":
            print(f"  {k}: {v}")
        else:
            print(f"  {k}: {v}")
    print()
    print("=== PER-TURN INDEX (first {} rows) ===".format(limit or len(rows)))
    hdr = f"{'#':>4} {'line':>5} {'timestamp':<24} {'type':<9} {'model':<16} {'sc':<3} {'cmp':<4} reads"
    print(hdr)
    print("-" * len(hdr))
    shown = rows if limit is None else rows[:limit]
    for r in shown:
        print(f"{r['turn']:>4} {r['line']:>5} {str(r['timestamp']):<24} {str(r['type']):<9} "
              f"{str(r['model'] or ''):<16} {('Y' if r['isSidechain'] else ''):<3} "
              f"{('BND' if r['compaction_boundary'] else ''):<4} {_fmt_reads(r['reads'])}")


def self_test():
    """Tiny in-memory schema check — no disk I/O, proves the extraction logic."""
    import tempfile, os
    fixture = [
        {"type": "user", "timestamp": "2026-07-22T01:00:00.000Z",
         "message": {"role": "user", "content": "hello"}},
        {"type": "assistant", "timestamp": "2026-07-22T01:00:01.000Z", "isSidechain": False,
         "message": {"role": "assistant", "model": "claude-opus-4-8",
                     "content": [{"type": "tool_use", "name": "Read", "id": "tu_1",
                                  "input": {"file_path": "G:\\proj\\wiki\\index.md"}}]}},
        {"type": "user", "timestamp": "2026-07-22T01:00:02.000Z",
         "message": {"role": "user", "content": [
             {"type": "tool_result", "tool_use_id": "tu_1", "content": "..."}]},
         "toolUseResult": {"type": "text", "file": {"filePath": "G:\\proj\\wiki\\index.md", "numLines": 356}}},
        {"type": "user", "timestamp": "2026-07-22T13:11:13.415Z", "isCompactSummary": True,
         "message": {"role": "user", "content": "This session is being continued..."}},
        {"type": "pr-link"},  # bookkeeping record — counted, not a turn
    ]
    fd, tmp = tempfile.mkstemp(suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for r in fixture:
                fh.write(json.dumps(r) + "\n")
        summary, rows = build_index(tmp)
        assert summary["models"] == {"claude-opus-4-8": 1}, summary["models"]
        assert summary["compaction_boundaries"] == 1, summary
        assert summary["record_type_counts"].get("pr-link") == 1, summary
        assert summary["turns_with_reads"] == 1, summary
        # the Read turn must resolve the confirmed path from the paired result
        read_turn = next(r for r in rows if r["reads"])
        assert read_turn["reads"][0]["confirmed_paths"] == ["G:\\proj\\wiki\\index.md"], read_turn
        assert any(r["compaction_boundary"] for r in rows)
        print("self-test OK — models, compaction boundary, read-pairing, bookkeeping all detected")
    finally:
        os.remove(tmp)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only per-turn metadata index for ONE Claude Code JSONL.")
    ap.add_argument("jsonl", nargs="?", help="path to a single Claude Code session JSONL")
    ap.add_argument("--json", dest="json_out", help="write structured JSON to this path (else table to stdout)")
    ap.add_argument("--limit", type=int, default=None, help="cap table rows printed")
    ap.add_argument("--self-test", action="store_true", help="run in-memory schema check and exit")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return 0
    if not args.jsonl:
        ap.error("provide a JSONL path (or --self-test)")

    summary, rows = build_index(args.jsonl)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "rows": rows}, fh, indent=2)
        print(f"wrote {args.json_out}: {summary['turn_rows']} turn rows, "
              f"{len(summary['distinct_files_read'])} distinct files read")
    else:
        print_table(summary, rows, limit=args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
