#!/usr/bin/env python3
"""THE DEMO THE SECRETARY ASKED TO BE RUN IN FRONT OF THE ROOM.

Their words (`secretary-GRAPHRAG-V0-DUE-TONIGHT-...`, §2.5), and the queries are theirs verbatim:

    "ACCEPTANCE, and it must be run in front of the room: query with Jon's own misspellings --
     "vector embeding", "stylomantic difference between trunks", "fense is wider than you assume",
     "blocer questions" -- and retrieve the correct page. ⛔ `grep` for those exact strings must
     FAIL on at least the ones that are typos, or the demo has not shown why the index exists."

⚠️ This file asserts NO expected page, on purpose. `acceptance.py` is the graded test with ground
truth; this is the room demo, and its job is to show what comes back and what grep does with the
same string. A demo that hid a bad result behind a pass/fail summary would be worth nothing here.
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrieve import DEFAULT_DB, Index  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

QUERIES = [
    "vector embeding",
    "stylomantic difference between trunks",
    "fense is wider than you assume",
    "blocer questions",
]


def literal_grep(pattern: str) -> int:
    """The control: what the tooling we already own returns for this exact string."""
    try:
        out = subprocess.run(
            ["git", "grep", "-c", "-i", "-F", pattern, "--", "wiki", "CLAUDE.md"],
            cwd=REPO, capture_output=True, text=True, timeout=120)
        return len([ln for ln in out.stdout.splitlines() if ln.strip()])
    except Exception as exc:  # a control that errors is UNKNOWN, never a pass
        print(f"   (grep control unavailable: {exc})")
        return -1


def main() -> int:
    idx = Index(DEFAULT_DB)
    stale, why = idx.staleness()
    secs = idx.meta.get("build_seconds")
    print(f"index    : {idx.n_chunks} chunks · {idx.meta.get('embedder')} "
          f"({idx.meta.get('dims')}d) · built {idx.meta.get('built_utc')} "
          f"in {secs + 's' if secs else '(not recorded by this build)'} · "
          f"{os.path.getsize(DEFAULT_DB) / 1e6:.1f} MB")
    print(f"staleness: {'⚠️ STALE -- ' + why if stale else 'FRESH (corpus fingerprint matches)'}\n")

    for query in QUERIES:
        hits = literal_grep(query)
        order, expansions, _ = idx.hybrid(query, None, 3)
        meta = idx.chunk_rows([c for c, _ in order])
        control = ("0 files -- EXACT SEARCH FINDS NOTHING" if hits == 0
                   else f"{hits} files (this string IS present literally)" if hits > 0
                   else "UNKNOWN")
        print(f'Q: "{query}"')
        print(f"   git grep -F : {control}")
        for rank, (cid, info) in enumerate(order, start=1):
            m = meta.get(cid, {})
            print(f"   {rank}. {m.get('path')}:{m.get('start_line')}-{m.get('end_line')}"
                  f"   [chunk#{info.get('dense') or '-'} doc#{info.get('doc') or '-'} "
                  f"lex#{info.get('lex') or '-'}]")
            if m.get("heading"):
                print(f"      § {m['heading'][:88]}")
            print(f"      {' '.join(m.get('text', '').split())[:150]}")
        for tok, cands in expansions.items():
            fuzzy = [(t, w) for t, w in cands if w < 1.0]
            if fuzzy:
                print(f"      typo bridge: {tok} -> "
                      + ", ".join(f"{t}:{w}" for t, w in fuzzy[:3]))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
