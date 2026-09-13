#!/usr/bin/env python3
"""
wiki_agent.py — Local Ollama Wiki Agent
========================================
Runs wiki-master operations (ingest, query, lint, triage) using a local
Ollama model instead of the Anthropic API. Intended for overnight batch
work that doesn't consume Claude Code compute.

Ported from: skills/wiki-master/scripts/pipeline.py
Model: wiki-master (deepseek-r1:32b via Modelfile in this directory)

Usage:
  python scripts/ollama_wiki/wiki_agent.py ingest raw/transcripts/claude-ai/fl/myfile.md
  python scripts/ollama_wiki/wiki_agent.py ingest-zip raw/Anthropic_zips/data-....zip
  python scripts/ollama_wiki/wiki_agent.py query "What does the wiki say about FBC?"
  python scripts/ollama_wiki/wiki_agent.py lint
  python scripts/ollama_wiki/wiki_agent.py run-script scripts/map_conversations.py [args...]

Requirements:
  pip install requests
  ollama serve  (running in background)
  ollama create wiki-master -f scripts/ollama_wiki/Modelfile

Environment:
  OLLAMA_HOST  — Ollama server address (default: http://localhost:11434)
  WIKI_REPO_PATH — path to repo root (default: current directory)
"""

import os
import sys
import json
import zipfile
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

# ── Configuration ──────────────────────────────────────────────────────────────

CONFIG = {
    "model": "wiki-master",
    "ollama_host": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
    "wiki_repo_path": os.environ.get("WIKI_REPO_PATH", "."),
    "auto_commit": True,
    "auto_push": False,
    "request_timeout": 7200,  # seconds — 32B at 1-3 t/s needs up to 60 min per call
}

# Project UUIDs from map_conversations.py — used for zip triage
PROJECT_SLUGS = {
    "019d8279-90ca-7468-8fb1-37534b6daefc": "fl",
    "019cc2fb-0284-77e5-ba27-1a880954817e": "personal",
    "019cc2fc-35c1-72ac-8ca8-7ce60433bc01": "pro",
    "019ca63c-3818-7510-aad8-5db3c583bd40": "how-to-use-claude",
    None: "unassigned",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_repo_path() -> Path:
    return Path(CONFIG["wiki_repo_path"]).resolve()

def read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote: {path.relative_to(get_repo_path())}")

def git_commit(repo_path: Path, message: str):
    if not CONFIG["auto_commit"]:
        return
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  committed: {message}")
        else:
            print(f"  nothing to commit")
        if CONFIG["auto_push"]:
            subprocess.run(["git", "push"], cwd=repo_path, check=True, capture_output=True)
            print("  pushed to origin")
    except subprocess.CalledProcessError as e:
        print(f"  git error: {e}")

def append_log(repo_path: Path, entry: str):
    log_path = repo_path / "wiki" / "log.md"
    date = datetime.now().strftime("%Y-%m-%d")
    line = f"\n## {date} | ollama | {entry}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)

def get_log_tail(repo_path: Path, n: int = 30) -> str:
    log_path = repo_path / "wiki" / "log.md"
    if not log_path.exists():
        return ""
    lines = log_path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[-n:])

def get_existing_slugs(repo_path: Path) -> dict:
    """Return sets of existing slugs for sources, concepts, and entities."""
    slugs = {"sources": set(), "concepts": set(), "entities": set()}
    for category in slugs:
        d = repo_path / "wiki" / category
        if d.exists():
            slugs[category] = {p.stem for p in d.glob("*.md")}
    return slugs

def load_wiki_context(repo_path: Path) -> dict:
    ctx = {
        "schema": read_file_safe(repo_path / "SCHEMA.md"),
        "index": read_file_safe(repo_path / "wiki" / "index.md"),
        "log_tail": get_log_tail(repo_path, n=30),
    }
    slugs = get_existing_slugs(repo_path)
    ctx["existing_source_slugs"] = sorted(slugs["sources"])
    ctx["existing_concept_slugs"] = sorted(slugs["concepts"])
    ctx["existing_entity_slugs"] = sorted(slugs["entities"])
    return ctx

def load_system_prompt() -> str:
    sp_path = Path(__file__).parent / "system_prompt.md"
    return read_file_safe(sp_path)

# ── Ollama API ─────────────────────────────────────────────────────────────────

def call_model(user_message: str) -> str:
    """Call the local Ollama model and return the text response."""
    url = f"{CONFIG['ollama_host']}/api/chat"
    system_prompt = load_system_prompt()

    payload = {
        "model": CONFIG["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 4096,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=CONFIG["request_timeout"])
        resp.raise_for_status()
    except requests.ConnectionError:
        print("ERROR: Cannot connect to Ollama. Is 'ollama serve' running?")
        sys.exit(1)
    except requests.Timeout:
        print(f"ERROR: Request timed out after {CONFIG['request_timeout']}s.")
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"ERROR: Ollama returned HTTP {e.response.status_code}")
        print(e.response.text[:500])
        sys.exit(1)

    data = resp.json()
    return data["message"]["content"]

def parse_json_response(raw: str) -> dict:
    """Strip markdown fences if present and parse JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    # DeepSeek R1 sometimes wraps with <think>...</think> — strip it
    if "<think>" in raw and "</think>" in raw:
        raw = raw.split("</think>", 1)[1].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Model returned invalid JSON: {e}")
        print("Raw response (first 800 chars):\n", raw[:800])
        sys.exit(1)

# ── Script Runner ──────────────────────────────────────────────────────────────

def run_script(script_path: str, *args) -> tuple[int, str, str]:
    """Run a Python script from repo root and return (returncode, stdout, stderr)."""
    repo_path = get_repo_path()
    cmd = [sys.executable, str(repo_path / script_path)] + list(args)
    print(f"  running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout[:2000])
    if result.returncode != 0 and result.stderr:
        print(f"  stderr: {result.stderr[:500]}")
    return result.returncode, result.stdout, result.stderr

# ── Conversation Extraction ────────────────────────────────────────────────────

def slug_from_conv(conv: dict) -> str:
    uuid = conv.get("uuid", "").replace("-", "")[:6]
    date = conv.get("created_at", "")[:10]
    name = conv.get("name") or "untitled"
    slug = name.lower()
    for ch in " /\\:\"'<>|?*,()[]{}":
        slug = slug.replace(ch, "-")
    slug = slug[:60].strip("-")
    return f"chat-{date}-{uuid}-{slug}.md"

def render_message(msg: dict) -> str:
    role = msg.get("sender", "unknown")
    label = "**Human:**" if role == "human" else "**Claude:**"
    ts = msg.get("created_at", "")[:16].replace("T", " ")
    content = ""
    for block in msg.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            content += block.get("text", "")
    return f"{label}\n\n[{ts}]\n\n{content.strip()}"

def conv_to_markdown(conv: dict) -> str:
    name = conv.get("name") or "(unnamed)"
    uuid = conv.get("uuid", "")
    created = conv.get("created_at", "")[:10]
    messages = conv.get("chat_messages", [])
    lines = [f"# {name}", "", f"**UUID:** {uuid}", f"**Date:** {created}", "", "---", ""]
    for msg in messages:
        lines.append(render_message(msg))
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)

def get_known_uuids(repo_path: Path) -> set:
    """
    Return the set of 6-char UUID prefixes already known (processed or screened).

    Primary: full history conversations.json — definitive; anything not in it is new.
    Fallback: scan filenames for 6-char hex strings.
    """
    known = set()

    # Primary: full history export is the authoritative prior-run list
    full_export = repo_path / "raw" / "exports" / "2026-05-12-full" / "conversations.json"
    if full_export.exists():
        with open(full_export, encoding="utf-8") as f:
            all_convs = json.load(f)
        for conv in all_convs:
            uuid6 = conv.get("uuid", "").replace("-", "")[:6]
            if uuid6:
                known.add(uuid6)
        return known

    # Fallback: parse filenames for 6-char hex UUID strings
    # Wiki source filenames end with -YYYY-MM-DD-uuid6 → last segment is uuid6
    for p in (repo_path / "wiki").rglob("*.md"):
        parts = p.stem.split("-")
        candidate = parts[-1]
        if len(candidate) == 6 and all(c in "0123456789abcdef" for c in candidate.lower()):
            known.add(candidate)
    # raw exports: chat-YYYY-MM-DD-uuid6-slug → uuid6 is at index 4
    for p in (repo_path / "raw" / "exports").rglob("chat-*.md"):
        parts = p.stem.split("-")
        if len(parts) >= 5:
            candidate = parts[4]
            if len(candidate) == 6 and all(c in "0123456789abcdef" for c in candidate.lower()):
                known.add(candidate)

    return known

# ── Operations ─────────────────────────────────────────────────────────────────

def op_ingest(source_path_str: str):
    """Ingest a single raw source file into the wiki."""
    repo_path = get_repo_path()
    source_path = Path(source_path_str)
    if not source_path.is_absolute():
        source_path = repo_path / source_path
    if not source_path.exists():
        print(f"ERROR: file not found: {source_path}")
        sys.exit(1)

    source_content = source_path.read_text(encoding="utf-8")
    ctx = load_wiki_context(repo_path)

    # Estimate context size and warn if large
    char_count = len(source_content)
    if char_count > 40_000:
        print(f"  WARNING: source is {char_count:,} chars — may exceed context window. Consider splitting.")

    user_message = f"""
WIKI MASTER PROTOCOL:
{load_system_prompt()}

WIKI SCHEMA:
{ctx['schema']}

CURRENT INDEX:
{ctx['index']}

RECENT LOG:
{ctx['log_tail']}

EXISTING SOURCE SLUGS: {', '.join(ctx['existing_source_slugs'][:50])}
EXISTING CONCEPT SLUGS: {', '.join(ctx['existing_concept_slugs'])}
EXISTING ENTITY SLUGS: {', '.join(ctx['existing_entity_slugs'])}

SOURCE TO INGEST:
Filename: {source_path.name}

Content:
{source_content[:30000]}

Operation: INGEST
Return valid JSON only using the ingest schema defined in the protocol above.
"""

    print(f"\nIngesting: {source_path.name} ({char_count:,} chars)")
    print("  calling Ollama model (this may take several minutes)...")

    raw = call_model(user_message)
    result = parse_json_response(raw)

    print("\nWriting wiki files:")
    write_file(repo_path / result["source_page"]["filename"], result["source_page"]["content"])
    for page in result.get("new_pages", []):
        write_file(repo_path / page["filename"], page["content"])
    for page in result.get("updated_pages", []):
        write_file(repo_path / page["filename"], page["content"])
    if result.get("index_update"):
        write_file(repo_path / result["index_update"]["filename"], result["index_update"]["content"])
    if result.get("overview_update", {}).get("changed"):
        write_file(repo_path / result["overview_update"]["filename"], result["overview_update"]["content"])

    append_log(repo_path, result.get("log_entry", f"ingest | {source_path.stem}"))
    print(f"\nSummary: {result.get('summary', 'no summary provided')}")
    git_commit(repo_path, result.get("commit_message", f"ingest: {source_path.stem}"))


def op_ingest_zip(zip_path_str: str):
    """
    Extract a new Anthropic export zip, identify new conversations,
    triage each one, and ingest approved files.

    Steps:
    1. Extract zip to raw/exports/[timestamp]-partial/
    2. Load conversations.json
    3. Filter by project (default: fl)
    4. Skip conversations already in wiki
    5. Extract each to markdown
    6. Triage (model decides INGEST_FL / INGEST_PERSONAL / SKIP)
    7. Ingest approved files
    """
    repo_path = get_repo_path()
    zip_path = Path(zip_path_str)
    if not zip_path.is_absolute():
        zip_path = repo_path / zip_path
    if not zip_path.exists():
        print(f"ERROR: zip not found: {zip_path}")
        sys.exit(1)

    # Step 1: Extract zip
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    extract_dir = repo_path / "raw" / "exports" / f"{timestamp}-partial"
    extract_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nExtracting {zip_path.name} to {extract_dir.relative_to(repo_path)}")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)

    # Step 2: Find conversations.json
    convs_file = extract_dir / "conversations.json"
    if not convs_file.exists():
        candidates = list(extract_dir.rglob("conversations.json"))
        if not candidates:
            print("ERROR: conversations.json not found in zip.")
            sys.exit(1)
        convs_file = candidates[0]

    print(f"  loading: {convs_file.name}")
    with open(convs_file, encoding="utf-8") as f:
        conversations = json.load(f)
    print(f"  found {len(conversations)} conversations in zip")

    # Step 3 + 4: Identify truly new conversations (not in full history export)
    # Anthropic export format does not include project field per conversation —
    # project mapping is in a separate project-map.json from the live API.
    # Strategy: any conversation whose UUID was NOT in the full history export is new.
    # The triage model classifies FL / personal / skip.
    known = get_known_uuids(repo_path)
    new_convs = []
    for conv in conversations:
        uuid6 = conv.get("uuid", "").replace("-", "")[:6]
        if uuid6 not in known:
            new_convs.append(conv)

    print(f"  {len(new_convs)} new conversations not yet in wiki")
    if not new_convs:
        print("  Nothing to ingest.")
        return

    # Step 5 + 6 + 7: Extract, triage, ingest each
    md_dir = extract_dir / "extracted"
    md_dir.mkdir(exist_ok=True)
    ctx = load_wiki_context(repo_path)

    for conv in new_convs:
        name = conv.get("name", "untitled")
        uuid6 = conv.get("uuid", "").replace("-", "")[:6]
        fname = slug_from_conv(conv)
        md_path = md_dir / fname
        md_content = conv_to_markdown(conv)
        md_path.write_text(md_content, encoding="utf-8")

        char_count = len(md_content)
        print(f"\n── {name} ({uuid6}, {char_count:,} chars) ──")

        # Triage: ask model to decide INGEST_FL / INGEST_PERSONAL / SKIP
        triage_msg = f"""
WIKI MASTER PROTOCOL:
{load_system_prompt()}

CURRENT INDEX (summary):
Sources: {len(ctx['existing_source_slugs'])} existing
Concepts: {', '.join(ctx['existing_concept_slugs'][:20])}

CONVERSATION TO TRIAGE:
Filename: {fname}

Content (first 8000 chars):
{md_content[:8000]}

Operation: TRIAGE
Return JSON: {{"decision": "INGEST_FL" | "INGEST_PERSONAL" | "SKIP", "reason": "one sentence"}}
"""
        print("  triaging...")
        raw = call_model(triage_msg)
        triage = parse_json_response(raw)
        decision = triage.get("decision", "SKIP")
        reason = triage.get("reason", "no reason given")
        print(f"  decision: {decision} — {reason}")

        if decision == "SKIP":
            continue

        # Ingest it
        print("  ingesting...")
        op_ingest(str(md_path))

    print(f"\nZip ingest complete.")


def op_query(question: str):
    """Query the wiki for a synthesized answer."""
    repo_path = get_repo_path()
    ctx = load_wiki_context(repo_path)

    # Load log + index only — sufficient for most queries; keeps prompt short at 1-3 t/s
    log_content = read_file_safe(repo_path / "wiki" / "log.md")
    index_content = read_file_safe(repo_path / "wiki" / "index.md")
    pages_context = f"=== wiki/log.md ===\n{log_content}\n\n=== wiki/index.md ===\n{index_content}"

    user_message = f"""
WIKI MASTER PROTOCOL:
{load_system_prompt()}

WIKI CONTENTS:
{pages_context}

QUESTION: {question}

Operation: QUERY
Return valid JSON using the query schema defined in the protocol above.
"""

    print(f"\nQuerying: {question[:80]}...")
    print("  calling Ollama model...")
    raw = call_model(user_message)
    result = parse_json_response(raw)

    print(f"\n── ANSWER ──────────────────────────────────────────────────────")
    print(result.get("answer", "no answer"))
    print(f"────────────────────────────────────────────────────────────────")
    print(f"Pages consulted: {result.get('pages_consulted', [])}")

    if result.get("file_answer") and result.get("filed_page"):
        page = result["filed_page"]
        write_file(repo_path / page["filename"], page["content"])
        append_log(repo_path, result.get("log_entry", "query | filed analysis"))
        git_commit(repo_path, f"query: filed analysis {Path(page['filename']).stem}")
    else:
        append_log(repo_path, result.get("log_entry", f"query | {question[:60]}"))


def op_lint():
    """Run a lint pass on the wiki."""
    repo_path = get_repo_path()

    wiki_dir = repo_path / "wiki"
    pages_context = ""
    if wiki_dir.exists():
        for md_file in sorted(wiki_dir.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            rel = str(md_file.relative_to(repo_path))
            pages_context += f"\n\n=== {rel} ===\n{content[:400]}"

    user_message = f"""
WIKI MASTER PROTOCOL:
{load_system_prompt()}

WIKI PAGES (truncated for lint):
{pages_context[:20000]}

Operation: LINT
Return valid JSON using the lint schema defined in the protocol above.
"""

    print("\nRunning lint pass...")
    print("  calling Ollama model...")
    raw = call_model(user_message)
    result = parse_json_response(raw)

    print("\n── LINT REPORT ─────────────────────────────────────────────────")
    if result.get("orphan_pages"):
        print(f"Orphans ({len(result['orphan_pages'])}): {result['orphan_pages']}")
    if result.get("unresolved_conflicts"):
        print(f"Conflicts: {result['unresolved_conflicts']}")
    if result.get("missing_concept_pages"):
        print(f"Missing pages: {result['missing_concept_pages']}")
    print(f"\n{result.get('summary', '')}")
    print(f"────────────────────────────────────────────────────────────────")

    for fix in result.get("index_fixes", []):
        write_file(repo_path / fix["filename"], fix["content"])

    append_log(repo_path, result.get("log_entry", "lint | completed"))
    if result.get("index_fixes"):
        git_commit(repo_path, "lint: index fixes applied")


def op_run_script(script_and_args: list):
    """Run a repo script directly and log the operation."""
    if not script_and_args:
        print("ERROR: specify a script path. Example: run-script scripts/map_conversations.py")
        sys.exit(1)
    script = script_and_args[0]
    args = script_and_args[1:]
    returncode, stdout, stderr = run_script(script, *args)
    if returncode == 0:
        print("  script completed successfully.")
    else:
        print(f"  script exited with code {returncode}")


# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ollama Wiki Agent")
    parser.add_argument(
        "operation",
        choices=["ingest", "ingest-zip", "query", "lint", "run-script"],
        help="Operation to perform"
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Source path (ingest/ingest-zip), question (query), or script path (run-script)"
    )
    parser.add_argument("--repo-path", help="Override WIKI_REPO_PATH")
    parser.add_argument("--model", help="Override Ollama model name (default: wiki-master)")
    parser.add_argument("--no-commit", action="store_true", help="Skip git commits")
    parser.add_argument("--push", action="store_true", help="Push after commit")
    parser.add_argument("--all-projects", action="store_true",
                        help="For ingest-zip: include personal project conversations (default: fl only)")
    args = parser.parse_args()

    if args.repo_path:
        CONFIG["wiki_repo_path"] = args.repo_path
    if args.model:
        CONFIG["model"] = args.model
    if args.no_commit:
        CONFIG["auto_commit"] = False
    if args.push:
        CONFIG["auto_push"] = True

    op = args.operation
    rest = args.args

    if op == "ingest":
        if not rest:
            print("ERROR: ingest requires a source path.")
            sys.exit(1)
        op_ingest(rest[0])

    elif op == "ingest-zip":
        if not rest:
            print("ERROR: ingest-zip requires a zip file path.")
            sys.exit(1)
        op_ingest_zip(rest[0])

    elif op == "query":
        if not rest:
            print("ERROR: query requires a question string.")
            sys.exit(1)
        op_query(" ".join(rest))

    elif op == "lint":
        op_lint()

    elif op == "run-script":
        op_run_script(rest)


if __name__ == "__main__":
    main()
