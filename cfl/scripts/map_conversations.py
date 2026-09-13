"""
map_conversations.py
--------------------
Produces an authoritative, project-categorized map of all known conversations,
then reorganizes raw/exports/2026-05-09-full/ into project subfolders and
writes a manifest usable by downstream intake/wiki operations.

Data sources (in priority order):
  1. raw/exports/project-map.json       — live API pull; has real project_uuid
  2. intake/Anthropic download .../conversations.json — static export; has dates/summaries
  3. raw/exports/2026-05-09-full/       — CDP-exported markdown files

Outputs:
  scripts/output/conversation_map.md       — human-readable map by project
  scripts/output/conversation_manifest.json — machine-readable; uuid -> project, file path
  raw/exports/2026-05-09-full/by-project/  — symlink-free copy organized by project

Run:
  python scripts/map_conversations.py [--dry-run]

Flags:
  --dry-run   Print what would happen; write no files to raw/exports/
"""

import io
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DRY_RUN = "--dry-run" in sys.argv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO = Path(__file__).parent.parent
PROJECT_MAP_FILE  = REPO / "raw" / "exports" / "project-map.json"
EXPORT_DIR        = REPO / "raw" / "exports" / "2026-05-09-full"
BY_PROJECT_DIR    = REPO / "raw" / "exports" / "2026-05-09-full" / "by-project"
CONVERSATIONS_FILE = REPO / "raw" / "exports" / "2026-05-12-full" / "conversations.json"
OUTPUT_DIR        = REPO / "scripts" / "output"
MAP_OUTPUT        = OUTPUT_DIR / "conversation_map.md"
MANIFEST_OUTPUT   = OUTPUT_DIR / "conversation_manifest.json"

OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Project short names (for folder names)
# ---------------------------------------------------------------------------

PROJECT_SLUGS = {
    "019d8279-90ca-7468-8fb1-37534b6daefc": "fl",
    "019cc2fb-0284-77e5-ba27-1a880954817e": "personal",
    "019cc2fc-35c1-72ac-8ca8-7ce60433bc01": "pro",
    "019ca63c-3818-7510-aad8-5db3c583bd40": "how-to-use-claude",
    None: "unassigned",
}

PROJECT_DISPLAY = {
    "019d8279-90ca-7468-8fb1-37534b6daefc": "Claude Foundational Layer",
    "019cc2fb-0284-77e5-ba27-1a880954817e": "Personal Life Questions",
    "019cc2fc-35c1-72ac-8ca8-7ce60433bc01": "Professional Life Questions",
    "019ca63c-3818-7510-aad8-5db3c583bd40": "How to use Claude",
    None: "Unassigned (no project)",
}

PROJECT_ORDER = [
    "019d8279-90ca-7468-8fb1-37534b6daefc",
    "019ca63c-3818-7510-aad8-5db3c583bd40",
    "019cc2fc-35c1-72ac-8ca8-7ce60433bc01",
    "019cc2fb-0284-77e5-ba27-1a880954817e",
    None,
]

# ---------------------------------------------------------------------------
# Load sources
# ---------------------------------------------------------------------------

def load_project_map():
    """Load raw/exports/project-map.json — keyed by full UUID."""
    with open(PROJECT_MAP_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_conversations():
    """Load Anthropic export conversations.json — list of dicts with uuid, name, dates."""
    if not CONVERSATIONS_FILE.exists():
        print("  [warn] conversations.json not found — dates will be missing")
        return {}
    with open(CONVERSATIONS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return {c["uuid"]: c for c in data}


def find_export_file(uuid6: str) -> Path | None:
    """Find the markdown file in 2026-05-09-full/ matching a 6-char UUID prefix."""
    if not EXPORT_DIR.exists():
        return None
    matches = [f for f in EXPORT_DIR.iterdir()
               if f.is_file() and f.suffix == ".md" and uuid6 in f.name]
    return matches[0] if len(matches) == 1 else None


# ---------------------------------------------------------------------------
# Build unified record set
# ---------------------------------------------------------------------------

def build_records(project_map: dict, conv_lookup: dict) -> list[dict]:
    """
    Merge project-map (authoritative project assignment) with conversations.json
    (authoritative for date and summary).

    Returns a list of dicts:
      uuid, uuid6, name, project_uuid, project_name, project_slug,
      date, export_file (Path or None)
    """
    records = []
    seen = set()

    # Start with project-map entries (authoritative project data)
    for full_uuid, pm in project_map.items():
        uuid6 = full_uuid.replace("-", "")[:6]
        conv = conv_lookup.get(full_uuid, {})
        date_str = conv.get("created_at", "")[:10] if conv else ""
        p_uuid = pm.get("project_uuid")

        records.append({
            "uuid":         full_uuid,
            "uuid6":        uuid6,
            "name":         pm.get("conv_name") or conv.get("name") or "(unnamed)",
            "project_uuid": p_uuid,
            "project_name": pm.get("project_name") or PROJECT_DISPLAY.get(p_uuid, "Unknown"),
            "project_slug": PROJECT_SLUGS.get(p_uuid, "unassigned"),
            "date":         date_str,
            "export_file":  find_export_file(uuid6),
            "source":       "project-map",
        })
        seen.add(full_uuid)

    # Add conversations only in conversations.json (not in project-map)
    for full_uuid, conv in conv_lookup.items():
        if full_uuid in seen:
            continue
        uuid6 = full_uuid.replace("-", "")[:6]
        records.append({
            "uuid":         full_uuid,
            "uuid6":        uuid6,
            "name":         conv.get("name") or "(unnamed)",
            "project_uuid": None,
            "project_name": "Unassigned (export-only)",
            "project_slug": "unassigned",
            "date":         conv.get("created_at", "")[:10],
            "export_file":  find_export_file(uuid6),
            "source":       "export-only",
        })

    records.sort(key=lambda r: (r["project_slug"], r["date"]))
    return records


# ---------------------------------------------------------------------------
# Organize by-project folder
# ---------------------------------------------------------------------------

def organize_by_project(records: list[dict]):
    """
    Copy files from 2026-05-09-full/ into by-project/[slug]/ subdirectories.
    Only processes files that exist in the export. Does not overwrite.
    """
    if DRY_RUN:
        print("\n[DRY RUN] Would create by-project/ structure:")
    else:
        BY_PROJECT_DIR.mkdir(exist_ok=True)

    counts = {}
    for r in records:
        slug = r["project_slug"]
        src = r["export_file"]
        if src is None:
            continue

        dest_dir = BY_PROJECT_DIR / slug
        dest = dest_dir / src.name

        if DRY_RUN:
            print(f"  {slug}/{src.name}")
        else:
            dest_dir.mkdir(exist_ok=True)
            if not dest.exists():
                shutil.copy2(src, dest)
        counts[slug] = counts.get(slug, 0) + 1

    return counts


# ---------------------------------------------------------------------------
# Write manifest
# ---------------------------------------------------------------------------

def write_manifest(records: list[dict]):
    manifest = {}
    for r in records:
        manifest[r["uuid"]] = {
            "uuid6":        r["uuid6"],
            "name":         r["name"],
            "date":         r["date"],
            "project_uuid": r["project_uuid"],
            "project_name": r["project_name"],
            "project_slug": r["project_slug"],
            "export_file":  str(r["export_file"].name) if r["export_file"] else None,
            "by_project_path": f"by-project/{r['project_slug']}/{r['export_file'].name}"
                                if r["export_file"] else None,
            "source":       r["source"],
        }
    with open(MANIFEST_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Manifest written: {MANIFEST_OUTPUT.relative_to(REPO)}")


# ---------------------------------------------------------------------------
# Write markdown map
# ---------------------------------------------------------------------------

def write_map(records: list[dict], counts_by_project: dict):
    by_project = {}
    for r in records:
        key = r["project_uuid"]
        by_project.setdefault(key, []).append(r)

    lines = []
    now = datetime.now().strftime("%Y-%m-%d")
    total = len(records)
    pm_count = sum(1 for r in records if r["source"] == "project-map")
    export_only = sum(1 for r in records if r["source"] == "export-only")

    lines += [
        f"# Conversation Map — Authoritative (project-map.json)",
        f"",
        f"Generated: {now}  |  Script: `scripts/map_conversations.py`",
        f"",
        f"**Primary source:** `raw/exports/project-map.json` (live API, {pm_count} conversations)",
        f"**Supplemental:** `intake/Anthropic download 20260503/conversations.json`"
        f" ({export_only} additional, export-only)",
        f"**Total:** {total} conversations",
        f"",
        f"## Summary by Project",
        f"",
        f"| Project | Slug | Count | Exported files |",
        f"|---|---|---|---|",
    ]
    for p_uuid in PROJECT_ORDER:
        bucket = by_project.get(p_uuid, [])
        if not bucket:
            continue
        slug = PROJECT_SLUGS.get(p_uuid, "unassigned")
        name = PROJECT_DISPLAY.get(p_uuid, "Unknown")
        exported = counts_by_project.get(slug, 0)
        lines.append(f"| {name} | `{slug}` | {len(bucket)} | {exported} |")
    lines.append(f"")

    # Per-project tables
    for p_uuid in PROJECT_ORDER:
        bucket = by_project.get(p_uuid, [])
        if not bucket:
            continue
        name = PROJECT_DISPLAY.get(p_uuid, "Unknown")
        slug = PROJECT_SLUGS.get(p_uuid, "unassigned")
        lines += [
            f"## {name} ({len(bucket)})",
            f"",
            f"| Date | UUID-6 | Title | Export file |",
            f"|---|---|---|---|",
        ]
        for r in sorted(bucket, key=lambda x: x["date"]):
            ef = r["export_file"].name if r["export_file"] else "*(missing)*"
            lines.append(f"| {r['date']} | `{r['uuid6']}` | {r['name']} | `{ef}` |")
        lines.append(f"")

    # Notes section
    lines += [
        f"## Notes",
        f"",
        f"- `project-map.json` was built via Chrome DevTools Protocol against the live",
        f"  claude.ai API. It has real `project_uuid` fields that the Anthropic data",
        f"  export (`conversations.json`) does not include.",
        f"- Export-only conversations (source=export-only) have no project assignment",
        f"  because they were not reachable when the CDP script ran. They may be deleted,",
        f"  private, or post-date the project-map fetch.",
        f"- `by-project/` under `raw/exports/2026-05-09-full/` mirrors this classification",
        f"  as a browsable folder structure.",
        f"",
        f"## raw/ Cleanup Plan (pending Jon approval)",
        f"",
        f"See session notes. Short version:",
        f"- Archive `raw/sessions/archive_attempt_incomplete/` — deprecated DOM extractions",
        f"- Archive `raw/first_intake_v2/` — superseded by exports",
        f"- Archive `raw/tracker-recovery/` — built on summaries, not sessions (known bad)",
        f"- Expand `raw/sessions/personal/` and `raw/sessions/pro/` from by-project/",
        f"- Create `raw/sessions/how-to-use-claude/` from by-project/how-to-use-claude/",
        f"- Create `raw/sessions/unassigned/` for the 14 null-project conversations",
        f"- Do NOT overwrite existing curated files in `raw/sessions/fl/`",
    ]

    MAP_OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Map written:      {MAP_OUTPUT.relative_to(REPO)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"\n{'='*60}")
    print(f"map_conversations.py  {'[DRY RUN]' if DRY_RUN else ''}")
    print(f"{'='*60}\n")

    print("Loading project-map.json ...")
    project_map = load_project_map()
    print(f"  {len(project_map)} entries")

    print("Loading conversations.json ...")
    conv_lookup = load_conversations()
    print(f"  {len(conv_lookup)} entries")

    print("Building unified records ...")
    records = build_records(project_map, conv_lookup)
    print(f"  {len(records)} total conversations")

    by_slug = {}
    for r in records:
        by_slug.setdefault(r["project_slug"], []).append(r)
    print("\nProject breakdown:")
    for slug, recs in sorted(by_slug.items(), key=lambda x: -len(x[1])):
        has_file = sum(1 for r in recs if r["export_file"])
        print(f"  {slug:25s}  {len(recs):3d} conversations  ({has_file} export files found)")

    print("\nOrganizing by-project/ ...")
    counts = organize_by_project(records)

    print("\nWriting outputs ...")
    write_manifest(records)
    write_map(records, counts)

    print("\nDone.")


if __name__ == "__main__":
    main()
