#!/usr/bin/env python3
"""mint_window.py — CFL committed window emitter, format record-pipeline-window/v1.1.

Replaces the seven ad-hoc RP-2 window parsers (v0.1..v0.4.1), each of which
dropped a different content class. Stdlib only.

CLI:
    python mint_window.py <session-jsonl> <lo-utc-iso> <hi-utc-iso> --out <file> [--receipt <basename>]

Window semantics: (lo, hi] at second granularity — the entire lo second is
excluded, the entire hi second is included, so adjacent windows sharing a
boundary never double-count an entry.

v1.1 (RP-27): Jon's mid-turn messages exist in the session JSONL ONLY as
`{"type": "attachment", "attachment": {"type": "queued_command", ...}}`
entries — v1 rendered only etype user/assistant and silently dropped every
one of them. v1.1 renders queued_command entries.

Who typed it is read from `attachment.commandMode`, not inferred: "prompt"
is Jon-typed (human), any other value (e.g. "task-notification") is the
harness talking to itself (machine). When commandMode is absent (older
capture, or a shape nobody has seen yet), fall back to a prefix check on
the rendered text — a prompt starting with one of MACHINE_PREFIXES is
machine-shaped even with no commandMode to say so.

Nothing is filtered out of the render — human and machine rows both render,
under distinct headings, so a later reader can re-derive the ratio from the
file alone. Only human rows count toward queued_human / "Jon's words".
`prompt` may be a plain string or a list of content blocks; both are
handled by text_of().

RP-27b (2026-09-02): the same commandMode rule is now also in the corpus
converter, skills/chat-exporter/scripts/convert-claude-code.py (queued_command
-> `## Human (queued, commandMode=prompt)` / `## Machine (queued, ...)`, plus
`queue-operation` rows as `## Queue-operation`). Acceptance test:
scripts/tests/selftest_convert_queued.py. If the rule changes here, change it
there too — the minted window and the raw .md must agree on who typed what.
"""
import argparse
import json
import os
import sys

STUB_LEN = 80

# Prefixes that mark a queued_command's text as machine-generated when
# commandMode itself is missing. Never used to override an actual commandMode.
MACHINE_PREFIXES = (
    "<local-command", "<command-name>", "<system-reminder",
    "<task-notification", "[Request interrupted",
)


def bound_key(iso, side):
    """Second-granularity comparison key. lo/hi given without fractional part."""
    if "." not in iso:
        iso = iso.rstrip("Z") + ".999999Z"
    return iso


def hms(ts):
    """'2026-08-31T18:30:01.123Z' -> '18:30:01Z'"""
    return ts[11:19] + "Z"


def text_of(content):
    """Extract concatenated text from a string or a content-block list."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text" and (b.get("text") or "").strip():
                parts.append(b["text"])
            elif isinstance(b, str) and b.strip():
                parts.append(b)
        return "\n\n".join(parts)
    return ""


def stub(s):
    """One-line first-80-chars stub; ellipsis only when truncated."""
    s = " ".join(s.split())
    return s[:STUB_LEN] + "…" if len(s) > STUB_LEN else s


def classify_queued(att):
    """(class, mode, text) for one queued_command attachment.

    class is "human" or "machine". mode is attachment.commandMode verbatim
    (may be None). commandMode is authoritative when present; the prefix
    fallback only fires when it is missing.
    """
    mode = att.get("commandMode")
    txt = text_of(att.get("prompt"))
    if mode == "prompt":
        return "human", mode, txt
    if mode:
        return "machine", mode, txt
    stripped = txt.lstrip()
    if any(stripped.startswith(p) for p in MACHINE_PREFIXES):
        return "machine", mode, txt
    return "human", mode, txt


def mint(jsonl_path, lo, hi, receipt=None):
    lo_key = bound_key(lo, "lo")
    hi_key = bound_key(hi, "hi")
    session = os.path.splitext(os.path.basename(jsonl_path))[0]
    counts = {
        "user_text_turns": 0, "assistant_text_blocks": 0, "tool_calls": 0,
        "tool_results": 0, "thinking_blocks": 0, "askuser_results": 0,
        "total_messages": 0, "queued_human": 0, "queued_machine": 0,
    }
    queued_by_mode = {}
    id2name = {}
    body = []

    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = e.get("timestamp") or ""
            if not (ts > lo_key and ts <= hi_key):
                continue
            counts["total_messages"] += 1
            etype = e.get("type")
            content = (e.get("message") or {}).get("content")
            t = hms(ts)

            if etype == "user":
                txt = text_of(content)
                if txt.strip():
                    counts["user_text_turns"] += 1
                    body.append("## Human [%s]\n\n%s\n" % (t, txt))
                if isinstance(content, list):
                    for b in content:
                        if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                            continue
                        name = id2name.get(b.get("tool_use_id"), "unknown")
                        rtxt = text_of(b.get("content"))
                        if name == "AskUserQuestion":
                            counts["askuser_results"] += 1
                            body.append("## Human (via AskUserQuestion) [%s]\n\n%s\n" % (t, rtxt))
                        else:
                            counts["tool_results"] += 1
                            body.append("- RESULT %s: %s\n" % (name, stub(rtxt)))

            elif etype == "assistant" and isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    btype = b.get("type")
                    if btype == "text" and (b.get("text") or "").strip():
                        counts["assistant_text_blocks"] += 1
                        body.append("## Assistant [%s]\n\n%s\n" % (t, b["text"]))
                    elif btype == "tool_use":
                        counts["tool_calls"] += 1
                        id2name[b.get("id")] = b.get("name", "unknown")
                        body.append("- TOOL %s: %s\n" % (
                            b.get("name", "unknown"),
                            stub(json.dumps(b.get("input", {}), ensure_ascii=False))))
                    elif btype == "thinking":
                        counts["thinking_blocks"] += 1

            elif etype == "attachment" and (e.get("attachment") or {}).get("type") == "queued_command":
                att = e["attachment"]
                cls, mode, txt = classify_queued(att)
                mode_key = mode if mode else "(none)"
                queued_by_mode[mode_key] = queued_by_mode.get(mode_key, 0) + 1
                if not txt.strip():
                    continue
                if cls == "human":
                    counts["queued_human"] += 1
                    body.append("## Human (queued, commandMode=%s) [%s]\n\n%s\n" % (mode_key, t, txt))
                else:
                    counts["queued_machine"] += 1
                    body.append("## Machine (queued, commandMode=%s) [%s]\n\n%s\n" % (mode_key, t, txt))

    fm = ["---",
          "format: record-pipeline-window/v1.1",
          "session: %s" % session,
          'window_utc: "(%s → %s]"' % (lo, hi)]
    if receipt:
        fm.append("receipt: %s" % receipt)
    for k in ("user_text_turns", "assistant_text_blocks", "tool_calls",
              "tool_results", "thinking_blocks", "askuser_results",
              "total_messages", "queued_human", "queued_machine"):
        fm.append("%s: %d" % (k, counts[k]))
    fm.append("queued_by_mode: {%s}" % ", ".join(
        "%s: %d" % (k, queued_by_mode[k]) for k in sorted(queued_by_mode)))
    fm.append("generated_by: mint_window.py v1.1")
    fm.append("---")
    return "\n".join(fm) + "\n\n" + "\n".join(body), counts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("jsonl")
    ap.add_argument("lo")
    ap.add_argument("hi")
    ap.add_argument("--out", required=True)
    ap.add_argument("--receipt")
    args = ap.parse_args(argv)
    doc, counts = mint(args.jsonl, args.lo, args.hi, args.receipt)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    print("WROTE %s  %s" % (args.out,
          "  ".join("%s=%d" % kv for kv in sorted(counts.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
