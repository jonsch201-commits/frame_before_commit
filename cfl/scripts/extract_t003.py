"""
extract_t003.py — Extract T-003 conversations from full history conversations.json
and convert to readable markdown for wiki ingestion.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
CONVS_FILE = REPO / "raw" / "exports" / "2026-05-12-full" / "conversations.json"
OUTPUT_DIR = REPO / "raw" / "exports" / "2026-05-09-full"  # same dir as CDP exports

T003 = {
    "1fe1190b-0ca0-4e78-91d2-4d69d5291224",
    "b04c8b74-55f2-483a-aadb-add0e12a000f",
    "b60686b6-d81f-43b1-aa24-0bf4bc6c887a",
}

def render_message(msg):
    role = msg.get("sender", "unknown")
    role_label = "**Human:**" if role == "human" else "**Claude:**"
    content = ""
    for block in msg.get("content", []):
        if isinstance(block, dict):
            if block.get("type") == "text":
                content += block.get("text", "")
            elif block.get("type") == "thinking":
                # Skip internal thinking blocks
                pass
        elif isinstance(block, str):
            content += block
    return f"{role_label}\n\n{content.strip()}"


def conv_to_markdown(conv):
    name = conv.get("name") or "(unnamed)"
    uuid = conv.get("uuid", "")
    created = conv.get("created_at", "")[:10]
    messages = conv.get("chat_messages", [])

    lines = [
        f"# {name}",
        f"",
        f"**UUID:** {uuid}",
        f"**Date:** {created}",
        f"",
        "---",
        "",
    ]
    for msg in messages:
        lines.append(render_message(msg))
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def slug_from_conv(conv):
    uuid = conv.get("uuid", "")
    uuid6 = uuid.replace("-", "")[:6]
    date = conv.get("created_at", "")[:10]
    name = conv.get("name") or "untitled"
    slug = name.lower()
    for ch in " /\\:\"'<>|?*,()[]{}":
        slug = slug.replace(ch, "-")
    slug = slug[:60].strip("-")
    return f"chat-{date}-{uuid6}-{slug}.md"


def main():
    print(f"Loading {CONVS_FILE} ...")
    with open(CONVS_FILE, encoding="utf-8") as f:
        convs = json.load(f)
    print(f"  {len(convs)} total conversations")

    found = [c for c in convs if c.get("uuid") in T003]
    print(f"  {len(found)} T-003 conversations found")

    if not found:
        print("ERROR: None of the T-003 UUIDs found in conversations.json")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    for conv in found:
        fname = slug_from_conv(conv)
        out_path = OUTPUT_DIR / fname
        md = conv_to_markdown(conv)
        msgs = conv.get("chat_messages", [])
        print(f"  Writing {fname}  ({len(msgs)} messages, {len(md)} chars)")
        out_path.write_text(md, encoding="utf-8")

    print("\nDone. Files written to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
