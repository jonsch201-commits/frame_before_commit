"""ONE place that decides where the graph lives. Import it; never re-derive the path.

Jon, 2026-09-12 ~23:1x CDT, verbatim: *"why the fuck does the graph live on C?"*

THE ANSWER, from the record rather than from memory. `wiki/concepts/graphrag-retrieval.md`:
*"off Drive, `%LOCALAPPDATA%\\claude\\graphrag\\`. The first build wrote to `wiki/.graphrag/` on Drive
and was still running at 14 minutes / 60 MB of journal churn; the identical build off Drive took 61
seconds — a >13x difference."* `%LOCALAPPDATA%` was simply the conventional not-Drive location.

⛔ **THAT CHOICE PREDATES N: BEING THE WORKING TREE.** The tree moved to `N:\\claude-cfl\\clone` on
2026-09-02 and the index never followed. `[measured 2026-09-12 23:0x]` C: is 465 GB with **53.4 GB
free**; N: is a local fixed NTFS volume of 1,863 GB with **1,769.9 GB free**, 5% used. The provenance
reduction that loses 544.2 MB of raw conversation is downstream of a placement nobody re-examined.

⛔ **AND THE KNOB THAT WAS SUPPOSED TO MAKE THE MOVE POSSIBLE DID NOT COVER THE FLEET.**
`build_index.py` has honoured `CFL_GRAPHRAG_HOME` since it was written, and `[measured 23:1x]` SEVEN
other scripts hardcode `LOCALAPPDATA/claude/graphrag` and would not follow it -- `index_coverage.py`,
`index_queue_drain.py`, `postcompact_pipeline.py`, `recover_from_index.py` (written twenty minutes
earlier, by me), `session_in_graph.py`, `terms_oracle_check.py`, `verdict_provenance_lint.py`.
⭐ **So setting the variable alone would have pointed the BUILDER at N: while every READER stayed on
C:, and each would have reported success.** That is the `wake.md` two-homes failure with a database
instead of a markdown file: a fix that lands in one of several copies and prints a green.

**This module is the single home. A path derived any other way is a bug.**

    from graphrag_home import HOME, DB          # HOME: Path, DB: Path to index.sqlite
    from graphrag_home import resolve_db        # resolve_db(explicit_or_None) -> Path

⚠️ **`where()` reports EVERY candidate it can see and says which one is live**, so a seat that is
reading a stale copy on the old disk finds out by running one command instead of by being wrong.
"""
import os
import sys
from pathlib import Path

ENV = "CFL_GRAPHRAG_HOME"
# Known homes, newest intent first. This is a MIGRATION table, not a search path: `HOME` is exactly
# one of these, and the rest exist so `where()` can name a stale copy instead of ignoring it.
KNOWN = (
    Path("N:/claude-graphrag"),
    Path(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.cache")) / "claude" / "graphrag",
)


def home() -> Path:
    """The live home: the env override if set, else the first KNOWN home that holds an index,
    else the last KNOWN home (the historical default) so a first build still has somewhere to go."""
    env = os.environ.get(ENV)
    if env:
        return Path(env)
    for cand in KNOWN:
        if (cand / "index.sqlite").is_file():
            return cand
    return KNOWN[-1]


HOME = home()
DB = HOME / "index.sqlite"


def resolve_db(explicit=None) -> Path:
    """An explicit --db wins; otherwise the live home. Never falls back silently to another disk."""
    return Path(explicit) if explicit else DB


def where():
    """Every candidate, its size, and which is live. Returns a list of (path, bytes, is_live)."""
    live = HOME / "index.sqlite"
    rows = []
    seen = set()
    for cand in (Path(os.environ[ENV]) if os.environ.get(ENV) else None,) + KNOWN:
        if cand is None or str(cand) in seen:
            continue
        seen.add(str(cand))
        db = cand / "index.sqlite"
        try:
            size = db.stat().st_size if db.is_file() else 0
        except OSError:
            size = -1
        rows.append((db, size, db == live))
    return rows


def main():
    print(f"{ENV} = {os.environ.get(ENV) or '(unset)'}")
    print(f"live home    = {HOME}")
    print()
    for db, size, is_live in where():
        mark = "LIVE   " if is_live else "       "
        if size > 0:
            print(f"  {mark} {size/1e9:6.2f} GB  {db}")
        elif size == 0:
            print(f"  {mark}      --  {db}   (no index here)")
        else:
            print(f"  {mark} UNKNOWN  {db}   (unreadable -- never treat as absent)")
    stale = [db for db, size, is_live in where() if size > 0 and not is_live]
    if stale:
        print()
        print("⚠️ A COPY EXISTS OFF THE LIVE HOME. Until it is removed by a decision (never by a"
              " sweep), any script that hardcodes its path is reading a different database than the"
              " builder writes:")
        for db in stale:
            print(f"     {db}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
