#!/usr/bin/env python3
"""scripts/session_identity.py — session IDENTITY pages (main sessions and subagents) for this trunk, with no defaulted field.

Derived from Antigravity's approved prototype (barrier_session_identity.py, sha256 9d424c2e…, 2026-09-05) with the two
review conditions applied: every count names what it counts, and Jon's turns are a separate measured field.

Rules (Jon 2026-09-05 20:4x, 22:1x; Professional map OV-4):
  * A field the parser could not read renders UNKNOWN, never 0.  A truncated JSONL marks every count UNKNOWN.
  * jon_turns = user lines with origin.kind == "human".  Where NO line in the file carries an `origin` field (older harness),
    the structural fallback is used and the field is labelled "<n> (structural fallback)".
  * user_lines counts every type:user line; tool_result_lines those carrying a tool_result block; meta_lines the isMeta ones.
  * render is matched by the renderer's 6-char prefix.  subagents are counted live (<key>/<sid>/subagents/) and archived
    (raw/session-archive/<sid>/subagents/).

Modes:
  --jsonl <path> [--trunk-root R] [--output F]       one page
  --all --trunk-root R                                every main session under the trunk's project keys -> wiki/sources/sessions/
  --subagents --trunk-root R                          one page per subagent JSONL (live + archived) -> wiki/sources/sessions/subagents/<sid8>/
  --coverage --trunk-root R                           print the MISSING list (sessions with no page), exit 3 if non-empty
  --selftest                                          planted fixture, truncated fixture, no-origin fixture
"""
import argparse, hashlib, io, json, os, re, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_KEYS = {"professional": ["N--claude-professional", "G--My-Drive-Claude-Claude-Professional-claude-professional"]}
PROJECTS = Path(os.path.expanduser("~/.claude/projects"))


def script_sha() -> str:
    return hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()


def read_jsonl(path: Path):
    """Yield parsed records; return (records, parse_errors, truncated). Truncated = last non-empty line unparseable."""
    recs, errors, truncated = [], 0, False
    try:
        lines = io.open(path, encoding="utf-8", errors="replace").read().split("\n")
    except Exception:
        return [], 0, True
    nonempty = [l for l in lines if l.strip()]
    for i, l in enumerate(nonempty):
        try:
            recs.append(json.loads(l))
        except Exception:
            errors += 1
            if i == len(nonempty) - 1:
                truncated = True
    return recs, errors, truncated


def user_text(msg):
    c = (msg or {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""


def has_tool_result(msg):
    c = (msg or {}).get("content")
    return isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c)


def measure(jsonl_path: Path, trunk_root: Path | None = None, kind: str = "main") -> dict:
    sid_full = jsonl_path.stem
    sid8 = sid_full[:8]
    proj_key = jsonl_path.parent.name if kind == "main" else jsonl_path.parent.parent.parent.name
    recs, parse_errors, truncated = read_jsonl(jsonl_path)
    ts = [r.get("timestamp") for r in recs if r.get("timestamp")]
    user_lines = tool_result_lines = meta_lines = tool_use = boundaries = queued = 0
    jon_origin = 0
    jon_structural = 0
    any_origin = False
    models = set()
    first_user_text = ""
    for r in recs:
        t = r.get("type")
        msg = r.get("message") if isinstance(r.get("message"), dict) else {}
        if t == "attachment" and isinstance(r.get("attachment"), dict) and r["attachment"].get("type") == "queued_command":
            queued += 1
        if t == "user":
            user_lines += 1
            if has_tool_result(msg):
                tool_result_lines += 1
                continue
            if r.get("isMeta"):
                meta_lines += 1
                continue
            og = r.get("origin")
            if isinstance(og, dict):
                any_origin = True
                if og.get("kind") == "human":
                    jon_origin += 1
            txt = user_text(msg).lstrip()
            if txt and not txt.startswith("<system-reminder>") and not txt.startswith("<local-command"):
                jon_structural += 1
                if not first_user_text:
                    first_user_text = txt[:160].replace("\n", " ")
        if t == "assistant":
            for b in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tool_use += 1
            m = msg.get("model")
            if m and m != "<synthetic>":
                models.add(m)
        if r.get("subtype") == "compact_boundary":
            boundaries += 1
    U = "UNKNOWN"
    if any_origin:
        jon_turns = str(jon_origin)
    elif recs:
        jon_turns = f"{jon_structural} (structural fallback: no origin field in this file)"
    else:
        jon_turns = U
    out = {
        "session": sid_full, "sid8": sid8, "kind": kind, "project_key": proj_key,
        "born": min(ts) if ts else U, "last_write": max(ts) if ts else U,
        "records": len(recs) if not truncated else U,
        "user_lines": user_lines if not truncated else U,
        "tool_result_lines": tool_result_lines if not truncated else U,
        "meta_lines": meta_lines if not truncated else U,
        "jon_turns": jon_turns if not truncated else U,
        "queued_commands": queued if not truncated else U,
        "tool_use": tool_use if not truncated else U,
        "models": sorted(models) if models else [U],
        "compact_boundaries": boundaries if not truncated else U,
        "first_user_text": first_user_text or U,
        "parse_errors": parse_errors, "truncated": truncated,
        "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "measured_by": f"scripts/session_identity.py sha256:{script_sha()}",
    }
    if kind == "main":
        live_dir = jsonl_path.parent / sid_full / "subagents"
        out["subagents_live"] = len(list(live_dir.glob("agent-*.jsonl"))) if live_dir.exists() else 0
        if trunk_root:
            arch = trunk_root / "raw" / "session-archive" / sid_full
            out["archived"] = "YES" if arch.exists() and any(p.suffix == ".jsonl" and p.stat().st_size > 0 for p in arch.iterdir()) else "NO"
            arch_sub = arch / "subagents"
            out["subagents_archived"] = len(list(arch_sub.glob("agent-*.jsonl"))) if arch_sub.exists() else 0
            rd = trunk_root / "raw" / "transcripts" / "claude-code"
            m = sorted(rd.glob(f"*{sid_full[:6]}*.md")) if rd.exists() else []
            out["render"] = m[0].name if m else ("NO" if rd.exists() else "NO_DIR")
            out["elder_note"] = "YES" if (trunk_root / "exchange" / "elders" / f"NOTE-{sid8}.md").exists() else "NO"
            lg = trunk_root / "wiki" / "log.md"
            out["log_mentions"] = len(re.findall(re.escape(sid8), lg.read_text(encoding="utf-8", errors="replace"))) if lg.exists() else U
            try:
                res = subprocess.run(["git", "-C", str(trunk_root), "log", "--all", "--oneline", f"--grep={sid8}"], capture_output=True, text=True, timeout=20)
                out["commits"] = len([l for l in res.stdout.splitlines() if l.strip()]) if res.returncode == 0 else U
            except Exception:
                out["commits"] = U
        else:
            for k in ("archived", "subagents_archived", "render", "elder_note", "log_mentions", "commits"):
                out[k] = U
    else:
        out["parent_session"] = jsonl_path.parent.parent.name
        out["bytes"] = jsonl_path.stat().st_size
    return out


def page(meta: dict) -> str:
    fm = ["---", "kind: session-identity" if meta["kind"] == "main" else "subagent-identity"]
    if meta["kind"] != "main":
        fm[-1] = "kind: subagent-identity"
    for k, v in meta.items():
        if k == "kind":
            continue
        if isinstance(v, list):
            fm.append(f"{k}: {json.dumps(v)}")
        elif isinstance(v, (int, bool)):
            fm.append(f"{k}: {str(v).lower() if isinstance(v, bool) else v}")
        else:
            fm.append(f"{k}: {json.dumps(str(v))}")
    fm.append("status: MEASURED_NO_DEFAULTS" + (" (TRUNCATED FILE — counts UNKNOWN)" if meta.get("truncated") else ""))
    fm.append("---")
    title = f"# {'Session' if meta['kind']=='main' else 'Subagent'} identity — {meta['sid8'] if meta['kind']=='main' else meta['session']}"
    body = [title, "", "Identity only: measured fields, no content summary. A field reads UNKNOWN where the parser could not read it; nothing here is a default.", "",
            "| field | value |", "|---|---|"]
    for k, v in meta.items():
        body.append(f"| {k} | `{v if not isinstance(v, list) else ', '.join(v)}` |")
    return "\n".join(fm + [""] + body) + "\n"


def main_sessions(trunk: str):
    for key in PROJECT_KEYS[trunk]:
        d = PROJECTS / key
        if d.exists():
            for p in sorted(d.glob("*.jsonl")):
                yield p


def cmd_all(trunk_root: Path, trunk: str):
    outdir = trunk_root / "wiki" / "sources" / "sessions"
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in main_sessions(trunk):
        m = measure(p, trunk_root)
        date = m["born"][:10] if m["born"] != "UNKNOWN" else "UNKNOWN-DATE"
        f = outdir / f"{date}-{m['sid8']}.md"
        f.write_text(page(m), encoding="utf-8", newline="\n")
        rows.append((date, m))
    rows.sort(key=lambda r: r[0])
    idx = ["# Session identity index", "", f"Trunk `{trunk}`; keys {PROJECT_KEYS[trunk]}; {len(rows)} main sessions; written by `scripts/session_identity.py --all` at {datetime.now(timezone.utc).isoformat(timespec='seconds')} (sha256 {script_sha()[:12]}…). Every field measured; UNKNOWN where unreadable.", "",
           "| date | sid8 | jon_turns | user_lines | tool_use | boundaries | subagents live/archived | archived | render | elder note |", "|---|---|---|---|---|---|---|---|---|---|"]
    for date, m in rows:
        idx.append(f"| {date} | [{m['sid8']}]({date}-{m['sid8']}.md) | {m['jon_turns']} | {m['user_lines']} | {m['tool_use']} | {m['compact_boundaries']} | {m['subagents_live']}/{m['subagents_archived']} | {m['archived']} | {'Y' if m['render'] not in ('NO','NO_DIR','UNKNOWN') else m['render']} | {m['elder_note']} |")
    (outdir / "INDEX.md").write_text("\n".join(idx) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(rows)} session pages + INDEX.md to {outdir}")


def cmd_subagents(trunk_root: Path, trunk: str):
    base = trunk_root / "wiki" / "sources" / "sessions" / "subagents"
    n = 0
    seen = set()
    sources = []
    for key in PROJECT_KEYS[trunk]:
        for p in (PROJECTS / key).glob("*/subagents/agent-*.jsonl"):
            sources.append(("live", p))
    arch = trunk_root / "raw" / "session-archive"
    if arch.exists():
        for p in arch.glob("*/subagents/agent-*.jsonl"):
            sources.append(("archived", p))
    for where, p in sources:
        parent = p.parent.parent.name
        if (parent, p.stem) in seen:
            continue
        seen.add((parent, p.stem))
        m = measure(p, trunk_root, kind="subagent")
        m["source"] = where
        d = base / parent[:8]
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{p.stem}.md").write_text(page(m), encoding="utf-8", newline="\n")
        n += 1
    print(f"wrote {n} subagent identity pages under {base} (live+archived, deduplicated by parent+agent id)")


def boundary_count(p: Path) -> int:
    """Structural count of compact_boundary records. The string is a PREFILTER only —
    the verdict is the parsed subtype, never the grep (the grep returned 123 against 102
    structural on CFL, 2026-09-05)."""
    n = 0
    try:
        with p.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "compact_boundary" not in line:
                    continue
                try:
                    if json.loads(line).get("subtype") == "compact_boundary":
                        n += 1
                except Exception:
                    continue
    except OSError:
        return 0
    return n


def coverage_report(sessions, outdir: Path, live_sid: str = "", boundaries=boundary_count):
    """Partition sessions with no identity page into two classes that behave differently.

    LIVE  — this very seat, which has not reached a barrier yet, so no barrier has had the
            chance to write its page. Reported, NOT a failure.
    GAP   — every other missing page, INCLUDING the live seat once it has passed a compact
            boundary. A failure.

    The exemption is deliberately one session wide and conditioned on boundaries == 0, so it
    is failable on its own axis: a live seat that HAS compacted and still has no page is a GAP.
    Without that condition the exemption would silently absorb the barrier defect it exists to
    make visible.
    """
    live, gap, total = [], [], 0
    for p in sessions:
        total += 1
        if list(outdir.glob(f"*-{p.stem[:8]}.md")):
            continue
        if live_sid and p.stem == live_sid and boundaries(p) == 0:
            live.append(p.stem)
        else:
            gap.append(p.stem)
    return total, live, gap


def cmd_coverage(trunk_root: Path, trunk: str, live_sid: str = "") -> int:
    trunk_root = trunk_root or Path(".")
    outdir = trunk_root / "wiki" / "sources" / "sessions"
    total, live, gap = coverage_report(main_sessions(trunk), outdir, live_sid)
    present = total - len(live) - len(gap)
    print(f"COVERAGE: {present} of {total} main sessions have an identity page; "
          f"GAP {len(gap)}; LIVE-NO-BARRIER-YET {len(live)}")
    for m in gap:
        print("  MISSING-GAP ", m)
    for m in live:
        print("  MISSING-LIVE", m, "(this seat, 0 compact boundaries — not counted as a gap)")
    return 3 if gap else 0


def selftest() -> int:
    fails = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "N--claude-professional"
        d.mkdir()
        planted = d / "11111111-aaaa-bbbb-cccc-dddddddddddd.jsonl"
        recs = [
            {"timestamp": "2026-09-05T12:00:00Z", "type": "user", "origin": {"kind": "human"}, "message": {"content": "hello"}},
            {"timestamp": "2026-09-05T12:00:30Z", "type": "user", "origin": {"kind": "peer"}, "message": {"content": "peer says hi"}},
            {"timestamp": "2026-09-05T12:01:00Z", "type": "user", "isMeta": True, "message": {"content": "meta"}},
            {"timestamp": "2026-09-05T12:01:30Z", "type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}},
            {"timestamp": "2026-09-05T12:02:00Z", "type": "assistant", "message": {"model": "claude-opus-5", "content": [{"type": "tool_use", "name": "a"}]}},
            {"timestamp": "2026-09-05T12:03:00Z", "type": "assistant", "message": {"model": "claude-fable-5-1", "content": [{"type": "tool_use", "name": "b"}]}},
            {"timestamp": "2026-09-05T12:03:30Z", "type": "attachment", "attachment": {"type": "queued_command", "prompt": "later"}},
            {"timestamp": "2026-09-05T12:04:00Z", "type": "system", "subtype": "compact_boundary"},
        ]
        planted.write_text("\n".join(json.dumps(r) for r in recs), encoding="utf-8")
        m = measure(planted, Path(td))
        exp = {"jon_turns": "1", "user_lines": 4, "tool_result_lines": 1, "meta_lines": 1, "tool_use": 2, "compact_boundaries": 1, "queued_commands": 1,
               "models": ["claude-fable-5-1", "claude-opus-5"], "born": "2026-09-05T12:00:00Z", "last_write": "2026-09-05T12:04:00Z", "archived": "NO", "render": "NO_DIR"}
        for k, v in exp.items():
            if m.get(k) != v:
                fails.append(f"planted {k}: expected {v!r} got {m.get(k)!r}")
        # truncated fixture: last line cut mid-record -> every count UNKNOWN
        trunc = d / "22222222-aaaa-bbbb-cccc-dddddddddddd.jsonl"
        trunc.write_text("\n".join(json.dumps(r) for r in recs[:3]) + "\n" + json.dumps(recs[4])[:40], encoding="utf-8")
        mt = measure(trunc, Path(td))
        for k in ("user_lines", "tool_use", "compact_boundaries", "jon_turns"):
            if mt.get(k) != "UNKNOWN":
                fails.append(f"truncated {k}: expected UNKNOWN got {mt.get(k)!r}")
        if not mt.get("truncated"):
            fails.append("truncated flag not set")
        # no-origin fixture: older harness -> structural fallback, labelled
        old = d / "33333333-aaaa-bbbb-cccc-dddddddddddd.jsonl"
        old.write_text("\n".join(json.dumps(r) for r in [
            {"timestamp": "2026-08-01T00:00:00Z", "type": "user", "message": {"content": "typed by jon, no origin field"}},
            {"timestamp": "2026-08-01T00:01:00Z", "type": "assistant", "message": {"model": "claude-opus-5", "content": []}}]), encoding="utf-8")
        mo = measure(old, Path(td))
        if not str(mo.get("jon_turns")).startswith("1 (structural fallback"):
            fails.append(f"no-origin jon_turns: expected '1 (structural fallback…)' got {mo.get('jon_turns')!r}")
        # empty file -> UNKNOWN born/models/jon_turns
        empty = d / "44444444-aaaa-bbbb-cccc-dddddddddddd.jsonl"
        empty.write_text("", encoding="utf-8")
        me = measure(empty, Path(td))
        for k in ("born", "jon_turns"):
            if me.get(k) != "UNKNOWN":
                fails.append(f"empty {k}: expected UNKNOWN got {me.get(k)!r}")
        if me.get("models") != ["UNKNOWN"]:
            fails.append(f"empty models: {me.get('models')!r}")
        # ---- coverage, four cases: both verdicts, plus a control for each negative ----
        # (before 2026-09-07 this block built fixtures and asserted NOTHING — an inert stub
        #  inside a passing selftest, which is the same shape as a guard that cannot fail.)
        root = Path(td)
        cov = root / "wiki" / "sources" / "sessions"
        cov.mkdir(parents=True)
        s_done = d / "aaaaaaaa-0000-0000-0000-000000000000.jsonl"
        s_live = d / "bbbbbbbb-0000-0000-0000-000000000000.jsonl"
        for s in (s_done, s_live):
            s.write_text("", encoding="utf-8")
        (cov / "2026-09-05-aaaaaaaa.md").write_text("x", encoding="utf-8")
        live_sid = s_live.stem

        # C1 CLEAN: every session has a page -> PASS
        (cov / "2026-09-05-bbbbbbbb.md").write_text("x", encoding="utf-8")
        t, lv, gp = coverage_report([s_done, s_live], cov, live_sid, lambda p: 0)
        if (t, lv, gp) != (2, [], []):
            fails.append(f"coverage C1 clean: expected (2,[],[]) got {(t, lv, gp)}")
        (cov / "2026-09-05-bbbbbbbb.md").unlink()

        # C2 GAP: a session that is NOT the live seat has no page -> FAIL
        t, lv, gp = coverage_report([s_done, s_live], cov, live_sid="", boundaries=lambda p: 0)
        if gp != [s_live.stem]:
            fails.append(f"coverage C2 gap: expected the missing page to be a GAP, got {gp}")

        # C3 LIVE: the live seat, 0 boundaries, no page -> reported LIVE, NOT a gap
        t, lv, gp = coverage_report([s_done, s_live], cov, live_sid, lambda p: 0)
        if (lv, gp) != ([live_sid], []):
            fails.append(f"coverage C3 live: expected live={[live_sid]} gap=[] got live={lv} gap={gp}")

        # C4 CONTROL on the exemption — the live seat HAS compacted and still has no page.
        # This must FAIL, or the C3 exemption absorbs the barrier defect it exists to expose.
        t, lv, gp = coverage_report([s_done, s_live], cov, live_sid, lambda p: 1)
        if (lv, gp) != ([], [live_sid]):
            fails.append(f"coverage C4 control: a compacted live seat with no page must be a GAP, got live={lv} gap={gp}")

        # C5 CONTROL on the counter — a grep-only counter would score 2 on this fixture;
        # the parsed subtype is the verdict, so it must score 1.
        bf = d / "cccccccc-0000-0000-0000-000000000000.jsonl"
        bf.write_text("\n".join([
            json.dumps({"type": "system", "subtype": "compact_boundary"}),
            json.dumps({"type": "assistant", "message": {"content": "we discussed compact_boundary records"}}),
        ]), encoding="utf-8")
        if boundary_count(bf) != 1:
            fails.append(f"boundary_count: prose mentioning compact_boundary must not count; got {boundary_count(bf)}")
    for f in fails:
        print("SELFTEST FAIL", f)
    print("SELFTEST", "PASS" if not fails else f"FAIL ({len(fails)})",
          "— planted / truncated / no-origin / empty fixtures; coverage C1 clean / C2 gap / C3 live / C4 exemption-control / C5 counter-control")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", type=Path); ap.add_argument("--trunk-root", type=Path, default=Path(".")); ap.add_argument("--output", type=Path)
    ap.add_argument("--live-sid", default=os.environ.get("CLAUDE_CODE_SESSION_ID", ""),
                    help="the seat running this check; its own page cannot exist before its first barrier. "
                         "Exempt ONLY while it has 0 compact boundaries — see coverage_report().")
    ap.add_argument("--outdir", type=Path, help="write <outdir>/<born-date>-<sid8>.md — the same name --all uses, so a barrier run never makes a second page for one session")
    ap.add_argument("--trunk", default="professional")
    ap.add_argument("--all", action="store_true"); ap.add_argument("--subagents", action="store_true"); ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.all:
        cmd_all(a.trunk_root, a.trunk); return
    if a.subagents:
        cmd_subagents(a.trunk_root, a.trunk); return
    if a.coverage:
        sys.exit(cmd_coverage(a.trunk_root, a.trunk, a.live_sid))
    if a.jsonl:
        m = measure(a.jsonl, a.trunk_root)
        md = page(m)
        if a.outdir:
            date = m["born"][:10] if m["born"] != "UNKNOWN" else "UNKNOWN-DATE"
            a.outdir.mkdir(parents=True, exist_ok=True)
            f = a.outdir / f"{date}-{m['sid8']}.md"
            f.write_text(md, encoding="utf-8", newline="\n"); print("wrote", f); return
        if a.output:
            a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(md, encoding="utf-8", newline="\n"); print("wrote", a.output)
        else:
            print(md)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
