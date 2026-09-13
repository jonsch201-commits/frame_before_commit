"""
Restore analysis-batch-0.json from the pre-audit knowledge-graph.json (commit b92f213),
then re-run the merge to produce a correct post-audit graph.

Run from repo root: python scripts/rebuild_graph_from_git.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import subprocess
from pathlib import Path

# Step 1: extract pre-audit knowledge-graph.json content from git
result = subprocess.run(
    ['git', 'show', 'b92f213:wiki/.understand-anything/knowledge-graph.json'],
    capture_output=True, text=True, encoding='utf-8'
)
if result.returncode != 0:
    print(f"ERROR: git show failed: {result.stderr}")
    sys.exit(1)

old_kg = json.loads(result.stdout)
print(f"Pre-audit graph: {len(old_kg['nodes'])} nodes, {len(old_kg['edges'])} edges")

# Step 2: extract entities and claims (LLM-analyzed content)
batch_nodes = [n for n in old_kg['nodes'] if n['type'] in ('entity', 'claim')]
batch_edges = [e for e in old_kg['edges'] if e['type'] not in ('related', 'categorized_under')]
print(f"Extracted for batch: {len(batch_nodes)} nodes, {len(batch_edges)} edges")

# Step 3: write analysis-batch-0.json
batch_path = Path('wiki/.understand-anything/intermediate/analysis-batch-0.json')
batch_path.parent.mkdir(parents=True, exist_ok=True)
batch_path.write_text(json.dumps({
    'nodes': batch_nodes,
    'edges': batch_edges
}, indent=2), encoding='utf-8')
print(f"Written: {batch_path}")
print("Now run parse-knowledge-base.py and merge-knowledge-graph.py")
