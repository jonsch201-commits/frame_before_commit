#!/usr/bin/env python3
"""PROTOTYPE — throwaway code that answers ONE question (ES-2 on wayfinder-everyone-sees-everything-2026-09-06):

    Does rendering Jon's typed-prompt log (~/.claude/history.jsonl) into the wiki, one month per page, one turn per
    section, make the FORGOTTEN-PRIOR-RULINGS probes return his primary at rank <= 3?

What it does: reads every line of history.jsonl (display, timestamp ms, project, sessionId), writes
wiki/sources/jon-typed-prompts/history-YYYY-MM.md with `### L<line> · <YYYY-MM-DD HH:MM CDT> · <project tail> · <sid8>`
headings and the verbatim display text (typos his), and an INDEX.md. Line numbers are preserved so a hit cites
`history.jsonl:<line>` exactly as the fleet already does by hand.

Deviation from the /prototype adaptation note, stated: the proto/ branch + off-Drive worktree rule is NOT used, because
this trunk's builder (scripts/graphrag_pro.py) is root-bound and writes the ONE shared DB (professional.sqlite); a
worktree would index a different root into the same DB and answer a different question. The pages are the experiment
and are removed or kept on the measured verdict (rule 6).

Not production: no error handling beyond runnability, no tests. Selftest = a planted line must round-trip to a page.
"""
import io, json, os, sys, datetime, collections
from pathlib import Path

SRC = Path(os.path.expanduser("~/.claude/history.jsonl"))
OUT = Path(__file__).resolve().parent.parent / "wiki" / "sources" / "jon-typed-prompts"


def render(src=SRC, out=OUT):
    out.mkdir(parents=True, exist_ok=True)
    months = collections.defaultdict(list)
    excluded = []
    n = 0
    with io.open(src, encoding="utf-8", errors="replace") as fh:
        for line_no, line in enumerate(fh, 1):
            try:
                o = json.loads(line)
            except Exception:
                continue
            ts = o.get("timestamp")
            if not ts:
                continue
            dt = datetime.datetime.fromtimestamp(ts / 1000)  # local clock (CDT on this machine)
            proj = (o.get("project") or "")
            # 2026-09-06 15:5x — CONTENT SCREEN (Herald's finding: a census that selects on SPEAKER cannot enforce a CONTENT rule).
            # XC-Exchequer is a T2/T3 content class whose no-remote rule is ABSOLUTE; prompts typed into that project stay OUT of
            # this tracked render. They remain in ~/.claude/history.jsonl and are written, untracked, under raw/ instead.
            if "XC-Exchequer" in proj or "exchequer" in proj.lower():
                excluded.append((line_no, ts, proj, o))
                continue
            tail = proj.replace("\\", "/").rstrip("/").split("/")[-1] or "?"
            sid8 = (o.get("sessionId") or "")[:8]
            text = (o.get("display") or "").replace("\r", "")
            months[dt.strftime("%Y-%m")].append((line_no, dt, tail, sid8, text))
            n += 1
    idx = ["---", "kind: source-index", "title: Jon's typed prompts (Claude Code), rendered from ~/.claude/history.jsonl — one page per month, one section per prompt, line numbers preserved",
           f"rendered: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (local clock)", f"prompts: {n}", "source: ~/.claude/history.jsonl (machine-global; every typed prompt to any trunk, with a millisecond clock)",
           "verbatim: true — typos his; emphasis never added inside a prompt", "status: PROTOTYPE-RENDER (ES-2) — kept if the probe set passes, else removed",
           "---", "", "# Jon's typed prompts, by month", "", "| month | prompts | page |", "|---|---|---|"]
    for m in sorted(months):
        rows = months[m]
        p = out / f"history-{m}.md"
        lines = ["---", "kind: jon-source", f"title: Jon's typed prompts — {m} ({len(rows)} prompts, verbatim, from ~/.claude/history.jsonl)",
                 f"month: {m}", f"prompts: {len(rows)}", "verbatim: true", "source: ~/.claude/history.jsonl", "status: PROTOTYPE-RENDER (ES-2)", "---", "",
                 f"# Jon's typed prompts — {m}", "", "Each section is one prompt he typed into a Claude Code session, verbatim (typos his). The heading carries the history.jsonl LINE number, the local clock, the project directory's last segment, and the session's 8-char prefix.", ""]
        for line_no, dt, tail, sid8, text in rows:
            lines.append(f"### L{line_no} · {dt.strftime('%Y-%m-%d %H:%M')} CDT · {tail} · {sid8}")
            lines.append("")
            lines.append(text if text.strip() else "(empty prompt)")
            lines.append("")
        p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        idx.append(f"| {m} | {len(rows)} | [{p.name}]({p.name}) |")
    idx.append("")
    idx.append(f"CONTENT SCREEN: {len(excluded)} prompt(s) typed into the XC-Exchequer project are NOT rendered here (T2/T3 content class; no-remote rule absolute). They stay in ~/.claude/history.jsonl and, untracked, under raw/jon-typed-prompts-exchequer/ (gitignored by raw/). Selecting on speaker does not enforce a content rule; this line is the screen.")
    (out / "INDEX.md").write_text("\n".join(idx) + "\n", encoding="utf-8", newline="\n")
    if excluded:
        xdir = out.parent.parent.parent / "raw" / "jon-typed-prompts-exchequer"
        xdir.mkdir(parents=True, exist_ok=True)
        xl = ["# Jon's typed prompts — XC-Exchequer project (UNTRACKED by design; raw/ is gitignored; never move into a tracked path, never quote into a letter)", ""]
        for line_no, ts, proj, o in excluded:
            dt = datetime.datetime.fromtimestamp(ts / 1000)
            xl.append(f"### L{line_no} · {dt.strftime('%Y-%m-%d %H:%M')} CDT · XC-Exchequer · {(o.get('sessionId') or '')[:8]}")
            xl.append("")
            xl.append((o.get("display") or "").replace("\r", "") or "(empty prompt)")
            xl.append("")
        (xdir / "history-exchequer.md").write_text("\n".join(xl) + "\n", encoding="utf-8", newline="\n")
    return n, sorted(months)


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "history.jsonl"
        src.write_text(json.dumps({"display": "PLANTED-PROBE-TOKEN xyzzy", "timestamp": 1757000000000, "project": "N:\\claude-professional", "sessionId": "abcdef12-0000"}) + "\n", encoding="utf-8")
        out = Path(td) / "out"
        n, months = render(src, out)
        pages = list(out.glob("history-*.md"))
        ok = n == 1 and len(pages) == 1 and "PLANTED-PROBE-TOKEN xyzzy" in pages[0].read_text(encoding="utf-8") and "### L1 ·" in pages[0].read_text(encoding="utf-8")
        print("SELFTEST", "PASS" if ok else "FAIL", f"prompts={n} pages={len(pages)}")
        return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    n, months = render()
    print(f"rendered {n} prompts into {len(months)} monthly pages under {OUT}")
