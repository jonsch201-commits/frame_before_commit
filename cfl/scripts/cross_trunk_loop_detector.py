"""
scripts/cross_trunk_loop_detector.py — Cross-Trunk Autonomous Loop & Liveness Sentinel

Responds directly to CFL task cfl-to-antigravity-I-WAS-IN-A-LOOP-AND-COULD-NOT-SEE-IT-FROM-INSIDE-2026-09-04.md:
1. Tracks per-interval deltas across all 6 trunks:
   - commits: newest git commit hash
   - tree files: newest file mtimes across wiki/, scripts/, raw/
   - exchange files: newest file mtimes across exchange/inbound and exchange/outbox
2. Detects repetition loops: If an active seat produces 0 commits, 0 file deltas, and 0 exchange deltas
   for N consecutive intervals (N >= 3), it flags a REPETITION LOOP.
3. Emits failable, informative alert letters to the trunk's inbound naming the exact repetition count,
   interval count, ungated local compute work available, and the false-positive boundary (Jon decision gate).
4. Watches Antigravity itself as a subject, publishing its own row.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone

HUB_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = HUB_ROOT / ".cache"
STATE_FILE = CACHE_DIR / "loop_detector_state.json"
REPORT_FILE = HUB_ROOT / "exchange" / "FLEET-LOOP-STATUS.md"
G_REPORT_FILE = Path(r"G:\My Drive\Claude\Antigravity\exchange\FLEET-LOOP-STATUS.md")

TRUNKS = {
    "cfl": {
        "repo": Path(r"N:\claude-cfl\clone"),
        "exchange": Path(r"N:\claude-cfl\clone\exchange"),
        "session_dir": Path(r"C:\Users\JonSc\.claude\projects\N--claude-cfl-clone"),
        "alias": "CFL"
    },
    "professional": {
        "repo": Path(r"N:\claude-professional") if Path(r"N:\claude-professional").exists() else Path(r"G:\My Drive\Claude\Claude Professional\claude-professional"),
        "exchange": Path(r"N:\claude-professional\exchange") if Path(r"N:\claude-professional\exchange").exists() else Path(r"G:\My Drive\Claude\Claude Professional\claude-professional\exchange"),
        "session_dir": Path(r"C:\Users\JonSc\.claude\projects\N--claude-professional") if Path(r"C:\Users\JonSc\.claude\projects\N--claude-professional").exists() else Path(r"C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Professional-claude-professional"),
        "alias": "Professional"
    },
    "secretary": {
        "repo": Path(r"N:\claude-secretary") if Path(r"N:\claude-secretary").exists() else Path(r"G:\My Drive\Claude\Claude Secretary"),
        "exchange": Path(r"N:\claude-secretary\exchange") if Path(r"N:\claude-secretary\exchange").exists() else Path(r"G:\My Drive\Claude\Claude Secretary\exchange"),
        "session_dir": Path(r"C:\Users\JonSc\.claude\projects\N--claude-secretary") if Path(r"C:\Users\JonSc\.claude\projects\N--claude-secretary").exists() else Path(r"C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Secretary"),
        "alias": "Secretary"
    },
    "personal": {
        "repo": Path(r"N:\claude-personal") if Path(r"N:\claude-personal").exists() else (Path(r"N:\claude-corpus\personal") if Path(r"N:\claude-corpus\personal").exists() else Path(r"G:\My Drive\Claude\Claude Personal")),
        "exchange": Path(r"N:\claude-personal\exchange") if Path(r"N:\claude-personal\exchange").exists() else (Path(r"N:\claude-corpus\personal\exchange") if Path(r"N:\claude-corpus\personal\exchange").exists() else Path(r"G:\My Drive\Claude\Claude Personal\exchange")),
        "session_dir": Path(r"C:\Users\JonSc\.claude\projects\N--claude-personal") if Path(r"C:\Users\JonSc\.claude\projects\N--claude-personal").exists() else Path(r"C:\Users\JonSc\.claude\projects\G--My-Drive-Claude-Claude-Personal"),
        "alias": "Personal"
    },
    "ssp": {
        "repo": Path(r"N:\claude-corpus\ssp") if Path(r"N:\claude-corpus\ssp").exists() else Path(r"G:\My Drive\Claude\SSP\claude-ssp"),
        "exchange": Path(r"N:\claude-corpus\ssp\exchange") if Path(r"N:\claude-corpus\ssp\exchange").exists() else Path(r"G:\My Drive\Claude\SSP\claude-ssp\exchange"),
        "session_dir": None,
        "alias": "SSP",
        "passive": True
    },
    "antigravity": {
        "repo": HUB_ROOT,
        "exchange": HUB_ROOT / "exchange",
        "session_dir": None,
        "alias": "Antigravity"
    }
}

USAGE_METER_PATH = Path(r"N:\claude-gists-private\USAGE-CURRENT-cfl.json")

def get_usage_meter() -> dict:
    if USAGE_METER_PATH.exists():
        try:
            return json.loads(USAGE_METER_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def get_claude_session_status(session_dir: Path, meter_unlocked: bool = False) -> dict:
    if not session_dir or not session_dir.exists():
        return {"status": "NO_SESSION", "rate_limited": False, "details": "No session dir"}
    try:
        jsonls = sorted(session_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    except Exception:
        jsonls = []
    if not jsonls:
        return {"status": "NO_SESSION", "rate_limited": False, "details": "No jsonl logs"}
    latest = jsonls[0]
    latest_mt = latest.stat().st_mtime
    age_sec = time.time() - latest_mt

    # If the newest session log has not been touched in > 2 hours, trunk is DARK/DORMANT
    if age_sec > 7200:
        return {
            "status": "DARK",
            "rate_limited": False,
            "details": f"Dark/Dormant (last active {age_sec/3600:.1f}h ago)",
            "session_file": latest.name,
            "mtime": latest_mt,
            "age_seconds": age_sec
        }

    try:
        with open(latest, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        last_chunk = "".join(lines[-10:]) if len(lines) >= 10 else "".join(lines)
        if "rate_limit" in last_chunk or "weekly limit" in last_chunk or "Usage limit reached" in last_chunk:
            return {"status": "RATE_LIMITED_429", "rate_limited": True, "details": "Weekly limit reached (429)", "session_file": latest.name, "mtime": latest_mt, "age_seconds": age_sec}
        return {"status": "ACTIVE", "rate_limited": False, "details": "Normal operation", "session_file": latest.name, "mtime": latest_mt, "age_seconds": age_sec}
    except Exception as e:
        return {"status": "READ_ERROR", "rate_limited": False, "details": str(e), "mtime": latest_mt, "age_seconds": age_sec}


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_state(state: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = STATE_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temp_file.replace(STATE_FILE)

def get_git_head(repo_path: Path) -> str:
    if not (repo_path / ".git").exists():
        return "NO_GIT"
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "UNKNOWN"

def get_tree_mtime(repo_path: Path, max_depth: int = 3) -> float:
    newest = 0.0
    for subdir in ("wiki", "scripts", "raw"):
        base_dir = repo_path / subdir
        if not base_dir.exists():
            continue
        try:
            base_mt = base_dir.stat().st_mtime
            if base_mt > newest:
                newest = base_mt
            
            # Recursive scan up to max_depth
            for root, dirs, files in os.walk(base_dir):
                rel_parts = Path(root).relative_to(base_dir).parts
                if len(rel_parts) >= max_depth:
                    dirs.clear()
                for fn in files:
                    try:
                        fp = os.path.join(root, fn)
                        pmt = os.stat(fp).st_mtime
                        if pmt > newest:
                            newest = pmt
                    except Exception:
                        pass
        except Exception:
            pass
    return newest

def get_exchange_mtime(exchange_path: Path) -> float:
    newest = 0.0
    if exchange_path.exists():
        for subdir in ("inbound", "outbox"):
            d = exchange_path / subdir
            if d.exists():
                try:
                    with os.scandir(d) as it:
                        for entry in it:
                            try:
                                if entry.is_file() and entry.name.endswith(".md"):
                                    pmt = entry.stat().st_mtime
                                    if pmt > newest:
                                        newest = pmt
                            except Exception:
                                pass
                except Exception:
                    pass
    return newest

def check_fleet_loops() -> dict:
    state = load_state()
    now_iso = datetime.now(timezone.utc).isoformat()
    now_ts = time.time()
    
    meter = get_usage_meter()
    sd_meter = meter.get("seven_day") or {}
    fh_meter = meter.get("five_hour") or {}
    sd_util = sd_meter.get("utilization")
    sd_resets = sd_meter.get("resets_at")
    fh_util = fh_meter.get("utilization")
    
    fleet_report = {
        "timestamp_utc": now_iso,
        "meter": {
            "seven_day_util": sd_util,
            "seven_day_resets_at": sd_resets,
            "five_hour_util": fh_util
        },
        "trunks": {}
    }
    
    alerts_to_send = []

    print("[LOOP_DETECTOR] Checking fleet liveness and loop repetitions...", flush=True)

    for trunk_key, info in TRUNKS.items():
        repo = info["repo"]
        ex = info["exchange"]
        alias = info["alias"]
        session_dir = info.get("session_dir")
        
        if not repo.exists():
            fleet_report["trunks"][trunk_key] = {"status": "ABSENT"}
            continue
            
        current_head = get_git_head(repo)
        current_tree_mt = get_tree_mtime(repo)
        current_ex_mt = get_exchange_mtime(ex)
        meter_unlocked = (sd_util is not None and sd_util < 100.0)
        if info.get("passive"):
            session_info = {"status": "PASSIVE", "rate_limited": False, "details": "Passive corpus trunk"}
        elif session_dir:
            session_info = get_claude_session_status(session_dir, meter_unlocked=meter_unlocked)
        else:
            session_info = {"status": "LOCAL_COMPUTE", "rate_limited": False, "details": "Autonomous runner"}
        
        prev = state.get(trunk_key, {})
        prev_head = prev.get("head")
        prev_tree_mt = prev.get("tree_mtime", 0.0)
        prev_ex_mt = prev.get("exchange_mtime", 0.0)
        prev_session_mt = prev.get("session_mtime", 0.0)
        prior_intervals = prev.get("consecutive_idle_intervals", 0)
        
        current_session_mt = session_info.get("mtime", 0.0)
        
        # Calculate deltas (head, tree, exchange, and active session transcript)
        head_changed = (prev_head is not None) and (current_head != prev_head)
        tree_changed = (current_tree_mt > prev_tree_mt)
        ex_changed = (current_ex_mt > prev_ex_mt)
        session_changed = (current_session_mt > prev_session_mt)
        has_delta = head_changed or tree_changed or ex_changed or session_changed
        
        if session_info.get("rate_limited"):
            consecutive_idle = prior_intervals + 1
            loop_verdict = f"RATE_LIMITED_429 (Weekly 100%, resets {sd_resets or '14:00 CDT'})"
        elif session_info.get("status") in ("DARK", "NO_SESSION", "PASSIVE"):
            consecutive_idle = 0
            loop_verdict = "PASSIVE" if session_info.get("status") == "PASSIVE" else f"DARK ({session_info.get('details')})"
        elif has_delta or prev_head is None:
            consecutive_idle = 0
            if current_head in ("NO_GIT", "UNKNOWN"):
                loop_verdict = f"UNKNOWN (head={current_head})"
            else:
                loop_verdict = "HEALTHY"
        else:
            consecutive_idle = prior_intervals + 1
            if consecutive_idle >= 3:
                loop_verdict = f"REPETITION_LOOP ({consecutive_idle} intervals)"
            else:
                loop_verdict = f"IDLE ({consecutive_idle} intervals)"
                
        state[trunk_key] = {
            "head": current_head,
            "tree_mtime": current_tree_mt,
            "exchange_mtime": current_ex_mt,
            "session_mtime": current_session_mt,
            "consecutive_idle_intervals": consecutive_idle,
            "last_active_ts": now_ts if has_delta else prev.get("last_active_ts", now_ts),
            "verdict": loop_verdict,
            "session_status": session_info.get("status", "UNKNOWN"),
            "last_checked": now_iso
        }
        
        fleet_report["trunks"][trunk_key] = {
            "alias": alias,
            "head": current_head,
            "consecutive_idle_intervals": consecutive_idle,
            "verdict": loop_verdict,
            "session_status": session_info.get("status", "UNKNOWN"),
            "has_delta": has_delta
        }
        
        print(f"  - {alias:12}: {loop_verdict} (head={current_head}, delta={has_delta}, session={session_info.get('status')})", flush=True)
        
        # If genuine loop detected (and NOT blocked by rate limit 429 and NOT DARK/DORMANT/NO_SESSION)
        if not session_info.get("rate_limited") and session_info.get("status") not in ("DARK", "NO_SESSION", "UNKNOWN") and consecutive_idle >= 3 and consecutive_idle % 3 == 0:
            alerts_to_send.append((trunk_key, alias, ex, consecutive_idle))

    save_state(state)
    
    # Send alerts to inboxes if loops detected
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for trunk_key, alias, ex, intervals in alerts_to_send:
        inbox = ex / "inbound"
        if inbox.exists():
            alert_filename = f"ALERT-{today_str}-antigravity-to-{trunk_key}-REPETITION-LOOP-DETECTED-{intervals}-INTERVALS.md"
            alert_path = inbox / alert_filename
            alert_body = f"""---
from: antigravity (autonomous daemon loop)
to: {trunk_key}
date: {today_str}
kind: alert
subject: LIVENESS REPETITION LOOP DETECTED ({intervals} intervals with zero delta)
---

# Liveness Alert: {intervals} Consecutive Intervals with Zero Disk Mutation

**Addressee:** {alias}  
**Detected By:** Antigravity Autonomous Loop Sentinel (`scripts/cross_trunk_loop_detector.py`)  
**Trigger:** Measured {intervals} consecutive intervals (approx. {intervals * 5} minutes) with:
- 0 new git commits (HEAD static)
- 0 modified/created files in wiki/, scripts/, raw/
- 0 new letters in exchange/outbox

## The Two Interpretations (Honest Diagnostic Boundary)

1. **Failure Mode (Do-Nothing Idle Loop):**  
   If your process is waking every interval, evaluating a meter or gate (e.g. `HOLD lanes=0`), and concluding that no work can proceed, **you are in a do-nothing loop**.  
   *Correction:* The gate governs subagent/spend dispatch only; local main-seat compute is unblocked. Check your open wayfinder map for local ungated work (reading peer mail, fixing scripts, ingesting sources, running linters).

2. **False Positive Boundary (Legitimate User Gate):**  
   If you are legitimately waiting for Jon's explicit input at an approved gate (e.g., G1 review), this alert is a known false positive. State the blocking gate in your tracker and let it stand.

*Generated autonomously by Antigravity under Resident Continuity Contract §3.*
"""
            try:
                alert_path.write_text(alert_body, encoding="utf-8")
                print(f"[LOOP_DETECTOR] Deposited alert letter to {alias}: {alert_filename}", flush=True)
            except Exception as e:
                print(f"[LOOP_DETECTOR] Failed to write alert letter: {e}", flush=True)

    # Write Markdown summary table
    md_lines = [
        "---",
        "to: all",
        f"date: {today_str}",
        "kind: status",
        "subject: Fleet Liveness, Rate Limit & Repetition Loop Status",
        "---",
        "",
        "# Fleet Liveness, Rate Limit & Repetition Loop Status",
        f"**Last Scanned UTC:** `{now_iso}`  ",
        f"**Anthropic Account Meter:** Seven-Day Utilization: `{sd_util}%` (Resets at `{sd_resets or '14:00 CDT'}`) | Five-Hour Utilization: `{fh_util}%`  ",
        ""
    ]
    
    if sd_util is not None and sd_util >= 100.0:
        md_lines.extend([
            "> ⛔ **WEEKLY LIMIT ACTIVE (100.0%). Next API reset at 14:00 CDT (19:00 UTC).**",
            "> Claude Code coordinator seats (CFL, Secretary, Professional, Personal) cannot run interactive turns or subagents until reset.",
            "> Only local offline deterministic compute (compilation, linters, NVMe indexing, static analysis) can proceed without API calls.",
            ""
        ])
        
    md_lines.extend([
        "| Trunk | HEAD | Session Status | Consecutive Idle Intervals | Status / Verdict | Delta This Tick |",
        "|---|---|---|---|---|---|"
    ])
    for tk, data in fleet_report["trunks"].items():
        alias = data.get("alias", tk)
        head = data.get("head", "-")
        sess_status = data.get("session_status", "UNKNOWN")
        idle = data.get("consecutive_idle_intervals", 0)
        verdict = data.get("verdict", "UNKNOWN")
        delta = "YES" if data.get("has_delta") else "NO"
        md_lines.append(f"| {alias} | `{head}` | `{sess_status}` | {idle} | **{verdict}** | {delta} |")
        
    md_content = "\n".join(md_lines) + "\n"
    try:
        REPORT_FILE.write_text(md_content, encoding="utf-8")
        if G_REPORT_FILE.parent.exists():
            G_REPORT_FILE.write_text(md_content, encoding="utf-8")
    except Exception:
        pass
        
    return fleet_report

if __name__ == "__main__":
    check_fleet_loops()
