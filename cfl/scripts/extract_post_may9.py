"""
Extract specific post-May-9 conversations from conversations.json for screening.
"""
import json
from pathlib import Path

REPO = Path(__file__).parent.parent
CONVS_FILE = REPO / "raw" / "exports" / "2026-05-12-full" / "conversations.json"
OUTPUT_DIR = REPO / "raw" / "exports" / "2026-05-09-full"

TARGETS = {
    "44fbe5": None,
    "9fa7cd": None,
    "9f20bf": None,
    "9afe69": None,
    "ad34e5": None,
    "557aa5": None,
}

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

def render_message(msg):
    role = msg.get("sender", "unknown")
    role_label = "**Human:**" if role == "human" else "**Claude:**"
    content = ""
    for block in msg.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            content += block.get("text", "")
    return f"{role_label}\n\n{content.strip()}"

def conv_to_markdown(conv):
    name = conv.get("name") or "(unnamed)"
    uuid = conv.get("uuid", "")
    created = conv.get("created_at", "")[:10]
    messages = conv.get("chat_messages", [])
    lines = [f"# {name}", f"", f"**UUID:** {uuid}", f"**Date:** {created}", f"", "---", ""]
    for msg in messages:
        lines.append(render_message(msg))
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)

with open(CONVS_FILE, encoding="utf-8") as f:
    convs = json.load(f)

for conv in convs:
    uuid6 = conv.get("uuid", "").replace("-", "")[:6]
    if uuid6 in TARGETS:
        fname = slug_from_conv(conv)
        out_path = OUTPUT_DIR / fname
        if not out_path.exists():
            md = conv_to_markdown(conv)
            out_path.write_text(md, encoding="utf-8")
            msgs = conv.get("chat_messages", [])
            print(f"Extracted: {fname} ({len(msgs)} msgs, {len(md)} chars)")
        else:
            print(f"Already exists: {fname}")
