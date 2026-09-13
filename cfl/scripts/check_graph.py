import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from pathlib import Path
from collections import Counter

kg = json.loads(Path('wiki/.understand-anything/knowledge-graph.json').read_text(encoding='utf-8'))
nodes = {n['id']: n for n in kg['nodes']}

inbound = {}
outbound = {}
for e in kg['edges']:
    outbound.setdefault(e['source'], []).append(e)
    inbound.setdefault(e['target'], []).append(e)

# Topic nodes
print('=== TOPIC NODES ===')
topics = [n for n in kg['nodes'] if n['type'] == 'topic']
for t in sorted(topics, key=lambda x: len(inbound.get(x['id'], [])), reverse=True):
    cat_under = [e for e in inbound.get(t['id'], []) if e['type'] == 'categorized_under']
    print(f"  {t.get('name','?')}: {len(cat_under)} categorized_under")

print()
print('=== FBC INBOUND SOURCES ===')
fbc_id = None
for n in kg['nodes']:
    if n['type'] == 'article' and n.get('name','') == 'frame-before-commit':
        fbc_id = n['id']
        break
if fbc_id:
    in_fbc = [e for e in inbound.get(fbc_id, []) if e['type'] in ('related', 'builds_on', 'supports')]
    print(f'Total inbound (related/builds_on/supports): {len(in_fbc)}')
    for e in sorted(in_fbc, key=lambda x: nodes.get(x['source'], {}).get('name', '')):
        src = nodes.get(e['source'], {})
        print(f"  [{e['type']}] {src.get('name','?')} type={src.get('type','?')}")

print()
print('=== PERSONAL WIKI LAYER CHECK ===')
personal_topic = None
for n in kg['nodes']:
    if n['type'] == 'topic' and 'personal' in n.get('name','').lower():
        personal_topic = n
        print(f"Topic: {n['name']} id={n['id']}")
        cat_edges = [e for e in inbound.get(n['id'], []) if e['type'] == 'categorized_under']
        print(f'categorized_under count: {len(cat_edges)}')
        for e in cat_edges:
            src = nodes.get(e['source'], {})
            print(f"  {src.get('name','?')} type={src.get('type','?')}")
        break

if not personal_topic:
    print('No personal topic node found!')
    for n in kg['nodes']:
        if n['type'] == 'topic':
            print(f"  Topic: {n.get('name','?')}")

print()
print('=== SKILLS-SYSTEM INBOUND ===')
ss_id = None
for n in kg['nodes']:
    if n['type'] == 'article' and n.get('name','').lower() == 'skills-system':
        ss_id = n['id']
        break
if ss_id:
    inbound_ss = [e for e in inbound.get(ss_id, [])]
    print(f'Total inbound: {len(inbound_ss)}')
    for e in sorted(inbound_ss, key=lambda x: nodes.get(x['source'], {}).get('name', '')):
        src = nodes.get(e['source'], {})
        print(f"  [{e['type']}] {src.get('name','?')} type={src.get('type','?')}")

print()
print('=== WIKI-MASTER-ORIGIN INBOUND ===')
wmo_id = None
for n in kg['nodes']:
    if n['type'] == 'article' and 'wiki-master-origin' in n.get('name','').lower():
        wmo_id = n['id']
        break
if wmo_id:
    inbound_wmo = [e for e in inbound.get(wmo_id, [])]
    print(f'Total inbound: {len(inbound_wmo)}')
    for e in sorted(inbound_wmo, key=lambda x: nodes.get(x['source'], {}).get('name', '')):
        src = nodes.get(e['source'], {})
        print(f"  [{e['type']}] {src.get('name','?')} type={src.get('type','?')}")
