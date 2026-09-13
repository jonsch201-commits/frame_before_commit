#!/usr/bin/env python3
"""render_horizon.py -- how far behind the newest RECORD this trunk's RENDERED tree is. Per session.

BUILT 2026-09-12 ~16:0x CDT on Jon's manual trigger, verbatim, typos his:

    "3. PRINT THE HORIZON. Records on disk, records rendered, the difference, your largest unrendered
     session. The graph is current to the newest RENDER, never to the newest RECORD, so the gap is
     never zero and a report claiming zero has not measured. A trunk that cannot print this cannot
     tell a query's silence from its own blindness."

⛔ WHY A NEW FILE RATHER THAN THE EXISTING CHECK. `scripts/audit/render_freshness_check.py` compares
the NEWEST md against the NEWEST compact stamp and printed
`render-freshness PASS: newest md 2026-09-12 13:44:19 vs newest compact stamp 2026-09-12 11:26:54`
`[measured 16:0x today]`. ⭐ That is a two-file comparison and it PASSES while any number of individual
sessions are unrendered, because a single fresh render satisfies it. **It is a max(), not a coverage
measure.** Jon's step 3 asks for the per-session difference, which no instrument in this trunk had.

WHAT IT MEASURES, and each line degrades to a NAMED UNKNOWN:
  * RECORDS ON DISK   -- every `*.jsonl` under every project dir this tree resolves to (derived via
    `project_dirs`, live-plus-legacy, so the G:-era store counts too), main sessions and `subagents/`.
  * RECORDS RENDERED  -- a record is rendered if some `.md` under a render root carries its session
    id's short form in the filename. Two roots are searched: this repo's `raw/transcripts/` and the
    corpus mirror `N:\\claude-corpus\\cfl\\raw\\transcripts\\`, because the index walks the mirror.
  * STALE RENDER      -- rendered, but the JSONL is NEWER than its newest render. Invisible to the
    max()-style check above whenever anything else was rendered later.
  * LARGEST UNRENDERED -- by JSONL bytes, because that is the most content a markdown index cannot see.

⚠️ BOUND, stated because the match is a heuristic: renders are matched by the 6-char session prefix in
the filename (`code-2026-09-12-ab87d7-...`). A 6-char prefix CAN collide, and a render whose filename
drops the prefix reads as missing. So an UNRENDERED row is a CANDIDATE, and the count is an upper bound
on loss. It is still the only per-session measurement this trunk has.

Exit: 0 measured (with or without a gap -- a gap is the expected state, never an error) · 2 a root was
UNKNOWN, which dominates · 3 usage.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts", "audit"))

RENDER_ROOTS = [
    os.path.join(ROOT, "raw", "transcripts"),
    r"N:\claude-corpus\cfl\raw\transcripts",
]


def project_dirs_list():
    try:
        import project_dirs
        dirs = project_dirs.existing_dirs(ROOT)
        return [str(d) for d in dirs], None
    except Exception as exc:
        return [], "project_dirs unavailable (%s: %s)" % (type(exc).__name__, exc)


def records(dirs):
    """[(sid, path, bytes, mtime, kind)] over EVERY *.jsonl under each project dir, at any depth.

    ⛔ THE FIRST RUN OF THIS FILE COUNTED 0 SUBAGENT RECORDS AND THAT WAS A DEFECT IN THIS FUNCTION,
    not an absence on disk. It looked in `<project>/subagents/`, which is the path the machine-global
    constitution documents (`~/.claude/projects/**/subagents/agent-*.jsonl`).
    `[measured 2026-09-12 16:0x CDT]` **No `subagents/` directory exists at that depth for any project
    key -- `find ~/.claude/projects -maxdepth 2 -type d -name subagents` returns 0.** The live layout is
    `<project>/<session-id>/subagents/agent-*.jsonl`, ONE LEVEL DEEPER, and the live CFL store holds
    **204** such files.
    ⭐ So an instrument joining the documented path literally reads a real, populated channel as empty --
    and that channel is the ONLY place Jon's mid-turn messages to subagents exist. A zero from it is
    indistinguishable from him never having typed. Walk, never join."""
    out = []
    for d in dirs:
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in ("tool-results", "__pycache__")]
            for fn in filenames:
                if not fn.endswith(".jsonl"):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                sid = fn[:-6]
                kind = "subagent" if (fn.startswith("agent-") or
                                      os.path.basename(dirpath) == "subagents") else "main"
                out.append((sid, p, st.st_size, st.st_mtime, kind))
    return out


def render_index():
    """short-prefix -> newest render mtime, and the count of renders carrying it."""
    idx, unknown = {}, []
    for root in RENDER_ROOTS:
        if not os.path.isdir(root):
            unknown.append((root, "render root absent"))
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                for m in re.finditer(r"-([0-9a-f]{6})[-.]", fn):
                    key = m.group(1)
                    p = os.path.join(dirpath, fn)
                    try:
                        mt = os.path.getmtime(p)
                    except OSError:
                        continue
                    cur = idx.get(key)
                    if cur is None or mt > cur[0]:
                        idx[key] = (mt, (cur[1] + 1) if cur else 1, p)
                    else:
                        idx[key] = (cur[0], cur[1] + 1, cur[2])
    return idx, unknown


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass
    dirs, derr = project_dirs_list()
    unknown = []
    if derr:
        unknown.append(("project_dirs", derr))
    recs = records(dirs)
    idx, runk = render_index()
    unknown += runk

    rendered, stale, missing = [], [], []
    for sid, p, sz, mt, kind in recs:
        # ⛔ STRIP THE `agent-` PREFIX BEFORE TAKING SIX CHARS. The first run with subagents included
        # reported 1,117 unrendered of 1,210 and 546.6 MB "invisible" -- because `sid[:6]` of
        # `agent-ab87d73f16663f858` is the literal string `agent-`, which matches nothing.
        # `[measured 2026-09-12 16:1x]` Subagent renders DO exist and are keyed by the AGENT id's
        # prefix: `raw/transcripts/claude-code/subagents/8634ad/code-2026-09-12-ab87d7-….md`.
        # ⭐ A matcher bug reads exactly like a corpus gap, and a 546 MB one reads like a crisis.
        # Caught by asking why a file I had watched get rendered an hour earlier counted as missing.
        stem = sid[6:] if sid.startswith("agent-") else sid
        key = stem[:6].lower()
        hit = idx.get(key)
        if hit is None:
            missing.append((sid, p, sz, mt, kind))
        else:
            rendered.append((sid, sz, kind))
            if mt > hit[0] + 1:
                stale.append((sid, sz, kind, mt - hit[0]))

    print("=== RENDER HORIZON -- per session, not a max() ===")
    print("  tree          : %s" % ROOT)
    print("  project dirs  : %d %s" % (len(dirs), [os.path.basename(d) for d in dirs]))
    print("  render roots  : %s" % RENDER_ROOTS)
    print()
    print("  RECORDS ON DISK      : %d  (%d main, %d subagent)"
          % (len(recs), sum(1 for r in recs if r[4] == "main"), sum(1 for r in recs if r[4] == "subagent")))
    print("  RECORDS RENDERED     : %d" % len(rendered))
    print("  ⛔ DIFFERENCE (no render found) : %d" % len(missing))
    print("  ⚠️ STALE (jsonl newer than its newest render) : %d" % len(stale))
    if missing:
        missing.sort(key=lambda r: -r[2])
        print()
        print("  LARGEST UNRENDERED, by jsonl bytes -- the most content no markdown index can see:")
        for sid, p, sz, mt, kind in missing[:8]:
            print("    %10d B  %-8s %s" % (sz, kind, sid))
        print("    total unrendered bytes: %d (%.1f MB)"
              % (sum(r[2] for r in missing), sum(r[2] for r in missing) / 1048576.0))
    if stale:
        stale.sort(key=lambda r: -r[3])
        print()
        print("  STALEST RENDERS, by how far the record is ahead:")
        for sid, sz, kind, dt in stale[:5]:
            print("    %7.1f h behind  %-8s %s" % (dt / 3600.0, kind, sid))
    print()
    print("  ⭐ THE GAP IS NEVER ZERO AND A ZERO HERE MEANS NOT MEASURED.")
    if unknown:
        print("  ⛔ UNKNOWN -- %d root(s) unreadable; every count above is a FLOOR:" % len(unknown))
        for what, why in unknown:
            print("     %s -- %s" % (what, why))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
