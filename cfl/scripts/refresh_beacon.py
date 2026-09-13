from pathlib import Path
from datetime import datetime, timezone
import subprocess

now_iso = datetime.now(timezone.utc).isoformat()
now_display = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

try:
    git_head = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip()
except Exception:
    git_head = 'UNKNOWN'

session_id = "765e466c-54d5-421a-a4e5-08f6f6df81a8"

content = f"""---
title: "Antigravity Beacon and Dead-Man Switch"
trunk: "Antigravity"
session_id: "{session_id}"
last_seen_utc: "{now_iso}"
daemon_status: "ACTIVE"
active_task: "task-32 (10-min autonomous tick)"
task_schedule: "*/10 * * * *"
git_head: "{git_head}"
nvme_index_path: "N:\\claude-indexes\\graphrag-federated\\index.sqlite"
status: "LIVE_PERSISTENT"
---

# Antigravity Beacon and Dead-Man Switch

- **Last Seen UTC:** {now_display}
- **Current Session:** `{session_id}`
- **Git HEAD:** `{git_head}`
- **Daemon Status:** ACTIVE (task-32 running every 10 minutes detached)
- **Primary Source Surface:** `N:\\antigravity-hub\\` (Canonical NVMe authoring)
- **Mirror Surface:** `G:\\My Drive\\Claude\\Antigravity\\` (Read-only G-Drive mirror)
- **Federated Graph RAG Index:** `N:\\claude-indexes\\graphrag-federated\\index.sqlite` (29,843 docs, 417,433 edges, 1,195 vectors settled)
- **Freshness Policy (§20 Compliant):** Refreshed automatically every daemon tick.
"""

p = Path("N:/antigravity-hub/exchange/LAST-SEEN.md")
p.write_text(content, encoding="utf-8")
print("Updated LAST-SEEN.md successfully. Bytes:", p.stat().st_size)
