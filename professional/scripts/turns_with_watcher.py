import json, sys
# usage: python turns_with_watcher.py <jsonl> [since_iso_utc]
since = sys.argv[2] if len(sys.argv) > 2 else None
turns = []; cur = None
for l in open(sys.argv[1], encoding='utf-8'):
    try: d = json.loads(l)
    except Exception: continue
    m = d.get('message') or {}
    if d.get('type') == 'user' and not d.get('isMeta') and isinstance(m.get('content'), str):
        cur = {'ts': d.get('timestamp'), 'start': m['content'][:30], 'w': 0, 'tools': 0}; turns.append(cur)
    if d.get('type') == 'assistant' and cur:
        for b in m.get('content') or []:
            if isinstance(b, dict) and b.get('type') == 'tool_use':
                cur['tools'] += 1
                if 'watch_inbound' in json.dumps(b.get('input')): cur['w'] += 1
sel = [t for t in turns if (since is None or (t['ts'] or '') >= since)]
print("turns", len(turns), "| selected(since=%s)" % since, len(sel),
      "| turns_with_watcher", sum(1 for t in sel if t['w']),
      "| watcher_starts", sum(t['w'] for t in sel))
for t in sel:
    if not t['w']: print("  NO-WATCHER", t['ts'], repr(t['start']), "tools=%d" % t['tools'])
print("first watcher start ts:", next((t['ts'] for t in turns if t['w']), None))
