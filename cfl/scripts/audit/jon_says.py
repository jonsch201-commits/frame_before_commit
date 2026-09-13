#!/usr/bin/env python3
"""Find what Jon ACTUALLY SAID about X — across every venue, from any trunk, with the bound stated.

⛔ WHY THIS EXISTS
------------------
Jon, 2026-08-09: *"You need to help all ground to my words current and older?"* — and the answer was
yes, because **no instrument in this program could do it.** `[measured 2026-08-09 10:4x]`

  * `find_answer.py` searches CFL wiki PAGES. Sibling-trunk coverage: 0. `history.jsonl`: 0.
  * Four scripts are named for finding Jon's words. **None crosses a trunk boundary.**

So every lane greps its own roots and reports "not found" — which `CLAUDE.md` itself warns means
only *"not in the rows I searched."* That warning has been in the file for days with no instrument
behind it, and the cost is on record: a Jon ruling sat unreachable for twenty minutes in a live
sibling session on the same disk, and a lane wrote *"Unsearchable by any tool here"* about text that
was in this repo's own `raw/`.

⭐ THE DESIGN RULE, and it is the whole point
---------------------------------------------
**This tool reports WHICH VENUES IT SEARCHED AND WHICH IT COULD NOT REACH, every single time,
including on a hit.** A search that returns nothing and does not name its own scope is the defect it
was built to fix. `CLAUDE.md`'s closure test applies to this file: *"a venue belongs here once any
Jon utterance is found in it. Add the row when you find it; never conclude absence from this table."*

⚠️ ASOP framing, since Jon named that standard: this is a RELIANCE DISCLOSURE. The output says what
was relied on and what was not available, so a reader can grade the answer instead of trusting it.
"Not found" is never rendered as "never said."
"""
import argparse, json, os, pathlib, re, sys, subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HOME = pathlib.Path(os.path.expanduser("~"))
PROJECTS = HOME / ".claude" / "projects"
DRIVE = pathlib.Path("G:/My Drive/Claude")


def venues(repo):
    """Every known channel. Each entry: (label, kind, path). MISSING ones are REPORTED, not skipped."""
    v = [
        ("typed prompts (history.jsonl)", "jsonl-history", HOME / ".claude" / "history.jsonl"),
        ("parsed transcript corpus", "md", pathlib.Path(repo) / "raw" / "transcripts"),
        ("GitHub comments (Jon-typed subset)", "md", pathlib.Path(repo) / "raw" / "github-comments"),
        ("paste-cache", "any", HOME / ".claude" / "paste-cache"),
    ]
    # ⭐ SIBLING TRUNKS. The row CLAUDE.md added 2026-08-08 after a ruling sat unreachable for 20
    # minutes in a live sibling session on this same disk. `find_answer.py`'s nine roots contain
    # ZERO of these. This is the whole reason the file exists.
    if PROJECTS.is_dir():
        for d in sorted(PROJECTS.iterdir()):
            if d.is_dir():
                v.append((f"trunk JSONL: {d.name[:46]}", "jsonl-session", d))
    return v


def hits_in_history(path, rx, limit):
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                if not rx.search(line):
                    continue
                try:
                    d = json.loads(line)
                    txt = d.get("display", "")
                    ts = d.get("timestamp", "")
                    proj = (d.get("project") or "")[-40:]
                except Exception:
                    txt, ts, proj = line, "", ""
                m = rx.search(txt) or rx.search(line)
                if m:
                    s = max(0, m.start() - 90)
                    out.append((f"{path.name}:{n}", ts, proj, txt[s:m.end() + 140].replace("\n", " ")))
                if len(out) >= limit:
                    break
    except Exception as e:
        return None, str(e)
    return out, None


def hits_in_jsonl_dir(d, rx, limit):
    """Session + subagent JSONLs. Jon's mid-turn messages to subagents appear in NO main transcript."""
    out, err = [], None
    try:
        files = list(d.rglob("*.jsonl"))
    except Exception as e:
        return None, str(e)
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    if not rx.search(line):
                        continue
                    try:
                        d2 = json.loads(line)
                    except Exception:
                        continue
                    # human-authored only: type user, and either isMeta (mid-turn to a subagent)
                    # or origin.kind == human (a typed dispatch).
                    if d2.get("type") != "user":
                        continue
                    origin = (d2.get("origin") or {}).get("kind", "")
                    if not (d2.get("isMeta") or origin == "human"):
                        continue
                    txt = json.dumps(d2.get("message", d2))[:4000]
                    m = rx.search(txt)
                    if m:
                        s = max(0, m.start() - 90)
                        out.append((f"{f.name}:{n}", d2.get("timestamp", ""), f.parent.name[:30],
                                    txt[s:m.end() + 140].replace("\\n", " ")))
                    if len(out) >= limit:
                        return out, None
        except Exception:
            continue
    return out, err


def hits_in_md(root, rx, limit):
    out = []
    try:
        r = subprocess.run(["grep", "-rioE", "-m", "2",
                            r".{0,90}" + rx.pattern + r".{0,140}", str(root)],
                           capture_output=True, text=True, timeout=180)
    except Exception as e:
        return None, str(e)
    for line in (r.stdout or "").splitlines()[:limit]:
        p, _, txt = line.partition(":")
        out.append((pathlib.Path(p).name, "", "", txt.strip()))
    return out, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="what Jon might have said about it (regex ok)")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--limit", type=int, default=4, help="hits per venue")
    a = ap.parse_args()
    rx = re.compile(a.query, re.I)

    print(f'=== jon_says: "{a.query}" ===\n')
    searched, unreachable, total = [], [], 0

    for label, kind, path in venues(a.repo):
        if not path.exists():
            unreachable.append((label, "does not exist on this machine"))
            continue
        if kind == "jsonl-history":
            hits, err = hits_in_history(path, rx, a.limit)
        elif kind == "jsonl-session":
            hits, err = hits_in_jsonl_dir(path, rx, a.limit)
        elif kind == "md":
            hits, err = hits_in_md(path, rx, a.limit)
        else:
            hits, err = hits_in_md(path, rx, a.limit)
        if hits is None:
            unreachable.append((label, err or "unreadable"))
            continue
        searched.append(label)
        if hits:
            print(f"--- {label} --- {len(hits)} hit(s)")
            for loc, ts, ctx, txt in hits:
                # history.jsonl stamps are epoch-ms INTEGERS; session JSONLs are ISO strings.
                # Coerce rather than assume -- the first run died on exactly this.
                ts = str(ts)
                print(f"  {loc}  {ts[:19]}  {ctx}")
                print(f"    ...{txt[:210]}")
            print()
            total += len(hits)

    # ⭐ THE BOUND. Printed on EVERY run, hit or miss. This block is the reason the file exists.
    print("=== RELIANCE DISCLOSURE — read this before quoting the result ===")
    print(f"  venues SEARCHED   : {len(searched)}")
    print(f"  venues UNREACHABLE: {len(unreachable)}")
    for lbl, why in unreachable:
        print(f"      - {lbl}: {why}")
    print(f"  total hits        : {total}")
    if total == 0:
        print("\n  [!] ZERO HITS. This means NOT FOUND IN THE VENUES ABOVE.")
        print("      It does NOT mean he never said it. Venues no instrument here reads include:")
        print("      AskUserQuestion selections (captured nowhere) | Google Docs he annotates |")
        print("      claude.ai project instructions he edits | merge-commit messages | zip members.")
        print("      CLAUDE.md: 'never conclude absence from this table.'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
