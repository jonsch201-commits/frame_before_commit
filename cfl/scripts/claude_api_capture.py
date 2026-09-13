#!/usr/bin/env python3
"""
claude_api_capture.py — Call the Anthropic Messages API with extended thinking
PRESERVED (display: summarized) and log the readable thinking + response to a file.

This is the durable "capture reasoning" tool that Claude Code cannot provide: CC
discards readable thinking (encrypted-in-signature; see
skills/session-order "Claude Code Reasoning Capture" + memory
cc-jsonl-thinking-signature-only). The Anthropic Messages API, by contrast, returns
readable *summarized* thinking when you ask for it — this script captures it.

It also supports REWIND-STYLE FBC counterfactual testing: because the API gives you
full control of the message history, you can fork a conversation from any prior
point and run alternative framings against the SAME context, then compare the
replies. That is the programmatic, capturable version of Claude Code's /rewind — the
counterfactual FBC instrument ("different words, different questions, same moment").

Credentials: reads ANTHROPIC_API_KEY from the environment ONLY. Never hardcode it,
never pass it on the command line.

Usage:
  # Single prompt — capture thinking + reply to a dated markdown log:
  ANTHROPIC_API_KEY=... python claude_api_capture.py --prompt "..." --out raw/api-capture

  # Fork from a prior conversation (rewind-style) and run one reframed prompt:
  python claude_api_capture.py --history convo.json --prompt "<reframed>" --tag frameB

  # FBC counterfactual: same history/context, several frames, compare the replies:
  python claude_api_capture.py --history convo.json --frames frames.json --compare

  # OFFLINE self-test of the parsing (no API call, no key needed):
  python claude_api_capture.py --parse-only tests/sample_response.json

--history / --frames JSON formats:
  history: a JSON list of Anthropic messages, e.g.
           [{"role":"user","content":"..."},{"role":"assistant","content":"..."}]
  frames:  a JSON list of {"tag": "...", "prompt": "..."} to fork the history with.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-opus-4-8"


# ---------------------------------------------------------------------------
# Request construction
# ---------------------------------------------------------------------------

def build_payload(messages, model, max_tokens, thinking_budget, display):
    """Build a Messages API payload with extended thinking preserved.

    NB (verify in the live test): the exact thinking config for the newest models
    (Opus 4.8 / Sonnet 5 / Fable 5) may differ — those use adaptive thinking and
    may not require `budget_tokens`, and default `display` to "omitted", so
    `display: "summarized"` MUST be set explicitly to get readable text back. The
    Claude 4 family defaults to "summarized". This tool sets it explicitly either way.
    If the API rejects `budget_tokens` for an adaptive model, drop it with
    --no-thinking-budget.
    """
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    thinking = {"type": "enabled"}
    if thinking_budget is not None:
        thinking["budget_tokens"] = thinking_budget
    if display:
        thinking["display"] = display  # "summarized" → readable thinking in the response
    payload["thinking"] = thinking
    return payload


def call_api(payload):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("ERROR: ANTHROPIC_API_KEY is not set. This tool reads the key from the "
                 "environment only and never stores it. Set it and re-run.")
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, method="POST")
    req.add_header("x-api-key", key)
    req.add_header("anthropic-version", API_VERSION)
    req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit(f"API HTTP {e.code}: {body[:800]}")
    except urllib.error.URLError as e:
        sys.exit(f"API connection error: {e}")


# ---------------------------------------------------------------------------
# Response parsing (offline-testable — this is the part we can verify without a key)
# ---------------------------------------------------------------------------

def extract_blocks(response):
    """Return (thinking_blocks, visible_text, tool_names, usage) from a response.

    thinking_blocks: list of {"text": <readable summary or "">, "signature_len": int,
                              "has_text": bool}
    """
    content = response.get("content", []) or []
    thinking_blocks = []
    texts = []
    tools = []
    for b in content:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "thinking":
            txt = (b.get("thinking") or "").strip()
            thinking_blocks.append({
                "text": txt,
                "signature_len": len(b.get("signature") or ""),
                "has_text": bool(txt),
            })
        elif t == "redacted_thinking":
            thinking_blocks.append({"text": "", "signature_len": len(b.get("data") or ""),
                                    "has_text": False, "redacted": True})
        elif t == "text":
            s = (b.get("text") or "").strip()
            if s:
                texts.append(s)
        elif t == "tool_use":
            tools.append(b.get("name", "unknown_tool"))
    return thinking_blocks, "\n\n".join(texts), tools, response.get("usage", {})


def render_markdown(prompt, thinking_blocks, visible_text, model, tag, usage):
    """Render a capture log: readable thinking as <details>, then the reply."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    n_text = sum(1 for b in thinking_blocks if b.get("has_text"))
    n_total = len(thinking_blocks)
    if n_total == 0:
        status = "none"
    elif n_text == 0:
        status = f"signature-only ({n_total} blocks — set display:summarized / check model)"
    else:
        status = f"preserved ({n_text} of {n_total} blocks)"

    fm = [
        "---",
        "source_type: api-capture",
        f"model: {model}",
        f"captured: {now}",
        f"thinking_blocks: {status}",
        f"tag: {tag or 'none'}",
        f"usage: {json.dumps(usage)}",
        "---",
        "",
        f"## Prompt{f' [{tag}]' if tag else ''}",
        "",
        prompt,
        "",
    ]
    body = ["## Reply", ""]
    for b in thinking_blocks:
        if b.get("has_text"):
            body.append("<details>\n<summary>Extended thinking</summary>\n\n"
                        f"{b['text']}\n\n</details>\n")
    body.append(visible_text or "*(no visible text)*")
    return "\n".join(fm) + "\n".join(body) + "\n"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def load_history(path):
    if not path:
        return []
    msgs = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(msgs, list):
        sys.exit("ERROR: --history must be a JSON list of {role, content} messages.")
    return msgs


def one_call(prompt, args, tag=None):
    messages = load_history(args.history) + [{"role": "user", "content": prompt}]
    budget = None if args.no_thinking_budget else args.thinking_budget
    payload = build_payload(messages, args.model, args.max_tokens, budget, args.display)
    response = call_api(payload)
    thinking, text, tools, usage = extract_blocks(response)
    md = render_markdown(prompt, thinking, text, args.model, tag, usage)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    fname = f"api-capture-{stamp}{('-' + tag) if tag else ''}.md"
    (out_dir / fname).write_text(md, encoding="utf-8")
    n_text = sum(1 for b in thinking if b.get("has_text"))
    print(f"WROTE {out_dir / fname}  (thinking blocks w/ text: {n_text}/{len(thinking)}, "
          f"reply {len(text):,} chars)")
    return md


def cmd_run(args):
    if args.compare and args.frames:
        frames = json.loads(Path(args.frames).read_text(encoding="utf-8"))
        for fr in frames:
            one_call(fr["prompt"], args, tag=fr.get("tag"))
        print("\nCompare pass complete — each frame ran against the same history/context "
              "(rewind-style FBC counterfactual). Diff the reply files to score frame-sensitivity.")
    else:
        if not args.prompt:
            sys.exit("ERROR: provide --prompt (or --frames + --compare).")
        one_call(args.prompt, args, tag=args.tag)


def cmd_parse_only(args):
    """Offline test: parse a saved API response JSON, print the extraction. No key."""
    response = json.loads(Path(args.parse_only).read_text(encoding="utf-8"))
    thinking, text, tools, usage = extract_blocks(response)
    n_text = sum(1 for b in thinking if b.get("has_text"))
    print(f"thinking blocks: {len(thinking)} (with text: {n_text})")
    for i, b in enumerate(thinking):
        preview = b["text"][:80].replace("\n", " ")
        print(f"  [{i}] has_text={b['has_text']} sig_len={b['signature_len']} :: {preview}")
    print(f"visible text: {len(text)} chars :: {text[:100]!r}")
    print(f"tools: {tools}")
    print(f"usage: {usage}")
    print("\n--- rendered markdown (first 600 chars) ---")
    print(render_markdown("(sample prompt)", thinking, text, "sample-model", "test", usage)[:600])


def main():
    p = argparse.ArgumentParser(description="Capture Anthropic API thinking + reply to a file.")
    p.add_argument("--prompt", help="The user prompt for a single call")
    p.add_argument("--history", help="JSON file: prior messages to fork from (rewind-style)")
    p.add_argument("--frames", help="JSON file: list of {tag, prompt} to run against the history")
    p.add_argument("--compare", action="store_true", help="Run all --frames (FBC counterfactual)")
    p.add_argument("--tag", help="Label for a single-call capture")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--max-tokens", type=int, default=8192, dest="max_tokens")
    p.add_argument("--thinking-budget", type=int, default=4096, dest="thinking_budget",
                   help="budget_tokens for extended thinking (Claude 4 family). Ignored with "
                        "--no-thinking-budget (newest adaptive-thinking models).")
    p.add_argument("--no-thinking-budget", action="store_true", dest="no_thinking_budget",
                   help="Omit budget_tokens (for adaptive-thinking models that reject it)")
    p.add_argument("--display", default="summarized",
                   help='thinking.display: "summarized" (readable, default) or "omitted"')
    p.add_argument("--out", default="raw/api-capture", help="Output dir (default: raw/api-capture)")
    p.add_argument("--parse-only", metavar="RESPONSE_JSON",
                   help="Offline: parse a saved API response and print extraction (no API call)")
    args = p.parse_args()

    if args.parse_only:
        cmd_parse_only(args)
    else:
        cmd_run(args)


if __name__ == "__main__":
    main()
