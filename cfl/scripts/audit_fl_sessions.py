"""
audit_fl_sessions.py
--------------------
Audits every file in raw/sessions/fl/ against the authoritative project-map.json.
Flags files that don't belong to the Claude Foundational Layer project,
are unrecognized (UUID not in project-map), or are Claude Code sessions
(which belong in fl/ but have no project-map entry since they came from
a different source).

Output:
  Console report
  scripts/output/fl_audit.md

Run:
  python scripts/audit_fl_sessions.py
"""

import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO = Path(__file__).parent.parent
PROJECT_MAP_FILE = REPO / "raw" / "exports" / "project-map.json"
FL_DIR           = REPO / "raw" / "sessions" / "fl"
OUTPUT_FILE      = REPO / "scripts" / "output" / "fl_audit.md"

CFL_PROJECT_UUID = "019d8279-90ca-7468-8fb1-37534b6daefc"

# Claude Code sessions: ingested directly, not in project-map or conversations.json.
# These legitimately belong in fl/ regardless of project-map absence.
CLAUDE_CODE_UUID6 = {"740c93", "e4c393", "8989d1"}

PROJECT_DISPLAY = {
    "019d8279-90ca-7468-8fb1-37534b6daefc": "Claude Foundational Layer",
    "019cc2fb-0284-77e5-ba27-1a880954817e": "Personal Life Questions",
    "019cc2fc-35c1-72ac-8ca8-7ce60433bc01": "Professional Life Questions",
    "019ca63c-3818-7510-aad8-5db3c583bd40": "How to use Claude",
    None: "Unassigned",
}


def extract_uuid6(path: Path) -> str | None:
    """
    Pull the 6-char UUID from a filename. Handles two conventions:
      topic-YYYY-MM-DD-uuid6.md         (UUID at end of stem)
      chat-YYYY-MM-DD-uuid6-title.md    (UUID after date, before title)
    Strategy: find a 6-char hex group that appears right after a date component.
    """
    m = re.search(r"\d{4}-\d{2}-\d{2}-([0-9a-f]{6})", path.name)
    return m.group(1) if m else None


def build_uuid6_to_project(project_map: dict) -> dict:
    """Build uuid6 -> (full_uuid, project_uuid, project_name, conv_name) lookup."""
    result = {}
    for full_uuid, pm in project_map.items():
        uuid6 = full_uuid.replace("-", "")[:6]
        result[uuid6] = {
            "full_uuid":    full_uuid,
            "project_uuid": pm.get("project_uuid"),
            "project_name": pm.get("project_name"),
            "conv_name":    pm.get("conv_name"),
        }
    return result


def collect_fl_files(fl_dir: Path) -> list[Path]:
    """Recursively collect all .md files under raw/sessions/fl/."""
    return sorted(fl_dir.rglob("*.md"))


def audit(files: list[Path], uuid6_lookup: dict) -> dict:
    """
    Classify each file. Returns dict keyed by verdict:
      CORRECT        — UUID in project-map, project is CFL
      WRONG_PROJECT  — UUID in project-map, project is NOT CFL
      CLAUDE_CODE    — UUID matches known Claude Code session (legitimately fl/)
      UNKNOWN        — UUID not in project-map and not Claude Code
      NO_UUID        — filename has no extractable UUID
    """
    buckets = {k: [] for k in ["CORRECT", "WRONG_PROJECT", "CLAUDE_CODE", "UNKNOWN", "NO_UUID"]}

    for f in files:
        uuid6 = extract_uuid6(f)
        if uuid6 is None:
            buckets["NO_UUID"].append({"file": f, "uuid6": None, "detail": ""})
            continue

        if uuid6 in CLAUDE_CODE_UUID6:
            buckets["CLAUDE_CODE"].append({"file": f, "uuid6": uuid6,
                                           "detail": "Claude Code session — legitimately fl/"})
            continue

        match = uuid6_lookup.get(uuid6)
        if match is None:
            buckets["UNKNOWN"].append({"file": f, "uuid6": uuid6,
                                       "detail": "UUID not in project-map"})
            continue

        p_uuid = match["project_uuid"]
        p_name = match["project_name"] or PROJECT_DISPLAY.get(p_uuid, "Unknown")
        conv   = match["conv_name"]

        if p_uuid == CFL_PROJECT_UUID:
            buckets["CORRECT"].append({"file": f, "uuid6": uuid6,
                                       "detail": f'"{conv}"'})
        else:
            buckets["WRONG_PROJECT"].append({"file": f, "uuid6": uuid6,
                                             "detail": f'"{conv}" -> actually: {p_name}',
                                             "actual_project": p_name,
                                             "actual_uuid": p_uuid})

    return buckets


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def main():
    print(f"\n{'='*60}")
    print(f"fl/ audit vs project-map.json")
    print(f"{'='*60}\n")

    with open(PROJECT_MAP_FILE, encoding="utf-8") as f:
        project_map = json.load(f)

    uuid6_lookup = build_uuid6_to_project(project_map)
    files = collect_fl_files(FL_DIR)
    print(f"Files in raw/sessions/fl/: {len(files)}")

    buckets = audit(files, uuid6_lookup)

    # Console summary
    for verdict, items in buckets.items():
        print(f"\n--- {verdict} ({len(items)}) ---")
        for item in items:
            print(f"  {item['uuid6'] or '??????'}  {rel(item['file'])}")
            if item["detail"]:
                print(f"           {item['detail']}")

    # Markdown report
    lines = [
        "# fl/ Session Audit",
        "",
        f"Checked all files in `raw/sessions/fl/` against `raw/exports/project-map.json`.",
        f"Total files: {len(files)}",
        "",
        "## Verdict Key",
        "",
        "| Verdict | Meaning |",
        "|---|---|",
        "| CORRECT | UUID confirmed as Claude Foundational Layer project |",
        "| WRONG_PROJECT | UUID found in project-map but belongs to a different project |",
        "| CLAUDE_CODE | Known Claude Code session — legitimately fl/ regardless |",
        "| UNKNOWN | UUID not in project-map (may be old/deleted/pre-export) |",
        "| NO_UUID | Filename has no parseable UUID |",
        "",
    ]

    verdict_order = ["CORRECT", "WRONG_PROJECT", "CLAUDE_CODE", "UNKNOWN", "NO_UUID"]
    for verdict in verdict_order:
        items = buckets[verdict]
        lines.append(f"## {verdict} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("*(none)*")
        else:
            lines.append("| UUID-6 | File | Detail |")
            lines.append("|---|---|---|")
            for item in items:
                lines.append(f"| `{item['uuid6'] or '---'}` | `{rel(item['file'])}` | {item['detail']} |")
        lines.append("")

    # Action items
    wrong = buckets["WRONG_PROJECT"]
    unknown = buckets["UNKNOWN"]
    lines += [
        "## Action Items",
        "",
    ]
    if wrong:
        lines.append("### Files to move out of fl/")
        lines.append("")
        lines.append("These files belong to a different project and should be moved:")
        lines.append("")
        for item in wrong:
            lines.append(f"- `{rel(item['file'])}` — belongs in **{item['actual_project']}**")
        lines.append("")
    if unknown:
        lines.append("### Unknown UUID files — needs manual review")
        lines.append("")
        lines.append("These UUIDs are not in project-map. Possible causes:")
        lines.append("- Session was deleted from claude.ai since the project-map was built")
        lines.append("- Session predates the project-map fetch")
        lines.append("- File was manually placed here and UUID is from a different system")
        lines.append("")
        for item in unknown:
            lines.append(f"- `{rel(item['file'])}`")
        lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written: {OUTPUT_FILE.relative_to(REPO)}")
    print(f"\nSummary: {len(buckets['CORRECT'])} correct, "
          f"{len(buckets['WRONG_PROJECT'])} wrong project, "
          f"{len(buckets['CLAUDE_CODE'])} Claude Code, "
          f"{len(buckets['UNKNOWN'])} unknown, "
          f"{len(buckets['NO_UUID'])} no UUID")


if __name__ == "__main__":
    main()
