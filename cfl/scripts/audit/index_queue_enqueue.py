#!/usr/bin/env python3
"""index_queue_enqueue.py — PostToolUse hook on Write/Edit: enqueue the
written path for graphrag indexing. GR-1.

Jon, verbatim, the ticket this fixes: "does writing to the exchange hook raw
md updates so vector embeded graph rag can function as intended yet so all
trunks can ground while reading?" -> the answer was NO (nothing wrote to the
index queue on a wiki/exchange write; the index only ever moved on a manual
or scheduled `build_index.py` run, so a page written mid-session was
unreachable to retrieval until someone remembered to rebuild). This hook is
the fix's first half: it makes every wiki/exchange write SELF-QUEUING.

BUDGET, and it is the whole design constraint: PostToolUse hooks share a
30s ceiling across every entry in the matcher's chain (see .claude/settings.json,
H-3's note). This script's OWN target is under 1s (measured, see report) and
it does ZERO indexing work itself -- indexing (embedding, sqlite writes) is
the drain's job (index_queue_drain.py), run out-of-band. Enqueue is an
append of one JSON line; nothing here touches the graphrag index file.

Reads the hook payload from stdin (tool_input.file_path), same convention as
exchange_write_check.py. For a path under wiki/** or exchange/** (and NOT
under exchange/su-close/ -- the ledger this hook itself writes, or the queue
would enqueue its own queue-file writes forever), appends one line
{ts, path, sha256} to exchange/su-close/INDEX-QUEUE.jsonl (append-only,
never rewritten -- the drain marks rows DRAINED by appending a second row,
never by rewriting this one).

Exits 0 always. A hook that can block a write over an indexing concern is a
defect this program has already named (over-gating); this one only ever
records, never refuses.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "exchange" / "su-close" / "INDEX-QUEUE.jsonl"


def sha256_of(path: Path) -> str:
    try:
        digest = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return ""


def in_scope(rel_parts) -> bool:
    if not rel_parts:
        return False
    top = rel_parts[0]
    if top not in ("wiki", "exchange"):
        return False
    # Never enqueue writes to the queue's own ledger (or its sibling su-close
    # machinery) -- that would self-trigger forever and the drain's own
    # DRAINED rows would re-enqueue themselves.
    if top == "exchange" and len(rel_parts) > 1 and rel_parts[1] == "su-close":
        return False
    return True


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # fail VISIBLE-but-silent: an unparseable payload cannot be enqueued,
        # but this is a best-effort convenience hook, not a fence -- it must
        # never block or noisily fail the write it is riding on.
        return 0

    fp = (payload.get("tool_input") or {}).get("file_path", "")
    if not fp:
        return 0
    p = Path(fp)
    try:
        rel = p.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return 0
    if p.suffix != ".md":
        return 0
    if not in_scope(rel.parts):
        return 0

    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "path": str(rel).replace("\\", "/"),
        "sha256": sha256_of(p),
    }
    try:
        QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(QUEUE_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        # best-effort: a queue write failure must not surface as a blocked
        # tool use -- exit 0 regardless, same discipline as the try above.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
