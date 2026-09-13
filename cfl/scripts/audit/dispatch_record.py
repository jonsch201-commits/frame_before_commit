#!/usr/bin/env python3
"""dispatch_record.py -- the DISPATCH half of a subagent exchange, as raw md, written BEFORE the Agent call.

Jon, 2026-09-02 ~18:0x CDT (typed to CFL; the same message plus more went to Antigravity),
verbatim, typos his:
  "getting an exchange to/from a subagent should hook wiki updates in terms of raw md files -
   those subagents need to be able to ground to your state when you sent that message to them! -
   and in terms of both their raw md files and a compact-equivilent wiki update from them in
   terms of subagent summaries that should be in the wiki."

What exists for the RETURN half: SubagentStop -> route_agent_return.py (CAPTURE row) and
agent_end_ingest.py (I0 render of the subagent JSONL to raw md, I1 extract page under
wiki/intake-triage/agent-end/<session6>/). Measured 2026-09-02 18:3x: 191 subagent JSONLs for
session e515d858 today, 57 rendered to raw md, 0 I1 pages -- the hooks were dead all day, so the
return half ran for nothing until it was hand-run.

What existed for the DISPATCH half: nothing. The prompt lives only inside the subagent JSONL
(first user entry) and the coordinator's state at that instant (HEAD, WAKE age, meter, live map
amendment) is nowhere. A forked self or a peer trunk cannot ground "what did main know when it
sent this", which is the half Jon named first.

This script writes ONE md file per dispatch to exchange/dispatches/<date>/<stamp>-<slug>.md with:
the prompt verbatim, the state snapshot (branch, HEAD, WAKE.md written-line, meter line, gate
verdict, newest map amendment heading, git porcelain count), the write-set the lane was given,
and the model tier. The Agent call cites the file path in its prompt so the lane can open it and
ground to it. Nothing here is a hook; it is the coordinator's obligation before every dispatch,
and a SubagentStop consumer can join return to dispatch by the agent id written back at return
(--returned AGENT_ID appends the id and the return time to the same file).

Usage:
  dispatch_record.py --slug S-cd-04 --tier fable --write-set "wiki/sources/**,wiki/intake-triage/S-cd-04-*" \
      --prompt-file PATH            # prints the record path; put it in the prompt
  dispatch_record.py --returned AGENT_ID --record PATH
  dispatch_record.py --selftest
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
OUT = ROOT / "exchange" / "dispatches"
METER = Path(r"N:\claude-gists-private\USAGE-CURRENT-cfl.json")


def sh(*a):
    try:
        return subprocess.run(a, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=60).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"UNKNOWN ({e.__class__.__name__})"


def snapshot():
    wake = ROOT / "exchange" / "WAKE.md"
    wake_line = "UNKNOWN"
    if wake.is_file():
        for ln in wake.read_text(encoding="utf-8", errors="replace").splitlines()[:6]:
            if ln.startswith("written:"):
                wake_line = ln.strip()
    meter = "UNKNOWN (meter file missing)"
    if METER.is_file():
        try:
            m = json.loads(METER.read_text(encoding="utf-8"))
            meter = (f"fetched {m.get('fetched_at')} seven_day={ (m.get('seven_day') or {}).get('utilization') } "
                     f"five_hour={ (m.get('five_hour') or {}).get('utilization') }")
        except Exception:  # noqa: BLE001
            meter = "UNKNOWN (meter unparseable)"
    gate = sh(sys.executable, "scripts/audit/dispatch_gate.py").splitlines()
    gate = gate[-1] if gate else "UNKNOWN"
    maps = sorted((ROOT / "wiki" / "tracker").glob("wayfinder-*.md"), key=lambda p: p.stat().st_mtime)
    amend = "UNKNOWN"
    if maps:
        heads = [l for l in maps[-1].read_text(encoding="utf-8", errors="replace").splitlines()
                 if l.startswith("## Amendment")]
        amend = f"{maps[-1].name}: {heads[-1] if heads else '(no amendment heading)'}"
    return {
        "clock": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S local"),
        "branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD"),
        "head": sh("git", "rev-parse", "--short", "HEAD"),
        "origin": sh("git", "rev-parse", "--short", "origin/" + sh("git", "rev-parse", "--abbrev-ref", "HEAD")),
        "porcelain_lines": str(len(sh("git", "status", "--porcelain").splitlines())),
        "wake": wake_line,
        "meter": meter,
        "gate": gate,
        "live_map": amend,
    }


def write_record(slug, tier, write_set, prompt, out_dir=OUT):
    snap = snapshot()
    day = dt.datetime.now().strftime("%Y-%m-%d")
    stamp = dt.datetime.now().strftime("%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", slug).strip("-")[:60]
    d = out_dir / day
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{stamp}-{safe}.md"
    body = ["---", "kind: dispatch-record", f"slug: {slug}", f"tier: {tier}", f"date: {day} {stamp}",
            f"write_set: \"{write_set}\"", "returned: null", "---", "",
            "## Coordinator state at dispatch (measured, not recalled)", ""]
    body += [f"- {k}: {v}" for k, v in snap.items()]
    body += ["", "## Prompt (verbatim)", "", "```", prompt.rstrip("\n"), "```", ""]
    p.write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")
    back = p.read_text(encoding="utf-8")
    if prompt.rstrip("\n") not in back:
        raise SystemExit(f"READBACK FAIL: prompt not found in {p}")
    return p


def mark_returned(record, agent_id):
    p = Path(record)
    s = p.read_text(encoding="utf-8")
    if "returned: null" not in s:
        raise SystemExit(f"record already marked returned: {p}")
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S local")
    s = s.replace("returned: null", f"returned: {agent_id} at {now}", 1)
    p.write_text(s, encoding="utf-8", newline="\n")
    return p


def selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="dispatch_record_"))
    prompt = "Test prompt line 1\nline 2 with `code` and a 'quote'\n"
    p = write_record("SELFTEST", "sonnet", "none", prompt, out_dir=tmp)
    s = p.read_text(encoding="utf-8")
    ok = all(x in s for x in ("kind: dispatch-record", "- head:", "- gate:", "- meter:", "line 2 with `code`"))
    print("PASS record written with state + verbatim prompt" if ok else "FAIL record incomplete")
    mark_returned(p, "a0000000000000000")
    s2 = p.read_text(encoding="utf-8")
    ok2 = "returned: a0000000000000000 at" in s2
    print("PASS returned stamp" if ok2 else "FAIL returned stamp")
    try:
        mark_returned(p, "a1")
        print("FAIL double-return accepted"); ok3 = False
    except SystemExit:
        print("PASS double-return refused"); ok3 = True
    print("SELFTEST", "PASS" if ok and ok2 and ok3 else "FAIL")
    return 0 if ok and ok2 and ok3 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug"); ap.add_argument("--tier", default="UNKNOWN")
    ap.add_argument("--write-set", default="UNKNOWN"); ap.add_argument("--prompt-file")
    ap.add_argument("--returned"); ap.add_argument("--record")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.returned:
        if not a.record:
            ap.error("--returned needs --record")
        print(mark_returned(a.record, a.returned)); return 0
    if not (a.slug and a.prompt_file):
        ap.error("--slug and --prompt-file are required")
    prompt = Path(a.prompt_file).read_text(encoding="utf-8")
    print(write_record(a.slug, a.tier, a.write_set, prompt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
