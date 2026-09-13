#!/usr/bin/env python3
"""FL audit-program census (metadata-only, no models, no writes to pages).

Scans every wiki source page, records structural metadata, guesses source_kind,
infers audit_state, and computes an exposure-based priority score:

    exposure = load_bearing * error_risk * verify_cost   (advisor packet, 2026-07-13)

Prices the backfill. Output: a summary + top-N queue to stdout. The full per-page
table is written only with --write-table, to wiki/references/audit-census-<as-of>.md.

Run from repo root (worktree ok). Reads raw sources from the MAIN checkout
(raws are gitignored -> not in the worktree) via --main-root.

FIXED 2026-07-26, three defects that made this unrunnable-in-practice:
  - `today` was hardcoded to datetime.date(2026,7,13), so the vintage term inside
    error_risk reproduced July-13 staleness on every re-run forever. A frozen clock
    inside a freshness metric. Now defaults to today; --as-of reproduces a past run.
  - the audit_state HEURISTIC ran unconditionally and contradicted the ratified
    authoritative frontmatter field (13 "verified?" vs 12 actually stamped), so the
    census and the ledger disagreed about the same pages. The declared field now wins;
    guesses are prefixed "guess:" so the two can never be confused again.
  - it wrote a tracked wiki page as a SIDE EFFECT of measuring, which is why it could
    not be run routinely. Writing is now opt-in.
"""
import os, re, sys, glob, argparse, datetime

WIKI = "wiki"
TRUNKS = {
    "wiki/sources": "fl",
    "wiki/personal/sources": "personal",
    "wiki/home/sources": "home",
    "wiki/pro/sources": "pro",
}

def trunk_of(path):
    p = path.replace("\\", "/")
    for pre, name in TRUNKS.items():
        if p.startswith(pre):
            return name
    return "other"

def parse(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    fm = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                m = re.match(r"^([a-z_]+):\s*(.*)$", line.strip())
                if m:
                    fm[m.group(1)] = m.group(2).strip()
            body = text[end+4:]
        else:
            body = text
    else:
        body = text
    return fm, body, text

def date_from(path, fm):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    if m: return m.group(1)
    return fm.get("date", fm.get("date_ingested", ""))

def main():
    ap = argparse.ArgumentParser()
    # ⛔ WAS a hardcoded G: tree path. That is R4b on Professional's restart gate and G30's shape:
    # a stale tree used as a DEFAULT, which produces a confident wrong answer rather than an error.
    # ⭐ Flagged independently by two instruments the same afternoon — CFL's own expiring_values.py
    # (93.3% precision, seed 1337) and Professional's R4b grep, different trunks, different methods,
    # this exact line. DERIVE from the script's own location: parents[2] of scripts/audit/<this>.py
    # IS the checkout containing the code being run, in every clone, and cannot name a tree the
    # caller is not in. [[derive-dont-record]]
    ap.add_argument("--main-root",
                    default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--as-of", default=None, metavar="YYYY-MM-DD",
                    help="valuation date for the vintage term in error_risk. Defaults to TODAY. "
                         "Was hardcoded to 2026-07-13, so every re-run silently reproduced "
                         "July-13 staleness no matter when it ran — a frozen clock inside a "
                         "freshness metric. Pass a date to reproduce a historical run.")
    ap.add_argument("--write-table", action="store_true",
                    help="write the full per-page table to wiki/references/. OFF by default: "
                         "measuring must not mutate what it measures.")
    args = ap.parse_args()

    pages = sorted(p.replace("\\","/") for p in glob.glob(f"{WIKI}/**/*.md", recursive=True)
                   if "/sources/" in p.replace("\\","/"))

    # pass 1: gather + build slug set for inbound-link counting
    rows = []
    all_link_text = []
    slugs = {}
    for path in pages:
        fm, body, text = parse(path)
        slug = os.path.basename(path)[:-3]
        slugs[slug] = path
        all_link_text.append(text)
        key_claims = 0
        mkc = re.search(r"^##\s*Key Claims\s*$(.*?)(^##\s|\Z)", body, re.M|re.S)
        if mkc:
            key_claims = len(re.findall(r"^\s*-\s+\*\*", mkc.group(1), re.M)) or len(re.findall(r"^\s*-\s+", mkc.group(1), re.M))
        anchors = len(re.findall(r":T\d+", text))
        fidelity = len(re.findall(r"\[(verbatim|paraphrase|reconstructed|contextual|inferred|uncaptured)\]", text))
        out_links = len(re.findall(r"\[\[[^\]]+\]\]", text))
        has_req = all(f"## {s}" in body for s in ("Summary","Key Claims","Conflicts"))
        has_find = "retrieval_key:" in text
        has_prov = "generated_by:" in text
        has_fixity = "raw_sha256:" in text
        has_kind = "source_kind:" in text
        sf = fm.get("source_file","")
        src_avail = bool(sf) and sf.lower()!="none" and os.path.isfile(os.path.join(args.main_root, sf))
        src_lines = 0
        if src_avail:
            try:
                with open(os.path.join(args.main_root, sf), encoding="utf-8", errors="ignore") as g:
                    src_lines = sum(1 for _ in g)
            except Exception:
                src_avail = False
        rows.append(dict(path=path, slug=slug, trunk=trunk_of(path), date=date_from(path, fm),
                         key_claims=key_claims, anchors=anchors, fidelity=fidelity, out_links=out_links,
                         has_req=has_req, has_find=has_find, has_prov=has_prov, has_fixity=has_fixity,
                         has_kind=has_kind, src_avail=src_avail, src_lines=src_lines, body=body, fm=fm))
    blob = "\n".join(all_link_text)

    # pass 2: inbound links + source_kind guess + audit_state + score
    today = (datetime.date.fromisoformat(args.as_of) if args.as_of else datetime.date.today())
    for r in rows:
        r["inbound"] = len(re.findall(r"\[\[" + re.escape(r["slug"]) + r"\]\]", blob))
        # source_kind guess
        b = r["body"]
        if not re.search(r"\d{4}-\d{2}-\d{2}-[a-f0-9]{6}", r["slug"]) or "concepts/" in r["path"] or "analyses/" in r["path"]:
            kind = "candidate-analysis"
        elif "## Key Claims" in b and "## Summary" in b:
            kind = "session"
        elif re.search(r"^##\s*(Product|Warranty|Ticket|Spec|Model|Intake|Photos|Action Items)", b, re.M):
            kind = "reference"
        else:
            kind = "session?"
        r["kind"] = r["fm"].get("source_kind", kind)
        # audit_state — the AUTHORITATIVE frontmatter field wins; the heuristic only
        # fills in where the field is absent, and says so. Previously the heuristic ran
        # unconditionally and contradicted the ratified field (13 "verified?" vs 12
        # actually stamped), so the census disagreed with the ledger about the same pages.
        declared = r["fm"].get("audit_state", "").strip()
        if declared:
            r["state"] = declared.split("@")[0].split("{")[0].strip() or "unaudited"
            r["state_source"] = "declared"
        else:
            if r["has_fixity"] and r["anchors"] > 0 and r["has_kind"]:
                r["state"] = "guess:verified?"
            elif r["anchors"] > 0 or r["has_find"] or r["has_fixity"]:
                r["state"] = "guess:partial"
            else:
                r["state"] = "guess:unaudited"
            r["state_source"] = "heuristic"
        # vintage months
        try:
            d = datetime.date.fromisoformat(r["date"][:10]); months = (today-d).days/30.0
        except Exception:
            months = 6.0
        r["months"] = months
        # components (normalized-ish proxies)
        load_bearing = 1 + r["inbound"] + 0.3*r["key_claims"]
        uncited = 1.0 if r["anchors"]==0 else 0.2
        error_risk = uncited + (0.6 if r["fidelity"]==0 else 0) + (0.4 if not r["has_fixity"] else 0) + min(months/12.0, 1.5)*0.5
        verify_cost = 1 + (r["src_lines"]/200.0 if r["src_avail"] else 3.0)  # missing source = expensive/uncertain
        r["load_bearing"]=round(load_bearing,2); r["error_risk"]=round(error_risk,2); r["verify_cost"]=round(verify_cost,2)
        r["exposure"] = round(load_bearing*error_risk*verify_cost, 1)
        r["bang"] = round(load_bearing*error_risk/verify_cost, 2)  # value-per-cost alt sort

    # summary
    n=len(rows)
    def pct(f): return f"{100*sum(1 for r in rows if f(r))//n}%"
    print(f"=== FL AUDIT CENSUS — {n} source pages, as-of {today.isoformat()} ===")
    from collections import Counter
    tc=Counter(r["trunk"] for r in rows); kc=Counter(r["kind"] for r in rows); sc=Counter(r["state"] for r in rows)
    print("by trunk:      ", dict(tc))
    print("by kind(guess):", dict(kc))
    print("by state:      ", dict(sc))
    print(f"conformance:   anchors {pct(lambda r:r['anchors']>0)} | fidelity {pct(lambda r:r['fidelity']>0)} | "
          f"findability {pct(lambda r:r['has_find'])} | fixity {pct(lambda r:r['has_fixity'])} | "
          f"source_kind {pct(lambda r:r['has_kind'])} | source-available {pct(lambda r:r['src_avail'])}")
    print(f"\n=== TOP {args.top} PRIORITY (by exposure = load_bearing x error_risk x verify_cost) ===")
    top = sorted(rows, key=lambda r:-r["exposure"])[:args.top]
    print(f"{'exp':>6} {'lb':>4} {'er':>4} {'vc':>4} {'in':>3} {'kc':>3} {'anc':>3} {'trunk':<8} slug")
    for r in top:
        print(f"{r['exposure']:>6} {r['load_bearing']:>4} {r['error_risk']:>4} {r['verify_cost']:>4} "
              f"{r['inbound']:>3} {r['key_claims']:>3} {r['anchors']:>3} {r['trunk']:<8} {r['slug'][:52]}")

    # write full table — OPT-IN. Writing it unconditionally meant that merely running
    # the census mutated a tracked wiki page, which is why it could not be run routinely.
    if not args.write_table:
        print(f"\n(table not written — pass --write-table to regenerate it)")
        return
    out = f"{WIKI}/references/audit-census-{today.isoformat()}.md"
    with open(out,"w",encoding="utf-8") as f:
        f.write("---\ntitle: FL Audit Census (2026-07-13)\nstatus: generated by scripts/audit/census.py (metadata-only)\n---\n\n")
        f.write(f"# FL Audit Census — {n} source pages\n\n")
        f.write(f"by trunk: {dict(tc)}  \nby kind(guess): {dict(kc)}  \nby state: {dict(sc)}\n\n")
        f.write("Conformance: anchors "+pct(lambda r:r['anchors']>0)+", fidelity "+pct(lambda r:r['fidelity']>0)+
                ", findability "+pct(lambda r:r['has_find'])+", fixity "+pct(lambda r:r['has_fixity'])+
                ", source_kind "+pct(lambda r:r['has_kind'])+", source-available "+pct(lambda r:r['src_avail'])+".\n\n")
        f.write("| exposure | lb | er | vc | inbound | claims | anchors | state | kind | trunk | slug |\n")
        f.write("|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|\n")
        for r in sorted(rows, key=lambda r:-r["exposure"]):
            f.write(f"| {r['exposure']} | {r['load_bearing']} | {r['error_risk']} | {r['verify_cost']} | {r['inbound']} | "
                    f"{r['key_claims']} | {r['anchors']} | {r['state']} | {r['kind']} | {r['trunk']} | {r['slug']} |\n")
    print(f"\nfull table -> {out}")

if __name__=="__main__":
    main()
