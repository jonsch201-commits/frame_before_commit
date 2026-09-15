"""
scripts/inbound_dispatcher.py — Autonomous Cross-Trunk Courier & Inbound Dispatcher

Fulfills T-9 (Courier closure) and T-1 across the multi-agent ecosystem:
1. Sweeps outboxes across all 6 trunks (Antigravity, CFL, Secretary, Professional, Personal, SSP).
2. Parses IMEP YAML frontmatter (`to:`, `from:`, `kind:`, `date:`).
3. Delivers outbound letters to target inboxes (both on N: and G:).
4. Maintains an immutable dispatch audit log in `exchange/COURIER-DISPATCH.jsonl`.
5. Scans Antigravity's own inbound queue for incoming tasks/orders.
"""

import os
import re
import sys
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HUB_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = HUB_ROOT / ".cache"
STATE_FILE = CACHE_DIR / "courier_state.json"
DISPATCH_LOG = HUB_ROOT / "exchange" / "COURIER-DISPATCH.jsonl"
G_DISPATCH_LOG = Path(r"G:\My Drive\Claude\Antigravity\exchange\COURIER-DISPATCH.jsonl")

FRONTMATTER_PATTERN = re.compile(r'^---\r?\n(.*?)\r?\n---', re.DOTALL)

from anti_decoy_resolver import (
    resolve_exchange_dir,
    safe_prepare_inbox,
    has_repo_marker,
    DecoyRootError,
)

TRUNK_MAP = {
    "antigravity": {
        "primary": HUB_ROOT / "exchange",
        "mirror": Path(r"G:\My Drive\Claude\Antigravity\exchange"),
        "aliases": ["agy", "antigravity-hub"]
    },
    "cfl": {
        "primary": Path(r"N:\claude-cfl\clone\exchange"),
        "mirror": Path(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer\exchange"),
        "aliases": ["foundational", "claude-cfl", "cfl-clone"]
    },
    "secretary": {
        "primary": Path(r"N:\claude-secretary\exchange") if Path(r"N:\claude-secretary\exchange").exists() else Path(r"N:\claude-corpus\secretary\exchange"),
        "mirror": Path(r"G:\My Drive\Claude\Claude Secretary\exchange"),
        "aliases": ["sec", "claude-secretary"]
    },
    "professional": {
        "primary": Path(r"N:\claude-professional\exchange") if Path(r"N:\claude-professional\exchange").exists() else Path(r"N:\claude-corpus\professional\exchange"),
        "mirror": Path(r"G:\My Drive\Claude\Claude Professional\claude-professional\exchange"),
        "aliases": ["pro", "claude-professional", "fable"]
    },
    "personal": {
        "primary": Path(r"N:\claude-personal\exchange") if Path(r"N:\claude-personal\exchange").exists() else Path(r"N:\claude-corpus\personal\exchange"),
        "mirror": Path(r"G:\My Drive\Claude\Claude Personal\exchange"),
        "aliases": ["per", "claude-personal"]
    },
    "ssp": {
        "primary": Path(r"N:\claude-corpus\ssp\exchange"),
        "mirror": Path(r"G:\My Drive\Claude\Claude SSP\claude-ssp\exchange"),
        "aliases": ["claude-ssp"]
    }
}

def get_file_hash(filepath: Path) -> str:
    try:
        h = hashlib.sha256()
        h.update(filepath.read_bytes())
        return h.hexdigest()
    except Exception:
        return ""

def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_PATTERN.match(text)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, _, v = line.partition(':')
            meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta

def resolve_recipients(to_str: str, sender_key: str) -> list[str]:
    if not to_str:
        return []
    
    parts = [p.strip().lower() for p in re.split(r'[,;]+', to_str)]
    all_trunks = list(TRUNK_MAP.keys())
    
    # Broadcast keywords
    for p in parts:
        if p in ["all", "fleet", "all trunks", "co trunks", "everyone", "all-trunks"]:
            return [t for t in all_trunks if t != sender_key]
            
    recipients = set()
    for p in parts:
        matched = False
        for trunk_key, info in TRUNK_MAP.items():
            if p == trunk_key or p in info["aliases"]:
                if trunk_key != sender_key:
                    recipients.add(trunk_key)
                matched = True
                break
        if not matched and "antigravity" in p and sender_key != "antigravity":
            recipients.add("antigravity")
        elif not matched and "secretary" in p and sender_key != "secretary":
            recipients.add("secretary")
        elif not matched and "cfl" in p and sender_key != "cfl":
            recipients.add("cfl")
        elif not matched and "pro" in p and sender_key != "professional":
            recipients.add("professional")
        elif not matched and "per" in p and sender_key != "personal":
            recipients.add("personal")
            
    return list(recipients)

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_state(state: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def log_dispatch(entry: dict):
    line = json.dumps(entry) + "\n"
    DISPATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DISPATCH_LOG, "a", encoding="utf-8") as f:
        f.write(line)
    if G_DISPATCH_LOG.parent.exists():
        try:
            with open(G_DISPATCH_LOG, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass

def courier_sweep() -> tuple[int, int]:
    state = load_state()
    delivered_count = 0
    scanned_count = 0
    now_iso = datetime.now(timezone.utc).isoformat()
    
    for sender_key, trunk_info in TRUNK_MAP.items():
        outbox_dirs = []
        # Prioritize local NVMe primary path to avoid slow G: drive network stalls
        pri = trunk_info.get("primary")
        if pri and pri.exists():
            try:
                ex_dir = resolve_exchange_dir(pri)
                out = ex_dir / "outbox"
                if out.exists():
                    outbox_dirs.append(out)
            except Exception:
                pass
        else:
            mir = trunk_info.get("mirror")
            if mir and mir.exists():
                try:
                    ex_dir = resolve_exchange_dir(mir)
                    out = ex_dir / "outbox"
                    if out.exists():
                        outbox_dirs.append(out)
                except Exception:
                    pass
            
        for outbox in outbox_dirs:
            if not outbox.exists():
                continue
                
            for letter_path in outbox.glob("*.md"):
                scanned_count += 1
                try:
                    raw_bytes = letter_path.read_bytes()
                except Exception:
                    continue
                    
                content = raw_bytes.decode("utf-8", errors="replace")
                meta = parse_frontmatter(content)
                raw_to = meta.get("to", "")
                recipients = resolve_recipients(raw_to, sender_key)
                if not recipients:
                    continue
                    
                file_hash = hashlib.sha256(raw_bytes).hexdigest()
                file_name = letter_path.name
                
                for dest_key in recipients:
                    dest_info = TRUNK_MAP[dest_key]
                    state_key = f"{sender_key}:{file_name}:{dest_key}"
                    
                    if state.get(state_key) == file_hash:
                        continue  # Already delivered this exact version
                        
                    # Deliver to destination primary NVMe inbound (mirror_n_to_g replicates to G:)
                    target_inboxes = []
                    dest_pri = dest_info.get("primary")
                    if dest_pri and dest_pri.exists():
                        try:
                            inbox = safe_prepare_inbox(dest_pri)
                            target_inboxes.append(inbox)
                        except Exception as e:
                            print(f"[COURIER] Target inbox resolution error for {dest_key} at {dest_pri}: {e}")
                    else:
                        dest_mir = dest_info.get("mirror")
                        if dest_mir and dest_mir.exists():
                            try:
                                inbox = safe_prepare_inbox(dest_mir)
                                target_inboxes.append(inbox)
                            except Exception as e:
                                print(f"[COURIER] Target inbox resolution error for {dest_key} at {dest_mir}: {e}")
                        
                    delivery_success = False
                    all_targets_ok = True
                    for inbox in target_inboxes:
                        try:
                            dest_file = inbox / file_name
                            
                            # Write if absent or different hash
                            if not dest_file.exists() or get_file_hash(dest_file) != file_hash:
                                shutil.copy2(letter_path, dest_file)
                                delivery_success = True
                        except Exception as e:
                            all_targets_ok = False
                            print(f"[COURIER] Delivery error {file_name} -> {inbox}: {e}")
                            
                    if delivery_success:
                        delivered_count += 1
                        state[state_key] = file_hash
                        entry = {
                            "timestamp": now_iso,
                            "source_trunk": sender_key,
                            "file": file_name,
                            "sha256": file_hash,
                            "dest_trunk": dest_key,
                            "status": "DELIVERED"
                        }
                        log_dispatch(entry)
                        print(f"[COURIER] DELIVERED: {file_name} from {sender_key} -> {dest_key}")
                    elif all_targets_ok and target_inboxes:
                        state[state_key] = file_hash
                        
    save_state(state)
    return scanned_count, delivered_count

INBOUND_STATE_FILE = CACHE_DIR / "inbound_state.json"
INBOUND_QUEUE_MD = HUB_ROOT / "exchange" / "INBOUND-QUEUE.md"
G_INBOUND_QUEUE_MD = Path(r"G:\My Drive\Claude\Antigravity\exchange\INBOUND-QUEUE.md")

def load_inbound_state() -> dict:
    if INBOUND_STATE_FILE.exists():
        try:
            return json.loads(INBOUND_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_inbound_state(state: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        temp_file = INBOUND_STATE_FILE.with_suffix(".tmp")
        temp_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        temp_file.replace(INBOUND_STATE_FILE)
    except Exception as e:
        print(f"[DISPATCHER] Failed to save inbound state: {e}", flush=True)

def sync_trunk_inbounds():
    """Sync inbound files between primary and mirror for all trunks, resolving the two-inbox EAR-1 asymmetry."""
    for trunk_key, info in TRUNK_MAP.items():
        prim = info.get("primary")
        mirr = info.get("mirror")
        if not prim or not mirr:
            continue
        try:
            p_inbox = safe_prepare_inbox(prim)
            m_inbox = safe_prepare_inbox(mirr)
            if not p_inbox.exists() or not m_inbox.exists():
                continue
            
            # Fast scan of files using os.scandir
            def get_files_map(directory: Path) -> dict[str, float]:
                fmap = {}
                with os.scandir(directory) as it:
                    for entry in it:
                        try:
                            if entry.is_file() and entry.name.endswith(".md"):
                                fmap[entry.name] = entry.stat().st_size
                        except Exception:
                            pass
                return fmap

            p_map = get_files_map(p_inbox)
            m_map = get_files_map(m_inbox)
            
            # Primary -> Mirror only (N: is authoritative; never resurrect deleted files from G:)
            for fname, size in p_map.items():
                if fname.startswith("ASK-JON-ARRIVAL-") and fname != "ASK-JON-ARRIVALS-ROLLUP-SESSION-44983b83-5ef7-44df-aca6-b9c2e8529a2b.md":
                    continue
                if fname not in m_map or m_map[fname] != size:
                    try:
                        shutil.copy2(p_inbox / fname, m_inbox / fname)
                        print(f"[COURIER] Reconciled inbound for {trunk_key}: {fname} -> {m_inbox}", flush=True)
                    except Exception:
                        pass
        except Exception:
            pass

def scan_antigravity_inbound():
    inbound_dir = HUB_ROOT / "exchange" / "inbound"
    if not inbound_dir.exists():
        return
        
    inbound_files = sorted(
        [f for f in inbound_dir.glob("*.md") if f.name != "README.md"],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    print(f"[DISPATCHER] Antigravity inbound queue: {len(inbound_files)} files present.", flush=True)
    
    state = load_inbound_state()
    now_iso = datetime.now(timezone.utc).isoformat()
    new_arrivals = []
    
    for fp in inbound_files:
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        meta = parse_frontmatter(content)
        sender = meta.get("from", "UNKNOWN")
        kind = meta.get("kind", "letter").strip()
        ticket = meta.get("ticket", "")
        subject = meta.get("subject", meta.get("title", fp.stem))
        file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        prev_entry = state.get(fp.name)
        is_new = prev_entry is None or prev_entry.get("sha256") != file_hash
        
        if is_new:
            new_arrivals.append({
                "file": fp.name,
                "from": sender,
                "kind": kind,
                "subject": subject,
                "bytes": len(content),
                "mtime": datetime.fromtimestamp(fp.stat().st_mtime, timezone.utc).isoformat()
            })
            state[fp.name] = {
                "sha256": file_hash,
                "from": sender,
                "kind": kind,
                "subject": subject,
                "first_seen": now_iso,
                "last_seen": now_iso,
                "backfilled": False,
                "consumption_status": "QUEUED"
            }
            # Surface every new arrival loudly without ANY kind filtering!
            print(f"  * [NEW ARRIVAL] [{sender}] {fp.name} (kind: {kind})", flush=True)
            if not any(k in kind.upper() for k in ["ORDER", "TASK", "FINDING", "PROPOSAL", "RECEIPT", "DELIVERABLE", "LETTER", "AMENDMENT", "ROUTING"]):
                print(f"    [CUSTOM/UNUSUAL KIND] '{kind}'", flush=True)
        else:
            prev_entry["last_seen"] = now_iso
            
    save_inbound_state(state)
    
    if new_arrivals:
        print(f"[DISPATCHER] Total new or updated letters this tick: {len(new_arrivals)}", flush=True)
    else:
        print("[DISPATCHER] Inbound queue steady (0 new arrivals this tick).", flush=True)
        
    # Write persistent INBOUND-QUEUE.md for coordinators and human inspection
    queue_lines = [
        "---",
        "to: all",
        "date: 2026-09-04",
        "kind: queue",
        "subject: Antigravity Active Inbound Queue",
        "---",
        "",
        "# Antigravity Active Inbound Queue",
        f"**Last Scanned UTC:** `{now_iso}`  ",
        f"**Total Inbound Letters:** `{len(inbound_files)}`  ",
        f"**New / Updated This Tick:** `{len(new_arrivals)}`  ",
        "",
        "## Recent Inbound Letters (Newest 25)",
        "| Arrival / Mtime | Sender | Kind | Filename | Subject |",
        "|---|---|---|---|---|"
    ]
    for fp in inbound_files[:25]:
        st = state.get(fp.name, {})
        sender = st.get("from", "UNKNOWN")
        kind = st.get("kind", "")
        subject = str(st.get("subject", ""))[:60].replace("|", "\\|")
        mtime_str = datetime.fromtimestamp(fp.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M")
        queue_lines.append(f"| {mtime_str} | {sender} | `{kind}` | `{fp.name}` | {subject} |")
    
    queue_content = "\n".join(queue_lines) + "\n"
    try:
        INBOUND_QUEUE_MD.write_text(queue_content, encoding="utf-8")
        if G_INBOUND_QUEUE_MD.parent.exists():
            G_INBOUND_QUEUE_MD.write_text(queue_content, encoding="utf-8")
    except Exception:
        pass

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Autonomous Cross-Trunk Courier & Inbound Dispatcher"
    )
    parser.add_argument("--dry-run", action="store_true", help="Scan without moving or copying files")
    parser.add_argument("--scan-only", action="store_true", help="Scan Antigravity inbound queue only")
    args = parser.parse_args()

    # 1. First-order priority: Scan and catalogue Antigravity's local inbound immediately (NVMe speed)
    scan_antigravity_inbound()
    if args.scan_only:
        return
    
    # 2. Reconcile primary <-> mirror mailboxes
    if not args.dry_run:
        sync_trunk_inbounds()
    
    # 3. Courier outgoing letters across trunks
    print(f"[COURIER] Starting cross-trunk sweep across {len(TRUNK_MAP)} trunks...", flush=True)
    if not args.dry_run:
        scanned, delivered = courier_sweep()
        print(f"[COURIER] Sweep complete. Scanned {scanned} outbox files, delivered {delivered} letters.", flush=True)

if __name__ == "__main__":
    main()
