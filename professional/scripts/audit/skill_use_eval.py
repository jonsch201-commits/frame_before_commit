#!/usr/bin/env python3
"""skill_use_eval.py -- criterion E for PR 4: how often each skill fired, with a denominator.

Population: MAIN session JSONLs (top level of each ~/.claude/projects/<key>/, subagents/ excluded)
whose file mtime is on or after --since (default 2026-09-05, the day the fleet skills were deployed).
Two use classes per skill:
  tool_use    = an assistant `tool_use` block with name == "Skill" and input.skill == <name>
                (the seat chose to invoke it; this INCLUDES cases where Jon asked for it in prose,
                 e.g. "frame before commit your statement" -- so it is NOT an unprompted count)
  slash_typed = a user turn whose text carries "<command-name>/<name>" (the typed slash command)
THREE BUCKETS (Soul 2026-09-13 00:4x; wiki/references/skills-two-roots-and-why-the-list-keeps-being-wrong.md:94):
  LOAD-AT-OPEN  in context every session by that trunk's configuration -> tool_use count is MEANINGLESS
  INVOKED       a real tool_use or slash event exists
  NEITHER       installed, not loaded at open, never invoked -- the only bucket where 0 means 0
This script measures INVOKED only. The LOAD-AT-OPEN bucket is read from each trunk's CLAUDE.md /
skill frontmatter by the caller, never inferred from a count.
Denominators: sessions scanned, assistant turns, user turns, per project key.
Bound: use is counted BY NAME ONLY. A skill whose behaviour a seat applied without invoking it is
not counted; a Skill call whose body never ran is counted. So tool_use is a floor on invocation
and nothing here measures effect. An unreadable line is counted as UNREADABLE, never dropped as 0.
Excluded by construction: any key containing 'XC-Exchequer' (no-remote absolute; not read).
"""
import argparse, json, os, re, sys, glob, datetime, collections

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-09-05")
    ap.add_argument("--projects", default=os.path.join(os.path.expanduser("~"), ".claude", "projects"))
    ap.add_argument("--skills", default="frame-before-commit,ground-before-stating,wiki-query,wikiskills-improve,peer-review,wayfinder,wake,dream,su-compact,gbs,fbc")
    ap.add_argument("--tsv", default=None, help="write per-key rows here")
    a = ap.parse_args()
    since = datetime.datetime.strptime(a.since, "%Y-%m-%d").timestamp()
    skills = [s.strip() for s in a.skills.split(",") if s.strip()]
    cmd_rx = re.compile(r"<command-name>/?([A-Za-z0-9_-]+)</command-name>")
    per_key = {}
    unreadable = 0
    keys = sorted(d for d in os.listdir(a.projects) if os.path.isdir(os.path.join(a.projects, d)))
    for key in keys:
        if "XC-Exchequer" in key:
            per_key[key] = {"EXCLUDED": "XC-Exchequer no-remote rule; not read"}
            continue
        files = [f for f in glob.glob(os.path.join(a.projects, key, "*.jsonl")) if os.path.getmtime(f) >= since]
        if not files:
            continue
        st = {"sessions": len(files), "assistant_turns": 0, "user_turns": 0,
              "tool_use": collections.Counter(), "slash_typed": collections.Counter(), "unreadable": 0}
        for f in files:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                for ln in fh:
                    try:
                        rec = json.loads(ln)
                    except Exception:
                        st["unreadable"] += 1; unreadable += 1; continue
                    t = rec.get("type")
                    msg = rec.get("message") or {}
                    content = msg.get("content")
                    if t == "assistant":
                        st["assistant_turns"] += 1
                        if isinstance(content, list):
                            for b in content:
                                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Skill":
                                    nm = str((b.get("input") or {}).get("skill", "")).split(":")[-1]
                                    st["tool_use"][nm] += 1
                    elif t == "user":
                        st["user_turns"] += 1
                        txt = content if isinstance(content, str) else json.dumps(content) if content else ""
                        for m in cmd_rx.finditer(txt):
                            st["slash_typed"][m.group(1)] += 1
        per_key[key] = st
    # report
    print("SKILL-USE EVAL  since=%s  population=MAIN session JSONLs under %s (mtime filter; subagents/ excluded)" % (a.since, a.projects))
    print("BOUND: counts INVOCATION BY NAME only (Skill tool_use; <command-name> in a user turn); never effect, never load-at-open. A 0 here is 'no invocation record', not 'never ran' -- read the LOAD-AT-OPEN bucket first. unreadable lines=%d (counted, not dropped)" % unreadable)
    tot = {"sessions": 0, "assistant_turns": 0, "user_turns": 0}
    tot_u = collections.Counter(); tot_p = collections.Counter()
    rows = []
    for key, st in per_key.items():
        if "EXCLUDED" in st:
            print("  %-70s EXCLUDED: %s" % (key[:70], st["EXCLUDED"])); continue
        for k in tot: tot[k] += st[k]
        tot_u.update(st["tool_use"]); tot_p.update(st["slash_typed"])
        u = " ".join("%s=%d" % (s, st["tool_use"][s]) for s in skills if st["tool_use"][s])
        p = " ".join("%s=%d" % (s, st["slash_typed"][s]) for s in skills if st["slash_typed"][s])
        print("  %-70s sessions=%d asst=%d user=%d | tool_use[%s] slash_typed[%s]" % (key[:70], st["sessions"], st["assistant_turns"], st["user_turns"], u or "-", p or "-"))
        rows.append((key, st))
    print("TOTAL sessions=%d assistant_turns=%d user_turns=%d" % (tot["sessions"], tot["assistant_turns"], tot["user_turns"]))
    print("%-24s %10s %10s %14s" % ("skill", "tool_use", "slash_typed", "per_1k_asst"))
    for s in skills:
        rate = (1000.0 * tot_u[s] / tot["assistant_turns"]) if tot["assistant_turns"] else float("nan")
        print("%-24s %10d %10d %14.2f" % (s, tot_u[s], tot_p[s], rate))
    others_u = {k: v for k, v in tot_u.items() if k not in skills}
    if others_u:
        print("other Skill names invoked (not in --skills): " + ", ".join("%s=%d" % kv for kv in sorted(others_u.items(), key=lambda x: -x[1])[:15]))
    measured_keys = sum(1 for st in per_key.values() if "EXCLUDED" not in st)
    print("FLOOR CHECK (criterion E): measured trunk keys=%d (floor 5) -> %s" % (measured_keys, "PASS" if measured_keys >= 5 else "FAIL"))
    if a.tsv:
        with open(a.tsv, "w", encoding="utf-8") as fh:
            fh.write("key\tsessions\tassistant_turns\tuser_turns\t" + "\t".join("tu_" + s for s in skills) + "\t" + "\t".join("st_" + s for s in skills) + "\n")
            for key, st in rows:
                fh.write("\t".join([key, str(st["sessions"]), str(st["assistant_turns"]), str(st["user_turns"])] + [str(st["tool_use"][s]) for s in skills] + [str(st["slash_typed"][s]) for s in skills]) + "\n")
        print("tsv -> " + a.tsv)

if __name__ == "__main__":
    main()
