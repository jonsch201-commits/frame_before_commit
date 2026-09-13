#!/usr/bin/env python3
"""Harvest the largest assistant text block from a subagent JSONL."""

import json
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Harvest largest assistant report from subagent JSONL"
    )
    parser.add_argument("jsonl_path", help="Path to subagent JSONL file")
    parser.add_argument("--out", help="Output file path (optional)")
    args = parser.parse_args()

    jsonl_path = Path(args.jsonl_path)

    # Check if file exists
    if not jsonl_path.exists():
        sys.exit(2)

    # Collect all assistant text blocks
    blocks = []
    try:
        with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "assistant":
                        message = entry.get("message", {})
                        content = message.get("content", [])
                        if isinstance(content, list):
                            for block in content:
                                if block.get("type") == "text":
                                    text = block.get("text", "")
                                    if text:
                                        blocks.append(text)
                except json.JSONDecodeError:
                    continue
    except Exception:
        sys.exit(2)

    # Check if we found any blocks
    if not blocks:
        sys.exit(2)

    # Find the largest block
    largest_block = max(blocks, key=len)

    # Print header and block to stdout
    print(str(jsonl_path))
    print(f"Total assistant text blocks: {len(blocks)}")
    print(f"Selected block size: {len(largest_block)} chars")
    print(largest_block)

    # Write to output file if specified
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(largest_block)

    sys.exit(0)


if __name__ == "__main__":
    main()
