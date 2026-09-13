"""
compare_zips.py
---------------
Compare two Anthropic claude.ai export directories and extract new or updated
conversations to markdown files.

Delegates rendering to skills/chat-exporter/scripts/convert-export.py so that
output format matches all other session exports in raw/transcripts/ (raw/sessions/
retired, 2026-07-28 L1 move).

Usage:
  python scripts/compare_zips.py [--old PATH] [--new PATH] [--dry-run]

Options:
  --old PATH   Older extracted zip dir (default: auto-detect 2nd-newest)
  --new PATH   Newer extracted zip dir (default: auto-detect newest)
  --dry-run    Print delta UUIDs; do not render or write files

Auto-detection:
  Scans raw/Anthropic_zips/extracted-*/ dirs sorted by numeric timestamp
  embedded in the directory name (e.g. extracted-1781576479).

Output locations:
  {new_dir}/new-sessions/      -- conversations in new but absent from old
  {new_dir}/updated-sessions/  -- conversations in both where new has more
                                   messages or a later updated_at timestamp

Both output dirs are created only if they contain at least one result.

Exit codes: 0 = success, 1 = fatal error.
"""

import argparse
import io
import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO = Path(__file__).parent.parent
ZIPS_DIR = REPO / "raw" / "Anthropic_zips"
CONVERT_SCRIPT = REPO / "skills" / "chat-exporter" / "scripts" / "convert-export.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_extracted_dirs():
    """Return extracted-* dirs sorted newest-first by embedded timestamp."""
    dirs = []
    for d in ZIPS_DIR.iterdir():
        if d.is_dir():
            m = re.match(r"extracted-(\d+)$", d.name)
            if m:
                dirs.append((int(m.group(1)), d))
    dirs.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in dirs]


def load_convs(extracted_dir):
    """Load conversations.json from an extracted dir; return {uuid: conv}."""
    p = Path(extracted_dir) / "conversations.json"
    if not p.exists():
        sys.exit(f"ERROR: conversations.json not found in {extracted_dir}")
    data = json.loads(p.read_text(encoding="utf-8"))
    return {c["uuid"]: c for c in data}


def delta(old_convs, new_convs):
    """Return (new_uuids, updated_uuids) as lists."""
    new_uuids = []
    updated_uuids = []
    for uuid, conv in new_convs.items():
        if uuid not in old_convs:
            new_uuids.append(uuid)
        else:
            old = old_convs[uuid]
            if (conv.get("updated_at", "") > old.get("updated_at", "") or
                    len(conv.get("chat_messages", [])) > len(old.get("chat_messages", []))):
                updated_uuids.append(uuid)
    return new_uuids, updated_uuids


def conv_summary(uuid, convs):
    c = convs[uuid]
    uuid6 = uuid.replace("-", "")[:6]
    name = c.get("name") or "(unnamed)"
    created = c.get("created_at", "")[:10]
    updated = c.get("updated_at", "")[:10]
    msgs = len(c.get("chat_messages", []))
    return f"  [{uuid6}] {name} — created {created}, updated {updated}, {msgs} msgs"


def run_convert(extracted_dir, out_dir, uuids, dry_run):
    """Call convert-export.py --run --out OUT --ids UUID,... for the given UUIDs."""
    if not uuids:
        return
    if dry_run:
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    ids_arg = ",".join(uuids)
    cmd = [
        sys.executable, str(CONVERT_SCRIPT),
        str(extracted_dir),
        "--run",
        "--out", str(out_dir),
        "--ids", ids_arg,
        "--force",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode != 0:
        print(f"WARNING: convert-export.py exited {result.returncode}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--old", metavar="PATH",
                        help="Older extracted zip dir (auto-detected if omitted)")
    parser.add_argument("--new", metavar="PATH",
                        help="Newer extracted zip dir (auto-detected if omitted)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print delta; do not write files")
    args = parser.parse_args()

    # Resolve dirs
    if args.old and args.new:
        old_dir = Path(args.old)
        new_dir = Path(args.new)
    else:
        extracted = find_extracted_dirs()
        if len(extracted) < 2:
            sys.exit("ERROR: need at least 2 extracted-* dirs; use --old and --new to specify")
        new_dir = extracted[0]
        old_dir = extracted[1]
        if args.old:
            old_dir = Path(args.old)
        if args.new:
            new_dir = Path(args.new)

    print(f"Old dir: {old_dir.name}")
    print(f"New dir: {new_dir.name}")
    print()

    # Load and compare
    old_convs = load_convs(old_dir)
    new_convs = load_convs(new_dir)
    print(f"Old: {len(old_convs)} conversations")
    print(f"New: {len(new_convs)} conversations")
    print()

    new_uuids, updated_uuids = delta(old_convs, new_convs)

    # Report
    print(f"NEW ({len(new_uuids)}):")
    for uuid in sorted(new_uuids, key=lambda u: new_convs[u].get("created_at", "")):
        print(conv_summary(uuid, new_convs))

    print(f"\nUPDATED ({len(updated_uuids)}):")
    for uuid in sorted(updated_uuids,
                       key=lambda u: new_convs[u].get("updated_at", ""), reverse=True):
        old_msgs = len(old_convs[uuid].get("chat_messages", []))
        new_msgs = len(new_convs[uuid].get("chat_messages", []))
        base = conv_summary(uuid, new_convs)
        print(f"{base}  (msgs {old_msgs}→{new_msgs})")

    if args.dry_run:
        print("\n[dry-run] No files written.")
        return

    if not new_uuids and not updated_uuids:
        print("\nNo delta — nothing to render.")
        return

    # Render via convert-export.py
    if new_uuids:
        out = new_dir / "new-sessions"
        print(f"\nRendering {len(new_uuids)} new sessions → {out.name}/")
        run_convert(new_dir, out, new_uuids, dry_run=False)

    if updated_uuids:
        out = new_dir / "updated-sessions"
        print(f"Rendering {len(updated_uuids)} updated sessions → {out.name}/")
        run_convert(new_dir, out, updated_uuids, dry_run=False)

    print("\nDone.")
    print(f"Review output in: {new_dir}")


if __name__ == "__main__":
    main()
