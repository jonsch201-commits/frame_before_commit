#!/usr/bin/env python3
"""
scripts/query_federated.py — Fast Zero-Dependency Federated GraphRAG Query Client

Target: ~20-30ms query latency across the 60,000+ document GraphRAG index.
Runs across all trunks with zero external dependencies (stdlib only: sqlite3, json, sys, pathlib).

Supports:
  - FTS5 full-text keyword retrieval with BM25 ranking.
  - Multi-trunk courier deduplication (collapses 5 identical deliveries into 1 slot).
  - --dialogue filter (searches only live Jon dialogue turns).
  - --transcripts filter (searches Antigravity execution steps, tool calls, and parser errors).
  - --edges for 1-hop topological knowledge graph inspection.
  - Programmatic API via quick_query().
"""

import sys
import json
import sqlite3
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

CANDIDATE_PATHS = [
    Path(r"N:\claude-indexes\graphrag-federated\index.sqlite"),
    Path(r"N:\antigravity-hub\.cache\index.sqlite"),
    Path(r"G:\My Drive\Claude\Antigravity\.cache\index.sqlite"),
]

def find_index_db(explicit_path: Optional[Path] = None) -> Path:
    if explicit_path:
        if explicit_path.exists():
            return explicit_path
        raise FileNotFoundError(f"Specified database not found: {explicit_path}")
    for p in CANDIDATE_PATHS:
        if p.exists():
            return p
    raise FileNotFoundError(f"Federated index not found in candidate paths: {[str(p) for p in CANDIDATE_PATHS]}")

def sanitize_fts_query(query: str) -> str:
    """Sanitize query string into safe FTS5 syntax and expand shell operator tokens."""
    has_shell_tokens = "&&" in query or "||" in query or "cmdlet" in query or "powershell" in query.lower()
    cleaned = re.sub(r'["\'\*\^\(\)\[\]\{\}\:\;\~]', ' ', query)
    tokens = [w.strip() for w in cleaned.split() if w.strip()]
    
    if has_shell_tokens:
        tokens.extend(["ParserError", "TerminatorExpectedAtEndOfString"])

    if not tokens:
        return '""'
    meaningful = [w for w in tokens if len(w) > 1 and w.lower() not in STOPWORDS]
    if not meaningful:
        meaningful = tokens
    return " OR ".join(f'"{t}"' for t in set(meaningful))

def normalize_title_for_dedupe(title: str, slug: str) -> str:
    """Extract a canonical title or base slug to identify courier replications."""
    t = (title or "").strip()
    if t:
        # Strip trunk prefix if present
        t = re.sub(r'^(?:cfl|pro|secretary|personal|soul|antigravity)\s*[-:]\s*', '', t, flags=re.I)
        return t.lower()
    return Path(slug).name.lower()

def query_index(
    conn: sqlite3.Connection,
    query_str: str,
    limit: int = 8,
    dialogue_only: bool = False,
    transcripts_only: bool = False,
    include_edges: bool = False,
    dedupe: bool = True
) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    fts_q = sanitize_fts_query(query_str)

    cur.execute("PRAGMA table_info(docs_meta)")
    has_created_at = any(col[1] == "created_at" for col in cur.fetchall())
    created_at_col = "d.created_at," if has_created_at else "NULL AS created_at,"

    sql = f"""
        SELECT 
            d.slug,
            d.trunk,
            d.title,
            d.kind,
            d.status,
            {created_at_col}
            snippet(docs_fts, 3, '>>', '<<', '...', 25) AS snippet
        FROM docs_fts
        JOIN docs_meta d ON d.slug = docs_fts.slug
        WHERE docs_fts MATCH ?
    """
    params = [fts_q]

    if dialogue_only:
        sql += " AND d.slug LIKE 'Dialogue:%'"
    elif transcripts_only:
        sql += " AND d.slug LIKE 'Transcript:%'"

    # Overfetch candidates to allow deduplication of redundant courier copies
    fetch_limit = limit * 4 if dedupe else limit
    sql += " ORDER BY rank LIMIT ?"
    params.append(fetch_limit)

    rows = cur.execute(sql, params).fetchall()
    results = []
    seen_titles: Dict[str, Dict[str, Any]] = {}

    for r in rows:
        slug = r["slug"]
        trunk = r["trunk"]
        title = r["title"]
        kind = r["kind"]
        status = r["status"]
        created_at = r["created_at"] if "created_at" in r.keys() and r["created_at"] else None
        snip = (r["snippet"] or "").replace("\n", " ")

        if dedupe and not transcripts_only and not dialogue_only:
            norm_key = normalize_title_for_dedupe(title, slug)
            if norm_key in seen_titles:
                entry = seen_titles[norm_key]
                if trunk not in entry["all_trunks"]:
                    entry["all_trunks"].append(trunk)
                continue

        edges = []
        if include_edges:
            edge_rows = cur.execute("""
                SELECT target_slug, kind FROM edges 
                WHERE source_slug = ?
                LIMIT 5
            """, (slug,)).fetchall()
            edges = [{"target": er[0], "kind": er[1]} for er in edge_rows]

        res_item = {
            "slug": slug,
            "trunk": trunk,
            "all_trunks": [trunk],
            "title": title,
            "kind": kind,
            "status": status,
            "created_at": created_at,
            "snippet": snip,
            "edges": edges
        }

        if dedupe and not transcripts_only and not dialogue_only:
            seen_titles[norm_key] = res_item

        results.append(res_item)
        if len(results) >= limit:
            break

    return results

def quick_query(
    query_str: str, 
    limit: int = 5, 
    dialogue_only: bool = False, 
    transcripts_only: bool = False,
    include_edges: bool = False, 
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """One-line programmatic query helper for Antigravity, subagents, and scripts."""
    db = find_index_db(db_path)
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    try:
        return query_index(
            conn, 
            query_str, 
            limit=limit, 
            dialogue_only=dialogue_only, 
            transcripts_only=transcripts_only,
            include_edges=include_edges
        )
    finally:
        conn.close()

def print_status(conn: sqlite3.Connection, db_path: Path):
    cur = conn.cursor()
    docs = cur.execute("SELECT COUNT(*) FROM docs_meta").fetchone()[0]
    edges = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    fts_cnt = cur.execute("SELECT COUNT(*) FROM docs_fts").fetchone()[0]
    dialogues = cur.execute("SELECT COUNT(*) FROM docs_meta WHERE slug LIKE 'Dialogue:%'").fetchone()[0]
    transcripts = cur.execute("SELECT COUNT(*) FROM docs_meta WHERE slug LIKE 'Transcript:%'").fetchone()[0]
    symbols = cur.execute("SELECT COUNT(*) FROM symbols").fetchone()[0] if cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='symbols'").fetchone()[0] else 0
    
    meta_rows = cur.execute("SELECT key, value FROM meta").fetchall()
    build_state = "UNKNOWN"
    build_utc = "UNKNOWN"
    for r in meta_rows:
        k, v = r[0], r[1]
        if k == "build_state": build_state = v
        if k == "build_settled_utc": build_utc = v

    print(f"=== Federated GraphRAG Index Status ===")
    print(f"  Database Path:     {db_path}")
    print(f"  Build State:       {build_state} ({build_utc})")
    print(f"  Total Documents:   {docs:,} (FTS5 matched: {fts_cnt:,})")
    print(f"  Exact Symbols:     {symbols:,}")
    print(f"  Total Edges:       {edges:,}")
    print(f"  Live Dialogue:     {dialogues:,} turns")
    print(f"  Session Steps:     {transcripts:,} steps")

def main():
    parser = argparse.ArgumentParser(description="Query the federated GraphRAG index across all fleet trunks.")
    parser.add_argument("query", nargs="?", default="", help="Search query string")
    parser.add_argument("--db", type=Path, default=None, help="Explicit path to index.sqlite")
    parser.add_argument("--limit", "-k", type=int, default=8, help="Number of results to return (default: 8)")
    parser.add_argument("--dialogue", action="store_true", help="Filter strictly for live Jon dialogue turns")
    parser.add_argument("--transcripts", action="store_true", help="Filter strictly for Antigravity transcript/log steps")
    parser.add_argument("--no-dedupe", action="store_true", help="Disable courier duplicate collapsing")
    parser.add_argument("--edges", action="store_true", help="Include 1-hop graph edges for each match")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--status", action="store_true", help="Show index status and row counts")
    args = parser.parse_args()

    try:
        db_path = find_index_db(args.db)
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    try:
        if args.status or not args.query.strip():
            print_status(conn, db_path)
            if not args.query.strip():
                return

        results = query_index(
            conn, 
            args.query, 
            limit=args.limit, 
            dialogue_only=args.dialogue, 
            transcripts_only=args.transcripts,
            include_edges=args.edges,
            dedupe=not args.no_dedupe
        )

        if args.json:
            print(json.dumps(results, indent=2))
            return

        print(f"\n=== Query: '{args.query}' ({len(results)} hits from {db_path.name}) ===")
        if not results:
            print("  No matching documents found.")
            return

        for i, res in enumerate(results, 1):
            trunk = res["trunk"]
            all_trunks = res.get("all_trunks", [trunk])
            trunk_display = trunk if len(all_trunks) <= 1 else f"{trunk} (+{', '.join(t for t in all_trunks if t != trunk)})"
            slug = res["slug"]
            title = res["title"]
            snip = res["snippet"]
            print(f"\n{i}. [{trunk_display}] {slug} — \"{title}\"")
            print(f"   {snip}")
            if res["edges"]:
                edge_str = ", ".join(f"{e['kind']} -> {e['target']}" for e in res["edges"])
                print(f"   Edges: {edge_str}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
