#!/usr/bin/env python3
# ⛔ ONE HOME FOR THE GRAPH. This file hardcoded %LOCALAPPDATA%/claude/graphrag and would NOT
# have followed CFL_GRAPHRAG_HOME -- [measured 2026-09-12 23:1x] seven scripts had that bug,
# so setting the variable would have pointed the BUILDER at a new disk while every READER
# stayed on the old one, each reporting success. See scripts/lib/graphrag_home.py.
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "lib"))
from graphrag_home import DB as _GRAPHRAG_DB  # noqa: E402

r"""index_queue_drain.py — drain exchange/su-close/INDEX-QUEUE.jsonl into the
graphrag index. GR-1, half two.

Half one (index_queue_enqueue.py, a PostToolUse hook) appends {ts, path,
sha256} rows for every wiki/exchange Write/Edit, in under a second, doing NO
indexing itself. This script is the out-of-band consumer: it reads the
queue, DEDUPES BY PATH (a page can be written several times between drains;
only the newest row matters), calls the existing incremental `--include`
upsert (scripts/graphrag/build_index.py -- proven idempotent-by-content-hash
and per-path-replacing in RP-28/RP-28-fix and this lane's own timing test,
see wiki/intake-triage/R3R4-gr1-2026-09-02.md) for every pending path that
still exists on disk, and appends one DRAINED row per path back onto the
SAME append-only ledger -- never rewriting an existing line. A path whose
file has since vanished from disk is reported SKIPPED-MISSING and drained
(there is nothing to index; a future write re-enqueues it).

"Pending" = a path whose most recent row in the ledger, in file order, is an
enqueue row (no "event" key) rather than a DRAINED row. This makes the
ledger the single source of truth for what still needs draining -- no
separate cursor file that could itself drift from the ledger.

⛔ CROSS-ROOT GUARD, added 2026-09-02 after this script destroyed most of the
production index in its own first real-target test run. build_index.py's
corpus_files() does a FULL DEFAULT WALK of `root` on every call (--include
only WIDENS it); root defaults to wherever build_index.py itself resolves
its REPO constant, i.e. THIS invocation's working tree. Pointing --db at an
index that was built from a DIFFERENT tree (e.g. this lane's clone
N:\claude-cfl\clone calling --db against the production index built from
G:\...\claude-foundational-layer) makes every file that exists in the OTHER
tree but not this one look "gone" -- and build_index.py deletes a gone
file's rows (files/chunks/vectors/edges) as designed. Measured: a single
--include drain from the clone against the G:\ production index dropped it
from 5,986 to 1,989 files in one call, exit 0, no warning. Restored from
`index.sqlite.bak-2026-09-02` (byte-identical, sha256 verified) the same
session. So: before calling build_index.py, this script reads the target
db's `meta.corpus_root` and refuses (exit 3) unless it matches this
invocation's own resolved ROOT, or --allow-cross-root is passed explicitly.
This is a SAFETY GATE, not a correctness fix for build_index.py itself --
that script's contract (full walk of `root`, `--include` widens it) is
correct and documented; the hazard is only in POINTING it at an index built
from elsewhere without saying so.

Usage:
  python scripts/audit/index_queue_drain.py [--db PATH] [--dry-run] [--allow-cross-root]
Exit codes: 0 drained (or nothing pending) · 1 the underlying build_index.py
call failed (queue rows are NOT marked drained in that case, so the next
drain retries them) · 2 the queue file could not be read · 3 the target
index's corpus_root does not match this invocation's tree (cross-root guard).
"""
import argparse
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "exchange" / "su-close" / "INDEX-QUEUE.jsonl"
BUILD_SCRIPT = ROOT / "scripts" / "graphrag" / "build_index.py"


def default_db_path() -> str:
    import os
    return str(_GRAPHRAG_DB)


def corpus_root_of(db_path: str) -> str | None:
    """The tree a built index's rows currently claim to describe, or None if
    unreadable/absent (a brand-new or not-yet-built index has no rows to
    protect -- the guard does not apply)."""
    try:
        con = sqlite3.connect(db_path)
        row = con.execute("SELECT value FROM meta WHERE key='corpus_root'").fetchone()
        con.close()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def read_queue():
    if not QUEUE_PATH.exists():
        return []
    rows = []
    with open(QUEUE_PATH, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                # a corrupt line does not stop the drain; it is reported and
                # skipped -- append-only ledgers accumulate exactly one bad
                # line under a concurrent-write race and this must not brick
                # every future drain over it.
                print(f"WARN unparseable queue line {lineno}, skipped", file=sys.stderr)
    return rows


def pending_paths(rows):
    """Return {path: latest_enqueue_row} for every path whose most recent
    ledger row (in file order) is an enqueue, not a DRAINED marker."""
    last = {}
    for row in rows:
        path = row.get("path")
        if not path:
            continue
        last[path] = row  # later rows overwrite earlier ones, in file order
    return {p: r for p, r in last.items() if r.get("event") != "drained"}


def append_drained(path: str, note: str):
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "path": path,
        "event": "drained",
        "note": note,
    }
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=None, help="passed through to build_index.py --db")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be drained; write no DRAINED rows, run no index build")
    ap.add_argument("--allow-cross-root", action="store_true",
                    help="bypass the cross-root guard (see module docstring) -- only for a "
                         "deliberate cross-trunk index, never the default")
    args = ap.parse_args()

    effective_db = args.db or default_db_path()
    existing_root = corpus_root_of(effective_db)
    this_root = str(ROOT).replace("\\", "/")
    if existing_root and existing_root.rstrip("/") != this_root.rstrip("/") and not args.allow_cross_root:
        print(f"REFUSED cross-root guard: {effective_db}\n"
              f"  index corpus_root = {existing_root}\n"
              f"  this invocation's root = {this_root}\n"
              f"  Draining from a different tree than the index was built over deletes every "
              f"row for a file this tree does not see (measured: 5,986 -> 1,989 files, one call). "
              f"Pass --allow-cross-root only if this is deliberate.", file=sys.stderr)
        return 3

    try:
        rows = read_queue()
    except OSError as exc:
        print(f"FAIL cannot read queue: {exc}", file=sys.stderr)
        return 2

    pending = pending_paths(rows)
    print(f"queue rows read: {len(rows)}; unique pending paths: {len(pending)}")
    if not pending:
        print("nothing pending, exit 0")
        return 0

    existing, missing = [], []
    for path in sorted(pending):
        full = ROOT / path
        (existing if full.is_file() else missing).append(path)

    for path in missing:
        print(f"SKIPPED-MISSING {path} (file no longer on disk)")
        if not args.dry_run:
            append_drained(path, "skipped-missing")

    if args.dry_run:
        print(f"DRY-RUN: would index {len(existing)} path(s): "
              + ", ".join(existing[:10]) + (" ..." if len(existing) > 10 else ""))
        return 0

    if not existing:
        print("no existing paths to index; drained missing-only, exit 0")
        return 0

    cmd = [sys.executable, str(BUILD_SCRIPT)]
    if args.db:
        cmd += ["--db", args.db]
    for path in existing:
        cmd += ["--include", path]

    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=ROOT)
        elapsed = time.time() - t0
    except Exception as exc:
        print(f"FAIL build_index.py invocation raised: {exc}", file=sys.stderr)
        return 1

    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    print(f"build_index.py exit={r.returncode}, elapsed={elapsed:.1f}s")

    if r.returncode != 0:
        # DO NOT mark drained -- SKIPPED-never-PASS semantics for the caller
        # (postcompact_pipeline.py step). Rows stay pending for the next run.
        print(f"FAIL build_index.py exit={r.returncode}; rows left pending for next drain",
              file=sys.stderr)
        return 1

    for path in existing:
        append_drained(path, f"indexed (build exit 0, {elapsed:.1f}s batch)")

    print(f"DRAINED {len(existing)} path(s), {len(missing)} missing, "
          f"{elapsed:.1f}s total build time")
    return 0


if __name__ == "__main__":
    sys.exit(main())
