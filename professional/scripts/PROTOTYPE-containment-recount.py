"""Containment recount (Secretary's correction 22:4x): a session is COVERED when its RECORDS are covered, not when its name appears.
For each B-era floor session that has no render by filename, collect its record uuids and test whether they are a subset of the
uuids of any RENDERED session in the same project key (continuations, resumes and forks share records with their parent).
Also report the reverse: rendered sessions that are strict subsets of another rendered session (duplicate load)."""
import os, json, glob, io, sys
ROOT = os.path.expanduser("~/.claude/projects")
H = ["key","kind","base","direct","meta_jon","meta_coord","queued","first","last","era","archived","rendered","indexed","sample"]
rows = []
for l in io.open("N:/claude-professional/evidence/jon-direct-input-census-2026-09-05.tsv", encoding="utf-8"):
    x = l.rstrip("\n").split("\t")
    if len(x) == len(H) and x[0] != "key": rows.append(dict(zip(H, x)))
gaps = [r for r in rows if r["kind"] == "main" and int(r["direct"]) > 0 and r["rendered"] == "N" and r["era"] == "B" and "switchboard" not in r["key"] and not r["key"].startswith("C--Users")]
rendered_by_key = {}
for r in rows:
    if r["kind"] == "main" and r["rendered"] == "Y":
        rendered_by_key.setdefault(r["key"], []).append(r["base"])

def uuids(path):
    s = set()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try: o = json.loads(line)
            except Exception: continue
            u = o.get("uuid")
            if u: s.add(u)
    return s

out = []
out.append("| gap session | key | Jon turns | records | contained in (rendered) | verdict |")
out.append("|---|---|---|---|---|---|")
survivors = []
for g in gaps:
    gp = f"{ROOT}/{g['key']}/{g['base']}.jsonl"
    gu = uuids(gp)
    best = None
    # candidates: rendered sessions in the same key; also any key sharing the same trunk (N/G) — check same key first, then all keys
    cands = [(g["key"], b) for b in rendered_by_key.get(g["key"], [])]
    for k, bs in rendered_by_key.items():
        if k != g["key"]:
            cands += [(k, b) for b in bs]
    for k, b in cands:
        p = f"{ROOT}/{k}/{b}.jsonl"
        if not os.path.exists(p): continue
        # cheap prefilter: file must be at least as large in bytes as a fraction of the gap; skip tiny
        cu = uuids(p)
        if gu and gu <= cu:
            best = (k, b, len(cu)); break
        if gu and len(gu & cu) >= 0.9 * len(gu):
            best = best or (k, b, len(cu), "90%")
    if best and len(best) == 3:
        verdict = "COVERED (strict subset)"
    elif best:
        verdict = "MOSTLY (>=90% shared) — not a subset"
        survivors.append(g)
    else:
        verdict = "GAP survives containment"
        survivors.append(g)
    out.append(f"| {g['base'][:8]} | {g['key'][:34]} | {g['direct']} | {len(gu)} | {best[1][:8] + ' (' + best[0][:20] + ', ' + str(best[2]) + ' records)' if best else '—'} | {verdict} |")
out.append("")
out.append(f"gaps by filename: {len(gaps)}; survive containment: {len(survivors)}")
for s in survivors:
    out.append(f"SURVIVOR\t{s['key']}\t{s['base']}\t{s['direct']}\t{s['queued']}\t{s['last']}\t{s['sample'][:60]}")
txt = "\n".join(out)
io.open("N:/claude-professional/evidence/jon-direct-input-census-2026-09-05-CONTAINMENT.md", "w", encoding="utf-8", newline="\n").write(
    "# Containment recount of the 13 B-era filename gaps (Secretary's rule, 22:4x)\n\nmeasured: " + __import__('datetime').datetime.now().strftime('%F %T') + " CDT\n\n" + txt + "\n")
print(txt)
