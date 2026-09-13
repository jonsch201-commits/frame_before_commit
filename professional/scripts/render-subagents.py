#!/usr/bin/env python3
"""scripts/render-subagents.py -- render every SUBAGENT JSONL under this trunk's project dirs to markdown.

WHY (2026-09-12, wikiskills pass 3, seat 682d274b): render-sessions.sh renders <key>/*.jsonl -- the MAIN
sessions only. Nothing rendered <key>/<sid>/subagents/agent-*.jsonl, so the whole class the universal
CLAUDE.md names ("type: user + isMeta: true -- messages he sends mid-turn to a subagent -- never appear in
any main transcript") reached no markdown, no index, no retriever. [m 14:5x] 127 such files under this
trunk's keys, 0 rendered.

WE DO NOT HAND-ROLL THE TRANSCRIPT BODY. render-sessions.sh's rule holds here: CFL's chat-exporter
convert-claude-code.py is the fleet converter, and it already detects subagent records by shape
(isSidechain + agentId) and writes session_kind/parent_session/agent_models frontmatter. This script CALLS
it once per subagent JSONL. What the converter does NOT do -- and what this script adds, additively, after
the converter's own output -- is distinguish `isMeta: true` user turns from the orchestrator's dispatch: the
converter renders both as `## Dispatch`. So an appendix lists every isMeta user turn VERBATIM, each marked
`JON MID-TURN (isMeta)`.

THE MARKER IS A CLASS LABEL, NOT AN ATTRIBUTION. [m 14:5x, this trunk, 37 isMeta user turns]: 29 open
`[SYSTEM NOTIFICATION - NOT USER INPUT]` or `[Image: ...]`, 8 open `The coordinator sent a message while
you were working:`, 0 are Jon-typed. The universal file's row calls the class Jon's; the 09-05 census calls
it "Jon-possible". Read the text before quoting it as his.

Naming: the converter's own (code-<date>-<stem6>-<slug>.md + .sidecar.md), inside
  raw/transcripts/claude-code-subagents/<parent-sid8>/
so the 6-char-prefix match every other instrument here uses keeps working. Idempotent by mtime: a subagent
whose md is newer than its jsonl is skipped. Missing converter => UNKNOWN, exit 2, never a fallback.

Usage: python scripts/render-subagents.py [--all] [--selftest] [--verbose]
Env:   PRO_CONVERTER, PRO_SUBAGENT_RENDER_OUT, PRO_PROJECT_DIR (space-separated, overrides project_dirs.py)
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONV = Path(os.environ.get("PRO_CONVERTER", "N:/claude-cfl/clone/skills/chat-exporter/scripts/convert-claude-code.py"))
OUT = Path(os.environ.get("PRO_SUBAGENT_RENDER_OUT", str(ROOT / "raw/transcripts/claude-code-subagents")))
MARKER = "JON MID-TURN (isMeta)"
QUALIFIER = ("class label only -- isMeta user turns are Jon-POSSIBLE (universal CLAUDE.md row 2), "
             "not Jon-attributed; system notifications and coordinator relays land in the same class")


def project_dirs():
    env = os.environ.get("PRO_PROJECT_DIR")
    if env:
        return [Path(p) for p in env.split() if p]
    r = subprocess.run([sys.executable, str(ROOT / "scripts/project_dirs.py")], capture_output=True, text=True)
    return [Path(l.strip()) for l in r.stdout.splitlines() if l.strip()]


def turn_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def read_jsonl(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except Exception:
                continue


def ismeta_turns(path):
    out = []
    for o in read_jsonl(path):
        if o.get("type") == "user" and o.get("isMeta") is True:
            out.append((o.get("timestamp", "?"), turn_text((o.get("message") or {}).get("content"))))
    return out


def parent_sid(path):
    for o in read_jsonl(path):
        if o.get("sessionId"):
            return o["sessionId"]
    return path.parent.parent.name  # path-derived fallback; the converter derives it from the records


def existing_render(outdir, stem6):
    if not outdir.exists():
        return None
    for p in outdir.glob(f"code-*-{stem6}-*.md"):
        if not p.name.endswith(".sidecar.md"):
            return p
    return None


def append_ismeta(md_path, turns, parent, jsonl):
    if not turns:
        return
    lines = ["", "---", "", f"## Mid-turn user turns (`isMeta: true`) -- {len(turns)} in this subagent", "",
             f"Parent session: `{parent}`. Source: `{jsonl}`. Appended by scripts/render-subagents.py; the",
             "converter above renders these under `## Dispatch`, indistinguishable from the opening brief.",
             f"Marker `{MARKER}` is a {QUALIFIER}.", ""]
    for i, (ts, txt) in enumerate(turns, 1):
        lines += [f"### {MARKER} #{i} -- {ts}", "", txt, ""]
    with open(md_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def render_one(jsonl, outdir, force=False, verbose=False):
    """returns (status, md_path). status in rendered|skipped|failed"""
    stem6 = jsonl.stem.replace("agent-", "")[:6]
    prev = existing_render(outdir, stem6)
    if prev is not None and not force and prev.stat().st_mtime > jsonl.stat().st_mtime:
        return "skipped", prev
    outdir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(CONV), "--run", str(jsonl), "--out", str(outdir), "--force", "--project", "pro"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    wrote = [l for l in r.stdout.splitlines() if l.startswith("WROTE:") and ".sidecar.md" not in l]
    if r.returncode != 0 or not wrote:
        if verbose:
            print(r.stdout[-800:], r.stderr[-800:], file=sys.stderr)
        return "failed", None
    md_path = Path(wrote[0].split("WROTE:", 1)[1].split("  (")[0].strip())
    if not md_path.exists():
        return "failed", None
    append_ismeta(md_path, ismeta_turns(jsonl), parent_sid(jsonl), jsonl)
    return "rendered", md_path


def main(argv):
    force = "--all" in argv
    verbose = "--verbose" in argv
    if not CONV.exists():
        print(f"RENDER-SUBAGENTS: UNKNOWN -- converter not found at {CONV}; not zero, and not a reason to hand-roll one.")
        return 2
    dirs = project_dirs()
    if not dirs:
        print("RENDER-SUBAGENTS: UNKNOWN -- no project dir resolves for this tree (project_dirs.py)")
        return 2
    pre = max([p.stat().st_mtime for p in OUT.rglob("*.md")] or [0]) if OUT.exists() else 0
    scanned = rendered = skipped = failed = 0
    meta_total = 0
    for d in dirs:
        files = sorted(d.glob("*/subagents/agent-*.jsonl"))
        n_meta = 0
        for j in files:
            scanned += 1
            n_meta += len(ismeta_turns(j))
            st, md = render_one(j, OUT / j.parent.parent.name[:8], force, verbose)
            if st == "rendered":
                rendered += 1
                if verbose:
                    print(f"  RENDERED: {j} -> {md}")
            elif st == "skipped":
                skipped += 1
            else:
                failed += 1
                print(f"  FAILED: {j}")
        meta_total += n_meta
        print(f"  POPULATION: {d}  subagent_jsonl={len(files)} isMeta_user_turns={n_meta}")
    print(f"RENDER-SUBAGENTS: scanned={scanned} rendered={rendered} skipped={skipped} failed={failed}  isMeta_user_turns={meta_total}  out={OUT}")
    if rendered > 0:
        post = max([p.stat().st_mtime for p in OUT.rglob("*.md")] or [0])
        if post <= pre:
            print(f"RENDER-SUBAGENTS: FAIL -- claimed rendered={rendered} but newest md did not advance ({pre} -> {post})")
            return 1
        print(f"  EFFECT PROVEN: newest md mtime advanced {int(pre)} -> {int(post)}")
    if scanned == 0:
        print("RENDER-SUBAGENTS: UNKNOWN -- scanned 0 subagent JSONLs. A zero population is not a pass.")
        return 2
    return 1 if failed else 0


def _fixture(dirpath, sid, aid, with_meta):
    sub = Path(dirpath) / sid / "subagents"
    sub.mkdir(parents=True)
    base = {"isSidechain": True, "agentId": aid, "sessionId": sid, "version": "9.9.9", "gitBranch": "master", "cwd": str(dirpath)}
    recs = [dict(base, parentUuid=None, uuid="u1", type="user", timestamp="2026-09-12T19:00:00.000Z",
                 message={"role": "user", "content": "Fixture dispatch brief from the orchestrator."}),
            dict(base, parentUuid="u1", uuid="a1", type="assistant", timestamp="2026-09-12T19:00:01.000Z",
                 message={"role": "assistant", "model": "claude-fixture-1", "content": [{"type": "text", "text": "Fixture assistant reply."}]})]
    if with_meta:
        recs.append(dict(base, parentUuid="a1", uuid="u2", type="user", isMeta=True, timestamp="2026-09-12T19:00:02.000Z",
                         message={"role": "user", "content": "FIXTURE-ISMETA-TEXT typed mid-turn, verbatim, typos kept."}))
        recs.append(dict(base, parentUuid="u2", uuid="a2", type="assistant", timestamp="2026-09-12T19:00:03.000Z",
                         message={"role": "assistant", "model": "claude-fixture-1", "content": [{"type": "text", "text": "Ack."}]}))
    p = sub / f"agent-{aid}.jsonl"
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return p


def selftest():
    if not CONV.exists():
        print(f"SELFTEST: UNKNOWN -- converter not found at {CONV}")
        return 2
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out"
        j1 = _fixture(td, "11111111-aaaa-bbbb-cccc-000000000001", "a1fixture00000001", True)
        j2 = _fixture(td, "22222222-aaaa-bbbb-cccc-000000000002", "b2fixture00000002", False)
        s1, m1 = render_one(j1, out / "11111111")
        s2, m2 = render_one(j2, out / "22222222")
        t1 = m1.read_text(encoding="utf-8") if m1 else ""
        t2 = m2.read_text(encoding="utf-8") if m2 else ""
        v1 = (s1 == "rendered" and MARKER in t1
              and "FIXTURE-ISMETA-TEXT typed mid-turn, verbatim, typos kept." in t1
              and "parent_session: 11111111-aaaa-bbbb-cccc-000000000001" in t1 and "claude-fixture-1" in t1)
        v2 = s2 == "rendered" and MARKER not in t2 and "Fixture dispatch brief" in t2
        s3, _ = render_one(j1, out / "11111111")
        s4, _ = render_one(j2, out / "22222222")
        v3 = s3 == "skipped" and s4 == "skipped"
        print(f"SELFTEST fixture-with-isMeta: {'PASS' if v1 else 'FAIL'} (status={s1}, marker={MARKER in t1}, "
              f"verbatim={'FIXTURE-ISMETA-TEXT' in t1}, parent+model in frontmatter={'parent_session: 1111' in t1 and 'claude-fixture-1' in t1})")
        print(f"SELFTEST fixture-without-isMeta: {'PASS' if v2 else 'FAIL'} (status={s2}, marker absent={MARKER not in t2})")
        print(f"SELFTEST idempotent-by-mtime: {'PASS' if v3 else 'FAIL'} (second pass: {s3}, {s4})")
        ok = v1 and v2 and v3
        print(f"SELFTEST: {'PASS' if ok else 'FAIL'} -- 3 checks, converter={CONV}")
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main(sys.argv[1:]))
