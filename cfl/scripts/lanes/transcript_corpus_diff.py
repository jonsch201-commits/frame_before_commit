#!/usr/bin/env python3
"""transcript_corpus_diff.py — incremental mirror-corpus refresh (zero-token).

Ratified 2026-07-21 (fable-mirror pipeline, items 9-11 + stub amendments). Sibling of
scripts/lanes/nightly_corpus_delta.py's Leg-1 manifest diff. Does NOT parse anything itself
— it diffs conversations.json on (uuid, updated_at) and shells out to the ONE canonical
extractor, skills/chat-exporter/scripts/convert-export.py, for only the new/changed
conversations. No second extractor.

Why this exists: convert-export.py's own incremental skips a conversation whose 6-char uuid
prefix already has a file, so an UPDATED conversation (new turns) is silently skipped. Keying
on (uuid, updated_at) re-parses edited conversations so the mirror never answers from a stale
transcript.

Corpus location (Jon ruling 2026-07-21): gitignored, on-Drive, never pushed to GitHub. The
manifest lives OFF Drive (MEMORY: Drive-lag stale reads).

Usage:
  python transcript_corpus_diff.py <export-dir> [--out DIR] [--dry-run] [--no-thinking]

Exit codes: 0 = ok / no-op; 2 = thinking-block escalation (see stub amendment i); 1 = error.
"""
import json
import os
import subprocess
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXTRACTOR = REPO / "skills" / "chat-exporter" / "scripts" / "convert-export.py"
DEFAULT_OUT = REPO / "raw" / "sessions" / "claude-ai-transcripts"  # gitignored via raw/
# State (manifest) off Drive — same rationale as the nightly lane.
STATE_DIR = Path(os.environ.get(
    "CFL_TRANSCRIPT_STATE_DIR",
    Path(os.environ.get("LOCALAPPDATA", Path.home())) / "cfl-lanes" / "transcript-corpus"))
MANIFEST = STATE_DIR / "manifest.json"


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def load_conversations(export_dir):
    path = Path(export_dir) / "conversations.json"
    if not path.exists():
        log(f"ERROR: conversations.json not found in {export_dir}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def thinking_diagnostic(convs):
    """Stub amendment (i): every parse reports thinking-block presence. If a non-empty
    export has zero thinking blocks, REFUSE and escalate — never build transcripts-only."""
    total_msgs = 0
    thinking_blocks = 0
    for c in convs:
        for msg in c.get("chat_messages", []):
            total_msgs += 1
            for block in (msg.get("content") or []):
                if isinstance(block, dict) and block.get("type") == "thinking":
                    thinking_blocks += 1
    log(f"DIAGNOSTIC: {len(convs)} conversations, {total_msgs} messages, "
        f"{thinking_blocks} thinking blocks present.")
    if convs and total_msgs > 0 and thinking_blocks == 0:
        log("ESCALATION (stub amendment i): export contains conversations but ZERO thinking "
            "blocks. Jon's belief they are included is [JON/instinct] and appears FALSE for "
            "this export. Refusing to build a transcripts-only corpus silently. Escalate to "
            "Jon — do not proceed until the export schema is reconfirmed.")
        sys.exit(2)
    return thinking_blocks


def current_manifest(convs):
    return {c.get("uuid", ""): c.get("updated_at", "") for c in convs if c.get("uuid")}


def load_prev_manifest():
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            log("WARN: manifest unreadable; treating all conversations as new.")
    return {}


def diff(curr, prev):
    """Return uuids that are new or whose updated_at changed."""
    return [u for u, upd in curr.items() if prev.get(u) != upd]


def run_extractor(export_dir, out_dir, ids, include_thinking):
    args = [sys.executable, str(EXTRACTOR), str(export_dir),
            "--run", "--out", str(out_dir), "--ids", ",".join(ids), "--force"]
    if not include_thinking:
        args.append("--no-thinking")
    log(f"Reparsing {len(ids)} new/changed conversation(s) via convert-export.py …")
    r = subprocess.run(args, cwd=str(REPO))
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("export_dir", help="Unzipped export dir containing conversations.json")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="Corpus dir (gitignored)")
    ap.add_argument("--dry-run", action="store_true", help="Report the delta; write nothing")
    ap.add_argument("--no-thinking", action="store_true",
                    help="Omit thinking blocks (count still recorded in frontmatter)")
    args = ap.parse_args()

    if not EXTRACTOR.exists():
        log(f"ERROR: canonical extractor not found: {EXTRACTOR}")
        sys.exit(1)

    convs = load_conversations(args.export_dir)
    thinking_diagnostic(convs)  # exits 2 on escalation

    curr = current_manifest(convs)
    prev = load_prev_manifest()
    changed = diff(curr, prev)
    new = [u for u in changed if u not in prev]
    updated = [u for u in changed if u in prev]

    log(f"Delta: {len(new)} new, {len(updated)} updated, "
        f"{len(curr) - len(changed)} unchanged.")

    if not changed:
        log("NO-OP: corpus already current for this export.")
        return

    if args.dry_run:
        log("DRY RUN: the following would be (re)parsed:")
        for u in changed:
            log(f"  {u[:6]}  updated_at={curr[u]}  ({'NEW' if u in new else 'UPDATED'})")
        return

    rc = run_extractor(args.export_dir, args.out, changed, not args.no_thinking)
    if rc != 0:
        log(f"ERROR: extractor exited {rc}; manifest NOT advanced.")
        sys.exit(1)

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(curr, indent=0, sort_keys=True), encoding="utf-8")
    watermark = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log(f"Corpus refreshed: {len(changed)} file(s). Manifest advanced. "
        f"Corpus current through export watermark {watermark}.")


if __name__ == "__main__":
    main()
