import json, os, re

base = r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer"

with open(os.path.join(base, r"raw\Anthropic_zips\extracted-1779504602\conversations.json"), encoding="utf-8") as f:
    zip_convs = json.load(f)

zip_by_full = {c.get("uuid", ""): c for c in zip_convs}
zip_by_uuid6 = {c.get("uuid", "")[:6]: c for c in zip_convs}

raw_files = []
sessions_dir = os.path.join(base, "raw", "sessions")
for root, dirs, files in os.walk(sessions_dir):
    for fname in files:
        if fname.endswith(".md"):
            path = os.path.join(root, fname)
            with open(path, encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            uuid_m = re.search(r"chat_id:\s*([0-9a-f-]{36})", content)
            char_m = re.search(r"char_count:\s*(\d+)", content)
            upd_m = re.search(r"date_updated:\s*(\S+)", content)
            if uuid_m:
                raw_files.append({
                    "path": path,
                    "uuid": uuid_m.group(1),
                    "char_count": int(char_m.group(1)) if char_m else 0,
                    "date_updated": upd_m.group(1) if upd_m else "",
                })

updated = []
for rf in raw_files:
    uuid = rf["uuid"]
    zip_c = zip_by_full.get(uuid) or zip_by_uuid6.get(uuid[:6])
    if not zip_c:
        continue
    zip_msgs = zip_c.get("chat_messages", [])
    zip_chars = sum(
        len(p.get("text", "")) if isinstance(p, dict) else len(str(p))
        for m in zip_msgs
        for p in (m.get("content", []) if isinstance(m.get("content"), list) else [{"text": str(m.get("content", ""))}])
    )
    zip_updated = zip_c.get("updated_at", "")
    if zip_updated > rf["date_updated"] or zip_chars > rf["char_count"] * 1.05:
        short_path = rf["path"].replace(base + os.sep, "")
        delta = zip_chars - rf["char_count"]
        updated.append({
            "path": short_path,
            "uuid6": uuid[:6],
            "name": zip_c.get("name", "?"),
            "raw_chars": rf["char_count"],
            "zip_chars": zip_chars,
            "raw_updated": rf["date_updated"][:10],
            "zip_updated": zip_updated[:10],
            "zip_msgs": len(zip_msgs),
            "delta": delta,
        })

print(f"Raw session files found: {len(raw_files)}")
print(f"With updates in new zip: {len(updated)}")
print()
for u in sorted(updated, key=lambda x: x["zip_updated"], reverse=True):
    print(f"[{u['uuid6']}] {u['name']}")
    print(f"  raw: {u['raw_chars']:,}c / {u['raw_updated']}   zip: {u['zip_chars']:,}c / {u['zip_updated']} ({u['zip_msgs']} msgs) +{u['delta']:,}c")
    print(f"  {u['path']}")
    print()
