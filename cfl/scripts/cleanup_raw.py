"""
cleanup_raw.py
--------------
Executes the approved raw/ cleanup plan:

  1. Archive deprecated folders to raw/_deprecated/
       - raw/sessions/archive_attempt_incomplete/
       - raw/first_intake_v2/
       - raw/tracker-recovery/

  2. Expand raw/sessions/ from raw/exports/2026-05-09-full/by-project/
     (only adds files not already present; never overwrites curated content)
       - raw/sessions/personal/       (adds from by-project/personal/)
       - raw/sessions/pro/            (adds from by-project/pro/)
       - raw/sessions/how-to-use-claude/ (adds from by-project/how-to-use-claude/)
       - raw/sessions/unassigned/     (creates new; adds from by-project/unassigned/)

  3. Move top-level intake/ to raw/intake-archive/

Run:
  python scripts/cleanup_raw.py [--dry-run]
"""

import io
import shutil
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DRY_RUN = "--dry-run" in sys.argv

REPO = Path(__file__).parent.parent
BY_PROJECT = REPO / "raw" / "exports" / "2026-05-09-full" / "by-project"
SESSIONS    = REPO / "raw" / "sessions"
DEPRECATED  = REPO / "raw" / "_deprecated"


def log(msg: str):
    print(msg)


def move(src: Path, dst: Path, label: str = ""):
    tag = f"  [{label}] " if label else "  "
    if not src.exists():
        log(f"{tag}SKIP (not found): {src.relative_to(REPO)}")
        return
    if dst.exists():
        log(f"{tag}SKIP (already exists): {dst.relative_to(REPO)}")
        return
    log(f"{tag}MOVE {src.relative_to(REPO)} -> {dst.relative_to(REPO)}")
    if not DRY_RUN:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))


def copy_new(src_dir: Path, dst_dir: Path, label: str = ""):
    """Copy files from src_dir into dst_dir, skipping any that already exist by UUID-6."""
    if not src_dir.exists():
        log(f"  [{label}] SKIP source not found: {src_dir.relative_to(REPO)}")
        return 0

    # Build a set of uuid6 values already present in dst_dir (recursive)
    existing_uuid6 = set()
    if dst_dir.exists():
        for f in dst_dir.rglob("*.md"):
            # Extract uuid6 from filename — look for 6-char hex after date
            import re
            m = re.search(r"\d{4}-\d{2}-\d{2}-([0-9a-f]{6})", f.name)
            if m:
                existing_uuid6.add(m.group(1))

    added = 0
    skipped = 0
    for src_file in sorted(src_dir.iterdir()):
        if not src_file.is_file() or src_file.suffix != ".md":
            continue
        import re
        m = re.search(r"\d{4}-\d{2}-\d{2}-([0-9a-f]{6})", src_file.name)
        uuid6 = m.group(1) if m else None

        if uuid6 and uuid6 in existing_uuid6:
            skipped += 1
            continue

        dst_file = dst_dir / src_file.name
        log(f"  [{label}] ADD {src_file.name}")
        if not DRY_RUN:
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
        added += 1

    log(f"  [{label}] {added} added, {skipped} skipped (already present)")
    return added


def main():
    log(f"\n{'='*60}")
    log(f"cleanup_raw.py  {'[DRY RUN]' if DRY_RUN else ''}")
    log(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # 1. Archive deprecated folders
    # ------------------------------------------------------------------
    log("--- 1. Archive deprecated ---")
    DEPRECATED.mkdir(exist_ok=True) if not DRY_RUN else None

    move(
        SESSIONS / "archive_attempt_incomplete",
        DEPRECATED / "archive-attempt-incomplete",
        "archive"
    )
    move(
        REPO / "raw" / "first_intake_v2",
        DEPRECATED / "first-intake-v2",
        "archive"
    )
    move(
        REPO / "raw" / "tracker-recovery",
        DEPRECATED / "tracker-recovery",
        "archive"
    )

    # ------------------------------------------------------------------
    # 2. Expand raw/sessions/ from by-project/
    # ------------------------------------------------------------------
    log("\n--- 2. Expand raw/sessions/ ---")

    expansions = [
        ("personal",          SESSIONS / "personal"),
        ("pro",               SESSIONS / "pro"),
        ("how-to-use-claude", SESSIONS / "how-to-use-claude"),
        ("unassigned",        SESSIONS / "unassigned"),
    ]

    for slug, dst_dir in expansions:
        src_dir = BY_PROJECT / slug
        copy_new(src_dir, dst_dir, label=slug)

    # ------------------------------------------------------------------
    # 3. Move top-level intake/ to raw/intake-archive/
    # ------------------------------------------------------------------
    log("\n--- 3. Move intake/ to raw/intake-archive/ ---")
    move(
        REPO / "intake",
        REPO / "raw" / "intake-archive",
        "intake"
    )

    log("\nDone.")
    if DRY_RUN:
        log("(No files were changed — dry run only)")


if __name__ == "__main__":
    main()
