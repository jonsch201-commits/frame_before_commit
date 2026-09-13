"""Census v2: every JSONL under ~/.claude/projects carrying a message typed by Jon, graded for archive / render / index presence.
direct  = type:user, not isMeta, human text (string content, text blocks, or a <command-name> wrapper), no tool_result. For SUBAGENT files the
          dispatch prompt is the coordinator's, so direct is forced to 0 there and Jon can only appear as isMeta.
meta_jon = isMeta user turns NOT opening with the coordinator relay wrapper ("The coordinator sent a message").  MIXED CLASS: could still be a relay in another wording.
meta_coord = isMeta turns opening with that wrapper.
queued  = type:attachment / queued_command entries (Jon typing while a turn ran).
archived = raw/session-archive/<full id or agent id> exists in ANY trunk tree.
rendered = a *.md under any trunk's raw/transcripts/** or N:/claude-corpus/** whose filename contains the 6-char prefix (main) or the agent id.
indexed  = a path in the graphrag `files` table (dumped to evidence/graphrag-index-files-2026-09-05.tsv) containing the same key.
era     = by LAST direct-Jon timestamp: B >= 2026-09-04 21:00Z (last all-trunk compact ~16:00 CDT) · D >= 2026-08-30 02:45Z (PR-2 merge) · C >= 2026-08-23 03:26Z (PR-1 merge) · OLDER.
"""
import os, json, glob, sys, io, collections
ROOT = os.path.expanduser("~/.claude/projects")
TRUNK_TREES = ["N:/claude-professional", "N:/claude-personal", "N:/claude-cfl/clone", "N:/claude-secretary", "N:/antigravity-hub",
               "G:/My Drive/Claude/Claude Personal", "G:/My Drive/Claude/Claude Secretary", "G:/My Drive/Claude/Antigravity",
               "G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer",
               "G:/My Drive/Claude/Claude Professional/claude-professional"]
out_tsv, out_md, idx_tsv = sys.argv[1], sys.argv[2], sys.argv[3]

archived = set()
for t in TRUNK_TREES:
    d = t + "/raw/session-archive"
    if os.path.isdir(d):
        for n in os.listdir(d): archived.add(n)
render_names = []
for r in [t + "/raw/transcripts" for t in TRUNK_TREES] + ["N:/claude-corpus"]:
    if not os.path.isdir(r): continue
    for dp, dn, fn in os.walk(r):
        for f in fn:
            if f.endswith(".md"): render_names.append(f)
render_str = "\n".join(render_names)
index_str = io.open(idx_tsv, encoding="utf-8").read()

def key_for(base, kind):
    return base if kind == "subagent" else base[:6]

rows = []
files = glob.glob(ROOT + "/*/*.jsonl") + glob.glob(ROOT + "/*/subagents/*.jsonl") + glob.glob(ROOT + "/*/*/subagents/*.jsonl")
for f in files:
    key = os.path.relpath(f, ROOT).split(os.sep)[0]
    base = os.path.basename(f)[:-6]
    kind = "subagent" if os.sep + "subagents" + os.sep in f or "/subagents/" in f else "main"
    direct = meta_jon = meta_coord = queued = 0; first = last = None; sample = ""; n_user = 0
    try:
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try: o = json.loads(line)
                except Exception: continue
                ts = o.get("timestamp"); t = o.get("type")
                if t == "attachment" and (o.get("attachment") or {}).get("type") == "queued_command":
                    queued += 1; continue
                if t != "user": continue
                m = o.get("message") or {}; c = m.get("content"); text = None
                if isinstance(c, str): text = c
                elif isinstance(c, list):
                    if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c): continue
                    tb = [b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"]
                    if tb: text = "\n".join(tb)
                if not text: continue
                s = text.lstrip()
                if s.startswith("<system-reminder>") or s.startswith("<local-command-stdout") or s.startswith("<local-command-caveat"):
                    continue
                if o.get("isMeta"):
                    if s.startswith("The coordinator sent a message") or s.startswith("<coordinator"): meta_coord += 1
                    else: meta_jon += 1
                    continue
                n_user += 1
                if kind == "subagent": continue
                direct += 1
                if ts: first = first or ts; last = ts
                if not sample: sample = s[:90].replace("\n", " ").replace("\t", " ").replace("|", "/")
    except Exception as e:
        rows.append(dict(key=key, kind=kind, base=base, err=str(e)[:60])); continue
    jon = direct + meta_jon + queued
    if jon == 0: continue
    k = key_for(base, kind)
    era = "OLDER"
    if last:
        if last >= "2026-09-04T21:00": era = "B"
        elif last >= "2026-08-30T02:45": era = "D"
        elif last >= "2026-08-23T03:26": era = "C"
    rows.append(dict(key=key, kind=kind, base=base, direct=direct, meta_jon=meta_jon, meta_coord=meta_coord, queued=queued,
                     first=first or "", last=last or "", era=era,
                     archived="Y" if (base in archived or any(base in a for a in archived)) else "N",
                     rendered="Y" if k in render_str else "N", indexed="Y" if k in index_str else "N", sample=sample))

rows.sort(key=lambda r: r.get("last", ""), reverse=True)
cols = ["key", "kind", "base", "direct", "meta_jon", "meta_coord", "queued", "first", "last", "era", "archived", "rendered", "indexed", "sample"]
with io.open(out_tsv, "w", encoding="utf-8", newline="\n") as w:
    w.write("\t".join(cols) + "\n")
    for r in rows:
        w.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")

good = [r for r in rows if "err" not in r]
def tab(rs, by):
    c = collections.defaultdict(lambda: collections.Counter())
    for r in rs:
        g = r[by]; c[g]["files"] += 1; c[g]["direct"] += r["direct"]; c[g]["meta_jon"] += r["meta_jon"]; c[g]["queued"] += r["queued"]
        c[g]["archived"] += r["archived"] == "Y"; c[g]["rendered"] += r["rendered"] == "Y"; c[g]["indexed"] += r["indexed"] == "Y"
    return c
mains = [r for r in good if r["kind"] == "main" and r["direct"] > 0]
subs = [r for r in good if r["kind"] == "subagent"]
L = []
L.append(f"scanned {len(files)} JSONLs; {len(good)} carry Jon input; unreadable {len(rows)-len(good)}")
L.append(f"MAIN sessions with >=1 direct Jon turn: {len(mains)}; direct turns {sum(r['direct'] for r in mains)}; queued {sum(r['queued'] for r in mains)}")
L.append(f"SUBAGENT files with isMeta non-relay turns (Jon-possible, MIXED CLASS): {len(subs)}; turns {sum(r['meta_jon'] for r in subs)}")
L.append("")
L.append("| era (by last direct turn) | main files | direct turns | archived | rendered | indexed |")
L.append("|---|---|---|---|---|---|")
te = tab(mains, "era")
for e in ["B", "D", "C", "OLDER"]:
    x = te[e]; L.append(f"| {e} | {x['files']} | {x['direct']} | {x['archived']} | {x['rendered']} | {x['indexed']} |")
L.append("")
L.append("| project key | main files | direct turns | archived | rendered | indexed |")
L.append("|---|---|---|---|---|---|")
tk = tab(mains, "key")
for k, x in sorted(tk.items(), key=lambda kv: -kv[1]["files"]):
    L.append(f"| {k} | {x['files']} | {x['direct']} | {x['archived']} | {x['rendered']} | {x['indexed']} |")
L.append("")
L.append("| subagent project key | files w/ Jon-possible isMeta | turns | archived | rendered | indexed |")
L.append("|---|---|---|---|---|---|")
ts_ = tab(subs, "key")
for k, x in sorted(ts_.items(), key=lambda kv: -kv[1]["files"]):
    L.append(f"| {k} | {x['files']} | {x['meta_jon']} | {x['archived']} | {x['rendered']} | {x['indexed']} |")
io.open(out_md, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("\n".join(L))
