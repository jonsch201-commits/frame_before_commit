import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from pathlib import Path
from collections import Counter

kg = json.loads(Path('wiki/.understand-anything/knowledge-graph.json').read_text(encoding='utf-8'))
nodes = {n['id']: n for n in kg['nodes']}
edge_count = Counter()
for e in kg['edges']:
    edge_count[e['source']] += 1
    edge_count[e['target']] += 1

top = sorted([(edge_count[n['id']], n.get('name','?')) for n in kg['nodes'] if n['type']=='article'], reverse=True)[:15]
print('TOP 15 ARTICLE HUBS (post-audit):')
for cnt, name in top:
    print(f'{cnt:3d}  {name}')

print()
total_nodes = len(kg['nodes'])
total_edges = len(kg['edges'])
print(f'Total nodes: {total_nodes}')
print(f'Total edges: {total_edges}')
